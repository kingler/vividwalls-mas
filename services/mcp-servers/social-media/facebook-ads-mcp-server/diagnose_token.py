#!/usr/bin/env python3
"""
Diagnostic script for Facebook token and permissions
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def diagnose_token():
    """Diagnose Facebook token and permissions"""
    
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    if not token:
        print("❌ No token found")
        return
    
    print("🔍 FACEBOOK TOKEN DIAGNOSTICS")
    print("=" * 50)
    
    # Test 1: Token info
    print("\n1️⃣ Token Information:")
    try:
        response = requests.get(f"https://graph.facebook.com/v22.0/me", params={'access_token': token})
        if response.status_code == 200:
            me_data = response.json()
            print(f"✅ Token belongs to: {me_data.get('name', 'Unknown')} (ID: {me_data.get('id')})")
        else:
            print(f"❌ Token validation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return
    
    # Test 2: Token permissions
    print("\n2️⃣ Token Permissions:")
    try:
        response = requests.get(f"https://graph.facebook.com/v22.0/me/permissions", params={'access_token': token})
        if response.status_code == 200:
            permissions = response.json()
            granted_perms = [p['permission'] for p in permissions.get('data', []) if p.get('status') == 'granted']
            print(f"✅ Granted permissions ({len(granted_perms)}):")
            for perm in sorted(granted_perms):
                print(f"   - {perm}")
            
            # Check required permissions
            required = ['ads_read', 'ads_management', 'business_management']
            missing = [perm for perm in required if perm not in granted_perms]
            if missing:
                print(f"\n⚠️ Missing required permissions: {missing}")
            else:
                print(f"\n✅ All required permissions present")
        else:
            print(f"❌ Permissions check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
    
    # Test 3: Ad accounts via different endpoints
    print("\n3️⃣ Ad Accounts Discovery:")
    
    # Try direct me/adaccounts
    try:
        response = requests.get(f"https://graph.facebook.com/v22.0/me/adaccounts", params={'access_token': token})
        if response.status_code == 200:
            accounts = response.json()
            account_count = len(accounts.get('data', []))
            print(f"✅ me/adaccounts: Found {account_count} account(s)")
            for acc in accounts.get('data', [])[:3]:  # Show first 3
                print(f"   - {acc.get('name', 'Unknown')} ({acc.get('id')})")
        else:
            print(f"❌ me/adaccounts failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error with me/adaccounts: {e}")
    
    # Try businesses endpoint
    print("\n4️⃣ Business Accounts:")
    try:
        response = requests.get(f"https://graph.facebook.com/v22.0/me/businesses", params={'access_token': token})
        if response.status_code == 200:
            businesses = response.json()
            business_count = len(businesses.get('data', []))
            print(f"✅ me/businesses: Found {business_count} business(es)")
            for biz in businesses.get('data', [])[:3]:
                print(f"   - {biz.get('name', 'Unknown')} ({biz.get('id')})")
                
                # Try to get ad accounts for each business
                try:
                    biz_response = requests.get(
                        f"https://graph.facebook.com/v22.0/{biz['id']}/owned_ad_accounts",
                        params={'access_token': token}
                    )
                    if biz_response.status_code == 200:
                        biz_accounts = biz_response.json()
                        biz_account_count = len(biz_accounts.get('data', []))
                        print(f"     └── Ad accounts: {biz_account_count}")
                except:
                    pass
        else:
            print(f"❌ me/businesses failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error with me/businesses: {e}")
    
    # Test 5: Pages (might lead to ad accounts)
    print("\n5️⃣ Facebook Pages:")
    try:
        response = requests.get(f"https://graph.facebook.com/v22.0/me/accounts", params={'access_token': token})
        if response.status_code == 200:
            pages = response.json()
            page_count = len(pages.get('data', []))
            print(f"✅ me/accounts (pages): Found {page_count} page(s)")
            for page in pages.get('data', [])[:3]:
                print(f"   - {page.get('name', 'Unknown')} ({page.get('id')})")
        else:
            print(f"❌ me/accounts failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error with me/accounts: {e}")
    
    print("\n" + "=" * 50)
    print("📝 RECOMMENDATIONS:")
    print("1. If no ad accounts found, you may need to:")
    print("   - Create an ad account in Facebook Business Manager")
    print("   - Get access to existing ad accounts")
    print("   - Use a different token with proper business access")
    print("2. If permissions are missing, regenerate token with required permissions")
    print("3. For testing, you can create a new ad account at:")
    print("   https://business.facebook.com/")

if __name__ == "__main__":
    diagnose_token()