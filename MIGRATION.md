# Migration from churn_prediction to tpw-retention

## What Was Extracted

### BigQuery Project
```
tpw-ga4-bigquery
```

### Source Tables (read-only)

| Table | Purpose | Old Usage |
|-------|---------|-----------|
| `churn_prediction.business_development` | Supplier profiles, plans, AMs | Primary source for all models |
| `ga4_dataform_output.bedrijven_pageview_events` | Processed GA4 pageviews | Activity features |
| `ga4_dataform_output.generate_lead` | Contact form submissions | Lead counting |
| `ga4_dataform_output.show_phone` | Phone number reveals | Lead intent signal |
| `ga4_dataform_output.bedrijven_matches` | Matches/inquiries | Lead analysis |
| `ga4_dataform_customer_journey.cj_lead_scoring` | Lead conversions (won/lost) | Conversion tracking |
| `analytics_251061328.events_*` | Raw GA4 events | Fallback |

### Key Columns in business_development

```sql
profile_id, profile_name, category, plan_name, plan_value,
plan_start, plan_end, business_status, account_manager,
num_paid_plans_before
```

**Important filter:** `plan_name != 'Gratis'` — free plans excluded in old system.

### Thresholds Comparison

| System | Threshold | Flag Rate | Precision |
|--------|-----------|-----------|-----------|
| Old dashboard | 0.304 | ~60% | Unknown |
| Old production | 0.60 | 29% | 50% |
| Old hybrid | 0.78 | ~15% | Unknown |
| **New system** | **0.75** | **~9%** | **Target: 65%+** |

### Environment Variables

| Variable | Old System | New System |
|----------|-----------|------------|
| `SLACK_WEBHOOK_URL` | `src/slack_notifications.py` | `src/actions/slack.py` |
| `GCP_PROJECT_ID` | `src/slack_notifications.py` | Hardcoded to `tpw-ga4-bigquery` |
| `SENDGRID_API_KEY` | Not used | New |
| `MESSAGEBIRD_API_KEY` | Not used | New |
| `CRM_API_KEY` | Not used | New |

---

## What Changed

### Old System
```
churn_prediction/
├── 200+ scripts (ab_test, validate, analyze)
├── Multiple model versions
├── Cascading predictor (1,800+ lines)
├── Dashboard with 500-line CSS
└── No automated actions
```

### New System
```
tpw-retention/
├── 1 daily pipeline (jobs/daily_pipeline.py)
├── 1 churn scorer (src/signals/churn_scorer.py, ~150 lines)
├── Clean dashboard (src/dashboard/app.py, ~150 lines)
├── Automated CRM tasks, emails, Slack alerts
└── Supplier-facing API (webhooks, stats)
```

---

## Migration Steps

### 1. Create BigQuery Dataset and Tables

```bash
cd tpw-retention
python jobs/setup_bigquery.py
```

This creates the `retention` dataset with:
- `supplier_stats_daily`
- `signals_daily`
- `actions_log`
- `outcomes`
- `email_log`
- `intervention_log`

### 2. Run Daily Pipeline Locally

```bash
export SLACK_WEBHOOK_URL="..."
python jobs/daily_pipeline.py
```

### 3. Compare Outputs

Check that the new system's outputs make sense:
- P1 count should be ~30-40 (not 114)
- Risk factors should be human-readable
- Stats should match old system's raw numbers

### 4. Deploy to Cloud Run

```bash
gcloud builds submit --config cloudbuild.yaml
```

### 5. Set Up Cloud Scheduler

```bash
gcloud scheduler jobs create http tpw-daily-retention \
    --schedule="0 7 * * *" \
    --uri="https://tpw-retention-api-xxx.run.app/jobs/daily" \
    --http-method=POST \
    --time-zone="Europe/Amsterdam"
```

### 6. Point Lead Webhook to New API

Update your existing lead system to POST to:
```
POST https://tpw-retention-api-xxx.run.app/webhooks/lead
```

### 7. Archive Old System

Once validated:
```bash
mv churn_prediction churn_prediction_archive_2025
```

Keep it for 30 days, then delete.

---

## Data Consistency Check

Run this query to compare old and new predictions side-by-side:

```sql
SELECT
    s.profile_id,
    s.profile_name,
    old.churn_probability AS old_probability,
    new.churn_probability AS new_probability,
    old.priority_tier AS old_tier,
    new.priority_tier AS new_tier,
    new.risk_factors
FROM `tpw-ga4-bigquery.churn_prediction.daily_churn_predictions_segmented` old
JOIN `tpw-ga4-bigquery.retention.signals_daily` new
    ON old.profile_id = new.profile_id
    AND old.prediction_date = new.stats_date
JOIN `tpw-ga4-bigquery.churn_prediction.business_development` s
    ON old.profile_id = s.profile_id
WHERE old.prediction_date = (
    SELECT MAX(prediction_date)
    FROM `tpw-ga4-bigquery.churn_prediction.daily_churn_predictions_segmented`
)
ORDER BY new.churn_probability DESC
LIMIT 50;
```

---

## Rollback Plan

If something goes wrong:

1. Old predictions table is untouched: `churn_prediction.daily_churn_predictions_segmented`
2. Old dashboard is still running: `https://churn-dashboard-678140050967.europe-west4.run.app/`
3. Old Slack notifications still work if `SLACK_WEBHOOK_URL` is set

Simply stop the new Cloud Scheduler job and re-enable the old one.
