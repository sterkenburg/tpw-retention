# 24 — Spike 3 Answer: Exposure Features in the Churn Model (YOO-230)

**Status:** Spike answer (closes Definition of Done) · **Date:** 2026-06-09 · **Linear:** [YOO-230](https://linear.app/yoonsterkenburg/issue/YOO-230) (parent YOO-227)
**Owner:** Lifecycle (tpw-lifecycle) · churn_prediction

Source spec: `docs/strategy/21_phase0_confirmation_spikes.md` §Spike 3. Prior audit: `docs/strategy/12_churn_prediction_audit.md`.
**Definition of done:** feasibility + plan + expected recall-lift estimate (or fallback decision).

---

## TL;DR — Decision: **fallback overlay, not a retrain**

The live cascading model misses ~60–72% of churners (27.6–40.4% recall) **because it
lacks exposure features — the #1 churn driver our multivariate analysis found**
(docs/strategy/17; memory: churn-drivers-multivariate). The honest fix is **not**
another retrain of the 200-script `churn_prediction` project. It is to **consume the
live model's scores and OR-in an exposure-driven at-risk overlay** — which is already
~90% built in `src/signals/targeting.py` (`_at_risk_score`).

| Question | Answer |
|---|---|
| Training/deploy/retrain pipeline? | Lives in the **external `churn_prediction` project** (not this repo). Daily 7 AM predictions → BigQuery → Cloud Run dashboard + Slack. Phase-2 decision deliberately **stopped retraining** (GA4 discrimination 0.269). §1 |
| Add exposure level+trend + dashboard-engagement recency? | **Exposure level+trend: yes, available now** (`supplier_exposure_daily`, WS-A). **Dashboard-engagement recency: blocked** — no true supplier-dashboard login source exists; today's "last login" is a GA4 public-profile proxy. §2 |
| Fallback (overlay rule-based exposure signal)? | **Recommended path.** Already implemented as `targeting.at_risk_score`. §3 |
| Expected recall lift | Directional: should recover a large share of missed churners (they're disproportionately low-exposure/declining). Exact number needs a backtest against churn_prediction's labelled outcomes — method in §4. |

---

## 1. The live model — what it is and why retraining is the wrong lever

From the prior audit (doc 12) + `config`/`suppliers.py` references:

- **Architecture:** cascading ML (baseline + trend models). Daily predictions at
  **7 AM** → BigQuery (`daily_churn_predictions_segmented`) → Cloud Run dashboard +
  Slack. Source data in the `churn_prediction` BQ dataset (`business_development`,
  `profiles`).
- **The pipeline is external** to tpw-lifecycle — this repo holds a *simplified*
  rule-based scorer (`src/signals/churn_scorer.py`) and the exposure-driven targeting
  signal (`src/signals/targeting.py`), **not** the cascading model's training code.
- **Performance gap:** validation precision/recall (78.8% / 82.4%) collapse in
  production (50% / 40.4%; the spike cites 27.6% recall on a later cut). Causes:
  overfitting, concept drift, small label set.
- **Phase-2 decision (correct at the time):** GA4 discrimination measured **0.269**,
  judged too weak to justify retraining → they froze the model and rely on signal
  scoring. **Caveat that reopens the door for us:** that 0.269 was *generic GA4
  activity*, **not** the **exposure level + trend** features our analysis isolated as
  the #1 driver. So "GA4 didn't help" ≠ "exposure won't help" — but it does mean a
  full retrain is high-risk/high-effort for uncertain lift.

**Conclusion:** retraining the cascading model requires access to the external
`churn_prediction` repo + retrain infra, carries concept-drift/overfit risk, and
fights the (reasonable) Phase-2 freeze. **Not worth it for Stage-1.**

## 2. Feature availability

| Feature | Available now? | Source / blocker |
|---|---|---|
| **Exposure level** (views 60d/365d) | ✅ Yes | `supplier_exposure_daily` (WS-A) → `targeting._exposure_features` |
| **Exposure trend** (60d vs prior 60d) | ✅ Yes | same |
| **Days since last view** | ✅ Yes | same |
| **Dashboard-engagement recency** (supplier logging into *their own* dashboard) | ❌ **Blocked** | No supplier-dashboard auth/login event in BQ. Today's `days_since_last_login` (`supplier_stats.py`) is **approximated from GA4 public-profile pageviews** — that's couple-side traffic, not supplier engagement. A true signal needs the dashboard app to emit login/session events to BQ. |

The dashboard-engagement-recency gap is a genuine new finding: it's listed as a
driver but is **not measurable** with current data. → follow-up: instrument
supplier-dashboard logins (owner: dashboard app), out of scope for Stage-1.

## 3. The fallback overlay — recommended, already ~90% built

`src/signals/targeting.py::_at_risk_score` already scores suppliers on the
**validated drivers** the live model lacks:

- exposure level (`views_365d` < 330/yr → +0.30; < 165 → +0.10) — the #1 driver
- exposure trend (declining > 30% → +0.15)
- first-term (year-1 cliff 38% vs 12% → +0.20)
- short/non-annual term (+0.10)
- no recent exposure (no view in 30d → +0.15)

**Integration plan (Stage-1, low effort):**

1. **Keep the live model's `churn_probability`** as one input (don't touch the
   external pipeline).
2. **Blend, don't replace:** final at-risk = `OR` of (live P1/P2 tier) and
   (`targeting.at_risk_tier`). The overlay's whole job is to **catch the
   low-exposure churners the live model structurally misses** — which is exactly the
   recall gap. Union maximises recall; precision is protected because the overlay
   uses validated drivers, not noise.
3. **Surface "why":** `targeting` already emits the driver columns (views, trend,
   first_term, days_since_last_view) → satisfies doc 12's "add Why to the dashboard".
4. **No new infra:** `build_targeting` already runs and writes `supplier_targeting`.
   Only a join/union against the live predictions table is new.

This is the doc-12 "consume current scores + overlay a rule-based signal" path, and
it's the Stage-1 recommendation.

## 4. Expected recall-lift — estimate + how to confirm

**Directional estimate:** the churners the live model misses are
**disproportionately low-exposure / declining-exposure** suppliers (because that's
the driver the model lacks). The overlay flags exactly that population, so it should
**recover a large share of the false negatives** — the bulk of the recall gap is
addressable. A precise % is not assertable from this repo because the **labelled
churn outcomes live in the `churn_prediction` project**, not here.

**Backtest to confirm (the one data-access follow-up):**

1. Pull the historical churned set + the live model's prediction at the time (from
   `churn_prediction`, e.g. `daily_churn_predictions_segmented` joined to actual
   renewal outcomes).
