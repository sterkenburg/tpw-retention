# Technical Integration Spec: Churn Prediction → Retention Actions

This document bridges your existing churn prediction system with the retention automation strategy. Concrete code changes, SQL queries, and API specs.

---

## Current Architecture

```
BigQuery (business data + GA4)
    ↓
daily_prediction_pipeline.py (7 AM cron)
    ↓
BigQuery: daily_churn_predictions_segmented
    ↓
Streamlit Dashboard (Cloud Run)
    ↓
Sales manager views list → Manually decides who to call
```

**Missing:** The connection to automated actions, CRM, and supplier-facing communications.

---

## Target Architecture

```
BigQuery (business data + GA4)
    ↓
daily_prediction_pipeline.py (7 AM cron)
    ↓
BigQuery: daily_churn_predictions_segmented
    ↓
├─→ Streamlit Dashboard (for sales managers)
├─→ CRM / Task System (for inside sales)
├─→ Email Automation (for supplier communications)
├─→ Supplier Dashboard (for self-service value proof)
└─→ Slack Alerts (for urgent cases)
```

---

## Change 1: Add Risk Factors to Predictions Table

**File:** Modify `daily_prediction_pipeline.py` or BigQuery table schema

**Current table schema:**
```sql
-- daily_churn_predictions_segmented (current)
profile_id STRING,
profile_name STRING,
churn_probability FLOAT64,
predicted_churn INT64,
risk_level STRING,  -- "Critical", "High", "Medium", "Low"
plan_value FLOAT64,
category STRING
```

**Add columns:**
```sql
ALTER TABLE `tpw-ga4-bigquery.churn_prediction.daily_churn_predictions_segmented`
ADD COLUMN IF NOT EXISTS days_since_last_login INT64,
ADD COLUMN IF NOT EXISTS days_since_last_lead INT64,
ADD COLUMN IF NOT EXISTS profile_completion_pct FLOAT64,
ADD COLUMN IF NOT EXISTS page_views_30d INT64,
ADD COLUMN IF NOT EXISTS page_views_trend FLOAT64,  -- vs previous 30d
ADD COLUMN IF NOT EXISTS leads_30d INT64,
ADD COLUMN IF NOT EXISTS risk_factors ARRAY<STRING>,
ADD COLUMN IF NOT EXISTS recommended_action STRING,
ADD COLUMN IF NOT EXISTS priority_tier STRING;  -- P1, P2, P3, P4
```

