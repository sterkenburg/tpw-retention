# Instant Lead Notification — Product Spec

## Why This Matters

A supplier who gets a real-time alert that a couple is interested feels immediate value. The €500/year subscription transforms from an abstract expense into a **lead generation machine** that just paid for itself.

**Psychology:**
- **Recency bias:** The supplier associates TPW with a fresh opportunity
- **Loss aversion:** Missing a lead because they didn't see it in time = pain
- **Tangible ROI:** "I paid €500 and just got a €3,000 booking inquiry" = easy math

---

## Notification Triggers

Define what counts as a "lead-worthy" event. Start simple, expand later.

| Event | Priority | Channels | Rationale |
|-------|----------|----------|-----------|
| **Contact form submitted** on supplier profile | High | Email + SMS | Direct intent — hottest lead |
| **Phone number revealed** (couple clicks "show phone") | High | Email | Strong intent, supplier should be ready |
| **Quote request sent** | High | Email + SMS | Direct commercial intent |
| **Supplier saved to shortlist** | Medium | Email | Interest signal, good for morale |
| **Profile shared** (couple shares profile via WhatsApp/email) | Medium | Email (daily digest) | Word-of-mouth indicator |
| **Photo gallery viewed** (5+ photos) | Low | Weekly digest only | Engagement signal, not urgent |

---

## Notification Design

### Email Notification

**Subject:** 🔔 New lead from ThePerfectWedding — [Couple] is interested in [Category]

```
Hi [Supplier Name],

Great news! A couple just showed interest in your business.

📋 Lead Details:
• Event date: [Date or "Not specified"]
• Guest count: [Number or "Not specified"]
• Location preference: [Region]
• Message: "[Quote from contact form]"

💡 Recommended next step:
Respond within 2 hours — suppliers who reply fast 
convert 3x more bookings.

[View Full Lead →]
[Go to Dashboard →]

---
This is lead #3 you've received this month.
Your profile has been viewed 45 times.

Need help optimizing your profile? 
[Get free tips →]
```

**Design notes:**
- Mobile-first (suppliers check email on phone)
- Single CTA above the fold
- Include "reply time" social proof
- End with gentle upsell/nudge

### SMS Notification

**For:** Contact form + quote request only (high priority)

```
ThePerfectWedding: New lead! [First name] is interested in 
[Category] for [Date if known]. Reply fast for best results. 
View: [short link]
```

**Constraints:**
- Max 160 characters (single SMS)
- Short link to lead detail page
- Include supplier login token (auto-login)
- Send only during business hours (8am-8pm) unless "urgent" flag

### In-App / Dashboard Notification

- Red badge on notification bell
- Notification center with timestamp
- "Mark as responded" + "Mark as booked" actions
- Filter: All / Unread / Responded / Booked

---

## Supplier Settings

Let suppliers control their notification preferences:

| Setting | Default | Options |
|---------|---------|---------|
| Email notifications | On | Instant / Daily digest / Off |
| SMS notifications | On | Instant / Off |
| Quiet hours | Off | 10pm-8am block |
| Minimum lead quality | All | Only verified couples / All |

**Onboarding prompt:** During sign-up, ask for mobile number with value prop: *"Get instant SMS alerts when couples contact you. Suppliers who respond within 2 hours book 3x more weddings."*

---

## Backend Requirements

### Data Needed
- Couple profile data (event date, guest count, region)
- Supplier contact preferences
- Notification history (prevent duplicates)

### Logic
```
WHEN couple submits contact form OR reveals phone OR requests quote:
  1. Log event in supplier dashboard
  2. IF supplier has email notifications ON:
     Send email immediately (queue, target <2 min delay)
  3. IF supplier has SMS notifications ON AND event is high priority:
     Send SMS immediately
  4. Update notification center (in-app badge +1)
  5. Update "leads this month" counter
  6. IF first lead ever: trigger "first lead celebration" email
```

### Edge Cases
- **Duplicate protection:** Same couple contacting same supplier within 24h = suppress duplicate notification, update existing thread
- **Bounce handling:** If email bounces, flag account for "update your email" flow
- **SMS failure:** Fallback to email if SMS undelivered
- **Supplier inactive:** If supplier hasn't logged in 30 days, add "We miss you" nudge to notification

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Notification delivery rate | >98% | Sent / attempted |
| Email open rate | >60% | Email analytics |
| SMS open rate | >90% | Delivery receipt |
| Supplier response time | <4 hours median | Time from notification to supplier reply |
| Supplier satisfaction | >4.0/5 | Quarterly survey: "How useful are lead notifications?" |
| Lead-to-booking conversion | Baseline + track | Supplier self-reported or tracked via "mark as booked" |

---

## Implementation Estimate

| Task | Effort | Owner |
|------|--------|-------|
| Add mobile number field to supplier profile | 1-2 days | Engineering |
| Build notification preference settings | 2-3 days | Engineering |
| Email template + sending logic | 3-5 days | Engineering + Marketing |
| SMS integration (MessageBird/Twilio) | 2-3 days | Engineering |
| In-app notification center | 5-7 days | Engineering |
| "Mark as responded/booked" tracking | 2-3 days | Engineering |
| **Total** | **2-3 weeks** | |

**Cost:** ~€3,000-6,000 engineering + €50-150/month SMS
