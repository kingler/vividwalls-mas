# VividWalls MCP Servers Integration Guide

## ✅ Deployment Status: COMPLETE

Both high-priority MCP servers have been successfully deployed to the DigitalOcean droplet at `157.230.13.13`.

## 📍 Deployed Servers

### 1. **Pinterest MCP Server**
- **Location**: `/opt/mcp-servers/pinterest-mcp-server/`
- **Service**: `pinterest-mcp.service`
- **Status**: ✅ Installed and ready for configuration
- **Tools Available**: 10 Pinterest marketing automation tools

### 2. **Email Marketing MCP Server**  
- **Location**: `/opt/mcp-servers/email-marketing-mcp-server/`
- **Service**: `email-marketing-mcp.service`
- **Status**: ✅ Installed and ready for configuration
- **Tools Available**: 10 Email marketing automation tools

## 🔧 Integration Steps for n8n MCP Client

### Step 1: Configure API Credentials

SSH into the droplet and configure the API tokens:

```bash
# Connect to droplet
ssh -i ~/.ssh/digitalocean root@157.230.13.13

# Configure Pinterest MCP Server
cd /opt/mcp-servers/pinterest-mcp-server
nano .env
# Add your Pinterest API token:
# PINTEREST_ACCESS_TOKEN=your_pinterest_token_here

# Configure Email Marketing MCP Server
cd /opt/mcp-servers/email-marketing-mcp-server
nano .env
# Add your email service API keys:
# EMAIL_PROVIDER=sendgrid
# SENDGRID_API_KEY=your_sendgrid_api_key_here
# MAILCHIMP_API_KEY=your_mailchimp_api_key_here
```

### Step 2: Start the MCP Servers

```bash
# Start both servers
/opt/mcp-servers/start-mcp-servers.sh

# Or start individually
systemctl start pinterest-mcp
systemctl start email-marketing-mcp

# Check status
systemctl status pinterest-mcp email-marketing-mcp
```

### Step 3: Configure n8n MCP Client

The n8n MCP client configuration is ready at `/opt/mcp-servers/n8n-mcp-config.json`:

```json
{
  "mcpServers": {
    "pinterest-mcp": {
      "command": "python",
      "args": ["/opt/mcp-servers/pinterest-mcp-server/server.py"],
      "cwd": "/opt/mcp-servers/pinterest-mcp-server",
      "env": {
        "PINTEREST_ACCESS_TOKEN": "YOUR_PINTEREST_TOKEN_HERE"
      }
    },
    "email-marketing-mcp": {
      "command": "python",
      "args": ["/opt/mcp-servers/email-marketing-mcp-server/server.py"],
      "cwd": "/opt/mcp-servers/email-marketing-mcp-server",
      "env": {
        "EMAIL_PROVIDER": "sendgrid",
        "SENDGRID_API_KEY": "YOUR_SENDGRID_API_KEY_HERE",
        "MAILCHIMP_API_KEY": "YOUR_MAILCHIMP_API_KEY_HERE"
      }
    }
  }
}
```

## 🛠️ Available MCP Tools

### Pinterest MCP Server Tools

1. **`create_pin`** - Post new pins with product links
2. **`create_promoted_pin`** - Create Pinterest ads campaigns
3. **`get_pin_metrics`** - Track performance metrics
4. **`create_board`** - Organize themed collections
5. **`schedule_pins`** - Content calendar management
6. **`get_trending_topics`** - Market research
7. **`search_pins`** - Find relevant content
8. **`get_boards`** - Retrieve board information
9. **`get_user_profile`** - Account statistics
10. **`manage_business_account`** - Business account operations

### Email Marketing MCP Server Tools

1. **`create_campaign`** - Newsletter and promotional emails
2. **`segment_audience`** - Customer list segmentation
3. **`track_engagement`** - Open rates and click tracking
4. **`automate_sequences`** - Welcome series and win-back campaigns
5. **`create_template`** - Email design management
6. **`schedule_send`** - Campaign timing optimization
7. **`send_transactional`** - Order confirmations and shipping updates
8. **`manage_subscribers`** - Add/remove from lists
9. **`get_analytics`** - Campaign performance metrics
10. **`create_automation`** - Trigger-based email workflows

