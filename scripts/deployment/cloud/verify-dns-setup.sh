#!/bin/bash

# VividWalls DNS Verification Script
# Verifies DNS configuration for CopilotKit integration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 VividWalls DNS Configuration Verification${NC}"
echo "=============================================="

# Domain configuration
DOMAIN="vividwalls.blog"
SERVER_IP="157.230.13.13"

# Required subdomains for VividMAS platform
SUBDOMAINS=("n8n" "webui" "flowise" "supabase" "langfuse" "searxng" "ollama")

echo -e "${YELLOW}📋 Checking DNS records for $DOMAIN...${NC}"

# Check main domain
echo -e "\n${BLUE}Main Domain:${NC}"
MAIN_IP=$(dig +short $DOMAIN)
if [ "$MAIN_IP" = "$SERVER_IP" ]; then
    echo -e "✅ $DOMAIN → $MAIN_IP"
else
    echo -e "❌ $DOMAIN → $MAIN_IP (expected: $SERVER_IP)"
fi

# Check subdomains
echo -e "\n${BLUE}Subdomains:${NC}"
ALL_GOOD=true

for subdomain in "${SUBDOMAINS[@]}"; do
    FULL_DOMAIN="${subdomain}.${DOMAIN}"
    IP=$(dig +short $FULL_DOMAIN)
    
    if [ "$IP" = "$SERVER_IP" ]; then
        echo -e "✅ $FULL_DOMAIN → $IP"
    else
        echo -e "❌ $FULL_DOMAIN → $IP (expected: $SERVER_IP)"
        ALL_GOOD=false
    fi
done

# Check SSL certificates
echo -e "\n${BLUE}SSL Certificate Status:${NC}"
for subdomain in "${SUBDOMAINS[@]}"; do
    FULL_DOMAIN="${subdomain}.${DOMAIN}"
    
    # Check if HTTPS is working
    if curl -s -I "https://$FULL_DOMAIN" >/dev/null 2>&1; then
        echo -e "✅ $FULL_DOMAIN - SSL certificate valid"
    else
        echo -e "❌ $FULL_DOMAIN - SSL certificate issue or service not running"
        ALL_GOOD=false
    fi
done

# Specific check for n8n webhook endpoint
echo -e "\n${BLUE}CopilotKit Webhook Endpoint:${NC}"
WEBHOOK_URL="https://n8n.vividwalls.blog/webhook/vividwalls-copilot"

# Test webhook accessibility (expect 405 Method Not Allowed for GET, which means it's working)
# 404 is expected if workflow hasn't been imported yet
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL")

if [ "$HTTP_STATUS" = "405" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo -e "✅ Webhook endpoint accessible: $WEBHOOK_URL"
    echo -e "   Status: $HTTP_STATUS (webhook is active and working)"
elif [ "$HTTP_STATUS" = "404" ]; then
    echo -e "⚠️  Webhook endpoint not found: $WEBHOOK_URL"
    echo -e "   Status: $HTTP_STATUS (workflow not imported yet - this is expected)"
    echo -e "   📝 Next step: Import Enhanced-VividWalls-CopilotKit-Workflow.json into n8n"
else
    echo -e "❌ Webhook endpoint issue: $WEBHOOK_URL"
    echo -e "   Status: $HTTP_STATUS"
    ALL_GOOD=false
fi

# WordPress site check
echo -e "\n${BLUE}WordPress Site:${NC}"
WP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN")
if [ "$WP_STATUS" = "200" ]; then
    echo -e "✅ WordPress site accessible: https://$DOMAIN"
else
    echo -e "❌ WordPress site issue: https://$DOMAIN (Status: $WP_STATUS)"
    ALL_GOOD=false
fi

# Summary
echo -e "\n${BLUE}Summary:${NC}"
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}🎉 All DNS and SSL configurations are correct!${NC}"
    if [ "$HTTP_STATUS" = "404" ]; then
        echo -e "${YELLOW}⚠️  Webhook not active yet (workflow needs to be imported)${NC}"
        echo -e "${GREEN}✅ Infrastructure ready for CopilotKit integration${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Run the migration script: ./scripts/migrate-to-droplet.sh"
        echo "2. Import Enhanced-VividWalls-CopilotKit-Workflow.json into n8n"
        echo "3. Install the WordPress plugin"
    else
        echo -e "${GREEN}✅ Ready for CopilotKit integration${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Install the WordPress plugin"
        echo "2. Test the integration"
    fi
else
    echo -e "${RED}❌ Some DNS/SSL issues found${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting steps:${NC}"
    echo "1. Check DNS records in DigitalOcean control panel"
    echo "2. Verify Caddy configuration and restart if needed"
    echo "3. Check Docker containers are running: docker ps"
    echo "4. Review Caddy logs: docker logs caddy"
fi

echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "• Check DNS: dig n8n.vividwalls.blog"
echo "• Test SSL: curl -I https://n8n.vividwalls.blog"
echo "• View containers: ssh -i ~/.ssh/digitalocean root@157.230.13.13 'docker ps'"
echo "• Restart Caddy: ssh -i ~/.ssh/digitalocean root@157.230.13.13 'cd /home/vivid/vivid_mas && docker-compose restart caddy'" 