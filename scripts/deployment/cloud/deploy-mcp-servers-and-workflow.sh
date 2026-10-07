#!/bin/bash

# VividWalls E-commerce Order Fulfillment System Deployment
# This script deploys both Shopify and Pictorem MCP servers and the n8n workflow

set -e

# Configuration
DROPLET_IP="157.230.13.13"
DROPLET_USER="root"
PROJECT_ROOT="/root/vivid_mas"
MCP_DIR="${PROJECT_ROOT}/mcp"
N8N_WORKFLOWS_DIR="${PROJECT_ROOT}/n8n/workflows"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Function to check if we're running on the droplet
check_environment() {
    if [[ "$(hostname -I | awk '{print $1}')" == "$DROPLET_IP" ]]; then
        log "Running on Digital Ocean droplet"
        REMOTE_EXEC=""
    else
        log "Running locally, will execute commands on droplet via SSH"
        REMOTE_EXEC="ssh -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_IP"
    fi
}

# Function to install MCP dependencies
install_mcp_dependencies() {
    log "Installing MCP server dependencies..."
    
    $REMOTE_EXEC << 'EOF'
# Install Node.js and npm if not already installed
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    apt-get install -y nodejs
fi

# Install global MCP packages
npm install -g @modelcontextprotocol/sdk
npm install -g typescript ts-node

# Verify installations
node --version
npm --version
EOF
}

# Function to build and setup Shopify MCP server
setup_shopify_mcp() {
    log "Setting up Shopify MCP server..."
    
    $REMOTE_EXEC << EOF
cd $MCP_DIR/shopify-mcp-server

# Install dependencies
npm install

# Build the TypeScript project
npm run build

# Create environment file for Shopify MCP
cat > .env << 'ENV_FILE'
SHOPIFY_ACCESS_TOKEN=${SHOPIFY_ACCESS_TOKEN:-your-shopify-access-token}
MYSHOPIFY_DOMAIN=${MYSHOPIFY_DOMAIN:-vividwalls.myshopify.com}
ENV_FILE

# Make the server executable
chmod +x dist/index.js

log "Shopify MCP server setup complete"
EOF
}

