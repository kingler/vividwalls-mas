#!/bin/bash

# VividMAS Shopify MCP Quick Setup Script
# This script helps you set up the Shopify MCP integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${CYAN}🚀 VividMAS Shopify MCP Setup${NC}"
    echo "=================================="
}

# Check if running from correct directory
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "Please run this script from the VividMAS root directory"
    exit 1
fi

print_header

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_success "Prerequisites check passed"

# Step 2: Install Shopify MCP dependencies
print_info "Installing Shopify MCP dependencies..."

# Create package.json if it doesn't exist
if [[ ! -f "package.json" ]]; then
    print_info "Creating package.json..."
    cat > package.json << EOF
{
  "name": "vividmas-shopify-mcp",
  "version": "1.0.0",
  "description": "VividMAS Shopify MCP Integration",
  "main": "scripts/test-shopify-connection.js",
  "scripts": {
    "test-shopify": "node scripts/test-shopify-connection.js",
    "start-mcp": "node scripts/shopify-mcp-server.js"
  },
  "dependencies": {
    "https": "^1.0.0"
  },
  "devDependencies": {},
  "author": "VividWalls",
  "license": "MIT"
}
EOF
    print_success "Created package.json"
fi

# Install dependencies
npm install

print_success "Dependencies installed"

# Step 3: Set up environment configuration
print_info "Setting up environment configuration..."

if [[ ! -f ".env.shopify" ]]; then
    cp .env.shopify.example .env.shopify
    print_warning "Created .env.shopify file. Please edit it with your Shopify credentials."
else
    print_info ".env.shopify already exists"
fi

print_success "Environment configuration ready"

# Step 4: Update MCP configuration
print_info "Checking MCP configuration..."

if [[ -f ".cursor/mcp.json" ]]; then
    print_success "MCP configuration file found"
    print_info "Shopify MCP integration has been added to your MCP configuration"
else
    print_warning "No MCP configuration file found. The integration has been prepared but may need manual setup."
fi

# Step 5: Create database tables (if using Supabase)
print_info "Database setup information..."
print_warning "You'll need to create the following tables in your Supabase database:"
echo ""
echo "1. vividwalls_products"
echo "2. vividwalls_orders"
echo "3. vividwalls_inventory"
echo "4. customer_analytics"
echo ""
print_info "SQL scripts will be generated in the next step..."

# Step 6: Generate SQL for database setup
print_info "Generating database setup SQL..."

cat > scripts/setup-shopify-database.sql << 'EOF'
-- VividWalls Shopify Integration Database Setup
-- Run this in your Supabase SQL editor

-- Products table
CREATE TABLE IF NOT EXISTS vividwalls_products (
    id SERIAL PRIMARY KEY,
    shopify_id BIGINT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    handle TEXT,
    product_type TEXT,
    tags TEXT[],
    variants JSONB,
    images JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS vividwalls_orders (
    id SERIAL PRIMARY KEY,
    shopify_order_id BIGINT UNIQUE NOT NULL,
    order_number TEXT,
    customer_email TEXT,
    customer_name TEXT,
    shipping_address JSONB,
    line_items JSONB,
    total_price DECIMAL(10,2),
    currency TEXT,
    financial_status TEXT,
    fulfillment_status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory table
CREATE TABLE IF NOT EXISTS vividwalls_inventory (
    id SERIAL PRIMARY KEY,
    variant_id BIGINT UNIQUE NOT NULL,
    inventory_item_id BIGINT,
    sku TEXT,
    current_quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    product_title TEXT,
    variant_title TEXT,
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer analytics table
CREATE TABLE IF NOT EXISTS customer_analytics (
    id SERIAL PRIMARY KEY,
    customer_id BIGINT UNIQUE NOT NULL,
    email TEXT,
    name TEXT,
    total_orders INTEGER DEFAULT 0,
    artwork_purchases INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    preferred_frame TEXT,
    preferred_size TEXT,
    last_order_date TIMESTAMP WITH TIME ZONE,
    customer_since TIMESTAMP WITH TIME ZONE,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_shopify_id ON vividwalls_products(shopify_id);
CREATE INDEX IF NOT EXISTS idx_orders_shopify_id ON vividwalls_orders(shopify_order_id);
CREATE INDEX IF NOT EXISTS idx_inventory_variant_id ON vividwalls_inventory(variant_id);
CREATE INDEX IF NOT EXISTS idx_analytics_customer_id ON customer_analytics(customer_id);

-- Enable RLS (Row Level Security) if needed
-- ALTER TABLE vividwalls_products ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE vividwalls_orders ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE vividwalls_inventory ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE customer_analytics ENABLE ROW LEVEL SECURITY;

EOF

print_success "Database setup SQL generated: scripts/setup-shopify-database.sql"

# Step 7: Make scripts executable
print_info "Making scripts executable..."
chmod +x scripts/test-shopify-connection.js
chmod +x scripts/setup-shopify-mcp.sh

print_success "Scripts are now executable"

# Step 8: Final instructions
echo ""
print_success "🎉 Shopify MCP setup completed!"
echo ""
print_info "Next steps:"
echo "1. Edit .env.shopify with your Shopify store credentials"
echo "2. Create a Shopify private app (see SHOPIFY-MCP-SETUP.md)"
echo "3. Run the database setup SQL in your Supabase console"
echo "4. Test the connection: npm run test-shopify"
echo "5. Import the n8n workflow: n8n/workflows/VividWalls_Shopify_MCP_Basic.json"
echo ""
print_info "Documentation:"
echo "- Setup guide: SHOPIFY-MCP-SETUP.md"
echo "- Test script: scripts/test-shopify-connection.js"
echo "- Database SQL: scripts/setup-shopify-database.sql"
echo ""
print_warning "Remember to keep your Shopify credentials secure!"
echo ""
print_success "Happy automating! 🚀"
