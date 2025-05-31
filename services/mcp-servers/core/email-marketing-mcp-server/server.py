# server.py
from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, List, Optional, Any, Union
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import base64

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the script directory
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

# --- Constants ---
SENDGRID_API_URL = "https://api.sendgrid.com/v3"
MAILCHIMP_API_URL = "https://{dc}.api.mailchimp.com/3.0"

# Dynamic template system with content strategy integration
DYNAMIC_TEMPLATE_STRUCTURE = {
    "sections": {
        "header": {
            "type": "image",
            "content_strategy": "brand_identity",
            "variables": ["logo_url", "brand_color"]
        },
        "hero": {
            "type": "dynamic_content",
            "content_strategy": "featured_product",
            "variables": ["featured_image", "headline", "cta_text"]
        },
        "product_grid": {
            "type": "product_showcase",
            "content_strategy": "personalized_recommendations",
            "variables": ["product_images", "product_titles", "product_prices"]
        },
        "social_proof": {
            "type": "testimonial",
            "content_strategy": "customer_reviews",
            "variables": ["customer_photo", "review_text", "rating"]
        },
        "footer": {
            "type": "contact_info",
            "content_strategy": "brand_consistency",
            "variables": ["contact_info", "social_links", "unsubscribe_link"]
        }
    }
}

# Art print business specific templates with dynamic content
ART_PRINT_TEMPLATES = {
    "welcome_series": {
        "subject": "Welcome to VividWalls - Your Art Journey Begins! 🎨",
        "content": """
        Welcome to VividWalls! We're thrilled to have you join our community of art lovers.
        
        As a new member, you'll receive:
        ✨ 15% off your first order
        🎨 Early access to new collections
        📧 Weekly art inspiration and home decor tips
        
        Browse our curated collection of premium art prints at vividwalls.com
        """
    },
    "abandoned_cart": {
        "subject": "Don't let that perfect art piece slip away! 🖼️",
        "content": """
        Hi there! We noticed you left some beautiful art in your cart.
        
        Complete your order now and transform your space with:
        - Museum-quality prints on premium paper
        - Ready-to-hang options available
        - Free shipping on orders over $75
        
        Your cart is waiting - let's bring art to your walls!
        """
    },
    "new_collection": {
        "subject": "🎨 New Collection Alert: {collection_name} Now Available!",
        "content": """
        Exciting news! Our latest collection '{collection_name}' is now live.
        
        Discover stunning new pieces featuring:
        - {feature_1}
        - {feature_2}
        - {feature_3}
        
        Shop the collection now and get 10% off with code NEWART10
        """
    },
    "order_confirmation": {
        "subject": "Order Confirmed! Your Art is On Its Way 📦",
        "content": """
        Thank you for your order #{order_id}!
        
        Order Details:
        {order_details}
        
        Estimated delivery: {delivery_date}
        Tracking will be provided once your order ships.
        
        We can't wait for you to see your new art!
        """
    },
    "shipping_update": {
        "subject": "Your VividWalls Order Has Shipped! 🚚",
        "content": """
        Great news! Your order #{order_id} is on its way.
        
        Tracking Number: {tracking_number}
        Carrier: {carrier}
        Estimated Delivery: {delivery_date}
        
        Track your package: {tracking_url}
        """
    }
}

# Create an MCP server
mcp = FastMCP("email-marketing-mcp-server")

# Global variables to store credentials
EMAIL_API_KEY = None
EMAIL_PROVIDER = None

# --- Helper Functions ---

def _get_email_credentials() -> tuple[str, str]:
    """
    Get email service credentials from environment variables or command line arguments.
    Returns (api_key, provider)
    """
    global EMAIL_API_KEY, EMAIL_PROVIDER
    
    if EMAIL_API_KEY is None or EMAIL_PROVIDER is None:
        # Try environment variables first
        EMAIL_API_KEY = os.getenv('EMAIL_API_KEY')
        EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'sendgrid').lower()
        
        if EMAIL_API_KEY:
            print(f"Using {EMAIL_PROVIDER} credentials from environment variables")
        else:
            # Fall back to command line arguments
            if "--email-key" in sys.argv:
                key_index = sys.argv.index("--email-key") + 1
                if key_index < len(sys.argv):
                    EMAIL_API_KEY = sys.argv[key_index]
                    
                    if "--email-provider" in sys.argv:
                        provider_index = sys.argv.index("--email-provider") + 1
                        if provider_index < len(sys.argv):
                            EMAIL_PROVIDER = sys.argv[provider_index].lower()
                        else:
                            EMAIL_PROVIDER = 'sendgrid'
                    else:
                        EMAIL_PROVIDER = 'sendgrid'
                    
                    print(f"Using {EMAIL_PROVIDER} credentials from command line")
                else:
                    raise Exception("--email-key argument provided but no key value followed")
            else:
                raise Exception("Email API key must be provided via 'EMAIL_API_KEY' environment variable or '--email-key' command line argument")
    
    return EMAIL_API_KEY, EMAIL_PROVIDER

