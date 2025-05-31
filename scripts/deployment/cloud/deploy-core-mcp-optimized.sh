#!/bin/bash

# Optimized Core MCP Servers Deployment
# Excludes node_modules and rebuilds on droplet

set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"
MCP_BASE_DIR="/opt/mcp-servers"

echo "🚀 Deploying Core MCP Servers (Optimized)..."

# Function to run commands on droplet
run_on_droplet() {
    ssh -i "$SSH_KEY" root@"$DROPLET_IP" "$1"
}

# Function to copy files to droplet excluding heavy directories
copy_optimized() {
    rsync -avz -e "ssh -i $SSH_KEY" --exclude='node_modules' --exclude='venv' --exclude='build' --exclude='dist' --exclude='coverage' "$1" root@"$DROPLET_IP":"$2"
}

echo "📦 1. Creating optimized MCP packages..."

# Create temp directory
mkdir -p /tmp/mcp-optimized/{shopify,facebook-ads,n8n}

# Prepare Shopify MCP (exclude node_modules)
echo "  📋 Shopify MCP..."
cp -r mcp/shopify-mcp-server/* /tmp/mcp-optimized/shopify/ 2>/dev/null || true
rm -rf /tmp/mcp-optimized/shopify/node_modules /tmp/mcp-optimized/shopify/build

# Prepare Facebook Ads MCP (exclude venv)
echo "  📋 Facebook Ads MCP..."
cp -r mcp/facebook-ads-mcp-server/* /tmp/mcp-optimized/facebook-ads/ 2>/dev/null || true
rm -rf /tmp/mcp-optimized/facebook-ads/venv

# Create lightweight n8n MCP server
echo "  📋 n8n MCP..."
cat > /tmp/mcp-optimized/n8n/server.py << 'EOF'
#!/usr/bin/env python3
import json
import os
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

N8N_API_URL = os.getenv('N8N_API_URL', 'http://localhost:5678/api/v1')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

app = Server("n8n-mcp")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="list_workflows", description="List n8n workflows", inputSchema={"type": "object", "properties": {}}),
        Tool(name="execute_workflow", description="Execute workflow", inputSchema={"type": "object", "properties": {"workflow_id": {"type": "string"}, "data": {"type": "object"}}, "required": ["workflow_id"]}),
        Tool(name="get_workflow", description="Get workflow details", inputSchema={"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]})
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    headers = {'X-N8N-API-KEY': N8N_API_KEY, 'Content-Type': 'application/json'}
    
    async with httpx.AsyncClient() as client:
        if name == "list_workflows":
            response = await client.get(f"{N8N_API_URL}/workflows", headers=headers)
        elif name == "execute_workflow":
            workflow_id = arguments["workflow_id"]
            data = arguments.get("data", {})
            response = await client.post(f"{N8N_API_URL}/workflows/{workflow_id}/execute", headers=headers, json=data)
        elif name == "get_workflow":
            workflow_id = arguments["workflow_id"]
            response = await client.get(f"{N8N_API_URL}/workflows/{workflow_id}", headers=headers)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
EOF

cat > /tmp/mcp-optimized/n8n/requirements.txt << 'EOF'
mcp==1.0.0
httpx==0.27.0
EOF

echo "📤 2. Transferring optimized packages..."

# Create directories on droplet
run_on_droplet "mkdir -p $MCP_BASE_DIR/{shopify-mcp-server,facebook-ads-mcp-server,n8n-mcp-server}"

# Transfer optimized packages
copy_optimized "/tmp/mcp-optimized/shopify/" "$MCP_BASE_DIR/shopify-mcp-server/"
copy_optimized "/tmp/mcp-optimized/facebook-ads/" "$MCP_BASE_DIR/facebook-ads-mcp-server/"
copy_optimized "/tmp/mcp-optimized/n8n/" "$MCP_BASE_DIR/n8n-mcp-server/"

echo "🔧 3. Installing dependencies on droplet..."

# Install Shopify MCP
run_on_droplet "cd $MCP_BASE_DIR/shopify-mcp-server && npm install && npm run build"

# Install Facebook Ads MCP
run_on_droplet "cd $MCP_BASE_DIR/facebook-ads-mcp-server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Install n8n MCP
run_on_droplet "cd $MCP_BASE_DIR/n8n-mcp-server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo "🔑 4. Creating environment files..."

# Environment files with placeholder tokens
run_on_droplet "cat > $MCP_BASE_DIR/shopify-mcp-server/.env << 'EOF'
SHOPIFY_STORE_URL=vividwalls-2.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-shopify-access-token-here
SHOPIFY_API_VERSION=2024-01
NODE_ENV=production
EOF"

run_on_droplet "cat > $MCP_BASE_DIR/facebook-ads-mcp-server/.env << 'EOF'
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token-here
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_AD_ACCOUNT_ID=your-ad-account-id-here
EOF"

run_on_droplet "cat > $MCP_BASE_DIR/n8n-mcp-server/.env << 'EOF'
N8N_API_URL=http://localhost:5678/api/v1
N8N_API_KEY=your-n8n-api-key-here
EOF"

echo "🎛️ 5. Creating systemd services..."

# Shopify MCP Service
run_on_droplet "cat > /etc/systemd/system/shopify-mcp.service << 'EOF'
[Unit]
Description=Shopify MCP Server for VividWalls
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MCP_BASE_DIR/shopify-mcp-server
Environment=NODE_ENV=production
ExecStart=/usr/bin/node build/index.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

# Facebook Ads MCP Service
run_on_droplet "cat > /etc/systemd/system/facebook-ads-mcp.service << 'EOF'
[Unit]
Description=Facebook Ads MCP Server for VividWalls
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MCP_BASE_DIR/facebook-ads-mcp-server
ExecStart=$MCP_BASE_DIR/facebook-ads-mcp-server/venv/bin/python server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

# n8n MCP Service
run_on_droplet "cat > /etc/systemd/system/n8n-mcp.service << 'EOF'
[Unit]
Description=n8n MCP Server for VividWalls
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MCP_BASE_DIR/n8n-mcp-server
ExecStart=$MCP_BASE_DIR/n8n-mcp-server/venv/bin/python server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

echo "🚀 6. Enabling services..."

run_on_droplet "systemctl daemon-reload"
run_on_droplet "systemctl enable shopify-mcp facebook-ads-mcp n8n-mcp"

echo "📋 7. Creating management scripts..."

run_on_droplet "cat > $MCP_BASE_DIR/start-all-mcp-servers.sh << 'EOF'
#!/bin/bash
echo \"🚀 Starting All MCP Servers...\"
systemctl start pinterest-mcp email-marketing-mcp shopify-mcp facebook-ads-mcp n8n-mcp
sleep 3
echo \"📊 Status Check:\"
systemctl status pinterest-mcp email-marketing-mcp shopify-mcp facebook-ads-mcp n8n-mcp --no-pager
EOF"

run_on_droplet "cat > $MCP_BASE_DIR/status-all-mcp.sh << 'EOF'
#!/bin/bash
echo \"=== VividWalls MCP Servers Status ===\" 
echo \"📍 Pinterest MCP:\"
systemctl is-active pinterest-mcp
echo \"📧 Email Marketing MCP:\"
systemctl is-active email-marketing-mcp
echo \"🛒 Shopify MCP:\"
systemctl is-active shopify-mcp
echo \"📱 Facebook Ads MCP:\"
systemctl is-active facebook-ads-mcp
echo \"⚡ n8n MCP:\"
systemctl is-active n8n-mcp
echo \"\"
echo \"=== Recent Logs (Last 5 lines each) ===\" 
for service in pinterest-mcp email-marketing-mcp shopify-mcp facebook-ads-mcp n8n-mcp; do
    echo \"--- $service ---\"
    journalctl -u $service --since \"5 minutes ago\" --no-pager | tail -3
done
EOF"

run_on_droplet "chmod +x $MCP_BASE_DIR/start-all-mcp-servers.sh"
run_on_droplet "chmod +x $MCP_BASE_DIR/status-all-mcp.sh"

echo "📝 8. Creating unified MCP configuration..."

run_on_droplet "cat > $MCP_BASE_DIR/vividwalls-mcp-config.json << 'EOF'
{
  \"description\": \"VividWalls Complete MCP Server Configuration\",
  \"mcpServers\": {
    \"shopify-mcp\": {
      \"command\": \"node\",
      \"args\": [\"$MCP_BASE_DIR/shopify-mcp-server/build/index.js\"],
      \"cwd\": \"$MCP_BASE_DIR/shopify-mcp-server\",
      \"env\": {
        \"SHOPIFY_STORE_URL\": \"vividwalls-2.myshopify.com\",
        \"SHOPIFY_ACCESS_TOKEN\": \"your-shopify-access-token-here\",
        \"SHOPIFY_API_VERSION\": \"2024-01\"
      }
    },
    \"facebook-ads-mcp\": {
      \"command\": \"$MCP_BASE_DIR/facebook-ads-mcp-server/venv/bin/python\",
      \"args\": [\"$MCP_BASE_DIR/facebook-ads-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/facebook-ads-mcp-server\"
    },
    \"n8n-mcp\": {
      \"command\": \"$MCP_BASE_DIR/n8n-mcp-server/venv/bin/python\",
      \"args\": [\"$MCP_BASE_DIR/n8n-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/n8n-mcp-server\"
    },
    \"pinterest-mcp\": {
      \"command\": \"python\",
      \"args\": [\"$MCP_BASE_DIR/pinterest-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/pinterest-mcp-server\"
    },
    \"email-marketing-mcp\": {
      \"command\": \"python\",
      \"args\": [\"$MCP_BASE_DIR/email-marketing-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/email-marketing-mcp-server\"
    }
  }
}
EOF"

# Clean up
rm -rf /tmp/mcp-optimized

echo "✅ Core MCP Servers Deployment Complete!"
echo ""
echo "🎯 Deployment Summary:"
echo "  ✅ Shopify MCP Server deployed"
echo "  ✅ Facebook Ads MCP Server deployed" 
echo "  ✅ n8n MCP Server deployed"
echo "  ✅ All services configured and enabled"
echo ""
echo "📋 Management Commands:"
echo "  Start all: ssh -i $SSH_KEY root@$DROPLET_IP '$MCP_BASE_DIR/start-all-mcp-servers.sh'"
echo "  Check status: ssh -i $SSH_KEY root@$DROPLET_IP '$MCP_BASE_DIR/status-all-mcp.sh'"
echo ""
echo "🔑 Next Steps:"
echo "  1. Configure API credentials in .env files"
echo "  2. Start services and verify they're running"
echo "  3. Update local MCP config to use droplet endpoints"