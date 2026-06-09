# Category analysis — views, leads & churn danger zone

Per-category reports on supplier **exposure (views)**, **demand (leads)**, and the
**churn "danger zone"** (churn rate by leads received before renewal). One report
per marketplace category, generated identically so they're directly comparable.

> **▶ Start with the synthesis: [00_bundle_priority.md](00_bundle_priority.md)** —
> ranks categories into bundle-priority tiers by Exposure-Addressable Revenue.
> Regenerate with `python jobs/bundle_priority.py`.

## How to generate

```bash
python jobs/analyze_category.py            # list categories with active suppliers
python jobs/analyze_category.py "Trouwfotograaf"   # write docs/category_analysis/<slug>.md
```

Logic lives in `src/analytics/category_report.py`. Re-run any time the underlying
tables refresh.

## What each report contains

1. **Exposure & demand (active base):** views/yr and leads/yr distributions, % with
   ≥1 lead, the **views→leads** correlation + conversion (leads per 100 views), and
   the low- vs higher-exposure lead split (<330 vs ≥330 views/yr).
2. **Churn danger zone — by LEADS:** churn rate by leads-in-the-pre-renewal-year,
   avg views per bucket, the size of the ≤2-leads group, escape thresholds.
3. **Churn danger zone — by VIEWS:** churn rate by views-in-the-pre-renewal-year
   (the upstream driver), avg leads per bucket, and the share below the 330-view
   cliff. Views are typically the **cleaner, more monotonic** churn signal.

## Method (identical across categories)

| element | definition |
|---|---|
| Active base | `retention.supplier_targeting` (current active paid suppliers) |
| Views | `views_365d` (trailing year, from `supplier_exposure_daily`) |
| Leads | `ga4_dataform_output.generate_lead`, keyed by `company_id` = `profile_id` |
| Views (history) | `ga4_dataform_output.view_item`, `item_list_name`='Profiles index', keyed by `item_id` = `profile_id` (2023+) |
| Renewal cohort | `business_development` decisions with an **observed** outcome (next plan exists), `plan_end ≥ 2024-03-01` so the full prior-year of leads/views is in range |
| Churn | next plan downgraded to `Gratis` |
| Danger zone | ≤2 leads (or <330 views) in the year before the renewal decision |

> Lead category strings in `generate_lead` are lowercase-hyphenated and unreliable;
> always join on `company_id`=`profile_id`, never on the lead-side category string.
> For views, **must** filter `view_item` to `item_list_name`='Profiles index' — it
> also contains blog/article rows whose `item_id` can collide with a `profile_id`.

## Segment baseline (reference for low-N categories)

For **non-venue lead-driven** suppliers overall (2,227 decisions, the pooled
reference when a single category has too few renewals for stable per-bucket rates):

| leads/yr | % of base | churn rate |
|---|---|---|
| 0 | 11% | 39% |
| 1–2 | 23% | 32% |
| 3–5 | 25% | 27% |
| 6–10 | 19% | 23% |
| 11–20 | 14% | 18% |
| 21+ | 7% | 7% |

- **Danger zone (≤2 leads/yr): ~35% of the base, churning at 35%** (vs 22% above 2).
- **Escape thresholds:** >5 leads/yr → ~baseline; **>10 → 15%**; **21+ → 7%**.
- Leads relate to churn **monotonically but with a high bar** — escaping needs
  ~10+ leads/yr ≈ ~690 views/yr (at ~1.45 leads/100 views), >2× the median. So the
  realistic lever is **upstream exposure**, not buying leads (see docs/strategy/17–18).
- **Views is the cleaner cut.** In the photographer report the by-views churn curve
  is smoothly monotonic (50% → 3%) with **54% of the cohort below the 330-view cliff
  churning at 36% vs 18% above** — the clearest single articulation of the thesis.
  Read each category's **by-VIEWS** table as the primary signal; leads is downstream.

This is the segment whose categories warrant individual reports (venue and retail
run on different models — see the `segment` definition in `targeting.py`).

## Index (non-venue)

Sorted by active suppliers. **Danger zone** = share with ≤2 leads/yr; **churn** = cohort churn rate.

| category | active | decisions | churn | ≤2-lead danger zone | report |
|---|---|---|---|---|---|
| Trouwfotograaf | 227 | 620 | 27% | 39% | [trouwfotograaf.md](trouwfotograaf.md) |
| Trouwjurken | 99 | 271 | 14% | 53% | [trouwjurken.md](trouwjurken.md) |
| Trouwambtenaar | 93 | 238 | 30% | 31% | [trouwambtenaar.md](trouwambtenaar.md) |
| Bruidsmake-up | 65 | 155 | 19% | 1% | [bruidsmake-up.md](bruidsmake-up.md) |
| Muziek | 60 | 156 | 22% | 31% | [muziek.md](muziek.md) |
| Videograaf | 58 | 155 | 30% | 28% | [videograaf.md](videograaf.md) |
| Weddingplanner | 58 | 140 | 38% | 62% | [weddingplanner.md](weddingplanner.md) |
| Bruidstaarten | 45 | 94 | 17% | 5% | [bruidstaarten.md](bruidstaarten.md) |
| Bruidsboeket | 42 | 72 | 25% | 8% | [bruidsboeket.md](bruidsboeket.md) |
| Bruidskapsels | 40 | 102 | 21% | 13% | [bruidskapsels.md](bruidskapsels.md) |
| Decoratie | 27 | 57 | 33% | 28% | [decoratie.md](decoratie.md) |
| Entertainment | 24 | 71 | 39% | 34% | [entertainment.md](entertainment.md) |
| Huwelijksnacht | 12 | 56 | 45% | 86% | [huwelijksnacht.md](huwelijksnacht.md) |

_Skipped (too few active suppliers): Verhuur (9), Trouwen in het buitenland (2), Huwelijksreis (1)._
_Regenerate all with `python jobs/analyze_category.py --non-venue`._

## Cross-category observations

- **Churn and the danger zone vary widely** — categories are not interchangeable, so
  targeting and the lift bar should be set per category, not globally.
- **High-churn, lead-starved (clearest bundle candidates):** Weddingplanner (38% churn,
  62% danger zone), Huwelijksnacht (45% / 86%), Entertainment (39% / 34%),
  Trouwfotograaf (27% / 39%). Exposure redistribution should land hardest here.
- **Lead volume ≠ churn for everyone.** Trouwjurken (dresses) sits in the ≤2-lead zone
  for 53% of suppliers yet churns at only **14%** — the *lowest* of any category. For
  dresses, leads through the platform aren't the value/retention mechanism (couples
  browse and buy differently), so the lead-based danger zone over-flags them. Read the
  **by-VIEWS** table and the churn rate, not the lead count, before acting.
- **Well-served, low danger zone:** Bruidsmake-up (1%), Bruidstaarten (5%),
  Bruidsboeket (8%) get plenty of leads relative to the threshold — exposure is not
  their problem; any churn there is a different lever (pricing/fit).
