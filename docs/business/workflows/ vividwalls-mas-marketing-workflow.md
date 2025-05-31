# VIVIDWALLS MARKETING AUTOMATION WORKFLOW

## 1. WORKFLOW OVERVIEW

**Primary objective:** Automate creation, review, and publication of daily social-media campaigns that promote VividWalls art.

**Executive summary:** This workflow orchestrates a complete marketing automation pipeline that researches trending art topics, generates platform-specific content featuring VividWalls products, creates visual assets, obtains human approval, and publishes across multiple social channels. The system operates on a daily schedule, ensuring consistent brand presence while maintaining quality through AI-powered content generation and human oversight.

**Key benefits / expected outcomes:**
- 85% reduction in manual content creation time
- Consistent daily posting across 4+ platforms
- Data-driven topic selection based on trending searches
- Brand-aligned messaging with product integration
- Quality control through approval gates

**Target users & use-cases:**
- VividWalls marketing team for daily campaign automation
- Social media managers requiring consistent content flow
- E-commerce brands needing product-focused social presence
- Teams balancing automation with human oversight

## 2. DETAILED WORKFLOW STRUCTURE

### STEP 1: DAILY TRIGGER & INITIALIZATION

**A. Step Overview**
- Step name: Campaign Initialization & Context Setup
- Purpose: Trigger daily workflow and establish campaign parameters
- Key deliverables: Campaign ID, execution context, date parameters
- Dependencies: None (entry point)
- Required nodes: Cron, Set, Function, Date & Time

**B. Sub-steps:**

1. **Cron Trigger Activation**
   - Actions: Fire workflow at 9:00 AM EST daily
   - Inputs: Cron expression `0 9 * * *`
   - Outputs: Trigger timestamp
   - Error handling: Missed execution catch-up
   - Complexity: Low (5 min)

2. **Generate Campaign UUID**
   - Actions: Create unique campaign identifier
   - Inputs: Current timestamp
   - Outputs: `campaignId` (UUID v4)
   - Error handling: Collision check
   - Complexity: Low (2 min)

3. **Set Date Parameters**
   - Actions: Calculate posting windows for each platform
   - Inputs: Current date/time
   - Outputs: `postSchedule` object with platform timings
   - Error handling: Timezone validation
   - Complexity: Medium (10 min)

4. **Load Brand Guidelines**
   - Actions: Fetch VividWalls brand voice, colors, hashtags
   - Inputs: Supabase query to `brandAssets` table
   - Outputs: `brandContext` object
   - Error handling: Fallback to cached values
   - Complexity: Low (5 min)

5. **Initialize Campaign Context**
   - Actions: Create master context object
   - Inputs: Campaign ID, brand guidelines, schedule
   - Outputs: `campaignContext` JSON
   - Error handling: Schema validation
   - Complexity: Medium (15 min)

6. **Check Previous Campaign Status**
   - Actions: Query last campaign completion
   - Inputs: Supabase `campaigns` table
   - Outputs: `lastCampaignStatus`
   - Error handling: Handle first run
   - Complexity: Low (5 min)

7. **Set Execution Flags**
   - Actions: Configure workflow behavior flags
   - Inputs: Environment variables
   - Outputs: `executionFlags` (testMode, platforms)
   - Error handling: Default to production
   - Complexity: Low (3 min)

8. **Log Initialization**
   - Actions: Write campaign start to logs
   - Inputs: Campaign context
   - Outputs: Log entry ID
   - Error handling: Async write
   - Complexity: Low (2 min)

### STEP 2: TREND RESEARCH & TOPIC SELECTION

**A. Step Overview**
- Step name: Market Intelligence Gathering
- Purpose: Identify trending art topics and competitor content
- Key deliverables: Ranked topic list, competitor insights
- Dependencies: Tavily API, Google Trends API
- Required nodes: HTTP Request, Function, Aggregate, Sort

**B. Sub-steps:**

1. **Tavily Trend Search**
   - Actions: Query trending abstract art topics
   - Inputs: Search query "trending abstract art 2024"
   - Outputs: `trendingTopics` array
   - Error handling: API timeout (30s), retry 3x
   - Complexity: Medium (20 min)

2. **Google Trends Analysis**
   - Actions: Fetch search volume data
   - Inputs: Top 10 topics from Tavily
   - Outputs: `searchVolumes` with trend scores
   - Error handling: Rate limit backoff
   - Complexity: Medium (15 min)

