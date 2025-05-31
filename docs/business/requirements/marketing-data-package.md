Based on your workflow description, here's the JSON structure that would be passed between the agents:

```json
{
  "trigger_event": "new_collection_release",
  "trigger_details": {
    "collection_name": "Spring 2024 Collection",
    "release_date": "2024-03-01",
    "product_categories": ["dresses", "accessories", "shoes"],
    "target_demographics": ["women 25-45", "urban professionals"]
  },
  "company_name": "VividWalls Studio",
  "reporting_quarter": "Q1 2024",
  "time_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  },
  "data_requests": {
    "facebook_agent": {
      "request_type": "quarterly_metrics",
      "metrics_needed": ["impressions", "engagement", "conversions", "ad_spend", "roas"],
      "content_analysis": true,
      "audience_insights": true
    },
    "instagram_agent": {
      "request_type": "quarterly_metrics",
      "metrics_needed": ["reach", "engagement_rate", "story_views", "reel_performance"],
      "content_analysis": true,
      "audience_insights": true
    },
    "pinterest_agent": {
      "request_type": "quarterly_metrics",
      "metrics_needed": ["impressions", "saves", "clicks", "conversions"],
      "content_analysis": true,
      "audience_insights": true
    },
    "youtube_agent": {
      "request_type": "quarterly_metrics",
      "metrics_needed": ["views", "watch_time", "subscribers", "engagement"],
      "content_analysis": true,
      "audience_insights": true
    }
  },
  "sm_platform": {
    "facebook": {
      "status": "pending_data_retrieval"
    },
    "instagram": {
      "status": "pending_data_retrieval"
    },
    "pinterest": {
      "status": "pending_data_retrieval"
    },
    "youtube": {
      "status": "pending_data_retrieval"
    }
  },
  "report_requirements": {
    "report_type": "quarterly_marketing_strategy",
    "include_competitor_analysis": true,
    "include_campaign_recommendations": true,
    "delivery_format": "markdown",
    "recipient_agents": ["social_media_marketing_agent", "campaign_creation_agent"]
  }
}
```

The workflow would be:

1. **Trigger Event** → Market Research Agent receives notification of new collection release or quarterly report schedule

2. **Market Research Agent** → Sends data requests to individual platform agents:
   ```json
   {
     "agent_id": "facebook_agent",
     "request_id": "MRA-2024-Q1-001",
     "company_name": "Example Fashion Brand",
     "time_period": {
       "start_date": "2024-01-01",
       "end_date": "2024-03-31"
     },
     "metrics_requested": ["impressions", "engagement", "conversions", "ad_spend", "roas"],
     "return_format": "structured_json"
   }
   ```

3. **Platform Agents** → Return data to Market Research Agent:
   ```json
   {
     "platform": "facebook",
     "metrics": {
       "total_impressions": 1250000,
       "total_engagements": 45000,
       "engagement_rate": 3.6,
       "conversions": 850,
       "ad_spend": 12500,
       "roas": 4.2
     },
     "content": {
       "top_performing": [...],
       "content_types": {...}
     },
     "audience": {
       "demographics": {...},
       "interests": [...]
     }
   }
   ```

4. **Market Research Agent** → Compiles and sends final report to Social Media Marketing Agent with populated `sm_platform` data for campaign creation.