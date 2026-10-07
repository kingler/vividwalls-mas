# Store Audit — 2026-10-07

Live data pulled from Shopify (`vividwalls-2.myshopify.com`) on 2026-10-07.

## Headline
The store gets traffic but **has never converted a real customer**. 15 sessions reached
checkout in the last 6 months and 0 completed. Fixing checkout and product-page trust
comes before spending on traffic.

## Funnel (Apr–Oct 2026)
1,770 sessions → 15 add-to-cart (0.85%) → 15 reached checkout → **0 purchases**.
Every add-to-cart reached checkout, so the cart page isn't the blocker. People who decide to
buy are dropping in checkout itself. Likely causes, in order:
1. Payment provider not fully activated, or stuck in test mode.
2. No or very high shipping rate for oversized canvas (53x72), or no rate for the buyer's region.
3. A theme/custom-pricing script (the `vividwalls-shopify-theme` repo has "dynamic pricing"
   customizations) changing the price between cart and checkout.
4. Surprise costs at checkout (shipping and tax shown only at the last step).

**Action:** place a real order with a live card, then review Settings → Payments and Shipping.

## Orders
All 8 orders are test or owner orders (#1001–#1005 "Test User", #1006–#1008 owner, Feb 2026).
Three are still open (#1006 and #1007 pending payment, #1008 paid and unfulfilled).
Recommend cancelling them so dashboards stay clean.

## Catalog (37 active products, 9 collections)
Good:
- Every product has a description, 5–7 images, a collection and a series tag, and is
  published to the Online Store.

Problems:
| Issue | Products affected | Fix |
|---|---|---|
| SEO title doesn't match product name | Fractal Red no1 (SEO title is a keyword-stuffed "...Fractal Double Red 72x53, Black Frame"); Parallelogram Illusion no2 ("Structured Emerald No3"); no3 ("Prismatic Warmth"); no4 ("Structured Noir no1"); Royal Shade ("Textured Royal no1"); Vivid Mosaic no4 ("no5"); Intersecting Perspectives No4 and No5 (titled as No3 and No1) | Rewrite to `<Name> — Abstract Canvas Wall Art \| VividWalls` |
| SEO title hard-codes one size ("24x36 Gallery Wrapped Canvas") | ~34 | Remove the size; every product comes in 3 sizes |
| Meta description missing | Space & Form no1, no2, Space Form no4 | Write one (≤160 chars) |
| Meta description far too long (450–1,000 chars; Google shows ~155) | 34 | Rewrite to 140–155 chars with a call to action |
| URL handle doesn't match the name | `fractal-double-red`, `verdant-layers`, `prismatic-warmth`, `structured-noir-no1`, `textured-royal-no1`, `vivid-mosaic-no5`, `untiled-n011` (typo) | Change the handle **with a 301 redirect** (Shopify offers this when you edit the handle) |
| Title inconsistency | "Intersecting Perspective No3" (singular); "no1" vs "No1" capitalization; "Space Form no4" vs "Space & Form" | Standardize |
| Inventory tracked at 273–450 units with "stop selling when out" | all | Untrack inventory (print-on-demand), or set real edition sizes |
| Odd-cent pricing ($237.18, $315.94, $550.92) | all | Round prices (needs approval) |
| 53x72 offered only as gallery-wrapped (5 variants on Fractal Red no1, 6 on the rest) | check | Confirm the variant set is the same across products |

## Traffic sources
77% direct, 18% search, 5% social. There is almost no Pinterest, Instagram or Google
Shopping traffic, which are the main free discovery channels for wall art. Traffic has
fallen since June (492 → 152 sessions/month).

## Security (repo, not store)
The public GitHub repo `kingler/vividwalls-mas` contains, in plain text: the Pictorem account
password (11 files including README.md), a DigitalOcean SSH private key
(`docs/guides/setup/GITHUB_CICD_SETUP.md`), an n8n API key, and a database password.
**Rotate all of them.** Then either make the repo private or purge the git history.
