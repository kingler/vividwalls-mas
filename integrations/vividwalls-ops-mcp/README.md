# vividwalls-ops: n8n workflows as agent functions

The retired n8n workflows rewritten as tested Python functions that Claude agents call as
MCP tools. The design rule: **the agent does the judgement work, the functions do the exact
work.** Analysing artwork, writing copy and choosing what to recommend are the agent's job.
Prices, order handling, saved data and search ranking go through these functions, which are
covered by tests.

## Which n8n workflow became what

| n8n workflow (removed Oct 2026) | Now |
|---|---|
| E-commerce Order Fulfillment, Orders Fulfillment Agent, Pictorem Agent | `fulfillment_queue`, `pictorem_quote_order`, `pictorem_submit_order`, `pictorem_order_status`, `mark_fulfilled` (Pictorem ArtFlow API), with `pictorem_order_sheet` and `record_pictorem_submission` as the manual fallback, plus the `fulfill-order` playbook |
| Artwork Color Analysis (both versions) | The agent looks at the image, then `save_artwork_profile` validates the profile and stores it on the product. `unprofiled_artworks` lists what's left to do |
| Database Integration & Search, Prompt-Chain Image Retrieval, Sales Agent (recommendations) | `search_artworks` (colour, mood, room, budget; best fit first, with reasons) |
| Marketing Campaign Agent, Content Marketing Agent (+ Human Approval versions) | `campaign` playbook, `pin_drafts`, `utm_link`, plus the Pinterest, Meta ads and WordPress servers |
| Telegram approval steps in the "Human Approval" workflows | The approval gate on every store-changing function (below) |
| Business Manager Orchestration | `CLAUDE.md` plus the playbooks. Claude routes work to the right playbook, so there is no router code |
| Marketing Research Agent (monthly schedule) | `weekly-review` playbook run as a scheduled routine |
| Customer Service / Customer Relationship agents | `daily-brief` (inbox scan) and drafted replies, with `search_artworks` for product questions |
| DB connection test, WordPress chatbot, starter-kit RAG and Slack/Google Doc templates | Not ported: unused or broken |

Artwork profiles are stored on the products as Shopify metafields in the `vividwalls`
namespace (`dominant_colors`, `color_temperature`, `moods`, `rooms`), so there is no
separate database.

## Tools

| Tool | Changes the store? |
|---|---|
| `fulfillment_queue` | No |
| `pictorem_order_sheet` | No |
| `pictorem_quote_order` | No (asks Pictorem to validate and price) |
| `pictorem_submit_order` | Yes: places a Pictorem order (charges the card) and tags the Shopify order. `sandbox=true` uses Pictorem's test mode instead |
| `pictorem_order_status` | No |
| `pictorem_artworks` | No |
| `set_print_file` | Yes: product metafield linking it to its Pictorem print file |
| `record_pictorem_submission` | Yes: adds an order tag |
| `mark_fulfilled` | Yes: creates the fulfillment and emails the customer |
| `price_check` | No |
| `unprofiled_artworks` | No |
| `save_artwork_profile` | Yes: product metafields |
| `search_artworks` | No |
| `utm_link`, `pin_drafts` | No |

**Pictorem ordering.** Orders go through Pictorem's ArtFlow API
([docs](https://www.pictorem.com/artflow/0.1/docs)). Each Shopify product is linked to the file Pictorem
prints with `set_print_file`: a Pictorem artwork ID (`vividwalls.pictorem_collection_id`, from
`pictorem_artworks`) or a public https print file (`vividwalls.print_file_url`). Variants map to product
codes as gallery wrap = `canvas|stretched|...|c15|imagewrap` and roll = `canvas|canvasroll|...`; Pictorem's
sanitizer completes the code (hanging wire) and the tool re-validates the corrected code. A quote more
than 10% above the pricing rule's expected cost, a missing print file, a non-US/Canada address or an
existing `pictorem:` tag stops the order. The PO is `VW-<order number>`, so Pictorem rejects a second
print of the same order and returns the first.

**Order safety.** `pictorem_order_sheet` and `mark_fulfilled` refuse test, cancelled, unpaid and
already-fulfilled orders. Order numbers must look like `#1009`. Tracking links must be https links
on a carrier site, because they go into customer emails.

**Approval gate.** A store-changing tool only acts when it is called with `confirm=true`
**and** the environment has `VIVIDWALLS_ALLOW_WRITES=1`. In every other case it returns
exactly what it would change. Scheduled routines run without the switch, so they can only
prepare drafts for the owner.

## Setup

1. In Shopify admin, go to **Settings → Apps → Develop apps** and create an app. Grant the
   Admin API scopes `read_orders`, `write_orders`, `read_products`, `write_products`,
   `read_merchant_managed_fulfillment_orders` and `write_merchant_managed_fulfillment_orders`,
   then install the app and copy the Admin API access token.
2. Install and register:
   ```bash
   # from the repository root
   (cd integrations/vividwalls-ops-mcp && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)
   claude mcp add vividwalls-ops \
     -e SHOPIFY_ADMIN_TOKEN=... \
     -e VIVIDWALLS_TEST_CUSTOMERS="Test User" \
     -e VIVIDWALLS_ALLOW_WRITES=1 -- \
     integrations/vividwalls-ops-mcp/.venv/bin/python integrations/vividwalls-ops-mcp/server.py
   ```
   Leave out `VIVIDWALLS_ALLOW_WRITES=1` wherever the server should only ever draft.
3. Pictorem API token: in Pictorem go to **My Account → API Key & Docs**, create a token, then store it
   in the macOS Keychain (it is read at call time and never written to disk by the server):
   ```bash
   security add-generic-password -U -s vividwalls-pictorem-api -a "<your Pictorem email>" -w
   ```
   On other machines set `PICTOREM_ARTFLOW_KEY` instead.

| Variable | Purpose | Default |
|---|---|---|
| `SHOPIFY_ADMIN_TOKEN` | Admin API token (required for store tools) | none |
| `SHOPIFY_STORE_DOMAIN` | Store admin domain | `vividwalls-2.myshopify.com` |
| `VIVIDWALLS_TEST_CUSTOMERS` | Comma-separated customer names whose orders are tests. The store owner's name (from Shopify) is always added | `Test User` |
| `VIVIDWALLS_ALLOW_WRITES` | `1` lets confirmed writes through | off |
| `PICTOREM_ARTFLOW_KEY` | Pictorem ArtFlow API token. If unset, read from the macOS Keychain item `vividwalls-pictorem-api` | none |

## Tests

```bash
.venv/bin/python -m pytest -q tests
```
The tests use fake Shopify and Pictorem transports, so they need no token and make no network calls.
The GraphQL queries were checked against the live store (Admin API 2026-10).
