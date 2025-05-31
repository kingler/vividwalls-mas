#!/bin/bash

# Fix Caddyfile Configuration
# This script fixes the Caddyfile syntax error and adds missing services

set -e

SERVER_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo "🔧 Fixing Caddyfile configuration..."

# Function to run commands on remote server
run_remote() {
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "$1"
}

# Create a complete, corrected Caddyfile
echo "📝 Creating corrected Caddyfile..."

cat > /tmp/Caddyfile << 'EOF'
{
    # Global options - works for both environments
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

# Flowise - No-code AI Builder
{$FLOWISE_HOSTNAME} {
    reverse_proxy 127.0.0.1:3001
    
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

# SearXNG - Privacy Search
{$SEARXNG_HOSTNAME} {
    reverse_proxy 127.0.0.1:8080
    
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}

# Ollama - Local LLMs
{$OLLAMA_HOSTNAME} {
    reverse_proxy 127.0.0.1:11434
    
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
    
    # WordPress-specific optimizations
    encode gzip
    
    # Cache static assets
    @static {
        path *.css *.js *.png *.jpg *.jpeg *.gif *.ico *.svg *.woff *.woff2 *.ttf *.eot
    }
    
    header @static {
        Cache-Control "public, max-age=31536000"
    }
    
    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
EOF

# Upload the corrected Caddyfile
echo "📤 Uploading corrected Caddyfile..."
scp -i ~/.ssh/digitalocean /tmp/Caddyfile root@${SERVER_IP}:/home/vivid/vivid_mas/Caddyfile

# Restart Caddy
echo "🔄 Restarting Caddy..."
run_remote "cd /home/vivid/vivid_mas && docker-compose restart caddy"

# Wait for Caddy to start
echo "⏳ Waiting for Caddy to start..."
sleep 10

# Check Caddy status
echo "✅ Checking Caddy status..."
CADDY_STATUS=$(run_remote "docker ps --filter name=caddy --format '{{.Status}}'")
echo "Caddy status: $CADDY_STATUS"

if echo "$CADDY_STATUS" | grep -q "Up"; then
    echo "🎉 Caddy is now running successfully!"
    echo "🌐 All services should now be accessible via their domain names"
else
    echo "❌ Caddy is still having issues. Checking logs..."
    run_remote "docker logs caddy --tail 10"
fi

echo "🏁 Caddyfile fix completed" 