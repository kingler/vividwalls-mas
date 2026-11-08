"""Order fulfillment: replaces the n8n order-fulfillment, Pictorem and Orders Fulfillment agents."""
import re
from datetime import datetime, timezone

from . import config, pricing
from .gate import blocked
from .shopify import Shopify

UNFULFILLED_QUERY = """
query Unfulfilled($q: String!) {
  orders(first: 50, query: $q, sortKey: CREATED_AT) {
    nodes {
      id name createdAt tags displayFinancialStatus displayFulfillmentStatus
      customer { displayName }
      shippingAddress { name address1 address2 city provinceCode zip countryCodeV2 phone }
      lineItems(first: 20) {
        nodes { title quantity variantTitle product { handle } originalUnitPriceSet { shopMoney { amount } } }
      }
    }
  }
}
"""

TAGS_ADD = """
mutation TagOrder($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) { node { id } userErrors { field message } }
}
"""

FULFILLMENT_ORDERS = """
query FulfillmentOrders($id: ID!) {
  order(id: $id) { name fulfillmentOrders(first: 10) { nodes { id status } } }
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


def is_test_order(order: dict) -> bool:
    name = ((order.get("customer") or {}).get("displayName") or "").strip().lower()
    tags = {t.lower() for t in order.get("tags", [])}
    return name in config.test_customer_names() or "test" in tags


def parse_variant(variant_title: str) -> tuple[str | None, str | None]:
    """'36x48 / Gallery Wrapped Stretched Canvas' -> ('36x48', 'Canvas, stretched, 1.5in gallery wrap')."""
    size_match = re.search(r"(\d+)\s*x\s*(\d+)", variant_title or "", re.I)
    size = f"{size_match.group(1)}x{size_match.group(2)}" if size_match else None
    fmt = next((v for k, v in FORMATS.items() if k in (variant_title or "").lower()), None)
    return size, fmt


def fulfillment_queue(shop: Shopify, now: datetime | None = None) -> list[dict]:
    """Paid, unfulfilled, real orders, oldest first. Over 24 hours old is urgent."""
    now = now or datetime.now(timezone.utc)
    data = shop.run(UNFULFILLED_QUERY, {"q": "financial_status:paid fulfillment_status:unfulfilled"})
    queue = []
    for o in data["orders"]["nodes"]:
        if is_test_order(o):
            continue
        created = datetime.fromisoformat(o["createdAt"].replace("Z", "+00:00"))
        age = (now - created).total_seconds() / 3600
        queue.append({
            "order_id": o["id"], "order": o["name"], "customer": (o.get("customer") or {}).get("displayName"),
            "age_hours": round(age, 1), "urgent": age > 24,
            "sent_to_pictorem": any(t.lower().startswith("pictorem:") for t in o.get("tags", [])),
            "items": [f'{li["quantity"]} x {li["title"]} ({li["variantTitle"]})' for li in o["lineItems"]["nodes"]],
        })
    return queue


def pictorem_order_sheet(order: dict) -> dict:
    """Everything the owner types into the Pictorem pro dashboard for one order."""
    problems = []
    if is_test_order(order):
        problems.append("test order: do not submit")
    if order.get("displayFulfillmentStatus") not in (None, "UNFULFILLED"):
        problems.append(f'already {order["displayFulfillmentStatus"].lower()}: do not order another print')
    if order.get("displayFinancialStatus") != "PAID":
        problems.append(f'payment is {order.get("displayFinancialStatus")}, not PAID')
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
    data = shop.run(UNFULFILLED_QUERY, {"q": f"name:{order_name}"})
    nodes = data["orders"]["nodes"]
    if not nodes:
        return {"ready": False, "problems": [f"order {order_name} not found"]}
    return pictorem_order_sheet(nodes[0])


def record_pictorem_submission(shop: Shopify, order_id: str, pictorem_order_id: str, confirm: bool = False) -> dict:
    tag = f"pictorem:{pictorem_order_id.strip()}"
    preview = blocked(confirm, "tag order with Pictorem order number", {"order_id": order_id, "add_tag": tag})
    if preview:
        return preview
    shop.run(TAGS_ADD, {"id": order_id, "tags": [tag]})
    return {"applied": True, "order_id": order_id, "tag": tag}


def mark_fulfilled(shop: Shopify, order_id: str, tracking_number: str, tracking_url: str = "",
                   carrier: str = "", notify_customer: bool = True, confirm: bool = False) -> dict:
    """Creates the Shopify fulfillment with tracking, which emails the customer."""
    data = shop.run(FULFILLMENT_ORDERS, {"id": order_id})
    open_ids = [f["id"] for f in data["order"]["fulfillmentOrders"]["nodes"] if f["status"] in ("OPEN", "IN_PROGRESS")]
    if not open_ids:
        return {"applied": False, "reason": f'{data["order"]["name"]} has no open fulfillment orders'}
    tracking = {"number": tracking_number}
    if tracking_url:
        tracking["url"] = tracking_url
    if carrier:
        tracking["company"] = carrier
    fulfillment = {
        "lineItemsByFulfillmentOrder": [{"fulfillmentOrderId": i} for i in open_ids],
        "trackingInfo": tracking, "notifyCustomer": notify_customer,
    }
    preview = blocked(confirm, f'mark {data["order"]["name"]} fulfilled', fulfillment)
    if preview:
        return preview
    out = shop.run(FULFILLMENT_CREATE, {"fulfillment": fulfillment})
    return {"applied": True, "fulfillment": out["fulfillmentCreate"]["fulfillment"]}