# Function to create Pictorem MCP server
create_pictorem_mcp() {
    log "Creating Pictorem MCP server..."
    
    $REMOTE_EXEC << 'EOF'
cd /root/vivid_mas/mcp

# Create Pictorem MCP server directory
mkdir -p pictorem-mcp-server
cd pictorem-mcp-server

# Initialize npm project
npm init -y

# Install dependencies
npm install @modelcontextprotocol/sdk zod axios form-data

# Create TypeScript configuration
cat > tsconfig.json << 'TSCONFIG'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
TSCONFIG

# Create source directory
mkdir -p src

# Create the main Pictorem MCP server
cat > src/index.ts << 'PICTOREM_SERVER'
#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios from "axios";
import FormData from "form-data";

const server = new McpServer({
  name: "pictorem-tools",
  version: "1.0.0",
});

// Pictorem API configuration
const PICTOREM_BASE_URL = "https://www.pictorem.com";
const PICTOREM_USERNAME = process.env.PICTOREM_USERNAME || "kingler@me.com";
const PICTOREM_PASSWORD = process.env.PICTOREM_PASSWORD || "REDACTED_SET_PICTOREM_PASSWORD_ENV";

// Authentication helper
let authToken: string | null = null;

async function authenticate(): Promise<string> {
  if (authToken) return authToken;
  
  try {
    const response = await axios.post(`${PICTOREM_BASE_URL}/api/auth/login`, {
      username: PICTOREM_USERNAME,
      password: PICTOREM_PASSWORD
    });
    
    authToken = response.data.token;
    return authToken;
  } catch (error) {
    throw new Error(`Authentication failed: ${error.message}`);
  }
}

// Order Configuration Schema
const OrderConfigSchema = z.object({
  shopify_order_id: z.string(),
  order_number: z.string(),
  customer_info: z.object({
    email: z.string().email(),
    name: z.string(),
    shipping_address: z.object({
      address1: z.string(),
      address2: z.string().optional(),
      city: z.string(),
      province: z.string(),
      country: z.string(),
      zip: z.string()
    })
  }),
  product_configuration: z.object({
    product_type: z.enum(["canvas", "framed", "canvas_roll", "mural", "panel", "acrylic", "metal", "wood", "poster"]),
    size: z.object({
      width: z.number().min(1).max(120),
      height: z.number().min(1).max(120),
      unit: z.literal("inches")
    }),
    canvas_type: z.enum(["stretched", "roll"]).optional(),
    frame_options: z.object({
      frame_type: z.enum(["none", "standard", "premium_white", "truffle"]),
      frame_cost: z.number().optional()
    }).optional(),
    quantity: z.number().min(1)
  }),
  image_data: z.object({
    file_path: z.string(),
    file_name: z.string(),
    file_format: z.enum(["jpg", "png", "pdf", "ai", "eps"]),
    file_size: z.number().max(100 * 1024 * 1024), // 100MB max
    upload_url: z.string().url()
  }),
  pricing: z.object({
    base_price: z.number(),
    pro_discount: z.number().default(0.15),
    canvas_roll_discount: z.number().default(0.25),
    vividwalls_markup: z.number().default(2.065),
    shipping_cost: z.number().optional()
  })
});

// Submit Order Tool
server.tool(
  "submit-order",
  "Submit a print order to Pictorem",
  {
    orderData: z.object({}).passthrough().describe("Complete order data following the Pictorem schema")
  },
  async ({ orderData }) => {
    try {
      // Validate order data
      const validatedOrder = OrderConfigSchema.parse(orderData);
      
      // Authenticate with Pictorem
      const token = await authenticate();
      
      // Calculate final pricing
      const basePrice = validatedOrder.pricing.base_price;
      const proDiscount = validatedOrder.pricing.pro_discount;
      const canvasRollDiscount = validatedOrder.product_configuration.canvas_type === "roll" 
        ? validatedOrder.pricing.canvas_roll_discount : 0;
      
      const totalDiscount = proDiscount + canvasRollDiscount;
      const discountedPrice = basePrice * (1 - totalDiscount);
      const finalPrice = discountedPrice * validatedOrder.pricing.vividwalls_markup;
      
      // Prepare Pictorem order payload
      const pictoremOrder = {
        product_type: validatedOrder.product_configuration.product_type,
        width: validatedOrder.product_configuration.size.width,
        height: validatedOrder.product_configuration.size.height,
        canvas_type: validatedOrder.product_configuration.canvas_type,
        frame_type: validatedOrder.product_configuration.frame_options?.frame_type || "none",
        quantity: validatedOrder.product_configuration.quantity,
        image_url: validatedOrder.image_data.upload_url,
        customer_email: validatedOrder.customer_info.email,
        shipping_address: validatedOrder.customer_info.shipping_address,
        order_reference: validatedOrder.shopify_order_id,
        pricing: {
          base_price: basePrice,
          final_price: finalPrice,
          discount_applied: totalDiscount
        }
      };
      
      // Submit to Pictorem API
      const response = await axios.post(
        `${PICTOREM_BASE_URL}/api/orders/submit`,
        pictoremOrder,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: true,
            pictorem_order_id: response.data.order_id,
            order_status: response.data.status,
            estimated_delivery: response.data.estimated_delivery,
            final_price: finalPrice,
            tracking_url: response.data.tracking_url
          }, null, 2)
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
          }, null, 2)
        }],
        isError: true
      };
    }
  }
);

// Get Order Status Tool
server.tool(
  "get-order-status",
  "Get the status of a Pictorem order",
  {
    pictoremOrderId: z.string().describe("Pictorem order ID to check status for")
  },
  async ({ pictoremOrderId }) => {
    try {
      const token = await authenticate();
      
      const response = await axios.get(
        `${PICTOREM_BASE_URL}/api/orders/${pictoremOrderId}/status`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify(response.data, null, 2)
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
          }, null, 2)
        }],
        isError: true
      };
    }
  }
);

