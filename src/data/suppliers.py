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
    """Get all currently active paid suppliers with contact info.

    Excludes suppliers whose latest plan is Gratis (churned).
    Flags suppliers with a future Gratis plan as 'will_churn'.
    Flags suppliers with a future paid plan as 'already_renewed'.
    """
    sql = f"""
    WITH ordered_plans AS (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY profile_id ORDER BY plan_end DESC) AS rn_end,
            ROW_NUMBER() OVER (PARTITION BY profile_id ORDER BY plan_start DESC) AS rn_start
        FROM `{_BUSINESS_TABLE}`
        WHERE profile_id IS NOT NULL
    ),
    latest_plan AS (
        SELECT * FROM ordered_plans WHERE rn_end = 1
    ),
    next_plan AS (
        SELECT
            profile_id,
            plan_name AS next_plan_name,
            plan_start AS next_plan_start,
            plan_end AS next_plan_end
        FROM ordered_plans
        WHERE plan_start > CURRENT_DATE()
          AND rn_start = 1
    )
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
        np.next_plan_name,
        np.next_plan_start,
        CASE
            WHEN np.next_plan_name = 'Gratis' THEN 'will_churn'
            WHEN np.next_plan_name IS NOT NULL AND np.next_plan_name != 'Gratis' THEN 'already_renewed'
            WHEN EXISTS(
                SELECT 1 FROM `{_BUSINESS_TABLE}` b2
                WHERE b2.profile_id = b.profile_id
                  AND b2.plan_name != 'Gratis'
                  AND b2.plan_end < b.plan_end
            ) THEN 'already_renewed'
            ELSE 'active'
        END AS renewal_status
    FROM latest_plan b
    LEFT JOIN `{_PROFILES_TABLE}` p
        ON b.profile_id = p.profile_id
    LEFT JOIN next_plan np
        ON b.profile_id = np.profile_id
    WHERE b.plan_name != 'Gratis'
      AND b.plan_end >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
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
