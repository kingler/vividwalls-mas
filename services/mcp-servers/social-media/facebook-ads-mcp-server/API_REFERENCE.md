# Facebook Ads MCP Server - Complete API Reference

## 🚀 Overview

This MCP server provides **40 comprehensive tools** for managing Facebook and Instagram advertising campaigns with full CRUD operations. Perfect for VividWalls marketing automation and n8n workflow integration.

## 📊 Account Management

### `list_ad_accounts()`
```typescript
// Returns all ad accounts accessible with the current token
list_ad_accounts() -> Dict
```

### `get_details_of_ad_account(act_id, fields?)`
```typescript
get_details_of_ad_account(
  act_id: string,              // Ad account ID (with act_ prefix)
  fields?: string[]            // Optional fields to retrieve
) -> Dict
```

### `update_ad_account(ad_account_id, options)`
```typescript
update_ad_account(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  name?: string,               // New account name
  timezone?: string,           // New timezone
  currency?: string,           // New currency code
  spend_cap?: number           // New spend cap in cents
) -> Dict
```

## 🎯 Campaign Management (Full CRUD)

### `create_campaign(ad_account_id, name, objective, options)`
```typescript
create_campaign(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  name: string,                // Campaign name
  objective: string,           // Campaign objective (REACH, TRAFFIC, CONVERSIONS, etc.)
  status?: string,             // Campaign status (ACTIVE, PAUSED) - defaults to PAUSED
  buying_type?: string,        // Buying type (AUCTION, RESERVED) - defaults to AUCTION
  special_ad_categories?: string[], // Special ad categories if applicable
  bid_strategy?: string,       // Bid strategy (LOWEST_COST_WITHOUT_CAP, COST_CAP)
  budget_rebalance_flag?: boolean, // Enable budget rebalancing
  lifetime_budget?: number,    // Lifetime budget in cents
  daily_budget?: number,       // Daily budget in cents
  promoted_object?: object,    // Object being promoted
  source_campaign_id?: string  // Campaign to copy settings from
) -> Dict
```

### `update_campaign(campaign_id, options)`
```typescript
update_campaign(
  campaign_id: string,         // Campaign ID to update
  name?: string,               // New campaign name
  status?: string,             // New status (ACTIVE, PAUSED, DELETED)
  bid_strategy?: string,       // New bid strategy
  lifetime_budget?: number,    // New lifetime budget in cents
  daily_budget?: number,       // New daily budget in cents
  budget_rebalance_flag?: boolean // Budget rebalancing setting
) -> Dict
```

### `delete_campaign(campaign_id)`
```typescript
delete_campaign(
  campaign_id: string          // Campaign ID to delete
) -> Dict
```

### `get_campaign_by_id(campaign_id, fields?)`
```typescript
get_campaign_by_id(
  campaign_id: string,         // Campaign ID
  fields?: string[]            // Optional fields to retrieve
) -> Dict
```

### `get_campaigns_by_adaccount(ad_account_id, options)`
```typescript
get_campaigns_by_adaccount(
  ad_account_id: string,       // Ad account ID
  fields?: string[],           // Fields to retrieve
  filtering?: object[],        // Filter conditions
  limit?: number,              // Number of results
  after?: string,              // Pagination cursor
  effective_status?: string[]  // Filter by status
) -> Dict
```

## 🎪 Ad Set Management (Full CRUD)

### `create_adset(ad_account_id, campaign_id, name, optimization_goal, billing_event, options)`
```typescript
create_adset(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  campaign_id: string,         // Campaign ID to create ad set in
  name: string,                // Ad set name
  optimization_goal: string,   // Optimization goal (REACH, IMPRESSIONS, CLICKS, CONVERSIONS)
  billing_event: string,       // Billing event (IMPRESSIONS, CLICKS, ACTIONS)
  bid_amount?: number,         // Bid amount in cents
  daily_budget?: number,       // Daily budget in cents
  lifetime_budget?: number,    // Lifetime budget in cents
  targeting?: object,          // Targeting specification
  status?: string,             // Ad set status (ACTIVE, PAUSED) - defaults to PAUSED
  promoted_object?: object,    // Object being promoted
  attribution_spec?: object[], // Attribution settings
  adset_schedule?: object[],   // Schedule for ad set
  destination_type?: string,   // Destination type for traffic campaigns
  instagram_actor_id?: string  // Instagram account ID for Instagram ads
) -> Dict
```

