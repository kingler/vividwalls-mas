# VividWalls Product Image Classification & Tagging Workflow

## **N8N Workflow Architecture: AI-Powered Product Processing Pipeline**

This workflow processes VividWalls product images from Shopify, performs AI-powered classification and tagging, stores optimized images in Digital Ocean storage, and creates comprehensive database records with vector embeddings in Supabase for the art recommendation system.

## **Workflow Overview**

### **Core Processing Pipeline**
1. **CSV Data Ingestion** - Process product CSV with Shopify image URLs
2. **Image Download & Optimization** - Fetch and optimize images for storage
3. **AI Image Analysis** - VividWalls AI classification and tagging
4. **Digital Ocean Storage** - Store optimized images with CDN access
5. **Supabase Integration** - Relational data + vector embeddings
6. **Quality Validation** - Ensure data integrity and completeness

## **Data Structure Analysis**

### **CSV Fields Available**
```
Handle, Title, Body (HTML), Vendor, Product Category, Type, Tags, Published,
Option1 Name, Option1 Value (Frame Size), Option2 Name, Option2 Value (Frame Color),
Option3 Name, Option3 Value (Frame Style), Variant SKU, Variant Price,
Image Src, Image Position, Image Alt Text, Status
```

### **Key Product Attributes**
- **Artwork Collections**: Chromatic Echoes, Resonant Structure, Intersecting Spaces
- **Frame Sizes**: 53x72, 36x48, 24x36, 72x53, 48x36, 36x24
- **Frame Colors**: Black, White, NA (No Frame)
- **Frame Styles**: Thin Floating Frame, No Frame, NA
- **Pricing**: $400-$1200 based on size
- **Image URLs**: High-quality Shopify CDN images

## **Detailed Workflow Implementation**

### **Phase 1: Data Ingestion & Preprocessing**

#### **Node 1: CSV File Reader**
```json
{
  "node_type": "csv_reader",
  "file_path": "/data/shared/products/vividwalls-products-list-2-23-2025.csv",
  "delimiter": ",",
  "headers": true,
  "encoding": "utf-8"
}
```

#### **Node 2: Data Preprocessing & Deduplication**
```javascript
// Control Node - Process and deduplicate product data
const preprocessProductData = (csvData) => {
  const products = new Map();
  
  csvData.forEach(row => {
    const handle = row.Handle;
    
    if (!products.has(handle)) {
      // Create base product record
      products.set(handle, {
        handle: handle,
        title: row.Title,
        description: row['Body (HTML)'],
        vendor: row.Vendor,
        category: row['Product Category'],
        type: row.Type,
        tags: row.Tags,
        collection: row.Tags, // Extract collection from tags
        published: row.Published === 'TRUE',
        status: row.Status,
        variants: [],
        images: []
      });
    }
    
    // Add variant information
    const product = products.get(handle);
    if (row['Image Src']) {
      product.variants.push({
        sku: row['Variant SKU'],
        frame_size: row['Option1 Value'],
        frame_color: row['Option2 Value'],
        frame_style: row['Option3 Value'],
        price: parseFloat(row['Variant Price']),
        image_url: row['Image Src'],
        image_position: parseInt(row['Image Position']),
        image_alt: row['Image Alt Text']
      });
    }
  });
  
  return Array.from(products.values());
};
```

