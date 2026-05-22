"""Aggregate per-supplier statistics from raw data. One table to rule them all."""

from datetime import datetime

import pandas as pd


def calculate(
    suppliers: pd.DataFrame,
    activity: pd.DataFrame,
    leads: pd.DataFrame,
    contract_activity: pd.DataFrame | None = None,
    contract_leads: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build supplier_stats_daily from raw data.

    Returns one row per active supplier with all metrics needed by
    dashboard, emails, churn scoring, and notifications.
    """
    today = pd.Timestamp.now().normalize()
    df = suppliers.copy()

    # --- GA4 activity (last 60d) ---
    activity_60d = activity[activity["event_date"] >= today - pd.Timedelta(days=60)]
    views_60d = (
        activity_60d.groupby("profile_id")
        .size()
        .rename("profile_views_60d")
    )

    # GA4 activity (previous 60-90d) for trend
    activity_60_90d = activity[
        (activity["event_date"] >= today - pd.Timedelta(days=90))
        & (activity["event_date"] < today - pd.Timedelta(days=60))
    ]
    views_60_90d = (
        activity_60_90d.groupby("profile_id")
        .size()
        .rename("profile_views_60_90d")
    )

    # --- Leads (last 60d) ---
    leads_60d = leads[leads["event_date"] >= today - pd.Timedelta(days=60)]
    lead_counts = (
        leads_60d.groupby("profile_id")
        .size()
        .rename("leads_60d")
    )

    # --- Merge ---
    df = df.set_index("profile_id")
    df = df.join(views_60d, how="left")
    df = df.join(views_60_90d, how="left")
    df = df.join(lead_counts, how="left")
    df = df.fillna(0).reset_index()

    # --- Contract-period totals ---
    if contract_activity is not None and not contract_activity.empty:
        contract_activity = contract_activity.set_index("profile_id")["contract_views_total"]
        df = df.set_index("profile_id").join(contract_activity, how="left").reset_index()
    else:
        df["contract_views_total"] = 0

    if contract_leads is not None and not contract_leads.empty:
        contract_leads = contract_leads.set_index("profile_id")["contract_leads_total"]
        df = df.set_index("profile_id").join(contract_leads, how="left").reset_index()
    else:
        df["contract_leads_total"] = 0

    df["contract_views_total"] = df.get("contract_views_total", 0).fillna(0).astype(int)
    df["contract_leads_total"] = df.get("contract_leads_total", 0).fillna(0).astype(int)

    # --- Category benchmarks (avg last 60d) ---
    category_avgs = (
        df.groupby("category")
        .agg({"profile_views_60d": "mean", "leads_60d": "mean"})
        .reset_index()
    )
    category_avgs.columns = [
        "category",
        "category_avg_views_60d",
        "category_avg_leads_60d",
    ]
    df = df.merge(category_avgs, on="category", how="left")

    # --- Derived metrics ---
    df["profile_views_60d"] = df["profile_views_60d"].astype(int)
    df["profile_views_60_90d"] = df["profile_views_60_90d"].astype(int)
    df["leads_60d"] = df["leads_60d"].astype(int)

    # Engagement trend: % change vs previous 60d period
    df["engagement_trend"] = (
        (df["profile_views_60d"] - df["profile_views_60_90d"])
        / df["profile_views_60_90d"].replace(0, pd.NA)
    ).fillna(0)

    # Days until renewal
    df["plan_end"] = pd.to_datetime(df["plan_end"], errors="coerce")
    df["days_until_renewal"] = (df["plan_end"] - today).dt.days

    # Days since last lead (if any in 90d window)
    last_lead = (
        leads.groupby("profile_id")["event_date"]
        .max()
        .rename("last_lead_date")
    )
    df = df.set_index("profile_id").join(last_lead, how="left").reset_index()
    df["days_since_last_lead"] = (today - pd.to_datetime(df["last_lead_date"], errors="coerce")).dt.days
    df["days_since_last_lead"] = df["days_since_last_lead"].fillna(999).astype(int)

    # Last login — approximate from GA4
    last_login = (
        activity.groupby("profile_id")["event_date"]
        .max()
        .rename("last_activity_date")
    )
    df = df.set_index("profile_id").join(last_login, how="left").reset_index()
    df["days_since_last_login"] = (today - pd.to_datetime(df["last_activity_date"], errors="coerce")).dt.days
    df["days_since_last_login"] = df["days_since_last_login"].fillna(999).astype(int)

    # Meta
    df["stats_date"] = today

    # Column order
    cols = [
        "profile_id",
        "profile_name",
        "phone",
        "category",
        "plan_name",
        "plan_value",
        "plan_start",
        "plan_end",
        "days_until_renewal",
        "business_status",
        "account_manager",
        "profile_views_60d",
        "profile_views_60_90d",
        "engagement_trend",
        "leads_60d",
        "days_since_last_lead",
        "days_since_last_login",
        "contract_views_total",
        "contract_leads_total",
        "category_avg_views_60d",
        "category_avg_leads_60d",
        "renewal_status",
        "num_paid_plans_before",
        "stats_date",
    ]
    return df[[c for c in cols if c in df.columns]]
