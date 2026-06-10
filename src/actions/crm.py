"""CRM task creation for at-risk accounts.

Replace the stub with your actual CRM API (HubSpot, Pipedrive, Salesforce, etc.)
"""

import os
from datetime import datetime, timedelta

import httpx

_CRM_API_URL = os.environ.get("CRM_API_URL", "")
_CRM_API_KEY = os.environ.get("CRM_API_KEY", "")


def create_retention_task(
    profile_id: str,
    profile_name: str,
    category: str,
    plan_value: float,
    plan_end,
    churn_probability: float,
    risk_factors: str,
    account_manager: str,
) -> bool:
    """Create a high-priority retention task in the CRM.

    Returns True if created successfully.
    """
    if not _CRM_API_URL:
        print(f"[crm] No CRM configured. Would create task for {profile_name}")
        return False

    task = {
        "title": f"[URGENT] Retention: {profile_name}",
        "description": f"""
Churn risk: {churn_probability:.0%}
Plan value: €{plan_value:.0f}
Plan ends: {plan_end}
Category: {category}
Risk factors: {risk_factors}

Recommended: Call within 24h. Offer profile optimization or annual discount.
        """.strip(),
        "assigned_to": account_manager or "sales-team",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "high",
        "tags": ["retention", "churn-risk", category],
        "external_id": f"tpw-lifecycle-{profile_id}-{datetime.now().strftime('%Y%m%d')}",
    }

    try:
        response = httpx.post(
            f"{_CRM_API_URL}/tasks",
            headers={"Authorization": f"Bearer {_CRM_API_KEY}"},
            json=task,
            timeout=30,
        )
        return response.status_code == 201
    except Exception as e:
        print(f"[crm] Failed to create task for {profile_name}: {e}")
        return False
