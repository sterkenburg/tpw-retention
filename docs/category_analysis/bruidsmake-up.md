# Bruidsmake-up — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **65**. Renewal decisions analysed (since 2024-03-01): **155**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 907, median 733  (p10=287  p25=472  p50=733  p75=986  p90=1241  p100=7149)
- **Leads/yr:** mean 21.9, median 18  (p10=7  p25=12  p50=18  p75=30  p90=36  p100=126)
- **Got ≥1 lead:** 98% of suppliers
- **Views→leads:** Pearson r = **0.81**, median conversion **2.88 leads / 100 views**
- **Exposure split:** <330 views/yr → 9 suppliers avg 5.2 leads; ≥330 → 56 suppliers avg 24.6 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **19%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 1-2 | 2 | 1% | 50% | 298 |
| 3-5 | 7 | 5% | 29% | 397 |
| 6-10 | 22 | 14% | 14% | 590 |
| 11-20 | 68 | 44% | 25% | 724 |
| 21+ | 56 | 36% | 11% | 1329 |

**Danger zone (≤2 leads/yr): 2 suppliers = 1% of the base, churning at 50%** (vs 18% for those above 2). They average just 298 views/yr.

Thresholds to escape (leads): >2→18%, >5→18%, >10→19%, >20→11%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 155.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 100-199 | 2 | 1% | 100% | 3.5 |
| 200-329 | 4 | 3% | 25% | 9.2 |
| 330-499 | 27 | 17% | 22% | 10.9 |
| 500-999 | 87 | 56% | 21% | 18.6 |
| 1000+ | 35 | 23% | 6% | 34.1 |

**Below the 330-view cliff: 6 suppliers = 4% of the base, churning at 50%** (vs 17% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
