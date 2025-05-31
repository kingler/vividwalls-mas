# VividWalls Prompt Chain Implementation Guide

## Overview

The VividWalls prompt chain system implements a sophisticated two-step AI workflow with bifurcated processing paths for art recommendation. This system transforms user inquiries into precise database searches and then intelligently selects the most relevant artworks through multiple specialized workflows.

## System Architecture

### Core Workflow: Prompt Chain with Bifurcation

```
User Inquiry → Parameter Extraction → Database Retrieval → Artwork Selection → Workflow Bifurcation → Response Aggregation
```

### Key Components

1. **Prompt Chain Step 1**: AI-powered search parameter extraction
2. **Database Integration**: Multi-criteria PostgreSQL queries
3. **Prompt Chain Step 2**: AI-powered artwork selection
4. **Workflow Bifurcation**: Dynamic branching based on confidence levels
5. **Response Aggregation**: Comprehensive result compilation

## Workflow Details

### 1. User Inquiry Processing

**Webhook Endpoint**: `https://n8n.vividwalls.blog/webhook/prompt-chain-retrieval`

**Input Format**:
```json
{
  "inquiry": "I need calming artwork for my home office",
  "roomType": "home office",
  "stylePreference": "modern",
  "colorPreferences": ["blue", "gray"],
  "moodPreference": "calming",
  "sizeRequirements": "large",
  "sessionId": "session_123",
  "userId": "user_456"
}
```

### 2. Search Parameter Extraction (Chain Step 1)

The first AI prompt analyzes user inquiries and extracts structured search parameters:

- **Room Types**: living room, bedroom, office, etc.
- **Style Categories**: modern, traditional, industrial, etc.
- **Color Analysis**: warm, cool, neutral classifications
- **Mood Classifications**: calming, energizing, sophisticated, etc.
- **Collection Mapping**: Maps to VividWalls collections
- **Size Preferences**: small, medium, large specifications

**Output**: Structured JSON with search parameters and database query strategies.

### 3. Database Retrieval System

#### Multi-Query Approach

The system executes four parallel database searches:

1. **Vector Similarity Search**: Semantic matching using embeddings
2. **Tag-Based Search**: Matches against product tags
3. **Category & Collection Search**: Filters by collections and room types
4. **Color-Based Search**: Matches color preferences

#### Database Schema Integration

```sql
-- Core tables used:
- products (id, handle, title, collection, published)
- product_analysis (primary_mood, dominant_colors, recommended_rooms)
- product_images (cdn_url, is_primary)
- product_variants (price, frame_size)
- product_embeddings (embedding, embedding_type)
- product_tags (tag_id, confidence_score)
- tags (name)
```

### 4. Artwork Selection (Chain Step 2)

The second AI prompt analyzes all database results and selects 5-8 most relevant artworks using:

- **Relevance Scoring**: Direct match (40%), contextual fit (25%), style harmony (20%), color compatibility (15%)
- **Diversity Considerations**: Style variety, size options, price range
- **Quality Factors**: Search confidence, multi-query validation

### 5. Workflow Bifurcation

Based on selection confidence, the system activates different workflow branches:

#### High Confidence (≥0.8)
- **Detailed Analysis Branch**: Image analysis, color extraction, style analysis
- **Personalization Branch**: User preference learning and customization

#### Lower Confidence (<0.8)
- **Recommendation Engine Branch**: Similar and complementary artwork suggestions
- **Feedback Loop Branch**: User feedback collection and learning

#### Always Active
- **Feedback Loop**: Continuous improvement through user interactions

### 6. Branch Workflows

Each branch calls specialized sub-workflows:

```
Detailed Analysis: https://n8n.vividwalls.blog/webhook/vividwalls-detailed-analysis
Personalization: https://n8n.vividwalls.blog/webhook/vividwalls-personalization
Recommendations: https://n8n.vividwalls.blog/webhook/vividwalls-recommendations
Feedback Loop: https://n8n.vividwalls.blog/webhook/vividwalls-feedback-loop
```

## Implementation Files

### Core Workflows

1. **`n8n/workflows/VividWalls-Prompt-Chain-Image-Retrieval.json`**
   - Main prompt chain workflow with bifurcation
   - Handles user inquiry → parameter extraction → database queries → artwork selection → branching

2. **`n8n/workflows/VividWalls-Database-Integration-Workflow.json`**
   - Standalone database integration workflow
   - Comprehensive search and enhancement capabilities

3. **`n8n/workflows/VividWalls-Test-Database-Connection.json`**
   - Simple test workflow for database connectivity verification

### Database Integration

The system integrates with your existing PostgreSQL database containing:
- 1,860 vector embeddings for semantic search
- 553 structured product records
- Comprehensive product analysis data
- Tag-based classification system

## Testing the System

### 1. Database Connection Test

```bash
curl -X POST https://n8n.vividwalls.blog/webhook/test-db-connection \
  -H "Content-Type: application/json"
```

### 2. Basic Prompt Chain Test

