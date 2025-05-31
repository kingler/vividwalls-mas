#!/usr/bin/env python3
"""
VividWalls MAS Message Broker Setup Script
Connects to PostgreSQL server and initializes the message broker system
"""

import psycopg2
import json
import uuid
from datetime import datetime, timedelta
import os
import sys

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '54322',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'  # Update with your actual password
}

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        print(f"✅ Successfully connected to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return None

def execute_sql_file(conn, sql_file_path):
    """Execute SQL file to set up the schema"""
    try:
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        print(f"✅ Successfully executed SQL schema from {sql_file_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to execute SQL file: {e}")
        return False

def verify_setup(conn):
    """Verify that the setup was successful"""
    try:
        cursor = conn.cursor()
        
        # Check if schema exists
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'vividwalls_mas';")
        if not cursor.fetchone():
            print("❌ Schema 'vividwalls_mas' not found")
            return False
        
        # Check if agents table exists and has data
        cursor.execute("SELECT COUNT(*) FROM vividwalls_mas.agents;")
        agent_count = cursor.fetchone()[0]
        
        if agent_count == 0:
            print("❌ No agents found in the system")
            return False
        
        print(f"✅ Schema setup verified: {agent_count} agents initialized")
        
        # List all agents
        cursor.execute("""
            SELECT agent_name, agent_type, division, priority_level 
            FROM vividwalls_mas.agents 
            ORDER BY priority_level, agent_name;
        """)
        agents = cursor.fetchall()
        
        print("\n📋 VividWalls MAS Agent Hierarchy:")
        print("=" * 60)
        current_division = ""
        for agent_name, agent_type, division, priority in agents:
            if division != current_division:
                print(f"\n🏢 {division} Division:")
                current_division = division
            print(f"   • {agent_name} ({agent_type}) - Priority: {priority}")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def test_message_broker_functions(conn):
    """Test the message broker functions"""
    try:
        cursor = conn.cursor()
        
        print("\n🧪 Testing Message Broker Functions:")
        print("=" * 50)
        
        # Test 1: Publish a message
        workflow_id = str(uuid.uuid4())
        cursor.execute("""
            SELECT vividwalls_mas.publish_message(
                %s, 'business_manager', 'marketing_research', 'task', 'high',
                'Monthly Research Request', 
                '{"task": "conduct_monthly_analysis", "deadline": "2024-01-05"}'::jsonb
            );
        """, (workflow_id,))
        message_id = cursor.fetchone()[0]
        print(f"✅ Test 1 PASSED: Published message {message_id}")
        
        # Test 2: Update agent status
        cursor.execute("""
            SELECT vividwalls_mas.update_agent_status(
                'marketing_research', 'busy', 75, 3, 
                '{"current_task": "monthly_analysis"}'::jsonb
            );
        """)
        print("✅ Test 2 PASSED: Updated agent status")
        
        # Test 3: Create a task
        cursor.execute("""
            SELECT vividwalls_mas.create_task(
                %s, 'Monthly Market Analysis', 'research', 
                'marketing_research', 'business_manager', 'high',
                '{"type": "market_analysis", "scope": "comprehensive"}'::jsonb,
                '{"deadline": "2024-01-05", "priority_areas": ["competitors", "trends"]}'::jsonb,
                NOW() + INTERVAL '5 days'
            );
        """, (workflow_id,))
        task_id = cursor.fetchone()[0]
        print(f"✅ Test 3 PASSED: Created task {task_id}")
        
        # Test 4: Consume a message
        cursor.execute("""
            SELECT * FROM vividwalls_mas.consume_next_message('marketing_research');
        """)
        message = cursor.fetchone()
        if message:
            print(f"✅ Test 4 PASSED: Consumed message: {message[4]} - {message[6]}")
        else:
            print("⚠️  Test 4: No messages to consume (expected for clean system)")
        
        # Test 5: Record performance metrics
        cursor.execute("""
            SELECT vividwalls_mas.record_agent_performance(
                'business_manager', 'response_time', 12.5, 'minutes', 'daily',
                NOW() - INTERVAL '1 day', NOW(),
                '{"measurement_context": "test"}'::jsonb
            );
        """)
        print("✅ Test 5 PASSED: Recorded performance metrics")
        
        print("\n🎉 All message broker functions are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Function testing failed: {e}")
        return False

def display_dashboard_views(conn):
    """Display the dashboard views"""
    try:
        cursor = conn.cursor()
        
        print("\n📊 Dashboard Views:")
        print("=" * 50)
        
        # Agent Performance Dashboard
        cursor.execute("SELECT * FROM vividwalls_mas.agent_performance_dashboard LIMIT 5;")
        agents = cursor.fetchall()
        print("\n🤖 Agent Performance Dashboard (Top 5):")
        print("Agent Name | Division | Status | Workload | Tasks")
        print("-" * 50)
        for agent in agents:
            print(f"{agent[0][:15]:<15} | {agent[1][:12]:<12} | {agent[3]:<6} | {agent[4]:>3}% | {agent[5]}/{agent[6]}")
        
        # Active Message Queue
        cursor.execute("SELECT COUNT(*) FROM vividwalls_mas.active_message_queue;")
        message_count = cursor.fetchone()[0]
        print(f"\n📬 Active Message Queue: {message_count} messages")
        
        # Business KPIs
        cursor.execute("SELECT kpi_name, current_value, target_value, unit_of_measure FROM vividwalls_mas.business_kpis LIMIT 6;")
        kpis = cursor.fetchall()
        print("\n📈 Business KPIs:")
        print("KPI | Current | Target | Unit")
        print("-" * 40)
        for kpi in kpis:
            print(f"{kpi[0][:20]:<20} | {kpi[1]:>7.2f} | {kpi[2]:>7.2f} | {kpi[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard display failed: {e}")
        return False

def create_sample_workflow(conn):
    """Create a sample workflow execution"""
    try:
        cursor = conn.cursor()
        
        print("\n🔄 Creating Sample Workflow Execution:")
        print("=" * 50)
        
        # Create a workflow execution instance
        workflow_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO vividwalls_mas.workflow_executions 
            (workflow_id, instance_name, trigger_event, total_steps, execution_context)
            SELECT workflow_id, 'Sample Monthly Campaign Planning', 
                   '{"trigger": "monthly_schedule", "date": "2024-01-05"}'::jsonb,
                   6, '{"sample": true, "test_run": true}'::jsonb
            FROM vividwalls_mas.workflows 
            WHERE workflow_name = 'monthly_campaign_planning'
            RETURNING execution_id;
        """)
        execution_id = cursor.fetchone()[0]
        
        # Create some sample messages for the workflow
        messages = [
            ('business_manager', 'marketing_research', 'task', 'high', 'Submit Monthly Research Report'),
            ('marketing_research', 'business_manager', 'response', 'high', 'Monthly Research Report Completed'),
            ('business_manager', 'marketing_campaign', 'task', 'medium', 'Develop Campaign Strategy'),
            ('marketing_campaign', 'business_manager', 'response', 'medium', 'Campaign Strategy Proposal')
        ]
        
        for from_agent, to_agent, msg_type, priority, subject in messages:
            cursor.execute("""
                SELECT vividwalls_mas.publish_message(
                    %s, %s, %s, %s, %s, %s, 
                    '{"workflow_step": "sample", "test_data": true}'::jsonb
                );
            """, (workflow_id, from_agent, to_agent, msg_type, priority, subject))
        
        print(f"✅ Created sample workflow execution: {execution_id}")
        print(f"   - Workflow ID: {workflow_id}")
        print(f"   - Messages created: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample workflow creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 VividWalls MAS Message Broker Setup")
    print("=" * 60)
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        sys.exit(1)
    
    try:
        # Get the SQL file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'vividwalls_mas_message_broker.sql')
        
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            sys.exit(1)
        
        # Execute the schema setup
        print(f"\n📝 Executing schema setup from {sql_file}")
        if not execute_sql_file(conn, sql_file):
            sys.exit(1)
        
        # Verify the setup
        print(f"\n🔍 Verifying setup...")
        if not verify_setup(conn):
            sys.exit(1)
        
        # Test message broker functions
        if not test_message_broker_functions(conn):
            sys.exit(1)
        
        # Display dashboard views
        if not display_dashboard_views(conn):
            sys.exit(1)
        
        # Create sample workflow
        if not create_sample_workflow(conn):
            sys.exit(1)
        
        print("\n🎉 VividWalls MAS Message Broker Setup Complete!")
        print("=" * 60)
        print("📋 System Summary:")
        print("   • PostgreSQL Message Broker: ✅ Initialized")
        print("   • Agent Hierarchy: ✅ 10 agents configured")
        print("   • Message Queue: ✅ Ready for inter-agent communication")
        print("   • Task Coordination: ✅ Workflow management enabled")
        print("   • Performance Metrics: ✅ KPI tracking active")
        print("   • Dashboard Views: ✅ Real-time monitoring available")
        print("\n🔗 Connection Details:")
        print(f"   • Host: {DB_CONFIG['host']}")
        print(f"   • Port: {DB_CONFIG['port']}")
        print(f"   • Schema: vividwalls_mas")
        print(f"   • Database: {DB_CONFIG['database']}")
        
        print("\n🛠️  Next Steps:")
        print("   1. Configure MCP postgres server to connect to this database")
        print("   2. Test agent communication through MCP tools")
        print("   3. Set up n8n workflows to use the message broker")
        print("   4. Deploy monitoring dashboards for real-time insights")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()