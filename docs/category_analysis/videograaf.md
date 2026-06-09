# Videograaf — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **58**. Renewal decisions analysed (since 2024-03-01): **155**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 376, median 328  (p10=150  p25=220  p50=328  p75=423  p90=551  p100=1698)
- **Leads/yr:** mean 5.7, median 4  (p10=1  p25=2  p50=4  p75=8  p90=11  p100=23)
- **Got ≥1 lead:** 90% of suppliers
- **Views→leads:** Pearson r = **0.57**, median conversion **1.28 leads / 100 views**
- **Exposure split:** <330 views/yr → 29 suppliers avg 3.2 leads; ≥330 → 29 suppliers avg 8.1 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **30%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 11 | 7% | 36% | 224 |
| 1-2 | 33 | 21% | 36% | 312 |
| 3-5 | 53 | 34% | 28% | 394 |
| 6-10 | 40 | 26% | 35% | 548 |
| 11-20 | 14 | 9% | 7% | 508 |
| 21+ | 4 | 3% | 0% | 949 |

**Danger zone (≤2 leads/yr): 44 suppliers = 28% of the base, churning at 36%** (vs 27% for those above 2). They average just 290 views/yr.

Thresholds to escape (leads): >2→27%, >5→26%, >10→6%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 155.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 1 | 1% | 0% | 0.0 |
| 100-199 | 16 | 10% | 50% | 1.8 |
| 200-329 | 53 | 34% | 32% | 3.6 |
| 330-499 | 48 | 31% | 23% | 6.4 |
| 500-999 | 29 | 19% | 31% | 7.8 |
| 1000+ | 8 | 5% | 12% | 11.2 |

**Below the 330-view cliff: 70 suppliers = 45% of the base, churning at 36%** (vs 25% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
