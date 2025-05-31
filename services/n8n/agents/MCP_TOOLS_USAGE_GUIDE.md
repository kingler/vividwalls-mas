# VividWalls MCP Tools Usage Guide for Agents

## Overview
This guide provides comprehensive instructions for VividWalls agents on when and how to use MCP (Model Context Protocol) tools across our 5 deployed MCP servers. Each agent should integrate these tools into their workflows for autonomous business operations.

## Available MCP Servers & Tools

### 🛒 Shopify MCP Server (24 tools)
**Purpose**: E-commerce operations, product management, order processing
**Location**: Droplet (SSH-tunneled)

#### Product Management Tools
- `mcp_shopify_get_products` - Retrieve product catalog
- `mcp_shopify_get_product` - Get specific product details
- `mcp_shopify_create_product` - Add new products to catalog
- `mcp_shopify_update_product` - Modify product information, pricing
- `mcp_shopify_delete_product` - Remove products from catalog

#### Order Processing Tools
- `mcp_shopify_get_orders` - Retrieve order data and analytics
- `mcp_shopify_get_order` - Get specific order details
- `mcp_shopify_create_order` - Create manual orders
- `mcp_shopify_update_order` - Modify order status, fulfillment

#### Customer Management Tools
- `mcp_shopify_get_customers` - Retrieve customer database
- `mcp_shopify_get_customer` - Get specific customer details
- `mcp_shopify_create_customer` - Add new customers
- `mcp_shopify_update_customer` - Update customer information

#### Collection & Inventory Tools
- `mcp_shopify_get_collections` - Retrieve product collections
- `mcp_shopify_get_collection` - Get specific collection details
- `mcp_shopify_create_collection` - Create new product collections
- `mcp_shopify_update_collection` - Modify collection settings
- `mcp_shopify_get_inventory` - Check inventory levels
- `mcp_shopify_update_inventory` - Adjust stock quantities

#### Automation Tools
- `mcp_shopify_get_webhooks` - List active webhooks
- `mcp_shopify_create_webhook` - Set up automation triggers
- `mcp_shopify_delete_webhook` - Remove webhook configurations

### 📱 Facebook Ads MCP Server (38 tools)
**Purpose**: Social media advertising, campaign management
**Location**: Droplet (SSH-tunneled)

#### Account Management Tools
- `mcp_facebook-ads_list_ad_accounts` - Get available ad accounts
- `mcp_facebook-ads_get_details_of_ad_account` - Account details and permissions
- `mcp_facebook-ads_update_ad_account` - Modify account settings

#### Campaign Management Tools
- `mcp_facebook-ads_get_campaigns_by_adaccount` - List all campaigns
- `mcp_facebook-ads_get_campaign_by_id` - Get specific campaign details
- `mcp_facebook-ads_create_campaign` - Create new ad campaigns
- `mcp_facebook-ads_update_campaign` - Modify campaign settings
- `mcp_facebook-ads_delete_campaign` - Remove campaigns
- `mcp_facebook-ads_bulk_update_campaigns` - Batch campaign updates

#### Ad Set Management Tools
- `mcp_facebook-ads_get_adsets_by_adaccount` - List all ad sets
- `mcp_facebook-ads_get_adsets_by_campaign` - Get campaign-specific ad sets
- `mcp_facebook-ads_get_adset_by_id` - Get specific ad set details
- `mcp_facebook-ads_create_adset` - Create new ad sets
- `mcp_facebook-ads_update_adset` - Modify ad set targeting/budget
- `mcp_facebook-ads_delete_adset` - Remove ad sets
- `mcp_facebook-ads_bulk_update_adsets` - Batch ad set updates

#### Ad Management Tools
- `mcp_facebook-ads_get_ads_by_adaccount` - List all ads
- `mcp_facebook-ads_get_ads_by_campaign` - Get campaign-specific ads
- `mcp_facebook-ads_get_ads_by_adset` - Get ad set-specific ads
- `mcp_facebook-ads_get_ad_by_id` - Get specific ad details
- `mcp_facebook-ads_create_ad` - Create new ads
- `mcp_facebook-ads_update_ad` - Modify ad content/targeting
- `mcp_facebook-ads_delete_ad` - Remove ads
- `mcp_facebook-ads_bulk_update_ads` - Batch ad updates

