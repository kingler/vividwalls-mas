---
name: daily-brief
description: Morning operations brief for VividWalls — new orders, fulfillment queue, yesterday's traffic and funnel, alerts, and today's top 3 priorities. Use when the owner asks for the daily brief, "what's happening today", or on the scheduled morning run.
---

# Daily Brief

Read `business/kpis.md` first for targets and the test-order exclusion rule.

## Steps
1. **Orders**: `list-orders` with query `created_at:>=<yesterday>`. Exclude test/owner orders.
   For each real order note: number, customer, items (artwork + size + format), total,
   payment status, fulfillment status.
2. **Fulfillment queue**: `list-orders` with `financial_status:paid fulfillment_status:unfulfilled`.
   Flag any paid order older than 24h that hasn't been sent to Pictorem as **URGENT**.
3. **Traffic & funnel (yesterday vs 7-day average)**:
   - `FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, sessions_that_completed_checkout TIMESERIES day SINCE -8d UNTIL today`
   - `FROM sessions SHOW sessions GROUP BY referrer_source SINCE -1d UNTIL today`
4. **Customers**: new customers or email subscribers yesterday (`list-customers` with `created_at:>=`).
5. **Inbox scan** (Gmail): unanswered customer emails, Pictorem shipping or tracking notices,
   B2B replies. Search: `newer_than:1d -category:promotions`.
6. **Alerts**: checkout reached but not completed, a traffic drop of more than 40% vs average,
   any refund or chargeback, low-stock flags (should be none for print-on-demand).

## Output
Short report, mobile-friendly:
```
VividWalls — <date>
Orders: N new ($X) · Queue: N to fulfill (N urgent)
Traffic: N sessions (±% vs 7d) · top source · ATC N · checkout N · bought N
Inbox: N need replies
Alerts: ...
Today's 3 priorities:
1. ...
```
Priorities come from: urgent fulfillment, then customer replies, then the current
phase of `business/growth-plan-90-day.md`.

## Guardrails
Read-only. Draft replies only, never send. Never fulfill, refund or cancel inside the brief.
