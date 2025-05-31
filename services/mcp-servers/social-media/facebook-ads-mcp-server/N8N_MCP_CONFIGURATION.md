# n8n MCP Client Configuration Guide

## 🎯 MCP Server Configuration for n8n

This guide provides the exact configuration for your three MCP servers in n8n:
- **Facebook Ads MCP Server** (49 tools) - **UPDATED with Events Manager features**
- **Shopify MCP Server** (24 tools) 
- **Pictorem MCP Server** (15 tools)

## 📊 Facebook Ads MCP Server Configuration

### **List_Tools Node Configuration:**
```json
{
  "serverName": "facebook-ads-mcp",
  "command": "/root/vivid_mas/mcp/facebook-ads-mcp-server/venv/bin/python",
  "args": ["/root/vivid_mas/mcp/facebook-ads-mcp-server/server.py"],
  "env": {
    "FACEBOOK_ACCESS_TOKEN": "{{ $env.FACEBOOK_ACCESS_TOKEN }}",
    "LOG_LEVEL": "INFO"
  }
}
```

### **Execute Node Configuration:**
```json
{
  "serverName": "facebook-ads-mcp",
  "toolName": "{{ $json.toolName }}",
  "arguments": "{{ $json.arguments }}",
  "command": "/root/vivid_mas/mcp/facebook-ads-mcp-server/venv/bin/python",
  "args": ["/root/vivid_mas/mcp/facebook-ads-mcp-server/server.py"],
  "env": {
    "FACEBOOK_ACCESS_TOKEN": "{{ $env.FACEBOOK_ACCESS_TOKEN }}",
    "LOG_LEVEL": "INFO"
  }
}
```

### **Available Facebook Ads Tools:**

**Core Campaign Management:**
- `list_ad_accounts` - List all ad accounts
- `create_campaign` - Create new campaigns
- `update_campaign` - Update existing campaigns
- `delete_campaign` - Delete campaigns
- `create_adset` - Create new ad sets
- `update_adset` - Update ad sets
- `delete_adset` - Delete ad sets
- `create_ad` - Create new ads
- `update_ad` - Update ads
- `delete_ad` - Delete ads
- `create_ad_creative` - Create ad creatives

**✨ NEW: Audience Management (from Events Manager):**
- `create_custom_audience` - Create custom audiences with app data
- `get_custom_audiences` - List existing custom audiences
- `create_lookalike_audience` - Create lookalike audiences
- `delete_custom_audience` - Remove custom audiences

**✨ NEW: Event Tracking & Conversions (from Events Manager):**
- `create_custom_conversion` - Track specific customer actions
- `get_custom_conversions` - List custom conversions
- `get_pixels` - Get Facebook Pixels for tracking
- `get_events` - Get events tracked by pixels

**Analytics & Bulk Operations:**
- `get_instagram_accounts` - Get Instagram accounts
- `bulk_update_campaigns` - Bulk campaign updates
- `get_ad_account_info` - Detailed account information (Ad Account ID: 1015508332916961)
- *(49 total tools available)*

## 🛒 Shopify MCP Server Configuration

### **List_Tools Node Configuration:**
```json
{
  "serverName": "shopify-mcp",
  "command": "node",
  "args": ["/root/vivid_mas/mcp/shopify-mcp-server/dist/index.js"],
  "env": {
    "SHOPIFY_STORE_URL": "{{ $env.SHOPIFY_STORE_URL }}",
    "SHOPIFY_ACCESS_TOKEN": "{{ $env.SHOPIFY_ACCESS_TOKEN }}",
    "SHOPIFY_API_VERSION": "2024-01"
  }
}
```

### **Execute Node Configuration:**
```json
{
  "serverName": "shopify-mcp",
  "toolName": "{{ $json.toolName }}",
  "arguments": "{{ $json.arguments }}",
  "command": "node",
  "args": ["/root/vivid_mas/mcp/shopify-mcp-server/dist/index.js"],
  "env": {
    "SHOPIFY_STORE_URL": "{{ $env.SHOPIFY_STORE_URL }}",
    "SHOPIFY_ACCESS_TOKEN": "{{ $env.SHOPIFY_ACCESS_TOKEN }}",
    "SHOPIFY_API_VERSION": "2024-01"
  }
}
```

### **Available Shopify Tools:**
- `get_products` - List products
- `get_product` - Get product details
- `create_product` - Create new products
- `update_product` - Update products
- `delete_product` - Delete products
- `get_orders` - List orders
- `create_order` - Create orders
- `update_order` - Update orders
- `get_customers` - List customers
- `create_customer` - Create customers
- `get_collections` - List collections
- `get_inventory` - Check inventory
- *(24 total tools available)*

## 🖼️ Pictorem MCP Server Configuration

### **List_Tools Node Configuration:**
```json
{
  "serverName": "pictorem-mcp",
  "command": "node",
  "args": ["/root/vivid_mas/mcp/pictorem-mcp-server/dist/index.js"],
  "env": {
    "PICTOREM_USERNAME": "{{ $env.PICTOREM_USERNAME }}",
    "PICTOREM_PASSWORD": "{{ $env.PICTOREM_PASSWORD }}",
    "PICTOREM_API_BASE": "https://api.pictorem.com"
  }
}
```

