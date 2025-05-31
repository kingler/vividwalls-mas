#!/usr/bin/env python3
"""
Update VividWalls Product Pricing with Current Pictorem Costs
Updates the cleaned product CSV with current Pictorem pricing including 15% Pro discount
"""

import pandas as pd
import numpy as np
import os
import json
import requests
from datetime import datetime

def update_pictorem_pricing():
    """
    Update VividWalls product pricing based on current Pictorem costs.
    Includes 15% Pro account discount and appropriate markup for profit.
    """
    
    # Current Pictorem Canvas Print Pricing (Standard prices, 15% Pro discount applied)
    # Source: https://www.pictorem.com/order.html?hash=ac3b92102e5d4c6c6cea7fae91e57156
    
    # SQUARE SIZES
    pictorem_square_prices = {
        "12x12": {"standard": 36.00, "pro": 30.60},  # $36 - 15% = $30.60
        "16x16": {"standard": 46.00, "pro": 39.10},  # $46 - 15% = $39.10
        "20x20": {"standard": 58.00, "pro": 49.30},  # Estimated
        "24x24": {"standard": 74.00, "pro": 62.90},  # $74 - 15% = $62.90
        "30x30": {"standard": 103.00, "pro": 87.55}, # $103 - 15% = $87.55
        "36x36": {"standard": 140.00, "pro": 119.00}, # Estimated
    }
    
    # LANDSCAPE SIZES (derived from patterns)
    pictorem_landscape_prices = {
        "16x12": {"standard": 40.00, "pro": 34.00},   # Based on pattern
        "24x16": {"standard": 57.00, "pro": 48.45},   # From pricing page
        "30x20": {"standard": 88.00, "pro": 74.80},   # From pricing page
        "36x24": {"standard": 100.00, "pro": 85.00},  # From pricing page example
        "48x32": {"standard": 150.00, "pro": 127.50}, # Estimated
        "48x36": {"standard": 177.00, "pro": 150.45}, # From pricing page
        "60x40": {"standard": 230.00, "pro": 195.50}, # Estimated
    }
    
    # PORTRAIT SIZES (same as landscape, flipped)
    pictorem_portrait_prices = {
        "12x16": {"standard": 40.00, "pro": 34.00},
        "16x24": {"standard": 57.00, "pro": 48.45},
        "20x30": {"standard": 88.00, "pro": 74.80},
        "24x36": {"standard": 100.00, "pro": 85.00},
        "32x48": {"standard": 150.00, "pro": 127.50},
        "36x48": {"standard": 177.00, "pro": 150.45},
        "40x60": {"standard": 230.00, "pro": 195.50},
    }
    
    # PANORAMIC SIZES
    pictorem_panoramic_prices = {
        "16x8": {"standard": 45.00, "pro": 38.25},    # From pricing page
        "24x12": {"standard": 48.00, "pro": 40.80},   # From pricing page
        "30x16": {"standard": 65.00, "pro": 55.25},   # From pricing page
        "36x16": {"standard": 74.00, "pro": 62.90},   # From pricing page
        "40x24": {"standard": 119.00, "pro": 101.15}, # From pricing page
        "48x24": {"standard": 130.00, "pro": 110.50}, # From pricing page
        "60x24": {"standard": 160.00, "pro": 136.00}, # Estimated
        "72x24": {"standard": 190.00, "pro": 161.50}, # Estimated
        "96x24": {"standard": 250.00, "pro": 212.50}, # Estimated
    }
    
    # CANVAS ROLL PRICING (typically 20-30% less than stretched canvas)
    canvas_roll_discount = 0.25  # 25% discount for canvas roll vs stretched
    
    # Combine all pricing into master dictionary
    all_pictorem_prices = {}
    all_pictorem_prices.update(pictorem_square_prices)
    all_pictorem_prices.update(pictorem_landscape_prices)
    all_pictorem_prices.update(pictorem_portrait_prices)
    all_pictorem_prices.update(pictorem_panoramic_prices)
    
    # Floating Frame Costs (with 15% Pro discount applied)
    # Based on Pictorem floating frame pricing
    frame_costs = {
        "FL-814-18": {"standard": 18.00, "pro": 15.30},  # Walnut
        "FL-814-51": {"standard": 18.00, "pro": 15.30},  # Pewter
        "FL-814-08": {"standard": 18.00, "pro": 15.30},  # Gold Antique
        "FL-814-61": {"standard": 18.00, "pro": 15.30},  # Ebony
        "FL-814-52": {"standard": 18.00, "pro": 15.30},  # Charcoal
        "FL-804-42": {"standard": 37.00, "pro": 31.45},  # White Premium
        "613-50": {"standard": 18.00, "pro": 15.30},     # Gold
        "FL-814-22": {"standard": 19.00, "pro": 16.15},  # Truffle
    }
    
    # Files
    input_file = "n8n/data/shared/vividwalls-products-cleaned.csv"
    output_file = "n8n/data/shared/vividwalls-products-updated-pricing.csv"
    
    print(f"🔄 Updating VividWalls pricing with current Pictorem costs...")
    print(f"📁 Input: {input_file}")
    print(f"📁 Output: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file {input_file} not found!")
        return False
    
    try:
        # Read the cleaned CSV file
        print("📖 Reading cleaned product CSV...")
        df = pd.read_csv(input_file)
        
        print(f"📊 Processing {len(df)} products...")
        
        # Add new cost and pricing columns
        df['Pictorem_Canvas_Cost_Stretched'] = 0.0
        df['Pictorem_Canvas_Cost_Roll'] = 0.0
        df['Pictorem_Frame_Cost'] = 0.0
        df['Canvas_Type'] = 'Stretched'  # Default to stretched
        df['Total_Cost'] = 0.0
        df['Suggested_Retail_Price'] = 0.0
        df['Markup_Percentage'] = 0.0
        df['Pictorem_Size_Match'] = ''
        df['Pricing_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        products_updated = 0
        
        # Process each product
        for idx, row in df.iterrows():
            canvas_cost_stretched = 0.0
            canvas_cost_roll = 0.0
            frame_cost = 0.0
            size_match = ''
            
            # Extract size from Option1 Value (Frame Size)
            if pd.notna(row.get('Option1 Value')):
                size = str(row['Option1 Value']).strip().replace('"', '').replace('in', '')
                
                # Clean and standardize size format
                if 'x' in size.lower():
                    size_parts = size.lower().split('x')
                    if len(size_parts) == 2:
                        try:
                            w = int(float(size_parts[0].strip()))
                            h = int(float(size_parts[1].strip()))
                            standardized_size = f"{w}x{h}"
                            size_match = standardized_size
                            
                            # Get Pictorem pricing for this size
                            if standardized_size in all_pictorem_prices:
                                canvas_cost_stretched = all_pictorem_prices[standardized_size]["pro"]
                                canvas_cost_roll = canvas_cost_stretched * (1 - canvas_roll_discount)
                            else:
                                # Estimate cost based on area if exact size not found
                                canvas_cost_stretched = estimate_canvas_cost(w, h, all_pictorem_prices)
                                canvas_cost_roll = canvas_cost_stretched * (1 - canvas_roll_discount)
                                size_match = f"{standardized_size} (estimated)"
                                
                        except ValueError:
                            # Handle non-numeric sizes
                            canvas_cost_stretched = estimate_canvas_cost_from_string(size, all_pictorem_prices)
                            canvas_cost_roll = canvas_cost_stretched * (1 - canvas_roll_discount)
                            size_match = f"{size} (estimated)"
            
            # Extract frame type from Option2 Value (Frame Color/Style)
            canvas_type = 'Stretched'  # Default
            if pd.notna(row.get('Option2 Value')):
                frame_style = str(row['Option2 Value']).strip().lower()
                
                # Check if it's a canvas roll product
                if 'roll' in frame_style or 'unframed' in frame_style:
                    canvas_type = 'Roll'
                    frame_cost = 0.0
                else:
                    # Map frame descriptions to frame costs
                    frame_cost = map_frame_cost(frame_style, frame_costs)
            
            # Calculate total cost based on canvas type
            if canvas_type == 'Roll':
                total_cost = canvas_cost_roll
            else:
                total_cost = canvas_cost_stretched + frame_cost
            
            # Apply markup strategy based on total cost
            if total_cost < 50:
                markup_multiplier = 2.8  # Higher markup for lower cost items
            elif total_cost < 100:
                markup_multiplier = 2.4  # Medium markup
            elif total_cost < 200:
                markup_multiplier = 2.1  # Lower markup for higher cost items
            else:
                markup_multiplier = 1.9  # Minimal markup for very expensive items
            
            suggested_price = round(total_cost * markup_multiplier, 2)
            markup_percentage = round(((suggested_price - total_cost) / total_cost) * 100, 1) if total_cost > 0 else 0
            
            # Update row values
            df.at[idx, 'Pictorem_Canvas_Cost_Stretched'] = round(canvas_cost_stretched, 2)
            df.at[idx, 'Pictorem_Canvas_Cost_Roll'] = round(canvas_cost_roll, 2)
            df.at[idx, 'Pictorem_Frame_Cost'] = round(frame_cost, 2)
            df.at[idx, 'Canvas_Type'] = canvas_type
            df.at[idx, 'Total_Cost'] = round(total_cost, 2)
            df.at[idx, 'Suggested_Retail_Price'] = suggested_price
            df.at[idx, 'Markup_Percentage'] = markup_percentage
            df.at[idx, 'Pictorem_Size_Match'] = size_match
            
            # Update existing price fields
            df.at[idx, 'Variant Price'] = suggested_price
            df.at[idx, 'Cost per item'] = round(total_cost, 2)
            
            if total_cost > 0:
                products_updated += 1
        
        # Save updated CSV
        print(f"💾 Saving updated pricing CSV...")
        df.to_csv(output_file, index=False)
        
        # Summary statistics
        total_products = len(df)
        avg_cost = df['Total_Cost'].mean()
        avg_price = df['Suggested_Retail_Price'].mean()
        avg_markup = df['Markup_Percentage'].mean()
        
        print(f"\n✅ Pricing update completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Total products: {total_products}")
        print(f"   - Products with updated pricing: {products_updated}")
        print(f"   - Average total cost: ${avg_cost:.2f}")
        print(f"   - Average retail price: ${avg_price:.2f}")
        print(f"   - Average markup: {avg_markup:.1f}%")
        
        # Show sample of updated products
        print(f"\n📋 Sample of updated pricing:")
        sample_cols = ['Title', 'Option1 Value', 'Canvas_Type', 'Total_Cost', 'Suggested_Retail_Price', 'Markup_Percentage', 'Pictorem_Size_Match']
        available_cols = [col for col in sample_cols if col in df.columns]
        sample_df = df[df['Total_Cost'] > 0][available_cols].head(10)
        if not sample_df.empty:
            print(sample_df.to_string(index=False))
        
        # Generate automation configuration
        generate_automation_config(df)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating pricing: {str(e)}")
        return False

def estimate_canvas_cost(width, height, price_dict):
    """
    Estimate canvas cost for custom sizes based on area calculation.
    """
    try:
        target_area = width * height
        
        # Find closest area match in price dictionary
        closest_size = None
        closest_area_diff = float('inf')
        
        for size_key, pricing in price_dict.items():
            size_parts = size_key.split('x')
            if len(size_parts) == 2:
                w = float(size_parts[0])
                h = float(size_parts[1])
                area = w * h
                
                area_diff = abs(target_area - area)
                if area_diff < closest_area_diff:
                    closest_area_diff = area_diff
                    closest_size = size_key
        
        if closest_size:
            base_price = price_dict[closest_size]["pro"]
            closest_parts = closest_size.split('x')
            closest_area = float(closest_parts[0]) * float(closest_parts[1])
            area_ratio = target_area / closest_area
            
            # Apply area-based pricing with diminishing returns
            if area_ratio > 1:
                estimated_price = base_price * (area_ratio ** 0.85)
            else:
                estimated_price = base_price * area_ratio
            
            return round(estimated_price, 2)
        
        # Fallback: estimate based on average price per square inch
        avg_price_per_sq_inch = calculate_avg_price_per_sq_inch(price_dict)
        return round(target_area * avg_price_per_sq_inch, 2)
        
    except:
        return 50.0  # Fallback price

def estimate_canvas_cost_from_string(size_str, price_dict):
    """
    Estimate cost when size is provided as string that may not parse cleanly.
    """
    # Try to extract numbers from the string
    import re
    numbers = re.findall(r'\d+\.?\d*', size_str)
    
    if len(numbers) >= 2:
        try:
            w = float(numbers[0])
            h = float(numbers[1])
            return estimate_canvas_cost(w, h, price_dict)
        except:
            pass
    
    # Fallback to average price
    all_prices = [pricing["pro"] for pricing in price_dict.values()]
    return round(sum(all_prices) / len(all_prices), 2)

def calculate_avg_price_per_sq_inch(price_dict):
    """
    Calculate average price per square inch from known sizes.
    """
    total_price = 0
    total_area = 0
    
    for size_key, pricing in price_dict.items():
        try:
            size_parts = size_key.split('x')
            if len(size_parts) == 2:
                w = float(size_parts[0])
                h = float(size_parts[1])
                area = w * h
                price = pricing["pro"]
                
                total_price += price
                total_area += area
        except:
            continue
    
    if total_area > 0:
        return total_price / total_area
    else:
        return 1.0  # Fallback

def map_frame_cost(frame_description, frame_costs):
    """
    Map frame description to frame cost based on color/style.
    """
    frame_desc = frame_description.lower()
    
    # Map common frame descriptions to frame codes
    frame_mapping = {
        'walnut': 'FL-814-18',
        'pewter': 'FL-814-51', 
        'gold antique': 'FL-814-08',
        'antique gold': 'FL-814-08',
        'ebony': 'FL-814-61',
        'black': 'FL-814-61',
        'charcoal': 'FL-814-52',
        'white': 'FL-804-42',
        'gold': '613-50',
        'truffle': 'FL-814-22',
        'brown': 'FL-814-22',
    }
    
    # Find matching frame
    for desc, code in frame_mapping.items():
        if desc in frame_desc:
            return frame_costs.get(code, {}).get("pro", 15.30)
    
    # Default frame cost if no match found
    return 15.30

def generate_automation_config(df):
    """
    Generate configuration file for Shopify-to-Pictorem automation.
    """
    try:
        # Create automation configuration
        automation_config = {
            "pictorem_api": {
                "base_url": "https://www.pictorem.com/api",
                "login_url": "https://www.pictorem.com/login",
                "order_url": "https://www.pictorem.com/order.html",
                "credentials": {
                    "username": "kingler@me.com",
                    "password": "#Freedom2023#"
                }
            },
            "size_mapping": {},
            "frame_mapping": {},
            "canvas_types": ["Stretched", "Roll"],
            "pro_discount": 0.15,
            "markup_strategy": {
                "low_cost": {"threshold": 50, "multiplier": 2.8},
                "medium_cost": {"threshold": 100, "multiplier": 2.4},
                "high_cost": {"threshold": 200, "multiplier": 2.1},
                "premium_cost": {"threshold": 999999, "multiplier": 1.9}
            }
        }
        
        # Extract unique size mappings from processed data
        unique_sizes = df[df['Pictorem_Size_Match'] != '']['Pictorem_Size_Match'].unique()
        for size in unique_sizes:
            if size and '(estimated)' not in size:
                automation_config["size_mapping"][size] = {
                    "pictorem_size": size,
                    "supported": True
                }
        
        # Extract frame mappings
        unique_frames = df[df['Option2 Value'].notna()]['Option2 Value'].unique()
        for frame in unique_frames:
            automation_config["frame_mapping"][str(frame)] = {
                "pictorem_frame": str(frame),
                "cost_added": True
            }
        
        # Save automation config
        config_file = "scripts/shopify_pictorem_automation_config.json"
        with open(config_file, 'w') as f:
            json.dump(automation_config, f, indent=2)
        
        print(f"\n🤖 Automation configuration saved to: {config_file}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not generate automation config: {str(e)}")

if __name__ == "__main__":
    success = update_pictorem_pricing()
    if success:
        print("\n🎉 Pictorem pricing update completed successfully!")
        print("💡 Next steps:")
        print("   1. Review the updated pricing in the output file")
        print("   2. Test the automation configuration")
        print("   3. Set up Shopify webhook integration")
        print("   4. Update your e-commerce platform with new prices")
    else:
        print("\n💥 Pictorem pricing update failed!") 