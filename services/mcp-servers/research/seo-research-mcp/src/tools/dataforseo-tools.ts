/**
 * DataForSEO MCP Tools
 * 
 * MCP tools for SEO research using DataForSEO APIs
 */

import { z } from 'zod';
import { dataForSEOClient } from '../clients/dataforseo.js';
import { logger } from '../server/logger.js';

/**
 * Keyword Research Tool Schema
 */
export const keywordResearchSchema = z.object({
  keywords: z.array(z.string()).min(1).max(100).describe('Keywords to research (1-100 keywords)'),
  location: z.string().optional().describe('Location for search volume data (e.g., "United States", "United Kingdom")'),
  language: z.string().optional().describe('Language for search volume data (e.g., "English", "Spanish")'),
  includeSerp: z.boolean().optional().default(true).describe('Include SERP information in results'),
  includeClickstream: z.boolean().optional().default(true).describe('Include clickstream data in results'),
  limit: z.number().min(1).max(1000).optional().default(100).describe('Maximum number of results to return'),
});

/**
 * Backlink Analysis Tool Schema
 */
export const backlinkAnalysisSchema = z.object({
  target: z.string().describe('Target domain or URL to analyze backlinks for'),
  mode: z.enum(['as_is', 'one_per_domain', 'one_per_anchor']).optional().default('as_is').describe('Analysis mode'),
  statusType: z.enum(['all', 'live', 'lost']).optional().default('live').describe('Backlink status type to analyze'),
  includeSubdomains: z.boolean().optional().default(false).describe('Include subdomains in analysis'),
  excludeInternal: z.boolean().optional().default(true).describe('Exclude internal backlinks'),
  limit: z.number().min(1).max(1000).optional().default(100).describe('Maximum number of backlinks to return'),
});

/**
 * SERP Analysis Tool Schema
 */
export const serpAnalysisSchema = z.object({
  keyword: z.string().describe('Keyword to analyze SERP for'),
  location: z.string().optional().describe('Location for SERP analysis (e.g., "United States", "United Kingdom")'),
  language: z.string().optional().describe('Language for SERP analysis (e.g., "English", "Spanish")'),
  device: z.enum(['desktop', 'mobile']).optional().default('desktop').describe('Device type for SERP analysis'),
  depth: z.number().min(1).max(100).optional().default(10).describe('Number of SERP results to analyze'),
});

/**
 * DataForSEO Connection Test Tool Schema
 */
export const connectionTestSchema = z.object({});

/**
 * Keyword Research Tool
 * Research keywords using DataForSEO Keywords Data API
 */
