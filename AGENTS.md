# TPW Lifecycle Platform — Agent Guide

This document is for AI coding agents. It assumes you know nothing about this project.

## Project Overview

The **TPW Lifecycle Platform** is the single system that manages the full supplier lifecycle for **The Perfect Wedding** (a Dutch wedding marketplace) — moving suppliers through onboarding → healthy → at_risk → renewal_window → lapsed. Retention is one phase/outcome within that lifecycle, not the whole system. It replaces a legacy `churn_prediction` system that had grown to 200+ scripts, cascading models, and analysis paralysis. (The BigQuery dataset and several Cloud Run services are still named `retention*` pending a rename migration.)

**Core philosophy:** churn risk is one signal among many, not the centerpiece. The platform is action-oriented — every signal triggers a concrete action (CRM task, email, Slack alert) rather than just producing a report.

**Key features:**
- Supplier value dashboard (views, leads, projected booking value, benchmarks)
- Instant lead notifications (real-time email + SMS when couples contact suppliers)
- Monthly results emails (automated value recap, 1st of every month)
- Churn risk scoring (~150 lines, rule-based, tuned quarterly)
- Sales dashboard (at-risk list with "why" and recommended actions)
- Automated CRM tasks (P1 accounts auto-create tasks for inside sales)
- Renewal prep flows (60 days before expiry: value recap + offer)
- Re-engagement emails (45 days no leads → automated tips email)
- Slack alerts (daily summary for sales leadership)

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.11+ |
| **Data** | pandas, numpy, pandas-gbq, google-cloud-bigquery, google-cloud-storage |
| **API** | FastAPI + Uvicorn |
| **Dashboard (legacy)** | Streamlit |
| **Dashboard (modern)** | Next.js 16.2.6 + React 19.2.4 + TypeScript 5 + Tailwind CSS v4 |
| **Validation/Config** | Pydantic v2, Pydantic-Settings, PyYAML |
| **HTTP Clients** | httpx |
| **Templating** | Jinja2 |
| **Resilience** | tenacity |
| **Code Quality** | ruff, mypy, ESLint v9 |
| **Testing** | pytest, pytest-asyncio (configured but **no tests exist yet**) |
| **Container** | Docker (python:3.11-slim) |
| **Cloud** | Google Cloud Platform (BigQuery, Cloud Run, Cloud Build, Cloud Scheduler) |

## Project Structure

