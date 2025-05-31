#!/bin/bash

# Fix WordPress SSL Issues Script
# This script resolves network connectivity and SSL configuration problems

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas"

echo "🔧 Fixing WordPress SSL Issues..."
echo "=================================="

# Step 1: Connect WordPress container to the main network
echo "📡 Connecting WordPress to main network..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Check current networks
echo "Current networks:"
docker network ls

# Connect wordpress-multisite to vivid_mas network if not already connected
if ! docker network inspect vivid_mas | grep -q "wordpress-multisite"; then
    echo "Connecting wordpress-multisite to vivid_mas network..."
    docker network connect vivid_mas wordpress-multisite
else
    echo "wordpress-multisite already connected to vivid_mas network"
fi

# Verify connection
echo "Verifying network connection..."
docker network inspect vivid_mas | grep -A 5 -B 5 "wordpress-multisite" || echo "Connection check complete"
EOF

# Step 2: Update Caddyfile to add wordpress.vividwalls.blog
echo "📝 Updating Caddyfile configuration..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Backup current Caddyfile
cp Caddyfile Caddyfile.backup.$(date +%Y%m%d_%H%M%S)

# Add WordPress subdomain configuration if not present
if ! grep -q "wordpress.vividwalls.blog" Caddyfile; then
    echo "" >> Caddyfile
    echo "# WordPress Subdomain" >> Caddyfile
    echo "wordpress.vividwalls.blog {" >> Caddyfile
    echo "    header {" >> Caddyfile
    echo "        Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\"" >> Caddyfile
    echo "        X-Content-Type-Options \"nosniff\"" >> Caddyfile
    echo "        X-Frame-Options \"SAMEORIGIN\"" >> Caddyfile
    echo "        X-XSS-Protection \"1; mode=block\"" >> Caddyfile
    echo "        Referrer-Policy \"strict-origin-when-cross-origin\"" >> Caddyfile
    echo "        Permissions-Policy \"camera=(), microphone=(), geolocation=()\"" >> Caddyfile
    echo "    }" >> Caddyfile
    echo "    reverse_proxy wordpress-multisite:80 {" >> Caddyfile
    echo "        header_up X-Forwarded-Proto https" >> Caddyfile
    echo "        header_up X-Real-IP {remote_host}" >> Caddyfile
    echo "        header_up Host {host}" >> Caddyfile
    echo "    }" >> Caddyfile
    echo "}" >> Caddyfile
    echo "✅ Added wordpress.vividwalls.blog configuration"
else
    echo "✅ wordpress.vividwalls.blog already configured"
fi
EOF

# Step 3: Restart Caddy to apply changes
echo "🔄 Restarting Caddy..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Restart Caddy to reload configuration
docker-compose restart caddy

# Wait for Caddy to start
sleep 5

# Check Caddy status
echo "Caddy status:"
docker-compose ps caddy
EOF

# Step 4: Test connectivity
echo "🧪 Testing connectivity..."
sleep 10

echo "Testing WordPress SSL endpoints:"
echo "1. Main domain (vividwalls.blog):"
curl -I -L --max-time 10 https://vividwalls.blog || echo "❌ Main domain failed"

echo "2. WordPress subdomain (wordpress.vividwalls.blog):"
curl -I -L --max-time 10 https://wordpress.vividwalls.blog || echo "❌ WordPress subdomain failed"

echo "3. SearXNG (should still work):"
curl -I -L --max-time 10 https://searxng.vividwalls.blog || echo "❌ SearXNG failed"

echo ""
echo "🎉 WordPress SSL fix completed!"
echo "If issues persist, check Caddy logs: docker logs caddy --tail=20" 