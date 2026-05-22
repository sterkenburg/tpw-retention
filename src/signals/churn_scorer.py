"""Simplified churn risk scoring. ~150 lines. No cascading models. No 200 scripts.

Uses proven features only:
- days_since_last_login
- days_since_last_lead
- engagement_trend
- profile_views_30d
- plan_value
- tenure_months
- days_until_renewal

Threshold: 0.80 for P1. Tune quarterly based on actual outcomes.
"""

import os

import pandas as pd
import yaml

# Load thresholds
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as f:
    _THRESHOLDS = yaml.safe_load(f)["thresholds"]

# Base risk score for an average supplier
_BASELINE = 0.10


def _calculate_raw_score(row: pd.Series) -> float:
    """Score from 0-1. Higher = more likely to churn.

    Logic: inactivity and negative signals INCREASE the score.
    Active, engaged, long-tenure suppliers stay near baseline.
    """
    score = _BASELINE

    # Inactivity increases risk (capped at 90 days to avoid outliers dominating)
    score += min(row.get("days_since_last_login", 0), 90) * 0.004
    score += min(row.get("days_since_last_lead", 0), 90) * 0.003

    # Declining engagement increases risk
    trend = row.get("engagement_trend", 0)
    if trend < -0.5:
        score += 0.15
    elif trend < 0:
        score += 0.05

    # Very low profile views increases risk
    if row.get("profile_views_30d", 0) < 5:
        score += 0.08

    # Renewal approaching increases risk
    if row.get("days_until_renewal", 999) < 30:
        score += 0.10

    # Higher-value plans slightly more likely to churn (or more worth saving)
    score += row.get("plan_value", 500) * 0.00002

    # Longer tenure = lower risk (loyalty effect)
    score -= min(row.get("tenure_months", 12), 60) * 0.002

    return max(0.0, min(1.0, score))


def calculate(stats: pd.DataFrame) -> pd.DataFrame:
    """Add churn_probability and priority_tier to supplier stats."""
    df = stats.copy()

    # Tenure in months
    df["plan_start"] = pd.to_datetime(df["plan_start"], errors="coerce")
    df["tenure_months"] = (
        (pd.Timestamp.now() - df["plan_start"]).dt.days / 30.0
    ).fillna(12)

    # Raw probability
    df["churn_probability"] = df.apply(_calculate_raw_score, axis=1)

    # Priority tier
    def _tier(prob: float) -> str:
        if prob >= _THRESHOLDS["churn_p1"]:
            return "P1"
        if prob >= _THRESHOLDS["churn_p2"]:
            return "P2"
        if prob >= _THRESHOLDS["churn_p3"]:
            return "P3"
        return "P4"

    df["priority_tier"] = df["churn_probability"].apply(_tier)

    # Risk factors (human-readable)
    def _risk_factors(row: pd.Series) -> str:
        factors = []
        if row.get("days_since_last_login", 0) > 30:
            factors.append("No login in 30+ days")
        if row.get("days_since_last_lead", 0) > 60:
            factors.append("No leads in 60+ days")
        if row.get("profile_views_30d", 0) < 10:
            factors.append("Very low views")
        if row.get("engagement_trend", 0) < -0.5:
            factors.append("Declining engagement")
        if row.get("days_until_renewal", 999) < 30:
            factors.append("Renewal approaching")
        return ", ".join(factors) if factors else "Stable"

    df["risk_factors"] = df.apply(_risk_factors, axis=1)

    # Recommended action
    def _action(row: pd.Series) -> str:
        tier = row.get("priority_tier", "P4")
        if tier == "P1":
            return "URGENT: Call within 24h"
        if tier == "P2":
            return "HIGH: Send re-engagement email + schedule call"
        if tier == "P3":
            return "MEDIUM: Include in monthly nurture"
        return "LOW: Standard nurture"

    df["recommended_action"] = df.apply(_action, axis=1)

    return df
