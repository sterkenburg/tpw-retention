# Refined Retention Strategy (Evidence-Led)

**Date:** 2026-06-05
**Status:** Agreed thesis — basis for value-add design and phased plan
**Supersedes:** the *assumptions* in docs 01–16 where they conflict (esp. the lead-centric and discount/price framings, and the Ad Boost Pool as a churn fix). The flows, templates, and infrastructure in those docs remain reusable.

---

## 1. The problem (sharp)

TPW loses ~**25% of paying suppliers per year**. The failure mode is concrete: before renewal, sales calls the supplier → supplier says *"I'm not getting value from the platform"* → they don't renew. The churn dashboard finds these suppliers earlier, but **finding them earlier just means having the same losing conversation sooner.** Sales has **no ammunition**, and for a large group there genuinely *is* a value gap. Discounting only destroys margin and trains suppliers to threaten churn.

So the real work is **creating (and making visible) value during the journey** — not better prediction, not discounts.

---

## 2. What the data established

All figures from a renewal-decision cohort (3,384 completed paid terms, ≥2023 for full lead coverage; cohort churn **24% ≈ the known 25%**, so the method is validated). See the analysis memos for detail.

**a. Most churners genuinely got little value.** Of churned suppliers: **51% got ≤2 leads** in their ~11-month final contract, 33% got 3–10, only 16% were well-served (11+). Lost ARR ≈ €549k across the cohort (~€40k/yr photographers, ~€35k/yr venues per the live dashboard).

**b. Leads are a *weak, high-threshold* churn driver — and a paid lead-boost does NOT pay back.** Churn by leads/yr: 31% (0–2) → 8% (26+), but there's a **dead zone 0–5 leads** where more leads barely move churn; it only drops above ~6/yr. Correlation just −0.11. A *feasible* boost (≈+8 leads) buys only ~3–9pp churn reduction → break-even cost-per-inquiry collapses to ~€7–21 vs real ~€25–50 → **uneconomic**. Worse, thin-demand categories can't even reach the threshold (photographers cap at ~4.6 leads/supplier/yr).

**c. The real drivers (multivariate, category-controlled):**
| Driver | Effect | |
|---|--|--|
| **Profile views (exposure)** | strongest (−61% odds/SD; univ. 42%→10% churn) | ✅ |
| **Tenure / first-term** | first term 38% vs 12% churn | ✅ |
| **Supplier dashboard engagement** | no-login 35% vs login 20% | ✅ |
| Term length (annual) | −18% | ✅ |
| Plan **price** | non-monotonic, **ns** (cheapest churn *least*) | ❌ not a driver |
| View→lead conversion | flat | ❌ |
| Leads/yr | subsumed by views (corr 0.81); no independent effect | ❌ |

**Exposure is king, and it's *views* not *leads*** — views are ~50× more abundant, discriminate earlier, and are driven by levers TPW controls. **Price is not the problem** — the "too expensive" complaint is a value-perception symptom.

**d. The exposure supply is flat and organic-dependent.** Organic search to supplier profiles has roughly **halved** (−20% to −34% YoY; market-wide zero-click trend) — SEO is a declining asset, not a lever. Total profile views *looked* like they were growing, but that was **venues**: venue Google-Ads spend tripled, venue views +32% in 2025, and venues are now ~68% of all profile views. **Excluding venues, exposure is FLAT (~800k views/yr) and softening in 2026.**

---

## 3. The thesis

> **Stop trying to predict-and-chase churners or manufacture leads. Instead, drive and *demonstrate* exposure, get suppliers engaged with their results, onboard first-termers fast, and grow the channels TPW owns — while pricing to match the value actually delivered.**

The churn dashboard becomes a **targeting tool for these interventions**, not the product.

---

## 4. Segmentation — different segments, different playbooks

| Segment | Profile | Primary levers |
|---|---|---|
| **Non-venue lead-driven** (photographers, videographers, music, planners, makeup, cakes, florists, dresses, …) | Flat/scarce leads, abundant-but-static views, Pareto-concentrated | **Exposure redistribution + dashboard engagement + onboarding + lead-independent value** |
| **Venues** | Paid-ads engine, get leads, lowest churn (15%); when they leave it's "got value, didn't see it" | **Maintain paid engine + proof/attribution + conversion help** (separate track) |
| **Wrong-model retail** (rings 97% starved, suits, catering, cards) | Couples don't shortlist-and-inquire; lead model misfits | **Right-pricing / different value prop** (brand/exposure metric); don't spend lead budget here |

