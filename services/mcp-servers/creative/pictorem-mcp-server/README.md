# Pictorem MCP Server with Browser Automation

A comprehensive Model Context Protocol (MCP) server for integrating with Pictorem's print-on-demand API. Features both **AI-driven browser automation** and **traditional browser automation** (Playwright/Puppeteer) for comprehensive order management and recursive validation.

## 🚀 New Features

### Browser Automation Capabilities
- **🤖 AI-Driven Automation**: Intelligent browser interactions for complex order flows
- **🔧 Traditional Automation**: Reliable Playwright/Puppeteer automation for validation
- **🔄 Recursive Validation**: Cross-validate orders using both automation methods
- **📸 Error Screenshots**: Automatic screenshots on automation failures
- **⚡ Performance Optimized**: Smart resource management and cleanup

### VividWalls Pricing Integration
- **Pro Account Discounts** (15%)
- **Canvas Roll Discounts** (25% additional)
- **VividWalls Markup** (106.5%)
- **Dynamic Pricing Calculation** with validation

## 📊 Available MCP Tools

### Authentication Tools
- **`authenticate-browser`** - Authenticate with Pictorem using browser automation

### Order Management Tools
- **`submit-order-browser-ai`** - Submit orders using AI-driven browser automation
- **`submit-order-browser-traditional`** - Submit orders using traditional browser automation
- **`validate-order-recursive`** - Validate orders using both AI and traditional methods
- **`get-order-status-browser`** - Get order status using browser automation
- **`upload-image-browser`** - Upload images using browser automation

### Pricing Tools
- **`calculate-pricing`** - Calculate VividWalls pricing with discounts and markup

### Legacy API Tools (Future)
- **`submit-order-api`** - API-based order submission (not yet available)
- **`get-order-status-api`** - API-based status checking (not yet available)
- **`upload-image-api`** - API-based image upload (not yet available)

## 🛠️ Browser Automation Options

All browser automation tools support these options:

```json
{
  "use_ai_agent": true,              // Use AI agent for automation
  "validate_with_traditional": true, // Validate with traditional automation
  "headless": true,                  // Run browser in headless mode
  "timeout": 30000,                  // Timeout in milliseconds
  "screenshot_on_error": true        // Take screenshot on errors
}
```

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Install Browser Dependencies

```bash
npm run setup-browsers
```

### 3. Set Environment Variables

Create a `.env` file:

```env
# Required: Pictorem credentials
PICTOREM_USERNAME=your_pictorem_email@example.com
PICTOREM_PASSWORD=your_pictorem_password

# Optional: Debugging
DEBUG=true
LOG_LEVEL=info
```

### 4. Build the Server

```bash
npm run build
```

### 5. Run the Server

```bash
npm start
```

## 🧪 Testing

### Run All Tests

