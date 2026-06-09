# Bruidskapsels — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **40**. Renewal decisions analysed (since 2024-03-01): **102**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 581, median 532  (p10=211  p25=367  p50=532  p75=666  p90=853  p100=2620)
- **Leads/yr:** mean 16.5, median 15  (p10=6  p25=10  p50=15  p75=21  p90=28  p100=40)
- **Got ≥1 lead:** 100% of suppliers
- **Views→leads:** Pearson r = **0.74**, median conversion **2.98 leads / 100 views**
- **Exposure split:** <330 views/yr → 9 suppliers avg 7.0 leads; ≥330 → 31 suppliers avg 19.3 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **21%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 5 | 5% | 60% | 112 |
| 1-2 | 8 | 8% | 50% | 213 |
| 3-5 | 14 | 14% | 14% | 282 |
| 6-10 | 27 | 26% | 22% | 459 |
| 11-20 | 29 | 28% | 14% | 627 |
| 21+ | 19 | 19% | 11% | 1045 |

**Danger zone (≤2 leads/yr): 13 suppliers = 13% of the base, churning at 54%** (vs 16% for those above 2). They average just 174 views/yr.

Thresholds to escape (leads): >2→16%, >5→16%, >10→12%, >20→11%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 102.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 2 | 2% | 50% | 0.0 |
| 100-199 | 11 | 11% | 45% | 2.9 |
| 200-329 | 19 | 19% | 26% | 4.6 |
| 330-499 | 20 | 20% | 30% | 10.1 |
| 500-999 | 42 | 41% | 7% | 15.7 |
| 1000+ | 8 | 8% | 12% | 28.6 |

**Below the 330-view cliff: 32 suppliers = 31% of the base, churning at 34%** (vs 14% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
