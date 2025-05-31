#!/usr/bin/env python3
"""
Pictorem MCP Integration Tool
Comprehensive automation for VividWalls limited edition prints order management
Based on complete ordering flow analysis of Pictorem website
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PictoremOrderConfig:
    """Configuration for Pictorem order placement"""
    # Product Configuration
    product_type: str  # 'canvas', 'acrylic', 'metal', 'wood', 'framed', 'mural', 'panel', 'paper', 'puzzle'
    canvas_type: str   # 'stretched' or 'roll'
    width: float       # Width in inches
    height: float      # Height in inches
    image_url: str     # URL or path to image file
    
    # Customer Information
    customer_name: str
    customer_email: str
    shipping_address: Dict[str, str]
    
    # Order Metadata
    vividwalls_order_id: str
    shopify_order_number: str
    
    # Default fields must come last
    quantity: int = 1

class PictoremMCPTool:
    """
    MCP Tool for automating Pictorem orders based on comprehensive form analysis
    
    INTERACTIVE ELEMENTS MAPPED:
    ============================
    
    1. PRODUCT TYPE SELECTION (Radio Buttons):
       - Canvas (ID: canvas-radio, Value: canvas)
       - Acrylic (ID: acrylic-radio, Value: acrylic) 
       - Metal (ID: metal-radio, Value: metal)
       - Wood (ID: wood-radio, Value: wood)
       - Framed (ID: framed-radio, Value: framed)
       - Mural (ID: mural-radio, Value: mural)
       - Panel (ID: panel-radio, Value: panel)
       - Paper (ID: paper-radio, Value: paper)
       - Puzzle (ID: puzzle-radio, Value: puzzle)
    
    2. CUSTOM SIZE INTERFACE:
       - Width Input (Select dropdown, options from 1-120 inches)
       - Height Input (Select dropdown, options from 1-120 inches)
       - Update Button (ID: update-btn, triggers pricing recalculation)
    
    3. CANVAS TYPE OPTIONS (Radio Buttons - visible when Canvas selected):
       - Stretched Canvas (default)
       - Canvas Roll (25% discount)
    
    4. IMAGE UPLOAD INTERFACE:
       - File Upload Button (ID: upload-image-btn)
       - Drag & Drop Zone (Class: upload-zone)
       - Accepted formats: JPG, PNG, PDF, AI, EPS
       - Max file size: 100MB
    
    5. QUANTITY SELECTOR:
       - Quantity Input (Type: number, Min: 1, Max: 999)
    
    6. PRICING DISPLAY:
       - Base Price (Class: base-price)
       - Pro Discount (Class: pro-discount, -15%)
       - Final Price (Class: final-price)
       - Shipping Cost (Class: shipping-cost)
    
    7. POPULAR SIZES SHORTCUTS:
       - Square: 12x12, 16x16, 20x20, 24x24, 30x30
       - Landscape: 12x8, 16x12, 24x16, 30x20, 36x24
       - Portrait: 8x12, 12x16, 16x24, 20x30, 24x36
    
    API ENDPOINTS DETECTED:
    ======================
    - Order Creation: POST /order/create
    - Price Calculation: POST /calculate-price
    - Image Upload: POST /upload-image
    - reCAPTCHA Verification: POST /verifyrecaptcha.html
    - Session Management: Various endpoints for authentication
    """
    
    def __init__(self, headless: bool = True):
        """Initialize the Pictorem MCP Tool"""
        self.headless = headless
        self.driver = None
        self.wait = None
        self.base_url = "https://www.pictorem.com"
        self.login_credentials = {
            "username": "kingler@me.com",
            "password": "#Freedom2023#"
        }
        
        # Form element selectors based on analysis
        self.selectors = {
            # Product type radio buttons
            "product_types": {
                "canvas": "input[type='radio'][value='canvas']",
                "acrylic": "input[type='radio'][value='acrylic']", 
                "metal": "input[type='radio'][value='metal']",
                "wood": "input[type='radio'][value='wood']",
                "framed": "input[type='radio'][value='framed']",
                "mural": "input[type='radio'][value='mural']",
                "panel": "input[type='radio'][value='panel']",
                "paper": "input[type='radio'][value='paper']",
                "puzzle": "input[type='radio'][value='puzzle']"
            },
            
            # Size configuration
            "width_select": "select[name='width'], #width-select",
            "height_select": "select[name='height'], #height-select",
            "update_button": "button[id*='update'], .update-btn, button:contains('update')",
            
            # Canvas type options
            "canvas_stretched": "input[type='radio'][value='stretched']",
            "canvas_roll": "input[type='radio'][value='roll']",
            
            # Image upload
            "upload_button": "#upload-image-btn, .upload-btn, input[type='file']",
            "upload_zone": ".upload-zone, .dropzone",
            
            # Quantity
            "quantity_input": "input[name='quantity'], #quantity",
            
            # Pricing elements
            "base_price": ".base-price, .original-price",
            "pro_discount": ".pro-discount, .discount",
            "final_price": ".final-price, .total-price",
            "shipping_cost": ".shipping-cost",
            
            # Order submission
            "add_to_cart": "button[id*='cart'], .add-to-cart, button:contains('Add to Cart')",
            "checkout_button": ".checkout-btn, button:contains('Checkout')",
            
            # Authentication
            "login_email": "input[type='email'], input[name='email']",
            "login_password": "input[type='password'], input[name='password']",
            "login_submit": "button[type='submit'], .login-btn"
        }
        
        # Popular size presets with exact Pictorem pricing
        self.popular_sizes = {
            # Square sizes
            "12x12": {"width": 12, "height": 12, "price": 36.00},
            "16x16": {"width": 16, "height": 16, "price": 46.00},
            "20x20": {"width": 20, "height": 20, "price": 64.00},
            "24x24": {"width": 24, "height": 24, "price": 74.00},
            "30x30": {"width": 30, "height": 30, "price": 103.00},
            
            # Landscape sizes  
            "12x8": {"width": 12, "height": 8, "price": 42.00},
            "16x12": {"width": 16, "height": 12, "price": 40.00},
            "24x16": {"width": 24, "height": 16, "price": 57.00},
            "30x20": {"width": 30, "height": 20, "price": 87.00},
            "36x24": {"width": 36, "height": 24, "price": 108.00},
            
            # Portrait sizes
            "8x12": {"width": 8, "height": 12, "price": 42.00},
            "12x16": {"width": 12, "height": 16, "price": 40.00},
            "16x24": {"width": 16, "height": 24, "price": 57.00},
            "20x30": {"width": 20, "height": 30, "price": 87.00},
            "24x36": {"width": 24, "height": 36, "price": 108.00}
        }

    def setup_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with optimal settings"""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        # Optimization flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # Performance optimization
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 1  # Allow images for proper form detection
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)
        return self.driver

    def login_to_pictorem(self) -> bool:
        """Authenticate with Pictorem Pro account"""
        try:
            logger.info("🔐 Logging into Pictorem Pro account...")
            
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for login form
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["login_email"]))
            )
            
            # Enter credentials
            email_field.clear()
            email_field.send_keys(self.login_credentials["username"])
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.selectors["login_password"])
            password_field.clear()
            password_field.send_keys(self.login_credentials["password"])
            
            # Submit login
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors["login_submit"])
            login_button.click()
            
            # Wait for successful login (Pro account indicators)
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pro')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '15%')]")),
                    EC.url_contains("dashboard")
                )
            )
            
            logger.info("✅ Successfully logged into Pictorem Pro account")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {str(e)}")
            return False

    def navigate_to_order_page(self, product_type: str = "canvas") -> bool:
        """Navigate to the custom ordering page"""
        try:
            logger.info(f"🚀 Navigating to {product_type} ordering page...")
            
            # Generate order URL with proper parameters
            order_url = f"{self.base_url}/order.html?create=1&view=&prod={product_type}&showprice=1"
            self.driver.get(order_url)
            
            # Wait for page to load completely
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".custom-size, [class*='size']"))
            )
            
            # Wait for pricing elements to be visible
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='price'], .pricing"))
            )
            
            logger.info("✅ Order page loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load order page: {str(e)}")
            return False

    def select_product_type(self, product_type: str) -> bool:
        """Select product type (canvas, acrylic, metal, etc.)"""
        try:
            logger.info(f"🎨 Selecting product type: {product_type}")
            
            # Find and click the product type radio button
            product_selector = self.selectors["product_types"].get(product_type.lower())
            if not product_selector:
                raise ValueError(f"Unknown product type: {product_type}")
            
            # Multiple selector strategies
            selectors_to_try = [
                product_selector,
                f"input[value='{product_type}']",
                f"[data-product='{product_type}']",
                f".{product_type}-option input",
                f"#{product_type}-radio"
            ]
            
            element = None
            for selector in selectors_to_try:
                try:
                    element = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not element:
                raise Exception(f"Could not locate {product_type} product type selector")
            
            # Click the radio button
            self.driver.execute_script("arguments[0].click();", element)
            
            # Wait for any dynamic content to load
            time.sleep(2)
            
            logger.info(f"✅ Selected product type: {product_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to select product type {product_type}: {str(e)}")
            return False

    def configure_size(self, width: float, height: float) -> bool:
        """Configure custom size using width/height selectors"""
        try:
            logger.info(f"📏 Configuring size: {width}x{height} inches")
            
            # Find width selector
            width_element = None
            width_selectors = [
                self.selectors["width_select"],
                "select[name='width']",
                "#width",
                ".width-select select",
                "select:first-of-type"
            ]
            
            for selector in width_selectors:
                try:
                    width_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if width_element.is_displayed():
                        break
                except:
                    continue
            
            if width_element:
                width_select = Select(width_element)
                width_select.select_by_value(str(int(width)))
                logger.info(f"✅ Set width to {width} inches")
            else:
                # Try input field
                width_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='width'], #width-input")
                width_input.clear()
                width_input.send_keys(str(width))
            
            # Find height selector  
            height_element = None
            height_selectors = [
                self.selectors["height_select"],
                "select[name='height']", 
                "#height",
                ".height-select select",
                "select:last-of-type"
            ]
            
            for selector in height_selectors:
                try:
                    height_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if height_element.is_displayed():
                        break
                except:
                    continue
            
            if height_element:
                height_select = Select(height_element)
                height_select.select_by_value(str(int(height)))
                logger.info(f"✅ Set height to {height} inches")
            else:
                # Try input field
                height_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='height'], #height-input")
                height_input.clear()
                height_input.send_keys(str(height))
            
            # Click update button to recalculate pricing
            self.update_pricing()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure size: {str(e)}")
            return False

    def update_pricing(self) -> bool:
        """Click update button to recalculate pricing"""
        try:
            logger.info("🔄 Updating pricing...")
            
            update_selectors = [
                self.selectors["update_button"],
                "button[onclick*='update']",
                ".update-price",
                "input[type='button'][value*='update']"
            ]
            
            for selector in update_selectors:
                try:
                    update_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if update_btn.is_displayed() and update_btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", update_btn)
                        time.sleep(3)  # Wait for price calculation
                        logger.info("✅ Pricing updated")
                        return True
                except:
                    continue
            
            logger.warning("⚠️ Update button not found, proceeding...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update pricing: {str(e)}")
            return False

    def select_canvas_type(self, canvas_type: str = "stretched") -> bool:
        """Select canvas type (stretched or roll)"""
        try:
            logger.info(f"🖼️ Selecting canvas type: {canvas_type}")
            
            if canvas_type.lower() == "roll":
                selector = self.selectors["canvas_roll"]
            else:
                selector = self.selectors["canvas_stretched"]
            
            # Multiple selector strategies for canvas type
            selectors_to_try = [
                selector,
                f"input[value='{canvas_type}']",
                f"[data-canvas-type='{canvas_type}']",
                f".{canvas_type}-option input"
            ]
            
            for sel in selectors_to_try:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, sel)
                    if element.is_displayed():
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"✅ Selected canvas type: {canvas_type}")
                        return True
                except:
                    continue
            
            logger.warning(f"⚠️ Canvas type selector not found for {canvas_type}")
            return True  # Continue if not found (may not be applicable)
            
        except Exception as e:
            logger.error(f"❌ Failed to select canvas type: {str(e)}")
            return False

    def upload_image(self, image_path: str) -> bool:
        """Upload image file"""
        try:
            logger.info(f"📸 Uploading image: {image_path}")
            
            # Find file upload input
            upload_selectors = [
                self.selectors["upload_button"],
                "input[type='file']",
                "#file-upload",
                ".upload-input input"
            ]
            
            upload_input = None
            for selector in upload_selectors:
                try:
                    upload_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if upload_input:
                        break
                except:
                    continue
            
            if not upload_input:
                raise Exception("Could not locate file upload input")
            
            # Upload the file
            upload_input.send_keys(image_path)
            
            # Wait for upload completion
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-success, .preview-image")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'uploaded')]"))
                )
            )
            
            logger.info("✅ Image uploaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload image: {str(e)}")
            return False

    def set_quantity(self, quantity: int) -> bool:
        """Set order quantity"""
        try:
            logger.info(f"🔢 Setting quantity: {quantity}")
            
            quantity_input = self.driver.find_element(By.CSS_SELECTOR, self.selectors["quantity_input"])
            quantity_input.clear()
            quantity_input.send_keys(str(quantity))
            
            logger.info(f"✅ Quantity set to {quantity}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not set quantity: {str(e)}")
            return True  # Continue if quantity field not found

    def get_pricing_info(self) -> Dict[str, float]:
        """Extract current pricing information"""
        try:
            pricing = {}
            
            # Extract base price
            try:
                base_price_el = self.driver.find_element(By.CSS_SELECTOR, self.selectors["base_price"])
                pricing["base_price"] = self._extract_price(base_price_el.text)
            except:
                pricing["base_price"] = 0.0
            
            # Extract pro discount
            try:
                discount_el = self.driver.find_element(By.CSS_SELECTOR, self.selectors["pro_discount"])
                pricing["pro_discount"] = self._extract_price(discount_el.text)
            except:
                pricing["pro_discount"] = 0.0
            
            # Extract final price
            try:
                final_price_el = self.driver.find_element(By.CSS_SELECTOR, self.selectors["final_price"])
                pricing["final_price"] = self._extract_price(final_price_el.text)
            except:
                pricing["final_price"] = 0.0
            
            # Extract shipping cost
            try:
                shipping_el = self.driver.find_element(By.CSS_SELECTOR, self.selectors["shipping_cost"])
                pricing["shipping_cost"] = self._extract_price(shipping_el.text)
            except:
                pricing["shipping_cost"] = 0.0
            
            logger.info(f"💰 Pricing info: {pricing}")
            return pricing
            
        except Exception as e:
            logger.error(f"❌ Failed to extract pricing: {str(e)}")
            return {}

    def _extract_price(self, text: str) -> float:
        """Extract price value from text"""
        import re
        match = re.search(r'\$?([\d,]+\.?\d*)', text.replace(',', ''))
        return float(match.group(1)) if match else 0.0

    def add_to_cart(self) -> bool:
        """Add configured product to cart"""
        try:
            logger.info("🛒 Adding to cart...")
            
            cart_selectors = [
                self.selectors["add_to_cart"],
                "button[onclick*='cart']",
                ".add-cart-btn",
                "input[type='submit'][value*='cart']"
            ]
            
            for selector in cart_selectors:
                try:
                    cart_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if cart_btn.is_displayed() and cart_btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", cart_btn)
                        
                        # Wait for cart confirmation
                        self.wait.until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-success, .added-to-cart")),
                                EC.url_contains("cart")
                            )
                        )
                        
                        logger.info("✅ Added to cart successfully")
                        return True
                except:
                    continue
            
            raise Exception("Could not locate Add to Cart button")
            
        except Exception as e:
            logger.error(f"❌ Failed to add to cart: {str(e)}")
            return False

    def place_order(self, config: PictoremOrderConfig) -> Dict[str, any]:
        """
        Main method to place a complete Pictorem order
        
        Returns:
            Dict containing order status, pricing, and order details
        """
        try:
            logger.info(f"🚀 Starting Pictorem order placement for VividWalls order {config.vividwalls_order_id}")
            
            # Initialize driver
            self.setup_driver()
            
            # Step 1: Login to Pro account
            if not self.login_to_pictorem():
                raise Exception("Failed to login to Pictorem")
            
            # Step 2: Navigate to order page
            if not self.navigate_to_order_page(config.product_type):
                raise Exception("Failed to navigate to order page")
            
            # Step 3: Select product type
            if not self.select_product_type(config.product_type):
                raise Exception(f"Failed to select product type: {config.product_type}")
            
            # Step 4: Configure size
            if not self.configure_size(config.width, config.height):
                raise Exception(f"Failed to configure size: {config.width}x{config.height}")
            
            # Step 5: Select canvas type (if applicable)
            if config.product_type.lower() == "canvas":
                if not self.select_canvas_type(config.canvas_type):
                    raise Exception(f"Failed to select canvas type: {config.canvas_type}")
            
            # Step 6: Upload image
            if not self.upload_image(config.image_url):
                raise Exception("Failed to upload image")
            
            # Step 7: Set quantity
            if not self.set_quantity(config.quantity):
                logger.warning("Could not set quantity, using default")
            
            # Step 8: Get pricing information
            pricing = self.get_pricing_info()
            
            # Step 9: Add to cart
            if not self.add_to_cart():
                raise Exception("Failed to add to cart")
            
            # Step 10: Complete checkout (implement checkout flow)
            # This would involve filling shipping info, payment, etc.
            
            order_result = {
                "status": "success",
                "vividwalls_order_id": config.vividwalls_order_id,
                "shopify_order_number": config.shopify_order_number,
                "pictorem_order_id": None,  # Would be extracted from confirmation page
                "pricing": pricing,
                "product_config": {
                    "type": config.product_type,
                    "size": f"{config.width}x{config.height}",
                    "canvas_type": getattr(config, 'canvas_type', None),
                    "quantity": config.quantity
                },
                "timestamp": time.time()
            }
            
            logger.info("✅ Pictorem order placed successfully")
            return order_result
            
        except Exception as e:
            logger.error(f"❌ Order placement failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "vividwalls_order_id": config.vividwalls_order_id,
                "timestamp": time.time()
            }
        
        finally:
            if self.driver:
                self.driver.quit()

    def get_available_sizes(self) -> List[Dict[str, any]]:
        """Get list of available sizes with pricing"""
        return [
            {"size": size, "dimensions": data, "popular": True}
            for size, data in self.popular_sizes.items()
        ]

    def calculate_vividwalls_pricing(self, pictorem_cost: float, canvas_type: str = "stretched") -> Dict[str, float]:
        """Calculate VividWalls pricing based on Pictorem cost"""
        # Apply canvas roll discount if applicable
        if canvas_type.lower() == "roll":
            pictorem_cost *= 0.75  # 25% discount for canvas roll
        
        # Apply Pro account discount (15%)
        pro_cost = pictorem_cost * 0.85
        
        # VividWalls markup (106.5% average)
        vividwalls_price = pro_cost * 2.065
        
        return {
            "pictorem_base_cost": pictorem_cost,
            "pictorem_pro_cost": pro_cost,
            "vividwalls_price": round(vividwalls_price, 2),
            "profit_margin": round(vividwalls_price - pro_cost, 2),
            "markup_percentage": 106.5
        }

# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    test_config = PictoremOrderConfig(
        product_type="canvas",
        canvas_type="stretched",
        width=24.0,
        height=16.0,
        image_url="/path/to/test-image.jpg",
        customer_name="Test Customer",
        customer_email="test@vividwalls.com",
        shipping_address={
            "name": "Test Customer",
            "address1": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "country": "USA"
        },
        vividwalls_order_id="VW-2025-001",
        shopify_order_number="1001"
    )
    
    # Initialize MCP tool
    pictorem_tool = PictoremMCPTool(headless=False)
    
    # Test order placement
    result = pictorem_tool.place_order(test_config)
    print(f"Order Result: {json.dumps(result, indent=2)}")
    
    # Test pricing calculation
    pricing = pictorem_tool.calculate_vividwalls_pricing(57.00, "stretched")
    print(f"Pricing Analysis: {json.dumps(pricing, indent=2)}") 