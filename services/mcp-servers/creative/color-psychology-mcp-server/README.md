# VividWalls Color Psychology MCP Server

An MCP server that analyzes customer room images and recommends artwork based on color composition and psychological analysis using OpenAI GPT-4o Vision API and DALL-E 3 Image Generation API.

## 🚨 CRITICAL CONTENT POLICY: NO HUMANS OR ANIMALS 🚨

### Absolute Rule
**ALL generated composite images MUST be completely devoid of humans, animals, or any living creatures.**

This is a non-negotiable requirement for all image generation operations. The system enforces this through:

1. **Comprehensive Negative Prompts** - Over 20 specific exclusions
2. **Input Validation** - Rejects requests mentioning humans/animals
3. **Post-Generation Checks** - Verifies safety phrases are included
4. **Multiple Safety Layers** - Redundant checks at every stage

### Why This Rule Exists
- **Privacy Protection**: Ensures customer privacy is never compromised
- **Brand Consistency**: VividWalls showcases artwork, not people
- **Legal Compliance**: Avoids any potential likeness or privacy issues
- **Professional Focus**: Keeps attention on the artwork and interior design

### Implementation Details

The `image_processing/generation_config.py` module contains:

```python
# Critical negative prompts always included:
- NO humans whatsoever
- NO people at all
- NO animals of any kind
- NO pets whatsoever
- NO living creatures
- ABSOLUTELY empty of life
- COMPLETELY uninhabited
```

## Features

- **Room Analysis**: Extracts color palettes and identifies optimal wall placement
- **Artwork Analysis**: Analyzes VividWalls artwork for color composition and mood
- **Smart Recommendations**: Suggests artwork based on color harmony and psychological compatibility
- **Composite Generation**: Creates realistic room visualizations with artwork (NO HUMANS/ANIMALS)
- **Color Theory Search**: Vector database of color psychology knowledge

## Installation

```bash
# Clone the repository
git clone [repository-url]

# Navigate to the server directory
cd services/mcp-servers/creative/color-psychology-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Environment Variables

```env
# Required
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

## Usage

### Starting the Server

```bash
# Run the MCP server
python server.py
```

### Available MCP Tools

#### 1. `analyze_room`
Analyzes customer room images, excluding any humans or animals from the analysis.

```python
result = analyze_room("path/to/room.jpg")
# Returns: color_palette, objects (furniture only), wall_analysis
```

#### 2. `analyze_artwork`
Analyzes VividWalls artwork for color and psychological attributes.

```python
result = analyze_artwork("vw_abstract_001")
# Returns: color_composition, mood_attributes, psychological_impact
```

#### 3. `recommend_artwork`
Generates artwork recommendations based on room analysis.

```python
recommendations = recommend_artwork(room_analysis, num_recommendations=3)
# Returns: List of recommendations with scores and rationale
```

#### 4. `generate_composite_image`
**⚠️ CRITICAL: Generates room visualization with NO HUMANS OR ANIMALS**

```python
result = generate_composite_image(
    room_image_path="room.jpg",
    artwork_id="vw_001",
    wall_position={...}
)
# Returns: Composite image path (guaranteed no living beings)
```

## Testing

Run the test suite to verify all safety checks are working:

```bash
# Run all tests
python -m pytest

# Run specific safety tests
python -m pytest tests/test_generation_safety.py -v
```

## Safety Checklist for Developers

Before ANY image generation:

- [ ] Verify request contains no human/animal references
- [ ] Confirm negative prompts are included in generation config
- [ ] Test with sample prompts to ensure no living beings appear
- [ ] Review generated images before showing to customers
- [ ] Document any edge cases or concerns

## Architecture

```
color-psychology-mcp-server/
├── image_processing/
│   ├── generation_config.py  # NO HUMANS/ANIMALS enforcement
│   ├── vision_api.py         # OpenAI Vision integration
│   └── color_extractor.py    # Color analysis
├── artwork_analysis/
│   └── analyzer.py           # Artwork attribute extraction
├── recommendation/
│   ├── color_harmony.py      # Color matching algorithms
│   └── psychological.py      # Mood/space compatibility
├── data/
│   └── vector_db.py          # pgvector integration
└── server.py                 # FastMCP server
```

## Contributing

When contributing to this project:

1. **NEVER** remove or weaken the NO HUMANS/ANIMALS rules
2. Test all image generation code thoroughly
3. Add safety checks to any new generation features
4. Update documentation if adding new safety measures

## License

[License information]

---

**Remember: The NO HUMANS OR ANIMALS rule is paramount. When in doubt, err on the side of safety.** 