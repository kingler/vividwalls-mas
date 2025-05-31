#!/usr/bin/env python3
"""
Helper script to setup Facebook access token
"""

import os
import webbrowser
from pathlib import Path

def setup_facebook_token():
    """Guide user through setting up Facebook access token"""
    
    print("🔧 FACEBOOK ACCESS TOKEN SETUP")
    print("=" * 50)
    
    print("\n📋 Steps to get your Facebook Access Token:")
    print("1. Go to Facebook Graph API Explorer")
    print("2. Select/Create your app with Marketing API")
    print("3. Add required permissions")
    print("4. Generate and copy the access token")
    
    print("\n🌐 Opening Facebook Graph API Explorer...")
    
    # Open Facebook Graph API Explorer
    webbrowser.open("https://developers.facebook.com/tools/explorer/")
    
    print("\n📝 Required Permissions:")
    print("   ✅ ads_read - Read ad accounts and campaigns")
    print("   ✅ ads_management - Create/modify campaigns (required for CRUD)")
    print("   ✅ pages_read_engagement - Access Facebook Pages")
    print("   ✅ instagram_basic - Basic Instagram access")
    print("   ✅ business_management - Access business manager")
    
    print("\n" + "=" * 50)
    token = input("🔑 Paste your Facebook Access Token here: ").strip()
    
    if not token or token == "your_facebook_access_token_here":
        print("❌ Invalid token. Please try again.")
        return False
    
    # Update .env file
    env_file = Path(__file__).parent / '.env'
    
    try:
        # Read current .env content
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
        else:
            content = ""
        
        # Replace or add token
        lines = content.split('\n')
        token_updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('FACEBOOK_ACCESS_TOKEN='):
                lines[i] = f'FACEBOOK_ACCESS_TOKEN={token}'
                token_updated = True
                break
        
        if not token_updated:
            lines.append(f'FACEBOOK_ACCESS_TOKEN={token}')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Token saved to .env file")
        print("\n🧪 Now let's test the connection...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

def test_token():
    """Quick test of the configured token"""
    try:
        # Import and test
        from server import _get_fb_access_token, list_ad_accounts
        
        print("\n🔍 Testing token...")
        token = _get_fb_access_token()
        
        if token == "your_facebook_access_token_here":
            print("❌ Token not configured properly")
            return False
        
        print("✅ Token loaded successfully")
        
        # Test API call
        print("🌐 Testing Facebook API connection...")
        accounts = list_ad_accounts()
        
        account_count = len(accounts.get('data', []))
        print(f"✅ Found {account_count} ad account(s)")
        
        if account_count > 0:
            first_account = accounts['data'][0]
            print(f"📊 First account: {first_account.get('name', 'Unknown')} ({first_account.get('id')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Token test failed: {e}")
        print("\nTroubleshooting:")
        print("- Check token permissions (ads_read, ads_management)")
        print("- Ensure token hasn't expired")
        print("- Verify app has Marketing API enabled")
        return False

def main():
    """Main setup function"""
    print("🚀 Welcome to Facebook Ads MCP Server Setup!")
    
    # Check if token is already configured
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'FACEBOOK_ACCESS_TOKEN=' in content and 'your_facebook_access_token_here' not in content:
                print("\n📋 Token appears to be configured. Testing...")
                if test_token():
                    print("\n🎉 Setup complete! Ready to create test campaigns.")
                    return
                else:
                    print("\n🔧 Need to reconfigure token...")
    
    # Setup new token
    if setup_facebook_token():
        test_token()
    
    print("\n" + "=" * 50)
    print("🎯 Next step: Run 'python test_connection.py' to create test campaign!")

if __name__ == "__main__":
    main()