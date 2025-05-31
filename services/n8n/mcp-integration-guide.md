# VividWalls MCP Server Integration Guide for n8n

This guide explains how to integrate all VividWalls MCP servers as AI Agent tools in n8n workflows.

## Available MCP Servers

### Creative Services (Ports 8001-8010)
- **Color Psychology MCP** (8001): Artwork color analysis and psychological profiling

### Analytics Services (Ports 8011-8020)
- **KPI Dashboard MCP** (8002): Business metrics and analytics dashboards

### Research Services (Ports 8021-8030)
- **Tavily Research MCP** (8003): AI-powered web research
- **SEO Research MCP** (8004): SEO analysis and keyword research

### Social Media Services (Ports 8031-8040)
- **Facebook Ads MCP** (8005): Facebook advertising management
- **Pinterest MCP** (8006): Pinterest content management

### Core Business Services (Ports 8041-8050)
- **Shopify MCP** (8007): E-commerce operations
- **WordPress MCP** (8008): Content management
- **Email Marketing MCP** (8009): Email campaign management

## Integration Methods

### Method 1: Function Node with Dynamic Service Discovery

```javascript
// Load MCP service configuration
const serviceConfig = {
  "color_psychology": "http://host.docker.internal:8001",
  "kpi_dashboard": "http://host.docker.internal:8002",
  "tavily_research": "http://host.docker.internal:8003",
  "seo_research": "http://host.docker.internal:8004",
  "facebook_ads": "http://host.docker.internal:8005",
  "pinterest": "http://host.docker.internal:8006",
  "shopify": "http://host.docker.internal:8007",
  "wordpress": "http://host.docker.internal:8008",
  "email_marketing": "http://host.docker.internal:8009"
};

// Get the service type from input
const serviceType = items[0].json.service_type || 'color_psychology';
const endpoint = items[0].json.endpoint || '/health';
const method = items[0].json.method || 'POST';
const payload = items[0].json.payload || {};

// Build the request
const mcpUrl = serviceConfig[serviceType];
if (!mcpUrl) {
  throw new Error(`Unknown MCP service: ${serviceType}`);
}

return {
  url: `${mcpUrl}${endpoint}`,
  method: method,
  headers: {
    'Content-Type': 'application/json'
  },
  body: payload
};
```

### Method 2: AI Agent Tool Integration

In n8n AI Agent nodes, configure each MCP server as a custom tool:

#### Example: Color Psychology Analysis Tool
```javascript
{
  "name": "analyzeArtworkColors",
  "description": "Analyze artwork colors and extract psychological profiles",
  "parameters": {
    "type": "object",
    "properties": {
      "image_path": {
        "type": "string",
        "description": "Path to the artwork image"
      }
    },
    "required": ["image_path"]
  },
  "execute": async (parameters) => {
    const response = await $http.request({
      method: 'POST',
      url: 'http://host.docker.internal:8001/analyze',
      body: {
        image_path: parameters.image_path
      }
    });
    return response.data;
  }
}
```

### Method 3: HTTP Request Node

Direct configuration in HTTP Request node:
- **URL**: `http://host.docker.internal:800X/endpoint`
- **Method**: POST/GET as required
- **Headers**: `Content-Type: application/json`
- **Body**: JSON payload

## Service-Specific Examples

### 1. Color Psychology MCP
```javascript
// Analyze artwork
{
  "service_type": "color_psychology",
  "endpoint": "/analyze",
  "method": "POST",
  "payload": {
    "image_path": "/path/to/artwork.jpg"
  }
}
```

### 2. KPI Dashboard MCP
```javascript
// Get sales metrics
{
  "service_type": "kpi_dashboard",
  "endpoint": "/metrics",
  "method": "GET",
  "payload": {
    "period": "last_30_days",
    "metrics": ["revenue", "orders", "conversion_rate"]
  }
}
```

### 3. Tavily Research MCP
```javascript
// Research market trends
{
  "service_type": "tavily_research",
  "endpoint": "/research",
  "method": "POST",
  "payload": {
    "query": "wall art market trends 2024",
    "max_results": 10
  }
}
```

### 4. Shopify MCP
```javascript
// Update product inventory
{
  "service_type": "shopify",
  "endpoint": "/inventory",
  "method": "PUT",
  "payload": {
    "product_id": "123456",
    "quantity": 50
  }
}
```

### 5. Email Marketing MCP
```javascript
// Send campaign
{
  "service_type": "email_marketing",
  "endpoint": "/campaigns",
  "method": "POST",
  "payload": {
    "list_id": "vip_customers",
    "template": "new_collection",
    "subject": "New Abstract Art Collection"
  }
}
```

## Error Handling

```javascript
try {
  const response = await $http.request({
    method: 'POST',
    url: mcpUrl,
    body: payload,
    timeout: 30000, // 30 seconds
    retry: {
      limit: 3,
      delay: 1000
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`MCP server error: ${response.statusText}`);
  }
  
  return response.data;
} catch (error) {
  // Fallback to direct IP if Docker host fails
  if (error.message.includes('host.docker.internal')) {
    const fallbackUrl = mcpUrl.replace('host.docker.internal', '172.17.0.1');
    return await $http.request({
      method: 'POST',
      url: fallbackUrl,
      body: payload
    });
  }
  throw error;
}
```

## Health Monitoring

Create a workflow to monitor all MCP servers:

```javascript
const services = Object.keys(serviceConfig);
const healthChecks = [];

for (const service of services) {
  try {
    const response = await $http.request({
      method: 'GET',
      url: `${serviceConfig[service]}/health`,
      timeout: 5000
    });
    
    healthChecks.push({
      service: service,
      status: 'healthy',
      response_time: response.timings.total
    });
  } catch (error) {
    healthChecks.push({
      service: service,
      status: 'unhealthy',
      error: error.message
    });
  }
}

return healthChecks;
```

## External Access via Caddy

All MCP servers are also accessible externally via:
- Base URL: `https://n8n.vividwalls.blog/mcp/`
- Service URLs:
  - Color Psychology: `https://n8n.vividwalls.blog/mcp/color-psychology`
  - KPI Dashboard: `https://n8n.vividwalls.blog/mcp/kpi-dashboard`
  - Tavily Research: `https://n8n.vividwalls.blog/mcp/tavily-research`
  - etc.

## Best Practices

1. **Use Service Discovery**: Always use the service registry for dynamic URL resolution
2. **Implement Retries**: Add retry logic for network failures
3. **Monitor Health**: Set up regular health checks for all services
4. **Cache Responses**: Cache frequently accessed data to reduce load
5. **Log Errors**: Implement comprehensive error logging for debugging
6. **Use Timeouts**: Set appropriate timeouts for each service type
7. **Validate Inputs**: Always validate inputs before sending to MCP servers 