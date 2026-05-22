# Automated Retention Flows — Detailed Playbooks

These flows replace high-touch AM work with automated, trigger-based interventions. Built for TPW's supplier base.

---

## Flow 1: Onboarding Rescue (Days 0-30)
**Goal:** Get suppliers to "aha moment" (first lead or first profile view spike).
**Channel:** Email + in-app/dashboard
**Owner:** Automated (Marketing Ops)

### Triggers
- Profile completion <80% after 7 days
- No photos uploaded after 3 days
- No description written after 5 days
- Zero profile views after 14 days

### Sequence

| Day | Trigger | Email Subject | Content |
|-----|---------|--------------|---------|
| 1 | Sign-up | "Welkom! Let's get your first booking" | Onboarding checklist, video tutorial link, "complete profile in 10 min" |
| 3 | No photos | "Suppliers with 10+ photos get 3x more inquiries" | Photo upload guide, examples from top performers |
| 7 | Profile incomplete | "You're 80% done — finish to go live" | Progress bar, what's missing, chatbot help |
| 14 | Zero views | "Your profile is live! Here's how to get noticed" | SEO tips, category trends, "upgrade to featured" soft pitch |
| 21 | No leads yet | "The secret of top TPW suppliers" | Case study: similar supplier who got 5 bookings, profile optimization tips |
| 30 | Active but no leads | "Let's review your first month" | Dashboard link, benchmark data, offer 15-min optimization call (inside sales) |

**Success Metric:** 80% profile completion by day 14, 50% receive first lead by day 30.

---

## Flow 2: Value Realization (Monthly)
**Goal:** Constantly remind suppliers what they're getting.
**Channel:** Email + dashboard
**Owner:** Automated

### The "Your Monthly Results" Email
Send on the 1st of every month to every active supplier.

```
Subject: Your ThePerfectWedding results for [Month]

Hi [Name],

Here's what you got last month:

📊 Your Stats:
• Profile views: 145 (↑ 12% vs last month)
• Photo views: 320
• Contact clicks: 8
• Quote requests: 2
• Saved to shortlist: 3 couples

💰 Estimated Value:
Based on your 8 contact clicks, suppliers in your category 
convert ~15% into bookings. That's potentially 1-2 bookings 
worth €[category avg].

🏆 Benchmark:
Top 10% suppliers in [Category] get 300+ views/month. 
Here's how to get there: [link to tips]

[CTA: View Full Dashboard]
```

**Success Metric:** Email open rate >40%, dashboard engagement up 50%.

---

## Flow 3: Churn Early Warning (Days 45-90)
**Goal:** Intervene before the cancellation decision.
**Channel:** Email → SMS → Inside Sales
**Owner:** Automated → Human handoff

### Risk Scoring Model
Assign points to behaviors:

| Behavior | Risk Points |
|----------|-------------|
| No login for 14 days | +20 |
| No login for 30 days | +50 |
| Profile views down 50% vs last month | +15 |
| Zero leads last 60 days | +30 |
| Visited cancellation page | +80 |
| Support ticket: "not getting leads" | +40 |
| **Total Score** | **Action** |
| 0-30 | Green — normal nurture |
| 31-60 | Yellow — automated re-engagement |
| 61-90 | Orange — personal email from CSM |
| 90+ | Red — inside sales call within 48h |

### Yellow Sequence (Score 31-60)
| Day | Subject | Content |
|-----|---------|---------|
| 1 | "We noticed you haven't checked in..." | Quick dashboard snapshot, trending searches in their category |
| 4 | "3 free ways to get more wedding leads" | Blog content: profile tips, photo guide, response time importance |
| 8 | "See how [Similar Supplier] got 10 bookings" | Case study with specific tactics |

### Orange Sequence (Score 61-90)
- Personalized email from named CSM: *"Hi [Name], I saw your profile views dropped last month. I have 3 quick ideas for you — can we do a 10-min call?"*
- If no response in 5 days, inside sales call.

### Red Sequence (Score 90+)
- Inside sales call within 48 hours
- Prep sheet: account history, last leads, profile gaps, renewal date
- Objective: diagnose problem, offer solution (profile help, downgrade, pause)

**Success Metric:** 30% of "Red" accounts saved, 20% of "Orange" re-engaged.

---

## Flow 4: Renewal Preparation (60 Days Before Renewal)
**Goal:** Secure renewal before the doubt sets in.
**Channel:** Email → Phone
**Owner:** Automated + Inside Sales

### Annual Contracts
| Day | Action | Owner |
|-----|--------|-------|
| -60 | "Your renewal is coming up — here's what you achieved" | Auto — value recap email |
| -45 | "Lock in your rate for 2 years" + 10% annual discount offer | Auto |
| -30 | If no response: inside sales call | Human |
| -14 | "Last chance: your account expires in 14 days" | Auto |
| -7 | Final call from inside sales | Human |
| -3 | "Your listing will be paused in 3 days" | Auto |

