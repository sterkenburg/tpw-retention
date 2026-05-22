# This Week Checklist — Start Immediately

Given what you already have (dashboard, annual billing), here are the highest-impact actions you can start **today** with minimal engineering.

---

## Monday: Projected Value Dashboard Addition
**Effort: Low | Impact: High**

- [ ] Pick 3 categories you have the most data on
- [ ] Estimate category booking rate and average booking value (use the table in [10_projected_value_model.md](10_projected_value_model.md) as starting point)
- [ ] Add a "Geschatte waarde" box to the dashboard for those 3 categories
- [ ] Frame it as "Dit is een schatting op basis van branchegemiddelden"
- [ ] Add a small survey: "Hoeveel boekingen heb je via TPW gehad?" to start calibrating

**Why:** Suppliers see €€€ instead of just clicks. Instant value perception shift.

---

## Tuesday: Monthly Results Email (Manual First)
**Effort: Low | Impact: High**

- [ ] Export last month's stats for your top 50 suppliers (views, clicks, inquiries)
- [ ] Use the template in [09_email_templates.md](09_email_templates.md) — "Monthly Results Email"
- [ ] Send manually from your CRM or even Mailchimp
- [ ] Track open rate and any replies

**Why:** Test the concept before automating. If suppliers reply "wow, I didn't know I got that many views," you know it works.

---

## Wednesday: Instant Notification Spec
**Effort: Low (planning) | Impact: High**

- [ ] Review [08_instant_notification_spec.md](08_instant_notification_spec.md)
- [ ] Decide: Email only first, or email + SMS together?
- [ ] Check if you have supplier mobile numbers in database
- [ ] Pick SMS provider (MessageBird, Twilio, or existing telecom partner)
- [ ] Write 1-pager for your engineering team with scope

**Why:** This is probably the single highest-ROI feature. A real-time "ding! new lead" creates emotional connection to the platform.

---

## Thursday: Exit Survey on Cancellation
**Effort: Very Low | Impact: Very High**

- [ ] Add 3 mandatory questions before cancellation completes:
  1. Main reason (dropdown: too expensive, not enough leads, switching competitor, business closed, other)
  2. Estimated bookings from TPW (0 / 1-2 / 3-5 / 6-10 / 10+)
  3. What would make you stay? (open text)
- [ ] Add "Pause instead" button as alternative to cancel

**Why:** Every cancellation without data is a wasted learning opportunity. After 50 responses, you'll know exactly what to fix.

---

## Friday: Internal Alignment
**Effort: Low | Impact: Medium**

- [ ] Share this strategy doc with sales leadership
- [ ] Calculate: How many accounts does each AM currently manage?
- [ ] Calculate: What % of AM time is spent on accounts under €750/year?
- [ ] Identify which accounts are actually worth field visits (top 10-15% by revenue)
- [ ] Sketch the 3-tier model (Starter/Growth/Premium) with your team's actual account list

**Why:** The sales team needs to see the math. "Driving 3 hours for a €500 account loses us €200 every time" is a powerful argument.

---

## Weekend: Competitive Intel (Optional but Valuable)

- [ ] Mystery-shop your top 2 competitors (Trouwland, Trouwinfo)
- [ ] Note their pricing, packages, and what they promise suppliers
- [ ] Sign up for their supplier newsletters if possible
- [ ] Document: What do they offer that TPW doesn't?

---

## If You Only Do 3 Things This Week

1. **Add projected value to dashboard** (3 categories) — proves ROI
2. **Send monthly results email** to top 50 suppliers — tests the concept
3. **Deploy exit survey** — stops flying blind on churn reasons

These three together cost almost nothing and will give you more actionable retention data than you have now.

---

## Next Week's Preview

Once this week's actions are live:
- Automate the monthly email (all suppliers, not just top 50)
- Build instant notification MVP (email first, SMS later)
- Start health scoring (login frequency + profile completion + leads)
- Design cancellation save flow (pause + downgrade options)