3. **Competitor Content Scan**
   - Actions: Crawl competitor social posts
   - Inputs: Competitor handle list
   - Outputs: `competitorPosts` last 7 days
   - Error handling: Access denied graceful skip
   - Complexity: High (30 min)

4. **Topic Relevance Scoring**
   - Actions: Score topics against VividWalls catalog
   - Inputs: Topics + product database
   - Outputs: `scoredTopics` with relevance %
   - Error handling: Fuzzy matching fallback
   - Complexity: Medium (20 min)

5. **Hashtag Research**
   - Actions: Extract trending hashtags per topic
   - Inputs: Instagram/Pinterest APIs
   - Outputs: `hashtagClusters` by topic
   - Error handling: API quota management
   - Complexity: Medium (15 min)

6. **Topic Selection Algorithm**
   - Actions: Apply weighted scoring formula
   - Inputs: All research data
   - Outputs: `selectedTopic` + alternatives
   - Error handling: Manual override option
   - Complexity: High (25 min)

7. **Market Context Assembly**
   - Actions: Compile research into context
   - Inputs: All research outputs
   - Outputs: `marketContext` object
   - Error handling: Required field validation
   - Complexity: Low (10 min)

8. **Cache Research Results**
   - Actions: Store in Redis with 6h TTL
   - Inputs: Market context
   - Outputs: Cache key
   - Error handling: Write-through on failure
   - Complexity: Low (5 min)

### STEP 3: CONTENT GENERATION & ADAPTATION

**A. Step Overview**
- Step name: AI-Powered Content Creation
- Purpose: Generate platform-specific copy and creative briefs
- Key deliverables: Platform-optimized content, visual descriptions
- Dependencies: OpenAI GPT-4, Claude 3, Google Gemini 2.5
- Required nodes: OpenAI, Function, Split in Batches, Merge

**B. Sub-steps:**

1. **Master Narrative Creation**
   - Actions: Generate core campaign story
   - Inputs: Topic, brand voice, product focus
   - Outputs: `masterNarrative` (500 words)
   - Error handling: Token limit validation
   - Complexity: High (30 min)

2. **Instagram Content Adaptation**
   - Actions: Create carousel copy + captions
   - Inputs: Master narrative, IG requirements
   - Outputs: `igContent` object
   - Error handling: Character limit enforcement
   - Complexity: Medium (20 min)

3. **Pinterest Pin Description**
   - Actions: SEO-optimized pin descriptions
   - Inputs: Master narrative, keywords
   - Outputs: `pinContent` with rich pins data
   - Error handling: Keyword density check
   - Complexity: Medium (15 min)

4. **Facebook Post Creation**
   - Actions: Engaging post with CTA
   - Inputs: Master narrative, FB best practices
   - Outputs: `fbContent` with link preview
   - Error handling: Link validation
   - Complexity: Medium (15 min)

5. **Twitter/X Thread Composition**
   - Actions: Break into tweet thread
   - Inputs: Master narrative
   - Outputs: `twitterThread` array
   - Error handling: Thread length limits
   - Complexity: Medium (20 min)

6. **Visual Brief Generation**
   - Actions: Describe required visuals
   - Inputs: Content + product imagery
   - Outputs: `visualBriefs` per platform
   - Error handling: Aspect ratio validation
   - Complexity: High (25 min)

7. **Hashtag Optimization**
   - Actions: Platform-specific hashtag sets
   - Inputs: Research + platform limits
   - Outputs: `optimizedHashtags`
   - Error handling: Banned hashtag filter
   - Complexity: Low (10 min)

8. **Content Quality Scoring**
   - Actions: AI self-evaluation
   - Inputs: All generated content
   - Outputs: `qualityScores` + revision flags
   - Error handling: Minimum score threshold
   - Complexity: Medium (15 min)

### STEP 4: VISUAL ASSET CREATION

**A. Step Overview**
- Step name: Dynamic Visual Generation
- Purpose: Create platform-optimized images featuring products
- Key deliverables: Sized images, product mockups, overlays
- Dependencies: DALL-E 3, Canva API, Sharp.js
- Required nodes: OpenAI Image, HTTP Request, Function, Binary

**B. Sub-steps:**

