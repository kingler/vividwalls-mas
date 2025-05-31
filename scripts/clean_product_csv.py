#!/usr/bin/env python3
"""
Clean VividWalls Product CSV File
Removes Google Shopping columns and keeps essential product information
following standard product information model practices.
"""

import pandas as pd
import os

def clean_product_csv():
    """
    Clean the product CSV file by removing Google Shopping columns
    and keeping only essential product information.
    """
    
    # Input and output file paths
    input_file = "n8n/data/shared/vividwalls-products-list-2-23-2025.csv"
    output_file = "n8n/data/shared/vividwalls-products-cleaned.csv"
    
    print(f"🧹 Cleaning product CSV file...")
    print(f"📁 Input: {input_file}")
    print(f"📁 Output: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file {input_file} not found!")
        return False
    
    try:
        # Read the CSV file
        print("📖 Reading CSV file...")
        df = pd.read_csv(input_file)
        
        print(f"📊 Original file: {len(df)} rows, {len(df.columns)} columns")
        print(f"💾 Original size: {os.path.getsize(input_file) / 1024:.1f} KB")
        
        # Define essential columns following product information model standards
        essential_columns = [
            # Core Product Identity
            'Handle',           # Unique product identifier
            'Title',           # Product name
            'Body (HTML)',     # Product description
            'Vendor',          # Brand/manufacturer
            'Product Category', # Category classification
            'Type',            # Product type
            'Collections',     # Product collections
            'Published',       # Availability status
            
            # Product Variants & Options
            'Option1 Name',    # First option name (Frame Size)
            'Option1 Value',   # First option value
            'Option2 Name',    # Second option name (Frame Color)  
            'Option2 Value',   # Second option value
            'Option3 Name',    # Third option name (Frame Style)
            'Option3 Value',   # Third option value
            
            # SKU & Inventory
            'Variant SKU',     # Stock keeping unit
            'Variant Inventory Tracker',
            'Variant Inventory Policy',
            'Variant Fulfillment Service',
            
            # Pricing
            'Variant Price',           # Base price
            'Variant Compare At Price', # MSRP/original price
            'Cost per item',          # Cost basis
            
            # Shipping & Tax
            'Variant Requires Shipping',
            'Variant Taxable',
            'Variant Weight Unit',
            'Variant Grams',
            
            # Images & Media
            'Image Src',       # Product image URL
            'Image Position',  # Image ordering
            'Image Alt Text',  # Accessibility text
            'Variant Image',   # Variant-specific image
            
            # SEO & Marketing
            'SEO Title',       # Search engine title
            'SEO Description', # Meta description
            'Gift Card',       # Gift card flag
            
            # Pricing by Region (if needed)
            'Included / United States',
            'Price / United States',
            'Compare At Price / United States',
            'Included / International', 
            'Price / International',
            'Compare At Price / International',
            
            # Status
            'Status'           # Product status (active/draft)
        ]
        
        # Filter to keep only essential columns that exist in the dataframe
        existing_essential_columns = [col for col in essential_columns if col in df.columns]
        
        # Identify Google Shopping columns being removed
        google_columns = [col for col in df.columns if 'Google' in col]
        
        print(f"\n🗑️  Removing {len(google_columns)} Google Shopping columns:")
        for col in google_columns:
            print(f"   - {col}")
        
        # Create cleaned dataframe
        df_cleaned = df[existing_essential_columns].copy()
        
        print(f"\n✅ Cleaned file: {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns")
        print(f"📉 Removed {len(df.columns) - len(df_cleaned.columns)} columns")
        
        # Calculate data completeness for key fields
        print(f"\n📈 Data Completeness Check:")
        key_fields = ['Handle', 'Title', 'Body (HTML)', 'Variant Price', 'Image Src']
        for field in key_fields:
            if field in df_cleaned.columns:
                completeness = (df_cleaned[field].notna().sum() / len(df_cleaned)) * 100
                print(f"   - {field}: {completeness:.1f}%")
        
        # Save cleaned CSV
        print(f"\n💾 Saving cleaned CSV...")
        df_cleaned.to_csv(output_file, index=False)
        
        # Show file size reduction
        new_size = os.path.getsize(output_file) / 1024
        original_size = os.path.getsize(input_file) / 1024
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"📊 File size: {original_size:.1f} KB → {new_size:.1f} KB")
        print(f"🎯 Size reduction: {reduction:.1f}%")
        
        print(f"\n✅ Successfully created cleaned product CSV: {output_file}")
        
        # Show sample of cleaned data
        print(f"\n📋 Sample of cleaned data (first 3 rows):")
        sample_columns = ['Handle', 'Title', 'Variant Price', 'Option1 Value', 'Option2 Value']
        available_sample_columns = [col for col in sample_columns if col in df_cleaned.columns]
        print(df_cleaned[available_sample_columns].head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    success = clean_product_csv()
    if success:
        print("\n🎉 Product CSV cleaning completed successfully!")
    else:
        print("\n💥 Product CSV cleaning failed!") 