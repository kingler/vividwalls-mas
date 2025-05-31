-- VividWalls Multi-Agent System (MAS) Message Broker Schema
-- PostgreSQL Database Schema for Inter-Agent Communication
-- Connection: localhost:54322

-- Create database schema for VividWalls MAS
CREATE SCHEMA IF NOT EXISTS vividwalls_mas;
SET search_path TO vividwalls_mas;

-- Enable necessary extensions (try uuid-ossp, fallback to gen_random_uuid)
DO $$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    EXCEPTION WHEN OTHERS THEN
        -- uuid-ossp not available, we'll use gen_random_uuid() directly
        NULL;
    END;
    
    BEGIN
        CREATE EXTENSION IF NOT EXISTS "btree_gin";
    EXCEPTION WHEN OTHERS THEN
        -- btree_gin not available, skip
        NULL;
    END;
END
$$;

-- =============================================
-- AGENT HIERARCHY AND CONFIGURATION
-- =============================================

-- Agent registry table
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    agent_type VARCHAR(50) NOT NULL,
    division VARCHAR(100) NOT NULL,
    priority_level INTEGER NOT NULL DEFAULT 5, -- 1 = highest, 10 = lowest
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    capabilities JSONB NOT NULL DEFAULT '[]',
    configuration JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent status tracking
