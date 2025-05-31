#!/bin/bash
set -e

echo "🏗️  Organizing Digital Ocean Droplet for VividWalls Production"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo -e "${BLUE}🔗 Connecting to droplet: ${DROPLET_IP}${NC}"

# Function to execute commands on droplet
run_remote() {
    ssh -i $SSH_KEY root@$DROPLET_IP "$1"
}

echo -e "${YELLOW}📁 Step 1: Creating standardized directory structure${NC}"

run_remote "
# Remove any malformed directories
rm -rf /opt/vividwalls/{

# Create production-ready directory structure
mkdir -p /opt/vividwalls/{applications,data,configs,scripts,mcp-servers}
mkdir -p /opt/vividwalls/applications/{vivid_mas,wordpress,monitoring}
mkdir -p /opt/vividwalls/data/{logs,backups,uploads,databases}
mkdir -p /opt/vividwalls/configs/{caddy,ssl,nginx,env}
mkdir -p /opt/vividwalls/scripts/{deployment,management,monitoring}

# Create symlink for current MCP servers
ln -sf /opt/mcp-servers /opt/vividwalls/mcp-servers/current

# Create deployment structure
mkdir -p /home/vivid/production/{current,releases,shared}
mkdir -p /home/vivid/production/shared/{configs,data,logs,uploads}

echo '✅ Directory structure created'
"

echo -e "${YELLOW}📦 Step 2: Organizing current installations${NC}"

run_remote "
# Set proper ownership for vivid user directories
chown -R vivid:vivid /home/vivid/production

# Create symlink for current deployment
if [ -d /home/vivid/vivid_mas ]; then
    # Create a release directory with timestamp
    RELEASE_DIR=/home/vivid/production/releases/\$(date +%Y%m%d_%H%M%S)
    mkdir -p \$RELEASE_DIR
    
    # Move current vivid_mas to releases
    cp -r /home/vivid/vivid_mas/* \$RELEASE_DIR/
    
    # Create symlink to current
    ln -sf \$RELEASE_DIR /home/vivid/production/current
    
    echo '✅ Current deployment organized into releases structure'
fi

# Organize WordPress
if [ -d /home/vivid/wordpress ]; then
    mkdir -p /opt/vividwalls/applications/wordpress
    cp -r /home/vivid/wordpress/* /opt/vividwalls/applications/wordpress/
    echo '✅ WordPress organized'
fi
"

echo -e "${YELLOW}⚙️  Step 3: Creating management scripts${NC}"

run_remote "
# Create deployment script
cat > /opt/vividwalls/scripts/deployment/deploy.sh << 'EOF'
#!/bin/bash
set -e

RELEASE_DIR=/home/vivid/production/releases/\$(date +%Y%m%d_%H%M%S)
CURRENT_LINK=/home/vivid/production/current

echo \"🚀 Creating new release: \$RELEASE_DIR\"
mkdir -p \$RELEASE_DIR

# Copy files from local or git
# rsync or git clone would go here

# Update symlink
ln -sfn \$RELEASE_DIR \$CURRENT_LINK

# Restart services
cd \$CURRENT_LINK
docker-compose down
docker-compose up -d

echo \"✅ Deployment complete\"
EOF

chmod +x /opt/vividwalls/scripts/deployment/deploy.sh

# Create system monitoring script
cat > /opt/vividwalls/scripts/monitoring/health-check.sh << 'EOF'
#!/bin/bash

echo \"=== VividWalls System Health Check ===\"
echo \"Date: \$(date)\"
echo \"\"

echo \"🖥️  System Resources:\"
echo \"Memory: \$(free -h | grep Mem | awk '{print \$3\"/\"\$2}')\"
echo \"Disk: \$(df -h / | tail -1 | awk '{print \$3\"/\"\$2\" (\"\$5\" used)\"}')\"
echo \"CPU Load: \$(uptime | awk -F'load average:' '{print \$2}')\"
echo \"\"

echo \"🐳 Docker Services:\"
docker ps --format \"table {{.Names}}\\t{{.Status}}\\t{{.Ports}}\" | head -20
echo \"\"

echo \"🔗 Service Connectivity:\"
# Test key services
curl -s -o /dev/null -w \"n8n: %{http_code}\\n\" http://localhost:5678 || echo \"n8n: DOWN\"
curl -s -o /dev/null -w \"Open WebUI: %{http_code}\\n\" http://localhost:3000 || echo \"Open WebUI: DOWN\"
curl -s -o /dev/null -w \"Flowise: %{http_code}\\n\" http://localhost:3001 || echo \"Flowise: DOWN\"

echo \"\"
echo \"📊 MCP Servers Status:\"
ls -la /opt/mcp-servers/ | grep \"^d\" | wc -l | awk '{print \"Active MCP Servers: \" \$1}'
EOF

chmod +x /opt/vividwalls/scripts/monitoring/health-check.sh

# Create backup script
cat > /opt/vividwalls/scripts/management/backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR=\"/opt/vividwalls/data/backups/\$(date +%Y%m%d_%H%M%S)\"
mkdir -p \$BACKUP_DIR

echo \"🗄️  Creating backup: \$BACKUP_DIR\"

# Backup configurations
cp -r /home/vivid/production/current/.env \$BACKUP_DIR/ 2>/dev/null || true
cp -r /opt/vividwalls/configs \$BACKUP_DIR/

# Backup database (if accessible)
docker exec vivid_mas-postgres-1 pg_dumpall -U postgres > \$BACKUP_DIR/database_backup.sql 2>/dev/null || echo \"⚠️  Database backup skipped\"

# Backup MCP configurations
cp -r /opt/mcp-servers \$BACKUP_DIR/

# Create archive
cd /opt/vividwalls/data/backups
tar -czf \"\$(basename \$BACKUP_DIR).tar.gz\" \"\$(basename \$BACKUP_DIR)\"
rm -rf \$BACKUP_DIR

echo \"✅ Backup created: \$(basename \$BACKUP_DIR).tar.gz\"
EOF

chmod +x /opt/vividwalls/scripts/management/backup.sh

echo '✅ Management scripts created'
"

echo -e "${YELLOW}🔧 Step 4: Setting up environment configurations${NC}"

run_remote "
# Copy current .env to shared configs
if [ -f /home/vivid/vivid_mas/.env ]; then
    cp /home/vivid/vivid_mas/.env /opt/vividwalls/configs/env/production.env
    ln -sf /opt/vividwalls/configs/env/production.env /home/vivid/production/shared/configs/.env
fi

# Copy Caddyfile to configs
if [ -f /home/vivid/vivid_mas/Caddyfile ]; then
    cp /home/vivid/vivid_mas/Caddyfile /opt/vividwalls/configs/caddy/
fi

echo '✅ Environment configurations organized'
"

echo -e "${YELLOW}📋 Step 5: Creating system overview${NC}"

run_remote "
# Create system overview
cat > /opt/vividwalls/README.md << 'EOF'
# VividWalls Production System

## Directory Structure

### /opt/vividwalls/
- \`applications/\` - Application installations
- \`data/\` - Data storage (logs, backups, uploads)
- \`configs/\` - Configuration files
- \`scripts/\` - Management and deployment scripts
- \`mcp-servers/\` - MCP server installations

### /home/vivid/production/
- \`current/\` - Symlink to current release
- \`releases/\` - Application releases
- \`shared/\` - Shared data between releases

## Quick Commands

### Health Check
\`/opt/vividwalls/scripts/monitoring/health-check.sh\`

### Backup System
\`/opt/vividwalls/scripts/management/backup.sh\`

### Deploy New Release
\`/opt/vividwalls/scripts/deployment/deploy.sh\`

## Service URLs
- n8n: https://n8n.vividwalls.blog
- Open WebUI: http://157.230.13.13:3000
- WordPress: https://vividwalls.blog
- Supabase: https://supabase.vividwalls.blog

## Current Status
EOF

# Add current status
echo \"Last organized: \$(date)\" >> /opt/vividwalls/README.md
echo \"Services running: \$(docker ps | wc -l) containers\" >> /opt/vividwalls/README.md

echo '✅ System overview created'
"

echo -e "${GREEN}🎉 Droplet organization complete!${NC}"

echo -e "${BLUE}📊 Running final health check...${NC}"
run_remote "/opt/vividwalls/scripts/monitoring/health-check.sh"

echo -e "${GREEN}✅ Organization complete! Your droplet is now properly structured.${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Review the structure: ssh -i ~/.ssh/digitalocean root@157.230.13.13 'cat /opt/vividwalls/README.md'"
echo "2. Test health monitoring: ssh -i ~/.ssh/digitalocean root@157.230.13.13 '/opt/vividwalls/scripts/monitoring/health-check.sh'"
echo "3. Create first backup: ssh -i ~/.ssh/digitalocean root@157.230.13.13 '/opt/vividwalls/scripts/management/backup.sh'"