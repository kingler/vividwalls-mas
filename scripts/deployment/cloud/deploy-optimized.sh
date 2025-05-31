#!/bin/bash

# =============================================================================
# VividMAS Optimized Deployment Script
# Services: n8n, WordPress, Supabase, OpenWebUI, Caddy
# Recommended: 4 vCPUs, 8GB RAM Digital Ocean Droplet
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
   exit 1
fi

log "🚀 Starting VividMAS Optimized Deployment"
log "📋 Services: n8n, WordPress, Supabase, OpenWebUI, Caddy"

# =============================================================================
# Step 1: System Requirements Check
# =============================================================================
log "🔍 Checking system requirements..."

# Check available memory
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
if [ "$TOTAL_MEM" -lt 7000 ]; then
    warn "Available memory: ${TOTAL_MEM}MB. Recommended: 8GB (8192MB)"
    warn "Consider upgrading your droplet for optimal performance"
else
    log "✅ Memory check passed: ${TOTAL_MEM}MB available"
fi

# Check available disk space
AVAILABLE_DISK=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_DISK" -lt 50 ]; then
    error "Insufficient disk space: ${AVAILABLE_DISK}GB available. Need at least 50GB"
    exit 1
else
    log "✅ Disk space check passed: ${AVAILABLE_DISK}GB available"
fi

# =============================================================================
# Step 2: Stop Current Services
# =============================================================================
log "🛑 Stopping current services to free up resources..."

# Stop all current docker containers
if docker ps -q | grep -q .; then
    log "Stopping all running containers..."
    docker stop $(docker ps -q) 2>/dev/null || true
fi

# Stop WordPress if running
if [ -f "wordpress-compose.yml" ]; then
    log "Stopping WordPress services..."
    docker-compose -f wordpress-compose.yml down 2>/dev/null || true
fi

# Stop main services if running
if [ -f "vivid_mas/docker-compose.yml" ]; then
    log "Stopping main VividMAS services..."
    cd vivid_mas
    docker-compose down 2>/dev/null || true
    cd ..
fi

# =============================================================================
# Step 3: Clean Up Resources
# =============================================================================
log "🧹 Cleaning up Docker resources..."

# Remove unused containers, networks, images
docker system prune -f
docker volume prune -f

# Remove specific heavy services that we're not using
UNUSED_IMAGES=(
    "ollama/ollama"
    "qdrant/qdrant"
    "flowiseai/flowise"
    "searxng/searxng"
    "langfuse/langfuse"
    "clickhouse/clickhouse-server"
    "minio/minio"
)

for image in "${UNUSED_IMAGES[@]}"; do
    if docker images | grep -q "$image"; then
        log "Removing unused image: $image"
        docker rmi "$image" 2>/dev/null || true
    fi
done

# =============================================================================
# Step 4: Setup Optimized Configuration
# =============================================================================
log "⚙️ Setting up optimized configuration..."

cd vivid_mas

# Backup current configuration
if [ -f ".env" ]; then
    log "Backing up current .env to .env.backup"
    cp .env .env.backup
fi

if [ -f "docker-compose.yml" ]; then
    log "Backing up current docker-compose.yml"
    cp docker-compose.yml docker-compose.yml.backup
fi

if [ -f "Caddyfile" ]; then
    log "Backing up current Caddyfile"
    cp Caddyfile Caddyfile.backup
fi

# Use optimized configurations
log "Applying optimized configurations..."
cp env.optimized .env
cp docker-compose.optimized.yml docker-compose.yml
cp Caddyfile.optimized Caddyfile

# Setup WordPress optimized config
cd ..
if [ -f "wordpress-compose.yml" ]; then
    cp wordpress-compose.yml wordpress-compose.yml.backup
fi
cp wordpress-compose.optimized.yml wordpress-compose.yml

# =============================================================================
# Step 5: DNS Configuration Check
# =============================================================================
log "🌐 Checking DNS configuration..."

