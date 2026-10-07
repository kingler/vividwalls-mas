#!/usr/bin/env node

/**
 * VividWalls MAS KPI Dashboard Server
 * Real-time web dashboard for monitoring multi-agent system performance
 */

import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const PORT = process.env.DASHBOARD_PORT || 3010;
const SUPABASE_URL = process.env.SUPABASE_URL || 'http://127.0.0.1:54321';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 'REDACTED_JWT';

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Store active WebSocket connections
const wsConnections = new Set();

// =============================================
// API ENDPOINTS
// =============================================

// Executive dashboard summary
app.get('/api/dashboard/executive', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('vividwalls_kpis.executive_dashboard')
            .select('*')
            .single();

        if (error) throw error;

        res.json({ success: true, data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Agent health summary
app.get('/api/dashboard/agents', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('vividwalls_kpis.agent_health_summary')
            .select('*')
            .order('agent_type', { ascending: true });

        if (error) throw error;

        res.json({ success: true, data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Real-time performance metrics
app.get('/api/dashboard/realtime', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('vividwalls_kpis.realtime_performance')
            .select('*');

        if (error) throw error;

        const metrics = {};
        data.forEach(row => {
            metrics[row.metric_name] = {
                value: row.value,
                period: row.period,
                date: row.metric_date
            };
        });

        res.json({ success: true, data: metrics });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Business KPIs over time
app.get('/api/dashboard/business-kpis', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const { data, error } = await supabase
            .from('vividwalls_kpis.business_kpis')
            .select('*')
            .gte('kpi_date', startDate.toISOString().split('T')[0])
            .order('kpi_date', { ascending: true });

        if (error) throw error;

        res.json({ success: true, data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Campaign performance
app.get('/api/dashboard/campaigns', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 7;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const { data, error } = await supabase
            .from('vividwalls_kpis.campaign_performance')
            .select('*')
            .gte('metric_date', startDate.toISOString().split('T')[0])
            .order('metric_date', { ascending: true });

        if (error) throw error;

        // Group by platform
        const campaigns = {};
        data.forEach(row => {
            if (!campaigns[row.platform]) {
                campaigns[row.platform] = [];
            }
            campaigns[row.platform].push(row);
        });

        res.json({ success: true, data: campaigns });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// System health status
app.get('/api/dashboard/system-health', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('vividwalls_kpis.system_health')
            .select('*')
            .order('last_check', { ascending: false });

        if (error) throw error;

        // Group by component type
        const health = {};
        data.forEach(row => {
            if (!health[row.component_type]) {
                health[row.component_type] = [];
            }
            health[row.component_type].push(row);
        });

        res.json({ success: true, data: health });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Active tasks
app.get('/api/dashboard/tasks', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('vividwalls_kpis.tasks')
            .select('*')
            .in('status', ['pending', 'in_progress'])
            .order('priority', { ascending: false })
            .order('created_at', { ascending: true })
            .limit(50);

        if (error) throw error;

        res.json({ success: true, data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// AI interaction analytics
app.get('/api/dashboard/ai-interactions', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 7;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const { data, error } = await supabase
            .from('vividwalls_kpis.ai_interactions')
            .select('*')
            .gte('created_at', startDate.toISOString())
            .order('created_at', { ascending: true });

        if (error) throw error;

        // Aggregate by day and interaction type
        const analytics = {};
        data.forEach(row => {
            const date = row.created_at.split('T')[0];
            if (!analytics[date]) {
                analytics[date] = {
                    total: 0,
                    by_type: {},
                    conversions: 0,
                    satisfaction: []
                };
            }
            
            analytics[date].total++;
            analytics[date].by_type[row.interaction_type] = 
                (analytics[date].by_type[row.interaction_type] || 0) + 1;
                
            if (row.conversion_occurred) {
                analytics[date].conversions++;
            }
            
            if (row.satisfaction_rating) {
                analytics[date].satisfaction.push(row.satisfaction_rating);
            }
        });

        res.json({ success: true, data: analytics });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// =============================================
// WEBSOCKET SERVER FOR REAL-TIME UPDATES
// =============================================

const server = app.listen(PORT, () => {
    console.log(`🚀 VividWalls KPI Dashboard running on http://localhost:${PORT}`);
});

const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
    console.log('📱 New dashboard client connected');
    wsConnections.add(ws);
    
    // Send initial data
    sendRealtimeUpdate(ws);
    
    ws.on('close', () => {
        console.log('📱 Dashboard client disconnected');
        wsConnections.delete(ws);
    });
    
    ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
        wsConnections.delete(ws);
    });
});

// Function to send real-time updates to all connected clients
async function sendRealtimeUpdate(targetWs = null) {
    try {
        // Fetch latest metrics
        const [realtimeData, agentsData, tasksData] = await Promise.all([
            supabase.from('vividwalls_kpis.realtime_performance').select('*'),
            supabase.from('vividwalls_kpis.agent_health_summary').select('*'),
            supabase.from('vividwalls_kpis.tasks').select('*').in('status', ['pending', 'in_progress']).limit(10)
        ]);

        const update = {
            timestamp: new Date().toISOString(),
            realtime: realtimeData.data || [],
            agents: agentsData.data || [],
            tasks: tasksData.data || []
        };

        const message = JSON.stringify(update);
        
        if (targetWs) {
            // Send to specific client
            if (targetWs.readyState === 1) {
                targetWs.send(message);
            }
        } else {
            // Broadcast to all clients
            wsConnections.forEach(ws => {
                if (ws.readyState === 1) {
                    ws.send(message);
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Failed to send real-time update:', error);
    }
}

// Send updates every 30 seconds
setInterval(sendRealtimeUpdate, 30000);

// =============================================
// SERVE DASHBOARD HTML
// =============================================

app.get('/', (req, res) => {
    res.send(generateDashboardHTML());
});

function generateDashboardHTML() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VividWalls MAS KPI Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .dashboard {
            padding: 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-4px);
        }
        
        .card h3 {
            margin-bottom: 1rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .metric-value.success { color: #4CAF50; }
        .metric-value.warning { color: #FF9800; }
        .metric-value.error { color: #F44336; }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }
        
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .agent-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            border-left: 4px solid #4CAF50;
        }
        
        .agent-card.warning {
            border-left-color: #FF9800;
        }
        
        .agent-card.error {
            border-left-color: #F44336;
        }
        
        .agent-name {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .agent-stats {
            font-size: 0.85rem;
            color: #666;
        }
        
        .task-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .task-item {
            padding: 0.75rem;
            border-left: 3px solid #667eea;
            margin-bottom: 0.5rem;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .task-title {
            font-weight: bold;
            margin-bottom: 0.25rem;
        }
        
        .task-meta {
            font-size: 0.8rem;
            color: #666;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s ease;
        }
        
        .refresh-btn:hover {
            background: #5a67d8;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .header {
                padding: 1rem;
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎨 VividWalls MAS Dashboard</div>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span id="connection-status">Connected</span>
            <button class="refresh-btn" onclick="refreshDashboard()">Refresh</button>
        </div>
    </div>
    
    <div class="dashboard">
        <!-- Executive Summary -->
        <div class="card">
            <h3>📊 Executive Summary</h3>
            <div id="executive-metrics">
                <div class="loading">Loading executive metrics...</div>
            </div>
        </div>
        
        <!-- Revenue Chart -->
        <div class="card">
            <h3>💰 Revenue Trend</h3>
            <div class="chart-container">
                <canvas id="revenueChart"></canvas>
            </div>
        </div>
        
        <!-- Agent Health -->
        <div class="card">
            <h3>🤖 Agent Health</h3>
            <div id="agent-health">
                <div class="loading">Loading agent status...</div>
            </div>
        </div>
        
        <!-- System Health -->
        <div class="card">
            <h3>🔧 System Health</h3>
            <div id="system-health">
                <div class="loading">Loading system status...</div>
            </div>
        </div>
        
        <!-- Active Tasks -->
        <div class="card">
            <h3>📋 Active Tasks</h3>
            <div id="active-tasks">
                <div class="loading">Loading tasks...</div>
            </div>
        </div>
        
        <!-- Campaign Performance -->
        <div class="card">
            <h3>📈 Campaign Performance</h3>
            <div class="chart-container">
                <canvas id="campaignChart"></canvas>
            </div>
        </div>
        
        <!-- AI Interactions -->
        <div class="card">
            <h3>🤖 AI Assistant Analytics</h3>
            <div id="ai-analytics">
                <div class="loading">Loading AI metrics...</div>
            </div>
        </div>
        
        <!-- Real-time Metrics -->
        <div class="card">
            <h3>⚡ Real-time Metrics</h3>
            <div id="realtime-metrics">
                <div class="loading">Loading real-time data...</div>
            </div>
        </div>
    </div>

    <script>
        let revenueChart, campaignChart;
        let wsConnection;
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.host;
            
            wsConnection = new WebSocket(wsUrl);
            
            wsConnection.onopen = function() {
                document.getElementById('connection-status').textContent = 'Connected';
                document.querySelector('.status-dot').style.background = '#4CAF50';
            };
            
            wsConnection.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateRealtimeData(data);
            };
            
            wsConnection.onclose = function() {
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.querySelector('.status-dot').style.background = '#F44336';
                
                // Attempt to reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            wsConnection.onerror = function(error) {
                console.error('WebSocket error:', error);
                document.getElementById('connection-status').textContent = 'Error';
                document.querySelector('.status-dot').style.background = '#F44336';
            };
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                // Load all dashboard sections
                await Promise.all([
                    loadExecutiveMetrics(),
                    loadAgentHealth(),
                    loadSystemHealth(),
                    loadActiveTasks(),
                    loadRevenueChart(),
                    loadCampaignChart(),
                    loadAIAnalytics(),
                    loadRealtimeMetrics()
                ]);
                
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }
        
        // Load executive metrics
        async function loadExecutiveMetrics() {
            try {
                const response = await fetch('/api/dashboard/executive');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const data = result.data;
                    document.getElementById('executive-metrics').innerHTML = \`
                        <div class="metric">
                            <span>Total Revenue</span>
                            <span class="metric-value success">$\${(data.total_revenue || 0).toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span>Total Orders</span>
                            <span class="metric-value">\${data.total_orders || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Conversion Rate</span>
                            <span class="metric-value">\${((data.avg_conversion_rate || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span>Average Order Value</span>
                            <span class="metric-value">$\${(data.avg_order_value || 0).toFixed(2)}</span>
                        </div>
                        <div class="metric">
                            <span>AI Interactions</span>
                            <span class="metric-value">\${data.total_ai_interactions || 0}</span>
                        </div>
                        <div class="metric">
                            <span>AI Conversion Rate</span>
                            <span class="metric-value">\${((data.avg_ai_conversion_rate || 0) * 100).toFixed(1)}%</span>
                        </div>
                    \`;
                } else {
                    document.getElementById('executive-metrics').innerHTML = '<div class="loading">No data available</div>';
                }
            } catch (error) {
                document.getElementById('executive-metrics').innerHTML = '<div class="loading">Failed to load metrics</div>';
            }
        }
        
        // Load agent health
        async function loadAgentHealth() {
            try {
                const response = await fetch('/api/dashboard/agents');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const agents = result.data;
                    const agentGrid = agents.map(agent => {
                        const statusClass = agent.current_success_rate < 0.8 ? 'error' : 
                                          agent.current_success_rate < 0.95 ? 'warning' : '';
                        
                        return \`
                            <div class="agent-card \${statusClass}">
                                <div class="agent-name">\${agent.agent_name}</div>
                                <div class="agent-stats">
                                    Success: \${(agent.current_success_rate * 100).toFixed(1)}%<br>
                                    Response: \${agent.avg_response_time}ms<br>
                                    Tasks: \${agent.active_tasks}
                                </div>
                            </div>
                        \`;
                    }).join('');
                    
                    document.getElementById('agent-health').innerHTML = \`
                        <div class="agent-grid">\${agentGrid}</div>
                    \`;
                } else {
                    document.getElementById('agent-health').innerHTML = '<div class="loading">No agent data available</div>';
                }
            } catch (error) {
                document.getElementById('agent-health').innerHTML = '<div class="loading">Failed to load agent health</div>';
            }
        }
        
        // Load system health
        async function loadSystemHealth() {
            try {
                const response = await fetch('/api/dashboard/system-health');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const health = result.data;
                    let healthHTML = '';
                    
                    Object.entries(health).forEach(([type, components]) => {
                        components.forEach(component => {
                            const statusClass = component.status === 'healthy' ? 'success' : 
                                              component.status === 'warning' ? 'warning' : 'error';
                            
                            healthHTML += \`
                                <div class="metric">
                                    <span>\${component.component_name}</span>
                                    <span class="metric-value \${statusClass}">\${component.status}</span>
                                </div>
                            \`;
                        });
                    });
                    
                    document.getElementById('system-health').innerHTML = healthHTML || '<div class="loading">No health data available</div>';
                } else {
                    document.getElementById('system-health').innerHTML = '<div class="loading">No health data available</div>';
                }
            } catch (error) {
                document.getElementById('system-health').innerHTML = '<div class="loading">Failed to load system health</div>';
            }
        }
        
        // Load active tasks
        async function loadActiveTasks() {
            try {
                const response = await fetch('/api/dashboard/tasks');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const tasks = result.data;
                    const taskList = tasks.map(task => \`
                        <div class="task-item">
                            <div class="task-title">\${task.description || task.task_type}</div>
                            <div class="task-meta">
                                Agent: \${task.agent_id} | Priority: \${task.priority} | Status: \${task.status}
                            </div>
                        </div>
                    \`).join('');
                    
                    document.getElementById('active-tasks').innerHTML = \`
                        <div class="task-list">\${taskList || '<div class="loading">No active tasks</div>'}</div>
                    \`;
                } else {
                    document.getElementById('active-tasks').innerHTML = '<div class="loading">No tasks available</div>';
                }
            } catch (error) {
                document.getElementById('active-tasks').innerHTML = '<div class="loading">Failed to load tasks</div>';
            }
        }
        
        // Load revenue chart
        async function loadRevenueChart() {
            try {
                const response = await fetch('/api/dashboard/business-kpis?days=14');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const data = result.data;
                    const labels = data.map(d => new Date(d.kpi_date).toLocaleDateString());
                    const revenues = data.map(d => d.revenue_total || 0);
                    
                    const ctx = document.getElementById('revenueChart').getContext('2d');
                    
                    if (revenueChart) {
                        revenueChart.destroy();
                    }
                    
                    revenueChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Revenue',
                                data: revenues,
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            return '$' + value.toLocaleString();
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            } catch (error) {
                console.error('Failed to load revenue chart:', error);
            }
        }
        
        // Load campaign chart
        async function loadCampaignChart() {
            try {
                const response = await fetch('/api/dashboard/campaigns?days=7');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const campaigns = result.data;
                    const platforms = Object.keys(campaigns);
                    const roas = platforms.map(platform => {
                        const platformData = campaigns[platform];
                        const avgRoas = platformData.reduce((sum, c) => sum + (c.roas || 0), 0) / platformData.length;
                        return avgRoas;
                    });
                    
                    const ctx = document.getElementById('campaignChart').getContext('2d');
                    
                    if (campaignChart) {
                        campaignChart.destroy();
                    }
                    
                    campaignChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: platforms.map(p => p.charAt(0).toUpperCase() + p.slice(1)),
                            datasets: [{
                                label: 'ROAS',
                                data: roas,
                                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            return value.toFixed(1) + 'x';
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            } catch (error) {
                console.error('Failed to load campaign chart:', error);
            }
        }
        
        // Load AI analytics
        async function loadAIAnalytics() {
            try {
                const response = await fetch('/api/dashboard/ai-interactions?days=7');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const analytics = result.data;
                    const dates = Object.keys(analytics).sort();
                    
                    let totalInteractions = 0;
                    let totalConversions = 0;
                    
                    dates.forEach(date => {
                        totalInteractions += analytics[date].total;
                        totalConversions += analytics[date].conversions;
                    });
                    
                    const conversionRate = totalInteractions > 0 ? (totalConversions / totalInteractions * 100).toFixed(1) : 0;
                    
                    document.getElementById('ai-analytics').innerHTML = \`
                        <div class="metric">
                            <span>Total Interactions</span>
                            <span class="metric-value">\${totalInteractions}</span>
                        </div>
                        <div class="metric">
                            <span>Conversions</span>
                            <span class="metric-value success">\${totalConversions}</span>
                        </div>
                        <div class="metric">
                            <span>Conversion Rate</span>
                            <span class="metric-value">\${conversionRate}%</span>
                        </div>
                        <div class="metric">
                            <span>Daily Average</span>
                            <span class="metric-value">\${Math.round(totalInteractions / Math.max(dates.length, 1))}</span>
                        </div>
                    \`;
                } else {
                    document.getElementById('ai-analytics').innerHTML = '<div class="loading">No AI data available</div>';
                }
            } catch (error) {
                document.getElementById('ai-analytics').innerHTML = '<div class="loading">Failed to load AI analytics</div>';
            }
        }
        
        // Load real-time metrics
        async function loadRealtimeMetrics() {
            try {
                const response = await fetch('/api/dashboard/realtime');
                const result = await response.json();
                
                if (result.success && result.data) {
                    const metrics = result.data;
                    let metricsHTML = '';
                    
                    Object.entries(metrics).forEach(([name, data]) => {
                        const displayName = name.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        const value = typeof data.value === 'number' ? 
                                    (name.includes('revenue') ? '$' + data.value.toFixed(2) :
                                     name.includes('percentage') || name.includes('uptime') ? data.value.toFixed(1) + '%' :
                                     Math.round(data.value)) : data.value;
                        
                        metricsHTML += \`
                            <div class="metric">
                                <span>\${displayName}</span>
                                <span class="metric-value">\${value}</span>
                            </div>
                        \`;
                    });
                    
                    document.getElementById('realtime-metrics').innerHTML = metricsHTML || '<div class="loading">No real-time data available</div>';
                } else {
                    document.getElementById('realtime-metrics').innerHTML = '<div class="loading">No real-time data available</div>';
                }
            } catch (error) {
                document.getElementById('realtime-metrics').innerHTML = '<div class="loading">Failed to load real-time metrics</div>';
            }
        }
        
        // Update real-time data from WebSocket
        function updateRealtimeData(data) {
            // Update agent health if data is available
            if (data.agents && data.agents.length > 0) {
                const agentGrid = data.agents.map(agent => {
                    const statusClass = agent.current_success_rate < 0.8 ? 'error' : 
                                      agent.current_success_rate < 0.95 ? 'warning' : '';
                    
                    return \`
                        <div class="agent-card \${statusClass}">
                            <div class="agent-name">\${agent.agent_name}</div>
                            <div class="agent-stats">
                                Success: \${(agent.current_success_rate * 100).toFixed(1)}%<br>
                                Response: \${agent.avg_response_time}ms<br>
                                Tasks: \${agent.active_tasks}
                            </div>
                        </div>
                    \`;
                }).join('');
                
                document.getElementById('agent-health').innerHTML = \`
                    <div class="agent-grid">\${agentGrid}</div>
                \`;
            }
            
            // Update tasks if data is available
            if (data.tasks && data.tasks.length > 0) {
                const taskList = data.tasks.map(task => \`
                    <div class="task-item">
                        <div class="task-title">\${task.description || task.task_type}</div>
                        <div class="task-meta">
                            Agent: \${task.agent_id} | Priority: \${task.priority} | Status: \${task.status}
                        </div>
                    </div>
                \`).join('');
                
                document.getElementById('active-tasks').innerHTML = \`
                    <div class="task-list">\${taskList}</div>
                \`;
            }
        }
        
        // Refresh dashboard
        function refreshDashboard() {
            loadDashboard();
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            initWebSocket();
            
            // Refresh dashboard every 2 minutes
            setInterval(loadDashboard, 120000);
        });
    </script>
</body>
</html>
    `;
}

export { app };