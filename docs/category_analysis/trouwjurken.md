# Trouwjurken — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **99**. Renewal decisions analysed (since 2024-03-01): **271**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 665, median 515  (p10=207  p25=362  p50=515  p75=816  p90=1230  p100=2791)
- **Leads/yr:** mean 4.7, median 3  (p10=0  p25=2  p50=3  p75=6  p90=9  p100=48)
- **Got ≥1 lead:** 84% of suppliers
- **Views→leads:** Pearson r = **0.33**, median conversion **0.51 leads / 100 views**
- **Exposure split:** <330 views/yr → 23 suppliers avg 2.0 leads; ≥330 → 76 suppliers avg 5.5 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **14%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 56 | 21% | 16% | 341 |
| 1-2 | 88 | 32% | 15% | 602 |
| 3-5 | 66 | 24% | 18% | 838 |
| 6-10 | 43 | 16% | 9% | 890 |
| 11-20 | 12 | 4% | 0% | 1491 |
| 21+ | 6 | 2% | 0% | 949 |

**Danger zone (≤2 leads/yr): 144 suppliers = 53% of the base, churning at 15%** (vs 13% for those above 2). They average just 500 views/yr.

Thresholds to escape (leads): >2→13%, >5→7%, >10→0%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 270.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 3 | 1% | 67% | 0.7 |
| 100-199 | 13 | 5% | 15% | 0.6 |
| 200-329 | 45 | 17% | 29% | 1.9 |
| 330-499 | 68 | 25% | 15% | 2.4 |
| 500-999 | 93 | 34% | 12% | 5.2 |
| 1000+ | 49 | 18% | 0% | 8.4 |

**Below the 330-view cliff: 61 suppliers = 23% of the base, churning at 28%** (vs 10% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
