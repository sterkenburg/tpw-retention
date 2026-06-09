# Bruidstaarten — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **45**. Renewal decisions analysed (since 2024-03-01): **94**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 781, median 627  (p10=219  p25=442  p50=627  p75=1008  p90=1581  p100=2003)
- **Leads/yr:** mean 20.5, median 21  (p10=3  p25=11  p50=21  p75=28  p90=37  p100=45)
- **Got ≥1 lead:** 93% of suppliers
- **Views→leads:** Pearson r = **0.75**, median conversion **2.66 leads / 100 views**
- **Exposure split:** <330 views/yr → 7 suppliers avg 2.6 leads; ≥330 → 38 suppliers avg 23.8 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **17%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 3 | 3% | 0% | 49 |
| 1-2 | 2 | 2% | 50% | 389 |
| 3-5 | 6 | 6% | 33% | 496 |
| 6-10 | 17 | 18% | 41% | 463 |
| 11-20 | 28 | 30% | 21% | 844 |
| 21+ | 38 | 40% | 0% | 1275 |

**Danger zone (≤2 leads/yr): 5 suppliers = 5% of the base, churning at 20%** (vs 17% for those above 2). They average just 185 views/yr.

Thresholds to escape (leads): >2→17%, >5→16%, >10→9%, >20→0%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 94.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 3 | 3% | 0% | 0.0 |
| 100-199 | 1 | 1% | 100% | 1.0 |
| 330-499 | 21 | 22% | 29% | 8.5 |
| 500-999 | 40 | 43% | 22% | 16.6 |
| 1000+ | 29 | 31% | 0% | 27.8 |

**Below the 330-view cliff: 4 suppliers = 4% of the base, churning at 25%** (vs 17% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
