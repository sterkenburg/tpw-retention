# Projected Booking Value Model

## The Concept

Turn abstract metrics (views, clicks) into an **estimated euro value**. This makes the ROI tangible.

**Important:** This is an *estimate*, not a guarantee. Frame it honestly to maintain trust.

---

## The Formula

```
Projected Value = (Contact Clicks × Contact-to-Conversation Rate × Conversation-to-Booking Rate × Average Booking Value) +
                  (Quote Requests × Quote-to-Booking Rate × Average Booking Value) +
                  (Phone Reveals × Phone-to-Booking Rate × Average Booking Value)
```

### Simplified Version (Dashboard Display)

```
Estimated Booking Value = Total Qualified Leads × Category Booking Rate × Category Average Booking Value

Where:
- Total Qualified Leads = Contact Clicks + Quote Requests + Phone Reveals
- Category Booking Rate = % of inquiries that result in a confirmed booking (by category)
- Category Average Booking Value = typical revenue per booking (by category)
```

---

## Category-Specific Assumptions (Dutch Wedding Market)

These are **starting estimates**. You should refine with your own data over time.

| Category | Avg Booking Value | Inquiry-to-Booking Rate | Notes |
|----------|------------------|------------------------|-------|
| **Venue** | €8,000 | 15% | High ticket, long decision, multiple visits |
| **Catering** | €6,500 | 20% | Often bundled with venue |
| **Photographer** | €2,500 | 35% | Portfolio-driven, faster decision |
| **Videographer** | €2,000 | 30% | Often upsold with photographer |
| **Florist** | €1,200 | 40% | Visual portfolio critical |
| **DJ / Music** | €1,000 | 45% | Lower ticket, faster booking |
| **Wedding Cake** | €600 | 50% | Very visual, quick decision |
| **Wedding Dress** | €2,000 | 25% | Often in-person visit required |
| **Suits** | €800 | 35% | Group bookings common |
| **Wedding Planner** | €3,500 | 20% | High trust, long sales cycle |
| **Hair & Makeup** | €500 | 40% | Trial session common |
| **Rings / Jewelry** | €3,000 | 30% | Often purchased offline |
| **Decor / Styling** | €2,000 | 30% | Visual-heavy |
| **Transport** | €800 | 35% | Functional purchase |
| **Stationery** | €400 | 45% | Lower involvement |
| **Honeymoon** | €5,000 | 15% | Often booked separately |

### How to Calculate Your Own Rates

**Step 1: Survey existing suppliers**
```
"In the past 12 months, approximately how many inquiries 
did you receive through ThePerfectWedding?"

"Of those, approximately how many resulted in a 
confirmed booking?"

"What was the average value of those bookings?"
```

**Step 2: Calculate category averages**
```
Category Booking Rate = Σ(Bookings per supplier) / Σ(Inquiries per supplier)
Category Avg Booking Value = Σ(Total booking value) / Σ(Total bookings)
```

**Step 3: Update quarterly**
- Start with industry estimates above
- After 100+ survey responses, use your own data
- Publish a "methodology" page for transparency

---

## Example Calculations

### Example 1: Photographer (High Conversion)
**Supplier stats (last 30 days):**
- Profile views: 180
- Contact clicks: 12
- Quote requests: 3
- Phone reveals: 2

**Calculation:**
```
Total Qualified Leads = 12 + 3 + 2 = 17
Category Booking Rate = 35%
Category Avg Value = €2,500

Estimated Value = 17 × 0.35 × €2,500 = €14,875

Conservative estimate (50% discount for uncertainty):
€14,875 × 0.5 = €7,438
```

**Dashboard display:**
> "💰 Based on your 17 interactions this month, photographers like you typically convert ~6 into bookings worth €2,500 each. **Estimated value: €7,400+**"

---

### Example 2: Venue (Lower Conversion, Higher Value)
**Supplier stats (last 30 days):**
- Profile views: 120
- Contact clicks: 8
- Quote requests: 2
- Phone reveals: 1

**Calculation:**
```
Total Qualified Leads = 8 + 2 + 1 = 11
Category Booking Rate = 15%
Category Avg Value = €8,000

Estimated Value = 11 × 0.15 × €8,000 = €13,200
Conservative: €13,200 × 0.5 = €6,600
```

