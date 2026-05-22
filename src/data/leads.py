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
