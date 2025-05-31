-- VividWalls Multi-Agent System - KPI Dashboard Database Schema
-- Real-time metrics collection and business intelligence

-- Create dedicated schema for VividWalls MAS KPI data
CREATE SCHEMA IF NOT EXISTS vividwalls_kpis;

-- ==============================================
-- CORE BUSINESS METRICS TABLES
-- ==============================================

-- Daily business performance indicators
CREATE TABLE vividwalls_kpis.business_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_date DATE NOT NULL,
    revenue_total DECIMAL(10,2) DEFAULT 0,
    orders_count INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0,
    average_order_value DECIMAL(10,2) DEFAULT 0,
    customer_acquisition_cost DECIMAL(10,2) DEFAULT 0,
    return_on_ad_spend DECIMAL(5,2) DEFAULT 0,
    total_visitors INTEGER DEFAULT 0,
    ai_assistant_interactions INTEGER DEFAULT 0,
    ai_conversion_rate DECIMAL(5,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual agent performance metrics
CREATE TABLE vividwalls_kpis.agent_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    agent_name VARCHAR(200) NOT NULL,
    metric_date DATE NOT NULL,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    average_response_time_ms INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    uptime_percentage DECIMAL(5,2) DEFAULT 100.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Real-time task tracking across all agents
CREATE TABLE vividwalls_kpis.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    description TEXT,
    context JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER
);

-- Campaign performance across all marketing channels
CREATE TABLE vividwalls_kpis.campaign_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'facebook', 'pinterest', 'email', 'shopify'
    campaign_name VARCHAR(200) NOT NULL,
    metric_date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    spend DECIMAL(10,2) DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    cpc DECIMAL(10,2) DEFAULT 0,
    roas DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer engagement and satisfaction metrics
CREATE TABLE vividwalls_kpis.customer_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL,
    total_customers INTEGER DEFAULT 0,
    new_customers INTEGER DEFAULT 0,
    returning_customers INTEGER DEFAULT 0,
    customer_lifetime_value DECIMAL(10,2) DEFAULT 0,
    churn_rate DECIMAL(5,4) DEFAULT 0,
    satisfaction_score DECIMAL(3,2) DEFAULT 0,
    support_tickets INTEGER DEFAULT 0,
    avg_resolution_time_hours INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- AGENT SYSTEM MONITORING
-- ==============================================

-- Active agents registry
CREATE TABLE vividwalls_kpis.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_name VARCHAR(200) NOT NULL,
    agent_type VARCHAR(100) NOT NULL, -- 'business_manager', 'marketing', 'operations', etc.
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    capabilities JSONB,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inter-agent communication logs
CREATE TABLE vividwalls_kpis.agent_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_agent_id VARCHAR(100) NOT NULL,
    receiver_agent_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(100) NOT NULL,
    message_content JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'sent',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    received_at TIMESTAMP WITH TIME ZONE,
    response_time_ms INTEGER
);

-- System health monitoring
CREATE TABLE vividwalls_kpis.system_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name VARCHAR(100) NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- 'mcp_server', 'database', 'webhook', 'api'
    status VARCHAR(50) NOT NULL, -- 'healthy', 'warning', 'critical', 'down'
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    response_time_ms INTEGER,
    error_rate DECIMAL(5,4),
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    details JSONB
);

-- ==============================================
-- E-COMMERCE SPECIFIC METRICS
-- ==============================================

