"""WS-E — measurement harness: exposure lift, treatment vs control.

The G1 readout. Answers "did the levers move exposure?" with a clean
difference-in-differences on `supplier_exposure_daily`, using the holdout arms in
`cohort_assignment` (WS-C) as treatment/control.

Method (docs/strategy/18 §pilot, doc 20 WS-E):
  - Anchor each supplier on its own `assigned_at`.
  - PRE  = [assigned_at − pre_days, assigned_at)   — baseline.
  - POST = [assigned_at, assigned_at + post_days)  — capped at the latest data
           date (so it reads cleanly even mid-pilot / before levers go live).
  - Per supplier, per period: each exposure metric as a **per-day rate** (sum ÷
    days observed), so unequal/short windows stay comparable.
  - **DiD per supplier** = post_rate − pre_rate. The headline test is
    t(treatment ΔΔ vs control ΔΔ) on profile_views — it nets out any baseline
    imbalance, so it's the causal estimate of the lift.
  - **Baseline balance** = t(treatment pre vs control pre). Run it NOW, before the
    levers turn on: the arms should be statistically indistinguishable. That is
    itself the first validation that the holdout split is sound.

Cross-region by design: cohort is US, exposure is EU → joined in pandas.

Also persists a per-supplier pre/post panel to `retention.measurement_panel` so a
readout is reproducible and auditable.
"""

import os

import pandas as pd
import yaml
from scipy import stats

from data import client

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_EXPOSURE_TABLE = (
    f"{client.PROJECT_ID}.{client.DATASET_EU}.{_CONFIG['tables']['supplier_exposure']}"
)
_COHORT_TABLE = f"{client.PROJECT_ID}.{client.DATASET}.{_CONFIG['tables']['cohort_assignment']}"
_PANEL_TABLE = "measurement_panel"

# Exposure metrics tracked for the lift readout (profile_views is the headline).
_METRICS = ["profile_views", "impressions", "list_clicks", "show_phone", "website_open"]

PRE_DAYS = 60
POST_DAYS = 60


def _load_cohort(experiment_id: str) -> pd.DataFrame:
    df = client.query(
        f"SELECT profile_id, arm, assigned_at FROM `{_COHORT_TABLE}` "
        f"WHERE experiment_id = '{experiment_id}'"
    )
    df["profile_id"] = df["profile_id"].astype(str)
    # assigned_at may come back tz-aware (BigQuery TIMESTAMP) or tz-naive (DATETIME)
    # depending on how it was written; force tz-naive so it compares with the
    # tz-naive exposure `date`.
    df["assigned_at"] = (
        pd.to_datetime(df["assigned_at"], utc=True).dt.tz_localize(None).dt.normalize()
    )
    return df


def _load_exposure(profile_ids: list[str], start: pd.Timestamp) -> pd.DataFrame:
    """Daily exposure (EU) for the enrolled suppliers from `start` onward."""
    ids = ",".join(f"'{p}'" for p in profile_ids)
    cols = ", ".join(_METRICS)
    df = client.query_eu(
        f"SELECT profile_id, date, {cols} FROM `{_EXPOSURE_TABLE}` "
        f"WHERE date >= '{start.date()}' AND profile_id IN ({ids})"
    )
    df["profile_id"] = df["profile_id"].astype(str)
    df["date"] = pd.to_datetime(df["date"])
    return df


def build_panel(
    experiment_id: str = "stage1_exposure", pre_days: int = PRE_DAYS, post_days: int = POST_DAYS
) -> pd.DataFrame:
    """Per-supplier × period exposure panel (one row per profile_id × pre/post)."""
    cohort = _load_cohort(experiment_id)
    if cohort.empty:
        return pd.DataFrame()

    earliest = (cohort["assigned_at"].min() - pd.Timedelta(days=pre_days)).normalize()
    exp = _load_exposure(cohort["profile_id"].tolist(), earliest)
    data_max = exp["date"].max() if not exp.empty else cohort["assigned_at"].max()

    rows = []
    for _, c in cohort.iterrows():
        a = c["assigned_at"]
        sub = exp[exp["profile_id"] == c["profile_id"]]
        windows = {
            "pre": (a - pd.Timedelta(days=pre_days), a),
            # POST capped at the latest available data date.
            "post": (a, min(a + pd.Timedelta(days=post_days), data_max + pd.Timedelta(days=1))),
        }
        for period, (lo, hi) in windows.items():
            days = max((hi - lo).days, 0)
            w = sub[(sub["date"] >= lo) & (sub["date"] < hi)]
            row = {
                "profile_id": c["profile_id"], "arm": c["arm"], "experiment_id": experiment_id,
                "period": period, "days": days,
            }
            for m in _METRICS:
                total = int(w[m].sum()) if not w.empty else 0
                row[m] = total
                row[f"{m}_per_day"] = total / days if days > 0 else 0.0
            rows.append(row)
    panel = pd.DataFrame(rows)
    panel["computed_at"] = pd.Timestamp.now()
    return panel


