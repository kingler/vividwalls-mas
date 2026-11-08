---
name: fulfill-order
description: Send a paid VividWalls Shopify order to Pictorem for print-on-demand fulfillment, then track it and mark it fulfilled in Shopify. Use when an order is paid and unfulfilled, or the owner says "fulfill order #NNNN".
---

# Fulfill an Order via Pictorem

Orders go to Pictorem through its ArtFlow API (`vividwalls-ops` tools,
`integrations/vividwalls-ops-mcp`). Claude prepares, prices and places the order; the owner
approves each one because it charges the business card.

## Steps
1. `fulfillment_queue`: paid, unfulfilled, real orders (test orders excluded), oldest first.
   Anything marked `urgent` (over 24 hours) goes first.
2. `pictorem_quote_order("#NNNN")`: validates every line with Pictorem and returns the exact
   product codes, print files, Pictorem cost per line and in total, and the cost the pricing rule
   expects. If `ready` is false, stop and handle each item in `problems`:
   - **no print file**: find the artwork with `pictorem_artworks(search=...)`, then
     `set_print_file(product_id, collection_id=...)` (or `file_url=` for a public https print file).
     It previews first; apply with `confirm=true` after the owner approves.
   - **quote more than 10% above expected**: show the owner both numbers. Proceed only if they
     accept the cost (`accept_quote=true`); also flag the product's price against the pricing rule.
   - **outside US/Canada**: submit by hand in the Pictorem dashboard (`pictorem_order_sheet`).
   - test, cancelled, unpaid, already fulfilled or already sent: do not order.
3. Optional dry run: `pictorem_submit_order("#NNNN", sandbox=true)` sends the order through
   Pictorem's test mode (validated end to end, nothing created or charged).
4. `pictorem_submit_order("#NNNN")` returns the preview: PO, ship-to, lines and total. Show it to
   the owner. After an explicit yes, call it again with `confirm=true`. It places the order and tags
   the Shopify order `pictorem:<id>`. The PO `VW-<number>` makes a retry safe: Pictorem returns the
   existing order instead of printing twice.
5. Draft the customer confirmation email as a Gmail draft, not sent: a thank-you, the printing
   timeline (Pictorem production plus shipping, typically 7-12 business days) and what to expect.
6. Check progress with `pictorem_order_status("#NNNN")`. When `ready_to_mark_fulfilled` is true, call
   `mark_fulfilled(order_id, tracking_number, carrier=...)` with its tracking number and carrier. It
   previews first and needs `confirm=true`. Shopify then emails the customer.

## Manual fallback
If the API is down or an order is outside US/Canada, `pictorem_order_sheet("#NNNN")` gives the sheet
the owner enters in the Pictorem pro dashboard; afterwards record it with
`record_pictorem_submission(order_id, pictorem_order_id)`.

## Guardrails
- Never place a Pictorem order or mark an order fulfilled without the owner's go-ahead.
- The Pictorem API token lives in the macOS Keychain (or `PICTOREM_ARTFLOW_KEY`), never in this repo.
- A paid order should reach Pictorem within 24 hours.
