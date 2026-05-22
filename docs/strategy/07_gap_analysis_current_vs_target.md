# Gap Analysis: What TPW Has vs. What's Missing

## ✅ Already Implemented

| Component | Status | Notes |
|-----------|--------|-------|
| Supplier dashboard (list views, profile views, clicks) | ✅ Live | Good foundation |
| Annual billing with discount | ✅ Live | Strong retention anchor |
| Monthly billing with premium | ✅ Live | Flexibility option |

## 🟡 Partial / Can Leverage

| Component | Current State | Gap | Opportunity |
|-----------|--------------|-----|-------------|
| Dashboard data | Views + clicks | No **projected value** or **benchmarking** | Add "Estimated booking value" + "Top 10% in your category gets X views" |
| Dashboard engagement | Suppliers can log in | Most probably don't check regularly | **Push** the data via email/SMS instead of hoping they pull |
| Lead attribution | Tracks clicks | No **instant notification** to supplier | Real-time alert = perceived value spikes immediately |
| Profile completion | Unknown | No **onboarding rescue flow** if incomplete | Automated nudge sequence |

## 🔴 Missing (High Impact)

| Component | Why It Matters | Effort |
|-----------|---------------|--------|
| **Instant lead notifications** | Supplier feels the platform working in real-time | Low |
| **Projected booking value** | Turns abstract clicks into €€€ | Low-Medium |
| **Monthly results email** | Proactive value proof, not reactive | Low |
| **Category benchmarking** | "You're at 120 views, top suppliers get 400" | Low |
| **Health scoring + early warning** | Predict churn before cancellation | Medium |
| **Cancellation save flow** | Pause option, exit survey, instant offer | Low-Medium |
| **Tiered packages** | Let suppliers self-select into value tiers | Medium |
| **Win-back sequences** | Reactivate churned accounts cheaply | Low |

---

## Recommended Priority (Updated)

Given your existing foundation, here's the revised implementation order:

### Phase 1: Quick Wins (Weeks 1-4) — Low Effort, High Impact
1. **Instant lead notifications** — spec ready in [08_instant_notification_spec.md](08_instant_notification_spec.md)
2. **Monthly results email** — templates ready in [09_email_templates.md](09_email_templates.md)
3. **Projected value formula** — calculation ready in [10_projected_value_model.md](10_projected_value_model.md)
4. **Dashboard additions** — benchmarking + value estimate

### Phase 2: Automation Layer (Weeks 5-12)
5. Health scoring + churn early warning
6. Cancellation save flow
7. Onboarding rescue sequence

### Phase 3: Strategic (Months 4-6)
8. Tiered packages
9. Win-back sequences
10. Sales team restructuring