#### Creative Management Tools
- `mcp_facebook-ads_get_ad_creatives_by_ad_id` - Get ad creative assets
- `mcp_facebook-ads_get_ad_creative_by_id` - Get specific creative details
- `mcp_facebook-ads_create_ad_creative` - Create new ad creatives
- `mcp_facebook-ads_update_ad_creative` - Modify creative content
- `mcp_facebook-ads_delete_ad_creative` - Remove creatives

#### Analytics & Insights Tools
- `mcp_facebook-ads_get_adaccount_insights` - Account-level performance
- `mcp_facebook-ads_get_campaign_insights` - Campaign performance metrics
- `mcp_facebook-ads_get_adset_insights` - Ad set performance data
- `mcp_facebook-ads_get_ad_insights` - Individual ad performance
- `mcp_facebook-ads_fetch_pagination_url` - Handle large data sets

#### Activity Tracking Tools
- `mcp_facebook-ads_get_activities_by_adaccount` - Account activity log
- `mcp_facebook-ads_get_activities_by_adset` - Ad set activity tracking

#### Instagram Integration Tools
- `mcp_facebook-ads_get_instagram_accounts` - Connected Instagram accounts
- `mcp_facebook-ads_get_instagram_media` - Instagram content library
- `mcp_facebook-ads_create_instagram_ad_creative` - Instagram-specific creatives

### ⚡ n8n MCP Server (14 tools)
**Purpose**: Workflow automation, process orchestration
**Location**: Local (Docker-based n8n)

#### Workflow Management Tools
- `mcp_n8n_list_workflows` - Get all available workflows
- `mcp_n8n_get_workflow` - Get specific workflow details
- `mcp_n8n_create_workflow` - Create new automation workflows
- `mcp_n8n_update_workflow` - Modify existing workflows
- `mcp_n8n_delete_workflow` - Remove workflows

#### Workflow Execution Tools
- `mcp_n8n_activate_workflow` - Enable workflow automation
- `mcp_n8n_deactivate_workflow` - Disable workflow automation
- `mcp_n8n_execute_workflow` - Manually trigger workflows
- `mcp_n8n_get_executions` - Get workflow execution history
- `mcp_n8n_get_execution` - Get specific execution details

#### Credential Management Tools
- `mcp_n8n_list_credentials` - Get available API connections
- `mcp_n8n_get_credential` - Get specific credential details
- `mcp_n8n_create_credential` - Add new API connections
- `mcp_n8n_update_credential` - Modify existing credentials
- `mcp_n8n_delete_credential` - Remove API connections

### 📌 Pinterest MCP Server (10 tools)
**Purpose**: Visual marketing, pin management
**Location**: Droplet

#### Pin Management Tools
- `create_pin` - Post new pins with product links
- `create_promoted_pin` - Create Pinterest ads campaigns
- `get_pin_metrics` - Track pin performance metrics
- `schedule_pins` - Content calendar management

#### Board Management Tools
- `create_board` - Organize themed collections
- `get_boards` - Retrieve board information

#### Research & Discovery Tools
- `get_trending_topics` - Market research and trends
- `search_pins` - Find relevant content inspiration

#### Account Management Tools
- `get_user_profile` - Account statistics and insights
- `manage_business_account` - Business account operations

### 📧 Email Marketing MCP Server (10 tools)
**Purpose**: Email campaigns, customer engagement
**Location**: Droplet

#### Campaign Management Tools
- `create_campaign` - Newsletter and promotional emails
- `schedule_send` - Campaign timing optimization
- `get_analytics` - Campaign performance metrics

#### Audience Management Tools
- `segment_audience` - Customer list segmentation
- `manage_subscribers` - Add/remove from lists

#### Automation Tools
- `automate_sequences` - Welcome series and win-back campaigns
- `create_automation` - Trigger-based email workflows

#### Content Tools
- `create_template` - Email design management
- `send_transactional` - Order confirmations and shipping updates
- `track_engagement` - Open rates and click tracking

## Agent-Specific MCP Usage Guidelines

### 🎯 Business Manager Agent

#### Daily Operations MCP Usage
```javascript
// Morning Performance Check (9:00 AM)
const dailyMetrics = {
  shopify: await mcp_shopify_get_orders({
    created_at_min: "yesterday",
    status: "any"
  }),
  facebook: await mcp_facebook-ads_get_adaccount_insights({
    date_preset: "yesterday",
    fields: ["spend", "revenue", "roas"]
  }),
  email: await get_analytics({
    campaign_type: "all",
    date_range: "yesterday"
  })
};

// Resource Allocation Decision
if (dailyMetrics.facebook.roas > 3.5) {
  await mcp_facebook-ads_update_campaign({
    campaign_id: "best_performer",
    daily_budget: dailyMetrics.facebook.daily_budget * 1.25
  });
}
```

