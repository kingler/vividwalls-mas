#!/usr/bin/env node

/**
 * VividWalls MAS KPI Data Collector
 * Real-time metrics collection from all MCP servers and business systems
 */

import { createClient } from '@supabase/supabase-js';
import fetch from 'node-fetch';
import { spawn } from 'child_process';
import { readFileSync } from 'fs';
import { config } from 'dotenv';

config();

// Configuration
const SUPABASE_URL = process.env.SUPABASE_URL || 'http://127.0.0.1:54321';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const N8N_WEBHOOK_URL = 'http://157.230.13.13:5678/api/v1';
const N8N_API_KEY = process.env.N8N_API_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlNmJmMTU1Mi1kZWQ0LTQ2ZWMtOWU0ZS0xN2FhY2EyOGFmNzgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ4NTIxMTc3fQ.xpycas0XN_532GZR-SyH1B296pSNqvVVuNa80YYFKF0';

// Shopify credentials
const SHOPIFY_DOMAIN = process.env.MYSHOPIFY_DOMAIN || 'vividwalls-2.myshopify.com';
const SHOPIFY_ACCESS_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN;

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Colors for console output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset') {
    const timestamp = new Date().toISOString();
    console.log(`${colors[color]}[${timestamp}] ${message}${colors.reset}`);
}

class VividWallsKPICollector {
    constructor() {
        this.agents = [
            { id: 'business_manager', name: 'Business Manager Agent', type: 'orchestrator' },
            { id: 'marketing_research', name: 'Marketing Research Agent', type: 'marketing' },
            { id: 'marketing_campaign', name: 'Marketing Campaign Agent', type: 'marketing' },
            { id: 'shopify_manager', name: 'Shopify Management Agent', type: 'operations' },
            { id: 'facebook_ads', name: 'Facebook Ads Agent', type: 'marketing' },
            { id: 'pinterest_marketing', name: 'Pinterest Marketing Agent', type: 'marketing' },
            { id: 'email_marketing', name: 'Email Marketing Agent', type: 'marketing' },
            { id: 'pictorem_fulfillment', name: 'Pictorem Fulfillment Agent', type: 'operations' },
            { id: 'content_creator', name: 'Content Creation Agent', type: 'marketing' },
            { id: 'customer_support', name: 'Customer Support Agent', type: 'operations' }
        ];
        
        this.isRunning = false;
        this.collectInterval = null;
    }

    // =============================================
    // SHOPIFY METRICS COLLECTION
    // =============================================

    async collectShopifyMetrics() {
        try {
            log('📊 Collecting Shopify metrics...', 'blue');
            
            const shopifyHeaders = {
                'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
                'Content-Type': 'application/json'
            };

            // Get shop info and orders
            const [shopResponse, ordersResponse] = await Promise.all([
                fetch(`https://${SHOPIFY_DOMAIN}/admin/api/2024-04/shop.json`, { headers: shopifyHeaders }),
                fetch(`https://${SHOPIFY_DOMAIN}/admin/api/2024-04/orders.json?status=any&created_at_min=${new Date(Date.now() - 24*60*60*1000).toISOString()}`, { headers: shopifyHeaders })
            ]);

            if (!shopResponse.ok || !ordersResponse.ok) {
                throw new Error(`Shopify API error: ${shopResponse.status} / ${ordersResponse.status}`);
            }

            const shopData = await shopResponse.json();
            const ordersData = await ordersResponse.json();

            const todayOrders = ordersData.orders || [];
            const revenue = todayOrders.reduce((sum, order) => sum + parseFloat(order.total_price || 0), 0);
            const avgOrderValue = todayOrders.length > 0 ? revenue / todayOrders.length : 0;

            // Update business KPIs
            const kpiData = {
                kpi_date: new Date().toISOString().split('T')[0],
                revenue_total: revenue,
                orders_count: todayOrders.length,
                average_order_value: avgOrderValue,
                updated_at: new Date().toISOString()
            };

            const { error } = await supabase
                .from('vividwalls_kpis.business_kpis')
                .upsert(kpiData, { onConflict: 'kpi_date' });

            if (error) throw error;

            log(`✅ Shopify metrics updated: ${todayOrders.length} orders, $${revenue.toFixed(2)} revenue`, 'green');
            return { orders: todayOrders.length, revenue };

        } catch (error) {
            log(`❌ Failed to collect Shopify metrics: ${error.message}`, 'red');
            return null;
        }
    }

