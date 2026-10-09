# 90-Day Plan — Oct 7 → Jan 5, 2027

Goal: **first 25 real orders and 3 repeat B2B accounts** before the end of the holiday season,
with a proven funnel to scale from.

## Phase 0 — Stop the leaks (Week 1)
| # | Action | Owner | Why |
|---|---|---|---|
| 0.1 | Change Pictorem password (and anywhere it was reused); make the `vividwalls-mas` and `vivid_mas` repos private | Owner | The password was exposed in the public repo. DigitalOcean and n8n are retired, so their keys are moot once those accounts are closed |
| 0.2 | Place a real $1 test order end-to-end (live payment, real address) and fix what breaks | Owner + Claude | 15 visitors reached checkout and **0** finished — checkout is likely broken (payment provider, shipping rates for oversized canvas, or theme bug) |
| 0.3 | Cancel stale test orders #1001–#1008 so analytics are clean | Claude (with approval) | |
| 0.4 | Confirm Pictorem shipping costs by size; set shipping policy (free over $X?) | Owner | Margin clarity |

## Phase 1 — Convert the traffic we already get (Weeks 2–4) · *Operations + Growth*
- Fix SEO titles/meta descriptions on all 37 products (`optimize-listing`).
- Add room-scene mockups to every product (Higgsfield) — buyers need to see scale.
- Trust layer on product pages: shipping time, free returns window, "printed in North America",
  canvas quality details, reviews app.
- Welcome offer: 10–15% off first order for email signup (pop-up) → starts the email list.
- Abandoned-checkout email flow in Shopify (built-in, free on Basic).
- Round prices ($239 / $319 / $549) and decide limited-vs-open edition messaging.

## Phase 2 — Build demand (Weeks 3–10) · *Growth*
- **Pinterest** is the #1 free channel for wall art: 5 pins/day from room mockups,
  boards per series and per room (living room, office, bedroom).
- **Google**: submit to Google Merchant Center (free Shopping listings) via Shopify Google channel.
- **Content**: 2 posts/week on the WordPress blog `vividwalls.blog` ("large wall art for living rooms", "how to choose art size
  above a sofa") linking to collections.
- **Holiday push** (Nov 1–Dec 15): gift guide, canvas-roll gift tier, BFCM offer, last-ship date
  banner tied to Pictorem lead times.
- Paid test once checkout converts: $20/day Meta + Pinterest ads on top 5 pieces, kill at CAC > $40.

## Phase 3 — Business development (Weeks 2–12) · *B2B*
- Trade program page: 20% trade discount, net-30 for approved accounts, volume pricing,
  custom sizes via Pictorem.
- Build a list of 100 prospects: NYC/NJ interior designers, home stagers, boutique hotels,
  Airbnb property managers, co-working spaces, real-estate developers (model units).
- `b2b-outreach`: 10 personalized emails/day, follow-up cadence day 3 and day 8.
- Lookbook PDF per segment (hospitality, office, residential staging).
- Target: 30 conversations → 10 quotes → 3 accounts.

## Operating rhythm (Claude runs, owner approves)
| Cadence | Playbook | Output |
|---|---|---|
| Daily | `daily-brief` | Orders, fulfillment queue, traffic, alerts, today's 3 priorities |
| Per order | `fulfill-order` | Pictorem order sheet + customer update draft |
| Weekly (Mon) | `weekly-review` | Scorecard vs `kpis.md`, wins, next week's plan |
| Weekly | `campaign` | Next week's pins, posts, email, creative |
| Daily (B2B) | `b2b-outreach` | Drafted emails for approval + pipeline update |
