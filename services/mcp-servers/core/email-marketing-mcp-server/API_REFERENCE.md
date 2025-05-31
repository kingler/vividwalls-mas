# Email Marketing MCP Server - API Reference

This document provides detailed API reference for all email marketing tools available in the MCP server.

## Tools Overview

| Tool | Purpose | Provider Support |
|------|---------|------------------|
| `create_campaign` | Create email campaigns | SendGrid, Mailchimp |
| `segment_audience` | Segment customer lists | SendGrid, Mailchimp |
| `track_engagement` | Monitor campaign metrics | SendGrid, Mailchimp |
| `automate_sequences` | Set up email sequences | SendGrid, Mailchimp |
| `create_template` | Manage email templates | SendGrid, Mailchimp |
| `schedule_send` | Schedule campaign delivery | SendGrid, Mailchimp |
| `send_transactional` | Send order confirmations | SendGrid, Mailchimp |
| `manage_subscribers` | Manage subscriber lists | SendGrid, Mailchimp |
| `get_analytics` | Get performance analytics | SendGrid, Mailchimp |
| `create_automation` | Build workflow automations | SendGrid, Mailchimp |

## Tool Details

### create_campaign

Create a new email marketing campaign for VividWalls art print business.

**Parameters:**
- `name` (string, required): Campaign name
- `subject` (string, required): Email subject line
- `content` (string, required): Email content (HTML or plain text)
- `template_type` (string, optional): Template type from pre-built options
- `sender_email` (string, optional): Sender email address (default: "hello@vividwalls.com")
- `sender_name` (string, optional): Sender display name (default: "VividWalls")
- `list_ids` (array[string], optional): List of recipient list IDs
- `personalization` (object, optional): Dynamic content variables

**Template Types:**
- `welcome_series`: Welcome email for new subscribers
- `abandoned_cart`: Cart abandonment recovery
- `new_collection`: New art collection announcements
- `order_confirmation`: Order confirmation emails
- `shipping_update`: Shipping notification emails

**Returns:**
```json
{
  "success": true,
  "campaign_id": "campaign_12345",
  "name": "Welcome Series Campaign",
  "subject": "Welcome to VividWalls!",
  "provider": "sendgrid",
  "status": "draft"
}
```

**Example:**
```python
result = create_campaign(
    name="Summer Art Collection Launch",
    subject="🌞 New Summer Collection - Transform Your Space!",
    content="<html>Discover our vibrant summer art collection...</html>",
    template_type="new_collection",
    list_ids=["art_lovers_123"],
    personalization={"collection_name": "Summer Vibes 2024"}
)
```

### segment_audience

Create audience segments for targeted email campaigns.

**Parameters:**
- `name` (string, required): Segment name
- `conditions` (array[object], required): Segmentation conditions
- `list_id` (string, optional): Base list ID to segment from

**Condition Object:**
- `field` (string): Field to filter on
- `operator` (string): Comparison operator
- `value` (string): Filter value

**Common Fields for Art Print Business:**
- `purchase_history`: Past purchase categories
- `location`: Customer location
- `total_spent`: Total amount spent
- `last_purchase`: Days since last purchase
- `favorite_style`: Preferred art style
- `room_type`: Home room preferences

**Returns:**
```json
{
  "success": true,
  "segment_id": "seg_456",
  "name": "Abstract Art Buyers",
  "recipient_count": 1250,
  "provider": "sendgrid"
}
```

**Example:**
```python
result = segment_audience(
    name="High-Value Abstract Art Customers",
    conditions=[
        {"field": "purchase_history", "operator": "contains", "value": "abstract"},
        {"field": "total_spent", "operator": "greater_than", "value": "200"},
        {"field": "last_purchase", "operator": "less_than", "value": "90_days"}
    ],
    list_id="main_customers"
)
```

### track_engagement

Track email engagement metrics including opens, clicks, and conversions.

**Parameters:**
- `campaign_id` (string, optional): Specific campaign ID to track
- `start_date` (string, optional): Start date for metrics (YYYY-MM-DD)
- `end_date` (string, optional): End date for metrics (YYYY-MM-DD)

