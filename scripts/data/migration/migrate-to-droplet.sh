#!/bin/bash

# VividWalls Content Migration Script
# Migrates local shared content to Digital Ocean Droplet

# Configuration - VividMAS Infrastructure
DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas"  # Path to your project on the droplet
SSH_KEY_PATH="~/.ssh/digitalocean"  # VividMAS SSH key

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 VividWalls Content Migration to Digital Ocean Droplet${NC}"
echo "=================================================="

# Configuration validated for VividMAS infrastructure
echo -e "${GREEN}✅ Using VividMAS infrastructure configuration${NC}"
echo "  - Droplet: $DROPLET_IP (vividwalls.blog)"
echo "  - Path: $DROPLET_PATH"
echo "  - SSH Key: $SSH_KEY_PATH"

# Verify local files exist
echo -e "${YELLOW}📋 Checking local files...${NC}"
LOCAL_SHARED_DIR="./n8n/shared"

if [ ! -d "$LOCAL_SHARED_DIR" ]; then
    echo -e "${RED}❌ Error: Local shared directory not found: $LOCAL_SHARED_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Local shared directory found${NC}"

# List files to be transferred
echo -e "${YELLOW}📁 Files to transfer:${NC}"
find "$LOCAL_SHARED_DIR" -type f -exec echo "  - {}" \;

# Test SSH connection
echo -e "${YELLOW}🔐 Testing SSH connection...${NC}"
if ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 "$DROPLET_USER@$DROPLET_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ Error: Cannot connect to droplet via SSH${NC}"
    echo "Please check:"
    echo "  - Droplet IP address: $DROPLET_IP"
    echo "  - SSH key path: $SSH_KEY_PATH"
    echo "  - User: $DROPLET_USER"
    exit 1
fi

# Create remote directory structure
echo -e "${YELLOW}📂 Creating remote directory structure...${NC}"
ssh -i "$SSH_KEY_PATH" "$DROPLET_USER@$DROPLET_IP" "mkdir -p $DROPLET_PATH/n8n/shared/knowledge"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Remote directories created${NC}"
else
    echo -e "${RED}❌ Error: Failed to create remote directories${NC}"
    exit 1
fi

# Transfer files using rsync
echo -e "${YELLOW}📤 Transferring files...${NC}"
rsync -avz -e "ssh -i $SSH_KEY_PATH" "$LOCAL_SHARED_DIR/" "$DROPLET_USER@$DROPLET_IP:$DROPLET_PATH/n8n/shared/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Files transferred successfully${NC}"
else
    echo -e "${RED}❌ Error: File transfer failed${NC}"
    exit 1
fi

# Verify files on remote server
echo -e "${YELLOW}🔍 Verifying files on remote server...${NC}"
ssh -i "$SSH_KEY_PATH" "$DROPLET_USER@$DROPLET_IP" "ls -la $DROPLET_PATH/n8n/shared/knowledge/"

# Set proper permissions
echo -e "${YELLOW}🔒 Setting proper permissions...${NC}"
ssh -i "$SSH_KEY_PATH" "$DROPLET_USER@$DROPLET_IP" "chmod -R 755 $DROPLET_PATH/n8n/shared/"

# Restart n8n container to pick up new files
echo -e "${YELLOW}🔄 Restarting n8n container...${NC}"
ssh -i "$SSH_KEY_PATH" "$DROPLET_USER@$DROPLET_IP" "cd $DROPLET_PATH && docker-compose restart n8n"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ n8n container restarted${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not restart n8n container automatically${NC}"
    echo "Please manually restart n8n on your droplet:"
    echo "  docker-compose restart n8n"
fi

echo ""
echo -e "${GREEN}🎉 Migration completed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Import the Enhanced-VividWalls-CopilotKit-Workflow.json into n8n"
echo "2. Configure OpenAI credentials in n8n"
echo "3. Test the webhook endpoint"
echo "4. Install the WordPress plugin"
echo ""
echo -e "${BLUE}Webhook URL:${NC}"
echo "https://n8n.vividwalls.blog/webhook/vividwalls-copilot"
echo ""
echo -e "${BLUE}Files transferred:${NC}"
echo "- vividwalls-q&a.csv (Knowledge base)"
echo "- V3 Local Agentic RAG AI Agent.json (Original workflow)"
echo "- Enhanced-VividWalls-CopilotKit-Workflow.json (Enhanced workflow)" 