-- VividWalls Data Migration Script
-- Migrates existing product data from CSV imports to new comprehensive schema

-- =====================================================
-- STEP 1: MIGRATE EXISTING PRODUCTS DATA
-- =====================================================

-- First, let's create a temporary table to import the existing products CSV data
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

-- Import the CSV data (this would be done via COPY command or similar)
-- COPY temp_products_import FROM '/path/to/vividwalls-products-list-2-23-2025.csv' WITH CSV HEADER;

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

-- =====================================================
-- STEP 5: MIGRATE PRODUCT IMAGES
-- =====================================================

-- Insert product images
INSERT INTO product_images (
    product_id,
    variant_id,
    image_type,
    storage_url,
    cdn_url,
    width,
    height,
    format,
    alt_text,
    is_primary
)
SELECT 
    p.id as product_id,
    pv.id as variant_id,
    CASE 
        WHEN t.image_position = 1 THEN 'primary'
        ELSE 'variant'
    END as image_type,
    t.image_src as storage_url,
    t.image_src as cdn_url,
    -- Default dimensions (would need actual image analysis)
    1200 as width,
    1200 as height,
    'jpeg' as format,
    COALESCE(t.image_alt_text, t.title) as alt_text,
    CASE WHEN t.image_position = 1 THEN true ELSE false END as is_primary
FROM temp_products_import t
JOIN products p ON p.handle = t.handle
LEFT JOIN product_variants pv ON pv.sku = t.variant_sku
WHERE t.image_src IS NOT NULL AND t.image_src != ''
ON CONFLICT (product_id, image_type, variant_id) DO UPDATE SET
    storage_url = EXCLUDED.storage_url,
    cdn_url = EXCLUDED.cdn_url;

-- =====================================================
-- STEP 6: GENERATE AI ANALYSIS PLACEHOLDERS
-- =====================================================

-- Insert placeholder AI analysis for all products
-- This would be populated by actual AI analysis workflows
INSERT INTO product_analysis (
    product_id,
    color_analysis,
    dominant_colors,
    color_temperature,
    color_harmony,
    style_classification,
    art_movement,
    composition_type,
    visual_complexity,
    mood_analysis,
    primary_mood,
    secondary_mood,
    emotional_associations,
    psychological_benefits,
    geometric_analysis,
    shape_types,
    pattern_recognition,
    symmetry_type,
    technical_characteristics,
    image_quality_score,
    visual_impact_strength,
    space_suitability,
    recommended_rooms,
    size_recommendations,
    lighting_compatibility,
    style_compatibility,
    ai_confidence_score,
    model_used,
    analysis_version
)
SELECT 
    p.id as product_id,
    -- Generate analysis based on collection characteristics
    json_build_object(
        'dominantColors', c.color_palette,
        'colorHarmony', 'harmonious',
        'moodClassification', json_build_object('primary', c.mood_profile)
    ) as color_analysis,
    c.color_palette as dominant_colors,
    CASE 
        WHEN c.mood_profile = 'energizing' THEN 'warm'
        WHEN c.mood_profile = 'calming' THEN 'cool'
        ELSE 'neutral'
    END as color_temperature,
    'harmonious' as color_harmony,
    json_build_object(
        'movement', 'Abstract',
        'compositionType', 'Geometric',
        'complexity', 'Moderate'
    ) as style_classification,
    'Abstract' as art_movement,
    'Geometric' as composition_type,
    'Moderate' as visual_complexity,
    json_build_object(
        'primaryMood', c.mood_profile,
        'emotions', c.style_characteristics
    ) as mood_analysis,
    c.mood_profile as primary_mood,
    CASE 
        WHEN c.mood_profile = 'energizing' THEN 'inspiring'
        WHEN c.mood_profile = 'calming' THEN 'peaceful'
        WHEN c.mood_profile = 'sophisticated' THEN 'elegant'
        WHEN c.mood_profile = 'dramatic' THEN 'bold'
        ELSE 'balanced'
    END as secondary_mood,
    ARRAY['inspiring', 'focused', 'creative'] as emotional_associations,
    ARRAY['stress_reduction', 'creativity_stimulation', 'focus_enhancement'] as psychological_benefits,
    json_build_object(
        'shapes', ARRAY['geometric', 'abstract'],
        'patterns', ARRAY['structured', 'flowing'],
        'symmetry', 'balanced'
    ) as geometric_analysis,
    ARRAY['geometric', 'abstract'] as shape_types,
    'structured' as pattern_recognition,
    'balanced' as symmetry_type,
    json_build_object(
        'imageQuality', 9,
        'clarity', 'high',
        'colorAccuracy', 'excellent'
    ) as technical_characteristics,
    9.0 as image_quality_score,
    8.5 as visual_impact_strength,
    json_build_object(
        'roomTypes', ARRAY['living_room', 'bedroom', 'office'],
        'sizeRecommendations', ARRAY['medium', 'large']
    ) as space_suitability,
    ARRAY['living_room', 'bedroom', 'office'] as recommended_rooms,
    ARRAY['medium', 'large'] as size_recommendations,
    ARRAY['natural', 'artificial', 'mixed'] as lighting_compatibility,
    ARRAY['modern', 'contemporary', 'transitional'] as style_compatibility,
    0.85 as ai_confidence_score,
    'placeholder-analysis-v1' as model_used,
    '1.0' as analysis_version
FROM products p
JOIN collections c ON p.collection = c.name
ON CONFLICT (product_id) DO NOTHING;

-- =====================================================
-- STEP 7: GENERATE PRODUCT TAGS
-- =====================================================