export async function keywordResearchTool(params: z.infer<typeof keywordResearchSchema>) {
  logger.mcpTool('keyword_research', 'Starting keyword research');
  
  try {
    const result = await dataForSEOClient.researchKeywords({
      keywords: params.keywords,
      location_name: params.location || undefined,
      language_name: params.language || undefined,
      include_serp_info: params.includeSerp,
      include_clickstream_data: params.includeClickstream,
      limit: params.limit,
    });

    if (result.success && result.data) {
      logger.mcpTool('keyword_research', 'Keyword research completed successfully');

      return {
        content: [
          {
            type: 'text' as const,
            text: `# Keyword Research Results\n\n` +
                  `**Keywords Analyzed:** ${params.keywords.join(', ')}\n` +
                  `**Location:** ${params.location || 'United States'}\n` +
                  `**Language:** ${params.language || 'English'}\n` +
                  `**Results Found:** ${result.data.length}\n\n` +
                  `## Keyword Data\n\n` +
                  result.data.map(keyword => 
                    `### ${keyword.keyword}\n` +
                    `- **Search Volume:** ${keyword.searchVolume?.toLocaleString() || 'N/A'}\n` +
                    `- **CPC:** $${keyword.cpc || 'N/A'}\n` +
                    `- **Competition:** ${keyword.competition || 'N/A'}\n` +
                    `- **Competition Level:** ${keyword.competitionLevel || 'N/A'}\n` +
                    (keyword.trends ? `- **Trends:** ${keyword.trends.length} months of data\n` : '') +
                    `\n`
                  ).join(''),
          },
        ],
      };
    } else {
      logger.mcpTool('keyword_research', 'Keyword research failed');
      
      return {
        content: [
          {
            type: 'text' as const,
            text: `# Keyword Research Failed\n\n` +
                  `**Error:** ${result.error?.message || 'Unknown error'}\n` +
                  `**Code:** ${result.error?.code || 'UNKNOWN'}\n\n` +
                  `Please check your DataForSEO API credentials and try again.`,
          },
        ],
        isError: true,
      };
    }
  } catch (error) {
    logger.error('Keyword research tool error:', error);
    
    return {
      content: [
        {
          type: 'text' as const,
          text: `# Keyword Research Error\n\n` +
                `An unexpected error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
}

/**
 * Backlink Analysis Tool
 * Analyze backlinks using DataForSEO Backlinks API
 */
export async function backlinkAnalysisTool(params: z.infer<typeof backlinkAnalysisSchema>) {
  logger.mcpTool('backlink_analysis', 'Starting backlink analysis');
  
  try {
    const result = await dataForSEOClient.analyzeBacklinks({
      target: params.target,
      mode: params.mode,
      backlinks_status_type: params.statusType,
      include_subdomains: params.includeSubdomains,
      exclude_internal_backlinks: params.excludeInternal,
      limit: params.limit,
    });

    if (result.success && result.data) {
      logger.mcpTool('backlink_analysis', 'Backlink analysis completed successfully');

      return {
        content: [
          {
            type: 'text' as const,
            text: `# Backlink Analysis Results\n\n` +
                  `**Target:** ${params.target}\n` +
                  `**Mode:** ${params.mode}\n` +
                  `**Status Type:** ${params.statusType}\n` +
                  `**Backlinks Found:** ${result.data.length}\n\n` +
                  `## Backlink Data\n\n` +
                  result.data.slice(0, 20).map((backlink, index) => 
                    `### ${index + 1}. ${backlink.domainFrom}\n` +
                    `- **From URL:** ${backlink.urlFrom}\n` +
                    `- **To URL:** ${backlink.urlTo}\n` +
                    `- **Anchor Text:** ${backlink.anchor || 'N/A'}\n` +
                    `- **Link Type:** ${backlink.linkType}\n` +
                    `- **Authority:** ${backlink.authority || 'N/A'}\n` +
                    `- **First Seen:** ${backlink.firstSeen || 'N/A'}\n` +
                    `- **Last Seen:** ${backlink.lastSeen || 'N/A'}\n\n`
                  ).join('') +
                  (result.data.length > 20 ? `\n*Showing first 20 of ${result.data.length} backlinks*\n` : ''),
          },
        ],
      };
    } else {
      logger.mcpTool('backlink_analysis', 'Backlink analysis failed');
      
      return {
        content: [
          {
            type: 'text' as const,
            text: `# Backlink Analysis Failed\n\n` +
                  `**Error:** ${result.error?.message || 'Unknown error'}\n` +
                  `**Code:** ${result.error?.code || 'UNKNOWN'}\n\n` +
                  `Please check your DataForSEO API credentials and try again.`,
          },
        ],
        isError: true,
      };
    }
  } catch (error) {
    logger.error('Backlink analysis tool error:', error);
    
    return {
      content: [
        {
          type: 'text' as const,
          text: `# Backlink Analysis Error\n\n` +
                `An unexpected error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
}

/**
 * SERP Analysis Tool
 * Analyze SERP using DataForSEO SERP API
 */
export async function serpAnalysisTool(params: z.infer<typeof serpAnalysisSchema>) {
  logger.mcpTool('serp_analysis', 'Starting SERP analysis');
  
  try {
    const result = await dataForSEOClient.analyzeSERP({
      keyword: params.keyword,
      location_name: params.location || undefined,
      language_name: params.language || undefined,
      device: params.device,
      depth: params.depth,
    });

    if (result.success && result.data) {
      logger.mcpTool('serp_analysis', 'SERP analysis completed successfully');

      return {
        content: [
          {
            type: 'text' as const,
            text: `# SERP Analysis Results\n\n` +
                  `**Keyword:** ${params.keyword}\n` +
                  `**Location:** ${params.location || 'United States'}\n` +
                  `**Language:** ${params.language || 'English'}\n` +
                  `**Device:** ${params.device}\n` +
                  `**Total Results:** ${result.data.totalResults?.toLocaleString() || 'N/A'}\n` +
                  `**Search Time:** ${result.data.searchTime || 'N/A'}s\n\n` +
                  `## SERP Results\n\n` +
                  result.data.results.map((item) => 
                    `### ${item.position}. ${item.title}\n` +
                    `- **URL:** ${item.url}\n` +
                    `- **Domain:** ${item.domain}\n` +
                    `- **Type:** ${item.type}\n` +
                    `- **Description:** ${item.description}\n\n`
                  ).join(''),
          },
        ],
      };
    } else {
      logger.mcpTool('serp_analysis', 'SERP analysis failed');
      
      return {
        content: [
          {
            type: 'text' as const,
            text: `# SERP Analysis Failed\n\n` +
                  `**Error:** ${result.error?.message || 'Unknown error'}\n` +
                  `**Code:** ${result.error?.code || 'UNKNOWN'}\n\n` +
                  `Please check your DataForSEO API credentials and try again.`,
          },
        ],
        isError: true,
      };
    }
  } catch (error) {
    logger.error('SERP analysis tool error:', error);
    
    return {
      content: [
        {
          type: 'text' as const,
          text: `# SERP Analysis Error\n\n` +
                `An unexpected error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
}

/**
 * DataForSEO Connection Test Tool
 * Test DataForSEO API connectivity and authentication
 */
export async function dataForSEOConnectionTestTool(_params: z.infer<typeof connectionTestSchema>) {
  logger.mcpTool('dataforseo_connection_test', 'Testing DataForSEO API connection');
  
  try {
    const result = await dataForSEOClient.testConnection();

    if (result.success && result.data) {
      logger.mcpTool('dataforseo_connection_test', 'Connection test successful');
      
      return {
        content: [
          {
            type: 'text' as const,
            text: `# DataForSEO Connection Test - SUCCESS ✅\n\n` +
                  `**Status:** ${result.data.status}\n` +
                  `**User:** ${result.data.user}\n` +
                  `**Timestamp:** ${result.metadata?.timestamp}\n\n` +
                  `DataForSEO API is properly configured and accessible.`,
          },
        ],
      };
    } else {
      logger.mcpTool('dataforseo_connection_test', 'Connection test failed');
      
      return {
        content: [
          {
            type: 'text' as const,
            text: `# DataForSEO Connection Test - FAILED ❌\n\n` +
                  `**Error:** ${result.error?.message || 'Unknown error'}\n` +
                  `**Code:** ${result.error?.code || 'UNKNOWN'}\n\n` +
                  `Please check your DataForSEO API credentials in the environment configuration.`,
          },
        ],
        isError: true,
      };
    }
  } catch (error) {
    logger.error('DataForSEO connection test error:', error);
    
    return {
      content: [
        {
          type: 'text' as const,
          text: `# DataForSEO Connection Test - ERROR ❌\n\n` +
                `An unexpected error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
} 