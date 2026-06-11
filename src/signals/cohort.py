"""WS-C — holdout / cohort assignment (the experiment integrity backbone).

`cohort_assignment` is the **single source of truth** for who is in which arm of
the lifecycle pilot. Every emitter (Elastic boost, newsletter, scraper trigger,
Bird email) must read it and **filter out control before acting** — otherwise the
pilot is unmeasurable (see docs/strategy/19 §"Holdout enforcement").

Design (docs/strategy/18 §pilot, doc 20 WS-C):
  - Unit          = profile_id, 1:1 randomization.
  - Assignment    = **stable hash** of (experiment_id, salt, profile_id). Same
                    inputs always yield the same arm, so re-runs NEVER reshuffle
                    anyone already assigned. Not Python's randomized hash().
  - Rerandomize   = on a FRESH experiment, search candidate salts and pick the one
                    that minimizes baseline imbalance (standardized mean diff on
                    views_60d/views_365d) between arms. The winning salt is LOCKED
                    (persisted per row as `salt_used`); later incremental enrolees
                    reuse it via the same stable hash, so the split stays stable.
                    (Fixes the mild profile_views imbalance WS-E flagged at N=164.)
  - Append-only   = each run enrolls newly-eligible suppliers into the experiment;
                    existing rows are never modified or deleted (stable cohort).
  - Stage-1 pool  = low-exposure photographers (± videographers/music) — the
                    fast exposure-lift mechanism test (~82/arm, well-powered).

Reads `supplier_targeting` (WS-B, EU `retention`) for the eligible pool; writes
`cohort_assignment` (EU `retention`). Stage-2 (renewal endpoint) reuses this module
with a wider category pool + a renewal-window enrolment gate.

Each experiment declares an `eligibility` mode that selects its population:
  - category_bundle : low-exposure bundle pool in named categories (stage1_exposure)
  - first_term      : suppliers in their first paid term (onboarding)
  - churned         : lapsed suppliers (winback) — NOTE: supplier_targeting is built
                      from ACTIVE suppliers only, so the churned feed must be wired
                      before this cohort populates (docs/strategy/28 follow-ups).
"""

import hashlib
import os

import pandas as pd
import yaml

from data import client
from signals import targeting

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_TARGETING_TABLE = _CONFIG["tables"]["supplier_targeting"]
_COHORT_TABLE = _CONFIG["tables"]["cohort_assignment"]


# --- Experiment registry -------------------------------------------------
# Each experiment defines WHO is eligible and the salt that fixes the split.
# Bump the salt only to deliberately re-randomize a *new* experiment_id — never
# the salt of a running experiment (it would reshuffle live arms).
EXPERIMENTS = {
    "stage1_exposure": {
        "cohort": "low_exposure_photo_video_music",
        "eligibility": "category_bundle",
        # Stage-1 mechanism test: fast exposure-lift endpoint, ~6–8 wks.
        "categories": {"Trouwfotograaf", "Videograaf", "Muziek"},
        # None → enrol every eligible supplier (Stage-1 wants N for the lift
        # endpoint, not renewal proximity). Stage-2 sets this to 90.
        "renewal_window_days": None,
        "salt": "stage1_exposure_v1",
    },
    # First-term activation cohort — targets the validated year-1 churn cliff.
    # Population = suppliers in their first paid term, any lead-driven category.
    "onboarding": {
        "cohort": "first_term_suppliers",
        "eligibility": "first_term",
        "categories": None,           # any category; first_term is the gate
        "renewal_window_days": None,
        "salt": "onboarding_v1",
    },
    # Reactivation cohort — lapsed suppliers, fed by suppliers.get_lapsed() via
    # targeting (renewal_status='lapsed', ended-terms feed — doc 29 §2.5). Enrol
    # deliberately (build_cohort.py winback) only when the winback sequence is
    # ready to launch — enrolees age out of the ≤6-month window while gated.
    "winback": {
        "cohort": "recently_churned",
        "eligibility": "churned",
        "categories": None,
        "renewal_window_days": None,
        "salt": "winback_v1",
    },
}

_OUTPUT_COLUMNS = [
    "profile_id", "experiment_id", "cohort", "arm", "category",
    "views_365d", "days_until_renewal", "salt_used", "assigned_at",
]

