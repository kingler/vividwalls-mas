#!/usr/bin/env python3
"""
Simple Facebook Ads test: Create campaign, then delete it
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from server import list_ad_accounts, create_campaign, delete_campaign

def simple_test():
    """Simple create and delete test"""
    
    print("🧪 SIMPLE FACEBOOK ADS TEST")
    print("=" * 40)
    
    try:
        # Get ad accounts
        print("1️⃣ Getting ad accounts...")
        accounts = list_ad_accounts()
        ad_accounts_data = accounts.get('adaccounts', {}).get('data', [])
        account_id = ad_accounts_data[0]['id']
        print(f"✅ Using account: {account_id}")
        
        # Create campaign
        print("\n2️⃣ Creating test campaign...")
        campaign_data = create_campaign(
            ad_account_id=account_id,
            name="🧪 Simple Test Campaign",
            objective="OUTCOME_AWARENESS",
            status="PAUSED",
            daily_budget=100,
            special_ad_categories=["NONE"]
        )
        
        campaign_id = campaign_data.get('id')
        print(f"✅ Campaign created: {campaign_id}")
        print(f"🌐 View at: https://www.facebook.com/adsmanager/")
        
        # Delete campaign
        print(f"\n3️⃣ Deleting test campaign...")
        delete_result = delete_campaign(campaign_id)
        print(f"✅ Campaign deleted successfully")
        
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"✅ Create: Working")
        print(f"✅ Delete: Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    simple_test()