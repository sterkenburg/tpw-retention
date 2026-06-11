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

# A term counts as renewed when the next paid plan starts within this many days
# of plan_end — renewals often process late, and a premature 'churned' label is
# worse than a short wait. Terms still inside this window with no successor are
# 'pending' in outcomes, not churned.
RENEWAL_GRACE_DAYS = 45


def _email_sql() -> tuple[str, str]:
    """(select clause, join clause) for the optional supplier-email source."""
    if _EMAIL_TABLE and _EMAIL_COLUMN:
        return (
            f"em.{_EMAIL_COLUMN} AS email",
            f"""
    LEFT JOIN `{_EMAIL_TABLE}` em
        ON CAST(b.profile_id AS STRING) = CAST(em.profile_id AS STRING)""",
        )
    return "CAST(NULL AS STRING) AS email", ""


def get_current() -> pd.DataFrame:
    """Get all currently active paid suppliers with contact info.

    Excludes suppliers whose latest plan is Gratis (churned).
    Flags suppliers with a future Gratis plan as 'will_churn'.
    Flags suppliers with a future paid plan as 'already_renewed'.

    Includes an `email` column if a supplier email source is configured
    (sources.supplier_email_table / supplier_email_column); otherwise `email`
    is NULL for every row and suppliers are not emailable.
    """
    # Optional email join, isolated so the rest of the query is unchanged
    # whether or not an email source is configured.
    email_select, email_join = _email_sql()

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
            WHEN np.next_plan_name IS NOT NULL
                 AND np.next_plan_name != 'Gratis' THEN 'already_renewed'
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


def get_ended_terms(months_back: int = 24) -> pd.DataFrame:
    """Completed paid terms — one renewal decision per row (doc 29 §2.5).

    Every paid (non-Gratis) plan whose plan_end falls in the last `months_back`
    months, labelled with the decision outcome:

      renewed          TRUE iff a later paid plan starts within
                       RENEWAL_GRACE_DAYS of plan_end (a following Gratis plan
                       is a downgrade, i.e. churn — only paid plans count)
      next_paid_start  start of the next paid plan, if any
      days_since_end   days from plan_end to today (≤ grace + not renewed ⇒
                       the decision is still pending, not churn)

    Feeds the `outcomes` table (Stage-2 renewal endpoint + doc-24 backtest
    labels) and winback analysis.
    """
    sql = f"""
    WITH paid_plans AS (
        SELECT
            profile_id, profile_name, category, plan_name, plan_value,
            plan_start, plan_end, num_paid_plans_before
        FROM `{_BUSINESS_TABLE}`
        WHERE profile_id IS NOT NULL
          AND plan_name != 'Gratis'
    ),
    with_next AS (
        SELECT
            *,
            LEAD(plan_start) OVER (
                PARTITION BY profile_id ORDER BY plan_start, plan_end
            ) AS next_paid_start
        FROM paid_plans
    )
    SELECT
        profile_id, profile_name, category, plan_name, plan_value,
        plan_start, plan_end, num_paid_plans_before, next_paid_start,
        COALESCE(
            DATE_DIFF(next_paid_start, plan_end, DAY) <= {RENEWAL_GRACE_DAYS},
            FALSE
        ) AS renewed,
        DATE_DIFF(CURRENT_DATE(), plan_end, DAY) AS days_since_end
    FROM with_next
    WHERE plan_end < CURRENT_DATE()
      AND plan_end >= DATE_SUB(CURRENT_DATE(), INTERVAL {int(months_back)} MONTH)
    ORDER BY plan_end
    """
    df = query(sql)
    for col in ["plan_start", "plan_end", "next_paid_start"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["profile_id"] = df["profile_id"].astype(str)
    return df


def get_lapsed(months_back: int = 6) -> pd.DataFrame:
    """Recently-lapsed suppliers — the winback pool (doc 29 §2.5).

    A supplier is lapsed when their LATEST paid (non-Gratis) plan ended more
    than 30 days ago (mirroring get_current()'s 30-day still-current grace, so
    the two feeds never overlap) with no later paid plan. Default window matches
    LEVERS['winback'] params.max_lapsed_months. Suppliers who downgraded to
    Gratis surface here too, once their paid plan_end passes the 30-day line.

    Same column shape as get_current(), with renewal_status='lapsed' — which is
    outside targeting.RETAINED_STATUSES, so these rows route to the journey
    `lapsed` stage and the winback experiment's `churned` eligibility.
    """
    email_select, email_join = _email_sql()
    sql = f"""
    WITH paid_plans AS (
        SELECT *
        FROM `{_BUSINESS_TABLE}`
        WHERE profile_id IS NOT NULL
          AND plan_name != 'Gratis'
    ),
    latest_paid AS (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY profile_id ORDER BY plan_end DESC) AS rn
        FROM paid_plans
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
        CAST(NULL AS STRING) AS next_plan_name,
        CAST(NULL AS DATE) AS next_plan_start,
        'lapsed' AS renewal_status
    FROM latest_paid b
    LEFT JOIN `{_PROFILES_TABLE}` p
        ON b.profile_id = p.profile_id{email_join}
    WHERE b.rn = 1
      AND b.plan_end < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      AND b.plan_end >= DATE_SUB(CURRENT_DATE(), INTERVAL {int(months_back)} MONTH)
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
