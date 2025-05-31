#!/bin/bash

# Test Caddy with Minimal Configuration
set -e

SERVER_IP="157.230.13.13"

echo "🔧 Creating minimal test Caddyfile..."

# Create minimal Caddyfile locally
cat > /tmp/Caddyfile_minimal << 'EOF'
{
    email kingler@vividwalls.co
}

n8n.vividwalls.blog {
    reverse_proxy 127.0.0.1:5678
}

webui.vividwalls.blog {
    reverse_proxy 127.0.0.1:3000
}

langfuse.vividwalls.blog {
    reverse_proxy 127.0.0.1:3002
}

vividwalls.blog {
    reverse_proxy 127.0.0.1:8080
}
EOF

echo "📤 Uploading minimal Caddyfile..."
scp -i ~/.ssh/digitalocean /tmp/Caddyfile_minimal root@${SERVER_IP}:/home/vivid/vivid_mas/Caddyfile

echo "🔄 Restarting Caddy..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cd /home/vivid/vivid_mas && docker-compose restart caddy"

echo "⏳ Waiting for Caddy to start..."
sleep 10

echo "✅ Checking Caddy status..."
CADDY_STATUS=$(ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker ps --filter name=caddy --format '{{.Status}}'")
echo "Caddy status: $CADDY_STATUS"

if echo "$CADDY_STATUS" | grep -q "Up"; then
    echo "🎉 Caddy is now running successfully with minimal config!"
else
    echo "❌ Still having issues. Checking logs..."
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker logs caddy --tail 10"
fi 