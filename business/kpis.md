# KPIs & Targets

## North-star targets (from original business plan)
| Metric | Target |
|---|---|
| Customer acquisition cost (CAC) | < $25 |
| Average order value (AOV) | > $150 |
| Customer lifetime value (LTV) | > $500 |

## Baseline — 2026-10-07 (real customers only, test orders excluded)
| Metric | Value | Source |
|---|---|---|
| Sessions, Apr–Oct 2026 | 1,770 (peak 492 in June, 152 in Sept) | `FROM sessions` |
| Traffic mix | 77% direct · 18% search · 5% social | `GROUP BY referrer_source` |
| Sessions with add-to-cart | 15 (0.85%) | funnel query |
| Sessions reaching checkout | 15 | funnel query |
| Completed checkouts | **0** | funnel query |
| Real customer orders, last 12 months | **0** (all 8 orders are tests/owner) | `list-orders` |

## Funnel benchmarks to aim for (home-decor ecommerce)
| Stage | Healthy range | Ours |
|---|---|---|
| Add-to-cart rate | 3–6% | 0.85% |
| Checkout completion (reached → bought) | 40–55% | 0% |
| Conversion rate | 0.8–1.5% | 0% |

## Weekly scorecard (produced by `weekly-review`)
Sessions · source mix · add-to-cart rate · checkout reach · orders · revenue · AOV ·
new email subscribers · B2B leads contacted / replied / quoted / won.
