"""Read GA4 engagement data from BigQuery.

Primary source: tpw-ga4-bigquery.ga4_dataform_output.bedrijven_pageview_events
Schema (verified):
  event_date: DATE
  profile_id: INTEGER
  page_location: STRING
  page_title: STRING
  engagement_time_msec: INTEGER
  source: STRING
  medium: STRING
  device_category: STRING
"""

import pandas as pd

from .client import query

_PROCESSED_TABLE = "tpw-ga4-bigquery.ga4_dataform_output.bedrijven_pageview_events"


def get_last_90d() -> pd.DataFrame:
    """Get pageview events for suppliers in the last 90 days."""
    sql = f"""
    SELECT
        CAST(profile_id AS STRING) AS profile_id,
        event_date,
        page_location,
        page_title,
        engagement_time_msec
    FROM `{_PROCESSED_TABLE}`
    WHERE event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
                         AND CURRENT_DATE()
      AND profile_id IS NOT NULL
      AND profile_id > 0
    """
    df = query(sql)
    if "event_date" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    return df


def get_profile_views(profile_ids: list[str], days: int = 30) -> pd.DataFrame:
    """Get profile view counts per supplier for the last N days."""
    id_list = ",".join(f"{int(pid)}" for pid in profile_ids)
    sql = f"""
    SELECT
        CAST(profile_id AS STRING) AS profile_id,
        COUNT(*) AS view_count
    FROM `{_PROCESSED_TABLE}`
    WHERE event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                         AND CURRENT_DATE()
      AND profile_id IN ({id_list})
    GROUP BY profile_id
    """
    return query(sql)
