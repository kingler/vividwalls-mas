#!/bin/bash

# Complete CSV Import Script for VividWalls
# Imports product data and runs the migration in one session

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Database connection settings
DB_HOST="localhost"
DB_PORT="54322"
DB_USER="postgres"
DB_PASSWORD="${DB_PASSWORD:?set DB_PASSWORD}"
DB_NAME="postgres"

echo -e "${BLUE}📥 VividWalls CSV Data Import Starting...${NC}"
echo "=================================================="

# Check if CSV file exists
CSV_FILE="n8n/data/shared/vividwalls-products-list-2-23-2025.csv"
if [[ ! -f "$CSV_FILE" ]]; then
    echo -e "${RED}❌ CSV file not found: $CSV_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found CSV file: $CSV_FILE${NC}"

# Get absolute path
CSV_ABSOLUTE_PATH="$(pwd)/$CSV_FILE"
echo -e "${BLUE}📁 Absolute path: $CSV_ABSOLUTE_PATH${NC}"

# Create a combined SQL script that does everything in one transaction
cat > /tmp/complete_import.sql << EOF
-- Complete VividWalls CSV Import and Migration

-- Create temporary table for product import
CREATE TEMP TABLE temp_products_import (
    handle VARCHAR(255),
    title VARCHAR(500),
    body_html TEXT,
    vendor VARCHAR(255),
    product_type VARCHAR(255),
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    published VARCHAR(10),
    template_suffix VARCHAR(100),
    published_scope VARCHAR(50),
    tags TEXT,
    status VARCHAR(50),
    admin_graphql_api_id VARCHAR(255),
    variant_id VARCHAR(255),
    variant_title VARCHAR(255),
    variant_sku VARCHAR(255),
    variant_position INTEGER,
    variant_inventory_tracker VARCHAR(50),
    variant_inventory_qty INTEGER,
    variant_inventory_policy VARCHAR(50),
    variant_fulfillment_service VARCHAR(50),
    variant_price DECIMAL(10,2),
    variant_compare_at_price DECIMAL(10,2),
    variant_requires_shipping VARCHAR(10),
    variant_taxable VARCHAR(10),
    variant_barcode VARCHAR(255),
    image_src TEXT,
    image_position INTEGER,
    image_alt_text TEXT,
    gift_card VARCHAR(10),
    seo_title VARCHAR(500),
    seo_description TEXT,
    google_shopping_google_product_category VARCHAR(255),
    google_shopping_gender VARCHAR(50),
    google_shopping_age_group VARCHAR(50),
    google_shopping_mpn VARCHAR(255),
    google_shopping_condition VARCHAR(50),
    google_shopping_custom_product VARCHAR(255),
    google_shopping_custom_label_0 VARCHAR(255),
    google_shopping_custom_label_1 VARCHAR(255),
    google_shopping_custom_label_2 VARCHAR(255),
    google_shopping_custom_label_3 VARCHAR(255),
    google_shopping_custom_label_4 VARCHAR(255),
    variant_image TEXT,
    variant_weight_unit VARCHAR(20),
    variant_weight DECIMAL(8,2),
    cost_per_item DECIMAL(10,2),
    included VARCHAR(10),
    price_international DECIMAL(10,2),
    compare_at_price_international DECIMAL(10,2),
    status_international VARCHAR(50)
);

-- Import CSV data
\COPY temp_products_import FROM '$CSV_ABSOLUTE_PATH' WITH CSV HEADER;

-- Check import success
SELECT 'CSV Import Complete - Records imported: ' || COUNT(*) FROM temp_products_import;
EOF

# Add the migration script content (without the temp table creation part)
cat >> /tmp/complete_import.sql << 'EOF'

-- =====================================================
-- STEP 2: EXTRACT AND CLASSIFY COLLECTIONS
-- =====================================================

