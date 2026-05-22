"""Email sending via SendGrid (or swap for Mailchimp/HubSpot).

All templates are rendered with Jinja2 from src/templates/emails/
"""

import os
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader

_SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
_FROM_EMAIL = "leveranciers@theperfectwedding.nl"
_FROM_NAME = "ThePerfectWedding"

# Jinja2 setup
_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"
_jinja = Environment(loader=FileSystemLoader(_TEMPLATE_DIR), autoescape=True)


def _send(to: str, subject: str, html: str) -> bool:
    """Send email via SendGrid API."""
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


def send_monthly_results(
    to: str,
    name: str,
    stats: dict,
) -> bool:
    """Send monthly results email."""
    template = _jinja.get_template("monthly_results.html")
    html = template.render(
        name=name,
        month=stats.get("month", ""),
        profile_views=stats.get("profile_views_60d", 0),
        photo_views=stats.get("photo_views_30d", 0),
        contact_clicks=stats.get("contact_clicks_30d", 0),
        quote_requests=stats.get("leads_60d", 0),
        estimated_value=stats.get("estimated_value", 0),
        benchmark_views=stats.get("benchmark_views_top10pct", 250),
        trend_pct=int(stats.get("engagement_trend", 0) * 100),
    )
    subject = f"Je ThePerfectWedding resultaten voor {stats.get('month', 'deze maand')}"
    return _send(to, subject, html)


def send_re_engagement(
    to: str,
    name: str,
    category: str,
    days_since_lead: int,
) -> bool:
    """Send re-engagement email to suppliers with no recent leads."""
    template = _jinja.get_template("re_engagement.html")
    html = template.render(
        name=name,
        category=category,
        days_since_lead=days_since_lead,
    )
    subject = "Je profiel is bekeken — hier is waarom er (nog) geen aanvraag is"
    return _send(to, subject, html)


def send_renewal_prep(
    to: str,
    name: str,
    plan_value: float,
    days_until_renewal: int,
    yearly_stats: dict,
) -> bool:
    """Send renewal preparation email."""
    template = _jinja.get_template("renewal_prep.html")
    html = template.render(
        name=name,
        days_until_renewal=days_until_renewal,
        total_views=yearly_stats.get("total_views", 0),
        total_leads=yearly_stats.get("total_leads", 0),
        estimated_value=yearly_stats.get("estimated_value", 0),
    )
    subject = f"Je abonnement loopt af over {days_until_renewal} dagen"
    return _send(to, subject, html)
