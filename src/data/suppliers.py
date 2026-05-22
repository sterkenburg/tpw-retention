"""Read supplier (business development) data from BigQuery.

Joins business_development with profiles for phone numbers.

Source tables:
  tpw-ga4-bigquery.churn_prediction.business_development
  tpw-ga4-bigquery.churn_prediction.profiles
"""

import pandas as pd

from .client import query

_BUSINESS_TABLE = "tpw-ga4-bigquery.churn_prediction.business_development"
_PROFILES_TABLE = "tpw-ga4-bigquery.churn_prediction.profiles"


def get_current() -> pd.DataFrame:
    """Get all currently active paid suppliers with contact info."""
    sql = f"""
    SELECT
        b.profile_id,
        b.profile_name,
        b.category,
        b.plan_name,
        b.plan_value,
        b.plan_start,
        b.plan_end,
        b.business_status,
        b.account_manager,
        b.num_paid_plans_before,
        b.next_plan_comparison,
        b.converted_lead,
        p.profile_telephone AS phone,
        -- Already renewed = has another paid plan that ends before this one
        EXISTS(
            SELECT 1
            FROM `{_BUSINESS_TABLE}` b2
            WHERE b2.profile_id = b.profile_id
              AND b2.plan_name != 'Gratis'
              AND b2.plan_end < b.plan_end
        ) AS already_renewed
    FROM `{_BUSINESS_TABLE}` b
    LEFT JOIN `{_PROFILES_TABLE}` p
        ON b.profile_id = p.profile_id
    WHERE b.plan_end >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      AND b.plan_name != 'Gratis'
      AND b.profile_id IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY b.profile_id
        ORDER BY b.plan_end DESC
    ) = 1
    """
    df = query(sql)
    for col in ["plan_start", "plan_end"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["profile_id"] = df["profile_id"].astype(str)
    return df


def get_by_id(profile_id: str) -> pd.DataFrame:
    """Get full history for a single supplier."""
    sql = f"""
    SELECT *
    FROM `{_BUSINESS_TABLE}`
    WHERE profile_id = {int(profile_id)}
    ORDER BY plan_start DESC
    """
    df = query(sql)
    for col in ["plan_start", "plan_end"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["profile_id"] = df["profile_id"].astype(str)
    return df
