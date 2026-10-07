#!/usr/bin/env python3
"""
Test Suite for Pictorem MCP Integration
Following TDD principles - tests define expected functionality
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from pictorem_mcp_integration import PictoremMCPTool, PictoremOrderConfig

class TestPictoremOrderConfig:
    """Test the PictoremOrderConfig dataclass"""
    
    def test_config_creation_with_required_fields(self):
        """Test that PictoremOrderConfig can be created with all required fields"""
        config = PictoremOrderConfig(
            product_type="canvas",
            canvas_type="stretched", 
            width=24.0,
            height=16.0,
            image_url="/path/to/test.jpg",
            customer_name="Test Customer",
            customer_email="test@example.com",
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
        
        assert config.product_type == "canvas"
        assert config.canvas_type == "stretched"
        assert config.width == 24.0
        assert config.height == 16.0
        assert config.quantity == 1  # Default value
        assert config.vividwalls_order_id == "VW-2025-001"
        assert config.shopify_order_number == "1001"

    def test_config_with_custom_quantity(self):
        """Test that quantity can be customized"""
        config = PictoremOrderConfig(
            product_type="canvas",
            canvas_type="stretched",
            width=12.0,
            height=12.0,
            image_url="/path/to/test.jpg",
            quantity=5,
            customer_name="Test Customer",
            customer_email="test@example.com", 
            shipping_address={},
            vividwalls_order_id="VW-2025-002",
            shopify_order_number="1002"
        )
        
        assert config.quantity == 5


class TestPictoremMCPToolInitialization:
    """Test PictoremMCPTool initialization and setup"""
    
    def test_tool_initialization_headless_default(self):
        """Test that tool initializes with headless=True by default"""
        tool = PictoremMCPTool()
        
        assert tool.headless is True
        assert tool.driver is None
        assert tool.wait is None
        assert tool.base_url == "https://www.pictorem.com"
        assert "username" in tool.login_credentials
        assert "password" in tool.login_credentials

    def test_tool_initialization_headless_false(self):
        """Test that tool can be initialized with headless=False"""
        tool = PictoremMCPTool(headless=False)
        
        assert tool.headless is False

    def test_selectors_are_properly_defined(self):
        """Test that all required selectors are defined"""
        tool = PictoremMCPTool()
        
        # Test product type selectors
        expected_product_types = [
            "canvas", "acrylic", "metal", "wood", "framed",
            "mural", "panel", "paper", "puzzle"
        ]
        
        for product_type in expected_product_types:
            assert product_type in tool.selectors["product_types"]
            assert tool.selectors["product_types"][product_type] is not None

        # Test critical selectors exist
        critical_selectors = [
            "width_select", "height_select", "update_button",
            "canvas_stretched", "canvas_roll", "upload_button",
            "quantity_input", "base_price", "final_price",
            "add_to_cart", "login_email", "login_password"
        ]
        
        for selector in critical_selectors:
            assert selector in tool.selectors
            assert tool.selectors[selector] is not None

    def test_popular_sizes_are_defined(self):
        """Test that popular sizes with pricing are properly defined"""
        tool = PictoremMCPTool()
        
        # Test that popular sizes exist
        expected_sizes = [
            "12x12", "16x16", "20x20", "24x24", "30x30",  # Square
            "12x8", "16x12", "24x16", "30x20", "36x24",   # Landscape
            "8x12", "12x16", "16x24", "20x30", "24x36"    # Portrait
        ]
        
        for size in expected_sizes:
            assert size in tool.popular_sizes
            assert "width" in tool.popular_sizes[size]
            assert "height" in tool.popular_sizes[size]
            assert "price" in tool.popular_sizes[size]
            assert tool.popular_sizes[size]["price"] > 0


class TestPictoremMCPToolDriverSetup:
    """Test WebDriver setup and configuration"""
    
    @patch('pictorem_mcp_integration.webdriver.Chrome')
    @patch('pictorem_mcp_integration.WebDriverWait')
    def test_setup_driver_headless_true(self, mock_wait, mock_chrome):
        """Test driver setup with headless=True"""
        tool = PictoremMCPTool(headless=True)
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        result = tool.setup_driver()
        
        # Verify Chrome was called with options
        mock_chrome.assert_called_once()
        args, kwargs = mock_chrome.call_args
        options = args[0] if args else kwargs.get('options')
        
        # Verify driver and wait are set
        assert tool.driver == mock_driver
        assert result == mock_driver
        mock_wait.assert_called_once_with(mock_driver, 30)

    @patch('pictorem_mcp_integration.webdriver.Chrome')
    @patch('pictorem_mcp_integration.WebDriverWait')
    def test_setup_driver_headless_false(self, mock_wait, mock_chrome):
        """Test driver setup with headless=False"""
        tool = PictoremMCPTool(headless=False)
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        result = tool.setup_driver()
        
        # Verify Chrome was called
        mock_chrome.assert_called_once()
        assert tool.driver == mock_driver
        assert result == mock_driver


class TestPictoremMCPToolAuthentication:
    """Test authentication functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_login_to_pictorem_success(self):
        """Test successful login to Pictorem"""
        # Setup mocks for successful login
        mock_email_field = Mock()
        mock_password_field = Mock()
        mock_login_button = Mock()
        
        self.tool.wait.until.return_value = mock_email_field
        self.tool.driver.find_element.side_effect = [mock_password_field, mock_login_button]
        
        # Mock successful login detection
        self.tool.wait.until.side_effect = [mock_email_field, None]  # Second call succeeds
        
        result = self.tool.login_to_pictorem()
        
        # Verify login flow
        assert result is True
        self.tool.driver.get.assert_called_with("https://www.pictorem.com/login")
        mock_email_field.clear.assert_called_once()
        mock_email_field.send_keys.assert_called_with("kingler@me.com")
        mock_password_field.clear.assert_called_once()
        mock_password_field.send_keys.assert_called_with("REDACTED_SET_PICTOREM_PASSWORD_ENV")
        mock_login_button.click.assert_called_once()

    def test_login_to_pictorem_failure(self):
        """Test failed login to Pictorem"""
        # Setup mocks for failed login
        self.tool.wait.until.side_effect = TimeoutException("Login failed")
        
        result = self.tool.login_to_pictorem()
        
        assert result is False

    def test_login_credentials_are_correct(self):
        """Test that login credentials are properly configured"""
        assert self.tool.login_credentials["username"] == "kingler@me.com"
        assert self.tool.login_credentials["password"] == "REDACTED_SET_PICTOREM_PASSWORD_ENV"


