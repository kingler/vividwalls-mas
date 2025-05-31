# VividWalls AI Art Selection & Visualization Workflow

## **N8N Workflow Architecture: AI Agent-Based Art Recommendation System**

This workflow implements a sophisticated AI agent system using the Seven Node Blueprint for selecting and visualizing artwork in customer spaces. The system processes user inputs (text descriptions and/or room images) to recommend the top 3 artwork options with comprehensive visualizations, powered by advanced color psychology and interior design expertise.

## **Workflow Overview**

### **Core Agent Components (Following Seven Node Blueprint)**

1. **LLM Agent Node** - Central reasoning and decision-making with VividWalls AI expertise
2. **Tool Nodes** - Database retrieval and image generation tools
3. **Control Nodes** - Flow routing and deterministic logic
4. **Memory Nodes** - Session and long-term preference storage
5. **Guardrail Nodes** - Input/output validation and scoring
6. **Fallback Nodes** - Error handling and graceful degradation
7. **User Input Nodes** - Space type selection and approval workflows

## **VividWalls AI Agent System Integration**

### **Core AI Agent Identity**
All LLM agents in this workflow embody the **VividWalls AI** persona with expertise in:
- **Color Psychology & Theory**: Scientific understanding of color emotional impact
- **Art Analysis**: Comprehensive visual analysis of artwork and spaces
- **Interior Design**: Space planning and art placement optimization
- **Product Expertise**: Complete VividWalls catalog knowledge

### **Color Psychology Framework**
The AI agents utilize advanced color psychology:

**Warm Colors:**
- **Red**: Energy, passion, urgency, power, love, danger
- **Orange**: Enthusiasm, creativity, warmth, confidence, playfulness  
- **Yellow**: Happiness, optimism, intellect, energy, caution

**Cool Colors:**
- **Blue**: Trust, calm, stability, professionalism, sadness, cold
- **Green**: Nature, growth, harmony, freshness, money, envy
- **Purple**: Luxury, creativity, mystery, spirituality, royalty

**Neutral Colors:**
- **Black**: Elegance, sophistication, mystery, power, death
- **White**: Purity, cleanliness, simplicity, peace, sterility
- **Gray**: Balance, neutrality, sophistication, depression
- **Brown**: Earthiness, stability, reliability, warmth, dullness

### **Mood Classifications System**
1. **Energizing**: Bright, saturated colors that stimulate and invigorate
2. **Calming**: Soft, muted tones that soothe and relax
3. **Sophisticated**: Rich, deep colors that convey elegance and refinement
4. **Playful**: Vibrant, contrasting colors that evoke joy and creativity
5. **Mysterious**: Dark, complex colors that intrigue and captivate
6. **Natural**: Earth tones and organic colors that ground and center
7. **Romantic**: Soft pastels and warm tones that inspire love and tenderness
8. **Dramatic**: High contrast combinations that create impact and tension

## **Detailed Workflow Implementation**

### **Phase 1: Input Processing & Validation**

#### **Node 1: Webhook Trigger**
```json
{
  "node_type": "webhook",
  "endpoint": "/webhook/vividwalls-copilot",
  "method": "POST",
  "expected_payload": {
    "user_prompt": "string (optional)",
    "room_image": "base64_string (optional)", 
    "space_type": "string (bedroom|bathroom|kitchen|livingroom|hotel_room|lobby|shared_spaces|executive_office|restaurant|hospital)",
    "client_type": "string (residential|commercial)",
    "session_id": "string",
    "user_preferences": "object (optional)"
  }
}
```

#### **Node 2: Input Guardrail & Validation**
```javascript
// Control Node - Input Validation
const validateInput = (input) => {
  const validation = {
    hasPrompt: !!input.user_prompt,
    hasImage: !!input.room_image,
    hasSpaceType: !!input.space_type,
    isValidSpaceType: ['bedroom', 'bathroom', 'kitchen', 'livingroom', 
                      'hotel_room', 'lobby', 'shared_spaces', 'executive_office', 
                      'restaurant', 'hospital'].includes(input.space_type),
    inputType: input.hasImage && input.hasPrompt ? 'image_text' : 
               input.hasImage ? 'image_only' : 
               input.hasPrompt ? 'text_only' : 'invalid'
  };
  
  if (validation.inputType === 'invalid') {
    throw new Error('Must provide either text prompt, image, or both');
  }
  
  return validation;
};
```

