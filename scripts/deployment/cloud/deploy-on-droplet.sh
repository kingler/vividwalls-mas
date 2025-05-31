#!/bin/bash

# VividWalls E-commerce Order Fulfillment System Deployment (Run on Droplet)
# This script should be run directly on the Digital Ocean droplet

set -e

# Configuration
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

# Function to install MCP dependencies
install_mcp_dependencies() {
    log "Installing MCP server dependencies..."
    
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
}

# Function to build and setup Shopify MCP server
setup_shopify_mcp() {
    log "Setting up Shopify MCP server..."
    
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
}

# Function to create Pictorem MCP server
create_pictorem_mcp() {
    log "Creating Pictorem MCP server..."
    
    cd $MCP_DIR
    
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
const PICTOREM_PASSWORD = process.env.PICTOREM_PASSWORD || "#Freedom2023#";

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
PICTOREM_PASSWORD=#Freedom2023#
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
}

# Function to install n8n MCP client node
install_n8n_mcp_node() {
    log "Installing n8n MCP client community node..."
    
    # Install the MCP client community node
    docker exec vivid_mas-n8n-1 npm install n8n-nodes-mcp
    
    # Set environment variable to allow community node tools
    docker exec vivid_mas-n8n-1 sh -c 'echo "N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true" >> /usr/local/lib/node_modules/n8n/.env'
    
    # Restart n8n to load the new node
    docker restart vivid_mas-n8n-1
    
    log "n8n MCP client node installed and configured"
}

