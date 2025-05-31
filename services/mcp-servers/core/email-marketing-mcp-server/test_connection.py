#!/usr/bin/env python3
"""
Test connection to email service providers
"""

import os
import sys
import requests
import base64
from pathlib import Path

# Add the current directory to Python path to import from server
sys.path.insert(0, str(Path(__file__).parent))

def test_sendgrid_connection(api_key):
    """Test SendGrid API connection"""
    print("Testing SendGrid connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test with a simple API call to get user profile
        response = requests.get("https://api.sendgrid.com/v3/user/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SendGrid connection successful!")
            print(f"   User: {data.get('username', 'N/A')}")
            print(f"   Email: {data.get('email', 'N/A')}")
            return True
        else:
            print(f"❌ SendGrid connection failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid connection error: {e}")
        return False

def test_mailchimp_connection(api_key):
    """Test Mailchimp API connection"""
    print("Testing Mailchimp connection...")
    
    # Extract datacenter from API key
    dc = api_key.split('-')[-1] if '-' in api_key else 'us1'
    
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'anystring:{api_key}'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test with a simple API call to get account info
        response = requests.get(f"https://{dc}.api.mailchimp.com/3.0/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mailchimp connection successful!")
            print(f"   Account: {data.get('account_name', 'N/A')}")
            print(f"   Email: {data.get('email', 'N/A')}")
            print(f"   Datacenter: {dc}")
            return True
        else:
            print(f"❌ Mailchimp connection failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Mailchimp connection error: {e}")
        return False

def main():
    """Main test function"""
    print("Email Marketing MCP Server - Connection Test")
    print("=" * 50)
    
    # Try to load from environment first
    api_key = os.getenv('EMAIL_API_KEY')
    provider = os.getenv('EMAIL_PROVIDER', 'sendgrid').lower()
    
    # Check command line arguments
    if not api_key:
        if len(sys.argv) < 3:
            print("Usage: python test_connection.py <provider> <api_key>")
            print("   or set EMAIL_API_KEY and EMAIL_PROVIDER environment variables")
            print("\nProviders: sendgrid, mailchimp")
            return False
        
        provider = sys.argv[1].lower()
        api_key = sys.argv[2]
    
    if not api_key:
        print("❌ No API key provided!")
        return False
    
    print(f"Testing {provider.title()} API...")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    if provider == 'sendgrid':
        success = test_sendgrid_connection(api_key)
    elif provider == 'mailchimp':
        success = test_mailchimp_connection(api_key)
    else:
        print(f"❌ Unsupported provider: {provider}")
        print("Supported providers: sendgrid, mailchimp")
        return False
    
    print()
    if success:
        print("🎉 Connection test completed successfully!")
        print("Your email marketing MCP server is ready to use.")
    else:
        print("💥 Connection test failed!")
        print("Please check your API key and try again.")
    
    return success

if __name__ == "__main__":
    main()