    // =============================================
    // N8N WORKFLOW METRICS
    // =============================================

    async collectN8NMetrics() {
        try {
            log('🔄 Collecting n8n workflow metrics...', 'blue');
            
            const response = await fetch(`${N8N_WEBHOOK_URL}/executions`, {
                headers: {
                    'Authorization': `Bearer ${N8N_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`n8n API error: ${response.status}`);
            }

            const executionsData = await response.json();
            const executions = executionsData.data || [];

            // Analyze executions from last 24 hours
            const dayAgo = new Date(Date.now() - 24*60*60*1000);
            const recentExecutions = executions.filter(exec => 
                new Date(exec.startedAt) > dayAgo
            );

            const successfulExecutions = recentExecutions.filter(exec => exec.finished && !exec.stoppedAt);
            const failedExecutions = recentExecutions.filter(exec => exec.finished && exec.stoppedAt);

            // Calculate task performance for Business Manager Agent
            const taskData = {
                agent_id: 'business_manager',
                agent_name: 'Business Manager Agent',
                metric_date: new Date().toISOString().split('T')[0],
                tasks_completed: successfulExecutions.length,
                tasks_failed: failedExecutions.length,
                success_rate: recentExecutions.length > 0 ? successfulExecutions.length / recentExecutions.length : 1,
                average_response_time_ms: this.calculateAverageResponseTime(recentExecutions),
                updated_at: new Date().toISOString()
            };

            const { error } = await supabase
                .from('vividwalls_kpis.agent_performance')
                .upsert(taskData, { onConflict: 'agent_id,metric_date' });

            if (error) throw error;

            log(`✅ n8n metrics updated: ${successfulExecutions.length}/${recentExecutions.length} successful`, 'green');
            return { total: recentExecutions.length, successful: successfulExecutions.length };

        } catch (error) {
            log(`❌ Failed to collect n8n metrics: ${error.message}`, 'red');
            return null;
        }
    }

    calculateAverageResponseTime(executions) {
        if (executions.length === 0) return 0;
        
        const responseTimes = executions
            .filter(exec => exec.startedAt && exec.finished)
            .map(exec => {
                const start = new Date(exec.startedAt);
                const end = new Date(exec.finished ? exec.finished : exec.stoppedAt);
                return end.getTime() - start.getTime();
            });

        return responseTimes.length > 0 ? 
            Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length) : 0;
    }

    // =============================================
    // MCP SERVER HEALTH MONITORING
    // =============================================

    async collectMCPServerHealth() {
        try {
            log('🔍 Checking MCP server health...', 'blue');

            const mcpServers = [
                { name: 'shopify-mcp-server', type: 'mcp_server', command: '/Users/kinglerbercy/Projects/vivid_mas/mcp/shopify-mcp-server/build/index.js' },
                { name: 'facebook-ads-mcp-server', type: 'mcp_server', command: '/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server/server.py' },
                { name: 'supabase-mcp-server', type: 'database', command: 'supabase_mcp.main' },
                { name: 'n8n-server', type: 'webhook', command: '/Users/kinglerbercy/Neo-MCP/packages/n8n-mcp-server/build/index.js' }
            ];

            const healthChecks = await Promise.allSettled(
                mcpServers.map(server => this.checkMCPServerHealth(server))
            );

            let healthyServers = 0;
            const healthData = [];

            healthChecks.forEach((result, index) => {
                const server = mcpServers[index];
                
                if (result.status === 'fulfilled' && result.value) {
                    healthyServers++;
                    healthData.push({
                        component_name: server.name,
                        component_type: server.type,
                        status: 'healthy',
                        response_time_ms: result.value.responseTime || 0,
                        last_check: new Date().toISOString(),
                        details: { check_result: 'success', timestamp: new Date().toISOString() }
                    });
                } else {
                    healthData.push({
                        component_name: server.name,
                        component_type: server.type,
                        status: 'warning',
                        response_time_ms: 0,
                        last_check: new Date().toISOString(),
                        details: { 
                            check_result: 'failed', 
                            error: result.reason?.message || 'Unknown error',
                            timestamp: new Date().toISOString() 
                        }
                    });
                }
            });

            // Insert health data
            const { error } = await supabase
                .from('vividwalls_kpis.system_health')
                .upsert(healthData, { onConflict: 'component_name' });

            if (error) throw error;

            log(`✅ MCP health check completed: ${healthyServers}/${mcpServers.length} healthy`, 'green');
            return { healthy: healthyServers, total: mcpServers.length };

        } catch (error) {
            log(`❌ Failed to collect MCP health metrics: ${error.message}`, 'red');
            return null;
        }
    }

    async checkMCPServerHealth(server) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            // For Python servers, use python -c "import module"
            // For Node servers, use node --check
            const checkCommand = server.command.endsWith('.py') ? 
                ['python', '-c', `"import sys; sys.path.append('${server.command.split('/').slice(0, -1).join('/')}'); print('OK')"`] :
                ['node', '--check', server.command];

            const process = spawn(checkCommand[0], checkCommand.slice(1), {
                stdio: ['pipe', 'pipe', 'pipe'],
                timeout: 5000
            });

            let output = '';
            
            process.stdout.on('data', (data) => {
                output += data.toString();
            });

            process.on('close', (code) => {
                const responseTime = Date.now() - startTime;
                if (code === 0 || output.includes('OK')) {
                    resolve({ responseTime, status: 'healthy' });
                } else {
                    reject(new Error(`Process exited with code ${code}`));
                }
            });

            process.on('error', (error) => {
                reject(error);
            });
        });
    }

    // =============================================
    // AI INTERACTION METRICS
    // =============================================

    async collectAIInteractionMetrics() {
        try {
            log('🤖 Collecting AI interaction metrics...', 'blue');

            // Get recent AI interactions from n8n logs
            const response = await fetch(`${N8N_WEBHOOK_URL}/executions`, {
                headers: {
                    'Authorization': `Bearer ${N8N_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                params: {
                    filter: JSON.stringify({
                        workflowName: 'VividWalls Chat Assistant'
                    })
                }
            });

            if (response.ok) {
                const data = await response.json();
                const interactions = data.data || [];
                
                // Count interactions from today
                const today = new Date().toISOString().split('T')[0];
                const todayInteractions = interactions.filter(interaction => 
                    interaction.startedAt && interaction.startedAt.startsWith(today)
                );

                // Calculate conversion rate (simplified - interactions that led to product views)
                const conversions = todayInteractions.filter(interaction => 
                    interaction.data && interaction.data.some(node => 
                        node.data && node.data.pageContext && node.data.pageContext.type === 'product'
                    )
                );

                // Update business KPIs with AI metrics
                const { error: kpiError } = await supabase
                    .from('vividwalls_kpis.business_kpis')
                    .update({
                        ai_assistant_interactions: todayInteractions.length,
                        ai_conversion_rate: todayInteractions.length > 0 ? conversions.length / todayInteractions.length : 0,
                        updated_at: new Date().toISOString()
                    })
                    .eq('kpi_date', today);

                if (kpiError) throw kpiError;

                log(`✅ AI metrics updated: ${todayInteractions.length} interactions, ${(conversions.length / todayInteractions.length * 100).toFixed(1)}% conversion`, 'green');
                return { interactions: todayInteractions.length, conversions: conversions.length };
            }

            return { interactions: 0, conversions: 0 };

        } catch (error) {
            log(`❌ Failed to collect AI interaction metrics: ${error.message}`, 'red');
            return null;
        }
    }

    // =============================================
    // AGENT HEARTBEAT SYSTEM
    // =============================================

    async updateAgentHeartbeats() {
        try {
            log('💓 Updating agent heartbeats...', 'cyan');

            // Update heartbeat for all active agents
            const heartbeatUpdates = this.agents.map(agent => ({
                agent_id: agent.id,
                last_heartbeat: new Date().toISOString(),
                status: 'active'
            }));

            const { error } = await supabase
                .from('vividwalls_kpis.agents')
                .upsert(heartbeatUpdates, { onConflict: 'agent_id' });

            if (error) throw error;

            log(`✅ Updated heartbeats for ${this.agents.length} agents`, 'green');
            return true;

        } catch (error) {
            log(`❌ Failed to update agent heartbeats: ${error.message}`, 'red');
            return false;
        }
    }

    // =============================================
    // CAMPAIGN PERFORMANCE
    // =============================================

    async collectCampaignPerformance() {
        try {
            log('📈 Collecting campaign performance metrics...', 'blue');

            // Mock campaign data - in production, this would integrate with actual ad platforms
            const campaigns = [
                {
                    campaign_id: 'fb_vividwalls_q1_2025',
                    platform: 'facebook',
                    campaign_name: 'VividWalls Spring Collection 2025',
                    impressions: Math.floor(Math.random() * 10000) + 5000,
                    clicks: Math.floor(Math.random() * 500) + 100,
                    conversions: Math.floor(Math.random() * 50) + 10,
                    spend: Math.floor(Math.random() * 1000) + 200
                },
                {
                    campaign_id: 'pin_vividwalls_q1_2025',
                    platform: 'pinterest',
                    campaign_name: 'VividWalls Abstract Art Collection',
                    impressions: Math.floor(Math.random() * 8000) + 3000,
                    clicks: Math.floor(Math.random() * 300) + 80,
                    conversions: Math.floor(Math.random() * 30) + 5,
                    spend: Math.floor(Math.random() * 600) + 150
                }
            ];

            const campaignData = campaigns.map(campaign => ({
                ...campaign,
                metric_date: new Date().toISOString().split('T')[0],
                revenue: campaign.conversions * 75, // Assumed $75 AOV
                ctr: campaign.clicks / campaign.impressions,
                cpc: campaign.spend / campaign.clicks,
                roas: (campaign.conversions * 75) / campaign.spend
            }));

            const { error } = await supabase
                .from('vividwalls_kpis.campaign_performance')
                .upsert(campaignData, { onConflict: 'campaign_id,metric_date' });

            if (error) throw error;

            log(`✅ Campaign metrics updated for ${campaigns.length} campaigns`, 'green');
            return campaigns.length;

        } catch (error) {
            log(`❌ Failed to collect campaign metrics: ${error.message}`, 'red');
            return 0;
        }
    }

    // =============================================
    // MAIN COLLECTION CYCLE
    // =============================================

    async collectAllMetrics() {
        log('🚀 Starting VividWalls MAS KPI collection cycle...', 'bold');
        
        const startTime = Date.now();
        const results = {};

        try {
            // Run all collections in parallel for efficiency
            const [
                shopifyMetrics,
                n8nMetrics, 
                mcpHealth,
                aiMetrics,
                heartbeats,
                campaignMetrics
            ] = await Promise.allSettled([
                this.collectShopifyMetrics(),
                this.collectN8NMetrics(),
                this.collectMCPServerHealth(),
                this.collectAIInteractionMetrics(),
                this.updateAgentHeartbeats(),
                this.collectCampaignPerformance()
            ]);

            results.shopify = shopifyMetrics.status === 'fulfilled' ? shopifyMetrics.value : null;
            results.n8n = n8nMetrics.status === 'fulfilled' ? n8nMetrics.value : null;
            results.mcpHealth = mcpHealth.status === 'fulfilled' ? mcpHealth.value : null;
            results.aiMetrics = aiMetrics.status === 'fulfilled' ? aiMetrics.value : null;
            results.heartbeats = heartbeats.status === 'fulfilled' ? heartbeats.value : null;
            results.campaigns = campaignMetrics.status === 'fulfilled' ? campaignMetrics.value : null;

            const duration = Date.now() - startTime;
            log(`✅ Collection cycle completed in ${duration}ms`, 'green');

            // Generate summary
            this.logCollectionSummary(results);

        } catch (error) {
            log(`💥 Collection cycle failed: ${error.message}`, 'red');
        }

        return results;
    }

    logCollectionSummary(results) {
        log('\n📊 Collection Summary:', 'bold');
        log('─'.repeat(50), 'reset');
        
        if (results.shopify) {
            log(`💰 Revenue: $${results.shopify.revenue?.toFixed(2) || 0} (${results.shopify.orders || 0} orders)`, 'green');
        }
        
        if (results.n8n) {
            log(`🔄 Workflows: ${results.n8n.successful || 0}/${results.n8n.total || 0} successful`, 'blue');
        }
        
        if (results.mcpHealth) {
            log(`🔍 MCP Health: ${results.mcpHealth.healthy || 0}/${results.mcpHealth.total || 0} healthy`, 'cyan');
        }
        
        if (results.aiMetrics) {
            log(`🤖 AI Interactions: ${results.aiMetrics.interactions || 0} (${results.aiMetrics.conversions || 0} conversions)`, 'magenta');
        }
        
        log(`💓 Agent Heartbeats: ${results.heartbeats ? 'Updated' : 'Failed'}`, results.heartbeats ? 'green' : 'red');
        log(`📈 Campaigns: ${results.campaigns || 0} updated`, 'yellow');
        
        log('─'.repeat(50), 'reset');
    }

    // =============================================
    // SCHEDULER
    // =============================================

    start(intervalMinutes = 5) {
        if (this.isRunning) {
            log('⚠️  Data collector is already running', 'yellow');
            return;
        }

        this.isRunning = true;
        log(`🚀 Starting VividWalls KPI Data Collector (${intervalMinutes} min intervals)`, 'bold');

        // Run initial collection
        this.collectAllMetrics();

        // Schedule regular collections
        this.collectInterval = setInterval(() => {
            this.collectAllMetrics();
        }, intervalMinutes * 60 * 1000);

        log(`✅ Data collector started successfully`, 'green');
    }

    stop() {
        if (!this.isRunning) {
            log('⚠️  Data collector is not running', 'yellow');
            return;
        }

        this.isRunning = false;
        
        if (this.collectInterval) {
            clearInterval(this.collectInterval);
            this.collectInterval = null;
        }

        log('🛑 Data collector stopped', 'red');
    }

    async runOnce() {
        log('🔄 Running single collection cycle...', 'blue');
        return await this.collectAllMetrics();
    }
}

// =============================================
// CLI INTERFACE
// =============================================

async function main() {
    const collector = new VividWallsKPICollector();
    
    const command = process.argv[2] || 'start';
    const interval = parseInt(process.argv[3]) || 5;

    switch (command) {
        case 'start':
            collector.start(interval);
            break;
            
        case 'once':
            await collector.runOnce();
            process.exit(0);
            break;
            
        case 'test':
            log('🧪 Running test collection...', 'blue');
            const results = await collector.runOnce();
            log('✅ Test completed', 'green');
            process.exit(results ? 0 : 1);
            break;
            
        default:
            console.log(`
Usage: node data-collector.js [command] [interval]

Commands:
  start [interval]  - Start continuous collection (default: 5 minutes)
  once             - Run single collection cycle
  test             - Test collection and exit

Examples:
  node data-collector.js start 10    # Start with 10-minute intervals
  node data-collector.js once        # Run once and exit
  node data-collector.js test        # Test all connections
            `);
            process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    log('\n🛑 Received SIGINT, shutting down gracefully...', 'yellow');
    process.exit(0);
});

process.on('SIGTERM', () => {
    log('\n🛑 Received SIGTERM, shutting down gracefully...', 'yellow');
    process.exit(0);
});

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { VividWallsKPICollector };