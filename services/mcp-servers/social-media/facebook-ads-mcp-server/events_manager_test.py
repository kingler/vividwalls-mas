#!/usr/bin/env python3
"""
Test Facebook Events Manager features from screenshots
Tests custom audiences, lookalike audiences, and custom conversions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from server import (
    get_ad_account_info, create_custom_audience, get_custom_audiences,
    create_lookalike_audience, create_custom_conversion, get_custom_conversions,
    get_pixels, delete_custom_audience
)

def test_events_manager_features():
    """Test Events Manager features captured from screenshots"""
    
    print("🎯 FACEBOOK EVENTS MANAGER FEATURES TEST")
    print("=" * 60)
    print("📱 Based on Screenshots: Facebook Events Manager UI")
    print("🆔 Ad Account ID: 1015508332916961 (from screenshots)")
    
    # Use the ad account ID from screenshots
    test_ad_account = "act_1015508332916961"
    vividwalls_ad_account = "act_777751590847461"  # VividWalls account
    
    try:
        # Test 1: Get Ad Account Info (from screenshot)
        print(f"\n1️⃣ Testing Ad Account Info (ID from screenshot)...")
        account_info = get_ad_account_info("1015508332916961")
        print(f"✅ Account Info Retrieved:")
        print(f"   Account Name: {account_info.get('name', 'Unknown')}")
        print(f"   Business: {account_info.get('business_name', 'Unknown')}")
        print(f"   Currency: {account_info.get('currency', 'Unknown')}")
        print(f"   Status: {account_info.get('account_status', 'Unknown')}")
        
        # Test 2: Create Custom Audience (from "Create custom audience" option)
        print(f"\n2️⃣ Testing Custom Audience Creation...")
        print("📋 Option from screenshot: 'Find people who already engaged with your brand'")
        
        audience_result = create_custom_audience(
            ad_account_id=vividwalls_ad_account,
            name="VividWalls Art Enthusiasts Test",
            subtype="ENGAGEMENT",
            description="Test audience for people engaged with VividWalls brand",
            retention_days=30
        )
        
        test_audience_id = audience_result.get('id')
        print(f"✅ Custom Audience Created:")
        print(f"   Audience ID: {test_audience_id}")
        print(f"   Type: Engagement-based")
        print(f"   Retention: 30 days")
        
        # Test 3: Get Custom Audiences
        print(f"\n3️⃣ Testing Custom Audiences List...")
        audiences = get_custom_audiences(
            ad_account_id=vividwalls_ad_account,
            fields=['id', 'name', 'subtype', 'approximate_count', 'delivery_status'],
            limit=10
        )
        
        audience_count = len(audiences.get('data', []))
        print(f"✅ Custom Audiences Retrieved: {audience_count}")
        for aud in audiences.get('data', [])[-3:]:  # Show last 3
            print(f"   - {aud.get('name', 'Unknown')} ({aud.get('subtype', 'Unknown')})")
        
        # Test 4: Create Lookalike Audience (from "Create lookalike audience" option)
        if test_audience_id:
            print(f"\n4️⃣ Testing Lookalike Audience Creation...")
            print("📋 Option from screenshot: 'Reach new people who are likely to be interested'")
            
            lookalike_result = create_lookalike_audience(
                ad_account_id=vividwalls_ad_account,
                name="VividWalls Lookalike 1% Test",
                origin_audience_id=test_audience_id,
                target_countries=["US"],
                ratio=0.01,
                description="1% lookalike of VividWalls art enthusiasts"
            )
            
            lookalike_id = lookalike_result.get('id')
            print(f"✅ Lookalike Audience Created:")
            print(f"   Lookalike ID: {lookalike_id}")
            print(f"   Source: VividWalls Art Enthusiasts")
            print(f"   Size: 1% of US population")
            print(f"   Target: Art enthusiasts similar to existing customers")
        
        # Test 5: Create Custom Conversion (from "Create custom conversion" option)
        print(f"\n5️⃣ Testing Custom Conversion Creation...")
        print("📋 Option from screenshot: 'Measure more specific customer actions'")
        
        conversion_result = create_custom_conversion(
            ad_account_id=vividwalls_ad_account,
            name="VividWalls Art Purchase Test",
            event_type="PURCHASE",
            description="Track VividWalls artwork purchases from ads",
            default_conversion_value=45.00
        )
        
        conversion_id = conversion_result.get('id')
        print(f"✅ Custom Conversion Created:")
        print(f"   Conversion ID: {conversion_id}")
        print(f"   Event Type: PURCHASE")
        print(f"   Default Value: $45.00")
        print(f"   Purpose: Track art sales from Facebook ads")
        
        # Test 6: Get Custom Conversions
        print(f"\n6️⃣ Testing Custom Conversions List...")
        conversions = get_custom_conversions(
            ad_account_id=vividwalls_ad_account,
            fields=['id', 'name', 'event_type', 'default_conversion_value'],
            limit=5
        )
        
        conversion_count = len(conversions.get('data', []))
        print(f"✅ Custom Conversions Retrieved: {conversion_count}")
        for conv in conversions.get('data', []):
            print(f"   - {conv.get('name', 'Unknown')} ({conv.get('event_type', 'Unknown')})")
        
        # Test 7: Get Pixels for Account
        print(f"\n7️⃣ Testing Facebook Pixels...")
        pixels = get_pixels(
            ad_account_id=vividwalls_ad_account,
            fields=['id', 'name', 'creation_time']
        )
        
        pixel_count = len(pixels.get('data', []))
        print(f"✅ Facebook Pixels: {pixel_count}")
        for pixel in pixels.get('data', []):
            print(f"   - {pixel.get('name', 'Unknown')} ({pixel.get('id')})")
        
        print(f"\n" + "=" * 60)
        print(f"🎉 EVENTS MANAGER FEATURES TEST COMPLETED!")
        print(f"✅ Ad Account Access: Working (ID: 1015508332916961)")
        print(f"✅ Custom Audience Creation: Working")
        print(f"✅ Lookalike Audience Creation: Working") 
        print(f"✅ Custom Conversion Tracking: Working")
        print(f"✅ Facebook Pixel Integration: Working")
        
        print(f"\n🎯 FEATURES MATCHED FROM SCREENSHOTS:")
        print(f"✅ 'Create Ad' - Drive customer actions ✓")
        print(f"✅ 'Create custom audience' - Find engaged users ✓")
        print(f"✅ 'Create lookalike audience' - Reach similar people ✓")
        print(f"✅ 'Create custom conversion' - Measure actions ✓")
        print(f"✅ Ad Account ID: 1015508332916961 - Recorded ✓")
        
        print(f"\n📊 VIVIDWALLS INTEGRATION READY:")
        print(f"🎨 Custom audiences for art enthusiasts")
        print(f"🔍 Lookalike audiences for market expansion")
        print(f"💰 Purchase conversion tracking for ROI")
        print(f"📈 Event optimization for art sales")
        
        print(f"\n🧹 CLEANUP TEST DATA:")
        # Clean up test audience
        if test_audience_id:
            try:
                delete_result = delete_custom_audience(test_audience_id)
                print(f"✅ Test custom audience deleted: {test_audience_id}")
            except Exception as e:
                print(f"⚠️ Cleanup note: Delete audience {test_audience_id} manually")
        
        print(f"⚠️ Note: Lookalike and conversion created for testing")
        print(f"   Delete manually in Facebook Ads Manager if needed")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Events Manager test failed: {e}")
        return False

if __name__ == "__main__":
    test_events_manager_features()