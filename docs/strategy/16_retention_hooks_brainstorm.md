# Retention Hooks Brainstorm — Non-Monetary Value-Add Ideas

> **⚠️ PARTIALLY SUPERSEDED (May 22 brainstorm).** The headline **Ad Boost Pool** (supplier-pays-more for leads) is **rejected** as a retention lever by [docs 17](17_refined_retention_strategy.md)–[18](18_value_add_bundle_and_pilot.md) (adverse selection; "pay more for leads" doesn't land with suppliers who feel overcharged). The individual hooks remain design inspiration for later phases.

**Date:** 2026-05-22  
**Context:** Brainstorm session exploring creative retention offers that do not involve discounts or out-of-pocket costs. Focus on positive value-adds that work for below-average performers and create genuine product stickiness.

---

## Framing & Constraints

- **No loss aversion:** All hooks must be framed positively (what you *gain*, not what you *lose*).
- **Zero marginal cost:** No discounts, cashback, or direct cash outlays from TPW.
- **Below-average performers matter:** Hooks must deliver value even to suppliers who do not rank in the top 50% for leads or views.
- **Dual persona:** The contract owner is often an *employee* (wants less work, less hassle, credit for good work), while the *business owner* cares about ROI and brand.
- **TPW owns the lead:** Where possible, the hook should route couples back to TPW rather than creating an independent supplier channel.

---

## Existing Assets to Build On

| Asset | What It Does | Retention Leverage |
|---|---|---|
| **Analytics Service** | GA OAuth connection → monthly PDF reports + year overview | Already sticky (data continuity); reports prove TPW outperforms other channels |
| **Profile Scraper** | Scrapes supplier website → auto-suggests company text, properties → one-click go-live | Reduces onboarding friction to near zero |
| **Review Widget** | Embeddable widget showcasing TPW reviews on supplier's own website | Very sticky — removing it means losing social proof on their site |
| **Real Weddings (Editorial)** | Editorial feature pages for real weddings | Can be opened up for supplier self-management |
| **Webhook / Instant Lead Alerts** | Real-time email + SMS on new leads | Foundation for auto-responder and lead enrichment |

---

## Selected Hooks for Further Development

### 🚀 Ad Boost Pool (Primary Focus)
**The mechanic:** TPW runs category-level Google Ads for solo-operator categories (photo, DJ, trouwambtenaar). Suppliers pay a monthly/yearly subscription to be included in the boosted traffic pool. TPW handles the ad spend, landing pages, and keyword optimization at scale — something no individual supplier can replicate.

**Current TPW ad model (for context):**
- Ads drive to category pages OR individual profile pages.
- Couples choose freely (choice-based = higher conversion than auto-routing).
- Couple fills in wedding date, name, email, phone on the profile page of their chosen supplier.
- Organic traffic is declining; ads are the backstop.

**Pilot categories:** Photography, DJ (Muziek), Trouwambtenaar.

**Pricing direction:** Monthly or yearly subscription (monthly +20% premium / yearly -20% discount). Same CPS as organic leads — no extra per-lead fee.

**Critical design tension:** If ads drive to a category page where couples freely choose, how do we guarantee boost subscribers receive leads? The bulk of requests already goes to a small percentage of top performers (Pareto problem).

**Distribution models under consideration:**
1. **Featured Placement** — Boost subscribers get top-of-page placement, larger cards, and a "Featured by TPW" badge on the category landing page.
2. **Rotating Spotlight** — One or two boost subscribers are prominently featured per week, rotating through the pool.
3. **Hybrid Lead Gen** — Ad drives to a "get quotes from top [category] in [region]" form. TPW distributes the lead to 2-3 boost subscribers based on availability/response time.
4. **Profile Page Ads** — Each boost subscriber gets their own dedicated ad campaign driving directly to their profile. Only viable for suppliers with strong profiles.

**Critical insight from TPW venue data & solo supplier behavior:**
- Generic/category ads work well and are profitable for TPW.
- Profile-specific ads are "bleeders" (unprofitable) when TPW bears the ad cost.
- Solo suppliers spend €200-500/month on DIY Google Ads as a **test**, then **stop** because they can't make it work.
- TPW's DNA is a marketplace that enables suppliers — not a pure marketing agency.

**This points to a pooled model, not individual ad management:**
- TPW pools subscription fees from boost subscribers.
- TPW runs optimized **category-level** ads using its existing expertise.
- Boost subscribers get **featured placement** + **profile optimization** (using the existing scraper/data).
- Suppliers pay a flat, predictable fee instead of burning money on DIY ads.

**The core value prop:** *"Stop wasting €200-500/month on Google Ads that don't work. For €49/month, TPW runs category ads at scale, optimizes your profile, and features you prominently."*

**Open questions:**
- How do we guarantee value to below-average performers in a choice-based system? (Profile optimization + minimum traffic guarantee?)
- How do we distinguish organic leads from ad-boosted leads in dashboards and billing?
- What is the right price point so that 1-2 extra leads per month makes it a no-brainer for the supplier?
- Do we roll out by category (photo → DJ → trouwambtenaar) or by region?

---

## 💰 Financial Model: Subscription vs. Performance-Based

**Updated assumptions based on TPW data:**
- TPW venue ad economics: **€125 per converted lead** (acquisition cost via Google Ads)
- Venue inquiry-to-booking rate: 15% → implied cost per inquiry: **~€19**
- TPW business model: **yearly subscription is the cash engine** that funds operations, projects, and personnel
- Ad Boost Pool is an **add-on subscription** on top of base listing — aligns with TPW's DNA

**Photography category assumptions (sensitivity range):**
- Avg. booking value: €2,500
- Inquiry-to-booking rate: 35%
- Expected value per lead: **€875**
- TPW venue benchmark: **€125 per converted lead** (~€19/inquiry)
- Photography keywords are more competitive than venues — model three scenarios:
  - **Efficient:** €25/inquiry (slightly higher than venues)
  - **Moderate:** €50/inquiry
  - **Expensive:** €100/inquiry (high competition, low category conversion)
- Target boost subscribers: **50**
- Organic CPS: **€50/lead**
- Pricing: Yearly €470 (€39/month effective) / Monthly €59 (+20% premium)

---

### Model A: Pure Subscription (Yearly Add-On)

**Mechanic:** Supplier pays a yearly boost subscription on top of their base listing. TPW pools all fees and runs category ads. All leads charged at standard organic CPS.

**TPW Economics (50 subscribers, €39/month effective):**

| Scenario | Cost per inquiry | Inquiries/month | CPS Revenue | Subscription Revenue | Total Revenue | Ad Cost | Margin | Margin % |
|---|---|---|---|---|---|---|---|---|
| **Efficient** | €25 | 78 | €3,900 | €1,950 | €5,850 | €1,950 | **€3,900** | **67%** |
| **Moderate** | €50 | 39 | €1,950 | €1,950 | €3,900 | €1,950 | **€1,950** | **50%** |
| **Expensive** | €100 | 19 | €950 | €1,950 | €2,900 | €1,950 | **€950** | **33%** |

**Supplier Economics (Moderate scenario):**

| | Calculation | Result |
|---|---|---|
| **Cost** | €39/month | **€39/month** |
| **Inquiries/month** | 39 ÷ 50 | **0.78** |
| **Bookings/month** | 0.78 × 35% | **0.27** |
| **Expected value** | 0.27 × €2,500 | **€683/month** |
| **ROI** | | **17.5x** |

Even in the **expensive** scenario:
- Cost: €39/month
- Inquiries: 0.38/month → bookings: 0.13/month → value: €333/month
- **ROI: 8.5x**

---

### Model B: Performance-Based (Ad Budget + CPS)

**Mechanic:** Supplier commits a monthly ad budget (e.g., €100). TPW manages the spend. Supplier pays standard CPS on all leads.

| | Calculation | Result |
|---|---|---|
| **Ad pool** | 50 × €100 | **€5,000/month** |
| **Inquiries** | €5,000 ÷ €50 | **100/month** |
| **Inquiries/subscriber** | | **2.0/month** |
| **TPW management fee** | 50 × €29 | **€1,450/month** |
| **TPW CPS revenue** | 100 × €50 | **€5,000/month** |
| **TPW total revenue** | | **€6,450/month** |
| **TPW ad cost** | (passed through) | **€5,000/month** |
| **TPW margin** | | **€1,450/month (22%)** |
| **Supplier cost** | €100 + €29 + (2.0 × €50) | **€229/month** |
| **Supplier ROI** | (2.0 × 35% × €2,500) ÷ €229 | **15.3x** |

**Cons:** Supplier cost approaches their current DIY burn rate (€200–500). If leads don't materialize, they feel cheated. TPW margin is thin unless management fee is much higher.

---

### Model C: Premium CPS (Venue-Style)

**Mechanic:** TPW runs ads at its own cost. Ad-driven leads charged at premium CPS (e.g., €100). No monthly fee.

| | Efficient | Moderate | Expensive |
|---|---|---|---|
| **TPW ad spend** | €1,950 | €1,950 | €1,950 |
| **Inquiries** | 78 | 39 | 19 |
| **TPW CPS revenue** | €7,800 | €3,900 | €1,900 |
| **TPW margin** | **€5,850 (75%)** | **€1,950 (50%)** | **€0 (0%)** |
| **Supplier cost/lead** | €100 | €100 | €100 |
| **Supplier ROI** | 8.75x | 8.75x | 8.75x |

**Cons:** In the expensive scenario, TPW breaks even. Supplier bears all volatility risk.

---

## 🎯 Comparison Summary

| Metric | A: Subscription | B: Ad Budget + CPS | C: Premium CPS |
|---|---|---|---|
| **Supplier monthly cost** | **€39** (yearly) | €229 | €0–€200 (variable) |
| **TPW margin (moderate)** | **50%** | 22% | 50% |
| **Revenue predictability** | **High** | Low | Medium |
| **Supplier risk** | **Low** | High | High |
| **Aligns with TPW DNA** | **Yes (subscription cash)** | No (agency model) | Partial |
| **Scales to 50+ subscribers** | **Yes** | Margin compression | Volatile |

---

## 💡 Key Insight

**Model A (Subscription) is the clear winner for TPW's business model.**

1. **Subscription cash funds operations** — aligns with how TPW already works.
2. **Even in the worst-case ad scenario, TPW makes 33% margin** and suppliers get 8.5x ROI.
3. **Supplier cost (€39/month) is 5–10x cheaper than their DIY waste** (€200–500/month).
4. **Predictable revenue** lets TPW plan ad spend quarters ahead, not month-to-month.

**The real unlock:** TPW currently doesn't advertise for solo categories because there's no CPS revenue stream to fund it. The boost subscription **creates that revenue stream** — turning organic-only categories into ad-funded growth categories.

**Recommended rollout:**
- **Yearly-only** for the first 6 months (locks in cash, reduces churn)
- **Price:** €470/year (€39/month effective)
- **Target:** 20 subscribers in Amsterdam photography as the pilot
- **Guarantee:** "If your profile isn't viewed by at least 10 extra couples in 90 days, we'll optimize it for free"

---

## ⚠️ Reality Check: Category-Specific Economics

**Critical insight from TPW:** The financial model above assumes category-average conversion rates from `categories.yaml`. But actual conversion varies wildly by category.

**Example — Trouwambtenaar:**
- Average invoice: €1,000
- Actual lead-to-booking conversion: **~1%**
- Expected value per lead: **€10**
- If TPW charges €50 CPS + ad budget: supplier pays €50+ for a lead worth €10.
- **This is economically unviable.**

**This means the Ad Boost Pool cannot be one-size-fits-all.**

**Categories where CPS + subscription might work (high value/lead):**
- Venue (€8,000 × 15% = €1,200/lead)
- Photography (€2,500 × 35% = €875/lead)
- Rings (€3,000 × 30% = €900/lead)
- Wedding Planner (€3,500 × 20% = €700/lead)

**Categories where CPS is likely broken (low value/lead):**
- Trouwambtenaar (€1,000 × 1% = €10/lead)
- Stationery (€400 × 45% = €180/lead — maybe viable if CPS is low)
- Transport (€800 × 35% = €280/lead)
- Hair & Makeup (€500 × 40% = €200/lead)

**Implication:** The Ad Boost Pool must be priced **per category** or limited to categories where the supplier ROI is clearly positive. For low-conversion categories, the model may need to be pure subscription (no CPS) with a much lower price point.

---

**Recommendation:** Do not launch Ad Boost Pool until real CPC and conversion data is available per category. Start with a category viability audit.

---

**Open questions:**
- How do we guarantee value to below-average performers in a choice-based system? (Profile optimization + minimum traffic guarantee?)
- How do we distinguish organic leads from ad-boosted leads in dashboards and billing?
- What is the right price point so that 1-2 extra leads per month makes it a no-brainer for the supplier?
- Do we roll out by category (photo → DJ → trouwambtenaar) or by region?

---

### 1. Instant Lead Auto-Responder
**The mechanic:** When a couple contacts a supplier via TPW, automatically send a warm first response on the supplier's behalf within 5 minutes. The supplier configures the template once.

**Why it's a hook:**
- The employee does zero work but looks hyper-responsive.
- Couples see fast response times, which improves booking rates even for below-average performers.
- If they churn, they lose this "always-on" first impression superpower.
- Builds on existing webhook infrastructure (`/webhooks/lead`).

---

### 2. Vendor Partner Matcher
**The mechanic:** Smart intro emails or in-app suggestions: "You're a photographer in Amsterdam. 2 florists and 1 venue within 5km are looking for preferred partners on TPW. Would you like an intro?"

**Why it's a hook:**
- Even low-lead suppliers get value from warm referral partnerships.
- Creates network effects — the more vendors on TPW, the more valuable the matching.
- Reframes TPW from a "lead site" to a "business network."
- Breaking the partnership means losing that referral stream.

---

### 3. Co-Branded Lead Magnet Generator
**The mechanic:** Auto-generate a beautiful PDF guide (e.g., *The Ultimate Wedding Planning Checklist*) co-branded with the supplier's company name + TPW logo. They embed it on their own website as a lead magnet.

**Critical constraint:** TPW must be the source for the leads. The download flow should capture the couple's email on TPW first, then route the enriched lead to the supplier.

**Why it's a hook:**
- Works for everyone regardless of TPW performance.
- Lives on their website — highly sticky.
- Supplier gets leads, TPW gets brand exposure and lead data.

---

### 4. Profile Refresh Bot
**The mechanic:** Seasonal one-click nudges: "Spring wedding season is coming — add 3 recent spring wedding photos to your profile." Or: "Update your 2026 pricing." One-click upload from phone or Instagram.

**Why it's a hook:**
- Keeps profiles fresh with near-zero friction.
- Works for below-average performers who might otherwise let their profile go stale.
- Creates a habit of logging into the TPW dashboard.

---

## Additional Hooks Under Consideration

### 5. Real Weddings Self-Management Portal
**The mechanic:** Open the existing editorial "Real Weddings" feature so suppliers can submit and manage their own real wedding stories. TPW auto-generates an SEO-optimized page with backlinks to each supplier's website and TPW profile.

**Why it's a hook:**
- Every wedding completed = free SEO backlink from a high-authority domain.
- Backlinks compound over time — the longer they stay, the more SEO value they accumulate.
- Creates cross-supplier collaboration (photographer tags florist, florist tags venue).

---

### 6. "Check Availability" Widget (Lead Capture Even When Booked)
**The mechanic:** An embeddable widget for the supplier's own website: "Check my availability for your wedding date."
- If available: routes to TPW message form.
- If booked: shows 3 similar available suppliers in the area → routes to TPW search results.

**Why it's a hook:**
- Saves the supplier time replying to "are you available?" emails.
- Even when fully booked, TPW still captures the lead via referrals.
- The supplier looks helpful by recommending peers.

---

### 7. Preferred Partner Network
**The mechanic:** Suppliers can mark 2-4 other TPW vendors as "preferred partners." When a couple views their profile, TPW surfaces: "This supplier often works with [Florist] and [Venue]. Want to see their profiles too?"

**Why it's a hook:**
- Creates passive cross-referrals without any work.
- Even low-lead suppliers get traffic from popular partners.
- Network effects: the more suppliers on TPW, the more valuable the matching.

---

### 8. Wedding Season Forecast Alerts
**The mechanic:** Based on aggregate TPW search data, send personalized trend alerts: "Searches for 'winter wedding photographer' in Amsterdam are up 47% this week. Consider adding winter wedding photos to your profile — here's a one-click upload link."

**Why it's a hook:**
- Even below-average performers can ride a trend and get a temporary boost.
- Makes TPW feel like an intelligent business advisor, not just a listing.
- Zero effort for the supplier — push notification with a one-click action.

---

### 9. Client Testimonial Collector (Universal Reviews)
**The mechanic:** A tool where suppliers can send a simple branded link to *any* past client — not just TPW couples — to collect testimonials. All testimonials feed into their TPW profile and can be exported to their website.

**Why it's a hook:**
- Their entire review library lives on TPW. If they leave, they lose the centralized collection.
- Even suppliers with few TPW leads can build social proof from offline/client work.

---

### 10. Response Time Gamification (Private)
**The mechanic:** A private dashboard metric: "You respond to leads in 2.3 hours on average — faster than 78% of photographers in Amsterdam." No public leaderboard, just a personal motivation nudge.

**Why it's a hook:**
- Below-average performers can win on speed even if they cannot win on popularity.
- Faster response → more bookings → higher retention.

---

### 11. Lead Enrichment / "Couple Insights"
**The mechanic:** When a lead comes in, TPW auto-enriches it with context: "This couple searched for 'rustic barn wedding,' has 120 guests, and their match score with your profile is 87%."

**Why it's a hook:**
- Saves the employee time researching the lead before responding.
- Helps them craft a personalized reply that converts better.
- Even below-average performers can punch above their weight with better context.

---

## Priority Matrix

| Hook | Build Effort | Stickiness | Works for Below-Avg? | TPW Owns Lead? | Selected? |
|---|---|---|---|---|---|
| Auto-Responder | Low | Very High | Yes | Yes | ✅ |
| Vendor Matcher | Low | High | Yes | No | ✅ |
| Lead Magnet | Medium | Medium | Yes | Partial | ✅ |
| Profile Refresh Bot | Low | Medium | Yes | No | ✅ |
| Real Weddings SEO | Medium | Very High | Yes | Yes | ⚠️ Under consideration |
| Availability Widget | Medium | Very High | Yes | Yes | ⚠️ Under consideration |
| Preferred Partners | Low | High | Yes | Partial | ⚠️ Under consideration |
| Season Forecast | Low | Medium | Yes | No | ⚠️ Under consideration |
| Testimonial Collector | Low | High | Yes | No | ⚠️ Under consideration |
| Response Time Gamification | Low | Medium | Yes | No | ⚠️ Under consideration |
| Lead Enrichment | Medium | Medium | Yes | Yes | ⚠️ Under consideration |

---

## Key Decisions

1. **Positive framing only:** Rejected all loss-aversion tactics (e.g., "what you'd lose" reports). Retention must feel like gaining a superpower, not avoiding a penalty.
2. **Below-average performers are not second-class:** Every hook must deliver value to the bottom 50% of suppliers, not just the top performers who already have great numbers to show.
3. **Employee persona matters:** The contract owner is often an employee who wants less work and more credit. Hooks that save time or generate ready-made internal reports are disproportionately sticky.
4. **Leverage existing infrastructure:** The GA analytics pipeline, webhook system, and profile scraper mean many of these hooks are 80% buildable with existing code.

---

## Open Questions

1. **Lead Magnet Lead Flow:** How exactly do we ensure TPW captures the lead when a couple downloads the co-branded PDF from a supplier's website? Redirect via TPW landing page? Embedded TPW form?
2. **Auto-Responder Tone:** Should the auto-responder be clearly labeled as automated ("This is an automatic confirmation...") or disguised as personal ("Hi, I'm [Name] and I'll reply properly soon")?
3. **Vendor Matcher Scope:** Should partner matching be purely algorithmic (category + region), or should suppliers manually approve/curate their preferred partners?
4. **Real Weddings Backlinks:** What is the editorial approval workflow if suppliers self-submit? How do we maintain quality while enabling scale?
5. **Season Forecast Data:** Do we have enough aggregate search volume data at the category/region level to generate meaningful weekly forecasts, or do we need to build that aggregation pipeline first?
6. **Ad Boost Lead Distribution:** If category-page ads drive traffic to a shared landing page, how do we ensure boost subscribers actually receive leads vs. non-subscribers? Is it featured placement, rotating spotlight, or a separate lead-gen form?
7. **Ad Boost Pricing:** Same CPS as organic, or a separate subscription tier? How do we handle the Pareto problem (bulk of requests already goes to top performers)?
8. **Ad Boost Cannibalization:** How do we distinguish organic leads from ad-boosted leads in the supplier dashboard and billing?

---

## Next Steps

→ **Deep-dive the Ad Boost Pool mechanics** — distribution model, pricing, pilot categories (photo, DJ, trouwambtenaar).  
→ Spec out the **Auto-Responder** data model and API endpoint first (lowest effort, highest stickiness).  
→ Deprioritize venue-specific hooks until browsing/engagement data quality is validated.
