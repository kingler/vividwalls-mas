#!/bin/bash

# VividMAS Unified Network Deployment Script
# This script deploys all services on a single vivid_mas network for better connectivity

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

SERVER_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

print_header "🚀 VividMAS Unified Network Deployment"

print_status "Connecting to server: $SERVER_IP"

# Function to run commands on the server
run_remote() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$SERVER_IP" "$1"
}

# Function to copy files to server
copy_to_server() {
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$1" root@"$SERVER_IP":"$2"
}

print_status "📋 Step 1: Stopping existing services"
run_remote "cd /home/vivid/vivid_mas && docker-compose down --remove-orphans || true"
run_remote "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml down --remove-orphans || true"

print_status "📋 Step 2: Removing old networks"
run_remote "docker network rm wordpress_network || true"
run_remote "docker network prune -f || true"

print_status "📋 Step 3: Creating unified vivid_mas network"
run_remote "docker network create vivid_mas --driver bridge || echo 'Network already exists'"

print_status "📋 Step 4: Uploading updated configuration files"
copy_to_server "vivid_mas/docker-compose.yml" "/home/vivid/vivid_mas/"
copy_to_server "vivid_mas/wordpress-compose.optimized.yml" "/home/vivid/vivid_mas/"

print_status "📋 Step 5: Starting services with unified network"

print_status "Starting main VividMAS stack..."
run_remote "cd /home/vivid/vivid_mas && COMPOSE_PROFILES=cpu docker-compose up -d"

print_status "Waiting for main services to stabilize..."
sleep 30

print_status "Starting WordPress stack..."
run_remote "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml up -d"

print_status "📋 Step 6: Verifying network connectivity"
sleep 15

print_status "Checking service status..."
run_remote "cd /home/vivid/vivid_mas && docker-compose ps"
run_remote "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml ps"

print_status "Checking network connectivity..."
run_remote "docker network inspect vivid_mas"

print_status "Testing inter-service connectivity..."
run_remote "docker exec n8n ping -c 2 postgres || echo 'n8n -> postgres: FAILED'"
run_remote "docker exec langfuse-web ping -c 2 postgres || echo 'langfuse -> postgres: FAILED'"
run_remote "docker exec langfuse-web ping -c 2 redis || echo 'langfuse -> redis: FAILED'"
run_remote "docker exec langfuse-web ping -c 2 clickhouse || echo 'langfuse -> clickhouse: FAILED'"
run_remote "docker exec wordpress-multisite ping -c 2 wordpress-mysql || echo 'wordpress -> mysql: FAILED'"

print_success "🎉 Unified network deployment complete!"

echo ""
print_header "📊 Service Status Summary"
echo ""
print_status "🌐 All services are now on the unified 'vivid_mas' network"
print_status "🔗 Services can communicate using container names:"
echo "   • n8n -> postgres:5432"
echo "   • langfuse -> postgres:5432, redis:6379, clickhouse:8123"
echo "   • wordpress -> wordpress-mysql:3306, wordpress-redis:6379"
echo "   • All services -> ollama:11434"
echo ""
print_status "🌍 External access points:"
echo "   • n8n: https://n8n.vividwalls.blog"
echo "   • Open WebUI: https://webui.vividwalls.blog"
echo "   • Langfuse: http://$SERVER_IP:3002"
echo "   • WordPress: https://vividwalls.blog"
echo "   • SearXNG: http://$SERVER_IP:8080"
echo ""
print_status "🔧 Troubleshooting commands:"
echo "   • Check network: ssh root@$SERVER_IP 'docker network inspect vivid_mas'"
echo "   • View logs: ssh root@$SERVER_IP 'cd /home/vivid/vivid_mas && docker-compose logs -f'"
echo "   • Test connectivity: ssh root@$SERVER_IP 'docker exec <container> ping <target>'"
echo ""
print_success "All services should now have proper network connectivity!" 