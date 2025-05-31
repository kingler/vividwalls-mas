#!/bin/bash

# Fix Authenticator Password Script
set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo "🔧 Fixing authenticator user password..."

ssh -i $SSH_KEY root@$DROPLET_IP << 'EOF'
cd /home/vivid/vivid_mas

echo "Setting password for authenticator user..."
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER authenticator WITH PASSWORD 'your-super-secret-supabase-db-password';"

echo "Setting password for anon user..."
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER anon WITH PASSWORD 'your-super-secret-supabase-db-password';"

echo "Setting password for service_role user..."
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER service_role WITH PASSWORD 'your-super-secret-supabase-db-password';"

echo "Restarting auth and rest services..."
docker restart supabase-auth supabase-rest

sleep 20

echo "Checking service status..."
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E '(auth|rest)'
EOF

echo "✅ Password fix completed!" 