#!/bin/bash

# VividMAS Domain DNS Setup Script
# Usage: ./setup-domain-dns.sh yourdomain.com your-server-ip your-email@domain.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if required parameters are provided
if [ $# -ne 3 ]; then
    print_error "Usage: $0 <domain> <server-ip> <email>"
    print_error "Example: $0 yourdomain.com 157.230.13.13 admin@yourdomain.com"
    exit 1
fi

DOMAIN="$1"
SERVER_IP="$2"
EMAIL="$3"

print_status "Setting up DNS for VividMAS platform"
print_status "Domain: $DOMAIN"
print_status "Server IP: $SERVER_IP"
print_status "Email: $EMAIL"

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

print_status "Creating DNS A records..."

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
        print_warning "⚠️  Failed to create ${subdomain}.${DOMAIN} (may already exist)"
    fi
done

print_status "Verifying DNS records..."
echo ""
doctl compute domain records list "$DOMAIN"

print_status ""
print_status "🎉 DNS setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Update server environment variables:"
print_status "   N8N_HOSTNAME=n8n.${DOMAIN}"
print_status "   WEBUI_HOSTNAME=webui.${DOMAIN}"
print_status "   FLOWISE_HOSTNAME=flowise.${DOMAIN}"
print_status "   SUPABASE_HOSTNAME=supabase.${DOMAIN}"
print_status "   LANGFUSE_HOSTNAME=langfuse.${DOMAIN}"
print_status "   SEARXNG_HOSTNAME=search.${DOMAIN}"
print_status "   OLLAMA_HOSTNAME=ollama.${DOMAIN}"
print_status "   WORDPRESS_HOSTNAME=wordpress.${DOMAIN}"
print_status "   LETSENCRYPT_EMAIL=${EMAIL}"
print_status ""
print_status "2. Update docker-compose.yml webhook URL:"
print_status "   WEBHOOK_URL=https://n8n.${DOMAIN}"
print_status ""
print_status "3. Restart services:"
print_status "   docker-compose restart caddy n8n"
print_status "   docker-compose -f wordpress-compose.yml restart"
print_status ""
print_status "4. Wait 5-30 minutes for DNS propagation"
print_status ""
print_status "Your services will be available at:"
for subdomain in "${SUBDOMAINS[@]}"; do
    print_status "   https://${subdomain}.${DOMAIN}"
done

print_status ""
print_status "DNS propagation can be checked with:"
print_status "   dig +short n8n.${DOMAIN}" 