```bash
curl -X POST https://n8n.vividwalls.blog/webhook/prompt-chain-retrieval \
  -H "Content-Type: application/json" \
  -d '{
    "inquiry": "I need calming blue artwork for my bedroom",
    "roomType": "bedroom",
    "moodPreference": "calming",
    "colorPreferences": ["blue"],
    "sessionId": "test_session_001"
  }'
```

### 3. Advanced Query Test

```bash
curl -X POST https://n8n.vividwalls.blog/webhook/prompt-chain-retrieval \
  -H "Content-Type: application/json" \
  -d '{
    "inquiry": "Looking for sophisticated geometric art for my modern home office that promotes focus and productivity",
    "roomType": "home office",
    "stylePreference": "modern",
    "moodPreference": "sophisticated",
    "sizeRequirements": "large",
    "userId": "test_user",
    "sessionId": "test_session_002"
  }'
```

## Expected Response Format

```json
{
  "selectedArtworks": [
    {
      "id": "artwork_id",
      "title": "Artwork Title",
      "collection": "Collection Name",
      "relevanceScore": 0.95,
      "selectionReason": "Why this piece was selected",
      "userMatchFactors": ["calming", "blue tones", "bedroom suitable"],
      "recommendedSizes": ["24x36", "36x48"],
      "placementSuggestions": ["above bed", "accent wall"],
      "styleNotes": "Modern minimalist design",
      "colorHarmony": "Cool blue tones create serene atmosphere",
      "moodImpact": "Promotes relaxation and peaceful sleep",
      "priority": "primary"
    }
  ],
  "selectionSummary": {
    "totalCandidates": 12,
    "selectedCount": 6,
    "primaryMatches": 3,
    "alternativeOptions": 2,
    "exploratoryPicks": 1,
    "averageRelevance": 0.87
  },
  "presentationStrategy": {
    "leadRecommendation": "artwork_id",
    "groupingLogic": "Organized by mood and style compatibility",
    "narrativeFlow": "Story connecting the recommendations",
    "nextSteps": ["view_in_room", "save_favorites", "request_consultation"]
  },
  "enhancedAnalysis": null,
  "personalizedRecommendations": null,
  "additionalRecommendations": null,
  "feedbackMechanism": {
    "feedbackSetup": "User feedback collection configured"
  },
  "metrics": {
    "totalProcessingTime": 2500,
    "activeBranches": ["detailedAnalysisBranch", "feedbackBranch"],
    "searchResultsCount": 45,
    "finalSelectionCount": 6,
    "overallConfidence": 0.92
  },
  "nextSteps": {
    "primaryAction": "view_selected_artworks",
    "secondaryActions": ["request_more_info", "refine_search", "save_favorites"],
    "feedbackOptions": ["like", "dislike", "need_different_style", "need_different_size"],
    "continuationPaths": ["similar_artworks", "different_collections", "room_specific_search"]
  },
  "timestamp": "2025-02-23T12:00:00.000Z",
  "status": "complete"
}
```

## Key Features

### 1. Intelligent Parameter Extraction
- Natural language processing of user inquiries
- Automatic mapping to database search parameters
- Context-aware interpretation of room and style preferences

### 2. Multi-Criteria Database Search
- Vector similarity for semantic matching
- Tag-based filtering for precise categorization
- Collection and room-type filtering
- Color-based matching

### 3. AI-Powered Selection
- Sophisticated relevance scoring
- Diversity balancing
- User experience optimization
- Detailed reasoning for each selection

### 4. Dynamic Workflow Branching
- Confidence-based branch activation
- Specialized processing paths
- Parallel workflow execution
- Comprehensive response aggregation

### 5. Continuous Learning
- User feedback integration
- Preference learning
- Performance optimization
- Recommendation refinement

## Integration with Open WebUI

To connect this system with your Open WebUI chat interface:

1. **Configure Webhook Integration**: Set up Open WebUI to call the prompt chain webhook
2. **Response Processing**: Parse the JSON response to display artwork recommendations
3. **User Interaction**: Implement feedback mechanisms for continuous learning
4. **Session Management**: Maintain user sessions for personalized experiences

## Performance Considerations

- **Processing Time**: Typically 2-5 seconds for complete workflow
- **Database Load**: Optimized queries with proper indexing
- **AI Processing**: Parallel execution where possible
- **Caching**: Consider implementing response caching for common queries

## Next Steps

1. **Test Database Connection**: Verify PostgreSQL connectivity
2. **Deploy Workflows**: Import all workflow files to n8n
3. **Configure Credentials**: Set up database and API credentials
4. **Test Prompt Chain**: Execute test queries to verify functionality
5. **Integrate with Frontend**: Connect to Open WebUI or other interfaces
6. **Monitor Performance**: Track response times and accuracy
7. **Implement Feedback**: Set up user feedback collection and learning

This implementation provides a robust, scalable foundation for intelligent art recommendation with sophisticated AI-powered analysis and dynamic workflow processing. 