### `update_adset(adset_id, options)`
```typescript
update_adset(
  adset_id: string,            // Ad set ID to update
  name?: string,               // New ad set name
  status?: string,             // New status (ACTIVE, PAUSED, DELETED)
  bid_amount?: number,         // New bid amount in cents
  daily_budget?: number,       // New daily budget in cents
  lifetime_budget?: number,    // New lifetime budget in cents
  targeting?: object,          // New targeting specification
  optimization_goal?: string,  // New optimization goal
  billing_event?: string       // New billing event
) -> Dict
```

### `delete_adset(adset_id)`
```typescript
delete_adset(
  adset_id: string             // Ad set ID to delete
) -> Dict
```

## 📢 Ad Management (Full CRUD)

### `create_ad(ad_account_id, adset_id, name, creative, options)`
```typescript
create_ad(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  adset_id: string,            // Ad set ID to create ad in
  name: string,                // Ad name
  creative: object,            // Ad creative specification
  status?: string,             // Ad status (ACTIVE, PAUSED) - defaults to PAUSED
  tracking_specs?: object[],   // Tracking specifications
  conversion_specs?: object[]  // Conversion specifications
) -> Dict
```

### `update_ad(ad_id, options)`
```typescript
update_ad(
  ad_id: string,               // Ad ID to update
  name?: string,               // New ad name
  status?: string,             // New status (ACTIVE, PAUSED, DELETED)
  creative?: object,           // New creative specification
  tracking_specs?: object[],   // New tracking specifications
  conversion_specs?: object[]  // New conversion specifications
) -> Dict
```

### `delete_ad(ad_id)`
```typescript
delete_ad(
  ad_id: string                // Ad ID to delete
) -> Dict
```

## 🎨 Creative Management (Full CRUD)

### `create_ad_creative(ad_account_id, name, options)`
```typescript
create_ad_creative(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  name: string,                // Creative name
  object_story_spec?: object,  // Creative content specification
  object_story_id?: string,    // Existing post ID to use
  image_hash?: string,         // Hash of uploaded image
  image_url?: string,          // URL of image to use
  video_id?: string,           // ID of uploaded video
  body?: string,               // Ad text body
  title?: string,              // Ad title
  call_to_action?: object,     // Call to action button specification
  instagram_actor_id?: string, // Instagram account ID
  instagram_permalink_url?: string, // Instagram post URL
  instagram_story_id?: string  // Instagram story ID
) -> Dict
```

### `update_ad_creative(creative_id, options)`
```typescript
update_ad_creative(
  creative_id: string,         // Creative ID to update
  name?: string,               // New creative name
  body?: string,               // New ad text body
  title?: string               // New ad title
) -> Dict
```

### `delete_ad_creative(creative_id)`
```typescript
delete_ad_creative(
  creative_id: string          // Creative ID to delete
) -> Dict
```

## 📱 Instagram-Specific Tools

### `get_instagram_accounts(ad_account_id)`
```typescript
get_instagram_accounts(
  ad_account_id: string        // Ad account ID (with act_ prefix)
) -> Dict
```

### `get_instagram_media(instagram_account_id, fields?)`
```typescript
get_instagram_media(
  instagram_account_id: string, // Instagram account ID
  fields?: string[]            // Fields to retrieve
) -> Dict
```

### `create_instagram_ad_creative(ad_account_id, name, instagram_actor_id, object_story_spec)`
```typescript
create_instagram_ad_creative(
  ad_account_id: string,       // Ad account ID (with act_ prefix)
  name: string,                // Creative name
  instagram_actor_id: string,  // Instagram account ID
  object_story_spec: object    // Instagram-specific content specification
) -> Dict
```

## ⚡ Bulk Operations

### `bulk_update_campaigns(campaign_updates)`
```typescript
bulk_update_campaigns(
  campaign_updates: Array<{
    id: string,                // Campaign ID
    [key: string]: any         // Fields to update
  }>
) -> Dict
```

