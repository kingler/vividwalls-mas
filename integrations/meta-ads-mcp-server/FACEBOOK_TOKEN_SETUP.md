# Facebook Access Token Setup Guide

## 🎯 Quick Setup for Testing

### Step 1: Get Facebook Access Token

1. **Go to Facebook Graph API Explorer**:
   👉 https://developers.facebook.com/tools/explorer/

2. **Select Your Application**:
   - If you don't have one, create a new app at https://developers.facebook.com/apps/
   - Choose "Business" app type
   - Add "Marketing API" product

3. **Configure Permissions**:
   Click "Add a Permission" and select:
   - ✅ `ads_read` - Read ad accounts and campaigns
   - ✅ `ads_management` - Create/modify campaigns (required for CRUD)
   - ✅ `pages_read_engagement` - Access Facebook Pages
   - ✅ `instagram_basic` - Basic Instagram access
   - ✅ `business_management` - Access business manager

4. **Generate Token**:
   - Click "Generate Access Token"
   - Complete Facebook login and grant permissions
   - Copy the generated token

### Step 2: Configure Token in Environment

```bash
# Edit the .env file
cd integrations/meta-ads-mcp-server
nano .env

# Replace the placeholder with your actual token:
FACEBOOK_ACCESS_TOKEN=your_actual_long_token_here
```

### Step 3: Test Connection

```bash
# Run the test script
cd integrations/meta-ads-mcp-server
source venv/bin/activate
python test_connection.py
```

## 🔐 Token Types & Longevity

### Short-lived Tokens (1-2 hours)
- Default from Graph API Explorer
- Good for quick testing

### Long-lived Tokens (60 days)
- Convert short-lived tokens
- Better for ongoing development

### System User Tokens (No expiration)
- For production applications
- Requires Business Manager setup

## 📝 Quick Test Commands

Once your token is configured, test these commands:

```python
# Test 1: List your ad accounts
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from server import list_ad_accounts
print(list_ad_accounts())
"

# Test 2: Check Instagram accounts
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from server import list_ad_accounts, get_instagram_accounts
accounts = list_ad_accounts()
if accounts.get('data'):
    account_id = accounts['data'][0]['id']
    print(get_instagram_accounts(account_id))
"
```

## ⚠️ Important Notes

1. **Permissions**: Ensure your app has Marketing API enabled
2. **Business Verification**: Some features require verified business
3. **Rate Limits**: Facebook has API rate limits (be careful with bulk operations)
4. **Token Security**: Never commit tokens to git (they're in .gitignore)

## 🚀 Ready to Test?

Once configured, run:
```bash
python test_connection.py
```

This will:
- ✅ Verify your token works
- ✅ List your ad accounts
- ✅ Check Instagram integration
- ✅ Optionally create a test campaign

## 🎯 Production Setup

For production use, consider:
- Using System User tokens (never expire)
- Setting up proper business verification
- Implementing token refresh logic
- Adding comprehensive error handling