#### **Node 3: Memory Retrieval**
```javascript
// Memory Node - Retrieve user preferences and session history
const retrieveMemory = async (sessionId) => {
  // Retrieve from vector database or session storage
  const userPreferences = await vectorDB.query({
    collection: 'user_preferences',
    filter: { session_id: sessionId },
    limit: 10
  });
  
  const conversationHistory = await sessionStorage.get(sessionId);
  
  return {
    preferences: userPreferences,
    history: conversationHistory,
    previousSelections: userPreferences.map(p => p.artwork_ids).flat()
  };
};
```

### **Phase 2: Image Analysis & Context Understanding**

#### **Node 4: LLM Agent - VividWalls AI Image Analysis**
```json
{
  "node_type": "llm_agent",
  "model": "gpt-4-vision-preview",
  "system_prompt": "You are VividWalls AI, an expert art consultant and interior design specialist with deep knowledge in color psychology, art analysis, and interior design. You have comprehensive understanding of how colors affect human emotions and behavior.",
  "tools": ["image_analyzer", "space_classifier", "color_extractor"],
  "conditional_execution": "input.hasImage === true"
}
```

**Enhanced LLM Prompt for Image Analysis:**
```
You are VividWalls AI, analyzing this room image with your expertise in color psychology and interior design.

COMPREHENSIVE ROOM ANALYSIS CHECKLIST:

SPATIAL ANALYSIS:
- Room dimensions (estimated): width x height x depth
- Wall identification: which walls are visible (front, back, left, right)
- Available wall space for artwork
- Ceiling height category (low: <8ft, standard: 8-10ft, high: >10ft)
- Viewing distances and sight lines

COLOR PSYCHOLOGY ANALYSIS:
Using your expertise in color theory, identify:
- Primary colors (3 dominant with hex codes) and their psychological impact
- Secondary colors (2-3 accents) and emotional associations
- Overall color temperature (warm/cool/neutral) and mood implications
- Color harmony type (complementary, analogous, triadic, monochromatic)
- Lighting conditions and how they affect color perception

STYLE & MOOD ASSESSMENT:
- Design style (modern, traditional, minimalist, industrial, etc.)
- Current mood classification (energizing, calming, sophisticated, playful, mysterious, natural, romantic, dramatic)
- Furniture style and materials
- Existing artwork or decorative elements
- Overall aesthetic coherence

PSYCHOLOGICAL IMPACT EVALUATION:
- Current emotional atmosphere of the space
- Stress/relaxation indicators in color choices
- Energy levels conveyed by the palette
- Focus/distraction elements
- Cultural considerations in color usage

ARTWORK PLACEMENT OPTIMIZATION:
- Optimal zones for art placement
- Scale recommendations based on wall space
- Lighting considerations for artwork
- Visual flow and focal point opportunities
- Complementary vs contrasting color strategies

OUTPUT REQUIREMENTS:
Provide structured JSON with:
- Detailed color analysis with psychological insights
- Mood classification and enhancement opportunities
- Specific artwork placement recommendations
- Color harmony suggestions for art selection
- Confidence scores for each assessment (1-10)

Format as comprehensive JSON for database querying and art selection.
```

#### **Node 5: LLM Agent - VividWalls AI Text Analysis**
```json
{
  "node_type": "llm_agent", 
  "model": "gpt-4",
  "system_prompt": "You are VividWalls AI, expert in color psychology and interior design. Extract artwork preferences from user descriptions using your deep understanding of color emotional impact and space psychology.",
  "conditional_execution": "input.hasPrompt === true"
}
```

