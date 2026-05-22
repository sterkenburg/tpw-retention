# Critical Information Needed Before Implementation

To design the right retention strategy, we need to fill these data gaps. **Do not build flows blindly.**

---

## 1. Churn Root Cause Data

### Exit Survey (Mandatory)
Implement a **mandatory 3-question exit survey** at cancellation:
1. *"What was the MAIN reason you decided to leave?"*
   - Too expensive / didn't see ROI
   - Not getting enough leads/sales
   - Switching to competitor (which one?)
   - Business closed / paused
   - Didn't use it enough
   - Other
2. *"How many bookings do you estimate you got from TPW in the past 12 months?"*
   - 0 / 1-2 / 3-5 / 6-10 / 10+
3. *"What would have made you stay?"* (open text)

### Win/Loss Analysis
- Interview 20 recently churned customers
- Interview 20 who renewed (what worked?)
- Map churn reasons by **supplier category** (DJ vs venue vs florist behave differently)

---

## 2. Customer Segmentation Data

### Financial Segmentation
| Data Point | Why It Matters |
|------------|----------------|
| Revenue per supplier (last 12mo) | Identify Premium tier |
| Margin per supplier | Some categories cost more to serve |
| Lifetime value (LTV) by cohort | See which vintage churns most |
| CAC by acquisition channel | Some channels bring worse customers |

### Behavioral Segmentation
| Data Point | Why It Matters |
|------------|----------------|
| Login frequency (last 30/90 days) | Leading churn indicator |
| Profile completion % | Correlates with lead generation |
| Photo count, description length | Quality signals |
| Response time to inquiries | Affects conversion, can be coached |
| Reviews/rating count | Social proof loop |
| Feature usage (analytics, promotions) | Stickiness indicator |

### Firmographic Segmentation
- Category (venue, dress, cake, flowers, DJ, etc.)
- Geography (region, urban vs rural)
- Business age (new vs established)
- Sole proprietor vs team/company
- Also listed on competitors? (ask in survey)

---

## 3. Unit Economics

### Must-Know Numbers
| Metric | How to Calculate | Target Benchmark |
|--------|------------------|------------------|
| **CAC** | Sales + marketing cost / new customers | <€150 for self-serve, <€400 for inside sales |
| **LTV** | ARPU × gross margin × avg lifespan | Should be 3x+ CAC |
| **CAC Payback** | CAC / monthly gross profit | <12 months |
| **Cost to Retain** | AM + support cost / retained customers | Currently likely >€200, target <€50 |
| **Net Revenue Retention** | Start ARR + expansions - churn / start ARR | Target >100% |
| **Gross Revenue Retention** | Start ARR - churn / start ARR | Target >90% |

### The "Car Ride Test"
Calculate: *(Cost of AM visit + opportunity cost) / Annual contract value*
- Rotterdam → Groningen: ~€200 travel + 6 hours = €400+ cost
- For €500 ACV: **unit economics are impossible**
- For €3,000 ACV: **maybe worth it once/year**

**Rule:** Field sales only for accounts where visit cost <10% of ACV.

---

## 4. Competitive Intelligence

### Questions to Answer
- Which competitors are churned customers joining? (Trouwland? Trouwinfo? Google Ads?)
- What do competitors charge?
- What do competitors offer that TPW doesn't? (e.g., pay-per-lead, booking fees)
- What is the **total addressable market** of wedding suppliers in NL?
- Market share by category?

### Pricing Benchmarks to Collect
| Competitor | Price | Model | Key Differentiator |
|------------|-------|-------|-------------------|
| Trouwland | ? | Subscription / lead fee | |
| Trouwinfo | ? | Subscription | |
| Google Ads (DIY) | Pay-per-click | Self-serve | Full control, no curation |
| Thuisbezorgd/Wedding variants | ? | Commission | |

---

## 5. Product Usage & Lead Attribution

### The "Black Box" Problem
Currently suppliers don't know if TPW drives sales. We need:
- **Track every interaction**: profile view, photo click, "contact" button, phone number reveal
- **Lead notification**: Instant email/SMS to supplier: *"A couple viewed your profile and clicked contact"*
- **Revenue tracking**: Optional field where supplier logs "booking value from TPW lead"
- **Benchmarking**: *"Your profile was viewed 120 times this month. Top 10% suppliers in your category get 300+ views. Here's how to improve..."*

### Data Collection Priority
1. **Phase 1 (Weeks 1-4)**: Implement basic event tracking (views, clicks)
2. **Phase 2 (Weeks 5-8)**: Build supplier dashboard MVP
3. **Phase 3 (Weeks 9-12)**: Add revenue estimator + benchmarking
4. **Phase 4 (Ongoing)**: Predictive churn scoring

---

## 6. Sales Team Structure & Cost Breakdown

### Current State Audit
| Question | Action |
|----------|--------|
| How many account managers? | Count FTEs |
| How many are field vs inside? | Categorize |
| Average accounts per AM? | Calculate ratio |
| Average travel time per week? | Survey AMs |
| What % of time is retention vs new sales? | Time study |
| Commission structure? | Review plan |
| Which accounts generate >€2,000/yr? | Run report |

### Target State
| Tier | Account Count | Touch Model | AM Coverage |
|------|--------------|-------------|-------------|
| Starter (<€750) | ~60% | Automated only | 0 |
| Growth (€750-€2,500) | ~30% | Inside sales (phone/video) | 1 AM per 200 accounts |
| Premium (>€2,500) | ~10% | Field + CSM | 1 AM per 50 accounts |

---

## 7. Quick Wins While Researching

You don't need perfect data to start. These can run in parallel:

1. **Deploy exit survey immediately** — learn why people churn today
2. **Send a "value recap" email** to all active suppliers with their last 12mo stats (even if crude)
3. **Call 10 recently churned customers** — qualitative gold
4. **Audit the top 20% of suppliers by revenue** — understand your Premium tier
5. **Map competitor pricing** — mystery shop their sales teams
