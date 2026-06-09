# TPW B2B Retention Strategy — Document Index

## What This Is
A comprehensive retention strategy for The Perfect Wedding (theperfectwedding.nl) to reduce supplier churn from 25% to <12% while cutting retention-related sales headcount by 40-50%.

## Documents

> **Reading order:** docs **17–28 (June)** are the current, evidence-led strategy and
> execution. Docs **01–16 (May 22)** are the pre-evidence exploration — several are
> superseded (each carries a banner pointing to its replacement) but retained for
> history and reusable design detail (email copy, flow designs, market research).

| # | File | What It Covers |
|---|------|----------------|
| 01 | [01_executive_summary.md](01_executive_summary.md) | The big picture: 4 strategic pillars, expected impact, org changes |
| 02 | [02_information_needed.md](02_information_needed.md) | Critical data gaps to fill before building (surveys, unit economics, segmentation) |
| 03 | [03_automated_flows.md](03_automated_flows.md) | 8 detailed automated email/SMS/phone flows with triggers and scripts |
| 04 | [04_best_practices_research.md](04_best_practices_research.md) | Market benchmarks, case studies, research findings |
| 05 | [05_implementation_roadmap.md](05_implementation_roadmap.md) | 18-month phased rollout, investment estimate, risk register |
| 06 | [06_sales_team_transition_playbook.md](06_sales_team_transition_playbook.md) | How to restructure the sales team, call scripts, change management |
| 07 | [07_gap_analysis_current_vs_target.md](07_gap_analysis_current_vs_target.md) | What TPW already has vs. what's missing |
| 08 | [08_instant_notification_spec.md](08_instant_notification_spec.md) | Product spec for real-time lead alerts (email + SMS) |
| 09 | [09_email_templates.md](09_email_templates.md) | 7 ready-to-use Dutch email templates |
| 10 | [10_projected_value_model.md](10_projected_value_model.md) | Formula + category data for estimated booking value |
| 11 | [11_this_week_checklist.md](11_this_week_checklist.md) | Day-by-day actions to start immediately |
| 12 | [12_churn_prediction_audit.md](12_churn_prediction_audit.md) | Audit of existing ML system + integration plan |
| 13 | [13_technical_integration_spec.md](13_technical_integration_spec.md) | Concrete code/SQL to connect predictions to actions |
| 14 | [14_todo_list.md](14_todo_list.md) | High-level todo list for implementing the retention strategy |
| 15 | [15_actionable_retention_workflow.md](15_actionable_retention_workflow.md) | Actionable retention workflow playbook with lifecycle and signal-based triggers |
| 16 | [16_retention_hooks_brainstorm.md](16_retention_hooks_brainstorm.md) | Brainstorm: non-monetary retention hooks — primary focus: Ad Boost Pool for solo categories |
| 17 | [17_refined_retention_strategy.md](17_refined_retention_strategy.md) | **Evidence-led refined strategy** — supersedes assumptions in 01–16; churn driven by exposure/engagement/onboarding, not leads or price |
| 18 | [18_value_add_bundle_and_pilot.md](18_value_add_bundle_and_pilot.md) | Value-add bundle (exposure redistribution + dashboard proof) + two-stage holdout pilot design |
| 19 | [19_system_architecture.md](19_system_architecture.md) | System architecture — retention decisioning engine integrating Elastic, Bird.com (`marketing_flow`), GA4, supplier dashboard; holdout enforcement; Stage-1 build order *(customer_journey = B2C venue flow, out of scope)* |
| 20 | [20_phased_implementation_plan.md](20_phased_implementation_plan.md) | Phased execution roadmap (Phase 0 confirmations → Stage-1 pilot → model/dashboard → Stage-2 readout & scale) with decision gates G0–G3 |
| 21 | [21_phase0_confirmation_spikes.md](21_phase0_confirmation_spikes.md) | Seven ready-to-create confirmation spikes (Elastic boost, exposure rollup, model features, serving/Bird, newsletter, scraper, invoices) to clear gate G0 |
| 22 | [22_elastic_boost_interface_contract.md](22_elastic_boost_interface_contract.md) | Interface contract for YOO-228 — the `retention_boost` published view, premium-isolated `function_score`, holdout/kill-switch guarantees, guardrail metrics (hand to TPW Elastic team) |
| 23 | [23_spike2_exposure_rollup_answer.md](23_spike2_exposure_rollup_answer.md) | **G0 spike answer (YOO-229)** — exposure rollup + dashboard feed: reuse `monthly_profile_stats` |
| 24 | [24_spike3_churn_exposure_features_answer.md](24_spike3_churn_exposure_features_answer.md) | **G0 spike answer (YOO-230)** — exposure features for the churn model: fallback overlay, not retrain |
| 25 | [25_spike4_bird_email_newsletter_answer.md](25_spike4_bird_email_newsletter_answer.md) | **G0 spike answer (YOO-231)** — supplier email + couple-newsletter via Bird; UTM attribution |
| 26 | [26_spike5_scraper_cohort_trigger_answer.md](26_spike5_scraper_cohort_trigger_answer.md) | **G0 spike answer (YOO-232)** — scraper cohort trigger + opt-in model |
| 27 | [27_spike6_invoice_profile_join_answer.md](27_spike6_invoice_profile_join_answer.md) | **G0 spike answer (YOO-233)** — Moneybird invoice → `profile_id` join (98.6% coverage) |
| 28 | [28_retention_flow_and_levers.md](28_retention_flow_and_levers.md) | **Full retention flow + lever catalog** — segmentation into populations; 6 built levers (incl. onboarding + winback) + 4 proposed |

## The Core Insight

TPW's churn problem is not primarily a "customer service" problem — it's a **value perception** problem. Suppliers pay €500/year and cannot see what they get in return. When budgets tighten, the invisible line item gets cut.

The solution is not more account manager visits. It's:
1. **Prove value** (dashboard, monthly reports, lead notifications)
2. **Automate scale** (triggered flows replace manual check-ins)
3. **Segment ruthlessly** (field sales only for accounts where it makes economic sense)
4. **Intervene early** (health scores predict churn before the cancellation click)

## Quick Start (This Week)

1. **Deploy exit survey** on cancellation page — learn why people churn TODAY
2. **Interview 10 churned + 10 happy suppliers** — qualitative beats guessing
3. **Calculate true CAC and cost-to-retain** per tier — know your numbers
4. **Send a manual "value recap"** to your top 50 suppliers — prototype the concept

## Questions?

This strategy is a starting point. The real work is in the data collection and iteration. Start with Phase 0 (information gathering) before building anything.
