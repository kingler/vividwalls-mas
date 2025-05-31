#!/usr/bin/env python3
"""
Test script for Facebook Ads MCP Server
This script tests the connection and basic functionality
"""

import os
import sys
import json
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
    create_campaign
)

def test_connection():
    """Test basic connection to Facebook Ads API"""
    print("🔍 Testing Facebook Ads MCP Server Connection...")
    
    try:
        # Test 1: Check if token is configured
        print("\n1️⃣ Checking access token...")
        token = _get_fb_access_token()
        if token == "your_facebook_access_token_here":
            print("❌ Please configure your Facebook access token in .env file")
            return False
        print("✅ Access token configured")
        
        # Test 2: List ad accounts
        print("\n2️⃣ Testing ad accounts access...")
        accounts = list_ad_accounts()
        
        # Handle the nested structure from MCP server
        ad_accounts_data = accounts.get('adaccounts', {}).get('data', [])
        print(f"✅ Found {len(ad_accounts_data)} ad account(s)")
        
        if not ad_accounts_data:
            print("❌ No ad accounts found. Check your token permissions.")
            return False
            
        # Test 3: Get details of first ad account
        first_account = ad_accounts_data[0]
        account_id = first_account['id']
        print(f"\n3️⃣ Testing account details for {account_id}...")
        
        details = get_details_of_ad_account(account_id)
        print(f"✅ Account: {details.get('name', 'Unknown')} ({details.get('currency', 'USD')})")
        
        # Test 4: Check Instagram accounts
        print(f"\n4️⃣ Testing Instagram integration...")
        try:
            instagram_accounts = get_instagram_accounts(account_id)
            instagram_count = len(instagram_accounts.get('data', []))
            print(f"✅ Found {instagram_count} connected Instagram account(s)")
        except Exception as e:
            print(f"⚠️ Instagram accounts test failed: {e}")
        
        print(f"\n🎯 Ready to create test campaign on account: {account_id}")
        return account_id
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_test_campaign(account_id):
    """Create a test campaign to validate CRUD operations"""
    print(f"\n🚀 Creating test campaign on account {account_id}...")
    
    try:
        # Create a simple test campaign
        campaign_data = create_campaign(
            ad_account_id=account_id,
            name="MCP Test Campaign - DELETE ME",
            objective="REACH",
            status="PAUSED",  # Keep it paused for safety
            daily_budget=100,  # $1.00 per day (in cents)
            special_ad_categories=[]
        )
        
        campaign_id = campaign_data.get('id')
        print(f"✅ Test campaign created successfully!")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Name: MCP Test Campaign - DELETE ME")
        print(f"   Status: PAUSED (safe for testing)")
        print(f"   Daily Budget: $1.00")
        
        return campaign_id
        
    except Exception as e:
        print(f"❌ Failed to create test campaign: {e}")
        return None

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 FACEBOOK ADS MCP SERVER CONNECTION TEST")
    print("=" * 60)
    
    # Test basic connection
    account_id = test_connection()
    
    if not account_id:
        print("\n❌ Connection test failed. Please check your configuration.")
        return
    
    # Ask user if they want to create a test campaign
    print(f"\n" + "=" * 60)
    response = input("📝 Create a test campaign? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        campaign_id = create_test_campaign(account_id)
        
        if campaign_id:
            print(f"\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("🎉 Facebook Ads MCP Server is working correctly!")
            print(f"\n📋 Test Campaign Details:")
            print(f"   Account ID: {account_id}")
            print(f"   Campaign ID: {campaign_id}")
            print(f"   Status: PAUSED (safe)")
            print(f"\n⚠️ Remember to delete the test campaign when done!")
            print("   You can delete it via Facebook Ads Manager or using:")
            print(f"   delete_campaign('{campaign_id}')")
    else:
        print("\n✅ Basic connection test completed successfully!")
        print("🎉 Facebook Ads MCP Server is ready to use!")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()