-- Product performance tracking
CREATE TABLE vividwalls_kpis.product_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(200),
    metric_date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    add_to_cart INTEGER DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    ai_recommendations INTEGER DEFAULT 0,
    ai_conversion_rate DECIMAL(5,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI assistant interaction analytics
CREATE TABLE vividwalls_kpis.ai_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(100) NOT NULL, -- 'chat', 'image_analysis', 'recommendation'
    page_type VARCHAR(50), -- 'product', 'collection', 'cart', 'home'
    product_context VARCHAR(100),
    user_message TEXT,
    ai_response TEXT,
    recommendations JSONB,
    conversion_occurred BOOLEAN DEFAULT FALSE,
    response_time_ms INTEGER,
    satisfaction_rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- QUALITY ASSURANCE & FULFILLMENT
-- ==============================================

-- Order fulfillment tracking
CREATE TABLE vividwalls_kpis.fulfillment_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    processing_time_hours INTEGER,
    quality_score INTEGER,
    shipping_time_days INTEGER,
    customer_satisfaction INTEGER,
    issues_reported JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

-- Business KPIs indexes
CREATE INDEX idx_business_kpis_date ON vividwalls_kpis.business_kpis(kpi_date);
CREATE INDEX idx_business_kpis_revenue ON vividwalls_kpis.business_kpis(revenue_total);

-- Agent performance indexes
CREATE INDEX idx_agent_performance_agent_date ON vividwalls_kpis.agent_performance(agent_id, metric_date);
CREATE INDEX idx_agent_performance_success_rate ON vividwalls_kpis.agent_performance(success_rate);

-- Tasks indexes
CREATE INDEX idx_tasks_status ON vividwalls_kpis.tasks(status);
CREATE INDEX idx_tasks_agent_id ON vividwalls_kpis.tasks(agent_id);
CREATE INDEX idx_tasks_priority ON vividwalls_kpis.tasks(priority);
CREATE INDEX idx_tasks_created_at ON vividwalls_kpis.tasks(created_at);

-- Campaign performance indexes
CREATE INDEX idx_campaign_performance_platform_date ON vividwalls_kpis.campaign_performance(platform, metric_date);
CREATE INDEX idx_campaign_performance_roas ON vividwalls_kpis.campaign_performance(roas);

-- AI interactions indexes
CREATE INDEX idx_ai_interactions_session ON vividwalls_kpis.ai_interactions(session_id);
CREATE INDEX idx_ai_interactions_type ON vividwalls_kpis.ai_interactions(interaction_type);
CREATE INDEX idx_ai_interactions_created_at ON vividwalls_kpis.ai_interactions(created_at);

-- ==============================================
-- VIEWS FOR DASHBOARD QUERIES
-- ==============================================

-- Executive dashboard summary view
CREATE VIEW vividwalls_kpis.executive_dashboard AS
SELECT 
    DATE_TRUNC('day', NOW()) as report_date,
    SUM(revenue_total) as total_revenue,
    SUM(orders_count) as total_orders,
    AVG(conversion_rate) as avg_conversion_rate,
    AVG(average_order_value) as avg_order_value,
    AVG(return_on_ad_spend) as avg_roas,
    SUM(ai_assistant_interactions) as total_ai_interactions,
    AVG(ai_conversion_rate) as avg_ai_conversion_rate
FROM vividwalls_kpis.business_kpis 
WHERE kpi_date >= CURRENT_DATE - INTERVAL '30 days';

-- Agent health summary view
CREATE VIEW vividwalls_kpis.agent_health_summary AS
SELECT 
    a.agent_id,
    a.agent_name,
    a.agent_type,
    a.status,
    COALESCE(ap.success_rate, 0) as current_success_rate,
    COALESCE(ap.average_response_time_ms, 0) as avg_response_time,
    COUNT(t.id) as active_tasks,
    a.last_heartbeat
FROM vividwalls_kpis.agents a
LEFT JOIN vividwalls_kpis.agent_performance ap ON a.agent_id = ap.agent_id 
    AND ap.metric_date = CURRENT_DATE
LEFT JOIN vividwalls_kpis.tasks t ON a.agent_id = t.agent_id 
    AND t.status IN ('pending', 'in_progress')
GROUP BY a.agent_id, a.agent_name, a.agent_type, a.status, ap.success_rate, ap.average_response_time_ms, a.last_heartbeat;

-- Real-time performance metrics view
CREATE VIEW vividwalls_kpis.realtime_performance AS
SELECT 
    'revenue' as metric_name,
    SUM(revenue_total) as value,
    'daily' as period,
    CURRENT_DATE as metric_date
FROM vividwalls_kpis.business_kpis 
WHERE kpi_date = CURRENT_DATE
UNION ALL
SELECT 
    'active_tasks' as metric_name,
    COUNT(*) as value,
    'realtime' as period,
    CURRENT_DATE as metric_date
FROM vividwalls_kpis.tasks 
WHERE status IN ('pending', 'in_progress')
UNION ALL
SELECT 
    'agent_uptime' as metric_name,
    AVG(uptime_percentage) as value,
    'current' as period,
    CURRENT_DATE as metric_date
FROM vividwalls_kpis.agent_performance 
WHERE metric_date = CURRENT_DATE;

-- ==============================================
-- TRIGGERS FOR REAL-TIME UPDATES
-- ==============================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION vividwalls_kpis.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_business_kpis_modtime 
    BEFORE UPDATE ON vividwalls_kpis.business_kpis 
    FOR EACH ROW EXECUTE FUNCTION vividwalls_kpis.update_modified_column();

CREATE TRIGGER update_agent_performance_modtime 
    BEFORE UPDATE ON vividwalls_kpis.agent_performance 
    FOR EACH ROW EXECUTE FUNCTION vividwalls_kpis.update_modified_column();

CREATE TRIGGER update_agents_modtime 
    BEFORE UPDATE ON vividwalls_kpis.agents 
    FOR EACH ROW EXECUTE FUNCTION vividwalls_kpis.update_modified_column();

-- ==============================================
-- INITIAL DATA POPULATION
-- ==============================================

-- Insert VividWalls MAS agents
INSERT INTO vividwalls_kpis.agents (agent_id, agent_name, agent_type, capabilities) VALUES
('business_manager', 'Business Manager Agent', 'orchestrator', '{"strategy": true, "coordination": true, "decision_making": true}'),
('marketing_research', 'Marketing Research Agent', 'marketing', '{"market_analysis": true, "trend_research": true, "competitor_analysis": true}'),
('marketing_campaign', 'Marketing Campaign Agent', 'marketing', '{"campaign_creation": true, "ad_management": true, "content_strategy": true}'),
('shopify_manager', 'Shopify Management Agent', 'operations', '{"store_management": true, "product_updates": true, "order_processing": true}'),
('facebook_ads', 'Facebook Ads Agent', 'marketing', '{"facebook_advertising": true, "instagram_ads": true, "audience_targeting": true}'),
('pinterest_marketing', 'Pinterest Marketing Agent', 'marketing', '{"pinterest_ads": true, "visual_content": true, "pin_optimization": true}'),
('email_marketing', 'Email Marketing Agent', 'marketing', '{"email_campaigns": true, "automation": true, "segmentation": true}'),
('pictorem_fulfillment', 'Pictorem Fulfillment Agent', 'operations', '{"order_fulfillment": true, "quality_control": true, "shipping": true}'),
('content_creator', 'Content Creation Agent', 'marketing', '{"content_creation": true, "copywriting": true, "visual_assets": true}'),
('customer_support', 'Customer Support Agent', 'operations', '{"customer_service": true, "issue_resolution": true, "satisfaction": true}');

-- Sample KPI data for current date
INSERT INTO vividwalls_kpis.business_kpis (kpi_date) VALUES (CURRENT_DATE);
INSERT INTO vividwalls_kpis.agent_performance (agent_id, agent_name, metric_date) 
SELECT agent_id, agent_name, CURRENT_DATE FROM vividwalls_kpis.agents;

COMMIT;