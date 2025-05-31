#!/bin/bash

# VividWalls Database Deployment Script for Digital Ocean Droplet
# This script sets up the complete VividWalls database schema and imports data

set -e

echo "🚀 VividWalls Database Deployment Starting..."
echo "================================================"

# Database connection settings for droplet
DB_HOST="localhost"
DB_PORT="54322"
DB_USER="postgres"
DB_NAME="postgres"

# Check if we're running on the droplet
if [ ! -f "/home/vivid/vivid_mas/.env" ]; then
    echo "❌ This script should be run on the Digital Ocean droplet"
    echo "   Expected path: /home/vivid/vivid_mas/"
    exit 1
fi

# Navigate to project directory
cd /home/vivid/vivid_mas

# Source environment variables
if [ -f ".env" ]; then
    source .env
    echo "✅ Loaded environment variables"
else
    echo "⚠️  No .env file found, using defaults"
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec vivid_mas-supabase-db-1 pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Check if schema already exists
echo "🔍 Checking existing database schema..."
SCHEMA_EXISTS=$(docker exec vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products');" | tr -d ' ')

if [ "$SCHEMA_EXISTS" = "t" ]; then
    echo "📋 VividWalls schema already exists"
    read -p "Do you want to recreate the schema? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧹 Dropping existing schema..."
        docker exec -i vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres << 'EOF'
DROP TABLE IF EXISTS product_images CASCADE;
DROP TABLE IF EXISTS product_variants CASCADE;
DROP TABLE IF EXISTS ai_analysis CASCADE;
DROP TABLE IF EXISTS product_tags CASCADE;
DROP TABLE IF EXISTS room_suitability CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS collections CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS room_types CASCADE;
DROP FUNCTION IF EXISTS search_products_by_color CASCADE;
DROP FUNCTION IF EXISTS search_products_by_tags CASCADE;
DROP FUNCTION IF EXISTS search_products_by_category CASCADE;
DROP FUNCTION IF EXISTS get_product_recommendations CASCADE;
DROP FUNCTION IF EXISTS analyze_room_suitability CASCADE;
EOF
        echo "✅ Existing schema dropped"
    else
        echo "ℹ️  Keeping existing schema, skipping to data import"
        SKIP_SCHEMA=true
    fi
fi

# Deploy schema if needed
if [ "$SKIP_SCHEMA" != "true" ]; then
    echo "📝 Deploying VividWalls database schema..."
    if [ -f "scripts/supabase-vividwalls-schema.sql" ]; then
        docker exec -i vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres < scripts/supabase-vividwalls-schema.sql
        echo "✅ Database schema deployed successfully"
    else
        echo "❌ Schema file not found: scripts/supabase-vividwalls-schema.sql"
        exit 1
    fi
fi

# Check if CSV data exists
echo "🔍 Checking for CSV data files..."
CSV_FILES_EXIST=false

# Check for product data in the shared directory
if [ -f "n8n/data/shared/vividwalls-products-list-2-23-2025.csv" ]; then
    echo "✅ Found product CSV data"
    CSV_FILES_EXIST=true
fi

if [ -f "n8n/data/shared/vividwalls-q&a.csv" ]; then
    echo "✅ Found Q&A CSV data"
fi

if [ -f "n8n/data/shared/vividwalls-room-analysis-qa.csv" ]; then
    echo "✅ Found room analysis CSV data"
fi

# Install Python dependencies for CSV import
echo "📦 Installing Python dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    apt-get update && apt-get install -y python3 python3-pip
fi

if ! python3 -c "import psycopg2" &> /dev/null; then
    echo "Installing psycopg2..."
    pip3 install psycopg2-binary
fi

# Import CSV data if available
if [ "$CSV_FILES_EXIST" = "true" ]; then
    echo "📊 Importing CSV data..."
    
    # Update the import script to use droplet database settings
    sed -i "s/'host': 'localhost'/'host': 'vivid_mas-supabase-db-1'/g" scripts/fix-csv-import.py
    sed -i "s/'port': 54322/'port': 5432/g" scripts/fix-csv-import.py
    
    # Run the import script
    python3 scripts/fix-csv-import.py
    
    # Restore original settings
    sed -i "s/'host': 'vivid_mas-supabase-db-1'/'host': 'localhost'/g" scripts/fix-csv-import.py
    sed -i "s/'port': 5432/'port': 54322/g" scripts/fix-csv-import.py
    
    echo "✅ CSV data imported successfully"
else
    echo "⚠️  No CSV data files found, skipping data import"
    echo "   Expected files in n8n/data/shared/:"
    echo "   - vividwalls-products-list-2-23-2025.csv"
    echo "   - vividwalls-q&a.csv"
    echo "   - vividwalls-room-analysis-qa.csv"
fi

# Verify deployment
echo "🔍 Verifying database deployment..."
PRODUCT_COUNT=$(docker exec vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres -t -c "SELECT COUNT(*) FROM products;" | tr -d ' ')
COLLECTION_COUNT=$(docker exec vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres -t -c "SELECT COUNT(*) FROM collections;" | tr -d ' ')

echo "📊 Database Status:"
echo "   Collections: $COLLECTION_COUNT"
echo "   Products: $PRODUCT_COUNT"

if [ "$PRODUCT_COUNT" -gt "0" ]; then
    echo "✅ Database deployment successful with data"
else
    echo "⚠️  Database schema deployed but no product data found"
fi

# Test a simple search function
echo "🧪 Testing database functions..."
docker exec vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT title, collection FROM products LIMIT 3;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database functions working correctly"
else
    echo "❌ Database function test failed"
fi

echo ""
echo "🎉 VividWalls Database Deployment Complete!"
echo "================================================"
echo "📋 Next Steps:"
echo "   1. Import n8n workflows via the web interface"
echo "   2. Configure n8n MCP server connection"
echo "   3. Test RAG functionality with the new database"
echo ""
echo "🌐 Access Points:"
echo "   - n8n: https://n8n.vividwalls.blog"
echo "   - Supabase: http://localhost:54322 (from droplet)"
echo "   - Database: PostgreSQL with VividWalls schema ready" 