#### **Node 3: Image URL Validation & Prioritization**
```javascript
// Control Node - Validate and prioritize images for processing
const prioritizeImages = (products) => {
  const imageQueue = [];
  
  products.forEach(product => {
    // Get the primary image (position 1, no frame for AI analysis)
    const primaryImage = product.variants.find(v => 
      v.image_position === 1 && 
      (v.frame_color === 'NA' || v.frame_style === 'No Frame')
    );
    
    if (primaryImage) {
      imageQueue.push({
        product_handle: product.handle,
        product_title: product.title,
        collection: extractCollection(product.tags),
        image_url: primaryImage.image_url,
        priority: 'primary',
        analysis_type: 'full' // Full AI analysis for primary images
      });
    }
    
    // Add other variants for storage only
    product.variants.forEach(variant => {
      if (variant !== primaryImage) {
        imageQueue.push({
          product_handle: product.handle,
          product_title: product.title,
          collection: extractCollection(product.tags),
          image_url: variant.image_url,
          variant_info: {
            frame_size: variant.frame_size,
            frame_color: variant.frame_color,
            frame_style: variant.frame_style,
            price: variant.price
          },
          priority: 'variant',
          analysis_type: 'basic' // Basic processing for variants
        });
      }
    });
  });
  
  return imageQueue.sort((a, b) => a.priority === 'primary' ? -1 : 1);
};

const extractCollection = (tags) => {
  const collections = ['Chromatic Echoes', 'Resonant Structure', 'Intersecting Spaces'];
  return collections.find(col => tags.includes(col)) || 'Unknown';
};
```

### **Phase 2: Image Download & Processing**

#### **Node 4: Image Download Manager**
```javascript
// Tool Node - Download images with retry logic
const downloadImage = async (imageUrl, productHandle) => {
  const maxRetries = 3;
  let attempt = 0;
  
  while (attempt < maxRetries) {
    try {
      const response = await fetch(imageUrl, {
        headers: {
          'User-Agent': 'VividWalls-ImageProcessor/1.0'
        },
        timeout: 30000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const buffer = await response.buffer();
      const contentType = response.headers.get('content-type');
      
      return {
        buffer: buffer,
        contentType: contentType,
        size: buffer.length,
        originalUrl: imageUrl,
        downloadedAt: new Date().toISOString()
      };
      
    } catch (error) {
      attempt++;
      if (attempt >= maxRetries) {
        throw new Error(`Failed to download image after ${maxRetries} attempts: ${error.message}`);
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
};
```

#### **Node 5: Image Optimization & Format Conversion**
```javascript
// Tool Node - Optimize images for storage and analysis
const optimizeImage = async (imageBuffer, options = {}) => {
  const sharp = require('sharp');
  
  const {
    maxWidth = 2048,
    maxHeight = 2048,
    quality = 85,
    format = 'webp'
  } = options;
  
  try {
    // Get image metadata
    const metadata = await sharp(imageBuffer).metadata();
    
    // Create optimized version for storage
    const optimizedBuffer = await sharp(imageBuffer)
      .resize(maxWidth, maxHeight, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .webp({ quality: quality })
      .toBuffer();
    
    // Create thumbnail for quick loading
    const thumbnailBuffer = await sharp(imageBuffer)
      .resize(400, 400, {
        fit: 'cover',
        position: 'center'
      })
      .webp({ quality: 80 })
      .toBuffer();
    
    // Create analysis version (RGB, no transparency)
    const analysisBuffer = await sharp(imageBuffer)
      .resize(1024, 1024, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .removeAlpha()
      .jpeg({ quality: 90 })
      .toBuffer();
    
    return {
      original: {
        buffer: imageBuffer,
        width: metadata.width,
        height: metadata.height,
        format: metadata.format,
        size: imageBuffer.length
      },
      optimized: {
        buffer: optimizedBuffer,
        format: 'webp',
        size: optimizedBuffer.length
      },
      thumbnail: {
        buffer: thumbnailBuffer,
        format: 'webp',
        size: thumbnailBuffer.length
      },
      analysis: {
        buffer: analysisBuffer,
        format: 'jpeg',
        size: analysisBuffer.length
      }
    };
    
  } catch (error) {
    throw new Error(`Image optimization failed: ${error.message}`);
  }
};
```

### **Phase 3: AI-Powered Image Analysis**

