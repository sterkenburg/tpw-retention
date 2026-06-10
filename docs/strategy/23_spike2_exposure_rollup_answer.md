# 23 — Spike 2 Answer: Exposure Rollup + Dashboard Feed (YOO-229)

**Status:** Spike answer (closes Definition of Done) · **Date:** 2026-06-09 · **Linear:** [YOO-229](https://linear.app/yoonsterkenburg/issue/YOO-229) (parent YOO-227)
**Owner:** Retention (tpw-retention) · analytics_reporting + BigQuery

This closes Spike 2. Source spec: `docs/strategy/21_phase0_confirmation_spikes.md` §Spike 2.
**Definition of done:** reuse-vs-build decision + `supplier_exposure_daily`/`_monthly` schemas + schedule.

---

## TL;DR

| Question | Answer |
|---|---|
| Reuse or build the rollup? | **Reuse** `ga4_dataform_reporting.monthly_profile_stats` via a thin retention job. Already built as WS-A. |
| Where does **rank** come from? | **No Elastic rank snapshot exists in BQ today.** Ship a **category-percentile proxy** now; defer true Elastic rank until Spike 1 (YOO-228) publishes a daily rank snapshot. Rank is **not** Stage-1-blocking. |
| Cross-region handling? | **Resolved by the 2026-06-05 US→EU migration.** Exposure rollup is now a pure server-side EU `INSERT…SELECT`. `business_development` (europe-west3) is still joined in **pandas** in the targeting step (WS-B). |
| Does the dashboard read a BQ reporting table? | **Confirmed.** `src/dashboard/app.py` queries `retention.supplier_stats_daily` directly. `supplier_exposure_monthly` is just a sibling table — **no serving layer**. |
| `_monthly` feed status | Schema proposed below. Full build is **Stage-2** (doc 19 §line 118) — not required to test whether the levers move exposure. |

---

## 1. Reuse-vs-build decision — **REUSE**

`analytics_reporting` already emits a reusable per-supplier daily funnel rollup:
`tpw-ga4-bigquery.ga4_dataform_reporting.monthly_profile_stats` — a
`(profile_id, date, event_name)` skeleton where the metric column **named after
`event_name`** holds the value (the `view_item` row populates `view_item`, etc.).

**Decision:** do **not** rebuild aggregation from raw GA4 events, and do **not**
mutate the reporting table. A **thin retention job** (`src/data/exposure.py`,
driven by `jobs/build_exposure_daily.py`) collapses the per-event skeleton into one
exposure row per `(profile_id, date)` via a server-side `INSERT…SELECT`. The
~388M-row source is never pulled to pandas.

**Freshness — open confirm item:** the retention job is idempotent per date and
runs incrementally (last 3 days), so it self-heals once upstream lands. The one
thing to confirm with the analytics_reporting owner is the **Dataform refresh
cadence of `monthly_profile_stats`** (daily? what hour?) so the retention job is
scheduled to run *after* it. → tracked as a follow-up below.

## 2. `supplier_exposure_daily` schema (built — WS-A)

Lives in `retention` (EU), partitioned by `date`. Source of truth in
`src/data/exposure.py`:

| column | type | meaning |
|---|---|---|
| `profile_id` | STRING | supplier profile |
| `date` | DATE | partition key |
| `profile_views` | INT64 | `view_item` (profile detail views) |
| `impressions` | INT64 | `view_item_list` (listing/search impressions) |
| `list_clicks` | INT64 | `select_item` |
| `show_phone` | INT64 | phone reveals |
| `website_open` | INT64 | outbound website clicks |
| `wishlist` | INT64 | `add_to_wishlist` |
| `purchase` | INT64 | `purchase` |
| `profile_total_time` | INT64 | dwell time |
| `ingested_at` | TIMESTAMP | build stamp |

**Coverage caveat (unchanged):** the source only populates the funnel metrics from
**2025-01 onward**; pre-2025 rows are null → views/impressions are 0 before 2025.
Sufficient for current/recent at-risk targeting. For longer history, blend in raw
`ga4_dataform_output.view_item` (2023+) — out of scope for Stage-1.

**Note — rank is intentionally NOT in the daily table.** See §4.

## 3. `supplier_exposure_monthly` schema (proposed — Stage-2 build)

Sibling **dashboard feed** table, monthly grain, co-located in `retention` (EU).
Aggregates `supplier_exposure_daily` to the month and joins the category benchmark.
Built fully in Stage-2 (doc 19 §line 118); spec'd here to close the spike DoD.

| column | type | meaning | source |
|---|---|---|---|
| `profile_id` | STRING | supplier | daily |
| `month` | DATE | first-of-month partition | daily |
| `profile_views` | INT64 | monthly views | SUM(daily) |
| `impressions` | INT64 | monthly impressions | SUM(daily) |
| `leads` | INT64 | monthly leads | `generate_lead` |
| `category` | STRING | supplier category | business_development |
| `category_median_views` | FLOAT | category benchmark (median views/mo) | computed (cf. `supplier_stats.category_avgs`) |
| `category_rank_pct` | FLOAT | **proxy rank** = percentile of views within category-month | computed |
| `elastic_rank` | INT64 *(nullable)* | true search rank — **null until Spike 1 snapshot** | Elastic (deferred) |
| `tpw_contributed_views` | INT64 | views attributable to TPW levers (boost/email/newsletter UTM) | measurement (WS-E) |
| `ingested_at` | TIMESTAMP | build stamp | — |

`tpw_contributed_views` is the dashboard's headline "TPW's contribution" number; it
depends on the measurement/attribution layer (WS-E + Spike 4 UTM tagging) and lands
with Stage-2, not Stage-1.

## 4. Rank source — no snapshot today; proxy now, true rank later

There is **no Elastic rank anywhere in the repo or in BQ** today (grep-confirmed).
Two paths:

- **(a) True rank** requires the **Elastic/ranking team to publish a daily rank
  snapshot to BigQuery** (`profile_id, date, category, rank`). This is a natural
  rider on **Spike 1 (YOO-228)** — the same team, the same surface direction — so
  it's folded there rather than opening a third integration.
- **(b) Interim proxy** = **category-percentile of `profile_views`** within each
  category-month (`category_rank_pct` above). We already compute category
  benchmarks/averages in `src/analytics/supplier_stats.py`, so this is pure SQL over
  tables we own — no external dependency.

**Decision:** ship the **proxy** now; leave `elastic_rank` nullable and backfill it
once Spike 1 lands a snapshot. Per doc 19 §line 118, true rank is **not required**
to test whether the levers move exposure, so this does not block Stage-1.

## 5. Cross-region handling — resolved

The cross-region concern in the spike spec is **resolved by the 2026-06-05
migration** that consolidated the `retention` dataset **US→EU** (see
`config/settings.yaml`: `dataset` = `dataset_eu` = `retention`, location `EU`):

- **Exposure rollup** — source (`ga4_dataform_reporting`, EU) and destination
  (`retention`, EU) are now co-located → the build is a pure **server-side
  `INSERT…SELECT`**, no region hop.
- **business_development** lives in `churn_prediction` (**europe-west3**) — a
  different region that **cannot be joined to EU sources in one BQ job**. It is
  therefore joined in **pandas** in the targeting step (`src/signals/targeting.py`,
  WS-B), which is the standing, intentional pattern.

**Cleanup item:** the `src/data/exposure.py` module docstring still references the
old `retention_eu`/US split — stale after the migration. Worth a one-line update
(non-blocking).

## 6. Dashboard feed — confirmed, no serving layer

Confirmed: the supplier dashboard reads **BigQuery reporting tables directly** —
`src/dashboard/app.py` queries `tpw-ga4-bigquery.retention.supplier_stats_daily`
(and `actions_log`) via the BQ client. Therefore `supplier_exposure_monthly` is
just **another sibling reporting table the dashboard reads** — there is **no
separate serving layer** to build (consistent with doc 19 §3 and the Spike scope
note).

## 7. Schedule

- **`supplier_exposure_daily`** — incremental rebuild of the trailing 3 days
  (idempotent per date), run **daily** as a Cloud Run job, sequenced **after**
  `monthly_profile_stats` refreshes (cadence to confirm — §1) and **before**
  `build_targeting`. Backfill path: `python jobs/build_exposure_daily.py <start> <end>`.
- **`supplier_exposure_monthly`** — **monthly** job on the **1st** (aligned with
  `email.monthly_send_day: 1` in settings), aggregating the prior month + joining
  the category benchmark. Stage-2.

## 8. Definition of Done — status

| DoD item | Status |
|---|---|
| Reuse-vs-build decision | ✅ **Reuse** (§1) |
| `supplier_exposure_daily` schema | ✅ Built, documented (§2) |
| `supplier_exposure_monthly` schema | ✅ Proposed (§3); build is Stage-2 |
| Schedule | ✅ Defined (§7) |

**Spike 2 is answered.** Remaining work is implementation, not investigation, and
is Stage-2 / dependency-gated:

1. Confirm `monthly_profile_stats` Dataform refresh cadence with analytics_reporting owner (schedules the daily job).
2. Fold a **daily rank snapshot** request into Spike 1 (YOO-228) for the Elastic team.
3. Build `supplier_exposure_monthly` + `tpw_contributed_views` attribution (Stage-2, with WS-E + Spike 4 UTM).
4. Tidy the stale `retention_eu`/US docstring in `src/data/exposure.py`.