## 🎯 VividWalls Business Use Cases

### Pinterest Marketing Automation
- **Art Collection Launches**: Create boards and pins for new collections
- **Seasonal Campaigns**: Pin art suitable for holidays and seasons
- **Product Promotion**: Create promoted pins for limited edition prints
- **Market Research**: Analyze trending art styles and themes

### Email Marketing Automation
- **Customer Onboarding**: Welcome series for new art collectors
- **Order Lifecycle**: Confirmation, production, shipping updates
- **Retention Campaigns**: Win-back emails for dormant customers
- **VIP Programs**: Exclusive previews and offers for high-value customers

## 🔄 Integration with VividWalls MAS Agents

### Marketing Campaign Agent Integration
```javascript
// Pinterest campaign creation
${pinterest_create_promoted_pin}({
  board_id: "vividwalls_collections",
  pin_data: {
    title: "Limited Edition Botanical Prints",
    description: "Exclusive art prints, only 50 available",
    link: "https://vividwalls.co/collections/botanical"
  },
  ad_targeting: {
    interests: ["art", "interior_design", "home_decor"],
    demographics: "25-65"
  }
})

// Email campaign for collection launch
${email_create_campaign}({
  campaign_name: "New Botanical Collection Launch",
  audience_segment: "art_enthusiasts",
  template_id: "collection_launch_template",
  send_time: "2025-02-01T10:00:00Z"
})
```

### Customer Relationship Agent Integration
```javascript
// Segment customers for targeted campaigns
${email_segment_audience}({
  criteria: {
    purchase_history: "2+ orders",
    art_preferences: ["abstract", "modern"],
    last_purchase: "< 90 days"
  },
  segment_name: "active_abstract_collectors"
})

// Create Pinterest board for customer interests
${pinterest_create_board}({
  name: "Abstract Art Collection 2025",
  description: "Modern abstract prints for sophisticated collectors",
  privacy: "public"
})
```

## 📊 Monitoring and Management

### Health Checks
```bash
# Check MCP server status
systemctl status pinterest-mcp email-marketing-mcp

# View logs
journalctl -u pinterest-mcp -f
journalctl -u email-marketing-mcp -f

# Test MCP connectivity
cd /opt/mcp-servers/pinterest-mcp-server && python test_connection.py
cd /opt/mcp-servers/email-marketing-mcp-server && python test_connection.py
```

### Performance Monitoring
- **Pinterest Metrics**: Pin impressions, saves, clicks, outbound clicks
- **Email Metrics**: Open rates, click rates, conversion rates, unsubscribe rates
- **Integration Health**: Response times, error rates, API quota usage

## 🚀 Next Steps

1. **Configure API Credentials**: Add Pinterest and email service API tokens
2. **Start Services**: Launch both MCP servers
3. **Test Integration**: Verify n8n can connect to MCP servers
4. **Deploy Workflows**: Implement VividWalls MAS marketing workflows
5. **Monitor Performance**: Track metrics and optimize campaigns

## 🔐 Security Considerations

- **API Keys**: Stored securely in environment files with restricted permissions
- **Network Security**: MCP servers run locally on droplet, not exposed externally
- **Service Isolation**: Each MCP server runs in separate virtual environment
- **Logging**: Comprehensive logging for audit and debugging

## 📞 Support and Troubleshooting

### Common Issues
- **Authentication Errors**: Check API tokens in .env files
- **Service Startup**: Verify Python virtual environments are activated
- **n8n Connection**: Ensure MCP client configuration matches server setup

### Management Commands
```bash
# Start all MCP servers
/opt/mcp-servers/start-mcp-servers.sh

# Restart individual services
systemctl restart pinterest-mcp
systemctl restart email-marketing-mcp

# View detailed logs
journalctl -u pinterest-mcp --since "1 hour ago"
journalctl -u email-marketing-mcp --since "1 hour ago"
```

---

## 🎉 Deployment Complete!

The Pinterest and Email Marketing MCP servers are now ready to power the VividWalls Multi-Agent System marketing automation. The next phase involves configuring API credentials and integrating with the n8n workflows for autonomous art print business management.

**Ready for Phase 2**: Medium priority MCP servers (WordPress and Analytics) deployment.