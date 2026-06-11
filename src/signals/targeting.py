"""WS-B — targeting + exposure-trend signal.

Combines the EU exposure rollup (`retention.supplier_exposure_daily`, WS-A)
with the europe-west3 business data (`business_development` via
`data.suppliers.get_current`) into one per-supplier targeting row:

  - segment            non-venue (lead-driven) / venue / retail (wrong-model)
  - exposure level     views over the last 60d and 365d
  - exposure trend     last 60d vs the prior 60d  ← the headline signal
  - tenure / first_term, term_months, days_until_renewal
  - at_risk_score      rule-based on the VALIDATED drivers (exposure level+trend,
                       first-term, term length, recency) — a signal that triggers
                       actions, not an ML product
  - at_risk_tier       the UNION of the rule overlay and the live churn model's
                       flags (doc 24 §3: blend, don't retrain — the model misses
                       low-exposure churners, the overlay misses what the model's
                       business/call features catch). `at_risk_tier_rule` keeps
                       the overlay-only tier; `live_churn_probability` /
                       `live_model_flag` record the model's view per snapshot
  - bundle_eligible    non-venue lead-driven + low-exposure (the pilot pool)

Rows cover active paid suppliers (suppliers.get_current) PLUS the recently-lapsed
(suppliers.get_lapsed, renewal_status='lapsed') so the journey `lapsed` stage and
the winback experiment have a real population (ended-terms feed, doc 29 §2.5).

Cross-region by design: exposure is EU, business data is europe-west3 → joined in
pandas. Output is written to the US `retention` dataset (like supplier_stats_daily).

Targeting is the engine that decides WHO enters the value-add bundle. See
docs/strategy/17–20.
"""

import os

import pandas as pd
import yaml

from data import client, predictions, suppliers

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_EXPOSURE_TABLE = (
    f"{client.PROJECT_ID}.{client.DATASET_EU}.{_CONFIG['tables']['supplier_exposure']}"
)

# Low-exposure threshold (views/yr) — the 42%→30% churn cliff (≈ photographer
# median) from the multi-driver analysis (docs/strategy/17 §2c).
LOW_EXPOSURE_VIEWS_YR = 330

# renewal_status values that mean the supplier is still in a paid relationship —
# 'active' (current term), 'already_renewed' (a future paid term exists), or
# 'will_churn' (current paid term running but a Gratis downgrade is already
# scheduled — a SAVE population, not winback: they only become lapsed after the
# term actually ends, via the ended-terms feed). Anything else is genuinely
# lapsed (the winback pool). Defined as an allowlist so unknown future churned
# markers default to lapsed, not retained. Lapsed rows come from
# suppliers.get_lapsed() (renewal_status='lapsed', ended-terms feed — doc 29 §2.5).
RETAINED_STATUSES = {"active", "already_renewed", "will_churn"}

# How far back a lapsed supplier stays in targeting (months since their last paid
# term ended). Matches directives.LEVERS['winback'] params.max_lapsed_months —
# beyond this, winback is no longer the right motion.
WINBACK_LAPSED_MONTHS = 6

VENUE_CATEGORY = "Trouwlocaties"
# Wrong-model retail: couples don't shortlist-and-inquire → exposure lever N/A.
WRONG_MODEL_CATEGORIES = {
    "Trouwringen",
    "Trouwpak",
    "Catering",
    "Trouwkaarten",
    "Huwelijksbedankjes",
    "Bruidsschoenen",
    "Bruidsaccessoires",
    "Trouwauto",
}


