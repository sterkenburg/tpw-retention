# Entertainment — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **24**. Renewal decisions analysed (since 2024-03-01): **71**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 274, median 244  (p10=48  p25=119  p50=244  p75=330  p90=536  p100=983)
- **Leads/yr:** mean 5.4, median 4  (p10=0  p25=2  p50=4  p75=6  p90=10  p100=31)
- **Got ≥1 lead:** 79% of suppliers
- **Views→leads:** Pearson r = **0.88**, median conversion **1.60 leads / 100 views**
- **Exposure split:** <330 views/yr → 18 suppliers avg 2.9 leads; ≥330 → 6 suppliers avg 12.8 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **39%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 7 | 10% | 86% | 92 |
| 1-2 | 17 | 24% | 35% | 244 |
| 3-5 | 17 | 24% | 41% | 293 |
| 6-10 | 20 | 28% | 35% | 402 |
| 11-20 | 7 | 10% | 29% | 736 |
| 21+ | 3 | 4% | 0% | 951 |

**Danger zone (≤2 leads/yr): 24 suppliers = 34% of the base, churning at 50%** (vs 34% for those above 2). They average just 199 views/yr.

Thresholds to escape (leads): >2→34%, >5→30%, >10→20%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 71.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 6 | 8% | 83% | 1.7 |
| 100-199 | 14 | 20% | 50% | 2.5 |
| 200-329 | 22 | 31% | 32% | 4.1 |
| 330-499 | 15 | 21% | 33% | 5.7 |
| 500-999 | 12 | 17% | 33% | 12.8 |
| 1000+ | 2 | 3% | 0% | 23.5 |

**Below the 330-view cliff: 42 suppliers = 59% of the base, churning at 45%** (vs 31% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
