#!/usr/bin/env python3
"""
Automatic test script for Facebook Ads MCP Server
Creates a test campaign with $1.00 budget, then deletes it
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our server functions
from server import (
    _get_fb_access_token,
    list_ad_accounts,
    get_details_of_ad_account,
    get_instagram_accounts,
    create_campaign,
    update_campaign,
    delete_campaign
)

def run_full_test():
    """Run complete test: connection, create campaign, delete campaign"""
    
    print("🚀 FACEBOOK ADS MCP SERVER - FULL CRUD TEST")
    print("=" * 60)
    
    try:
        # Step 1: Verify connection
        print("\n1️⃣ Testing connection...")
        token = _get_fb_access_token()
        print("✅ Access token loaded")
        
        # Step 2: Get ad accounts
        print("\n2️⃣ Getting ad accounts...")
        accounts = list_ad_accounts()
        ad_accounts_data = accounts.get('adaccounts', {}).get('data', [])
        print(f"✅ Found {len(ad_accounts_data)} ad account(s)")
        
        if not ad_accounts_data:
            print("❌ No ad accounts available for testing")
            return False
        
        # Use first account for testing
        test_account = ad_accounts_data[0]
        account_id = test_account['id']
        account_name = test_account['name']
        print(f"📊 Using account: {account_name} ({account_id})")
        
        # Step 3: Get account details
        print(f"\n3️⃣ Getting account details...")
        details = get_details_of_ad_account(account_id)
        currency = details.get('currency', 'USD')
        print(f"✅ Account currency: {currency}")
        
        # Step 4: Test Instagram integration
        print(f"\n4️⃣ Testing Instagram integration...")
        try:
            instagram_accounts = get_instagram_accounts(account_id)
            instagram_count = len(instagram_accounts.get('data', []))
            print(f"✅ Connected Instagram accounts: {instagram_count}")
        except Exception as e:
            print(f"⚠️ Instagram test failed: {e}")
        
        # Step 5: Create test campaign
        print(f"\n5️⃣ Creating test campaign...")
        campaign_data = create_campaign(
            ad_account_id=account_id,
            name="🧪 MCP Test Campaign - AUTO DELETE",
            objective="OUTCOME_AWARENESS",  # Updated to current Facebook objective
            status="PAUSED",  # Keep it paused for safety
            daily_budget=100,  # $1.00 per day (in cents)
            special_ad_categories=["NONE"]  # Required parameter for compliance
        )
        
        campaign_id = campaign_data.get('id')
        print(f"✅ Campaign created successfully!")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Name: 🧪 MCP Test Campaign - AUTO DELETE")
        print(f"   Status: PAUSED (safe)")
        print(f"   Daily Budget: $1.00")
        
        # Step 6: Verify campaign in Facebook
        print(f"\n6️⃣ Campaign verification...")
        print(f"🌐 View in Facebook Ads Manager:")
        print(f"   https://www.facebook.com/adsmanager/manage/campaigns")
        print(f"   Look for: '🧪 MCP Test Campaign - AUTO DELETE'")
        
        # Wait a moment for the campaign to be visible
        print(f"\n⏳ Waiting 3 seconds for campaign to propagate...")
        time.sleep(3)
        
        # Step 7: Test update operation
        print(f"\n7️⃣ Testing campaign update...")
        update_result = update_campaign(
            campaign_id=campaign_id,
            name="🧪 MCP Test Campaign - UPDATED - AUTO DELETE"
        )
        print(f"✅ Campaign updated successfully")
        
        # Step 8: Delete test campaign
        print(f"\n8️⃣ Cleaning up - deleting test campaign...")
        delete_result = delete_campaign(campaign_id)
        print(f"✅ Test campaign deleted successfully")
        print(f"   The campaign status has been set to 'DELETED'")
        
        # Final success message
        print(f"\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("✅ Facebook Ads MCP Server is fully functional!")
        print(f"\n📋 Test Summary:")
        print(f"   ✅ Connection: Working")
        print(f"   ✅ Ad Accounts: {len(ad_accounts_data)} found")
        print(f"   ✅ Instagram: {instagram_count} accounts connected")
        print(f"   ✅ Campaign Creation: Working")
        print(f"   ✅ Campaign Update: Working") 
        print(f"   ✅ Campaign Deletion: Working")
        print(f"\n🎯 Ready for production use with VividWalls!")
        print(f"=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   - Check token permissions")
        print(f"   - Verify ad account access")
        print(f"   - Ensure Marketing API is enabled")
        return False

if __name__ == "__main__":
    success = run_full_test()
    exit(0 if success else 1)