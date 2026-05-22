# Churn Prediction System Audit & Integration Plan

## What You Have (The Good)

Your churn prediction system is **substantially more sophisticated** than most companies at this stage:

| Component | Status | Assessment |
|-----------|--------|------------|
| Cascading ML model (baseline + trends) | ✅ Live | Solid architecture |
| BigQuery integration | ✅ Live | Scalable data pipeline |
| Daily automated predictions (7 AM) | ✅ Live | Good operational rhythm |
| Cloud Run dashboard | ✅ Live | Accessible to sales team |
| Slack notifications | ✅ Live | Alerts delivered |
| Phase 2 analysis (silent churners) | ✅ Done | Smart decision to stop retraining |

**The Phase 2 decision was correct.** You measured GA4 discrimination (0.269), realized it wasn't enough to justify retraining, and stuck with signal scoring. That saved 2-3 weeks of work.

---

## The Problem: Validation vs. Reality

Your system has a **performance gap** that's common but dangerous:

| Metric | Validation Claim | Production Reality (Nov 19) | Gap |
|--------|-----------------|---------------------------|-----|
| Precision | 78.8% | **50.0%** | -28.8pp |
| Recall | 82.4% | **40.4%** | -42.0pp |
| F1 | 0.805 | **0.447** | -0.358 |

**What this means in practice:**
- You flag 114 customers as at-risk
- Of those, ~57 will actually churn (50% precision)
- But you miss ~34 churners (40.4% recall = 59.6% missed)
- **Your sales team is working with a coin-flip prediction**

### Why the Gap Exists

1. **Overfitting on historical patterns** — The model learned "customers with churn flags churn" but the business has changed
2. **Small validation set** — 196 known outcomes is not enough for robust measurement
3. **Concept drift** — Post-COVID wedding market, pricing changes, competitor moves = the world changed
4. **Flag rate too high** — 29% of customers flagged means the threshold is too low

---

## The Bigger Problem: Predictions Without Action

Your dashboard answers: **"Who is at risk?"**

It does NOT answer:
- **"Why are they at risk?"**
- **"What should we do about it?"**
- **"Did the intervention work?"**

**Current workflow:**
```
7 AM: Dashboard updates
  → Sales manager sees 114 red flags
  → Calls 10 random ones
  → No tracking of what was said
  → No tracking of outcome
  → Next day: 114 new flags
```

**This is a hamster wheel.** The system generates predictions but doesn't close the loop.

---

## Recommended Fixes (Priority Order)

### 1. Fix the Threshold (This Week)

**Current:** 0.55 threshold → 114 flagged (29%)
**Problem:** Sales team can't call 29% of customers every day

**Fix:** Raise threshold to reduce false positives

| Threshold | Flagged | Expected Precision | Actionable? |
|-----------|---------|-------------------|-------------|
| 0.55 | 114 (29%) | 50% | ❌ No |
| 0.65 | ~70 (18%) | ~60% | ⚠️ Maybe |
| 0.75 | ~35 (9%) | ~70% | ✅ Yes |
| 0.85 | ~15 (4%) | ~80% | ✅ Yes |

**Recommendation:** Start with **0.75 threshold** for P1 (urgent) and **0.65** for P2 (monitor). This gives the sales team ~35-50 real at-risk accounts to focus on, not 114.

---

### 2. Add "Why" to the Dashboard (2 Weeks)

The current dashboard shows:
- Customer name
- Churn probability
- Plan value
- Category

**Missing:** The actual behavioral signals driving the prediction

**Add these columns to the dashboard:**

| New Column | Source | Why It Matters |
|------------|--------|----------------|
| Days since last login | GA4 | Inactivity = disengagement |
| Days since last lead | Lead system | No leads = value anxiety |
| Profile completion % | Your DB | Incomplete = low conversion |
| Last 30d views vs avg | GA4 | Declining = early warning |
| Response time to leads | Your DB | Slow = bad experience |
| Support tickets (last 90d) | Your DB | Complaints = churn signal |

**Sales team needs to see:**
> "This customer is at 78% risk because: (1) hasn't logged in 45 days, (2) profile is 40% complete, (3) zero leads in last 60 days"

Not just:
> "This customer is at 78% risk"

---

### 3. Connect Predictions to Actions (2-4 Weeks)

**Current:** Dashboard is a standalone tool
**Needed:** Dashboard feeds the retention flows

**Integration plan:**

```
Churn Prediction System
    ↓ (daily export)
BigQuery: at_risk_customers table
    ↓ (triggers)
Automated Retention Flows
    ├── P1 (>75% risk): Inside sales call within 24h
    ├── P2 (65-75%): Automated email + monitor
    ├── P3 (55-65%): Monthly results email (nudge)
    └── P4 (<55%): Standard nurture
```

**Technical change:** Add a `recommended_action` column to the predictions table:

```sql
ALTER TABLE daily_churn_predictions_segmented
ADD COLUMN recommended_action STRING,
ADD COLUMN risk_factors ARRAY<STRING>,
ADD COLUMN last_intervention_date DATE,
ADD COLUMN intervention_outcome STRING;
```