#### **Node 6: VividWalls AI Image Classifier**
```json
{
  "node_type": "llm_agent",
  "model": "gpt-4-vision-preview",
  "system_prompt": "You are VividWalls AI, an expert art analyst specializing in abstract and geometric artwork classification. Analyze artwork images to extract detailed visual, stylistic, and psychological characteristics for the VividWalls recommendation system.",
  "conditional_execution": "item.analysis_type === 'full'"
}
```

**VividWalls AI Classification Prompt:**
```
You are VividWalls AI analyzing this artwork image for comprehensive classification and tagging.

ARTWORK CONTEXT:
- Product: {{product_title}}
- Collection: {{collection}}
- Handle: {{product_handle}}

COMPREHENSIVE ANALYSIS REQUIRED:

COLOR ANALYSIS:
- Primary colors (3-5 dominant colors with hex codes)
- Secondary colors (2-3 accent colors with hex codes)
- Color temperature (warm/cool/neutral with percentage breakdown)
- Color harmony type (complementary, analogous, triadic, monochromatic, split-complementary)
- Saturation level (high/medium/low)
- Brightness level (bright/medium/dark)

STYLE CLASSIFICATION:
- Art movement (Abstract, Geometric, Minimalist, Op Art, etc.)
- Composition type (Symmetrical, Asymmetrical, Radial, Grid-based)
- Visual complexity (Simple, Moderate, Complex)
- Texture appearance (Smooth, Textured, Mixed)
- Depth perception (Flat, Layered, Three-dimensional)

MOOD & PSYCHOLOGICAL IMPACT:
- Primary mood classification (energizing, calming, sophisticated, playful, mysterious, natural, romantic, dramatic)
- Secondary mood influences
- Emotional associations (list 3-5 emotions the artwork evokes)
- Psychological benefits (stress reduction, energy boost, focus enhancement, creativity stimulation)
- Target audience suitability (professional, residential, commercial, healthcare, hospitality)

GEOMETRIC ANALYSIS:
- Shape types present (circles, triangles, rectangles, organic forms, etc.)
- Pattern recognition (repetitive, random, structured, flowing)
- Symmetry analysis (perfect, approximate, asymmetrical)
- Scale relationships (uniform, varied, hierarchical)
- Movement suggestion (static, dynamic, flowing, angular)

TECHNICAL CHARACTERISTICS:
- Image quality score (1-10)
- Clarity and sharpness
- Color accuracy and vibrancy
- Composition balance
- Visual impact strength (1-10)

SPACE SUITABILITY:
- Recommended room types (bedroom, living room, office, etc.)
- Size recommendations (small, medium, large spaces)
- Lighting compatibility (natural, artificial, mixed)
- Style compatibility (modern, traditional, eclectic, minimalist)
- Commercial vs residential suitability

SEARCH TAGS:
Generate 15-20 relevant tags for search and filtering:
- Style tags (e.g., "geometric", "abstract", "minimalist")
- Color tags (e.g., "blue-dominant", "warm-tones", "monochromatic")
- Mood tags (e.g., "calming", "energizing", "sophisticated")
- Space tags (e.g., "office-suitable", "bedroom-art", "large-wall")
- Collection-specific tags

OUTPUT FORMAT:
Provide structured JSON with all analysis data for database storage and vector embedding generation.
```

