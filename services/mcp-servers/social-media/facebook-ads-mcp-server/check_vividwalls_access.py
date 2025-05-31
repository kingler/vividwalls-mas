#!/usr/bin/env python3
"""
Check access to VividWalls business account
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def check_vividwalls_access():
    """Check access to VividWalls business and ad accounts"""
    
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    vividwalls_business_id = "281179304635214"
    
    print("🎨 VIVIDWALLS BUSINESS ACCESS CHECK")
    print("=" * 50)
    print(f"Business ID: {vividwalls_business_id}")
    print(f"Domain: vividwalls.space")
    
    try:
        # Check user's businesses
        print(f"\n1️⃣ Checking your business access...")
        response = requests.get(
            f"https://graph.facebook.com/v22.0/me/businesses",
            params={'access_token': token}
        )
        
        if response.status_code == 200:
            businesses = response.json()
            print(f"✅ Found {len(businesses.get('data', []))} business(es):")
            
            vividwalls_found = False
            for biz in businesses.get('data', []):
                biz_id = biz.get('id')
                biz_name = biz.get('name', 'Unknown')
                print(f"   - {biz_name} ({biz_id})")
                
                if biz_id == vividwalls_business_id:
                    vividwalls_found = True
                    print(f"     ✅ VividWalls business found!")
            
            if not vividwalls_found:
                print(f"   ⚠️ VividWalls business not found in your accessible businesses")
        
        # Try to access VividWalls business directly
        print(f"\n2️⃣ Checking direct VividWalls business access...")
        response = requests.get(
            f"https://graph.facebook.com/v22.0/{vividwalls_business_id}",
            params={'access_token': token, 'fields': 'name,id,primary_page'}
        )
        
        if response.status_code == 200:
            vividwalls_data = response.json()
            print(f"✅ VividWalls business accessible:")
            print(f"   Name: {vividwalls_data.get('name', 'Unknown')}")
            print(f"   ID: {vividwalls_data.get('id')}")
            if 'primary_page' in vividwalls_data:
                print(f"   Primary Page: {vividwalls_data['primary_page'].get('name')}")
        else:
            print(f"❌ Cannot access VividWalls business directly")
            print(f"   Status: {response.status_code}")
            if response.text:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown')}")
        
        # Check VividWalls ad accounts
        print(f"\n3️⃣ Checking VividWalls ad accounts...")
        response = requests.get(
            f"https://graph.facebook.com/v22.0/{vividwalls_business_id}/owned_ad_accounts",
            params={'access_token': token, 'fields': 'name,id,account_status,currency'}
        )
        
        if response.status_code == 200:
            ad_accounts = response.json()
            account_count = len(ad_accounts.get('data', []))
            print(f"✅ VividWalls ad accounts: {account_count}")
            
            for acc in ad_accounts.get('data', []):
                print(f"   - {acc.get('name', 'Unknown')} ({acc.get('id')})")
                print(f"     Status: {acc.get('account_status')}")
                print(f"     Currency: {acc.get('currency', 'Unknown')}")
        else:
            print(f"❌ Cannot access VividWalls ad accounts")
            print(f"   Status: {response.status_code}")
        
        # Check VividWalls pages
        print(f"\n4️⃣ Checking VividWalls pages...")
        response = requests.get(
            f"https://graph.facebook.com/v22.0/{vividwalls_business_id}/owned_pages",
            params={'access_token': token, 'fields': 'name,id,username,website'}
        )
        
        if response.status_code == 200:
            pages = response.json()
            page_count = len(pages.get('data', []))
            print(f"✅ VividWalls pages: {page_count}")
            
            for page in pages.get('data', []):
                print(f"   - {page.get('name', 'Unknown')} ({page.get('id')})")
                if page.get('username'):
                    print(f"     Username: @{page.get('username')}")
                if page.get('website'):
                    print(f"     Website: {page.get('website')}")
        else:
            print(f"❌ Cannot access VividWalls pages")
        
        print(f"\n" + "=" * 50)
        print(f"📝 RECOMMENDATIONS:")
        print(f"1. If VividWalls business not accessible:")
        print(f"   - Request business admin access from VividWalls owner")
        print(f"   - Get added as a business user with Marketing permissions")
        print(f"   - Generate new token with business access")
        print(f"2. If ad accounts not found:")
        print(f"   - Create ad account under VividWalls business")
        print(f"   - Get access to existing VividWalls ad accounts")
        print(f"3. For vividwalls.space integration:")
        print(f"   - Verify page ownership of vividwalls.space")
        print(f"   - Configure pixel for website tracking")
        
    except Exception as e:
        print(f"❌ Error checking VividWalls access: {e}")

if __name__ == "__main__":
    check_vividwalls_access()