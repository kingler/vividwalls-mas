# VividWalls MAS Implementation Guide

## Best Practices for Deploying Your Multiagent System

---

## 1. Prompt Engineering Best Practices Applied

### 1.1 Clarity and Specificity

- **Role Definition**: Each agent starts with a clear identity statement
- **Bounded Context**: Specific responsibilities prevent scope creep
- **Measurable Objectives**: Concrete KPIs for performance tracking

### 1.2 Structured Information Architecture

- **Hierarchical Organization**: Clear sections for easy navigation
- **Consistent Format**: All prompts follow the same structure
- **Progressive Detail**: High-level overview → specific instructions

### 1.3 Tool Integration Patterns

```javascript
// Consistent tool calling syntax
${tool_category_function_name}

// Examples:
${shopify_get_products}
${pictorem_submit_order_browser_ai}
${facebook_create_campaign}
```

### 1.4 Context 

- **Business Context**: Each agent understands VividWalls' value proposition
- **Integration Context**: Clear understanding of other agents' roles
- **Performance Context**: Embedded success metrics

---

## 2. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **Database Setup**
   ```sql
   -- Create PostgreSQL schema
   CREATE SCHEMA vividwalls_mas;
   
   -- Set up agent tables
   CREATE TABLE agents (
     agent_id VARCHAR(50) PRIMARY KEY,
     agent_type VARCHAR(50),
     status VARCHAR(20),
     last_active TIMESTAMP,
     configuration JSONB
   );
   ```

2. **n8n Workflow Configuration**
   - Install n8n with PostgreSQL backend
   - Configure LangChain integration
   - Set up agent communication queues

3. **MCP Tool Deployment**
   - Deploy Shopify MCP Server
   - Deploy Pictorem MCP Server  
   - Deploy Facebook Ads MCP Server
   - Configure authentication for each

### Phase 2: Core Agents (Week 3-4)

1. **Business Manager Agent**
   - Deploy with orchestration capabilities
   - Test delegation mechanisms
   - Implement monitoring dashboard

2. **Order Flow Agents**
   - Shopify Agent → Orders Fulfillment → Pictorem
   - Test complete order lifecycle
   - Implement error handling

3. **Initial Testing**
   - Single order processing
   - Error scenario handling
   - Performance benchmarking

### Phase 3: Marketing Agents (Week 5-6)

1. **Marketing Research Agent**
   - Configure web search capabilities
   - Set up monthly triggers
   - Test report generation

2. **Marketing Campaign Agent**
   - Implement campaign planning logic
   - Test budget allocation
   - Verify sub-agent delegation

3. **Channel Agents**
   - Deploy Facebook Meta Agent
   - Configure Pinterest Agent
   - Test campaign execution

### Phase 4: Customer Agents (Week 7-8)

1. **Sales Agent**
   - Implement CopilotKit integration
   - Configure Shopify storefront hooks
   - Test real-time assistance

2. **Customer Service Agent**
   - Set up email integration
   - Implement response templates
   - Test escalation procedures

3. **Customer Relationship Agent**
   - Configure segmentation rules
   - Implement retention campaigns
   - Test VIP program logic

### Phase 5: Optimization (Week 9-10)

1. **Performance Tuning**
   - Optimize agent response times
   - Implement caching strategies
   - Load test the system

2. **Monitoring Setup**
   - Deploy monitoring dashboards
   - Configure alerting rules
   - Implement logging aggregation

---

## 3. n8n Workflow Examples

### 3.1 Monthly Research Trigger

```json
{
  "nodes": [
    {
      "name": "Monthly Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 0 1 * *"
      }
    },
    {
      "name": "Marketing Research Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "prompt": "[Research Agent System Prompt]",
        "tools": ["web_search", "query_customer_data"]
      }
    },
    {
      "name": "Send to Campaign Agent",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "insert",
        "table": "agent_messages",
        "columns": "from_agent,to_agent,payload"
      }
    }
  ]
}
```

### 3.2 Order Processing 

```json
{
  "nodes": [
    {
      "name": "Shopify Order Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "shopify-order",
        "method": "POST"
      }
    },
    {
      "name": "Orders Fulfillment Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "prompt": "[Fulfillment Agent System Prompt]",
        "tools": ["${pictorem_submit_order_browser_ai}"]
      }
    }
  ]
}
```

---

## 4. Testing Framework

### 4.1 Unit Tests per Agent

```javascript
// Example test for Marketing Campaign Agent
describe('Marketing Campaign Agent', () => {
  test('should create 3-month campaign plan', async () => {
    const researchData = mockResearchReport();
    const response = await agent.createCampaignStrategy(researchData);
    
    expect(response).toHaveProperty('campaigns');
    expect(response.campaigns).toHaveLength(3);
    expect(response.totalBudget).toBeLessThanOrEqual(10000);
  });
  
  test('should delegate to channel agents', async () => {
    const campaign = mockCampaign();
    const delegations = await agent.delegateToChannels(campaign);
    
    expect(delegations).toContainKey('facebook');
    expect(delegations).toContainKey('pinterest');
  });
});
```

### 4.2 Integration Tests

```javascript
// End-to-end order flow test
describe('Order Fulfillment Flow', () => {
  test('complete order lifecycle', async () => {
    // Create test order in Shopify
    const order = await shopifyAgent.createTestOrder();
    
    // Wait for fulfillment
    await waitFor(() => {
      const status = fulfillmentAgent.getOrderStatus(order.id);
      return status === 'submitted_to_pictorem';
    });
    
    // Verify Pictorem submission
    const pictoremOrder = await pictoremAgent.getOrder(order.id);
    expect(pictoremOrder.status).toBe('processing');
  });
});
```

---

## 5. Monitoring & Observability