```
tpw-lifecycle/
├── config/
│   ├── settings.yaml          # Thresholds, table names, API config, BigQuery project
│   └── categories.yaml        # Wedding supplier category benchmarks (16 categories)
├── docs/
│   ├── ARCHITECTURE.md        # System design & decisions (deep dive)
│   ├── MIGRATION.md           # Migration guide from old churn_prediction system
│   └── strategy/              # 14 planning documents (~2,800 lines)
├── jobs/
│   ├── daily_pipeline.py      # THE main daily cron job (Cloud Scheduler)
│   └── setup_bigquery.py      # One-time BQ table creation script
├── src/                       # Python backend
│   ├── __init__.py            # Empty
│   ├── data/                  # BigQuery I/O only
│   │   ├── client.py          # pandas_gbq wrapper; single point of contact for BQ I/O
│   │   ├── suppliers.py       # Read business_development + profiles tables
│   │   ├── activity.py        # Read GA4 pageview events
│   │   └── leads.py           # Read generate_lead + show_phone events
│   ├── analytics/             # Value + stats aggregation
│   │   ├── supplier_stats.py  # Aggregate views/clicks per supplier (one table to rule them all)
│   │   └── projected_value.py # Estimated booking value formula using category benchmarks
│   ├── signals/               # Risk/engagement detection
│   │   ├── churn_scorer.py    # ~150 lines, rule-based churn probability (P1-P4 tiers)
│   │   └── engagement.py      # Detects engagement decline (>50% drop) and no-activity flags
│   ├── actions/               # Execution layer
│   │   ├── emails.py          # SendGrid wrapper with Jinja2 templates (Dutch)
│   │   ├── notifications.py   # Instant lead alerts (email + SMS via MessageBird)
│   │   ├── crm.py             # CRM task creation stub (POST to configured API)
│   │   └── slack.py           # Daily summary to Slack webhook
│   ├── templates/emails/      # Jinja2 HTML email templates (Dutch language)
│   │   ├── monthly_results.html
│   │   ├── re_engagement.html
│   │   └── renewal_prep.html
│   ├── api/
│   │   └── main.py            # FastAPI: /health, /webhooks/lead, /suppliers/{id}/stats
│   └── dashboard/
│       └── app.py             # Streamlit sales dashboard (KPIs, at-risk table, CSV export)
├── tests/                     # EMPTY — no tests exist yet
├── web/                       # Next.js 16 frontend (modern replacement for Streamlit)
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── page.tsx       # Server page: loads BQ data, renders OverviewClient
│   │   │   ├── OverviewClient.tsx  # Client: search, tier/AM filters, KPI stat cards, supplier table
│   │   │   ├── actions/page.tsx    # Action queue (P1 urgent, renewals <60d, no leads 45d+)
│   │   │   ├── suppliers/[id]/page.tsx  # Detailed supplier health page
│   │   │   ├── layout.tsx     # Global nav, Inter font, gray-50 background
│   │   │   └── globals.css    # Tailwind imports
│   │   ├── components/        # Reusable React components
│   │   │   ├── SupplierTable.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── TierBadge.tsx
│   │   │   └── ActionHistory.tsx
│   │   └── lib/
│   │       └── bigquery.ts    # Server-side BigQuery client + typed query functions
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   ├── .env.example
│   └── .env.local             # Contains secrets (gitignored)
├── .env.example               # Root env var template
├── Dockerfile                 # Multi-mode: api or dashboard via APP_MODE
├── cloudbuild.yaml            # GCP CI/CD: build → push → deploy both services
├── pyproject.toml             # Python package config
└── README.md                  # Human-facing quick start
```

## Build, Run, and Test Commands

### Python Backend

```bash
# Install (editable, with dev dependencies)
pip install -e ".[dev]"

# Run the daily pipeline
python jobs/daily_pipeline.py

# Run the API locally
uvicorn src.api.main:app --reload

# Run the Streamlit dashboard locally
streamlit run src/dashboard/app.py

# Lint and format
ruff check .
ruff format .

# Type check
mypy src/

# Run tests (currently no tests exist)
pytest
```

### Web Frontend (Next.js)

```bash
cd web

# Install dependencies
npm install

# Dev server (port 3000)
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint
npm run lint
```

### Docker (Cloud Run simulation)

```bash
# Build
docker build -t tpw-lifecycle .

# Run API
docker run -p 8080:8080 -e APP_MODE=api tpw-lifecycle

# Run Dashboard
docker run -p 8080:8080 -e APP_MODE=dashboard tpw-lifecycle
```

### Deploy to GCP

```bash
# One command deploys both API and Dashboard services
gcloud builds submit --config cloudbuild.yaml
```

## Code Style Guidelines

### Python

- **Line length:** 100 characters (ruff config in `pyproject.toml`)
- **Target version:** Python 3.11
- **Imports:** ruff sorts imports automatically (`select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]`)
- **Type hints:** Used where helpful but not obsessively. `mypy` runs with `strict = false` and `ignore_missing_imports = true`.
- **Docstrings:** Every module and public function has a docstring explaining purpose and args.
- **Comments:** Use `# --- Section ---` style dividers for long functions. Inline comments explain *why*, not *what*.
- **Error handling:** Prefer `try/except Exception` with print-logging rather than crashing, especially in action modules (emails, CRM, Slack). Actions should be resilient — if one notification fails, the pipeline continues.
- **Config loading:** Many modules load `config/settings.yaml` at module level using `yaml.safe_load()`. Environment variable overrides use the pattern `TPW__SECTION__KEY=value` (though pydantic-settings is available, most code reads yaml directly).

### TypeScript / React

