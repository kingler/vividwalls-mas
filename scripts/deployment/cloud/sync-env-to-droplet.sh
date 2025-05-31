#!/bin/bash

# Script to synchronize .env file from local to droplet with secure key generation
# This ensures both environments have the same configuration with proper security

set -e

DROPLET_IP="159.223.204.139"
DROPLET_USER="vivid"
DROPLET_PATH="/home/vivid/vivid_mas/.env"
LOCAL_ENV_FILE=".env"

echo "🔄 Synchronizing .env file to droplet..."

# First, backup the current droplet .env file
echo "📦 Creating backup of current droplet .env file..."
ssh ${DROPLET_USER}@${DROPLET_IP} "cp ${DROPLET_PATH} ${DROPLET_PATH}.backup.$(date +%Y%m%d_%H%M%S)"

# Copy the local .env file to droplet
echo "📤 Copying local .env file to droplet..."
scp ${LOCAL_ENV_FILE} ${DROPLET_USER}@${DROPLET_IP}:${DROPLET_PATH}

# Generate secure keys on the droplet
echo "🔐 Generating secure keys on droplet..."
ssh ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Generate secure random passwords and keys
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
VAULT_ENC_KEY=$(openssl rand -hex 16)  # 32 characters for AES-256-GCM
SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
REALTIME_SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

echo "Generated secure keys:"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
echo "VAULT_ENC_KEY: ${VAULT_ENC_KEY}"
echo "SECRET_KEY_BASE: ${SECRET_KEY_BASE}"
echo "REALTIME_SECRET_KEY_BASE: ${REALTIME_SECRET_KEY_BASE}"

# Replace placeholder values in .env file
sed -i "s/your-super-secret-and-long-postgres-password/${POSTGRES_PASSWORD}/g" .env
sed -i "s/your-32-character-encryption-key/${VAULT_ENC_KEY}/g" .env
sed -i "s/UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1\/u2oq/${SECRET_KEY_BASE}/g" .env

# Also update the PGRST_DB_URI with the new password
PGRST_DB_URI="postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/postgres"
if grep -q "PGRST_DB_URI=" .env; then
    sed -i "s|PGRST_DB_URI=.*|PGRST_DB_URI=${PGRST_DB_URI}|g" .env
else
    echo "PGRST_DB_URI=${PGRST_DB_URI}" >> .env
fi

echo "✅ .env file updated with secure keys"
echo "📋 Verifying key replacements..."
grep -E "(POSTGRES_PASSWORD|VAULT_ENC_KEY|SECRET_KEY_BASE)" .env | head -5
EOF

echo "✅ .env file synchronization complete!"
echo "🔄 Ready to restart Supabase services with new configuration" 