### 5.1 Key Dashboards

#### System Health Dashboard

```yaml
panels:
  - agent_availability:
      query: "SELECT agent_id, status FROM agents WHERE last_active > NOW() - INTERVAL '5 minutes'"
  
  - message_queue_depth:
      query: "SELECT COUNT(*) FROM agent_messages WHERE status = 'pending'"
  
  - error_rate:
      query: "SELECT COUNT(*) FROM agent_logs WHERE level = 'ERROR' AND timestamp > NOW() - INTERVAL '1 hour'"
```

#### Business Performance Dashboard

```yaml
panels:
  - daily_revenue:
      source: "shopify_orders"
      metric: "SUM(total_price)"
      
  - conversion_funnel:
      stages: ["visited", "added_to_cart", "checkout", "purchased"]
      
  - campaign_roi:
      calculation: "(revenue - spend) / spend * 100"
```

### 5.2 Alerting Rules

```yaml
alerts:
  - name: "Agent Down"
    condition: "agent.last_active < NOW() - INTERVAL '10 minutes'"
    severity: "critical"
    notify: ["ops-team@vividwalls.co"]
    
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    severity: "high"
    notify: ["dev-team@vividwalls.co"]
    
  - name: "Low Conversion Rate"
    condition: "conversion_rate < 2%"
    severity: "medium"
    notify: ["marketing@vividwalls.co"]
```

---

## 6. Security Implementation

### 6.1 API Key Management

```javascript
// Secure storage for MCP tools
const secrets = {
  shopify: {
    token: process.env.SHOPIFY_ACCESS_TOKEN,
    domain: process.env.SHOPIFY_DOMAIN
  },
  pictorem: {
    username: process.env.PICTOREM_USERNAME,
    password: process.env.PICTOREM_PASSWORD
  },
  facebook: {
    token: process.env.FACEBOOK_ACCESS_TOKEN
  }
};

// Rotation schedule
const rotateKeys = async () => {
  // Implement 30-day rotation
  // Update n8n credentials
  // Notify agents of updates
};
```

### 6.2 Agent Permissions

```javascript
const agentPermissions = {
  business_manager: ["*"], // Full access
  marketing_campaign: ["marketing_*", "read_sales"],
  customer_service: ["read_orders", "update_orders", "read_customers"],
  fulfillment: ["read_orders", "submit_pictorem", "update_fulfillment"]
};
```

---

## 7. Troubleshooting Guide

### Common Issues & Solutions

#### Issue: Agent Communication Timeout

```bash
# Check message queue
SELECT * FROM agent_messages 
WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';

# Restart stuck agent
n8n restart-node --workflow=main --node="Agent Name"
```

#### Issue: MCP Tool Authentication Failure

```bash
# Test Shopify connection
curl -X GET "https://{shop}.myshopify.com/admin/api/2024-01/shop.json" \
  -H "X-Shopify-Access-Token: {token}"

# Verify Pictorem credentials
npm run test:pictorem-auth

# Check Facebook token
curl -G "https://graph.facebook.com/v19.0/me" \
  -d "access_token={token}"
```

#### Issue: Poor Campaign Performance

```sql
-- Analyze campaign metrics
SELECT 
  channel,
  AVG(ctr) as avg_ctr,
  AVG(conversion_rate) as avg_conv,
  SUM(spend)/SUM(revenue) as cost_ratio
FROM campaign_analytics
WHERE date > CURRENT_DATE - INTERVAL '30 days'
GROUP BY channel;
```

---

## 8. Scaling Considerations

### 8.1 Horizontal Scaling

- Deploy multiple instances of stateless agents
- Use PostgreSQL connection pooling
- Implement Redis for caching

### 8.2 Performance Optimization

```javascript
// Implement caching for frequently accessed data
const cacheStrategy = {
  products: { ttl: 3600 }, // 1 hour
  customers: { ttl: 900 }, // 15 minutes
  campaigns: { ttl: 300 }  // 5 minutes
};

// Batch operations where possible
const batchOrderSubmission = async (orders) => {
  const chunks = chunk(orders, 10);
  return Promise.all(chunks.map(submitBatch));
};
```

---

## 9. Continuous Improvement Process

### 9.1 Weekly Review 

- [ ] Review agent error logs
- [ ] Analyze performance metrics
- [ ] Check customer feedback
- [ ] Update prompts based on learnings
- [ ] Test new scenarios

### 9.2 Monthly Optimization

- [ ] Refine agent prompts based on performance
- [ ] Update tool integrations
- [ ] Optimize workflow efficiency
- [ ] Review and adjust KPIs
- [ ] Plan feature additions

---

## 10. Next Steps & Advanced Features

### 10.1 Immediate Priorities

1. Implement core order flow (Week 1-2)
2. Deploy marketing research capabilities (Week 3)
3. Launch customer service automation (Week 4)

### 10.2 Future Enhancements

- **Predictive Analytics**: ML models for demand forecasting
- **Dynamic Pricing**: Algorithm for edition-based pricing
- **Social Listening**: Expand research capabilities
- **Multi-language Support**: International expansion
- **Mobile App Integration**: Native app support

### 10.3 Advanced MCP Tools to Develop

```javascript
// Pinterest MCP Server
const pinterestTools = [
  'create_pin',
  'manage_boards',
  'analyze_trends',
  'schedule_content'
];

// Email Marketing MCP
const emailTools = [
  'create_campaign',
  'segment_audience',
  'track_engagement',
  'automate_sequences'
];

// Analytics MCP
const analyticsTools = [
  'generate_reports',
  'predict_trends',
  'calculate_ltv',
  'identify_opportunities'
];
```

---

Remember: Start small, test thoroughly, and scale gradually. Each agent should prove its value before adding complexity to the system.