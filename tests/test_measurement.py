"""Measurement harness: DiD math on synthetic panels + audit scoping."""

import pandas as pd

from analytics import measurement


def _panel(n_per_arm=40, treatment_post=2.0, control_post=1.0):
    """Synthetic per-supplier pre/post panel.

    Deterministic jitter, different cycle lengths pre vs post, so per-supplier
    DiD has variance (the t-test needs it) without any randomness.
    """
    rows = []
    for arm, post_base in (("treatment", treatment_post), ("control", control_post)):
        for k in range(n_per_arm):
            rates = {"pre": 1.0 + (k % 5) * 0.01, "post": post_base + (k % 7) * 0.01}
            for period, rate in rates.items():
                rows.append(
                    {
                        "profile_id": f"{arm[0]}{k}",
                        "arm": arm,
                        "experiment_id": "test",
                        "period": period,
                        "days": 60,
                        "profile_views": int(rate * 60),
                        "profile_views_per_day": rate,
                    }
                )
    return pd.DataFrame(rows)


def test_two_arm_detects_real_lift():
    out = measurement._two_arm(_panel(treatment_post=2.0, control_post=1.0), "profile_views")
    assert out["n_treatment"] == 40 and out["n_control"] == 40
    assert out["baseline_balance_p"] > 0.2            # arms indistinguishable pre
    assert abs(out["did_treatment"] - 1.0) < 0.02     # ≈ +1 view/day in treatment
    assert abs(out["did_control"]) < 0.02
    assert out["did_p"] < 0.001                       # headline causal test fires
    assert 95 < out["lift_pct"] < 100
    assert out["did_cohens_d"] > 1


def test_two_arm_null_when_no_lift():
    out = measurement._two_arm(_panel(treatment_post=1.0, control_post=1.0), "profile_views")
    # identical DiD distributions in both arms → no detected effect
    assert out["did_treatment"] == out["did_control"]
    assert pd.isna(out["did_p"]) or out["did_p"] > 0.5


def test_two_arm_detects_baseline_imbalance():
    panel = _panel()
    # shift the treatment arm's PRE rates up — the balance check must flag it
    pre_t = (panel["arm"] == "treatment") & (panel["period"] == "pre")
    panel.loc[pre_t, "profile_views_per_day"] += 0.5
    out = measurement._two_arm(panel, "profile_views")
    assert out["baseline_balance_p"] < 0.001


# --- Contamination audit scoping --------------------------------------------

def _patch_audit(monkeypatch, control_ids, log_ids, assigned="2026-06-10"):
    def fake_query(sql, **kw):
        if "cohort_assignment" in sql:
            return pd.DataFrame(
                {"profile_id": control_ids, "assigned_at": [assigned] * len(control_ids)}
            )
        return pd.DataFrame({"profile_id": log_ids})

    monkeypatch.setattr(measurement.client, "query", fake_query)
    monkeypatch.setattr(measurement.client, "table_exists", lambda t: t == "actions_log")
    monkeypatch.setattr(measurement, "_date_column", lambda t: "action_date")


def test_audit_flags_control_in_emitter_log(monkeypatch):
    _patch_audit(monkeypatch, control_ids=["1", "2"], log_ids=["2", "99"])
    out = measurement.contamination_audit("stage1_exposure")
    assert out["status"] == "CONTAMINATED"
    assert out["control_contamination"] == {"actions_log": 1}


def test_audit_clean_when_logs_only_touch_treatment(monkeypatch):
    _patch_audit(monkeypatch, control_ids=["1", "2"], log_ids=["99", "98"])
    out = measurement.contamination_audit("stage1_exposure")
    assert out["status"] == "CLEAN"
    assert out["control_contamination"] == {"actions_log": 0}
