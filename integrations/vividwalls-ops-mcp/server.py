"""VividWalls Ops MCP server: the n8n workflows as tools for Claude agents.

Store-changing tools preview by default. They only act with confirm=true AND
VIVIDWALLS_ALLOW_WRITES=1, so scheduled runs (which don't set it) can only draft."""
from functools import wraps

import httpx

from mcp.server.fastmcp import FastMCP

from vividwalls_ops import catalog, marketing, orders, pictorem, pricing
from vividwalls_ops.pictorem import Pictorem
from vividwalls_ops.shopify import Shopify, ShopifyError

mcp = FastMCP("vividwalls-ops")
_shop: Shopify | None = None


_pic: Pictorem | None = None


def shop() -> Shopify:
    global _shop
    _shop = _shop or Shopify()
    return _shop


def pic() -> Pictorem:
    global _pic
    _pic = _pic or Pictorem()
    return _pic


def safe(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ShopifyError, RuntimeError, ValueError) as e:
            return {"error": str(e)}
        except httpx.HTTPError as e:
            return {"error": f"Shopify request failed: {e}"}
    return wrapper


# --- Operations: orders and Pictorem fulfillment -------------------------
@mcp.tool()
@safe
def fulfillment_queue() -> list | dict:
    """List paid, unfulfilled, real customer orders (test orders excluded), oldest first.
    Each shows age in hours, whether it is urgent (over 24h) and whether it was already sent to Pictorem."""
    return orders.fulfillment_queue(shop())


@mcp.tool()
@safe
def pictorem_order_sheet(order_name: str) -> dict:
    """Build the exact Pictorem order sheet for one order (e.g. '#1009'): print file, format, size,
    quantity, ship-to address, packing note and expected cost. `ready` is false with `problems` if the
    order must not be submitted (unpaid, test order, missing address, unreadable variant)."""
    return orders.get_order_sheet(shop(), order_name if order_name.startswith("#") else f"#{order_name}")


@mcp.tool()
@safe
def record_pictorem_submission(order_id: str, pictorem_order_id: str, confirm: bool = False) -> dict:
    """After the owner submits an order in Pictorem, tag the Shopify order with 'pictorem:<id>'.
    Previews unless confirm=true and writes are switched on."""
    return orders.record_pictorem_submission(shop(), order_id, pictorem_order_id, confirm)


@mcp.tool()
@safe
def mark_fulfilled(order_id: str, tracking_number: str, tracking_url: str = "", carrier: str = "",
                   notify_customer: bool = True, confirm: bool = False) -> dict:
    """Mark a Shopify order fulfilled with Pictorem's tracking number (emails the customer by default).
    Refuses test, cancelled, unpaid or already-fulfilled orders. tracking_url must be https on a carrier
    site (UPS, FedEx, USPS, DHL, Canada Post, Purolator, Pictorem); otherwise pass only carrier.
    Previews unless confirm=true and writes are switched on."""
    return orders.mark_fulfilled(shop(), order_id, tracking_number, tracking_url, carrier, notify_customer, confirm)


# --- Pictorem ArtFlow API: automated ordering -------------------------------
@mcp.tool()
@safe
def pictorem_quote_order(order_name: str, accept_quote: bool = False) -> dict:
    """Validate and price an order (e.g. '#1009') with Pictorem's API without placing it: the exact
    product codes, print files, your Pictorem cost per line and in total, and the expected cost from the
    pricing rule. `ready` is false with `problems` when it must not be submitted (test/unpaid/fulfilled
    order, already sent, no print file set, outside US/Canada, or a quote over 10% above expected)."""
    return orders.quote_order(shop(), pic(), order_name, accept_quote)


@mcp.tool()
@safe
def pictorem_submit_order(order_name: str, confirm: bool = False, sandbox: bool = False,
                          accept_quote: bool = False) -> dict:
    """Place a paid Shopify order with Pictorem through its API and tag the Shopify order 'pictorem:<id>'.
    This charges the business card. Previews unless confirm=true and writes are switched on; call with
    confirm=true only after the owner approves the preview. sandbox=true sends it through Pictorem's test
    mode instead (validated end to end, nothing created or charged). Safe to retry: the PO 'VW-<number>'
    stops a second print of the same order."""
    return orders.submit_order(shop(), pic(), order_name, confirm, sandbox, accept_quote)


