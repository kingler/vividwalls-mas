#!/bin/bash

# Fix Supabase Issues Script
# This script disables problematic services and restarts core Supabase services
# WARNING: This script will remove the existing Supabase database volume,
# leading to data loss in the database. Ensure you have backups if needed.

set -e

DROPLET_IP="157.230.13.13"
SSH_KEY="~/.ssh/digitalocean"

echo "🔑 Ensuring local 'supabase-env-fix.env' file exists..."
if [ ! -f "supabase-env-fix.env" ]; then
    echo "❌ Error: 'supabase-env-fix.env' not found in the current local directory."
    echo "Please create it with the correct Supabase environment variables, especially POSTGRES_PASSWORD."
    exit 1
fi

echo "📤 Uploading Supabase environment configuration (supabase-env-fix.env)..."
scp -i $SSH_KEY supabase-env-fix.env root@$DROPLET_IP:/home/vivid/vivid_mas/supabase-env-fix.env

echo "🔧 Fixing Supabase Configuration on server $DROPLET_IP..."

# Connect to server and fix Supabase
ssh -i $SSH_KEY root@$DROPLET_IP << 'EOF'
set -e
cd /home/vivid/vivid_mas

echo "📋 Current Supabase container status:"
docker ps -a | grep supabase

echo ""
echo "🛑 Stopping all Supabase containers using supabase-env-fix.env..."
docker compose -f supabase/docker/docker-compose.yml --env-file supabase-env-fix.env down

echo ""
echo "🗑️ Removing problematic Supabase service containers..."
# Stop and remove any containers that might be lingering from a previous version of the compose file or bad state
SUPABASE_CONTAINERS=$(docker ps -a --filter "name=supabase" --format="{{.ID}}")
if [ -n "$SUPABASE_CONTAINERS" ]; then
    docker rm -f $SUPABASE_CONTAINERS 2>/dev/null || true
else
    echo "No Supabase containers found to remove."
fi

echo ""
echo "🗑️ Removing Supabase database volume to reset password and re-initialize database..."
# Assuming default project name 'docker' based on -f supabase/docker/docker-compose.yml
# and service name 'db' and volume name 'db_data' (common Supabase setup)
# Default volume name becomes <project>_<volume_name_in_compose_file>
# For supabase/docker/docker-compose.yml, project name is 'docker'
# If db service volume in YML is 'db_data', full name is 'docker_db_data'
DB_VOLUME_NAME_PATTERN="docker_db_data" # Common pattern
DB_VOLUME_NAME=$(docker volume ls -q --filter name=${DB_VOLUME_NAME_PATTERN})

if [ -n "$DB_VOLUME_NAME" ]; then
  echo "Found database volume: $DB_VOLUME_NAME. Removing..."
  docker volume rm -f $DB_VOLUME_NAME
else
  # Fallback: Try to find volume by common labels if compose v2+ is used
  DB_VOLUME_BY_LABEL=$(docker volume ls -q --filter "label=com.docker.compose.project=docker" --filter "label=com.docker.compose.service=db")
  if [ -n "$DB_VOLUME_BY_LABEL" ]; then
    echo "Found database volume by label: $DB_VOLUME_BY_LABEL. Removing..."
    docker volume rm -f $DB_VOLUME_BY_LABEL
  else
    echo "⚠️ Could not automatically find the database volume '${DB_VOLUME_NAME_PATTERN}' or by standard labels."
    echo "Common volume names might also include 'supabase_postgres_data'."
    echo "If password issues persist, please manually identify and remove the Postgres volume and re-run."
    echo "You can inspect 'supabase/docker/docker-compose.yml' for the 'db' service's volume definition."
  fi
fi


echo ""
echo "🔄 Starting core Supabase services (db, vector, imgproxy) using supabase-env-fix.env..."
# Start database and vector first
docker compose -f supabase/docker/docker-compose.yml --env-file supabase-env-fix.env up -d db vector imgproxy

echo "⏳ Waiting for database to initialize (60 seconds)..."
sleep 60

echo ""
echo "🔄 Starting other core API services (auth, rest, kong, studio, meta) using supabase-env-fix.env..."
# Start core API services
docker compose -f supabase/docker/docker-compose.yml --env-file supabase-env-fix.env up -d auth rest kong studio meta

echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "📊 Final status check:"
docker ps --format 'table {{.Names}}	{{.Status}}	{{.Ports}}' | grep supabase

echo ""
echo "🌐 Testing Supabase Studio access..."
# Wait a bit more for studio to be fully up
sleep 10
curl -f -s --max-time 15 "https://supabase.vividwalls.blog" > /dev/null && echo "✅ Supabase Studio responding" || echo "❌ Supabase Studio not responding (this might take a few minutes after a fresh start)"

EOF

echo ""
echo "✅ Supabase fix script completed!"
echo "⚠️ REMEMBER: The Supabase database was re-initialized. All previous data in it is GONE."
echo "If 'supabase-env-fix.env' did not have the correct POSTGRES_PASSWORD, issues might persist." 