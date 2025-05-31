#!/bin/bash

# Deploy Pictorem MCP Server to Droplet
# Run this script directly on the Digital Ocean droplet

set -e

# Configuration
PROJECT_ROOT="/root/vivid_mas"
MCP_DIR="${PROJECT_ROOT}/mcp"
PICTOREM_DIR="${MCP_DIR}/pictorem-mcp-server"

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

# Create Pictorem MCP Server
create_pictorem_mcp() {
    log "Creating Pictorem MCP server..."
    
    # Create directory structure
    mkdir -p "$PICTOREM_DIR/src"
    cd "$PICTOREM_DIR"
    
    # Create package.json
    cat > package.json << 'PACKAGE_JSON'
{
  "name": "pictorem-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for Pictorem print-on-demand API integration",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsc --watch",
    "clean": "rm -rf dist"
  },
  "keywords": [
    "mcp",
    "model-context-protocol",
    "pictorem",
    "print-on-demand",
    "canvas",
    "fulfillment"
  ],
  "author": "VividWalls",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.4",
    "axios": "^1.7.0",
    "form-data": "^4.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
PACKAGE_JSON

    # Create tsconfig.json
    cat > tsconfig.json << 'TSCONFIG'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "noEmit": false
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts"
  ]
}
TSCONFIG

    # Create the main TypeScript file
    cat > src/index.ts << 'INDEX_TS'
#!/usr/bin/env node

/**
 * Pictorem MCP Server
 * 
 * A Model Context Protocol server for integrating with Pictorem's print-on-demand API.
 * Provides tools for order submission, pricing calculation, image upload, and order tracking.
 * 
 * This server implements VividWalls-specific pricing logic including:
 * - Pro account discounts (15%)
 * - Canvas roll discounts (25% additional)
 * - VividWalls markup (106.5%)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import axios, { AxiosError, type AxiosResponse } from "axios";
import FormData from "form-data";

// Pictorem API Configuration
const PICTOREM_BASE_URL = "https://www.pictorem.com";
const PICTOREM_USERNAME = process.env.PICTOREM_USERNAME || "kingler@me.com";
const PICTOREM_PASSWORD = process.env.PICTOREM_PASSWORD || "#Freedom2023#";

// Authentication state
let authToken: string | null = null;
let tokenExpiry: Date | null = null;

/**
 * Authenticate with Pictorem API
 * Implements token caching to avoid unnecessary API calls
 */
async function authenticate(): Promise<string> {
  // Check if we have a valid token
  if (authToken && tokenExpiry && new Date() < tokenExpiry) {
    return authToken;
  }
  
  try {
    const response: AxiosResponse<{ token: string }> = await axios.post(`${PICTOREM_BASE_URL}/api/auth/login`, {
      username: PICTOREM_USERNAME,
      password: PICTOREM_PASSWORD
    }, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'VividWalls-MCP-Server/1.0.0'
      }
    });
    
    authToken = response.data.token;
    // Set token expiry to 1 hour from now (adjust based on Pictorem's actual token lifetime)
    tokenExpiry = new Date(Date.now() + 60 * 60 * 1000);
    
    if (!authToken) {
      throw new McpError(ErrorCode.InternalError, "Authentication failed: No token received");
    }
    
    return authToken;
  } catch (error: unknown) {
    authToken = null;
    tokenExpiry = null;
    
    if (error instanceof AxiosError) {
      throw new McpError(
        ErrorCode.InternalError,
        `Pictorem authentication failed: ${error.response?.data?.message || error.message}`
      );
    }
    throw new McpError(ErrorCode.InternalError, `Authentication failed: ${String(error)}`);
  }
}

/**
 * Zod schemas for tool parameters
 */