---

## 5. Levers & value-adds (priority order)

**1. Redistribute on-platform exposure** *(hits the #1 driver; abundant pie; low marginal cost)*
- Weight ranking/search toward low-exposure, at-risk, and first-term suppliers; featured rotation for the tail; "similar suppliers" cross-profile recommendations; regional spotlights; feature suppliers in couple-facing emails.
- **Pair with profile optimization** (existing scraper) so boosted profiles actually convert views.
- *Constraint: it's a fixed/zero-sum pie — don't starve the middle. Validate headroom.*

**2. Dashboard engagement + value-proof** *(driver #4; makes exposure visible; cheap; all segments; doubles as sales ammunition)*
- Supplier dashboard centered on **exposure** (views, search appearances, ranking vs category, benchmark) — not just leads. Monthly "your results" email + instant view/lead notifications to drive logins. "You were seen X times this month."

**3. First-term onboarding** *(driver #2; year-1 is the 38% cliff)*
- Auto-fill profile (scraper), week-1 activation to first exposure, build the dashboard habit early.

**4. Grow owned channels** *(protect the exposure pie from organic decline)*
- Couple newsletter/email featuring suppliers, app engagement, Real-Weddings/editorial (direct traffic + backlinks, not SEO-dependent), partner/vendor network.

**5. Right-pricing** *(kills "too expensive" without discounting; price isn't a churn driver, but value/price *fit* is)*
- Lower tier / pause option for low-exposure or wrong-model suppliers; align price to delivered exposure.

**6. Lead-independent stickiness** *(value even for low-lead suppliers)*
- Review widget/collector (social proof, lives on their site), auto-responder (responsiveness), testimonial collector, partner referrals.

**Venue track (parallel):** sustain paid engine; build booking attribution + ROI reporting so the value they *do* get is visible at renewal; conversion coaching.

---

## 6. Explicitly rejected (so we don't re-litigate)

- **Paid lead-boost as a retention lever** — doesn't pencil; leads are weak/high-threshold; categories are demand-constrained.
- **Discounting** — price is not a churn driver; cheapest plans churn least.
- **SEO as a growth lever** — structural, market-wide decline.
- **Ad Boost Pool (supplier-pays-more) as a save for doubters** — adverse selection; "pay more for leads" doesn't land with suppliers who already feel overcharged. (May still work as an *upsell for believers* — out of scope for retention.)

---

## 7. Rebuild the churn signal on the real drivers

Replace the current lead/login rule weights with the validated features: **exposure level + trend, tenure / first-term flag, term length, dashboard-engagement recency.** Use the score to **target** redistribution/onboarding/proof interventions — not just to produce a list.

---

## 8. Success metrics

- **North star:** non-venue annual churn (25% → target band to set post-pilot).
- **Leading indicators:** % of suppliers above an exposure threshold (e.g., >~330 views/yr, the point where churn drops); dashboard login rate; first-term activation rate; non-venue exposure pie size and owned-channel share of profile views.
- **Discipline:** every intervention runs with a **holdout control** to measure the real save-rate.

---

## 9. Open questions → pilot first

1. **Causal test (the key unknown):** does *redistributing exposure* to the low-exposure tail actually reduce churn, or do high-view suppliers simply renew because they're better businesses (selection)? → holdout-controlled pilot.
2. **Headroom:** non-venue view concentration — can we lift the tail toward the median without harming the middle?
3. **Owned-channel growth:** can email/app/content grow non-venue direct traffic enough to offset organic decline?
4. **Profile conversion:** do boosted weak profiles convert views, or is profile optimization a prerequisite?

---

## 10. Next steps

1. Design the **value-add bundle** for the non-venue segment (start with exposure redistribution + dashboard-engagement, the two highest-leverage levers).
2. Define the **holdout-controlled pilot** (likely photographers) to test the causal exposure→retention link.
3. Translate into a **phased implementation plan**.
