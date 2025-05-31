#!/usr/bin/env node

/**
 * VividWalls MAS KPI Database Setup
 * Initializes the database schema and populates initial data
 */

import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const SUPABASE_URL = process.env.SUPABASE_URL || 'http://127.0.0.1:54321';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';

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
    console.log(`${colors[color]}${message}${colors.reset}`);
}

class DatabaseSetup {
    constructor() {
        this.supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    }

    async setupDatabase() {
        try {
            log('🚀 Starting VividWalls MAS KPI Database Setup...', 'bold');
            
            // Test connection
            await this.testConnection();
            
            // Execute schema SQL
            await this.executeSchema();
            
            // Populate initial data
            await this.populateInitialData();
            
            // Verify setup
            await this.verifySetup();
            
            log('✅ Database setup completed successfully!', 'green');
            
        } catch (error) {
            log(`❌ Database setup failed: ${error.message}`, 'red');
            process.exit(1);
        }
    }

    async testConnection() {
        log('🔌 Testing database connection...', 'blue');
        
        try {
            const { data, error } = await this.supabase
                .from('information_schema.tables')
                .select('table_name')
                .limit(1);

            if (error) throw error;
            
            log('✅ Database connection successful', 'green');
        } catch (error) {
            throw new Error(`Database connection failed: ${error.message}`);
        }
    }

    async executeSchema() {
        log('📋 Executing database schema...', 'blue');
        
        try {
            // Read schema file
            const schemaPath = path.join(__dirname, 'schema.sql');
            const schemaSQL = readFileSync(schemaPath, 'utf8');
            
            // Split into individual statements and execute
            const statements = schemaSQL
                .split(';')
                .map(stmt => stmt.trim())
                .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));

            let executedStatements = 0;
            
            for (const statement of statements) {
                try {
                    if (statement.toLowerCase().includes('commit')) {
                        continue; // Skip COMMIT statements
                    }
                    
                    const { error } = await this.supabase.rpc('exec_sql', {
                        sql: statement
                    });

                    if (error && !error.message.includes('already exists')) {
                        log(`⚠️  Warning executing statement: ${error.message}`, 'yellow');
                    }
                    
                    executedStatements++;
                } catch (err) {
                    if (!err.message.includes('already exists')) {
                        log(`⚠️  Warning: ${err.message}`, 'yellow');
                    }
                }
            }
            
