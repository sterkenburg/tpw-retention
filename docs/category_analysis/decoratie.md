# Decoratie — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **27**. Renewal decisions analysed (since 2024-03-01): **57**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 388, median 307  (p10=72  p25=165  p50=307  p75=474  p90=580  p100=2483)
- **Leads/yr:** mean 5.6, median 4  (p10=0  p25=2  p50=4  p75=8  p90=13  p100=17)
- **Got ≥1 lead:** 81% of suppliers
- **Views→leads:** Pearson r = **0.10**, median conversion **1.18 leads / 100 views**
- **Exposure split:** <330 views/yr → 15 suppliers avg 3.6 leads; ≥330 → 12 suppliers avg 8.0 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **33%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 7 | 12% | 43% | 814 |
| 1-2 | 9 | 16% | 44% | 578 |
| 3-5 | 12 | 21% | 17% | 338 |
| 6-10 | 19 | 33% | 32% | 491 |
| 11-20 | 10 | 18% | 40% | 564 |

**Danger zone (≤2 leads/yr): 16 suppliers = 28% of the base, churning at 44%** (vs 29% for those above 2). They average just 682 views/yr.

Thresholds to escape (leads): >2→29%, >5→34%, >10→40%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 57.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 100-199 | 4 | 7% | 50% | 1.8 |
| 200-329 | 13 | 23% | 38% | 3.6 |
| 330-499 | 17 | 30% | 6% | 6.1 |
| 500-999 | 19 | 33% | 53% | 9.3 |
| 1000+ | 4 | 7% | 25% | 4.5 |

**Below the 330-view cliff: 17 suppliers = 30% of the base, churning at 41%** (vs 30% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
