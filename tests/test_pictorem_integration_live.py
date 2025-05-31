#!/usr/bin/env python3
"""
Live Integration Test for Pictorem MCP Tool
Tests actual functionality against the real Pictorem website
Run with caution - this will make real web requests and login attempts
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from pictorem_mcp_integration import PictoremMCPTool, PictoremOrderConfig

def create_test_image():
    """Create a simple test image for upload testing"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple 100x100 test image
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple test pattern
        draw.rectangle([10, 10, 90, 90], outline='black', width=2)
        draw.text((30, 40), "TEST", fill='black')
        
        test_image_path = "/tmp/pictorem_test_image.jpg"
        img.save(test_image_path, "JPEG")
        
        print(f"✅ Created test image: {test_image_path}")
        return test_image_path
        
    except ImportError:
        print("⚠️ PIL not available, creating dummy image path")
        return "/tmp/dummy_test_image.jpg"
    except Exception as e:
        print(f"⚠️ Could not create test image: {e}")
        return "/tmp/dummy_test_image.jpg"

def test_pictorem_login():
    """Test 1: Verify login functionality"""
    print("\n🔐 **TEST 1: Login Authentication**")
    
    tool = PictoremMCPTool(headless=False)  # Show browser for verification
    
    try:
        # Setup driver
        driver = tool.setup_driver()
        print("✅ Browser driver initialized")
        
        # Test login
        login_success = tool.login_to_pictorem()
        
        if login_success:
            print("✅ **LOGIN SUCCESS** - Pro account authenticated")
            
            # Take a screenshot for verification
            driver.save_screenshot("/tmp/pictorem_login_success.png")
            print("📸 Screenshot saved: /tmp/pictorem_login_success.png")
            
            return True
        else:
            print("❌ **LOGIN FAILED**")
            driver.save_screenshot("/tmp/pictorem_login_failure.png")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
        return False
    finally:
        if tool.driver:
            tool.driver.quit()

def test_pictorem_navigation():
    """Test 2: Verify navigation to order page"""
    print("\n🚀 **TEST 2: Order Page Navigation**")
    
    tool = PictoremMCPTool(headless=False)
    
    try:
        # Setup and login
        tool.setup_driver()
        if not tool.login_to_pictorem():
            print("❌ Login failed, cannot test navigation")
            return False
        
        # Test navigation to canvas order page
        nav_success = tool.navigate_to_order_page("canvas")
        
        if nav_success:
            print("✅ **NAVIGATION SUCCESS** - Canvas order page loaded")
            
            # Take screenshot
            tool.driver.save_screenshot("/tmp/pictorem_order_page.png")
            print("📸 Screenshot saved: /tmp/pictorem_order_page.png")
            
            return True
        else:
            print("❌ **NAVIGATION FAILED**")
            return False
            
    except Exception as e:
        print(f"❌ Navigation test failed: {str(e)}")
        return False
    finally:
        if tool.driver:
            tool.driver.quit()

def test_pictorem_size_configuration():
    """Test 3: Verify size configuration functionality"""
    print("\n📏 **TEST 3: Size Configuration**")
    
    tool = PictoremMCPTool(headless=False)
    
    try:
        # Setup, login, and navigate
        tool.setup_driver()
        if not tool.login_to_pictorem():
            print("❌ Login failed, cannot test size configuration")
            return False
            
        if not tool.navigate_to_order_page("canvas"):
            print("❌ Navigation failed, cannot test size configuration")
            return False
        
        # Test size configuration
        size_success = tool.configure_size(24.0, 16.0)
        
        if size_success:
            print("✅ **SIZE CONFIGURATION SUCCESS** - 24x16 inches set")
            
            # Get pricing info
            pricing = tool.get_pricing_info()
            print(f"💰 Pricing extracted: {pricing}")
            
            # Take screenshot
            tool.driver.save_screenshot("/tmp/pictorem_size_config.png")
            print("📸 Screenshot saved: /tmp/pictorem_size_config.png")
            
            return True
        else:
            print("❌ **SIZE CONFIGURATION FAILED**")
            return False
            
    except Exception as e:
        print(f"❌ Size configuration test failed: {str(e)}")
        return False
    finally:
        if tool.driver:
            tool.driver.quit()