#### **Node 7: Color Extraction & Analysis**
```javascript
// Tool Node - Extract precise color information
const extractColors = async (imageBuffer) => {
  const sharp = require('sharp');
  const ColorThief = require('colorthief');
  
  try {
    // Convert to RGB for color analysis
    const rgbBuffer = await sharp(imageBuffer)
      .resize(400, 400)
      .removeAlpha()
      .raw()
      .toBuffer();
    
    // Extract dominant colors
    const palette = await ColorThief.getPalette(rgbBuffer, 8);
    const dominantColor = await ColorThief.getColor(rgbBuffer);
    
    // Convert RGB to hex and analyze
    const colors = palette.map(rgb => ({
      hex: rgbToHex(rgb[0], rgb[1], rgb[2]),
      rgb: { r: rgb[0], g: rgb[1], b: rgb[2] },
      hsl: rgbToHsl(rgb[0], rgb[1], rgb[2]),
      temperature: getColorTemperature(rgb[0], rgb[1], rgb[2]),
      saturation: getSaturation(rgb[0], rgb[1], rgb[2]),
      brightness: getBrightness(rgb[0], rgb[1], rgb[2])
    }));
    
    return {
      dominant_color: {
        hex: rgbToHex(dominantColor[0], dominantColor[1], dominantColor[2]),
        rgb: { r: dominantColor[0], g: dominantColor[1], b: dominantColor[2] }
      },
      color_palette: colors,
      color_analysis: {
        temperature_distribution: analyzeTemperatureDistribution(colors),
        saturation_level: calculateAverageSaturation(colors),
        brightness_level: calculateAverageBrightness(colors),
        color_harmony: determineColorHarmony(colors)
      }
    };
    
  } catch (error) {
    throw new Error(`Color extraction failed: ${error.message}`);
  }
};

// Helper functions for color analysis
const rgbToHex = (r, g, b) => "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
const getColorTemperature = (r, g, b) => (r + g/2) > (b + g/2) ? 'warm' : 'cool';
// ... additional color analysis functions
```

### **Phase 4: Digital Ocean Storage Integration**

