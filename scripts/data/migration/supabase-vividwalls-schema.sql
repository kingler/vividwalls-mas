-- VividWalls Comprehensive Database Schema for Supabase/PostgreSQL
-- Supports product image tagging, classification, categorization, and AI analysis

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- CORE PRODUCT TABLES
-- =====================================================

-- Main products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    handle VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    vendor VARCHAR(255),
    category VARCHAR(255),
    type VARCHAR(255),
    collection VARCHAR(255),
    published BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'active',
    tags TEXT[],
    shopify_id VARCHAR(255),
    shopify_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product variants table (different sizes, frames, etc.)
CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(255) UNIQUE NOT NULL,
    frame_size VARCHAR(50),
    frame_color VARCHAR(50),
    frame_style VARCHAR(100),
    price DECIMAL(10,2),
    compare_at_price DECIMAL(10,2),
    shopify_image_url TEXT,
    image_position INTEGER,
    image_alt TEXT,
    inventory_quantity INTEGER DEFAULT 0,
    weight DECIMAL(8,2),
    dimensions JSONB, -- {width: 24, height: 36, depth: 1.5, unit: "inches"}
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- IMAGE STORAGE AND MANAGEMENT
-- =====================================================

-- Product images table (optimized storage)
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(id) ON DELETE SET NULL,
    image_type VARCHAR(50) NOT NULL, -- 'primary', 'variant', 'optimized', 'thumbnail', 'analysis'
    storage_url TEXT NOT NULL,
    storage_key VARCHAR(500),
    cdn_url TEXT,
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    format VARCHAR(20), -- 'webp', 'jpeg', 'png'
    quality INTEGER,
    alt_text TEXT,
    is_primary BOOLEAN DEFAULT false,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, image_type, variant_id)
);

-- =====================================================
-- AI ANALYSIS AND CLASSIFICATION
-- =====================================================

-- Comprehensive AI analysis results
CREATE TABLE product_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    
    -- Color Analysis
    color_analysis JSONB, -- {dominantColors: [...], colorHarmony: "...", moodClassification: {...}}
    dominant_colors TEXT[], -- ["#2E5BBA", "#8B4A9C", "#E8E8E8"]
    color_temperature VARCHAR(20), -- 'warm', 'cool', 'neutral'
    color_harmony VARCHAR(50), -- 'complementary', 'analogous', 'triadic', etc.
    
    -- Style Classification
    style_classification JSONB, -- {movement: "...", compositionType: "...", complexity: "..."}
    art_movement VARCHAR(100), -- 'Abstract', 'Geometric', 'Minimalist', 'Op Art'
    composition_type VARCHAR(50), -- 'Symmetrical', 'Asymmetrical', 'Radial', 'Grid-based'
    visual_complexity VARCHAR(20), -- 'Simple', 'Moderate', 'Complex'
    
    -- Mood and Psychological Analysis
    mood_analysis JSONB, -- {primaryMood: "...", secondaryMood: "...", emotions: [...]}
    primary_mood VARCHAR(50), -- 'energizing', 'calming', 'sophisticated', etc.
    secondary_mood VARCHAR(50),
    emotional_associations TEXT[], -- ['peaceful', 'inspiring', 'focused']
    psychological_benefits TEXT[], -- ['stress_reduction', 'creativity_stimulation']
    
    -- Geometric and Pattern Analysis
    geometric_analysis JSONB, -- {shapes: [...], patterns: [...], symmetry: "..."}
    shape_types TEXT[], -- ['circles', 'triangles', 'organic_forms']
    pattern_recognition VARCHAR(50), -- 'repetitive', 'random', 'structured', 'flowing'
    symmetry_type VARCHAR(30), -- 'perfect', 'approximate', 'asymmetrical'
    
    -- Technical Characteristics
    technical_characteristics JSONB, -- {imageQuality: 9, clarity: "high", colorAccuracy: "excellent"}
    image_quality_score DECIMAL(3,1), -- 1-10 scale
    visual_impact_strength DECIMAL(3,1), -- 1-10 scale
    
    -- Space Suitability
    space_suitability JSONB, -- {roomTypes: [...], sizeRecommendations: [...]}
    recommended_rooms TEXT[], -- ['bedroom', 'living_room', 'office']
    size_recommendations TEXT[], -- ['small', 'medium', 'large']
    lighting_compatibility TEXT[], -- ['natural', 'artificial', 'mixed']
    style_compatibility TEXT[], -- ['modern', 'traditional', 'eclectic']
    
    -- AI Metadata
    ai_confidence_score DECIMAL(3,2), -- 0.00-1.00
    model_used VARCHAR(100),
    analysis_version VARCHAR(20),
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(product_id)
);

