# Huwelijksnacht — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **12**. Renewal decisions analysed (since 2024-03-01): **56**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 74, median 61  (p10=10  p25=25  p50=61  p75=106  p90=112  p100=248)
- **Leads/yr:** mean 0.7, median 0  (p10=0  p25=0  p50=0  p75=1  p90=2  p100=2)
- **Got ≥1 lead:** 50% of suppliers
- **Views→leads:** Pearson r = **0.68**, median conversion **0.81 leads / 100 views**
- **Exposure split:** <330 views/yr → 12 suppliers avg 0.7 leads; ≥330 → 0 suppliers avg <NA> leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **45%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 21 | 38% | 33% | 54 |
| 1-2 | 27 | 48% | 48% | 105 |
| 3-5 | 7 | 12% | 57% | 179 |
| 6-10 | 1 | 2% | 100% | 799 |

**Danger zone (≤2 leads/yr): 48 suppliers = 86% of the base, churning at 42%** (vs 62% for those above 2). They average just 83 views/yr.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 55.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 33 | 59% | 36% | 0.7 |
| 100-199 | 18 | 32% | 61% | 1.6 |
| 200-329 | 3 | 5% | 0% | 2.0 |
| 330-499 | 1 | 2% | 100% | 4.0 |
| 500-999 | 1 | 2% | 100% | 8.0 |

**Below the 330-view cliff: 54 suppliers = 96% of the base, churning at 43%** (vs 100% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