def _exposure_features() -> pd.DataFrame:
    """Per-supplier exposure level + trend, anchored on the latest data date."""
    sql = f"""
    WITH anchor AS (SELECT MAX(date) AS d FROM `{_EXPOSURE_TABLE}`)
    SELECT
        profile_id,
        SUM(IF(date > DATE_SUB((SELECT d FROM anchor), INTERVAL 60 DAY),
               profile_views, 0)) AS views_60d,
        SUM(IF(date <= DATE_SUB((SELECT d FROM anchor), INTERVAL 60 DAY)
               AND date > DATE_SUB((SELECT d FROM anchor), INTERVAL 120 DAY),
               profile_views, 0)) AS views_prev_60d,
        SUM(IF(date > DATE_SUB((SELECT d FROM anchor), INTERVAL 365 DAY),
               profile_views, 0)) AS views_365d,
        SUM(IF(date > DATE_SUB((SELECT d FROM anchor), INTERVAL 60 DAY),
               impressions, 0)) AS impressions_60d,
        SUM(IF(date > DATE_SUB((SELECT d FROM anchor), INTERVAL 60 DAY),
               show_phone, 0)) AS show_phone_60d,
        DATE_DIFF((SELECT d FROM anchor),
                  MAX(IF(profile_views > 0, date, NULL)), DAY) AS days_since_last_view
    FROM `{_EXPOSURE_TABLE}`
    WHERE date > DATE_SUB((SELECT d FROM anchor), INTERVAL 365 DAY)
    GROUP BY profile_id
    """
    df = client.query_eu(sql)
    df["profile_id"] = df["profile_id"].astype(str)
    return df


def _segment(category: str) -> str:
    if category == VENUE_CATEGORY:
        return "venue"
    if category in WRONG_MODEL_CATEGORIES:
        return "retail"
    return "non-venue"


def _at_risk_score(row) -> float:
    """Rule-based at-risk score on the validated churn drivers (0–1)."""
    score = 0.10
    # Exposure level (the #1 driver)
    if row["views_365d"] < LOW_EXPOSURE_VIEWS_YR:
        score += 0.30
    if row["views_365d"] < LOW_EXPOSURE_VIEWS_YR / 2:
        score += 0.10
    # Exposure trend (declining)
    if row["exposure_trend"] < -0.3:
        score += 0.15
    # First term (year-1 cliff: 38% vs 12%)
    if row["first_term"]:
        score += 0.20
    # Short (non-annual) term
    if row["term_months"] < 12:
        score += 0.10
    # No recent exposure at all
    if row["days_since_last_view"] is None or row["days_since_last_view"] > 30:
        score += 0.15
    # Downgrade to Gratis already scheduled — the supplier has decided; the
    # save conversation is now, not at a predicted-risk threshold
    if row.get("renewal_status") == "will_churn":
        score += 0.40
    return max(0.0, min(1.0, score))


def _tier(score: float) -> str:
    if score >= 0.70:
        return "P1"
    if score >= 0.50:
        return "P2"
    if score >= 0.30:
        return "P3"
    return "P4"


_TIER_RANK = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}


def _blend_tier(rule_tier: str, live_flag: bool, live_critical: bool) -> str:
    """Union of the rule overlay and the live churn model (doc 24 §3: OR-blend).

    The live model is high-precision / ~27% recall and lacks exposure features;
    the overlay IS those features. The union maximises recall: a supplier is at
    least P2 when the live model flags churn at its own calibrated threshold,
    at least P1 when it says Critical (probability ≥ ~0.80). The rule tier is
    never downgraded.
    """
    live_tier = "P1" if live_critical else ("P2" if live_flag else None)
    if live_tier and _TIER_RANK[live_tier] < _TIER_RANK[rule_tier]:
        return live_tier
    return rule_tier


