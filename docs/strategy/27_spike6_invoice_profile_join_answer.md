# 27 — Spike 6 Answer: Invoice → `profile_id` Join (YOO-233)

**Status:** Spike answer (closes Definition of Done) · **Date:** 2026-06-09 · **Linear:** [YOO-233](https://linear.app/yoonsterkenburg/issue/YOO-233) (parent YOO-227)
**Owner:** Lifecycle (tpw-lifecycle) · invoice_service

Source spec: `docs/strategy/21_phase0_confirmation_spikes.md` §Spike 6. Revenue-source decision: doc 19 §7.
**Definition of done:** documented join key + coverage + a per-supplier revenue view. *(Stage-1 proceeds on `business_development.plan_value` interim.)*

> Investigated against live BigQuery (`bq`) on 2026-06-09. Two corrections to the
> strategy-doc assumptions surfaced — see §1.

---

## TL;DR

| Item | Finding |
|---|---|
| Where the data actually lives | **Not** `finance_dashboard.matched_invoices`. It's the **`moneybird`** dataset: **`moneybird.mb-2015-2020`** (invoices) + **`moneybird.mb-contacts`** (contacts). §1 |
| Join key | invoice **`klantnummer`** (INT) → contact **`customer_id`** (INT) → **`companies_profiles.moneybird_customer_id`** (STRING, 100% numeric → CAST) → **`profile_id`**. §2 |
| Coverage (the number that matters) | **98.6% of active paid suppliers** (1,524 / 1,545) carry a `moneybird_customer_id`; 100% have a profiles row. §3 |
| Per-supplier revenue view | SQL drafted (§4) — **cannot execute yet**: the `moneybird.*` tables are **Drive-backed external tables** and the current credentials lack **Drive scope**. §5 |
| Recommendation | Keep `plan_value` for Stage-1 (DoD allows it). Switch to Moneybird revenue once two blockers clear: **(1) Drive scope**, **(2) confirm invoice recency** (table named `…2015-2020`). §5–6 |

---

## 1. Where the revenue data actually lives (correction)

The strategy docs reference `finance_dashboard.matched_invoices`. **That dataset/table
does not exist.** Live inspection found:

- **`tpw-ga4-bigquery.moneybird.mb-2015-2020`** — invoices (EXTERNAL table)
- **`tpw-ga4-bigquery.moneybird.mb-contacts`** — Moneybird contacts (EXTERNAL table)

Both are **EXTERNAL tables backed by Google Drive/Sheets** (not native BQ). Naming in
docs 19/20/21 should be corrected to `moneybird.*`.

**Invoice schema (relevant cols):** `id`, `factuurnummer`, `status`, `factuurdatum`
(DATE), `vervaldatum`, `contact` (STRING), **`klantnummer`** (INT — Moneybird customer
no.), `referentie`, **`totaalprijs_inclusief_btw__EUR_`** / `…exclusief_btw__EUR_`
(FLOAT, revenue), `betaald_op` (DATE paid).
**Contacts schema:** `id`, `company_name`, `email`, **`customer_id`** (INT), …
**Bridge (`companies_profiles`):** `profile_id` (INT), **`moneybird_customer_id`**
(STRING), `company_id`, `profile_email`, `category_name`.

## 2. Join key

```
moneybird.mb-2015-2020.klantnummer  (INT, Moneybird customer number)
   = moneybird.mb-contacts.customer_id  (INT)                 -- contact identity
   = CAST(companies_profiles.moneybird_customer_id AS INT64)  -- STRING, 100% numeric
   → companies_profiles.profile_id  (INT)                     -- the supplier key
```

- `companies_profiles.moneybird_customer_id` is **100% numeric**, so `CAST(... AS
  INT64)` is safe to match the INT invoice/contact keys.
- **Likely shortcut:** `moneybird_customer_id` is almost certainly the Moneybird
  customer number == invoice `klantnummer` **directly**, so the `mb-contacts` hop may
  be unnecessary (contacts is useful for company_name/email enrichment). **Confirm
  `klantnummer` vs `customer_id` semantics once Drive scope lands** (§5).

## 3. Coverage

Measured live (companies_profiles is native EU; counts exact):

| Population | Count | With `moneybird_customer_id` |
|---|---|---|
| All profiles | 50,944 (47,630 distinct ids) | 3,632 distinct (~8%) — most profiles are free/unclaimed |
| **Active paid suppliers** (`plan_end ≥ now AND plan_value > 0`) | **1,545** | **1,524 (98.6%)** |
| (all active paid had a `companies_profiles` row) | 1,545 | 100% |

**The 98.6% on the active-paid cohort is the number that matters** — the lifecycle
pilot universe is essentially fully covered by the Moneybird bridge. The low 8%
overall is just the 50k free profiles that were never customers.

> Cross-region note (consistent with Spikes 2–4): `business_development` is
> **europe-west3**, `companies_profiles` is **EU** — they can't be joined in one BQ
> job. The overlap above was measured by materialising the 1,545 active ids and
> matching in EU. The standing pattern (pandas join across regions) applies to the
> revenue join too.

## 4. Per-supplier revenue view (draft)

To create once Drive scope lands (names assume the direct `klantnummer` ==
`moneybird_customer_id` link; add the `mb-contacts` hop if §2 confirms it's needed):

```sql
CREATE OR REPLACE VIEW `tpw-ga4-bigquery.retention.vw_supplier_revenue` AS
WITH inv AS (
  SELECT
    klantnummer                                   AS moneybird_customer_id,
    factuurdatum                                  AS invoice_date,
    totaalprijs_inclusief_btw__EUR_               AS amount_incl_vat_eur,
    totaalprijs_exclusief_btw__EUR_               AS amount_excl_vat_eur,
    status, betaald_op
  FROM `tpw-ga4-bigquery.moneybird.mb-2015-2020`
  WHERE status IN ('paid','Betaald')               -- confirm status vocab
)
SELECT
  p.profile_id,
  p.profile_name,
  p.category_name,
  COUNT(*)                                          AS invoices_all_time,
  SUM(inv.amount_excl_vat_eur)                      AS revenue_excl_vat_all_time,
  -- trailing-12-month run-rate = ARR proxy
  SUM(IF(inv.invoice_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH),
         inv.amount_excl_vat_eur, 0))               AS arr_ttm_eur,
  MAX(inv.invoice_date)                             AS last_invoice_date
FROM `tpw-ga4-bigquery.ga4_dataform_seed.companies_profiles` p
JOIN inv
  ON CAST(p.moneybird_customer_id AS INT64) = inv.moneybird_customer_id
WHERE p.moneybird_customer_id IS NOT NULL AND TRIM(p.moneybird_customer_id) != ''
GROUP BY 1,2,3
```

- **ARR** = trailing-12-month invoiced revenue (run-rate); **churn-value** = last
  active ARR at the time a supplier lapses (joins to `business_development` plan
  dates). Both derive cleanly from this view once it's populated.

## 5. Blockers (why it's interim, not live)

1. **Drive scope.** Querying `moneybird.*` fails with *"Permission denied while
   getting Drive credentials."* The external tables need the BQ service/user
   credential to carry the **Google Drive OAuth scope**, or the sheets to be
   materialised into a native BQ table by `invoice_service`. **→ owner action.**
2. **Recency.** The invoice table is named **`mb-2015-2020`** — if it really stops at
   2020 it's useless for *current* ARR. Must confirm `MAX(factuurdatum)` once §1
   access lands; if stale, get the current invoice feed from `invoice_service`.
3. **Status vocabulary + key semantics** (`status` values; `klantnummer` vs
   `customer_id`) — confirm on first real query.

## 6. Definition of Done — status

| DoD item | Status |
|---|---|
| Join key | ✅ Documented (§2) — `klantnummer`→`customer_id`→`moneybird_customer_id`(CAST)→`profile_id` |
| Coverage | ✅ Measured (§3) — **98.6% of active paid suppliers** |
| Per-supplier revenue view | ✅ Drafted (§4); execution blocked on Drive scope (§5) |
| Interim | ✅ Stage-1 stays on `business_development.plan_value` |

**Spike 6 is answered.** The join is viable and well-covered; the only thing standing
between us and Moneybird-based ARR is **operational access** (Drive scope) +
**recency confirmation**, both owned by `invoice_service`. No need to block Stage-1 —
`plan_value` carries it (doc 19 §7 names Moneybird as the eventual source of truth).

**Follow-ups:** (1) grant Drive scope or materialise `moneybird.*` to native BQ;
(2) confirm invoice recency (`MAX(factuurdatum)`) + `status`/key semantics;
(3) create `vw_supplier_revenue` (§4) and swap `plan_value` → ARR in value/churn
measurement; (4) fix the `finance_dashboard.matched_invoices` naming in docs 19/20/21.
