"""Internal Slack alerts for the sales team."""

import os
from datetime import datetime

import httpx

_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def send_summary(
    total_suppliers: int,
    p1_count: int,
    p2_count: int,
    p3_count: int,
    revenue_at_risk: float,
) -> None:
    """Post daily summary to Slack."""
    if not _WEBHOOK_URL:
        print("[slack] No webhook configured, skipping")
        return

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 Lifecycle Daily — {datetime.now().strftime('%d %b %Y')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Suppliers:*\n{total_suppliers}"},
                {"type": "mrkdwn", "text": f"*Revenue at Risk:*\n€{revenue_at_risk:,.0f}"},
                {"type": "mrkdwn", "text": f"*P1 (Urgent):*\n{p1_count} 🔴"},
                {"type": "mrkdwn", "text": f"*P2 (High):*\n{p2_count} 🟠"},
                {"type": "mrkdwn", "text": f"*P3 (Medium):*\n{p3_count} 🟡"},
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open Dashboard"},
                    "url": "https://churn-dashboard-678140050967.europe-west4.run.app/",
                }
            ],
        },
    ]

    try:
        httpx.post(_WEBHOOK_URL, json={"blocks": blocks}, timeout=10)
    except Exception as e:
        print(f"[slack] Failed to send: {e}")