            log(`✅ Executed ${executedStatements} database statements`, 'green');
            
        } catch (error) {
            throw new Error(`Schema execution failed: ${error.message}`);
        }
    }

    async populateInitialData() {
        log('📊 Populating initial data...', 'blue');
        
        try {
            // Check if data already exists
            const { data: existingAgents } = await this.supabase
                .from('vividwalls_kpis.agents')
                .select('agent_id')
                .limit(1);

            if (existingAgents && existingAgents.length > 0) {
                log('✅ Initial data already exists, skipping population', 'yellow');
                return;
            }

            // Insert VividWalls MAS agents
            const agents = [
                {
                    agent_id: 'business_manager',
                    agent_name: 'Business Manager Agent',
                    agent_type: 'orchestrator',
                    capabilities: {
                        strategy: true,
                        coordination: true,
                        decision_making: true,
                        kpi_monitoring: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'marketing_research',
                    agent_name: 'Marketing Research Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        market_analysis: true,
                        trend_research: true,
                        competitor_analysis: true,
                        customer_insights: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'marketing_campaign',
                    agent_name: 'Marketing Campaign Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        campaign_creation: true,
                        ad_management: true,
                        content_strategy: true,
                        performance_optimization: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'shopify_manager',
                    agent_name: 'Shopify Management Agent',
                    agent_type: 'operations',
                    capabilities: {
                        store_management: true,
                        product_updates: true,
                        order_processing: true,
                        inventory_management: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'facebook_ads',
                    agent_name: 'Facebook Ads Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        facebook_advertising: true,
                        instagram_ads: true,
                        audience_targeting: true,
                        ad_optimization: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'pinterest_marketing',
                    agent_name: 'Pinterest Marketing Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        pinterest_ads: true,
                        visual_content: true,
                        pin_optimization: true,
                        board_management: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'email_marketing',
                    agent_name: 'Email Marketing Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        email_campaigns: true,
                        automation: true,
                        segmentation: true,
                        personalization: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'pictorem_fulfillment',
                    agent_name: 'Pictorem Fulfillment Agent',
                    agent_type: 'operations',
                    capabilities: {
                        order_fulfillment: true,
                        quality_control: true,
                        shipping: true,
                        customer_communication: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'content_creator',
                    agent_name: 'Content Creation Agent',
                    agent_type: 'marketing',
                    capabilities: {
                        content_creation: true,
                        copywriting: true,
                        visual_assets: true,
                        brand_consistency: true
                    },
                    status: 'active'
                },
                {
                    agent_id: 'customer_support',
                    agent_name: 'Customer Support Agent',
                    agent_type: 'operations',
                    capabilities: {
                        customer_service: true,
                        issue_resolution: true,
                        satisfaction_tracking: true,
                        knowledge_base: true
                    },
                    status: 'active'
                }
            ];

            const { error: agentsError } = await this.supabase
                .from('vividwalls_kpis.agents')
                .insert(agents);

            if (agentsError) throw agentsError;

            // Create initial business KPIs record for today
            const today = new Date().toISOString().split('T')[0];
            const { error: kpisError } = await this.supabase
                .from('vividwalls_kpis.business_kpis')
                .insert({
                    kpi_date: today,
                    revenue_total: 0,
                    orders_count: 0,
                    conversion_rate: 0,
                    average_order_value: 0,
                    customer_acquisition_cost: 0,
                    return_on_ad_spend: 0,
                    total_visitors: 0,
                    ai_assistant_interactions: 0,
                    ai_conversion_rate: 0
                });

            if (kpisError && !kpisError.message.includes('duplicate key')) {
                throw kpisError;
            }

            // Create initial agent performance records
            const agentPerformanceData = agents.map(agent => ({
                agent_id: agent.agent_id,
                agent_name: agent.agent_name,
                metric_date: today,
                tasks_completed: 0,
                tasks_failed: 0,
                average_response_time_ms: 0,
                success_rate: 1.0,
                error_count: 0,
                uptime_percentage: 100.0
            }));

            const { error: performanceError } = await this.supabase
                .from('vividwalls_kpis.agent_performance')
                .insert(agentPerformanceData);

            if (performanceError && !performanceError.message.includes('duplicate key')) {
                throw performanceError;
            }

            // Create sample system health records
            const systemHealthData = [
                {
                    component_name: 'shopify-mcp-server',
                    component_type: 'mcp_server',
                    status: 'healthy',
                    cpu_usage: 5.2,
                    memory_usage: 12.8,
                    response_time_ms: 150,
                    error_rate: 0.001,
                    details: { version: '1.0.1', last_restart: new Date().toISOString() }
                },
                {
                    component_name: 'supabase-mcp-server',
                    component_type: 'database',
                    status: 'healthy',
                    cpu_usage: 8.1,
                    memory_usage: 24.5,
                    response_time_ms: 75,
                    error_rate: 0.0,
                    details: { connections: 15, uptime: '99.98%' }
                },
                {
                    component_name: 'n8n-server',
                    component_type: 'webhook',
                    status: 'healthy',
                    cpu_usage: 15.3,
                    memory_usage: 45.2,
                    response_time_ms: 300,
                    error_rate: 0.002,
                    details: { active_workflows: 8, executions_today: 127 }
                }
            ];

            const { error: healthError } = await this.supabase
                .from('vividwalls_kpis.system_health')
                .insert(systemHealthData);

            if (healthError && !healthError.message.includes('duplicate key')) {
                throw healthError;
            }

            log(`✅ Populated initial data: ${agents.length} agents, KPIs, and system health`, 'green');
            
        } catch (error) {
            throw new Error(`Initial data population failed: ${error.message}`);
        }
    }

    async verifySetup() {
        log('🔍 Verifying database setup...', 'blue');
        
        try {
            // Check if all tables exist and have data
            const checks = [
                { table: 'vividwalls_kpis.agents', expectedMin: 10 },
                { table: 'vividwalls_kpis.business_kpis', expectedMin: 1 },
                { table: 'vividwalls_kpis.agent_performance', expectedMin: 10 },
                { table: 'vividwalls_kpis.system_health', expectedMin: 1 }
            ];

            for (const check of checks) {
                const { data, error } = await this.supabase
                    .from(check.table)
                    .select('*', { count: 'exact' });

                if (error) {
                    throw new Error(`Failed to verify ${check.table}: ${error.message}`);
                }

                const count = data?.length || 0;
                if (count < check.expectedMin) {
                    log(`⚠️  Warning: ${check.table} has only ${count} records (expected min: ${check.expectedMin})`, 'yellow');
                } else {
                    log(`✅ ${check.table}: ${count} records`, 'green');
                }
            }

            // Test views
            const { data: dashboardData, error: dashboardError } = await this.supabase
                .from('vividwalls_kpis.executive_dashboard')
                .select('*')
                .single();

            if (dashboardError) {
                log(`⚠️  Warning: Executive dashboard view not accessible: ${dashboardError.message}`, 'yellow');
            } else {
                log('✅ Executive dashboard view working', 'green');
            }

            const { data: healthData, error: healthError } = await this.supabase
                .from('vividwalls_kpis.agent_health_summary')
                .select('*')
                .limit(5);

            if (healthError) {
                log(`⚠️  Warning: Agent health summary view not accessible: ${healthError.message}`, 'yellow');
            } else {
                log(`✅ Agent health summary view working (${healthData?.length || 0} agents)`, 'green');
            }

            log('✅ Database verification completed', 'green');
            
        } catch (error) {
            throw new Error(`Database verification failed: ${error.message}`);
        }
    }

    async generateSampleData() {
        log('🎲 Generating sample data for testing...', 'blue');
        
        try {
            const today = new Date();
            const sampleData = [];

            // Generate last 7 days of sample data
            for (let i = 6; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                const dateStr = date.toISOString().split('T')[0];

                // Sample business metrics
                const revenue = Math.floor(Math.random() * 2000) + 500;
                const orders = Math.floor(Math.random() * 20) + 5;
                const interactions = Math.floor(Math.random() * 100) + 20;

                sampleData.push({
                    kpi_date: dateStr,
                    revenue_total: revenue,
                    orders_count: orders,
                    conversion_rate: (Math.random() * 0.05) + 0.02, // 2-7%
                    average_order_value: revenue / orders,
                    customer_acquisition_cost: Math.floor(Math.random() * 50) + 15,
                    return_on_ad_spend: (Math.random() * 3) + 2, // 2-5x ROAS
                    total_visitors: Math.floor(Math.random() * 1000) + 200,
                    ai_assistant_interactions: interactions,
                    ai_conversion_rate: (Math.random() * 0.3) + 0.1 // 10-40%
                });
            }

            const { error } = await this.supabase
                .from('vividwalls_kpis.business_kpis')
                .upsert(sampleData, { onConflict: 'kpi_date' });

            if (error) throw error;

            log(`✅ Generated ${sampleData.length} days of sample business data`, 'green');

            // Generate sample campaign data
            const campaigns = [
                {
                    campaign_id: 'fb_spring_2025',
                    platform: 'facebook',
                    campaign_name: 'Spring Collection 2025',
                    metric_date: today.toISOString().split('T')[0],
                    impressions: 15000,
                    clicks: 750,
                    conversions: 45,
                    spend: 250,
                    revenue: 2250,
                    ctr: 0.05,
                    cpc: 0.33,
                    roas: 9.0
                },
                {
                    campaign_id: 'pin_abstract_art',
                    platform: 'pinterest',
                    campaign_name: 'Abstract Art Collection',
                    metric_date: today.toISOString().split('T')[0],
                    impressions: 8000,
                    clicks: 320,
                    conversions: 18,
                    spend: 150,
                    revenue: 1350,
                    ctr: 0.04,
                    cpc: 0.47,
                    roas: 9.0
                }
            ];

            const { error: campaignError } = await this.supabase
                .from('vividwalls_kpis.campaign_performance')
                .upsert(campaigns, { onConflict: 'campaign_id,metric_date' });

            if (campaignError) throw campaignError;

            log(`✅ Generated ${campaigns.length} sample campaigns`, 'green');

        } catch (error) {
            throw new Error(`Sample data generation failed: ${error.message}`);
        }
    }
}

// CLI interface
async function main() {
    const command = process.argv[2] || 'setup';
    const setup = new DatabaseSetup();

    switch (command) {
        case 'setup':
            await setup.setupDatabase();
            break;

        case 'verify':
            await setup.verifySetup();
            break;

        case 'sample-data':
            await setup.generateSampleData();
            break;

        case 'test':
            await setup.testConnection();
            break;

        default:
            console.log(`
Usage: node setup-database.js [command]

Commands:
  setup        - Complete database setup (schema + initial data)
  verify       - Verify database setup
  sample-data  - Generate sample data for testing
  test         - Test database connection

Examples:
  node setup-database.js setup
  node setup-database.js verify
  node setup-database.js sample-data
            `);
            process.exit(1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(error => {
        console.error('Setup failed:', error);
        process.exit(1);
    });
}

export { DatabaseSetup };