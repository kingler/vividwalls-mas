---
name: fulfill-order
description: Send a paid VividWalls Shopify order to Pictorem for print-on-demand fulfillment, then track it and mark it fulfilled in Shopify. Use when an order is paid and unfulfilled, or the owner says "fulfill order #NNNN".
---

# Fulfill an Order via Pictorem

Pictorem has no API connector, so Claude prepares everything and the owner submits the
order in the Pictorem pro dashboard (about 2 minutes).

## Steps
1. `get-order` for the order. Confirm: payment captured (PAID), not a test order, and the
   shipping address is complete. Stop and ask if anything is off.
2. For each line item, build the **Pictorem order sheet**:
   | Field | Source |
   |---|---|
   | Artwork | product title + handle |
   | Print file | master file name in Pictorem library (same as product handle) |
   | Format | Gallery Wrapped Stretched Canvas → "Canvas, stretched, 1.5in gallery wrap" · Canvas Roll → "Canvas, rolled" |
   | Size | variant size (e.g. 36x48), orientation from the artwork |
   | Quantity | line quantity |
   | Ship to | customer name and full address, phone |
   | Packing | brand as VividWalls, no Pictorem invoice in the box |
   | Expected cost | retail ÷ 2.065 (sanity check: flag if the Pictorem quote is >10% higher) |
3. Draft the customer confirmation email (Gmail draft, not sent): thank-you, printing timeline
   (Pictorem production plus shipping, typically 7–12 business days), what to expect.
4. After the owner confirms submission, record the Pictorem order number in a Shopify order note
   or tag (`pictorem:<id>`), with approval.
5. When tracking arrives (Gmail search `from:pictorem tracking`), create the Shopify fulfillment
   with the tracking number so Shopify emails the customer. Get approval before running the mutation.

## Guardrails
- Never submit to Pictorem or mark an order fulfilled without the owner's go-ahead.
- Credentials are never stored in this repo. The owner logs in to Pictorem.
- A paid order should reach Pictorem within 24 hours.
