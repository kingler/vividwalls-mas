"""Order fulfillment: replaces the n8n order-fulfillment, Pictorem and Orders Fulfillment agents."""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from . import config, pricing
from .gate import blocked
from .shopify import Shopify

ORDER_FIELDS = """
      id name createdAt cancelledAt tags displayFinancialStatus displayFulfillmentStatus
      customer { displayName }
      shippingAddress { name address1 address2 city provinceCode zip countryCodeV2 phone }
      lineItems(first: 20) {
        nodes { title quantity variantTitle product { handle } originalUnitPriceSet { shopMoney { amount } } }
      }
"""

UNFULFILLED_QUERY = """
query Unfulfilled($q: String!) {
  orders(first: 50, query: $q, sortKey: CREATED_AT) { nodes {""" + ORDER_FIELDS + """} }
}
"""

ORDER_QUERY = """
query OrderById($id: ID!) {
  order(id: $id) {""" + ORDER_FIELDS + """    fulfillmentOrders(first: 10) { nodes { id status } }
  }
}
"""

OWNER_QUERY = "query Owner { shop { shopOwnerName } }"

TAGS_ADD = """
mutation TagOrder($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) { node { id } userErrors { field message } }
}
"""

FULFILLMENT_CREATE = """
mutation Fulfill($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment { id status trackingInfo { number url company } }
    userErrors { field message }
  }
}
"""

FORMATS = {
    "gallery wrapped stretched canvas": "Canvas, stretched, 1.5in gallery wrap",
    "canvas roll": "Canvas, rolled",
}

# Tracking links go into customer emails, so only carrier sites are accepted.
CARRIER_DOMAINS = ("ups.com", "fedex.com", "usps.com", "dhl.com", "canadapost.ca",
                   "canadapost-postescanada.ca", "purolator.com", "pictorem.com")

ORDER_NAME = re.compile(r"^#?(\d{1,10})$")
PICTOREM_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def test_names(shop: Shopify) -> set[str]:
    """Configured test customers plus the store owner (CLAUDE.md rule 3)."""
    if getattr(shop, "_test_names", None) is None:
        owner = shop.run(OWNER_QUERY)["shop"].get("shopOwnerName") or ""
        shop._test_names = config.test_customer_names() | ({owner.strip().lower()} if owner.strip() else set())
    return shop._test_names


def is_test_order(order: dict, names: set[str] | None = None) -> bool:
    name = ((order.get("customer") or {}).get("displayName") or "").strip().lower()
    tags = {t.lower() for t in order.get("tags", [])}
    return name in (names if names is not None else config.test_customer_names()) or "test" in tags


def parse_variant(variant_title: str) -> tuple[str | None, str | None]:
    """'36x48 / Gallery Wrapped Stretched Canvas' -> ('36x48', 'Canvas, stretched, 1.5in gallery wrap')."""
    size_match = re.search(r"(\d+)\s*x\s*(\d+)", variant_title or "", re.I)
    size = f"{size_match.group(1)}x{size_match.group(2)}" if size_match else None
    fmt = next((v for k, v in FORMATS.items() if k in (variant_title or "").lower()), None)
    return size, fmt


def _created(order: dict) -> datetime:
    return datetime.fromisoformat(order["createdAt"].replace("Z", "+00:00"))


def fulfillment_queue(shop: Shopify, now: datetime | None = None) -> list[dict]:
    """Paid, unfulfilled, real orders, oldest first. Over 24 hours old is urgent."""
    now = now or datetime.now(timezone.utc)
    names = test_names(shop)
    data = shop.run(UNFULFILLED_QUERY, {"q": "financial_status:paid fulfillment_status:unfulfilled"})
    live = [o for o in data["orders"]["nodes"] if not o.get("cancelledAt") and not is_test_order(o, names)]
    queue = []
    for o in sorted(live, key=_created):
        age = (now - _created(o)).total_seconds() / 3600
        queue.append({
            "order_id": o["id"], "order": o["name"], "customer": (o.get("customer") or {}).get("displayName"),
            "age_hours": round(age, 1), "urgent": age > 24,
            "sent_to_pictorem": any(re.fullmatch(r"pictorem:\S+", t, re.I) for t in o.get("tags", [])),
            "items": [f'{li["quantity"]} x {li["title"]} ({li["variantTitle"]})' for li in o["lineItems"]["nodes"]],
        })
    return queue


def eligibility_problems(order: dict, names: set[str] | None = None) -> list[str]:
    """Reasons an order must not be printed or marked fulfilled."""
    problems = []
    if is_test_order(order, names):
        problems.append("test order: do not submit")
    if order.get("cancelledAt"):
        problems.append("order was cancelled")
    if order.get("displayFulfillmentStatus") not in (None, "UNFULFILLED"):
        problems.append(f'already {order["displayFulfillmentStatus"].lower()}: do not order another print')
    if order.get("displayFinancialStatus") != "PAID":
        problems.append(f'payment is {order.get("displayFinancialStatus")}, not PAID')
    return problems


