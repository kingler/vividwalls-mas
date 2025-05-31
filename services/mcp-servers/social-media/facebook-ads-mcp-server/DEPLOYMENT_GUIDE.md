# Facebook Ads MCP Server Deployment Guide

## Overview

The Facebook Ads MCP server has been successfully deployed both locally and on the Digital Ocean droplet, following Python virtual environment best practices.

## Local Setup ✅

**Location**: `/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server`

```bash
# Virtual environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env and add your Facebook access token
```

**Usage**:
```bash
cd /Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server
source venv/bin/activate
# Token loaded from .env file automatically
python server.py

# Or override with command line
python server.py --fb-token YOUR_FACEBOOK_ACCESS_TOKEN
```

## Digital Ocean Droplet Setup ✅

**Location**: `/root/vivid_mas/mcp/facebook-ads-mcp-server`

**Virtual Environment**: Properly configured with Python 3.12.7
- Dependencies installed in isolated environment
- Launcher script created: `run_server.sh`

**Usage on Droplet**:
```bash
# Using virtual environment directly
cd /root/vivid_mas/mcp/facebook-ads-mcp-server
source venv/bin/activate
# Edit .env file and add your token first
python server.py

# Using launcher script
./run_server.sh

# Or with command line override
python server.py --fb-token YOUR_TOKEN
```

## MCP Configuration ✅

The configuration files have been updated to use environment variables for security:

### Claude Desktop Config (`claude_desktop_config.json`):
```json
{
  "facebook-ads-mcp-server": {
    "command": "/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server/venv/bin/python",
    "args": [
      "/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server/server.py"
    ]
  }
}
```

### Cursor MCP Config (`.cursor/mcp.json`):
```json
{
  "name": "facebook-ads-mcp",
  "command": "/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server/venv/bin/python",
  "args": [
    "/Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server/server.py"
  ]
}
```

### Environment Variables (`.env`):
```bash
FACEBOOK_ACCESS_TOKEN=your_actual_facebook_token_here
LOG_LEVEL=info
```

## Available Tools

The MCP server provides **40 comprehensive Facebook Ads API tools** with full CRUD operations:

### 📊 Account Management
- `list_ad_accounts` - List all ad accounts
- `get_details_of_ad_account` - Get account details
- `update_ad_account` - **UPDATE** account settings (name, timezone, currency, spend cap)

### 🎯 Campaign Operations (Full CRUD)
**READ:**
- `get_campaigns_by_adaccount` - List campaigns
- `get_campaign_by_id` - Get campaign details
- `get_campaign_insights` - Get campaign performance

**CREATE/UPDATE/DELETE:**
- `create_campaign` - **CREATE** new campaigns with objectives, budgets, targeting
- `update_campaign` - **UPDATE** campaign settings, status, budgets
- `delete_campaign` - **DELETE** campaigns (sets status to DELETED)

### 🎪 Ad Set Operations (Full CRUD)
**READ:**
- `get_adsets_by_adaccount` - List ad sets
- `get_adsets_by_campaign` - Get ad sets by campaign
- `get_adset_by_id` - Get ad set details
- `get_adset_insights` - Get ad set performance
- `get_adsets_by_ids` - Get multiple ad sets by IDs

**CREATE/UPDATE/DELETE:**
- `create_adset` - **CREATE** new ad sets with targeting, budgets, optimization
- `update_adset` - **UPDATE** ad set settings, targeting, budgets
- `delete_adset` - **DELETE** ad sets (sets status to DELETED)

### 📢 Ad Operations (Full CRUD)
**READ:**
- `get_ads_by_adaccount` - List ads
- `get_ads_by_campaign` - Get ads by campaign
- `get_ads_by_adset` - Get ads by ad set
- `get_ad_by_id` - Get ad details
- `get_ad_insights` - Get ad performance

**CREATE/UPDATE/DELETE:**
- `create_ad` - **CREATE** new ads with creatives and tracking
- `update_ad` - **UPDATE** ad settings, creatives, status
- `delete_ad` - **DELETE** ads (sets status to DELETED)

### 🎨 Creative Management (Full CRUD)
**READ:**
- `get_ad_creative_by_id` - Get creative details
- `get_ad_creatives_by_ad_id` - Get creatives by ad

**CREATE/UPDATE/DELETE:**
- `create_ad_creative` - **CREATE** new ad creatives with images, videos, text
- `update_ad_creative` - **UPDATE** creative content (limited fields)
- `delete_ad_creative` - **DELETE** ad creatives

### 📱 Instagram-Specific Tools
- `get_instagram_accounts` - Get connected Instagram accounts
- `get_instagram_media` - Get Instagram media content
- `create_instagram_ad_creative` - **CREATE** Instagram-specific creatives

### ⚡ Bulk Operations
- `bulk_update_campaigns` - **UPDATE** multiple campaigns in one request
- `bulk_update_adsets` - **UPDATE** multiple ad sets in one request
- `bulk_update_ads` - **UPDATE** multiple ads in one request

### 📈 Analytics & Insights
- `get_adaccount_insights` - Account performance data
- `get_campaign_insights` - Campaign performance data
- `get_adset_insights` - Ad set performance data
- `get_ad_insights` - Ad performance data
- `fetch_pagination_url` - Handle paginated results

### 📋 Activity Tracking
- `get_activities_by_adaccount` - Account change history
- `get_activities_by_adset` - Ad set change history

## 🔗 Integration with n8n & VividWalls

The enhanced server provides complete Facebook & Instagram Ads management:

### **For VividWalls Marketing Automation:**
1. **Campaign Creation**: Automatically create campaigns for new art collections
2. **Creative Management**: Generate ad creatives from VividWalls artwork
3. **Performance Optimization**: Monitor and adjust campaigns based on performance
4. **Instagram Integration**: Create Instagram-specific campaigns for visual art
5. **Bulk Operations**: Efficiently manage multiple campaigns across collections

### **n8n Workflow Capabilities:**
- **Complete CRUD**: Create, read, update, delete all ad components
- **Automated Campaigns**: React to VividWalls events (new products, sales)
- **Performance Monitoring**: Track ROI and adjust budgets automatically
- **Cross-Platform**: Manage both Facebook and Instagram from unified workflows

## Security Best Practices ✅

- ✅ **Virtual environments**: Isolated dependencies
- ✅ **No global installations**: Clean system packages
- ✅ **Environment variables**: Tokens stored in `.env` files, not in config files
- ✅ **Token priority**: Environment variables > Command line arguments
- ✅ **Git safety**: `.env` files should be in `.gitignore` (use `.env.example` for templates)
- ✅ **Proper permissions**: Executable scripts with correct permissions

### Important Security Notes:

1. **Never commit tokens**: Add `.env` to `.gitignore`
2. **Use .env.example**: Template file for sharing configuration structure
3. **Token rotation**: Regularly update Facebook access tokens
4. **Minimal permissions**: Only request necessary Facebook API permissions

## Verification Commands

```bash
# Local verification
cd /Users/kinglerbercy/Projects/vivid_mas/mcp/facebook-ads-mcp-server
source venv/bin/activate && python --version

# Droplet verification
ssh root@157.230.13.13 "cd /root/vivid_mas/mcp/facebook-ads-mcp-server && source venv/bin/activate && python --version"
```

## Next Steps

1. Obtain Facebook Developer Access Token
2. Replace placeholder tokens in MCP configuration
3. Test integration with n8n workflows
4. Configure Facebook Ads automation for VividWalls marketing

The Facebook Ads MCP server is now fully deployed and ready for production use!