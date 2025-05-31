/**
 * MCP Server Agent Tools for n8n
 * This file provides helper functions and tool definitions for integrating 
 * VividWalls MCP servers as AI Agent tools in n8n workflows
 */

// MCP Service Configuration
const MCP_SERVICES = {
  // Creative Services
  color_psychology: {
    url: "http://host.docker.internal:8001",
    name: "Color Psychology Analysis",
    description: "Analyze artwork colors and extract psychological profiles"
  },
  
  // Analytics Services
  kpi_dashboard: {
    url: "http://host.docker.internal:8002",
    name: "KPI Dashboard Analytics",
    description: "Access business metrics and analytics dashboards"
  },
  
  // Research Services
  tavily_research: {
    url: "http://host.docker.internal:8003",
    name: "Tavily AI Research",
    description: "AI-powered web research and information gathering"
  },
  seo_research: {
    url: "http://host.docker.internal:8004",
    name: "SEO Research Analysis",
    description: "SEO analysis, keyword research, and competitor tracking"
  },
  
  // Social Media Services
  facebook_ads: {
    url: "http://host.docker.internal:8005",
    name: "Facebook Ads Management",
    description: "Facebook advertising campaign management and analytics"
  },
  pinterest: {
    url: "http://host.docker.internal:8006",
    name: "Pinterest Management",
    description: "Pinterest content management and analytics"
  },
  
  // Core Business Services
  shopify: {
    url: "http://host.docker.internal:8007",
    name: "Shopify E-commerce",
    description: "Shopify store management and e-commerce operations"
  },
  wordpress: {
    url: "http://host.docker.internal:8008",
    name: "WordPress CMS",
    description: "WordPress content management and blog operations"
  },
  email_marketing: {
    url: "http://host.docker.internal:8009",
    name: "Email Marketing",
    description: "Email campaign management and subscriber analytics"
  }
};

/**
 * Generic MCP request handler with error handling and retries
 */
async function callMCPService(service, endpoint, method = 'POST', payload = {}) {
  const serviceConfig = MCP_SERVICES[service];
  if (!serviceConfig) {
    throw new Error(`Unknown MCP service: ${service}`);
  }
  
  const url = `${serviceConfig.url}${endpoint}`;
  const maxRetries = 3;
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await $http.request({
        method: method,
        url: url,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: method !== 'GET' ? payload : undefined,
        qs: method === 'GET' ? payload : undefined,
        timeout: 30000,
        returnFullResponse: true
      });
      
      if (response.statusCode === 200) {
        return response.body;
      } else {
        throw new Error(`MCP server returned ${response.statusCode}: ${response.statusMessage}`);
      }
    } catch (error) {
      lastError = error;
      
      // Try fallback IP if Docker host fails
      if (error.message.includes('host.docker.internal') && attempt < maxRetries) {
        url = url.replace('host.docker.internal', '172.17.0.1');
        continue;
      }
      
      // Wait before retry
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }
  
  throw lastError;
}

/**
 * AI Agent Tool Definitions
 * Copy these into your n8n AI Agent node custom tools
 */
const MCP_AGENT_TOOLS = {
  // Color Psychology Tool
  analyzeArtworkColors: {
    name: "analyzeArtworkColors",
    description: "Analyze artwork image to extract dominant colors and psychological profiles",
    parameters: {
      type: "object",
      properties: {
        image_path: {
          type: "string",
          description: "File path or URL to the artwork image"
        }
      },
      required: ["image_path"]
    },
    execute: async (parameters) => {
      return await callMCPService('color_psychology', '/analyze', 'POST', {
        image_path: parameters.image_path
      });
    }
  },
  
  // KPI Dashboard Tool
  getBusinessMetrics: {
    name: "getBusinessMetrics",
    description: "Retrieve business KPIs and analytics metrics",
    parameters: {
      type: "object",
      properties: {
        period: {
          type: "string",
          description: "Time period (e.g., 'last_30_days', 'last_quarter')"
        },
        metrics: {
          type: "array",
          items: { type: "string" },
          description: "List of metrics to retrieve (e.g., ['revenue', 'orders'])"
        }
      },
      required: ["period"]
    },
    execute: async (parameters) => {
      return await callMCPService('kpi_dashboard', '/metrics', 'GET', parameters);
    }
  },
  
  // Tavily Research Tool
  researchTopic: {
    name: "researchTopic",
    description: "Research any topic using AI-powered web search",
    parameters: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Research query or topic"
        },
        max_results: {
          type: "number",
          description: "Maximum number of results (default: 10)"
        }
      },
      required: ["query"]
    },
    execute: async (parameters) => {
      return await callMCPService('tavily_research', '/research', 'POST', parameters);
    }
  },
  
  // SEO Research Tool
  analyzeSEO: {
    name: "analyzeSEO",
    description: "Perform SEO analysis and keyword research",
    parameters: {
      type: "object",
      properties: {
        target: {
          type: "string",
          description: "URL or keyword to analyze"
        },
        analysis_type: {
          type: "string",
          enum: ["keywords", "competitors", "backlinks"],
          description: "Type of SEO analysis"
        }
      },
      required: ["target", "analysis_type"]
    },
    execute: async (parameters) => {
      return await callMCPService('seo_research', '/analysis', 'POST', parameters);
    }
  },
  
  // Shopify Tool
  manageShopifyStore: {
    name: "manageShopifyStore",
    description: "Manage Shopify products, orders, and inventory",
    parameters: {
      type: "object",
      properties: {
        action: {
          type: "string",
          enum: ["get_products", "update_inventory", "get_orders"],
          description: "Shopify action to perform"
        },
        data: {
          type: "object",
          description: "Action-specific data"
        }
      },
      required: ["action"]
    },
    execute: async (parameters) => {
      const endpoints = {
        get_products: '/products',
        update_inventory: '/inventory',
        get_orders: '/orders'
      };
      return await callMCPService('shopify', endpoints[parameters.action], 
        parameters.action === 'get_products' ? 'GET' : 'POST', 
        parameters.data || {}
      );
    }
  }
};

/**
 * Health Check Function
 * Use this to monitor all MCP services
 */
async function checkMCPHealth() {
  const results = [];
  
  for (const [service, config] of Object.entries(MCP_SERVICES)) {
    try {
      const startTime = Date.now();
      await callMCPService(service, '/health', 'GET');
      
      results.push({
        service: service,
        name: config.name,
        status: 'healthy',
        response_time: Date.now() - startTime
      });
    } catch (error) {
      results.push({
        service: service,
        name: config.name,
        status: 'unhealthy',
        error: error.message
      });
    }
  }
  
  return results;
}

// Export for use in n8n Function nodes
return {
  MCP_SERVICES,
  callMCPService,
  MCP_AGENT_TOOLS,
  checkMCPHealth
}; 