- **Framework:** Next.js 16 App Router with React Server Components by default.
- **Styling:** Tailwind CSS v4. Utility-first, no custom CSS files beyond `globals.css`.
- **Path alias:** `@/*` maps to `./src/*`.
- **Dynamic rendering:** All data-fetching pages export `const dynamic = "force-dynamic";` because they read from BigQuery and should never be cached.
- **Client components:** Marked explicitly with `"use client";`. Keep client components minimal — only interactivity (search, filters) lives in client components. Data fetching stays in server pages.
- **Component style:** Functional components, explicit prop types, `function` keyword preferred over arrow functions for components.

## Testing Instructions

> **Critical gap:** The `tests/` directory is completely empty. `pyproject.toml` lists `pytest>=7.4` and `pytest-asyncio>=0.21` as dev dependencies, but there are zero test files. No frontend test framework is configured.

When adding tests:
- Use `pytest` for Python unit tests.
- Place tests under `tests/` mirroring the `src/` structure.
- Use `pytest-asyncio` for async test cases (the FastAPI endpoints and notification actions are async-ready).
- Mock BigQuery I/O at `src/data/client.py` level — do not hit real BigQuery in tests.
- Mock external APIs (SendGrid, MessageBird, Slack, CRM) in action tests.

## Security Considerations

### SQL Injection Risk

**Both Python and TypeScript code construct SQL queries via string interpolation.** This is a known pattern in the codebase:

- `src/api/main.py`: `WHERE profile_id = '{profile_id}'`
- `src/data/suppliers.py`: `WHERE profile_id = {int(profile_id)}`
- `src/data/activity.py`: `CAST(profile_id AS STRING) IN ({id_list})`
- `web/src/lib/bigquery.ts`: `WHERE profile_id = '${profileId}'`

**In practice:** `profile_id` values are numeric strings from an internal system, but this pattern is fragile. If you modify these queries, use parameterized queries or BigQuery query parameters instead of string formatting.

### Environment Variables and Secrets

- Never commit `.env.local` or service account JSON files. Both are gitignored.
- The web frontend reads `GOOGLE_APPLICATION_CREDENTIALS_JSON` (base64-encoded service account key) from environment variables. This runs server-side only in Next.js.
- Python reads `GOOGLE_APPLICATION_CREDENTIALS` (path to JSON file) for local development.
- API keys (SendGrid, MessageBird, CRM) are optional stubs — if missing, the code prints a warning and skips the action rather than crashing.

### BigQuery Access

- The Python backend and Next.js frontend both connect directly to BigQuery.
- The retention dataset (`tpw-ga4-bigquery.retention`) is read-write for the pipeline and read-only for dashboards.
- Source tables (GA4, business_development) are read-only.

## Data Flow and Architecture

```
BigQuery (source of truth)
    ↓
Daily Pipeline (7 AM Cloud Scheduler → POST /jobs/daily)
    ↓
├─→ supplier_stats_daily   (one table powers everything)
├─→ signals_daily          (churn scores)
├─→ actions_log            (what we did)
└─→ Slack summary
    ↓
├─→ Sales Dashboard (Streamlit on Cloud Run)
├─→ Modern Dashboard (Next.js on Vercel)
├─→ API (FastAPI on Cloud Run)
└─→ Supplier-facing tools (via API)
```

### The Daily Pipeline (`jobs/daily_pipeline.py`)

1. **Load data** — suppliers, GA4 activity, leads (last 90d)
2. **Calculate stats** — `supplier_stats.calculate()` aggregates views, leads, trends, renewal dates
3. **Calculate signals** — `churn_scorer.calculate()` adds `churn_probability`, `priority_tier` (P1-P4), `risk_factors`, `recommended_action`
4. **Determine actions** — P1 suppliers get CRM tasks; email flows (renewal/re-engagement/monthly) are targeted by `flows.determine_email_actions()` and sent via `emails.send()` in **dry-run by default** (no provider call until `EMAIL_DRY_RUN=false` + a configured email source)
5. **Save to BigQuery** — writes `supplier_stats_daily`, `signals_daily`, `actions_log`
6. **Slack summary** — posts daily stats to configured webhook

### Churn Scoring (`src/signals/churn_scorer.py`)

- Rule-based, ~150 lines, no ML models.
- Baseline 0.10, adds/subtracts based on: days since login/lead, engagement trend, profile views, renewal proximity, plan value, tenure.
- Tiers: P1 (≥0.80), P2 (≥0.55), P3 (≥0.35), P4 (<0.35).
- Thresholds defined in `config/settings.yaml`.

