"""Renewal outcomes — the ended-terms feed (doc 29 §2.5).

Every completed paid term is a renewal decision. This builds `outcomes`: one row
per ended term in the window (default 24 months), labelled with the decision:

  renewed       a later paid plan starts within suppliers.RENEWAL_GRACE_DAYS of
                plan_end (a following Gratis plan is a downgrade = churn)
  pending       not renewed AND the term ended inside the grace window — the
                decision isn't final yet; endpoint reads must filter these out
  experiment_id / arm
                attached from cohort_assignment ONLY when the term ended on/after
                the supplier's enrolment (plan_end >= assigned_at) — a renewal
                decision made before enrolment must not inherit an arm

Consumers: the Stage-2 renewal endpoint (renewed vs control, doc 18), the doc-24
recall backtest (rows with experiment_id NULL are plain labels), and winback
analysis. The table is small and rebuilt in full on every run (idempotent).
"""

import os

import pandas as pd
import yaml

from data import client, suppliers
from signals import targeting

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_TABLE = _CONFIG["tables"]["outcomes"]
_COHORT_TABLE = _CONFIG["tables"]["cohort_assignment"]

_OUTPUT_COLUMNS = [
    "profile_id", "profile_name", "category", "segment", "plan_name",
    "plan_value", "plan_start", "plan_end", "term_months", "first_term",
    "num_paid_plans_before", "renewed", "pending", "next_paid_start",
    "days_since_end", "experiment_id", "arm", "computed_at",
]


def _enrolments() -> pd.DataFrame:
    """(profile_id, experiment_id, arm, assigned_at) for every enrolment."""
    if not client.table_exists(_COHORT_TABLE):
        return pd.DataFrame(columns=["profile_id", "experiment_id", "arm", "assigned_at"])
    df = client.query(
        f"SELECT profile_id, experiment_id, arm, assigned_at "
        f"FROM `{client.PROJECT_ID}.{client.DATASET}.{_COHORT_TABLE}`"
    )
    df["profile_id"] = df["profile_id"].astype(str)
    df["assigned_at"] = (
        pd.to_datetime(df["assigned_at"], utc=True).dt.tz_localize(None).dt.normalize()
    )
    return df


def calculate(months_back: int = 24) -> pd.DataFrame:
    """One labelled row per ended paid term (× post-enrolment experiment, if any)."""
    terms = suppliers.get_ended_terms(months_back=months_back)
    terms["segment"] = terms["category"].apply(targeting._segment)
    terms["first_term"] = terms["num_paid_plans_before"].fillna(0).astype(int) == 0
    terms["term_months"] = ((terms["plan_end"] - terms["plan_start"]).dt.days / 30.0).round(1)
    terms["pending"] = ~terms["renewed"] & (
        terms["days_since_end"] <= suppliers.RENEWAL_GRACE_DAYS
    )

    df = terms.merge(_enrolments(), on="profile_id", how="left")
    # An arm applies only to renewal decisions made under the experiment: null out
    # enrolments for terms that ended before assignment, then collapse duplicates
    # (a term can otherwise fan out across a supplier's multiple enrolments).
    pre_enrolment = df["experiment_id"].notna() & (df["plan_end"] < df["assigned_at"])
    df.loc[pre_enrolment, ["experiment_id", "arm"]] = pd.NA
    df = df.drop(columns=["assigned_at"])
    df = df.drop_duplicates(subset=["profile_id", "plan_start", "plan_end", "experiment_id", "arm"])

    df["computed_at"] = pd.Timestamp.now()
    return df[_OUTPUT_COLUMNS].copy()


def build(months_back: int = 24) -> pd.DataFrame:
    """Calculate and fully refresh the `outcomes` table."""
    df = calculate(months_back=months_back)
    client.write(df, _TABLE, if_exists="replace")
    return df
