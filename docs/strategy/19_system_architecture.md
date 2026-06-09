# System Architecture

**Date:** 2026-06-05
**Status:** Design — basis for build-order and phased plan
**Builds on:** [17_refined_retention_strategy.md](17_refined_retention_strategy.md), [18_value_add_bundle_and_pilot.md](18_value_add_bundle_and_pilot.md)

How the value-add bundle + pilot live in TPW's existing systems.

---

## Core principle: a decisioning engine that integrates, not a new monolith

The retention platform (this repo) is the **supplier-retention brain**: it ingests data, computes the targeting signal, assigns the holdout, and **emits directives** to surfaces it does not own. Crucially, **delivery and serving already exist** in adjacent services — we integrate with them rather than rebuild.

```
                         ┌─────────────────────────────────────┐
   DATA (BigQuery)       │   RETENTION DECISIONING ENGINE       │
   monthly_profile_stats │   (this repo, extended)              │
   view_item / _list ───▶│   1 exposure aggregation             │
   searchconsole         │   2 targeting signal (exposure/      │
   business_development   │     tenure/engagement)              │
   Elastic rank snapshot │   3 cohort + HOLDOUT assignment      │
                         │   4 directive generation             │
                         │   5 outcome tracking                 │
                         └───────┬───────┬───────┬───────┬──────┘
            boost directive      │       │       │       │   dashboard feed
            ┌────────────────────┘       │       │       └────────────┐
            ▼                            ▼       ▼                     ▼
   ┌──────────────┐         ┌────────────────────────┐      ┌──────────────────┐
   │  ELASTIC     │         │ marketing_flow (Bird.com)│      │ Supplier dashboard│
   │  (ranking)   │         │ supplier emails + couple │      │ reads BQ reporting│
   │ free layer;  │         │ newsletter               │      │ table + TPW DB    │
   │ premium kept │         └────────────────────────┘      │ requests          │
   └──────────────┘         ┌────────────────────────┐      └──────────────────┘
                            │ profile_auto_complete    │
                            │ (scraper optimize)       │   holdout flags: BigQuery → Elastic
                            └────────────────────────┘   (NOT customer_journey — that's B2C venue)
```

---

## Full TPW ecosystem (system map)

The retention brain is thin — it orchestrates these existing services:

| Repo / system | Role | Retention integration |
|---|---|---|
| **tpw-retention** (this) | Retention decisioning brain | targeting + holdout + directives + measurement |
| **churn_prediction** | Live churn model (Streamlit + segmented XGBoost; ~100% precision but **27.6% recall** @0.65) | **Extend with exposure features** (the missing driver → should lift recall); owns `business_development` |
| **analytics_reporting** | GA4 reporting producer (`monthly_profile_stats`, dimensional data, supplier reports) | **Source/producer of exposure data — reuse/extend, don't rebuild** |
| **profile_auto_complete** | Scraper / profile auto-complete + onboarding | Trigger for profile optimization (bundle step 2) + onboarding lever |
| **customer_journey** | **B2C venue flow** | **Out of scope — kept separate from retention** |
| **marketing_flow** | Bird.com newsletter / marketing engine | **Supplier email + couple-newsletter delivery** |
| **gads_api** | Venue Google Ads automation (the tripled budget) | Venue track (separate); source of venue exposure inflation |
| **invoice_service** | Moneybird → `finance_dashboard.matched_invoices` | **Revenue source of truth** — ARR / churn-value / right-pricing |

---

## Integration contracts (what we emit, to which system, how)

| Surface | System | Mechanism / contract | Build |
|---|---|---|---|
| **Exposure data** | `monthly_profile_stats` (GA4, 388M), `searchconsole`, Elastic rank snapshot | Aggregate **in BigQuery** → `supplier_exposure_daily` | New |
| **Redistribution** | **Elastic** | Per-supplier `retention_boost` weight on the supplier doc; ranking applies it via `function_score` **in the non-premium layer only**; premium stays its own higher-tier boost | New (needs Elastic owner) |
| **Couple newsletter** | `marketing_flow` (Bird.com) | Feature-list directive → campaign input | New (small) |
| **Supplier emails / newsletter** | `marketing_flow` (Bird.com) | Email + featured-suppliers directives via Bird — **NOT** the SendGrid prototype, **NOT** customer_journey | New (small) |
| **Profile optimization** | `profile_auto_complete` (scraper) | Optimize-list directive → scraper trigger | New (small) |
| **Dashboard exposure feed** | BQ reporting table the dashboard reads | New sibling table `supplier_exposure_monthly` (views, rank, benchmark, **TPW-contributed views**) — don't mutate `monthly_profile_stats` | New |
| **Holdout flags** | BigQuery `cohort_assignment` → synced to Elastic | Emitters (batch) read from BQ; Elastic boost reads a synced flag | New |
| **Sales value recap** | internal Next.js (`web/`) | Reads BQ | Extend |

---

## Key technical decisions