-- Extract unique collections from the imported data and classify them
INSERT INTO collections (name, slug, description, mood_profile, color_palette, style_characteristics)
SELECT DISTINCT
    TRIM(product_type) as name,
    LOWER(REPLACE(REPLACE(TRIM(product_type), ' ', '-'), '&', 'and')) as slug,
    CASE 
        WHEN TRIM(product_type) LIKE '%Chromatic%' THEN 'Vibrant abstract pieces exploring emotional color resonance'
        WHEN TRIM(product_type) LIKE '%Geometric%' AND TRIM(product_type) LIKE '%Intersection%' THEN 'Clean geometric forms creating sophisticated visual harmony'
        WHEN TRIM(product_type) LIKE '%Geometric%' AND TRIM(product_type) LIKE '%Symmetry%' THEN 'Balanced compositions emphasizing order and elegance'
        WHEN TRIM(product_type) LIKE '%Resonant%' THEN 'Cool-toned pieces promoting focus and tranquility'
        WHEN TRIM(product_type) LIKE '%Intersecting%' THEN 'Bold compositions with dramatic visual impact'
        WHEN TRIM(product_type) LIKE '%Shape%' THEN 'Organic forms flowing naturally through space'
        WHEN TRIM(product_type) LIKE '%Fractal%' THEN 'Complex patterns stimulating creativity and energy'
        WHEN TRIM(product_type) LIKE '%Mosaic%' THEN 'Textured compositions with rich layered detail'
        WHEN TRIM(product_type) LIKE '%Vivid%' THEN 'Dimensional pieces creating depth and sophistication'
        ELSE 'Contemporary abstract artwork collection'
    END as description,
    CASE 
        WHEN TRIM(product_type) LIKE '%Chromatic%' THEN 'energizing'
        WHEN TRIM(product_type) LIKE '%Geometric%' THEN 'sophisticated'
        WHEN TRIM(product_type) LIKE '%Resonant%' THEN 'calming'
        WHEN TRIM(product_type) LIKE '%Intersecting%' THEN 'dramatic'
        WHEN TRIM(product_type) LIKE '%Shape%' THEN 'natural'
        WHEN TRIM(product_type) LIKE '%Fractal%' THEN 'energizing'
        WHEN TRIM(product_type) LIKE '%Mosaic%' THEN 'sophisticated'
        WHEN TRIM(product_type) LIKE '%Vivid%' THEN 'sophisticated'
        ELSE 'sophisticated'
    END as mood_profile,
    CASE 
        WHEN TRIM(product_type) LIKE '%Chromatic%' THEN ARRAY['red', 'orange', 'yellow', 'coral']
        WHEN TRIM(product_type) LIKE '%Geometric%' THEN ARRAY['blue', 'gray', 'white', 'black']
        WHEN TRIM(product_type) LIKE '%Resonant%' THEN ARRAY['blue', 'teal', 'navy', 'mint']
        WHEN TRIM(product_type) LIKE '%Intersecting%' THEN ARRAY['black', 'white', 'red', 'gold']
        WHEN TRIM(product_type) LIKE '%Shape%' THEN ARRAY['green', 'brown', 'earth', 'natural']
        WHEN TRIM(product_type) LIKE '%Fractal%' THEN ARRAY['rainbow', 'multi', 'vibrant']
        WHEN TRIM(product_type) LIKE '%Mosaic%' THEN ARRAY['multi', 'rich', 'layered']
        WHEN TRIM(product_type) LIKE '%Vivid%' THEN ARRAY['deep', 'rich', 'dimensional']
        ELSE ARRAY['neutral', 'versatile']
    END as color_palette,
    CASE 
        WHEN TRIM(product_type) LIKE '%Chromatic%' THEN ARRAY['vibrant', 'emotional', 'warm']
        WHEN TRIM(product_type) LIKE '%Geometric%' THEN ARRAY['geometric', 'clean', 'modern']
        WHEN TRIM(product_type) LIKE '%Resonant%' THEN ARRAY['cool', 'structured', 'calming']
        WHEN TRIM(product_type) LIKE '%Intersecting%' THEN ARRAY['bold', 'high-contrast', 'dramatic']
        WHEN TRIM(product_type) LIKE '%Shape%' THEN ARRAY['organic', 'flowing', 'natural']
        WHEN TRIM(product_type) LIKE '%Fractal%' THEN ARRAY['complex', 'energizing', 'creative']
        WHEN TRIM(product_type) LIKE '%Mosaic%' THEN ARRAY['textured', 'detailed', 'rich']
        WHEN TRIM(product_type) LIKE '%Vivid%' THEN ARRAY['layered', 'dimensional', 'sophisticated']
        ELSE ARRAY['contemporary', 'abstract']
    END as style_characteristics
FROM temp_products_import 
WHERE TRIM(product_type) IS NOT NULL AND TRIM(product_type) != ''
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- STEP 3: MIGRATE PRODUCTS
-- =====================================================

-- Insert products from imported data
INSERT INTO products (
    handle, 
    title, 
    description, 
    vendor, 
    category, 
    type, 
    collection, 
    published, 
    status, 
    tags,
    shopify_id,
    shopify_url
)
SELECT DISTINCT
    handle,
    title,
    body_html as description,
    vendor,
    google_shopping_google_product_category as category,
    product_type as type,
    TRIM(product_type) as collection,
    CASE WHEN LOWER(published) = 'true' THEN true ELSE false END as published,
    COALESCE(status, 'active') as status,
    CASE 
        WHEN tags IS NOT NULL AND tags != '' 
        THEN string_to_array(tags, ',')
        ELSE ARRAY[]::TEXT[]
    END as tags,
    admin_graphql_api_id as shopify_id,
    CASE 
        WHEN handle IS NOT NULL 
        THEN 'https://vividwalls.com/products/' || handle
        ELSE NULL
    END as shopify_url
