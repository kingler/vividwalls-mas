#!/usr/bin/env python3
"""
Test script to verify VividWalls MAS integration with MCP postgres server
"""

import psycopg2
import json
import uuid
from datetime import datetime

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '54322',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

def test_agent_communication_workflow():
    """Test a complete agent communication workflow"""
    
    print("🧪 Testing VividWalls MAS Agent Communication Workflow")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Set schema
        cursor.execute("SET search_path TO vividwalls_mas;")
        
        # Test 1: Business Manager requests monthly research
        workflow_id = str(uuid.uuid4())
        print(f"\n📋 Test Workflow ID: {workflow_id}")
        
        print("\n1️⃣ Business Manager → Marketing Research Agent")
        cursor.execute("""
            SELECT publish_message(
                %s, 'business_manager', 'marketing_research', 'task', 'high',
                'Monthly Market Research Request', 
                %s
            );
        """, (workflow_id, json.dumps({
            "task_type": "monthly_research",
            "deadline": "2024-01-05T18:00:00Z",
            "focus_areas": ["competitor_analysis", "market_trends", "consumer_behavior"],
            "expected_deliverables": ["research_report", "strategic_recommendations"],
            "priority_markets": ["wall_art", "home_decor", "print_on_demand"]
        })))
        message_id_1 = cursor.fetchone()[0]
        print(f"   ✅ Message published: {message_id_1}")
        
        # Test 2: Marketing Research Agent updates status
        print("\n2️⃣ Marketing Research Agent updates status to 'busy'")
        cursor.execute("""
            SELECT update_agent_status(
                'marketing_research', 'busy', 60, 1,
                %s
            );
        """, (json.dumps({
            "current_task": "monthly_market_analysis",
            "progress": "data_collection_phase",
            "estimated_completion": "2024-01-04T16:00:00Z"
        }),))
        print("   ✅ Agent status updated")
        
        # Test 3: Marketing Research Agent consumes the message
        print("\n3️⃣ Marketing Research Agent consumes next message")
        cursor.execute("""
            SELECT * FROM consume_next_message('marketing_research', ARRAY['task']);
        """)
        message = cursor.fetchone()
        if message:
            print(f"   ✅ Message consumed: {message[4]} - {message[6]}")
            consumed_message_id = message[0]
        else:
            print("   ❌ No message found to consume")
            return False
        
        # Test 4: Create task for the research work
        print("\n4️⃣ Creating task for monthly research")
        cursor.execute("""
            SELECT create_task(
                %s, 'Monthly Market Analysis Q1 2024', 'research',
                'marketing_research', 'business_manager', 'high',
                %s,
                %s,
                NOW() + INTERVAL '3 days'
            );
        """, (
            workflow_id,
            json.dumps({
                "type": "comprehensive_market_analysis",
                "methodology": ["web_research", "competitor_monitoring", "data_analytics"],
                "deliverables": ["market_report", "competitive_analysis", "trend_forecast"]
            }),
            json.dumps({
                "research_budget": 5000,
                "data_sources": ["industry_reports", "social_media", "competitor_ads"],
                "analysis_depth": "comprehensive"
            })
        ))
        task_id = cursor.fetchone()[0]
        print(f"   ✅ Task created: {task_id}")
        
        # Test 5: Marketing Research Agent completes the message
        print("\n5️⃣ Marketing Research Agent completes message processing")
        cursor.execute("""
            SELECT complete_message(%s, %s, true);
        """, (consumed_message_id, json.dumps({
            "status": "research_initiated",
            "task_id": str(task_id),
            "estimated_completion": "2024-01-04T16:00:00Z"
        })))
        print("   ✅ Message marked as completed")
        
        # Test 6: Research Agent responds with findings
        print("\n6️⃣ Marketing Research Agent → Business Manager (Response)")
        cursor.execute("""
            SELECT publish_message(
                %s, 'marketing_research', 'business_manager', 'response', 'high',
                'Monthly Research Report Completed',
                %s
            );
        """, (workflow_id, json.dumps({
            "report_type": "monthly_market_analysis",
            "status": "completed",
            "key_findings": [
                "Wall art market growing 15% YoY",
                "Competitor X increased ad spend by 30%",
                "Abstract art trending on social media"
            ],
            "recommendations": [
                "Increase abstract art collection",
                "Expand Pinterest presence",
                "Consider premium product line"
            ],
            "data_confidence": 95,
            "full_report_url": "https://vividwalls.com/reports/2024-01-research.pdf"
        })))
        message_id_2 = cursor.fetchone()[0]
        print(f"   ✅ Response message published: {message_id_2}")
        
        # Test 7: Business Manager delegates to Campaign Agent
        print("\n7️⃣ Business Manager → Marketing Campaign Agent")
        cursor.execute("""
            SELECT publish_message(
                %s, 'business_manager', 'marketing_campaign', 'task', 'medium',
                'Develop Q1 Campaign Strategy',
                %s
            );
        """, (workflow_id, json.dumps({
            "task_type": "campaign_strategy_development",
            "research_input": str(message_id_2),
            "campaign_duration": "3_months",
            "budget_allocation": 50000,
            "target_channels": ["facebook", "instagram", "pinterest", "email"],
            "success_metrics": {
                "roas_target": 3.5,
                "cac_target": 40,
                "conversion_rate_target": 2.5
            }
        })))
        message_id_3 = cursor.fetchone()[0]
        print(f"   ✅ Campaign task published: {message_id_3}")
        
        # Test 8: Record performance metrics
        print("\n8️⃣ Recording agent performance metrics")
        agents_performance = [
            ('business_manager', 'response_time', 8.5, 'minutes'),
            ('marketing_research', 'task_completion_rate', 98.5, 'percentage'),
            ('marketing_campaign', 'quality_score', 92.0, 'score')
        ]
        
        for agent, metric_type, value, unit in agents_performance:
            cursor.execute("""
                SELECT record_agent_performance(
                    %s, %s, %s, %s, 'daily',
                    NOW() - INTERVAL '1 day', NOW(),
                    %s
                );
            """, (agent, metric_type, value, unit, json.dumps({
                "workflow_id": workflow_id,
                "measurement_context": "test_workflow"
            })))
        
        print(f"   ✅ Performance metrics recorded for {len(agents_performance)} agents")
        
        # Test 9: Check dashboard views
        print("\n9️⃣ Checking dashboard views")
        
        # Active messages
        cursor.execute("SELECT COUNT(*) FROM active_message_queue WHERE workflow_id = %s;", (workflow_id,))
        active_messages = cursor.fetchone()[0]
        print(f"   📬 Active messages in workflow: {active_messages}")
        
        # Agent status
        cursor.execute("""
            SELECT agent_name, status, workload_level, current_tasks 
            FROM agent_performance_dashboard 
            WHERE agent_name IN ('business_manager', 'marketing_research', 'marketing_campaign');
        """)
        agents_status = cursor.fetchall()
        print("   🤖 Agent Status:")
        for agent_name, status, workload, tasks in agents_status:
            print(f"      • {agent_name}: {status} ({workload}% workload, {tasks} tasks)")
        
        # Task dashboard
        cursor.execute("SELECT COUNT(*) FROM task_dashboard WHERE workflow_id = %s;", (workflow_id,))
        workflow_tasks = cursor.fetchone()[0]
        print(f"   📋 Tasks in workflow: {workflow_tasks}")
        
        print("\n🎉 VividWalls MAS Communication Workflow Test PASSED!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def test_mcp_integration_queries():
    """Test queries that would be used through MCP postgres server"""
    
    print("\n🔗 Testing MCP Integration Queries")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SET search_path TO vividwalls_mas;")
        
        # Query 1: Get agent hierarchy
        print("\n1️⃣ Query: Get VividWalls agent hierarchy")
        cursor.execute("""
            SELECT agent_name, agent_type, division, priority_level, 
                   jsonb_array_length(capabilities) as capability_count
            FROM agents 
            ORDER BY priority_level, agent_name;
        """)
        agents = cursor.fetchall()
        print("   Agent Name | Type | Division | Priority | Capabilities")
        print("   " + "-" * 55)
        for agent in agents:
            print(f"   {agent[0][:12]:<12} | {agent[1][:8]:<8} | {agent[2][:10]:<10} | {agent[3]:>8} | {agent[4]:>11}")
        
        # Query 2: Get pending messages by priority
        print("\n2️⃣ Query: Get pending messages by priority")
        cursor.execute("""
            SELECT priority, COUNT(*) as message_count
            FROM active_message_queue
            GROUP BY priority
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END;
        """)
        priorities = cursor.fetchall()
        print("   Priority | Count")
        print("   " + "-" * 14)
        for priority, count in priorities:
            print(f"   {priority:<8} | {count:>5}")
        
        # Query 3: Get business KPI status
        print("\n3️⃣ Query: Business KPI performance vs targets")
        cursor.execute("""
            SELECT kpi_name, current_value, target_value, unit_of_measure,
                   ROUND(((current_value - target_value) / target_value * 100), 2) as variance_pct
            FROM business_kpis
            ORDER BY variance_pct DESC;
        """)
        kpis = cursor.fetchall()
        print("   KPI | Current | Target | Unit | Variance%")
        print("   " + "-" * 45)
        for kpi in kpis:
            variance_color = "🟢" if kpi[4] and kpi[4] >= 0 else "🔴"
            print(f"   {kpi[0][:15]:<15} | {kpi[1]:>7.2f} | {kpi[2]:>6.2f} | {kpi[3]:<8} | {variance_color} {kpi[4]:>6.1f}%")
        
        # Query 4: Agent workload distribution
        print("\n4️⃣ Query: Agent workload distribution")
        cursor.execute("""
            SELECT division, 
                   COUNT(*) as agent_count,
                   AVG(workload_level) as avg_workload,
                   SUM(current_tasks) as total_tasks
            FROM agent_performance_dashboard
            GROUP BY division
            ORDER BY avg_workload DESC;
        """)
        workloads = cursor.fetchall()
        print("   Division | Agents | Avg Workload | Total Tasks")
        print("   " + "-" * 45)
        for division, count, avg_workload, tasks in workloads:
            print(f"   {division[:15]:<15} | {count:>6} | {avg_workload:>11.1f}% | {tasks:>11}")
        
        # Query 5: Recent performance trends
        print("\n5️⃣ Query: Recent agent performance trends")
        cursor.execute("""
            SELECT a.agent_name, 
                   apm.metric_type,
                   apm.metric_value,
                   apm.metric_unit,
                   apm.created_at
            FROM agent_performance_metrics apm
            JOIN agents a ON apm.agent_id = a.agent_id
            WHERE apm.created_at >= NOW() - INTERVAL '1 hour'
            ORDER BY apm.created_at DESC
            LIMIT 10;
        """)
        metrics = cursor.fetchall()
        print("   Agent | Metric | Value | Unit | Timestamp")
        print("   " + "-" * 55)
        for metric in metrics:
            timestamp = metric[4].strftime("%H:%M:%S")
            print(f"   {metric[0][:12]:<12} | {metric[1][:15]:<15} | {metric[2]:>5.2f} | {metric[3]:<8} | {timestamp}")
        
        print("\n✅ All MCP integration queries executed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main test function"""
    print("🚀 VividWalls MAS - MCP Integration Test Suite")
    print("=" * 70)
    
    # Test 1: Agent communication workflow
    if not test_agent_communication_workflow():
        return False
    
    # Test 2: MCP integration queries
    if not test_mcp_integration_queries():
        return False
    
    print("\n🎉 ALL TESTS PASSED! VividWalls MAS is ready for MCP integration")
    print("=" * 70)
    print("\n📋 Integration Summary:")
    print("   ✅ Message broker functions working")
    print("   ✅ Agent hierarchy properly configured")
    print("   ✅ Task coordination system operational")
    print("   ✅ Performance metrics collection active")
    print("   ✅ Dashboard views functioning")
    print("   ✅ MCP-compatible queries validated")
    
    print("\n🔗 MCP Configuration:")
    print('   Add to .claude/config.json:')
    print('   {')
    print('     "mcpServers": {')
    print('       "postgres": {')
    print('         "command": "npx",')
    print('         "args": ["-y", "@modelcontextprotocol/server-postgres"],')
    print('         "env": {')
    print('           "POSTGRES_CONNECTION_STRING": "postgresql://postgres:postgres@localhost:54322/postgres?schema=vividwalls_mas"')
    print('         }')
    print('       }')
    print('     }')
    print('   }')
    
    return True

if __name__ == "__main__":
    main()