# Trouwfotograaf — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **227**. Renewal decisions analysed (since 2024-03-01): **620**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 409, median 310  (p10=149  p25=213  p50=310  p75=434  p90=713  p100=3685)
- **Leads/yr:** mean 6.0, median 5  (p10=1  p25=2  p50=5  p75=8  p90=12  p100=52)
- **Got ≥1 lead:** 92% of suppliers
- **Views→leads:** Pearson r = **0.76**, median conversion **1.44 leads / 100 views**
- **Exposure split:** <330 views/yr → 126 suppliers avg 4.1 leads; ≥330 → 101 suppliers avg 8.4 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **27%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 68 | 11% | 44% | 231 |
| 1-2 | 174 | 28% | 30% | 277 |
| 3-5 | 207 | 33% | 29% | 372 |
| 6-10 | 125 | 20% | 18% | 534 |
| 11-20 | 40 | 6% | 8% | 845 |
| 21+ | 6 | 1% | 17% | 3426 |

**Danger zone (≤2 leads/yr): 242 suppliers = 39% of the base, churning at 34%** (vs 23% for those above 2). They average just 264 views/yr.

Thresholds to escape (leads): >2→23%, >5→15%, >10→9%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 620.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 14 | 2% | 50% | 0.3 |
| 100-199 | 90 | 15% | 39% | 2.4 |
| 200-329 | 231 | 37% | 33% | 3.1 |
| 330-499 | 152 | 25% | 25% | 4.7 |
| 500-999 | 103 | 17% | 12% | 6.8 |
| 1000+ | 30 | 5% | 3% | 16.1 |

**Below the 330-view cliff: 335 suppliers = 54% of the base, churning at 36%** (vs 18% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
