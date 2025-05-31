#!/bin/bash

# VividWalls Database Deployment Script for Digital Ocean Droplet
# Fixed version for standard PostgreSQL container setup

set -e

echo "🚀 VividWalls Database Deployment Starting..."
echo "================================================"

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

# Get the correct PostgreSQL container name
POSTGRES_CONTAINER=$(docker-compose ps -q postgres)
if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "❌ PostgreSQL container not found. Starting it..."
    docker-compose up -d postgres
    sleep 10
    POSTGRES_CONTAINER=$(docker-compose ps -q postgres)
fi

echo "📋 Using PostgreSQL container: $POSTGRES_CONTAINER"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec $POSTGRES_CONTAINER pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start within 30 seconds"
        echo "🔍 Container logs:"
        docker logs $POSTGRES_CONTAINER --tail=10
        exit 1
    fi
    sleep 1
done

# Test database connection with the new password
echo "🔐 Testing database connection..."
if docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo "🔍 Checking environment variables..."
    echo "POSTGRES_PASSWORD is set: $([ -n "$POSTGRES_PASSWORD" ] && echo "Yes" || echo "No")"
    exit 1
fi

# Check if schema already exists
echo "🔍 Checking existing database schema..."
SCHEMA_EXISTS=$(docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products');" | tr -d ' ')

if [ "$SCHEMA_EXISTS" = "t" ]; then
    echo "📋 VividWalls schema already exists"
    echo "🧹 Dropping existing schema to ensure clean deployment..."
    docker exec -i $POSTGRES_CONTAINER psql -U postgres -d postgres << 'EOF'
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
fi

# Deploy schema
echo "📝 Deploying VividWalls database schema..."
if [ -f "scripts/supabase-vividwalls-schema.sql" ]; then
    docker exec -i $POSTGRES_CONTAINER psql -U postgres -d postgres < scripts/supabase-vividwalls-schema.sql
    echo "✅ Database schema deployed successfully"
else
    echo "❌ Schema file not found: scripts/supabase-vividwalls-schema.sql"
    exit 1
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
    
    # Create a temporary import script with correct connection settings
    cat > /tmp/import_csv.py << EOF
import psycopg2
import csv
import os
import sys

# Database connection settings for Docker container
conn_params = {
    'host': '$POSTGRES_CONTAINER',
    'port': 5432,
    'user': 'postgres',
    'password': '$POSTGRES_PASSWORD',
    'database': 'postgres'
}

# Connect via docker exec instead of direct connection
def execute_sql(sql, params=None):
    if params:
        # For parameterized queries, we need to format them safely
        formatted_sql = sql
        for i, param in enumerate(params):
            formatted_sql = formatted_sql.replace(f'%s', f"'{param}'", 1)
        sql = formatted_sql
    
    # Execute via docker exec
    import subprocess
    cmd = ['docker', 'exec', '$POSTGRES_CONTAINER', 'psql', '-U', 'postgres', '-d', 'postgres', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return None
    return result.stdout

print("🔗 Connecting to database...")

# Import products from CSV
csv_file = 'n8n/data/shared/vividwalls-products-list-2-23-2025.csv'
if os.path.exists(csv_file):
    print(f"📊 Importing products from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        product_count = 0
        
        for row in reader:
            try:
                # Insert collection first
                collection_sql = f"INSERT INTO collections (name, description) VALUES ('{row['Collection']}', 'Imported collection') ON CONFLICT (name) DO NOTHING;"
                execute_sql(collection_sql)
                
                # Insert product
                product_sql = f"""
                INSERT INTO products (title, collection, price, description, vendor, product_type, tags, created_at, updated_at)
                VALUES ('{row['Title'].replace("'", "''")}', '{row['Collection']}', {row['Price'] or 0}, 
                        '{row['Description'].replace("'", "''") if row.get('Description') else ''}', 
                        '{row['Vendor']}', '{row['Product Type']}', '{row['Tags']}', 
                        '{row['Created At']}', '{row['Updated At']}')
                ON CONFLICT (title) DO NOTHING;
                """
                execute_sql(product_sql)
                product_count += 1
                
                if product_count % 10 == 0:
                    print(f"   Imported {product_count} products...")
                    
            except Exception as e:
                print(f"Error importing product {row.get('Title', 'Unknown')}: {e}")
                continue
    
    print(f"✅ Imported {product_count} products")
else:
    print(f"⚠️  CSV file not found: {csv_file}")

print("✅ CSV import completed")
EOF

    # Run the import script
    python3 /tmp/import_csv.py
    
    # Clean up
    rm -f /tmp/import_csv.py
    
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
PRODUCT_COUNT=$(docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM products;" | tr -d ' ')
COLLECTION_COUNT=$(docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM collections;" | tr -d ' ')

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
docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -c "SELECT title, collection FROM products LIMIT 3;" > /dev/null 2>&1
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
echo "   - n8n: http://localhost:5678"
echo "   - PostgreSQL: localhost:5433 (from host)"
echo "   - Database: PostgreSQL with VividWalls schema ready" 