
Based on the Pictorem integration documentation, here are the data fields that are passed to the Pictorem MCP server:

```json
{
  "order": {
    "shopify_order_id": "strin,
    "order_number": "string",
    "customer_info": {
      "email": "string",
      "name": "string",
      "shipping_address": {
        "address1": "string",
        "address2": "string",
        "city": "string",
        "province": "string",
        "country": "string",
        "zip": "string"
      }
    }
  },
  "product_configuration": {
    "product_type": "canvas|framed|canvas_roll|mural|panel|acrylic|metal|wood|poster",
    "size": {
      "width": "number (1-120 inches)",
      "height": "number (1-120 inches)",
      "unit": "inches"
    },
    "canvas_type": "stretched|roll",
    "frame_options": {
      "frame_type": "none|standard|premium_white|truffle",
      "frame_cost": "number"
    },
    "quantity": "number"
  },
  "image_data": {
    "file_path": "string",
    "file_name": "string",
    "file_format": "jpg|png|pdf|ai|eps",
    "file_size": "number (max 100MB)",
    "upload_url": "string"
  },
  "pricing": {
    "base_price": "number",
    "pro_discount": "0.15 (15%)",
    "canvas_roll_discount": "0.25 (25%)",
    "final_pictorem_cost": "number",
    "vividwalls_markup": "2.065 (106.5%)",
    "vividwalls_selling_price": "number",
    "shipping_cost": "number"
  },
  "authentication": {
    "username": "kingler@me.com",
    "password": "#Freedom2023#",
    "pro_account": true,
    "session_token": "string"
  },
  "processing_options": {
    "auto_submit": "boolean",
    "validate_pricing": "boolean",
    "generate_preview": "boolean",
    "track_order": "boolean",
    "notification_email": "string"
  },
  "metadata": {
    "source": "shopify_webhook",
    "timestamp": "ISO 8601 datetime",
    "processing_id": "string",
    "retry_count": "number",
    "error_log": "array of strings"
  }
}
```

**Key Data Field Categories:**

1. **Order Information**: Shopify order details and customer data
2. **Product Configuration**: Canvas type, size, frame options
3. **Image Data**: File upload information and formats
4. **Pricing Structure**: Pro discounts, markups, final costs
5. **Authentication**: Pictorem Pro account credentials
6. **Processing Options**: Automation behavior flags
7. **Metadata**: Tracking and logging information

**Size Mapping Examples:**
- Popular sizes: 12x12, 16x16, 24x16, 30x20, 36x24
- Custom sizes: Any dimension from 1-120 inches
- Panoramic: 16x8, 24x12, 40x24, 48x24

**Product Type Options:**
- Canvas (primary for VividWalls)
- Framed, Canvas Roll, Mural, Panel
- Acrylic, Metal, Wood, Poster

This JSON structure represents the comprehensive data passed to the Pictorem MCP server for automated order processing from Shopify to Pictorem's print-on-demand service.
