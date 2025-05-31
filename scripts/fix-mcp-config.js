#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the current mcp.json
const mcpConfigPath = path.join(__dirname, '..', '.cursor', 'mcp.json');
const mcpConfig = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf8'));

// Remove the hardcoded env section
delete mcpConfig.env;

// Update the mcpServers to reference environment variables properly
if (mcpConfig.mcpServers) {
    // Update task-master-ai to use process.env references
    if (mcpConfig.mcpServers['task-master-ai']) {
        mcpConfig.mcpServers['task-master-ai'].env = {
            "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
            "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
            "MODEL": "${TASKMASTER_MODEL:-claude-3-7-sonnet-20250219}",
            "PERPLEXITY_MODEL": "${PERPLEXITY_MODEL:-sonar-pro}",
            "MAX_TOKENS": "${TASKMASTER_MAX_TOKENS:-64000}",
            "TEMPERATURE": "${TASKMASTER_TEMPERATURE:-0.2}",
            "DEFAULT_SUBTASKS": "${DEFAULT_SUBTASKS:-5}",
            "DEFAULT_PRIORITY": "${DEFAULT_PRIORITY:-medium}"
        };
    }
}

// Update the n8n-mcp to use environment variables
const n8nServer = mcpConfig.mcpClient.servers.find(s => s.name === 'n8n-mcp');
if (n8nServer && n8nServer.env) {
    n8nServer.env = {
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "DEBUG": "${MCP_DEBUG:-false}"
    };
}

// Add environment variables for Shopify MCP (these should be set on the remote server)
const shopifyServer = mcpConfig.mcpClient.servers.find(s => s.name === 'shopify-mcp');
if (shopifyServer) {
    shopifyServer.env = {
        "SHOPIFY_STORE_URL": "${SHOPIFY_STORE_URL}",
        "SHOPIFY_ACCESS_TOKEN": "${SHOPIFY_ACCESS_TOKEN}",
        "SHOPIFY_API_VERSION": "${SHOPIFY_API_VERSION:-2024-01}"
    };
}

// Write the updated config
fs.writeFileSync(mcpConfigPath, JSON.stringify(mcpConfig, null, 4));

console.log('✅ Updated .cursor/mcp.json to use environment variables');

// Create a comprehensive .env.mcp.example file
const envExample = `# MCP Server Environment Variables
# Copy this file to .env.mcp and fill in your actual values

# Shopify MCP Configuration
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-shopify-access-token-here
SHOPIFY_API_VERSION=2024-01

# n8n MCP Configuration
N8N_API_URL=https://your-n8n-instance.com/api/v1
N8N_API_KEY=your-n8n-api-key-here

# Task Master AI Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
TASKMASTER_MODEL=claude-3-7-sonnet-20250219
PERPLEXITY_MODEL=sonar-pro
TASKMASTER_MAX_TOKENS=64000
TASKMASTER_TEMPERATURE=0.2
DEFAULT_SUBTASKS=5
DEFAULT_PRIORITY=medium

# Facebook Ads MCP Configuration
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token-here

# Digital Ocean SSH Configuration
DIGITALOCEAN_SSH_KEY_PATH=~/.ssh/digitalocean
DIGITALOCEAN_SERVER_IP=157.230.13.13
DIGITALOCEAN_SERVER_USER=root

# MCP Debug Settings
MCP_DEBUG=false
`;

fs.writeFileSync(path.join(__dirname, '..', '.env.mcp.example'), envExample);
console.log('✅ Created .env.mcp.example file');

// Update .gitignore to ensure .env.mcp is ignored
const gitignorePath = path.join(__dirname, '..', '.gitignore');
const gitignoreContent = fs.readFileSync(gitignorePath, 'utf8');

if (!gitignoreContent.includes('.env.mcp')) {
    fs.appendFileSync(gitignorePath, '\n# MCP environment file\n.env.mcp\n');
    console.log('✅ Updated .gitignore to include .env.mcp');
}

console.log('\n📝 Next steps:');
console.log('1. Copy .env.mcp.example to .env.mcp');
console.log('2. Fill in your actual values in .env.mcp');
console.log('3. The MCP configuration will now read from environment variables'); 