class TestPictoremMCPToolNavigation:
    """Test navigation functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_navigate_to_order_page_canvas(self):
        """Test navigation to canvas order page"""
        # Mock successful page load
        self.tool.wait.until.return_value = Mock()
        
        result = self.tool.navigate_to_order_page("canvas")
        
        expected_url = "https://www.pictorem.com/order.html?create=1&view=&prod=canvas&showprice=1"
        self.tool.driver.get.assert_called_with(expected_url)
        assert result is True

    def test_navigate_to_order_page_other_products(self):
        """Test navigation to other product order pages"""
        self.tool.wait.until.return_value = Mock()
        
        for product_type in ["acrylic", "metal", "wood"]:
            result = self.tool.navigate_to_order_page(product_type)
            expected_url = f"https://www.pictorem.com/order.html?create=1&view=&prod={product_type}&showprice=1"
            assert result is True

    def test_navigate_to_order_page_failure(self):
        """Test failed navigation to order page"""
        self.tool.wait.until.side_effect = TimeoutException("Page load failed")
        
        result = self.tool.navigate_to_order_page("canvas")
        
        assert result is False


class TestPictoremMCPToolProductSelection:
    """Test product type selection functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_select_product_type_canvas(self):
        """Test selecting canvas product type"""
        mock_element = Mock()
        self.tool.wait.until.return_value = mock_element
        
        result = self.tool.select_product_type("canvas")
        
        assert result is True
        self.tool.driver.execute_script.assert_called_with("arguments[0].click();", mock_element)

    def test_select_product_type_all_types(self):
        """Test selecting all supported product types"""
        mock_element = Mock()
        self.tool.wait.until.return_value = mock_element
        
        product_types = ["canvas", "acrylic", "metal", "wood", "framed", "mural", "panel", "paper", "puzzle"]
        
        for product_type in product_types:
            result = self.tool.select_product_type(product_type)
            assert result is True

    def test_select_product_type_invalid(self):
        """Test selecting invalid product type"""
        result = self.tool.select_product_type("invalid_type")
        
        assert result is False

    def test_select_product_type_element_not_found(self):
        """Test handling when product type element is not found"""
        self.tool.wait.until.side_effect = TimeoutException("Element not found")
        
        result = self.tool.select_product_type("canvas")
        
        assert result is False