-- Auto-generate tags based on collection and analysis
INSERT INTO product_tags (product_id, tag_id, tag_source, confidence_score)
SELECT DISTINCT
    p.id as product_id,
    t.id as tag_id,
    'auto_generated' as tag_source,
    0.8 as confidence_score
FROM products p
JOIN product_analysis pa ON p.id = pa.product_id
JOIN tags t ON (
    -- Match mood tags
    (t.category = 'mood' AND t.name = pa.primary_mood) OR
    -- Match color temperature tags
    (t.category = 'color' AND t.name = pa.color_temperature || '-tones') OR
    -- Match style tags based on art movement
    (t.category = 'style' AND LOWER(t.name) = LOWER(pa.art_movement)) OR
    -- Match room tags
    (t.category = 'room' AND t.name = ANY(pa.recommended_rooms))
)
ON CONFLICT (product_id, tag_id) DO NOTHING;

-- =====================================================
-- STEP 8: GENERATE VECTOR EMBEDDINGS PLACEHOLDERS
-- =====================================================

-- Insert placeholder embeddings (would be generated by actual embedding model)
INSERT INTO product_embeddings (
    product_id,
    embedding,
    embedding_text,
    embedding_type,
    model_used
)
SELECT 
    p.id as product_id,
    -- Generate a random vector for placeholder (replace with actual embeddings)
    array_fill(0.0, ARRAY[1536])::vector as embedding,
    CONCAT(
        p.title, ' ',
        COALESCE(p.description, ''), ' ',
        p.collection, ' ',
        pa.primary_mood, ' ',
        array_to_string(pa.dominant_colors, ' ')
    ) as embedding_text,
    'comprehensive' as embedding_type,
    'text-embedding-3-large' as model_used
FROM products p
LEFT JOIN product_analysis pa ON p.id = pa.product_id
ON CONFLICT (product_id, embedding_type) DO NOTHING;

-- =====================================================
-- STEP 9: GENERATE ROOM SUITABILITY SCORES
-- =====================================================

-- Generate room suitability scores for all product-room combinations
INSERT INTO product_room_suitability (
    product_id,
    room_type_id,
    suitability_score,
    reasoning,
    size_recommendations,
    placement_suggestions,
    lighting_requirements
)
SELECT 
    p.id as product_id,
    rt.id as room_type_id,
    CASE 
        WHEN rt.name = ANY(pa.recommended_rooms) THEN 0.9
        WHEN pa.primary_mood = 'calming' AND rt.category = 'private' THEN 0.8
        WHEN pa.primary_mood = 'energizing' AND rt.category = 'living' THEN 0.8
        WHEN pa.primary_mood = 'sophisticated' AND rt.category = 'work' THEN 0.9
        ELSE 0.6
    END as suitability_score,
    CONCAT(
        'Based on ', pa.primary_mood, ' mood and ', pa.art_movement, ' style, ',
        'this artwork is well-suited for ', rt.name, ' environments.'
    ) as reasoning,
    pa.size_recommendations,
    CASE 
        WHEN rt.name = 'Living Room' THEN ARRAY['above sofa', 'focal wall', 'gallery wall']
        WHEN rt.name = 'Bedroom' THEN ARRAY['above bed', 'side wall', 'dresser area']
        WHEN rt.name = 'Home Office' THEN ARRAY['behind desk', 'side wall', 'inspiration wall']
        ELSE ARRAY['feature wall', 'accent placement']
    END as placement_suggestions,
    pa.lighting_compatibility
FROM products p
JOIN product_analysis pa ON p.id = pa.product_id
CROSS JOIN room_types rt
WHERE rt.is_active = true
ON CONFLICT (product_id, room_type_id) DO UPDATE SET
    suitability_score = EXCLUDED.suitability_score,
    reasoning = EXCLUDED.reasoning;

-- =====================================================
-- STEP 10: UPDATE STATISTICS AND CLEANUP
-- =====================================================

-- Update tag usage counts
UPDATE tags SET usage_count = (
    SELECT COUNT(*) 
    FROM product_tags pt 
    WHERE pt.tag_id = tags.id
);

-- Update collection metadata with product counts
UPDATE collections SET metadata = json_build_object(
    'product_count', (
        SELECT COUNT(*) 
        FROM products p 
        WHERE p.collection = collections.name
    ),
    'avg_price', (
        SELECT AVG(pv.price)
        FROM products p
        JOIN product_variants pv ON p.id = pv.product_id
        WHERE p.collection = collections.name
    )
);

-- Clean up temporary table
DROP TABLE temp_products_import;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify migration results
SELECT 
    'Products' as table_name,
    COUNT(*) as record_count
FROM products
UNION ALL
SELECT 
    'Product Variants' as table_name,
    COUNT(*) as record_count
FROM product_variants
UNION ALL
SELECT 
    'Product Images' as table_name,
    COUNT(*) as record_count
FROM product_images
UNION ALL
SELECT 
    'Product Analysis' as table_name,
    COUNT(*) as record_count
FROM product_analysis
UNION ALL
SELECT 
    'Product Tags' as table_name,
    COUNT(*) as record_count
FROM product_tags
UNION ALL
SELECT 
    'Product Embeddings' as table_name,
    COUNT(*) as record_count
FROM product_embeddings
UNION ALL
SELECT 
    'Collections' as table_name,
    COUNT(*) as record_count
FROM collections
UNION ALL
SELECT 
    'Tags' as table_name,
    COUNT(*) as record_count
FROM tags;

-- Sample query to test the comprehensive view
SELECT * FROM product_details_view LIMIT 5;

COMMENT ON SCRIPT IS 'VividWalls data migration script - migrates existing product data to comprehensive schema with AI analysis placeholders'; 