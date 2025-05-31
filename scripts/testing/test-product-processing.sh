#!/bin/bash

# VividWalls Product Classification Test Script
# This script tests the product classification workflow

set -e

echo "🧪 VividWalls Product Classification Test"
echo "========================================"

# Check if workflow is accessible
WEBHOOK_URL="https://n8n.vividwalls.blog/webhook/vividwalls-product-processor"

echo "🔗 Testing webhook endpoint: $WEBHOOK_URL"

# Test webhook accessibility
if curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" | grep -q "404"; then
    echo "⚠️  Webhook returns 404 - workflow may not be imported or activated"
    echo "   Please ensure the workflow is imported and activated in n8n"
    echo "   Workflow file: n8n/shared/knowledge/VividWalls-Product-Classification-Workflow.json"
    exit 1
elif curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" | grep -q "405"; then
    echo "✅ Webhook is accessible (405 Method Not Allowed is expected for GET request)"
else
    echo "❓ Unexpected response from webhook endpoint"
fi

# Test with sample data
echo "📊 Sending test payload to workflow..."

# Create test payload
TEST_PAYLOAD='{
  "test_mode": true,
  "batch_size": 2,
  "start_row": 1,
  "end_row": 3,
  "process_images": true,
  "skip_existing": false
}'

echo "📤 Test payload:"
echo "$TEST_PAYLOAD" | jq .

# Send test request
echo "🚀 Triggering workflow..."

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD" \
  "$WEBHOOK_URL")

echo "📥 Response:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"

# Check if response indicates success
if echo "$RESPONSE" | grep -q "success\|started\|processing"; then
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "📊 Monitor progress at: https://n8n.vividwalls.blog"
    echo "   - Go to Executions tab"
    echo "   - Look for 'VividWalls Product Classification' workflow"
    echo ""
    echo "🔍 Check Supabase database for processed products:"
    echo "   - Products table: SELECT * FROM products LIMIT 5;"
    echo "   - Analysis table: SELECT * FROM product_analysis LIMIT 5;"
    echo "   - Images table: SELECT * FROM product_images LIMIT 5;"
else
    echo "❌ Workflow may not have triggered successfully"
    echo "   Response: $RESPONSE"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check if workflow is imported and activated in n8n"
    echo "2. Verify all credentials are configured in n8n"
    echo "3. Check n8n execution logs for errors"
    echo "4. Ensure environment variables are set correctly"
fi

echo ""
echo "🔗 Useful links:"
echo "   - n8n Dashboard: https://n8n.vividwalls.blog"
echo "   - Supabase Dashboard: https://supabase.com/dashboard"
echo "   - Digital Ocean Spaces: https://cloud.digitalocean.com/spaces" 