class TestPictoremMCPToolSizeConfiguration:
    """Test size configuration functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_configure_size_with_selects(self):
        """Test configuring size using select dropdowns"""
        mock_width_element = Mock()
        mock_height_element = Mock()
        
        # Mock finding select elements
        self.tool.driver.find_element.side_effect = [mock_width_element, mock_height_element]
        mock_width_element.is_displayed.return_value = True
        mock_height_element.is_displayed.return_value = True
        
        with patch('pictorem_mcp_integration.Select') as mock_select:
            mock_width_select = Mock()
            mock_height_select = Mock()
            mock_select.side_effect = [mock_width_select, mock_height_select]
            
            # Mock update_pricing method
            with patch.object(self.tool, 'update_pricing', return_value=True):
                result = self.tool.configure_size(24.0, 16.0)
            
            assert result is True
            mock_width_select.select_by_value.assert_called_with("24")
            mock_height_select.select_by_value.assert_called_with("16")

    def test_configure_size_with_inputs(self):
        """Test configuring size using input fields"""
        # Mock select elements not found, use inputs
        mock_width_input = Mock()
        mock_height_input = Mock()
        
        def find_element_side_effect(by, selector):
            if "select" in selector or "Select" in selector:
                # Mock select elements not being found
                raise Exception("Select not found")
            elif "width" in selector and "input" in selector:
                return mock_width_input
            elif "height" in selector and "input" in selector:
                return mock_height_input
            raise Exception("Element not found")
        
        self.tool.driver.find_element.side_effect = find_element_side_effect
        
        with patch.object(self.tool, 'update_pricing', return_value=True):
            result = self.tool.configure_size(30.0, 20.0)
        
        assert result is True
        mock_width_input.clear.assert_called_once()
        mock_width_input.send_keys.assert_called_with("30.0")
        mock_height_input.clear.assert_called_once()
        mock_height_input.send_keys.assert_called_with("20.0")

    def test_configure_size_failure(self):
        """Test size configuration failure"""
        self.tool.driver.find_element.side_effect = Exception("Elements not found")
        
        result = self.tool.configure_size(24.0, 16.0)
        
        assert result is False

    def test_update_pricing_success(self):
        """Test successful pricing update"""
        mock_button = Mock()
        mock_button.is_displayed.return_value = True
        mock_button.is_enabled.return_value = True
        
        self.tool.driver.find_element.return_value = mock_button
        
        result = self.tool.update_pricing()
        
        assert result is True
        self.tool.driver.execute_script.assert_called_with("arguments[0].click();", mock_button)

    def test_update_pricing_button_not_found(self):
        """Test pricing update when button not found"""
        self.tool.driver.find_element.side_effect = Exception("Button not found")
        
        result = self.tool.update_pricing()
        
        # Should return True (continue) even if button not found
        assert result is True


class TestPictoremMCPToolCanvasTypeSelection:
    """Test canvas type selection functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_select_canvas_type_stretched(self):
        """Test selecting stretched canvas type"""
        mock_element = Mock()
        mock_element.is_displayed.return_value = True
        
        self.tool.driver.find_element.return_value = mock_element
        
        result = self.tool.select_canvas_type("stretched")
        
        assert result is True
        self.tool.driver.execute_script.assert_called_with("arguments[0].click();", mock_element)

    def test_select_canvas_type_roll(self):
        """Test selecting canvas roll type"""
        mock_element = Mock()
        mock_element.is_displayed.return_value = True
        
        self.tool.driver.find_element.return_value = mock_element
        
        result = self.tool.select_canvas_type("roll")
        
        assert result is True
        self.tool.driver.execute_script.assert_called_with("arguments[0].click();", mock_element)

    def test_select_canvas_type_not_found(self):
        """Test canvas type selection when element not found"""
        self.tool.driver.find_element.side_effect = Exception("Element not found")
        
        result = self.tool.select_canvas_type("stretched")
        
        # Should return True (continue) even if not found
        assert result is True