-- =====================================================
-- TAGGING AND CATEGORIZATION SYSTEM
-- =====================================================

-- Master tags table for consistent tagging
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'color', 'style', 'mood', 'room', 'collection', 'technical'
    description TEXT,
    parent_tag_id UUID REFERENCES tags(id),
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product-tag relationships with context
CREATE TABLE product_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    tag_source VARCHAR(50), -- 'ai_analysis', 'manual', 'user_generated', 'shopify_import'
    confidence_score DECIMAL(3,2), -- 0.00-1.00 for AI-generated tags
    context JSONB, -- Additional context about why this tag was applied
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, tag_id)
);

-- Categories for hierarchical organization
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_category_id UUID REFERENCES categories(id),
    level INTEGER DEFAULT 0, -- 0=root, 1=subcategory, etc.
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB, -- Additional category-specific data
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product-category relationships
CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    assigned_by VARCHAR(50) DEFAULT 'system', -- 'system', 'admin', 'ai'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, category_id)
);

-- =====================================================
-- VECTOR EMBEDDINGS FOR SIMILARITY SEARCH
-- =====================================================

-- Vector embeddings for semantic search
CREATE TABLE product_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    embedding VECTOR(1536), -- OpenAI text-embedding-3-large dimensions
    embedding_text TEXT, -- The text used to generate the embedding
    embedding_type VARCHAR(50) DEFAULT 'comprehensive', -- 'comprehensive', 'visual', 'textual'
    model_used VARCHAR(100) DEFAULT 'text-embedding-3-large',
    dimensions INTEGER DEFAULT 1536,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, embedding_type)
);

-- =====================================================
-- SEARCH AND RECOMMENDATION SYSTEM
-- =====================================================

-- Search queries and results tracking
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    query_text TEXT,
    search_parameters JSONB, -- Extracted search parameters
    search_type VARCHAR(50), -- 'vector', 'tag', 'category', 'color', 'hybrid'
    results_count INTEGER,
    selected_products UUID[], -- Array of product IDs user interacted with
    user_feedback JSONB, -- User feedback on results
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User preferences and personalization
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    preferred_styles TEXT[], -- ['modern', 'minimalist']
    preferred_colors TEXT[], -- ['blue', 'gray', 'white']
    preferred_moods TEXT[], -- ['calming', 'sophisticated']
    room_types TEXT[], -- ['bedroom', 'office', 'living_room']
    size_preferences TEXT[], -- ['large', 'medium']
    budget_range JSONB, -- {min: 400, max: 1200}
    avoided_elements TEXT[], -- Things user doesn't like
    interaction_history JSONB, -- Detailed interaction patterns
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Product recommendations tracking
CREATE TABLE product_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50), -- 'similar', 'complementary', 'trending', 'personalized'
    relevance_score DECIMAL(3,2),
    recommendation_reason TEXT,
    source_product_id UUID REFERENCES products(id), -- If based on another product
    algorithm_version VARCHAR(20),
    presented_at TIMESTAMPTZ DEFAULT NOW(),
    user_action VARCHAR(50), -- 'viewed', 'liked', 'saved', 'purchased', 'ignored'
    action_timestamp TIMESTAMPTZ
);

-- =====================================================
-- COLLECTIONS AND SERIES MANAGEMENT
-- =====================================================