---

### 4. Track Intervention Outcomes (4 Weeks)

**Current:** No feedback loop
**Needed:** Did the sales call save the account?

**Add to BigQuery:**

| Table | Columns | Purpose |
|-------|---------|---------|
| `intervention_log` | profile_id, date, type, notes, am_id | What was done |
| `intervention_outcomes` | profile_id, intervention_id, saved, churned, revenue_preserved | Did it work |

**This closes the loop:**
```
1. Predict churn → 2. Intervene → 3. Track outcome → 4. Improve model
```

Without step 3, you're flying blind.

---

### 5. Simplify the System (Ongoing)

**Current state:** 200+ scripts, many experiments, multiple model versions

**The honest assessment:** This level of complexity is slowing you down. The marginal improvement from the 50th A/B test is near zero.

**Recommended simplification:**

| Keep | Archive/Delete |
|------|---------------|
| `daily_prediction_pipeline.py` | All `ab_test_*.py` scripts (50+) |
| `churn_prediction_dashboard.py` | All `validate_*.py` scripts (30+) |
| `train_baseline_model.py` | `archive/experiments/` folder |
| `predict_churn_cascading.py` | Duplicate model versions |
| `send_churn_alerts.py` | Obsolete cloud run tests |
| BigQuery tables | Old CSV exports |

**Move to a single pipeline:**
```
daily_prediction_pipeline.py
    → trains model (if needed)
    → generates predictions
    → uploads to BigQuery
    → sends Slack alert
    → triggers retention flows
```

One script, one cron job, done.

---

## Integration with Retention Strategy

Your churn prediction system and retention strategy are currently **two separate worlds**. Here's how to merge them:

### The Predict → Act → Measure Loop

```
┌─────────────────────────────────────────────────────────────┐
│  CHURN PREDICTION SYSTEM                                    │
│  • Daily predictions (BigQuery)                             │
│  • 393 customers scored                                     │
│  • ~35 P1 accounts flagged                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  RETENTION AUTOMATION SYSTEM                                │
│  • P1 (>75%): Inside sales gets task in CRM                 │
│  • P2 (65-75%): "No lead in 60 days" email sent             │
│  • P3 (55-65%): Monthly results email with benchmark        │
│  • All: Profile completion nudges                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  SUPPLIER VALUE DASHBOARD                                   │
│  • Instant lead notifications (new!)                        │
│  • Monthly "Your Results" email (new!)                      │
│  • Projected booking value (new!)                           │
│  • Profile optimization tips                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTCOME TRACKING                                           │
│  • Saved: 15 accounts (43% save rate)                       │
│  • Churned: 20 accounts                                     │
│  • Revenue preserved: €12,500                               │
│  • Feedback: Update model + refine thresholds               │
└─────────────────────────────────────────────────────────────┘
```

---

## Immediate Action Plan

### Week 1: Quick Fixes
- [ ] **Raise threshold to 0.75** → reduces flag count from 114 to ~35
- [ ] **Add "days since last login"** to dashboard columns
- [ ] **Add "days since last lead"** to dashboard columns
- [ ] **Test the instant notification** concept with 5 suppliers

### Week 2-3: Dashboard Enhancements
- [ ] **Add risk factors column** to dashboard (why is this customer at risk?)
- [ ] **Add "last intervention" column** (what did we already do?)
- [ ] **Add CSV export** filtered by P1 only (sales team's daily list)

### Week 4-6: Automation Integration
- [ ] **Build P1 → CRM task creation** (automatic ticket for inside sales)
- [ ] **Build P2 → automated email flow** (re-engagement sequence)
- [ ] **Build outcome tracking table** in BigQuery

### Month 3: Value Dashboard Integration
- [ ] **Connect predicted churn risk** to supplier-facing dashboard
- [ ] **Show at-risk suppliers**: "Your profile engagement is declining — here's how to fix it"
- [ ] **A/B test:** Does showing risk score + tips reduce churn vs. not showing?

---

## Success Metrics for the Integrated System

| Metric | Current | Target (3mo) |
|--------|---------|--------------|
| Daily flagged accounts | 114 | 35-50 |
| Precision (production) | 50% | 65%+ |
| Sales team action rate | Unknown | 80%+ of P1 flagged |
| Intervention save rate | Unknown | 30%+ |
| Days from flag to action | Unknown | <2 days |
| Supplier dashboard engagement | Unknown | 60%+ monthly |

---

## Bottom Line

Your churn prediction system is **technically impressive** but **operationally disconnected**. The model predicts. The sales team guesses. The supplier never knows.

**The fix is not another model iteration.** It's connecting the prediction to:
1. **Actionable insights** (why is this supplier at risk?)
2. **Automated flows** (email, SMS, CRM tasks)
3. **Value proof** (dashboard + notifications)
4. **Outcome tracking** (did we save them?)

You already built the engine. Now build the car around it.
