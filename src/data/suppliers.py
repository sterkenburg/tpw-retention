"""Read supplier (business development) data from BigQuery.

Joins business_development with profiles for phone numbers.

Source tables:
  tpw-ga4-bigquery.churn_prediction.business_development
  tpw-ga4-bigquery.churn_prediction.profiles
"""

import os

import pandas as pd
import yaml

from .client import query

_BUSINESS_TABLE = "tpw-ga4-bigquery.churn_prediction.business_development"
_PROFILES_TABLE = "tpw-ga4-bigquery.churn_prediction.profiles"

# --- Optional supplier email source (D1) ---------------------------------
# There is no email column in the business/profiles tables yet. When an email
# feed becomes available, configure it in config/settings.yaml under
# sources.supplier_email_table / supplier_email_column and it is joined in
# automatically. Until then, `email` is NULL and suppliers are not emailable.
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _SOURCES = yaml.safe_load(_f).get("sources", {})
_EMAIL_TABLE = _SOURCES.get("supplier_email_table") or ""
_EMAIL_COLUMN = _SOURCES.get("supplier_email_column") or ""


def get_current() -> pd.DataFrame:
    """Get all currently active paid suppliers with contact info.

    Excludes suppliers whose latest plan is Gratis (churned).
    Flags suppliers with a future Gratis plan as 'will_churn'.
    Flags suppliers with a future paid plan as 'already_renewed'.

    Includes an `email` column if a supplier email source is configured
    (sources.supplier_email_table / supplier_email_column); otherwise `email`
    is NULL for every row and suppliers are not emailable.
    """
    # Build the optional email join. Keep it isolated so the rest of the query
    # is unchanged whether or not an email source is configured.
    if _EMAIL_TABLE and _EMAIL_COLUMN:
        email_select = f"em.{_EMAIL_COLUMN} AS email"
        email_join = f"""
    LEFT JOIN `{_EMAIL_TABLE}` em
        ON CAST(b.profile_id AS STRING) = CAST(em.profile_id AS STRING)"""
    else:
        email_select = "CAST(NULL AS STRING) AS email"
        email_join = ""

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
        {email_select},
        np.next_plan_name,
        np.next_plan_start,
        CASE
            WHEN np.next_plan_name = 'Gratis' THEN 'will_churn'
            WHEN np.next_plan_name IS NOT NULL AND np.next_plan_name != 'Gratis' THEN 'already_renewed'
            ELSE 'active'
        END AS renewal_status
    FROM latest_plan b
    LEFT JOIN `{_PROFILES_TABLE}` p
        ON b.profile_id = p.profile_id
    LEFT JOIN next_plan np
        ON b.profile_id = np.profile_id{email_join}
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