### **Execute Node Configuration:**
```json
{
  "serverName": "pictorem-mcp",
  "toolName": "{{ $json.toolName }}",
  "arguments": "{{ $json.arguments }}",
  "command": "node",
  "args": ["/root/vivid_mas/mcp/pictorem-mcp-server/dist/index.js"],
  "env": {
    "PICTOREM_USERNAME": "{{ $env.PICTOREM_USERNAME }}",
    "PICTOREM_PASSWORD": "{{ $env.PICTOREM_PASSWORD }}",
    "PICTOREM_API_BASE": "https://api.pictorem.com"
  }
}
```

### **Available Pictorem Tools:**
- `get_products` - List available print products
- `get_pricing` - Get pricing for products
- `calculate_vividwalls_pricing` - VividWalls-specific pricing
- `upload_image` - Upload artwork for printing
- `create_order` - Submit print orders
- `get_order_status` - Check order status
- `get_shipping_rates` - Calculate shipping
- `validate_image` - Check image quality
- *(15 total tools available)*

## 🔧 Environment Variables Configuration

### **In n8n Environment (.env):**
```bash
# Facebook Ads MCP
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here

# Shopify MCP
SHOPIFY_STORE_URL=vividwalls-2.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token_here
SHOPIFY_API_VERSION=2024-01

# Pictorem MCP
PICTOREM_USERNAME=kingler@me.com
PICTOREM_PASSWORD=your_pictorem_password_here
PICTOREM_API_BASE=https://api.pictorem.com
```

## 📋 n8n Workflow Configuration Examples

### **Example 1: VividWalls Order Fulfillment Agent**
```json
{
  "name": "VividWalls Order Fulfillment",
  "nodes": [
    {
      "name": "Shopify - Get New Orders",
      "type": "MCP Client",
      "config": "shopify-mcp",
      "operation": "Execute",
      "parameters": {
        "toolName": "get_orders",
        "arguments": {
          "status": "unfulfilled",
          "limit": 10
        }
      }
    },
    {
      "name": "Pictorem - Submit Print Order",
      "type": "MCP Client", 
      "config": "pictorem-mcp",
      "operation": "Execute",
      "parameters": {
        "toolName": "create_order",
        "arguments": {
          "product_id": "{{ $json.product_id }}",
          "image_url": "{{ $json.image_url }}",
          "quantity": "{{ $json.quantity }}"
        }
      }
    }
  ]
}
```

### **Example 2: Facebook Ads Campaign Creation Agent**
```json
{
  "name": "VividWalls Marketing Campaign",
  "nodes": [
    {
      "name": "Facebook - Create Campaign",
      "type": "MCP Client",
      "config": "facebook-ads-mcp",
      "operation": "Execute", 
      "parameters": {
        "toolName": "create_campaign",
        "arguments": {
          "ad_account_id": "act_777751590847461",
          "name": "VividWalls {{ $json.collection_name }} Collection",
          "objective": "OUTCOME_TRAFFIC",
          "daily_budget": 500,
          "special_ad_categories": ["NONE"]
        }
      }
    },
    {
      "name": "Facebook - Create Ad Set",
      "type": "MCP Client",
      "config": "facebook-ads-mcp", 
      "operation": "Execute",
      "parameters": {
        "toolName": "create_adset",
        "arguments": {
          "ad_account_id": "act_777751590847461",
          "campaign_id": "{{ $json.campaign_id }}",
          "name": "Art Enthusiasts Targeting",
          "optimization_goal": "CLICKS",
          "billing_event": "CLICKS",
          "daily_budget": 300
        }
      }
    }
  ]
}
```

## 🎯 Agent-Specific Configurations

### **Facebook Ads Agent:**
- **Purpose**: Campaign management and Instagram promotion
- **Tools Focus**: Campaign CRUD, creative management, insights
- **VividWalls Use**: Art collection promotion, retargeting

### **Shopify Agent:**
- **Purpose**: Order processing and inventory management  
- **Tools Focus**: Order fulfillment, product management
- **VividWalls Use**: Process canvas orders, update inventory

### **Pictorem Agent:**
- **Purpose**: Print-on-demand fulfillment
- **Tools Focus**: Order submission, pricing, tracking
- **VividWalls Use**: Submit print orders with VividWalls pricing

## 🔗 Integration Flow Example

```
New Shopify Order → Shopify Agent (get order details)
                 ↓
Extract artwork URL → Pictorem Agent (calculate pricing)
                 ↓
Submit print order → Pictorem Agent (create order)
                 ↓
Update Shopify → Shopify Agent (mark as fulfilled)
                 ↓
Create retargeting ad → Facebook Agent (create campaign)
```

## 🚀 Quick Setup Checklist

1. ✅ **Deploy all MCP servers** to Digital Ocean droplet
2. ✅ **Configure environment variables** in n8n
3. ✅ **Test List_Tools** for each MCP server
4. ✅ **Test Execute** with simple operations
5. ✅ **Build agent workflows** for order fulfillment
6. ✅ **Configure error handling** and retry logic
7. ✅ **Set up monitoring** for MCP server health

This configuration enables complete VividWalls automation across Shopify orders, Pictorem fulfillment, and Facebook advertising!