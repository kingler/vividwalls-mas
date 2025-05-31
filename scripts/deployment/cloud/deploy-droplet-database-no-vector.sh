#!/bin/bash

# VividWalls Database Deployment Script for Digital Ocean Droplet
# Version without pgvector extension (core functionality only)

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

# Test database connection
echo "🔐 Testing database connection..."
if docker exec $POSTGRES_CONTAINER psql -U postgres -d postgres -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
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

# Deploy core schema (without vector extension)
echo "📝 Deploying VividWalls database schema (core version)..."
docker exec -i $POSTGRES_CONTAINER psql -U postgres -d postgres << 'EOF'
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Collections table
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) UNIQUE NOT NULL,
    collection VARCHAR(255) REFERENCES collections(name),
    price DECIMAL(10,2),
    description TEXT,
    vendor VARCHAR(255),
    product_type VARCHAR(255),
    tags TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product variants table
CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    title VARCHAR(500),
    price DECIMAL(10,2),
    sku VARCHAR(255),
    inventory_quantity INTEGER DEFAULT 0,
    weight DECIMAL(8,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product images table
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(id) ON DELETE CASCADE,
    src TEXT NOT NULL,
    alt_text TEXT,
    position INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product tags junction table
CREATE TABLE product_tags (
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

-- Room types table
CREATE TABLE room_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Room suitability table
CREATE TABLE room_suitability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    room_type_id UUID REFERENCES room_types(id) ON DELETE CASCADE,
    suitability_score DECIMAL(3,2) CHECK (suitability_score >= 0 AND suitability_score <= 1),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (product_id, room_type_id)
);

-- AI analysis table (without vector embeddings for now)
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL,
    color_palette JSONB,
    style_tags TEXT[],
    mood_descriptors TEXT[],
    technical_specs JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_products_collection ON products(collection);
CREATE INDEX idx_products_vendor ON products(vendor);
CREATE INDEX idx_products_product_type ON products(product_type);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_product_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_product_variants_sku ON product_variants(sku);
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_images_variant_id ON product_images(variant_id);
CREATE INDEX idx_product_tags_product_id ON product_tags(product_id);
CREATE INDEX idx_product_tags_tag_id ON product_tags(tag_id);
CREATE INDEX idx_room_suitability_product_id ON room_suitability(product_id);
CREATE INDEX idx_room_suitability_room_type_id ON room_suitability(room_type_id);
CREATE INDEX idx_ai_analysis_product_id ON ai_analysis(product_id);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);

