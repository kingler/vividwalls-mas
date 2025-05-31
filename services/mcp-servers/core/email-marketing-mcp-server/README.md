# Email Marketing MCP Server

A comprehensive Email Marketing MCP server designed for VividWalls art print business, providing tools for email marketing automation, customer segmentation, and campaign management.

## Features

### Core Email Marketing Tools
- **create_campaign**: Create newsletter and promotional email campaigns
- **segment_audience**: Advanced customer list segmentation
- **track_engagement**: Monitor open rates, clicks, and conversions
- **automate_sequences**: Set up welcome series and win-back campaigns
- **create_template**: Manage email design templates
- **schedule_send**: Optimize campaign timing
- **send_transactional**: Handle order confirmations and shipping updates
- **manage_subscribers**: Add/remove/update subscriber information
- **get_analytics**: Comprehensive campaign performance metrics
- **create_automation**: Build trigger-based email workflows

### Art Print Business Specialization
- Pre-built templates for art print industry
- Customer journey automations
- Product collection launch campaigns
- Abandoned cart recovery sequences
- Purchase behavior segmentation

## Supported Email Providers

### SendGrid (Recommended)
- Robust API with advanced features
- Excellent deliverability
- Comprehensive analytics
- Automation capabilities

### Mailchimp
- User-friendly interface
- Strong segmentation tools
- Built-in A/B testing
- Journey builder for automations

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your email provider credentials
   ```

3. **Run the Server**
   ```bash
   # With environment variables
   python server.py
   
   # With command line arguments
   python server.py --email-key YOUR_API_KEY --email-provider sendgrid
   ```

## Configuration

### Environment Variables

Create a `.env` file with your email service provider credentials:

```env
EMAIL_PROVIDER=sendgrid
EMAIL_API_KEY=your_api_key_here
DEFAULT_FROM_EMAIL=hello@vividwalls.com
DEFAULT_FROM_NAME=VividWalls
```

### SendGrid Setup

1. **Create SendGrid Account**
   - Sign up at [SendGrid](https://sendgrid.com)
   - Verify your sender identity
   - Create an API key with full access

2. **Domain Authentication**
   - Set up domain authentication for better deliverability
   - Add DNS records as instructed by SendGrid

3. **Sender Identity**
   - Verify email addresses you'll send from
   - Set up sender profiles

### Mailchimp Setup

1. **Create Mailchimp Account**
   - Sign up at [Mailchimp](https://mailchimp.com)
   - Get your API key from Account settings

2. **API Key Format**
   - Mailchimp API keys include datacenter: `key-us1`
   - The server extracts datacenter automatically

## Usage Examples

### 1. Create Welcome Campaign

```python
# Create a welcome email campaign
result = create_campaign(
    name="Welcome Series - New Subscribers",
    subject="Welcome to VividWalls - Your Art Journey Begins! 🎨",
    content="<html>Welcome email content...</html>",
    template_type="welcome_series",
    sender_email="hello@vividwalls.com",
    sender_name="VividWalls",
    list_ids=["your_list_id"]
)
```

### 2. Segment Art Buyers

```python
# Segment customers who bought abstract art
result = segment_audience(
    name="Abstract Art Buyers",
    conditions=[
        {"field": "purchase_history", "operator": "contains", "value": "abstract"},
        {"field": "total_spent", "operator": "greater_than", "value": "100"}
    ],
    list_id="main_list_id"
)
```

### 3. Automate Abandoned Cart Recovery

```python
# Set up abandoned cart sequence
result = automate_sequences(
    sequence_type="abandoned_cart",
    trigger_event="cart_abandonment",
    emails=[
        {
            "delay": 1,  # 1 hour
            "template": "abandoned_cart",
            "subject": "Don't let that perfect art piece slip away! 🖼️"
        },
        {
            "delay": 72,  # 3 days
            "template": "last_chance",
            "subject": "Last chance - 10% off your cart"
        }
    ],
    list_id="cart_abandoners"
)
```

### 4. Send Order Confirmation

```python
# Send transactional order confirmation
result = send_transactional(
    to_email="customer@example.com",
    template_type="order_confirmation",
    data={
        "order_id": "ORD-12345",
        "order_details": "2x Abstract Canvas Prints - $89.99",
        "delivery_date": "3-5 business days"
    },
    from_email="orders@vividwalls.com"
)
```

### 5. Track Campaign Performance

```python
# Get engagement metrics
result = track_engagement(
    campaign_id="campaign_12345",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(f"Open Rate: {result['metrics']['unique_opens']} opens")
print(f"Click Rate: {result['metrics']['unique_clicks']} clicks")
```

## Pre-built Templates

The server includes art print business-specific templates:

### Welcome Series
- **Subject**: "Welcome to VividWalls - Your Art Journey Begins! 🎨"
- **Purpose**: Onboard new subscribers
- **Features**: 15% discount, collection highlights

### Abandoned Cart
- **Subject**: "Don't let that perfect art piece slip away! 🖼️"
- **Purpose**: Recover abandoned purchases
- **Features**: Product images, urgency messaging

### New Collection
- **Subject**: "🎨 New Collection Alert: {collection_name} Now Available!"
- **Purpose**: Announce new art collections
- **Features**: Collection preview, early access

### Order Confirmation
- **Subject**: "Order Confirmed! Your Art is On Its Way 📦"
- **Purpose**: Confirm successful orders
- **Features**: Order details, tracking info

### Shipping Update
- **Subject**: "Your VividWalls Order Has Shipped! 🚚"
- **Purpose**: Notify customers of shipments
- **Features**: Tracking number, delivery estimate

## Advanced Features

### Customer Journey Automation

Create sophisticated customer journeys:

```python
# Create browse abandonment automation
result = create_automation(
    name="Abstract Art Browse Abandonment",
    trigger_type="website_visit",
    trigger_conditions={
        "page": "/collections/abstract",
        "time_on_page": ">30s",
        "no_purchase": "24h"
    },
    actions=[
        {"type": "wait", "duration": "1_hour"},
        {
            "type": "send_email",
            "template": "abandoned_browse",
            "personalization": {"collection": "abstract"}
        },
        {"type": "wait", "duration": "3_days"},
        {
            "type": "send_email",
            "template": "collection_discount",
            "discount_code": "ABSTRACT15"
        }
    ]
)
```

### Analytics and Insights

Get comprehensive campaign analytics:

```python
# Get detailed analytics
result = get_analytics(
    metric_type="overview",
    date_range=30,
    campaign_ids=["campaign1", "campaign2"]
)

# Access insights
insights = result['analytics']['insights']
print("AI-powered insights:")
for insight in insights:
    print(f"- {insight}")
```

## MCP Integration

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "email-marketing": {
      "command": "python",
      "args": [
        "/path/to/email-marketing-mcp-server/server.py",
        "--email-key", "your_api_key",
        "--email-provider", "sendgrid"
      ]
    }
  }
}
```

### n8n Workflow Integration

The server works seamlessly with n8n workflows:

1. **Trigger Node**: HTTP webhook for customer actions
2. **MCP Node**: Call email marketing tools
3. **Condition Node**: Route based on customer behavior
4. **Database Node**: Update customer profiles

Example n8n workflow:
```
Webhook (New Signup) → MCP (Add Subscriber) → MCP (Send Welcome Email)
```

## Error Handling

The server includes comprehensive error handling:

- **API Rate Limits**: Automatic retry with exponential backoff
- **Authentication Errors**: Clear error messages for token issues
- **Validation Errors**: Input validation with helpful error descriptions
- **Network Errors**: Graceful handling of connection issues

## Best Practices

### Email Deliverability
1. **Authenticate Your Domain**: Set up SPF, DKIM, and DMARC records
2. **Warm Up IPs**: Gradually increase sending volume
3. **Monitor Reputation**: Track bounce rates and spam complaints
4. **Clean Lists**: Remove inactive subscribers regularly

### Campaign Optimization
1. **A/B Testing**: Test subject lines, send times, and content
2. **Segmentation**: Target specific customer groups
3. **Personalization**: Use dynamic content and customer data
4. **Mobile Optimization**: Ensure emails render well on mobile

### Art Print Specific Tips
1. **Visual Content**: Use high-quality product images
2. **Room Mockups**: Show art in home settings
3. **Size Guides**: Include dimensions and sizing information
4. **Customer Stories**: Feature customer installations

## Troubleshooting

### Common Issues

**Authentication Errors**
```
Error: Invalid API key
Solution: Verify your API key in the .env file
```

**Template Not Found**
```
Error: Template 'custom_template' not found
Solution: Use built-in templates or create custom templates first
```

**List ID Invalid**
```
Error: List ID not found
Solution: Check your list IDs in your email provider dashboard
```

### Debug Mode

Run with debug logging:
```bash
DEBUG=true python server.py --email-key YOUR_KEY --email-provider sendgrid
```

## Support

For issues and questions:

1. **Check Documentation**: Review this README and provider docs
2. **Test Connection**: Use the connection test tools
3. **Check Logs**: Review error messages for specific issues
4. **Provider Support**: Contact SendGrid or Mailchimp support for API issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Changelog

### v1.0.0
- Initial release with SendGrid and Mailchimp support
- Pre-built art print business templates
- Advanced automation workflows
- Comprehensive analytics and reporting