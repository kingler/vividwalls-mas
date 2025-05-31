# Keywork Research Tool PRD

## **Product Requirements Document (PRD): Multi-Source SEO Research MCP Server**

### **1. Overview**

**Objective:**  
Develop a backend-only MCP (Model Context Protocol) server that aggregates and exposes advanced keyword research, web scraping, backlink analysis, and SERP data from multiple sources (Crawl4AI, DataForSEO, Brave Search, Perplexity, Tavily, SerpAPI) for AI agents to orchestrate content marketing strategies and campaign development.

---

### **2. Target Users**

- AI agents and LLM-powered marketing automation tools
- SEO/data engineers building agent workflows
- Marketing teams needing programmatic, multi-source SEO data

---

### **3. Integrated MCP Servers & Capabilities**

| MCP Server         | Main Capabilities                                                                                             |
|--------------------|--------------------------------------------------------------------------------------------------------------|
| **Crawl4AI MCP**   | Web crawling, keyword/content scraping, RAG (Retrieval Augmented Generation), custom extraction               |
| **DataForSEO MCP** | Keyword metrics, suggestions, trends, SERP, backlink analysis, domain analytics (via your DataForSEO account) |
| **Brave MCP**      | Web search, news, image/video search, local search (Brave API)                                               |
| **Perplexity MCP** | Web search with recency filters (Perplexity API)                                                             |
| **Tavily MCP**     | Real-time web search, domain-specific and news search, structured extraction (Tavily API)                    |
| **SerpAPI MCP**    | Google/Bing/Yahoo/News/Scholar/Trends/Finance/Maps/Images/YouTube search and data extraction                 |

---

### **4. Core Features**

#### **A. Keyword Research & Analysis**
- Multi-source keyword registration, lookup, and clustering
- Fetch keyword metrics: search volume, CPC, competition, trends (DataForSEO, SerpAPI, Tavily)
- SERP snapshot and competitor analysis (DataForSEO, SerpAPI)
- Semantic clustering/grouping (optionally via LLM or RAG from Crawl4AI)

#### **B. Backlink Analysis**
- Retrieve backlink profiles for domains/URLs (DataForSEO)
- Aggregate referring domains, anchor text, link type, authority
- Bulk backlink queries and analytics

#### **C. Web Scraping & Content Extraction**
- Crawl and extract content from arbitrary URLs (Crawl4AI MCP)
- Smart extraction: LLM-based or selector-based (Crawl4AI, Tavily)
- Store and index crawled content for RAG and further analysis

#### **D. Search Aggregation**
- Query web search results from Brave, Perplexity, Tavily, SerpAPI for real-time context, news, and competitor discovery
- Support for recency, domain filtering, and content extraction

#### **E. Unified API for AI Agents**
- Expose all tools via MCP-compliant endpoints
- Standardized JSON schemas and tool definitions for agent orchestration
- Session/context management for multi-step agent workflows

---

### **5. Example API/Tool Schema**

| Endpoint/Tool                  | Description                                         | Source MCP         |
|------------------------------- |-----------------------------------------------------|--------------------|
| `/keywords/register`           | Register/search keywords                            | DataForSEO, SerpAPI, Tavily |
| `/keywords/metrics`            | Keyword metrics and analytics                       | DataForSEO, SerpAPI, Tavily |
| `/keywords/cluster`            | Semantic keyword grouping                           | Crawl4AI, LLM      |
| `/backlinks/domain`            | Backlink profile for a domain                       | DataForSEO         |
| `/backlinks/url`               | Backlink profile for a URL                          | DataForSEO         |
| `/backlinks/stats`             | Aggregate backlink stats                            | DataForSEO         |
| `/scrape/url`                  | Scrape/extract content from a URL                   | Crawl4AI, Tavily   |
| `/search/web`                  | General web search                                  | Brave, Perplexity, Tavily, SerpAPI |
| `/search/news`                 | News search                                         | Brave, Tavily, SerpAPI |
| `/search/serp`                 | SERP snapshot for keyword/domain                    | DataForSEO, SerpAPI |
| `/analytics/competitors`       | Top competitors for a keyword/domain                | DataForSEO, SerpAPI, Tavily |
| `/analytics/historical`        | Historical keyword/domain metrics                   | DataForSEO         |

---

### **6. Technical Requirements**

- **MCP Protocol:** All endpoints/tools must conform to MCP standards for agent compatibility[1][3][5][12][13][15][21][22].
- **Authentication:** API keys/tokens for each integrated service (DataForSEO, Brave, Tavily, Perplexity, SerpAPI, Crawl4AI).
- **Dockerization:** Each MCP server (Crawl4AI, DataForSEO, etc.) runs as a Docker container or managed process for modularity and scaling[3][11][19].
- **Orchestration Layer:** A lightweight router/aggregator (could be a Python or Node.js service) dispatches requests to the appropriate MCP server(s) and aggregates responses.
- **Caching:** Cache common queries to minimize API costs and latency.
- **Logging & Monitoring:** Track API usage, errors, and performance.
- **Security:** Secure storage of all API credentials and access controls for agent clients.

---

### **7. Deployment & Operations**

- **Environment Variables:** Store all API keys and credentials securely.
- **Docker Compose:** Use a Compose file to spin up all required MCP servers and the aggregator.
- **Health Checks:** Ensure each MCP server is running and responsive.
- **Extensibility:** Allow for easy addition/removal of MCP servers as new data sources/tools become available.

---

### **8. Example Workflow for an AI Agent**

1. **Keyword Discovery:**  
   Agent calls `/keywords/register` (DataForSEO, SerpAPI, Tavily) to build a seed list.
2. **SERP & Competitor Analysis:**  
   Agent calls `/search/serp` and `/analytics/competitors` to identify ranking pages and competitors.