FROM temp_products_import
WHERE handle IS NOT NULL
ON CONFLICT (handle) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    updated_at = NOW();

-- Show products imported
SELECT 'Products imported: ' || COUNT(*) FROM products;

-- =====================================================
-- STEP 4: MIGRATE PRODUCT VARIANTS
-- =====================================================

-- Insert product variants
INSERT INTO product_variants (
    product_id,
    sku,
    frame_size,
    frame_color,
    frame_style,
    price,
    compare_at_price,
    shopify_image_url,
    image_position,
    image_alt,
    inventory_quantity,
    weight,
    dimensions,
    available
)
SELECT 
    p.id as product_id,
    t.variant_sku as sku,
    -- Extract frame size from variant title or SKU
    CASE 
        WHEN t.variant_title ~ '\d+x\d+' THEN 
            (regexp_matches(t.variant_title, '(\d+x\d+)', 'g'))[1]
        WHEN t.variant_sku ~ '\d+x\d+' THEN 
            (regexp_matches(t.variant_sku, '(\d+x\d+)', 'g'))[1]
        ELSE 'standard'
    END as frame_size,
    -- Extract frame color (if mentioned)
    CASE 
        WHEN LOWER(t.variant_title) LIKE '%black%' THEN 'black'
        WHEN LOWER(t.variant_title) LIKE '%white%' THEN 'white'
        WHEN LOWER(t.variant_title) LIKE '%natural%' THEN 'natural'
        WHEN LOWER(t.variant_title) LIKE '%silver%' THEN 'silver'
        ELSE 'standard'
    END as frame_color,
    -- Extract frame style
    CASE 
        WHEN LOWER(t.variant_title) LIKE '%framed%' THEN 'framed'
        WHEN LOWER(t.variant_title) LIKE '%canvas%' THEN 'canvas'
        WHEN LOWER(t.variant_title) LIKE '%print%' THEN 'print'
        ELSE 'standard'
    END as frame_style,
    t.variant_price as price,
    t.variant_compare_at_price as compare_at_price,
    t.variant_image as shopify_image_url,
    t.image_position,
    t.image_alt_text as image_alt,
    COALESCE(t.variant_inventory_qty, 0) as inventory_quantity,
    t.variant_weight as weight,
    -- Create dimensions JSON from extracted size
    CASE 
        WHEN t.variant_title ~ '\d+x\d+' THEN 
            json_build_object(
                'width', split_part((regexp_matches(t.variant_title, '(\d+)x(\d+)', 'g'))[1], 'x', 1)::integer,
                'height', split_part((regexp_matches(t.variant_title, '(\d+)x(\d+)', 'g'))[1], 'x', 2)::integer,
                'unit', 'inches'
            )
        ELSE json_build_object('width', 24, 'height', 36, 'unit', 'inches')
    END as dimensions,
    CASE WHEN LOWER(status) = 'active' THEN true ELSE false END as available
FROM temp_products_import t
JOIN products p ON p.handle = t.handle
WHERE t.variant_sku IS NOT NULL
ON CONFLICT (sku) DO UPDATE SET
    price = EXCLUDED.price,
    compare_at_price = EXCLUDED.compare_at_price,
    inventory_quantity = EXCLUDED.inventory_quantity;

-- Show variants imported
SELECT 'Product variants imported: ' || COUNT(*) FROM product_variants;

-- =====================================================
-- FINAL SUMMARY
-- =====================================================

SELECT 'Import Summary:' as summary;
SELECT 'Collections: ' || COUNT(*) FROM collections;
SELECT 'Products: ' || COUNT(*) FROM products;
SELECT 'Product Variants: ' || COUNT(*) FROM product_variants;
SELECT 'Tags: ' || COUNT(*) FROM tags;
SELECT 'Room Types: ' || COUNT(*) FROM room_types;
EOF

echo -e "${YELLOW}📝 Running complete import and migration...${NC}"

# Run the complete import
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /tmp/complete_import.sql; then
    echo -e "${GREEN}✅ CSV import and migration completed successfully!${NC}"
else
    echo -e "${RED}❌ Import failed${NC}"
    exit 1
fi

# Clean up
rm -f /tmp/complete_import.sql

echo -e "\n${GREEN}🎉 VividWalls CSV Data Import Complete!${NC}"
echo "==================================================" 