// Calculate Pricing Tool
server.tool(
  "calculate-pricing",
  "Calculate final pricing for a Pictorem order",
  {
    basePrice: z.number().describe("Base price from Pictorem"),
    productType: z.enum(["canvas", "canvas_roll"]).describe("Product type for discount calculation"),
    size: z.object({
      width: z.number(),
      height: z.number()
    }).describe("Product dimensions")
  },
  async ({ basePrice, productType, size }) => {
    try {
      // VividWalls pricing logic
      const proDiscount = 0.15; // 15% Pro account discount
      const canvasRollDiscount = productType === "canvas_roll" ? 0.25 : 0; // 25% additional for canvas roll
      const vividwallsMarkup = 2.065; // 106.5% markup
      
      const totalDiscount = proDiscount + canvasRollDiscount;
      const discountedPrice = basePrice * (1 - totalDiscount);
      const finalPrice = discountedPrice * vividwallsMarkup;
      
      // Calculate square inches for size validation
      const squareInches = size.width * size.height;
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            base_price: basePrice,
            pro_discount: proDiscount,
            canvas_roll_discount: canvasRollDiscount,
            total_discount: totalDiscount,
            discounted_price: discountedPrice,
            vividwalls_markup: vividwallsMarkup,
            final_price: finalPrice,
            square_inches: squareInches,
            size_category: squareInches <= 144 ? "small" : squareInches <= 576 ? "medium" : "large"
          }, null, 2)
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: false,
            error: error.message
          }, null, 2)
        }],
        isError: true
      };
    }
  }
);

