#!/bin/bash

# Deploy Core MCP Servers to DigitalOcean Droplet
# This script deploys Shopify, n8n, and Facebook Ads MCP servers

set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"
MCP_BASE_DIR="/opt/mcp-servers"

echo "🚀 Deploying Core MCP Servers to DigitalOcean Droplet..."

# Function to run commands on droplet
run_on_droplet() {
    ssh -i "$SSH_KEY" root@"$DROPLET_IP" "$1"
}

# Function to copy files to droplet
copy_to_droplet() {
    scp -i "$SSH_KEY" -r "$1" root@"$DROPLET_IP":"$2"
}

echo "📦 1. Preparing MCP servers for deployment..."

# Create deployment packages locally
mkdir -p /tmp/mcp-deployment/{shopify,n8n,facebook-ads}

# Prepare Shopify MCP Server
echo "  📋 Preparing Shopify MCP Server..."
cp -r mcp/shopify-mcp-server/* /tmp/mcp-deployment/shopify/

# Prepare Facebook Ads MCP Server  
echo "  📋 Preparing Facebook Ads MCP Server..."
cp -r mcp/facebook-ads-mcp-server/* /tmp/mcp-deployment/facebook-ads/

# Create n8n MCP server package (we'll use a lightweight proxy)
echo "  📋 Preparing n8n MCP Server..."
cat > /tmp/mcp-deployment/n8n/server.py << 'EOF'
#!/usr/bin/env python3
"""
n8n MCP Server Proxy
Routes MCP requests to local n8n instance
"""
import json
import os
import sys
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

# Environment configuration
N8N_API_URL = os.getenv('N8N_API_URL', 'http://localhost:5678/api/v1')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

app = Server("n8n-mcp")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available n8n tools"""
    return [
        Tool(
            name="list_workflows",
            description="List all n8n workflows",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="execute_workflow",
            description="Execute an n8n workflow",
            inputSchema={
                "type": "object", 
                "properties": {
                    "workflow_id": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="get_workflow",
            description="Get workflow details",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"}
                },
                "required": ["workflow_id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls to n8n API"""
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        if name == "list_workflows":
            response = await client.get(f"{N8N_API_URL}/workflows", headers=headers)
            
        elif name == "execute_workflow":
            workflow_id = arguments["workflow_id"]
            data = arguments.get("data", {})
            response = await client.post(
                f"{N8N_API_URL}/workflows/{workflow_id}/execute",
                headers=headers,
                json=data
            )
            
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

# Create requirements for n8n MCP
cat > /tmp/mcp-deployment/n8n/requirements.txt << 'EOF'
mcp==1.0.0
httpx==0.27.0
pydantic==2.10.3
EOF

# Create package.json for n8n MCP
cat > /tmp/mcp-deployment/n8n/package.json << 'EOF'
{
  "name": "n8n-mcp-server",
  "version": "1.0.0",
  "description": "n8n MCP Server for VividWalls",
  "main": "server.py",
  "scripts": {
    "start": "python server.py"
  }
}
EOF

echo "📤 2. Transferring MCP servers to droplet..."

# Transfer all servers
copy_to_droplet "/tmp/mcp-deployment/shopify" "$MCP_BASE_DIR/"
copy_to_droplet "/tmp/mcp-deployment/facebook-ads" "$MCP_BASE_DIR/"
copy_to_droplet "/tmp/mcp-deployment/n8n" "$MCP_BASE_DIR/n8n-mcp-server"

echo "🔧 3. Installing MCP servers on droplet..."

# Install Shopify MCP Server
run_on_droplet "cd $MCP_BASE_DIR/shopify && npm install && npm run build"

# Install Facebook Ads MCP Server
run_on_droplet "cd $MCP_BASE_DIR/facebook-ads && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Install n8n MCP Server
run_on_droplet "cd $MCP_BASE_DIR/n8n-mcp-server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo "🔑 4. Creating environment files..."

# Shopify environment
run_on_droplet "cat > $MCP_BASE_DIR/shopify/.env << 'EOF'
SHOPIFY_STORE_URL=vividwalls-2.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-shopify-access-token-here
SHOPIFY_API_VERSION=2024-01
NODE_ENV=production
EOF"

# Facebook Ads environment
run_on_droplet "cat > $MCP_BASE_DIR/facebook-ads/.env << 'EOF'
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token-here
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_AD_ACCOUNT_ID=your-ad-account-id-here
EOF"

# n8n MCP environment
run_on_droplet "cat > $MCP_BASE_DIR/n8n-mcp-server/.env << 'EOF'
N8N_API_URL=http://localhost:5678/api/v1
N8N_API_KEY=your-n8n-api-key-here
EOF"

echo "🎛️ 5. Creating systemd services..."

# Shopify MCP Service
run_on_droplet "cat > /etc/systemd/system/shopify-mcp.service << 'EOF'
[Unit]
Description=Shopify MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MCP_BASE_DIR/shopify
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
Description=Facebook Ads MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MCP_BASE_DIR/facebook-ads
ExecStart=$MCP_BASE_DIR/facebook-ads/venv/bin/python server.py
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
Description=n8n MCP Server
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

echo "🚀 6. Enabling and starting services..."

# Reload systemd and enable services
run_on_droplet "systemctl daemon-reload"
run_on_droplet "systemctl enable shopify-mcp facebook-ads-mcp n8n-mcp"

echo "📋 7. Creating management scripts..."

# Create start script
run_on_droplet "cat > $MCP_BASE_DIR/start-core-mcp-servers.sh << 'EOF'
#!/bin/bash
echo \"Starting Core MCP Servers...\"
systemctl start shopify-mcp
systemctl start facebook-ads-mcp  
systemctl start n8n-mcp
echo \"Checking status...\"
systemctl status shopify-mcp facebook-ads-mcp n8n-mcp --no-pager
EOF"

# Create status script
run_on_droplet "cat > $MCP_BASE_DIR/check-core-mcp-status.sh << 'EOF'
#!/bin/bash
echo \"=== Core MCP Servers Status ===\" 
systemctl status shopify-mcp facebook-ads-mcp n8n-mcp --no-pager
echo \"\"
echo \"=== Recent Logs ===\" 
echo \"--- Shopify MCP ---\"
journalctl -u shopify-mcp --since \"10 minutes ago\" --no-pager | tail -5
echo \"--- Facebook Ads MCP ---\"
journalctl -u facebook-ads-mcp --since \"10 minutes ago\" --no-pager | tail -5
echo \"--- n8n MCP ---\"
journalctl -u n8n-mcp --since \"10 minutes ago\" --no-pager | tail -5
EOF"

# Make scripts executable
run_on_droplet "chmod +x $MCP_BASE_DIR/start-core-mcp-servers.sh"
run_on_droplet "chmod +x $MCP_BASE_DIR/check-core-mcp-status.sh"

echo "📝 8. Creating unified MCP configuration..."

run_on_droplet "cat > $MCP_BASE_DIR/unified-mcp-config.json << 'EOF'
{
  \"mcpServers\": {
    \"shopify-mcp\": {
      \"command\": \"node\",
      \"args\": [\"$MCP_BASE_DIR/shopify/build/index.js\"],
      \"cwd\": \"$MCP_BASE_DIR/shopify\",
      \"env\": {
        \"SHOPIFY_STORE_URL\": \"vividwalls-2.myshopify.com\",
        \"SHOPIFY_ACCESS_TOKEN\": \"your-shopify-access-token-here\",
        \"SHOPIFY_API_VERSION\": \"2024-01\"
      }
    },
    \"facebook-ads-mcp\": {
      \"command\": \"$MCP_BASE_DIR/facebook-ads/venv/bin/python\",
      \"args\": [\"$MCP_BASE_DIR/facebook-ads/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/facebook-ads\",
      \"env\": {
        \"FACEBOOK_ACCESS_TOKEN\": \"your-facebook-access-token-here\",
        \"FACEBOOK_APP_ID\": \"your-facebook-app-id-here\", 
        \"FACEBOOK_APP_SECRET\": \"your-facebook-app-secret-here\",
        \"FACEBOOK_AD_ACCOUNT_ID\": \"your-ad-account-id-here\"
      }
    },
    \"n8n-mcp\": {
      \"command\": \"$MCP_BASE_DIR/n8n-mcp-server/venv/bin/python\",
      \"args\": [\"$MCP_BASE_DIR/n8n-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/n8n-mcp-server\",
      \"env\": {
        \"N8N_API_URL\": \"http://localhost:5678/api/v1\",
        \"N8N_API_KEY\": \"your-n8n-api-key-here\"
      }
    },
    \"pinterest-mcp\": {
      \"command\": \"python\",
      \"args\": [\"$MCP_BASE_DIR/pinterest-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/pinterest-mcp-server\",
      \"env\": {
        \"PINTEREST_ACCESS_TOKEN\": \"your-pinterest-token-here\"
      }
    },
    \"email-marketing-mcp\": {
      \"command\": \"python\",
      \"args\": [\"$MCP_BASE_DIR/email-marketing-mcp-server/server.py\"],
      \"cwd\": \"$MCP_BASE_DIR/email-marketing-mcp-server\",
      \"env\": {
        \"EMAIL_PROVIDER\": \"sendgrid\",
        \"SENDGRID_API_KEY\": \"your-sendgrid-api-key-here\",
        \"MAILCHIMP_API_KEY\": \"your-mailchimp-api-key-here\"
      }
    }
  }
}
EOF"

# Clean up local temp files
rm -rf /tmp/mcp-deployment

echo "✅ Core MCP Servers Deployment Complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Configure API credentials in .env files on droplet"
echo "2. Start services: ssh -i $SSH_KEY root@$DROPLET_IP '$MCP_BASE_DIR/start-core-mcp-servers.sh'"
echo "3. Check status: ssh -i $SSH_KEY root@$DROPLET_IP '$MCP_BASE_DIR/check-core-mcp-status.sh'"
echo "4. Update local MCP configuration to use droplet endpoints"
echo ""
echo "📍 Deployed MCP Servers:"
echo "  - Shopify MCP: $MCP_BASE_DIR/shopify (shopify-mcp.service)"
echo "  - Facebook Ads MCP: $MCP_BASE_DIR/facebook-ads (facebook-ads-mcp.service)"  
echo "  - n8n MCP: $MCP_BASE_DIR/n8n-mcp-server (n8n-mcp.service)"
echo "  - Pinterest MCP: $MCP_BASE_DIR/pinterest-mcp-server (pinterest-mcp.service)"
echo "  - Email Marketing MCP: $MCP_BASE_DIR/email-marketing-mcp-server (email-marketing-mcp.service)"