3. **Backlink Audit:**  
   Agent calls `/backlinks/domain` and `/backlinks/stats` for backlink opportunities and gaps.
4. **Content Gap & RAG:**  
   Agent uses `/scrape/url` (Crawl4AI, Tavily) to extract content for RAG and topic modeling.
5. **Market Trends:**  
   Agent calls `/search/news` and `/search/web` (Brave, Perplexity, Tavily, SerpAPI) for fresh market and trend data.

---

### **9. Setup & Integration References**

- **Crawl4AI MCP:**  
  - Docker setup and usage[3][4][6][11][16][19]
- **DataForSEO MCP:**  
  - Official server and open-source implementations[5][12][13][14][15][18][21][22]
- **Brave Search MCP:**  
  - Docker and npx installation, API key setup[7][17][20]
- **Perplexity MCP:**  
  - npx/Smithery install, API key[8]
- **Tavily MCP:**  
  - npx install, API key, config for Cursor/Claude[1][9]
- **SerpAPI MCP:**  
  - Python, Docker and stdio setup, API key[10]

---

### **10. Out of Scope for MVP**

- No frontend or UI
- No user management (API key only)
- No custom crawling outside of Crawl4AI MCP
- No manual data enrichment (all automated via MCP servers)

---

### **11. Success Criteria**

- AI agents can orchestrate multi-source keyword and backlink research via a unified MCP interface
- All major SEO research flows (keyword, SERP, backlink, content extraction, competitive analysis) are supported
- System is modular, extensible, and easily maintainable

---

**References:**  
- DataForSEO MCP Server setup and features[5][12][13][14][15][18][21][22]  
- Crawl4AI MCP Docker and RAG integration[3][4][6][11][16][19]  
- Brave, Perplexity, Tavily, SerpAPI MCP installation and usage[1][7][8][9][10][17][20]

---

**Summary:**  
Your MCP server will orchestrate DataForSEO, Crawl4AI, Brave, Perplexity, Tavily, and SerpAPI MCPs—providing AI agents with a unified, programmatic interface for advanced SEO research, keyword analytics, backlink intelligence, and content scraping, all via open MCP standards and Dockerized infrastructure.

Sources
[1] mcp https://docs.tavily.com/documentation/mcp
[2] serpapi-mc https://github.com/ilyazub/serpapi-mc
[3] coleam00/mcp-crawl4ai-rag: Web Crawling and RAG ... - GitHub https://github.com/coleam00/mcp-crawl4ai-rag
[4] Crawl4AI Web Scraper MCP Server - GitHub https://github.com/MaitreyaM/WEB-SCRAPING-MCP
[5] A comprehensive stdio MCP server for DataForSEO API - GitHub https://github.com/Skobyn/dataforseo-mcp-server
[6] Crawl4AI MCP server - Apify https://apify.com/janbuchar/crawl4ai/api/mcp
[7] mikechao/brave-search-mcp: An MCP Server implementation that ... https://github.com/mikechao/brave-search-mcp
[8] jsonallen/perplexity-mcp: A Model Context Protocol (MCP) server ... https://github.com/jsonallen/perplexity-mcp
[9] URDJMK/serpapi-mcp-server - GitHub https://github.com/URDJMK/serpapi-mcp-server
[10] Crawl4AI RAG MCP server for AI agents - Playbooks https://playbooks.com/mcp/coleam00-crawl4ai-rag
[11] Setting Up the Official DataForSEO MCP Server: Simple Guide https://dataforseo.com/help-center/setting-up-the-official-dataforseo-mcp-server-simple-guide
[12] Skobyn/mcp-dataforseo: Model Context Protocol server for ... - GitHub https://github.com/skobyn/mcp-dataforseo
[13] DataForSEO MCP Server - Glama https://glama.ai/mcp/servers/@Skobyn/mcp-dataforseo
[14] SEO Tools MCP Server | Glama https://glama.ai/mcp/servers/@Skobyn/dataforseo-mcp-server
[15] Unlocking the Power of AI with Crawl4AI MCP: A Step-by-Step Guide https://onedollarvps.com/blogs/how-to-set-up-and-use-crawl4ai-mcp
[16] w-jeon/mcp-brave-search - GitHub https://github.com/w-jeon/mcp-brave-search
[17] DataForSEO MCP Server - UBOS - UBOS.tech https://ubos.tech/mcp/dataforseo-mcp-server/
[18] BjornMelin/crawl4ai-mcp-server - GitHub https://github.com/BjornMelin/crawl4ai-mcp-server
[19] isaacgounton/Brave-Search-MCP-SSE - GitHub https://github.com/isaacgounton/brave-search-mcp-sse
[20] DataForSEO MCP server for AI agents - Playbooks https://playbooks.com/mcp/skobyn-dataforseo-seo
[21] DataForSEO MCP Server Launch: Connect APIs and AI Agents https://dataforseo.com/update/dataforseo-mcp-server-launch
[22] Crawl4AI Web Scraper and Crawler - UBOS.tech https://ubos.tech/mcp/crawl4ai-mcp/
[23] Crawl4AI: Web Scraping & Crawling for AI Assistants - MCP Market https://mcpmarket.com/server/crawl4ai-3
[24] Brave Search MCP Server - GitHub https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search
[25] arben-adm/brave-mcp-search - GitHub https://github.com/arben-adm/brave-mcp-search
[26] Brave Search - Claude MCP Servers https://www.claudemcp.com/servers/brave-search
[27] The EASIEST way to get SEO insights [DataForSEO MCP ... - YouTube https://www.youtube.com/watch?v=4C6dgxiQIpY
[28] DataForSEO MCP Server by skobyn - PulseMCP https://www.pulsemcp.com/servers/skobyn-dataforseo
