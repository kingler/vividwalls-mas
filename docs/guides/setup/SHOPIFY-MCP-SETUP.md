# Shopify MCP Integration Setup Guide

This guide will help you connect your VividMAS platform to your Shopify store using the Model Context Protocol (MCP).

## 📋 Prerequisites

1. A Shopify store (you already have VividWalls store based on your product data)
2. Admin access to your Shopify store
3. VividMAS platform running with MCP support

## 🔑 Step 1: Create Shopify Private App

1. **Log into your Shopify Admin Panel**
   - Go to your Shopify admin dashboard
   - Navigate to **Settings** → **Apps and sales channels**

2. **Create a Private App**
   - Click **Develop apps for your store**
   - Click **Create an app**
   - Enter app name: `VividMAS AI Integration`
   - Click **Create app**

3. **Configure API Scopes**
   Add the following scopes for your app:

   **Products & Inventory:**
   - `read_products` - View products, variants, and collections
   - `write_products` - Create and modify products, variants, and collections
   - `read_inventory` - View inventory levels and locations
   - `write_inventory` - Adjust inventory levels

   **Orders & Customers:**
   - `read_orders` - View orders
   - `write_orders` - Create and modify orders
   - `read_customers` - View customer information
   - `write_customers` - Create and modify customer information

   **Additional Permissions:**
   - `read_analytics` - View analytics data
   - `read_reports` - View reports
   - `write_checkouts` - Create checkouts

4. **Install the App**
   - Click **Install app**
   - Review and accept the permissions

5. **Get API Credentials**
   - After installation, go to **API credentials** tab
   - Copy the **Admin API access token**
   - Note your store's **myshopify.com URL**

## 🔧 Step 2: Configure Environment Variables

Update your `.cursor/mcp.json` file with your Shopify credentials:

```json
{
  "env": {
    "SHOPIFY_STORE_URL": "your-store-name.myshopify.com",
    "SHOPIFY_ACCESS_TOKEN": "shpat_your_access_token_here",
    "SHOPIFY_API_VERSION": "2024-01"
  }
}
```

**Security Note:** Never commit these credentials to version control. Add them to your local environment or use a secure secrets management system.

## 🚀 Step 3: Install Shopify MCP Server

Install the Shopify MCP server package:

```bash
# Using npm
npm install -g @shopify/shopify-mcp-server

# Or using npx (recommended for testing)
npx @shopify/shopify-mcp-server
```

## 🔌 Step 4: Test the Connection

Create a test script to verify your Shopify connection:

```typescript
// test-shopify-connection.ts
import { ShopifyMCP } from '@shopify/shopify-mcp-server';

const shopify = new ShopifyMCP({
  storeUrl: process.env.SHOPIFY_STORE_URL,
  accessToken: process.env.SHOPIFY_ACCESS_TOKEN,
  apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01'
});

async function testConnection() {
  try {
    const products = await shopify.getProducts({ limit: 5 });
    console.log('✅ Connected to Shopify successfully!');
    console.log(`Found ${products.length} products`);
    return true;
  } catch (error) {
    console.error('❌ Failed to connect to Shopify:', error);
    return false;
  }
}

testConnection();
```

## 🎯 Step 5: Available MCP Functions

Once configured, you'll have access to these Shopify functions through MCP:

### Products
- `mcp_shopify_get_products` - List all products
- `mcp_shopify_get_product` - Get specific product details
- `mcp_shopify_create_product` - Create new products
- `mcp_shopify_update_product` - Update existing products
- `mcp_shopify_delete_product` - Delete products

### Orders
- `mcp_shopify_get_orders` - List orders
- `mcp_shopify_get_order` - Get specific order details
- `mcp_shopify_create_order` - Create new orders
- `mcp_shopify_update_order` - Update order status

### Customers
- `mcp_shopify_get_customers` - List customers
- `mcp_shopify_get_customer` - Get customer details
- `mcp_shopify_create_customer` - Add new customers
- `mcp_shopify_update_customer` - Update customer information

### Collections
- `mcp_shopify_get_collections` - List product collections
- `mcp_shopify_create_collection` - Create new collections
- `mcp_shopify_update_collection` - Update collections

### Inventory
- `mcp_shopify_get_inventory` - Check inventory levels
- `mcp_shopify_update_inventory` - Update stock levels

## 🔄 Step 6: Integration with n8n Workflows

Your VividMAS platform can now use Shopify data in n8n workflows:

1. **Product Sync Workflow**
   - Automatically sync product data between systems
   - Update inventory levels based on sales
   - Generate product recommendations

2. **Order Processing Workflow**
   - Automate order fulfillment
   - Send customer notifications
   - Update inventory after orders

3. **Customer Management Workflow**
   - Segment customers based on purchase history
   - Automate marketing campaigns
   - Generate customer insights

## 🛡️ Security Best Practices

1. **Secure Token Storage**
   - Use environment variables
   - Never commit tokens to git
   - Rotate tokens regularly

2. **API Rate Limiting**
   - Respect Shopify's API limits
   - Implement retry logic
   - Monitor API usage

3. **Permissions**
   - Use minimal required scopes
   - Review permissions regularly
   - Monitor API access logs

## 🔍 Troubleshooting

### Common Issues

1. **Invalid Access Token**
   - Verify token is correct
   - Check token hasn't expired
   - Ensure app is installed

2. **Insufficient Permissions**
   - Review API scopes
   - Reinstall app with correct permissions

3. **Rate Limiting**
   - Implement exponential backoff
   - Reduce request frequency
   - Use bulk operations when possible

### Debug Mode

Enable debug logging by setting:
```bash
export SHOPIFY_DEBUG=true
```

## 📊 Example Use Cases for VividWalls

Based on your product data, here are specific use cases:

1. **Automated Product Updates**
   - Sync artwork metadata
   - Update frame options and pricing
   - Manage product variants (sizes, frames)

2. **Inventory Management**
   - Track frame stock levels
   - Automate reorder notifications
   - Sync with printing partners

3. **Customer Analytics**
   - Analyze purchase patterns
   - Generate art preference insights
   - Personalized product recommendations

4. **Order Automation**
   - Auto-process artwork orders
   - Send to print partners
   - Track fulfillment status

## 🎨 VividWalls Specific Configuration

For your VividWalls store, you may want to focus on these specific integrations:

1. **Art Collections Management**
2. **Frame Options Automation**
3. **Size Variant Handling**
4. **Customer Art Preferences**
5. **Print-on-Demand Integration**

## 📝 Next Steps

1. Set up your Shopify private app
2. Configure environment variables
3. Test the connection
4. Create your first n8n workflow with Shopify integration
5. Monitor and optimize performance

## 🆘 Support

- Shopify API Documentation: https://shopify.dev/docs/api
- MCP Documentation: https://modelcontextprotocol.io/
- VividMAS GitHub Issues: [Your repository issues]

---

**⚠️ Important:** Keep your API credentials secure and never share them publicly. Consider using a secrets management service for production deployments.
