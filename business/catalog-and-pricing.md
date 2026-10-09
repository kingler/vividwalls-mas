# Catalog & Pricing

## Pricing rule
`retail price = Pictorem pro cost × 2.065`
(Pictorem pro discount 15%; canvas rolls carry an extra 25% Pictorem discount.)

Floor: never sell below **1.8× Pictorem cost** (covers payment fees, shipping subsidy,
and returns) without owner approval.

## Current price ladder (identical for every artwork, Oct 2026)

| Variant | Retail | Implied Pictorem cost (÷2.065) | Gross margin before shipping & fees |
|---|---|---|---|
| 24x36 canvas roll | $153.00 | ~$74 | ~$79 (52%) |
| 24x36 gallery-wrapped | $204.00 | ~$99 | ~$105 (52%) |
| 36x48 canvas roll | $237.18 | ~$115 | ~$122 (52%) |
| 36x48 gallery-wrapped | $315.94 | ~$153 | ~$163 (52%) |
| 53x72 gallery-wrapped | $550.92 | ~$267 | ~$284 (52%) |

Shopify Basic payment fees are roughly 2.9% + $0.30 per order. Shipping cost on oversized
53x72 canvas is the biggest unknown — **confirm actual Pictorem shipping quotes** and
decide whether shipping is free (built into price) or charged at checkout.

## Known catalog issues (from 2026-10-07 audit)
- Prices end in odd cents ($237.18, $315.94, $550.92) — round to $239 / $319 / $549 for
  a more premium feel (needs approval).
- Inventory is tracked (273–450 units) with "deny when out of stock" — meaningless for
  print-on-demand and conflicts with "limited edition" messaging. Decide: true limited
  editions (e.g. 50 per size, numbered) **or** untracked open editions.
- Several handles/SEO titles don't match product names — see `ops/reports/2026-10-07-store-audit.md`.

## Adding new art
Use the `list-artwork` skill. Every new piece needs: high-res master file uploaded to
Pictorem, 5 variants on the ladder above, ≥5 images (flat + 2 room mockups + detail + scale),
series tag + collection, SEO title ≤60 chars, meta description ≤160 chars.
