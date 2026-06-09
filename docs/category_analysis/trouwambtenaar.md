# Trouwambtenaar — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **93**. Renewal decisions analysed (since 2024-03-01): **238**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 482, median 327  (p10=118  p25=227  p50=327  p75=488  p90=913  p100=3828)
- **Leads/yr:** mean 7.3, median 5  (p10=1  p25=3  p50=5  p75=8  p90=15  p100=68)
- **Got ≥1 lead:** 92% of suppliers
- **Views→leads:** Pearson r = **0.84**, median conversion **1.45 leads / 100 views**
- **Exposure split:** <330 views/yr → 49 suppliers avg 4.6 leads; ≥330 → 44 suppliers avg 10.3 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **30%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 21 | 9% | 62% | 181 |
| 1-2 | 53 | 22% | 42% | 277 |
| 3-5 | 70 | 29% | 26% | 398 |
| 6-10 | 43 | 18% | 19% | 496 |
| 11-20 | 41 | 17% | 24% | 594 |
| 21+ | 10 | 4% | 10% | 2111 |

**Danger zone (≤2 leads/yr): 74 suppliers = 31% of the base, churning at 47%** (vs 23% for those above 2). They average just 250 views/yr.

Thresholds to escape (leads): >2→23%, >5→20%, >10→22%, >20→10%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 238.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 5 | 2% | 60% | 1.6 |
| 100-199 | 40 | 17% | 65% | 1.7 |
| 200-329 | 60 | 25% | 28% | 4.4 |
| 330-499 | 64 | 27% | 25% | 5.8 |
| 500-999 | 54 | 23% | 17% | 8.5 |
| 1000+ | 15 | 6% | 7% | 24.9 |

**Below the 330-view cliff: 105 suppliers = 44% of the base, churning at 44%** (vs 20% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
