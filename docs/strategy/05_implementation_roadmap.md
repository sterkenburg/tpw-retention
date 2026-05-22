# Implementation Roadmap

## Phase 0: Foundation (Weeks 1-4)
**Theme: Learn before building**

| Week | Action | Owner | Deliverable |
|------|--------|-------|-------------|
| 1 | Deploy exit survey on cancellation | Product/Marketing | Live survey collecting data |
| 1 | Interview 10 churned + 10 retained suppliers | CS Lead | Qualitative insights doc |
| 2 | Audit current supplier base: segment by revenue, category, geography | Data/Finance | Customer segmentation report |
| 2 | Calculate true CAC and cost-to-retain per tier | Finance | Unit economics model |
| 3 | Competitive pricing mystery shop | Marketing | Competitor matrix |
| 3 | Map current sales team activities (% time on retention vs new, travel costs) | Sales Ops | Sales efficiency audit |
| 4 | Define tier boundaries (Starter/Growth/Premium) | Leadership | Tier definition doc |
| 4 | Build business case for headcount restructure | Leadership | Board-ready proposal |

**Quick wins (parallel):**
- Send manual "value recap" email to top 100 suppliers
- A/B test annual pricing on new signups (+20% for monthly)
- Add 1 in-app message: "Complete your profile to get 3x more leads"

---

## Phase 1: Value Realization MVP (Weeks 5-12)
**Theme: Prove value or lose the customer**

| Week | Action | Owner |
|------|--------|-------|
| 5-6 | Implement event tracking: profile views, photo clicks, contact button, phone reveal | Engineering |
| 5-6 | Build "lead notification" system (email/SMS to supplier when couple contacts) | Engineering |
| 7-8 | Launch Supplier Dashboard MVP: views, clicks, inquiries, simple benchmark | Engineering |
| 7-8 | Create "Your Monthly Results" email template | Marketing |
| 9-10 | Build revenue estimator: "Based on your stats, potential booking value is €X" | Engineering + Data |
| 9-10 | Onboarding rescue flow: 5-email sequence for incomplete profiles | Marketing Ops |
| 11-12 | Soft launch dashboard to 50 suppliers, gather feedback, iterate | CS + Product |

**Success metrics:**
- Dashboard adoption: 60% of suppliers log in within 30 days of launch
- Monthly results email: >40% open rate
- Lead notification: suppliers report "this is useful" in survey

---

## Phase 2: Automation & Segmentation (Weeks 13-24)
**Theme: Replace field sales with scalable flows**

| Week | Action | Owner |
|------|--------|-------|
| 13-14 | Launch tiered packages: Basic/Plus/Premium with clear feature differences | Product + Marketing |
| 13-14 | Deploy health scoring model (login + engagement + leads) | Data/Engineering |
| 15-16 | Build automated churn early warning flows (Yellow/Orange/Red sequences) | Marketing Ops |
| 15-16 | Implement cancellation save flow: pause option + exit survey + instant offer | Product |
| 17-18 | Train inside sales team on phone/video retention calls | Sales Ops |
| 17-18 | Launch renewal prep sequence (60 days before expiry) | Marketing Ops |
| 19-20 | Build win-back sequence for churned accounts (30/90/180/365 days) | Marketing Ops |
| 21-22 | Launch self-service downgrade/upgrade in account settings | Engineering |
| 23-24 | Full rollout: all suppliers get dashboard + automated flows | All |

**Org changes:**
- Begin transitioning field AMs to inside sales or premium-only accounts
- Hire 1 Retention Marketing Manager
- Hire 1 Digital Customer Success Manager (low-touch)

**Success metrics:**
- Automated flow coverage: 100% of suppliers
- Human touch only for Premium + Red scores
- Field sales travel reduced by 50%

---

## Phase 3: Optimization & Expansion (Months 7-18)
**Theme: Fine-tune and grow**

| Month | Action | Owner |
|-------|--------|-------|
| 7-9 | A/B test email subject lines, offers, timing | Marketing |
| 7-9 | Launch category-specific seasonal campaigns | Marketing |
| 7-9 | Introduce upsell prompts in dashboard ("Get 3x views with Featured") | Product |
| 10-12 | Build predictive churn model (ML-based) | Data |
| 10-12 | Launch supplier referral program ("Refer a colleague, get 1 month free") | Marketing |
| 13-15 | Expand to new value-added services (insurance, payments, booking tools) | Product |
| 13-15 | Optimize pricing based on willingness-to-pay research | Leadership |
| 16-18 | Full organizational restructure complete | Leadership |

**Success metrics:**
- Churn <12% annual
- NRR >105%
- Expansion revenue >10% of ARR
- CAC payback <6 months

---

## Investment & ROI Estimate

### One-Time Costs
| Item | Estimate |
|------|----------|
| Dashboard development | €15,000-30,000 |
| CRM/marketing automation setup | €5,000-10,000 |
| Data infrastructure | €5,000-10,000 |
| Training & change management | €5,000 |
| **Total one-time** | **€30,000-55,000** |

### Recurring Costs (Monthly)
| Item | Estimate |
|------|----------|
| CRM + marketing automation | €700-1,200 |
| Analytics/dashboard tools | €1,000-2,000 |
| SMS/communication | €200-500 |
| New hires (2 digital CS/retention) | €8,000-12,000 |
| **Total monthly** | **€10,000-16,000** |

### Savings (Monthly)
| Item | Estimate |
|------|----------|
| Reduced field AM headcount (3-4 FTE) | €15,000-24,000 |
| Reduced travel costs | €2,000-4,000 |
| **Total savings** | **€17,000-28,000** |

### Net Impact
- **Monthly P&L improvement:** +€5,000-15,000 from headcount alone
- **Retention impact:** Reducing churn from 25% → 12% on €2M ARR = **€260,000 saved annually**
- **Payback period:** 3-6 months

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Suppliers resist dashboard (don't log in) | Medium | Medium | Embed data in emails; make it required for profile edits |
| Field AMs resist change | High | Medium | Retrain, offer premium account focus, communicate "quality over quantity" |
| Churn spike during transition | Medium | High | Grandfather existing customers; phase changes by cohort |
| Engineering delays | Medium | Medium | Start with email flows (no dev); dashboard can be MVP |
| "Too expensive" perception persists | Medium | High | Prove value first, then adjust pricing; offer downgrade path |

---

## Governance

**Weekly:** Retention task force standup (Product, Marketing, Sales, Engineering)
**Monthly:** Metrics review — churn, health scores, flow performance, sales efficiency
**Quarterly:** Board update on retention strategy progress

**Owner:** VP Revenue / COO (or equivalent)
**Sponsor:** CEO
