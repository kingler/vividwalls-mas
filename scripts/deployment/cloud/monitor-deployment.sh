#!/bin/bash

# Monitor VividMAS Deployment Script
# This script monitors the GitHub Actions deployment and server health

set -e

DROPLET_IP="157.230.13.13"
GITHUB_REPO="kingler/vivid_mas"
SSH_KEY="~/.ssh/digitalocean"

echo "🔍 VividMAS Deployment Monitor"
echo "================================"
echo "Droplet IP: $DROPLET_IP"
echo "GitHub Repo: $GITHUB_REPO"
echo ""

# Function to check GitHub Actions status
check_github_actions() {
    echo "📊 GitHub Actions Status:"
    echo "Visit: https://github.com/$GITHUB_REPO/actions"
    echo ""
}

# Function to check server connectivity
check_server_connectivity() {
    echo "🌐 Testing server connectivity..."
    if ping -c 3 $DROPLET_IP > /dev/null 2>&1; then
        echo "✅ Server is reachable"
    else
        echo "❌ Server is not reachable"
        return 1
    fi
    echo ""
}

# Function to check SSH access
check_ssh_access() {
    echo "🔐 Testing SSH access..."
    if ssh -i $SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'SSH connection successful'" 2>/dev/null; then
        echo "✅ SSH access working"
    else
        echo "❌ SSH access failed"
        echo "💡 Try using DigitalOcean web console if SSH is unresponsive"
        return 1
    fi
    echo ""
}

# Function to check running containers
check_containers() {
    echo "🐳 Checking running containers..."
    ssh -i $SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$DROPLET_IP "
        echo 'Container Status:'
        docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo 'Docker not accessible'
        echo ''
        echo 'System Resources:'
        free -h
        echo ''
        df -h /
    " 2>/dev/null || echo "❌ Could not connect to check containers"
    echo ""
}

# Function to check service endpoints
check_service_endpoints() {
    echo "🌍 Testing service endpoints..."
    
    services=(
        "https://n8n.vividwalls.blog"
        "https://webui.vividwalls.blog" 
        "https://vividwalls.blog"
        "https://supabase.vividwalls.blog"
    )
    
    for service in "${services[@]}"; do
        echo -n "Testing $service... "
        if curl -f -s --max-time 10 "$service" > /dev/null 2>&1; then
            echo "✅ Responding"
        else
            echo "❌ Not responding"
        fi
    done
    echo ""
}

# Function to show deployment logs
show_deployment_logs() {
    echo "📋 Recent deployment logs..."
    ssh -i $SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$DROPLET_IP "
        cd /home/vivid/vivid_mas 2>/dev/null || cd /root
        echo 'Recent Docker Compose logs:'
        docker compose -f docker-compose.optimized.yml logs --tail=20 2>/dev/null || echo 'No optimized compose logs available'
        echo ''
        echo 'System logs (last 10 lines):'
        journalctl --no-pager -n 10 2>/dev/null || echo 'Cannot access system logs'
    " 2>/dev/null || echo "❌ Could not retrieve logs"
    echo ""
}

# Main monitoring function
main() {
    echo "Starting deployment monitoring..."
    echo ""
    
    # Check GitHub Actions
    check_github_actions
    
    # Wait a moment for deployment to start
    echo "⏳ Waiting 30 seconds for deployment to initialize..."
    sleep 30
    
    # Check server status
    check_server_connectivity
    
    # Check SSH access
    if check_ssh_access; then
        # If SSH works, check containers and services
        check_containers
        show_deployment_logs
        
        echo "⏳ Waiting for services to start (60 seconds)..."
        sleep 60
        
        check_service_endpoints
    fi
    
    echo "🎯 Monitoring complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Check GitHub Actions: https://github.com/$GITHUB_REPO/actions"
    echo "2. Monitor services: https://n8n.vividwalls.blog"
    echo "3. Check WordPress: https://vividwalls.blog"
    echo "4. If issues persist, run: ./scripts/diagnose-server-health.sh"
}

# Run the monitoring
main 