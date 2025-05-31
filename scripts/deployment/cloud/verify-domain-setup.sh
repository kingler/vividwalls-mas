#!/bin/bash

# VividMAS Domain Verification Script
# This script checks the status of DNS propagation and SSL certificates

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
    echo -e "${BLUE}[CHECK]${NC} $1"
}

# Configuration
DOMAIN="vividwalls.blog"
SERVER_IP="157.230.13.13"
SUBDOMAINS=("n8n" "webui" "flowise" "supabase" "langfuse" "search" "ollama" "wordpress")

print_header "🔍 VividMAS Domain Verification for $DOMAIN"
echo ""

print_header "📋 Step 1: DNS Propagation Check"
echo ""

dns_ready=true
for subdomain in "${SUBDOMAINS[@]}"; do
    result=$(dig +short ${subdomain}.${DOMAIN} 2>/dev/null || echo "")
    if [ "$result" = "$SERVER_IP" ]; then
        print_status "✅ ${subdomain}.${DOMAIN} → $result"
    else
        print_warning "⏳ ${subdomain}.${DOMAIN} → ${result:-'Not resolved'} (expected: $SERVER_IP)"
        dns_ready=false
    fi
done

echo ""
if [ "$dns_ready" = true ]; then
    print_status "🎉 All DNS records are properly propagated!"
else
    print_warning "⏱️  Some DNS records are still propagating. This can take 5-30 minutes."
fi

print_header "📋 Step 2: SSL Certificate Check"
echo ""

ssl_ready=true
for subdomain in "${SUBDOMAINS[@]}"; do
    url="https://${subdomain}.${DOMAIN}"
    
    # Check if HTTPS is working
    if curl -s -I --connect-timeout 10 "$url" > /dev/null 2>&1; then
        # Get certificate info
        cert_info=$(curl -s -I --connect-timeout 10 "$url" 2>/dev/null | head -1)
        if echo "$cert_info" | grep -q "200\|301\|302"; then
            print_status "✅ ${subdomain}.${DOMAIN} - SSL working"
        else
            print_warning "⚠️  ${subdomain}.${DOMAIN} - SSL responding but service may not be ready"
        fi
    else
        print_warning "⏳ ${subdomain}.${DOMAIN} - SSL not ready yet"
        ssl_ready=false
    fi
done

echo ""
if [ "$ssl_ready" = true ]; then
    print_status "🔒 All SSL certificates are working!"
else
    print_warning "⏱️  Some SSL certificates are still being generated. This can take 5-15 minutes after DNS propagation."
fi

print_header "📋 Step 3: Service Health Check"
echo ""

# Check specific service endpoints
services_ready=true

# Check n8n
if curl -s --connect-timeout 10 "https://n8n.${DOMAIN}" > /dev/null 2>&1; then
    print_status "✅ n8n - Service responding"
else
    print_warning "⏳ n8n - Service not ready"
    services_ready=false
fi

# Check WordPress
if curl -s --connect-timeout 10 "https://wordpress.${DOMAIN}/wp-admin/" > /dev/null 2>&1; then
    print_status "✅ WordPress - Service responding"
else
    print_warning "⏳ WordPress - Service not ready"
    services_ready=false
fi

# Check Open WebUI
if curl -s --connect-timeout 10 "https://webui.${DOMAIN}" > /dev/null 2>&1; then
    print_status "✅ Open WebUI - Service responding"
else
    print_warning "⏳ Open WebUI - Service not ready"
    services_ready=false
fi

print_header "📋 Step 4: Server Status Check"
echo ""

# Check if we can SSH to the server
if ssh -o ConnectTimeout=10 -o BatchMode=yes root@$SERVER_IP "echo 'SSH connection successful'" 2>/dev/null; then
    print_status "✅ SSH connection to server working"
    
    # Check Docker services
    print_status "Checking Docker services on server..."
    ssh root@$SERVER_IP "cd /home/vivid/vivid_mas && docker-compose ps --format table" 2>/dev/null || print_warning "Could not check Docker services"
    
else
    print_error "❌ Cannot connect to server via SSH"
fi

print_header "📊 Summary"
echo ""

if [ "$dns_ready" = true ] && [ "$ssl_ready" = true ] && [ "$services_ready" = true ]; then
    print_status "🎉 Your VividMAS platform is fully operational!"
    echo ""
    print_status "🌐 Access your services:"
    for subdomain in "${SUBDOMAINS[@]}"; do
        print_status "   • ${subdomain^}: https://${subdomain}.${DOMAIN}"
    done
    echo ""
    print_status "🔧 WordPress Admin: https://wordpress.${DOMAIN}/wp-admin/"
    print_status "   Username: kingler-admin"
    print_status "   Password: VQC\$RkIJxzZDL)xh(Y"
    
elif [ "$dns_ready" = false ]; then
    print_warning "⏱️  Waiting for DNS propagation to complete..."
    print_status "Check again in 10-15 minutes with: ./scripts/verify-domain-setup.sh"
    
elif [ "$ssl_ready" = false ]; then
    print_warning "⏱️  Waiting for SSL certificates to be generated..."
    print_status "Check again in 5-10 minutes with: ./scripts/verify-domain-setup.sh"
    print_status "Monitor Caddy logs: ssh root@$SERVER_IP 'docker logs caddy --follow'"
    
else
    print_warning "⏱️  Some services are still starting up..."
    print_status "Check again in a few minutes with: ./scripts/verify-domain-setup.sh"
fi

echo ""
print_status "🔧 Troubleshooting commands:"
print_status "   • Check DNS: dig +short n8n.${DOMAIN}"
print_status "   • Test SSL: curl -I https://n8n.${DOMAIN}"
print_status "   • View logs: ssh root@$SERVER_IP 'docker logs caddy --follow'"
print_status "   • Server status: ssh root@$SERVER_IP 'cd /home/vivid/vivid_mas && docker-compose ps'" 