**Enhanced LLM Prompt for Text Analysis:**
```
You are VividWalls AI, analyzing this user request with your expertise in color psychology and interior design.

USER REQUEST: {{user_prompt}}
SPACE TYPE: {{space_type}}
CLIENT TYPE: {{client_type}}

COMPREHENSIVE PREFERENCE EXTRACTION:

COLOR PSYCHOLOGY ANALYSIS:
- Explicit color preferences mentioned
- Implied color preferences from mood descriptions
- Color temperature preferences (warm/cool/neutral)
- Psychological goals (energy, calm, sophistication, etc.)
- Color harmony preferences (complementary, analogous, etc.)

MOOD & EMOTIONAL CONTEXT:
Using your mood classification system, identify:
- Desired emotional atmosphere (energizing, calming, sophisticated, playful, mysterious, natural, romantic, dramatic)
- Current mood vs desired mood transformation
- Psychological benefits sought (stress reduction, energy enhancement, focus improvement, creativity stimulation)
- Target audience considerations (personal, guests, clients, patients)

STYLE PREFERENCES:
- Art styles mentioned or implied
- Design aesthetic alignment
- Cultural considerations
- Professional vs personal space requirements

FUNCTIONAL REQUIREMENTS:
- Space constraints and sizing needs
- Viewing distance considerations
- Lighting environment
- Existing decor integration needs
- Budget or timeline constraints

PSYCHOLOGICAL INSIGHTS:
- Underlying emotional needs
- Lifestyle alignment
- Personality expression goals
- Behavioral influence objectives

OUTPUT REQUIREMENTS:
- Confidence score for each extracted preference (1-10)
- Priority ranking of requirements
- Suggested mood classifications
- Color psychology recommendations
- Potential style conflicts to avoid
- Personalization opportunities

Format as structured JSON optimized for artwork database querying.
```

### **Phase 3: Database Retrieval & Artwork Selection**

#### **Node 6: Tool Node - VividWalls Database Query Orchestrator**
```javascript
// Tool Node - Coordinates multiple database queries using VividWalls AI insights
const queryArtworkDatabase = async (analysisResults) => {
  const queries = [];
  
  // Color Psychology-based queries
  if (analysisResults.colors) {
    queries.push({
      tool: 'get_image_by_color',
      params: {
        primary_colors: analysisResults.colors.primary,
        secondary_colors: analysisResults.colors.secondary,
        color_harmony: analysisResults.colors.harmony_type,
        psychological_impact: analysisResults.colors.emotional_associations,
        mood_enhancement: analysisResults.mood.target_mood
      }
    });
  }
  
  // Mood-based queries using VividWalls classification
  if (analysisResults.mood) {
    queries.push({
      tool: 'get_image_by_mood',
      params: {
        current_mood: analysisResults.mood.current,
        target_mood: analysisResults.mood.target,
        mood_classification: analysisResults.mood.category, // energizing, calming, sophisticated, etc.
        psychological_goals: analysisResults.mood.psychological_benefits,
        emotional_transformation: analysisResults.mood.transformation_type
      }
    });
  }
  
  // Size-based queries with psychological considerations
  if (analysisResults.spatial) {
    queries.push({
      tool: 'get_image_by_size',
      params: {
        wall_width: analysisResults.spatial.available_width,
        wall_height: analysisResults.spatial.available_height,
        viewing_distance: analysisResults.spatial.viewing_distance,
        space_type: analysisResults.space_type,
        psychological_scale: analysisResults.spatial.psychological_impact // intimate, grand, balanced
      }
    });
  }
  
  return queries;
};
```

#### **Node 7-9: Enhanced MCP Tool Nodes - Database Retrieval**

**Tool Node 7: get_image_by_color (Enhanced)**
```json
{
  "node_type": "mcp_tool",
  "tool_name": "get_image_by_color",
  "parameters": {
    "primary_colors": "array of hex codes",
    "secondary_colors": "array of hex codes", 
    "color_harmony": "complementary|analogous|triadic|monochromatic|split_complementary",
    "psychological_impact": "array of emotional associations",
    "mood_enhancement": "energizing|calming|sophisticated|playful|mysterious|natural|romantic|dramatic",
    "limit": 20
  },
  "output": "array of artwork objects with color_psychology_score and emotional_impact_rating"
}
```

**Tool Node 8: get_image_by_mood (Enhanced)**
```json
{
  "node_type": "mcp_tool",
  "tool_name": "get_image_by_mood",
  "parameters": {
    "current_mood": "string",
    "target_mood": "string", 
    "mood_classification": "energizing|calming|sophisticated|playful|mysterious|natural|romantic|dramatic",
    "psychological_goals": "array of psychological benefits",
    "emotional_transformation": "enhance|balance|contrast|complement",
    "limit": 20
  },
  "output": "array of artwork objects with mood_alignment_score and psychological_benefit_rating"
}
```

**Tool Node 9: get_image_by_size (Enhanced)**
```json
{
  "node_type": "mcp_tool",
  "tool_name": "get_image_by_size",
  "parameters": {
    "wall_width": "number (inches)",
    "wall_height": "number (inches)",
    "viewing_distance": "number (feet)",
    "space_type": "string",
    "psychological_scale": "intimate|balanced|grand",
    "limit": 20
  },
  "output": "array of artwork objects with size_optimization_score and spatial_harmony_rating"
}
```

