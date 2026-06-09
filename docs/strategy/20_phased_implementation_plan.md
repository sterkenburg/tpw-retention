# Phased Implementation Plan

**Date:** 2026-06-05
**Status:** Plan — execution roadmap for docs 17–19
**Builds on:** [17 strategy](17_refined_retention_strategy.md), [18 bundle+pilot](18_value_add_bundle_and_pilot.md), [19 architecture](19_system_architecture.md)

Turns the architecture into sequenced phases with deliverables, owning repos, dependencies, and **decision gates**. Guiding rule: **spend the least to learn the most** — gate every expensive build on evidence the prior step worked.

---

## Phasing at a glance

| Phase | Goal | Gate to exit |
|---|---|---|
| **0 — Foundations & confirmations** | De-risk: confirm interfaces, size cohort, lock experiment design | **G0:** interfaces confirmed + cohort sized + design signed off |
| **1 — Stage-1 pilot MVP** | Prove the levers *move exposure & engagement* (clean holdout) | **G1:** exposure lift vs control + engagement up + couple guardrails intact |
| **2 — Deepen (model + dashboard)** | Durable assets: exposure features in the model; exposure-first dashboard | **G2:** model recall improved; dashboard reframe live to cohort |
| **3 — Stage-2 readout & scale** | Prove *retention* impact, then roll out | **G3:** renewal uplift vs control → roll out; else revisit thesis |

**Honest timeline:** Phase 0 ~1–2 wks · Phase 1 build ~4–6 wks + run 6–8 wks · Phase 2 ~4–6 wks (overlaps Phase 1 run) · Phase 3 run 6–12 mo. Causal retention readout is ~9–15 months out — Phase 1 gives a *mechanism* signal in ~2–3 months.

---

## Phase 0 — Foundations & confirmations

**Can start now (no external dependency, this repo / BigQuery):**
- Spec `supplier_exposure_daily` (rollup over `analytics_reporting` outputs).
- Draft targeting logic (segment + exposure level/trend + first-term + at-risk).
- Draft stable-hash holdout assignment.

**Confirmations (each a short spike with the owning team):**
| Item | Owner repo/team |
|---|---|
| Elastic `retention_boost` mechanism (premium-aware) | Elastic / marketplace |
| Where the exposure rollup lives | `analytics_reporting` |
| Path to add exposure features to the live model | `churn_prediction` |
| Supplier email-directive + "featured suppliers" injection (Bird) | `marketing_flow` |
| Scraper cohort-trigger interface | `profile_auto_complete` |
| `matched_invoices` → `profile_id` join | `invoice_service` |

**Analytical deliverables:** size the Stage-1 cohort from the renewal calendar; define the "low-exposure" threshold + Stage-1 lift bar; lock the experiment design (arms, randomization unit = profile_id, primary/secondary endpoints, guardrails, MDE/power).

**G0:** all interfaces confirmed, cohort sized, experiment design signed off.

---

## Phase 1 — Stage-1 pilot MVP ("can we move exposure?")

Minimum slice to test the mechanism. Workstreams:

| WS | Deliverable | Repo |
|---|---|---|
| **A — Data** | `supplier_exposure_daily` (rollup); cross-region join to `business_development`; revenue join from `matched_invoices` | this repo / `analytics_reporting` |
| **B — Targeting** | segment classifier (non-venue/venue/retail) + low-exposure photographer (±pooled) cohort | this repo |
| **C — Holdout** | `cohort_assignment` (stable hash) in BQ → synced to Elastic flag; **enforcement check in every emitter** | this repo |
| **D1 — Boost** | Elastic `retention_boost` on treatment, **free layer only** | Elastic |
| **D2 — Newsletter** | feature-list directive → campaign | `marketing_flow` |
| **D3 — Optimize** | optimize-list trigger (treatment) | `profile_auto_complete` |
| **D4 — Email** | monthly-results email via Bird (treatment) | `marketing_flow` |
| **E — Measurement** | exposure lift (treatment vs control), dashboard engagement (`bedrijven_pageview_events`), couple guardrails (boosted-placement CTR/conversion), directives audit | this repo |

**Critical path & biggest risk:** **D1 (Elastic boost)** — it's the core lever and the hardest integration (premium-aware). Front-load it.

**G1 (exit):** treatment exposure lift ≥ bar vs control; dashboard engagement up; couple CTR/conversion not degraded; zero control contamination. **If G1 fails → stop and iterate; do not start the churn readout.**

---

## Phase 2 — Deepen (model + dashboard)

Starts during the Phase-1 *run* (these strengthen targeting/proof and are valuable regardless of G1, but full rollout gates on G1/G2).

| WS | Deliverable | Repo |
|---|---|---|
| **F — Model** | add exposure level+trend + dashboard-engagement features to the live churn model; re-evaluate recall/precision (target: lift the 27.6% recall) | `churn_prediction` |
| **G — Dashboard** | `supplier_exposure_monthly` feed (views, rank, benchmark, **TPW-contributed views**); dashboard leads with exposure; surface "TPW's contribution" | `analytics_reporting` + dashboard team |
| **H — Sales recap** | per-supplier value-recap view for renewal calls | this repo (`web/`) |

**G2:** model recall measurably improved on holdout; dashboard reframe live to the pilot cohort.

---

## Phase 3 — Stage-2 readout & scale

- Pool thin-lead non-venue categories for adequate N; **maintain the randomized holdout**; run through renewal decisions.
- **Primary endpoint:** renewal rate treatment vs control. **Secondary:** renewal-intent/NPS, sustained exposure, engagement.
- **G3 decision:**
  - **Positive →** roll the bundle out to all non-venue; fold targeting into BAU; keep a small permanent holdout for ongoing measurement.
  - **Null →** the exposure→retention link wasn't causal at achievable lift; revisit the thesis (don't scale on faith).

**Parallel tracks (independent of the pilot):**
- **Venue track** — proof/attribution + conversion (uses `gads_api` engine; `matched_invoices` for ROI).
- **Wrong-model retail** — right-pricing/tiering (rings/suits/catering).
- **Owned-channel growth** — grow the non-venue exposure pie (newsletter/app/content) to offset organic decline.

---

## Cross-cutting (every phase)
- **Holdout discipline:** one source of truth; every emitter filters control; audit via `retention_directives`.
- **Couple-experience guardrails:** monitor boosted-placement CTR/conversion; protect premium revenue; cap views drawn from non-churning top suppliers.
- **Measurement-first:** instrument before you intervene.

## Dependencies / risks
- **Elastic boost** is the critical path and the top risk (couple experience + premium). Front-load the spike (Phase 0) and the build (Phase 1).
- **Cross-team coordination** across 8 repos is the real-world bottleneck — Phase 0 confirmations exist to surface blockers early.
- **BQ aggregation cost** on 200–400M-row tables — incremental, partition-pruned.

## Next step
Phase 0: kick off the seven confirmations + cohort sizing, and start the no-dependency foundation work (`supplier_exposure_daily` spec, targeting logic, holdout design).
