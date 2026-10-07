---
name: weekly-review
description: Monday growth review for VividWalls — weekly scorecard vs KPIs, funnel diagnosis, channel performance, B2B pipeline, and the plan for next week. Use on the weekly scheduled run or when the owner asks how the business is doing.
---

# Weekly Growth Review

## Data to pull (last 7 days vs prior 7, test orders excluded)
- `FROM sales SHOW orders, gross_sales, net_sales, average_order_value SINCE -7d UNTIL today COMPARE TO previous_period`
- `FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, sessions_that_completed_checkout SINCE -7d UNTIL today COMPARE TO previous_period`
- `FROM sessions SHOW sessions GROUP BY referrer_source, referrer_name SINCE -7d UNTIL today`
- `FROM sales SHOW gross_sales, orders GROUP BY product_title ORDER BY gross_sales DESC LIMIT 10 SINCE -30d UNTIL today`
- New customers and email subscribers (`list-customers`)
- B2B pipeline: `ops/pipeline.md` (contacted, replied, quoted, won)

## Analysis
1. Scorecard against `business/kpis.md` (add-to-cart rate, checkout completion, conversion, AOV, CAC if there's ad spend).
2. Find the single biggest funnel leak this week and its likely cause.
3. Channels: which source grew or shrank, and why (campaigns that ran).
4. Products: which pieces get views or add-to-carts and which get nothing. Candidates for
   mockup refresh or promotion.
5. Progress against the current phase of `business/growth-plan-90-day.md`.

## Output
Save to `ops/reports/<date>-weekly-review.md`, then send the owner a 10-line summary:
scorecard, 2 wins, 2 problems, **next week's 5 actions** (each with an owner, Claude or the
business owner).
