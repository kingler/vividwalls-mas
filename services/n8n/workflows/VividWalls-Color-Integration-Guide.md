# VividWalls Color Analysis Integration Guide

## Overview

This guide explains the complete integration between the VividWalls product CSV, n8n color analysis workflow, PostgreSQL database with pgvector, and the Color Psychology MCP Server. The system processes artwork images to extract color attributes, psychological profiles, and spatial recommendations for AI agents.

## Architecture Flow

```
┌─────────────────────┐
│   CSV Product File  │ (vividwalls-products-cleaned.csv)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python ETL Script  │ (process_vividwalls_artwork.py)
└──────────┬──────────┘
           │ Downloads images & extracts data
           ▼
┌─────────────────────┐
│  n8n Color Analysis │ (VividWalls-Artwork-Color-Analysis.json)
│      Workflow       │
└──────────┬──────────┘
           │ Calls OpenAI Vision API
           ▼
┌─────────────────────┐
│ PostgreSQL Database │
│   with pgvector     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AI Agent Access   │ (Color Palette, Sales, CRM Agents)
└─────────────────────┘
```

## Components

### 1. CSV Data Source
- **File**: `services/n8n/data/shared/vividwalls-products-cleaned.csv`
- **Content**: Product catalog with artwork metadata
- **Key Fields**:
  - `Handle`: Unique artwork identifier
  - `Title`: Artwork name
  - `Collections`: Collection name (e.g., "Chromatic Echoes")
  - `Image Src`: CDN URL for artwork image
  - `Body (HTML)`: Description and tags
  - `Status`: Active/Draft indicator

### 2. Python ETL Script
- **File**: `services/n8n/scripts/process_vividwalls_artwork.py`
- **Functions**:
  - Parses CSV and extracts unique artworks (filtering variants)
  - Downloads images from CDN URLs
  - Sends artwork data to n8n webhook
  - Handles batch processing for efficiency
  - Generates processing reports

**Usage**:
```bash
# Process first 10 artworks
python process_vividwalls_artwork.py --limit 10

# Process all using bulk endpoint
python process_vividwalls_artwork.py --bulk

# Custom CSV path
python process_vividwalls_artwork.py --csv /path/to/csv
```

### 3. n8n Color Analysis Workflow
- **File**: `services/n8n/workflows/VividWalls-Artwork-Color-Analysis.json`
- **Endpoints**:
  - Single: `https://n8n.vividwalls.blog/webhook/artwork-color-analysis`
  - Bulk: `https://n8n.vividwalls.blog/webhook/bulk-artwork-analysis`
- **Process**:
  1. Receives artwork metadata
  2. Calls OpenAI GPT-4o Vision API
  3. Extracts color composition, moods, room recommendations
  4. Generates vector embeddings
  5. Stores in PostgreSQL

### 4. Database Schema

#### Artwork Table
```sql
CREATE TABLE artwork (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    artist VARCHAR,
    collection VARCHAR,
    description TEXT,
    image_url TEXT,
    thumbnail_url TEXT,
    dominant_colors JSONB,
    color_temperature VARCHAR,
    color_harmony JSONB,
    mood_attributes TEXT[],
    recommended_spaces TEXT[],
    style_attributes JSONB,
    color_embedding vector(1536),
    style_embedding vector(1536),
    analysis_status VARCHAR,
    analyzed_at TIMESTAMP,
    analysis_confidence FLOAT,
    tags TEXT[],
    metadata JSONB,
    availability BOOLEAN DEFAULT true,
    price DECIMAL(10, 2)
);
```

