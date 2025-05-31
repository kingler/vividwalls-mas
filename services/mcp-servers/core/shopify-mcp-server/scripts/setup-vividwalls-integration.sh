#!/bin/bash

# VividWalls Shopify CopilotKit Integration Setup Script
# This script sets up the complete VividWalls AI assistant integration for Shopify

set -e

echo "🎨 VividWalls Shopify CopilotKit Integration Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    echo "❌ Error: This script must be run from the shopify-mcp-server directory"
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking environment configuration..."

if [ -z "$SHOPIFY_ACCESS_TOKEN" ]; then
    echo "❌ Error: SHOPIFY_ACCESS_TOKEN environment variable is required"
    echo "   Please set your Shopify private app access token"
    exit 1
fi

if [ -z "$MYSHOPIFY_DOMAIN" ]; then
    echo "❌ Error: MYSHOPIFY_DOMAIN environment variable is required"
    echo "   Please set your shop domain (e.g., your-store.myshopify.com)"
    exit 1
fi

echo "✅ Environment variables configured"

# Build the MCP server
echo "🔨 Building Shopify MCP server..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build MCP server"
    exit 1
fi

echo "✅ MCP server built successfully"

# Make the integration script executable
chmod +x scripts/create-vividwalls-copilot-integration.js

# Run the integration
echo "🚀 Installing VividWalls CopilotKit integration..."
node scripts/create-vividwalls-copilot-integration.js

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ VividWalls CopilotKit integration completed successfully!"
    echo ""
    echo "📋 What was installed:"
    echo "   • AI-powered chat assistant on all store pages"
    echo "   • Product-specific recommendations and help"
    echo "   • Collection browsing assistance"
    echo "   • Room photo analysis capabilities"
    echo "   • Integration with VividWalls n8n workflows"
    echo ""
    echo "🌐 Your customers can now:"
    echo "   • Get personalized art recommendations"
    echo "   • Upload room photos for AI analysis"
    echo "   • Ask questions about products and collections"
    echo "   • Receive sizing and framing advice"
    echo "   • Get help with limited edition information"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Visit your Shopify store to test the integration"
    echo "   2. Look for the floating 'Get Art Recommendations' button"
    echo "   3. Test the AI assistant with various questions"
    echo "   4. Upload a room photo to test image analysis"
    echo "   5. Configure webhook settings if needed"
    echo ""
    echo "📊 Monitoring:"
    echo "   • Check your n8n workflow at: http://157.230.13.13:5678"
    echo "   • Monitor webhook traffic in n8n dashboard"
    echo "   • Review customer interactions for insights"
    echo ""
else
    echo ""
    echo "❌ Integration failed. Please check the error messages above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   • Verify SHOPIFY_ACCESS_TOKEN has theme modification permissions"
    echo "   • Ensure MYSHOPIFY_DOMAIN is correct"
    echo "   • Check that your Shopify app has the required scopes:"
    echo "     - themes"
    echo "     - write_themes"
    echo "     - read_products"
    echo "     - read_collections"
    echo "   • Verify the n8n webhook endpoint is accessible"
    echo ""
    exit 1
fi

# Optional: Create snippet files for advanced integration
echo "📄 Creating optional Liquid snippet files..."
if [ -f "scripts/shopify-vividwalls-snippets.liquid" ]; then
    echo "   • Found shopify-vividwalls-snippets.liquid"
    echo "   • You can manually add these snippets to your theme for enhanced functionality"
else
    echo "   • Snippet file not found, skipping..."
fi

echo ""
echo "🎉 Setup complete! Your VividWalls AI assistant is now live."
echo "   Visit your store to see it in action!"