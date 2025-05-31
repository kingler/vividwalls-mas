#!/usr/bin/env python3

import csv
import psycopg2
import os
import sys
import uuid
from datetime import datetime
import html

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            database="postgres",
            user="postgres",
            password=os.getenv('POSTGRES_PASSWORD', 'your-secure-password')
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def clean_html_content(content):
    """Clean HTML content and handle encoding issues"""
    if not content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Remove HTML tags (basic cleanup)
    import re
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up whitespace
    content = ' '.join(content.split())
    
    return content.strip()

def get_or_create_collection(cursor, collection_name):
    """Get collection ID or create if doesn't exist"""
    if not collection_name or collection_name.strip() == '':
        return None
    
    collection_name = collection_name.strip()
    
    # Check if collection exists
    cursor.execute("SELECT id FROM collections WHERE name = %s", (collection_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new collection
    collection_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO collections (id, name, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
        (collection_id, collection_name, f"Collection: {collection_name}", datetime.now(), datetime.now())
    )
    return collection_id

def import_products_from_csv(csv_file_path):
    """Import products from CSV file"""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    print(f"📊 Starting import from: {csv_file_path}")
    
    # Counters
    products_imported = 0
    variants_imported = 0
    images_imported = 0
    errors = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Read first few lines to understand structure
            sample_lines = []
            file.seek(0)
            for i, line in enumerate(file):
                sample_lines.append(line.strip())
                if i >= 5:
                    break
            
            print("📋 CSV Structure Analysis:")
            for i, line in enumerate(sample_lines):
                print(f"   Line {i}: {line[:100]}...")
            
            # Reset file pointer
            file.seek(0)
            
            # Try to detect delimiter and structure
            csv_reader = csv.DictReader(file)
            
            print(f"📋 Detected columns: {csv_reader.fieldnames}")
            
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Extract basic product info
                    handle = row.get('Handle', '').strip()
                    title = row.get('Title', '').strip()
                    
                    if not handle or not title:
                        print(f"⚠️  Row {row_num}: Missing handle or title, skipping")
                        continue
                    
                    # Get or determine collection
                    collection_name = None
                    for col in ['Collection', 'Product Category', 'Type', 'Vendor']:
                        if col in row and row[col].strip():
                            collection_name = row[col].strip()
                            break
                    
                    if not collection_name:
                        # Try to infer from title
                        if 'Mosaic' in title:
                            collection_name = 'Mosaics'
                        elif 'Fractal' in title:
                            collection_name = 'Fractal Color'
                        elif 'Kimono' in title:
                            collection_name = 'Kimono'
                        elif 'Shade' in title:
                            collection_name = 'Chromatic Echoes'
                        elif 'Weave' in title:
                            collection_name = 'Shape Emergence'
                        else:
                            collection_name = 'Geometric Intersection'
                    
                    collection_id = get_or_create_collection(cursor, collection_name)
                    
                    # Check if product already exists
                    cursor.execute("SELECT id FROM products WHERE handle = %s", (handle,))
                    existing_product = cursor.fetchone()
                    
                    if existing_product:
                        product_id = existing_product[0]
                        print(f"✅ Product exists: {title}")
                    else:
                        # Create new product
                        product_id = str(uuid.uuid4())
                        
                        # Clean description
                        body_html = clean_html_content(row.get('Body (HTML)', ''))
                        
                        # Insert product
                        cursor.execute("""
                            INSERT INTO products (
                                id, handle, title, body_html, vendor, product_type, 
                                collection_id, published, created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            product_id,
                            handle,
                            title,
                            body_html,
                            row.get('Vendor', 'VividWalls'),
                            row.get('Type', 'Wall Art'),
                            collection_id,
                            True,
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        products_imported += 1
                        print(f"✅ Imported product: {title}")
                    
                    # Handle variant data
                    variant_title = row.get('Variant Title', '').strip()
                    variant_price = row.get('Variant Price', '0').strip()
                    variant_sku = row.get('Variant SKU', '').strip()
                    
                    if variant_title or variant_price != '0':
                        # Check if variant exists
                        cursor.execute(
                            "SELECT id FROM product_variants WHERE product_id = %s AND title = %s", 
                            (product_id, variant_title)
                        )
                        existing_variant = cursor.fetchone()
                        
                        if not existing_variant:
                            variant_id = str(uuid.uuid4())
                            
                            # Parse price
                            try:
                                price = float(variant_price) if variant_price else 0.0
                            except:
                                price = 0.0
                            
                            cursor.execute("""
                                INSERT INTO product_variants (
                                    id, product_id, title, price, sku, inventory_quantity,
                                    created_at, updated_at
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                variant_id,
                                product_id,
                                variant_title or 'Default',
                                price,
                                variant_sku,
                                100,  # Default inventory
                                datetime.now(),
                                datetime.now()
                            ))
                            
                            variants_imported += 1
                    
                    # Handle image data
                    image_src = row.get('Image Src', '').strip()
                    if image_src:
                        # Check if image exists
                        cursor.execute(
                            "SELECT id FROM product_images WHERE product_id = %s AND src = %s", 
                            (product_id, image_src)
                        )
                        existing_image = cursor.fetchone()
                        
                        if not existing_image:
                            image_id = str(uuid.uuid4())
                            
                            cursor.execute("""
                                INSERT INTO product_images (
                                    id, product_id, src, alt_text, position, created_at, updated_at
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                image_id,
                                product_id,
                                image_src,
                                row.get('Image Alt Text', title),
                                1,
                                datetime.now(),
                                datetime.now()
                            ))
                            
                            images_imported += 1
                    
                    # Commit every 10 products
                    if row_num % 10 == 0:
                        conn.commit()
                        print(f"📊 Processed {row_num} rows...")
                
                except Exception as e:
                    print(f"❌ Error processing row {row_num}: {e}")
                    errors += 1
                    continue
        
        # Final commit
        conn.commit()
        
        print(f"\n🎉 Import completed!")
        print(f"   ✅ Products imported: {products_imported}")
        print(f"   ✅ Variants imported: {variants_imported}")
        print(f"   ✅ Images imported: {images_imported}")
        print(f"   ❌ Errors: {errors}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    print("🚀 VividWalls Product Import Tool")
    print("=" * 40)
    
    # CSV file path
    csv_file = "/home/vivid/vivid_mas/n8n/data/shared/vividwalls-products-list-2-23-2025.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    import_products_from_csv(csv_file)

if __name__ == "__main__":
    main() 