class TestPictoremMCPToolImageUpload:
    """Test image upload functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_upload_image_success(self):
        """Test successful image upload"""
        mock_upload_input = Mock()
        self.tool.driver.find_element.return_value = mock_upload_input
        self.tool.wait.until.return_value = Mock()
        
        result = self.tool.upload_image("/path/to/test-image.jpg")
        
        assert result is True
        mock_upload_input.send_keys.assert_called_with("/path/to/test-image.jpg")

    def test_upload_image_input_not_found(self):
        """Test image upload when input not found"""
        self.tool.driver.find_element.side_effect = Exception("Input not found")
        
        result = self.tool.upload_image("/path/to/test-image.jpg")
        
        assert result is False

    def test_upload_image_upload_fails(self):
        """Test image upload failure"""
        mock_upload_input = Mock()
        self.tool.driver.find_element.return_value = mock_upload_input
        self.tool.wait.until.side_effect = TimeoutException("Upload failed")
        
        result = self.tool.upload_image("/path/to/test-image.jpg")
        
        assert result is False


class TestPictoremMCPToolQuantityManagement:
    """Test quantity management functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_set_quantity_success(self):
        """Test successful quantity setting"""
        mock_quantity_input = Mock()
        self.tool.driver.find_element.return_value = mock_quantity_input
        
        result = self.tool.set_quantity(5)
        
        assert result is True
        mock_quantity_input.clear.assert_called_once()
        mock_quantity_input.send_keys.assert_called_with("5")

    def test_set_quantity_input_not_found(self):
        """Test quantity setting when input not found"""
        self.tool.driver.find_element.side_effect = Exception("Input not found")
        
        result = self.tool.set_quantity(3)
        
        # Should return True (continue) even if quantity input not found
        assert result is True


class TestPictoremMCPToolPricingExtraction:
    """Test pricing information extraction"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_get_pricing_info_success(self):
        """Test successful pricing extraction"""
        # Mock pricing elements
        mock_base_price = Mock()
        mock_base_price.text = "$57.00"
        
        mock_discount = Mock()
        mock_discount.text = "-$8.55"
        
        mock_final_price = Mock()
        mock_final_price.text = "$48.45"
        
        mock_shipping = Mock()
        mock_shipping.text = "$15.99"
        
        def find_element_side_effect(by, selector):
            if "base-price" in selector or "original-price" in selector:
                return mock_base_price
            elif "pro-discount" in selector or "discount" in selector:
                return mock_discount
            elif "final-price" in selector or "total-price" in selector:
                return mock_final_price
            elif "shipping-cost" in selector:
                return mock_shipping
            raise Exception("Element not found")
        
        self.tool.driver.find_element.side_effect = find_element_side_effect
        
        result = self.tool.get_pricing_info()
        
        expected = {
            "base_price": 57.00,
            "pro_discount": 8.55,
            "final_price": 48.45,
            "shipping_cost": 15.99
        }
        
        assert result == expected

    def test_extract_price_various_formats(self):
        """Test price extraction from various text formats"""
        test_cases = [
            ("$57.00", 57.00),
            ("57.00", 57.00),
            ("$1,234.56", 1234.56),
            ("Price: $89.99", 89.99),
            ("Total $0.00", 0.00),
            ("No price here", 0.0)
        ]
        
        for text, expected in test_cases:
            result = self.tool._extract_price(text)
            assert result == expected

    def test_get_pricing_info_elements_not_found(self):
        """Test pricing extraction when elements not found"""
        self.tool.driver.find_element.side_effect = Exception("Elements not found")
        
        result = self.tool.get_pricing_info()
        
        expected = {
            "base_price": 0.0,
            "pro_discount": 0.0, 
            "final_price": 0.0,
            "shipping_cost": 0.0
        }
        
        assert result == expected


class TestPictoremMCPToolCartManagement:
    """Test cart management functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.tool.driver = Mock()
        self.tool.wait = Mock()

    def test_add_to_cart_success(self):
        """Test successful add to cart"""
        mock_cart_button = Mock()
        mock_cart_button.is_displayed.return_value = True
        mock_cart_button.is_enabled.return_value = True
        
        self.tool.driver.find_element.return_value = mock_cart_button
        self.tool.wait.until.return_value = Mock()
        
        result = self.tool.add_to_cart()
        
        assert result is True
        self.tool.driver.execute_script.assert_called_with("arguments[0].click();", mock_cart_button)

    def test_add_to_cart_button_not_found(self):
        """Test add to cart when button not found"""
        self.tool.driver.find_element.side_effect = Exception("Button not found")
        
        result = self.tool.add_to_cart()
        
        assert result is False

    def test_add_to_cart_confirmation_timeout(self):
        """Test add to cart when confirmation times out"""
        mock_cart_button = Mock()
        mock_cart_button.is_displayed.return_value = True
        mock_cart_button.is_enabled.return_value = True
        
        self.tool.driver.find_element.return_value = mock_cart_button
        self.tool.wait.until.side_effect = TimeoutException("Confirmation timeout")
        
        result = self.tool.add_to_cart()
        
        assert result is False


