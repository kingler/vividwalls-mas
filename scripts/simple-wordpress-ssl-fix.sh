#!/bin/bash

# Simple WordPress SSL Fix Script
# Focuses on the most critical SSL configuration issues

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"

echo "🔧 Simple WordPress SSL Fix..."
echo "=============================="

# Step 1: Fix WordPress wp-config.php duplicate definitions
echo "📝 Fixing WordPress configuration..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Fix duplicate WP_HOME definition
docker exec wordpress-multisite sed -i '/require_once ABSPATH.*wp-settings.php.*define.*WP_HOME/d' /var/www/html/wp-config.php

# Add SSL configuration if not present
if ! docker exec wordpress-multisite grep -q "HTTP_X_FORWARDED_PROTO" /var/www/html/wp-config.php; then
    docker exec wordpress-multisite sed -i '/require_once ABSPATH.*wp-settings.php/i\\n/* SSL Configuration */\nif (isset($_SERVER["HTTP_X_FORWARDED_PROTO"]) && $_SERVER["HTTP_X_FORWARDED_PROTO"] === "https") {\n    $_SERVER["HTTPS"] = "on";\n}\ndefine("FORCE_SSL_ADMIN", true);\n' /var/www/html/wp-config.php
    echo "✅ Added SSL configuration to WordPress"
else
    echo "✅ SSL configuration already present"
fi
EOF

# Step 2: Update Caddyfile with proper headers
echo "🌐 Updating Caddyfile..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Update the WordPress section in Caddyfile to fix SSL issues
sed -i '/# WordPress Main Site/,/^}$/{
    s/header_up X-Forwarded-For {remote_host}/header_up X-Forwarded-Host {host}/
    /header_up X-Forwarded-Proto https/a\        header_up X-Forwarded-Host {host}
}' Caddyfile

# Update the WordPress subdomain section
sed -i '/# WordPress Subdomain/,/^}$/{
    s/header_up X-Forwarded-For {remote_host}/header_up X-Forwarded-Host {host}/
    /header_up X-Forwarded-Proto https/a\        header_up X-Forwarded-Host {host}
}' Caddyfile

echo "✅ Caddyfile updated"
EOF

# Step 3: Restart services
echo "🔄 Restarting services..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Restart WordPress
docker-compose -f wordpress-compose.yml restart wordpress
sleep 5

# Restart Caddy
docker-compose restart caddy
sleep 5

echo "✅ Services restarted"
EOF

# Step 4: Test endpoints
echo "🧪 Testing SSL endpoints..."
sleep 10

echo "1. Main domain (vividwalls.blog):"
curl -I -L --max-time 10 https://vividwalls.blog 2>/dev/null | head -1 || echo "❌ Failed"

echo "2. WordPress subdomain (wordpress.vividwalls.blog):"
curl -I -L --max-time 10 https://wordpress.vividwalls.blog 2>/dev/null | head -1 || echo "❌ Failed"

echo "3. SearXNG (searxng.vividwalls.blog):"
curl -I -L --max-time 10 https://searxng.vividwalls.blog 2>/dev/null | head -1 || echo "❌ Failed"

echo ""
echo "🎉 Simple WordPress SSL fix completed!"
echo ""
echo "🌐 Test these URLs in your browser:"
echo "• https://vividwalls.blog"
echo "• https://wordpress.vividwalls.blog"
echo "• https://vividwalls.blog/wp-admin/" 