1. **Product Selection Logic**
   - Actions: Choose featured products
   - Inputs: Topic relevance, inventory
   - Outputs: `featuredProducts` array
   - Error handling: Stock verification
   - Complexity: Medium (15 min)

2. **Base Image Generation**
   - Actions: Create with DALL-E 3
   - Inputs: Visual briefs
   - Outputs: `baseImages` (4 variants)
   - Error handling: NSFW filter retry
   - Complexity: High (45 min)

3. **Product Overlay Compositing**
   - Actions: Add product shots to base
   - Inputs: Base images + product PNGs
   - Outputs: `compositedImages`
   - Error handling: Alpha channel issues
   - Complexity: High (30 min)

4. **Platform-Specific Sizing**
   - Actions: Resize for each platform
   - Inputs: Master composites
   - Outputs: `sizedAssets` object
   - Error handling: Quality preservation
   - Complexity: Medium (20 min)

5. **Text Overlay Addition**
   - Actions: Add titles, CTAs, prices
   - Inputs: Sized images + copy
   - Outputs: `finalAssets`
   - Error handling: Readability checks
   - Complexity: Medium (25 min)

6. **Color Harmony Adjustment**
   - Actions: Ensure brand color presence
   - Inputs: Final assets
   - Outputs: `colorCorrectedAssets`
   - Error handling: Color space issues
   - Complexity: Medium (20 min)

7. **Asset Optimization**
   - Actions: Compress without quality loss
   - Inputs: Color corrected assets
   - Outputs: `optimizedAssets`
   - Error handling: Size limit compliance
   - Complexity: Low (10 min)

8. **Upload to Media Store**
   - Actions: Save to Supabase storage
   - Inputs: All optimized assets
   - Outputs: `assetUrls` + metadata
   - Error handling: Upload retry logic
   - Complexity: Low (10 min)

### STEP 5: QUALITY REVIEW & APPROVAL

**A. Step Overview**
- Step name: Human-in-the-Loop Validation
- Purpose: Ensure quality before publication
- Key deliverables: Approval status, revision requests
- Dependencies: Telegram Bot API, Web UI
- Required nodes: Telegram, Wait, IF, Function

**B. Sub-steps:**

1. **Preview Package Assembly**
   - Actions: Compile all content/visuals
   - Inputs: Generated assets + copy
   - Outputs: `previewPackage`
   - Error handling: Missing asset flags
   - Complexity: Low (10 min)

2. **Telegram Preview Send**
   - Actions: Send to approval channel
   - Inputs: Preview package
   - Outputs: Message IDs
   - Error handling: Chunked sending
   - Complexity: Medium (15 min)

3. **Approval UI Generation**
   - Actions: Create web preview link
   - Inputs: Campaign assets
   - Outputs: `approvalUrl`
   - Error handling: Expiry handling
   - Complexity: Medium (20 min)

4. **Wait for Response**
   - Actions: Poll for approval (2h timeout)
   - Inputs: Message IDs
   - Outputs: `approvalDecision`
   - Error handling: Timeout escalation
   - Complexity: Low (5 min)

5. **Revision Request Parsing**
   - Actions: Extract feedback if rejected
   - Inputs: Rejection message
   - Outputs: `revisionRequests`
   - Error handling: Unstructured text parsing
   - Complexity: Medium (15 min)

6. **Automated Revision Attempt**
   - Actions: Apply AI fixes if possible
   - Inputs: Revision requests
   - Outputs: `revisedContent`
   - Error handling: Complex revision flag
   - Complexity: High (30 min)

7. **Final Approval Check**
   - Actions: Confirm all changes
   - Inputs: Revised content
   - Outputs: `finalApproval` boolean
   - Error handling: Force approval option
   - Complexity: Low (5 min)

8. **Approval Logging**
   - Actions: Record decision + feedback
   - Inputs: All approval data
   - Outputs: Audit trail entry
   - Error handling: Async write
   - Complexity: Low (5 min)

### STEP 6: MULTI-PLATFORM PUBLISHING

**A. Step Overview**
- Step name: Orchestrated Social Distribution
- Purpose: Publish approved content across all platforms
- Key deliverables: Published post IDs, engagement URLs
- Dependencies: Platform APIs (Meta, Pinterest, Twitter)
- Required nodes: HTTP Request, Parallel, Error Workflow

**B. Sub-steps:**