### **Phase 4: AI-Powered Scoring & Selection**

#### **Node 10: LLM Agent - VividWalls AI Artwork Scoring & Selection**
```json
{
  "node_type": "llm_agent",
  "model": "gpt-4",
  "system_prompt": "You are VividWalls AI, expert art curator and interior designer. Use your comprehensive knowledge of color psychology, mood classification, and interior design to score and select artwork that will enhance the user's space both aesthetically and psychologically.",
  "tools": ["artwork_scorer", "selection_optimizer", "color_harmony_analyzer"]
}
```

**Enhanced LLM Prompt for VividWalls AI Scoring:**
```
You are VividWalls AI, using your expertise in color psychology and interior design to score and select the top 3 artwork options.

INPUT DATA:
- Original user request: {{user_prompt}}
- Room analysis: {{room_analysis}}
- Space type: {{space_type}}
- Retrieved artworks: {{artwork_candidates}}
- User's psychological goals: {{psychological_goals}}

VIVIDWALLS AI SCORING CRITERIA (1-10 scale):

1. COLOR PSYCHOLOGY HARMONY (30%): 
   - How well artwork colors enhance the desired emotional atmosphere
   - Alignment with color psychology principles
   - Emotional impact and mood enhancement potential

2. MOOD TRANSFORMATION EFFECTIVENESS (25%):
   - Ability to achieve target mood classification
   - Psychological benefit delivery
   - Emotional atmosphere enhancement

3. STYLE & AESTHETIC ALIGNMENT (20%):
   - Match with room's design style and user preferences
   - Visual coherence and artistic merit
   - Cultural and personal relevance

4. SPATIAL OPTIMIZATION (15%):
   - Optimal sizing for wall space and viewing distance
   - Visual flow and focal point creation
   - Spatial harmony and proportion

5. FUNCTIONAL SUITABILITY (10%):
   - Appropriate for space type and daily usage
   - Lighting compatibility
   - Maintenance and longevity considerations

VIVIDWALLS AI SELECTION PROCESS:
1. Apply color psychology expertise to evaluate emotional impact
2. Assess mood transformation potential using classification system
3. Calculate weighted composite scores with psychological insights
4. Ensure diversity in final selection (different moods/styles)
5. Provide detailed psychological rationale for each selection
6. Consider long-term satisfaction and emotional well-being

OUTPUT FORMAT:
```json
{
  "selections": [
    {
      "artwork_id": "string",
      "rank": 1,
      "total_score": 8.7,
      "score_breakdown": {
        "color_psychology_harmony": 9.2,
        "mood_transformation": 8.8,
        "style_alignment": 8.5,
        "spatial_optimization": 8.1,
        "functional_suitability": 8.9
      },
      "psychological_analysis": {
        "emotional_impact": "Enhances calm and focus through cool blue tones",
        "mood_classification": "calming",
        "color_psychology_benefits": ["stress reduction", "mental clarity", "peaceful atmosphere"],
        "target_audience_fit": "Perfect for professionals seeking tranquil workspace"
      },
      "selection_rationale": "This artwork leverages the psychological power of blue to create a calming, focused environment. The soft gradients will reduce visual stress while the abstract composition stimulates creativity without distraction.",
      "placement_optimization": "Position at eye level, 60 inches from floor, with soft LED backlighting to enhance the calming blue tones",
      "key_strengths": ["Superior color psychology alignment", "Proven mood enhancement", "Optimal spatial integration"]
    }
  ]
}
```

#### **Node 11: Tool Node - get_image_by_id (Batch Retrieval)**
```json
{
  "node_type": "mcp_tool",
  "tool_name": "get_image_by_id",
  "parameters": {
    "artwork_ids": "array of selected artwork IDs",
    "include_metadata": true,
    "include_high_res": true,
    "include_psychology_data": true
  },
  "output": "array of complete artwork objects with full metadata and color psychology analysis"
}
```

### **Phase 5: Image Generation & Visualization**

#### **Node 12: Control Node - VividWalls AI Image Generation Orchestrator**
```javascript
// Control Node - Manages parallel image generation with VividWalls AI expertise
const orchestrateImageGeneration = (selectedArtworks, spaceType, roomAnalysis) => {
  const generationTasks = [];
  
  selectedArtworks.forEach((artwork, index) => {
    // Task 1: Standalone image (professional product photography)
    generationTasks.push({
      type: 'standalone',
      artwork_id: artwork.id,
      prompt: `Create a high-quality professional product photograph of "${artwork.title}" artwork. Very light gray background (#F8F8F8), centered composition, soft even lighting, no shadows on background. Professional art gallery photography style, crisp details, accurate color representation.`,
      rank: index + 1
    });
    
    // Task 2: Wall placement with psychological considerations
    generationTasks.push({
      type: 'wall_placement',
      artwork_id: artwork.id,
      prompt: `Show "${artwork.title}" artwork hanging on a wall in a ${spaceType}. ${roomAnalysis ? `Room style: ${roomAnalysis.style}. Wall color: ${roomAnalysis.wall_color}. Lighting: ${roomAnalysis.lighting}.` : 'Modern, well-lit space.'} Position at optimal viewing height (60 inches center). Realistic perspective, proper scale, professional interior photography. Emphasize how the artwork enhances the room's ${artwork.psychological_analysis.mood_classification} atmosphere.`,
      rank: index + 1
    });
    
    // Task 3: Alternative space with mood enhancement focus
    generationTasks.push({
      type: 'alternative_space',
      artwork_id: artwork.id,
      prompt: `Display "${artwork.title}" artwork in a ${getAlternativeSpace(spaceType)} setting that showcases its ${artwork.psychological_analysis.mood_classification} qualities. High-end interior design, optimal lighting to enhance the artwork's color psychology benefits: ${artwork.psychological_analysis.color_psychology_benefits.join(', ')}. Realistic scale and perspective, professional photography.`,
      rank: index + 1
    });
  });
  
  return generationTasks;
};

