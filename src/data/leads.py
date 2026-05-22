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

    values = []
    for _, row in suppliers_df.iterrows():
        pid = int(row["profile_id"])
        plan_start = row["plan_start"].strftime("%Y-%m-%d") if pd.notna(row["plan_start"]) else "1900-01-01"
        values.append(f"STRUCT({pid} AS profile_id, DATE('{plan_start}') AS plan_start)")

    if not values:
        return pd.DataFrame(columns=["profile_id", "contract_leads_total"])

    values_str = ",\n        ".join(values)

    sql = f"""
    WITH supplier_periods AS (
        SELECT * FROM UNNEST([
            {values_str}
        ])
    ),
    all_leads AS (
        SELECT company_id AS profile_id, event_date
        FROM `{_LEADS_TABLE}`
        WHERE company_id IS NOT NULL

        UNION ALL

        SELECT profile_id, event_date
        FROM `{_PHONE_TABLE}`
        WHERE profile_id IS NOT NULL
    )
    SELECT
        CAST(l.profile_id AS STRING) AS profile_id,
        COUNT(*) AS contract_leads_total
    FROM all_leads l
    INNER JOIN supplier_periods s
        ON l.profile_id = s.profile_id
    WHERE l.event_date >= s.plan_start
    GROUP BY profile_id
    """
    return query(sql)


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
