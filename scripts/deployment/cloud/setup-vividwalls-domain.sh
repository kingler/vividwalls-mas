#!/bin/bash

# VividMAS Domain Setup Script for vividwalls.blog
# This script configures DNS and server settings for the VividMAS platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Configuration
DOMAIN="vividwalls.blog"
SERVER_IP="157.230.13.13"
EMAIL="kingler@vividwalls.co"

print_header "🚀 VividMAS Domain Setup for $DOMAIN"
print_status "Server IP: $SERVER_IP"
print_status "Email: $EMAIL"
echo ""

# Check if doctl is installed and authenticated
if ! command -v doctl &> /dev/null; then
    print_error "doctl is not installed. Please install it first:"
    print_error "brew install doctl"
    exit 1
fi

# Check authentication
if ! doctl auth list &> /dev/null; then
    print_error "doctl is not authenticated. Please run:"
    print_error "doctl auth init"
    exit 1
fi

# Array of subdomains for VividMAS platform
SUBDOMAINS=("n8n" "webui" "flowise" "supabase" "langfuse" "search" "ollama" "wordpress")

print_header "📋 Step 1: Creating DNS A Records"

# Create A records for each subdomain
for subdomain in "${SUBDOMAINS[@]}"; do
    print_status "Creating A record for ${subdomain}.${DOMAIN}"
    
    if doctl compute domain records create "$DOMAIN" \
        --record-type A \
        --record-name "$subdomain" \
        --record-data "$SERVER_IP" \
        --record-ttl 300 > /dev/null 2>&1; then
        print_status "✅ Created ${subdomain}.${DOMAIN}"
    else
        print_warning "⚠️  ${subdomain}.${DOMAIN} may already exist"
    fi
done

print_status ""
print_status "Current DNS records for $DOMAIN:"
doctl compute domain records list "$DOMAIN"

print_header "📋 Step 2: Updating Server Configuration"

# Create server update script
cat > update_server_config.sh << 'EOF'
#!/bin/bash

# Server configuration update script
DOMAIN="vividwalls.blog"
EMAIL="kingler@vividwalls.co"

cd /home/vivid/vivid_mas

# Backup current configuration
echo "Creating configuration backup..."
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)

# Update .env file with domain configuration
echo "Updating environment variables..."

# Update hostname variables
sed -i "s/N8N_HOSTNAME=.*/N8N_HOSTNAME=n8n.${DOMAIN}/" .env
sed -i "s/WEBUI_HOSTNAME=.*/WEBUI_HOSTNAME=webui.${DOMAIN}/" .env || echo "WEBUI_HOSTNAME=webui.${DOMAIN}" >> .env
sed -i "s/FLOWISE_HOSTNAME=.*/FLOWISE_HOSTNAME=flowise.${DOMAIN}/" .env || echo "FLOWISE_HOSTNAME=flowise.${DOMAIN}" >> .env
sed -i "s/SUPABASE_HOSTNAME=.*/SUPABASE_HOSTNAME=supabase.${DOMAIN}/" .env || echo "SUPABASE_HOSTNAME=supabase.${DOMAIN}" >> .env
sed -i "s/LANGFUSE_HOSTNAME=.*/LANGFUSE_HOSTNAME=langfuse.${DOMAIN}/" .env || echo "LANGFUSE_HOSTNAME=langfuse.${DOMAIN}" >> .env
sed -i "s/SEARXNG_HOSTNAME=.*/SEARXNG_HOSTNAME=search.${DOMAIN}/" .env || echo "SEARXNG_HOSTNAME=search.${DOMAIN}" >> .env
sed -i "s/OLLAMA_HOSTNAME=.*/OLLAMA_HOSTNAME=ollama.${DOMAIN}/" .env || echo "OLLAMA_HOSTNAME=ollama.${DOMAIN}" >> .env
sed -i "s/WORDPRESS_HOSTNAME=.*/WORDPRESS_HOSTNAME=wordpress.${DOMAIN}/" .env || echo "WORDPRESS_HOSTNAME=wordpress.${DOMAIN}" >> .env

# Update SSL and security settings
sed -i "s/LETSENCRYPT_EMAIL=.*/LETSENCRYPT_EMAIL=${EMAIL}/" .env || echo "LETSENCRYPT_EMAIL=${EMAIL}" >> .env
sed -i "s/N8N_SECURE_COOKIE=.*/N8N_SECURE_COOKIE=true/" .env || echo "N8N_SECURE_COOKIE=true" >> .env