const getAlternativeSpace = (originalSpace) => {
  const alternatives = {
    'bedroom': 'living room',
    'livingroom': 'bedroom', 
    'kitchen': 'dining room',
    'bathroom': 'bedroom',
    'hotel_room': 'hotel lobby',
    'lobby': 'executive office',
    'executive_office': 'conference room',
    'restaurant': 'hotel lobby',
    'hospital': 'waiting area'
  };
  return alternatives[originalSpace] || 'modern living space';
};
```

#### **Node 13-15: Tool Nodes - Enhanced Image Generation**
```json
{
  "node_type": "image_generation_tool",
  "model": "dall-e-3",
  "parallel_execution": true,
  "batch_size": 9,
  "parameters": {
    "size": "1024x1024",
    "quality": "hd",
    "style": "natural"
  },
  "enhancement_settings": {
    "color_accuracy": "high",
    "lighting_optimization": "true",
    "psychological_mood_enhancement": "true"
  }
}
```

### **Phase 6: Output Validation & Formatting**

#### **Node 16: Guardrail Node - VividWalls AI Output Validation**
```javascript
// Guardrail Node - Validate using VividWalls AI standards
const validateOutput = (generatedImages, selections) => {
  const validation = {
    all_images_generated: generatedImages.length === 9, // 3 artworks × 3 images each
    scores_valid: selections.every(s => s.total_score >= 1 && s.total_score <= 10),
    images_accessible: generatedImages.every(img => img.url && img.status === 'success'),
    proper_grouping: generatedImages.filter(img => img.type === 'standalone').length === 3,
    psychological_analysis_complete: selections.every(s => s.psychological_analysis && s.psychological_analysis.mood_classification),
    color_psychology_included: selections.every(s => s.psychological_analysis.color_psychology_benefits.length > 0)
  };
  
  if (!validation.all_images_generated) {
    throw new Error('Image generation incomplete - retry required');
  }
  
  if (!validation.psychological_analysis_complete) {
    throw new Error('Psychological analysis incomplete - VividWalls AI standards not met');
  }
  
  return validation;
};
```

#### **Node 17: LLM Agent - VividWalls AI Response Formatting**
```json
{
  "node_type": "llm_agent",
  "model": "gpt-4",
  "system_prompt": "You are VividWalls AI, formatting the final response with your expertise in color psychology and interior design. Create engaging, educational responses that explain the psychological benefits of each recommendation."
}
```

**Enhanced LLM Prompt for VividWalls AI Response Formatting:**
```
You are VividWalls AI, presenting artwork recommendations with your expertise in color psychology and interior design.

