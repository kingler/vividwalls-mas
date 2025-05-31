#!/usr/bin/env python3

"""
VividWalls CSV Import Script
Properly handles CSV with HTML content and inserts into PostgreSQL database
"""

import csv
import psycopg2
import psycopg2.extras
import json
import sys
import re
from datetime import datetime

import os

 # Database connection settings
 DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '54322')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'postgres')
 }

def clean_html(html_content):
    """Remove HTML tags and clean up content"""
    if not html_content:
        return ""
    # Remove HTML tags
    clean = re.sub('<[^<]+?>', '', html_content)
    # Clean up whitespace
    clean = ' '.join(clean.split())
    return clean.strip()

def extract_dimensions(text):
    """Extract dimensions from text like '24x36'"""
    if not text:
        return None
    match = re.search(r'(\d+)x(\d+)', text)
    if match:
        return {
            'width': int(match.group(1)),
            'height': int(match.group(2)),
            'unit': 'inches'
        }
    return None

def safe_float(value):
    """Safely convert to float"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None

def safe_int(value):
    """Safely convert to integer"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None

def main():
    print("🚀 VividWalls CSV Import Script Starting...")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Read and process CSV
    csv_file = 'n8n/data/shared/vividwalls-products-list-2-23-2025.csv'
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Use csv.reader with proper settings for multiline content
            reader = csv.DictReader(file, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL)
            
            products_data = []
            variants_data = []
            collections_set = set()
            
            print("📝 Processing CSV data...")
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Extract basic product info with better field mapping
                    handle = row.get('Handle', '').strip()
                    title = row.get('Title', '').strip()
                    body_html = row.get('Body (HTML)', '')
                    vendor = row.get('Vendor', '').strip()
                    product_type = row.get('Type', '').strip()
                    tags = row.get('Tags', '').strip()
                    published = row.get('Published', '').strip().lower() == 'true'
                    
                    if not handle:
                        continue
                    
                    # If title is empty, try to generate from handle
                    if not title and handle:
                        title = handle.replace('-', ' ').title()
                    
                    # Clean description
                    description = clean_html(body_html)
                    
                    # Process tags
                    tag_array = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
                    
                    # Add to collections set
                    if product_type:
                        collections_set.add(product_type.strip())
                    
                    # Product data
                    product_data = {
                        'handle': handle,
                        'title': title,
                        'description': description,
                        'vendor': vendor,
                        'type': product_type,
                        'collection': product_type.strip() if product_type else None,
                        'published': published,
                        'status': 'active',
                        'tags': tag_array,
                        'shopify_url': f'https://vividwalls.com/products/{handle}' if handle else None
                    }
                    
                    products_data.append(product_data)
                    
                    # Variant data
                    variant_sku = row.get('Variant SKU', '').strip()
                    if variant_sku:
                        # Extract frame info from option values
                        option1_value = row.get('Option1 Value', '').strip()
                        option2_value = row.get('Option2 Value', '').strip()
                        option3_value = row.get('Option3 Value', '').strip()
                        
                        # Determine frame size, color, style
                        frame_size = 'standard'
                        frame_color = 'standard'
                        frame_style = 'standard'
                        
                        # Check all option values for size info
                        for option_val in [option1_value, option2_value, option3_value]:
                            if re.search(r'\d+x\d+', option_val):
                                frame_size = re.search(r'(\d+x\d+)', option_val).group(1)
                            if any(color in option_val.lower() for color in ['black', 'white', 'natural', 'silver']):
                                for color in ['black', 'white', 'natural', 'silver']:
                                    if color in option_val.lower():
                                        frame_color = color
                                        break
                            if any(style in option_val.lower() for style in ['framed', 'canvas', 'print']):
                                for style in ['framed', 'canvas', 'print']:
                                    if style in option_val.lower():
                                        frame_style = style
                                        break
                        
                        # Extract dimensions
                        dimensions = extract_dimensions(frame_size)
                        if not dimensions:
                            dimensions = {'width': 24, 'height': 36, 'unit': 'inches'}
                        
                        variant_data = {
                            'handle': handle,
                            'sku': variant_sku,
                            'frame_size': frame_size,
                            'frame_color': frame_color,
                            'frame_style': frame_style,
                            'price': safe_float(row.get('Variant Price', '')),
                            'compare_at_price': safe_float(row.get('Variant Compare At Price', '')),
                            'inventory_quantity': safe_int(row.get('Variant Inventory Qty', '0')) or 0,
                            'weight': safe_float(row.get('Variant Grams', '')),
                            'dimensions': json.dumps(dimensions),  # Convert to JSON string
                            'available': True,
                            'image_src': row.get('Image Src', '').strip(),
                            'image_position': safe_int(row.get('Image Position', '1')) or 1,
                            'image_alt': row.get('Image Alt Text', '').strip()
                        }
                        
                        variants_data.append(variant_data)
                
                except Exception as e:
                    print(f"⚠️  Error processing row {row_num}: {e}")
                    continue
            
            print(f"📊 Processed {len(products_data)} products and {len(variants_data)} variants")
            
            # Clear existing data first
            print("🧹 Clearing existing product data...")
            cur.execute("DELETE FROM product_images WHERE product_id IN (SELECT id FROM products)")
            cur.execute("DELETE FROM product_variants WHERE product_id IN (SELECT id FROM products)")
            cur.execute("DELETE FROM products")
            
            # Insert collections first
            print("📝 Inserting collections...")
            for collection_name in collections_set:
                if not collection_name:
                    continue
                
                # Determine collection characteristics
                mood_profile = 'sophisticated'
                color_palette = ['neutral', 'versatile']
                style_characteristics = ['contemporary', 'abstract']
                
                if 'chromatic' in collection_name.lower():
                    mood_profile = 'energizing'
                    color_palette = ['red', 'orange', 'yellow', 'coral']
                    style_characteristics = ['vibrant', 'emotional', 'warm']
                elif 'geometric' in collection_name.lower():
                    mood_profile = 'sophisticated'
                    color_palette = ['blue', 'gray', 'white', 'black']
                    style_characteristics = ['geometric', 'clean', 'modern']
                elif 'resonant' in collection_name.lower():
                    mood_profile = 'calming'
                    color_palette = ['blue', 'teal', 'navy', 'mint']
                    style_characteristics = ['cool', 'structured', 'calming']
                
                slug = collection_name.lower().replace(' ', '-').replace('&', 'and')
                description = f"Contemporary abstract artwork from the {collection_name} collection"
                
                cur.execute("""
                    INSERT INTO collections (name, slug, description, mood_profile, color_palette, style_characteristics)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        mood_profile = EXCLUDED.mood_profile,
                        color_palette = EXCLUDED.color_palette,
                        style_characteristics = EXCLUDED.style_characteristics
                """, (collection_name, slug, description, mood_profile, color_palette, style_characteristics))
            
            # Insert products
            print("📝 Inserting products...")
            for product in products_data:
                cur.execute("""
                    INSERT INTO products (
                        handle, title, description, vendor, type, collection, 
                        published, status, tags, shopify_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (handle) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        updated_at = NOW()
                """, (
                    product['handle'], product['title'], product['description'],
                    product['vendor'], product['type'], product['collection'],
                    product['published'], product['status'], product['tags'],
                    product['shopify_url']
                ))
            
            # Insert variants
            print("📝 Inserting product variants...")
            for variant in variants_data:
                # Get product ID
                cur.execute("SELECT id FROM products WHERE handle = %s", (variant['handle'],))
                result = cur.fetchone()
                if not result:
                    continue
                
                product_id = result[0]
                
                cur.execute("""
                    INSERT INTO product_variants (
                        product_id, sku, frame_size, frame_color, frame_style,
                        price, compare_at_price, inventory_quantity, weight,
                        dimensions, available
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (sku) DO UPDATE SET
                        price = EXCLUDED.price,
                        compare_at_price = EXCLUDED.compare_at_price,
                        inventory_quantity = EXCLUDED.inventory_quantity
                """, (
                    product_id, variant['sku'], variant['frame_size'],
                    variant['frame_color'], variant['frame_style'],
                    variant['price'], variant['compare_at_price'],
                    variant['inventory_quantity'], variant['weight'],
                    variant['dimensions'], variant['available']
                ))
                
                # Insert product image if available
                if variant['image_src']:
                    cur.execute("""
                        INSERT INTO product_images (
                            product_id, image_type, storage_url, cdn_url,
                            width, height, format, alt_text, is_primary
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id, image_type, variant_id) DO NOTHING
                    """, (
                        product_id, 'primary' if variant['image_position'] == 1 else 'variant',
                        variant['image_src'], variant['image_src'],
                        1200, 1200, 'jpeg', variant['image_alt'],
                        variant['image_position'] == 1
                    ))
            
            # Commit transaction
            conn.commit()
            
            # Show final counts
            cur.execute("SELECT COUNT(*) FROM products")
            product_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM product_variants")
            variant_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM collections")
            collection_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM product_images")
            image_count = cur.fetchone()[0]
            
            # Show sample data
            print("\n📋 Sample imported data:")
            cur.execute("SELECT handle, title, collection FROM products WHERE title IS NOT NULL AND title != '' LIMIT 3")
            for row in cur.fetchall():
                print(f"   Product: {row[0]} - {row[1]} ({row[2]})")
            
            print("\n🎉 Import completed successfully!")
            print("=" * 50)
            print(f"📊 Final counts:")
            print(f"   Collections: {collection_count}")
            print(f"   Products: {product_count}")
            print(f"   Variants: {variant_count}")
            print(f"   Images: {image_count}")
            
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main() 