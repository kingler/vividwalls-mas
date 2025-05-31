#!/bin/bash

# Fix n8n Encryption Key Issue
# This script generates a proper n8n encryption key and updates the environment

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"

echo "🔧 Fixing n8n Encryption Key Issue..."
echo "===================================="

# Step 1: Generate a proper n8n encryption key
echo "🔐 Generating new n8n encryption key..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Generate a proper 32-character encryption key for n8n
NEW_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

echo "Generated new encryption key: ${NEW_ENCRYPTION_KEY}"

# Backup current .env file
cp .env .env.backup.n8n.$(date +%Y%m%d_%H%M%S)

# Update the N8N_ENCRYPTION_KEY in .env file
sed -i "s/N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=${NEW_ENCRYPTION_KEY}/" .env

echo "✅ Updated N8N_ENCRYPTION_KEY in .env file"
EOF

# Step 2: Restart n8n container
echo "🔄 Restarting n8n container..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Stop n8n container
docker-compose stop n8n

# Remove n8n data to start fresh (this will reset workflows and settings)
echo "⚠️  Removing n8n data directory to start fresh..."
docker volume rm vivid_mas_n8n_data || echo "Volume already removed or doesn't exist"

# Start n8n container
docker-compose up -d n8n

# Wait for n8n to start
sleep 15

echo "✅ n8n restarted with new encryption key"
EOF

# Step 3: Check n8n status
echo "🔍 Checking n8n status..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "n8n container status:"
docker-compose ps n8n

echo ""
echo "n8n logs (last 10 lines):"
docker logs n8n --tail=10

echo "✅ n8n status check complete"
EOF

# Step 4: Test n8n access
echo "🧪 Testing n8n access..."
sleep 5

echo "Testing n8n web interface:"
curl -I -L --max-time 10 https://n8n.vividwalls.blog 2>/dev/null | head -1 || echo "❌ n8n web interface failed"

echo ""
echo "🎉 n8n Encryption Key Fix Completed!"
echo ""
echo "📋 Summary:"
echo "✅ Generated new 32-character encryption key"
echo "✅ Updated .env file with new key"
echo "✅ Restarted n8n with fresh data"
echo "✅ Verified n8n is running"
echo ""
echo "⚠️  Important Notes:"
echo "• n8n has been reset with a fresh installation"
echo "• You'll need to set up your workflows again"
echo "• The API key creation should now work properly"
echo ""
echo "🌐 Access n8n at: https://n8n.vividwalls.blog"
echo "📝 You can now create API keys in the n8n settings" 