#### Weekly Budget Reallocation
```javascript
// Get weekly performance data
const weeklyInsights = await mcp_facebook-ads_get_campaign_insights({
  date_preset: "last_7_days",
  fields: ["campaign_name", "spend", "revenue", "roas"]
});

// Identify top and bottom performers
const topPerformers = weeklyInsights.filter(c => c.roas > 4);
const underPerformers = weeklyInsights.filter(c => c.roas < 2.5);

// Reallocate budget
for (const campaign of topPerformers) {
  await mcp_facebook-ads_update_campaign({
    campaign_id: campaign.id,
    daily_budget: campaign.daily_budget * 1.3
  });
}

for (const campaign of underPerformers) {
  await mcp_facebook-ads_update_campaign({
    campaign_id: campaign.id,
    status: "PAUSED"
  });
}
```

### 📈 Marketing Campaign Agent

#### Campaign Creation Workflow
```javascript
// 1. Analyze Research Insights
const researchData = await mcp_n8n_execute_workflow({
  workflow_id: "marketing-research-analysis",
  data: { month: "current" }
});

// 2. Create Facebook Campaign Structure
const newCampaign = await mcp_facebook-ads_create_campaign({
  name: `VividWalls ${researchData.trendTheme} Collection Q${researchData.quarter}`,
  objective: "CONVERSIONS",
  status: "ACTIVE",
  special_ad_categories: []
});

// 3. Create Ad Sets for Different Audiences
const audiences = ["art_collectors", "interior_designers", "home_decorators"];
for (const audience of audiences) {
  await mcp_facebook-ads_create_adset({
    campaign_id: newCampaign.id,
    name: `${audience}_targeting`,
    optimization_goal: "CONVERSIONS",
    daily_budget: 5000, // $50
    targeting: {
      interests: researchData.audienceInterests[audience],
      age_min: 25,
      age_max: 65
    }
  });
}

// 4. Create Pinterest Campaign
await create_promoted_pin({
  board_id: "vividwalls_collections",
  pin_data: {
    title: `${researchData.trendTheme} Art Collection`,
    description: researchData.productDescription,
    link: `https://vividwalls.co/collections/${researchData.collectionSlug}`
  },
  budget: 3000, // $30/day
  targeting: {
    keywords: researchData.trendKeywords,
    interests: ["art", "interior_design", "home_decor"]
  }
});

// 5. Set up Email Campaign
await create_campaign({
  campaign_name: `New ${researchData.trendTheme} Collection Launch`,
  audience_segment: "active_customers",
  template_id: "collection_launch_template",
  send_time: "2025-02-01T10:00:00Z",
  personalization: {
    collection_theme: researchData.trendTheme,
    featured_products: researchData.featuredProducts
  }
});
```

#### A/B Testing Implementation
```javascript
// Create A/B test variants
const testCampaigns = await Promise.all([
  mcp_facebook-ads_create_ad({
    adset_id: adSetId,
    name: "Creative_A_lifestyle",
    creative: {
      object_story_spec: {
        page_id: pageId,
        link_data: {
          image_hash: "lifestyle_image_hash",
          headline: "Transform Your Space with Art",
          message: "Discover handpicked art that speaks to your style"
        }
      }
    }
  }),
  mcp_facebook-ads_create_ad({
    adset_id: adSetId,
    name: "Creative_B_product",
    creative: {
      object_story_spec: {
        page_id: pageId,
        link_data: {
          image_hash: "product_image_hash",
          headline: "Limited Edition Art Prints",
          message: "Shop exclusive designs before they're gone"
        }
      }
    }
  })
]);

// Schedule performance check
await mcp_n8n_create_workflow({
  name: "AB_Test_Performance_Check",
  nodes: [{
    type: "cron",
    parameters: { cronExpression: "0 */6 * * *" }, // Every 6 hours
    nextNode: "facebook_insights_check"
  }, {
    type: "facebook_insights",
    name: "facebook_insights_check",
    parameters: {
      ad_ids: testCampaigns.map(c => c.id),
      fields: ["impressions", "clicks", "conversions", "cost_per_conversion"]
    }
  }]
});
```

### 🛒 Customer Relationship Agent

#### Customer Segmentation & Personalization
```javascript
// 1. Get Customer Data from Shopify
const customers = await mcp_shopify_get_customers({
  limit: 250,
  fields: "id,email,orders_count,total_spent,created_at,last_order_date"
});

