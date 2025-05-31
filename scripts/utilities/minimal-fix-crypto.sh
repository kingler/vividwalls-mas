#!/bin/bash

# Minimal fix: Only update the VAULT_ENC_KEY to fix the crypto error
# This preserves all existing passwords and connections

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas/.env"

echo "🔧 Applying minimal fix for crypto error..."

# Generate only a 32-character encryption key for VAULT_ENC_KEY
echo "🔐 Generating secure 32-character encryption key..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Generate exactly 32 characters for AES-256-GCM
VAULT_ENC_KEY=$(openssl rand -hex 16)  # 16 bytes = 32 hex characters

echo "Generated VAULT_ENC_KEY: ${VAULT_ENC_KEY}"

# Backup current .env
cp .env .env.backup.minimal.$(date +%Y%m%d_%H%M%S)

# Only replace the VAULT_ENC_KEY if it exists, or add it if missing
if grep -q "VAULT_ENC_KEY=" .env; then
    sed -i "s/VAULT_ENC_KEY=.*/VAULT_ENC_KEY=${VAULT_ENC_KEY}/" .env
else
    echo "VAULT_ENC_KEY=${VAULT_ENC_KEY}" >> .env
fi

echo "✅ Updated VAULT_ENC_KEY only"
echo "📋 Verifying change..."
grep "VAULT_ENC_KEY=" .env
EOF

echo "✅ Minimal crypto fix complete!"
echo "🔄 This should resolve the supabase-pooler crypto error without breaking existing connections" 