```bash
# Run tests once
npm run test:run

# Run tests with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

### Test Coverage

The test suite includes **72 comprehensive tests** covering:

- ✅ **VividWalls Pricing Logic** (15 tests)
- ✅ **Browser Automation Tools** (18 tests)
- ✅ **Schema Validation** (23 tests)
- ✅ **MCP Tools Functionality** (16 tests)

## 📋 Usage Examples

### Submit Order with AI Automation

```json
{
  "name": "submit-order-browser-ai",
  "arguments": {
    "shopify_order_id": "SHOP123",
    "order_number": "ORD-001",
    "customer_info": {
      "email": "customer@example.com",
      "name": "John Doe",
      "shipping_address": {
        "address1": "123 Main St",
        "city": "Anytown",
        "province": "CA",
        "country": "US",
        "zip": "12345"
      }
    },
    "product_configuration": {
      "product_type": "canvas",
      "size": { "width": 16, "height": 20, "unit": "inches" },
      "canvas_type": "stretched",
      "quantity": 1
    },
    "image_data": {
      "file_path": "/tmp/artwork.jpg",
      "file_name": "artwork.jpg",
      "file_format": "jpg",
      "file_size": 2048000,
      "upload_url": "https://example.com/artwork.jpg"
    },
    "pricing": {
      "base_price": 45.00,
      "pro_discount": 0.15,
      "canvas_roll_discount": 0,
      "vividwalls_markup": 2.065
    },
    "options": {
      "headless": true,
      "screenshot_on_error": true
    }
  }
}
```

### Recursive Order Validation

```json
{
  "name": "validate-order-recursive",
  "arguments": {
    "order_id": "PICTOREM-ORDER-123",
    "original_config": { /* order configuration */ },
    "options": {
      "use_ai_agent": true,
      "validate_with_traditional": true
    }
  }
}
```

### Calculate VividWalls Pricing

```json
{
  "name": "calculate-pricing",
  "arguments": {
    "basePrice": 45.00,
    "productType": "canvas",
    "size": { "width": 16, "height": 20 }
  }
}
```

## 🏗️ Architecture

### Browser Manager Class

The `PictoremBrowserManager` class handles all browser automation:

- **Initialization**: Smart browser instance management
- **Authentication**: Secure login with session management
- **Order Submission**: Both AI-driven and traditional automation
- **Validation**: Cross-validation using multiple methods
- **Resource Management**: Automatic cleanup and optimization

### AI-Driven vs Traditional Automation

| Feature | AI-Driven | Traditional |
|---------|-----------|-------------|
| **Adaptability** | High - can handle UI changes | Medium - requires selector updates |
| **Reliability** | Medium - depends on AI accuracy | High - deterministic |
| **Performance** | Medium - AI processing overhead | High - direct automation |
| **Maintenance** | Low - self-adapting | Medium - requires updates |
| **Use Case** | Complex flows, dynamic UIs | Validation, known workflows |

### Recursive Validation Process

1. **AI Automation**: Submit order using intelligent automation
2. **Traditional Validation**: Verify result using deterministic automation
3. **Consistency Check**: Compare results from both methods
4. **Recommendation**: Provide confidence level and recommendations

## 🔍 Error Handling

### Automatic Error Recovery

- **Screenshot Capture**: Automatic screenshots on failures
- **Retry Logic**: Intelligent retry with exponential backoff
- **Fallback Methods**: Switch between AI and traditional automation
- **Detailed Logging**: Comprehensive error reporting

### Common Error Scenarios

- **Network Timeouts**: Automatic retry with increased timeout
- **Element Not Found**: AI-driven element discovery
- **Authentication Failures**: Session refresh and re-authentication
- **Browser Crashes**: Automatic browser restart

## 🚀 Deployment

### Local Development

```bash
npm run setup-all  # Install everything and build
npm start          # Start the MCP server
```

### Production Deployment

```bash
# On your server
npm install --production
npm run setup-browsers
npm run build
npm start
```

### Docker Deployment

```dockerfile
FROM node:18-alpine

# Install Playwright dependencies
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont

# Set Playwright to use system Chromium
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /app
COPY package*.json ./
RUN npm install --production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔒 Security Considerations

- **Credential Management**: Environment variables for sensitive data
- **Browser Security**: Sandboxed browser execution
- **Network Security**: HTTPS-only connections
- **Session Management**: Secure token handling

## 📈 Performance Optimization

- **Resource Management**: Automatic browser cleanup
- **Image Loading**: Skip unnecessary image downloads
- **Concurrent Limits**: Prevent browser resource exhaustion
- **Memory Management**: Proactive memory cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and support:
1. Check the error logs and screenshots
2. Review the test results
3. Check browser automation compatibility
4. Contact the VividWalls development team

---

**Note**: This MCP server provides a foundation for AI-driven browser automation. While it includes placeholders for advanced AI libraries like `browser-use`, the current implementation uses Playwright and Puppeteer for reliable, production-ready automation. 