**Returns:**
```json
{
  "success": true,
  "metrics": {
    "delivered": 5000,
    "opens": 1250,
    "unique_opens": 1100,
    "clicks": 320,
    "unique_clicks": 280,
    "bounces": 25,
    "spam_reports": 2,
    "unsubscribes": 15
  },
  "provider": "sendgrid"
}
```

**Example:**
```python
result = track_engagement(
    campaign_id="campaign_12345",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

open_rate = (result['metrics']['unique_opens'] / result['metrics']['delivered']) * 100
print(f"Open rate: {open_rate:.2f}%")
```

### automate_sequences

Create automated email sequences for customer lifecycle marketing.

**Parameters:**
- `sequence_type` (string, required): Type of automation
- `trigger_event` (string, required): Event that triggers the sequence
- `emails` (array[object], required): List of emails in the sequence
- `list_id` (string, optional): Target list ID

**Sequence Types:**
- `welcome`: Welcome series for new subscribers
- `abandoned_cart`: Cart abandonment recovery
- `win_back`: Re-engagement for inactive customers
- `post_purchase`: Follow-up after purchase
- `birthday`: Birthday celebration emails

**Email Object:**
- `delay` (number): Hours to wait before sending
- `template` (string): Template to use
- `subject` (string): Email subject
- `personalization` (object): Dynamic content

**Returns:**
```json
{
  "success": true,
  "automation_id": "auto_789",
  "sequence_type": "welcome",
  "trigger_event": "subscription",
  "email_count": 3,
  "provider": "sendgrid"
}
```

**Example:**
```python
result = automate_sequences(
    sequence_type="welcome",
    trigger_event="subscription",
    emails=[
        {
            "delay": 0,
            "template": "welcome_series",
            "subject": "Welcome to VividWalls! 🎨"
        },
        {
            "delay": 72,
            "template": "first_purchase",
            "subject": "Ready to transform your space?"
        },
        {
            "delay": 168,
            "template": "collection_showcase",
            "subject": "Discover our most popular pieces"
        }
    ]
)
```

### create_template

Create reusable email templates for VividWalls campaigns.

**Parameters:**
- `name` (string, required): Template name
- `html_content` (string, required): HTML content of the template
- `category` (string, optional): Template category (default: "art_print")
- `variables` (array[string], optional): Template variables for personalization

**Categories:**
- `art_print`: Art print business specific
- `transactional`: Order and shipping emails
- `promotional`: Sales and marketing campaigns
- `seasonal`: Holiday and seasonal campaigns

**Returns:**
```json
{
  "success": true,
  "template_id": "tpl_101",
  "version_id": "ver_202",
  "name": "Modern Art Collection Template",
  "category": "art_print",
  "variables": ["customer_name", "collection_name", "discount_code"],
  "provider": "sendgrid"
}
```

**Example:**
```python
html_content = """
<html>
<body>
  <h1>Hello {{customer_name}}!</h1>
  <p>Check out our new {{collection_name}} collection.</p>
  <p>Use code {{discount_code}} for 15% off!</p>
  <img src="{{collection_image}}" alt="{{collection_name}}">
</body>
</html>
"""

result = create_template(
    name="New Collection Announcement",
    html_content=html_content,
    category="promotional",
    variables=["customer_name", "collection_name", "discount_code", "collection_image"]
)
```

### schedule_send

Schedule a campaign to be sent at a specific time.

**Parameters:**
- `campaign_id` (string, required): Campaign ID to schedule
- `send_time` (string, required): Send time in ISO format (YYYY-MM-DDTHH:MM:SS)
- `timezone` (string, optional): Timezone for scheduling (default: "America/New_York")

**Returns:**
```json
{
  "success": true,
  "campaign_id": "campaign_12345",
  "scheduled_time": "2024-03-15T10:00:00",
  "timezone": "America/New_York",
  "provider": "sendgrid"
}
```

**Example:**
```python
result = schedule_send(
    campaign_id="campaign_12345",
    send_time="2024-03-15T10:00:00",
    timezone="America/Los_Angeles"
)
```

### send_transactional

Send transactional emails for order confirmations, shipping updates, etc.

