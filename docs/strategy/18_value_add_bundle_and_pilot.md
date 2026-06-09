# Value-Add Bundle + Pilot Design

**Date:** 2026-06-05
**Status:** Design — ready to scope into implementation
**Builds on:** [17_refined_retention_strategy.md](17_refined_retention_strategy.md) (the evidence and thesis)

Designs the two highest-leverage levers for the **non-venue** segment — **exposure redistribution** and **dashboard engagement + proof** — as one closed loop, plus the pilot to prove the causal link before full build.

---

## Confirmed assets (we build on these)

| Asset | Use in the bundle |
|---|---|
| **Supplier dashboard** (exists; suppliers log in) | Enhance to be exposure-centric (Lever 2) |
| **Profile scraper** (works) | Auto-optimize profiles so boosted views convert (step 2) |
| **Couple-facing newsletter** (exists) | Additive exposure channel for the tail (Lever 1, mechanic B) |
| **Ranking control** | Redistribution — **caveat: premium spots are a PAID product** (see guardrail) |
| Monthly-results email infra (partly prototyped in repo) | Engagement driver (Lever 2) |

---

## The bundle: "TPW gets you seen — and shows you the proof"

A closed loop for low-exposure / at-risk / first-term non-venue suppliers:

```
1. IDENTIFY  → rebuilt churn signal: low-exposure / first-term / at-risk
2. OPTIMIZE  → scraper improves the profile so views convert
3. BOOST     → redistribute FREE exposure to them      ── Lever 1
4. SHOW      → surface the boosted exposure + TPW's role ── Lever 2
5. ARM       → sales value-recap at renewal
6. MEASURE   → randomized holdout on everything
```

Exposure and engagement only work together: boosting exposure the supplier can't see does nothing for *perceived* value; showing exposure you haven't improved just documents the problem.

---

## Lever 1 — Exposure redistribution (free layer only)

**Goal:** lift a bottom-quintile supplier (~180 views/yr) toward the median (~330/yr) ≈ **+12 views/month** — the data links this to ~12pp lower churn. The ~800k/yr non-venue pie funds it *if* we don't cannibalize the head or the paid premium product.

**Mechanics (additive/owned/relevance first; never the paid premium inventory):**

| # | Mechanic | Touches premium? | Zero-sum? |
|---|---|---|---|
| A | **Cross-profile recommendations** ("similar suppliers" on popular profiles / high-traffic pages) | No | No (uses head traffic additively) |
| B | **Couple-newsletter features** of tail suppliers | No | No (grows the pie — owned channel) |
| C | **Long-tail / regional / niche search surfacing** (relevance, not top slot) | No | Mostly no |
| D | **"Rising / Discover" spotlight surface** — a NON-premium module, rotating at-risk/tail | **No (separate from paid spots)** | Partly |
| — | Premium top spots | **Paid product — off-limits to free redistribution** | — |
| E | Core ranking re-weight | Conflicts with premium | **Deferred** |

**Premium-spot guardrail:** redistribution operates only in free/organic/owned positions and a separate "Discover/Rising" surface — **never the paid premium slots**. Premium stays a paid upsell for believers; we don't undercut it or punish payers.

**Always paired with profile optimization (step 2)** — a boosted weak profile wastes the placement and hurts couples.

**Targeting:** the rebuilt churn signal — low-exposure, first-term, and approaching-renewal non-venue suppliers (these are, by definition, not premium buyers).

**Couple-experience guardrails:** monitor placement CTR and view→lead conversion of boosted positions; cap views drawn from non-churning top suppliers; dial back if couple metrics degrade.

---

### ⭐ Flagship mechanic — Venue → related-suppliers carousel (cross-category)

On venue profiles (the highest-traffic category, ~68% of all profile views), show a carousel of **related suppliers from *other* categories** — *"couples who booked this venue also booked this photographer / florist"* — ranked by **location proximity** and **real co-booking affinity** seen in our data.

