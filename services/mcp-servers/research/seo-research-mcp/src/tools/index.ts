/**
 * MCP Tools Registration
 * 
 * Central registration point for all MCP tools
 */

import { FastMCP } from 'fastmcp';
import { z } from 'zod';
import { config } from '../config/index.js';
import { logger } from '../server/logger.js';
import {
  keywordResearchSchema,
  backlinkAnalysisSchema,
  serpAnalysisSchema,
  connectionTestSchema,
  keywordResearchTool,
  backlinkAnalysisTool,
  serpAnalysisTool,
  dataForSEOConnectionTestTool,
} from './dataforseo-tools.js';

/**
 * Health Check Tool Schema
 */
const healthCheckSchema = z.object({});

/**
 * Health Check Tool
 * Reports server status and API configuration
 */
async function healthCheckTool(_params: z.infer<typeof healthCheckSchema>) {
  logger.mcpTool('health_check', 'Performing health check');
  
  try {
    // Get configured APIs list
    const configuredApis = config.getConfiguredApis();
    const allApis = ['dataForSEO', 'brave', 'perplexity', 'tavily', 'serpApi', 'openai'] as const;
    const unconfiguredApis = allApis.filter(api => !config.isApiConfigured(api));

    // Get API configurations for display
    const apiDetails = configuredApis.map(apiName => {
      const apiConfig = config.getApiConfig(apiName);
      return {
        name: apiName,
        baseUrl: apiConfig.baseUrl,
        configured: true,
      };
    });

    return {
      content: [
        {
          type: 'text' as const,
          text: `# SEO Research MCP Server - Health Check ✅\n\n` +
                `**Server Status:** Running\n` +
                `**Timestamp:** ${new Date().toISOString()}\n` +
                `**Environment:** ${process.env['NODE_ENV'] || 'development'}\n\n` +
                `## API Configuration Status\n\n` +
                `### ✅ Configured APIs (${configuredApis.length})\n` +
                apiDetails.map(api => 
                  `- **${api.name}**: ${api.baseUrl}\n`
                ).join('') +
                (unconfiguredApis.length > 0 ? 
                  `\n### ❌ Unconfigured APIs (${unconfiguredApis.length})\n` +
                  unconfiguredApis.map(name => `- **${name}**: Missing API key\n`).join('')
                : '') +
                `\n## Available Tools\n\n` +
                `- **keyword_research**: Research keywords using DataForSEO\n` +
                `- **backlink_analysis**: Analyze backlinks using DataForSEO\n` +
                `- **serp_analysis**: Analyze SERP results using DataForSEO\n` +
                `- **dataforseo_connection_test**: Test DataForSEO API connection\n` +
                `- **health_check**: Server health and configuration status\n\n` +
                `## Usage\n\n` +
                `Use the available tools to perform comprehensive SEO research. ` +
                `Make sure to configure the required API keys in your environment variables.`,
        },
      ],
    };
  } catch (error) {
    logger.error('Health check failed:', error);
    
    return {
      content: [
        {
          type: 'text' as const,
          text: `# SEO Research MCP Server - Health Check ❌\n\n` +
                `**Error:** ${error instanceof Error ? error.message : 'Unknown error'}\n` +
                `**Timestamp:** ${new Date().toISOString()}\n\n` +
                `The server encountered an error during health check.`,
        },
      ],
      isError: true,
    };
  }
}

/**
 * Register all MCP tools with the FastMCP server
 */
export function registerTools(server: FastMCP) {
  logger.info('🔧 Registering MCP tools...');

  // Health Check Tool
  server.addTool({
    name: 'health_check',
    description: 'Check server health and API configuration status',
    parameters: healthCheckSchema,
    execute: healthCheckTool,
  });

  // DataForSEO Tools
  server.addTool({
    name: 'keyword_research',
    description: 'Research keywords using DataForSEO Keywords Data API. Provides search volume, CPC, competition data, and trends.',
    parameters: keywordResearchSchema,
    execute: keywordResearchTool,
  });

  server.addTool({
    name: 'backlink_analysis',
    description: 'Analyze backlinks for a domain or URL using DataForSEO Backlinks API. Provides detailed backlink data including anchor text, authority, and link types.',
    parameters: backlinkAnalysisSchema,
    execute: backlinkAnalysisTool,
  });

  server.addTool({
    name: 'serp_analysis',
    description: 'Analyze SERP (Search Engine Results Page) for a keyword using DataForSEO SERP API. Provides ranking positions, URLs, titles, and descriptions.',
    parameters: serpAnalysisSchema,
    execute: serpAnalysisTool,
  });

  server.addTool({
    name: 'dataforseo_connection_test',
    description: 'Test DataForSEO API connectivity and authentication. Verifies that API credentials are working correctly.',
    parameters: connectionTestSchema,
    execute: dataForSEOConnectionTestTool,
  });

  logger.info('✅ All MCP tools registered successfully');
}

// TODO: Individual tool registration functions will be added here as tools are implemented
// Example structure:

/*
async function registerKeywordResearchTool(server: FastMCP): Promise<void> {
  server.addTool({
    name: 'keyword_research',
    description: 'Research keywords using multiple data sources including DataForSEO',
    parameters: z.object({
      keywords: z.array(z.string()).describe('List of keywords to research'),
      location: z.string().optional().default('United States').describe('Geographic location for search data'),
      language: z.string().optional().default('en').describe('Language code for search data'),
    }),
    execute: async (params: { keywords: string[]; location?: string; language?: string }) => {
      // Implementation will go here
    },
  });
}
*/ 