// 2. Create Behavioral Segments
const segments = {
  highValue: customers.filter(c => c.total_spent > 500),
  frequent: customers.filter(c => c.orders_count > 3),
  dormant: customers.filter(c => 
    new Date() - new Date(c.last_order_date) > 90 * 24 * 60 * 60 * 1000
  ),
  newCustomers: customers.filter(c => 
    new Date() - new Date(c.created_at) < 30 * 24 * 60 * 60 * 1000
  )
};

// 3. Create Facebook Custom Audiences
for (const [segmentName, segmentCustomers] of Object.entries(segments)) {
  const customAudience = await mcp_facebook-ads_create_custom_audience({
    name: `VividWalls_${segmentName}_Customers`,
    description: `${segmentName} customer segment`,
    customer_file_source: "USER_PROVIDED_ONLY",
    customer_data: segmentCustomers.map(c => ({
      email: c.email,
      lifetime_value: c.total_spent
    }))
  });
  
  // Create targeted campaign for each segment
  await mcp_facebook-ads_create_campaign({
    name: `Retargeting_${segmentName}`,
    objective: "CONVERSIONS",
    targeting: {
      custom_audiences: [customAudience.id]
    }
  });
}

// 4. Set up Email Automation based on Segments
for (const [segmentName, segmentCustomers] of Object.entries(segments)) {
  await segment_audience({
    segment_name: `shopify_${segmentName}`,
    criteria: getSegmentCriteria(segmentName),
    customer_emails: segmentCustomers.map(c => c.email)
  });
  
  // Create automated email sequence
  await create_automation({
    name: `${segmentName}_nurture_sequence`,
    trigger: {
      type: "segment_entry",
      segment: `shopify_${segmentName}`
    },
    emails: getEmailSequence(segmentName)
  });
}
```

#### Cart Abandonment Recovery
```javascript
// 1. Trigger workflow when cart is abandoned (via Shopify webhook)
await mcp_n8n_create_workflow({
  name: "Cart_Abandonment_Recovery",
  trigger: {
    type: "webhook",
    path: "/shopify/cart_abandoned"
  },
  nodes: [
    {
      name: "delay_1_hour",
      type: "wait",
      parameters: { amount: 1, unit: "hours" }
    },
    {
      name: "send_recovery_email",
      type: "email_marketing",
      parameters: {
        template: "cart_abandonment_1",
        personalization: {
          cart_items: "{{ $webhook.body.line_items }}",
          total_price: "{{ $webhook.body.total_price }}"
        }
      }
    },
    {
      name: "create_facebook_retargeting",
      type: "facebook_ads",
      parameters: {
        campaign_type: "dynamic_product_ads",
        audience: "cart_abandoners",
        products: "{{ $webhook.body.line_items }}"
      }
    }
  ]
});

// 2. Create Facebook Dynamic Retargeting Campaign
await mcp_facebook-ads_create_campaign({
  name: "Cart_Abandonment_Recovery",
  objective: "CONVERSIONS",
  status: "ACTIVE"
});

await mcp_facebook-ads_create_adset({
  campaign_id: campaignId,
  name: "Cart_Abandoners_Retargeting",
  optimization_goal: "CONVERSIONS",
  daily_budget: 2000, // $20
  targeting: {
    custom_audiences: ["cart_abandoners_30_days"]
  }
});
```

### 🎨 Content Marketing Agent

#### Content Calendar Management
```javascript
// 1. Get upcoming product releases from Shopify
const upcomingProducts = await mcp_shopify_get_products({
  status: "draft",
  created_at_min: new Date().toISOString()
});

// 2. Create Pinterest content calendar
const contentCalendar = upcomingProducts.map(product => ({
  date: new Date(product.published_at),
  pinterest_pins: [
    {
      title: `${product.title} - Room Inspiration`,
      description: `See how ${product.title} transforms any space`,
      board: "room_inspiration",
      image_type: "lifestyle"
    },
    {
      title: `${product.title} - Product Showcase`,
      description: product.description,
      board: "art_collections",
      image_type: "product"
    }
  ]
}));

