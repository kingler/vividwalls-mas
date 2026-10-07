# VividWalls Shopify-Pictorem Automation Deployment Guide

## 🎯 Overview

This system automatically processes Shopify orders and places corresponding orders on Pictorem using their Pro account (15% discount). The automation handles canvas sizing, frame selection, and maintains synchronized pricing between platforms.

## 📊 Current Pricing Status

✅ **Pricing Successfully Updated**
- **522 products** processed with updated Pictorem costs
- **Average markup**: 106.5% (profit margin)
- **Canvas Roll support**: 25% discount vs stretched canvas
- **Pro account pricing**: All costs include 15% Pictorem Pro discount

## 🏗️ System Architecture

```
Shopify Order (Paid) → Webhook → Automation Server → Pictorem Order
                                      ↓
                              Product Pricing Sync
```

## 🚀 Deployment Steps

### 1. Environment Setup

Create `.env` file:
```bash
# Shopify Configuration
SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret_here

# Pictorem Credentials (already configured)
PICTOREM_USERNAME=kingler@me.com
PICTOREM_PASSWORD=REDACTED_SET_PICTOREM_PASSWORD_ENV

# Server Configuration
FLASK_ENV=production
PORT=5000
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r scripts/requirements.txt

# Or using conda
conda install flask selenium requests pandas python-dotenv gunicorn
```

### 3. Install Chrome and ChromeDriver

**For Ubuntu/Debian:**
```bash
# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# ChromeDriver will be auto-installed by the script
```

**For macOS:**
```bash
# Install Chrome
brew install --cask google-chrome

# ChromeDriver auto-installation handled by script
```

### 4. Start the Automation Server

```bash
# Development mode
python scripts/shopify_pictorem_automation.py

# Production mode
gunicorn -w 4 -b 0.0.0.0:5000 scripts.shopify_pictorem_automation:app
```

### 5. Configure Shopify Webhooks

In your Shopify admin:

1. Go to **Settings** → **Notifications**
2. Scroll to **Webhooks** section
3. Click **Create webhook**
4. Configure:
   - **Event**: `Order payment`
   - **Format**: `JSON`
   - **URL**: `https://your-server.com/webhook/shopify/order`
   - **API Version**: Latest

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ ./scripts/
COPY logs/ ./logs/

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "scripts.shopify_pictorem_automation:app"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  pictorem-automation:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SHOPIFY_WEBHOOK_SECRET=${SHOPIFY_WEBHOOK_SECRET}
      - PICTOREM_USERNAME=${PICTOREM_USERNAME}
      - PICTOREM_PASSWORD=${PICTOREM_PASSWORD}
    volumes:
      - ./logs:/app/logs
      - ./scripts:/app/scripts
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 Size and Frame Mapping

### Supported Canvas Sizes
The system supports all standard Pictorem sizes with accurate Pro pricing:

**Square Sizes:**
- 12x12" → $30.60 (Pro price)
- 16x16" → $39.10
- 24x24" → $62.90
- 30x30" → $87.55

**Landscape/Portrait Sizes:**
- 16x12" → $34.00
- 24x16" → $48.45
- 30x20" → $74.80
- 36x24" → $85.00
- 48x36" → $150.45

**Panoramic Sizes:**
- 16x8" → $38.25
- 24x12" → $40.80
- 40x24" → $101.15
- 48x24" → $110.50

### Frame Options
All frame costs include 15% Pro discount:
- Standard frames: $15.30
- Premium white: $31.45
- Truffle: $16.15

## 💰 Pricing Strategy

The system applies dynamic markup based on total cost:

| Cost Range | Markup | Example |
|------------|--------|---------|
| Under $50 | 2.8x | $30 → $84 |
| $50-$100 | 2.4x | $75 → $180 |
| $100-$200 | 2.1x | $150 → $315 |
| Over $200 | 1.9x | $250 → $475 |

## 📋 Testing the System

### 1. Health Check
```bash
curl http://localhost:5000/health
```

### 2. Webhook Test
```bash
curl -X POST http://localhost:5000/webhook/shopify/order \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "TEST123",
    "financial_status": "paid",
    "line_items": [{
      "title": "Test Art Print",
      "variant_title": "24x36 / Black Frame",
      "quantity": 1
    }]
  }'
```

## 🔍 Monitoring and Logs

### Log Files
- **Application logs**: `logs/pictorem_automation.log`
- **Error tracking**: Detailed error messages with timestamps
- **Order processing**: Complete audit trail

### Key Metrics to Monitor
- ✅ **Webhook response time**
- ✅ **Order processing success rate**
- ✅ **Pictorem login success**
- ✅ **Size mapping accuracy**

## 🚨 Troubleshooting

### Common Issues

**1. ChromeDriver Issues**
```bash
# Auto-install ChromeDriver
pip install chromedriver-autoinstaller
```

**2. Webhook Signature Validation**
- Ensure `SHOPIFY_WEBHOOK_SECRET` is correctly set
- Check Shopify webhook configuration

**3. Pictorem Login Failures**
- Verify credentials are correct
- Check for rate limiting
- Ensure Pro account is active

**4. Size Mapping Errors**
- Check Shopify variant title format
- Verify custom size parsing logic
- Review size mapping configuration

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
python scripts/shopify_pictorem_automation.py
```

## 🔄 Maintenance Tasks

### Weekly
- ✅ Review automation logs
- ✅ Check order processing success rates
- ✅ Verify Pictorem Pro account status

### Monthly
- ✅ Update pricing if Pictorem changes rates
- ✅ Review and optimize markup strategy
- ✅ Test webhook endpoint health

### As Needed
- ✅ Update browser automation if Pictorem UI changes
- ✅ Add new size mappings for new products
- ✅ Optimize order processing performance

## 📞 Support

For issues with the automation system:
1. Check logs in `logs/pictorem_automation.log`
2. Verify configuration in `scripts/shopify_pictorem_automation_config.json`
3. Test individual components (webhook, browser automation, size mapping)
4. Review Shopify webhook delivery status

## 🎯 Next Steps

1. **Deploy to production server**
2. **Configure Shopify webhooks**
3. **Test with real orders**
4. **Monitor performance**
5. **Optimize based on usage patterns**

---

## 📈 Performance Optimizations

### Batch Processing
- Process multiple items from same order together
- Reuse browser sessions for efficiency
- Cache Pictorem login sessions

### Error Handling
- Retry failed orders automatically
- Alert on repeated failures
- Graceful degradation for partial failures

### Scaling
- Horizontal scaling with multiple workers
- Load balancing for high-volume stores
- Database logging for order tracking

---

*This automation system provides seamless integration between VividWalls Shopify store and Pictorem printing services, ensuring accurate pricing, automatic order fulfillment, and optimal profit margins.* 