### `bulk_update_adsets(adset_updates)`
```typescript
bulk_update_adsets(
  adset_updates: Array<{
    id: string,                // Ad set ID
    [key: string]: any         // Fields to update
  }>
) -> Dict
```

### `bulk_update_ads(ad_updates)`
```typescript
bulk_update_ads(
  ad_updates: Array<{
    id: string,                // Ad ID
    [key: string]: any         // Fields to update
  }>
) -> Dict
```

## 📈 Analytics & Insights

### `get_adaccount_insights(ad_account_id, options)`
```typescript
get_adaccount_insights(
  ad_account_id: string,       // Ad account ID
  fields?: string[],           // Metrics to retrieve
  date_preset?: string,        // Date range preset
  time_range?: object,         // Custom time range
  time_increment?: string,     // Time grouping
  filtering?: object[],        // Filter conditions
  breakdowns?: string[],       // Data breakdowns
  action_breakdowns?: string[], // Action breakdowns
  level?: string               // Aggregation level
) -> Dict
```

### `get_campaign_insights(campaign_id, options)`
### `get_adset_insights(adset_id, options)`
### `get_ad_insights(ad_id, options)`
Similar parameter structure to `get_adaccount_insights`.

## 📋 Activity Tracking

### `get_activities_by_adaccount(ad_account_id, options)`
```typescript
get_activities_by_adaccount(
  ad_account_id: string,       // Ad account ID
  fields?: string[],           // Fields to retrieve
  since?: string,              // Start date
  until?: string,              // End date
  limit?: number,              // Number of results
  after?: string               // Pagination cursor
) -> Dict
```

## 🏷️ Common Parameters

### Campaign Objectives
- `REACH` - Reach as many people as possible
- `TRAFFIC` - Drive traffic to website/app
- `CONVERSIONS` - Drive conversions
- `APP_INSTALLS` - Increase app installations
- `VIDEO_VIEWS` - Increase video views
- `LEAD_GENERATION` - Generate leads
- `MESSAGES` - Get people to message your business

### Ad Set Optimization Goals
- `REACH` - Maximize reach
- `IMPRESSIONS` - Maximize impressions
- `CLICKS` - Maximize clicks
- `CONVERSIONS` - Maximize conversions
- `VIDEO_VIEWS` - Maximize video views

### Billing Events
- `IMPRESSIONS` - Pay per impression
- `CLICKS` - Pay per click
- `ACTIONS` - Pay per action/conversion

### Status Values
- `ACTIVE` - Running/enabled
- `PAUSED` - Paused/disabled
- `DELETED` - Deleted (soft delete)

## 🎯 Example Usage Scenarios

### Creating a Complete Campaign Structure
```typescript
// 1. Create Campaign
const campaign = await create_campaign(
  "act_123456789", 
  "VividWalls Art Collection Launch",
  "TRAFFIC",
  { daily_budget: 5000 } // $50/day
);

// 2. Create Ad Set
const adset = await create_adset(
  "act_123456789",
  campaign.id,
  "Modern Art Enthusiasts",
  "CLICKS",
  "CLICKS",
  { 
    daily_budget: 2500,
    targeting: {
      geo_locations: { countries: ["US"] },
      interests: [{ id: "6003139266461", name: "Modern art" }]
    }
  }
);

// 3. Create Creative
const creative = await create_ad_creative(
  "act_123456789",
  "Modern Art Showcase",
  {
    object_story_spec: {
      page_id: "page_123",
      link_data: {
        link: "https://vividwalls.com/modern-collection",
        message: "Discover stunning modern art for your space",
        image_hash: "image_hash_123"
      }
    }
  }
);

// 4. Create Ad
const ad = await create_ad(
  "act_123456789",
  adset.id,
  "Modern Art Discovery Ad",
  { creative_id: creative.id }
);
```

### Bulk Campaign Management
```typescript
// Update multiple campaigns at once
const updates = [
  { id: "campaign_1", status: "ACTIVE", daily_budget: 7500 },
  { id: "campaign_2", status: "PAUSED" },
  { id: "campaign_3", daily_budget: 5000 }
];

const result = await bulk_update_campaigns(updates);
```

This comprehensive API provides everything needed to fully automate Facebook and Instagram advertising for VividWalls or any other business through n8n workflows.