# Rerandomization: how many candidate salts to search, the baseline metrics to
# balance on (max standardized-mean-diff is minimized), and the max arm-size skew
# tolerated (mod-2 hashing isn't exactly 50/50).
_RERANDOMIZE_N = 2000
_BALANCE_METRICS = ["views_60d", "views_365d"]
_MAX_ARM_SKEW = 0.10  # |n_treatment − n/2| ≤ 10% of N


def _stable_arm(profile_id: str, experiment_id: str, salt: str) -> str:
    """Deterministic 1:1 treatment/control split via a stable hash.

    Uses SHA-256 (not the process-salted built-in hash()) so the assignment is
    identical across runs, machines and languages.
    """
    key = f"{experiment_id}|{salt}|{profile_id}".encode()
    digest = int(hashlib.sha256(key).hexdigest(), 16)
    return "treatment" if digest % 2 == 0 else "control"


def _eligible(experiment_id: str) -> pd.DataFrame:
    """The eligible pool for an experiment, from the live targeting table."""
    spec = EXPERIMENTS[experiment_id]
    df = client.query(
        f"SELECT * FROM `{client.PROJECT_ID}.{client.DATASET}.{_TARGETING_TABLE}`"
    )
    df["profile_id"] = df["profile_id"].astype(str)
    # Latest snapshot only (targeting is append-per-day).
    if "stats_date" in df.columns:
        df = df[df["stats_date"] == df["stats_date"].max()]

    mode = spec.get("eligibility", "category_bundle")
    if mode == "category_bundle":
        mask = df["bundle_eligible"] & df["category"].isin(spec["categories"])
        # First-termers belong to the `onboarding` experiment (journey-stage
        # priority). Excluding them here prevents one supplier holding opposite
        # arms across experiments, which would contaminate stage1 (doc 29 §3).
        mask &= ~df["first_term"].fillna(False).astype(bool)
        window = spec["renewal_window_days"]
        if window is not None:
            mask &= df["days_until_renewal"].between(0, window)
    elif mode == "first_term":
        mask = df["first_term"].fillna(False).astype(bool)
        # Welcome material is for suppliers still deciding: a first-termer with a
        # scheduled downgrade (will_churn) belongs to the save motion
        # (renewal_window/at_risk via journey.stage), and one who already renewed
        # has cleared the year-1 cliff — neither enrols in onboarding.
        if "renewal_status" in df.columns:
            mask &= df["renewal_status"] == "active"
        if spec.get("categories"):
            mask &= df["category"].isin(spec["categories"])
    elif mode == "churned":
        # Lapsed = renewal_status NOT in the retained allowlist. 'already_renewed' is
        # retained (future term), so it is NOT winback. Rows arrive via
        # suppliers.get_lapsed() in targeting (≤ WINBACK_LAPSED_MONTHS since the
        # last paid term ended — ended-terms feed, doc 29 §2.5).
        if "renewal_status" in df.columns:
            mask = ~df["renewal_status"].isin(targeting.RETAINED_STATUSES)
        else:
            mask = pd.Series(False, index=df.index)
        if spec.get("categories"):
            mask &= df["category"].isin(spec["categories"])
    else:
        raise ValueError(f"Unknown eligibility mode for {experiment_id}: {mode}")
    return df[mask].copy()


def _existing(experiment_id: str) -> tuple[set[str], str | None]:
    """(profile_ids already enrolled, locked salt) for this experiment.

    The locked salt is the one the existing rows were assigned under; new enrolees
    must reuse it so the stable hash keeps them in a stable arm. None on a fresh
    experiment → triggers rerandomization.
    """
    if not client.table_exists(_COHORT_TABLE):
        return set(), None
    df = client.query(
        f"SELECT profile_id, salt_used "
        f"FROM `{client.PROJECT_ID}.{client.DATASET}.{_COHORT_TABLE}` "
        f"WHERE experiment_id = '{experiment_id}'"
    )
    if df.empty:
        return set(), None
    salts = df["salt_used"].dropna().unique()
    locked = str(salts[0]) if len(salts) else None
    return set(df["profile_id"].astype(str)), locked