1. **Publishing Queue Setup**
   - Actions: Order platforms by priority
   - Inputs: Platform schedule
   - Outputs: `publishQueue`
   - Error handling: Platform availability
   - Complexity: Low (5 min)

2. **Instagram Media Container**
   - Actions: Create IG media objects
   - Inputs: Assets + captions
   - Outputs: `igMediaIds`
   - Error handling: Asset upload retry
   - Complexity: Medium (20 min)

3. **Pinterest Pin Creation**
   - Actions: Publish pins to boards
   - Inputs: Pin content + boards
   - Outputs: `pinIds`
   - Error handling: Board permission check
   - Complexity: Medium (15 min)

4. **Facebook Page Post**
   - Actions: Publish with scheduling
   - Inputs: FB content + timing
   - Outputs: `fbPostId`
   - Error handling: Page token refresh
   - Complexity: Medium (15 min)

5. **Twitter Thread Post**
   - Actions: Sequential tweet posting
   - Inputs: Thread array
   - Outputs: `tweetIds`
   - Error handling: Rate limit pause
   - Complexity: Medium (20 min)

6. **Cross-Platform Linking**
   - Actions: Add platform links to posts
   - Inputs: All post IDs
   - Outputs: Updated posts
   - Error handling: Edit permission check
   - Complexity: Medium (15 min)

7. **Publication Verification**
   - Actions: Confirm all posts live
   - Inputs: Post IDs
   - Outputs: `publicationStatus`
   - Error handling: Retry failed platforms
   - Complexity: Low (10 min)

8. **Share Analytics Setup**
   - Actions: Initialize tracking pixels
   - Inputs: Post URLs
   - Outputs: `trackingData`
   - Error handling: Pixel load verification
   - Complexity: Low (10 min)

### STEP 7: PERFORMANCE MONITORING

**A. Step Overview**
- Step name: Real-Time Engagement Tracking
- Purpose: Monitor early performance indicators
- Key deliverables: Engagement metrics, performance alerts
- Dependencies: Platform Analytics APIs
- Required nodes: Cron, HTTP Request, Aggregate, IF

**B. Sub-steps:**

1. **Initial Metrics Pull**
   - Actions: Fetch 1-hour metrics
   - Inputs: Published post IDs
   - Outputs: `initialMetrics`
   - Error handling: API availability
   - Complexity: Medium (15 min)

2. **Engagement Rate Calculation**
   - Actions: Compute platform ERs
   - Inputs: Metrics + follower counts
   - Outputs: `engagementRates`
   - Error handling: Division by zero
   - Complexity: Low (10 min)

3. **Anomaly Detection**
   - Actions: Compare to baselines
   - Inputs: Current + historical data
   - Outputs: `anomalyFlags`
   - Error handling: Insufficient data
   - Complexity: Medium (20 min)

4. **Competitor Benchmarking**
   - Actions: Compare performance
   - Inputs: Competitor metrics
   - Outputs: `benchmarkScores`
   - Error handling: Private account skip
   - Complexity: Medium (15 min)

5. **Alert Threshold Check**
   - Actions: Evaluate alert rules
   - Inputs: All metrics
   - Outputs: `alertTriggers`
   - Error handling: Rule validation
   - Complexity: Low (10 min)

6. **Performance Report Generation**
   - Actions: Create summary report
   - Inputs: All analytics
   - Outputs: `performanceReport`
   - Error handling: Template errors
   - Complexity: Medium (15 min)

7. **Slack/Email Notifications**
   - Actions: Send alerts if needed
   - Inputs: Alert triggers
   - Outputs: Notification receipts
   - Error handling: Channel availability
   - Complexity: Low (5 min)

8. **Metrics Storage**
   - Actions: Write to time-series DB
   - Inputs: All metrics
   - Outputs: Storage confirmation
   - Error handling: Batch write retry
   - Complexity: Low (10 min)

### STEP 8: CAMPAIGN WRAP-UP & LEARNING

**A. Step Overview**
- Step name: Analysis & Optimization Loop
- Purpose: Extract learnings and optimize future campaigns
- Key deliverables: Performance insights, model updates
- Dependencies: BigQuery, ML Pipeline
- Required nodes: Function, BigQuery, Set, Email

**B. Sub-steps:**

1. **24-Hour Metrics Collection**
   - Actions: Final metrics pull
   - Inputs: All platform APIs
   - Outputs: `completeMetrics`
   - Error handling: Partial data handling
   - Complexity: Medium (20 min)