**Why it's the best redistribution instance:**
- Routes the demand-rich **venue** surface → the **starved** non-venue categories (photographers, florists) that have the exposure-driven churn problem.
- **Additive** (uses venue traffic, takes from no one), **free-layer** (doesn't touch premium), **relevance-based** (good couple experience), and it hits the #1 churn driver (exposure) for the tail.
- Doubles as a couple-experience win (one-stop planning) and seeds the **vendor-network** hook (doc 16).

**Data dependency (likely a spike):** co-booking affinity needs a "which couple booked which suppliers" relationship — derivable from same-couple links (e.g., shared lead email in `generate_lead`, or `matched_invoices` bookings) and/or shared wedding date+region. Start with **location proximity** (simple, available now) and layer in **co-booking affinity** where the data supports it. Respect the holdout (feature at-risk/tail treatment suppliers in the carousel; controls excluded).

---

## Lever 2 — Dashboard engagement + value-proof

**Principle 1: lead with exposure, not leads.** "2 leads" demoralizes; "seen 340×, rank #4 of 38 in Noord-Holland" motivates — and exposure is the #1 churn driver. For low-lead suppliers, exposure is the honest, positive story.

**Principle 2: concrete beats abstract.** A statistic ("5 leads") is forgettable; a tangible artifact — a masked lead email, the *actual search query* a couple used, "a couple from Utrecht viewed you 3× and shortlisted you" — is *felt*. Felt value is what survives the renewal conversation. Prefer real moments over aggregate counts wherever possible.

**Components:**
1. **Exposure-centric dashboard** (enhance existing): views + trend, search appearances, ranking vs category, benchmark vs top performers. Leads secondary.
2. **Engagement drivers:** monthly "your results" email + view/lead notifications → build the login habit (logging in cuts churn 35%→20%).
3. **Tangible lead proof (masked):** in the monthly overview, show not just counts but the **masked email of each lead** (e.g. `t****ed@gmail.com`). Turns an abstract number into evidence of *real couples* — the direct counter to "I'm not getting value." **Full contact is revealed only in-dashboard**, which (a) drives the login that itself cuts churn (35%→20%) and (b) keeps the lead on TPW (couples aren't poached off-platform — the "TPW owns the lead" principle). GDPR-safe by construction; full PII stays in the authenticated dashboard, never in the email.
4. **Show TPW's contribution:** *"TPW featured you in 3 couple newsletters and surfaced you in 1,200 searches this month → +Y views."* The supplier sees TPW actively working for them — this is what ties Lever 1 to Lever 2 and prevents "showing flat exposure backfires."
5. **Sales-ammunition view:** per-supplier value recap for renewal calls — views delivered, searches, ranking, benchmark, "here's what we did for you."

---

## Rebuilt churn signal (targeting engine)

Replace the current lead/login rule weights with the validated drivers: **exposure level + trend, tenure / first-term flag, term length, dashboard-engagement recency.** Output drives *who* enters the bundle — not just a report.

---

## The pilot

**The one thing it must prove:** the causal link — does boosting + showing exposure actually reduce churn, or do high-view suppliers just renew because they're better businesses (selection)? Everything rests on this.

**Hard constraint — statistical power.** Photographers alone (~249 active, ~125 renewals/yr → ~60/arm) is underpowered for a churn endpoint (~300/arm needed to detect a 10pp drop). Hence a **two-stage design.**

### Stage 1 — "Can we move the levers?" (~6–8 weeks, high-power)
- **Population:** low-exposure photographers (pool in videographers/music if N needed), randomized **treatment vs holdout**.
- **Treatment:** profile optimization + additive exposure boost (A–D) + enhanced dashboard/monthly email.
- **Primary endpoints (fast):** exposure lift (views delta vs holdout), dashboard engagement (login rate), profile view→lead conversion, couple-experience guardrails intact.
- **Decision gate:** if exposure/engagement don't move, stop — don't bother measuring churn.

### Stage 2 — "Does it retain?" (~6–12 months, pooled)
- **Population:** pooled thin-lead non-venue categories for adequate N; randomized holdout maintained.
- **Primary endpoint:** renewal rate (treatment vs control) at the renewal decision.
- **Secondary:** renewal-intent / NPS, sustained exposure, engagement.

**Why two stages:** Stage 1 de-risks the *mechanism* cheaply and fast; we only commit to the slow churn read once the levers demonstrably move.

**Guardrails throughout:** couple-side metrics; premium-spot revenue (ensure no cannibalization); top-supplier exposure not materially harmed.

---

## Success criteria

| Stage | Pass bar (illustrative — set precisely at kickoff) |
|---|---|
| Stage 1 | Treatment exposure ≥ +X% vs holdout; dashboard login rate up; couple CTR/conversion not degraded |
| Stage 2 | Renewal rate uplift vs control, significant at the pooled N |

---

## Pilot sizing & experiment spec (Phase-0 results, 2026-06-05)

**Renewal calendar (active paid terms):** ~290–300 non-venue + ~60–75 photographer renewals **per quarter** (base: 1,540 paid / 1,100 non-venue / 249 photographers).

**Low-exposure threshold = <330 profile views/yr** (the 42%→30% churn cliff; ≈ the photographer median of 328). Flags ~50% of photographers and ~47% of non-venue.

**Eligible pool (low-exposure, renewing next 2 quarters):** non-venue **302**, photographers **81** (avg plan ~€600).

**Power:**
- *Stage-1 (exposure lift, continuous):* photographers alone (~40/arm) detect ~0.6 SD; pooled non-venue (~150/arm) ~0.32 SD → **well-powered for the mechanism.**
- *Stage-2 (renewal, binary):* −10pp needs ~280/arm; −7pp ~600/arm; −5pp ~1,200/arm. Photographers alone can't reach it. **Pooled low-exposure non-venue enrolled over ~12 months ≈ ~270/arm → powered for ~−10pp only.**

**Spec:**
- Unit = profile_id, 1:1 randomization; **enroll at renewal − 90 days**.
- **Stage-1:** photographers (±pool videographers/music), endpoint = exposure lift, ~6–8 wks → G1.
- **Stage-2:** all low-exposure non-venue **excluding wrong-model retail** (rings/suits/catering/cards), enrolled over ~12 months (~270/arm); primary = renewal rate (powered ~10pp); **pre-register leading indicators** (renewal-intent/NPS, sustained exposure, engagement) so a smaller real effect isn't missed.

---

## Later-phase / parallel value-adds (captured; not in the Stage-1 pilot)

**Free Ad Boost trial → self-serve paid (freemium).** Offer a **2-month free ad boost** — TPW spends a bounded €X driving paid traffic to the profile — that **auto-stops** (no manual cleanup). Afterwards the supplier can **self-enable it as a paid option in their profile and cancel anytime.**
- *Why it's the smart version of the Ad Boost Pool (doc 16):* it sidesteps the adverse-selection problem that killed the original — you don't ask doubters to "pay more" upfront; they **experience** the value free, and only believers convert. Self-serve toggle = no sales effort (fits the automate-and-reduce-sales thesis); auto-stop = bounded cost + ops hygiene (no headache).
- *Reconciles with the data:* leads are a weak lever, but this boosts **exposure** (the real churn driver) and is **felt** (a concrete view jump). Restrict to **categories where ad-driven exposure is plausibly worth it** (doc-16 reality check — skip low-conversion ones like rings/officiants).
- *Silent feasibility + cost-discovery probe (worth doing early, even pre-pilot):* run a small free boost on a handful of **possible churners** to learn, with real money:
  - **Can we boost at profile level?** (gads_api is venue/category-level today — does per-profile work operationally?)
  - **Real CPC by category** and **real cost-per-conversion** — fills the gap in the spend-vs-lose model (doc 17/§5), which ran on doc-16 *estimates*.
  - A **directional** read on whether boosting an at-risk supplier retains them.
  - *Caveat:* feasibility + cost numbers are clean (measured directly); the **retention read is directional only** (uncontrolled → selection/regression-to-mean) — the causal claim still needs the formal holdout pilot. Keep it **separate from the Stage-1/2 arms** so it doesn't confound them.
- *Also a revenue funnel*, not only retention — measure free→paid conversion **and** retention of converters.

---

## Open items / dependencies

- **Pilot sizing** from the actual renewal calendar (how many non-venue terms come up for renewal per quarter).
- **Eng scope** for the "Discover/Rising" surface + cross-rec module + dashboard exposure view.
- **Define the exposure threshold** for targeting and the Stage-1 lift bar.
- **Profile-optimization throughput** — can the scraper process the pilot cohort quickly.

---

## Next steps
1. Size the pilot from the renewal calendar.
2. Scope the eng work (dashboard exposure view, Discover surface, cross-recs, targeting signal).
3. Phased implementation plan across the full strategy.