**Dashboard display:**
> "💰 Based on your 11 inquiries, venues typically convert ~1-2 into bookings worth €8,000 each. **Estimated value: €6,600+**"

---

### Example 3: Wedding Cake (High Conversion, Lower Value)
**Supplier stats (last 30 days):**
- Profile views: 90
- Contact clicks: 6
- Quote requests: 4
- Phone reveals: 0

**Calculation:**
```
Total Qualified Leads = 6 + 4 = 10
Category Booking Rate = 50%
Category Avg Value = €600

Estimated Value = 10 × 0.50 × €600 = €3,000
Conservative: €3,000 × 0.5 = €1,500
```

---

## Conservative vs. Optimistic Display

### Option A: Conservative (Recommended for Trust)
Use 50% of calculated value. Frame as "potential" not "guaranteed."

```
💰 Potentiële waarde deze maand: €3,200

Berekend op basis van [X] aanvragen × [Y]% 
conversieratio × gemiddelde boekingswaarde €[Z].

Dit is een schatting — je werkelijke resultaten 
kunnen afwijken.
```

### Option B: Range
```
💰 Geschatte waarde: €2,400 — €4,800

Gebaseerd op je [X] aanvragen en conversieratio's 
van vergelijkbare leveranciers.
```

### Option C: ROI Comparison (Most Powerful)
```
💰 Geschatte waarde deze maand: €3,200
📋 Jouw abonnement: €42/maand
📈 Rendement: 75x je investering

---
Jaar-tot-datum:
• Totaal aanvragen: [X]
• Geschatte waarde: €[Y]
• Kosten TPW: €[Z]
• Netto rendement: €[Y-Z]
```

---

## Dashboard Integration

### Where to Show It

| Location | Display | Frequency |
|----------|---------|-----------|
| **Dashboard header** | Big number: "Geschatte waarde deze maand" | Real-time |
| **Monthly email** | Prominent section with trend | Monthly |
| **Profile completeness bar** | "Compleet je profiel om je geschatte waarde te verhogen" | Always |
| **Renewal page** | "Dit jaar haalde je €[X] aan waarde uit je €[Y] abonnement" | At renewal |

### Trend Visualization

```
Geschatte waarde (€)

€4,000 |        ▲
€3,000 |    ▲   │
€2,000 |▲  │   │
€1,000 |│  │   │
    €0 └──┴───┴──
      Jan  Feb  Mar

↑ 12% vs vorige maand
```

---

## Accuracy & Trust

### Transparency Section (Footer of Estimate)
```
Hoe berekenen we dit?
We nemen je aantal aanvragen, vermenigvuldigen dit 
met de gemiddelde conversieratio van [Categorie]-
leveranciers ([X]%), en vermenigvuldigen met de 
gemiddelde boekingswaarde (€[Y]).

We hanteren een voorzichtige schatting (50%) omdat 
niet elke aanvraag resulteert in een boeking.

Help ons de nauwkeurigheid te verbeteren:
[Hoeveel boekingen heb je via TPW gehad?]
```

### Calibration Over Time

| Quarter | Action |
|---------|--------|
| Q1 | Launch with industry estimates |
| Q2 | Survey 50+ suppliers per category |
| Q3 | Update formulas with real TPW data |
| Q4 | Publish "Your category averages" report |

---

## Red Flags to Avoid

1. **Don't guarantee bookings** — Always say "estimate" or "potential"
2. **Don't inflate numbers** — Better to under-promise and over-deliver
3. **Don't ignore seasonality** — January has more searches than November
4. **Don't show €0 as failure** — If no leads, show views + tips to improve
5. **Don't forget cancellations** — If supplier churned, stop showing "lost value"

---

## Seasonality Adjustment (Optional)

Wedding inquiries in NL follow a pattern:

| Month | Inquiry Volume | Adjustment Factor |
|-------|---------------|-------------------|
| January | Very High | 1.5x |
| February | High | 1.3x |
| March | High | 1.2x |
| April-May | Medium | 1.0x (baseline) |
| June-August | Medium | 1.0x |
| September-October | Medium-Low | 0.8x |
| November-December | Low | 0.6x |

**Use case:** In December, a supplier with 3 inquiries is actually performing *above average*. Adjust their benchmark accordingly.