**Parameters:**
- `to_email` (string, required): Recipient email address
- `template_type` (string, required): Template type
- `data` (object, required): Data to populate the template
- `from_email` (string, optional): Sender email (default: "orders@vividwalls.com")
- `from_name` (string, optional): Sender name (default: "VividWalls")

**Template Types:**
- `order_confirmation`: Order confirmation emails
- `shipping_update`: Shipping notification emails
- `delivery_confirmation`: Delivery confirmation
- `refund_processed`: Refund notifications
- `account_created`: Account creation welcome

**Data Fields by Template:**

**Order Confirmation:**
- `order_id`: Order number
- `order_details`: Order line items
- `delivery_date`: Expected delivery

**Shipping Update:**
- `order_id`: Order number
- `tracking_number`: Tracking number
- `carrier`: Shipping carrier
- `delivery_date`: Expected delivery
- `tracking_url`: Tracking URL

**Returns:**
```json
{
  "success": true,
  "to_email": "customer@example.com",
  "template_type": "order_confirmation",
  "subject": "Order Confirmed! Your Art is On Its Way 📦",
  "provider": "sendgrid"
}
```

**Example:**
```python
result = send_transactional(
    to_email="jane@example.com",
    template_type="shipping_update",
    data={
        "order_id": "ORD-12345",
        "tracking_number": "1Z999AA1234567890",
        "carrier": "UPS",
        "delivery_date": "March 15, 2024",
        "tracking_url": "https://tracking.ups.com/..."
    }
)
```

### manage_subscribers

Manage email subscribers - add, remove, or update.

**Parameters:**
- `action` (string, required): Action to perform ("add", "remove", "update")
- `email` (string, required): Subscriber email address
- `list_id` (string, required): Target list ID
- `subscriber_data` (object, optional): Additional subscriber data

**Subscriber Data Fields:**
- `first_name`: First name
- `last_name`: Last name
- `location`: City/State
- `preferences`: Art style preferences
- `purchase_history`: Past purchase categories
- `birthday`: Birthday for special campaigns
- `customer_segment`: Customer tier/segment

**Returns:**
```json
{
  "success": true,
  "action": "add",
  "email": "newcustomer@example.com",
  "list_id": "main_list",
  "provider": "sendgrid"
}
```

**Examples:**
```python
# Add new subscriber
result = manage_subscribers(
    action="add",
    email="artlover@example.com",
    list_id="main_customers",
    subscriber_data={
        "first_name": "Sarah",
        "last_name": "Johnson",
        "location": "San Francisco, CA",
        "preferences": "abstract,modern",
        "customer_segment": "premium"
    }
)

# Update existing subscriber
result = manage_subscribers(
    action="update",
    email="artlover@example.com",
    list_id="main_customers",
    subscriber_data={
        "customer_segment": "vip",
        "last_purchase": "2024-03-01"
    }
)

# Remove subscriber
result = manage_subscribers(
    action="remove",
    email="unsubscribe@example.com",
    list_id="main_customers"
)
```

### get_analytics

Get comprehensive email marketing analytics for VividWalls campaigns.

**Parameters:**
- `metric_type` (string, optional): Type of analytics (default: "overview")
- `date_range` (number, optional): Number of days to include (default: 30)
- `campaign_ids` (array[string], optional): Specific campaigns to analyze

**Metric Types:**
- `overview`: General performance overview
- `engagement`: Detailed engagement metrics
- `revenue`: Revenue attribution from emails
- `growth`: List growth and churn metrics
- `segmentation`: Segment performance comparison

**Returns:**
```json
{
  "success": true,
  "analytics": {
    "date_range": {
      "start": "2024-02-15",
      "end": "2024-03-15",
      "days": 30
    },
    "overview": {
      "total_delivered": 45000,
      "total_opens": 13500,
      "total_clicks": 2700,
      "avg_open_rate": 30.0,
      "avg_click_rate": 6.0
    },
    "engagement_trends": [...],
    "top_performing_campaigns": [...],
    "insights": [
      "Consider A/B testing subject lines for better open rates",
      "Art print campaigns perform best on weekends",
      "New collection announcements have highest engagement"
    ]
  },
  "provider": "sendgrid"
}
```

