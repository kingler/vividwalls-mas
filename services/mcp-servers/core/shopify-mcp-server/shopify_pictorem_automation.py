#!/usr/bin/env python3
"""
Shopify to Pictorem Order Automation System
Handles automatic order placement on Pictorem when Shopify orders are completed
"""

import json
import requests
import time
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
import hashlib
import hmac

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pictorem_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PictoremAutomation:
    """
    Automation system for placing orders on Pictorem from Shopify webhooks
    """
    
    def __init__(self, config_file="shopify_pictorem_automation_config.json"):
        """Initialize the automation system with configuration"""
        self.config = self.load_config(config_file)
        self.driver = None
        self.logged_in = False
        
    def load_config(self, config_file):
        """Load automation configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {str(e)}")
            raise
    
    def setup_driver(self, headless=True):
        """Set up Chrome WebDriver for browser automation"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup WebDriver: {str(e)}")
            return False
    
    def login_to_pictorem(self):
        """Log in to Pictorem with Pro account credentials"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            # Navigate to login page
            self.driver.get(self.config["pictorem_api"]["login_url"])
            
            # Wait for login form and fill credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(self.config["pictorem_api"]["credentials"]["username"])
            
            password_field.clear()
            password_field.send_keys(self.config["pictorem_api"]["credentials"]["password"])
            
            # Submit login form
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for successful login (check for user account elements)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'account')]"))
            )
            
            self.logged_in = True
            logger.info("✅ Successfully logged in to Pictorem")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to login to Pictorem: {str(e)}")
            return False
    
    def place_pictorem_order(self, order_data):
        """
        Place an order on Pictorem based on Shopify order data
        
        Args:
            order_data: Dictionary containing order details from Shopify
        """
        try:
            if not self.logged_in:
                if not self.login_to_pictorem():
                    return False
            
            results = []
            
            # Process each line item in the order
            for item in order_data.get('line_items', []):
                result = self.process_order_item(item, order_data)
                results.append(result)
            
            logger.info(f"✅ Processed {len(results)} items for order {order_data.get('order_number')}")
            return all(results)
            
        except Exception as e:
            logger.error(f"❌ Failed to place Pictorem order: {str(e)}")
            return False
    
    def process_order_item(self, item, order_data):
        """Process a single order item and place it on Pictorem"""
        try:
            # Extract item details
            product_title = item.get('title', '')
            variant_title = item.get('variant_title', '')
            quantity = item.get('quantity', 1)
            
            # Parse size and frame information from variant
            size, frame_type, canvas_type = self.parse_item_details(item)
            
            if not size:
                logger.error(f"❌ Could not determine size for item: {product_title}")
                return False
            
            # Navigate to Pictorem canvas order page
            order_url = f"{self.config['pictorem_api']['order_url']}?hash=new&create=1&prod=canvas"
            self.driver.get(order_url)
            
            # Set custom size
            success = self.set_canvas_size(size)
            if not success:
                return False
            
            # Set canvas type (Stretched vs Roll)
            success = self.set_canvas_type(canvas_type)
            if not success:
                return False
            
            # Add frame if specified
            if frame_type and frame_type.lower() != 'none':
                success = self.add_frame(frame_type)
                if not success:
                    logger.warning(f"⚠️ Could not add frame {frame_type}, continuing without frame")
            
            # Upload image (placeholder - would need actual image processing)
            success = self.handle_image_upload(item, order_data)
            if not success:
                return False
            
            # Set quantity and complete order
            success = self.complete_order(quantity, order_data)
            if not success:
                return False
            
            logger.info(f"✅ Successfully processed item: {product_title} - {size}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process order item: {str(e)}")
            return False
    
    def parse_item_details(self, item):
        """Parse size, frame, and canvas type from Shopify item data"""
        try:
            variant_title = item.get('variant_title', '')
            properties = item.get('properties', [])
            
            # Initialize defaults
            size = None
            frame_type = 'None'
            canvas_type = 'Stretched'
            
            # Parse variant title for size (e.g., "24x36 / Black Frame")
            if 'x' in variant_title:
                parts = variant_title.split('/')
                if parts:
                    size_part = parts[0].strip()
                    if 'x' in size_part:
                        size = size_part.replace('"', '').replace('in', '').strip()
                
                # Check for frame information
                if len(parts) > 1:
                    frame_part = parts[1].strip().lower()
                    if 'frame' in frame_part:
                        frame_type = frame_part.replace('frame', '').strip().title()
                    elif 'roll' in frame_part or 'unframed' in frame_part:
                        canvas_type = 'Roll'
                        frame_type = 'None'
            
            # Check properties for additional details
            for prop in properties:
                name = prop.get('name', '').lower()
                value = prop.get('value', '')
                
                if 'size' in name and 'x' in value:
                    size = value.strip()
                elif 'frame' in name:
                    frame_type = value.strip()
                elif 'canvas' in name and 'roll' in value.lower():
                    canvas_type = 'Roll'
            
            return size, frame_type, canvas_type
            
        except Exception as e:
            logger.error(f"❌ Failed to parse item details: {str(e)}")
            return None, 'None', 'Stretched'
    
    def set_canvas_size(self, size):
        """Set custom canvas size on Pictorem order page"""
        try:
            # Parse width and height
            if 'x' not in size:
                return False
            
            width, height = size.split('x')
            width = width.strip()
            height = height.strip()
            
            # Find and set width dropdown
            width_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "width"))
            )
            Select(width_select).select_by_value(width)
            
            # Find and set height dropdown
            height_select = self.driver.find_element(By.NAME, "height")
            Select(height_select).select_by_value(height)
            
            # Wait for price update
            time.sleep(2)
            
            logger.info(f"✅ Set canvas size to {size}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set canvas size {size}: {str(e)}")
            return False
    
    def set_canvas_type(self, canvas_type):
        """Set canvas type (Stretched vs Roll)"""
        try:
            if canvas_type.lower() == 'roll':
                # Select Canvas Roll radio button
                canvas_roll_radio = self.driver.find_element(
                    By.XPATH, "//input[@value='Canvas Roll']"
                )
                canvas_roll_radio.click()
            else:
                # Select Stretched Canvas radio button (usually default)
                stretched_radio = self.driver.find_element(
                    By.XPATH, "//input[@value='Stretched Canvas']"
                )
                stretched_radio.click()
            
            time.sleep(1)
            logger.info(f"✅ Set canvas type to {canvas_type}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not set canvas type {canvas_type}: {str(e)}")
            return True  # Continue even if this fails
    
    def add_frame(self, frame_type):
        """Add floating frame if specified"""
        try:
            # Look for frame options (usually in a dropdown or checkbox)
            frame_option = self.driver.find_element(
                By.XPATH, f"//option[contains(text(), '{frame_type}')]"
            )
            frame_option.click()
            
            time.sleep(1)
            logger.info(f"✅ Added frame: {frame_type}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not add frame {frame_type}: {str(e)}")
            return False
    
    def handle_image_upload(self, item, order_data):
        """Handle image upload for the order"""
        try:
            # This is a placeholder - in a real implementation, you would:
            # 1. Download the image from Shopify
            # 2. Process it if needed
            # 3. Upload to Pictorem
            
            # For now, we'll assume there's a placeholder image or skip upload
            logger.info("📸 Image upload handling (placeholder)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle image upload: {str(e)}")
            return False
    
    def complete_order(self, quantity, order_data):
        """Complete the order with customer details"""
        try:
            # Set quantity if needed
            if quantity > 1:
                qty_field = self.driver.find_element(By.NAME, "quantity")
                qty_field.clear()
                qty_field.send_keys(str(quantity))
            
            # Add to cart or proceed to checkout
            add_to_cart_btn = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Order') or contains(text(), 'Add to Cart')]"
            )
            add_to_cart_btn.click()
            
            # Wait for confirmation
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'success')]"))
            )
            
            logger.info("✅ Order completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to complete order: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("🧹 WebDriver cleanup completed")

# Flask app for webhook handling
app = Flask(__name__)
automation = PictoremAutomation()

@app.route('/webhook/shopify/order', methods=['POST'])
def handle_shopify_webhook():
    """Handle incoming Shopify order webhooks"""
    try:
        # Verify webhook authenticity (recommended)
        webhook_secret = os.environ.get('SHOPIFY_WEBHOOK_SECRET')
        if webhook_secret:
            if not verify_webhook(request.data, request.headers.get('X-Shopify-Hmac-Sha256'), webhook_secret):
                logger.error("❌ Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse order data
        order_data = request.get_json()
        
        if not order_data:
            logger.error("❌ No order data received")
            return jsonify({'error': 'No order data'}), 400
        
        # Log the incoming order
        order_number = order_data.get('order_number')
        financial_status = order_data.get('financial_status')
        
        logger.info(f"📦 Received order #{order_number} with status: {financial_status}")
        
        # Only process paid orders
        if financial_status != 'paid':
            logger.info(f"⏸️ Skipping order #{order_number} - not paid yet")
            return jsonify({'message': 'Order not paid yet'}), 200
        
        # Process the order
        success = automation.place_pictorem_order(order_data)
        
        if success:
            logger.info(f"✅ Successfully processed order #{order_number}")
            return jsonify({'message': 'Order processed successfully'}), 200
        else:
            logger.error(f"❌ Failed to process order #{order_number}")
            return jsonify({'error': 'Order processing failed'}), 500
            
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def verify_webhook(data, signature, secret):
    """Verify Shopify webhook signature"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Start the Flask app
    logger.info("🚀 Starting Shopify-Pictorem automation server...")
    app.run(host='0.0.0.0', port=5000, debug=False) 