**SQL to populate (run as part of pipeline):**
```sql
-- Add this CTE to your existing prediction query
WITH supplier_signals AS (
  SELECT
    p.profile_id,
    -- Days since last login
    DATE_DIFF(CURRENT_DATE(), MAX(a.event_date), DAY) as days_since_last_login,
    -- Days since last lead
    DATE_DIFF(CURRENT_DATE(), MAX(l.created_at), DAY) as days_since_last_lead,
    -- Profile completion
    (LENGTH(p.description) > 0)::INT + 
    (p.photo_count >= 5)::INT + 
    (p.phone IS NOT NULL)::INT + 
    (p.website IS NOT NULL)::INT as profile_completion_score,
    -- Page views
    COUNTIF(a.event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()) as page_views_30d,
    COUNTIF(a.event_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) as page_views_30_60d,
    -- Leads
    COUNTIF(l.created_at BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()) as leads_30d
  FROM `tpw-ga4-bigquery.churn_prediction.business_development` p
  LEFT JOIN `tpw-ga4-bigquery.analytics_xxx.events_*` a  -- your GA4 table
    ON p.profile_id = a.user_pseudo_id
  LEFT JOIN `tpw-ga4-bigquery.leads.leads_table` l  -- your leads table
    ON p.profile_id = l.profile_id
  WHERE p.plan_end >= CURRENT_DATE()
  GROUP BY p.profile_id, p.description, p.photo_count, p.phone, p.website
)

-- Calculate risk factors array
SELECT
  p.*,
  s.days_since_last_login,
  s.days_since_last_lead,
  s.profile_completion_score / 4.0 * 100 as profile_completion_pct,
  s.page_views_30d,
  SAFE_DIVIDE(s.page_views_30d - s.page_views_30_60d, s.page_views_30_60d) as page_views_trend,
  s.leads_30d,
  -- Risk factors as array
  ARRAY_TO_STRING(ARRAY[
    IF(s.days_since_last_login > 30, "No login in 30+ days", NULL),
    IF(s.days_since_last_lead > 60, "No leads in 60+ days", NULL),
    IF(s.profile_completion_score < 2, "Incomplete profile", NULL),
    IF(s.page_views_30d < 10, "Very low profile views", NULL),
    IF(s.page_views_trend < -0.5, "Declining engagement", NULL),
    IF(s.leads_30d = 0, "No recent leads", NULL)
  ], ", ") as risk_factors,
  -- Recommended action
  CASE
    WHEN p.churn_probability >= 0.75 THEN "URGENT: Call within 24h"
    WHEN p.churn_probability >= 0.65 THEN "HIGH: Send re-engagement email + schedule call"
    WHEN p.churn_probability >= 0.55 THEN "MEDIUM: Include in monthly nurture"
    ELSE "LOW: Standard nurture"
  END as recommended_action,
  -- Priority tier
  CASE
    WHEN p.churn_probability >= 0.75 THEN "P1"
    WHEN p.churn_probability >= 0.65 THEN "P2"
    WHEN p.churn_probability >= 0.55 THEN "P3"
    ELSE "P4"
  END as priority_tier
FROM predictions p
LEFT JOIN supplier_signals s ON p.profile_id = s.profile_id
```

---

## Change 2: Update Dashboard to Show Risk Factors

**File:** `churn_prediction_dashboard.py`

**Add to column config (~line 1670):**
```python
column_config = {
    # ... existing columns ...
    "risk_factors": st.column_config.TextColumn(
        "Why at risk?",
        help="Key behavioral signals driving the prediction",
        width="large"
    ),
    "recommended_action": st.column_config.TextColumn(
        "Recommended Action",
        help="What to do next",
        width="large"
    ),
    "days_since_last_login": st.column_config.NumberColumn(
        "Days since login",
        help="Last time supplier logged into dashboard"
    ),
    "days_since_last_lead": st.column_config.NumberColumn(
        "Days since lead",
        help="Last time supplier received an inquiry"
    ),
}
```