**Example:**
```python
result = get_analytics(
    metric_type="overview",
    date_range=30,
    campaign_ids=["campaign_1", "campaign_2"]
)

analytics = result['analytics']
print(f"Average open rate: {analytics['overview']['avg_open_rate']:.1f}%")
print(f"Top insight: {analytics['insights'][0]}")
```

### create_automation

Create advanced email automation workflows with multiple triggers and actions.

**Parameters:**
- `name` (string, required): Automation workflow name
- `trigger_type` (string, required): Type of trigger
- `trigger_conditions` (object, required): Conditions for triggering
- `actions` (array[object], required): Actions to perform when triggered
- `settings` (object, optional): Additional workflow settings

**Trigger Types:**
- `website_visit`: Website page visits
- `purchase`: Product purchases
- `cart_abandonment`: Shopping cart abandonment
- `email_engagement`: Email opens/clicks
- `date_based`: Anniversary/birthday triggers
- `inactivity`: Customer inactivity periods

**Action Types:**
- `send_email`: Send an email
- `wait`: Wait for specified duration
- `add_tag`: Add customer tag
- `move_list`: Move to different list
- `webhook`: Call external webhook

**Settings:**
- `timezone`: Workflow timezone
- `send_time_optimization`: Optimize send times
- `frequency_capping`: Limit email frequency
- `unsubscribe_on_spam`: Auto-unsubscribe on spam reports

**Returns:**
```json
{
  "success": true,
  "automation_id": "auto_456",
  "name": "Abstract Art Browse Abandonment",
  "trigger_type": "website_visit",
  "action_count": 2,
  "status": "draft",
  "provider": "sendgrid"
}
```

**Example:**
```python
result = create_automation(
    name="VIP Customer Nurture Sequence",
    trigger_type="purchase",
    trigger_conditions={
        "product_category": "premium_prints",
        "order_value": ">$500"
    },
    actions=[
        {
            "type": "wait",
            "duration": "24_hours"
        },
        {
            "type": "send_email",
            "template": "vip_welcome",
            "subject": "Welcome to VIP! Exclusive benefits await",
            "personalization": {
                "customer_tier": "VIP"
            }
        },
        {
            "type": "wait",
            "duration": "7_days"
        },
        {
            "type": "send_email",
            "template": "vip_exclusive_preview",
            "subject": "VIP Preview: New Collection Launching Soon"
        },
        {
            "type": "add_tag",
            "tag": "vip_customer"
        }
    ],
    settings={
        "timezone": "America/New_York",
        "send_time_optimization": True,
        "frequency_capping": True
    }
)
```

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Detailed error message describing what went wrong"
}
```

**Common Error Types:**
- Authentication errors: Invalid API keys
- Validation errors: Missing or invalid parameters
- Rate limit errors: API quota exceeded
- Network errors: Connection issues
- Provider errors: Service-specific errors

## Rate Limits

### SendGrid
- 600 requests per minute
- 10,000 emails per month (free tier)
- Higher limits with paid plans

### Mailchimp
- 10 requests per second
- 500 requests per day (free tier)
- Higher limits with paid plans

## Best Practices

### Campaign Creation
1. **Subject Line Testing**: A/B test subject lines for better open rates
2. **Mobile Optimization**: Ensure emails render well on mobile devices
3. **Personalization**: Use customer data for personalized content
4. **Clear CTAs**: Include clear calls-to-action

### Automation Workflows
1. **Journey Mapping**: Plan customer journey before creating automations
2. **Timing Optimization**: Test different delays between emails
3. **Segmentation**: Use targeted segments for better relevance
4. **Performance Monitoring**: Regularly review automation metrics

### List Management
1. **Double Opt-in**: Use double opt-in for better list quality
2. **Regular Cleaning**: Remove inactive subscribers periodically
3. **Segmentation**: Keep lists organized by customer behavior
4. **Compliance**: Follow email marketing regulations (CAN-SPAM, GDPR)

### Analytics and Optimization
1. **Regular Monitoring**: Check metrics weekly
2. **A/B Testing**: Continuously test different elements
3. **Benchmark Tracking**: Compare against industry standards
4. **ROI Measurement**: Track revenue attribution from emails