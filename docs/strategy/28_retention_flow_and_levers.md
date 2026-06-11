# 28 — Lifecycle Flow & Lever Catalog

**Date:** 2026-06-09
**Status:** Design — the end-to-end supplier-lifecycle flow and the full lever set
**Builds on:** [17 strategy](17_refined_retention_strategy.md), [18 bundle+pilot](18_value_add_bundle_and_pilot.md), [19 architecture](19_system_architecture.md), [20 phased plan](20_phased_implementation_plan.md). Spike answers: [23](23_spike2_exposure_rollup_answer.md)–[27](27_spike6_invoice_profile_join_answer.md).

This pulls the whole decisioning flow into one picture and catalogs **every lever** —
the four built for the Stage-1 exposure pilot plus the populations and levers that
extend coverage to the *other* validated churn drivers.

---

## TL;DR

| | |
|---|---|
| **The gap it closes** | The four built levers (`boost`, `optimize`, `newsletter`, `email`) all attack **one** validated driver — *exposure*. The multivariate work ([churn-drivers]) found three: **exposure, first-term tenure, dashboard engagement**. Two were unserved. |
| **The structural change** | A **segmentation** step routes each supplier to a *population* (new / at-risk / high-value / churned), and each population gets its own **experiment** + lever-set. Levers are now scoped per experiment, so adding one never disturbs the live `stage1_exposure` pilot. |
| **Journey layer (built)** | `signals/journey.py` places each supplier in one lifecycle **stage** and maps it to next-best levers; `jobs/preview_journey.py` is a read-only dry-run of the whole journey on real suppliers. Makes the flow observable before any channel is enabled (§1a). |
| **What's added now (code)** | **`onboarding`** lever + experiment (first-term tenure) and **`winback`** lever + experiment (lapsed suppliers). Both gated (`onboarding_enabled`, `winback_enabled` = false), computed-but-inert until their cohorts populate. |
| **What's proposed (doc-only)** | `offer` (right-pricing), `reengage` (dashboard nudge — blocked on login telemetry), `alert` (CSM hand-off), `survey` (feedback loop). |
| **Decisions locked** | Segmentation = yes (multi-experiment). Win-back = in scope. Onboarding + winback = added. Offer/reengage/alert/survey = staged, greenlit individually. |

---

## 1. End-to-end flow

```
┌─ WS-A/B  SIGNALS ──────────────────────────────────────────────┐
│  exposure rollup        monthly_profile_stats → supplier_exposure_daily
│  churn drivers          targeting.py: exposure level/trend, first_term,
│                         term_months, days_since_last_view
│  live churn model       churn_prediction.business_development (external)
│                         → blended into at_risk_tier (Spike 3 / doc 24)
│  revenue                business_development.plan_value (now)
│                         → Moneybird ARR (Spike 6 / doc 27, gated on Drive scope)
│        ▼ writes
│  supplier_targeting     {profile_id, at_risk_tier, drivers, first_term,
│                          renewal_status, plan_value, …}
└────────────────────────────────────────────────────────────────┘
            ▼
┌─ SEGMENTATION (new) ───────────────────────────────────────────┐
│  route each supplier to a POPULATION → its lever-set            │
│  (cohort.py EXPERIMENTS[*].eligibility selects the population)   │
└────────────────────────────────────────────────────────────────┘
            ▼
┌─ WS-C  COHORT / EXPERIMENT ────────────────────────────────────┐
│  cohort_assignment      treatment / control  (single source of truth)
│  one experiment PER population: stage1_exposure · onboarding · winback
│  stable-hash split, append-only, baseline-balanced (cohort.py)  │
└────────────────────────────────────────────────────────────────┘
            ▼
┌─ WS-D  DECISION / DIRECTIVES (the brain) ──────────────────────┐
│  generate(experiment_id): for each TREATMENT supplier × each    │
│  lever whose `experiments` includes this experiment →           │
│  retention_directives {type, channel, params, status, arm}      │
│  • holdout: control never produced + leak AssertionError         │
│  • gating: status='gated' until the channel enable-flag flips    │
└────────────────────────────────────────────────────────────────┘
            ▼ (each channel polls dispatchable treatment rows)
┌─ DELIVERY (external systems own this) ─────────────────────────┐
│  Elastic ............. boost                                     │
│  Bird/marketing_flow . email · newsletter · onboarding · winback · survey
│  profile_auto_complete optimize                                 │
│  CSM/CRM webhook ..... alert (human touch)                      │
│  Billing/Moneybird ... offer fulfillment                        │
└────────────────────────────────────────────────────────────────┘
            ▼
┌─ WS-E  MEASUREMENT ────────────────────────────────────────────┐
│  tpw_contributed_views  (UTM attribution → GA4, doc 25 §3)      │
│  contamination_audit    (holdout integrity)                     │
│  outcome vs control     renewal rate, churn rate, ARR retained  │
│  recall-lift backtest   (vs churn_prediction labels, doc 24)    │
│  feedback loop          survey/NPS responses → back into signals │
└────────────────────────────────────────────────────────────────┘
```

