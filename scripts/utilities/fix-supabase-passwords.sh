#!/bin/bash

# Fix All Supabase User Passwords Script
set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo "🔧 Fixing all Supabase user passwords..."

ssh -i $SSH_KEY root@$DROPLET_IP << 'EOF'
cd /home/vivid/vivid_mas

echo "📋 Setting passwords for all Supabase users..."

# Set password for supabase_admin (the one causing the error)
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER supabase_admin WITH PASSWORD 'your-super-secret-supabase-db-password';"

# Set password for supabase_auth_admin
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER supabase_auth_admin WITH PASSWORD 'your-super-secret-supabase-db-password';"

# Set password for authenticator
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER authenticator WITH PASSWORD 'your-super-secret-supabase-db-password';"

# Set password for anon user
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER anon WITH PASSWORD 'your-super-secret-supabase-db-password';"

# Set password for service_role user
docker exec supabase-db psql -U postgres -d postgres -c "ALTER USER service_role WITH PASSWORD 'your-super-secret-supabase-db-password';"

echo "✅ All user passwords updated!"

echo ""
echo "🔄 Restarting all Supabase services..."
docker restart supabase-studio supabase-auth supabase-rest supabase-kong supabase-meta

echo ""
echo "⏳ Waiting for services to restart..."
sleep 30

echo ""
echo "📊 Final service status:"
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep supabase

echo ""
echo "🌐 Testing Supabase Studio access..."
curl -f -s --max-time 10 "https://supabase.vividwalls.blog" > /dev/null && echo "✅ Supabase Studio responding" || echo "❌ Supabase Studio not responding"

EOF

echo ""
echo "✅ Supabase password fix completed!" 