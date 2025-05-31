#!/bin/bash

# VividWalls Product Classification Setup Script
# This script sets up the environment and database for the product classification workflow

set -e

echo "🎨 VividWalls Product Classification Setup"
echo "=========================================="

# Check if we're in the correct directory
if [ ! -f "n8n/shared/products/vividwalls-products-list-2-23-2025.csv" ]; then
    echo "❌ Error: Product CSV file not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Product CSV file found"

# Check for required environment variables
echo "🔧 Checking environment variables..."

REQUIRED_VARS=(
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
    "OPENAI_API_KEY"
    "DO_SPACES_KEY"
    "DO_SPACES_SECRET"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set these variables in your .env file or environment."
    exit 1
fi

echo "✅ All required environment variables are set"

# Create Supabase database tables
echo "🗄️  Setting up Supabase database tables..."

# Create SQL file for database setup
cat > /tmp/vividwalls_schema.sql << 'EOF'
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  handle VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  vendor VARCHAR(255),
  category VARCHAR(255),
  type VARCHAR(255),
  collection VARCHAR(255),
  published BOOLEAN DEFAULT false,
  status VARCHAR(50),
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product variants table
CREATE TABLE IF NOT EXISTS product_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  sku VARCHAR(255) UNIQUE NOT NULL,
  frame_size VARCHAR(50),
  frame_color VARCHAR(50),
  frame_style VARCHAR(100),
  price DECIMAL(10,2),
  shopify_image_url TEXT,
  image_position INTEGER,
  image_alt TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product analysis table
CREATE TABLE IF NOT EXISTS product_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  color_analysis JSONB,
  style_classification JSONB,
  mood_analysis JSONB,
  geometric_analysis JSONB,
  technical_characteristics JSONB,
  space_suitability JSONB,
  search_tags TEXT[],
  ai_confidence_score DECIMAL(3,2),
  analyzed_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(product_id)
);

-- Product images table
CREATE TABLE IF NOT EXISTS product_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  image_type VARCHAR(50), -- 'optimized', 'thumbnail', 'analysis'
  storage_url TEXT NOT NULL,
  storage_key VARCHAR(500),
  cdn_url TEXT,
  file_size INTEGER,
  uploaded_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(product_id, image_type)
);