The one structural addition versus the prior architecture (doc 19) is the
**segmentation** step. Today's flow implicitly assumes a single population
(`stage1_exposure` at-risk suppliers). The new levers target *different*
populations — and a brand-new supplier and a churned supplier cannot live in the
same experiment. Segmentation makes the population explicit and maps each
unserved driver to a population that now has a lever.

### 1a. Journey layer (built) — lifecycle stage + next-best-action

`signals/journey.py` makes the segmentation **observable**: it places each supplier in
a single lifecycle **stage** from columns already in `supplier_targeting` (no new data)
and maps the stage to its next-best levers (single-sourced from `directives.LEVERS`).
`jobs/preview_journey.py` is a **read-only dry-run** — it dispatches nothing, it just
shows the journey on real suppliers and the gate blocking each action. This is what
turns the flat catalog into an inspectable, ordered path while every channel is gated.

Stages (priority order, first match wins) and the live readout (latest snapshot,
N=1,444):

| Stage | Definition | Next-best action | Count |
|---|---|---|---:|
| `lapsed` | `renewal_status` not retained (churned) | `winback` | 0 |
| `onboarding` | active, `first_term` | `onboarding` | 217 |
| `renewal_window` | active, `0 ≤ days_until_renewal ≤ 60` | `boost` + `email` | 63 |
| `at_risk` | active, `at_risk_tier ∈ {P1,P2}` | full stage-1 set | 175 |
| `healthy` | retained / low-risk (incl. `already_renewed`) | monitor (no directive) | 989 |

