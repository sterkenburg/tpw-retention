"""Read lead/inquiry data from BigQuery.

Source tables (verified):
- tpw-ga4-bigquery.ga4_dataform_output.generate_lead (contact forms)
  Schema: company_id INTEGER, event_date DATE, category STRING,
          region STRING, engagement_time_seconds FLOAT, etc.

- tpw-ga4-bigquery.ga4_dataform_output.show_phone (phone reveals)
  Schema: profile_id INTEGER, event_date DATE, etc.
"""

import pandas as pd

from .client import query

_LEADS_TABLE = "tpw-ga4-bigquery.ga4_dataform_output.generate_lead"
_PHONE_TABLE = "tpw-ga4-bigquery.ga4_dataform_output.show_phone"


def get_last_90d() -> pd.DataFrame:
    """Get all lead events from the last 90 days."""
    sql = f"""
    SELECT
        CAST(company_id AS STRING) AS profile_id,
        event_date,
        category,
        COUNT(*) AS lead_count,
        COUNT(DISTINCT user_id) AS unique_inquirers,
        'contact_form' AS lead_type
    FROM `{_LEADS_TABLE}`
    WHERE event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
                         AND CURRENT_DATE()
      AND company_id IS NOT NULL
    GROUP BY company_id, event_date, category

    UNION ALL

    SELECT
        CAST(profile_id AS STRING) AS profile_id,
        event_date,
        CAST(NULL AS STRING) AS category,
        COUNT(*) AS lead_count,
        COUNT(DISTINCT user_id) AS unique_inquirers,
        'phone_reveal' AS lead_type
    FROM `{_PHONE_TABLE}`
    WHERE event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
                         AND CURRENT_DATE()
      AND profile_id IS NOT NULL
    GROUP BY profile_id, event_date, category
    """
    df = query(sql)
    if "event_date" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    return df


def get_contract_period_leads(suppliers_df: pd.DataFrame) -> pd.DataFrame:
    """Get total leads since each supplier's plan_start."""
    if suppliers_df.empty:
        return pd.DataFrame(columns=["profile_id", "contract_leads_total"])

    min_plan_start = suppliers_df["plan_start"].min()
    start_date = min_plan_start.strftime("%Y-%m-%d") if pd.notna(min_plan_start) else "2020-01-01"

    ids = [int(pid) for pid in suppliers_df["profile_id"].unique() if str(pid).isdigit()]
    if not ids:
        return pd.DataFrame(columns=["profile_id", "contract_leads_total"])

    id_list = ",".join(str(i) for i in ids)

    sql = f"""
    SELECT
        profile_id,
        event_date
    FROM (
        SELECT CAST(company_id AS STRING) AS profile_id, event_date
        FROM `{_LEADS_TABLE}`
        WHERE company_id IS NOT NULL
          AND event_date >= '{start_date}'
          AND CAST(company_id AS STRING) IN ({','.join(repr(str(i)) for i in ids)})

        UNION ALL

        SELECT CAST(profile_id AS STRING) AS profile_id, event_date
        FROM `{_PHONE_TABLE}`
        WHERE profile_id IS NOT NULL
          AND event_date >= '{start_date}'
          AND CAST(profile_id AS STRING) IN ({','.join(repr(str(i)) for i in ids)})
    )
    """
    df = query(sql)
    if df.empty:
        return pd.DataFrame(columns=["profile_id", "contract_leads_total"])

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    suppliers_df = suppliers_df[["profile_id", "plan_start"]].copy()
    suppliers_df["plan_start"] = pd.to_datetime(suppliers_df["plan_start"], errors="coerce")

    merged = df.merge(suppliers_df, on="profile_id", how="left")
    valid = merged[merged["event_date"] >= merged["plan_start"]]

    counts = valid.groupby("profile_id").size().rename("contract_leads_total").reset_index()
    return counts


def get_by_supplier(profile_id: str, days: int = 30) -> pd.DataFrame:
    """Get lead events for a specific supplier in the last N days."""
    sql = f"""
    SELECT
        CAST(company_id AS STRING) AS profile_id,
        event_date,
        category,
        user_id,
        region,
        'contact_form' AS lead_type
    FROM `{_LEADS_TABLE}`
    WHERE company_id = {int(profile_id)}
      AND event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                         AND CURRENT_DATE()

    UNION ALL

    SELECT
        CAST(profile_id AS STRING) AS profile_id,
        event_date,
        NULL AS category,
        user_id,
        NULL AS region,
        'phone_reveal' AS lead_type
    FROM `{_PHONE_TABLE}`
    WHERE profile_id = {int(profile_id)}
      AND event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                         AND CURRENT_DATE()

    ORDER BY event_date DESC
    """
    df = query(sql)
    if "event_date" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    return df