-- Art collections (Chromatic Echoes, Geometric Intersection, etc.)
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    artist_statement TEXT,
    inspiration TEXT,
    color_palette TEXT[], -- Dominant colors in collection
    style_characteristics TEXT[], -- Key style elements
    mood_profile VARCHAR(50), -- Overall mood of collection
    is_featured BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    metadata JSONB, -- Additional collection data
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Update products table to reference collections properly
ALTER TABLE products ADD CONSTRAINT fk_products_collection 
    FOREIGN KEY (collection) REFERENCES collections(name);

-- =====================================================
-- ROOM AND SPACE ANALYSIS
-- =====================================================

-- Room types and characteristics
CREATE TABLE room_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'living', 'private', 'work', 'functional', 'specialized'
    typical_functions TEXT[], -- ['relaxation', 'entertainment', 'work']
    lighting_characteristics TEXT[], -- ['natural', 'artificial', 'mixed', 'low']
    size_considerations TEXT[], -- ['small', 'medium', 'large', 'variable']
    style_compatibility TEXT[], -- Compatible interior styles
    artwork_guidelines JSONB, -- Guidelines for artwork in this room type
    is_active BOOLEAN DEFAULT true
);

-- Space suitability scoring
CREATE TABLE product_room_suitability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    room_type_id UUID REFERENCES room_types(id) ON DELETE CASCADE,
    suitability_score DECIMAL(3,2), -- 0.00-1.00
    reasoning TEXT,
    size_recommendations TEXT[], -- Recommended sizes for this room
    placement_suggestions TEXT[], -- Where to place in room
    lighting_requirements TEXT[], -- Lighting needs
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, room_type_id)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Core product indexes
CREATE INDEX idx_products_handle ON products(handle);
CREATE INDEX idx_products_collection ON products(collection);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_published ON products(published);
CREATE INDEX idx_products_tags ON products USING GIN(tags);

-- Product variants indexes
CREATE INDEX idx_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_variants_sku ON product_variants(sku);
CREATE INDEX idx_variants_frame_size ON product_variants(frame_size);
CREATE INDEX idx_variants_price ON product_variants(price);

-- Image indexes
CREATE INDEX idx_images_product_id ON product_images(product_id);
CREATE INDEX idx_images_type ON product_images(image_type);
CREATE INDEX idx_images_primary ON product_images(is_primary);

-- Analysis indexes
CREATE INDEX idx_analysis_product_id ON product_analysis(product_id);
CREATE INDEX idx_analysis_primary_mood ON product_analysis(primary_mood);
CREATE INDEX idx_analysis_art_movement ON product_analysis(art_movement);
CREATE INDEX idx_analysis_color_temperature ON product_analysis(color_temperature);
CREATE INDEX idx_analysis_dominant_colors ON product_analysis USING GIN(dominant_colors);

-- Tagging indexes
CREATE INDEX idx_tags_category ON tags(category);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_product_tags_product_id ON product_tags(product_id);
CREATE INDEX idx_product_tags_tag_id ON product_tags(tag_id);
CREATE INDEX idx_product_tags_source ON product_tags(tag_source);

-- Vector similarity index
CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Search and recommendation indexes
CREATE INDEX idx_search_queries_user_id ON search_queries(user_id);
CREATE INDEX idx_search_queries_session_id ON search_queries(session_id);
CREATE INDEX idx_search_queries_created_at ON search_queries(created_at);
CREATE INDEX idx_recommendations_user_id ON product_recommendations(user_id);
CREATE INDEX idx_recommendations_product_id ON product_recommendations(product_id);

