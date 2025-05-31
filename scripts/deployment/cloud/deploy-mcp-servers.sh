#!/bin/bash
set -e

# Configuration
DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"
SSH_USER="root"
PASSPHRASE="freedom"

echo "🚀 Deploying Pinterest and Email Marketing MCP Servers to DigitalOcean Droplet..."
echo "Droplet IP: $DROPLET_IP"

# Function to run SSH commands
run_ssh() {
    local command="$1"
    echo "🔧 Executing: $command"
    ssh -i ~/.ssh/digitalocean -o StrictHostKeyChecking=no $SSH_USER@$DROPLET_IP "$command"
}

# Function to upload files
upload_files() {
    local local_path="$1"
    local remote_path="$2"
    echo "📤 Uploading: $local_path -> $remote_path"
    scp -i ~/.ssh/digitalocean -o StrictHostKeyChecking=no -r "$local_path" $SSH_USER@$DROPLET_IP:"$remote_path"
}

echo "📋 Step 1: Checking droplet connectivity..."
run_ssh "echo 'Connected successfully!' && whoami && pwd"

echo "📋 Step 2: Creating MCP servers directory structure..."
run_ssh "mkdir -p /opt/mcp-servers"
run_ssh "mkdir -p /opt/mcp-servers/pinterest-mcp-server"
run_ssh "mkdir -p /opt/mcp-servers/email-marketing-mcp-server"

echo "📋 Step 3: Installing system dependencies..."
run_ssh "apt update && apt install -y python3 python3-pip python3-venv curl"

echo "📋 Step 4: Uploading Pinterest MCP Server..."
upload_files "/Users/kinglerbercy/Projects/vivid_mas/mcp/pinterest-mcp-server" "/opt/mcp-servers/"

echo "📋 Step 5: Uploading Email Marketing MCP Server..."
upload_files "/Users/kinglerbercy/Projects/vivid_mas/mcp/email-marketing-mcp-server" "/opt/mcp-servers/"

echo "📋 Step 6: Setting up Pinterest MCP Server..."
run_ssh "cd /opt/mcp-servers/pinterest-mcp-server && python3 -m venv venv"
run_ssh "cd /opt/mcp-servers/pinterest-mcp-server && source venv/bin/activate && pip install --upgrade pip"
run_ssh "cd /opt/mcp-servers/pinterest-mcp-server && source venv/bin/activate && pip install -r requirements.txt"

echo "📋 Step 7: Setting up Email Marketing MCP Server..."
run_ssh "cd /opt/mcp-servers/email-marketing-mcp-server && python3 -m venv venv"
run_ssh "cd /opt/mcp-servers/email-marketing-mcp-server && source venv/bin/activate && pip install --upgrade pip"
run_ssh "cd /opt/mcp-servers/email-marketing-mcp-server && source venv/bin/activate && pip install -r requirements.txt"

echo "📋 Step 8: Creating environment files..."
run_ssh "cd /opt/mcp-servers/pinterest-mcp-server && cp .env.example .env"
run_ssh "cd /opt/mcp-servers/email-marketing-mcp-server && cp .env.example .env"

echo "📋 Step 9: Creating systemd service files..."

# Pinterest MCP Server service
run_ssh "cat > /etc/systemd/system/pinterest-mcp.service << 'EOL'
[Unit]
Description=Pinterest MCP Server for VividWalls
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mcp-servers/pinterest-mcp-server
Environment=PATH=/opt/mcp-servers/pinterest-mcp-server/venv/bin
ExecStart=/opt/mcp-servers/pinterest-mcp-server/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL"

# Email Marketing MCP Server service
run_ssh "cat > /etc/systemd/system/email-marketing-mcp.service << 'EOL'
[Unit]
Description=Email Marketing MCP Server for VividWalls
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mcp-servers/email-marketing-mcp-server
Environment=PATH=/opt/mcp-servers/email-marketing-mcp-server/venv/bin
ExecStart=/opt/mcp-servers/email-marketing-mcp-server/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL"

echo "📋 Step 10: Enabling and starting services..."
run_ssh "systemctl daemon-reload"
run_ssh "systemctl enable pinterest-mcp.service"
run_ssh "systemctl enable email-marketing-mcp.service"

echo "📋 Step 11: Creating startup script for n8n integration..."
run_ssh "cat > /opt/mcp-servers/start-mcp-servers.sh << 'EOL'
#!/bin/bash
echo \"Starting VividWalls MCP Servers...\"

# Start Pinterest MCP Server
echo \"Starting Pinterest MCP Server...\"
systemctl start pinterest-mcp.service
sleep 2

# Start Email Marketing MCP Server
echo \"Starting Email Marketing MCP Server...\"
systemctl start email-marketing-mcp.service
sleep 2

