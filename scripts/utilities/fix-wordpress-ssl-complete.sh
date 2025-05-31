#!/bin/bash

# Complete WordPress SSL Fix Script
# This script resolves all WordPress SSL issues including configuration problems

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas"

echo "🔧 Complete WordPress SSL Fix..."
echo "================================="

# Step 1: Fix WordPress wp-config.php duplicate definitions
echo "📝 Fixing WordPress configuration..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Backup current wp-config.php
docker exec wordpress-multisite cp /var/www/html/wp-config.php /var/www/html/wp-config.php.backup.$(date +%Y%m%d_%H%M%S)

# Fix duplicate WP_HOME definition and add proper SSL configuration
docker exec wordpress-multisite bash -c '
# Remove duplicate WP_HOME line
sed -i "/require_once ABSPATH.*wp-settings.php.*define.*WP_HOME/d" /var/www/html/wp-config.php

# Add proper SSL configuration before wp-settings.php
sed -i "/require_once ABSPATH.*wp-settings.php/i\\
\\
/* SSL and HTTPS Configuration */\\
if (isset(\$_SERVER[\"HTTP_X_FORWARDED_PROTO\"]) && \$_SERVER[\"HTTP_X_FORWARDED_PROTO\"] === \"https\") {\\
    \$_SERVER[\"HTTPS\"] = \"on\";\\
}\\
\\
/* Force SSL Admin */\\
define(\"FORCE_SSL_ADMIN\", true);\\
\\
/* Trust proxy headers */\\
if (isset(\$_SERVER[\"HTTP_X_FORWARDED_FOR\"])) {\\
    \$_SERVER[\"REMOTE_ADDR\"] = \$_SERVER[\"HTTP_X_FORWARDED_FOR\"];\\
}\\
" /var/www/html/wp-config.php

echo "✅ WordPress configuration updated"
'
EOF

# Step 2: Update WordPress database URLs to use HTTPS
echo "🗄️ Updating WordPress database URLs..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Update WordPress database to use HTTPS URLs
docker exec wordpress-multisite wp --allow-root option update home "https://vividwalls.blog"
docker exec wordpress-multisite wp --allow-root option update siteurl "https://vividwalls.blog"

# Update any remaining HTTP URLs in the database
docker exec wordpress-multisite wp --allow-root search-replace "http://vividwalls.blog" "https://vividwalls.blog" --dry-run
docker exec wordpress-multisite wp --allow-root search-replace "http://vividwalls.blog" "https://vividwalls.blog"

echo "✅ WordPress database URLs updated to HTTPS"
EOF

# Step 3: Update Caddyfile to handle both domains properly
echo "🌐 Updating Caddyfile for proper SSL handling..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Backup current Caddyfile
cp Caddyfile Caddyfile.backup.ssl.$(date +%Y%m%d_%H%M%S)

# Create a new optimized Caddyfile
cat > Caddyfile << 'CADDY_EOF'
{
    email kingler@vividwalls.co
}

# WordPress Main Site - Primary Domain
vividwalls.blog {
    header {
        # Security Headers
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy wordpress-multisite:80 {
        header_up X-Forwarded-Proto https
        header_up X-Forwarded-Host {host}
        header_up X-Real-IP {remote_host}
        header_up Host vividwalls.blog
    }
}

# WordPress Subdomain - Alternative Access
wordpress.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy wordpress-multisite:80 {
        header_up X-Forwarded-Proto https
        header_up X-Forwarded-Host {host}
        header_up X-Real-IP {remote_host}
        header_up Host vividwalls.blog
    }
}

# n8n Automation Platform
n8n.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss: https:; frame-ancestors 'none';"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=()"
        X-Robots-Tag "noindex, nofollow"
    }
    reverse_proxy n8n:5678 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# Open WebUI (LLM Interface)
webui.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy open-webui:8080 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# Langfuse (LLM Analytics)
langfuse.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy vivid_mas-langfuse-web-1:3000 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# Flowise (AI Workflows)
flowise.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy flowise:3001 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# Supabase API Gateway
supabase.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
    }
    reverse_proxy supabase-kong:8000 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# SearXNG (Private Search)
searxng.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        X-Robots-Tag "noindex, nofollow"
    }
    reverse_proxy searxng:8080 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}

# Ollama (Local LLM)
ollama.vividwalls.blog {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        X-Robots-Tag "noindex, nofollow"
    }
    reverse_proxy ollama:11434 {
        header_up X-Forwarded-Proto https
        header_up X-Real-IP {remote_host}
        header_up Host {host}
    }
}
CADDY_EOF

echo "✅ Caddyfile updated with optimized SSL configuration"
EOF

# Step 4: Restart services in proper order
echo "🔄 Restarting services..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Restart WordPress first
docker-compose -f wordpress-compose.yml restart wordpress

# Wait for WordPress to be ready
sleep 10

# Restart Caddy to reload configuration
docker-compose restart caddy

# Wait for Caddy to start
sleep 10

echo "✅ Services restarted"
EOF

# Step 5: Test all endpoints
echo "🧪 Testing all SSL endpoints..."
sleep 15

echo ""
echo "Testing WordPress SSL endpoints:"
echo "1. Main domain (vividwalls.blog):"
curl -I -L --max-time 15 https://vividwalls.blog 2>/dev/null | head -1 || echo "❌ Main domain failed"

echo "2. WordPress subdomain (wordpress.vividwalls.blog):"
curl -I -L --max-time 15 https://wordpress.vividwalls.blog 2>/dev/null | head -1 || echo "❌ WordPress subdomain failed"

echo "3. WordPress admin (vividwalls.blog/wp-admin/):"
curl -I -L --max-time 15 https://vividwalls.blog/wp-admin/ 2>/dev/null | head -1 || echo "❌ WordPress admin failed"

echo "4. SearXNG (searxng.vividwalls.blog):"
curl -I -L --max-time 15 https://searxng.vividwalls.blog 2>/dev/null | head -1 || echo "❌ SearXNG failed"

echo ""
echo "🎉 Complete WordPress SSL fix completed!"
echo ""
echo "📋 Summary:"
echo "✅ Fixed duplicate WP_HOME definitions"
echo "✅ Added proper SSL configuration to WordPress"
echo "✅ Updated database URLs to HTTPS"
echo "✅ Optimized Caddyfile for SSL handling"
echo "✅ Restarted services in proper order"
echo ""
echo "🌐 Access URLs:"
echo "• Main site: https://vividwalls.blog"
echo "• WordPress admin: https://vividwalls.blog/wp-admin/"
echo "• Alternative: https://wordpress.vividwalls.blog" 