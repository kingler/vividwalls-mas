# Pinterest MCP Server

A Model Context Protocol (MCP) server that provides Pinterest marketing automation tools for the VividWalls art print business. This server enables programmatic access to Pinterest API v5 for managing pins, boards, analytics, and advertising campaigns.

## Features

This MCP server provides the following Pinterest marketing tools:

### 📌 Pin Management
- **create_pin**: Post new pins to boards with product links and metadata
- **get_pin_metrics**: Track pin performance (impressions, saves, clicks, outbound clicks)
- **search_pins**: Find pins using search queries

### 📋 Board Management  
- **create_board**: Create new themed boards for organizing content
- **get_boards**: Retrieve all user boards with pagination support

### 📊 Analytics & Insights
- **get_pin_metrics**: Detailed analytics for individual pins
- **get_trending_topics**: Market research with trending keywords and topics
- **get_user_profile**: Account information and follower statistics

### 🎯 Advertising
- **create_promoted_pin**: Create Pinterest ads campaigns for promoted pins
- **schedule_pins**: Content calendar management (simulation for approved tools)

### 👤 Account Management
- **get_user_profile**: Retrieve authenticated user's profile and statistics

## Setup

### Prerequisites

- Python 3.10+
- Pinterest Business Account (for advertising features)
- Pinterest Developer Account and API access

### Installation

1. **Clone or download this directory**

2. **(Optional but Recommended) Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your Pinterest API credentials
   ```

### Pinterest API Setup

1. **Create a Pinterest Developer Account:**
   - Visit [Pinterest Developers](https://developers.pinterest.com/)
   - Sign up for a developer account

2. **Create an App:**
   - Go to [Pinterest App Console](https://developers.pinterest.com/apps/)
   - Click "Create app"
   - Fill in your app details

3. **Get Access Token:**
   - In your app dashboard, generate an access token
   - Required scopes: `boards:read`, `boards:write`, `pins:read`, `pins:write`, `ads:read`, `ads:write`

4. **Configure Environment:**
   ```bash
   # In your .env file
   PINTEREST_ACCESS_TOKEN=your_actual_pinterest_access_token
   PINTEREST_BUSINESS_ID=your_business_account_id  # For advertising features
   ```

### Running the Server

#### Method 1: Direct Python
```bash
python server.py --pinterest-token YOUR_TOKEN
```

#### Method 2: Environment Variable
```bash
# Set token in .env file first
python server.py
```

#### Method 3: MCP Client Integration
Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "pinterest": {
      "command": "python",
      "args": ["/path/to/pinterest-mcp-server/server.py", "--pinterest-token", "YOUR_TOKEN"]
    }
  }
}
```

## Usage Examples

### Creating a Pin
```python
# Create a pin for a VividWalls art print
create_pin(
    board_id="123456789",
    title="Abstract Mountain Art Print",
    description="Modern minimalist mountain landscape perfect for home decor. Available as digital download and physical print.",
    image_url="https://vividwalls.com/images/mountain-art.jpg",
    link="https://vividwalls.com/products/mountain-art-print",
    alt_text="Abstract geometric mountain landscape in blue and white tones"
)
```

### Creating a Board
```python
# Create a themed board for art collection
create_board(
    name="Minimalist Art Prints",
    description="Clean, modern art prints perfect for contemporary homes",
    privacy="PUBLIC"
)
```

### Getting Pin Analytics
```python
# Track performance of a specific pin
get_pin_metrics(
    pin_id="987654321",
    start_date="2024-01-01",
    end_date="2024-01-31",
    metric_types=["IMPRESSION", "SAVE", "PIN_CLICK", "OUTBOUND_CLICK"]
)
```

### Creating a Promoted Pin Campaign
```python
# Promote a high-performing pin
create_promoted_pin(
    pin_id="987654321",
    campaign_name="VividWalls Abstract Art Campaign",
    daily_budget_micros=10000000,  # $10.00
    target_audience={
        "age_bucket": ["35-44", "45-54"],
        "gender": ["FEMALE"],
        "geo": {"countries": ["US", "CA"]},
        "interests": ["home_decor", "art", "interior_design"]
    },
    objective="CONVERSIONS"
)
```

### Getting Trending Topics
```python
# Research trending art and decor topics
get_trending_topics(
    region="US",
    limit=20
)
```

## API Reference

### Pin Tools