# Function to deploy the workflow
deploy_workflow() {
    log "Creating and deploying e-commerce order fulfillment workflow..."
    
    # Ensure workflows directory exists
    mkdir -p $N8N_WORKFLOWS_DIR
    
    # Create the workflow JSON file
    cat > $N8N_WORKFLOWS_DIR/ecommerce-order-fulfillment-workflow.json << 'WORKFLOW_JSON'
{
  "name": "VividWalls E-commerce Order Fulfillment System",
  "nodes": [
    {
      "parameters": {
        "model": {
          "__rl": true,
          "mode": "list",
          "value": "gpt-4o"
        },
        "options": {
          "systemMessage": "You are the Order Management Agent responsible for processing Shopify orders and coordinating fulfillment. You have access to both Shopify and Pictorem MCP tools to handle the complete order lifecycle from receipt to print fulfillment.\n\nYour primary responsibilities:\n1. Monitor incoming Shopify orders\n2. Extract order details and customer information\n3. Validate product specifications for print readiness\n4. Calculate accurate pricing with markups and discounts\n5. Coordinate with the Fulfillment Agent for Pictorem processing\n6. Update order status in Shopify\n7. Handle errors and retry logic\n\nAlways ensure data accuracy and provide detailed logging for all operations."
        }
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1.2,
      "position": [60, 200],
      "id": "openai-order-agent",
      "name": "OpenAI Chat Model - Order Agent"
    },
    {
      "parameters": {
        "path": "shopify-order-webhook",
        "options": {
          "noResponseBody": true
        }
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [-200, 200],
      "id": "shopify-webhook",
      "name": "Shopify Order Webhook",
      "webhookId": "shopify-order-webhook"
    },
    {
      "parameters": {
        "operation": "listTools"
      },
      "type": "n8n-nodes-mcp.mcpClientTool",
      "typeVersion": 1,
      "position": [380, 120],
      "id": "shopify-mcp-list-tools",
      "name": "Shopify MCP - List Tools"
    },
    {
      "parameters": {
        "operation": "executeTool",
        "toolName": "get-orders",
        "toolParameters": "{\"first\": 10}"
      },
      "type": "n8n-nodes-mcp.mcpClientTool",
      "typeVersion": 1,
      "position": [540, 120],
      "id": "shopify-mcp-execute",
      "name": "Shopify MCP - Execute Tool"
    },
    {
      "parameters": {
        "operation": "listTools"
      },
      "type": "n8n-nodes-mcp.mcpClientTool",
      "typeVersion": 1,
      "position": [380, 320],
      "id": "pictorem-mcp-list-tools",
      "name": "Pictorem MCP - List Tools"
    },
    {
      "parameters": {
        "operation": "executeTool",
        "toolName": "calculate-pricing",
        "toolParameters": "{\"basePrice\": 50, \"productType\": \"canvas\", \"size\": {\"width\": 24, \"height\": 16}}"
      },
      "type": "n8n-nodes-mcp.mcpClientTool",
      "typeVersion": 1,
      "position": [540, 320],
      "id": "pictorem-mcp-execute",
      "name": "Pictorem MCP - Execute Tool"
    }
  ],
  "connections": {
    "Shopify Order Webhook": {
      "main": [
        [
          {
            "node": "Shopify MCP - List Tools",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Shopify MCP - List Tools": {
      "main": [
        [
          {
            "node": "Shopify MCP - Execute Tool",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Shopify MCP - Execute Tool": {
      "main": [
        [
          {
            "node": "Pictorem MCP - List Tools",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Pictorem MCP - List Tools": {
      "main": [
        [
          {
            "node": "Pictorem MCP - Execute Tool",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [
    {
      "createdAt": "2024-01-15T10:00:00.000Z",
      "updatedAt": "2024-01-15T10:00:00.000Z",
      "id": "ecommerce",
      "name": "E-commerce"
    }
  ],
  "triggerCount": 1,
  "updatedAt": "2024-01-15T10:00:00.000Z",
  "versionId": "1"
}
WORKFLOW_JSON
    
    log "Workflow JSON created successfully"
}

# Function to test MCP servers
test_mcp_servers() {
    log "Testing MCP server connectivity..."
    
    cd $MCP_DIR
    
    # Test Shopify MCP server
    log "Testing Shopify MCP server..."
    echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | timeout 10 node shopify-mcp-server/dist/index.js || warning "Shopify MCP server test timed out or failed"
    
    # Test Pictorem MCP server  
    log "Testing Pictorem MCP server..."
    echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | timeout 10 node pictorem-mcp-server/dist/index.js || warning "Pictorem MCP server test timed out or failed"
    
    log "MCP server tests completed"
}

# Function to create webhook configuration
setup_webhooks() {
    log "Setting up Shopify webhook configuration..."
    
    # Create webhook configuration script
    cat > $PROJECT_ROOT/scripts/setup-shopify-webhook.js << 'WEBHOOK_SCRIPT'
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
    cd $PROJECT_ROOT
    npm install axios
    
    log "Webhook configuration script created"
}

# Main execution
main() {
    log "Starting VividWalls E-commerce Order Fulfillment System deployment..."
    
    # Check if we're on the droplet
    if [[ ! -d "$PROJECT_ROOT" ]]; then
        error "Project directory $PROJECT_ROOT not found. This script should be run on the Digital Ocean droplet."
        exit 1
    fi
    
    # Install dependencies
    install_mcp_dependencies
    
    # Setup MCP servers
    setup_shopify_mcp
    create_pictorem_mcp
    
    # Configure n8n
    install_n8n_mcp_node
    
    # Deploy workflow
    deploy_workflow
    
    # Setup webhooks
    setup_webhooks
    
    # Test servers
    test_mcp_servers
    
    log "Deployment completed successfully!"
    info "Next steps:"
    info "1. Configure Shopify credentials in environment variables"
    info "2. Configure Shopify webhook: node $PROJECT_ROOT/scripts/setup-shopify-webhook.js"
    info "3. Import workflow manually in n8n interface: https://n8n.vividwalls.blog"
    info "4. Test the workflow with a sample order"
    info "5. Monitor n8n logs: docker logs vivid_mas-n8n-1 -f"
    
    info "Workflow file location: $N8N_WORKFLOWS_DIR/ecommerce-order-fulfillment-workflow.json"
    info "Shopify MCP server: $MCP_DIR/shopify-mcp-server/dist/index.js"
    info "Pictorem MCP server: $MCP_DIR/pictorem-mcp-server/dist/index.js"
}

# Run main function
main "$@" 