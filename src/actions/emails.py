"""Email sending via SendGrid (or swap for Mailchimp/HubSpot).

Templates are rendered with Jinja2 from src/templates/emails/.

Safety model (D2):
  - A master dry-run switch (config email.dry_run, overridable with the env var
    EMAIL_DRY_RUN) gates ALL real sends. While dry-run is on, send() logs what
    *would* go out and returns False without calling SendGrid.
  - Dedup is enforced upstream via the email_log table: recent_sends() reports
    which (profile_id, flow) pairs were emailed inside each flow's window, and
    log_sends() records what actually went out (or would have, in dry-run).
"""

import os
from pathlib import Path

import httpx
import yaml
from jinja2 import Environment, FileSystemLoader

from .flows import EmailAction

# --- Config --------------------------------------------------------------
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_EMAIL_CFG = _CONFIG.get("email", {})
_SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
_FROM_EMAIL = _EMAIL_CFG.get("from_address", "partners@theperfectwedding.nl")
_FROM_NAME = _EMAIL_CFG.get("from_name", "ThePerfectWedding")
_DEDUP_DAYS = _EMAIL_CFG.get(
    "dedup_days",
    {"monthly_results": 25, "re_engagement": 14, "renewal_prep": 21},
)


def is_dry_run() -> bool:
    """Master safety switch. Env EMAIL_DRY_RUN overrides config email.dry_run."""
    env = os.environ.get("EMAIL_DRY_RUN")
    if env is not None:
        return env.strip().lower() not in ("false", "0", "no")
    return bool(_EMAIL_CFG.get("dry_run", True))


# --- Jinja2 --------------------------------------------------------------
_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"
_jinja = Environment(loader=FileSystemLoader(_TEMPLATE_DIR), autoescape=True)

# Maps each flow to its template file. Adding a flow = add a template + an entry.
_FLOW_TEMPLATES = {
    "monthly_results": "monthly_results.html",
    "re_engagement": "re_engagement.html",
    "renewal_prep": "renewal_prep.html",
}


def _render(action: EmailAction) -> str:
    """Render the HTML body for an action, mapping its payload to template vars.

    The mapping adapts the semantic payload from flows.py to the variables each
    template currently expects. Fields the current stats pipeline does not yet
    produce (e.g. photo_views, contact_clicks) default to 0 until D4 enriches
    both templates and stats.
    """
    template = _jinja.get_template(_FLOW_TEMPLATES[action.flow])
    p = action.payload

    if action.flow == "monthly_results":
        ctx = {
            "name": action.name,
            "month": p.get("month", ""),
            "profile_views": p.get("profile_views", 0),
            "photo_views": 0,
            "contact_clicks": 0,
            "quote_requests": p.get("leads", 0),
            "benchmark_views": p.get("benchmark_views", 250),
            "estimated_value": p.get("estimated_value", 0),
        }
    elif action.flow == "re_engagement":
        ctx = {
            "name": action.name,
            "category": p.get("category", ""),
            "days_since_lead": p.get("days_since_lead", 0),
        }
    elif action.flow == "renewal_prep":
        ctx = {
            "name": action.name,
            "days_until_renewal": p.get("days_until_renewal", 0),
            "total_views": p.get("total_views", 0),
            "total_leads": p.get("total_leads", 0),
            "estimated_value": p.get("estimated_value", 0),
        }
    else:
        ctx = {"name": action.name}

    return template.render(**ctx)


def _send(to: str, subject: str, html: str) -> bool:
    """Send one email via the SendGrid API. Returns True on a 202 accept."""
    if not _SENDGRID_API_KEY:
        print(f"[email] No SendGrid key. Would send to {to}: {subject}")
        return False

    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": _FROM_EMAIL, "name": _FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }

    try:
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {_SENDGRID_API_KEY}"},
            json=payload,
            timeout=30,
        )
        return response.status_code == 202
    except Exception as e:
        print(f"[email] Failed to send to {to}: {e}")
        return False


def send(action: EmailAction) -> bool:
    """Send a single flow email. No-op (returns False) while dry-run is on.

    Returns True only when a real send succeeded.
    """
    if is_dry_run():
        print(f"[email:dry-run] {action.flow} → {action.email}: {action.subject}")
        return False
    html = _render(action)
    return _send(action.email, action.subject, html)


# --- email_log (dedup + audit) ------------------------------------------
def recent_sends() -> set[tuple[str, str]]:
    """Return (profile_id, flow) pairs emailed inside each flow's dedup window.

    Reads the email_log table. Returns an empty set if the table is missing or
    unreadable (so a fresh environment simply has no dedup history yet).
    """
    from data import client  # lazy import: keeps module importable off-pipeline

    if not client.table_exists("email_log"):
        return set()

    # One condition per flow so each respects its own window.
    conditions = " OR ".join(
        f"(email_type = '{flow}' AND sent_at >= "
        f"TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {int(days)} DAY))"
        for flow, days in _DEDUP_DAYS.items()
    )
    sql = f"""
        SELECT DISTINCT CAST(profile_id AS STRING) AS profile_id, email_type
        FROM `{client.PROJECT_ID}.{client.DATASET}.email_log`
        WHERE {conditions}
    """
    try:
        df = client.query(sql)
    except Exception as e:
        print(f"[email] Could not read email_log for dedup: {e}")
        return set()
    if df.empty:
        return set()
    return set(zip(df["profile_id"].astype(str), df["email_type"].astype(str), strict=False))


def log_sends(sent_actions: list[EmailAction]) -> None:
    """Append one email_log row per email that was REALLY sent.

    Only real sends are logged here, because email_log drives dedup
    (recent_sends): in dry-run nothing sends, so nothing is logged and previews
    stay stable across re-runs. Every attempt (dry-run included) is still
    captured in actions_log by the pipeline. `opened`/`clicked` start False and
    are updated later by webhook events.
    """
    from datetime import datetime

    import pandas as pd

    from data import client

    if not sent_actions:
        return
    rows = [
        {
            "profile_id": a.profile_id,
            "sent_at": datetime.now(),
            "email_type": a.flow,
            "template": _FLOW_TEMPLATES.get(a.flow, ""),
            "opened": False,
            "clicked": False,
            "created_at": datetime.now(),
        }
        for a in sent_actions
    ]
    client.write(pd.DataFrame(rows), "email_log", if_exists="append")