# Update webhook URL in docker-compose.yml
sed -i "s|WEBHOOK_URL=.*|WEBHOOK_URL=https://n8n.${DOMAIN}|" docker-compose.yml

# Update WordPress configuration if wordpress-compose.yml exists
if [ -f "wordpress-compose.yml" ]; then
    echo "Updating WordPress configuration..."
    sed -i "s/WORDPRESS_DOMAIN=.*/WORDPRESS_DOMAIN=wordpress.${DOMAIN}/" .env || echo "WORDPRESS_DOMAIN=wordpress.${DOMAIN}" >> .env
fi

# Update Caddyfile to include WordPress if not already present
if [ -f "Caddyfile" ] && ! grep -q "wordpress.${DOMAIN}" Caddyfile; then
    echo "" >> Caddyfile
    echo "# WordPress" >> Caddyfile
    echo "{\$WORDPRESS_HOSTNAME} {" >> Caddyfile
    echo "    reverse_proxy localhost:8080" >> Caddyfile
    echo "}" >> Caddyfile
fi

echo "✅ Server configuration updated successfully!"
echo ""
echo "Updated services:"
echo "  - n8n: https://n8n.${DOMAIN}"
echo "  - Open WebUI: https://webui.${DOMAIN}"
echo "  - Flowise: https://flowise.${DOMAIN}"
echo "  - Supabase: https://supabase.${DOMAIN}"
echo "  - Langfuse: https://langfuse.${DOMAIN}"
echo "  - SearXNG: https://search.${DOMAIN}"
echo "  - Ollama: https://ollama.${DOMAIN}"
echo "  - WordPress: https://wordpress.${DOMAIN}"
EOF

chmod +x update_server_config.sh

print_status "Uploading configuration script to server..."
scp update_server_config.sh root@$SERVER_IP:/tmp/

print_status "Executing configuration update on server..."
ssh root@$SERVER_IP "bash /tmp/update_server_config.sh"

print_header "📋 Step 3: Restarting Services"

print_status "Restarting Docker services..."
ssh root@$SERVER_IP "cd /home/vivid/vivid_mas && docker-compose restart caddy n8n"

# Restart WordPress if it exists
ssh root@$SERVER_IP "cd /home/vivid/vivid_mas && if [ -f wordpress-compose.yml ]; then docker-compose -f wordpress-compose.yml restart; fi"

print_header "📋 Step 4: Verification"

print_status "Checking DNS propagation..."
echo ""
for subdomain in "${SUBDOMAINS[@]}"; do
    result=$(dig +short ${subdomain}.${DOMAIN} 2>/dev/null || echo "Not propagated yet")
    if [ "$result" = "$SERVER_IP" ]; then
        print_status "✅ ${subdomain}.${DOMAIN} → $result"
    else
        print_warning "⏳ ${subdomain}.${DOMAIN} → $result (propagating...)"
    fi
done

print_header "🎉 Setup Complete!"
echo ""
print_status "Your VividMAS platform is now configured for $DOMAIN"
print_status ""
print_status "🌐 Service URLs (available after DNS propagation):"
print_status "   • n8n Automation: https://n8n.$DOMAIN"
print_status "   • Open WebUI: https://webui.$DOMAIN"
print_status "   • Flowise: https://flowise.$DOMAIN"
print_status "   • Supabase: https://supabase.$DOMAIN"
print_status "   • Langfuse: https://langfuse.$DOMAIN"
print_status "   • SearXNG: https://search.$DOMAIN"
print_status "   • Ollama: https://ollama.$DOMAIN"
print_status "   • WordPress: https://wordpress.$DOMAIN/wp-admin/"
print_status ""
print_status "⏱️  DNS propagation typically takes 5-30 minutes"
print_status "🔒 SSL certificates will be automatically generated by Caddy"
print_status "🍪 Secure cookies are now enabled for HTTPS"
print_status ""
print_status "📊 Monitor progress:"
print_status "   • DNS: dig +short n8n.$DOMAIN"
print_status "   • SSL: curl -I https://n8n.$DOMAIN"
print_status "   • Logs: ssh root@$SERVER_IP 'docker logs caddy --follow'"
print_status ""
print_status "🔧 WordPress Admin:"
print_status "   • URL: https://wordpress.$DOMAIN/wp-admin/"
print_status "   • User: kingler-admin"
print_status "   • Pass: VQC\$RkIJxzZDL)xh(Y"

# Cleanup
rm -f update_server_config.sh

print_status ""
print_status "🚀 Your professional VividMAS platform is ready!" 