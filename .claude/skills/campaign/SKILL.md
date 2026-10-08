---
name: campaign
description: Plan and produce a VividWalls marketing campaign — Pinterest pins, Instagram/Facebook posts, email, blog post, ad creative and a Shopify discount — around a theme, season, or series launch. Use for holiday pushes, new series launches, or weekly content batches.
---

# Campaign Builder

## Brief (confirm with the owner)
Theme or occasion · featured series or pieces · audience segment (`business/company.md`) ·
offer (if any) · dates · channels · budget (paid ads only).

## Produce
1. **Hero creative** (Higgsfield): 3 room mockups per featured piece, sized for Pinterest 2:3,
   Instagram 4:5 and Stories 9:16. Optionally one 6–10s slow-pan video per piece.
2. **Pinterest** (`pinterest` MCP server): 5 pins per piece. Keyword-rich titles and descriptions
   ("Large abstract wall art for living room — <Name>"), each linking to the product with UTM
   `?utm_source=pinterest&utm_campaign=<slug>`. Use `get_boards` to pick the series or room board.
   After approval, publish with `create_pin` or `schedule_pins`. Use `get_trending_topics` for seasonal keywords.
3. **Instagram/Facebook organic**: 3 posts plus 3 stories, caption in the brand voice, CTA to the
   collection. Delivered as copy and creative for the owner to post.
4. **Meta ads** (`meta-ads` MCP server, only once checkout converts): propose campaign, ad sets
   (audience: US, 30–60, home décor / interior design interests; retargeting site visitors) and
   ads (3 creatives × 2 headlines). Start budgets at $10–20/day. Create everything **PAUSED** and
   activate only after owner approval. Kill rule: CAC > $40 after $150 spend.
5. **Email** (Shopify Email): subject line ×3 options, preheader, 150-word body, 3 product blocks.
6. **Blog post** (`wordpress` MCP server, `vividwalls.blog`): 800–1,200 words targeting one keyword
   theme, linking to 3+ products on `vividwalls.co` with UTM `utm_source=blog`. Create as a
   **draft** and publish after owner review.
7. **Offer**: if approved, create the discount with `create-discount` (unique code, start and
   end dates, minimum order). **Never publish without the owner's approval.**
8. **Calendar**: add the publish schedule to Google Calendar (after approval).

## Output
`ops/reports/<date>-campaign-<slug>.md` with all copy, creative links, schedule and success
metric (sessions from source, add-to-carts, orders with the code). For running Meta campaigns,
pull insights weekly (spend, CTR, CPC, purchases, CAC) for `weekly-review`.

## Holiday calendar
BFCM (late Nov) · Holiday gifting, last order date = Pictorem lead time + shipping (~Dec 10) ·
New Year refresh (Jan) · Valentine's (Feb) · Spring refresh (Mar–Apr) · Mother's Day · Back-to-school dorms (Aug).