#### **Node 8: Digital Ocean Spaces Upload**
```javascript
// Tool Node - Upload images to Digital Ocean Spaces
const uploadToDigitalOcean = async (imageData, productHandle, imageType) => {
  const AWS = require('aws-sdk');
  
  // Configure Digital Ocean Spaces (S3-compatible)
  const spacesEndpoint = new AWS.Endpoint(process.env.DO_SPACES_ENDPOINT);
  const s3 = new AWS.S3({
    endpoint: spacesEndpoint,
    accessKeyId: process.env.DO_SPACES_KEY,
    secretAccessKey: process.env.DO_SPACES_SECRET,
    region: process.env.DO_SPACES_REGION
  });
  
  const bucketName = process.env.DO_SPACES_BUCKET;
  const timestamp = new Date().toISOString().split('T')[0];
  
  try {
    const uploads = [];
    
    // Upload optimized image
    if (imageData.optimized) {
      const optimizedKey = `products/${timestamp}/${productHandle}/${imageType}_optimized.webp`;
      const optimizedUpload = await s3.upload({
        Bucket: bucketName,
        Key: optimizedKey,
        Body: imageData.optimized.buffer,
        ContentType: 'image/webp',
        ACL: 'public-read',
        CacheControl: 'max-age=31536000', // 1 year cache
        Metadata: {
          'product-handle': productHandle,
          'image-type': imageType,
          'processed-at': new Date().toISOString()
        }
      }).promise();
      
      uploads.push({
        type: 'optimized',
        url: optimizedUpload.Location,
        key: optimizedKey,
        size: imageData.optimized.size
      });
    }
    
    // Upload thumbnail
    if (imageData.thumbnail) {
      const thumbnailKey = `products/${timestamp}/${productHandle}/${imageType}_thumbnail.webp`;
      const thumbnailUpload = await s3.upload({
        Bucket: bucketName,
        Key: thumbnailKey,
        Body: imageData.thumbnail.buffer,
        ContentType: 'image/webp',
        ACL: 'public-read',
        CacheControl: 'max-age=31536000'
      }).promise();
      
      uploads.push({
        type: 'thumbnail',
        url: thumbnailUpload.Location,
        key: thumbnailKey,
        size: imageData.thumbnail.size
      });
    }
    
    // Upload analysis version (for AI processing)
    if (imageData.analysis) {
      const analysisKey = `products/${timestamp}/${productHandle}/${imageType}_analysis.jpg`;
      const analysisUpload = await s3.upload({
        Bucket: bucketName,
        Key: analysisKey,
        Body: imageData.analysis.buffer,
        ContentType: 'image/jpeg',
        ACL: 'private', // Keep analysis images private
        Metadata: {
          'purpose': 'ai-analysis',
          'product-handle': productHandle
        }
      }).promise();
      
      uploads.push({
        type: 'analysis',
        url: analysisUpload.Location,
        key: analysisKey,
        size: imageData.analysis.size
      });
    }
    
    return {
      success: true,
      uploads: uploads,
      cdn_base_url: `https://${bucketName}.${process.env.DO_SPACES_REGION}.cdn.digitaloceanspaces.com`,
      uploaded_at: new Date().toISOString()
    };
    
  } catch (error) {
    throw new Error(`Digital Ocean upload failed: ${error.message}`);
  }
};
```

### **Phase 5: Supabase Database Integration**

#### **Node 9: Supabase Product Records Creation**
```javascript
// Tool Node - Create comprehensive product records in Supabase
const createSupabaseRecords = async (productData, analysisData, storageData) => {
  const { createClient } = require('@supabase/supabase-js');
  
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );
  
  try {
    // 1. Insert/Update main product record
    const { data: product, error: productError } = await supabase
      .from('products')
      .upsert({
        handle: productData.handle,
        title: productData.title,
        description: productData.description,
        vendor: productData.vendor,
        category: productData.category,
        type: productData.type,
        collection: productData.collection,
        published: productData.published,
        status: productData.status,
        tags: productData.tags,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'handle'
      })
      .select()
      .single();
    
    if (productError) throw productError;
    
    // 2. Insert product variants
    const variantInserts = productData.variants.map(variant => ({
      product_id: product.id,
      sku: variant.sku,
      frame_size: variant.frame_size,
      frame_color: variant.frame_color,
      frame_style: variant.frame_style,
      price: variant.price,
      shopify_image_url: variant.image_url,
      image_position: variant.image_position,
      image_alt: variant.image_alt
    }));
    
    const { data: variants, error: variantError } = await supabase
      .from('product_variants')
      .upsert(variantInserts, {
        onConflict: 'sku'
      })
      .select();
    
    if (variantError) throw variantError;
    
    // 3. Insert AI analysis data
    if (analysisData) {
      const { data: analysis, error: analysisError } = await supabase
        .from('product_analysis')
        .upsert({
          product_id: product.id,
          color_analysis: analysisData.color_analysis,
          style_classification: analysisData.style_classification,
          mood_analysis: analysisData.mood_analysis,
          geometric_analysis: analysisData.geometric_analysis,
          technical_characteristics: analysisData.technical_characteristics,
          space_suitability: analysisData.space_suitability,
          search_tags: analysisData.search_tags,
          ai_confidence_score: analysisData.confidence_score,
          analyzed_at: new Date().toISOString()
        }, {
          onConflict: 'product_id'
        })
        .select()
        .single();
      
      if (analysisError) throw analysisError;
    }
    
    // 4. Insert image storage records
    if (storageData && storageData.uploads) {
      const imageInserts = storageData.uploads.map(upload => ({
        product_id: product.id,
        image_type: upload.type,
        storage_url: upload.url,
        storage_key: upload.key,
        file_size: upload.size,
        cdn_url: `${storageData.cdn_base_url}/${upload.key}`,
        uploaded_at: storageData.uploaded_at
      }));
      
      const { data: images, error: imageError } = await supabase
        .from('product_images')
        .upsert(imageInserts, {
          onConflict: 'product_id,image_type'
        })
        .select();
      
      if (imageError) throw imageError;
    }
    
    return {
      success: true,
      product_id: product.id,
      variants_created: variants.length,
      analysis_created: !!analysisData,
      images_created: storageData?.uploads?.length || 0
    };
    
  } catch (error) {
    throw new Error(`Supabase record creation failed: ${error.message}`);
  }
};
```

#### **Node 10: Vector Embedding Generation**
```javascript
// Tool Node - Generate and store vector embeddings for similarity search
const generateVectorEmbeddings = async (productId, analysisData) => {
  const { createClient } = require('@supabase/supabase-js');
  const OpenAI = require('openai');
  
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );
  
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });
  
  try {
    // Create comprehensive text representation for embedding
    const embeddingText = createEmbeddingText(analysisData);
    
    // Generate embedding using OpenAI
    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-large",
      input: embeddingText,
      dimensions: 1536
    });
    
    const embedding = embeddingResponse.data[0].embedding;
    
    // Store embedding in Supabase vector table
    const { data, error } = await supabase
      .from('product_embeddings')
      .upsert({
        product_id: productId,
        embedding: embedding,
        embedding_text: embeddingText,
        model_used: "text-embedding-3-large",
        dimensions: 1536,
        created_at: new Date().toISOString()
      }, {
        onConflict: 'product_id'
      })
      .select()
      .single();
    
    if (error) throw error;
    
    return {
      success: true,
      embedding_id: data.id,
      dimensions: embedding.length,
      text_length: embeddingText.length
    };
    
  } catch (error) {
    throw new Error(`Vector embedding generation failed: ${error.message}`);
  }
};