#### Analysis Logs Table
```sql
CREATE TABLE analysis_logs (
    id SERIAL PRIMARY KEY,
    artwork_id VARCHAR REFERENCES artwork(id),
    analysis_type VARCHAR,
    analysis_data JSONB,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Color Analysis Output

The workflow generates comprehensive analysis including:

**Color Analysis**:
```json
{
  "dominantColors": [
    {
      "hex": "#1A5F7A",
      "name": "Deep Ocean Blue",
      "percentage": 35,
      "rgb": {"r": 26, "g": 95, "b": 122},
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
    "description": "Strong contrast between blue and orange"
  }
}
```

**Psychological Profile**:
```json
{
  "primaryMood": "calming",
  "secondaryMood": "sophisticated",
  "emotionalImpact": [
    "promotes relaxation",
    "encourages contemplation"
  ],
  "atmosphereType": "serene professional"
}
```

**Spatial Recommendations**:
```json
{
  "recommendedRooms": ["office", "bedroom", "study"],
  "avoidRooms": ["kitchen", "playroom"],
  "lightingRequirements": "works well with natural light",
  "wallPlacement": ["focal wall", "behind desk"]
}
```

## Vector Search Capabilities

The system uses pgvector for semantic search:

1. **Color-Based Search**: Find artworks with similar color palettes
2. **Mood-Based Search**: Match artworks by emotional impact
3. **Style Matching**: Find artworks that complement existing decor
4. **Room Compatibility**: Search by space recommendations

Example query:
```sql
-- Find artworks similar to a color profile
SELECT id, title, 
       color_embedding <-> '[0.1, 0.2, ...]'::vector AS distance
FROM artwork
ORDER BY distance
LIMIT 10;
```

## Agent Integration

AI agents can access this data for various use cases:

### Color Palette Agent
- Analyzes customer room photos
- Matches artwork based on color harmony
- Suggests complementary pieces
- **NO HUMANS/ANIMALS** in generated composites

### Sales Agent
- Recommends artwork based on customer preferences
- Uses mood profiles for personalized suggestions
- Filters by room type and style compatibility

### Customer Relationship Agent
- Tracks customer color preferences over time
- Suggests new collections based on purchase history
- Provides style evolution insights

## Running the Complete Pipeline

1. **Ensure PostgreSQL has pgvector**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Deploy n8n workflow**:
   - Import `VividWalls-Artwork-Color-Analysis.json` in n8n
   - Configure OpenAI API credentials
   - Set PostgreSQL connection

3. **Run ETL script**:
   ```bash
   cd services/n8n/scripts
   python process_vividwalls_artwork.py --limit 5  # Test with 5 artworks
   ```

4. **Verify results**:
   ```sql
   -- Check processed artworks
   SELECT id, title, analysis_status, 
          array_length(mood_attributes, 1) as mood_count
   FROM artwork
   WHERE analysis_status = 'completed';
   ```

## Monitoring & Maintenance

1. **Check processing logs**:
   - `vividwalls_processing.log` for ETL details
   - `analysis_results.json` for color analysis output
   - `processing_report.json` for summary statistics

2. **Database maintenance**:
   ```sql
   -- Analyze vector index performance
   ANALYZE artwork;
   
   -- Check analysis success rate
   SELECT analysis_status, COUNT(*) 
   FROM artwork 
   GROUP BY analysis_status;
   ```

3. **Re-process failed artworks**:
   ```python
   # Extract failed IDs from report and reprocess
   python process_vividwalls_artwork.py --limit 100 --skip-processed
   ```

## Security Considerations

1. **API Keys**: Store in environment variables
2. **Webhook Security**: Implement authentication on n8n endpoints
3. **Rate Limiting**: Respect OpenAI API limits
4. **Data Privacy**: No PII in artwork analysis

## Future Enhancements

1. **Real-time Processing**: Webhook from Shopify for new products
2. **Batch Optimization**: Process multiple images in single API call
3. **Cache Layer**: Redis for frequently accessed color profiles
4. **ML Enhancement**: Train custom color extraction model
5. **Analytics Dashboard**: Visualize color trends across collections

## Troubleshooting

**Issue**: Images fail to download
- Check CDN URL validity
- Verify network connectivity
- Review failed_artwork_ids in report

**Issue**: OpenAI API errors
- Verify API key and credits
- Check image size/format
- Review rate limits

**Issue**: Database connection fails
- Confirm pgvector extension installed
- Check connection string
- Verify network access to database

**Issue**: Vector search not working
- Ensure embeddings are generated (1536 dimensions)
- Check vector column data type
- Rebuild vector indexes if needed

---

This integration provides a robust foundation for VividWalls' AI-powered artwork recommendation system, enabling sophisticated color-based matching and personalized customer experiences. 