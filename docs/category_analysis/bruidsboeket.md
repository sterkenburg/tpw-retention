# Bruidsboeket — views, leads & churn danger zone

_Generated from live data. Active paid suppliers: **42**. Renewal decisions analysed (since 2024-03-01): **72**._

## Exposure & demand (active base, trailing year)

- **Views/yr:** mean 508, median 402  (p10=142  p25=248  p50=402  p75=570  p90=1018  p100=2258)
- **Leads/yr:** mean 11.5, median 10  (p10=2  p25=5  p50=10  p75=18  p90=25  p100=29)
- **Got ≥1 lead:** 93% of suppliers
- **Views→leads:** Pearson r = **0.73**, median conversion **2.03 leads / 100 views**
- **Exposure split:** <330 views/yr → 15 suppliers avg 4.3 leads; ≥330 → 27 suppliers avg 15.4 leads

## Churn danger zone — by LEADS (in the pre-renewal year)

Overall churn for this cohort: **25%**.

| leads/yr | suppliers | % of base | churn rate | avg views/yr |
|---|---|---|---|---|
| 0 | 2 | 3% | 100% | 125 |
| 1-2 | 4 | 6% | 50% | 244 |
| 3-5 | 11 | 15% | 36% | 464 |
| 6-10 | 21 | 29% | 29% | 512 |
| 11-20 | 20 | 28% | 10% | 706 |
| 21+ | 14 | 19% | 14% | 1191 |

**Danger zone (≤2 leads/yr): 6 suppliers = 8% of the base, churning at 67%** (vs 21% for those above 2). They average just 205 views/yr.

Thresholds to escape (leads): >2→21%, >5→18%, >10→12%, >20→14%.

## Churn danger zone — by VIEWS (the upstream driver)

Pre-renewal-year profile views; r(views,leads) here is strong, so views move churn earlier in the funnel. (Suppliers with view history: 72.)

| views/yr | suppliers | % of base | churn rate | avg leads/yr |
|---|---|---|---|---|
| 100-199 | 3 | 4% | 100% | 0.7 |
| 200-329 | 8 | 11% | 38% | 7.1 |
| 330-499 | 19 | 26% | 42% | 6.9 |
| 500-999 | 31 | 43% | 10% | 14.1 |
| 1000+ | 11 | 15% | 9% | 21.1 |

**Below the 330-view cliff: 11 suppliers = 15% of the base, churning at 55%** (vs 20% at ≥330 views/yr).

## Caveats

- Leads from `generate_lead` keyed by `company_id`=`profile_id`.
- Views from `view_item` (`item_list_name`='Profiles index', keyed by `item_id`=`profile_id`) — real profile views only, excludes blog/article rows. History from 2023; this differs slightly from the active-base `views_365d` (supplier_exposure_daily, 2025+).
- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.
- Distribution section = current active base (trailing 365d); danger-zone sections = historical renewal cohort (leads & views in each supplier's pre-decision year).
