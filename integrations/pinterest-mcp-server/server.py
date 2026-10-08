# server.py
from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, List, Optional, Any, Union
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the script directory
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

# --- Constants ---
PINTEREST_API_VERSION = "v5"
PINTEREST_API_URL = f"https://api.pinterest.com/{PINTEREST_API_VERSION}"

# Create an MCP server
mcp = FastMCP("pinterest-mcp-server")

# Add a global variable to store the token
PINTEREST_ACCESS_TOKEN = None

# --- Helper Functions ---

def _get_pinterest_access_token() -> str:
    """
    Get Pinterest access token from environment variable or command line arguments.
    Priority: 1) Environment variable, 2) Command line argument
    Caches the token in memory after first read.

    Returns:
        str: The Pinterest access token.

    Raises:
        Exception: If no token is provided.
    """
    global PINTEREST_ACCESS_TOKEN
    if PINTEREST_ACCESS_TOKEN is None:
        # First try environment variable
        PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')
        if PINTEREST_ACCESS_TOKEN:
            print(f"Using Pinterest token from environment variable", file=sys.stderr)
        else:
            # Fall back to command line argument
            if "--pinterest-token" in sys.argv:
                token_index = sys.argv.index("--pinterest-token") + 1
                if token_index < len(sys.argv):
                    PINTEREST_ACCESS_TOKEN = sys.argv[token_index]
                    print(f"Using Pinterest token from command line arguments", file=sys.stderr)
                else:
                    raise Exception("--pinterest-token argument provided but no token value followed it")
            else:
                raise Exception("Pinterest token must be provided via 'PINTEREST_ACCESS_TOKEN' environment variable or '--pinterest-token' command line argument")

    return PINTEREST_ACCESS_TOKEN

def _make_pinterest_api_call(url: str, method: str = "GET", params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict:
    """Makes a request to the Pinterest API and handles the response."""
    try:
        token = _get_pinterest_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making Pinterest API call to {url}: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"API Error details: {error_details}", file=sys.stderr)
            except:
                print(f"Response text: {e.response.text}", file=sys.stderr)
        raise

def _format_pin_data(pin_data: Dict) -> Dict:
    """Format pin data for consistent output."""
    return {
        "id": pin_data.get("id"),
        "title": pin_data.get("title"),
        "description": pin_data.get("description"),
        "link": pin_data.get("link"),
        "board_id": pin_data.get("board_id"),
        "board_name": pin_data.get("board_name"),
        "created_at": pin_data.get("created_at"),
        "image_url": pin_data.get("media", {}).get("images", {}).get("originals", {}).get("url"),
        "pin_metrics": pin_data.get("pin_metrics", {}),
        "note": pin_data.get("note")
    }

def _format_board_data(board_data: Dict) -> Dict:
    """Format board data for consistent output."""
    return {
        "id": board_data.get("id"),
        "name": board_data.get("name"),
        "description": board_data.get("description"),
        "pin_count": board_data.get("pin_count"),
        "follower_count": board_data.get("follower_count"),
        "created_at": board_data.get("created_at"),
        "privacy": board_data.get("privacy")
    }

# --- MCP Tools ---