@mcp.tool()
@safe
def pictorem_order_status(order_name: str = "", pictorem_order_id: str = "") -> dict:
    """Pictorem status for a Shopify order number or a Pictorem order ID: order and production stage,
    progress, tracking number and carrier. When `ready_to_mark_fulfilled` is true, call mark_fulfilled."""
    return orders.pictorem_status(pic(), order_name, pictorem_order_id)


@mcp.tool()
@safe
def pictorem_artworks(search: str = "") -> list | dict:
    """Artworks on the Pictorem account (private albums included) with their collection IDs, to link a
    Shopify product to its print file with set_print_file. Optional search filters by name."""
    found = pictorem.artworks(pic())
    words = search.lower().split()
    return [a for a in found if all(w in a["name"].lower() for w in words)]


@mcp.tool()
@safe
def set_print_file(product_id: str, collection_id: str = "", file_url: str = "", confirm: bool = False) -> dict:
    """Link a Shopify product to the file Pictorem prints: a Pictorem artwork collection_id (from
    pictorem_artworks) or a public https file_url. Exactly one. Orders for products without one are refused.
    Previews unless confirm=true and writes are switched on."""
    return orders.set_print_file(shop(), product_id, collection_id, file_url, confirm)


# --- Pricing --------------------------------------------------------------
@mcp.tool()
def price_check(retail: float, pictorem_cost: float) -> dict:
    """Check a retail price against the rule (Pictorem cost x 2.065) and the 1.8x floor."""
    return pricing.check_price(retail, pictorem_cost)


# --- Catalog: artwork profiles and search ---------------------------------
@mcp.tool()
@safe
def unprofiled_artworks() -> list | dict:
    """Active artworks with no colour/mood/room profile yet. Look at each image, then save_artwork_profile."""
    return catalog.unprofiled_artworks(shop())


@mcp.tool()
@safe
def save_artwork_profile(product_id: str, dominant_colors: list[str], color_temperature: str,
                         moods: list[str], rooms: list[str], confirm: bool = False) -> dict:
    """Store an artwork's profile on the Shopify product (namespace 'vividwalls').
    dominant_colors: 1-6 plain colour names. color_temperature: warm | cool | neutral.
    moods: 1-3 of bold, calm, dramatic, energetic, minimal, moody, playful, serene, sophisticated, warm.
    rooms: 1-4 of living room, bedroom, office, dining room, entryway, hospitality, kids room.
    Previews unless confirm=true and writes are switched on."""
    profile = {"dominant_colors": dominant_colors, "color_temperature": color_temperature,
               "moods": moods, "rooms": rooms}
    return catalog.save_artwork_profile(shop(), product_id, profile, confirm)


@mcp.tool()
@safe
def search_artworks(colors: list[str] | None = None, moods: list[str] | None = None, room: str = "",
                    temperature: str = "", max_price: float | None = None, limit: int = 5) -> dict:
    """Recommend artworks by colour, mood, room and budget, best fit first, with the reasons.
    Use for customer questions ('something calm and blue for a bedroom under $250') and B2B curation."""
    return catalog.search_artworks(shop(), colors, moods, room, temperature, max_price, limit)


# --- Marketing ------------------------------------------------------------
@mcp.tool()
def utm_link(url: str, source: str, campaign: str, medium: str = "social", content: str = "") -> str:
    """Add consistent UTM tags to a store link so the weekly review can attribute traffic."""
    return marketing.utm_link(url, source, campaign, medium, content)


@mcp.tool()
@safe
def pin_drafts(title: str, product_url: str, campaign: str, rooms: list[str], image_url: str,
               board_id: str = "") -> list | dict:
    """Draft Pinterest pins (one per room angle) with UTM links and the exact arguments of the
    pinterest server's create_pin. image_url: public https image (e.g. a room mockup on cdn.shopify.com).
    Publish only after the owner approves."""
    return marketing.pin_drafts(title, product_url, campaign, rooms, image_url, board_id)


if __name__ == "__main__":
    mcp.run()