### Key Configuration Files

- **`config/settings.yaml`** — BigQuery project/dataset, source table names, retention table names, churn thresholds, email settings, notification settings.
- **`config/categories.yaml`** — 16 wedding supplier categories with `avg_booking_value`, `inquiry_to_booking_rate`, `avg_views_top10pct`, `avg_leads_top10pct`.

## Deployment

### Cloud Run Services (from single Docker image)

| Service | Mode | Entry Point |
|---------|------|-------------|
| `tpw-lifecycle-api` | `APP_MODE=api` | Uvicorn serving FastAPI |
| `tpw-lifecycle-dashboard` | `APP_MODE=dashboard` | Streamlit |

### Cloud Scheduler

- Daily at 7 AM Amsterdam time: POST to API `/jobs/daily` (or run `python jobs/daily_pipeline.py` directly if triggered differently).

### Next.js Frontend

- The `web/` directory has a `.vercel/project.json`, indicating deployment on **Vercel**.
- It connects to the same BigQuery dataset as the Python backend.

## Important Notes for Agents

1. **Two frontends exist.** There is a Streamlit dashboard (`src/dashboard/app.py`) and a Next.js dashboard (`web/`). They query the same `supplier_stats_daily` table. When adding dashboard features, prefer the Next.js frontend; the Streamlit dashboard is the legacy sales view.

2. **Email actions run in dry-run by default.** The pipeline now wires three email flows (renewal prep, re-engagement, monthly results) via `src/actions/flows.py` (pure targeting) → `src/actions/emails.py` (sending + dedup). A master switch (`config email.dry_run`, overridable with `EMAIL_DRY_RUN`) gates all real sends — while dry-run is on, it computes and logs who *would* be emailed but calls no provider. Going live needs `EMAIL_DRY_RUN=false` + `SENDGRID_API_KEY` **and** a supplier email source: there is no email column in the business/profiles tables, so configure `sources.supplier_email_table` / `supplier_email_column` in `settings.yaml`. Until then, every supplier's `email` is NULL and no emails are targeted. Dedup is enforced via the `email_log` table (`recent_sends()`); only real sends are logged there.

3. **Config is loaded at module level.** Many Python modules open `config/settings.yaml` at import time using `yaml.safe_load()`. If you add new config fields, update both `config/settings.yaml` and the code that reads it.

4. **No `src/analytics/benchmarks.py` or `src/signals/renewal.py`.** `docs/ARCHITECTURE.md` references these, but they do not exist. Benchmark logic lives in `projected_value.py`; renewal logic is inline in `churn_scorer.py` and `supplier_stats.py`.

5. **Dutch language for customer-facing content.** All email templates in `src/templates/emails/` are in Dutch. Internal dashboards and code comments are in English.

6. **Path hacks for imports.** `jobs/daily_pipeline.py` and `src/api/main.py` use `sys.path.insert(0, str(Path(__file__).parent.parent / "src"))` to make `from data import ...` work without package installation. Keep this pattern when adding new runnable scripts.

7. **One EU `retention` dataset; sources span locations (footgun).** `retention` is in **EU** (all platform tables: supplier_exposure_daily, supplier_targeting, cohort_assignment, retention_directives, supplier_stats_daily, signals_daily, actions_log). It was migrated US→EU on 2026-06-05 (`jobs/migrate_retention_to_eu.py`) — it holds EU supplier PII and must stay in the EU; the old `retention_eu` workaround dataset was folded in and dropped. `config.bigquery.dataset` and `dataset_eu` now both point at `retention` (EU). **Always create datasets with an explicit `.location`** — the BigQuery client defaults to US, which is exactly how this got mislocated. You still **cannot** join across locations in one BQ job: GA4 = EU and `churn_prediction` (business_development) = **europe-west3** are different locations, so the business×exposure merge is still aggregate-each-side-then-join-in-pandas. `client.query()`/`query_eu()` (pandas_gbq) auto-detect location for reads (works for both EU and europe-west3); `client.write()` passes `location=EU`; use `client.execute()` for server-side EU DDL/DML.
