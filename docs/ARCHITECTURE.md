# TPW Lifecycle Platform — Architecture

## What This Is

A single platform that manages the **full** supplier lifecycle for The Perfect Wedding — onboarding → healthy → at_risk → renewal_window → lapsed — with retention as one key phase/outcome:
- Supplier value dashboard (views, leads, projected value)
- Instant lead notifications (email/SMS)
- Automated email flows (monthly results, re-engagement, renewal)
- Churn risk scoring (ONE of several signals)
- Sales team tools (at-risk list, CRM tasks)
- Exit surveys + cancellation save

**Not a churn prediction project with retention bolted on.**

---

## Design Principles

1. **One database of truth** — BigQuery, not scattered CSVs
2. **One daily job** — not 200 scripts
3. **One dashboard** — not separate tools
4. **Signal-agnostic** — churn risk is one signal; engagement drop is another; renewal approaching is another
5. **Action-oriented** — every signal triggers an action, not just a report
6. **Supplier-facing + internal** — same data, different views

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BIGQUERY (Source of Truth)                                                 │
│  ├── analytics_xxx.events_*        (GA4: views, clicks, engagement)        │
│  ├── churn_prediction.business_development  (plans, profiles, AMs)         │
│  ├── leads.leads_table             (inquiries, contacts)                   │
│  └── retention.*                   (this platform's tables)                │
│      ├── supplier_stats_daily      (aggregated per supplier)               │
│      ├── signals_daily             (all risk/engagement signals)           │
│      ├── actions_log               (what we did)                           │
│      └── outcomes                  (what happened)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DAILY PIPELINE (7 AM Cloud Scheduler)                                      │
│  1. Ingest GA4 + business data → supplier_stats_daily                      │
│  2. Calculate signals → signals_daily                                       │
│     • churn_probability (simplified model)                                  │
│     • engagement_trend (views up/down)                                      │
│     • days_until_renewal                                                    │
│     • days_since_last_lead                                                  │
│     • profile_completion_pct                                                │
│  3. Determine actions → actions_queue                                       │
│     • P1 (>75% churn): CRM task                                             │
│     • P2 (65-75%): retention email                                          │
│     • Renewal <60d: renewal email                                           │
│     • No lead 45d: re-engagement email                                      │
│  4. Execute actions                                                         │
│     • Create CRM tasks                                                      │
│     • Send emails (batch)                                                   │
│     • Post Slack summary                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌───────────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  SUPPLIER-FACING      │ │  SALES DASHBOARD │ │  AUTOMATION      │
│  (API/Web)            │ │  (Streamlit)     │ │  (Triggers)      │
│                       │ │                  │ │                  │
│  • Value dashboard    │ │  • At-risk list  │ │  • Instant lead  │
│  • Instant notifs     │ │  • CRM tasks     │ │    notifications │
│  • Monthly email      │ │  • Outcome       │ │  • Email flows   │
│  • Profile tips       │ │    tracking      │ │  • Win-back      │
└───────────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Project Structure

```
tpw-lifecycle/
├── README.md                          # What this is, how to deploy
├── ARCHITECTURE.md                    # This file
├── pyproject.toml                     # Python deps
├── Dockerfile                         # Cloud Run
├── cloudbuild.yaml                    # CI/CD
├── config/
│   ├── settings.yaml                  # BigQuery project, thresholds, API keys
│   └── categories.yaml                # Wedding category definitions + benchmarks
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                          # BigQuery I/O only
│   │   ├── __init__.py
│   │   ├── client.py                  # pandas_gbq wrapper
│   │   ├── suppliers.py               # Read supplier profiles/plans
│   │   ├── activity.py                # Read GA4 engagement data
│   │   └── leads.py                   # Read lead/contact data
│   │
│   ├── analytics/                     # Value + stats (supplier-facing data)
│   │   ├── __init__.py
│   │   ├── supplier_stats.py          # Aggregate views/clicks per supplier
│   │   ├── projected_value.py         # Estimated booking value formula
│   │   └── benchmarks.py              # Category averages (top 10%, etc.)
│   │
│   ├── signals/                       # Risk/engagement signals
│   │   ├── __init__.py
│   │   ├── churn_scorer.py            # Simplified model (NOT the star)
│   │   ├── engagement.py              # Trend detection (views up/down)
│   │   └── renewal.py                 # Renewal approaching calculations
│   │
│   ├── actions/                       # What we DO when signals fire
│   │   ├── __init__.py
│   │   ├── emails.py                  # SendGrid/Mailchimp wrapper
│   │   ├── notifications.py           # Instant lead alerts (email + SMS)
│   │   ├── crm.py                     # CRM task creation
│   │   └── slack.py                   # Internal alerts
│   │
│   ├── templates/                     # Email copy (Dutch)
│   │   ├── instant_lead.html
│   │   ├── monthly_results.html
│   │   ├── re_engagement.html
│   │   ├── renewal_prep.html
│   │   └── cancellation_save.html
│   │
│   ├── api/                           # FastAPI (webhooks, supplier endpoints)
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   └── dashboard/                     # Streamlit (internal sales view)
│       ├── __init__.py
│       └── app.py
│
├── jobs/                              # Runnable scripts (Cloud Scheduler)
│   ├── daily_pipeline.py              # THE main job
│   └── send_instant_notification.py   # Webhook handler for lead events
│
└── tests/                             # Minimal but real tests
    └── ...
```

---

## Key Decisions

### Churn Scoring is a Signal, Not a Product

The old system treated churn prediction as the centerpiece. It isn't.

**New approach:** `churn_scorer.py` is ~150 lines. It calculates a probability using proven features only:
- `days_since_last_activity`
- `days_since_last_lead`
- `profile_completion_pct`
- `page_views_trend`
- `plan_value`
- `tenure_months`

**No cascading models. No 200 scripts. No threshold optimization.** Set threshold to 0.75, tune once per quarter based on actual outcomes.

### One Daily Pipeline, Not 50 Scripts

```python
# jobs/daily_pipeline.py

def run():
    # 1. Load data
    suppliers = data.suppliers.get_current()
    activity = data.activity.get_last_90d()
    leads = data.leads.get_last_90d()
    
    # 2. Calculate stats
    stats = analytics.supplier_stats.calculate(suppliers, activity, leads)
    
    # 3. Calculate signals
    signals = signals.all.calculate(stats)
    #   - churn_probability
    #   - engagement_trend
    #   - days_until_renewal
    #   - days_since_last_lead
    
    # 4. Determine actions
    actions = actions.determine(signals)
    #   - CRM tasks for P1
    #   - Emails for P2 / no-lead / renewal
    
    # 5. Execute
    actions.execute()
    
    # 6. Log + notify
    actions.slack.summary(actions)
```

**One file. One cron job. Done.**

### Supplier Stats Drive Everything

The old system had separate data flows for predictions, dashboard, and emails.

**New approach:** One `supplier_stats_daily` table powers everything:

| Column | Used By |
|--------|---------|
| `profile_views_30d` | Dashboard, monthly email, churn signal |
| `contact_clicks_30d` | Dashboard, monthly email, projected value |
| `leads_30d` | Instant notification, monthly email, churn signal |
| `profile_completion_pct` | Dashboard, re-engagement email, churn signal |
| `days_since_last_login` | Dashboard, churn signal, re-engagement email |
| `estimated_value_30d` | Dashboard, monthly email |
| `churn_probability` | Dashboard, CRM tasks |
| `engagement_trend` | Dashboard, re-engagement email |

**One query per day. One table. Everything reads from it.**

---

## What We Cherry-Pick from Old System

| From Old | To New | Why |
|----------|--------|-----|
| BigQuery connection logic | `src/data/client.py` | Proven, keep |
| GA4 event querying | `src/data/activity.py` | Proven, keep |
| `days_since_last_activity` feature | `src/signals/churn_scorer.py` | Best discriminator |
| Cloud Run deployment | `Dockerfile` + `cloudbuild.yaml` | Proven, keep |
| Slack notification format | `src/actions/slack.py` | Proven, keep |
| Phase 2 decision (stop retraining) | Architecture doc | Correct call |

## What We Leave Behind

| From Old | Why Drop |
|----------|----------|
| 50+ `ab_test_*.py` scripts | Over-engineering |
| 30+ `validate_*.py` scripts | Analysis paralysis |
| Cascading predictor complexity | Production precision was 50%, not 78% |
| Multiple model versions | One model, tune quarterly |
| `archive/experiments/` folder | Historical baggage |
| Threshold optimization scripts | Set 0.75, move on |

---

## Deployment

One Cloud Run service. Two entry points:

| Entry Point | Command | Purpose |
|-------------|---------|---------|
| Dashboard | `streamlit run src/dashboard/app.py` | Sales team UI |
| API | `uvicorn src.api.main:app` | Webhooks, supplier endpoints |

One Cloud Scheduler job:

| Job | Schedule | Command |
|-----|----------|---------|
| Daily pipeline | `0 7 * * *` | `python jobs/daily_pipeline.py` |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily pipeline runtime | <5 minutes | Logs |
| Dashboard load time | <3 seconds | User experience |
| Flagged accounts (P1) | <50/day | BigQuery |
| Intervention save rate | >30% | `outcomes` table |
| Supplier dashboard engagement | >60% monthly | Email opens + logins |
| Email open rate (monthly) | >40% | SendGrid/Mailchimp |
| Instant notification delivery | >98% | Logs |