const createEmbeddingText = (analysisData) => {
  const {
    color_analysis,
    style_classification,
    mood_analysis,
    space_suitability,
    search_tags
  } = analysisData;
  
  return [
    // Color information
    `Colors: ${color_analysis.primary_colors.join(', ')}`,
    `Color temperature: ${color_analysis.temperature}`,
    `Color harmony: ${color_analysis.harmony_type}`,
    
    // Style information
    `Art style: ${style_classification.movement}`,
    `Composition: ${style_classification.composition_type}`,
    `Complexity: ${style_classification.complexity}`,
    
    // Mood and psychological impact
    `Primary mood: ${mood_analysis.primary_mood}`,
    `Emotional associations: ${mood_analysis.emotions.join(', ')}`,
    `Psychological benefits: ${mood_analysis.benefits.join(', ')}`,
    
    // Space suitability
    `Suitable for: ${space_suitability.room_types.join(', ')}`,
    `Space size: ${space_suitability.size_recommendations.join(', ')}`,
    `Style compatibility: ${space_suitability.style_compatibility.join(', ')}`,
    
    // Search tags
    `Tags: ${search_tags.join(', ')}`
  ].join('. ');
};
```

### **Phase 6: Quality Validation & Error Handling**

#### **Node 11: Data Quality Validator**
```javascript
// Guardrail Node - Validate processed data quality
const validateDataQuality = (productData, analysisData, storageData) => {
  const validation = {
    product_data_complete: validateProductData(productData),
    analysis_data_quality: validateAnalysisData(analysisData),
    storage_data_integrity: validateStorageData(storageData),
    overall_score: 0
  };
  
  // Calculate overall quality score
  const scores = Object.values(validation).filter(v => typeof v === 'object' && v.score);
  validation.overall_score = scores.reduce((sum, v) => sum + v.score, 0) / scores.length;
  
  // Fail if overall score is too low
  if (validation.overall_score < 7.0) {
    throw new Error(`Data quality too low: ${validation.overall_score}/10`);
  }
  
  return validation;
};

const validateProductData = (data) => {
  const checks = {
    has_title: !!data.title,
    has_description: !!data.description && data.description.length > 50,
    has_collection: !!data.collection && data.collection !== 'Unknown',
    has_variants: data.variants && data.variants.length > 0,
    has_pricing: data.variants.every(v => v.price > 0)
  };
  
  const score = Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 10;
  
  return { checks, score, passed: score >= 8.0 };
};

const validateAnalysisData = (data) => {
  if (!data) return { score: 0, passed: false, reason: 'No analysis data' };
  
  const checks = {
    has_colors: data.color_analysis && data.color_analysis.primary_colors.length >= 3,
    has_style: data.style_classification && data.style_classification.movement,
    has_mood: data.mood_analysis && data.mood_analysis.primary_mood,
    has_tags: data.search_tags && data.search_tags.length >= 10,
    confidence_high: data.confidence_score >= 7.0
  };
  
  const score = Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 10;
  
  return { checks, score, passed: score >= 8.0 };
};

