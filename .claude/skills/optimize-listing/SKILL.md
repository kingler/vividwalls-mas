---
name: optimize-listing
description: Audit and rewrite SEO titles, meta descriptions, handles, alt text and product copy for VividWalls Shopify products to grow organic search and Pinterest traffic. Use for "fix SEO", "improve product pages", or working through the audit list.
---

# Optimize Product Listings

## Steps
1. Pull products with GraphQL (follow the Shopify GraphQL workflow: schema, then validate,
   then query): `title handle seo{title description} description media alt text`.
2. Score each product:
   - SEO title matches the product name, is ≤60 chars, and has no hard-coded size.
   - Meta description is 140–155 chars and includes a call to action.
   - Handle matches the title.
   - Every image has alt text (`<Name> abstract canvas wall art in <room>`).
   - Description opens with a benefit or room, not technique jargon.
3. Produce a **change table** (current → proposed) and save it to
   `ops/reports/<date>-seo-changes.md`.
4. After the owner approves, apply the changes with `update-product`, a batch of 10 at a time.
   For handle changes, make sure a URL redirect from the old handle is created.
5. Re-check two weeks later: `FROM sessions SHOW sessions WHERE referrer_source = 'search' TIMESERIES week`.

## Keyword themes
large abstract wall art, geometric canvas art, modern living room wall art, oversized canvas
print, black and white abstract art, red abstract wall art, office wall art, statement art above sofa.
