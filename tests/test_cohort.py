"""Holdout assignment machinery: stable hash, rerandomization, eligibility."""

import pandas as pd

from signals import cohort

# --- Stable hash ----------------------------------------------------------

def test_stable_arm_is_deterministic():
    for pid in ("1", "14479", "999999"):
        first = cohort._stable_arm(pid, "stage1_exposure", "stage1_exposure_v1")
        assert first in ("treatment", "control")
        for _ in range(3):
            assert cohort._stable_arm(pid, "stage1_exposure", "stage1_exposure_v1") == first


def test_stable_arm_changes_with_salt_and_experiment():
    ids = [str(i) for i in range(200)]
    base = [cohort._stable_arm(p, "exp", "salt_a") for p in ids]
    assert base != [cohort._stable_arm(p, "exp", "salt_b") for p in ids]
    assert base != [cohort._stable_arm(p, "other_exp", "salt_a") for p in ids]


def test_stable_arm_is_roughly_balanced():
    ids = [str(i) for i in range(2000)]
    arms = [cohort._stable_arm(p, "exp", "salt") for p in ids]
    treat = arms.count("treatment")
    assert abs(treat - 1000) < 100  # well within the 10% skew tolerance


# --- Rerandomization ------------------------------------------------------

def _pool(n=24):
    return pd.DataFrame(
        {
            "profile_id": [str(100 + i) for i in range(n)],
            "views_60d": [10 + (i % 7) * 5 for i in range(n)],
            "views_365d": [100 + (i % 5) * 40 for i in range(n)],
            "category": "Trouwfotograaf",
            "days_until_renewal": 120,
        }
    )


def test_choose_salt_respects_skew_and_improves_balance():
    pool = _pool()
    salt, score = cohort._choose_salt(pool, "exp", "base")
    assert salt.startswith("base#")
    arms = pool["profile_id"].apply(lambda p: cohort._stable_arm(p, "exp", salt))
    n = len(pool)
    assert abs((arms == "treatment").sum() - n / 2) <= cohort._MAX_ARM_SKEW * n
    assert score == cohort._imbalance(pool, arms)


def test_assign_reuses_locked_salt_and_skips_enrolled(monkeypatch):
    pool = _pool()
    monkeypatch.setattr(cohort, "_eligible", lambda eid: pool.copy())
    already = {"100", "101"}
    monkeypatch.setattr(cohort, "_existing", lambda eid: (already, "locked_salt"))

    new = cohort.assign("stage1_exposure")
    assert set(new["profile_id"]).isdisjoint(already)
    assert (new["salt_used"] == "locked_salt").all()
    for _, row in new.iterrows():
        assert row["arm"] == cohort._stable_arm(
            row["profile_id"], "stage1_exposure", "locked_salt"
        )


def test_assign_rerandomizes_fresh_experiment(monkeypatch):
    monkeypatch.setattr(cohort, "_eligible", lambda eid: _pool())
    monkeypatch.setattr(cohort, "_existing", lambda eid: (set(), None))
    new = cohort.assign("stage1_exposure")
    assert len(new) == 24
    assert new["salt_used"].nunique() == 1
    assert new["salt_used"].iloc[0].startswith("stage1_exposure_v1#")


# --- Eligibility rules (the collision/leakage fixes of doc 29) -------------

def _patch_targeting(monkeypatch, df):
    monkeypatch.setattr(cohort.client, "query", lambda sql, **kw: df.copy())


def test_stage1_excludes_first_term_and_requires_bundle(monkeypatch, targeting_df):
    df = targeting_df(
        [
            {"profile_id": "1", "bundle_eligible": True},
            {"profile_id": "2", "bundle_eligible": True, "first_term": True},
            {"profile_id": "3", "bundle_eligible": False},
            {"profile_id": "4", "bundle_eligible": True, "category": "Trouwlocaties"},
        ]
    )
    _patch_targeting(monkeypatch, df)
    assert set(cohort._eligible("stage1_exposure")["profile_id"]) == {"1"}


def test_onboarding_requires_active_first_term(monkeypatch, targeting_df):
    df = targeting_df(
        [
            {"profile_id": "1", "first_term": True},
            {"profile_id": "2", "first_term": True, "renewal_status": "will_churn"},
            {"profile_id": "3", "first_term": True, "renewal_status": "already_renewed"},
            {"profile_id": "4", "first_term": True, "renewal_status": "lapsed"},
            {"profile_id": "5", "first_term": False},
        ]
    )
    _patch_targeting(monkeypatch, df)
    assert set(cohort._eligible("onboarding")["profile_id"]) == {"1"}


def test_winback_takes_only_non_retained(monkeypatch, targeting_df):
    df = targeting_df(
        [
            {"profile_id": "1", "renewal_status": "lapsed"},
            {"profile_id": "2", "renewal_status": "active"},
            {"profile_id": "3", "renewal_status": "will_churn"},
            {"profile_id": "4", "renewal_status": "already_renewed"},
        ]
    )
    _patch_targeting(monkeypatch, df)
    assert set(cohort._eligible("winback")["profile_id"]) == {"1"}


def test_eligibility_uses_latest_snapshot_only(monkeypatch, targeting_df):
    old = targeting_df([{"profile_id": "1", "bundle_eligible": True}])
    old["stats_date"] = pd.Timestamp("2026-06-01")
    new = targeting_df([{"profile_id": "2", "bundle_eligible": True}])
    _patch_targeting(monkeypatch, pd.concat([old, new], ignore_index=True))
    assert set(cohort._eligible("stage1_exposure")["profile_id"]) == {"2"}