1. **Integrate, don't rebuild delivery.** Emails/newsletters go through **Bird.com via `marketing_flow`** — **not** `customer_journey` (that's the B2C venue flow, kept separate). No separate serving layer: the dashboard feed is a **BigQuery reporting table the dashboard already reads**, and holdout flags live in BigQuery (synced to Elastic). The repo's SendGrid `emails.py` (D1–D3) is **deprecated**.
2. **Reuse `analytics_reporting`, don't rebuild exposure.** It already produces `monthly_profile_stats` + dimensional GA4 data; `supplier_exposure_daily` should be a thin rollup over its outputs (or built *inside* that service), not a parallel pipeline. Still aggregate in BigQuery (388M/206M rows are too big to pandas — scheduled incremental SQL, partition pruning).
3. **Cross-region** (churn_prediction = eu-west3, GA4/SC = EU): aggregate each side to small per-supplier tables, then join (no single cross-region query).
4. **Redistribution = an Elastic boost field**, applied only in the free/organic layer; **premium spots untouched** (paid product preserved). Exact `function_score` shape to confirm with the Elastic owner.
5. **Holdout integrity is central and enforced everywhere** (see below).
6. **Targeting = extend the live `churn_prediction` model, not a parallel scorer.** It already segments new-vs-legacy (matches our tenure finding) and runs at ~100% precision but only **27.6% recall** — it misses 72% of churners precisely because it's lead/activity/business/call-centric and **lacks exposure features**. Adding exposure level+trend (+ dashboard-engagement) features there is the highest-value model change. The retention platform consumes its scores to target the bundle. (A simple rule-based override remains a fallback.)

7. **Revenue source of truth = `invoice_service` (`finance_dashboard.matched_invoices`, Moneybird)** — use it for ARR, churn-value, and right-pricing inputs, not `business_development.plan_value`.
7. **Dashboard gets a new sibling reporting table**, not edits to `monthly_profile_stats` (which the live dashboard depends on).

---

## Data model (new tables, `retention` dataset)

| Table | Purpose |
|---|---|
| `supplier_exposure_daily` | profile_id, date, category, impressions, profile_views, show_phone, website_open, purchase, rank_position, derived trends |
| `supplier_targeting` | profile_id, segment (non-venue/venue/retail), exposure level+trend, first_term, term_months, dash_engagement_recency, at_risk_score, bundle_eligible |
| `cohort_assignment` | profile_id, experiment_id, arm (treatment/control), cohort, assigned_at — **stable hash; single source of truth** |
| `retention_directives` | profile_id, type (boost/newsletter/optimize/email), channel, params, arm, status, created_at, delivered_at |
| `outcomes` | profile_id, experiment_id, arm, exposure_pre/post, engagement_pre/post, renewed, plan_end |
| `supplier_exposure_monthly` | dashboard feed: views, rank, category benchmark, **TPW-contributed views** |

---

## Holdout enforcement (the integrity backbone)

`cohort_assignment` is the **single source of truth** in BigQuery, **synced to Elastic** as a boost flag; batch emitters read it from BigQuery directly. **Every emitter filters out control before acting** — no boost, no newsletter, no scraper, no extra email for control suppliers — and `retention_directives` records the arm so we can prove no control contamination. Without this the pilot is unmeasurable.

---

## Build order — Stage-1 pilot MVP (minimum slice to test "can we move exposure")

1. `supplier_exposure_daily` aggregation (BQ scheduled SQL).
2. `supplier_targeting` — segment + low-exposure photographer cohort.
3. `cohort_assignment` — stable treatment/control split; publish to serving + Elastic flag.
4. **Elastic `retention_boost`** directive (treatment, free layer) — the core lever.
5. Newsletter feature directive → `marketing_flow` (treatment).
6. Scraper optimize trigger (treatment).
7. Monthly-results email via Bird (engagement lever, treatment).
8. **Measurement:** exposure lift (treatment vs control from `supplier_exposure_daily`), dashboard engagement (`bedrijven_pageview_events`), couple-experience guardrails.

*(The full dashboard exposure-reframe and `supplier_exposure_monthly` feed are Stage-2 — not required to test whether the levers move exposure.)*

---

## Risks / dependencies

- **Elastic boost** must not degrade couple experience or cannibalize premium — careful scoring + guardrail metrics. Biggest unknown; needs the Elastic owner.
- **Holdout leakage** across 3 repos + Elastic — mitigated by central enforcement.
- **BQ aggregation cost** on 200–400M-row tables — incremental, partition-pruned.
- **Cross-team coordination** (retention repo, customer_journey, marketing_flow, Elastic, TPW DB) — the real-world critical path.

---

## To confirm with service owners
- Elastic: how to add/apply a `retention_boost` field within the existing (premium-aware) ranking.
- `analytics_reporting`: where the exposure rollup should live (inside it vs a thin retention job over its tables).
- `churn_prediction`: ownership/path to add exposure features to the live model.
- `marketing_flow`: the supplier email-directive + "featured suppliers" injection (both via Bird). *(customer_journey = B2C venue flow, intentionally not used.)*
- `profile_auto_complete`: trigger interface for a cohort list.
- `invoice_service`: join key from `matched_invoices` to `profile_id` for revenue/churn-value.

---

## Next steps
1. Confirm the four integration interfaces above.
2. Size the Stage-1 cohort from the renewal calendar.
3. Phased implementation plan (this architecture → tickets).
