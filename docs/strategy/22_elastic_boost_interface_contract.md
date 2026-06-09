# 22 — Elastic `retention_boost` Interface Contract (YOO-228)

**Status:** Draft for the TPW Elastic team · **Date:** 2026-06-05 · **Linear:** [YOO-228](https://linear.app/yoonsterkenburg/issue/YOO-228) (parent YOO-227)
**Owner of this doc:** Retention (tpw-retention) · **Owner of the Elastic side:** TPW ranking team

This is the integration contract for the **core retention lever**: a per-supplier
placement boost applied **only in the free/organic ranking layer**, never to paid
premium spots. It defines the **stable surface** the retention platform publishes,
exactly what the ranker must read, and the guarantees each side commits to — so
the Elastic side can be built without depending on retention internals.

---

## 1. What the boost is (and is not)

- **Is:** an additive, bounded relevance boost for at-risk / low-exposure suppliers
  (low-exposure non-venue: photographers ± videographers/music in Stage-1), so they
  surface more in organic/long-tail/regional results and non-premium discovery
  modules. Goal: lift a bottom-quintile supplier (~180 views/yr) toward the
  category median (~330/yr), ≈ **+12 views/month**.
- **Is NOT:** anything that touches **paid premium inventory**. Premium top spots
  are a revenue product and are **off-limits** — no pinning, no premium-slot
  reweighting, no displacement of paid placements. (docs/strategy/18, Lever 1.)
- **Is experiment-gated:** only the **treatment** arm of the running holdout is
  boosted. The **control** arm must rank exactly as it does today — this is what
  makes the pilot measurable.

---

## 2. Division of responsibility

| Retention platform (this repo) owns | Elastic / ranking team owns |
|---|---|
| Who is treatment vs control (holdout) | How supplier ranking is scored today |
| The published boost flag + magnitude + window | How **premium** is implemented + kept isolated |
| Holdout integrity (control never flagged) | Reading the flag + applying `function_score` in the **non-premium** layer |
| Master kill-switch on the data surface | Query-level feature flag for instant disable |
| Guardrail measurement (CTR, view→lead) | Emitting **which results were boosted** (impression logging) |

---

## 3. The published surface (the contract)

The retention platform publishes **one stable BigQuery view** in the (US) `retention`
dataset. This is the *only* object the Elastic side reads — internal tables
(`retention_directives`, `cohort_assignment`) may change; this view will not, except
by versioned change agreed here.

**`tpw-ga4-bigquery.retention.vw_elastic_retention_boost`**

| column | type | meaning |
|---|---|---|
| `profile_id` | STRING | Supplier profile id (matches the Elastic supplier document id / `profile_id` field) |
| `retention_boost` | BOOL | **TRUE only** for an active, non-gated, treatment-arm boost. Never TRUE for control. |
| `boost_weight` | FLOAT64 | Magnitude knob (see §5). Default `1.0`. Ignore if `retention_boost = FALSE`. |
| `layer` | STRING | Always `"free"`. A guardrail assertion — if it is ever not `"free"`, **do not apply**. |
| `experiment_id` | STRING | e.g. `stage1_exposure`. For logging/attribution. |
| `valid_from` | TIMESTAMP | Boost active from (inclusive). |
| `valid_to` | TIMESTAMP | Boost active until (exclusive); NULL = open-ended. |
| `updated_at` | TIMESTAMP | Last refresh of this row. |

**Contract semantics:**
- **Absence of a row, or `retention_boost = FALSE` ⇒ no boost.** The ranker must
  default to today's behaviour for any supplier not TRUE here.
- **Control + every non-enrolled supplier is guaranteed absent-or-FALSE.** The
  retention side asserts this on every publish (holdout enforcement); the ranker
  needs no knowledge of arms beyond honouring the boolean.
- `boost_weight` is the **only** tuning input the ranker takes from us. Bounds in §5.
- The view reflects the **master kill-switch** (§6): when disabled, every row is
  `retention_boost = FALSE`.

> DDL is in §9 so the Elastic team can see precisely how the boolean is derived
> (treatment arm + boost directive + status active + channel enabled).

---

## 4. Sync mechanism (BigQuery → Elastic index)

**Proposed (Elastic team confirms):** the supplier indexer mirrors the view into
the Elastic supplier document on its existing reindex cadence (target **≤ 24h**
freshness; Stage-1 does not need real-time). Two document fields:

```jsonc
// supplier document (additive — does not change existing fields)
{
  "profile_id": "14479",
  "retention_boost": true,        // from vw_elastic_retention_boost.retention_boost
  "retention_boost_weight": 1.0   // from boost_weight; 1.0 / absent ⇒ no effect
}
```

- Defaulting: if the indexer can't read the view, fields default to
  `retention_boost=false` / weight `1.0` → **fail safe to no-boost**.
- We can switch to a push model later; for Stage-1 a daily pull is sufficient.
- **Open Q (spike):** does the indexer prefer to read this BQ view, or should we
  publish to GCS / a different store the indexer already consumes?

---

## 5. Scoring (non-premium layer only)

Apply the boost as a bounded `function_score` multiplier **in the organic/non-premium
query path only**. Premium query path is untouched.

```jsonc
// organic / non-premium ranking query — illustrative
{
  "function_score": {
    "query": { /* existing organic relevance query */ },
    "functions": [
      {
        "filter": { "term": { "retention_boost": true } },
        "weight": 1.15          // ← maps from retention_boost_weight; see bounds
      }
    ],
    "score_mode": "multiply",
    "boost_mode": "multiply",
    "max_boost": 1.30           // hard ceiling — never overwhelm relevance
  }
}
```

- **Magnitude:** `boost_weight = 1.0` is the neutral/default unit; the live applied
  multiplier should sit in a **conservative band ≈ 1.05–1.30**. The exact mapping
  from `boost_weight` → applied multiplier and the ceiling are the Elastic team's
  call (they know the score distribution) — we just need **one tunable knob and a
  documented ceiling**, with relevance still dominating.
- **Premium isolation:** the function must be absent from any premium/paid placement
  query. If premium and organic share one query, the boost filter must additionally
  exclude premium docs. **Open Q (spike): how are premium spots implemented today —
  pinning, a boost, or a separate query?** That answer determines the safe injection
  point.
- **Couples first:** boost adjusts ordering within relevance; it must not surface
  irrelevant suppliers (no boosting outside the couple's category/region intent).

---

## 6. Kill-switch (two independent levels)

1. **Data-surface master switch (retention side):** a single control flag flips
   every `retention_boost` to `FALSE` within one refresh cycle. Use for "turn the
   experiment off" / guardrail breach.
2. **Query-level feature flag (Elastic side):** an instant, deploy-free toggle that
   stops applying the `function_score` regardless of the field — for sub-minute
   incident response. **This is a required deliverable** (level 1 is bounded by
   refresh latency; level 2 is immediate).

Either level off ⇒ ranking reverts exactly to today's behaviour.

---

## 7. Guardrail measurement (couple-experience safety)

The boost ships only if it doesn't degrade the couple experience. To attribute, the
**ranker must log, per impression, whether a result was retention-boosted** (a
boolean on the search/impression event, plus `experiment_id`). With that we monitor:

| metric | definition | guardrail |
|---|---|---|
| Boosted-placement CTR | clicks / impressions on boosted results | not materially below comparable non-boosted positions |
| View→lead conversion | leads / profile views for boosted suppliers | not degraded vs control |
| Head-supplier exposure | views drawn from non-churning top suppliers | capped; no material harm |
| Premium integrity | premium impressions / CTR / revenue | **zero** change attributable to the boost |

**Auto-disable rule (pre-registered):** if boosted-placement CTR or view→lead
conversion drops beyond an agreed threshold over a rolling window, trigger the
kill-switch and alert. Threshold set jointly before launch.

---

## 8. Open questions the spike (YOO-228) must close

These need the Elastic team's knowledge and gate the build:

1. **Ranking today:** how is organic supplier ranking scored (fields, function_score
   already in use, sort)?
2. **Premium implementation:** pinning vs boost vs separate query — the single most
   important answer (determines the safe, premium-isolated injection point).
3. **Flag ingestion:** read the BQ view directly, or publish elsewhere the indexer
   already consumes? Achievable freshness?
4. **Magnitude:** given the score distribution, what `boost_weight`→multiplier
   mapping + ceiling yields ≈ +12 views/month without distorting relevance?
5. **Impression logging:** can we add the `retention_boosted` boolean +
   `experiment_id` to search/impression events for guardrail attribution?
6. **Kill-switch:** confirm the query-level instant toggle is feasible.
7. **Effort estimate** for the above → feeds the Phase-1 plan.

**Definition of done (mirrors YOO-228):** documented mechanism (field + scoring +
magnitude + holdout-aware + kill-switch) + guardrail metrics + effort estimate.

---

## 9. Reference: published-view DDL (retention side)

How the retention platform derives the contract view from its internal tables. The
boolean is TRUE **only** when a supplier is treatment-arm AND has an active boost
directive AND the channel is enabled — so the holdout and premium guarantees are
structural, not conventions.

```sql
CREATE OR REPLACE VIEW `tpw-ga4-bigquery.retention.vw_elastic_retention_boost` AS
SELECT
  d.profile_id,
  -- TRUE only for an active, treatment-arm boost on an enabled channel:
  (c.arm = 'treatment'
     AND d.type = 'boost'
     AND d.status IN ('delivered', 'dry_run')   -- i.e. not 'gated'
     AND JSON_VALUE(d.params, '$.layer') = 'free'
  ) AS retention_boost,
  CAST(JSON_VALUE(d.params, '$.weight') AS FLOAT64) AS boost_weight,  -- default 1.0 if null
  JSON_VALUE(d.params, '$.layer')  AS layer,
  d.experiment_id,
  d.created_at  AS valid_from,
  d.delivered_at AS valid_to,
  d.created_at  AS updated_at
FROM `tpw-ga4-bigquery.retention.retention_directives` d
JOIN `tpw-ga4-bigquery.retention.cohort_assignment` c
  ON d.profile_id = c.profile_id AND d.experiment_id = c.experiment_id
WHERE d.type = 'boost';
```

> Today every boost directive is `status = 'gated'` (Elastic channel disabled until
> this spike closes), so the view currently returns **0 active boosts** — the correct
> pre-launch state. Flipping `directives.elastic_enabled = true` (config) after the
> spike lands makes treatment rows go TRUE. The retention side will materialize this
> view as part of wiring the dispatch adapter.

---

## 10. Summary of guarantees

**Retention platform commits:**
- One stable view; control + non-enrolled suppliers **never** `retention_boost=TRUE`.
- `layer` always `"free"`; a single tuning knob; a master kill-switch.

**Elastic team commits (post-spike):**
- Read the flag, apply a **bounded** `function_score` in the **non-premium layer only**.
- Premium inventory provably unaffected.
- A query-level instant kill-switch.
- Per-impression `retention_boosted` logging for guardrail attribution.
