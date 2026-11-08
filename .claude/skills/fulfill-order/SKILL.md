---
name: fulfill-order
description: Send a paid VividWalls Shopify order to Pictorem for print-on-demand fulfillment, then track it and mark it fulfilled in Shopify. Use when an order is paid and unfulfilled, or the owner says "fulfill order #NNNN".
---

# Fulfill an Order via Pictorem

Pictorem has no API connector, so Claude prepares everything and the owner submits the
order in the Pictorem pro dashboard (about 2 minutes).

## Steps
Use the `vividwalls-ops` tools (`integrations/vividwalls-ops-mcp`).
1. `fulfillment_queue`: lists paid, unfulfilled, real orders (test orders are already excluded),
   oldest first. Anything marked `urgent` (over 24 hours) goes first.
2. `pictorem_order_sheet("#NNNN")`: gives the exact sheet the owner enters in the Pictorem pro
   dashboard (print file, format, size, quantity, ship-to address, packing note, expected cost).
   If `ready` is false, stop and tell the owner each item in `problems`.
3. Draft the customer confirmation email as a Gmail draft, not sent: a thank-you, the printing
   timeline (Pictorem production plus shipping, typically 7-12 business days) and what to expect.
4. Once the owner confirms the order is submitted, call `record_pictorem_submission(order_id,
   pictorem_order_id)`. It previews first; call it again with `confirm=true` after approval.
5. When tracking arrives (Gmail search `from:pictorem tracking`), call `mark_fulfilled(order_id,
   tracking_number, carrier=...)`. It previews first and needs `confirm=true`. Shopify then
   emails the customer.

## Guardrails
- Never submit to Pictorem or mark an order fulfilled without the owner's go-ahead.
- Credentials are never stored in this repo. The owner logs in to Pictorem.
- A paid order should reach Pictorem within 24 hours.
