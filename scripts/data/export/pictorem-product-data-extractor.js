#!/usr/bin/env node

/**
 * Pictorem Product Data Extractor
 * 
 * This tool extracts comprehensive product configuration data from Pictorem
 * including dimensions, floating frame options, canvas types, and stretcher bar specs
 * for storage in VividWalls database to align product offerings.
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

class PictoremProductDataExtractor {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.isAuthenticated = false;
        this.siteMapping = null;
        this.productData = {
            metadata: {
                extracted_date: new Date().toISOString(),
                site_url: 'https://www.pictorem.com',
                extractor_version: '1.0.0'
            },
            dimensions: {
                canvas_sizes: [],
                custom_size_limits: {},
                aspect_ratios: []
            },
            floating_frames: {
                available_sizes: [],
                colors: [],
                materials: [],
                thickness_options: []
            },
            printing_surfaces: {
                canvas_types: [],
                canvas_weights: [],
                canvas_textures: []
            },
            stretcher_bars: {
                depths: [],
                wood_types: [],
                corner_reinforcement: []
            },
            pricing_tiers: [],
            size_categories: [],
            shipping_options: []
        };
    }

    async initialize() {
        console.log('🎨 Initializing Pictorem Product Data Extractor...');
        
        // Load site mapping if it exists
        try {
            const mappingPath = path.join(process.cwd(), '..', 'mcp', 'pictorem-mcp-server', 'mapping', 'pictorem-site-mapping.json');
            if (fs.existsSync(mappingPath)) {
                this.siteMapping = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));
                console.log('✅ Loaded existing site mapping');
            } else {
                console.log('⚠️ No site mapping found, will use default selectors');
                this.siteMapping = this.getDefaultSiteMapping();
            }
        } catch (error) {
            console.log('⚠️ Failed to load site mapping, using defaults');
            this.siteMapping = this.getDefaultSiteMapping();
        }
        
        this.browser = await chromium.launch({ 
            headless: false, // Keep visible for data extraction
            slowMo: 300 
        });
        
        this.context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        });
        
        this.page = await this.context.newPage();
        this.page.setDefaultTimeout(30000);
        
        // Enable logging
        this.page.on('console', msg => console.log('🔍 Browser:', msg.text()));
    }

    getDefaultSiteMapping() {
        return {
            authentication: {
                login_url: 'https://www.pictorem.com/myaccount.html',
                email_field: 'input[name="email"]',
                password_field: 'input[type="password"]',
                submit_button: 'input[type="submit"]'
            },
            product_configuration: {
                width_selector: 'select[name="width"]',
                height_selector: 'select[name="height"]'
            }
        };
    }

    async authenticate() {
        if (!this.page) throw new Error('Browser not initialized');

        try {
            console.log('🔐 Authenticating with Pictorem...');
            
            // Use saved authentication selectors
            await this.page.goto(this.siteMapping.authentication.login_url);
            await this.page.waitForTimeout(2000);
            
            await this.page.fill(this.siteMapping.authentication.email_field, process.env.PICTOREM_USERNAME || '');
            await this.page.fill(this.siteMapping.authentication.password_field, process.env.PICTOREM_PASSWORD || '');
            await this.page.click(this.siteMapping.authentication.submit_button);
            
            await this.page.waitForTimeout(3000);
            
            const currentUrl = this.page.url();
            this.isAuthenticated = currentUrl.includes('myaccount') || currentUrl.includes('account');
            
            console.log(`✅ Authentication ${this.isAuthenticated ? 'successful' : 'failed'}`);
            return this.isAuthenticated;
            
        } catch (error) {
            console.error('❌ Authentication failed:', error);
            return false;
        }
    }

    async extractDimensionsData() {
        console.log('\n📐 Extracting Dimensions Data...');
        
        try {
            // Navigate to canvas print page to see size options
            await this.page.goto('https://www.pictorem.com/canvas-print.html');
            await this.page.waitForTimeout(3000);
            
            // Look for size information in the content
            const sizeInfo = await this.page.evaluate(() => {
                const sizeElements = document.querySelectorAll('*');
                const sizeData = [];
                
                for (const element of sizeElements) {
                    const text = element.textContent || '';
                    
                    // Look for dimension patterns like "24x36", "8x10 inches", etc.
                    const dimensionMatches = text.match(/(\d+)\s*[x×]\s*(\d+)\s*(inches?|in\.?|")?/gi);
                    if (dimensionMatches) {
                        dimensionMatches.forEach(match => {
                            const [width, height] = match.replace(/[^0-9x×]/g, '').split(/[x×]/);
                            if (width && height) {
                                sizeData.push({
                                    width: parseInt(width),
                                    height: parseInt(height),
                                    text: match.trim(),
                                    source_element: element.tagName.toLowerCase()
                                });
                            }
                        });
                    }
                    
                    // Look for size range information
                    const rangeMatches = text.match(/(\d+)\s*-\s*(\d+)\s*inches?/gi);
                    if (rangeMatches) {
                        rangeMatches.forEach(match => {
                            sizeData.push({
                                range: match.trim(),
                                type: 'size_range',
                                source_element: element.tagName.toLowerCase()
                            });
                        });
                    }
                }
                
                return sizeData;
            });
            
            // Navigate to order page to extract actual size selectors
            await this.page.goto('https://www.pictorem.com/order.html?hash=new&create=1&prod=canvas');
            await this.page.waitForTimeout(3000);
            
            // Extract width options
            const widthOptions = await this.extractSelectOptions(this.siteMapping.product_configuration.width_selector);
            const heightOptions = await this.extractSelectOptions(this.siteMapping.product_configuration.height_selector);
            
            this.productData.dimensions.canvas_sizes = this.generateCanvasSizes(widthOptions, heightOptions);
            this.productData.dimensions.width_options = widthOptions;
            this.productData.dimensions.height_options = heightOptions;
            this.productData.dimensions.size_patterns_found = sizeInfo;
            
            console.log(`✅ Found ${this.productData.dimensions.canvas_sizes.length} canvas size combinations`);
            console.log(`✅ Width options: ${widthOptions.length}, Height options: ${heightOptions.length}`);
            
        } catch (error) {
            console.error('❌ Dimension extraction failed:', error);
        }
    }

    async extractFloatingFrameData() {
        console.log('\n🖼️ Extracting Floating Frame Data...');
        
        try {
            // Navigate to canvas page and look for frame information
            await this.page.goto('https://www.pictorem.com/canvas-print.html');
            await this.page.waitForTimeout(3000);
            
            // Extract frame information from page content
            const frameInfo = await this.page.evaluate(() => {
                const frameData = {
                    colors: [],
                    sizes: [],
                    materials: [],
                    descriptions: []
                };
                
                // Look for frame-related text
                const allText = document.body.textContent || '';
                
                // Extract frame colors
                const colorMatches = allText.match(/(white|black|brown|natural|silver|gold|oak|walnut|cherry|mahogany|pine)\s+(frame|floating)/gi);
                if (colorMatches) {
                    colorMatches.forEach(match => {
                        const color = match.replace(/\s+(frame|floating)/gi, '').trim();
                        if (!frameData.colors.includes(color.toLowerCase())) {
                            frameData.colors.push(color.toLowerCase());
                        }
                    });
                }
                
                // Look for frame thickness/depth
                const thicknessMatches = allText.match(/(\d+(?:\.\d+)?)\s*(inch|in|mm|cm)\s+(thick|deep|depth|frame)/gi);
                if (thicknessMatches) {
                    frameData.sizes = thicknessMatches.map(match => match.trim());
                }
                
                // Look for material mentions
                const materialMatches = allText.match(/(wood|wooden|timber|pine|oak|maple|birch|poplar|mdf)\s*(frame|floating)?/gi);
                if (materialMatches) {
                    materialMatches.forEach(match => {
                        const material = match.replace(/\s*(frame|floating)/gi, '').trim();
                        if (!frameData.materials.includes(material.toLowerCase())) {
                            frameData.materials.push(material.toLowerCase());
                        }
                    });
                }
                
                return frameData;
            });
            
            // Try to navigate to a frame-specific page if it exists
            try {
                await this.page.goto('https://www.pictorem.com/floating-frame.html');
                await this.page.waitForTimeout(3000);
                
                const additionalFrameInfo = await this.page.evaluate(() => {
                    const frameSelectors = document.querySelectorAll('select, input[type="radio"], .frame-option, .color-option');
                    const frameData = [];
                    
                    frameSelectors.forEach(element => {
                        if (element.tagName === 'SELECT') {
                            const options = Array.from(element.options).map(opt => ({
                                value: opt.value,
                                text: opt.textContent.trim()
                            }));
                            frameData.push({
                                type: 'select',
                                name: element.name || element.id,
                                options: options
                            });
                        } else if (element.type === 'radio') {
                            frameData.push({
                                type: 'radio',
                                name: element.name,
                                value: element.value,
                                label: element.nextElementSibling?.textContent || ''
                            });
                        }
                    });
                    
                    return frameData;
                });
                
                this.productData.floating_frames.form_options = additionalFrameInfo;
                
            } catch (e) {
                console.log('⚠️ No dedicated frame page found, using canvas page data');
            }
            
            this.productData.floating_frames.colors = frameInfo.colors;
            this.productData.floating_frames.thickness_options = frameInfo.sizes;
            this.productData.floating_frames.materials = frameInfo.materials;
            
            console.log(`✅ Found ${frameInfo.colors.length} frame colors, ${frameInfo.materials.length} materials`);
            
        } catch (error) {
            console.error('❌ Frame extraction failed:', error);
        }
    }

    async extractCanvasData() {
        console.log('\n🎨 Extracting Canvas Surface Data...');
        
        try {
            await this.page.goto('https://www.pictorem.com/canvas-print.html');
            await this.page.waitForTimeout(3000);
            
            const canvasInfo = await this.page.evaluate(() => {
                const canvasData = {
                    types: [],
                    weights: [],
                    textures: [],
                    finishes: []
                };
                
                const allText = document.body.textContent || '';
                
                // Look for canvas types
                const typeMatches = allText.match(/(cotton|polyester|linen|hemp|bamboo|blend)\s+(canvas|fabric)/gi);
                if (typeMatches) {
                    typeMatches.forEach(match => {
                        const type = match.replace(/\s+(canvas|fabric)/gi, '').trim();
                        if (!canvasData.types.includes(type.toLowerCase())) {
                            canvasData.types.push(type.toLowerCase());
                        }
                    });
                }
                
                // Look for canvas weights (gsm, oz)
                const weightMatches = allText.match(/(\d+)\s*(gsm|oz|g\/m²|gram)/gi);
                if (weightMatches) {
                    canvasData.weights = weightMatches.map(match => match.trim());
                }
                
                // Look for canvas textures/finishes
                const textureMatches = allText.match(/(matte|satin|gloss|semi-gloss|textured|smooth|fine|medium|coarse)\s*(finish|canvas|texture)?/gi);
                if (textureMatches) {
                    textureMatches.forEach(match => {
                        const texture = match.replace(/\s*(finish|canvas|texture)/gi, '').trim();
                        if (!canvasData.finishes.includes(texture.toLowerCase())) {
                            canvasData.finishes.push(texture.toLowerCase());
                        }
                    });
                }
                
                return canvasData;
            });
            
            this.productData.printing_surfaces.canvas_types = canvasInfo.types;
            this.productData.printing_surfaces.canvas_weights = canvasInfo.weights;
            this.productData.printing_surfaces.canvas_textures = canvasInfo.finishes;
            
            console.log(`✅ Found ${canvasInfo.types.length} canvas types, ${canvasInfo.weights.length} weights`);
            
        } catch (error) {
            console.error('❌ Canvas extraction failed:', error);
        }
    }

    async extractStretcherBarData() {
        console.log('\n🪵 Extracting Stretcher Bar Data...');
        
        try {
            await this.page.goto('https://www.pictorem.com/canvas-print.html');
            await this.page.waitForTimeout(3000);
            
            const stretcherInfo = await this.page.evaluate(() => {
                const stretcherData = {
                    depths: [],
                    wood_types: [],
                    features: []
                };
                
                const allText = document.body.textContent || '';
                
                // Look for stretcher bar depths
                const depthMatches = allText.match(/(\d+(?:\.\d+)?)\s*(inch|in|mm|cm)\s+(deep|depth|stretcher|bar)/gi);
                if (depthMatches) {
                    stretcherData.depths = depthMatches.map(match => match.trim());
                }
                
                // Look for wood types for stretcher bars
                const woodMatches = allText.match(/(pine|fir|poplar|birch|maple|oak)\s*(stretcher|bar|frame|wood)?/gi);
                if (woodMatches) {
                    woodMatches.forEach(match => {
                        const wood = match.replace(/\s*(stretcher|bar|frame|wood)/gi, '').trim();
                        if (!stretcherData.wood_types.includes(wood.toLowerCase())) {
                            stretcherData.wood_types.push(wood.toLowerCase());
                        }
                    });
                }
                
                // Look for features
                const featureMatches = allText.match(/(corner\s+reinforcement|solid\s+wood|kiln\s+dried|gallery\s+wrap|museum\s+quality)/gi);
                if (featureMatches) {
                    stretcherData.features = featureMatches.map(match => match.trim().toLowerCase());
                }
                
                return stretcherData;
            });
            
            this.productData.stretcher_bars.depths = stretcherInfo.depths;
            this.productData.stretcher_bars.wood_types = stretcherInfo.wood_types;
            this.productData.stretcher_bars.corner_reinforcement = stretcherInfo.features;
            
            console.log(`✅ Found ${stretcherInfo.depths.length} depth options, ${stretcherInfo.wood_types.length} wood types`);
            
        } catch (error) {
            console.error('❌ Stretcher bar extraction failed:', error);
        }
    }

    async extractPricingData() {
        console.log('\n💰 Extracting Pricing Data...');
        
        try {
            // Navigate to order page and try different sizes to understand pricing
            await this.page.goto('https://www.pictorem.com/order.html?hash=new&create=1&prod=canvas');
            await this.page.waitForTimeout(3000);
            
            const pricingData = [];
            const testSizes = [
                { width: 8, height: 10 },
                { width: 12, height: 16 },
                { width: 16, height: 20 },
                { width: 24, height: 36 },
                { width: 30, height: 40 }
            ];
            
            for (const size of testSizes) {
                try {
                    // Set dimensions if selectors exist
                    const widthSelector = this.siteMapping.product_configuration.width_selector;
                    const heightSelector = this.siteMapping.product_configuration.height_selector;
                    
                    if (await this.page.locator(widthSelector).count() > 0) {
                        await this.page.selectOption(widthSelector, size.width.toString());
                    }
                    if (await this.page.locator(heightSelector).count() > 0) {
                        await this.page.selectOption(heightSelector, size.height.toString());
                    }
                    
                    await this.page.waitForTimeout(2000);
                    
                    // Try to extract price
                    const priceInfo = await this.page.evaluate((size) => {
                        const priceSelectors = [
                            '.price', '#price', '.total', '.cost', '.amount',
                            '[data-price]', '.price-display', '.product-price'
                        ];
                        
                        for (const selector of priceSelectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                const text = element.textContent || '';
                                const priceMatch = text.match(/\$(\d+(?:\.\d{2})?)/);
                                if (priceMatch) {
                                    return {
                                        size: size,
                                        price: parseFloat(priceMatch[1]),
                                        text: text.trim(),
                                        selector: selector
                                    };
                                }
                            }
                        }
                        return null;
                    }, size);
                    
                    if (priceInfo) {
                        pricingData.push(priceInfo);
                        console.log(`✅ ${size.width}x${size.height}: $${priceInfo.price}`);
                    }
                    
                } catch (e) {
                    console.log(`⚠️ Could not get pricing for ${size.width}x${size.height}`);
                }
            }
            
            this.productData.pricing_tiers = pricingData;
            
        } catch (error) {
            console.error('❌ Pricing extraction failed:', error);
        }
    }

    async extractSelectOptions(selector) {
        if (!selector || await this.page.locator(selector).count() === 0) {
            return [];
        }
        
        try {
            const options = await this.page.evaluate((sel) => {
                const selectElement = document.querySelector(sel);
                if (!selectElement) return [];
                
                return Array.from(selectElement.options)
                    .filter(opt => opt.value && opt.value !== '')
                    .map(opt => ({
                        value: opt.value,
                        text: opt.textContent.trim(),
                        numeric_value: parseInt(opt.value) || null
                    }));
            }, selector);
            
            return options;
        } catch (e) {
            return [];
        }
    }

    generateCanvasSizes(widthOptions, heightOptions) {
        const sizes = [];
        
        for (const width of widthOptions) {
            for (const height of heightOptions) {
                if (width.numeric_value && height.numeric_value) {
                    const squareInches = width.numeric_value * height.numeric_value;
                    const aspectRatio = width.numeric_value / height.numeric_value;
                    
                    sizes.push({
                        width: width.numeric_value,
                        height: height.numeric_value,
                        width_text: width.text,
                        height_text: height.text,
                        square_inches: squareInches,
                        aspect_ratio: Math.round(aspectRatio * 100) / 100,
                        size_category: this.categorizeSize(squareInches),
                        orientation: aspectRatio > 1 ? 'landscape' : aspectRatio < 1 ? 'portrait' : 'square'
                    });
                }
            }
        }
        
        return sizes.sort((a, b) => a.square_inches - b.square_inches);
    }

    categorizeSize(squareInches) {
        if (squareInches <= 100) return 'small';
        if (squareInches <= 400) return 'medium';
        if (squareInches <= 900) return 'large';
        return 'extra_large';
    }

    async saveProductData() {
        const outputDir = path.join(process.cwd(), 'data');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const outputFile = path.join(outputDir, 'pictorem-product-data.json');
        fs.writeFileSync(outputFile, JSON.stringify(this.productData, null, 2));
        
        console.log(`\n💾 Product data saved to: ${outputFile}`);
        
        // Also create a SQL schema file for database integration
        await this.generateDatabaseSchema(outputDir);
    }

    async generateDatabaseSchema(outputDir) {
        const sqlSchema = `-- Pictorem Product Data Schema for VividWalls Integration
-- Generated on ${new Date().toISOString()}

-- Canvas dimensions available on Pictorem
CREATE TABLE pictorem_canvas_sizes (
    id SERIAL PRIMARY KEY,
    width_inches INTEGER NOT NULL,
    height_inches INTEGER NOT NULL,
    square_inches INTEGER NOT NULL,
    aspect_ratio DECIMAL(4,2) NOT NULL,
    size_category VARCHAR(20) NOT NULL,
    orientation VARCHAR(10) NOT NULL,
    pictorem_width_value VARCHAR(10),
    pictorem_height_value VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Floating frame options
CREATE TABLE pictorem_floating_frames (
    id SERIAL PRIMARY KEY,
    color VARCHAR(50) NOT NULL,
    material VARCHAR(50),
    thickness_inches DECIMAL(3,2),
    thickness_description TEXT,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Canvas printing surfaces and specifications
CREATE TABLE pictorem_canvas_types (
    id SERIAL PRIMARY KEY,
    canvas_material VARCHAR(50) NOT NULL,
    weight_specification VARCHAR(20),
    texture_finish VARCHAR(50),
    description TEXT,
    recommended_for TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stretcher bar specifications
CREATE TABLE pictorem_stretcher_bars (
    id SERIAL PRIMARY KEY,
    depth_inches DECIMAL(3,2) NOT NULL,
    wood_type VARCHAR(50),
    features TEXT[],
    quality_grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pricing data for different sizes
CREATE TABLE pictorem_pricing_tiers (
    id SERIAL PRIMARY KEY,
    width_inches INTEGER NOT NULL,
    height_inches INTEGER NOT NULL,
    base_price DECIMAL(8,2) NOT NULL,
    price_per_square_inch DECIMAL(6,4),
    size_category VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VividWalls product mapping to Pictorem options
CREATE TABLE vividwalls_pictorem_mapping (
    id SERIAL PRIMARY KEY,
    vividwalls_product_id VARCHAR(50) NOT NULL,
    pictorem_canvas_size_id INTEGER REFERENCES pictorem_canvas_sizes(id),
    pictorem_frame_id INTEGER REFERENCES pictorem_floating_frames(id),
    pictorem_canvas_type_id INTEGER REFERENCES pictorem_canvas_types(id),
    pictorem_stretcher_bar_id INTEGER REFERENCES pictorem_stretcher_bars(id),
    vividwalls_price DECIMAL(8,2),
    pictorem_base_price DECIMAL(8,2),
    markup_percentage DECIMAL(5,2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Limited edition inventory tracking
CREATE TABLE vividwalls_limited_editions (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(100),
    total_edition_size INTEGER NOT NULL,
    remaining_count INTEGER NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    image_url TEXT,
    description TEXT,
    pictorem_mapping_id INTEGER REFERENCES vividwalls_pictorem_mapping(id),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order tracking between Shopify -> VividWalls -> Pictorem
CREATE TABLE order_fulfillment_tracking (
    id SERIAL PRIMARY KEY,
    shopify_order_id VARCHAR(50) NOT NULL,
    vividwalls_order_number VARCHAR(50) NOT NULL,
    pictorem_order_id VARCHAR(50),
    limited_edition_id INTEGER REFERENCES vividwalls_limited_editions(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    shopify_webhook_received TIMESTAMP,
    pictorem_order_submitted TIMESTAMP,
    pictorem_order_confirmed TIMESTAMP,
    estimated_delivery DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data based on extracted information
${this.generateSampleDataInserts()}
`;
        
        const schemaFile = path.join(outputDir, 'pictorem-product-schema.sql');
        fs.writeFileSync(schemaFile, sqlSchema);
        
        console.log(`📝 Database schema saved to: ${schemaFile}`);
    }

    generateSampleDataInserts() {
        let inserts = '\n-- Sample data inserts based on extracted product information\n';
        
        // Insert canvas sizes
        if (this.productData.dimensions.canvas_sizes.length > 0) {
            inserts += '\nINSERT INTO pictorem_canvas_sizes (width_inches, height_inches, square_inches, aspect_ratio, size_category, orientation, pictorem_width_value, pictorem_height_value) VALUES\n';
            const sizeInserts = this.productData.dimensions.canvas_sizes.slice(0, 10).map(size => 
                `(${size.width}, ${size.height}, ${size.square_inches}, ${size.aspect_ratio}, '${size.size_category}', '${size.orientation}', '${size.width}', '${size.height}')`
            ).join(',\n');
            inserts += sizeInserts + ';\n';
        }
        
        // Insert frame colors
        if (this.productData.floating_frames.colors.length > 0) {
            inserts += '\nINSERT INTO pictorem_floating_frames (color, material, available) VALUES\n';
            const frameInserts = this.productData.floating_frames.colors.map(color => 
                `('${color}', 'wood', TRUE)`
            ).join(',\n');
            inserts += frameInserts + ';\n';
        }
        
        return inserts;
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async runFullExtraction() {
        try {
            await this.initialize();
            
            console.log('🚀 Starting Comprehensive Pictorem Product Data Extraction...');
            console.log('📋 This will extract dimensions, frames, canvas types, and pricing data\n');
            
            // Authenticate first
            const authSuccess = await this.authenticate();
            if (!authSuccess) {
                throw new Error('Authentication required for complete data extraction');
            }
            
            // Extract all product data
            await this.extractDimensionsData();
            await this.extractFloatingFrameData();
            await this.extractCanvasData();
            await this.extractStretcherBarData();
            await this.extractPricingData();
            
            await this.saveProductData();
            
            console.log('\n🎉 Pictorem product data extraction completed successfully!');
            console.log('\n📊 Extraction Summary:');
            console.log(`- Canvas Sizes: ${this.productData.dimensions.canvas_sizes.length} combinations`);
            console.log(`- Frame Colors: ${this.productData.floating_frames.colors.length} options`);
            console.log(`- Canvas Types: ${this.productData.printing_surfaces.canvas_types.length} materials`);
            console.log(`- Stretcher Options: ${this.productData.stretcher_bars.depths.length} depths`);
            console.log(`- Pricing Data: ${this.productData.pricing_tiers.length} size tiers`);
            console.log('\n✅ Data ready for VividWalls database integration!');
            
        } catch (error) {
            console.error('❌ Product extraction failed:', error.message);
        } finally {
            await this.cleanup();
        }
    }
}

// Run the extraction tool
if (import.meta.url === `file://${process.argv[1]}`) {
    const extractor = new PictoremProductDataExtractor();
    extractor.runFullExtraction();
}

export default PictoremProductDataExtractor; 