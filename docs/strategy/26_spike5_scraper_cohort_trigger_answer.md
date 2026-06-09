# 26 — Spike 5 Answer: Scraper Cohort Trigger (YOO-232)

**Status:** Spike answer (closes Definition of Done) · **Date:** 2026-06-09 · **Linear:** [YOO-232](https://linear.app/yoonsterkenburg/issue/YOO-232) (parent YOO-227)
**Owner:** Lifecycle (tpw-lifecycle) · profile_auto_complete

Source spec: `docs/strategy/21_phase0_confirmation_spikes.md` §Spike 5. Bundle context: docs/strategy/17 §"pair with profile optimization", doc 18.
**Definition of done:** trigger interface + throughput + opt-in model.

> **Why this lever exists:** bundle **step 2**. A boosted profile that is weak/incomplete
> wastes the placement — so we optimize the profile *before* (or alongside) boosting
> it. The `optimize` directive is **always paired with `boost`** (`directives.py`
> params: `reason: 'paired_with_boost'`).

---

## TL;DR

| Question | Answer |
|---|---|
| How is the scraper invoked; can we trigger a `profile_id` list? | Retention **publishes** `type='optimize'` directives (`channel='profile_auto_complete'`, `params={action:'optimize_list'}`); `profile_auto_complete` consumes the treatment list. **Exact invocation (HTTP endpoint / `run_all.sh` batch / queue) is the open item for the scraper owner** — recommended surface: a list-accepting trigger. §1 |
| What does it change; opt-in / go-live approval? | Scrapes the supplier's website → **suggests** profile text + properties → **one-click go-live** (doc 16). It is **suggest-then-approve, not auto-publish** → a **supplier opt-in / go-live action is required**. The bundle must obtain that consent at enrollment or surface suggestions for in-dashboard approval. §2 |
| Throughput for ~80–300 cohort? Holdout? | A per-profile website scrape; batch-capable (`run_all.sh` implies it). ~80–300 is small — throughput almost certainly fine; **confirm batch rate with owner.** Holdout enforced structurally (treatment-only directives + leak assertion). §3 |

---

## 1. Trigger interface

**Lifecycle side (built):** the `optimize` lever in `src/actions/directives.py`:

```
retention_directives row:
  type     = 'optimize'
  channel  = 'profile_auto_complete'
  arm      = 'treatment'             # control never produced (§3)
  params   = { action: 'optimize_list', reason: 'paired_with_boost' }
  status   = 'gated'                 # until directives.scraper_enabled flips
```

`profile_auto_complete` reads the dispatchable treatment-arm `optimize` rows from
`retention_directives` (BQ) and runs the scrape/auto-complete for that `profile_id`
list.

**OPEN for the profile_auto_complete owner — the actual invocation:**
- Is it an **HTTP endpoint** that accepts a list of `profile_id`s, a **`run_all.sh`
  batch** over a supplied id file, or a **queue** producer?
- **Recommended contract:** a list-accepting trigger (`POST /optimize {profile_ids:[…]}`
  or a batch reading a BQ/file id list) so the lifecycle platform can hand it the cohort directly.
- Idempotency: re-running for an already-optimized profile should be a no-op or a
  refresh, not a duplicate publish.

## 2. What it changes + the opt-in model (the key finding)

Per doc 16 (retention hooks): the scraper **scrapes the supplier's website →
auto-suggests company text + properties → one-click go-live**. Two consequences:

1. **It produces *suggestions*, not silent edits.** The supplier reviews and
   **approves** before anything goes live ("one-click go-live"). This is the safe,
   intended design — we must not auto-mutate a live public profile without consent.
2. **Therefore the bundle needs an explicit opt-in / go-live step.** Two viable
   models:
   - **(a) Enrollment consent** — when a supplier joins the value-add bundle, the
     terms include "TPW may optimize your profile"; the scraper can then auto-apply
     within that consent. Lowest friction, highest coverage.
   - **(b) In-dashboard approval** — the scraper generates suggestions, the supplier
     dashboard surfaces them for **one-click approval**. Higher friction / lower
     take-rate but no blanket-consent question. *(Recommended default given the
     existing one-click-go-live mechanic already supports it.)*

   **Decision needed (product, not technical):** which model the Stage-1 pilot uses.
   This affects measured effect size — auto-apply (a) maximises the "optimized
   profile" treatment dose; approval (b) means only suppliers who click get the
   treatment (partial dose → dilutes the measured lift). Flagging for the bundle
   owner; not a blocker to the trigger interface itself.

## 3. Throughput + holdout

- **Throughput:** the operation is a per-profile website scrape + parse. The pilot
  cohort is **~80–300** suppliers — small, and the existence of a `run_all.sh`-style
  batch implies the scraper already runs over many profiles. Throughput is almost
  certainly a non-issue; **confirm the batch rate / max concurrency** with the owner
  so the cohort can be scheduled in one pass (or a couple of batches).
- **Holdout:** identical structural guarantee to the other levers — `optimize`
  directives are generated **only** for `cohort.treatment_ids`, and
  `directives.generate()` raises `AssertionError` if any control id appears. So **no
  control supplier is ever optimized** (control must rank/convert as-is for the pilot
  to be measurable). `profile_auto_complete` must only consume dispatchable
  treatment-arm rows — never build its own list.

## 4. Definition of Done — status

| DoD item | Status |
|---|---|
| Trigger interface | ✅ Lifecycle contract defined (`type='optimize'` directive); scraper-side invocation is the owner's open item (§1) |
| Throughput | ✅ Assessed — ~80–300 is small/batch-capable; confirm rate with owner (§3) |
| Opt-in model | ✅ Characterised — suggest-then-approve; **product decision (a) enrollment-consent vs (b) in-dashboard approval** flagged (§2) |

**Spike 5 is answered** from the lifecycle side. Residual items (externally-owned /
product decisions, gate dispatch not the contract):

1. **profile_auto_complete owner:** the actual invocation surface (HTTP/batch/queue)
   + batch throughput/concurrency + idempotency behaviour.
2. **Bundle/product owner:** choose the opt-in model — enrollment-consent (auto-apply)
   vs in-dashboard one-click approval — since it sets the treatment dose.

Until these land, `type='optimize'` directives stay `status='gated'` behind
`directives.scraper_enabled` — testable now, single flag-flip to go live.