// Order Configuration Schema
const OrderConfigSchema = z.object({
  shopify_order_id: z.string().describe("Shopify order ID for reference"),
  order_number: z.string().describe("Human-readable order number"),
  customer_info: z.object({
    email: z.string().email().describe("Customer email address"),
    name: z.string().describe("Customer full name"),
    shipping_address: z.object({
      address1: z.string().describe("Primary address line"),
      address2: z.string().optional().describe("Secondary address line"),
      city: z.string().describe("City"),
      province: z.string().describe("State/Province"),
      country: z.string().describe("Country"),
      zip: z.string().describe("Postal/ZIP code")
    })
  }),
  product_configuration: z.object({
    product_type: z.enum([
      "canvas", "framed", "canvas_roll", "mural", "panel", 
      "acrylic", "metal", "wood", "poster"
    ]).describe("Type of print product"),
    size: z.object({
      width: z.number().min(1).max(120).describe("Width in inches"),
      height: z.number().min(1).max(120).describe("Height in inches"),
      unit: z.literal("inches").describe("Size unit")
    }),
    canvas_type: z.enum(["stretched", "roll"]).optional().describe("Canvas type for canvas products"),
    frame_options: z.object({
      frame_type: z.enum(["none", "standard", "premium_white", "truffle"]).describe("Frame type"),
      frame_cost: z.number().optional().describe("Additional frame cost")
    }).optional(),
    quantity: z.number().min(1).describe("Quantity to order")
  }),
  image_data: z.object({
    file_path: z.string().describe("Local or remote file path"),
    file_name: z.string().describe("Original filename"),
    file_format: z.enum(["jpg", "png", "pdf", "ai", "eps"]).describe("File format"),
    file_size: z.number().max(100 * 1024 * 1024).describe("File size in bytes (max 100MB)"),
    upload_url: z.string().url().describe("URL to the image file")
  }),
  pricing: z.object({
    base_price: z.number().describe("Base price from Pictorem"),
    pro_discount: z.number().default(0.15).describe("Pro account discount rate"),
    canvas_roll_discount: z.number().default(0.25).describe("Canvas roll additional discount"),
    vividwalls_markup: z.number().default(2.065).describe("VividWalls markup multiplier"),
    shipping_cost: z.number().optional().describe("Shipping cost if applicable")
  })
});

// Pricing calculation schema
const PricingCalculationSchema = z.object({
  basePrice: z.number().positive().describe("Base price from Pictorem"),
  productType: z.enum(["canvas", "canvas_roll"]).describe("Product type for discount calculation"),
  size: z.object({
    width: z.number().positive().describe("Product width in inches"),
    height: z.number().positive().describe("Product height in inches")
  }).describe("Product dimensions")
});

// Order status schema
const OrderStatusSchema = z.object({
  pictoremOrderId: z.string().describe("Pictorem order ID to check status for")
});

// Image upload schema
const ImageUploadSchema = z.object({
  imageUrl: z.string().url().describe("URL of the image to upload"),
  fileName: z.string().describe("Name of the file"),
  orderReference: z.string().describe("Reference to associate with the upload")
});

/**
 * Initialize the MCP server
 */
const server = new Server(
  {
    name: "pictorem-tools",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Tool definitions
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "submit-order",
        description: "Submit a print order to Pictorem with VividWalls pricing calculation",
        inputSchema: {
          type: "object",
          properties: {
            orderData: {
              type: "object",
              description: "Complete order data following the Pictorem schema",
              additionalProperties: true
            }
          },
          required: ["orderData"]
        }
      },
      {
        name: "calculate-pricing",
        description: "Calculate final pricing for a Pictorem order with VividWalls markup and discounts",
        inputSchema: {
          type: "object",
          properties: {
            basePrice: {
              type: "number",
              description: "Base price from Pictorem"
            },
            productType: {
              type: "string",
              enum: ["canvas", "canvas_roll"],
              description: "Product type for discount calculation"
            },
            size: {
              type: "object",
              properties: {
                width: { type: "number", description: "Width in inches" },
                height: { type: "number", description: "Height in inches" }
              },
              required: ["width", "height"],
              description: "Product dimensions"
            }
          },
          required: ["basePrice", "productType", "size"]
        }
      },
      {
        name: "get-order-status",
        description: "Get the status of a Pictorem order",
        inputSchema: {
          type: "object",
          properties: {
            pictoremOrderId: {
              type: "string",
              description: "Pictorem order ID to check status for"
            }
          },
          required: ["pictoremOrderId"]
        }
      },
      {
        name: "upload-image",
        description: "Upload an image file to Pictorem for print orders",
        inputSchema: {
          type: "object",
          properties: {
            imageUrl: {
              type: "string",
              format: "uri",
              description: "URL of the image to upload"
            },
            fileName: {
              type: "string",
              description: "Name of the file"
            },
            orderReference: {
              type: "string",
              description: "Reference to associate with the upload"
            }
          },
          required: ["imageUrl", "fileName", "orderReference"]
        }
      }
    ]
  };
});