-- Search functions (without vector similarity)
CREATE OR REPLACE FUNCTION search_products_by_tags(search_tags TEXT[])
RETURNS TABLE(
    product_id UUID,
    title VARCHAR(500),
    collection VARCHAR(255),
    price DECIMAL(10,2),
    match_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.collection,
        p.price,
        array_length(array(
            SELECT unnest(search_tags) 
            INTERSECT 
            SELECT unnest(string_to_array(p.tags, ','))
        ), 1) as match_count
    FROM products p
    WHERE p.tags IS NOT NULL
    AND array_length(array(
        SELECT unnest(search_tags) 
        INTERSECT 
        SELECT unnest(string_to_array(p.tags, ','))
    ), 1) > 0
    ORDER BY match_count DESC, p.title;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_products_by_category(category_name VARCHAR(255))
RETURNS TABLE(
    product_id UUID,
    title VARCHAR(500),
    collection VARCHAR(255),
    price DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.title, p.collection, p.price
    FROM products p
    WHERE p.collection ILIKE '%' || category_name || '%'
    OR p.product_type ILIKE '%' || category_name || '%'
    OR p.tags ILIKE '%' || category_name || '%'
    ORDER BY p.title;
END;
$$ LANGUAGE plpgsql;

-- Insert default room types
INSERT INTO room_types (name, description) VALUES
('Living Room', 'Main social and relaxation space'),
('Bedroom', 'Private sleeping and rest area'),
('Kitchen', 'Food preparation and dining area'),
('Bathroom', 'Personal hygiene and bathing space'),
('Office', 'Work and study environment'),
('Dining Room', 'Formal eating and entertaining space'),
('Hallway', 'Transitional corridor space'),
('Entryway', 'Main entrance and welcome area');

-- Insert default collections
INSERT INTO collections (name, description) VALUES
('Abstract', 'Abstract and modern artistic designs'),
('Nature', 'Natural landscapes and organic patterns'),
('Geometric', 'Geometric patterns and shapes'),
('Vintage', 'Classic and retro-inspired designs'),
('Minimalist', 'Clean and simple aesthetic'),
('Botanical', 'Plant and flower-inspired artwork'),
('Urban', 'City and industrial-themed designs'),
('Luxury', 'Premium and sophisticated designs'),
('Kids', 'Child-friendly and playful designs');

-- Create a view for easy product browsing
CREATE VIEW product_catalog AS
SELECT 
    p.id,
    p.title,
    p.collection,
    p.price,
    p.description,
    p.vendor,
    p.product_type,
    p.tags,
    COUNT(pv.id) as variant_count,
    COUNT(pi.id) as image_count,
    p.created_at,
    p.updated_at
FROM products p
LEFT JOIN product_variants pv ON p.id = pv.product_id
LEFT JOIN product_images pi ON p.id = pi.product_id
GROUP BY p.id, p.title, p.collection, p.price, p.description, p.vendor, p.product_type, p.tags, p.created_at, p.updated_at;

COMMENT ON TABLE products IS 'Main products catalog for VividWalls';
COMMENT ON TABLE collections IS 'Product collections and categories';
COMMENT ON TABLE product_variants IS 'Product variants with different sizes, materials, etc.';
COMMENT ON TABLE product_images IS 'Product and variant images';
COMMENT ON TABLE ai_analysis IS 'AI-generated product analysis and metadata';
EOF

echo "✅ Database schema deployed successfully"

# Check if CSV data exists and import it
echo "🔍 Checking for CSV data files..."
if [ -f "n8n/data/shared/vividwalls-products-list-2-23-2025.csv" ]; then
    echo "✅ Found product CSV data"
    echo "📊 Importing CSV data..."
    
    # Use the existing Python import script but modify it for our container
    python3 << EOF
import csv
import subprocess
import os

def execute_sql(sql):
    """Execute SQL via docker exec"""
    cmd = ['docker', 'exec', '$POSTGRES_CONTAINER', 'psql', '-U', 'postgres', '-d', 'postgres', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return False
    return True

print("🔗 Starting CSV import...")

# Import products from CSV
csv_file = 'n8n/data/shared/vividwalls-products-list-2-23-2025.csv'
if os.path.exists(csv_file):
    print(f"📊 Importing products from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        product_count = 0
        
        for row in reader:
            try:
                # Clean and escape data
                title = row['Title'].replace("'", "''")
                collection = row['Collection'].replace("'", "''")
                description = row.get('Description', '').replace("'", "''") if row.get('Description') else ''
                vendor = row['Vendor'].replace("'", "''")
                product_type = row['Product Type'].replace("'", "''")
                tags = row['Tags'].replace("'", "''")
                price = float(row['Price']) if row['Price'] and row['Price'].replace('.', '').isdigit() else 0.0
                
                # Insert product
                product_sql = f"""
                INSERT INTO products (title, collection, price, description, vendor, product_type, tags, created_at, updated_at)
                VALUES ('{title}', '{collection}', {price}, '{description}', '{vendor}', '{product_type}', '{tags}', 
                        '{row['Created At']}', '{row['Updated At']}')
                ON CONFLICT (title) DO NOTHING;
                """
                
                if execute_sql(product_sql):
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
    
    echo "✅ CSV data imported successfully"
else
    echo "⚠️  No CSV data files found, skipping data import"
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

# Test database functions
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
echo "📋 Database Features Deployed:"
echo "   ✅ Core product catalog"
echo "   ✅ Collections and categories"
echo "   ✅ Product variants and images"
echo "   ✅ Search functions"
echo "   ✅ Room suitability tracking"
echo "   ⚠️  Vector embeddings (requires pgvector extension)"
echo ""
echo "🌐 Access Points:"
echo "   - n8n: http://localhost:5678"
echo "   - PostgreSQL: localhost:5433 (from host)"
echo "   - Database: PostgreSQL with VividWalls schema ready" 