def test_pictorem_pricing_calculation():
    """Test 4: Verify pricing calculations are working"""
    print("\n💰 **TEST 4: Pricing Calculations**")
    
    try:
        tool = PictoremMCPTool()
        
        # Test VividWalls pricing calculation for stretched canvas
        stretched_pricing = tool.calculate_vividwalls_pricing(57.00, "stretched")
        print(f"📊 Stretched Canvas Pricing: {json.dumps(stretched_pricing, indent=2)}")
        
        # Test VividWalls pricing calculation for canvas roll
        roll_pricing = tool.calculate_vividwalls_pricing(57.00, "roll")
        print(f"📊 Canvas Roll Pricing: {json.dumps(roll_pricing, indent=2)}")
        
        # Test available sizes
        sizes = tool.get_available_sizes()
        print(f"📐 Available sizes: {len(sizes)} sizes configured")
        
        # Verify calculations are reasonable
        assert stretched_pricing["pictorem_base_cost"] == 57.00
        assert stretched_pricing["pictorem_pro_cost"] == 57.00 * 0.85  # 15% discount
        assert stretched_pricing["markup_percentage"] == 106.5
        
        assert roll_pricing["pictorem_base_cost"] == 57.00 * 0.75  # 25% roll discount
        assert len(sizes) == 15  # 15 popular sizes
        
        print("✅ **PRICING CALCULATIONS SUCCESS** - All calculations verified")
        return True
        
    except Exception as e:
        print(f"❌ Pricing calculation test failed: {str(e)}")
        return False

def test_pictorem_full_workflow_simulation():
    """Test 5: Simulate full order workflow (without actual purchase)"""
    print("\n🛒 **TEST 5: Full Workflow Simulation**")
    
    # Create test configuration
    test_config = PictoremOrderConfig(
        product_type="canvas",
        canvas_type="stretched",
        width=16.0,
        height=12.0,
        image_url=create_test_image(),
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
        vividwalls_order_id="VW-TEST-001",
        shopify_order_number="TEST-1001"
    )
    
    tool = PictoremMCPTool(headless=False)
    
    try:
        # Setup and login
        tool.setup_driver()
        print("🔐 Logging in...")
        
        if not tool.login_to_pictorem():
            print("❌ Login failed, cannot test full workflow")
            return False
        
        print("🚀 Navigating to order page...")
        if not tool.navigate_to_order_page(test_config.product_type):
            print("❌ Navigation failed")
            return False
        
        print("🎨 Selecting product type...")
        if not tool.select_product_type(test_config.product_type):
            print("❌ Product selection failed")
            return False
        
        print("📏 Configuring size...")
        if not tool.configure_size(test_config.width, test_config.height):
            print("❌ Size configuration failed")
            return False
        
        print("🖼️ Selecting canvas type...")
        if not tool.select_canvas_type(test_config.canvas_type):
            print("⚠️ Canvas type selection warning (may not be available)")
        
        print("💰 Extracting pricing...")
        pricing = tool.get_pricing_info()
        print(f"Pricing: {pricing}")
        
        # Take final screenshot
        tool.driver.save_screenshot("/tmp/pictorem_full_workflow.png")
        print("📸 Final screenshot saved: /tmp/pictorem_full_workflow.png")
        
        print("✅ **FULL WORKFLOW SIMULATION SUCCESS** - All steps completed")
        print("⚠️ Stopped before image upload and cart addition for safety")
        
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {str(e)}")
        return False
    finally:
        if tool.driver:
            print("🔄 Cleaning up browser...")
            tool.driver.quit()

def run_integration_tests():
    """Run all integration tests"""
    print("🎯 **PICTOREM MCP INTEGRATION TESTS**")
    print("=" * 50)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️ **WARNING**: These tests make real requests to Pictorem's website")
    print()
    
    tests = [
        ("Login Authentication", test_pictorem_login),
        ("Order Page Navigation", test_pictorem_navigation), 
        ("Size Configuration", test_pictorem_size_configuration),
        ("Pricing Calculations", test_pictorem_pricing_calculation),
        ("Full Workflow Simulation", test_pictorem_full_workflow_simulation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"\n❌ FAILED: {test_name} - {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 **INTEGRATION TEST RESULTS SUMMARY**")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 **OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)**")
    
    if passed == total:
        print("🎉 **ALL INTEGRATION TESTS PASSED!**")
        print("✅ Pictorem MCP tool is ready for production use!")
    else:
        print("⚠️ Some tests failed - review issues before production deployment")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    print("🚨 **LIVE INTEGRATION TESTING**")
    print("This will test against the real Pictorem website!")
    
    response = input("\nProceed with live testing? (y/N): ")
    
    if response.lower() == 'y':
        success = run_integration_tests()
        exit(0 if success else 1)
    else:
        print("❌ Integration testing cancelled by user")
        exit(1) 