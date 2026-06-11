# 29 — Lifecycle Journey Refinement (onboarding → engagement → retention → churn/winback)

**Date:** 2026-06-11
**Status:** Refinement — stage-by-stage strategy review + re-sequenced build plan
**Builds on:** [17 strategy](17_refined_retention_strategy.md), [18 bundle+pilot](18_value_add_bundle_and_pilot.md), [20 phased plan](20_phased_implementation_plan.md), [28 flow+levers](28_retention_flow_and_levers.md). Spike answers: [22](22_elastic_boost_interface_contract.md)–[27](27_spike6_invoice_profile_join_answer.md).

The thesis (doc 17) and the holdout/gate discipline (docs 18–20) are sound and stay
unchanged. This doc refines the strategy **as a lifecycle journey** — the four phases
the program must cover (onboard → engage → retain → prevent/recover churn) — and
closes the gaps found by walking each journey stage against what is actually built
(`signals/journey.py`, `cohort.py`, `directives.py`, `measurement.py`).

---

## TL;DR — what this refinement changes

| # | Finding | Action |
|---|---|---|
| 1 | **Cross-experiment collision:** first-term low-exposure suppliers are eligible for *both* `stage1_exposure` and `onboarding`, with independent salts → a supplier can be stage1-**control** and onboarding-**treatment**. Onboarding emails drive exposure → inflates stage1 control → understates lift; `contamination_audit` (unscoped across experiments) will read **CONTAMINATED**. | **Exclude `first_term` from stage1 eligibility** (1-line mask change) *before* onboarding enrols. §3 |
| 2 | **Engagement (driver #3) is unmeasurable:** G1 requires "dashboard engagement up", but no supplier-login telemetry exists (doc 24); `measurement.py` metrics are all couple-side. | Instrument dashboard logins → BQ (dashboard team); **interim: re-specify the G1 engagement endpoint to UTM-attributed dashboard deep-link clicks** (doc 25 §3). §4 |
| 3 | **Onboarding is the largest live population (217) with an undesigned lever** — and it is Bird-only, *not* blocked on Elastic (the P0 critical path). | Design the first-90d sequence now (content proposed §2.1); go live on the Bird contract, ahead of/parallel to the boost. |
| 4 | **Winback is structurally empty** (targeting reads active suppliers only) and **outcomes tracking is absent** (Stage-2's primary endpoint!). Both need the *same* data: ended paid terms. | One data job: ended-term feed → `outcomes` (renewed?) + lapsed rows into targeting. §2.5, §5 |
| 5 | **Renewal window has no sales ammunition** — the original problem statement ("sales has no ammunition", doc 17 §1) — yet the value-recap is the least-built artifact (Phase-2 WS-H, `web/` scaffold only). | Pull forward a **minimal recap view**; the data (`supplier_exposure_daily`, targeting) already exists. §2.4 |
| 6 | Integrity backbone (hash split, leak assertion, audit, DiD) has **zero tests**; legacy `daily_pipeline` actions bypass cohort filtering. | Test the holdout machinery; gate/retire the legacy emitters. §5 |
| 7 | Stages have no per-stage KPIs and no persisted history (journey is derived, batch). | Per-stage KPI table §6; persist `supplier_journey` snapshots. |

---

## 1. The journey is the spine

The lifecycle stages (`signals/journey.py`, live counts from doc 28) are the
organizing structure: every population, driver, lever, experiment and KPI hangs off
a stage. The user-facing framing — *onboard new suppliers, keep engagement, retain,
prevent churn* — maps cleanly:

| Journey stage | N (live) | Lifecycle phase | Validated driver | Experiment | Coverage today |
|---|---:|---|---|---|---|
| `onboarding` | 217 | Onboard | first-term cliff (38% vs 12%) | `onboarding` | lever registered, **sequence undesigned** |
| `healthy` | 989 | Engage | dashboard engagement (35% vs 20%) | — | **none** (monitor only) |
| `at_risk` | 175 | Retain | exposure (#1 driver) | `stage1_exposure` | full bundle, gated on Elastic/Bird |
| `renewal_window` | 63 | Retain (decision point) | value *proof* at renewal | `stage1_exposure` | boost+email mapped; **no sales recap** |
| `lapsed` | 0* | Recover | — (reactivation) | `winback` | lever registered, **feed missing** |

\* zero because `supplier_targeting` is built from active suppliers only — not because nobody churns.

Two phases (retain) are well-served by the Stage-1 bundle. The other three —
onboard, engage, recover — each have a concrete hole. §2 takes them in journey order.

---

## 2. Stage-by-stage refinements

### 2.1 Onboarding (217 suppliers — the largest actionable population)

The year-1 cliff (38% vs 12%) is the **#2 validated driver**, the population is live
today, and the lever needs only Bird — not Elastic. Since the Bird integration items
(doc 25: template id, submission API) must land for stage1's email/newsletter anyway,
**onboarding can go live first**, giving the program its first live lever while the
Elastic spike (YOO-228) is still open. Prerequisite: fix the eligibility collision (§3).

**Define activation, then drive it.** The stage currently spans the whole first term
(`first_term == True`) with no notion of progress. Define **activation milestones**
and make "activated by day 30" the leading KPI (outcome = first-term renewal):

1. **Profile complete** — scraper suggestions approved (one-click go-live; opt-in
   model (b) of doc 26 §2 — the mechanic already exists).
2. **First exposure** — first N profile views (exposure-first; visible proof TPW works).
3. **Proof habit** — opened the first monthly-results email / visited the dashboard.

**Proposed first-90d sequence** (content for the `first_90d` steps already registered
in `directives.LEVERS`; Dutch copy in docs 03/09 is reusable):

| Day | Step (`params.steps`) | Content | Activation goal |
|---|---|---|---|
| 0 | `welcome` | welcome + what happens next + dashboard deep-link (UTM) | expectation set |
| ~3 | `profile_push` | scraper suggestions ready → one-click approve | profile complete |
| 7–14 | *(new)* `first_results` teaser | "you've been seen X times already" — first real numbers, however small | first exposure felt |
| 30 | `first_results` | first full results: views, searches, category benchmark | proof habit |
| 60 | *(new)* tips/social proof | profile tips + a category success story (docs 03/09) | engagement |
| 90 | `renewal_runway` | trajectory vs category + what TPW did (contributed views) | value narrative starts |

*Suggested code tweak (when designing the templates): extend `params.steps` from the
current 4 to the 6 above — the day-7 "first results teaser" is the cheapest "aha"
moment in the journey.*

**KPI:** day-30 activation rate (composite of the 3 milestones); first-term renewal
rate vs the 62% baseline, treatment vs control.

### 2.2 Healthy (989 — engagement is built here, not at at_risk)

Today `healthy` = monitor, no directive. That is correct *during the pilot* (don't
contaminate), but strategically the engagement habit — the 35%→20% churn lever — is
cheapest to build **before** a supplier drifts to at-risk. Post-G1 decision to
pre-register now:

- **Monthly-results email becomes BAU for all active suppliers** (not just at-risk
  treatment), with a **small permanent holdout** for ongoing measurement. Value-proof
  is universal (doc 17 lever 2); withholding it from 989 healthy suppliers is only
  justified while the pilot needs a clean control.
- The reengage lever (#8, gated on login telemetry §4) belongs to this stage:
  trigger = engagement decay *while still healthy*, not after the at-risk tier fires.

### 2.3 At-risk (175 — covered; two cheap improvements)

The Stage-1 bundle covers this stage. Keep Elastic (YOO-228) as the P0 critical path.
Two low-effort improvements from the spike answers, both this-repo work:

1. **Wire the at-risk union** (doc 24 §3): final at-risk = live model P1/P2 **OR**
   `targeting.at_risk_tier`. The overlay exists; only the join against
   `daily_churn_predictions_segmented` is new. This is what recovers the live model's
   ~72% missed churners for targeting.
2. **Run the recall backtest** (doc 24 §4) once the labelled outcomes land via the
   ended-term feed (§2.5) — it is measurement, not model work.

> **✔ Built 2026-06-11 — union wired, and it caught a coverage bug.**
>
> **The union** (`data/predictions.py` + blend in `targeting.py`): `at_risk_tier`
> is now the OR of the rule overlay and the live model's own flags (flagged ⇒ ≥P2,
> Critical ⇒ P1; rule tier never downgraded). `at_risk_tier_rule`,
> `live_churn_probability`, `live_model_flag` are persisted per snapshot — which
> also creates the prediction **history** the external table doesn't keep (it holds
> one day only), making the union's recall lift measurable prospectively against
> `outcomes`. Degrades to overlay-only if the external pipeline is down.
>
> **The coverage bug:** wiring exposed that only 14 of the live model's 127
> flagged suppliers were visible to targeting. Cause: ~137 active paid suppliers
> carry a scheduled trailing `Gratis` row (`plan_end` 2100-01-01) that shadowed
> their running paid term in `get_current()`'s latest-plan ranking — silently
> dropping the **scheduled-cancellation population** (the literal doc-17 failure
> mode) from the entire system. Fixed: current plan ranks over paid plans only;
> earliest future plan sets `renewal_status` (`will_churn` = save population, now
> in `RETAINED_STATUSES`, +0.40 at-risk, routed to renewal_window/at_risk — never
> onboarding/healthy/winback). Live readout after fix: 1,716 targeting rows
> (+137), all 127 live flags visible, 114 `will_churn` all P1/P2; journey:
> renewal_window 60→118, at_risk 188→244. `churn_scorer`'s existing `will_churn`
> branches finally receive the value they were written for. Onboarding eligibility
> tightened alongside (`renewal_status == 'active'`): a first-termer with a
> scheduled downgrade gets the save motion, not a welcome sequence — verified
> across all three experiment pools (129 / 222 / 138, no status leakage).
>
> **Backtest (overlay side; live side has no history):** on 3,109 decided terms
> (≥2024-07, churn base 23.6%), scored at renewal−90d: P1 = 34.4% recall / 39.1%
> precision; **P1+P2 = 82.7% recall** / 27.2% precision (vs the live model's
> 27.6% recall) — confirming doc 24's directional claim, with the precision cost
> now quantified. Implication: the union (P2+) is the right targeting net for
> **cheap automated levers**; reserve P1 + `live_critical` for **expensive human
> touches** (`alert`/`offer`). The union's own lift gets measured prospectively
> as targeting snapshots accumulate beside `outcomes`.

### 2.4 Renewal window (63 — the decision point, still unarmed)

Doc 17's sharpest line — *sales calls the supplier with no ammunition* — describes
**this stage**, and it is the least-built part of the system: the value-recap view is
Phase-2 WS-H and `web/` has no recap today. Meanwhile ~63 suppliers sit in the window
*right now* and renewal conversations happen weekly.

**Pull forward a minimal sales recap** (this repo, `web/` or even a BQ-backed sheet):
per supplier — views + trend, search appearances, category rank/benchmark, masked-lead
list, TPW-contributed views (once UTM attribution flows). Every number already exists
in `supplier_exposure_daily` + `supplier_targeting`. The polished dashboard reframe
stays Phase-2; the recap is sales ammunition, not supplier UX, and shouldn't wait for it.

Also note: the journey maps `renewal_window → boost + email`, but those levers belong
to the `stage1_exposure` experiment — a renewal-window supplier *outside* the pilot
gets nothing. Correct during the pilot; pre-register the post-G1 BAU decision (boost +
recap for every renewal-window supplier, permanent holdout).

### 2.5 Lapsed / winback (structurally empty — and blocking Stage-2 measurement)

`supplier_targeting` reads `suppliers.get_current()` (active only) → the `churned`
eligibility returns empty → winback can never enrol. The same missing data —
**ended paid terms + whether a new term followed** — is also: the Stage-2 primary
endpoint (renewal vs control), the labels for the doc-24 recall backtest, and the
`outcomes` table that is absent from the codebase.

**One data job closes all four gaps:** from `business_development` (interim) /
Moneybird (doc 27, when Drive scope lands), emit terms that ended in the last N
months with `renewed: bool`:
- rows with `renewed = false` and lapse ≤ 6 months → lapsed rows into targeting
  (winback pool populates);
- all rows → `outcomes` (profile_id, experiment_id, arm, plan_end, renewed) —
  Stage-2's endpoint and the backtest labels.

**Winback sequence** (design alongside onboarding; both are Bird sequences): what
changed since they left — "couples searched your category X times last month; your
profile would have appeared in Y searches" — i.e. *foregone exposure*, the same
honest currency as the rest of the strategy. Pair with right-pricing (`offer`, lever
#7) for wrong-model/low-exposure churners once Moneybird ARR is available.

> **✔ Built 2026-06-11** — `suppliers.get_ended_terms()` + `get_lapsed()` (the
> ended-terms feed), `analytics/outcomes.py` + `jobs/build_outcomes.py`, and lapsed
> rows in `supplier_targeting` (`renewal_status='lapsed'`, ≤6 months, 30-day grace
> boundary so the active/lapsed feeds are disjoint).
>
> Live readout: journey `lapsed` stage = **138** (was structurally 0); winback
> eligibility returns the same 138 — **enrolment deliberately deferred** until the
> winback sequence is designed (gated enrolees would age out of the ≤6-month
> window). `outcomes`: **3,223 term rows / 1,925 suppliers** (24 months, 34
> pending). **Labels validate against doc 17:** decided churn 23.8% ≈ the known
> ~24–25%; first-term churn 39.3% ≈ the 38% cliff; venue 16.6% ≈ the 15% known
> low. Established-supplier churn reads 20.3% vs doc 17's 12% — different window
> (last 24 months vs the ≥2023 cohort), worth a look during the recall backtest.
> Post-enrolment outcome rows: 0 (correct pre-launch).

---

## 3. Fix the cross-experiment collision (before onboarding enrols)

**The mechanism (verified in code):** `stage1_exposure` eligibility =
`bundle_eligible & category ∈ {photo, video, music}` (`cohort.py:126`), and
`bundle_eligible` = non-venue ∧ low-exposure ∧ active (`targeting.py:162`) — **no
first-term exclusion**. `onboarding` eligibility = all first-termers. The two
experiments hash with independent salts, so a first-term low-exposure photographer
(common: `first_term` adds +0.20 to the at-risk score) can be assigned
**stage1-control + onboarding-treatment**. Onboarding emails drive exposure and
dashboard visits → stage1's control arm is no longer untouched → measured lift biased
**downward** — and `measurement.contamination_audit` checks `retention_directives`
*without experiment scoping* (`measurement.py:193-209`), so the stage1 readout will
correctly report **CONTAMINATED** the moment onboarding dispatches to an overlapping
control supplier. The journey layer already encodes the right priority (onboarding
outranks at_risk in `stage()`); cohort eligibility just doesn't follow it yet.

**Fix now (recommended):** exclude first-termers from stage1 —
`mask &= ~df["first_term"].fillna(False)` in the `category_bundle` branch (or fold
`~first_term` into `bundle_eligible`). One line; matches the journey-stage priority
and doc 18's intent (first-termers are the *onboarding* population). Then re-check
Stage-2 power (~270/arm assumed ~−10pp MDE, doc 18) after measuring how many of the
eligible pool drop; if the loss is material, widen Stage-2 categories rather than
re-including first-termers.

> **✔ Applied 2026-06-11** — pre-launch state verified safe first (every stage1
> directive `status='gated'`, onboarding cohort empty, nothing ever dispatched), then:
> 1. Eligibility mask excludes `first_term` (`cohort.py` `category_bundle` branch).
> 2. The **38 already-enrolled first-termers** (21 treatment / 17 control of 164)
>    deleted from `cohort_assignment` — arms reproducible from the locked salt if
>    ever needed. Remaining roster **66 / 60**, skew within tolerance, baseline
>    balance intact (`views_365d` 229.5 vs 225.8, std diff ≈ 0.05).
> 3. WS-D rebuilt: 264 directives (66 × 4 levers), all `gated`; leak assertion clean.
> 4. `build_cohort` re-run: **0 re-enrolled** — the exclusion holds end-to-end.
>
> Pool impact: 38 of 164 eligible (23%) — first-termers now flow to `onboarding`.

**✔ Stage-2 power re-check (run 2026-06-11, live targeting snapshot).** The
12-month Stage-2 enrollment flow is the current bundle-eligible stock (annual
terms: all 353 renew within 365d; new sign-ups hitting a *first* renewal are
excluded by this fix, and second renewals fall outside the window):

| Scenario | n/arm | MDE @80% power (churn 25–35%) |
|---|---:|---|
| Doc 18 assumption | ~270 | ~10–11pp (doc 18's claim reproduces ✓) |
| Live flow, *incl.* first-term | 176 | ~12–13pp |
| **Live flow, excl. first-term (current spec)** | **115** | **~14–16pp** |

Two findings: (a) the exclusion costs ~2.6pp of MDE (122 of 353 eligible — 35% —
are first-term, higher than stage1's 23%); (b) **the bigger problem predates the
exclusion** — the live renewal flow is well under doc 18's ~540/yr assumption, so
Stage-2 as specced was already underpowered for −10pp. Raising the low-exposure
threshold alone doesn't fix it (established non-venue actives: 343 below 440
views/yr, 455 below 660 → at best ~227/arm ≈ ~11pp, while diluting the expected
effect above the ~330 cliff). Reaching −10pp at the current spec needs ~2.2–2.8
years of enrollment.

**Recommended Stage-2 design changes (pre-register at Stage-2 kickoff):**
1. **Program-level primary readout:** stratified renewal analysis pooling the
   `stage1_exposure` (established) and `onboarding` (first-term) experiments —
   each has its own randomized holdout, and "does the lifecycle program retain?"
   is the actual G3 question. First-termers are not lost to measurement; they
   moved strata.
2. **Extend enrollment to ~18–24 months** and/or widen the threshold toward the
   ~440 cliff boundary (343 eligible) — ~18 months at <440 ≈ 257/arm ≈ −10pp.
3. Keep doc 18's pre-registered leading indicators (renewal-intent/NPS, sustained
   exposure, engagement) as the early decision inputs — the fixed-N churn readout
   alone cannot carry a 12-month G3 decision at this pool size.

**Decide before a third experiment ships:** per-experiment salts mean every new
experiment multiplies collision pairs. The structural alternative is a **single
lifecycle-level randomization** (one arm per supplier across all experiments) — clean
program-level measurement (the real G3 question) at the cost of a control group that
never receives *any* lever. Take this decision deliberately when `winback` (disjoint
population, no collision risk) or any overlapping experiment is next to enrol; an
eligibility-exclusion rule per §4's arbiter is the lighter-weight alternative.

---

## 4. Close the engagement measurement hole (driver #3)

Dashboard engagement is a validated driver (35% vs 20%), the `reengage` lever's
trigger, **and a G1 exit criterion** ("dashboard engagement up", doc 20) — yet doc 24
established that **no supplier-login telemetry exists**: today's `days_since_last_login`
is a GA4 *couple-side public-profile* proxy, and `measurement.py`'s panel metrics
(`profile_views, impressions, list_clicks, show_phone, website_open`) are all
couple-side exposure. As written, **G1's engagement criterion cannot be honestly
evaluated**.

Two-part fix:

1. **Instrument supplier-dashboard logins → BQ** (dashboard app team; small — one
   auth/session event). Treat it as critical path *alongside* Elastic: it unblocks
   the `reengage` lever, the engagement feature in targeting (doc 24 §2), and honest
   measurement of the program's third driver. Without it, "engagement" stays
   unmeasurable through Stage-2 as well.
2. **Interim, re-specify the G1 engagement endpoint** to what *is* measurable now:
   UTM-attributed dashboard deep-link clicks from the monthly-results email
   (doc 25 §3 — `utm_campaign=monthly_results` sessions per treatment supplier vs
   control). Pre-register this substitution in the experiment design so G1 isn't
   judged on a metric that doesn't exist.

---

## 5. Integrity & measurement hygiene (cheap, protects everything)

| Item | Why | Effort |
|---|---|---|
| **Tests for the holdout machinery** — stable-hash determinism + locked-salt reuse (`cohort.py`), leak `AssertionError` (`directives.generate`), audit scoping (`contamination_audit`), DiD math on a synthetic panel (`_two_arm`) | The entire experimental claim rests on these; today they have **zero tests** | S |
| **Gate or retire legacy emitters** — `jobs/daily_pipeline.py` CRM tasks + SendGrid email flows predate the holdout and bypass `cohort.filter_treatment()`. **✔ Gated 2026-06-11**: this risk materialized live — the 7AM job logged inert (`executed=false`) `crm_task` intents for 8 stage1-control suppliers. Stage 4 is now behind `legacy_actions.enabled` (default false); if re-enabled it excludes all enrolled suppliers (`cohort.enrolled_ids()`, both arms). The 36 inert intent rows (20 treatment / 16 control) were deleted; audit reads **CLEAN**. *Requires a Cloud Run image redeploy to take effect at 7AM.* | If ever switched on they contaminate every experiment; SendGrid path is already deprecated (doc 19) | S |
| **`outcomes` table** (§2.5) | Stage-2 primary endpoint; backtest labels | S–M (one feed) |
| **Persist `supplier_journey`** (stage per supplier per snapshot) | Stage-transition funnel: dwell time, onboarding→healthy conversion, at_risk save-rate — the per-stage KPIs in §6 need history, and it is the natural hook for the event-trigger path and the §4 arbiter (doc 28 §4) | S |
| **Wire `sources.supplier_email_*`** to `companies_profiles.profile_email` | Recipient resolution for every Bird lever (doc 25 §1) | XS |

---

## 6. Per-stage KPIs (make the journey measurable)

North star unchanged: non-venue annual churn 25% → target band post-pilot (doc 17 §8).
Per-stage leading indicators, each measured treatment-vs-control where a lever runs:

| Stage | Leading KPI | Outcome KPI |
|---|---|---|
| `onboarding` | day-30 activation rate (profile complete ∧ first exposure ∧ proof habit, §2.1) | first-term renewal rate (cliff: 38% churn → target band) |
| `healthy` | % above exposure threshold (>330 views/yr); monthly-email open / dashboard-visit rate | stay-healthy rate (no at_risk entry) |
| `at_risk` | exit-rate from P1/P2 tier (re-exposure); exposure lift vs control (G1) | renewal rate vs control (G3) |
| `renewal_window` | recap usage by sales; renewal-intent | renewal rate vs control |
| `lapsed` | winback-sequence response rate | reactivation rate ≤ 6 mo |

---

## 7. Re-sequenced build order

Ordered by dependency and value; (1)–(3) are this-repo and unblocked **today**.

| # | Build item | Phase served | Owner / blocker | Effort |
|---|---|---|---|---|
| 1 | **First-term exclusion** in stage1 eligibility (§3) — **✔ applied 2026-06-11** (code + cohort cleanup + directives rebuild); **✔ power re-checked** — Stage-2 needs a stratified program-level readout + longer/wider enrollment (§3) | retain + onboard | this repo — none | XS |
| 2 | **Ended-term feed** → `outcomes` + lapsed targeting rows (§2.5) — **✔ built 2026-06-11** (lapsed=138 live, outcomes=3,223 labels; winback enrolment deferred to sequence launch) | recover + measurement | this repo — none (interim `business_development`) | S–M |
| 3 | **At-risk union** with live model scores (§2.3) + recall backtest once (2) lands — **✔ built 2026-06-11** (union live; overlay backtested: P1+P2 recall 82.7% vs live 27.6%; fixed the will_churn coverage bug it exposed) | retain | this repo — read access to `churn_prediction` outputs | S |
| 4 | **Elastic spike YOO-228** → boost build (doc 22) | retain | **Elastic team — open, P0 critical path** | M |
| 5 | **Bird contract items** (template id, submission API, newsletter block; doc 25) | retain + onboard | marketing_flow owner | S–M |
| 6 | **Onboarding sequence design** (§2.1) + scraper opt-in decision (doc 26 §2) | onboard | this repo + product | S–M |
| 7 | **Dashboard login telemetry → BQ**; interim UTM engagement endpoint pre-registered (§4) | engage | dashboard team / this repo | S |
| 8 | **Minimal sales value-recap** (§2.4) | retain (renewal) | this repo (`web/`) | S–M |
| 9 | **Frequency cap / arbiter** across experiments (doc 28 §4; journey stage = arbiter) | all | this repo — before a 2nd experiment dispatches | M |
| 10 | **Holdout tests + legacy-emitter gating** (§5) — emitter gating **✔ done 2026-06-11** (audit CLEAN); holdout tests still open | all | this repo — none | S |
| 11 | Persist `supplier_journey`; per-stage KPI report (§6) | all | this repo | S |
| 12 | Post-G1 BAU decisions (pre-register now): healthy-stage monthly email + renewal-window boost/recap, each with permanent holdout (§2.2, §2.4) | engage + retain | product | — |

**Net effect on the journey:** every phase the strategy names gets a live, measured
path — onboard (1, 5, 6), engage (7, 12), retain (3, 4, 8), recover (2) — without
touching the thesis or the gate structure, and with the pilot's measurability
*strengthened* (1, 9, 10) rather than put at risk by the wider scope.
