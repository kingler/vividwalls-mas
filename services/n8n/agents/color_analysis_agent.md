# VividWalls Color Analysis Agent

## Overview
The VividWalls Color Analysis Agent is a specialized AI-powered system that analyzes artwork images to extract comprehensive color information, psychological attributes, and spatial recommendations for interior design purposes.

## Primary Functions

### 1. **Artwork Color Extraction**
- Analyzes artwork images using OpenAI GPT-4o Vision API
- Extracts dominant colors with precise hex codes and percentages
- Determines color temperature (warm/cool/neutral)
- Identifies color harmony patterns (complementary, analogous, etc.)
- Calculates contrast, saturation, and brightness levels

### 2. **Psychological Profiling**
- Determines primary and secondary moods of artwork
- Analyzes emotional impact and psychological effects
- Identifies atmosphere creation capabilities
- Maps colors to psychological states (calming, energizing, sophisticated, etc.)

### 3. **Spatial Recommendations**
- Recommends suitable room types for artwork placement
- Provides lighting requirements and wall placement suggestions
- Offers room size recommendations
- Identifies rooms to avoid based on color psychology

### 4. **Style Compatibility Analysis**
- Matches artwork to interior design styles
- Provides furniture and textile recommendations
- Suggests complementary accent colors
- Identifies compatible design aesthetics

### 5. **Vector Search Integration**
- Generates embeddings for semantic search using text-embedding-3-small
- Stores analysis results in PostgreSQL with pgvector
- Enables similarity-based artwork recommendations
- Supports color-based search queries

## Workflow Endpoints

### Single Artwork Analysis
- **Endpoint**: `POST /webhook/artwork-color-analysis`
- **Purpose**: Analyze a single artwork image for color attributes
- **Input Format**:
```json
{
  "artworkId": "unique-artwork-id",
  "title": "Artwork Title",
  "collection": "Collection Name",
  "artist": "Artist Name",
  "imageUrl": "https://example.com/artwork.jpg",
  "tags": ["abstract", "modern"],
  "analysisType": "comprehensive"
}
```

### Bulk Artwork Analysis
- **Endpoint**: `POST /webhook/bulk-artwork-analysis`
- **Purpose**: Process multiple artworks in batch
- **Input Format**:
```json
{
  "artworks": [
    {
      "id": "artwork-1",
      "title": "First Artwork",
      "collection": "Collection A",
      "imageUrl": "https://example.com/artwork1.jpg"
    },
    {
      "id": "artwork-2",
      "title": "Second Artwork",
      "collection": "Collection B",
      "imageUrl": "https://example.com/artwork2.jpg"
    }
  ]
}
```

## Response Format

### Successful Analysis Response
```json
{
  "success": true,
  "artwork": {
    "id": "artwork-123",
    "title": "Ocean Serenity",
    "collection": "Coastal Collection"
  },
  "colorAnalysis": {
    "dominantColors": [
      {
        "hex": "#1A5F7A",
        "name": "Deep Ocean Blue",
        "percentage": 35,
        "category": "cool"
      }
    ],
    "colorTemperature": {
      "overall": "cool",
      "warmPercentage": 20,
      "coolPercentage": 80
    },
    "colorHarmony": {
      "type": "complementary",
      "harmonyScore": 0.85
    }
  },
  "psychologicalProfile": {
    "primaryMood": "calming",
    "emotionalImpact": ["promotes relaxation", "reduces stress"],
    "atmosphereType": "serene professional"
  },
  "recommendations": {
    "recommendedRooms": ["office", "bedroom", "study"],
    "styleCompatibility": {
      "primaryStyles": ["modern", "contemporary"]
    }
  },
  "analysisMetadata": {
    "confidenceScore": 0.92,
    "processingTimeMs": 3450
  }
}
```

## Critical Safety Rules

### NO HUMANS OR ANIMALS Policy
The agent is strictly configured to:
- **NEVER** acknowledge or describe humans, animals, or living creatures
- Focus **ONLY** on colors, patterns, shapes, and abstract elements
- Analyze landscapes, objects, and architectural elements without mentioning inhabitants
- Maintain focus on artistic techniques and color composition

## Integration with Color Psychology MCP Server

This agent workflow is designed to work seamlessly with the Color Psychology MCP Server by:
- Using the same database schema and vector embeddings
- Following identical color extraction methodologies
- Maintaining consistent psychological profiling standards
- Sharing the same safety protocols (NO HUMANS OR ANIMALS)

## Usage Guidelines

### For Single Artwork Processing
1. Send artwork data to the single analysis endpoint
2. Wait for comprehensive color analysis (typically 3-5 seconds)
3. Use the returned data for recommendation engines or UI display

### For Bulk Processing
1. Prepare array of artwork objects
2. Send to bulk analysis endpoint
3. Monitor completion rate in response
4. Handle any failed analyses separately

### For Integration with Other Systems
- Use the vector embeddings for similarity search
- Query the PostgreSQL database directly for stored analyses
- Combine with room analysis data for personalized recommendations
- Cross-reference with customer preference data

## Performance Considerations

- Single artwork analysis: 3-5 seconds average
- Bulk processing: Processes items sequentially to avoid rate limits
- OpenAI Vision API: Subject to rate limits (adjust batch size accordingly)
- Database writes: Optimized with UPSERT operations
- Vector generation: Uses efficient text-embedding-3-small model

## Error Handling

The workflow includes comprehensive error handling:
- Validates required fields (especially image URLs)
- Provides fallback analysis on AI parsing errors
- Logs all analysis events for debugging
- Returns detailed error messages for troubleshooting

## Monitoring and Analytics

Track the following metrics:
- Analysis success rate
- Average processing time
- Confidence scores distribution
- Most common color profiles
- Room recommendation patterns

## Future Enhancements

Planned improvements include:
- Real-time analysis status updates via WebSocket
- Caching layer for frequently analyzed artworks
- Multi-language support for color names
- Integration with customer purchase history
- A/B testing for recommendation accuracy 