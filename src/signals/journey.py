"""WS-B+ — supplier lifecycle stage + next-best-action (the journey layer).

Turns the flat lever catalog (`directives.LEVERS`) into an ordered JOURNEY. Each
supplier is placed in a single lifecycle STAGE derived from columns already in
`supplier_targeting` (no new data), and each stage maps to the levers that should
fire there — the WHEN the directive layer lacked (docs/strategy/28 §1, §4).

Stages (priority order — first match wins):
  lapsed          renewal_status not retained (churned)     → winback
  onboarding      active, first_term (first paid term)      → onboarding
  renewal_window  active/will_churn, 0 ≤ days_until_renewal ≤ N → save: boost + email
  at_risk         active/will_churn, at_risk_tier in {P1,P2}  → full stage-1 exposure set
  healthy         retained / low-risk (incl. renewed)       → monitor (no directive)

`already_renewed` = retained for a *future* term → `healthy` (monitor). `will_churn`
= paid term running with a scheduled Gratis downgrade → the SAVE population: it
routes to renewal_window/at_risk (never onboarding/healthy/lapsed — they only become
winback after the term actually ends). Only genuinely churned statuses are the
winback pool (targeting.RETAINED_STATUSES).

Read-only: a derived view over targeting, not a written table (yet). The stage→lever
map references `directives.LEVERS` so gating/params stay single-source. A persisted
`supplier_journey` table + true event triggers are the next increment (doc 28 §4).
"""

import os

import pandas as pd
import yaml

from actions import directives
from data import client
from signals.targeting import RETAINED_STATUSES

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_TARGETING_TABLE = _CONFIG["tables"]["supplier_targeting"]
# Renewal-decision window (days before plan_end) — single-sourced from config.
RENEWAL_WINDOW_DAYS = _CONFIG.get("thresholds", {}).get("renewal_days", 60)

# Stage → recommended lever types (keys in directives.LEVERS). 'healthy' = monitor
# (no directive). The lever's experiment scoping + gating still apply downstream;
# this is the *recommendation*, the directive layer is the system of record.
STAGE_LEVERS = {
    "lapsed":         ["winback"],
    "onboarding":     ["onboarding"],
    "renewal_window": ["boost", "email"],
    "at_risk":        ["boost", "optimize", "newsletter", "email"],
    "healthy":        [],
}

# Display order: roughly the lifecycle path a supplier travels.
STAGE_ORDER = ["onboarding", "healthy", "at_risk", "renewal_window", "lapsed"]


def stage(row) -> str:
    """Place one targeting row in a single lifecycle stage (priority order)."""
    status = str(row.get("renewal_status", "active"))
    if status not in RETAINED_STATUSES:   # churned/unknown → winback pool
        return "lapsed"
    if status == "already_renewed":       # retained for a future term
        return "healthy"
    # 'active' and 'will_churn' (paid term running, Gratis downgrade already
    # scheduled) flow through the live stages: will_churn is the SAVE population
    # — renewal_window or at_risk (its +0.40 score guarantees ≥ P2), never a
    # welcome sequence, even for first-termers.
    if bool(row.get("first_term", False)) and status == "active":
        return "onboarding"
    days = row.get("days_until_renewal")
    if days is not None and pd.notna(days) and 0 <= days <= RENEWAL_WINDOW_DAYS:
        return "renewal_window"
    if str(row.get("at_risk_tier", "")) in ("P1", "P2"):
        return "at_risk"
    return "healthy"


def classify(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Add `journey_stage` to the latest targeting snapshot (or a supplied df)."""
    if df is None:
        df = client.query(
            f"SELECT * FROM `{client.PROJECT_ID}.{client.DATASET}.{_TARGETING_TABLE}`"
        )
        if "stats_date" in df.columns and len(df):
            df = df[df["stats_date"] == df["stats_date"].max()]
    df = df.copy()
    df["journey_stage"] = df.apply(stage, axis=1)
    return df


def actions_for(stage_name: str) -> list[dict]:
    """Recommended levers for a stage, each with its current gate status."""
    out = []
    for typ in STAGE_LEVERS.get(stage_name, []):
        spec = directives.LEVERS[typ]
        status, note = directives.lever_status(typ)
        out.append(
            {"type": typ, "channel": spec["channel"], "status": status, "note": note}
        )
    return out