INPUT DATA:
- Selected artworks with psychological analysis: {{selections}}
- Generated images: {{generated_images}}
- Original request: {{user_prompt}}
- Room analysis: {{room_analysis}}

FORMAT AS VIVIDWALLS AI EXPERT RESPONSE:

# 🎨 Your Perfect Artwork Matches

As your VividWalls AI art consultant, I've analyzed your {{space_type}} using color psychology and interior design principles. Here are my top 3 recommendations that will enhance both the beauty and emotional atmosphere of your space:

## 🥇 Option 1: [Artwork Title] (Score: X.X/10)

**🧠 Color Psychology Insight:**
[Explain the psychological impact of the artwork's colors using VividWalls AI expertise]

**💫 Why this transforms your space:**
[Personalized explanation based on mood classification and psychological analysis]

**🎯 Emotional Benefits:**
- **[Primary Benefit]**: [Specific color psychology explanation]
- **[Secondary Benefit]**: [Mood enhancement details]
- **[Tertiary Benefit]**: [Spatial psychology impact]

**📐 Optimal Placement:**
[Specific placement instructions with psychological reasoning]

**🖼️ Visualizations:**
1. **Product View:** [standalone_image_url] - *See the artwork's true colors and details*
2. **In Your {{space_type}}:** [wall_placement_image_url] - *Experience how it enhances your space*
3. **Alternative Setting:** [alternative_space_image_url] - *Discover its versatility*

**🛒 Investment in Your Well-being:** [Shopify CTA Button: "Transform Your Space - $XXX"]

---

## 🥈 Option 2: [Repeat enhanced format with different psychological insights]

## 🥉 Option 3: [Repeat enhanced format with different psychological insights]

---

**🏠 Want to see these in a different room?** 
[Space selector component with psychological benefits for each space type]

**🤔 Questions about color psychology or placement?** 
I'm here to help you create a space that not only looks beautiful but also supports your emotional well-being and daily goals.

**💡 VividWalls AI Tip:** 
[Include a relevant color psychology fact or interior design insight]
```

### **Phase 7: Memory Storage & Session Management**

#### **Node 18: Memory Node - VividWalls AI Interaction Storage**
```javascript
// Memory Node - Store interaction with VividWalls AI insights
const storeMemory = async (sessionId, interaction) => {
  const memoryData = {
    session_id: sessionId,
    timestamp: new Date().toISOString(),
    user_input: interaction.original_request,
    space_type: interaction.space_type,
    selected_artworks: interaction.final_selections,
    psychological_profile: {
      color_preferences: interaction.color_psychology_analysis,
      mood_goals: interaction.mood_classification,
      style_preferences: interaction.style_analysis,
      emotional_needs: interaction.psychological_goals
    },
    vividwalls_ai_insights: {
      color_harmony_analysis: interaction.color_harmony,
      mood_transformation_potential: interaction.mood_enhancement,
      psychological_benefits_delivered: interaction.psychological_benefits
    },
    interaction_type: interaction.input_type,
    satisfaction_indicators: {
      engagement_time: interaction.session_duration,
      selections_viewed: interaction.selections_viewed,
      cta_clicked: interaction.cta_clicked,
      psychological_resonance: interaction.emotional_response
    }
  };
  
  // Store in vector database for future personalization
  await vectorDB.upsert({
    collection: 'vividwalls_user_profiles',
    data: memoryData,
    embedding: await generateEmbedding(memoryData.user_input + ' ' + memoryData.psychological_profile)
  });
  
  // Update session storage
  await sessionStorage.update(sessionId, memoryData);
};
```

#### **Node 19: Fallback Node - VividWalls AI Error Handling**
```javascript
// Fallback Node - Handle errors with VividWalls AI expertise
const handleErrors = (error, context) => {
  const vividwallsAIFallbacks = {
    'image_generation_failed': {
      message: "I'm having trouble generating visualizations right now, but as your VividWalls AI consultant, I can still provide detailed color psychology analysis and placement recommendations for these artworks.",
      action: "provide_detailed_psychological_analysis"
    },
    'database_query_failed': {
      message: "Let me use my VividWalls AI expertise to manually curate recommendations based on color psychology principles for your space.",
      action: "fallback_to_psychology_based_recommendations"
    },
    'scoring_failed': {
      message: "I'll apply my color psychology knowledge to recommend our most psychologically beneficial pieces for your space type.",
      action: "show_psychology_optimized_artworks"
    }
  };
  
  const fallback = vividwallsAIFallbacks[error.type] || {
    message: "I'm experiencing some technical difficulties, but I'd love to connect you with our human art consultants who share my passion for color psychology and interior design.",
    action: "escalate_to_human_expert"
  };
  
  // Log error with VividWalls AI context
  console.error(`VividWalls AI Workflow error: ${error.type}`, { context, error });
  
  return fallback;
};
```

## **Enhanced MCP Tool Definitions**

### **VividWalls AI Database Retrieval Tools**

```typescript
// Enhanced MCP Tool: get_image_by_color
interface GetImageByColorParams {
  primary_colors: string[];              // Hex color codes
  secondary_colors?: string[];           // Optional accent colors
  color_harmony: 'complementary' | 'analogous' | 'triadic' | 'monochromatic' | 'split_complementary';
  psychological_impact: string[];        // Emotional associations
  mood_enhancement: 'energizing' | 'calming' | 'sophisticated' | 'playful' | 'mysterious' | 'natural' | 'romantic' | 'dramatic';
  limit?: number;                       // Default: 20
}

// Enhanced MCP Tool: get_image_by_mood
interface GetImageByMoodParams {
  current_mood: string;                 // Current space mood
  target_mood: string;                  // Desired mood transformation
  mood_classification: 'energizing' | 'calming' | 'sophisticated' | 'playful' | 'mysterious' | 'natural' | 'romantic' | 'dramatic';
  psychological_goals: string[];        // Desired psychological benefits
  emotional_transformation: 'enhance' | 'balance' | 'contrast' | 'complement';
  limit?: number;                      // Default: 20
}

// Enhanced MCP Tool: get_image_by_size
interface GetImageBySizeParams {
  wall_width: number;                  // Available wall width in inches
  wall_height: number;                 // Available wall height in inches
  viewing_distance: number;            // Viewing distance in feet
  space_type: string;                 // Room/space category
  psychological_scale: 'intimate' | 'balanced' | 'grand';
  limit?: number;                     // Default: 20
}

// Enhanced MCP Tool: get_image_by_id
interface GetImageByIdParams {
  artwork_ids: string[];              // Array of artwork IDs
  include_metadata: boolean;          // Include full artwork details
  include_high_res: boolean;          // Include high-resolution images
  include_psychology_data: boolean;   // Include color psychology analysis
}
```

## **VividWalls AI Workflow Configuration**

### **Environment Variables**
```bash
# AI Model Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL_TEXT=gpt-4
OPENAI_MODEL_VISION=gpt-4-vision-preview
OPENAI_MODEL_IMAGE=dall-e-3

# VividWalls AI Configuration
VIVIDWALLS_AI_EXPERTISE_LEVEL=expert
COLOR_PSYCHOLOGY_DATABASE_URL=your_psychology_db_url
MOOD_CLASSIFICATION_MODEL=vividwalls_ai_v2

# Database Configuration
ARTWORK_DATABASE_URL=your_database_url
VECTOR_DATABASE_URL=your_vector_db_url

# Memory Configuration
SESSION_STORAGE_TYPE=redis
SESSION_TIMEOUT=3600
PSYCHOLOGICAL_PROFILE_RETENTION=30_days

# Image Generation Configuration
IMAGE_GENERATION_TIMEOUT=60
MAX_PARALLEL_GENERATIONS=9
IMAGE_QUALITY=hd
COLOR_ACCURACY_MODE=high
```

### **VividWalls AI Workflow Execution Flow**
```
Webhook → Input Validation → Memory Retrieval → 
VividWalls AI Image Analysis (if image) → VividWalls AI Text Analysis (if text) → 
Color Psychology Database Queries (parallel) → VividWalls AI Scoring & Selection → 
Psychological Image Generation (parallel) → VividWalls AI Output Validation → 
Expert Response Formatting → Memory Storage with Psychological Profile → Response
```

### **VividWalls AI Success Metrics**
- **Psychological Accuracy**: Color psychology predictions vs user satisfaction
- **Mood Transformation**: Before/after emotional state assessments
- **Expert Credibility**: User trust in VividWalls AI recommendations
- **Educational Value**: User learning about color psychology
- **Long-term Satisfaction**: Follow-up surveys on space enjoyment

This comprehensive workflow integrates the full VividWalls AI expertise, ensuring every recommendation is grounded in color psychology science and interior design best practices, delivering not just beautiful art but meaningful emotional and psychological benefits to users' spaces.