def pictorem_order_sheet(order: dict, names: set[str] | None = None) -> dict:
    """Everything the owner types into the Pictorem pro dashboard for one order."""
    problems = eligibility_problems(order, names)
    addr = order.get("shippingAddress") or {}
    for field in ("name", "address1", "city", "zip", "countryCodeV2"):
        if not addr.get(field):
            problems.append(f"shipping address missing {field}")
    lines = []
    for li in order["lineItems"]["nodes"]:
        size, fmt = parse_variant(li.get("variantTitle", ""))
        if not size or not fmt:
            problems.append(f'cannot read size/format from "{li.get("variantTitle")}"')
        retail = float(li["originalUnitPriceSet"]["shopMoney"]["amount"])
        handle = (li.get("product") or {}).get("handle")
        lines.append({
            "artwork": li["title"], "print_file": handle, "format": fmt, "size": size,
            "quantity": li["quantity"], "retail_each": retail,
            "expected_pictorem_cost_each": pricing.implied_cost(retail),
            "check": "flag if Pictorem quotes more than 10% above expected cost",
        })
    return {
        "order": order["name"], "order_id": order["id"], "ready": not problems, "problems": problems,
        "ship_to": addr,
        "packing": "Brand as VividWalls; no Pictorem invoice in the box",
        "lines": lines,
    }


def get_order_sheet(shop: Shopify, order_name: str) -> dict:
    match = ORDER_NAME.match(str(order_name).strip())
    if not match:
        return {"ready": False, "problems": [f'"{order_name}" is not an order number like #1009']}
    name = f"#{match.group(1)}"
    data = shop.run(UNFULFILLED_QUERY, {"q": f"name:{name}"})
    exact = [o for o in data["orders"]["nodes"] if o["name"] == name]
    if not exact:
        return {"ready": False, "problems": [f"order {name} not found"]}
    return pictorem_order_sheet(exact[0], test_names(shop))


def record_pictorem_submission(shop: Shopify, order_id: str, pictorem_order_id: str, confirm: bool = False) -> dict:
    pid = str(pictorem_order_id).strip()
    if not PICTOREM_ID.match(pid):
        return {"applied": False, "errors": ["pictorem_order_id must be the Pictorem order number (letters, digits, - or _)"]}
    tag = f"pictorem:{pid}"
    preview = blocked(confirm, "tag order with Pictorem order number", {"order_id": order_id, "add_tag": tag})
    if preview:
        return preview
    shop.run(TAGS_ADD, {"id": order_id, "tags": [tag]})
    return {"applied": True, "order_id": order_id, "tag": tag}


def tracking_url_problem(url: str) -> str | None:
    parts = urlparse(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https":
        return "tracking_url must start with https://"
    if not any(host == d or host.endswith("." + d) for d in CARRIER_DOMAINS):
        return f"tracking_url must be on a carrier site ({', '.join(CARRIER_DOMAINS)}); leave it empty and pass carrier instead"
    return None


def mark_fulfilled(shop: Shopify, order_id: str, tracking_number: str, tracking_url: str = "",
                   carrier: str = "", notify_customer: bool = True, confirm: bool = False) -> dict:
    """Creates the Shopify fulfillment with tracking, which emails the customer."""
    if not str(tracking_number).strip():
        return {"applied": False, "errors": ["tracking_number is required"]}
    if tracking_url and (problem := tracking_url_problem(tracking_url)):
        return {"applied": False, "errors": [problem]}
    order = shop.run(ORDER_QUERY, {"id": order_id})["order"]
    if not order:
        return {"applied": False, "errors": [f"order {order_id} not found"]}
    problems = eligibility_problems(order, test_names(shop))
    if problems:
        return {"applied": False, "errors": problems}
    open_ids = [f["id"] for f in order["fulfillmentOrders"]["nodes"] if f["status"] in ("OPEN", "IN_PROGRESS")]
    if not open_ids:
        return {"applied": False, "errors": [f'{order["name"]} has no open fulfillment orders']}
    tracking = {"number": str(tracking_number).strip()}
    if tracking_url:
        tracking["url"] = tracking_url
    if carrier:
        tracking["company"] = carrier
    fulfillment = {
        "lineItemsByFulfillmentOrder": [{"fulfillmentOrderId": i} for i in open_ids],
        "trackingInfo": tracking, "notifyCustomer": notify_customer,
    }
    preview = blocked(confirm, f'mark {order["name"]} fulfilled', fulfillment)
    if preview:
        return preview
    out = shop.run(FULFILLMENT_CREATE, {"fulfillment": fulfillment})
    return {"applied": True, "fulfillment": out["fulfillmentCreate"]["fulfillment"]}
