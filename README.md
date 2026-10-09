# VividWalls — Business Operating System

VividWalls sells original abstract and geometric wall art on Shopify (`vividwalls.co`),
printed on demand and shipped by Pictorem. This repo is the operating manual Claude uses
to run the store and its marketing.

| Path | What's there |
|---|---|
| `CLAUDE.md` | How Claude operates the business: systems, playbooks, guardrails |
| `business/` | Company profile, catalog and pricing rules, KPIs, the 90-day growth plan |
| `business/data/` | Product catalog exports and customer Q&A data (CSV) |
| `business/reference/` | Marketing data package, newsletter notes, color theory, product classification |
| `.claude/skills/` | Playbooks: `daily-brief`, `weekly-review`, `fulfill-order`, `list-artwork`, `optimize-listing`, `campaign`, `b2b-outreach` |
| `integrations/` | MCP servers for Pinterest, Meta ads and the WordPress blog (setup in `integrations/README.md`) |
| `ops/` | Dated reports and the B2B pipeline |

The earlier n8n / Docker / DigitalOcean multi-agent stack was removed in Oct 2026. It is
still in git history if you ever need it.