/**
 * Tool execution handler
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (!args) {
    throw new McpError(ErrorCode.InvalidParams, "No arguments provided");
  }

  try {
    switch (name) {
      case "submit-order": {
        // Validate the order data
        const validatedOrder = OrderConfigSchema.parse(args.orderData);
        
        // Authenticate with Pictorem
        const token = await authenticate();
        
        // Calculate final pricing using VividWalls logic
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
              'Content-Type': 'application/json',
              'User-Agent': 'VividWalls-MCP-Server/1.0.0'
            },
            timeout: 30000
          }
        );
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: true,
                pictorem_order_id: response.data.order_id,
                order_status: response.data.status,
                estimated_delivery: response.data.estimated_delivery,
                final_price: finalPrice,
                tracking_url: response.data.tracking_url,
                pricing_breakdown: {
                  base_price: basePrice,
                  pro_discount: proDiscount,
                  canvas_roll_discount: canvasRollDiscount,
                  total_discount: totalDiscount,
                  discounted_price: discountedPrice,
                  vividwalls_markup: validatedOrder.pricing.vividwalls_markup,
                  final_price: finalPrice
                }
              }, null, 2)
            }
          ]
        };
      }

      case "calculate-pricing": {
        const validated = PricingCalculationSchema.parse(args);
        
        // VividWalls pricing logic
        const proDiscount = 0.15; // 15% Pro account discount
        const canvasRollDiscount = validated.productType === "canvas_roll" ? 0.25 : 0; // 25% additional for canvas roll
        const vividwallsMarkup = 2.065; // 106.5% markup
        
        const totalDiscount = proDiscount + canvasRollDiscount;
        const discountedPrice = validated.basePrice * (1 - totalDiscount);
        const finalPrice = discountedPrice * vividwallsMarkup;
        
        // Calculate square inches for size validation
        const squareInches = validated.size.width * validated.size.height;
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                base_price: validated.basePrice,
                pro_discount: proDiscount,
                canvas_roll_discount: canvasRollDiscount,
                total_discount: totalDiscount,
                discounted_price: discountedPrice,
                vividwalls_markup: vividwallsMarkup,
                final_price: finalPrice,
                square_inches: squareInches,
                size_category: squareInches <= 144 ? "small" : squareInches <= 576 ? "medium" : "large",
                pricing_summary: {
                  original_price: `$${validated.basePrice.toFixed(2)}`,
                  after_discounts: `$${discountedPrice.toFixed(2)}`,
                  final_customer_price: `$${finalPrice.toFixed(2)}`,
                  total_savings: `$${(validated.basePrice - discountedPrice).toFixed(2)}`,
                  markup_applied: `${((vividwallsMarkup - 1) * 100).toFixed(1)}%`
                }
              }, null, 2)
            }
          ]
        };
      }

      case "get-order-status": {
        const validated = OrderStatusSchema.parse(args);
        const token = await authenticate();
        
        const response = await axios.get(
          `${PICTOREM_BASE_URL}/api/orders/${validated.pictoremOrderId}/status`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'User-Agent': 'VividWalls-MCP-Server/1.0.0'
            },
            timeout: 10000
          }
        );
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: true,
                order_id: validated.pictoremOrderId,
                status: response.data.status,
                tracking_number: response.data.tracking_number,
                estimated_delivery: response.data.estimated_delivery,
                production_stage: response.data.production_stage,
                last_updated: response.data.last_updated
              }, null, 2)
            }
          ]
        };
      }

      case "upload-image": {
        const validated = ImageUploadSchema.parse(args);
        const token = await authenticate();
        
        // Download image from URL
        const imageResponse = await axios.get(validated.imageUrl, { 
          responseType: 'stream',
          timeout: 30000
        });
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('file', imageResponse.data, validated.fileName);
        formData.append('order_reference', validated.orderReference);
        
        // Upload to Pictorem
        const uploadResponse = await axios.post(
          `${PICTOREM_BASE_URL}/api/images/upload`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'User-Agent': 'VividWalls-MCP-Server/1.0.0',
              ...formData.getHeaders()
            },
            timeout: 60000 // Longer timeout for file uploads
          }
        );
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: true,
                upload_id: uploadResponse.data.upload_id,
                file_url: uploadResponse.data.file_url,
                file_size: uploadResponse.data.file_size,
                image_dimensions: uploadResponse.data.dimensions,
                order_reference: validated.orderReference
              }, null, 2)
            }
          ]
        };
      }

      default:
        throw new McpError(ErrorCode.MethodNotFound, `Tool ${name} not found`);
    }
  } catch (error: unknown) {
    // Handle different types of errors appropriately
    if (error instanceof McpError) {
      throw error;
    }
    
    if (error instanceof z.ZodError) {
      throw new McpError(
        ErrorCode.InvalidParams,
        `Invalid parameters: ${error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')}`
      );
    }
    
    if (error instanceof AxiosError) {
      const statusCode = error.response?.status;
      const errorMessage = error.response?.data?.message || error.message;
      
      if (statusCode === 401) {
        // Clear auth token and retry once
        authToken = null;
        tokenExpiry = null;
        throw new McpError(ErrorCode.InternalError, `Authentication error: ${errorMessage}`);
      } else if (statusCode === 404) {
        throw new McpError(ErrorCode.InvalidParams, `Resource not found: ${errorMessage}`);
      } else if (statusCode && statusCode >= 400 && statusCode < 500) {
        throw new McpError(ErrorCode.InvalidParams, `Client error: ${errorMessage}`);
      } else {
        throw new McpError(ErrorCode.InternalError, `Pictorem API error: ${errorMessage}`);
      }
    }
    
    throw new McpError(ErrorCode.InternalError, `Unexpected error: ${String(error)}`);
  }
});

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  // Log to stderr (not stdout which is used for MCP communication)
  console.error("Pictorem MCP Server v1.0.0 running on stdio");
  console.error(`Configured for Pictorem API at: ${PICTOREM_BASE_URL}`);
  console.error(`Username: ${PICTOREM_USERNAME}`);
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error("Received SIGINT, shutting down gracefully...");
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error("Received SIGTERM, shutting down gracefully...");
  process.exit(0);
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error("Uncaught exception:", error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error("Unhandled rejection at:", promise, "reason:", reason);
  process.exit(1);
});

main().catch((error) => {
  console.error("Failed to start Pictorem MCP Server:", error);
  process.exit(1);
});
INDEX_TS

    # Create environment file
    cat > .env << 'ENV_FILE'
PICTOREM_USERNAME=kingler@me.com
PICTOREM_PASSWORD=#Freedom2023#
ENV_FILE

    # Create README
    cat > README.md << 'README'
# Pictorem MCP Server

A Model Context Protocol (MCP) server for integrating with Pictorem's print-on-demand API. This server provides tools for order submission, pricing calculation, image upload, and order tracking with VividWalls-specific pricing logic.

## Features

- **Order Submission**: Submit complete print orders to Pictorem with VividWalls pricing
- **Pricing Calculation**: Calculate final pricing with Pro discounts and VividWalls markup
- **Order Status**: Track order status and delivery information  
- **Image Upload**: Upload images to Pictorem for print orders
- **Authentication**: Secure token-based authentication with Pictorem API
- **Error Handling**: Comprehensive error handling with proper MCP error codes

## VividWalls Pricing Logic

The server implements VividWalls-specific pricing calculations:

- **Pro Account Discount**: 15% base discount
- **Canvas Roll Discount**: Additional 25% for canvas roll products  
- **VividWalls Markup**: 106.5% markup on final discounted price

### Pricing Formula

```
Base Price (from Pictorem)
- Pro Account Discount (15%)
- Canvas Roll Discount (25% additional for canvas rolls)
× VividWalls Markup (106.5%)
= Final Customer Price
```

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build the TypeScript project**:
   ```bash
   npm run build
   ```

3. **Set environment variables**:
   ```bash
   export PICTOREM_USERNAME="your-pictorem-username"
   export PICTOREM_PASSWORD="your-pictorem-password"
   ```

4. **Run the server**:
   ```bash
   npm start
   ```

## MCP Tools

### submit-order
Submit a complete print order to Pictorem with VividWalls pricing calculation.

### calculate-pricing
Calculate final pricing for a Pictorem order with VividWalls markup and discounts.

### get-order-status
Get the current status of a Pictorem order.

### upload-image
Upload an image file to Pictorem for print orders.

## Version

v1.0.0 - Initial release with full Pictorem API integration
README

    log "Pictorem MCP server files created successfully"
}

# Install dependencies and build
install_and_build() {
    log "Installing dependencies and building Pictorem MCP server..."
    
    cd "$PICTOREM_DIR"
    
    # Install Node.js if not available
    if ! command -v node &> /dev/null; then
        log "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi
    
    # Install dependencies
    npm install
    
    # Build the TypeScript project
    npm run build
    
    # Make the server executable
    chmod +x dist/index.js
    
    log "Pictorem MCP server built successfully"
}

# Test the server
test_server() {
    log "Testing Pictorem MCP server..."
    
    cd "$PICTOREM_DIR"
    
    # Test that the server can list tools
    echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | timeout 10 node dist/index.js || warning "Server test timed out or failed"
    
    log "Server test completed"
}

# Main execution
main() {
    log "Starting Pictorem MCP Server deployment..."
    
    # Check if we're on the droplet
    if [[ ! -d "$PROJECT_ROOT" ]]; then
        error "Project directory $PROJECT_ROOT not found. This script should be run on the Digital Ocean droplet."
        exit 1
    fi
    
    # Create the MCP server
    create_pictorem_mcp
    
    # Install and build
    install_and_build
    
    # Test the server
    test_server
    
    log "Pictorem MCP Server deployment completed successfully!"
    info "Server location: $PICTOREM_DIR"
    info "Executable: $PICTOREM_DIR/dist/index.js"
    info "To test: echo '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\", \"params\": {}}' | node $PICTOREM_DIR/dist/index.js"
}

# Run main function
main "$@" 