def _two_arm(panel: pd.DataFrame, metric: str) -> dict:
    """Lift readout for one metric: baseline balance, post comparison, DiD test."""
    rate = f"{metric}_per_day"
    pre = panel[panel["period"] == "pre"].set_index("profile_id")
    post = panel[panel["period"] == "post"].set_index("profile_id")

    # Per-supplier DiD (post_rate − pre_rate), aligned on profile_id.
    did = (post[rate] - pre[rate]).to_frame("did").join(post["arm"])
    t_did = did[did["arm"] == "treatment"]["did"]
    c_did = did[did["arm"] == "control"]["did"]

    t_pre = pre[pre["arm"] == "treatment"][rate]
    c_pre = pre[pre["arm"] == "control"][rate]
    t_post = post[post["arm"] == "treatment"][rate]
    c_post = post[post["arm"] == "control"][rate]

    def _safe_t(a, b):
        if len(a) < 2 or len(b) < 2 or (a.std() == 0 and b.std() == 0):
            return (float("nan"), float("nan"))
        s = stats.ttest_ind(a, b, equal_var=False)
        return (float(s.statistic), float(s.pvalue))

    def _cohens_d(a, b):
        if len(a) < 2 or len(b) < 2:
            return float("nan")
        na, nb = len(a), len(b)
        pooled = (((na - 1) * a.var() + (nb - 1) * b.var()) / (na + nb - 2)) ** 0.5
        return float((a.mean() - b.mean()) / pooled) if pooled else float("nan")

    _, bal_p = _safe_t(t_pre, c_pre)
    _, did_p = _safe_t(t_did, c_did)
    lift_pct = (
        (t_post.mean() / c_post.mean() - 1.0) * 100 if c_post.mean() else float("nan")
    )
    return {
        "metric": metric,
        "n_treatment": int(len(t_post)), "n_control": int(len(c_post)),
        "baseline_treatment_per_day": round(float(t_pre.mean()), 3),
        "baseline_control_per_day": round(float(c_pre.mean()), 3),
        "baseline_balance_p": round(bal_p, 4),  # want NS pre-launch
        "post_treatment_per_day": round(float(t_post.mean()), 3),
        "post_control_per_day": round(float(c_post.mean()), 3),
        "lift_pct": round(lift_pct, 1),
        "did_treatment": round(float(t_did.mean()), 3),
        "did_control": round(float(c_did.mean()), 3),
        "did_p": round(did_p, 4),  # the headline causal test
        "did_cohens_d": round(_cohens_d(t_did, c_did), 3),
    }


def _date_column(table: str) -> str | None:
    """First DATE/TIMESTAMP/DATETIME column on a table (for time-scoping)."""
    schema = client._bq_client.get_table(
        f"{client.PROJECT_ID}.{client.DATASET}.{table}"
    ).schema
    for f in schema:
        if f.field_type in ("DATE", "TIMESTAMP", "DATETIME"):
            return f.name
    return None


def contamination_audit(experiment_id: str = "stage1_exposure") -> dict:
    """Did any CONTROL supplier receive a directive AFTER enrolment?

    Must be zero for a clean G1. Scoped to on/after the experiment's earliest
    `assigned_at` so pre-pilot/deprecated log rows (e.g. the old D1–D3 crm_tasks)
    don't read as contamination.
    """
    control = client.query(
        f"SELECT profile_id, assigned_at FROM `{_COHORT_TABLE}` "
        f"WHERE experiment_id = '{experiment_id}' AND arm = 'control'"
    )
    control_ids = set(control["profile_id"].astype(str))
    start = pd.to_datetime(control["assigned_at"]).min()
    # Emitter logs don't exist until WS-D is built; check the ones that do.
    candidates = ["intervention_log", "actions_log", "retention_directives"]
    leaks: dict[str, int] = {}
    unscoped: list[str] = []
    for tname in candidates:
        if not client.table_exists(tname):
            continue
        datecol = _date_column(tname)
        where = ""
        if datecol is not None:
            where = f" WHERE CAST({datecol} AS TIMESTAMP) >= TIMESTAMP('{start}')"
        else:
            unscoped.append(tname)
        log = client.query(
            f"SELECT DISTINCT profile_id "
            f"FROM `{client.PROJECT_ID}.{client.DATASET}.{tname}`{where}"
        )
        hit = control_ids & set(log["profile_id"].astype(str))
        leaks[tname] = len(hit)
    return {
        "control_n": len(control_ids),
        "since": str(start),
        "emitter_logs_checked": list(leaks.keys()),
        "logs_without_date_scope": unscoped,
        "control_contamination": leaks,
        "status": (
            "no emitter logs yet (WS-D not built)" if not leaks
            else ("CLEAN" if sum(leaks.values()) == 0 else "CONTAMINATED")
        ),
    }


def readout(
    experiment_id: str = "stage1_exposure", pre_days: int = PRE_DAYS, post_days: int = POST_DAYS,
    persist: bool = True,
) -> dict:
    """Full G1 readout: per-metric lift + baseline balance + contamination audit."""
    panel = build_panel(experiment_id, pre_days, post_days)
    if panel.empty:
        return {"experiment_id": experiment_id, "error": "no cohort enrolled"}
    if persist:
        # Snapshot table — overwrite with the latest run (computed_at is a full
        # timestamp, so an append-with-delete-today wouldn't dedupe cleanly).
        client.write(panel, _PANEL_TABLE, if_exists="replace")

    post = panel[panel["period"] == "post"]
    return {
        "experiment_id": experiment_id,
        "pre_days": pre_days, "post_days": post_days,
        "post_days_observed": int(post["days"].max()) if not post.empty else 0,
        "metrics": [_two_arm(panel, m) for m in _METRICS],
        "contamination": contamination_audit(experiment_id),
    }
