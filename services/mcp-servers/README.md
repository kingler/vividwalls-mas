# VividWalls MCP Servers Overview

This directory contains all Model Context Protocol (MCP) servers for VividWalls, organized by functional category. These servers provide AI-powered capabilities accessible through n8n workflows and external APIs.

## Architecture

All MCP servers follow a standardized architecture:
- **Port Allocation**: Each server has a dedicated port (8001-8050)
- **Internal Access**: Via `http://host.docker.internal:PORT` for n8n
- **External Access**: Via `https://n8n.vividwalls.blog/mcp/SERVICE-NAME`
- **Database**: PostgreSQL with pgvector extension on port 5433

## Server Categories

### 🎨 Creative Services (8001-8010)

#### Color Psychology MCP Server (Port 8001)
- **Location**: `/creative/color-psychology-mcp-server/`
- **Purpose**: Analyzes artwork images to extract color profiles and psychological attributes
- **Key Features**:
  - Color extraction using KMeans clustering
  - Psychological profiling based on color theory
  - NO HUMANS/ANIMALS rule enforcement
  - Integration with OpenAI Vision API
- **Status**: ✅ Deployed and Running

### 📊 Analytics Services (8011-8020)

#### KPI Dashboard MCP Server (Port 8002)
- **Location**: `/analytics/vividwalls-kpi-dashboard/`
- **Purpose**: Business metrics, analytics, and performance dashboards
- **Key Features**:
  - Sales analytics
  - Customer behavior tracking
  - Performance metrics
  - Real-time dashboards
- **Status**: 🚧 Ready for Implementation

### 🔍 Research Services (8021-8030)

#### Tavily Research MCP Server (Port 8003)
- **Location**: `/research/tavily-mcp/`
- **Purpose**: AI-powered web research and information gathering
- **Key Features**:
  - Advanced web search
  - Market research
  - Competitor analysis
  - Trend identification
- **Status**: 📦 Existing - Needs Configuration

#### SEO Research MCP Server (Port 8004)
- **Location**: `/research/seo-research-mcp/`
- **Purpose**: SEO analysis, keyword research, and optimization
- **Key Features**:
  - Keyword analysis
  - Competitor SEO tracking
  - Backlink analysis
  - Content optimization suggestions
- **Status**: 📦 Existing - Needs Configuration

### 📱 Social Media Services (8031-8040)

#### Facebook Ads MCP Server (Port 8005)
- **Location**: `/social-media/facebook-ads-mcp-server/`
- **Purpose**: Facebook advertising campaign management
- **Key Features**:
  - Campaign creation and management
  - Ad performance analytics
  - Audience targeting
  - Budget optimization
- **Status**: 📦 Existing - Needs Configuration

#### Pinterest MCP Server (Port 8006)
- **Location**: `/social-media/pinterest-mcp-server/`
- **Purpose**: Pinterest content and board management
- **Key Features**:
  - Pin creation and scheduling
  - Board management
  - Analytics and insights
  - Trend tracking
- **Status**: 📦 Existing - Needs Configuration

### 🏪 Core Business Services (8041-8050)

#### Shopify MCP Server (Port 8007)
- **Location**: `/core/shopify-mcp-server/`
- **Purpose**: E-commerce operations and Shopify store management
- **Key Features**:
  - Product management
  - Order processing
  - Inventory tracking
  - Customer management
- **Status**: 📦 Existing - Needs Configuration

#### WordPress MCP Server (Port 8008)
- **Location**: `/core/wordpress-mcp-server/`
- **Purpose**: Content management and blog operations
- **Key Features**:
  - Post and page management
  - Media library operations
  - User management
  - SEO optimization
- **Status**: 📦 Existing - Needs Configuration

#### Email Marketing MCP Server (Port 8009)
- **Location**: `/core/email-marketing-mcp-server/`
- **Purpose**: Email campaign management and automation
- **Key Features**:
  - Campaign creation
  - List management
  - Automation workflows
  - Analytics and reporting
- **Status**: 📦 Existing - Needs Configuration

## n8n Integration

All MCP servers are designed to work as AI Agent tools in n8n workflows:

### Quick Integration Steps:
1. Use the service registry at `/services/n8n/config/mcp-services.json`
2. Reference helper functions in `/services/n8n/mcp-agent-tools.js`
3. Access internally via `http://host.docker.internal:PORT`
4. Access externally via `https://n8n.vividwalls.blog/mcp/SERVICE`

### Example n8n Function Node:
```javascript
const { callMCPService } = require('./mcp-agent-tools.js');

// Analyze artwork colors
const colorAnalysis = await callMCPService(
  'color_psychology', 
  '/analyze', 
  'POST', 
  { image_path: '/path/to/artwork.jpg' }
);
```

## Deployment Template

Each MCP server follows the standard deployment template:
- See `/services/mcp-servers/deployment-template.md`
- Systemd service configuration
- Environment variables via .env
- Health monitoring endpoint
- Logging with Winston

## Development Guidelines

1. **Port Assignment**: Use assigned port ranges per category
2. **Health Endpoints**: All servers must expose `/health`
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Use Winston logger with appropriate levels
5. **Documentation**: Maintain README.md in each server directory
6. **Testing**: Include unit and integration tests
7. **Security**: Validate all inputs, use environment variables for secrets

## Monitoring

Monitor all services using the health check workflow:
```javascript
const { checkMCPHealth } = require('./mcp-agent-tools.js');
const healthStatus = await checkMCPHealth();
```

## Future Enhancements

- [ ] Implement remaining MCP servers
- [ ] Add authentication/authorization layer
- [ ] Create unified API gateway
- [ ] Implement rate limiting
- [ ] Add caching layer
- [ ] Create monitoring dashboard
- [ ] Implement service mesh for inter-service communication
- [ ] Add OpenTelemetry for distributed tracing

## Support

For issues or questions:
- Check individual server README files
- Review deployment logs: `journalctl -u SERVICE-NAME`
- Test health endpoints: `curl http://localhost:PORT/health`
- Check n8n workflow logs for integration issues 