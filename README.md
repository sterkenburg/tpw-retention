# TPW Lifecycle Platform

Single platform for the full supplier lifecycle at The Perfect Wedding — onboarding, healthy, at-risk, renewal, and lapsed — with retention as one key outcome.

## What It Does

| Feature | Description |
|---------|-------------|
| **Supplier Value Dashboard** | Profile views, leads, projected booking value, benchmarks |
| **Instant Lead Notifications** | Real-time email + SMS when couples contact suppliers |
| **Monthly Results Emails** | Automated value recap sent 1st of every month |
| **Churn Risk Scoring** | Simplified model, ~150 lines, tuned quarterly |
| **Sales Dashboard** | At-risk list with "why" and recommended actions |
| **Automated CRM Tasks** | P1 accounts auto-create tasks for inside sales |
| **Renewal Prep Flows** | 60 days before expiry: value recap + offer |
| **Re-engagement Emails** | 45 days no leads → automated tips email |
| **Slack Alerts** | Daily summary for sales leadership |

## Architecture

```
BigQuery (source of truth)
    ↓
Daily Pipeline (7 AM Cloud Scheduler)
    ↓
├─→ Sales Dashboard (Streamlit on Cloud Run)
├─→ API (FastAPI on Cloud Run)
└─→ Supplier-facing tools (via API)
```

## Project Structure

```
tpw-lifecycle/
├── config/
│   ├── settings.yaml          # Thresholds, table names, API keys
│   └── categories.yaml        # Category benchmarks for projected value
├── src/
│   ├── data/                  # BigQuery I/O
│   │   ├── client.py
│   │   ├── suppliers.py
│   │   ├── activity.py
│   │   └── leads.py
│   ├── analytics/             # Value + stats aggregation
│   │   ├── supplier_stats.py
│   │   └── projected_value.py
│   ├── signals/               # Risk detection
│   │   ├── churn_scorer.py    # ~150 lines, no cascading models
│   │   └── engagement.py
│   ├── actions/               # Execution
│   │   ├── emails.py
│   │   ├── notifications.py   # Instant lead alerts
│   │   ├── crm.py
│   │   └── slack.py
│   ├── templates/emails/      # Jinja2 templates (Dutch)
│   ├── api/
│   │   └── main.py            # FastAPI (webhooks, supplier endpoints)
│   └── dashboard/
│       └── app.py             # Streamlit (internal sales view)
├── jobs/
│   └── daily_pipeline.py      # THE main job
├── Dockerfile
├── cloudbuild.yaml
└── pyproject.toml
```

## Quick Start

### 1. Install

```bash
cd tpw-lifecycle
pip install -e ".[dev]"
```

### 2. Configure

```bash
cp config/settings.yaml config/settings.local.yaml
# Edit: add your GA4 dataset, API keys, table names
```

Set environment variables:
```bash
export SENDGRID_API_KEY="..."
export SLACK_WEBHOOK_URL="..."
export MESSAGEBIRD_API_KEY="..."
export CRM_API_KEY="..."
```

### 3. Run Daily Pipeline

```bash
python jobs/daily_pipeline.py
```

### 4. Run Dashboard Locally

```bash
streamlit run src/dashboard/app.py
```

### 5. Run API Locally

```bash
uvicorn src.api.main:app --reload
```

## Deploy to Cloud Run

```bash
gcloud builds submit --config cloudbuild.yaml
```

This deploys two services:
- `tpw-lifecycle-api` — FastAPI for webhooks and supplier endpoints
- `tpw-lifecycle-dashboard` — Streamlit for sales team

## Cloud Scheduler

```bash
# Daily pipeline at 7 AM
gcloud scheduler jobs create http tpw-daily-lifecycle \
    --schedule="0 7 * * *" \
    --uri="https://tpw-lifecycle-api-xxx.run.app/jobs/daily" \
    --http-method=POST \
    --time-zone="Europe/Amsterdam"
```

## What We Cherry-Picked from Old System

| From Old | To New |
|----------|--------|
| BigQuery connection | `src/data/client.py` |
| GA4 event querying | `src/data/activity.py` |
| `days_since_last_activity` | `src/signals/churn_scorer.py` |
| Cloud Run deployment | `Dockerfile` + `cloudbuild.yaml` |
| Slack notification format | `src/actions/slack.py` |
| Phase 2 decision (stop retraining) | Architecture doc |

## What We Left Behind

- 50+ `ab_test_*.py` scripts
- 30+ `validate_*.py` scripts
- Cascading predictor complexity
- Multiple model versions
- `archive/experiments/` folder
- Threshold optimization scripts

## Key Design Decisions

1. **Churn scoring is a signal, not a product** — ~150 lines, rule-based with optional quarterly retraining
2. **One daily pipeline** — not 200 scripts
3. **One stats table powers everything** — dashboard, emails, scoring, notifications
4. **Action-oriented** — every signal triggers an action, not just a report
5. **Supplier-facing + internal** — same data, different views

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SENDGRID_API_KEY` | Yes | Email sending |
| `SLACK_WEBHOOK_URL` | Yes | Internal alerts |
| `MESSAGEBIRD_API_KEY` | No | SMS notifications |
| `CRM_API_KEY` | No | CRM task creation |
| `CRM_API_URL` | No | CRM endpoint |
| `APP_MODE` | No | `api` or `dashboard` |

## Next Steps

1. Update `config/settings.yaml` with your actual BigQuery table names
2. Update `src/data/activity.py` with your GA4 dataset
3. Run `daily_pipeline.py` manually to test
4. Deploy to Cloud Run
5. Set up Cloud Scheduler
6. Connect webhook endpoint to your lead system