**Add filter for P1 only (sales team's daily view):**
```python
# Add near line 1714 (sidebar settings)
st.sidebar.header("🎯 Sales View")
show_only_p1 = st.sidebar.checkbox(
    "Show only P1 (Urgent)",
    help="Filter to highest priority accounts only"
)

if show_only_p1:
    actionable_list = actionable_list[actionable_list["priority_tier"] == "P1"]
    st.info(f"🔴 {len(actionable_list)} accounts require URGENT attention today")
```

---

## Change 3: Automated CRM Task Creation

**New file:** `scripts/create_retention_tasks.py`

```python
#!/usr/bin/env python3
"""
Daily script: Creates retention tasks in CRM for P1 at-risk accounts.
Run after daily_prediction_pipeline.py completes.
"""

import pandas as pd
import pandas_gbq
from datetime import datetime, timedelta
import requests  # or your CRM SDK

# Configuration
CRM_API_URL = "https://your-crm.com/api/v1/tasks"
CRM_API_KEY = "..."
BIGQUERY_PROJECT = "tpw-ga4-bigquery"

def get_p1_accounts():
    """Fetch P1 accounts from yesterday's predictions."""
    query = f"""
    SELECT
        profile_id,
        profile_name,
        category,
        plan_value,
        plan_end,
        churn_probability,
        risk_factors,
        recommended_action,
        account_manager,
        days_since_last_login,
        days_since_last_lead
    FROM `{BIGQUERY_PROJECT}.churn_prediction.daily_churn_predictions_segmented`
    WHERE prediction_date = (
        SELECT MAX(prediction_date) 
        FROM `{BIGQUERY_PROJECT}.churn_prediction.daily_churn_predictions_segmented`
    )
    AND priority_tier = 'P1'
    AND predicted_churn = 1
    ORDER BY churn_probability DESC
    """
    return pandas_gbq.read_gbq(query, project_id=BIGQUERY_PROJECT)

def create_crm_task(row):
    """Create a task in your CRM system."""
    task = {
        "title": f"[URGENT] Retention call: {row['profile_name']}",
        "description": f"""
Churn risk: {row['churn_probability']:.0%}
Plan value: €{row['plan_value']:.0f}
Plan ends: {row['plan_end']}
Risk factors: {row['risk_factors']}

Recommended action: {row['recommended_action']}

Call script tips:
- Mention: "We noticed you haven't logged in recently"
- Offer: Free profile optimization
- Ask: "What would make you stay?"
        """.strip(),
        "assigned_to": row.get('account_manager', 'sales-team'),
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "high",
        "tags": ["retention", "churn-risk", row['category']],
        "external_id": f"tpw-retention-{row['profile_id']}-{datetime.now().strftime('%Y%m%d')}"
    }
    
    # Example with generic CRM API
    # response = requests.post(
    #     CRM_API_URL,
    #     headers={"Authorization": f"Bearer {CRM_API_KEY}"},
    #     json=task
    # )
    # return response.ok
    
    # For now, just print (replace with actual CRM integration)
    print(f"Task created: {task['title']} → {task['assigned_to']}")
    return True

def main():
    df = get_p1_accounts()
    print(f"Found {len(df)} P1 accounts requiring intervention")
    
    for _, row in df.iterrows():
        create_crm_task(row)
    
    # Log to BigQuery for tracking
    log_data = df[['profile_id', 'churn_probability', 'recommended_action']].copy()
    log_data['intervention_date'] = datetime.now()
    log_data['intervention_type'] = 'crm_task'
    
    pandas_gbq.to_gbq(
        log_data,
        f"{BIGQUERY_PROJECT}.churn_prediction.intervention_log",
        project_id=BIGQUERY_PROJECT,
        if_exists='append'
    )

if __name__ == "__main__":
    main()
```

**Add to Cloud Scheduler (daily at 8 AM, 1 hour after predictions):**
```bash
gcloud scheduler jobs create http churn-retention-tasks \
    --schedule="0 8 * * *" \
    --uri="https://your-cloud-run-url/create-tasks" \
    --http-method=POST \
    --time-zone="Europe/Amsterdam"
```

---

## Change 4: Automated Email Flows (P2 Accounts)

**New file:** `scripts/trigger_retention_emails.py`

```python
#!/usr/bin/env python3
"""
Triggers automated retention emails for P2 accounts.
Uses the email templates from retention strategy.
"""

import pandas as pd
import pandas_gbq
from datetime import datetime

# Import your email service (Mailchimp, SendGrid, HubSpot, etc.)
# from services.email_service import send_retention_email

BIGQUERY_PROJECT = "tpw-ga4-bigquery"

def get_p2_accounts():
    """Fetch P2 accounts that haven't been emailed in 7 days."""
    query = f"""
    WITH last_email AS (
        SELECT profile_id, MAX(sent_at) as last_sent
        FROM `{BIGQUERY_PROJECT}.churn_prediction.email_log`
        GROUP BY profile_id
    )
    SELECT
        p.profile_id,
        p.profile_name,
        p.email,  -- need to add email column
        p.category,
        p.churn_probability,
        p.risk_factors,
        p.days_since_last_login,
        p.days_since_last_lead
    FROM `{BIGQUERY_PROJECT}.churn_prediction.daily_churn_predictions_segmented` p
    LEFT JOIN last_email e ON p.profile_id = e.profile_id
    WHERE p.prediction_date = (
        SELECT MAX(prediction_date) 
        FROM `{BIGQUERY_PROJECT}.churn_prediction.daily_churn_predictions_segmented`
    )
    AND p.priority_tier = 'P2'
    AND p.predicted_churn = 1
    AND (e.last_sent IS NULL OR e.last_sent < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY))
    ORDER BY p.churn_probability DESC
    LIMIT 50  -- daily cap
    """
    return pandas_gbq.read_gbq(query, project_id=BIGQUERY_PROJECT)

def send_email(row):
    """Send appropriate retention email based on risk factors."""
    
    # Determine which email template to use
    if row['days_since_last_lead'] > 60:
        template = "no_lead_reengagement"
        subject = f"Je profiel is bekeken — hier is waarom er (nog) geen aanvraag is"
    elif row['days_since_last_login'] > 30:
        template = "re_engagement"
        subject = f"We missen je op ThePerfectWedding"
    else:
        template = "monthly_results"
        subject = f"Je ThePerfectWedding resultaten"
    
    # Build email content (simplified — use templates from doc 09)
    email_data = {
        "to": row['email'],
        "subject": subject,
        "template": template,
        "variables": {
            "name": row['profile_name'],
            "days_since_login": row['days_since_last_login'],
            "days_since_lead": row['days_since_last_lead'],
            "category": row['category']
        }
    }
    
    # Send via your email provider
    # send_retention_email(email_data)
    
    print(f"Email queued: {subject} → {row['email']}")
    return True

def main():
    df = get_p2_accounts()
    print(f"Triggering retention emails for {len(df)} P2 accounts")
    
    for _, row in df.iterrows():
        send_email(row)
    
    # Log sends
    if not df.empty:
        log = df[['profile_id']].copy()
        log['sent_at'] = datetime.now()
        log['email_type'] = 'retention_automated'
        
        pandas_gbq.to_gbq(
            log,
            f"{BIGQUERY_PROJECT}.churn_prediction.email_log",
            project_id=BIGQUERY_PROJECT,
            if_exists='append'
        )

if __name__ == "__main__":
    main()
```

---

## Change 5: Outcome Tracking Table

**BigQuery DDL:**
```sql
-- Intervention tracking
CREATE TABLE IF NOT EXISTS `tpw-ga4-bigquery.churn_prediction.intervention_outcomes` (
    profile_id STRING NOT NULL,
    plan_end DATE NOT NULL,
    intervention_date DATE NOT NULL,
    intervention_type STRING,  -- 'crm_call', 'email', 'profile_optimize', 'discount_offer'
    assigned_to STRING,  -- AM name
    notes STRING,
    outcome STRING,  -- 'saved', 'churned', 'no_response', 'in_progress'
    revenue_preserved FLOAT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(intervention_date);

-- Email tracking
CREATE TABLE IF NOT EXISTS `tpw-ga4-bigquery.churn_prediction.email_log` (
    profile_id STRING NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    email_type STRING,
    template STRING,
    opened BOOLEAN,
    clicked BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Model performance tracking (production metrics over time)
CREATE TABLE IF NOT EXISTS `tpw-ga4-bigquery.churn_prediction.model_performance_history` (
    prediction_date DATE NOT NULL,
    total_customers INT64,
    flagged_customers INT64,
    known_outcomes INT64,
    precision FLOAT64,
    recall FLOAT64,
    f1_score FLOAT64,
    threshold_used FLOAT64,
    model_version STRING
)
PARTITION BY prediction_date;
```

---

## Change 6: Update Daily Pipeline to Log Performance

**Add to `daily_prediction_pipeline.py` (after predictions saved):**
```python
# Log production performance metrics
def log_model_performance(predictions_df, prediction_date):
    """Log daily model performance to BigQuery."""
    
    known = predictions_df[predictions_df['actual_outcome'].isin(['Churned', 'Retained'])]
    
    if len(known) > 0:
        tp = len(known[(known['predicted_churn'] == 1) & (known['actual_outcome'] == 'Churned')])
        fp = len(known[(known['predicted_churn'] == 1) & (known['actual_outcome'] == 'Retained')])
        fn = len(known[(known['predicted_churn'] == 0) & (known['actual_outcome'] == 'Churned')])
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    else:
        precision = recall = f1 = None
    
    performance_row = pd.DataFrame([{
        'prediction_date': prediction_date,
        'total_customers': len(predictions_df),
        'flagged_customers': predictions_df['predicted_churn'].sum(),
        'known_outcomes': len(known),
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'threshold_used': predictions_df['threshold_used'].iloc[0] if 'threshold_used' in predictions_df.columns else 0.55,
        'model_version': predictions_df['model_version'].iloc[0] if 'model_version' in predictions_df.columns else 'unknown'
    }])
    
    pandas_gbq.to_gbq(
        performance_row,
        'tpw-ga4-bigquery.churn_prediction.model_performance_history',
        project_id='tpw-ga4-bigquery',
        if_exists='append'
    )
    
    return precision, recall, f1

# Call this at the end of your pipeline
precision, recall, f1 = log_model_performance(df_predictions, pd.Timestamp.now())
print(f"Production metrics — Precision: {precision:.1%}, Recall: {recall:.1%}, F1: {f1:.3f}")
```

---

## Change 7: Slack Alert Enhancement

**Update Slack notification to include P1 count + action summary:**
```python
# In your Slack notification script
p1_count = len(df[df['priority_tier'] == 'P1'])
p2_count = len(df[df['priority_tier'] == 'P2'])

slack_message = f"""
🚨 *Daily Churn Alert — {prediction_date}*

*Predictions:* {len(df)} customers analyzed
*At Risk:* {df['predicted_churn'].sum()} flagged

*Priority Breakdown:*
🔴 P1 (Urgent): {p1_count} — *Call today*
🟠 P2 (High): {p2_count} — *Email + monitor*
🟡 P3 (Medium): {p3_count} — *Nurture*

*Top 3 Risk Factors Today:*
{risk_factor_summary}

*Dashboard:* https://churn-dashboard-678140050967.europe-west4.run.app/
*CRM Tasks:* Auto-created for P1 accounts
"""
```

---

## Implementation Order

| Week | Change | Effort | Impact |
|------|--------|--------|--------|
| 1 | Change 1: Add columns to BigQuery | 1 day | High |
| 1 | Change 2: Update dashboard | 2 days | High |
| 2 | Change 7: Enhanced Slack alerts | 0.5 day | Medium |
| 2 | Change 5: Create outcome tables | 0.5 day | High |
| 3 | Change 6: Log performance daily | 1 day | High |
| 3 | Change 3: CRM task creation | 2-3 days | High |
| 4 | Change 4: Automated emails | 2-3 days | High |

---

## What You Can Reuse from Existing System

| Existing Asset | Reuse For |
|----------------|-----------|
| `daily_prediction_pipeline.py` | Add performance logging + new columns |
| `churn_prediction_dashboard.py` | Add risk factors + P1 filter |
| BigQuery tables | Add outcome tracking tables |
| Slack notification script | Enhanced alerts with priority breakdown |
| Cloud Scheduler (7 AM) | Keep as-is, add 8 AM CRM task job |
| Cloud Run deployment | Deploy new dashboard version |

---

## What to Archive

| Item | Why Archive |
|------|-------------|
| 50+ `ab_test_*.py` scripts | Over-engineering, no longer needed |
| 30+ `validate_*.py` scripts | One validation script is enough |
| `archive/experiments/` | Historical, not operational |
| Multiple model versions | Pick one production model, delete others |
| Old CSV exports | Source of truth is BigQuery |

**Keep only:**
- `daily_prediction_pipeline.py`
- `churn_prediction_dashboard.py`
- `train_baseline_model.py` (for retraining)
- `scripts/create_retention_tasks.py` (new)
- `scripts/trigger_retention_emails.py` (new)
- `src/slack_notifications.py`
