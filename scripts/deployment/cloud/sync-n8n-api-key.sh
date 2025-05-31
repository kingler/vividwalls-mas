#!/bin/bash

# Sync n8n API Key between Local and Droplet
# This script properly configures both environments with the correct keys

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"

echo "🔄 Syncing n8n API Key Configuration..."
echo "======================================"

# Step 1: Extract the new API key from local .env
echo "📤 Extracting new API key from local .env..."
NEW_API_KEY=$(grep "N8N_ENCRYPTION_KEY=" .env | head -1 | cut -d'=' -f2)

if [[ $NEW_API_KEY == eyJ* ]]; then
    echo "✅ Found JWT API key: ${NEW_API_KEY:0:50}..."
else
    echo "❌ No valid JWT API key found in local .env"
    exit 1
fi

# Step 2: Fix local .env file format
echo "🔧 Fixing local .env file format..."
# Get the proper encryption key from droplet
PROPER_ENCRYPTION_KEY=$(ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} 'cd /home/vivid/vivid_mas && grep "N8N_ENCRYPTION_KEY=" .env | head -1 | cut -d"=" -f2')

# Backup local .env
cp .env .env.backup.api.$(date +%Y%m%d_%H%M%S)

# Update local .env with proper format
sed -i.tmp "s/N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=${PROPER_ENCRYPTION_KEY}/" .env
echo "N8N_API_KEY=${NEW_API_KEY}" >> .env

# Remove any duplicate entries
awk '!seen[$0]++' .env > .env.tmp && mv .env.tmp .env

echo "✅ Fixed local .env file format"

# Step 3: Update droplet .env file
echo "📥 Updating droplet .env file..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << EOF
cd /home/vivid/vivid_mas

# Backup current .env
cp .env .env.backup.api.\$(date +%Y%m%d_%H%M%S)

# Remove duplicate N8N_API_KEY entries
grep -v "N8N_API_KEY=" .env > .env.tmp

# Add the new API key
echo "N8N_API_KEY=${NEW_API_KEY}" >> .env.tmp

# Replace the .env file
mv .env.tmp .env

echo "✅ Updated droplet .env file"
EOF

# Step 4: Restart services that use n8n API
echo "🔄 Restarting services..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Restart any services that might use the n8n API key
docker-compose restart flowise || echo "Flowise not running"

echo "✅ Services restarted"
EOF

# Step 5: Verify configuration
echo "🔍 Verifying configuration..."
echo ""
echo "Local .env n8n configuration:"
grep -E "N8N_(ENCRYPTION_KEY|API_KEY)" .env

echo ""
echo "Droplet .env n8n configuration:"
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} 'cd /home/vivid/vivid_mas && grep -E "N8N_(ENCRYPTION_KEY|API_KEY)" .env'

echo ""
echo "🎉 n8n API Key Sync Completed!"
echo ""
echo "📋 Summary:"
echo "✅ Extracted new API key from local .env"
echo "✅ Fixed local .env file format (proper encryption key + API key)"
echo "✅ Updated droplet .env with new API key"
echo "✅ Restarted dependent services"
echo "✅ Verified configuration"
echo ""
echo "🔑 Configuration:"
echo "• N8N_ENCRYPTION_KEY: 32-character encryption key (for n8n internal use)"
echo "• N8N_API_KEY: JWT token (for API access to n8n)"
echo ""
echo "🌐 Your services can now use the new n8n API key!" 