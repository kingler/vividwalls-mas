# vividwalls-ops: n8n workflows as agent functions

The retired n8n workflows rewritten as tested Python functions that Claude agents call as
MCP tools. The design rule: **the agent does the judgement work, the functions do the exact
work.** Analysing artwork, writing copy and choosing what to recommend are the agent's job.
Prices, order handling, saved data and search ranking go through these functions, which are
covered by tests.

## Which n8n workflow became what

| n8n workflow (removed Oct 2026) | Now |
|---|---|
| E-commerce Order Fulfillment, Orders Fulfillment Agent, Pictorem Agent | `fulfillment_queue`, `pictorem_order_sheet`, `record_pictorem_submission`, `mark_fulfilled`, plus the `fulfill-order` playbook |
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
| `record_pictorem_submission` | Yes: adds an order tag |
| `mark_fulfilled` | Yes: creates the fulfillment and emails the customer |
| `price_check` | No |
| `unprofiled_artworks` | No |
| `save_artwork_profile` | Yes: product metafields |
| `search_artworks` | No |
| `utm_link`, `pin_drafts` | No |

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
   cd integrations/vividwalls-ops-mcp && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   claude mcp add vividwalls-ops \
     -e SHOPIFY_ADMIN_TOKEN=... \
     -e VIVIDWALLS_TEST_CUSTOMERS="Test User,<your name>" \
     -e VIVIDWALLS_ALLOW_WRITES=1 -- \
     integrations/vividwalls-ops-mcp/.venv/bin/python integrations/vividwalls-ops-mcp/server.py
   ```
   Leave out `VIVIDWALLS_ALLOW_WRITES=1` wherever the server should only ever draft.

| Variable | Purpose | Default |
|---|---|---|
| `SHOPIFY_ADMIN_TOKEN` | Admin API token (required for store tools) | none |
| `SHOPIFY_STORE_DOMAIN` | Store admin domain | `vividwalls-2.myshopify.com` |
| `VIVIDWALLS_TEST_CUSTOMERS` | Comma-separated customer names whose orders are tests | `Test User` |
| `VIVIDWALLS_ALLOW_WRITES` | `1` lets confirmed writes through | off |

## Tests

```bash
.venv/bin/python -m pytest -q tests
```
The tests use a fake Shopify transport, so they need no token and make no network calls.
The GraphQL queries were checked against the live store (Admin API 2026-10).
