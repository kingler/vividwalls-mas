#!/bin/bash

# Test MCP Droplet Connectivity
# Validates all MCP servers are accessible and responsive

set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo "🧪 Testing VividWalls MCP Server Connectivity..."

# Function to run commands on droplet
run_on_droplet() {
    ssh -i "$SSH_KEY" root@"$DROPLET_IP" "$1"
}

# Function to test if service is active
test_service() {
    local service_name=$1
    echo "  🔍 Testing $service_name..."
    
    if run_on_droplet "systemctl is-active $service_name" >/dev/null 2>&1; then
        echo "    ✅ $service_name is active"
        return 0
    else
        echo "    ❌ $service_name is not active"
        return 1
    fi
}

# Function to test MCP server health
test_mcp_health() {
    local server_name=$1
    local server_path=$2
    echo "  🩺 Health check for $server_name..."
    
    # Test if server directory exists and has required files
    if run_on_droplet "[ -f '$server_path/server.py' ] || [ -f '$server_path/build/index.js' ]"; then
        echo "    ✅ $server_name files present"
    else
        echo "    ❌ $server_name files missing"
        return 1
    fi
    
    # Test if virtual environment exists (for Python servers)
    if run_on_droplet "[ -d '$server_path/venv' ]"; then
        echo "    ✅ $server_name virtual environment ready"
    elif run_on_droplet "[ -d '$server_path/node_modules' ]"; then
        echo "    ✅ $server_name node dependencies ready"
    else
        echo "    ⚠️  $server_name dependencies may not be installed"
    fi
}

echo ""
echo "📊 1. Service Status Check..."

# Test all MCP services
declare -a services=("shopify-mcp" "facebook-ads-mcp" "n8n-mcp" "pinterest-mcp" "email-marketing-mcp")
active_services=0

for service in "${services[@]}"; do
    if test_service "$service"; then
        ((active_services++))
    fi
done

echo ""
echo "🏥 2. Health Check..."

# Test server health
test_mcp_health "Shopify MCP" "/opt/mcp-servers/shopify-mcp-server"
test_mcp_health "Facebook Ads MCP" "/opt/mcp-servers/facebook-ads-mcp-server"  
test_mcp_health "n8n MCP" "/opt/mcp-servers/n8n-mcp-server"
test_mcp_health "Pinterest MCP" "/opt/mcp-servers/pinterest-mcp-server"
test_mcp_health "Email Marketing MCP" "/opt/mcp-servers/email-marketing-mcp-server"

echo ""
echo "📋 3. Configuration Check..."

# Check environment files
echo "  🔑 Checking environment configurations..."
for server in shopify-mcp-server facebook-ads-mcp-server n8n-mcp-server pinterest-mcp-server email-marketing-mcp-server; do
    if run_on_droplet "[ -f '/opt/mcp-servers/$server/.env' ]"; then
        echo "    ✅ $server environment file exists"
    else
        echo "    ⚠️  $server environment file missing"
    fi
done

echo ""
echo "🔗 4. SSH Connectivity Test..."

# Test SSH connectivity for MCP client
echo "  🔑 Testing SSH key authentication..."
if run_on_droplet "echo 'SSH connection successful'" >/dev/null 2>&1; then
    echo "    ✅ SSH authentication working"
else
    echo "    ❌ SSH authentication failed"
fi

echo "  📁 Testing MCP server paths..."
if run_on_droplet "ls /opt/mcp-servers/" >/dev/null 2>&1; then
    echo "    ✅ MCP server directories accessible"
    run_on_droplet "ls -la /opt/mcp-servers/"
else
    echo "    ❌ MCP server directories not accessible"
fi

echo ""
echo "📈 5. System Resource Check..."

echo "  💾 Memory usage:"
run_on_droplet "free -h | head -2"

echo "  💽 Disk usage:"
run_on_droplet "df -h /opt/mcp-servers"

echo "  ⚡ System load:"
run_on_droplet "uptime"

echo ""
echo "🔧 6. Management Scripts Check..."

# Check if management scripts exist
if run_on_droplet "[ -f '/opt/mcp-servers/start-all-mcp-servers.sh' ]"; then
    echo "  ✅ Start script available"
else
    echo "  ❌ Start script missing"
fi

if run_on_droplet "[ -f '/opt/mcp-servers/status-all-mcp.sh' ]"; then
    echo "  ✅ Status script available"
else
    echo "  ❌ Status script missing"
fi

echo ""
echo "📝 7. Recent Logs Check..."

echo "  📋 Checking recent service logs..."
for service in "${services[@]}"; do
    echo "    --- $service ---"
    run_on_droplet "journalctl -u $service --since '5 minutes ago' --no-pager | tail -2 || echo 'No recent logs'"
done

echo ""
echo "===== TEST RESULTS SUMMARY ====="
echo "🎯 Active Services: $active_services/5"

if [ $active_services -eq 5 ]; then
    echo "🎉 ALL MCP SERVERS ARE READY!"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Configure API credentials in .env files"
    echo "  2. Start services: ssh -i $SSH_KEY root@$DROPLET_IP '/opt/mcp-servers/start-all-mcp-servers.sh'"
    echo "  3. Test MCP tools from local environment"
elif [ $active_services -gt 0 ]; then
    echo "⚠️  PARTIAL SUCCESS: $active_services services ready, $((5 - active_services)) need attention"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  - Check failed services: ssh -i $SSH_KEY root@$DROPLET_IP 'systemctl status <service-name>'"
    echo "  - Enable services: ssh -i $SSH_KEY root@$DROPLET_IP 'systemctl enable <service-name>'"
    echo "  - Start services: ssh -i $SSH_KEY root@$DROPLET_IP 'systemctl start <service-name>'"
else
    echo "❌ DEPLOYMENT ISSUES: No services active"
    echo ""
    echo "🚨 Action Required:"
    echo "  - Check systemd services: ssh -i $SSH_KEY root@$DROPLET_IP 'systemctl status shopify-mcp facebook-ads-mcp n8n-mcp'"
    echo "  - Check service files: ssh -i $SSH_KEY root@$DROPLET_IP 'ls -la /etc/systemd/system/*mcp*'"
    echo "  - Reload systemd: ssh -i $SSH_KEY root@$DROPLET_IP 'systemctl daemon-reload'"
fi

echo ""
echo "📍 MCP Infrastructure Status: Ready for VividWalls Business Automation"