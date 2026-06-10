# 25 — Spike 4 Answer: Supplier Email + Couple-Newsletter via Bird (YOO-231)

**Status:** Spike answer (closes Definition of Done) · **Date:** 2026-06-09 · **Linear:** [YOO-231](https://linear.app/yoonsterkenburg/issue/YOO-231) (parent YOO-227)
**Owner:** Retention (tpw-retention) · marketing_flow (Bird)

Source spec: `docs/strategy/21_phase0_confirmation_spikes.md` §Spike 4. System map: `docs/strategy/19_system_architecture.md`.
**Definition of done:** email-directive contract + newsletter-injection mechanism + attribution approach.

> **Scope guard:** delivery goes through **`marketing_flow` (Bird.com)** — **NOT**
> `customer_journey` (the B2C venue flow, kept separate) and **NOT** the deprecated
> SendGrid prototype (`src/actions/emails.py`, D1–D3). The retention repo is the
> **brain**: it publishes directives; Bird/marketing_flow **delivers**.

---

## TL;DR

| Question | Answer |
|---|---|
| Supplier **email-directive** contract? | Published already: `retention_directives` rows, `type='email'`, `channel='bird_marketing_flow'` (`src/actions/directives.py` LEVERS). §1 — recipient, template, variables, compliance defined; **Bird-side template id + submission API is the open item for the marketing_flow owner**. |
| **Newsletter injection** mechanism? | `type='newsletter'` directive carries a **featured-suppliers list** for the `couple_newsletter_feature` campaign; marketing_flow injects a dynamic block at assembly time. §2 |
| **Attribution** (TPW-contributed views)? | **UTM scheme** on every TPW-originated link (`utm_source=tpw_retention`, `utm_medium`, `utm_campaign`, `experiment_id`, `arm`) → measured back via GA4 → `supplier_exposure` / `tpw_contributed_views`. §3 |
| **Holdout** respected? | **Structurally.** Directives are generated for the **treatment arm only** and `directives.generate()` raises if any control id leaks. §4 |

---

## 1. Supplier email-directive contract

**What retention publishes** (already implemented, `directives.LEVERS['email']`):

```
retention_directives row:
  profile_id      <supplier>
  experiment_id   'stage1_exposure'
  arm             'treatment'        # control never produced (§4)
  type            'email'
  channel         'bird_marketing_flow'
  params (JSON)   { template: 'monthly_results',
                    exposure_first: true,        # lead with exposure, not leads
                    include_masked_leads: true } # concrete proof; full PII in-dashboard only
  status          'gated' | 'dry_run' | 'delivered'   # gated until bird_enabled flips
  created_at / delivered_at
```

**Recipient resolution:** supplier email = `ga4_dataform_seed.companies_profiles.profile_email`,
joined on `profile_id` (memory: supplier-email-source). Note `config/settings.yaml`
`sources.supplier_email_*` is still blank — wire it to that table/column so the
recipient is resolvable (small config change; non-blocking for the contract).

**Template variables** (retention supplies, Bird template renders): supplier name,
period, exposure metrics (views, impressions, trend vs prior period, category
benchmark/percentile), masked-lead count + masked snippets, dashboard deep-link
(UTM-tagged, §3).

**Compliance / rate limits — OPEN for the marketing_flow owner:**
- Bird template id for `monthly_results` + the **submission API** (how retention
  hands Bird a per-supplier send: API call vs. a BQ table Bird polls vs. a campaign
  audience upload).
- Unsubscribe/suppression handling (Bird-managed list) and transactional-vs-marketing
  classification (a monthly results email is arguably transactional → different
  consent basis).
- Send-rate limits and the **dedup window** (retention already carries
  `email.dedup_days.monthly_results: 25` in settings — confirm Bird won't double-send).

## 2. Couple-newsletter injection mechanism

**What retention publishes** (`directives.LEVERS['newsletter']`):

```
type='newsletter', channel='bird_marketing_flow',
params = { campaign: 'couple_newsletter_feature' }
```

The set of `type='newsletter'` treatment rows **is** the featured-suppliers list for
a given send. Mechanism: marketing_flow reads the current featured list (BQ
`retention_directives` filtered to `type='newsletter'`, `arm='treatment'`,
dispatchable status) and **injects a dynamic "featured suppliers" block** into the
couple newsletter at assembly time.

**OPEN for the marketing_flow owner:**
- How couple newsletters are assembled/sent today (content catalog, Bird campaign
  structure) and whether a **dynamic block from a supplied list** is supported.
- **Cadence + audience size** (couples) — sets how many feature-slots/month exist,
  which bounds how many treatment suppliers can be featured per cycle.
- Slot count per send + rotation policy (so the additive-exposure lever is sized).

## 3. Attribution — TPW-contributed views

Every TPW-originated link (email CTAs, newsletter feature block) carries a **UTM
scheme** so resulting profile views are attributable:

```
utm_source   = tpw_retention
utm_medium   = email | newsletter
utm_campaign = monthly_results | couple_newsletter_feature
utm_content  = <profile_id>
+ experiment_id = stage1_exposure, arm = treatment   (as query params)
```

Resulting sessions land in GA4 → joined back by `profile_id` to populate
`tpw_contributed_views` on the `supplier_exposure_monthly` dashboard feed (Spike 2 /
doc 23 §3) and feed the measurement layer (WS-E). This is the **"TPW's contribution"**
number the supplier dashboard surfaces.

**OPEN:** confirm GA4 captures these UTM params on supplier-profile pageviews
(`bedrijven_pageview_events` already has `source`/`medium` — likely yes) and that
Bird preserves UTM params through any link-wrapping/click-tracking redirect.

## 4. Holdout enforcement — structural

- Directives are generated **only** for `cohort.treatment_ids(experiment_id)`;
  control suppliers are never iterated.
- `directives.generate()` does an explicit **leak assertion**: it queries the
  `control` arm from `cohort_assignment` and **raises `AssertionError`** if any
  control id appears in the directive set.
- Therefore **no control supplier can ever be emailed or featured** — the pilot stays
  measurable (no contamination), provable via `measurement.contamination_audit`.
- Bird side must honour this by **only consuming dispatchable treatment-arm rows**
  from `retention_directives` (never building its own audience).

## 5. Definition of Done — status

| DoD item | Status |
|---|---|
| Email-directive contract | ✅ Defined + implemented (§1); Bird template/API is the owner's open item |
| Newsletter-injection mechanism | ✅ Defined (§2); assembly support to confirm with owner |
| Attribution approach | ✅ UTM scheme → GA4 → `tpw_contributed_views` (§3) |

**Spike 4 is answered** from the retention side. The residual items are genuinely
**externally-owned** (the Bird/marketing_flow integration surface) and gate dispatch,
not the contract:

1. **marketing_flow owner:** Bird template id + per-supplier **email submission API**;
   newsletter **dynamic-block** support, cadence, audience size, slot count.
2. **Compliance:** unsubscribe/suppression + transactional-vs-marketing consent basis.
3. **Config wire-up:** set `sources.supplier_email_table/column` to
   `companies_profiles.profile_email` (recipient resolution).
4. **Attribution check:** confirm Bird preserves UTM through click-tracking; confirm
   GA4 captures them on profile pageviews.

Until these land, all `type in (email, newsletter)` directives stay
`status='gated'` behind `directives.bird_enabled` — the brain is fully testable now
and going live is a single flag-flip (`bird_enabled: true`, then `dry_run: false`).

---

### Side-note (not part of this spike): post-migration region bug — fixed

`src/actions/directives.py::build()` explicitly passed `location="US"` to the
`DELETE` job. After the 2026-06-05 US→EU consolidation the `retention` dataset is
**EU**, so that override would fail/no-op — **fixed in this pass** (removed the
override so it inherits the configured EU `LOCATION`, like every other `execute`).
One residual: the control-leak check (`cohort.client.query`, ~line 118) reads via
`pandas_gbq` without an explicit location; prefer `client.query_eu` there if it
mis-defaults (low risk; follow-up).