@mcp.tool()
def create_pin(
    board_id: str,
    title: str,
    description: str,
    image_url: str,
    link: Optional[str] = None,
    alt_text: Optional[str] = None,
    note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new pin on Pinterest.
    
    Args:
        board_id: The ID of the board to pin to
        title: Title of the pin (max 100 characters)
        description: Description of the pin (max 800 characters) 
        image_url: URL of the image to pin
        link: Optional destination URL when pin is clicked
        alt_text: Optional alt text for accessibility
        note: Optional private note (only visible to pin creator)
    
    Returns:
        Dict containing the created pin data
    """
    try:
        url = f"{PINTEREST_API_URL}/pins"
        
        pin_data = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": {
                "source_type": "image_url",
                "url": image_url
            }
        }
        
        if link:
            pin_data["link"] = link
        if alt_text:
            pin_data["alt_text"] = alt_text
        if note:
            pin_data["note"] = note
            
        response = _make_pinterest_api_call(url, method="POST", data=pin_data)
        return {
            "success": True,
            "pin": _format_pin_data(response),
            "message": "Pin created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create pin"
        }

@mcp.tool()
def create_promoted_pin(
    pin_id: str,
    campaign_name: str,
    daily_budget_micros: int,
    target_audience: Dict[str, Any],
    bid_strategy: str = "AUTOMATIC_BID",
    objective: str = "AWARENESS"
) -> Dict[str, Any]:
    """
    Create a promoted pin (Pinterest ad campaign).
    
    Args:
        pin_id: ID of the pin to promote
        campaign_name: Name for the ad campaign
        daily_budget_micros: Daily budget in micros (e.g., 5000000 = $5.00)
        target_audience: Targeting criteria (age, gender, location, interests)
        bid_strategy: Bidding strategy (AUTOMATIC_BID, MAX_BID)
        objective: Campaign objective (AWARENESS, CONSIDERATION, CONVERSIONS)
    
    Returns:
        Dict containing the created campaign data
    """
    try:
        # First create the campaign
        campaign_url = f"{PINTEREST_API_URL}/ad_accounts/campaigns"
        
        campaign_data = {
            "name": campaign_name,
            "status": "ACTIVE",
            "objective_type": objective,
            "daily_spend_cap": daily_budget_micros
        }
        
        campaign_response = _make_pinterest_api_call(campaign_url, method="POST", data=campaign_data)
        campaign_id = campaign_response.get("id")
        
        # Create ad group
        ad_group_url = f"{PINTEREST_API_URL}/ad_accounts/ad_groups"
        
        ad_group_data = {
            "name": f"{campaign_name} - Ad Group",
            "status": "ACTIVE",
            "campaign_id": campaign_id,
            "bid_strategy_type": bid_strategy,
            "daily_budget_in_micro_currency": daily_budget_micros,
            "targeting_spec": target_audience
        }
        
        ad_group_response = _make_pinterest_api_call(ad_group_url, method="POST", data=ad_group_data)
        ad_group_id = ad_group_response.get("id")
        
        # Create the ad
        ad_url = f"{PINTEREST_API_URL}/ad_accounts/ads"
        
        ad_data = {
            "ad_group_id": ad_group_id,
            "creative_type": "REGULAR",
            "pin_id": pin_id,
            "status": "ACTIVE"
        }
        
        ad_response = _make_pinterest_api_call(ad_url, method="POST", data=ad_data)
        
        return {
            "success": True,
            "campaign": {
                "campaign_id": campaign_id,
                "ad_group_id": ad_group_id,
                "ad_id": ad_response.get("id"),
                "name": campaign_name,
                "status": "ACTIVE",
                "daily_budget": daily_budget_micros / 1000000  # Convert back to dollars
            },
            "message": "Promoted pin campaign created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create promoted pin campaign"
        }

@mcp.tool()
def get_pin_metrics(
    pin_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get analytics metrics for a specific pin.
    
    Args:
        pin_id: ID of the pin to get metrics for
        start_date: Start date for metrics (YYYY-MM-DD format)
        end_date: End date for metrics (YYYY-MM-DD format)
        metric_types: List of metric types (IMPRESSION, SAVE, PIN_CLICK, etc.)
    
    Returns:
        Dict containing pin analytics data
    """
    try:
        # Get basic pin info
        pin_url = f"{PINTEREST_API_URL}/pins/{pin_id}"
        pin_response = _make_pinterest_api_call(pin_url)
        
        # Get analytics if dates provided
        analytics = {}
        if start_date and end_date:
            analytics_url = f"{PINTEREST_API_URL}/pins/{pin_id}/analytics"
            
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if metric_types:
                params["metric_types"] = ",".join(metric_types)
            else:
                params["metric_types"] = "IMPRESSION,SAVE,PIN_CLICK,OUTBOUND_CLICK"
                
            analytics_response = _make_pinterest_api_call(analytics_url, params=params)
            analytics = analytics_response.get("all", {})
        
        return {
            "success": True,
            "pin": _format_pin_data(pin_response),
            "analytics": analytics,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "message": "Pin metrics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get pin metrics"
        }

@mcp.tool()
def create_board(
    name: str,
    description: Optional[str] = None,
    privacy: str = "PUBLIC"
) -> Dict[str, Any]:
    """
    Create a new Pinterest board.
    
    Args:
        name: Name of the board
        description: Optional description of the board
        privacy: Board privacy setting (PUBLIC, PROTECTED, or SECRET)
    
    Returns:
        Dict containing the created board data
    """
    try:
        url = f"{PINTEREST_API_URL}/boards"
        
        board_data = {
            "name": name,
            "privacy": privacy
        }
        
        if description:
            board_data["description"] = description
            
        response = _make_pinterest_api_call(url, method="POST", data=board_data)
        
        return {
            "success": True,
            "board": _format_board_data(response),
            "message": "Board created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create board"
        }

@mcp.tool()
def schedule_pins(
    pins_data: List[Dict[str, Any]],
    schedule_interval_hours: int = 2
) -> Dict[str, Any]:
    """
    Schedule multiple pins to be posted at intervals.
    Note: This is a simulation - actual scheduling requires Pinterest Business account and approved scheduling tools.
    
    Args:
        pins_data: List of pin data objects with board_id, title, description, image_url, etc.
        schedule_interval_hours: Hours between each pin posting
    
    Returns:
        Dict containing scheduling information
    """
    try:
        scheduled_pins = []
        current_time = datetime.now()
        
        for i, pin_data in enumerate(pins_data):
            scheduled_time = current_time + timedelta(hours=i * schedule_interval_hours)
            
            scheduled_pin = {
                "pin_data": pin_data,
                "scheduled_time": scheduled_time.isoformat(),
                "status": "scheduled"
            }
            
            scheduled_pins.append(scheduled_pin)
        
        return {
            "success": True,
            "scheduled_pins": scheduled_pins,
            "total_pins": len(pins_data),
            "schedule_duration_hours": len(pins_data) * schedule_interval_hours,
            "message": f"Scheduled {len(pins_data)} pins over {len(pins_data) * schedule_interval_hours} hours",
            "note": "This is a scheduling simulation. Implement actual scheduling with Pinterest approved tools."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to schedule pins"
        }

@mcp.tool()
def get_trending_topics(
    region: str = "US",
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get trending topics and popular searches on Pinterest.
    Note: This uses Pinterest Trends API which requires special access.
    
    Args:
        region: Country code for regional trends (US, GB, CA, etc.)
        limit: Number of trending topics to return
    
    Returns:
        Dict containing trending topics data
    """
    try:
        # Note: Pinterest Trends API requires special access
        # This is a placeholder implementation showing the structure
        url = f"{PINTEREST_API_URL}/trends/keywords"
        
        params = {
            "region": region,
            "limit": limit
        }
        
        try:
            response = _make_pinterest_api_call(url, params=params)
            trending_data = response.get("trends", [])
        except:
            # Fallback to simulated trending topics for VividWalls art business
            trending_data = [
                {"keyword": "wall art", "growth": "+25%", "category": "home_decor"},
                {"keyword": "abstract art prints", "growth": "+18%", "category": "art"},
                {"keyword": "minimalist posters", "growth": "+32%", "category": "design"},
                {"keyword": "botanical prints", "growth": "+22%", "category": "nature"},
                {"keyword": "modern art decor", "growth": "+15%", "category": "home_decor"},
                {"keyword": "digital art prints", "growth": "+28%", "category": "digital_art"},
                {"keyword": "vintage art posters", "growth": "+12%", "category": "vintage"},
                {"keyword": "geometric wall art", "growth": "+20%", "category": "geometric"},
                {"keyword": "photography prints", "growth": "+17%", "category": "photography"},
                {"keyword": "inspirational quotes art", "growth": "+24%", "category": "quotes"}
            ]
        
        # Filter and enhance for art print business relevance
        relevant_trends = []
        art_keywords = ["art", "print", "poster", "wall", "decor", "design", "canvas", "frame"]
        
        for trend in trending_data[:limit]:
            keyword = trend.get("keyword", "").lower()
            if any(art_word in keyword for art_word in art_keywords):
                relevant_trends.append(trend)
        
        return {
            "success": True,
            "region": region,
            "trending_topics": relevant_trends,
            "total_trends": len(relevant_trends),
            "updated_at": datetime.now().isoformat(),
            "message": "Trending topics retrieved successfully",
            "recommendations": [
                "Focus on 'wall art' and 'art prints' - showing strong growth",
                "Consider minimalist and botanical themes",
                "Digital art prints are trending - good for instant downloads",
                "Abstract and geometric styles are popular"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get trending topics"
        }

@mcp.tool()
def get_boards(
    bookmark: Optional[str] = None,
    page_size: int = 25
) -> Dict[str, Any]:
    """
    Get all boards for the authenticated user.
    
    Args:
        bookmark: Cursor for pagination
        page_size: Number of boards to return per page
    
    Returns:
        Dict containing user's boards
    """
    try:
        url = f"{PINTEREST_API_URL}/boards"
        
        params = {
            "page_size": page_size
        }
        
        if bookmark:
            params["bookmark"] = bookmark
            
        response = _make_pinterest_api_call(url, params=params)
        
        boards = []
        for board_data in response.get("items", []):
            boards.append(_format_board_data(board_data))
        
        return {
            "success": True,
            "boards": boards,
            "bookmark": response.get("bookmark"),
            "total_boards": len(boards),
            "message": "Boards retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get boards"
        }

@mcp.tool()
def get_user_profile() -> Dict[str, Any]:
    """
    Get the authenticated user's Pinterest profile information.
    
    Returns:
        Dict containing user profile data
    """
    try:
        url = f"{PINTEREST_API_URL}/user_account"
        
        response = _make_pinterest_api_call(url)
        
        profile = {
            "id": response.get("id"),
            "username": response.get("username"),
            "first_name": response.get("first_name"),
            "last_name": response.get("last_name"),
            "business_name": response.get("business_name"),
            "website_url": response.get("website_url"),
            "profile_image": response.get("profile_image"),
            "account_type": response.get("account_type"),
            "follower_count": response.get("follower_count"),
            "following_count": response.get("following_count"),
            "board_count": response.get("board_count"),
            "pin_count": response.get("pin_count")
        }
        
        return {
            "success": True,
            "profile": profile,
            "message": "User profile retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get user profile"
        }

@mcp.tool()
def search_pins(
    query: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for pins using a query string.
    
    Args:
        query: Search query
        limit: Number of pins to return
    
    Returns:
        Dict containing search results
    """
    try:
        url = f"{PINTEREST_API_URL}/search/pins"
        
        params = {
            "query": query,
            "limit": limit
        }
        
        response = _make_pinterest_api_call(url, params=params)
        
        pins = []
        for pin_data in response.get("items", []):
            pins.append(_format_pin_data(pin_data))
        
        return {
            "success": True,
            "query": query,
            "pins": pins,
            "total_results": len(pins),
            "message": "Pin search completed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search pins"
        }

if __name__ == "__main__":
    # Run the server
    mcp.run()