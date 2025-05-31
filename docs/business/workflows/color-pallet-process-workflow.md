# Instructions

## VividWalls Color Palette Agent - MCP Server Requirements

### Overview

Create an MCP server using FastMCP for the VividWalls Color Palette Agent. This agent will analyze customer-uploaded room images and recommend artwork based on color composition and psychological analysis.

### Core Functionality

#### 1. Image Processing Pipeline

**Input:** Customer-uploaded room/space images

**Processing Steps:**

- **Object Detection**: Identify all objects and subjects in the image
- **Subject Removal**: Remove humans and animals from the final output
- **Spatial Analysis**: 
  - Map furniture placement and relationships
  - Identify all wall surfaces
  - Determine optimal wall for artwork placement
- **Color Extraction**:
  - Extract color palette from the entire space
  - Generate hex color codes for each identified item
  - Output results as HTML/CSS grid format

#### 2. Artwork Analysis System
**Pre-processing Requirements:**
- Analyze each VividWalls artwork for:
  - Color composition
  - Mood and tone attributes
  - Psychological impact of colors
  - Emotional response indicators

**Data Structure:**
- Create a comprehensive data table mapping:
  - Color combinations → Psychological effects
  - Color attributes → Human emotional responses
  - Mood/tone classifications for recommendation engine

#### 3. Recommendation Engine

**Process Flow:**

1. Analyze customer's room image
2. Match room color palette with artwork attributes
3. Consider psychological compatibility
4. Generate recommendations based on color harmony and emotional impact

#### 4. Output Generation
**Final Deliverable:**
- Recreated room image showing:
  - Original space composition
  - Recommended VividWalls artwork
  - Artwork positioned (hanging or leaning) on identified wall
- Color palette visualization with hex codes
- List of room items with associated colors

### Data Sources
- **Product Catalog**: `@products_export.csv` (contains image URLs and SKUs)
- **Classification Workflow**: `@VividWalls-Product-Classification-Workflow.md`
- **System Prompt**: `@VIVIDWALLS_AI_SYSTEM_PROMPT.md`

### Technical Implementation
- **Framework**: FastMCP for server creation
- **Integration**: Color Palette Agent as primary processor
- **Database**: Store color-psychology mapping table for recommendations