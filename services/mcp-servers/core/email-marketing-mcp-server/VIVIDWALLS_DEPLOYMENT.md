# VividWalls Email Marketing MCP Deployment Guide

This guide explains how to integrate the Email Marketing MCP Server with the VividWalls art print business infrastructure.

## Integration with VividWalls Stack

### 1. n8n Workflow Integration

The Email Marketing MCP Server integrates seamlessly with your existing n8n workflows:

```json
{
  "name": "VividWalls Email Marketing Workflow",
  "nodes": [
    {
      "name": "Webhook - New Order",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "new-order"
      }
    },
    {
      "name": "MCP - Send Order Confirmation",
      "type": "n8n-nodes-base.mcp",
      "parameters": {
        "server": "email-marketing",
        "tool": "send_transactional",
        "parameters": {
          "to_email": "={{$json.customer_email}}",
          "template_type": "order_confirmation",
          "data": {
            "order_id": "={{$json.order_id}}",
            "order_details": "={{$json.items}}",
            "delivery_date": "={{$json.estimated_delivery}}"
          }
        }
      }
    }
  ]
}
```

### 2. Database Integration

Connect with your VividWalls PostgreSQL database for customer data:

```python
# Example: Segment customers who bought abstract art
result = segment_audience(
    name="Abstract Art Enthusiasts",
    conditions=[
        {"field": "purchase_history", "operator": "contains", "value": "abstract"},
        {"field": "last_purchase", "operator": "less_than", "value": "60_days"}
    ]
)
```

### 3. Shopify Integration

Sync with your Shopify store for order events:

```python
# Webhook from Shopify → n8n → Email MCP
{
  "trigger": "order_created",
  "action": "send_transactional",
  "template": "order_confirmation"
}
```

## VividWalls-Specific Use Cases

### 1. Welcome Series for Art Lovers

```python
# Create welcome sequence for new subscribers
automate_sequences(
    sequence_type="welcome",
    trigger_event="subscription",
    emails=[
        {
            "delay": 0,
            "template": "welcome_series",
            "subject": "Welcome to VividWalls! 🎨",
            "personalization": {"discount_code": "WELCOME15"}
        },
        {
            "delay": 72,  # 3 days
            "template": "collection_showcase",
            "subject": "Discover Our Most Popular Collections"
        },
        {
            "delay": 168,  # 1 week
            "template": "room_inspiration",
            "subject": "Transform Your Space with Art"
        }
    ]
)
```

### 2. Abandoned Cart Recovery

```python
# Set up cart abandonment workflow
create_automation(
    name="Cart Abandonment - Art Prints",
    trigger_type="cart_abandonment",
    trigger_conditions={
        "cart_value": ">$50",
        "time_since_abandonment": "1_hour"
    },
    actions=[
        {
            "type": "send_email",
            "template": "abandoned_cart",
            "subject": "Don't let that perfect art piece slip away! 🖼️",
            "personalization": {
                "cart_items": "{{abandoned_items}}",
                "cart_total": "{{cart_value}}"
            }
        },
        {
            "type": "wait",
            "duration": "24_hours"
        },
        {
            "type": "send_email",
            "template": "discount_offer",
            "subject": "10% Off - Complete Your Art Collection",
            "personalization": {"discount_code": "SAVE10"}
        }
    ]
)
```

### 3. New Collection Launches

```python
# Announce new art collections
create_campaign(
    name="Summer Abstract Collection Launch",
    subject="🌞 New Summer Collection - Bold Abstract Art",
    template_type="new_collection",
    personalization={
        "collection_name": "Summer Abstract 2024",
        "feature_1": "Vibrant summer colors",
        "feature_2": "Modern abstract compositions",
        "feature_3": "Multiple size options"
    },
    list_ids=["abstract_art_lovers", "premium_customers"]
)
```

### 4. Customer Segmentation by Art Preferences

```python
# Segment customers by art style preferences
segments = [
    {
        "name": "Abstract Art Lovers",
        "conditions": [
            {"field": "purchase_history", "operator": "contains", "value": "abstract"},
            {"field": "email_engagement", "operator": "greater_than", "value": "50%"}
        ]
    },
    {
        "name": "Photography Print Buyers",
        "conditions": [
            {"field": "purchase_history", "operator": "contains", "value": "photography"},
            {"field": "order_frequency", "operator": "greater_than", "value": "2"}
        ]
    },
    {
        "name": "Large Format Enthusiasts",
        "conditions": [
            {"field": "preferred_size", "operator": "contains", "value": "large"},
            {"field": "total_spent", "operator": "greater_than", "value": "200"}
        ]
    }
]

for segment in segments:
    segment_audience(
        name=segment["name"],
        conditions=segment["conditions"]
    )
```

## Environment Configuration for VividWalls

### Production Environment Variables