#### `create_pin(board_id, title, description, image_url, link?, alt_text?, note?)`
Creates a new pin on Pinterest.

**Parameters:**
- `board_id` (string): Target board ID
- `title` (string): Pin title (max 100 characters)
- `description` (string): Pin description (max 800 characters)
- `image_url` (string): URL of image to pin
- `link` (string, optional): Destination URL
- `alt_text` (string, optional): Accessibility text
- `note` (string, optional): Private note

#### `get_pin_metrics(pin_id, start_date?, end_date?, metric_types?)`
Retrieves analytics for a specific pin.

**Parameters:**
- `pin_id` (string): Pin ID to analyze
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)  
- `metric_types` (array, optional): Metrics to retrieve

### Board Tools

#### `create_board(name, description?, privacy?)`
Creates a new Pinterest board.

**Parameters:**
- `name` (string): Board name
- `description` (string, optional): Board description
- `privacy` (string, optional): "PUBLIC", "PROTECTED", or "SECRET"

#### `get_boards(bookmark?, page_size?)`
Retrieves user's boards with pagination.

**Parameters:**
- `bookmark` (string, optional): Pagination cursor
- `page_size` (number, optional): Results per page (default: 25)

### Advertising Tools

#### `create_promoted_pin(pin_id, campaign_name, daily_budget_micros, target_audience, bid_strategy?, objective?)`
Creates a Pinterest ads campaign.

**Parameters:**
- `pin_id` (string): Pin to promote
- `campaign_name` (string): Campaign name
- `daily_budget_micros` (number): Budget in micros (e.g., 5000000 = $5.00)
- `target_audience` (object): Targeting criteria
- `bid_strategy` (string, optional): "AUTOMATIC_BID" or "MAX_BID"
- `objective` (string, optional): "AWARENESS", "CONSIDERATION", or "CONVERSIONS"

### Analytics Tools

#### `get_trending_topics(region?, limit?)`
Gets trending Pinterest topics and keywords.

**Parameters:**
- `region` (string, optional): Country code (default: "US")
- `limit` (number, optional): Number of results (default: 50)

#### `get_user_profile()`
Retrieves authenticated user's profile information.

## VividWalls Business Integration

This MCP server is specifically designed for VividWalls art print business with:

### Optimized Workflows
- **Art Print Promotion**: Automated pin creation with product links
- **Trend Analysis**: Art and home decor trend monitoring
- **Performance Tracking**: ROI analysis for promoted pins
- **Content Planning**: Board organization for different art styles

### Recommended Pinterest Strategy
1. **Create Themed Boards**: Organize by style (minimalist, abstract, botanical, etc.)
2. **Pin Product Variations**: Multiple pins per product with different descriptions
3. **Use Rich Pins**: Include product pricing and availability
4. **Track Performance**: Monitor which art styles perform best
5. **Promote High-Performers**: Use advertising for successful organic pins

### Content Calendar Example
```python
# Schedule pins for new art collection
schedule_pins([
    {
        "board_id": "minimalist_board",
        "title": "Abstract Lines #1",
        "description": "Clean geometric lines perfect for modern spaces",
        "image_url": "https://vividwalls.com/abstract-lines-1.jpg",
        "link": "https://vividwalls.com/products/abstract-lines-1"
    },
    {
        "board_id": "nature_board", 
        "title": "Botanical Print #3",
        "description": "Elegant plant illustration for nature lovers",
        "image_url": "https://vividwalls.com/botanical-3.jpg",
        "link": "https://vividwalls.com/products/botanical-3"
    }
], schedule_interval_hours=4)
```

## Error Handling

The server includes comprehensive error handling:

- **Authentication Errors**: Invalid or expired tokens
- **Rate Limiting**: Automatic retry with exponential backoff
- **API Errors**: Detailed error messages and suggestions
- **Validation**: Input parameter validation

## Limitations

- **Scheduling**: Pin scheduling requires Pinterest approved tools
- **Trends API**: Limited access, fallback to curated art trends provided
- **Rate Limits**: Pinterest API has rate limits (200 requests per hour for most endpoints)
- **Business Features**: Some features require Pinterest Business account

## Support

For issues and questions:
1. Check Pinterest API documentation: https://developers.pinterest.com/docs/
2. Verify your API credentials and permissions
3. Check rate limits and quota usage
4. Review error messages for specific guidance

## License

This project follows the same license as the VividMAS project.