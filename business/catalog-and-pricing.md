# Catalog & Pricing

## Pricing rule
`retail price = Pictorem pro cost × 2.065`
(Pictorem pro discount 15%; canvas rolls carry an extra 25% Pictorem discount.)

Floor: never sell below **1.8× Pictorem cost** (covers payment fees, shipping subsidy,
and returns) without owner approval.

## Current price ladder (identical for every artwork, set 2026-11-08)

Prices were reset to the rule on 2026-11-08 from live Pictorem ArtFlow API quotes (pro
discount applied, US delivery, no shipping charge for US/Canada). The old ladder had the
53x72 gallery wrap at 1.18x cost, the 53x72 roll at 1.42x and the 36x48 wrap at 1.77x,
all below the floor.

| Variant | Retail | Pictorem cost (live quote) | Gross margin before fees |
|---|---|---|---|
| 24x36 canvas roll | $112.19 | $54.33 | $57.86 (52%) |
| 24x36 gallery-wrapped | $208.63 | $101.03 | $107.60 (52%) |
| 36x48 canvas roll | $194.28 | $94.08 | $100.20 (52%) |
| 36x48 gallery-wrapped | $368.62 | $178.51 | $190.11 (52%) |
| 53x72 canvas roll | $600.30 | $290.70 | $309.60 (52%) |
| 53x72 gallery-wrapped | $962.91 | $466.30 | $496.61 (52%) |

Re-check costs with `pictorem_quote_order` (vividwalls-ops); Pictorem prices change.

Shopify Basic payment fees are roughly 2.9% + $0.30 per order. Shipping cost on oversized
53x72 canvas is the biggest unknown — **confirm actual Pictorem shipping quotes** and
decide whether shipping is free (built into price) or charged at checkout.

## Known catalog issues (from 2026-10-07 audit)
- Prices end in odd cents ($194.28, $368.62, $962.91) — rounding (e.g. $199 / $369 / $965)
  would read as more premium; rounding down must stay at or above 1.8x cost (needs approval).
- Inventory is tracked (273–450 units) with "deny when out of stock" — meaningless for
  print-on-demand and conflicts with "limited edition" messaging. Decide: true limited
  editions (e.g. 50 per size, numbered) **or** untracked open editions.
- Several handles/SEO titles don't match product names — see `ops/reports/2026-10-07-store-audit.md`.

## Adding new art
Use the `list-artwork` skill. Every new piece needs: high-res master file uploaded to
Pictorem, 5 variants on the ladder above, ≥5 images (flat + 2 room mockups + detail + scale),
series tag + collection, SEO title ≤60 chars, meta description ≤160 chars.