def calculate() -> pd.DataFrame:
    """Build the per-supplier targeting table: active paid suppliers + the
    recently-lapsed (winback pool, renewal_status='lapsed')."""
    sup = suppliers.get_current()
    lapsed = suppliers.get_lapsed(months_back=WINBACK_LAPSED_MONTHS)
    # Active wins if a profile somehow appears in both feeds (the 30-day grace
    # boundary in suppliers.py makes the two windows disjoint by construction).
    sup = pd.concat([sup, lapsed], ignore_index=True)
    sup = sup.drop_duplicates(subset="profile_id", keep="first")
    sup["profile_id"] = sup["profile_id"].astype(str)
    exp = _exposure_features()

    df = sup.merge(exp, on="profile_id", how="left")
    today = pd.Timestamp.now().normalize()

    # Exposure columns → fill missing with 0 / sentinel
    for col in ["views_60d", "views_prev_60d", "views_365d", "impressions_60d", "show_phone_60d"]:
        df[col] = df[col].fillna(0).astype(int)
    df["days_since_last_view"] = df["days_since_last_view"].fillna(999).astype(int)

    # Derived features
    df["segment"] = df["category"].apply(_segment)
    df["first_term"] = df["num_paid_plans_before"].fillna(0).astype(int) == 0
    df["plan_start"] = pd.to_datetime(df["plan_start"], errors="coerce")
    df["plan_end"] = pd.to_datetime(df["plan_end"], errors="coerce")
    df["term_months"] = ((df["plan_end"] - df["plan_start"]).dt.days / 30.0).fillna(12.0)
    df["days_until_renewal"] = (df["plan_end"] - today).dt.days
    df["exposure_trend"] = (
        (df["views_60d"] - df["views_prev_60d"]) / df["views_prev_60d"].replace(0, pd.NA)
    ).fillna(0.0)
    df["low_exposure"] = df["views_365d"] < LOW_EXPOSURE_VIEWS_YR

    df["at_risk_score"] = df.apply(_at_risk_score, axis=1).round(3)
    df["at_risk_tier_rule"] = df["at_risk_score"].apply(_tier)

    # Live churn-model blend (doc 24 §3 / doc 29 §2.3): consume the external
    # model's scores — never retrain or replace it here. The targeting snapshot
    # is append-per-day, so these columns also become the durable prediction
    # history the external table doesn't keep. Degrades to overlay-only if the
    # external pipeline is unavailable.
    try:
        live = predictions.get_latest()
    except Exception as e:
        print(f"[targeting] live churn predictions unavailable ({e}) — overlay-only")
        live = pd.DataFrame(
            columns=["profile_id", "live_churn_probability", "live_model_flag", "live_critical"]
        )
    df = df.merge(live, on="profile_id", how="left")
    df["live_model_flag"] = df["live_model_flag"].fillna(False).astype(bool)
    df["live_critical"] = df["live_critical"].fillna(False).astype(bool)
    df["at_risk_tier"] = [
        _blend_tier(rule, flag, crit)
        for rule, flag, crit in zip(
            df["at_risk_tier_rule"], df["live_model_flag"], df["live_critical"], strict=True
        )
    ]

    # Pilot pool: non-venue lead-driven + low-exposure (+ not already churning/renewed)
    df["bundle_eligible"] = (
        (df["segment"] == "non-venue")
        & df["low_exposure"]
        & (df.get("renewal_status", "active") == "active")
    )

    df["stats_date"] = today
    return df


_OUTPUT_COLUMNS = [
    "profile_id", "profile_name", "category", "segment", "plan_value",
    "plan_start", "plan_end", "days_until_renewal", "renewal_status",
    "first_term", "num_paid_plans_before", "term_months",
    "views_60d", "views_prev_60d", "views_365d", "impressions_60d",
    "show_phone_60d", "days_since_last_view", "exposure_trend", "low_exposure",
    "at_risk_score", "at_risk_tier", "at_risk_tier_rule",
    "live_churn_probability", "live_model_flag", "bundle_eligible", "stats_date",
]


def build() -> pd.DataFrame:
    """Calculate and write supplier_targeting to the US retention dataset."""
    df = calculate()
    out = df[[c for c in _OUTPUT_COLUMNS if c in df.columns]].copy()
    table = _CONFIG["tables"]["supplier_targeting"]
    if client.table_exists(table):
        client.delete_today(table, date_column="stats_date")
    client.write(out, table, if_exists="append")
    return out