```env
# Email Marketing MCP Configuration
EMAIL_PROVIDER=sendgrid
EMAIL_API_KEY=your_production_sendgrid_key

# VividWalls Branding
DEFAULT_FROM_EMAIL=hello@vividwalls.com
DEFAULT_FROM_NAME=VividWalls
ORDERS_EMAIL=orders@vividwalls.com
SUPPORT_EMAIL=support@vividwalls.com

# Domain Configuration
VIVIDWALLS_DOMAIN=vividwalls.com
BRAND_COLORS_PRIMARY=#2C3E50
BRAND_COLORS_SECONDARY=#E74C3C

# Integration Endpoints
SHOPIFY_WEBHOOK_SECRET=your_shopify_secret
N8N_WEBHOOK_URL=https://n8n.vividwalls.com/webhook/email
```

## Docker Deployment

Add to your existing `docker-compose.yml`:

```yaml
version: '3.8'
services:
  email-marketing-mcp:
    build: ./mcp/email-marketing-mcp-server
    environment:
      - EMAIL_PROVIDER=${EMAIL_PROVIDER}
      - EMAIL_API_KEY=${EMAIL_API_KEY}
      - DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL}
    volumes:
      - ./shared:/data/shared
    networks:
      - vividwalls-network
    depends_on:
      - n8n
      - supabase

networks:
  vividwalls-network:
    external: true
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "server.py"]
```

## n8n Configuration

### 1. MCP Server Configuration

Add to n8n settings:

```json
{
  "mcpServers": {
    "email-marketing": {
      "command": "python",
      "args": [
        "/app/mcp/email-marketing-mcp-server/server.py",
        "--email-key", "{{$env.EMAIL_API_KEY}}",
        "--email-provider", "{{$env.EMAIL_PROVIDER}}"
      ]
    }
  }
}
```

### 2. Common Workflow Patterns

**Order Processing Workflow:**
```
Shopify Webhook → Extract Order Data → MCP Email Tool → Database Update
```

**Customer Journey Workflow:**
```
User Signup → MCP Segmentation → MCP Welcome Series → Analytics Tracking
```

**Collection Launch Workflow:**
```
New Products Added → MCP Audience Segment → MCP Campaign Creation → MCP Schedule Send
```

## Monitoring and Analytics

### 1. Email Performance Dashboard

Connect to your existing analytics:

```python
# Get campaign analytics
analytics = get_analytics(
    metric_type="overview",
    date_range=30
)

# Send to your dashboard
dashboard_data = {
    "open_rate": analytics["overview"]["avg_open_rate"],
    "click_rate": analytics["overview"]["avg_click_rate"],
    "revenue_attribution": analytics.get("revenue", 0)
}
```

### 2. Integration with Langfuse

Track email campaign performance:

```python
from langfuse import Langfuse

langfuse = Langfuse()

# Track email campaign performance
langfuse.trace(
    name="email_campaign",
    metadata={
        "campaign_id": campaign_id,
        "open_rate": metrics["open_rate"],
        "click_rate": metrics["click_rate"],
        "conversion_rate": metrics["conversion_rate"]
    }
)
```

## Security Considerations

### 1. API Key Management

Store sensitive credentials in environment variables:

```bash
# Use Docker secrets in production
docker secret create sendgrid_api_key sendgrid_key.txt
```

### 2. Rate Limiting

Implement rate limiting for email sends:

```python
# Built-in rate limiting in the MCP server
# Respects provider limits automatically
```

### 3. Data Privacy

Ensure GDPR/CCPA compliance:

```python
# Automatic unsubscribe handling
manage_subscribers(
    action="remove",
    email="user@example.com",
    list_id="main_list"
)
```

## Testing Strategy

### 1. Staging Environment

Test campaigns in staging:

```bash
# Set staging environment
export EMAIL_PROVIDER=sendgrid
export EMAIL_API_KEY=staging_key
export DEFAULT_FROM_EMAIL=staging@vividwalls.com

python test_connection.py
python test_tools.py
```

### 2. A/B Testing

Implement A/B testing for campaigns:

```python
# Create A/B test campaigns
campaign_a = create_campaign(
    name="Abstract Collection - Version A",
    subject="🎨 New Abstract Collection Available",
    template_type="new_collection"
)

campaign_b = create_campaign(
    name="Abstract Collection - Version B", 
    subject="Transform Your Space with Abstract Art",
    template_type="new_collection"
)
```

## Maintenance and Updates

### 1. Regular Health Checks

Monitor email deliverability:

```bash
# Daily health check
python test_connection.py
```

### 2. Template Updates

Keep templates current with brand changes:

```python
# Update templates for seasonal campaigns
create_template(
    name="Holiday 2024 Template",
    html_content=holiday_template_html,
    category="seasonal"
)
```

## Support and Troubleshooting

### Common Issues

1. **Authentication Errors**: Check API keys in environment
2. **Rate Limiting**: Monitor sending frequency
3. **Deliverability**: Maintain list hygiene
4. **Template Rendering**: Test across email clients

### Getting Help

1. Check logs: `docker logs email-marketing-mcp`
2. Test connection: `python test_connection.py`
3. Review documentation: `README.md` and `API_REFERENCE.md`
4. Monitor analytics for performance issues

This deployment guide ensures seamless integration of email marketing automation with your existing VividWalls infrastructure.