// Upload Image Tool
server.tool(
  "upload-image",
  "Upload an image file to Pictorem",
  {
    imageUrl: z.string().url().describe("URL of the image to upload"),
    fileName: z.string().describe("Name of the file"),
    orderReference: z.string().describe("Reference to associate with the upload")
  },
  async ({ imageUrl, fileName, orderReference }) => {
    try {
      const token = await authenticate();
      
      // Download image from URL
      const imageResponse = await axios.get(imageUrl, { responseType: 'stream' });
      
      // Create form data for upload
      const formData = new FormData();
      formData.append('file', imageResponse.data, fileName);
      formData.append('order_reference', orderReference);
      
      // Upload to Pictorem
      const uploadResponse = await axios.post(
        `${PICTOREM_BASE_URL}/api/images/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            ...formData.getHeaders()
          }
        }
      );
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: true,
            upload_id: uploadResponse.data.upload_id,
            file_url: uploadResponse.data.file_url,
            file_size: uploadResponse.data.file_size,
            image_dimensions: uploadResponse.data.dimensions
          }, null, 2)
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: false,
            error: error.message
          }, null, 2)
        }],
        isError: true
      };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Pictorem MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
PICTOREM_SERVER

# Create environment file
cat > .env << 'ENV_FILE'
PICTOREM_USERNAME=kingler@me.com
PICTOREM_PASSWORD=REDACTED_SET_PICTOREM_PASSWORD_ENV
ENV_FILE

# Add build script to package.json
npm pkg set scripts.build="tsc"
npm pkg set scripts.start="node dist/index.js"

# Install TypeScript as dev dependency
npm install -D typescript @types/node

# Build the server
npm run build

# Make executable
chmod +x dist/index.js

log "Pictorem MCP server created and built successfully"
EOF
}

# Function to setup n8n MCP credentials
setup_n8n_mcp_credentials() {
    log "Setting up n8n MCP credentials..."
    
    $REMOTE_EXEC << EOF
# Create n8n credentials directory if it doesn't exist
mkdir -p $PROJECT_ROOT/.n8n/credentials

# Shopify MCP Credentials
cat > $PROJECT_ROOT/.n8n/credentials/shopify-mcp.json << 'SHOPIFY_CREDS'
{
  "name": "Shopify MCP Server (STDIO)",
  "type": "mcpClientApi",
  "data": {
    "connectionType": "stdio",
    "command": "node",
    "arguments": ["$MCP_DIR/shopify-mcp-server/dist/index.js"],
    "environmentVariables": "SHOPIFY_ACCESS_TOKEN=\${SHOPIFY_ACCESS_TOKEN}\nMYSHOPIFY_DOMAIN=\${MYSHOPIFY_DOMAIN}"
  }
}
SHOPIFY_CREDS

# Pictorem MCP Credentials  
cat > $PROJECT_ROOT/.n8n/credentials/pictorem-mcp.json << 'PICTOREM_CREDS'
{
  "name": "Pictorem MCP Server (STDIO)",
  "type": "mcpClientApi", 
  "data": {
    "connectionType": "stdio",
    "command": "node",
    "arguments": ["$MCP_DIR/pictorem-mcp-server/dist/index.js"],
    "environmentVariables": "PICTOREM_USERNAME=kingler@me.com\nPICTOREM_PASSWORD=REDACTED_SET_PICTOREM_PASSWORD_ENV"
  }
}
PICTOREM_CREDS

log "n8n MCP credentials configured"
EOF
}

# Function to install n8n MCP client node
install_n8n_mcp_node() {
    log "Installing n8n MCP client community node..."
    
    $REMOTE_EXEC << 'EOF'
cd /root/vivid_mas

# Install the MCP client community node
docker exec vivid_mas-n8n-1 npm install n8n-nodes-mcp

# Set environment variable to allow community node tools
docker exec vivid_mas-n8n-1 sh -c 'echo "N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true" >> /usr/local/lib/node_modules/n8n/.env'

# Restart n8n to load the new node
docker restart vivid_mas-n8n-1

log "n8n MCP client node installed and configured"
EOF
}

# Function to deploy the workflow
deploy_workflow() {
    log "Deploying e-commerce order fulfillment workflow to n8n..."
    
    # Copy workflow to droplet if running locally
    if [[ -n "$REMOTE_EXEC" ]]; then
        scp n8n/workflows/ecommerce-order-fulfillment-workflow.json $DROPLET_USER@$DROPLET_IP:$N8N_WORKFLOWS_DIR/
    fi
    
    $REMOTE_EXEC << EOF
# Ensure workflows directory exists
mkdir -p $N8N_WORKFLOWS_DIR

# Import workflow into n8n via API (n8n must be running)
# Wait for n8n to be ready
sleep 30

# Use n8n CLI to import workflow
docker exec vivid_mas-n8n-1 n8n import:workflow --input=$N8N_WORKFLOWS_DIR/ecommerce-order-fulfillment-workflow.json

log "Workflow deployed successfully"
EOF
}

# Function to test MCP servers
test_mcp_servers() {
    log "Testing MCP server connectivity..."
    
    $REMOTE_EXEC << EOF
cd $MCP_DIR

# Test Shopify MCP server
echo "Testing Shopify MCP server..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node shopify-mcp-server/dist/index.js

# Test Pictorem MCP server  
echo "Testing Pictorem MCP server..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node pictorem-mcp-server/dist/index.js

log "MCP server tests completed"
EOF
}

# Function to create webhook configuration
setup_webhooks() {
    log "Setting up Shopify webhook configuration..."
    
    $REMOTE_EXEC << 'EOF'
# Create webhook configuration script
cat > /root/vivid_mas/scripts/setup-shopify-webhook.js << 'WEBHOOK_SCRIPT'
const axios = require('axios');

const SHOPIFY_DOMAIN = process.env.MYSHOPIFY_DOMAIN || 'vividwalls.myshopify.com';
const ACCESS_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN;
const WEBHOOK_URL = 'https://n8n.vividwalls.blog/webhook/shopify-order-webhook';

async function createWebhook() {
  try {
    const response = await axios.post(
      `https://${SHOPIFY_DOMAIN}/admin/api/2023-10/webhooks.json`,
      {
        webhook: {
          topic: 'orders/create',
          address: WEBHOOK_URL,
          format: 'json'
        }
      },
      {
        headers: {
          'X-Shopify-Access-Token': ACCESS_TOKEN,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Webhook created successfully:', response.data);
  } catch (error) {
    console.error('Error creating webhook:', error.response?.data || error.message);
  }
}

createWebhook();
WEBHOOK_SCRIPT

# Install axios for webhook script
cd /root/vivid_mas
npm install axios

log "Webhook configuration script created"
EOF
}

# Main execution
main() {
    log "Starting VividWalls E-commerce Order Fulfillment System deployment..."
    
    # Check environment
    check_environment
    
    # Install dependencies
    install_mcp_dependencies
    
    # Setup MCP servers
    setup_shopify_mcp
    create_pictorem_mcp
    
    # Configure n8n
    install_n8n_mcp_node
    setup_n8n_mcp_credentials
    
    # Deploy workflow
    deploy_workflow
    
    # Setup webhooks
    setup_webhooks
    
    # Test servers
    test_mcp_servers
    
    log "Deployment completed successfully!"
    info "Next steps:"
    info "1. Configure Shopify webhook: node /root/vivid_mas/scripts/setup-shopify-webhook.js"
    info "2. Test the workflow with a sample order"
    info "3. Monitor n8n logs: docker logs vivid_mas-n8n-1 -f"
    info "4. Access n8n interface: https://n8n.vividwalls.blog"
}

# Run main function
main "$@" 