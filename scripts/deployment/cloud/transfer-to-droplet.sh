#!/bin/bash

# VividWalls Database File Transfer Script
# Transfers all necessary files to Digital Ocean droplet

set -e

echo "🚀 VividWalls Database File Transfer"
echo "===================================="

# Check if droplet IP is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <droplet-ip-or-hostname>"
    echo "   Example: $0 your-droplet-ip"
    echo "   Example: $0 vividwalls.blog"
    exit 1
fi

DROPLET_HOST="$1"
DROPLET_USER="root"
PROJECT_DIR="/home/vivid/vivid_mas"

echo "📡 Target: $DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR"

# Test SSH connection
echo "🔍 Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 "$DROPLET_USER@$DROPLET_HOST" "echo 'SSH connection successful'"; then
    echo "❌ SSH connection failed. Please check:"
    echo "   - Droplet IP/hostname is correct"
    echo "   - SSH key is configured"
    echo "   - Droplet is running"
    exit 1
fi

echo "✅ SSH connection successful"

# Create directories on droplet
echo "📁 Creating directories on droplet..."
ssh "$DROPLET_USER@$DROPLET_HOST" "
    mkdir -p $PROJECT_DIR/scripts
    mkdir -p $PROJECT_DIR/n8n/workflows
    mkdir -p $PROJECT_DIR/n8n/data/shared
"

# Transfer database schema and scripts
echo "📝 Transferring database files..."
scp scripts/supabase-vividwalls-schema.sql "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/scripts/"
scp scripts/migrate-vividwalls-data.sql "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/scripts/"
scp scripts/fix-csv-import.py "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/scripts/"
scp scripts/deploy-droplet-database.sh "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/scripts/"

# Transfer n8n workflows
echo "🔄 Transferring n8n workflows..."
scp n8n/workflows/VividWalls-Database-Integration-Workflow.json "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/n8n/workflows/"
scp n8n/workflows/VividWalls-Prompt-Chain-Image-Retrieval.json "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/n8n/workflows/"

# Transfer CSV data if it exists locally
echo "📊 Transferring CSV data..."
if [ -f "n8n/data/shared/vividwalls-products-list-2-23-2025.csv" ]; then
    scp "n8n/data/shared/vividwalls-products-list-2-23-2025.csv" "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/n8n/data/shared/"
    echo "✅ Product CSV transferred"
else
    echo "⚠️  Product CSV not found locally - you'll need to upload it manually"
fi

if [ -f "n8n/data/shared/vividwalls-q&a.csv" ]; then
    scp "n8n/data/shared/vividwalls-q&a.csv" "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/n8n/data/shared/"
    echo "✅ Q&A CSV transferred"
else
    echo "⚠️  Q&A CSV not found locally"
fi

if [ -f "n8n/data/shared/vividwalls-room-analysis-qa.csv" ]; then
    scp "n8n/data/shared/vividwalls-room-analysis-qa.csv" "$DROPLET_USER@$DROPLET_HOST:$PROJECT_DIR/n8n/data/shared/"
    echo "✅ Room analysis CSV transferred"
else
    echo "⚠️  Room analysis CSV not found locally"
fi

# Set proper permissions
echo "🔐 Setting file permissions..."
ssh "$DROPLET_USER@$DROPLET_HOST" "
    chmod +x $PROJECT_DIR/scripts/deploy-droplet-database.sh
    chmod +x $PROJECT_DIR/scripts/fix-csv-import.py
    chown -R vivid:vivid $PROJECT_DIR/scripts
    chown -R vivid:vivid $PROJECT_DIR/n8n
"

echo ""
echo "🎉 File transfer completed successfully!"
echo "===================================="
echo "📋 Next steps:"
echo "   1. SSH into your droplet: ssh $DROPLET_USER@$DROPLET_HOST"
echo "   2. Switch to vivid user: su - vivid"
echo "   3. Navigate to project: cd $PROJECT_DIR"
echo "   4. Run deployment: ./scripts/deploy-droplet-database.sh"
echo ""
echo "🌐 Files transferred:"
echo "   ✅ Database schema and migration scripts"
echo "   ✅ CSV import script"
echo "   ✅ Deployment automation script"
echo "   ✅ n8n workflow files"
echo "   📊 CSV data files (if available locally)"
echo ""
echo "🔗 Access points after deployment:"
echo "   - n8n: https://n8n.vividwalls.blog"
echo "   - Database: PostgreSQL with VividWalls schema" 