DOMAINS=(
    "n8n.vividwalls.blog"
    "webui.vividwalls.blog"
    "supabase.vividwalls.blog"
    "vividwalls.blog"
)

for domain in "${DOMAINS[@]}"; do
    if nslookup "$domain" >/dev/null 2>&1; then
        log "✅ DNS configured for: $domain"
    else
        warn "❌ DNS not configured for: $domain"
        warn "Please add A record: $domain -> 157.230.13.13"
    fi
done

# =============================================================================
# Step 6: Start Optimized Services
# =============================================================================
log "🚀 Starting optimized services..."

# Start Supabase first (dependency for n8n)
cd vivid_mas
log "Starting Supabase services..."
docker-compose up -d db auth rest realtime storage

# Wait for Supabase to be ready
log "Waiting for Supabase to be ready..."
sleep 30

# Start n8n
log "Starting n8n..."
docker-compose up -d n8n

# Start OpenWebUI
log "Starting OpenWebUI..."
docker-compose up -d open-webui

# Start Caddy
log "Starting Caddy reverse proxy..."
docker-compose up -d caddy

# Start WordPress
cd ..
log "Starting WordPress..."
docker-compose up -d

# =============================================================================
# Step 7: Health Checks
# =============================================================================
log "🏥 Performing health checks..."

sleep 10

# Check service status
cd vivid_mas
SERVICES=("n8n" "open-webui" "caddy")
for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log "✅ $service is running"
    else
        error "❌ $service failed to start"
    fi
done

# Check WordPress
cd ..
if docker-compose ps | grep -q "wordpress.*Up"; then
    log "✅ WordPress is running"
else
    error "❌ WordPress failed to start"
fi

# =============================================================================
# Step 8: Display Access Information
# =============================================================================
log "🎉 Deployment completed!"
echo ""
echo "==============================================================================="
echo "🌟 VividMAS Optimized Stack - Access Information"
echo "==============================================================================="
echo ""
echo "🔗 Service URLs:"
echo "   • Main Website:    https://vividwalls.blog"
echo "   • n8n Workflows:   https://n8n.vividwalls.blog"
echo "   • AI Chat:         https://webui.vividwalls.blog"
echo "   • Supabase:        https://supabase.vividwalls.blog"
echo ""
echo "📊 Resource Usage:"
echo "   • Estimated RAM:   ~6-7GB"
echo "   • Services:        4 main + Caddy"
echo "   • Databases:       2 (PostgreSQL + MySQL)"
echo ""
echo "🔧 Management Commands:"
echo "   • View logs:       docker-compose logs -f [service]"
echo "   • Restart:         docker-compose restart [service]"
echo "   • Stop all:        docker-compose down"
echo ""
echo "⚠️  Important Notes:"
echo "   • SSL certificates will be automatically generated"
echo "   • Ensure all DNS records are configured"
echo "   • Monitor memory usage with: free -h"
echo ""
echo "==============================================================================="

# =============================================================================
# Step 9: Resource Monitoring Setup
# =============================================================================
log "📊 Setting up resource monitoring..."

# Create monitoring script
cat > monitor-resources.sh << 'EOF'
#!/bin/bash
echo "=== VividMAS Resource Monitor ==="
echo "Date: $(date)"
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "Docker Container Status:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
echo "Top Memory Consumers:"
ps aux --sort=-%mem | head -10
EOF

chmod +x monitor-resources.sh

log "✅ Resource monitor created: ./monitor-resources.sh"
log "🎯 Run './monitor-resources.sh' to check system resources"

# Final memory check
CURRENT_MEM=$(free -m | awk 'NR==2{printf "%.0f", $3}')
log "📈 Current memory usage: ${CURRENT_MEM}MB"

if [ "$CURRENT_MEM" -gt 6000 ]; then
    warn "High memory usage detected. Consider monitoring closely."
fi

log "🚀 VividMAS Optimized deployment completed successfully!" 