2. For the **false negatives** (churned but model said safe), compute the overlay
   (`views_365d < 330` OR `exposure_trend < -0.3` OR `days_since_last_view > 30` OR
   `first_term`) from `supplier_exposure_daily` as of that date.
3. **Recall lift = fraction of those false negatives the overlay would have flagged.**
   Report the union's new precision alongside (the cost of the extra flags).

This is a runnable analysis once we have the labelled outcomes — it's measurement,
not model work.

## 5. Definition of Done — status

| DoD item | Status |
|---|---|
| Feasibility | ✅ Live pipeline characterised; retrain assessed and rejected for Stage-1 (§1) |
| Plan | ✅ Blend live scores with the exposure overlay; ~90% built in `targeting.py` (§3) |
| Recall-lift estimate **or** fallback decision | ✅ **Fallback decision** taken; directional estimate + confirm-backtest method (§4) |

**Spike 3 is answered.** Follow-ups (implementation / data-access, not investigation):

1. **Wire the union:** join `supplier_targeting.at_risk_tier` with the live
   predictions table and take the OR for the final at-risk list.
   **✔ Done 2026-06-11** (doc 29 §2.3 note): `data/predictions.py` + blend in
   `targeting.py`; flagged ⇒ ≥P2, Critical ⇒ P1. Wiring exposed and fixed a
   `get_current()` coverage bug that hid the scheduled-cancellation (`will_churn`)
   population — 113 of the model's 127 flags were invisible to targeting.
2. **Backtest the recall lift** against `churn_prediction` labelled outcomes (§4) —
   needs read access to that project.
   **✔/△ Done for the overlay side 2026-06-11**: on 3,109 decided terms from the
   `outcomes` table (churn base 23.6%), the overlay at P1+P2 recalls **82.7%** of
   churners (precision 27.2%); P1 alone 34.4% / 39.1%. The §4 method as written is
   **impossible retroactively** — `daily_churn_predictions_segmented` keeps only the
   latest day, no history. Live flags are now snapshotted into `supplier_targeting`
   daily, so the union's lift becomes measurable prospectively against `outcomes`.
3. **Instrument supplier-dashboard logins** to BQ so dashboard-engagement recency
   becomes a real feature (owner: dashboard app) — deferred beyond Stage-1.
