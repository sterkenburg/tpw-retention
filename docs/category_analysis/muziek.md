# Muziek — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **60**. Renewal decisions analysed (since 2024-03-01): **156**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 434, median 332  (p10=112  p25=191  p50=332  p75=522  p90=832  p100=1634)
- **Leads/yr:** mean 11.1, median 10  (p10=2  p25=5  p50=10  p75=15  p90=22  p100=38)
- **Got ≥1 lead:** 97% of suppliers
- **Views→leads:** Pearson r = **0.71**, median conversion **2.54 leads / 100 views**
- **Exposure split:** <330 views/yr → 29 suppliers avg 6.7 leads; ≥330 → 31 suppliers avg 15.2 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **22%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 10 | 6% | 50% | 213 |
| 1-2 | 38 | 24% | 37% | 244 |
| 3-5 | 41 | 26% | 17% | 310 |
| 6-10 | 28 | 18% | 21% | 442 |
| 11-20 | 31 | 20% | 6% | 680 |
| 21+ | 8 | 5% | 0% | 1184 |

**Danger zone (≤2 leads/yr): 48 suppliers = 31% of the base, churning at 40%** (vs 14% for those above 2). They average just 237 views/yr.

Thresholds to escape (leads): >2→14%, >5→12%, >10→5%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 156.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 0-99 | 3 | 2% | 67% | 0.7 |
| 100-199 | 34 | 22% | 38% | 3.2 |
| 200-329 | 39 | 25% | 33% | 4.4 |
| 330-499 | 41 | 26% | 10% | 7.1 |
| 500-999 | 26 | 17% | 8% | 10.1 |
| 1000+ | 13 | 8% | 0% | 23.3 |

**Below the 330-view cliff: 76 suppliers = 49% of the base, churning at 37%** (vs 8% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
