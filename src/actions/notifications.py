"""Instant lead notifications — email + SMS when a couple contacts a supplier.

Triggered by webhook or event, not by daily pipeline.
"""

import os
from datetime import datetime

import httpx

_MESSAGEBIRD_API_KEY = os.environ.get("MESSAGEBIRD_API_KEY", "")
_SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
_FROM_EMAIL = "leveranciers@theperfectwedding.nl"


def send_instant_lead_email(
    to: str,
    supplier_name: str,
    couple_name: str,
    event_date: str | None,
    guest_count: int | None,
    region: str | None,
    message: str | None,
    lead_number: int,
    profile_views: int,
) -> bool:
    """Send instant email notification for a new lead."""
    if not _SENDGRID_API_KEY:
        print(f"[notify] Would email {to} about new lead from {couple_name}")
        return False

    subject = f"🔔 Nieuwe lead — {couple_name} is geïnteresseerd"

    event_str = event_date or "Nog niet bekend"
    guests_str = f"{guest_count}" if guest_count else "Nog niet bekend"
    region_str = region or "Nog niet bekend"
    message_str = f'"{message}"' if message else "Geen bericht"

    html = f"""
    <p>Hi {supplier_name},</p>
    <p>Geweldig nieuws! Een bruidspaar heeft zojuist interesse getoond.</p>
    <hr>
    <p><strong>Lead Details:</strong></p>
    <ul>
        <li>Trouwdatum: {event_str}</li>
        <li>Aantal gasten: {guest_str}</li>
        <li>Regio: {region_str}</li>
        <li>Bericht: {message_str}</li>
    </ul>
    <p><strong>💡 Tip:</strong> Reageer binnen 2 uur — leveranciers die snel reageren,
    boeken 3x vaker.</p>
    <p><a href="https://admin.theperfectwedding.nl">Bekijk lead →</a></p>
    <hr>
    <p>Dit is lead #{lead_number} deze maand. Je profiel is {profile_views}x bekeken.</p>
    """

    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": _FROM_EMAIL, "name": "ThePerfectWedding"},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }

    try:
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {_SENDGRID_API_KEY}"},
            json=payload,
            timeout=10,
        )
        return response.status_code == 202
    except Exception as e:
        print(f"[notify] Email failed: {e}")
        return False


def send_instant_lead_sms(
    to: str,
    couple_name: str,
    category: str,
) -> bool:
    """Send instant SMS notification for a new lead."""
    if not _MESSAGEBIRD_API_KEY:
        print(f"[notify] Would SMS {to} about new lead from {couple_name}")
        return False

    # Max 160 chars for single SMS
    message = (
        f"ThePerfectWedding: Nieuwe lead! {couple_name} is geïnteresseerd in "
        f"{category}. Reageer snel voor beste resultaat. "
        f"https://admin.theperfectwedding.nl"
    )[:160]

    try:
        response = httpx.post(
            "https://rest.messagebird.com/messages",
            headers={"Authorization": f"AccessKey {_MESSAGEBIRD_API_KEY}"},
            json={
                "originator": "TPW",
                "recipients": [to],
                "body": message,
            },
            timeout=10,
        )
        return response.status_code == 201
    except Exception as e:
        print(f"[notify] SMS failed: {e}")
        return False
