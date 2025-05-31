#!/bin/bash

# Fix Caddy Network Configuration
# Use proper Docker network addressing instead of localhost

set -e

SERVER_IP="157.230.13.13"

echo "🔧 Creating network-aware Caddyfile..."

# Create Caddyfile with proper Docker network addressing
cat > /tmp/Caddyfile_network << 'EOF'
{
    email kingler@vividwalls.co
}

n8n.vividwalls.blog {
    reverse_proxy n8n:5678
}

webui.vividwalls.blog {
    reverse_proxy open-webui:8080
}

langfuse.vividwalls.blog {
    reverse_proxy vivid_mas-langfuse-web-1:3000
}

vividwalls.blog {
    reverse_proxy wordpress-multisite:80
}

# Additional services for direct access
flowise.vividwalls.blog {
    reverse_proxy flowise:3001
}

ollama.vividwalls.blog {
    reverse_proxy ollama:11434
}
EOF

echo "📤 Uploading network-aware Caddyfile..."
scp -i ~/.ssh/digitalocean /tmp/Caddyfile_network root@${SERVER_IP}:/home/vivid/vivid_mas/Caddyfile

echo "🔄 Restarting Caddy..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cd /home/vivid/vivid_mas && docker-compose restart caddy"

echo "⏳ Waiting for Caddy to start..."
sleep 10

echo "✅ Testing n8n connectivity..."
N8N_STATUS=$(ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "curl -s -o /dev/null -w '%{http_code}' https://n8n.vividwalls.blog")
echo "n8n HTTPS status: $N8N_STATUS"

if [ "$N8N_STATUS" = "200" ]; then
    echo "🎉 n8n is now accessible via HTTPS!"
    echo ""
    echo "🌐 Available services:"
    echo "  • n8n: https://n8n.vividwalls.blog"
    echo "  • Open WebUI: https://webui.vividwalls.blog"
    echo "  • Langfuse: https://langfuse.vividwalls.blog"
    echo "  • WordPress: https://vividwalls.blog"
    echo "  • Flowise: https://flowise.vividwalls.blog"
    echo "  • Ollama: https://ollama.vividwalls.blog"
else
    echo "❌ Still having connectivity issues. Checking Caddy logs..."
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker logs caddy --tail 10"
fi

echo "🏁 Network fix completed" 