-- Product embeddings table
CREATE TABLE IF NOT EXISTS product_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  embedding VECTOR(1536),
  embedding_text TEXT,
  model_used VARCHAR(100),
  dimensions INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(product_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_handle ON products(handle);
CREATE INDEX IF NOT EXISTS idx_products_collection ON products(collection);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_product_variants_product_id ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_product_variants_sku ON product_variants(sku);
CREATE INDEX IF NOT EXISTS idx_product_analysis_product_id ON product_analysis(product_id);
CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_product_embeddings_product_id ON product_embeddings(product_id);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS idx_product_embeddings_vector 
ON product_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Create search functions
CREATE OR REPLACE FUNCTION search_products_by_vector(
  query_embedding VECTOR(1536),
  similarity_threshold FLOAT DEFAULT 0.7,
  max_results INT DEFAULT 10
)
RETURNS TABLE (
  product_id UUID,
  handle VARCHAR(255),
  title VARCHAR(500),
  collection VARCHAR(255),
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id,
    p.handle,
    p.title,
    p.collection,
    1 - (pe.embedding <=> query_embedding) AS similarity
  FROM products p
  JOIN product_embeddings pe ON p.id = pe.product_id
  WHERE 1 - (pe.embedding <=> query_embedding) > similarity_threshold
  ORDER BY pe.embedding <=> query_embedding
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create function to get products by color
CREATE OR REPLACE FUNCTION get_products_by_color(
  target_colors TEXT[],
  color_tolerance FLOAT DEFAULT 0.8,
  max_results INT DEFAULT 20
)
RETURNS TABLE (
  product_id UUID,
  handle VARCHAR(255),
  title VARCHAR(500),
  collection VARCHAR(255),
  color_match_score FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id,
    p.handle,
    p.title,
    p.collection,
    -- Simplified color matching score (in real implementation, use proper color distance)
    CASE 
      WHEN pa.color_analysis->>'primary_colors' IS NOT NULL THEN 0.8
      ELSE 0.5
    END AS color_match_score
  FROM products p
  JOIN product_analysis pa ON p.id = pa.product_id
  WHERE pa.color_analysis IS NOT NULL
  ORDER BY color_match_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create function to get products by mood
CREATE OR REPLACE FUNCTION get_products_by_mood(
  target_mood VARCHAR(100),
  max_results INT DEFAULT 20
)
RETURNS TABLE (
  product_id UUID,
  handle VARCHAR(255),
  title VARCHAR(500),
  collection VARCHAR(255),
  mood_match_score FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id,
    p.handle,
    p.title,
    p.collection,
    CASE 
      WHEN pa.mood_analysis->>'primary_mood' = target_mood THEN 1.0
      WHEN target_mood = ANY(string_to_array(pa.mood_analysis->>'secondary_moods', ',')) THEN 0.8
      ELSE 0.3
    END AS mood_match_score
  FROM products p
  JOIN product_analysis pa ON p.id = pa.product_id
  WHERE pa.mood_analysis IS NOT NULL
  ORDER BY mood_match_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
EOF

# Execute SQL using psql if available, otherwise provide instructions
if command -v psql &> /dev/null; then
    echo "📊 Executing database schema..."
    PGPASSWORD="$SUPABASE_SERVICE_KEY" psql -h "$(echo $SUPABASE_URL | sed 's|https://||' | sed 's|\.supabase\.co.*|.supabase.co|')" -U postgres -d postgres -f /tmp/vividwalls_schema.sql
    echo "✅ Database schema created successfully"
else
    echo "⚠️  psql not found. Please execute the following SQL in your Supabase SQL editor:"
    echo "   File: /tmp/vividwalls_schema.sql"
    cat /tmp/vividwalls_schema.sql
fi

# Create Digital Ocean Spaces bucket (if needed)
echo "☁️  Checking Digital Ocean Spaces configuration..."

# Test Digital Ocean Spaces connection
if command -v aws &> /dev/null; then
    echo "🔧 Testing Digital Ocean Spaces connection..."
    
    # Configure AWS CLI for Digital Ocean Spaces
    aws configure set aws_access_key_id "$DO_SPACES_KEY" --profile do-spaces
    aws configure set aws_secret_access_key "$DO_SPACES_SECRET" --profile do-spaces
    aws configure set default.region "${DO_SPACES_REGION:-nyc3}" --profile do-spaces
    
    # Test connection
    if aws s3 ls --endpoint-url "https://${DO_SPACES_REGION:-nyc3}.digitaloceanspaces.com" --profile do-spaces &> /dev/null; then
        echo "✅ Digital Ocean Spaces connection successful"
        
        # Create bucket if it doesn't exist
        BUCKET_NAME="${DO_SPACES_BUCKET:-vividwalls-products}"
        if ! aws s3 ls "s3://$BUCKET_NAME" --endpoint-url "https://${DO_SPACES_REGION:-nyc3}.digitaloceanspaces.com" --profile do-spaces &> /dev/null; then
            echo "📦 Creating Digital Ocean Spaces bucket: $BUCKET_NAME"
            aws s3 mb "s3://$BUCKET_NAME" --endpoint-url "https://${DO_SPACES_REGION:-nyc3}.digitaloceanspaces.com" --profile do-spaces
            echo "✅ Bucket created successfully"
        else
            echo "✅ Digital Ocean Spaces bucket already exists"
        fi
    else
        echo "❌ Failed to connect to Digital Ocean Spaces. Please check your credentials."
        exit 1
    fi
else
    echo "⚠️  AWS CLI not found. Please ensure Digital Ocean Spaces bucket exists: ${DO_SPACES_BUCKET:-vividwalls-products}"
fi

# Install required Node.js packages for n8n workflow
echo "📦 Checking required Node.js packages..."

REQUIRED_PACKAGES=(
    "sharp"
    "aws-sdk"
    "@supabase/supabase-js"
    "colorthief"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! npm list "$package" &> /dev/null; then
        echo "📦 Installing $package..."
        npm install "$package"
    else
        echo "✅ $package already installed"
    fi
done

# Create environment configuration file for n8n
echo "⚙️  Creating n8n environment configuration..."

cat > n8n/.env.product-classification << EOF
# VividWalls Product Classification Environment Variables

# Digital Ocean Spaces Configuration
DO_SPACES_ENDPOINT=${DO_SPACES_ENDPOINT:-nyc3.digitaloceanspaces.com}
DO_SPACES_REGION=${DO_SPACES_REGION:-nyc3}
DO_SPACES_BUCKET=${DO_SPACES_BUCKET:-vividwalls-products}
DO_SPACES_KEY=${DO_SPACES_KEY}
DO_SPACES_SECRET=${DO_SPACES_SECRET}

# Supabase Configuration
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL_VISION=gpt-4-vision-preview
OPENAI_MODEL_EMBEDDING=text-embedding-3-large

# Processing Configuration
BATCH_SIZE=5
MAX_RETRIES=3
RATE_LIMIT_DELAY=2000
IMAGE_QUALITY=85
MAX_IMAGE_SIZE=2048
EOF

echo "✅ Environment configuration created: n8n/.env.product-classification"

# Validate CSV file structure
echo "📋 Validating product CSV structure..."

# Check if CSV has required headers
REQUIRED_HEADERS=(
    "Handle"
    "Title"
    "Body (HTML)"
    "Vendor"
    "Product Category"
    "Type"
    "Tags"
    "Published"
    "Option1 Value"
    "Option2 Value"
    "Option3 Value"
    "Variant SKU"
    "Variant Price"
    "Image Src"
    "Image Position"
    "Image Alt Text"
    "Status"
)

CSV_FILE="n8n/shared/products/vividwalls-products-list-2-23-2025.csv"
HEADER_LINE=$(head -n 1 "$CSV_FILE")

MISSING_HEADERS=()
for header in "${REQUIRED_HEADERS[@]}"; do
    if [[ "$HEADER_LINE" != *"$header"* ]]; then
        MISSING_HEADERS+=("$header")
    fi
done

if [ ${#MISSING_HEADERS[@]} -ne 0 ]; then
    echo "❌ Missing required CSV headers:"
    for header in "${MISSING_HEADERS[@]}"; do
        echo "   - $header"
    done
    exit 1
fi

echo "✅ CSV structure validation passed"

# Count products and images
TOTAL_LINES=$(wc -l < "$CSV_FILE")
TOTAL_PRODUCTS=$((TOTAL_LINES - 1))  # Subtract header line
UNIQUE_HANDLES=$(tail -n +2 "$CSV_FILE" | cut -d',' -f1 | sort | uniq | wc -l)
IMAGES_COUNT=$(tail -n +2 "$CSV_FILE" | grep -c "https://cdn.shopify.com" || true)

echo "📊 Product Statistics:"
echo "   - Total CSV rows: $TOTAL_PRODUCTS"
echo "   - Unique products: $UNIQUE_HANDLES"
echo "   - Images to process: $IMAGES_COUNT"

# Estimate processing time
ESTIMATED_MINUTES=$((IMAGES_COUNT / 5 * 2 / 60))  # 5 images per batch, 2 seconds between batches
echo "   - Estimated processing time: ~$ESTIMATED_MINUTES minutes"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Import the workflow into n8n:"
echo "   - Go to https://n8n.vividwalls.blog"
echo "   - Click '+' → Import from file"
echo "   - Upload: n8n/shared/knowledge/VividWalls-Product-Classification-Workflow.json"
echo ""
echo "2. Configure credentials in n8n:"
echo "   - Add Supabase API credentials"
echo "   - Add OpenAI API credentials"
echo "   - Add Digital Ocean Spaces credentials (as AWS S3)"
echo ""
echo "3. Activate the workflow and trigger it via webhook:"
echo "   - POST to: https://n8n.vividwalls.blog/webhook/vividwalls-product-processor"
echo ""
echo "4. Monitor progress in n8n execution logs"
echo ""
echo "Environment file created: n8n/.env.product-classification"
echo "Database schema file: /tmp/vividwalls_schema.sql"

# Cleanup
rm -f /tmp/vividwalls_schema.sql 