class TestPictoremMCPToolPricingCalculations:
    """Test VividWalls pricing calculations"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()

    def test_calculate_vividwalls_pricing_stretched(self):
        """Test VividWalls pricing calculation for stretched canvas"""
        pictorem_cost = 57.00
        
        result = self.tool.calculate_vividwalls_pricing(pictorem_cost, "stretched")
        
        expected_pro_cost = 57.00 * 0.85  # 15% discount
        expected_vividwalls_price = expected_pro_cost * 2.065  # 106.5% markup
        expected_profit = expected_vividwalls_price - expected_pro_cost
        
        assert result["pictorem_base_cost"] == 57.00
        assert result["pictorem_pro_cost"] == expected_pro_cost
        assert result["vividwalls_price"] == round(expected_vividwalls_price, 2)
        assert result["profit_margin"] == round(expected_profit, 2)
        assert result["markup_percentage"] == 106.5

    def test_calculate_vividwalls_pricing_roll(self):
        """Test VividWalls pricing calculation for canvas roll"""
        pictorem_cost = 57.00
        
        result = self.tool.calculate_vividwalls_pricing(pictorem_cost, "roll")
        
        expected_roll_cost = 57.00 * 0.75  # 25% roll discount
        expected_pro_cost = expected_roll_cost * 0.85  # 15% Pro discount
        expected_vividwalls_price = expected_pro_cost * 2.065
        expected_profit = expected_vividwalls_price - expected_pro_cost
        
        assert result["pictorem_base_cost"] == expected_roll_cost
        assert result["pictorem_pro_cost"] == expected_pro_cost
        assert result["vividwalls_price"] == round(expected_vividwalls_price, 2)
        assert result["profit_margin"] == round(expected_profit, 2)

    def test_get_available_sizes(self):
        """Test getting available sizes with pricing"""
        result = self.tool.get_available_sizes()
        
        assert len(result) == 15  # 15 popular sizes defined
        
        for size_info in result:
            assert "size" in size_info
            assert "dimensions" in size_info
            assert "popular" in size_info
            assert size_info["popular"] is True
            
            dimensions = size_info["dimensions"]
            assert "width" in dimensions
            assert "height" in dimensions
            assert "price" in dimensions
            assert dimensions["price"] > 0


class TestPictoremMCPToolOrderPlacement:
    """Test complete order placement workflow"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()
        self.config = PictoremOrderConfig(
            product_type="canvas",
            canvas_type="stretched",
            width=24.0,
            height=16.0,
            image_url="/path/to/test-image.jpg",
            quantity=1,
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

    @patch.object(PictoremMCPTool, 'setup_driver')
    @patch.object(PictoremMCPTool, 'login_to_pictorem')
    @patch.object(PictoremMCPTool, 'navigate_to_order_page')
    @patch.object(PictoremMCPTool, 'select_product_type')
    @patch.object(PictoremMCPTool, 'configure_size')
    @patch.object(PictoremMCPTool, 'select_canvas_type')
    @patch.object(PictoremMCPTool, 'upload_image')
    @patch.object(PictoremMCPTool, 'set_quantity')
    @patch.object(PictoremMCPTool, 'get_pricing_info')
    @patch.object(PictoremMCPTool, 'add_to_cart')
    def test_place_order_success(self, mock_add_to_cart, mock_get_pricing,
                                 mock_set_quantity, mock_upload_image,
                                 mock_select_canvas_type, mock_configure_size,
                                 mock_select_product_type, mock_navigate,
                                 mock_login, mock_setup_driver):
        """Test successful complete order placement"""
        
        # Mock all methods to return success
        mock_setup_driver.return_value = Mock()
        mock_login.return_value = True
        mock_navigate.return_value = True
        mock_select_product_type.return_value = True
        mock_configure_size.return_value = True
        mock_select_canvas_type.return_value = True
        mock_upload_image.return_value = True
        mock_set_quantity.return_value = True
        mock_get_pricing.return_value = {
            "base_price": 57.00,
            "pro_discount": 8.55,
            "final_price": 48.45,
            "shipping_cost": 15.99
        }
        mock_add_to_cart.return_value = True
        
        # Mock driver quit
        self.tool.driver = Mock()
        
        result = self.tool.place_order(self.config)
        
        # Verify successful result
        assert result["status"] == "success"
        assert result["vividwalls_order_id"] == "VW-2025-001"
        assert result["shopify_order_number"] == "1001"
        assert "pricing" in result
        assert "product_config" in result
        assert "timestamp" in result
        
        # Verify all methods were called
        mock_setup_driver.assert_called_once()
        mock_login.assert_called_once()
        mock_navigate.assert_called_once_with("canvas")
        mock_select_product_type.assert_called_once_with("canvas")
        mock_configure_size.assert_called_once_with(24.0, 16.0)
        mock_select_canvas_type.assert_called_once_with("stretched")
        mock_upload_image.assert_called_once_with("/path/to/test-image.jpg")
        mock_set_quantity.assert_called_once_with(1)
        mock_get_pricing.assert_called_once()
        mock_add_to_cart.assert_called_once()

    @patch.object(PictoremMCPTool, 'setup_driver')
    @patch.object(PictoremMCPTool, 'login_to_pictorem')
    def test_place_order_login_failure(self, mock_login, mock_setup_driver):
        """Test order placement with login failure"""
        
        mock_setup_driver.return_value = Mock()
        mock_login.return_value = False
        self.tool.driver = Mock()
        
        result = self.tool.place_order(self.config)
        
        assert result["status"] == "error"
        assert "Failed to login to Pictorem" in result["error"]
        assert result["vividwalls_order_id"] == "VW-2025-001"

    @patch.object(PictoremMCPTool, 'setup_driver')
    @patch.object(PictoremMCPTool, 'login_to_pictorem')
    @patch.object(PictoremMCPTool, 'navigate_to_order_page')
    def test_place_order_navigation_failure(self, mock_navigate, mock_login, mock_setup_driver):
        """Test order placement with navigation failure"""
        
        mock_setup_driver.return_value = Mock()
        mock_login.return_value = True
        mock_navigate.return_value = False
        self.tool.driver = Mock()
        
        result = self.tool.place_order(self.config)
        
        assert result["status"] == "error"
        assert "Failed to navigate to order page" in result["error"]

    def test_place_order_driver_cleanup(self):
        """Test that driver is properly cleaned up after order placement"""
        mock_driver = Mock()
        self.tool.driver = mock_driver
        
        # Mock setup_driver to fail
        with patch.object(self.tool, 'setup_driver', side_effect=Exception("Setup failed")):
            result = self.tool.place_order(self.config)
        
        # Verify driver.quit() was called
        mock_driver.quit.assert_called_once()
        assert result["status"] == "error"


class TestPictoremMCPToolErrorHandling:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tool = PictoremMCPTool()

    def test_invalid_product_type_handling(self):
        """Test handling of invalid product types"""
        self.tool.driver = Mock()
        self.tool.wait = Mock()
        
        result = self.tool.select_product_type("invalid_product")
        
        assert result is False

    def test_timeout_exception_handling(self):
        """Test handling of timeout exceptions"""
        self.tool.driver = Mock()
        self.tool.wait = Mock()
        self.tool.wait.until.side_effect = TimeoutException("Timeout")
        
        result = self.tool.login_to_pictorem()
        
        assert result is False

    def test_element_not_interactable_handling(self):
        """Test handling of element not interactable exceptions"""
        self.tool.driver = Mock()
        self.tool.wait = Mock()
        
        mock_element = Mock()
        mock_element.is_displayed.return_value = False
        self.tool.driver.find_element.return_value = mock_element
        
        result = self.tool.add_to_cart()
        
        assert result is False

    def test_network_error_handling(self):
        """Test handling of network errors"""
        self.tool.driver = Mock()
        self.tool.driver.get.side_effect = Exception("Network error")
        
        result = self.tool.navigate_to_order_page("canvas")
        
        assert result is False


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"]) 