2. **ROI Calculation**
   - Actions: Attribute sales to posts
   - Inputs: UTM parameters + sales
   - Outputs: `campaignROI`
   - Error handling: Attribution window
   - Complexity: High (30 min)

3. **Content Performance Analysis**
   - Actions: Identify winning elements
   - Inputs: Metrics + content
   - Outputs: `performanceInsights`
   - Error handling: Statistical significance
   - Complexity: High (25 min)

4. **Audience Insight Extraction**
   - Actions: Analyze engagement patterns
   - Inputs: User interactions
   - Outputs: `audienceInsights`
   - Error handling: Privacy compliance
   - Complexity: Medium (20 min)

5. **Model Performance Feedback**
   - Actions: Update AI prompts
   - Inputs: Performance data
   - Outputs: `modelUpdates`
   - Error handling: Validation testing
   - Complexity: High (30 min)

6. **Executive Summary Creation**
   - Actions: Generate C-suite report
   - Inputs: All insights
   - Outputs: `executiveSummary`
   - Error handling: Data visualization
   - Complexity: Medium (20 min)

7. **Knowledge Base Update**
   - Actions: Store learnings
   - Inputs: Insights + context
   - Outputs: KB entries
   - Error handling: Duplicate detection
   - Complexity: Low (10 min)

8. **Next Campaign Seeds**
   - Actions: Generate topic ideas
   - Inputs: Performance winners
   - Outputs: `nextCampaignIdeas`
   - Error handling: Diversity check
   - Complexity: Medium (15 min)

## 3. TECHNICAL SPECIFICATIONS

**Full list of n8n nodes required:**
- Cron (Daily trigger)
- HTTP Request (API calls)
- Set (Variable management)
- Function (Custom logic)
- Merge (Data combination)
- IF (Conditional branching)
- Split In Batches (Parallel processing)
- Wait (Approval delays)
- Telegram (Notifications)
- Email Send (Reports)
- Postgres (Data storage)
- Redis (Caching)
- Error Workflow (Error handling)
- Webhook (External triggers)

**External integrations & APIs:**
- Tavily Search & Crawl API
- OpenAI GPT-4 & DALL-E 3
- Anthropic Claude 3
- Google Gemini 2.5 Flash
- Meta Graph API (Instagram/Facebook)
- Pinterest API v5
- Twitter API v2
- YouTube Data API v3
- Supabase (Media storage + DB)
- Redis Cloud (Caching)
- Telegram Bot API
- Google Analytics 4
- Stripe API (Sales attribution)

**Variables / data structures:**
```javascript
campaignContext = {
  campaignId: "uuid-v4",
  brandGuidelines: {},
  schedule: {},
  status: "initializing"
}

audienceProfile = {
  demographics: {},
  interests: [],
  behaviorPatterns: {},
  engagementHistory: []
}

assetBucket = {
  images: [],
  copy: {},
  hashtags: {},
  urls: {}
}

postQueue = [
  {platform: "instagram", priority: 1, content: {}},
  {platform: "pinterest", priority: 2, content: {}}
]
```

**Authentication requirements:**
- OAuth2: Meta, Google, Pinterest, Twitter
- API Keys: OpenAI, Anthropic, Tavily
- Bearer Tokens: Supabase, Telegram
- Service Accounts: Google Cloud

## 4. WORKFLOW LOGIC & FLOW

**Decision points & IF branches:**
- Content length validation (IF > platform limits)
- Asset generation success (IF all assets created)
- Approval status (IF approved/rejected/timeout)
- Platform availability (IF API healthy)
- Performance thresholds (IF engagement < baseline)

**Data transformation steps:**
- JSON to Form-Data (Meta media upload)
- Base64 to Binary (Image processing)
- CSV to JSON (Analytics export)
- Markdown to HTML (Email reports)

**Loop structures:**
- Platform posting loop (ForEach platform in queue)
- Revision iteration (While not approved, max 3)
- Metric polling (Every 15min for 24h)

**Node connections diagram:**
```
[Cron] → [Initialize] → [Research] → [Generate] 
                                          ↓
[Monitor] ← [Publish] ← [Approve] ← [Create Assets]
    ↓
[Analyze] → [Report] → [Optimize] → [Complete]
```

## 5. IMPLEMENTATION DETAILS

