# Phase-0 Confirmation Spikes

**Date:** 2026-06-05
**Status:** Ready to create as tickets (Linear project: **B2B Retention**)
**Source:** the integration unknowns in [19 architecture](19_system_architecture.md) / [20 plan](20_phased_implementation_plan.md) (gate **G0**)

Each spike is **investigation only** — produce a documented answer + effort estimate, not a build. Gate G0 (and the Stage-1 build) is blocked until the P0/P1 spikes are closed.

> **Scope note:** `customer_journey` (the **B2C venue flow**) is explicitly **out of scope** — not woven into retention. Supplier emails + couple-newsletter go via **`marketing_flow`** (Bird); the dashboard feed is a **BigQuery reporting table** the supplier dashboard already reads; holdout flags live in BigQuery (synced to Elastic). No separate serving layer.

## Summary

| # | Spike | Owner | Priority | Effort | Blocks |
|---|---|---|---|---|---|
| 1 | Elastic `retention_boost` mechanism | **Elastic owner** | **P0** (critical path) | M | Core lever (Stage-1 boost) |
| 2 | Exposure rollup + dashboard feed | me (analytics_reporting + BQ) | P1 | S–M | WS-A `supplier_exposure_daily` |
| 3 | Exposure features in churn model | me (churn_prediction) | P1 | M | Better targeting (not Stage-1-blocking) |
| 4 | Supplier email + couple-newsletter via Bird | me (marketing_flow) | P1 | S–M | Email + newsletter levers |
| 5 | Scraper cohort trigger | me (profile_auto_complete) | P1 | S | Bundle step 2 (profile optimize) |
| 6 | `moneybird.*` → `profile_id` join | me (invoice_service) | P2 | S | Accurate value/churn measurement |

**Critical path:** Spike 1 (Elastic) — the core lever and only externally-owned dependency. Front-load it. Spike 2 is the foundation everything reads from.

---

## Spike 1 — Elastic `retention_boost` mechanism (premium-aware)  · P0 · Elastic owner

**Context:** The redistribution lever needs to give at-risk/low-exposure suppliers a placement boost in the **free/organic** ranking layer **without touching paid premium spots** (premium is a revenue product).

**Questions:**
- How is supplier ranking scored today? How are **premium spots** implemented (pinning / boost / separate query)?
- Can we add a per-supplier `retention_boost` signal via `function_score` **only in the non-premium layer**? Magnitude knob + bounds?
- How does the ranker read the **holdout flag** so control suppliers are never boosted?
- How do we measure couple-experience impact (CTR / view→lead conversion of boosted placements) and instantly disable?

**Definition of done:** documented mechanism (field + scoring + magnitude + holdout-aware + kill-switch) + guardrail metrics + implementation effort estimate.

---

## Spike 2 — Exposure rollup + dashboard feed  · P1 · analytics_reporting + BQ

**Context:** Stage-1 needs `supplier_exposure_daily` (views, impressions, rank, trend per profile); the supplier dashboard needs a `supplier_exposure_monthly` feed (views, rank, benchmark, TPW-contributed views). `analytics_reporting` already produces `monthly_profile_stats`.

**Questions:**
- Does `analytics_reporting` already emit reusable per-supplier exposure aggregates? Rollup inside it, or a thin retention job over its tables? Freshness/schedule?
- Where does **rank** come from (Elastic snapshot) and how is it joined?
- Cross-region handling (GA4 EU vs `business_development` eu-west3)?
- Confirm the dashboard reads a BigQuery reporting table (so the exposure feed is just a sibling table — no serving layer).

**Definition of done:** reuse-vs-build decision + `supplier_exposure_daily`/`_monthly` schemas + schedule.

---

## Spike 3 — Exposure features in the churn model  · P1 · churn_prediction

**Context:** Live model runs ~100% precision but **27.6% recall** — it lacks exposure features, the #1 driver.

**Questions:**
- Training/deploy pipeline, feature inputs, retrain cadence?
- Add **exposure level + trend** and **dashboard-engagement recency** features — ingestion path? Effort? Expected recall lift on holdout?
- Fallback: consume current scores + overlay a rule-based exposure signal?

**Definition of done:** feasibility + plan + expected recall-lift estimate (or fallback decision).

---

## Spike 4 — Supplier email + couple-newsletter via Bird  · P1 · marketing_flow

**Context:** Two delivery needs, both via `marketing_flow` (Bird) — **not** customer_journey:
(a) supplier monthly-results email; (b) couple-newsletter "featured suppliers" block (additive exposure, mechanic B).

**Questions:**
- How to submit a **supplier email directive** to Bird (template, recipient, variables, unsubscribe/compliance, rate limits)?
- How are couple newsletters assembled/sent (content catalog, Bird campaigns)? Cadence/audience size? Can we inject a dynamic "featured suppliers" block from a supplied list?
- How to attribute resulting views back (UTM/tracked links) for "TPW-contributed views"?
- How is the **holdout** respected (never email/feature control)?

**Definition of done:** email-directive contract + newsletter-injection mechanism + attribution approach.

---

## Spike 5 — Scraper cohort trigger  · P1 · profile_auto_complete

**Context:** Bundle step 2 — optimize the profile so boosted views convert.

**Questions:**
- How is the scraper invoked (HTTP, `run_all.sh` batch, queue)? Can we trigger it for a list of `profile_id`s?
- What does it change, and does it require supplier opt-in / go-live approval?
- Throughput for the pilot cohort (~80–300)? Holdout respected?

**Definition of done:** trigger interface + throughput + opt-in model.

---

## Spike 6 — `moneybird.*` → `profile_id` join  · P2 · invoice_service

> **Answered in [doc 27](27_spike6_invoice_profile_join_answer.md) (YOO-233, Done).** Two corrections surfaced live: the table is **`moneybird.mb-2015-2020` + `moneybird.mb-contacts`** (Drive-backed external), **not** `finance_dashboard.matched_invoices` (which does not exist); coverage is **98.6% of active paid suppliers**.

**Context:** the Moneybird invoice tables (`moneybird.mb-2015-2020` + `moneybird.mb-contacts`) are the revenue source of truth for ARR/churn-value/right-pricing and outcome measurement.

**Questions:**
- Grain of `moneybird.mb-2015-2020`? Key to supplier (`klantnummer` → `mb-contacts.customer_id` / `companies_profiles.moneybird_customer_id` → `profile_id`)? Match/coverage rate?
- Reliable per-supplier ARR + churn-value derivation?

**Definition of done:** documented join key + coverage + a per-supplier revenue view. (Stage-1 can proceed on `business_development.plan_value` as interim.)

---

## Next
Close P0/P1 to clear gate **G0**; then start Phase-1 WS-A (`supplier_exposure_daily`).