// 3. Schedule Pinterest pins
for (const content of contentCalendar) {
  for (const pin of content.pinterest_pins) {
    await schedule_pins({
      pin_data: pin,
      scheduled_time: content.date,
      board_id: pin.board
    });
  }
}

// 4. Create Facebook content series
await mcp_n8n_execute_workflow({
  workflow_id: "content_series_creation",
  data: {
    products: upcomingProducts,
    platforms: ["facebook", "instagram"],
    content_types: ["product_showcase", "styling_tips", "behind_scenes"]
  }
});
```

#### User-Generated Content Campaigns
```javascript
// 1. Create UGC campaign on Facebook
const ugcCampaign = await mcp_facebook-ads_create_campaign({
  name: "VividWalls_UGC_Collection",
  objective: "ENGAGEMENT",
  status: "ACTIVE"
});

// 2. Set up hashtag tracking workflow
await mcp_n8n_create_workflow({
  name: "UGC_Content_Monitoring",
  trigger: {
    type: "cron",
    parameters: { cronExpression: "0 */2 * * *" } // Every 2 hours
  },
  nodes: [
    {
      name: "search_hashtags",
      type: "social_media_monitor",
      parameters: {
        hashtags: ["#VividWallsArt", "#MyVividWalls", "#ArtInMyHome"],
        platforms: ["instagram", "facebook"]
      }
    },
    {
      name: "curate_content",
      type: "content_curation",
      parameters: {
        quality_threshold: 0.8,
        engagement_minimum: 50
      }
    },
    {
      name: "request_permission",
      type: "email_marketing",
      parameters: {
        template: "ugc_permission_request"
      }
    }
  ]
});

// 3. Create email campaign for UGC participants
await create_campaign({
  campaign_name: "UGC_Showcase_Feature",
  audience_segment: "ugc_contributors",
  template_id: "ugc_feature_notification",
  personalization: {
    featured_content: true,
    discount_code: "UGC15"
  }
});
```

### 📦 Orders Fulfillment Agent

#### Order Processing Automation
```javascript
// 1. Set up real-time order monitoring
await mcp_n8n_create_workflow({
  name: "Order_Processing_Automation",
  trigger: {
    type: "webhook",
    path: "/shopify/order_created"
  },
  nodes: [
    {
      name: "order_validation",
      type: "data_validation",
      parameters: {
        required_fields: ["customer", "line_items", "shipping_address"],
        fraud_check: true
      }
    },
    {
      name: "inventory_check",
      type: "shopify_inventory",
      parameters: {
        action: "verify_availability",
        reserve_items: true
      }
    },
    {
      name: "pictorem_fulfillment",
      type: "pictorem_integration",
      parameters: {
        action: "create_print_order",
        quality_settings: "premium"
      }
    },
    {
      name: "customer_notification",
      type: "email_marketing",
      parameters: {
        template: "order_confirmation",
        include_tracking: true
      }
    }
  ]
});

// 2. Monitor order status and update customers
const recentOrders = await mcp_shopify_get_orders({
  status: "unfulfilled",
  created_at_min: new Date(Date.now() - 24*60*60*1000).toISOString()
});

for (const order of recentOrders) {
  // Check fulfillment status
  const fulfillmentStatus = await checkPictoremOrderStatus(order.id);
  
  if (fulfillmentStatus === "in_production") {
    await send_transactional({
      recipient: order.customer.email,
      template: "order_in_production",
      data: {
        order_number: order.order_number,
        estimated_completion: fulfillmentStatus.estimated_date
      }
    });
  }
  
  if (fulfillmentStatus === "shipped") {
    await mcp_shopify_update_order({
      order_id: order.id,
      fulfillment_status: "fulfilled",
      tracking_number: fulfillmentStatus.tracking_number
    });
    
    await send_transactional({
      recipient: order.customer.email,
      template: "order_shipped",
      data: {
        order_number: order.order_number,
        tracking_number: fulfillmentStatus.tracking_number,
        tracking_url: fulfillmentStatus.tracking_url
      }
    });
  }
}
```

#### Inventory Management
```javascript
// 1. Daily inventory sync with Pictorem
await mcp_n8n_execute_workflow({
  workflow_id: "daily_inventory_sync",
  data: {
    sync_type: "full",
    update_shopify: true,
    low_stock_threshold: 5
  }
});

// 2. Low stock alerts and actions
const lowStockProducts = await mcp_shopify_get_products({
  inventory_quantity: "<5",
  status: "active"
});