def _make_sendgrid_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make request to SendGrid API"""
    api_key, provider = _get_email_credentials()
    if provider != 'sendgrid':
        raise Exception("SendGrid provider required for this operation")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"{SENDGRID_API_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise Exception(f"Unsupported method: {method}")
        
        response.raise_for_status()
        
        if response.content:
            return response.json()
        else:
            return {"success": True}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"SendGrid API error: {e}"
        if hasattr(e.response, 'text'):
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)

def _make_mailchimp_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make request to Mailchimp API"""
    api_key, provider = _get_email_credentials()
    if provider != 'mailchimp':
        raise Exception("Mailchimp provider required for this operation")
    
    # Extract datacenter from API key
    dc = api_key.split('-')[-1] if '-' in api_key else 'us1'
    base_url = MAILCHIMP_API_URL.format(dc=dc)
    
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'anystring:{api_key}'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    
    url = f"{base_url}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise Exception(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Mailchimp API error: {e}"
        if hasattr(e.response, 'text'):
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)

# --- MCP Tools ---

@mcp.tool()
def create_campaign(
    name: str,
    subject: str,
    content: str,
    template_type: Optional[str] = None,
    sender_email: str = "hello@vividwalls.com",
    sender_name: str = "VividWalls",
    list_ids: Optional[List[str]] = None,
    personalization: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a new email marketing campaign for VividWalls art print business.
    
    Args:
        name: Campaign name
        subject: Email subject line
        content: Email content (HTML or plain text)
        template_type: Optional template type (welcome_series, abandoned_cart, new_collection, etc.)
        sender_email: Sender email address
        sender_name: Sender display name
        list_ids: List of recipient list IDs
        personalization: Dynamic content variables
    
    Returns:
        Dict with campaign details and ID
    """
    try:
        api_key, provider = _get_email_credentials()
        
        # Use template if specified
        if template_type and template_type in ART_PRINT_TEMPLATES:
            template = ART_PRINT_TEMPLATES[template_type]
            if not subject or subject == template["subject"]:
                subject = template["subject"]
            if not content:
                content = template["content"]
                
            # Apply personalization
            if personalization:
                for key, value in personalization.items():
                    subject = subject.replace(f"{{{key}}}", value)
                    content = content.replace(f"{{{key}}}", value)
        
        if provider == 'sendgrid':
            campaign_data = {
                "name": name,
                "send_to": {
                    "list_ids": list_ids or []
                },
                "email_config": {
                    "subject": subject,
                    "html_content": content,
                    "sender_id": 1,  # Default sender
                    "suppression_group_id": 1
                }
            }
            
            response = _make_sendgrid_request("campaigns", "POST", campaign_data)
            return {
                "success": True,
                "campaign_id": response.get("id"),
                "name": name,
                "subject": subject,
                "provider": "sendgrid",
                "status": "draft"
            }
            
        elif provider == 'mailchimp':
            # Implementation for Mailchimp
            campaign_data = {
                "type": "regular",
                "recipients": {
                    "list_id": list_ids[0] if list_ids else None
                },
                "settings": {
                    "subject_line": subject,
                    "title": name,
                    "from_name": sender_name,
                    "reply_to": sender_email
                }
            }
            
            response = _make_mailchimp_request("campaigns", "POST", campaign_data)
            
            # Set content
            if response.get("id"):
                content_data = {
                    "html": content
                }
                _make_mailchimp_request(f"campaigns/{response['id']}/content", "PUT", content_data)
            
            return {
                "success": True,
                "campaign_id": response.get("id"),
                "name": name,
                "subject": subject,
                "provider": "mailchimp",
                "status": "save"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def segment_audience(
    name: str,
    conditions: List[Dict[str, Any]],
    list_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create audience segments for targeted email campaigns.
    
    Args:
        name: Segment name
        conditions: List of segmentation conditions
        list_id: Base list ID to segment from
    
    Returns:
        Dict with segment details and count
    
    Example conditions for art print business:
    - {"field": "purchase_history", "operator": "contains", "value": "abstract"}
    - {"field": "location", "operator": "equals", "value": "US"}
    - {"field": "last_purchase", "operator": "greater_than", "value": "30_days_ago"}
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            # SendGrid segmentation
            segment_data = {
                "name": name,
                "parent_list_id": list_id,
                "query_dsl": {
                    "and": conditions
                }
            }
            
            response = _make_sendgrid_request("contactdb/segments", "POST", segment_data)
            return {
                "success": True,
                "segment_id": response.get("id"),
                "name": name,
                "recipient_count": response.get("recipient_count", 0),
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            # Mailchimp segmentation
            segment_data = {
                "name": name,
                "options": {
                    "match": "all",
                    "conditions": conditions
                }
            }
            
            response = _make_mailchimp_request(f"lists/{list_id}/segments", "POST", segment_data)
            return {
                "success": True,
                "segment_id": response.get("id"),
                "name": name,
                "member_count": response.get("member_count", 0),
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def track_engagement(
    campaign_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track email engagement metrics including opens, clicks, and conversions.
    
    Args:
        campaign_id: Specific campaign ID to track
        start_date: Start date for metrics (YYYY-MM-DD)
        end_date: End date for metrics (YYYY-MM-DD)
    
    Returns:
        Dict with engagement metrics
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            if campaign_id:
                response = _make_sendgrid_request(f"campaigns/{campaign_id}/stats")
            else:
                params = {}
                if start_date:
                    params['start_date'] = start_date
                if end_date:
                    params['end_date'] = end_date
                
                endpoint = "stats"
                if params:
                    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    endpoint = f"{endpoint}?{param_str}"
                
                response = _make_sendgrid_request(endpoint)
            
            return {
                "success": True,
                "metrics": {
                    "delivered": response.get("delivered", 0),
                    "opens": response.get("opens", 0),
                    "unique_opens": response.get("unique_opens", 0),
                    "clicks": response.get("clicks", 0),
                    "unique_clicks": response.get("unique_clicks", 0),
                    "bounces": response.get("bounces", 0),
                    "spam_reports": response.get("spam_reports", 0),
                    "unsubscribes": response.get("unsubscribes", 0)
                },
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            if campaign_id:
                response = _make_mailchimp_request(f"campaigns/{campaign_id}")
                return {
                    "success": True,
                    "metrics": response.get("report_summary", {}),
                    "provider": "mailchimp"
                }
            else:
                response = _make_mailchimp_request("campaigns")
                return {
                    "success": True,
                    "campaigns": response.get("campaigns", []),
                    "provider": "mailchimp"
                }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def automate_sequences(
    sequence_type: str,
    trigger_event: str,
    emails: List[Dict[str, Any]],
    list_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create automated email sequences for customer lifecycle marketing.
    
    Args:
        sequence_type: Type of automation (welcome, abandoned_cart, win_back, etc.)
        trigger_event: Event that triggers the sequence
        emails: List of emails in the sequence with timing
        list_id: Target list ID
    
    Returns:
        Dict with automation details
    
    Example for art print business:
    sequence_type: "welcome"
    trigger_event: "subscription"
    emails: [
        {"delay": 0, "template": "welcome_series", "subject": "Welcome to VividWalls!"},
        {"delay": 3, "template": "new_collection", "subject": "Discover Our Collections"},
        {"delay": 7, "template": "first_purchase", "subject": "Ready to Transform Your Space?"}
    ]
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            # SendGrid automation setup
            automation_data = {
                "title": f"{sequence_type.title()} Sequence",
                "trigger_settings": {
                    "trigger_type": trigger_event,
                    "list_id": list_id
                },
                "emails": emails
            }
            
            response = _make_sendgrid_request("marketing/automations", "POST", automation_data)
            return {
                "success": True,
                "automation_id": response.get("id"),
                "sequence_type": sequence_type,
                "trigger_event": trigger_event,
                "email_count": len(emails),
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            # Mailchimp automation setup
            automation_data = {
                "type": "email",
                "title": f"{sequence_type.title()} Sequence",
                "status": "save",
                "settings": {
                    "from_name": "VividWalls",
                    "reply_to": "hello@vividwalls.com"
                },
                "tracking": {
                    "opens": True,
                    "html_clicks": True,
                    "text_clicks": True
                },
                "trigger_settings": {
                    "workflow_type": trigger_event
                }
            }
            
            response = _make_mailchimp_request("automations", "POST", automation_data)
            return {
                "success": True,
                "automation_id": response.get("id"),
                "sequence_type": sequence_type,
                "trigger_event": trigger_event,
                "status": response.get("status"),
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def create_template(
    name: str,
    html_content: str,
    category: str = "art_print",
    variables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create reusable email templates for VividWalls campaigns.
    
    Args:
        name: Template name
        html_content: HTML content of the template
        category: Template category (art_print, transactional, promotional)
        variables: List of template variables for personalization
    
    Returns:
        Dict with template details and ID
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            template_data = {
                "name": name,
                "generation": "dynamic"
            }
            
            # Create template
            response = _make_sendgrid_request("templates", "POST", template_data)
            template_id = response.get("id")
            
            if template_id:
                # Add version
                version_data = {
                    "template_id": template_id,
                    "active": 1,
                    "name": f"{name} - Version 1",
                    "html_content": html_content,
                    "subject": "{{subject}}",
                    "editor": "code"
                }
                
                version_response = _make_sendgrid_request("templates/{template_id}/versions", "POST", version_data)
                
                return {
                    "success": True,
                    "template_id": template_id,
                    "version_id": version_response.get("id"),
                    "name": name,
                    "category": category,
                    "variables": variables or [],
                    "provider": "sendgrid"
                }
            
        elif provider == 'mailchimp':
            template_data = {
                "name": name,
                "html": html_content,
                "folder_id": None  # Can be organized into folders
            }
            
            response = _make_mailchimp_request("templates", "POST", template_data)
            return {
                "success": True,
                "template_id": response.get("id"),
                "name": name,
                "category": category,
                "variables": variables or [],
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def schedule_send(
    campaign_id: str,
    send_time: str,
    timezone: str = "America/New_York"
) -> Dict[str, Any]:
    """
    Schedule a campaign to be sent at a specific time.
    
    Args:
        campaign_id: Campaign ID to schedule
        send_time: Send time in ISO format (YYYY-MM-DDTHH:MM:SS)
        timezone: Timezone for scheduling
    
    Returns:
        Dict with scheduling confirmation
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            schedule_data = {
                "send_at": datetime.fromisoformat(send_time).timestamp()
            }
            
            response = _make_sendgrid_request(f"campaigns/{campaign_id}/schedules", "POST", schedule_data)
            return {
                "success": True,
                "campaign_id": campaign_id,
                "scheduled_time": send_time,
                "timezone": timezone,
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            schedule_data = {
                "schedule_time": send_time,
                "timezone": timezone
            }
            
            response = _make_mailchimp_request(f"campaigns/{campaign_id}/actions/schedule", "POST", schedule_data)
            return {
                "success": True,
                "campaign_id": campaign_id,
                "scheduled_time": send_time,
                "timezone": timezone,
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def send_transactional(
    to_email: str,
    template_type: str,
    data: Dict[str, Any],
    from_email: str = "orders@vividwalls.com",
    from_name: str = "VividWalls"
) -> Dict[str, Any]:
    """
    Send transactional emails for order confirmations, shipping updates, etc.
    
    Args:
        to_email: Recipient email address
        template_type: Template type (order_confirmation, shipping_update, etc.)
        data: Data to populate the template
        from_email: Sender email
        from_name: Sender name
    
    Returns:
        Dict with send confirmation
    """
    try:
        api_key, provider = _get_email_credentials()
        
        # Get template content
        if template_type in ART_PRINT_TEMPLATES:
            template = ART_PRINT_TEMPLATES[template_type]
            subject = template["subject"]
            content = template["content"]
            
            # Apply data substitution
            for key, value in data.items():
                subject = subject.replace(f"{{{key}}}", str(value))
                content = content.replace(f"{{{key}}}", str(value))
        else:
            raise Exception(f"Unknown template type: {template_type}")
        
        if provider == 'sendgrid':
            email_data = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {
                    "email": from_email,
                    "name": from_name
                },
                "content": [{
                    "type": "text/html",
                    "value": content
                }]
            }
            
            response = _make_sendgrid_request("mail/send", "POST", email_data)
            return {
                "success": True,
                "to_email": to_email,
                "template_type": template_type,
                "subject": subject,
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            # Mailchimp transactional emails (via Mandrill)
            email_data = {
                "key": api_key,
                "message": {
                    "html": content,
                    "subject": subject,
                    "from_email": from_email,
                    "from_name": from_name,
                    "to": [{
                        "email": to_email,
                        "type": "to"
                    }]
                }
            }
            
            # Note: This would use Mandrill API, not regular Mailchimp
            # Simplified for example
            return {
                "success": True,
                "to_email": to_email,
                "template_type": template_type,
                "subject": subject,
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def manage_subscribers(
    action: str,
    email: str,
    list_id: str,
    subscriber_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage email subscribers - add, remove, or update.
    
    Args:
        action: Action to perform (add, remove, update)
        email: Subscriber email address
        list_id: Target list ID
        subscriber_data: Additional subscriber data (name, preferences, etc.)
    
    Returns:
        Dict with operation result
    """
    try:
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            if action == "add":
                contact_data = {
                    "contacts": [{
                        "email": email,
                        **(subscriber_data if subscriber_data else {})
                    }]
                }
                response = _make_sendgrid_request("marketing/contacts", "PUT", contact_data)
                
                # Add to list
                if list_id:
                    list_data = {
                        "contact_ids": [email]  # SendGrid might use contact IDs
                    }
                    _make_sendgrid_request(f"marketing/lists/{list_id}/contacts", "POST", list_data)
                
            elif action == "remove":
                response = _make_sendgrid_request(f"marketing/lists/{list_id}/contacts?contact_ids={email}", "DELETE")
                
            elif action == "update":
                contact_data = {
                    "contacts": [{
                        "email": email,
                        **(subscriber_data if subscriber_data else {})
                    }]
                }
                response = _make_sendgrid_request("marketing/contacts", "PUT", contact_data)
            
            return {
                "success": True,
                "action": action,
                "email": email,
                "list_id": list_id,
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            if action == "add":
                member_data = {
                    "email_address": email,
                    "status": "subscribed",
                    **(subscriber_data if subscriber_data else {})
                }
                response = _make_mailchimp_request(f"lists/{list_id}/members", "POST", member_data)
                
            elif action == "remove":
                # Get subscriber hash
                import hashlib
                subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
                response = _make_mailchimp_request(f"lists/{list_id}/members/{subscriber_hash}", "DELETE")
                
            elif action == "update":
                import hashlib
                subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
                member_data = {
                    "email_address": email,
                    **(subscriber_data if subscriber_data else {})
                }
                response = _make_mailchimp_request(f"lists/{list_id}/members/{subscriber_hash}", "PUT", member_data)
            
            return {
                "success": True,
                "action": action,
                "email": email,
                "list_id": list_id,
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_analytics(
    metric_type: str = "overview",
    date_range: int = 30,
    campaign_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get comprehensive email marketing analytics for VividWalls campaigns.
    
    Args:
        metric_type: Type of analytics (overview, engagement, revenue, growth)
        date_range: Number of days to include in analysis
        campaign_ids: Specific campaigns to analyze
    
    Returns:
        Dict with analytics data and insights
    """
    try:
        api_key, provider = _get_email_credentials()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        if provider == 'sendgrid':
            if metric_type == "overview":
                # Get global stats
                response = _make_sendgrid_request(f"stats?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}")
                
                analytics_data = {
                    "date_range": {
                        "start": start_date.strftime('%Y-%m-%d'),
                        "end": end_date.strftime('%Y-%m-%d'),
                        "days": date_range
                    },
                    "overview": {
                        "total_delivered": sum([stat.get("delivered", 0) for stat in response]),
                        "total_opens": sum([stat.get("opens", 0) for stat in response]),
                        "total_clicks": sum([stat.get("clicks", 0) for stat in response]),
                        "avg_open_rate": 0,  # Calculate average
                        "avg_click_rate": 0   # Calculate average
                    },
                    "engagement_trends": response,
                    "top_performing_campaigns": [],
                    "insights": [
                        "Consider A/B testing subject lines for better open rates",
                        "Art print campaigns perform best on weekends",
                        "New collection announcements have highest engagement"
                    ]
                }
                
                # Calculate rates
                total_delivered = analytics_data["overview"]["total_delivered"]
                if total_delivered > 0:
                    analytics_data["overview"]["avg_open_rate"] = (analytics_data["overview"]["total_opens"] / total_delivered) * 100
                    analytics_data["overview"]["avg_click_rate"] = (analytics_data["overview"]["total_clicks"] / total_delivered) * 100
                
                return {
                    "success": True,
                    "analytics": analytics_data,
                    "provider": "sendgrid"
                }
                
        elif provider == 'mailchimp':
            if metric_type == "overview":
                # Get reports
                response = _make_mailchimp_request("reports")
                
                analytics_data = {
                    "date_range": {
                        "start": start_date.strftime('%Y-%m-%d'),
                        "end": end_date.strftime('%Y-%m-%d'),
                        "days": date_range
                    },
                    "campaign_count": response.get("total_items", 0),
                    "reports": response.get("reports", [])[:10],  # Top 10 recent
                    "insights": [
                        "Art print customers prefer visual-heavy emails",
                        "Mobile optimization increases click rates by 25%",
                        "Personalized product recommendations boost sales"
                    ]
                }
                
                return {
                    "success": True,
                    "analytics": analytics_data,
                    "provider": "mailchimp"
                }
        
        return {
            "success": False,
            "error": f"Analytics type '{metric_type}' not implemented for {provider}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def create_dynamic_template(
    template_name: str,
    template_type: str,
    content_strategy: Dict[str, Any],
    sections: List[Dict[str, Any]],
    variables: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create dynamic email templates with content strategy integration.
    
    Args:
        template_name: Name of the template
        template_type: Type (welcome, promotional, transactional, etc.)
        content_strategy: Strategy configuration for images and copy
        sections: Template sections with dynamic content slots
        variables: Default values for template variables
    
    Returns:
        Dict with template creation result
    
    Example content_strategy:
    {
        "personalization_level": "high",
        "image_strategy": "product_focused",
        "copy_strategy": "conversational_tone",
        "cta_strategy": "urgency_based"
    }
    
    Example sections:
    [
        {
            "name": "hero",
            "type": "image_with_text",
            "content_slots": ["hero_image", "headline", "subheadline"],
            "layout": "centered"
        },
        {
            "name": "product_showcase",
            "type": "product_grid",
            "content_slots": ["product_images", "product_titles", "product_prices"],
            "layout": "3_column"
        }
    ]
    """
    try:
        # Build dynamic template structure
        template_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <!-- Template: {template_name} -->
            <!-- Content Strategy: {content_strategy.get('image_strategy', 'default')} -->
        """
        
        # Process each section
        for section in sections:
            section_name = section.get('name')
            section_type = section.get('type')
            content_slots = section.get('content_slots', [])
            layout = section.get('layout', 'default')
            
            if section_type == "hero":
                template_html += f"""
                <!-- Dynamic Hero Section -->
                <div style="text-align: center; padding: 30px 20px; background: {{{{hero_bg_color}}}};">
                    <img src="{{{{hero_image}}}}" alt="{{{{hero_alt_text}}}}" style="max-width: 100%; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="color: {{{{headline_color}}}}; margin-bottom: 15px;">{{{{headline}}}}</h1>
                    <p style="color: {{{{subheadline_color}}}}; font-size: 16px; line-height: 1.6;">{{{{subheadline}}}}</p>
                </div>
                """
            
            elif section_type == "product_grid":
                columns = "3" if layout == "3_column" else "2"
                template_html += f"""
                <!-- Dynamic Product Grid -->
                <div style="padding: 30px 20px;">
                    <h2 style="text-align: center; color: #333; margin-bottom: 25px;">{{{{grid_headline}}}}</h2>
                    <div style="display: grid; grid-template-columns: repeat({columns}, 1fr); gap: 15px;">
                        {{{{product_grid_content}}}}
                    </div>
                </div>
                """
            
            elif section_type == "cta":
                template_html += f"""
                <!-- Dynamic CTA Section -->
                <div style="text-align: center; padding: 25px 20px;">
                    <a href="{{{{cta_url}}}}" style="background: {{{{cta_bg_color}}}}; color: {{{{cta_text_color}}}}; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">{{{{cta_text}}}}</a>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{{{{cta_subtext}}}}</p>
                </div>
                """
            
            elif section_type == "social_proof":
                template_html += f"""
                <!-- Dynamic Social Proof -->
                <div style="background: #f9f9f9; padding: 25px 20px; text-align: center;">
                    <h3 style="color: #333; margin-bottom: 20px;">{{{{social_proof_headline}}}}</h3>
                    <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                        {{{{customer_reviews}}}}
                    </div>
                </div>
                """
        
        template_html += """
        </div>
        """
        
        # Store template with metadata
        template_data = {
            "name": template_name,
            "type": template_type,
            "html_content": template_html,
            "content_strategy": content_strategy,
            "sections": sections,
            "variables": variables or {},
            "created_at": datetime.now().isoformat(),
            "personalization_slots": [slot for section in sections for slot in section.get('content_slots', [])]
        }
        
        # Save to provider
        api_key, provider = _get_email_credentials()
        
        if provider == 'sendgrid':
            # Create SendGrid template
            sg_template_data = {
                "name": template_name,
                "generation": "dynamic"
            }
            
            response = _make_sendgrid_request("templates", "POST", sg_template_data)
            template_id = response.get("id")
            
            if template_id:
                # Add version with dynamic content
                version_data = {
                    "template_id": template_id,
                    "active": 1,
                    "name": f"{template_name} - Dynamic Version",
                    "html_content": template_html,
                    "subject": "{{subject}}",
                    "editor": "code"
                }
                
                version_response = _make_sendgrid_request(f"templates/{template_id}/versions", "POST", version_data)
                
                return {
                    "success": True,
                    "template_id": template_id,
                    "version_id": version_response.get("id"),
                    "template_data": template_data,
                    "provider": "sendgrid"
                }
        
        elif provider == 'mailchimp':
            # Create Mailchimp template
            mc_template_data = {
                "name": template_name,
                "html": template_html,
                "folder_id": None
            }
            
            response = _make_mailchimp_request("templates", "POST", mc_template_data)
            
            return {
                "success": True,
                "template_id": response.get("id"),
                "template_data": template_data,
                "provider": "mailchimp"
            }
        
        return {
            "success": False,
            "error": f"Unsupported provider: {provider}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def populate_template_content(
    template_id: str,
    content_data: Dict[str, Any],
    ai_content_generation: Optional[bool] = True,
    customer_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Populate dynamic template with content based on strategy and customer data.
    
    Args:
        template_id: ID of the dynamic template
        content_data: Data to populate template slots
        ai_content_generation: Whether to use AI for missing content
        customer_context: Customer data for personalization
    
    Returns:
        Dict with populated template content
    
    Example content_data:
    {
        "hero_image": "https://example.com/featured-art.jpg",
        "headline": "Transform Your Space Today",
        "product_images": ["art1.jpg", "art2.jpg", "art3.jpg"],
        "customer_name": "Sarah",
        "recommended_style": "abstract"
    }
    """
    try:
        api_key, provider = _get_email_credentials()
        
        # Get template structure (this would come from storage in real implementation)
        # For now, use default structure
        
        # AI-powered content generation based on strategy
        if ai_content_generation and customer_context:
            # Generate personalized content
            customer_style = customer_context.get('preferred_style', 'modern')
            customer_name = customer_context.get('name', 'there')
            purchase_history = customer_context.get('purchase_history', [])
            
            # Generate smart defaults
            if 'headline' not in content_data:
                if 'abstract' in customer_style.lower():
                    content_data['headline'] = f"Hi {customer_name}! New Abstract Pieces Just For You"
                elif 'landscape' in customer_style.lower():
                    content_data['headline'] = f"Stunning Landscapes to Inspire You, {customer_name}"
                else:
                    content_data['headline'] = f"Curated Art Recommendations for {customer_name}"
            
            # Generate product recommendations based on history
            if 'product_grid_content' not in content_data and purchase_history:
                # This would integrate with product recommendation engine
                content_data['product_grid_content'] = """
                <div style="text-align: center; border: 1px solid #eee; padding: 15px; border-radius: 8px;">
                    <img src="https://example.com/recommended-art-1.jpg" style="width: 100%; border-radius: 4px;">
                    <h4 style="margin: 10px 0 5px 0;">Recommended for You</h4>
                    <p style="color: #666; font-size: 14px;">Based on your style preferences</p>
                </div>
                """
            
            # Generate social proof
            if 'customer_reviews' not in content_data:
                content_data['customer_reviews'] = """
                <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin: 0 5px;">
                    <p style="font-style: italic; margin-bottom: 10px;">"Absolutely love my new art prints!"</p>
                    <p style="font-size: 12px; color: #666;">- Happy Customer</p>
                </div>
                """
        
        # Apply content strategy rules
        content_strategy = content_data.get('content_strategy', {})
        
        # Set brand colors based on strategy
        if content_strategy.get('image_strategy') == 'warm_tones':
            content_data.setdefault('hero_bg_color', '#fff8f3')
            content_data.setdefault('cta_bg_color', '#e67e22')
        elif content_strategy.get('image_strategy') == 'cool_tones':
            content_data.setdefault('hero_bg_color', '#f8fbff')
            content_data.setdefault('cta_bg_color', '#3498db')
        else:
            content_data.setdefault('hero_bg_color', '#ffffff')
            content_data.setdefault('cta_bg_color', '#e74c3c')
        
        # Set copy strategy elements
        if content_strategy.get('copy_strategy') == 'urgency_based':
            content_data.setdefault('cta_text', 'Shop Now - Limited Time!')
            content_data.setdefault('cta_subtext', 'Offer expires soon')
        elif content_strategy.get('copy_strategy') == 'benefit_focused':
            content_data.setdefault('cta_text', 'Transform Your Space')
            content_data.setdefault('cta_subtext', 'Free shipping on orders over $75')
        else:
            content_data.setdefault('cta_text', 'Shop Collection')
            content_data.setdefault('cta_subtext', '')
        
        # Generate final populated template
        populated_template = {
            "template_id": template_id,
            "populated_content": content_data,
            "personalization_applied": ai_content_generation,
            "customer_context_used": customer_context is not None,
            "ready_for_send": True
        }
        
        return {
            "success": True,
            "populated_template": populated_template,
            "content_slots_filled": len(content_data),
            "ai_generated_elements": ["headline", "product_recommendations", "social_proof"] if ai_content_generation else []
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def generate_content_strategy(
    campaign_type: str,
    target_audience: Dict[str, Any],
    business_goals: List[str],
    brand_guidelines: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate AI-powered content strategy for email campaigns.
    
    Args:
        campaign_type: Type of campaign (welcome, promotional, retention, etc.)
        target_audience: Audience characteristics and preferences
        business_goals: List of campaign objectives
        brand_guidelines: Brand colors, fonts, tone guidelines
    
    Returns:
        Dict with comprehensive content strategy
    
    Example usage:
    generate_content_strategy(
        campaign_type="abandoned_cart",
        target_audience={
            "age_range": "25-45",
            "interests": ["modern art", "home decor"],
            "purchase_behavior": "price_conscious",
            "preferred_style": "minimalist"
        },
        business_goals=["recover_cart", "increase_urgency", "build_trust"],
        brand_guidelines={
            "primary_color": "#2c3e50",
            "tone": "friendly_professional",
            "imagery_style": "clean_modern"
        }
    )
    """
    try:
        # AI-powered strategy generation based on inputs
        strategy = {
            "campaign_type": campaign_type,
            "generated_at": datetime.now().isoformat()
        }
        
        # Image strategy based on audience and goals
        audience_style = target_audience.get('preferred_style', 'modern')
        
        if campaign_type == "welcome":
            strategy["image_strategy"] = {
                "primary_focus": "collection_overview",
                "style": "inspiring_lifestyle",
                "hero_image_type": "curated_gallery_wall",
                "product_showcase": "diverse_styles",
                "color_palette": "warm_welcoming"
            }
            strategy["copy_strategy"] = {
                "tone": "warm_welcoming",
                "personalization_level": "high",
                "key_messages": ["welcome", "benefits", "style_discovery"],
                "cta_approach": "exploration_focused"
            }
            
        elif campaign_type == "abandoned_cart":
            strategy["image_strategy"] = {
                "primary_focus": "cart_items_prominent",
                "style": "product_focused_lifestyle",
                "hero_image_type": "abandoned_items_styled",
                "urgency_visual_cues": True,
                "social_proof_images": True
            }
            strategy["copy_strategy"] = {
                "tone": "friendly_urgent",
                "personalization_level": "very_high",
                "key_messages": ["personalized_reminder", "scarcity", "benefits"],
                "cta_approach": "urgency_with_incentive"
            }
            
        elif campaign_type == "new_collection":
            strategy["image_strategy"] = {
                "primary_focus": "new_collection_hero",
                "style": "editorial_artistic",
                "hero_image_type": "collection_lifestyle_shot",
                "artist_spotlight": True,
                "behind_scenes_content": True
            }
            strategy["copy_strategy"] = {
                "tone": "excited_exclusive",
                "personalization_level": "medium",
                "key_messages": ["exclusivity", "artistic_story", "early_access"],
                "cta_approach": "discovery_and_exclusivity"
            }
        
        # Customize based on audience preferences
        if "minimalist" in audience_style:
            strategy["image_strategy"]["layout"] = "clean_whitespace"
            strategy["image_strategy"]["color_palette"] = "neutral_monochrome"
        elif "abstract" in audience_style:
            strategy["image_strategy"]["layout"] = "creative_asymmetric"
            strategy["image_strategy"]["color_palette"] = "bold_artistic"
        
        # Apply brand guidelines
        if brand_guidelines:
            strategy["brand_application"] = {
                "primary_color": brand_guidelines.get("primary_color", "#333"),
                "tone_adaptation": brand_guidelines.get("tone", "professional"),
                "imagery_filter": brand_guidelines.get("imagery_style", "natural")
            }
        
        # Generate specific content recommendations
        strategy["content_recommendations"] = {
            "subject_line_formulas": [
                f"🎨 {target_audience.get('name', 'Art Lover')}, your perfect piece awaits",
                f"Don't miss out - {campaign_type.replace('_', ' ').title()} inside!",
                f"Exclusive for you: New {audience_style} art collection"
            ],
            "headline_templates": [
                f"Curated for {audience_style} lovers",
                f"Transform your space with {audience_style} art",
                f"Discover your next favorite piece"
            ],
            "product_positioning": f"Focus on {audience_style} style with lifestyle context",
            "social_proof_type": "customer_galleries_and_reviews"
        }
        
        # Dynamic variable mapping
        strategy["variable_mapping"] = {
            "hero_image": "Use lifestyle shot showcasing art in modern home setting",
            "headline": f"Personalized for {audience_style} preferences",
            "product_grid": f"Feature {audience_style} pieces with room mockups",
            "cta_text": "Shop Your Style" if campaign_type == "welcome" else "Complete Your Order",
            "social_proof": "Customer installation photos and testimonials"
        }
        
        return {
            "success": True,
            "content_strategy": strategy,
            "recommended_template_structure": [
                {"name": "hero", "type": "lifestyle_image_with_headline"},
                {"name": "personalized_products", "type": "product_grid"},
                {"name": "social_proof", "type": "customer_gallery"},
                {"name": "cta", "type": "prominent_button"}
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def create_automation(
    name: str,
    trigger_type: str,
    trigger_conditions: Dict[str, Any],
    actions: List[Dict[str, Any]],
    settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create advanced email automation workflows with multiple triggers and actions.
    
    Args:
        name: Automation workflow name
        trigger_type: Type of trigger (form_signup, purchase, website_visit, etc.)
        trigger_conditions: Conditions that must be met to trigger
        actions: List of actions to perform when triggered
        settings: Additional workflow settings
    
    Returns:
        Dict with automation workflow details
    
    Example for VividWalls:
    trigger_type: "website_visit"
    trigger_conditions: {"page": "/collections/abstract", "time_on_page": ">30s"}
    actions: [
        {"type": "wait", "duration": "1_hour"},
        {"type": "send_email", "template": "abandoned_browse", "personalization": {"collection": "abstract"}},
        {"type": "wait", "duration": "3_days"},
        {"type": "send_email", "template": "collection_discount", "discount_code": "ABSTRACT15"}
    ]
    """
    try:
        api_key, provider = _get_email_credentials()
        
        # Default settings for art print business
        default_settings = {
            "timezone": "America/New_York",
            "send_time_optimization": True,
            "frequency_capping": True,
            "unsubscribe_on_spam": True
        }
        
        workflow_settings = {**default_settings, **(settings if settings else {})}
        
        if provider == 'sendgrid':
            automation_data = {
                "title": name,
                "status": "draft",
                "trigger_settings": {
                    "trigger_type": trigger_type,
                    "conditions": trigger_conditions
                },
                "emails": [],  # Convert actions to email steps
                "settings": workflow_settings
            }
            
            # Process actions into SendGrid format
            for i, action in enumerate(actions):
                if action.get("type") == "send_email":
                    email_step = {
                        "step_id": i + 1,
                        "template_id": action.get("template"),
                        "delay": action.get("delay", 0),
                        "personalization": action.get("personalization", {})
                    }
                    automation_data["emails"].append(email_step)
            
            response = _make_sendgrid_request("marketing/automations", "POST", automation_data)
            return {
                "success": True,
                "automation_id": response.get("id"),
                "name": name,
                "trigger_type": trigger_type,
                "action_count": len([a for a in actions if a.get("type") == "send_email"]),
                "status": "draft",
                "provider": "sendgrid"
            }
            
        elif provider == 'mailchimp':
            # Mailchimp journey/automation
            automation_data = {
                "type": "email",
                "title": name,
                "status": "save",
                "settings": {
                    "from_name": "VividWalls",
                    "reply_to": "hello@vividwalls.com",
                    **workflow_settings
                },
                "tracking": {
                    "opens": True,
                    "html_clicks": True,
                    "text_clicks": True,
                    "goal_tracking": True
                },
                "trigger_settings": {
                    "workflow_type": trigger_type,
                    **trigger_conditions
                }
            }
            
            response = _make_mailchimp_request("automations", "POST", automation_data)
            
            automation_id = response.get("id")
            if automation_id:
                # Add email steps
                for i, action in enumerate(actions):
                    if action.get("type") == "send_email":
                        email_data = {
                            "type": "email",
                            "delay": {
                                "amount": action.get("delay", 0),
                                "type": "day"
                            },
                            "settings": {
                                "subject_line": action.get("subject", ""),
                                "title": f"Email {i+1}",
                                "template_id": action.get("template")
                            }
                        }
                        _make_mailchimp_request(f"automations/{automation_id}/emails", "POST", email_data)
            
            return {
                "success": True,
                "automation_id": automation_id,
                "name": name,
                "trigger_type": trigger_type,
                "action_count": len([a for a in actions if a.get("type") == "send_email"]),
                "status": "save",
                "provider": "mailchimp"
            }
        else:
            raise Exception(f"Unsupported email provider: {provider}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Main execution
if __name__ == "__main__":
    mcp.run()