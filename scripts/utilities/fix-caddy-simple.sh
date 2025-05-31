#!/bin/bash

# Fix Caddy with Simplified Configuration
# Only include services with defined hostnames

set -e

SERVER_IP="157.230.13.13"

echo "🔧 Creating simplified Caddyfile..."

# Create simplified Caddyfile locally
cat > /tmp/Caddyfile_simple << 'EOF'
{
    email {$LETSENCRYPT_EMAIL}
}

# N8N - Workflow Automation
{$N8N_HOSTNAME} {
    reverse_proxy 127.0.0.1:5678
    
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}

# Open WebUI - AI Chat Interface
{$WEBUI_HOSTNAME} {
    reverse_proxy 127.0.0.1:3000
    
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}

# Langfuse - LLM Observability
{$LANGFUSE_HOSTNAME} {
    reverse_proxy 127.0.0.1:3002
    
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}

# WordPress - Main Website
{$WORDPRESS_HOSTNAME} {
    reverse_proxy 127.0.0.1:8080
    
    encode gzip
    
    @static {
        path *.css *.js *.png *.jpg *.jpeg *.gif *.ico *.svg *.woff *.woff2 *.ttf *.eot
    }
    
    header @static {
        Cache-Control "public, max-age=31536000"
    }
    
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
EOF

echo "📤 Uploading simplified Caddyfile..."
scp -i ~/.ssh/digitalocean /tmp/Caddyfile_simple root@${SERVER_IP}:/home/vivid/vivid_mas/Caddyfile

echo "🔄 Restarting Caddy..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cd /home/vivid/vivid_mas && docker-compose restart caddy"

echo "⏳ Waiting for Caddy to start..."
sleep 15

echo "✅ Checking Caddy status..."
CADDY_STATUS=$(ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker ps --filter name=caddy --format '{{.Status}}'")
echo "Caddy status: $CADDY_STATUS"

if echo "$CADDY_STATUS" | grep -q "Up"; then
    echo "🎉 Caddy is now running successfully!"
    echo ""
    echo "🌐 Available services:"
    echo "  • n8n: https://n8n.vividwalls.blog"
    echo "  • Open WebUI: https://webui.vividwalls.blog"
    echo "  • Langfuse: https://langfuse.vividwalls.blog"
    echo "  • WordPress: https://vividwalls.blog"
else
    echo "❌ Caddy is still having issues. Checking logs..."
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker logs caddy --tail 10"
fi

echo "🏁 Simplified Caddy fix completed" 