# Check status
echo \"MCP Servers Status:\"
systemctl status pinterest-mcp.service --no-pager -l
systemctl status email-marketing-mcp.service --no-pager -l

echo \"MCP Servers are ready for n8n integration!\"
EOL"

run_ssh "chmod +x /opt/mcp-servers/start-mcp-servers.sh"

echo "📋 Step 12: Creating configuration file for n8n MCP client..."
run_ssh "cat > /opt/mcp-servers/n8n-mcp-config.json << 'EOL'
{
  \"mcpServers\": {
    \"pinterest-mcp\": {
      \"command\": \"python\",
      \"args\": [\"/opt/mcp-servers/pinterest-mcp-server/server.py\"],
      \"cwd\": \"/opt/mcp-servers/pinterest-mcp-server\",
      \"env\": {
        \"PINTEREST_ACCESS_TOKEN\": \"YOUR_PINTEREST_TOKEN_HERE\"
      }
    },
    \"email-marketing-mcp\": {
      \"command\": \"python\",
      \"args\": [\"/opt/mcp-servers/email-marketing-mcp-server/server.py\"],
      \"cwd\": \"/opt/mcp-servers/email-marketing-mcp-server\",
      \"env\": {
        \"EMAIL_PROVIDER\": \"sendgrid\",
        \"SENDGRID_API_KEY\": \"YOUR_SENDGRID_API_KEY_HERE\",
        \"MAILCHIMP_API_KEY\": \"YOUR_MAILCHIMP_API_KEY_HERE\"
      }
    }
  }
}
EOL"

echo "📋 Step 13: Testing MCP servers installation..."
run_ssh "cd /opt/mcp-servers/pinterest-mcp-server && source venv/bin/activate && python -c 'import mcp; print(\"MCP library imported successfully\")'"
run_ssh "cd /opt/mcp-servers/email-marketing-mcp-server && source venv/bin/activate && python -c 'import mcp; print(\"MCP library imported successfully\")'"

echo "📋 Step 14: Creating deployment summary..."
run_ssh "cat > /opt/mcp-servers/DEPLOYMENT_SUMMARY.md << 'EOL'
# VividWalls MCP Servers Deployment Summary

## Deployment Date
$(date)

## Installed Servers
1. **Pinterest MCP Server**
   - Location: /opt/mcp-servers/pinterest-mcp-server/
   - Service: pinterest-mcp.service
   - Status: Installed, ready for configuration

2. **Email Marketing MCP Server**
   - Location: /opt/mcp-servers/email-marketing-mcp-server/
   - Service: email-marketing-mcp.service
   - Status: Installed, ready for configuration

## Next Steps
1. Configure API tokens in .env files
2. Start services: sudo systemctl start pinterest-mcp email-marketing-mcp
3. Integrate with n8n using /opt/mcp-servers/n8n-mcp-config.json
4. Test functionality with n8n workflows

## Management Commands
- Start all: /opt/mcp-servers/start-mcp-servers.sh
- Check status: systemctl status pinterest-mcp email-marketing-mcp
- View logs: journalctl -u pinterest-mcp -f
- Restart: systemctl restart pinterest-mcp email-marketing-mcp

## Configuration Files
- Pinterest: /opt/mcp-servers/pinterest-mcp-server/.env
- Email Marketing: /opt/mcp-servers/email-marketing-mcp-server/.env
- n8n Config: /opt/mcp-servers/n8n-mcp-config.json
EOL"

echo "📋 Step 15: Setting proper permissions..."
run_ssh "chown -R root:root /opt/mcp-servers"
run_ssh "chmod -R 755 /opt/mcp-servers"
run_ssh "chmod 600 /opt/mcp-servers/*/\.env"

echo "📋 Step 16: Final system check..."
run_ssh "ls -la /opt/mcp-servers/"
run_ssh "systemctl list-unit-files | grep mcp"

echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Deployment Summary:"
echo "- Pinterest MCP Server: Deployed to /opt/mcp-servers/pinterest-mcp-server/"
echo "- Email Marketing MCP Server: Deployed to /opt/mcp-servers/email-marketing-mcp-server/"
echo "- Systemd services created and enabled"
echo "- n8n configuration file ready"
echo ""
echo "🔧 Next Steps:"
echo "1. Configure API tokens in .env files"
echo "2. Start services: ssh -i ~/.ssh/digitalocean root@157.230.13.13 '/opt/mcp-servers/start-mcp-servers.sh'"
echo "3. Integrate with n8n MCP client using the config file"
echo ""
echo "📱 Access the droplet:"
echo "ssh -i ~/.ssh/digitalocean root@157.230.13.13"