### Monthly Contracts
| Day | Action |
|-----|--------|
| -14 | "Switch to annual, save 20%" |
| -7 | Value recap + annual offer |
| -3 | "Don't lose your reviews and ranking" (loss aversion) |
| -1 | Final renewal push |

**Success Metric:** Renewal rate >85% for annual, >70% for monthly.

---

## Flow 5: Cancellation Save & Exit Interview
**Goal:** Save the account OR learn why they left.
**Channel:** In-app + Email
**Owner:** Automated + optional human

### In-App Cancellation Flow
Step 1: **Pause, don't cancel**
```
"Before you go — would you rather pause for 3 months? 
Your reviews and ranking will be saved."
[Pause Account] [Continue to Cancel]
```

Step 2: **Exit survey** (mandatory before cancel)
- Main reason (dropdown)
- How many bookings from TPW? (dropdown)
- What would change your mind? (open)

Step 3: **Instant offer based on reason**
| Reason | Offer |
|--------|-------|
| Too expensive | Downgrade to Basic (€299/yr) OR pause for 3 months |
| Not getting leads | "Let our team optimize your profile for free — keep your account for 30 more days" |
| Business closed | Pause 6 months |
| Switching competitor | "We'll match their price + give 2 months free" |
| Don't use it | "Here's a 2-min tutorial that got [Supplier X] 5 leads" |

Step 4: **If still canceling**
- "Your listing will be removed on [date]. You'll lose [X reviews]. Reactivate anytime."
- Add to win-back cohort

**Success Metric:** 15% saved at cancellation page, 80% exit survey completion.

---

## Flow 6: Win-Back (Post-Churn, Day 30, 90, 180)
**Goal:** Reactivate churned accounts cheaper than acquiring new ones.
**Channel:** Email → Phone for high-value
**Owner:** Automated

| Day | Subject | Content |
|-----|---------|---------|
| 30 | "We miss you — here's what changed at TPW" | New features, success story, "come back for 50% off 3 months" |
| 90 | "Your competitors are getting these leads" | Category-specific: "47 couples searched for [Category] in [Region] last month" |
| 180 | "One year ago you were with us..." | Nostalgia + major product improvements + "founder rate" pricing |
| 365 | "Happy anniversary — want to try again?" | Deep discount, no strings attached |

**Success Metric:** 8% reactivation rate at 12 months.

---

## Flow 7: Expansion/Upsell (Quarterly)
**Goal:** Grow revenue from existing accounts.
**Channel:** Email + inside sales
**Owner:** Automated + human for Premium

### Triggers
- Supplier at max tier utilization (e.g., 10 photos uploaded on Basic plan)
- High engagement but not on featured/promoted
- Seasonal peaks (wedding season prep in Jan-Mar)

### Sequence
```
Subject: You're in the top 20% of [Category] suppliers — here's how to get more

Hi [Name],

Your profile is performing great (145 views last month). 
Suppliers who upgrade to Featured get 3x more visibility.

[Upgrade for €20/month — 1-click]
```

**Success Metric:** 10% of customers upsell annually.

---

## Flow 8: Seasonal & Category-Specific Campaigns
**Goal:** Stay relevant year-round, not just at renewal.
**Channel:** Email + SMS

### Wedding Season Calendar
| Month | Event | Campaign |
|-------|-------|----------|
| Jan | Engagement peak | "Newly engaged couples are searching NOW" |
| Mar | Booking season | "Update your availability for 2026" |
| Jun | Summer weddings | "Share your recent work — get featured" |
| Sep | Post-summer | "Collect reviews from summer couples" |
| Nov | Off-season | "Prep your profile for Jan rush" |

### Category-Specific
- **Venues:** "Peak booking season starts in January"
- **DJs:** "78% of couples book their DJ 8+ months ahead"
- **Photographers:** "Couples who view 10+ photo galleries book 2x faster"

---

## Tooling Stack Recommendation

| Function | Tool | Budget Estimate |
|----------|------|-----------------|
| CRM / Customer Data | HubSpot or Pipedrive | €500-800/mo |
| Email Automation | HubSpot / Mailchimp / ActiveCampaign | €200-400/mo |
| In-App Messages | Intercom / Crisp / custom | €100-300/mo |
| Supplier Dashboard | Custom build or embedded analytics (Metabase, Looker) | €1-2k/mo |
| Churn Scoring | Mixpanel / Amplitude + custom rules | €300-500/mo |
| SMS | MessageBird / Twilio | Pay per use |
| Exit Surveys | Typeform / Formbricks / custom | €50-100/mo |

**Total estimated tooling:** €2,500-4,000/month
**Equivalent to:** ~0.5-1 FTE account manager
