#!/usr/bin/env node

/**
 * SEO Research MCP Server
 * 
 * Multi-source SEO research MCP server that aggregates keyword research, 
 * backlink analysis, and SERP data from DataForSEO, Brave Search, 
 * Perplexity, Tavily, and SerpAPI for AI agents.
 * 
 * @author Neo-MCP Team
 * @version 0.1.0
 */

import { FastMCP } from 'fastmcp';
import { config } from './config/index.js';
import { logger } from './server/logger.js';
import { registerTools } from './tools/index.js';
import { registerResources } from './server/resources.js';

/**
 * Initialize and start the SEO Research MCP Server
 */
async function main(): Promise<void> {
  try {
    logger.info('🚀 Starting SEO Research MCP Server...');
    
    // Validate configuration
    await config.validate();
    logger.info('✅ Configuration validated successfully');
    
    // Create FastMCP server instance
    const server = new FastMCP({
      name: 'seo-research-mcp',
      version: '0.1.0',
    });
    
    // Register MCP tools
    await registerTools(server);
    logger.info('✅ MCP tools registered successfully');
    
    // Register MCP resources
    await registerResources(server);
    logger.info('✅ MCP resources registered successfully');
    
    // Start the server
    await server.start();
    logger.info('🎉 SEO Research MCP Server started successfully');
    
  } catch (error) {
    logger.error('❌ Failed to start SEO Research MCP Server:', error);
    process.exit(1);
  }
}

/**
 * Handle graceful shutdown
 */
process.on('SIGINT', () => {
  logger.info('🛑 Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('🛑 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('🚨 Unhandled Rejection at: ' + String(promise) + ', reason: ' + String(reason));
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('🚨 Uncaught Exception:', error);
  process.exit(1);
});

// Start the server
main().catch((error) => {
  logger.error('🚨 Fatal error during startup:', error);
  process.exit(1);
}); 