#!/bin/bash

# Setup Supabase Database Users Script
# This script creates the required database users for Supabase services

set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"
DB_PASSWORD="your-super-secret-supabase-db-password"

echo "🔧 Setting up Supabase Database Users..."

# Connect to server and setup database users
ssh -i $SSH_KEY root@$DROPLET_IP << EOF
cd /home/vivid/vivid_mas

echo "📋 Creating required Supabase database users..."

# Create the required users in PostgreSQL
docker exec -i supabase-db psql -U postgres -d postgres << 'PSQL'
-- Create supabase_auth_admin user
CREATE USER supabase_auth_admin WITH PASSWORD '$DB_PASSWORD';
ALTER USER supabase_auth_admin CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE postgres TO supabase_auth_admin;

-- Create supabase_admin user  
CREATE USER supabase_admin WITH PASSWORD '$DB_PASSWORD';
ALTER USER supabase_admin CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE postgres TO supabase_admin;

-- Create authenticator user
CREATE USER authenticator WITH PASSWORD '$DB_PASSWORD';

-- Create anon user
CREATE USER anon;

-- Create service_role user
CREATE USER service_role;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, service_role, authenticator;
GRANT ALL ON ALL TABLES IN SCHEMA public TO supabase_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO supabase_admin;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO supabase_admin;

-- List all users to verify
\du
PSQL

echo "✅ Database users created successfully!"

echo ""
echo "🔄 Restarting Supabase Auth and REST services..."
docker restart supabase-auth supabase-rest

echo ""
echo "⏳ Waiting for services to restart..."
sleep 30

echo ""
echo "📊 Final status check:"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(kong|auth|rest|studio|meta)'

EOF

echo ""
echo "✅ Supabase database users setup completed!" 