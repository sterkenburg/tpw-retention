# TPW B2B Retention Strategy — High-Level Todo List

This document outlines the structured high-level todo list for implementing the TPW B2B Retention Strategy. The goals are to reduce annual supplier churn from 25% to <12% within 18 months, shift high-touch field sales to scalable digital/inside sales, and integrate the daily machine-learning churn prediction system.

---

## 📍 Phase 0: Research & Foundation (Immediate — Weeks 1-4)

### Customer & Churn Research
- [ ] **Deploy Exit Survey:** Implement a mandatory 3-question exit survey on the cancellation page to gather structured data on why suppliers are leaving (Reference: `02_information_needed.md`).
- [ ] **Conduct Qualitative Interviews:** Call 10 recently churned and 10 highly active/retained suppliers to capture qualitative value-perception gaps and success stories.

### Segmentation & Unit Economics Auditing
- [ ] **Establish Account Tiers:** Segment the current supplier base by annual contract value (Starter: `<€750/yr`, Growth: `€750–€2,500/yr`, Premium: `>€2,500/yr`).
- [ ] **Map Unit Economics:** Calculate true CAC, LTV, and Cost-to-Retain per tier. Apply the "Car Ride Test" to confirm which accounts economically justify field visits.

### Quick Wins (Parallel execution)
- [ ] **Prototype the "Value Recap" Email:** Manually export last month's stats (views, clicks, inquiries) for the top 50 suppliers and send them a manual value-proof email using the template in `09_email_templates.md`.
- [ ] **A/B Test Pricing Models:** Implement and test annual-first billing (+20% premium for monthly options) on new supplier signups.

---

## 📈 Phase 1: Value Realization & Core Product MVP (Weeks 5-12)

### ROI Dashboard Upgrades
- [ ] **Incorporate Booking Estimation:** Integrate the **Projected Booking Value Model** directly into the supplier dashboard header (`10_projected_value_model.md`) to turn clicks and views into estimated potential revenue.
- [ ] **Add Category Benchmarking:** Display where the supplier stands compared to the top 10% in their category.

### Instant Notifications Spec
- [ ] **Launch Real-Time Alerts:** Implement real-time email and SMS alerts (via Twilio/MessageBird) triggering instantly when a couple submits a contact form or reveals a phone number (`08_instant_notification_spec.md`).

### Automated Engagement Lifecycle
- [ ] **Onboarding Rescue:** Build an automated 5-email sequence to guide new suppliers with incomplete profiles (<80% completion after 14 days) to their first profile views and leads.
- [ ] **Automate "Your Results" Emails:** Set up the automated monthly results newsletter on the 1st of every month to push value directly to suppliers' inboxes.

---

## ⚙️ Phase 2: Churn Prediction & Automation Integration (Weeks 13-24)

### ML Churn Model Optimization
- [ ] **Fix Thresholds:** Raise the prediction classification threshold from `0.55` to `0.75` for P1 (urgent) and `0.65` for P2 (high risk) to reduce sales team fatigue and increase precision (`12_churn_prediction_audit.md`).
- [ ] **Expose Behavioral Signals ("Why"):** Add *days since last login*, *days since last lead*, and *risk factors* columns to the Streamlit dashboard so account managers know why a customer is flagged.
- [ ] **Clean Up Codebase:** Deprecate and archive obsolete experiment/validation scripts (50+ `ab_test_*.py` and 30+ `validate_*.py` scripts) and keep a unified daily prediction pipeline (`13_technical_integration_spec.md`).

### Connecting Predictions to Actionable Flows
- [ ] **CRM Task Automation:** Build `scripts/create_retention_tasks.py` to auto-generate high-priority CRM tasks for inside sales reps when a supplier flags as P1.
- [ ] **Automated Re-engagement:** Set up `scripts/trigger_retention_emails.py` to auto-email P2 accounts with custom templates matching their specific risk factors.
- [ ] **Close Feedback Loop:** Create BigQuery tables (`intervention_outcomes`, `email_log`) to track saves, churns, and actual revenue preserved.

### In-App Cancellation Save Flow
- [ ] **Build Deflection Steps:** Program a multi-step cancellation page offering a 3-month account pause (saving reviews/rankings), a downgrade path to Basic, or free profile optimization support.

---

## 👥 Phase 3: Sales Restructuring & Tiered Packages (Months 7-18)

### Inside Sales & Digital CS Transition
- [ ] **Redefine Sales Roles:** Move 70-80% of accounts to a centralized, inside-sales model (using video/phone onboarding and QBRs). Keep Field AMs exclusively for Premium strategic accounts.
- [ ] **Align Compensation:** Pivot AM commission structures to reward Net Revenue Retention (NRR) and expansion over volume, and offer bonuses for saving "Red" (high risk) accounts.

### Pricing & Packaging
- [ ] **Introduce Tiered Packages:** Package services into Basic (€399), Plus (€799), and Premium (€1,499) with clear, gated features (priority placement, featured badges, analytics pro).
