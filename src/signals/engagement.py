"""Engagement trend detection — separate from churn scoring."""

import pandas as pd


def detect_decline(stats: pd.DataFrame, threshold: float = -0.5) -> pd.DataFrame:
    """Flag suppliers with significant engagement decline.

    Returns a subset of suppliers where profile views dropped >50% vs previous month.
    """
    declining = stats[
        (stats["engagement_trend"] <= threshold)
        & (stats["profile_views_60d"] < stats["profile_views_60_90d"])
    ].copy()
    declining["signal_type"] = "engagement_decline"
    declining["signal_severity"] = declining["engagement_trend"].apply(
        lambda x: "severe" if x <= -0.75 else "moderate"
    )
    return declining


def detect_no_activity(stats: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Flag suppliers with zero logins in the last N days."""
    inactive = stats[stats["days_since_last_login"] > days].copy()
    inactive["signal_type"] = "no_activity"
    inactive["signal_severity"] = inactive["days_since_last_login"].apply(
        lambda x: "severe" if x > 60 else "moderate"
    )
    return inactive
