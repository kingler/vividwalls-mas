#!/bin/bash
set -e

# VividWalls Local to Droplet Sync Script
# Based on the organized droplet structure

LOCAL_PROJECT_PATH="/Users/kinglerbercy/Projects/vivid_mas"
DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 VividWalls Local to Droplet Sync${NC}"

# Check if local project exists
if [ ! -d "$LOCAL_PROJECT_PATH" ]; then
    echo "❌ Local project not found at: $LOCAL_PROJECT_PATH"
    exit 1
fi

# Create release name
RELEASE_NAME=$(date +%Y%m%d_%H%M%S)
echo -e "${YELLOW}📦 Creating release: $RELEASE_NAME${NC}"

# Create release directory on droplet
ssh -i $SSH_KEY root@$DROPLET_IP "mkdir -p /home/vivid/production/releases/$RELEASE_NAME"

echo -e "${YELLOW}📤 Syncing files to droplet...${NC}"

# Sync project files (excluding large/unnecessary files)
rsync -avz --progress \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='supabase/docker/volumes' \
    --exclude='*.log' \
    --exclude='.env' \
    -e "ssh -i $SSH_KEY" \
    $LOCAL_PROJECT_PATH/ \
    root@$DROPLET_IP:/home/vivid/production/releases/$RELEASE_NAME/

echo -e "${YELLOW}⚙️  Configuring release on droplet...${NC}"

# Configure the release on droplet
ssh -i $SSH_KEY root@$DROPLET_IP "
    # Set proper ownership
    chown -R vivid:vivid /home/vivid/production/releases/$RELEASE_NAME
    
    # Copy production environment file
    if [ -f /opt/vividwalls/configs/env/production.env ]; then
        cp /opt/vividwalls/configs/env/production.env /home/vivid/production/releases/$RELEASE_NAME/.env
    fi
    
    # Update current symlink
    ln -sfn /home/vivid/production/releases/$RELEASE_NAME /home/vivid/production/current
    
    echo '✅ Release configured'
"

echo -e "${YELLOW}🐳 Restarting services...${NC}"

# Restart services with the new release
ssh -i $SSH_KEY root@$DROPLET_IP "
    cd /home/vivid/production/current
    
    # Graceful restart
    docker-compose down
    sleep 5
    docker-compose up -d
    
    echo '✅ Services restarted'
"

echo -e "${YELLOW}🔍 Running health check...${NC}"

# Wait a moment for services to start
sleep 10

# Run health check
ssh -i $SSH_KEY root@$DROPLET_IP "/opt/vividwalls/scripts/monitoring/health-check.sh"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}📊 Release: $RELEASE_NAME${NC}"
echo -e "${BLUE}🌐 Services available at:${NC}"
echo "   - n8n: https://n8n.vividwalls.blog"
echo "   - Open WebUI: http://$DROPLET_IP:3000"
echo "   - WordPress: https://wordpress.vividwalls.blog" 
echo "   - Supabase: https://supabase.vividwalls.blog"

echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Test all services are working"
echo "2. Import n8n workflows if needed"
echo "3. Configure MCP server API credentials"
echo "4. Run full system backup: ssh -i $SSH_KEY root@$DROPLET_IP '/opt/vividwalls/scripts/management/backup.sh'"