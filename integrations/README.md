# Integrations

MCP servers for the marketing channels VividWalls uses that have no ready-made Claude
connector. Shopify, Gmail, Google Calendar/Drive, Notion and Higgsfield are connected as
claude.ai connectors, so they need nothing here.

| Server | Channel | Tools | Credentials (environment variable) |
|---|---|---|---|
| `pinterest-mcp-server` (Python) | Pinterest organic and promoted pins, boards, metrics | 9 | `PINTEREST_ACCESS_TOKEN` |
| `meta-ads-mcp-server` (Python) | Meta (Facebook and Instagram) ads: campaigns, ad sets, ads, insights | 49 | `FACEBOOK_ACCESS_TOKEN` |
| `wordpress-mcp-server` (TypeScript) | WordPress blog `vividwalls.blog` ("Art of Space"): posts, pages, media | 56 | `WORDPRESS_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_PASSWORD` (an application password) |

Never commit tokens. Set them in your shell or in the MCP client config on your own machine.

## Setup

```bash
# Python servers
cd integrations/pinterest-mcp-server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ../meta-ads-mcp-server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# WordPress server
cd ../wordpress-mcp-server && npm install && npm run build
```

The Python servers need MCP SDK 1.x (`mcp<2`, pinned in `requirements.txt`). SDK 2.x
renamed `FastMCP`, and the servers won't start with it.

## Register with Claude Code

From the repo root (`claude mcp add` stores the config locally, not in git):

```bash
claude mcp add pinterest -e PINTEREST_ACCESS_TOKEN=... -- \
  integrations/pinterest-mcp-server/.venv/bin/python integrations/pinterest-mcp-server/server.py
claude mcp add meta-ads -e FACEBOOK_ACCESS_TOKEN=... -- \
  integrations/meta-ads-mcp-server/.venv/bin/python integrations/meta-ads-mcp-server/server.py
claude mcp add wordpress -e WORDPRESS_URL=https://vividwalls.blog \
  -e WORDPRESS_USERNAME=... -e WORDPRESS_PASSWORD=... -- \
  node integrations/wordpress-mcp-server/build/index.js
```

Getting tokens:
- **Pinterest:** developers.pinterest.com → My apps → create an app → generate an access token with
  `boards:read/write`, `pins:read/write`, `ads:read` scopes.
- **Meta:** see `meta-ads-mcp-server/FACEBOOK_TOKEN_SETUP.md`. Use a long-lived system-user token
  with `ads_management` and `ads_read`.
- **WordPress:** Users → Profile → Application Passwords. Don't use your login password.

## Guardrails
Creating promoted pins, launching or changing Meta campaigns, or publishing blog posts all spend
money or publish publicly. Per `CLAUDE.md`, Claude drafts these and only executes after the owner
approves in the conversation. Reading metrics and creating drafts are always fine.