def _smd(a: pd.Series, b: pd.Series) -> float:
    """Standardized mean difference between two arms (pooled-SD scaled)."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    pooled = (((na - 1) * a.var() + (nb - 1) * b.var()) / (na + nb - 2)) ** 0.5
    return abs(a.mean() - b.mean()) / pooled if pooled else 0.0


def _imbalance(df: pd.DataFrame, arm: pd.Series) -> float:
    """Worst standardized mean diff across the balance metrics (lower = better)."""
    t, c = arm == "treatment", arm == "control"
    return max(
        (_smd(df.loc[t, m], df.loc[c, m]) for m in _BALANCE_METRICS if m in df.columns),
        default=0.0,
    )


def _choose_salt(pool: pd.DataFrame, experiment_id: str, base_salt: str) -> tuple[str, float]:
    """Search candidate salts; return the one with the most balanced arms."""
    best_salt, best_score = base_salt, float("inf")
    n = len(pool)
    for i in range(_RERANDOMIZE_N):
        salt = f"{base_salt}#{i}"
        arm = pool["profile_id"].apply(
            lambda pid, s=salt: _stable_arm(pid, experiment_id, s)
        )
        if abs((arm == "treatment").sum() - n / 2) > _MAX_ARM_SKEW * n:
            continue
        score = _imbalance(pool, arm)
        if score < best_score:
            best_salt, best_score = salt, score
    return best_salt, best_score


def assign(experiment_id: str = "stage1_exposure") -> pd.DataFrame:
    """Compute the NEW enrolments for an experiment (does not write)."""
    if experiment_id not in EXPERIMENTS:
        raise ValueError(f"Unknown experiment_id: {experiment_id}")
    spec = EXPERIMENTS[experiment_id]

    pool = _eligible(experiment_id)
    already, locked = _existing(experiment_id)
    new = pool[~pool["profile_id"].isin(already)].copy()
    if new.empty:
        return new

    # Fresh experiment → rerandomize for baseline balance; otherwise reuse the
    # locked salt so prior assignments stay stable.
    if locked is None:
        salt, score = _choose_salt(new, experiment_id, spec["salt"])
        print(f"  rerandomized: salt={salt!r}  max baseline SMD={score:.3f}")
    else:
        salt = locked

    new["experiment_id"] = experiment_id
    new["cohort"] = spec["cohort"]
    new["arm"] = new["profile_id"].apply(lambda pid: _stable_arm(pid, experiment_id, salt))
    new["salt_used"] = salt
    new["assigned_at"] = pd.Timestamp.now()
    return new[[c for c in _OUTPUT_COLUMNS if c in new.columns]].copy()


def build(experiment_id: str = "stage1_exposure") -> pd.DataFrame:
    """Enrol newly-eligible suppliers into the experiment (append-only)."""
    new = assign(experiment_id)
    if not new.empty:
        client.write(new, _COHORT_TABLE, if_exists="append")
    return new


# --- Holdout enforcement helpers (used by every emitter) -----------------

def enrolled_ids() -> set[str]:
    """Every profile_id holding an arm in ANY experiment (treatment or control).

    For legacy / off-experiment emitters: they must skip ALL enrolled suppliers —
    control may never be touched, and treatment may not receive uncontrolled
    extra touches outside its experiment's lever set (doc 29 §5).
    """
    if not client.table_exists(_COHORT_TABLE):
        return set()
    df = client.query(
        f"SELECT DISTINCT profile_id FROM "
        f"`{client.PROJECT_ID}.{client.DATASET}.{_COHORT_TABLE}`"
    )
    return set(df["profile_id"].astype(str))


def treatment_ids(experiment_id: str = "stage1_exposure") -> set[str]:
    """profile_ids in the TREATMENT arm — the only suppliers an emitter may act on."""
    if not client.table_exists(_COHORT_TABLE):
        return set()
    df = client.query(
        f"SELECT profile_id FROM `{client.PROJECT_ID}.{client.DATASET}.{_COHORT_TABLE}` "
        f"WHERE experiment_id = '{experiment_id}' AND arm = 'treatment'"
    )
    return set(df["profile_id"].astype(str))


def filter_treatment(
    df: pd.DataFrame, experiment_id: str = "stage1_exposure", id_col: str = "profile_id"
) -> pd.DataFrame:
    """Drop control/unassigned rows so an emitter can only act on treatment.

    This is the enforcement check every emitter must run before emitting a
    directive — boost, newsletter, scraper trigger or email.
    """
    keep = treatment_ids(experiment_id)
    return df[df[id_col].astype(str).isin(keep)].copy()
