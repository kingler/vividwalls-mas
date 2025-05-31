#!/bin/bash

# Comprehensive script to safely update .env files with secure keys
# This ensures both local and droplet environments have matching secure credentials

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas"
LOCAL_ENV_FILE=".env"

echo "🔒 Starting secure environment update process..."

# Step 1: Generate secure keys locally first
echo "🔐 Generating secure keys..."
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
VAULT_ENC_KEY=$(openssl rand -hex 16)  # Exactly 32 characters for AES-256-GCM
SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
REALTIME_SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

echo "Generated keys:"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
echo "VAULT_ENC_KEY: ${VAULT_ENC_KEY} (${#VAULT_ENC_KEY} characters)"
echo "SECRET_KEY_BASE: ${SECRET_KEY_BASE}"
echo "REALTIME_SECRET_KEY_BASE: ${REALTIME_SECRET_KEY_BASE}"

# Step 2: Shutdown containers on droplet
echo "🛑 Shutting down affected containers on droplet..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "Stopping Supabase and related services..."
docker-compose down supabase-db supabase-auth supabase-rest supabase-realtime supabase-storage supabase-imgproxy supabase-meta supabase-studio supabase-edge-functions supabase-logflare supabase-vector supabase-pooler 2>/dev/null || true

echo "Stopping n8n and postgres services..."
docker-compose down n8n postgres langfuse-web langfuse-worker 2>/dev/null || true

echo "✅ Containers stopped"
EOF

# Step 3: Backup and update droplet .env file
echo "📦 Backing up and updating droplet .env file..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << EOF
cd ${DROPLET_PATH}

# Create backup
cp .env .env.backup.secure.$(date +%Y%m%d_%H%M%S)

# Update with secure keys
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PASSWORD}/" .env
sed -i "s/VAULT_ENC_KEY=.*/VAULT_ENC_KEY=${VAULT_ENC_KEY}/" .env
sed -i "s/SECRET_KEY_BASE=.*/SECRET_KEY_BASE=${SECRET_KEY_BASE}/" .env
sed -i "s/REALTIME_SECRET_KEY_BASE=.*/REALTIME_SECRET_KEY_BASE=${REALTIME_SECRET_KEY_BASE}/" .env

# Update PGRST_DB_URI with new password
PGRST_DB_URI="postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/postgres"
if grep -q "PGRST_DB_URI=" .env; then
    sed -i "s|PGRST_DB_URI=.*|PGRST_DB_URI=\${PGRST_DB_URI}|" .env
else
    echo "PGRST_DB_URI=\${PGRST_DB_URI}" >> .env
fi

echo "✅ Droplet .env updated"
EOF

# Step 4: Update local .env file with same keys
echo "📝 Updating local .env file with matching keys..."
cp ${LOCAL_ENV_FILE} ${LOCAL_ENV_FILE}.backup.secure.$(date +%Y%m%d_%H%M%S)

# Update local .env with the same secure keys
sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PASSWORD}/" ${LOCAL_ENV_FILE}
sed -i.bak "s/VAULT_ENC_KEY=.*/VAULT_ENC_KEY=${VAULT_ENC_KEY}/" ${LOCAL_ENV_FILE}
sed -i.bak "s/SECRET_KEY_BASE=.*/SECRET_KEY_BASE=${SECRET_KEY_BASE}/" ${LOCAL_ENV_FILE}
sed -i.bak "s/REALTIME_SECRET_KEY_BASE=.*/REALTIME_SECRET_KEY_BASE=${REALTIME_SECRET_KEY_BASE}/" ${LOCAL_ENV_FILE}

# Clean up backup files created by sed
rm -f ${LOCAL_ENV_FILE}.bak

echo "✅ Local .env updated"

# Step 5: Restart containers on droplet
echo "🔄 Restarting containers on droplet..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "Starting PostgreSQL first..."
docker-compose up -d postgres

echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo "Starting Supabase services..."
docker-compose up -d

echo "Waiting for services to stabilize..."
sleep 15

echo "Checking service status..."
docker-compose ps

echo "Checking for any container errors..."
docker-compose logs --tail=20 supabase-pooler 2>/dev/null || echo "supabase-pooler logs not available"
EOF

# Step 6: Verification
echo "🔍 Verifying the update..."
echo "Local .env keys:"
grep -E "(POSTGRES_PASSWORD|VAULT_ENC_KEY)" ${LOCAL_ENV_FILE}

echo ""
echo "Droplet .env keys:"
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} "grep -E '(POSTGRES_PASSWORD|VAULT_ENC_KEY)' ${DROPLET_PATH}/.env"

echo ""
echo "✅ Secure environment update complete!"
echo "🔄 Both local and droplet environments now have matching secure credentials"
echo "📋 Next step: Test database connectivity and run the VividWalls database deployment script" 