#!/usr/bin/env python3
"""
VividWalls CSV Import Script - Corrected Version
Imports Shopify CSV export data into PostgreSQL database
"""

import csv
import subprocess
import os
import sys
from datetime import datetime

def execute_sql(container_name, sql):
    """Execute SQL via docker exec"""
    cmd = ['docker', 'exec', container_name, 'psql', '-U', 'postgres', '-d', 'postgres', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return False
    return True

def clean_text(text):
    """Clean text for SQL insertion"""
    if not text:
        return ''
    return str(text).replace("'", "''").replace('\n', ' ').replace('\r', ' ').strip()

def parse_price(price_str):
    """Parse price string to float"""
    if not price_str:
        return 0.0
    try:
        # Remove any currency symbols and convert to float
        clean_price = price_str.replace('$', '').replace(',', '').strip()
        return float(clean_price) if clean_price else 0.0
    except (ValueError, AttributeError):
        return 0.0

def main():
    # Get PostgreSQL container name from environment or use default
    postgres_container = os.environ.get('POSTGRES_CONTAINER', 'vivid_mas-postgres-1')
    
    print("🔗 Starting VividWalls CSV import...")
    print(f"📋 Using PostgreSQL container: {postgres_container}")
    
    # CSV file path
    csv_file = 'n8n/data/shared/vividwalls-products-list-2-23-2025.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    print(f"📊 Importing products from {csv_file}...")
    
    # Track statistics
    products_imported = 0
    variants_imported = 0
    images_imported = 0
    collections_added = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Process each row
            for row_num, row in enumerate(reader, 1):
                try:
                    # Extract and clean data from Shopify CSV format
                    handle = clean_text(row.get('Handle', ''))
                    title = clean_text(row.get('Title', ''))
                    body_html = clean_text(row.get('Body (HTML)', ''))
                    vendor = clean_text(row.get('Vendor', ''))
                    product_category = clean_text(row.get('Product Category', ''))
                    product_type = clean_text(row.get('Type', ''))
                    tags = clean_text(row.get('Tags', ''))
                    published = clean_text(row.get('Published', ''))
                    
                    # Variant information
                    variant_sku = clean_text(row.get('Variant SKU', ''))
                    variant_price = parse_price(row.get('Variant Price', '0'))
                    variant_compare_price = parse_price(row.get('Variant Compare At Price', '0'))
                    variant_grams = clean_text(row.get('Variant Grams', '0'))
                    variant_inventory = clean_text(row.get('Variant Inventory Tracker', '0'))
                    
                    # Image information
                    image_src = clean_text(row.get('Image Src', ''))
                    image_position = clean_text(row.get('Image Position', '1'))
                    image_alt = clean_text(row.get('Image Alt Text', ''))
                    
                    # Skip rows without title
                    if not title:
                        continue
                    
                    # Determine collection from product category or type
                    collection = product_category if product_category else product_type
                    if not collection:
                        collection = 'Uncategorized'
                    
                    collections_added.add(collection)
                    
                    # Insert collection if not exists
                    collection_sql = f"""
                    INSERT INTO collections (name, description) 
                    VALUES ('{collection}', 'Imported from Shopify') 
                    ON CONFLICT (name) DO NOTHING;
                    """
                    execute_sql(postgres_container, collection_sql)
                    
                    # Insert product
                    product_sql = f"""
                    INSERT INTO products (
                        title, collection, price, description, vendor, 
                        product_type, tags, created_at, updated_at
                    ) VALUES (
                        '{title}', '{collection}', {variant_price}, 
                        '{body_html}', '{vendor}', '{product_type}', 
                        '{tags}', NOW(), NOW()
                    ) ON CONFLICT (title) DO NOTHING;
                    """
                    
                    if execute_sql(postgres_container, product_sql):
                        products_imported += 1
                        
                        # Get product ID for variants and images
                        get_product_id_sql = f"SELECT id FROM products WHERE title = '{title}' LIMIT 1;"
                        
                        # Insert variant if we have variant data
                        if variant_sku or variant_price > 0:
                            variant_sql = f"""
                            INSERT INTO product_variants (
                                product_id, title, price, sku, inventory_quantity, weight
                            ) SELECT 
                                id, '{title} - Variant', {variant_price}, '{variant_sku}', 
                                {variant_inventory if variant_inventory.isdigit() else 0}, 
                                {variant_grams if variant_grams.isdigit() else 0}
                            FROM products WHERE title = '{title}' LIMIT 1;
                            """
                            if execute_sql(postgres_container, variant_sql):
                                variants_imported += 1
                        
                        # Insert image if we have image data
                        if image_src:
                            image_sql = f"""
                            INSERT INTO product_images (
                                product_id, src, alt_text, position
                            ) SELECT 
                                id, '{image_src}', '{image_alt}', 
                                {image_position if image_position.isdigit() else 1}
                            FROM products WHERE title = '{title}' LIMIT 1;
                            """
                            if execute_sql(postgres_container, image_sql):
                                images_imported += 1
                    
                    # Progress indicator
                    if row_num % 10 == 0:
                        print(f"   Processed {row_num} rows... ({products_imported} products imported)")
                        
                except Exception as e:
                    print(f"Error processing row {row_num} (product: {title}): {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False
    
    # Print final statistics
    print(f"\n✅ Import completed successfully!")
    print(f"📊 Import Statistics:")
    print(f"   Products imported: {products_imported}")
    print(f"   Variants imported: {variants_imported}")
    print(f"   Images imported: {images_imported}")
    print(f"   Collections added: {len(collections_added)}")
    print(f"   Collections: {', '.join(sorted(collections_added))}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 