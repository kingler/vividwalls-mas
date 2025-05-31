#!/bin/bash

# Fixed script to safely update .env files with secure keys
# This version properly handles special characters and escaping

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
DROPLET_PATH="/home/vivid/vivid_mas"
LOCAL_ENV_FILE=".env"

echo "🔒 Starting secure environment update process..."

# Step 1: Generate secure keys locally first (avoiding problematic characters)
echo "🔐 Generating secure keys..."
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/\n" | cut -c1-25)
VAULT_ENC_KEY=$(openssl rand -hex 16)  # Exactly 32 characters for AES-256-GCM
SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/\n" | cut -c1-64)
REALTIME_SECRET_KEY_BASE=$(openssl rand -base64 64 | tr -d "=+/\n" | cut -c1-64)

echo "Generated keys:"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
echo "VAULT_ENC_KEY: ${VAULT_ENC_KEY} (${#VAULT_ENC_KEY} characters)"
echo "SECRET_KEY_BASE: ${SECRET_KEY_BASE}"
echo "REALTIME_SECRET_KEY_BASE: ${REALTIME_SECRET_KEY_BASE}"

# Step 2: Shutdown containers on droplet
echo "🛑 Shutting down affected containers on droplet..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "Stopping all services to ensure clean restart..."
docker-compose down

echo "✅ All containers stopped"
EOF

# Step 3: Create a temporary env update script and transfer it
echo "📝 Creating secure update script..."
cat > /tmp/update_env.sh << EOF
#!/bin/bash
cd /home/vivid/vivid_mas

# Create backup
cp .env .env.backup.secure.\$(date +%Y%m%d_%H%M%S)

# Use Python to safely update the .env file
python3 << 'PYTHON_EOF'
import re
import os

env_file = '.env'
with open(env_file, 'r') as f:
    content = f.read()

# Update each key safely
content = re.sub(r'POSTGRES_PASSWORD=.*', 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}', content)
content = re.sub(r'VAULT_ENC_KEY=.*', 'VAULT_ENC_KEY=${VAULT_ENC_KEY}', content)
content = re.sub(r'SECRET_KEY_BASE=.*', 'SECRET_KEY_BASE=${SECRET_KEY_BASE}', content)
content = re.sub(r'REALTIME_SECRET_KEY_BASE=.*', 'REALTIME_SECRET_KEY_BASE=${REALTIME_SECRET_KEY_BASE}', content)

# Update PGRST_DB_URI if it exists
pgrst_uri = 'postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/postgres'
if 'PGRST_DB_URI=' in content:
    content = re.sub(r'PGRST_DB_URI=.*', f'PGRST_DB_URI={pgrst_uri}', content)
else:
    content += f'\nPGRST_DB_URI={pgrst_uri}\n'

with open(env_file, 'w') as f:
    f.write(content)

print("✅ .env file updated successfully")
PYTHON_EOF

echo "✅ Droplet .env updated"
EOF

# Step 4: Transfer and execute the update script on droplet
echo "📤 Transferring update script to droplet..."
scp -i ~/.ssh/digitalocean /tmp/update_env.sh ${DROPLET_USER}@${DROPLET_IP}:/tmp/

echo "🔄 Executing update on droplet..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} "chmod +x /tmp/update_env.sh && /tmp/update_env.sh"

# Step 5: Update local .env file with same keys using Python
echo "📝 Updating local .env file with matching keys..."
cp ${LOCAL_ENV_FILE} ${LOCAL_ENV_FILE}.backup.secure.$(date +%Y%m%d_%H%M%S)

python3 << PYTHON_EOF
import re

env_file = '${LOCAL_ENV_FILE}'
with open(env_file, 'r') as f:
    content = f.read()

# Update each key safely
content = re.sub(r'POSTGRES_PASSWORD=.*', 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}', content)
content = re.sub(r'VAULT_ENC_KEY=.*', 'VAULT_ENC_KEY=${VAULT_ENC_KEY}', content)
content = re.sub(r'SECRET_KEY_BASE=.*', 'SECRET_KEY_BASE=${SECRET_KEY_BASE}', content)
content = re.sub(r'REALTIME_SECRET_KEY_BASE=.*', 'REALTIME_SECRET_KEY_BASE=${REALTIME_SECRET_KEY_BASE}', content)

with open(env_file, 'w') as f:
    f.write(content)

print("✅ Local .env file updated successfully")
PYTHON_EOF

# Step 6: Restart containers on droplet
echo "🔄 Restarting containers on droplet..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "Starting all services..."
docker-compose up -d

echo "Waiting for services to stabilize..."
sleep 20

echo "Checking service status..."
docker-compose ps

echo "Checking PostgreSQL connectivity..."
docker-compose exec -T postgres pg_isready -U postgres || echo "PostgreSQL not ready yet"

echo "Checking for supabase-pooler errors..."
docker-compose logs --tail=10 supabase-pooler 2>/dev/null || echo "supabase-pooler not found in this compose"
EOF

# Step 7: Verification
echo "🔍 Verifying the update..."
echo "Local .env keys:"
grep -E "(POSTGRES_PASSWORD|VAULT_ENC_KEY)" ${LOCAL_ENV_FILE} || echo "Keys not found in local file"

echo ""
echo "Droplet .env keys:"
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} "grep -E '(POSTGRES_PASSWORD|VAULT_ENC_KEY)' ${DROPLET_PATH}/.env" || echo "Keys not found in droplet file"

# Cleanup
rm -f /tmp/update_env.sh

echo ""
echo "✅ Secure environment update complete!"
echo "🔄 Both local and droplet environments now have matching secure credentials"
echo "📋 Next step: Test database connectivity and run the VividWalls database deployment script" 