CREATE TABLE agent_status (
    status_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- active, busy, idle, error, maintenance
    workload_level INTEGER NOT NULL DEFAULT 0, -- 0-100 percentage
    current_tasks INTEGER NOT NULL DEFAULT 0,
    max_concurrent_tasks INTEGER NOT NULL DEFAULT 5,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    performance_metrics JSONB DEFAULT '{}',
    error_details JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- MESSAGE QUEUE SYSTEM
-- =============================================

-- Main message queue table
CREATE TABLE agent_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL, -- Groups related messages
    from_agent_id UUID NOT NULL REFERENCES agents(agent_id),
    to_agent_id UUID NOT NULL REFERENCES agents(agent_id),
    message_type VARCHAR(50) NOT NULL, -- task, response, status, escalation, broadcast
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- critical, high, medium, low
    subject VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    business_context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    error_details JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Message response tracking
CREATE TABLE message_responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_message_id UUID NOT NULL REFERENCES agent_messages(message_id) ON DELETE CASCADE,
    response_message_id UUID NOT NULL REFERENCES agent_messages(message_id) ON DELETE CASCADE,
    response_type VARCHAR(50) NOT NULL, -- success, partial, failure, acknowledgment
    response_data JSONB DEFAULT '{}',
    processing_time_ms INTEGER DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- TASK COORDINATION SYSTEM
-- =============================================

-- Task coordination table
CREATE TABLE task_coordination (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL, -- campaign_creation, performance_analysis, optimization, research
    assigned_to_agent_id UUID NOT NULL REFERENCES agents(agent_id),
    requested_by_agent_id UUID NOT NULL REFERENCES agents(agent_id),
    parent_task_id UUID DEFAULT NULL REFERENCES task_coordination(task_id),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(30) NOT NULL DEFAULT 'pending', -- pending, assigned, in_progress, completed, failed, cancelled
    task_definition JSONB NOT NULL,
    task_parameters JSONB DEFAULT '{}',
    expected_deliverables JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]', -- Array of task_ids that must complete first
    estimated_duration_minutes INTEGER DEFAULT NULL,
    actual_duration_minutes INTEGER DEFAULT NULL,
    progress_percentage INTEGER DEFAULT 0,
    due_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    result_data JSONB DEFAULT '{}',
    quality_score INTEGER DEFAULT NULL, -- 1-100
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task dependencies tracking
CREATE TABLE task_dependencies (
    dependency_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dependent_task_id UUID NOT NULL REFERENCES task_coordination(task_id) ON DELETE CASCADE,
    prerequisite_task_id UUID NOT NULL REFERENCES task_coordination(task_id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) NOT NULL DEFAULT 'blocks', -- blocks, triggers, informs
    is_satisfied BOOLEAN DEFAULT FALSE,
    satisfied_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- PERFORMANCE METRICS SYSTEM
-- =============================================

-- Agent performance metrics
CREATE TABLE agent_performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL, -- response_time, task_completion_rate, quality_score, error_rate
    metric_value NUMERIC(10,4) NOT NULL,
    metric_unit VARCHAR(50) NOT NULL, -- milliseconds, percentage, score, count
    measurement_period VARCHAR(50) NOT NULL, -- hourly, daily, weekly, monthly
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    context_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System performance tracking
CREATE TABLE system_performance (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(15,4) NOT NULL,
    metric_category VARCHAR(50) NOT NULL, -- throughput, latency, resource_usage, business_kpi
    tags JSONB DEFAULT '{}',
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- WORKFLOW ORCHESTRATION
-- =============================================

-- Workflow definitions
CREATE TABLE workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(100) NOT NULL, -- campaign_execution, performance_review, crisis_response
    description TEXT,
    trigger_conditions JSONB NOT NULL,
    workflow_steps JSONB NOT NULL, -- Array of step definitions
    success_criteria JSONB DEFAULT '{}',
    failure_conditions JSONB DEFAULT '{}',
    timeout_minutes INTEGER DEFAULT 1440, -- 24 hours default
    retry_policy JSONB DEFAULT '{"max_retries": 3, "backoff_strategy": "exponential"}',
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow execution instances
CREATE TABLE workflow_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id),
    instance_name VARCHAR(255) NOT NULL,
    trigger_event JSONB NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'running', -- running, completed, failed, cancelled, paused
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    execution_context JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    error_details JSONB DEFAULT NULL,
    result_summary JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- BUSINESS CONTEXT AND KPI TRACKING
-- =============================================

-- Business KPI tracking
CREATE TABLE business_kpis (
    kpi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_name VARCHAR(100) NOT NULL,
    kpi_category VARCHAR(50) NOT NULL, -- revenue, marketing, customer, operational
    current_value NUMERIC(15,4) NOT NULL,
    target_value NUMERIC(15,4) DEFAULT NULL,
    unit_of_measure VARCHAR(50) NOT NULL,
    measurement_period VARCHAR(50) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trend_direction VARCHAR(20) DEFAULT NULL, -- up, down, stable
    variance_percentage NUMERIC(8,4) DEFAULT NULL,
    context_data JSONB DEFAULT '{}',
    responsible_agent_id UUID REFERENCES agents(agent_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign performance tracking
CREATE TABLE campaign_performance (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(100) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL, -- facebook, instagram, pinterest, email, shopify
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(15,4) NOT NULL,
    date_recorded DATE NOT NULL,
    hour_recorded INTEGER DEFAULT NULL, -- For hourly tracking
    additional_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Message queue indexes
CREATE INDEX idx_agent_messages_workflow_id ON agent_messages(workflow_id);
CREATE INDEX idx_agent_messages_to_agent_status ON agent_messages(to_agent_id, status);
CREATE INDEX idx_agent_messages_priority_scheduled ON agent_messages(priority, scheduled_for);
CREATE INDEX idx_agent_messages_created_at ON agent_messages(created_at);

-- Task coordination indexes
CREATE INDEX idx_task_coordination_workflow_id ON task_coordination(workflow_id);
CREATE INDEX idx_task_coordination_assigned_status ON task_coordination(assigned_to_agent_id, status);
CREATE INDEX idx_task_coordination_due_date ON task_coordination(due_date);

-- Performance metrics indexes
CREATE INDEX idx_agent_performance_agent_type ON agent_performance_metrics(agent_id, metric_type);
CREATE INDEX idx_agent_performance_period ON agent_performance_metrics(period_start, period_end);

-- Campaign performance indexes
CREATE INDEX idx_campaign_performance_channel_date ON campaign_performance(channel, date_recorded);
CREATE INDEX idx_campaign_performance_campaign_metric ON campaign_performance(campaign_id, metric_name);

-- =============================================
-- STORED PROCEDURES AND FUNCTIONS
-- =============================================

-- Function to publish a message
CREATE OR REPLACE FUNCTION publish_message(
    p_workflow_id UUID,
    p_from_agent_name VARCHAR(100),
    p_to_agent_name VARCHAR(100),
    p_message_type VARCHAR(50),
    p_priority VARCHAR(20),
    p_subject VARCHAR(255),
    p_content JSONB,
    p_business_context JSONB DEFAULT '{}',
    p_scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) RETURNS UUID AS $$
DECLARE
    v_message_id UUID;
    v_from_agent_id UUID;
    v_to_agent_id UUID;
BEGIN
    -- Get agent IDs
    SELECT agent_id INTO v_from_agent_id FROM agents WHERE agent_name = p_from_agent_name;
    SELECT agent_id INTO v_to_agent_id FROM agents WHERE agent_name = p_to_agent_name;
    
    IF v_from_agent_id IS NULL THEN
        RAISE EXCEPTION 'From agent % not found', p_from_agent_name;
    END IF;
    
    IF v_to_agent_id IS NULL THEN
        RAISE EXCEPTION 'To agent % not found', p_to_agent_name;
    END IF;
    
    -- Insert message
    INSERT INTO agent_messages (
        workflow_id, from_agent_id, to_agent_id, message_type, priority,
        subject, content, business_context, scheduled_for
    ) VALUES (
        p_workflow_id, v_from_agent_id, v_to_agent_id, p_message_type, p_priority,
        p_subject, p_content, p_business_context, p_scheduled_for
    ) RETURNING message_id INTO v_message_id;
    
    -- Notify listener (for real-time processing)
    PERFORM pg_notify('agent_message_queue', v_message_id::text);
    
    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql;

-- Function to consume next message for an agent
CREATE OR REPLACE FUNCTION consume_next_message(
    p_agent_name VARCHAR(100),
    p_message_types VARCHAR(50)[] DEFAULT NULL
) RETURNS TABLE (
    message_id UUID,
    workflow_id UUID,
    from_agent_name VARCHAR(100),
    message_type VARCHAR(50),
    priority VARCHAR(20),
    subject VARCHAR(255),
    content JSONB,
    business_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
    v_agent_id UUID;
    v_message_id UUID;
BEGIN
    -- Get agent ID
    SELECT agents.agent_id INTO v_agent_id FROM agents WHERE agent_name = p_agent_name;
    
    IF v_agent_id IS NULL THEN
        RAISE EXCEPTION 'Agent % not found', p_agent_name;
    END IF;
    
    -- Get next message with row-level locking
    SELECT am.message_id INTO v_message_id
    FROM agent_messages am
    WHERE am.to_agent_id = v_agent_id
      AND am.status = 'pending'
      AND am.scheduled_for <= NOW()
      AND (p_message_types IS NULL OR am.message_type = ANY(p_message_types))
    ORDER BY 
        CASE am.priority 
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2 
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
            ELSE 5
        END,
        am.created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;
    
    IF v_message_id IS NOT NULL THEN
        -- Mark message as processing
        UPDATE agent_messages 
        SET status = 'processing', processed_at = NOW()
        WHERE agent_messages.message_id = v_message_id;
        
        -- Return message details
        RETURN QUERY
        SELECT 
            am.message_id,
            am.workflow_id,
            from_agent.agent_name,
            am.message_type,
            am.priority,
            am.subject,
            am.content,
            am.business_context,
            am.created_at
        FROM agent_messages am
        JOIN agents from_agent ON am.from_agent_id = from_agent.agent_id
        WHERE am.message_id = v_message_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to complete message processing
CREATE OR REPLACE FUNCTION complete_message(
    p_message_id UUID,
    p_response_data JSONB DEFAULT '{}',
    p_success BOOLEAN DEFAULT TRUE
) RETURNS BOOLEAN AS $$
BEGIN
    IF p_success THEN
        UPDATE agent_messages 
        SET status = 'completed', completed_at = NOW()
        WHERE message_id = p_message_id;
    ELSE
        UPDATE agent_messages 
        SET status = 'failed', 
            completed_at = NOW(),
            error_details = p_response_data
        WHERE message_id = p_message_id;
    END IF;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to update agent status
CREATE OR REPLACE FUNCTION update_agent_status(
    p_agent_name VARCHAR(100),
    p_status VARCHAR(50),
    p_workload_level INTEGER DEFAULT NULL,
    p_current_tasks INTEGER DEFAULT NULL,
    p_performance_metrics JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    v_agent_id UUID;
BEGIN
    -- Get agent ID
    SELECT agent_id INTO v_agent_id FROM agents WHERE agent_name = p_agent_name;
    
    IF v_agent_id IS NULL THEN
        RAISE EXCEPTION 'Agent % not found', p_agent_name;
    END IF;
    
    -- Insert new status record
    INSERT INTO agent_status (
        agent_id, status, workload_level, current_tasks, 
        performance_metrics, last_heartbeat
    ) VALUES (
        v_agent_id, p_status, 
        COALESCE(p_workload_level, 0), 
        COALESCE(p_current_tasks, 0),
        COALESCE(p_performance_metrics, '{}'), 
        NOW()
    );
    
    -- Update agent last active time
    UPDATE agents 
    SET last_active_at = NOW()
    WHERE agent_id = v_agent_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to create a new task
CREATE OR REPLACE FUNCTION create_task(
    p_workflow_id UUID,
    p_task_name VARCHAR(255),
    p_task_type VARCHAR(100),
    p_assigned_to_agent_name VARCHAR(100),
    p_requested_by_agent_name VARCHAR(100),
    p_priority VARCHAR(20),
    p_task_definition JSONB,
    p_task_parameters JSONB DEFAULT '{}',
    p_due_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_dependencies UUID[] DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_task_id UUID;
    v_assigned_to_agent_id UUID;
    v_requested_by_agent_id UUID;
    v_dependency_id UUID;
BEGIN
    -- Get agent IDs
    SELECT agent_id INTO v_assigned_to_agent_id FROM agents WHERE agent_name = p_assigned_to_agent_name;
    SELECT agent_id INTO v_requested_by_agent_id FROM agents WHERE agent_name = p_requested_by_agent_name;
    
    IF v_assigned_to_agent_id IS NULL THEN
        RAISE EXCEPTION 'Assigned agent % not found', p_assigned_to_agent_name;
    END IF;
    
    IF v_requested_by_agent_id IS NULL THEN
        RAISE EXCEPTION 'Requesting agent % not found', p_requested_by_agent_name;
    END IF;
    
    -- Create task
    INSERT INTO task_coordination (
        workflow_id, task_name, task_type, assigned_to_agent_id, 
        requested_by_agent_id, priority, task_definition, task_parameters, due_date
    ) VALUES (
        p_workflow_id, p_task_name, p_task_type, v_assigned_to_agent_id,
        v_requested_by_agent_id, p_priority, p_task_definition, p_task_parameters, p_due_date
    ) RETURNING task_id INTO v_task_id;
    
    -- Add dependencies if provided
    IF p_dependencies IS NOT NULL AND array_length(p_dependencies, 1) > 0 THEN
        FOREACH v_dependency_id IN ARRAY p_dependencies LOOP
            INSERT INTO task_dependencies (dependent_task_id, prerequisite_task_id)
            VALUES (v_task_id, v_dependency_id);
        END LOOP;
    END IF;
    
    RETURN v_task_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record performance metrics
CREATE OR REPLACE FUNCTION record_agent_performance(
    p_agent_name VARCHAR(100),
    p_metric_type VARCHAR(100),
    p_metric_value NUMERIC(10,4),
    p_metric_unit VARCHAR(50),
    p_measurement_period VARCHAR(50),
    p_period_start TIMESTAMP WITH TIME ZONE,
    p_period_end TIMESTAMP WITH TIME ZONE,
    p_context_data JSONB DEFAULT '{}'
) RETURNS BOOLEAN AS $$
DECLARE
    v_agent_id UUID;
BEGIN
    -- Get agent ID
    SELECT agent_id INTO v_agent_id FROM agents WHERE agent_name = p_agent_name;
    
    IF v_agent_id IS NULL THEN
        RAISE EXCEPTION 'Agent % not found', p_agent_name;
    END IF;
    
    -- Insert performance metric
    INSERT INTO agent_performance_metrics (
        agent_id, metric_type, metric_value, metric_unit,
        measurement_period, period_start, period_end, context_data
    ) VALUES (
        v_agent_id, p_metric_type, p_metric_value, p_metric_unit,
        p_measurement_period, p_period_start, p_period_end, p_context_data
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- INITIALIZE VIVIDWALLS AGENT HIERARCHY
-- =============================================

-- Insert VividWalls agent hierarchy
INSERT INTO agents (agent_name, agent_type, division, priority_level, capabilities, configuration) VALUES
-- Business Manager Agent (Orchestrator)
('business_manager', 'orchestrator', 'Executive', 1, 
 '["strategic_oversight", "resource_management", "agent_coordination", "performance_analysis", "executive_reporting"]',
 '{"max_concurrent_workflows": 10, "response_time_sla_minutes": 15, "escalation_threshold": 85}'),

-- Marketing Intelligence Division
('marketing_research', 'analyst', 'Marketing Intelligence', 2,
 '["market_analysis", "competitor_intelligence", "consumer_insights", "performance_analytics", "trend_forecasting"]',
 '{"research_cycle_days": 30, "report_deadline_day": 5, "confidence_threshold": 95}'),

('marketing_campaign', 'strategist', 'Marketing Intelligence', 2,
 '["campaign_strategy", "creative_direction", "budget_planning", "testing_framework", "performance_tracking"]',
 '{"campaign_duration_months": 3, "optimization_cycle_hours": 24, "min_test_budget_percentage": 20}'),

-- Revenue & Customer Division  
('shopify_agent', 'platform_manager', 'Revenue & Customer', 3,
 '["store_optimization", "product_management", "email_marketing", "onsite_marketing", "analytics_reporting"]',
 '{"cro_targets": {"conversion_rate": 2.5, "cart_recovery_rate": 25}, "email_frequency_weekly": 3}'),

('facebook_ads_agent', 'platform_manager', 'Revenue & Customer', 3,
 '["facebook_advertising", "instagram_advertising", "audience_targeting", "creative_optimization", "performance_optimization"]',
 '{"min_roas": 3.5, "daily_budget_check": true, "auto_scaling_threshold": 120}'),

('instagram_agent', 'platform_manager', 'Revenue & Customer', 3,
 '["instagram_marketing", "story_campaigns", "reels_optimization", "influencer_coordination", "ugc_management"]',
 '{"engagement_targets": {"like_rate": 5, "comment_rate": 2}, "story_frequency_daily": 2}'),

('pinterest_agent', 'platform_manager', 'Revenue & Customer', 3,
 '["pinterest_marketing", "pin_optimization", "board_management", "seasonal_campaigns", "trend_analysis"]',
 '{"pin_frequency_weekly": 20, "board_refresh_cycle_weeks": 4, "trending_keyword_tracking": true}'),

-- Operations Division
('pictorem_agent', 'fulfillment_manager', 'Operations', 4,
 '["product_fulfillment", "inventory_sync", "quality_control", "shipping_coordination", "customer_service"]',
 '{"fulfillment_sla_days": 5, "quality_score_threshold": 95, "inventory_sync_hours": 2}'),

('email_marketing_agent', 'communication_manager', 'Operations', 4,
 '["email_campaigns", "automation_flows", "segmentation", "personalization", "deliverability_management"]',
 '{"open_rate_target": 25, "click_rate_target": 4, "unsubscribe_threshold": 2}'),

('customer_service_agent', 'support_manager', 'Operations', 4,
 '["customer_support", "order_tracking", "issue_resolution", "feedback_collection", "satisfaction_monitoring"]',
 '{"response_time_hours": 4, "satisfaction_score_target": 90, "escalation_criteria": "complex_issues"}');

-- Initialize agent status for all agents
INSERT INTO agent_status (agent_id, status, workload_level, current_tasks, max_concurrent_tasks)
SELECT 
    agent_id, 
    'active', 
    0, 
    0,
    CASE 
        WHEN agent_type = 'orchestrator' THEN 10
        WHEN agent_type IN ('analyst', 'strategist') THEN 5
        WHEN agent_type = 'platform_manager' THEN 8
        ELSE 6
    END
FROM agents;

-- =============================================
-- INITIAL WORKFLOW TEMPLATES
-- =============================================

-- Campaign Planning Workflow
INSERT INTO workflows (workflow_name, workflow_type, description, trigger_conditions, workflow_steps, created_by) VALUES
('monthly_campaign_planning', 'campaign_execution',
 'Monthly campaign planning and execution workflow based on research insights',
 '{"trigger_type": "scheduled", "schedule": "monthly", "day": 5}',
 '[
   {"step": 1, "agent": "marketing_research", "action": "submit_monthly_report", "sla_hours": 24},
   {"step": 2, "agent": "business_manager", "action": "review_research_insights", "sla_hours": 4},
   {"step": 3, "agent": "marketing_campaign", "action": "develop_campaign_strategy", "sla_hours": 48},
   {"step": 4, "agent": "business_manager", "action": "approve_budget_allocation", "sla_hours": 8},
   {"step": 5, "agent": "platform_agents", "action": "implement_campaigns", "sla_hours": 72},
   {"step": 6, "agent": "business_manager", "action": "monitor_performance", "sla_hours": 168}
 ]',
 'system'),

('daily_performance_review', 'performance_review',
 'Daily performance monitoring and optimization workflow',
 '{"trigger_type": "scheduled", "schedule": "daily", "time": "09:00"}',
 '[
   {"step": 1, "agent": "platform_agents", "action": "collect_performance_data", "sla_hours": 2},
   {"step": 2, "agent": "business_manager", "action": "analyze_performance", "sla_hours": 1},
   {"step": 3, "agent": "business_manager", "action": "identify_optimization_opportunities", "sla_hours": 1},
   {"step": 4, "agent": "platform_agents", "action": "implement_optimizations", "sla_hours": 4}
 ]',
 'system'),

('crisis_response', 'crisis_response',
 'Automated crisis response workflow for performance degradation',
 '{"trigger_type": "alert", "conditions": {"roas_below": 2.0, "cac_above": 50, "conversion_drop": 25}}',
 '[
   {"step": 1, "agent": "business_manager", "action": "assess_crisis_severity", "sla_hours": 0.5},
   {"step": 2, "agent": "platform_agents", "action": "pause_underperforming_campaigns", "sla_hours": 0.25},
   {"step": 3, "agent": "business_manager", "action": "analyze_root_cause", "sla_hours": 1},
   {"step": 4, "agent": "platform_agents", "action": "implement_fixes", "sla_hours": 2},
   {"step": 5, "agent": "business_manager", "action": "monitor_recovery", "sla_hours": 8}
 ]',
 'system');

-- =============================================
-- VIEWS FOR EASY QUERYING
-- =============================================

-- Active message queue view
CREATE VIEW active_message_queue AS
SELECT 
    am.message_id,
    am.workflow_id,
    from_agent.agent_name AS from_agent,
    to_agent.agent_name AS to_agent,
    am.message_type,
    am.priority,
    am.subject,
    am.status,
    am.created_at,
    am.scheduled_for
FROM agent_messages am
JOIN agents from_agent ON am.from_agent_id = from_agent.agent_id
JOIN agents to_agent ON am.to_agent_id = to_agent.agent_id
WHERE am.status IN ('pending', 'processing')
ORDER BY 
    CASE am.priority 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END,
    am.created_at;

-- Agent performance dashboard view
CREATE VIEW agent_performance_dashboard AS
SELECT 
    a.agent_name,
    a.division,
    a.agent_type,
    ast.status,
    ast.workload_level,
    ast.current_tasks,
    ast.max_concurrent_tasks,
    ast.last_heartbeat,
    EXTRACT(EPOCH FROM (NOW() - ast.last_heartbeat)) / 60 AS minutes_since_heartbeat
FROM agents a
LEFT JOIN LATERAL (
    SELECT * FROM agent_status 
    WHERE agent_id = a.agent_id 
    ORDER BY created_at DESC 
    LIMIT 1
) ast ON true;

-- Task coordination dashboard view
CREATE VIEW task_dashboard AS
SELECT 
    tc.task_id,
    tc.workflow_id,
    tc.task_name,
    tc.task_type,
    assigned_agent.agent_name AS assigned_to,
    requested_agent.agent_name AS requested_by,
    tc.priority,
    tc.status,
    tc.progress_percentage,
    tc.due_date,
    tc.created_at,
    CASE 
        WHEN tc.due_date < NOW() AND tc.status NOT IN ('completed', 'cancelled') THEN 'overdue'
        WHEN tc.due_date < NOW() + INTERVAL '24 hours' AND tc.status NOT IN ('completed', 'cancelled') THEN 'due_soon'
        ELSE 'on_track'
    END AS urgency_status
FROM task_coordination tc
JOIN agents assigned_agent ON tc.assigned_to_agent_id = assigned_agent.agent_id
JOIN agents requested_agent ON tc.requested_by_agent_id = requested_agent.agent_id;

-- Campaign performance summary view
CREATE VIEW campaign_performance_summary AS
SELECT 
    campaign_id,
    campaign_name,
    channel,
    date_recorded,
    SUM(CASE WHEN metric_name = 'spend' THEN metric_value ELSE 0 END) AS total_spend,
    SUM(CASE WHEN metric_name = 'revenue' THEN metric_value ELSE 0 END) AS total_revenue,
    CASE 
        WHEN SUM(CASE WHEN metric_name = 'spend' THEN metric_value ELSE 0 END) > 0 
        THEN SUM(CASE WHEN metric_name = 'revenue' THEN metric_value ELSE 0 END) / 
             SUM(CASE WHEN metric_name = 'spend' THEN metric_value ELSE 0 END)
        ELSE 0 
    END AS roas,
    COUNT(DISTINCT metric_name) AS metrics_recorded
FROM campaign_performance
GROUP BY campaign_id, campaign_name, channel, date_recorded;

-- =============================================
-- INITIAL KPI TARGETS
-- =============================================

-- Insert baseline KPI targets
INSERT INTO business_kpis (kpi_name, kpi_category, current_value, target_value, unit_of_measure, measurement_period, period_start, period_end) VALUES
('overall_roas', 'marketing', 3.2, 3.5, 'ratio', 'monthly', date_trunc('month', NOW()), date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 day'),
('customer_acquisition_cost', 'marketing', 45.00, 40.00, 'dollars', 'monthly', date_trunc('month', NOW()), date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 day'),
('conversion_rate', 'revenue', 2.3, 2.5, 'percentage', 'monthly', date_trunc('month', NOW()), date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 day'),
('monthly_revenue', 'revenue', 150000.00, 180000.00, 'dollars', 'monthly', date_trunc('month', NOW()), date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 day'),
('agent_task_completion_rate', 'operational', 92.0, 95.0, 'percentage', 'weekly', date_trunc('week', NOW()), date_trunc('week', NOW()) + INTERVAL '1 week' - INTERVAL '1 day'),
('average_response_time', 'operational', 18.5, 15.0, 'minutes', 'daily', date_trunc('day', NOW()), date_trunc('day', NOW()) + INTERVAL '1 day' - INTERVAL '1 second');

-- Grant permissions for MCP server access
GRANT ALL PRIVILEGES ON SCHEMA vividwalls_mas TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA vividwalls_mas TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA vividwalls_mas TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA vividwalls_mas TO postgres;

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_messages_pending_priority 
ON agent_messages(to_agent_id, status, priority, scheduled_for) 
WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_tasks_assigned_status
ON task_coordination(assigned_to_agent_id, status, priority, due_date)
WHERE status IN ('pending', 'assigned', 'in_progress');

CREATE INDEX IF NOT EXISTS idx_agent_status_latest
ON agent_status(agent_id, created_at DESC);

-- Create notification triggers for real-time updates
CREATE OR REPLACE FUNCTION notify_message_queue() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'pending' THEN
        PERFORM pg_notify('agent_message_inserted', 
            json_build_object(
                'message_id', NEW.message_id,
                'to_agent_id', NEW.to_agent_id,
                'priority', NEW.priority,
                'message_type', NEW.message_type
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notify_message_queue 
    AFTER INSERT ON agent_messages 
    FOR EACH ROW 
    EXECUTE FUNCTION notify_message_queue();

-- Success notification
SELECT 'VividWalls MAS Message Broker System initialized successfully!' AS status,
       COUNT(*) AS agents_created FROM agents;