const validateStorageData = (data) => {
  if (!data || !data.uploads) return { score: 0, passed: false, reason: 'No storage data' };
  
  const checks = {
    has_optimized: data.uploads.some(u => u.type === 'optimized'),
    has_thumbnail: data.uploads.some(u => u.type === 'thumbnail'),
    all_uploaded: data.uploads.every(u => u.url && u.url.startsWith('https')),
    reasonable_sizes: data.uploads.every(u => u.size > 1000 && u.size < 10000000)
  };
  
  const score = Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 10;
  
  return { checks, score, passed: score >= 9.0 };
};
```

#### **Node 12: Error Recovery & Retry Logic**
```javascript
// Fallback Node - Handle errors and implement retry strategies
const handleProcessingErrors = async (error, context, retryCount = 0) => {
  const maxRetries = 3;
  const retryableErrors = [
    'network timeout',
    'rate limit',
    'temporary unavailable',
    'connection reset'
  ];
  
  const isRetryable = retryableErrors.some(err => 
    error.message.toLowerCase().includes(err)
  );
  
  if (isRetryable && retryCount < maxRetries) {
    // Exponential backoff
    const delay = Math.pow(2, retryCount) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return {
      action: 'retry',
      delay: delay,
      attempt: retryCount + 1,
      reason: error.message
    };
  }
  
  // Log error for manual review
  await logProcessingError(error, context);
  
  // Determine fallback action
  const fallbackActions = {
    'image_download_failed': 'skip_image',
    'ai_analysis_failed': 'use_basic_tags',
    'storage_upload_failed': 'use_shopify_urls',
    'database_insert_failed': 'queue_for_retry'
  };
  
  const errorType = determineErrorType(error);
  const action = fallbackActions[errorType] || 'manual_review';
  
  return {
    action: action,
    error_type: errorType,
    original_error: error.message,
    context: context,
    requires_manual_review: action === 'manual_review'
  };
};

