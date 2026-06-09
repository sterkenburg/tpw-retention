# Weddingplanner — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **58**. Renewal decisions analysed (since 2024-03-01): **140**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 297, median 291  (p10=108  p25=189  p50=291  p75=358  p90=524  p100=748)
- **Leads/yr:** mean 2.1, median 2  (p10=0  p25=1  p50=2  p75=3  p90=4  p100=7)
- **Got ≥1 lead:** 81% of suppliers
- **Views→leads:** Pearson r = **0.46**, median conversion **0.67 leads / 100 views**
- **Exposure split:** <330 views/yr → 37 suppliers avg 1.6 leads; ≥330 → 21 suppliers avg 3.1 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **38%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 34 | 24% | 47% | 207 |
| 1-2 | 53 | 38% | 38% | 301 |
| 3-5 | 37 | 26% | 27% | 371 |
| 6-10 | 14 | 10% | 36% | 408 |
| 11-20 | 2 | 1% | 100% | 963 |

**Danger zone (≤2 leads/yr): 87 suppliers = 62% of the base, churning at 41%** (vs 32% for those above 2). They average just 264 views/yr.

Thresholds to escape (leads): >2→32%, >5→44%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 140.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 7 | 5% | 71% | 0.3 |
| 100-199 | 25 | 18% | 56% | 1.2 |
| 200-329 | 51 | 36% | 39% | 1.7 |
| 330-499 | 41 | 29% | 24% | 4.0 |
| 500-999 | 15 | 11% | 20% | 3.6 |
| 1000+ | 1 | 1% | 100% | 11.0 |

**Below the 330-view cliff: 83 suppliers = 59% of the base, churning at 47%** (vs 25% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