**Example payloads:**

Tavily Search Query:
```json
{
  "query": "trending abstract art styles 2024",
  "search_depth": "advanced",
  "max_results": 20,
  "include_images": true,
  "include_domains": ["behance.net", "artsy.net"]
}
```

Meta Media Container:
```json
{
  "image_url": "https://cdn.vividwalls.com/campaign/abc123.jpg",
  "caption": "Transform your space with 'Cosmic Dreams'...",
  "access_token": "{{$credentials.metaAccessToken}}",
  "media_type": "IMAGE"
}
```

Telegram Approval Message:
```json
{
  "chat_id": "-1001234567890",
  "text": "🎨 Campaign Ready for Review",
  "reply_markup": {
    "inline_keyboard": [[
      {"text": "✅ Approve", "callback_data": "approve_abc123"},
      {"text": "❌ Reject", "callback_data": "reject_abc123"}
    ]]
  }
}
```

**Sample expressions:**
```javascript
// Dynamic hashtag generation
$json.hashtags.slice(0, 30).map(tag => `#${tag}`).join(' ')

// ROI calculation
(($json.sales - $json.adSpend) / $json.adSpend * 100).toFixed(2)

// Platform-specific scheduling
DateTime.now().plus({hours: $json.platform === 'instagram' ? 2 : 4})
```

**Error handling & retry:**
- Exponential backoff: 1s, 2s, 4s (max 3 attempts)
- Circuit breaker for API failures
- Dead letter queue for failed posts
- Graceful degradation (skip platform if down)

**Performance optimizations:**
- Cache Tavily results for 6 hours
- Parallel platform posting (4 concurrent)
- Lazy load large images
- Batch API requests where possible

## 6. QUALITY ASSURANCE

**Potential bottlenecks:**
- AI model API rate limits (queue/throttle)
- Image generation time (pre-generate variants)
- Approval wait time (set reasonable timeout)
- Platform API quotas (monitor usage)

**Monitoring & logging:**
- n8n Execution Log (all node executions)
- Supabase `marketingLogs` table schema:
  ```sql
  CREATE TABLE marketingLogs (
    id SERIAL PRIMARY KEY,
    campaign_id UUID,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- CloudWatch metrics for API latency
- Sentry for error tracking

**Troubleshooting guide:**
1. Research timeout → Check Tavily API status
2. Image generation fails → Verify DALL-E quota
3. Platform post fails → Refresh OAuth tokens
4. Low engagement → Review time zone settings

**Validation checkpoints:**
- Post-research: Topic relevance > 70%
- Post-generation: Quality score > 8/10
- Pre-publish: Human approval required
- Post-publish: Verify all platforms succeeded

## 7. BEST PRACTICES & VARIATIONS

**Optimization tips:**
- Respect rate limits (Meta: 200/hour)
- Use cost-effective models (Gemini for summaries)
- Pre-warm caches during off-hours
- A/B test posting times monthly

**Alternative approaches:**
- Manual topic seed: Skip research, input topic directly
- Batch generation: Create week's content at once
- Platform-first: Generate unique content per platform
- Influencer mode: Mimic top performer styles

**Scalability notes:**
- Add TikTok agent (when API available)
- Multi-brand support (config switching)
- Language localization (translate content)
- Regional targeting (geo-specific campaigns)

**Maintenance recommendations:**
- Rotate API keys quarterly
- Update platform best practices monthly  
- Retrain AI models with performance data
- Archive campaigns older than 6 months

## 8. OUTPUT FORMAT

```json
{
  "name": "VividWalls Daily Marketing Automation",
  "nodes": [
    {
      "id": "cron_daily_trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {"interval": [{"field": "hours", "triggerAtHour": 9}]}
      }
    },
    {
      "id": "initialize_campaign",
      "type": "n8n-nodes-base.function",
      "position": [450, 300],
      "parameters": {
        "functionCode": "const campaignId = require('uuid').v4();\nreturn [{json: {campaignId, timestamp: new Date()}}];"
      }
    }
  ],
  "connections": {
    "cron_daily_trigger": {
      "main": [[{"node": "initialize_campaign", "type": "main", "index": 0}]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

This comprehensive workflow specification provides VividWalls with a production-ready marketing automation system that balances AI efficiency with human oversight, ensuring consistent, high-quality social media presence while maintaining brand integrity and driving measurable business results.