const logProcessingError = async (error, context) => {
  // Log to monitoring system and database
  console.error('Product processing error:', {
    error: error.message,
    context: context,
    timestamp: new Date().toISOString(),
    stack: error.stack
  });
};
```

### **Phase 7: Batch Processing & Progress Tracking**

#### **Node 13: Batch Processing Controller**
```javascript
// Control Node - Manage batch processing with progress tracking
const processBatch = async (products, batchSize = 5) => {
  const results = {
    total: products.length,
    processed: 0,
    successful: 0,
    failed: 0,
    errors: [],
    start_time: new Date().toISOString()
  };
  
  // Process in batches to avoid overwhelming APIs
  for (let i = 0; i < products.length; i += batchSize) {
    const batch = products.slice(i, i + batchSize);
    
    // Process batch in parallel
    const batchPromises = batch.map(async (product, index) => {
      try {
        const result = await processProduct(product);
        results.successful++;
        return { success: true, product: product.handle, result };
      } catch (error) {
        results.failed++;
        results.errors.push({
          product: product.handle,
          error: error.message,
          timestamp: new Date().toISOString()
        });
        return { success: false, product: product.handle, error: error.message };
      } finally {
        results.processed++;
        
        // Update progress
        const progress = (results.processed / results.total) * 100;
        console.log(`Progress: ${progress.toFixed(1)}% (${results.processed}/${results.total})`);
      }
    });
    
    await Promise.all(batchPromises);
    
    // Rate limiting - pause between batches
    if (i + batchSize < products.length) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  results.end_time = new Date().toISOString();
  results.duration_seconds = (new Date(results.end_time) - new Date(results.start_time)) / 1000;
  
  return results;
};
```

## **Database Schema Design**

### **Supabase Tables**

#### **Products Table**
```sql
CREATE TABLE products (
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
```

#### **Product Analysis Table**
```sql
CREATE TABLE product_analysis (
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
```

#### **Product Embeddings Table**
```sql
CREATE TABLE product_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  embedding VECTOR(1536),
  embedding_text TEXT,
  model_used VARCHAR(100),
  dimensions INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(product_id)
);

-- Create vector similarity search index
CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops);
```

#### **Product Images Table**
```sql
CREATE TABLE product_images (
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
```

#### **Product Variants Table**
```sql
CREATE TABLE product_variants (
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
```

## **MCP Tool Definitions**

### **Product Database Tools**

```typescript
// MCP Tool: get_image_by_color (Enhanced for product database)
interface GetImageByColorParams {
  primary_colors: string[];              // Hex color codes
  secondary_colors?: string[];           // Optional accent colors
  color_harmony: 'complementary' | 'analogous' | 'triadic' | 'monochromatic' | 'split_complementary';
  color_temperature: 'warm' | 'cool' | 'neutral';
  saturation_level: 'high' | 'medium' | 'low';
  limit?: number;                       // Default: 20
}

// MCP Tool: get_image_by_mood (Enhanced for product database)
interface GetImageByMoodParams {
  primary_mood: 'energizing' | 'calming' | 'sophisticated' | 'playful' | 'mysterious' | 'natural' | 'romantic' | 'dramatic';
  secondary_moods?: string[];           // Additional mood influences
  emotional_associations: string[];     // Specific emotions
  psychological_benefits: string[];     // Desired psychological effects
  target_audience: 'residential' | 'commercial' | 'healthcare' | 'hospitality';
  limit?: number;                      // Default: 20
}

// MCP Tool: get_image_by_size (Enhanced for product database)
interface GetImageBySizeParams {
  frame_sizes: string[];               // Available frame sizes
  space_size: 'small' | 'medium' | 'large';
  room_type: string;                   // Specific room type
  wall_space_available: {              // Available wall dimensions
    width: number;
    height: number;
  };
  viewing_distance: number;            // Optimal viewing distance
  limit?: number;                     // Default: 20
}

// MCP Tool: search_products_by_vector
interface SearchProductsByVectorParams {
  query_text: string;                  // Natural language query
  similarity_threshold: number;       // Minimum similarity score (0-1)
  limit?: number;                     // Default: 10
  filters?: {                         // Optional filters
    collection?: string;
    price_range?: { min: number; max: number; };
    frame_colors?: string[];
    published_only?: boolean;
  };
}
```

## **Workflow Configuration**

### **Environment Variables**
```bash
# Digital Ocean Spaces Configuration
DO_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=vividwalls-products
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_ANON_KEY=your_anon_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL_VISION=gpt-4-vision-preview
OPENAI_MODEL_EMBEDDING=text-embedding-3-large

# Processing Configuration
BATCH_SIZE=5
MAX_RETRIES=3
RATE_LIMIT_DELAY=2000
IMAGE_QUALITY=85
MAX_IMAGE_SIZE=2048
```

### **Workflow Execution Flow**
```
CSV Import → Data Preprocessing → Image Download → 
Image Optimization → AI Analysis → Color Extraction → 
Digital Ocean Upload → Supabase Records → Vector Embeddings → 
Quality Validation → Batch Processing → Progress Reporting
```

### **Performance Optimizations**
- **Parallel Processing**: Images processed in batches of 5
- **Rate Limiting**: 2-second delays between batches
- **Caching**: Optimized images cached with 1-year expiry
- **CDN Integration**: Digital Ocean Spaces CDN for fast delivery
- **Vector Indexing**: Optimized similarity search with ivfflat index

This comprehensive workflow will transform your Shopify product CSV into a fully-featured, AI-powered product database with vector search capabilities, optimized image storage, and detailed classification data for the VividWalls recommendation system. 