-- Full-text search indexes
CREATE INDEX idx_products_title_search ON products USING GIN(to_tsvector('english', title));
CREATE INDEX idx_products_description_search ON products USING GIN(to_tsvector('english', description));

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for products table
CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update tag usage count
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET usage_count = usage_count + 1 WHERE id = NEW.tag_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET usage_count = usage_count - 1 WHERE id = OLD.tag_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Trigger for tag usage tracking
CREATE TRIGGER update_tag_usage_trigger
    AFTER INSERT OR DELETE ON product_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION search_similar_products(
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id UUID,
    title VARCHAR(500),
    collection VARCHAR(255),
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.collection,
        1 - (pe.embedding <=> query_embedding) AS similarity
    FROM product_embeddings pe
    JOIN products p ON pe.product_id = p.id
    WHERE 1 - (pe.embedding <=> query_embedding) >= similarity_threshold
    AND p.published = true
    ORDER BY pe.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function for multi-criteria product search
CREATE OR REPLACE FUNCTION search_products_multi_criteria(
    search_tags TEXT[] DEFAULT NULL,
    search_collections TEXT[] DEFAULT NULL,
    search_moods TEXT[] DEFAULT NULL,
    search_rooms TEXT[] DEFAULT NULL,
    color_preferences TEXT[] DEFAULT NULL,
    price_min DECIMAL DEFAULT NULL,
    price_max DECIMAL DEFAULT NULL,
    max_results INTEGER DEFAULT 20
)
RETURNS TABLE (
    product_id UUID,
    title VARCHAR(500),
    collection VARCHAR(255),
    primary_mood VARCHAR(50),
    match_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.collection,
        pa.primary_mood,
        (
            CASE WHEN search_tags IS NULL OR p.tags && search_tags THEN 1 ELSE 0 END +
            CASE WHEN search_collections IS NULL OR p.collection = ANY(search_collections) THEN 1 ELSE 0 END +
            CASE WHEN search_moods IS NULL OR pa.primary_mood = ANY(search_moods) THEN 1 ELSE 0 END +
            CASE WHEN search_rooms IS NULL OR pa.recommended_rooms && search_rooms THEN 1 ELSE 0 END +
            CASE WHEN color_preferences IS NULL OR pa.dominant_colors && color_preferences THEN 1 ELSE 0 END
        ) AS score
    FROM products p
    LEFT JOIN product_analysis pa ON p.id = pa.product_id
    LEFT JOIN product_variants pv ON p.id = pv.product_id
    WHERE p.published = true
    AND (price_min IS NULL OR pv.price >= price_min)
    AND (price_max IS NULL OR pv.price <= price_max)
    HAVING (
        CASE WHEN search_tags IS NULL OR p.tags && search_tags THEN 1 ELSE 0 END +
        CASE WHEN search_collections IS NULL OR p.collection = ANY(search_collections) THEN 1 ELSE 0 END +
        CASE WHEN search_moods IS NULL OR pa.primary_mood = ANY(search_moods) THEN 1 ELSE 0 END +
        CASE WHEN search_rooms IS NULL OR pa.recommended_rooms && search_rooms THEN 1 ELSE 0 END +
        CASE WHEN color_preferences IS NULL OR pa.dominant_colors && color_preferences THEN 1 ELSE 0 END
    ) > 0
    ORDER BY score DESC, p.title
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on sensitive tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_recommendations ENABLE ROW LEVEL SECURITY;

-- Policy for user preferences (users can only see their own)
CREATE POLICY user_preferences_policy ON user_preferences
    FOR ALL USING (auth.uid()::text = user_id);

-- Policy for search queries (users can only see their own)
CREATE POLICY search_queries_policy ON search_queries
    FOR ALL USING (auth.uid()::text = user_id);

-- Policy for recommendations (users can only see their own)
CREATE POLICY recommendations_policy ON product_recommendations
    FOR ALL USING (auth.uid()::text = user_id);

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Insert default room types
INSERT INTO room_types (name, category, typical_functions, lighting_characteristics, size_considerations, style_compatibility) VALUES
('Living Room', 'living', ARRAY['relaxation', 'entertainment', 'socializing'], ARRAY['natural', 'artificial', 'mixed'], ARRAY['medium', 'large'], ARRAY['modern', 'traditional', 'transitional']),
('Bedroom', 'private', ARRAY['sleep', 'relaxation', 'privacy'], ARRAY['soft', 'warm', 'dimmable'], ARRAY['small', 'medium', 'large'], ARRAY['romantic', 'calming', 'personal']),
('Home Office', 'work', ARRAY['work', 'focus', 'productivity'], ARRAY['bright', 'natural', 'task'], ARRAY['small', 'medium'], ARRAY['professional', 'modern', 'minimalist']),
('Kitchen', 'functional', ARRAY['cooking', 'dining', 'gathering'], ARRAY['bright', 'task', 'warm'], ARRAY['medium', 'large'], ARRAY['modern', 'farmhouse', 'traditional']),
('Dining Room', 'functional', ARRAY['dining', 'entertaining', 'formal'], ARRAY['warm', 'ambient', 'chandelier'], ARRAY['medium', 'large'], ARRAY['formal', 'traditional', 'elegant']),
('Bathroom', 'functional', ARRAY['hygiene', 'relaxation', 'privacy'], ARRAY['bright', 'moisture-resistant'], ARRAY['small', 'medium'], ARRAY['spa', 'modern', 'clean']),
('Hallway', 'functional', ARRAY['transition', 'display', 'circulation'], ARRAY['ambient', 'accent'], ARRAY['narrow', 'long'], ARRAY['gallery', 'transitional']),
('Meditation Room', 'specialized', ARRAY['meditation', 'mindfulness', 'peace'], ARRAY['soft', 'natural', 'calming'], ARRAY['small', 'medium'], ARRAY['zen', 'minimalist', 'natural']);

-- Insert default collections
INSERT INTO collections (name, slug, description, mood_profile, color_palette, style_characteristics) VALUES
('Chromatic Echoes', 'chromatic-echoes', 'Vibrant abstract pieces that explore the emotional resonance of color', 'energizing', ARRAY['red', 'orange', 'yellow', 'coral'], ARRAY['vibrant', 'emotional', 'warm']),
('Geometric Intersection', 'geometric-intersection', 'Clean geometric forms that create sophisticated visual harmony', 'sophisticated', ARRAY['blue', 'gray', 'white', 'black'], ARRAY['geometric', 'clean', 'modern']),
('Geometric Symmetry', 'geometric-symmetry', 'Balanced compositions emphasizing order and professional elegance', 'calming', ARRAY['blue', 'teal', 'gray', 'white'], ARRAY['balanced', 'structured', 'professional']),
('Resonant Structure', 'resonant-structure', 'Cool-toned pieces that promote focus and tranquility', 'calming', ARRAY['blue', 'teal', 'navy', 'mint'], ARRAY['cool', 'structured', 'calming']),
('Intersecting Spaces', 'intersecting-spaces', 'Bold compositions with dramatic visual impact', 'dramatic', ARRAY['black', 'white', 'red', 'gold'], ARRAY['bold', 'high-contrast', 'dramatic']),
('Shape Emergence', 'shape-emergence', 'Organic forms that flow naturally through space', 'natural', ARRAY['green', 'brown', 'earth', 'natural'], ARRAY['organic', 'flowing', 'natural']),
('Fractal Color', 'fractal-color', 'Complex patterns that stimulate creativity and energy', 'energizing', ARRAY['rainbow', 'multi', 'vibrant'], ARRAY['complex', 'energizing', 'creative']),
('Mosaics', 'mosaics', 'Textured compositions with rich layered detail', 'sophisticated', ARRAY['multi', 'rich', 'layered'], ARRAY['textured', 'detailed', 'rich']),
('Vivid Layers', 'vivid-layers', 'Dimensional pieces that create depth and sophistication', 'sophisticated', ARRAY['deep', 'rich', 'dimensional'], ARRAY['layered', 'dimensional', 'sophisticated']);

-- Insert default tag categories
INSERT INTO tags (name, category, description) VALUES
-- Color tags
('blue', 'color', 'Blue color dominant in artwork'),
('red', 'color', 'Red color dominant in artwork'),
('green', 'color', 'Green color dominant in artwork'),
('yellow', 'color', 'Yellow color dominant in artwork'),
('orange', 'color', 'Orange color dominant in artwork'),
('purple', 'color', 'Purple color dominant in artwork'),
('black', 'color', 'Black color dominant in artwork'),
('white', 'color', 'White color dominant in artwork'),
('gray', 'color', 'Gray color dominant in artwork'),
('warm-tones', 'color', 'Warm color palette'),
('cool-tones', 'color', 'Cool color palette'),
('neutral-tones', 'color', 'Neutral color palette'),

-- Style tags
('abstract', 'style', 'Abstract art style'),
('geometric', 'style', 'Geometric patterns and shapes'),
('minimalist', 'style', 'Minimalist design approach'),
('modern', 'style', 'Modern contemporary style'),
('traditional', 'style', 'Traditional art style'),
('organic', 'style', 'Organic flowing forms'),

-- Mood tags
('calming', 'mood', 'Creates calming atmosphere'),
('energizing', 'mood', 'Creates energizing atmosphere'),
('sophisticated', 'mood', 'Creates sophisticated atmosphere'),
('playful', 'mood', 'Creates playful atmosphere'),
('romantic', 'mood', 'Creates romantic atmosphere'),
('dramatic', 'mood', 'Creates dramatic atmosphere'),
('peaceful', 'mood', 'Creates peaceful atmosphere'),
('inspiring', 'mood', 'Creates inspiring atmosphere'),

-- Room tags
('living-room', 'room', 'Suitable for living rooms'),
('bedroom', 'room', 'Suitable for bedrooms'),
('office', 'room', 'Suitable for offices'),
('kitchen', 'room', 'Suitable for kitchens'),
('dining-room', 'room', 'Suitable for dining rooms'),
('bathroom', 'room', 'Suitable for bathrooms'),
('hallway', 'room', 'Suitable for hallways'),

-- Technical tags
('high-contrast', 'technical', 'High contrast composition'),
('low-contrast', 'technical', 'Low contrast composition'),
('detailed', 'technical', 'Rich in detail'),
('simple', 'technical', 'Simple composition'),
('textured', 'technical', 'Textured appearance'),
('smooth', 'technical', 'Smooth appearance');

-- Create view for comprehensive product information
CREATE VIEW product_details_view AS
SELECT 
    p.id,
    p.handle,
    p.title,
    p.description,
    p.collection,
    p.status,
    p.published,
    pa.primary_mood,
    pa.secondary_mood,
    pa.art_movement,
    pa.color_temperature,
    pa.dominant_colors,
    pa.recommended_rooms,
    pa.ai_confidence_score,
    array_agg(DISTINCT t.name) as all_tags,
    array_agg(DISTINCT c.name) as categories,
    min(pv.price) as min_price,
    max(pv.price) as max_price,
    array_agg(DISTINCT pv.frame_size) as available_sizes,
    pi.cdn_url as primary_image_url
FROM products p
LEFT JOIN product_analysis pa ON p.id = pa.product_id
LEFT JOIN product_tags pt ON p.id = pt.product_id
LEFT JOIN tags t ON pt.tag_id = t.id
LEFT JOIN product_categories pc ON p.id = pc.product_id
LEFT JOIN categories c ON pc.category_id = c.id
LEFT JOIN product_variants pv ON p.id = pv.product_id
LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true
GROUP BY p.id, p.handle, p.title, p.description, p.collection, p.status, p.published,
         pa.primary_mood, pa.secondary_mood, pa.art_movement, pa.color_temperature,
         pa.dominant_colors, pa.recommended_rooms, pa.ai_confidence_score, pi.cdn_url;

COMMENT ON TABLE products IS 'Core product information for VividWalls artwork';
COMMENT ON TABLE product_analysis IS 'AI-generated analysis and classification of artwork';
COMMENT ON TABLE product_embeddings IS 'Vector embeddings for semantic similarity search';
COMMENT ON TABLE tags IS 'Master tag system for product categorization';
COMMENT ON TABLE product_tags IS 'Many-to-many relationship between products and tags';
COMMENT ON VIEW product_details_view IS 'Comprehensive view combining product, analysis, and tag data'; 