for (const product of lowStockProducts) {
  // Pause Facebook ads for out-of-stock products
  const relatedAds = await mcp_facebook-ads_search_ads({
    product_id: product.id,
    status: "ACTIVE"
  });
  
  for (const ad of relatedAds) {
    await mcp_facebook-ads_update_ad({
      ad_id: ad.id,
      status: "PAUSED"
    });
  }
  
  // Notify business manager
  await send_transactional({
    recipient: "manager@vividwalls.com",
    template: "low_stock_alert",
    data: {
      product_name: product.title,
      current_stock: product.inventory_quantity,
      paused_ads_count: relatedAds.length
    }
  });
}
```

## MCP Integration Best Practices

### 1. Error Handling & Retries
```javascript
async function safeExecuteMCP(tool, params, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await tool(params);
    } catch (error) {
      console.log(`MCP tool failed (attempt ${attempt}/${maxRetries}):`, error);
      
      if (attempt === maxRetries) {
        // Log to monitoring system
        await mcp_n8n_execute_workflow({
          workflow_id: "error_notification",
          data: {
            tool_name: tool.name,
            error_message: error.message,
            params: params
          }
        });
        throw error;
      }
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt-1)));
    }
  }
}
```

### 2. Rate Limiting & API Quotas
```javascript
// Facebook Ads API rate limiting
const facebookRateLimit = {
  callsPerHour: 200,
  callsRemaining: 200,
  resetTime: Date.now() + 3600000
};

async function rateLimitedFacebookCall(tool, params) {
  if (facebookRateLimit.callsRemaining <= 0) {
    const waitTime = facebookRateLimit.resetTime - Date.now();
    if (waitTime > 0) {
      await new Promise(resolve => setTimeout(resolve, waitTime));
      facebookRateLimit.callsRemaining = facebookRateLimit.callsPerHour;
      facebookRateLimit.resetTime = Date.now() + 3600000;
    }
  }
  
  const result = await tool(params);
  facebookRateLimit.callsRemaining--;
  return result;
}
```

### 3. Data Consistency & Synchronization
```javascript
// Ensure data consistency across platforms
async function syncCustomerData(customerId) {
  const shopifyCustomer = await mcp_shopify_get_customer({ customer_id: customerId });
  
  // Update email marketing segments
  await segment_audience({
    action: "update_customer",
    customer_id: customerId,
    customer_data: {
      email: shopifyCustomer.email,
      total_spent: shopifyCustomer.total_spent,
      order_count: shopifyCustomer.orders_count,
      last_order_date: shopifyCustomer.last_order_date
    }
  });
  
  // Update Facebook custom audiences
  await mcp_facebook-ads_update_custom_audience({
    audience_id: "vividwalls_customers",
    action: "add_users",
    payload: [{
      email: shopifyCustomer.email,
      lifetime_value: shopifyCustomer.total_spent
    }]
  });
}
```

### 4. Performance Monitoring
```javascript
// Track MCP tool performance
const mcpMetrics = {
  toolUsage: {},
  responseTime: {},
  errorRate: {}
};

async function monitoredMCPCall(toolName, tool, params) {
  const startTime = Date.now();
  
  try {
    const result = await tool(params);
    
    // Track success metrics
    mcpMetrics.toolUsage[toolName] = (mcpMetrics.toolUsage[toolName] || 0) + 1;
    mcpMetrics.responseTime[toolName] = Date.now() - startTime;
    
    return result;
  } catch (error) {
    // Track error metrics
    mcpMetrics.errorRate[toolName] = (mcpMetrics.errorRate[toolName] || 0) + 1;
    throw error;
  }
}

// Daily metrics reporting
await mcp_n8n_create_workflow({
  name: "MCP_Performance_Report",
  trigger: {
    type: "cron",
    parameters: { cronExpression: "0 9 * * *" } // Daily at 9 AM
  },
  nodes: [{
    name: "compile_metrics",
    type: "data_aggregation",
    parameters: {
      metrics: mcpMetrics,
      report_type: "daily_summary"
    }
  }]
});
```

## Conclusion

This comprehensive guide ensures all VividWalls agents understand when and how to use MCP tools effectively. Each agent should integrate these tools into their workflows to achieve autonomous business operations while maintaining data consistency and optimal performance across all platforms.

Remember to:
- Always handle errors gracefully with retries
- Respect API rate limits and quotas  
- Maintain data consistency across platforms
- Monitor tool performance and usage
- Coordinate actions between agents to avoid conflicts