> **`already_renewed` is retained, not churned.** Live data shows the only non-active
> status is `already_renewed` (a *future* paid term exists) — there are **zero genuinely
> churned rows** in targeting (it's active-only). So `lapsed` = 0 today, consistent with
> the winback churned-feed gap (§5). The retained allowlist lives in
> `targeting.RETAINED_STATUSES` and is shared by the journey stage and winback eligibility.

Still ahead for this layer: a **persisted `supplier_journey` table** (today it's a
derived view) and **event triggers** (today it's batch) — see §4.

---

## 2. Segmentation — populations → lever-sets

| Population | Definition (`eligibility` mode) | Lever-set | Experiment |
|---|---|---|---|
| **New / first-term** | `first_term == True` (year-1 cliff: 38% vs 12%) | `onboarding` (+ `optimize`) | `onboarding` |
| **Established at-risk** | low-exposure + tenure, not high-value | `boost` · `optimize` · `email` · `newsletter` | `stage1_exposure` |
| **High-value at-risk** | at-risk **AND** top ARR band | above **+ `offer` + `alert`** *(proposed)* | `stage1_exposure` (value stratum) |
| **Already churned** | `renewal_status != 'active'` (lapsed) | `winback` | `winback` |
| **All treatment (any pop)** | — | `survey` *(proposed)* | per-experiment |

`cohort.py` implements the routing via an `eligibility` mode per experiment:
`category_bundle` (stage1), `first_term` (onboarding), `churned` (winback).
`generate(experiment_id)` in `directives.py` then emits only the levers whose
`experiments` list contains that experiment.

---

## 3. Lever catalog

Drivers: **E** = exposure · **T** = first-term tenure · **G** = dashboard
engagement · **V** = value/price. ✅ built · 🟡 proposed.

| # | type | channel | enable_flag | driver | trigger | dep / blocker |
|---|---|---|---|---|---|---|
| ✅1 | `boost` | elastic | `elastic_enabled` | E | at-risk in treatment | YOO-228 (Elastic) |
| ✅2 | `optimize` | profile_auto_complete | `scraper_enabled` | E | paired w/ boost | opt-in model (doc 26) |
| ✅3 | `newsletter` | bird_marketing_flow | `bird_enabled` | E | slot available | Bird assembly (doc 25) |
| ✅4 | `email` | bird_marketing_flow | `bird_enabled` | E | monthly cadence | Bird API (doc 25) |
| ✅5 | `onboarding` | bird_marketing_flow | `onboarding_enabled` | **T** | enrollment + day 0/30/60/90 | sequence design |
| ✅6 | `winback` | bird_marketing_flow | `winback_enabled` | reactivation | lapsed ≤ 6 mo | **churned-supplier source** (§5) |
| 🟡7 | `offer` | bird (comms) + billing (fulfill) | `offer_enabled` | **V** | high-value at-risk | **Moneybird ARR** (doc 27) to size |
| 🟡8 | `reengage` | bird_marketing_flow | `reengage_enabled` | **G** | `days_since_login` high | **blocked: login telemetry** (doc 24) |
| 🟡9 | `alert` | csm_webhook | `csm_enabled` | V (tail) | high-value at-risk | CSM routing surface |
| 🟡10 | `survey` | bird_marketing_flow | `bird_enabled` | measurement | post-intervention | — |

Levers **1–6 are registered in `directives.py::LEVERS`** today (each tagged with
its `experiments`). Levers 7–10 are specified here; their `LEVERS` entries land
when the owning decision (§5) is greenlit. Built lever entries for the two new ones:

```python
"onboarding": {  # experiments: ["onboarding"]
    "channel": "bird_marketing_flow", "enable_flag": "onboarding_enabled",
    "params": {"sequence": "first_90d",
               "steps": ["welcome","profile_push","first_results","renewal_runway"],
               "exposure_first": True},
},
"winback": {     # experiments: ["winback"]
    "channel": "bird_marketing_flow", "enable_flag": "winback_enabled",
    "params": {"campaign": "reactivation", "max_lapsed_months": 6},
},
```

---

## 4. Cross-cutting (every lever inherits these)

- **Holdout — structural.** Directives are generated only for
  `cohort.treatment_ids(experiment_id)`; `generate()` raises `AssertionError` if any
  control id leaks. New levers inherit this for free **provided they read their own
  experiment's treatment ids**. No channel may build its own audience.
- **Gating.** Each lever's `enable_flag` defaults to `false` in `settings.yaml`.
  Directives are computed and stored `status='gated'` until the flag flips — the
  brain is fully testable now; go-live is a single flag-flip.
- **Sequencing / frequency cap (new plumbing).** With 6–10 levers we need an
  escalation ladder (e.g. email → newsletter → `alert`) and a **cross-channel
  frequency cap**, not just per-lever `dedup_days`. Not required for the 4-lever
  stage1 pilot; required before multiple levers fire at one supplier.
- **Trigger model.** Stage1 is batch/monthly. The journey layer (§1a) now computes a
  per-supplier stage each run, which is the hook an event path would fire on. `offer`,
  `reengage`, `alert` are naturally **event-triggered** (drop/lapse detected → fire);
  decide whether the flow stays batch or gains an event path before those go live.

---

## 5. Decisions & open follow-ups

**Locked this round:**
1. **Segmentation is a real stage** — multiple experiments (`onboarding`, `winback`)
   rather than one cohort. ✔
2. **Win-back is in scope** — the flow now covers already-lapsed suppliers, not just
   pre-churn. ✔
3. **`onboarding` + `winback` added** to `LEVERS`, `EXPERIMENTS`, and `settings.yaml`
   (gated). ✔
4. **Journey layer built** (§1a) — `signals/journey.py` (lifecycle stage +
   next-best-action) and `jobs/preview_journey.py` (read-only dry-run). Run live:
   217 onboarding / 175 at-risk / 63 renewal-window / 989 healthy / 0 lapsed. ✔

**Open (owner action before these populate / go live):**
- ~~**Winback churned-supplier source.**~~ **✔ Resolved 2026-06-11** — the
  ended-terms feed (`suppliers.get_lapsed()`, doc 29 §2.5) adds recently-lapsed
  suppliers (≤6 mo) to targeting with `renewal_status='lapsed'`; journey `lapsed`
  stage and winback eligibility populate (138 live). Enrolment is deliberately
  deferred until the winback sequence is designed. The same feed builds the
  `outcomes` table (`jobs/build_outcomes.py`) — renewal labels for Stage-2 and
  the doc-24 backtest.
- **Onboarding sequence design.** The day-0/30/60/90 step content + Bird templates.
- **Offer lever (`#7`).** Confirm right-pricing-via-offer is in pilot scope (it has a
  **billing side-effect**); it needs **Moneybird ARR** (doc 27, gated on Drive scope)
  to size offers by real revenue.
- **Reengage lever (`#8`).** Blocked on real dashboard-login telemetry — only the GA4
  public-profile proxy exists today (doc 24). Scaffold gated; do not flip live.
- **Persist + trigger the journey** — a written `supplier_journey` table (today it's a
  derived view) and an **event path** off the per-supplier stage (today batch). §1a, §4.
- **Sequencing + frequency cap** and the **batch-vs-event** trigger decision (§4)
  before more than one lever dispatches per supplier — the journey stage (§1a) is the
  natural hook for both.

[churn-drivers]: ./17_refined_retention_strategy.md
