"""Order fulfillment: replaces the n8n order-fulfillment, Pictorem and Orders Fulfillment agents."""
import hashlib
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from . import config, pictorem, pricing
from .gate import blocked
from .pictorem import Pictorem
from .shopify import Shopify

ORDER_FIELDS = """
      id name createdAt cancelledAt tags displayFinancialStatus displayFulfillmentStatus
      customer { displayName }
      shippingAddress { name address1 address2 city provinceCode zip countryCodeV2 phone }
      lineItems(first: 50) {
        pageInfo { hasNextPage }
        nodes {
          title quantity variantTitle originalUnitPriceSet { shopMoney { amount } }
          discountedUnitPriceAfterAllDiscountsSet { shopMoney { amount } }
          product {
            id handle
            printCollection: metafield(namespace: "vividwalls", key: "pictorem_collection_id") { value }
            printFileUrl: metafield(namespace: "vividwalls", key: "print_file_url") { value }
          }
        }
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


TEST_ORDER_PROBLEM = "test order: do not submit"


def eligibility_problems(order: dict, names: set[str] | None = None) -> list[str]:
    """Reasons an order must not be printed or marked fulfilled."""
    problems = []
    if is_test_order(order, names):
        problems.append(TEST_ORDER_PROBLEM)
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
    if (order["lineItems"].get("pageInfo") or {}).get("hasNextPage"):
        problems.append("order has more than 50 line items: split it and submit by hand")
    lines = []
    for li in order["lineItems"]["nodes"]:
        size, fmt = parse_variant(li.get("variantTitle", ""))
        if not size or not fmt:
            problems.append(f'cannot read size/format from "{li.get("variantTitle")}"')
        retail = float(li["originalUnitPriceSet"]["shopMoney"]["amount"])
        # The cost check uses what the customer actually paid, after every discount.
        paid = float(((li.get("discountedUnitPriceAfterAllDiscountsSet") or {}).get("shopMoney") or {})
                     .get("amount", retail))
        handle = (li.get("product") or {}).get("handle")
        lines.append({
            "artwork": li["title"], "print_file": handle, "format": fmt, "size": size,
            "quantity": li["quantity"], "retail_each": retail, "paid_each": paid,
            "expected_pictorem_cost_each": pricing.implied_cost(paid),
            "check": "flag if Pictorem quotes more than 10% above expected cost",
        })
    return {
        "order": order["name"], "order_id": order["id"], "ready": not problems, "problems": problems,
        # Enter this as the PO in Pictorem when submitting by hand, so the API never re-orders it.
        "po": purchase_order(order["name"]),
        "ship_to": addr,
        "packing": "Brand as VividWalls; no Pictorem invoice in the box",
        "lines": lines,
    }


def get_order_sheet(shop: Shopify, order_name: str, pic: Pictorem | None = None) -> dict:
    match = ORDER_NAME.match(str(order_name).strip())
    if not match:
        return {"ready": False, "problems": [f'"{order_name}" is not an order number like #1009']}
    name = f"#{match.group(1)}"
    data = shop.run(UNFULFILLED_QUERY, {"q": f"name:{name}"})
    exact = [o for o in data["orders"]["nodes"] if o["name"] == name]
    if not exact:
        return {"ready": False, "problems": [f"order {name} not found"]}
    sheet = pictorem_order_sheet(exact[0], test_names(shop))
    if pic is not None:
        try:
            placed = pictorem.find_order_by_po(pic, sheet["po"])
        except (pictorem.PictoremError, RuntimeError) as e:
            sheet["warnings"] = [f"could not check Pictorem for an existing order ({e}); check before submitting"]
        else:
            if placed:
                sheet["problems"].append(already_placed(placed, sheet["po"]))
                sheet["ready"] = False
    return sheet


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


# --- Pictorem ArtFlow API: quote, submit, track ------------------------------
PRINT_FILE_SET = """
mutation SetPrintFile($metafields: [MetafieldsSetInput!]!, $stale: [MetafieldIdentifierInput!]!) {
  metafieldsSet(metafields: $metafields) { metafields { key value } userErrors { field message } }
  metafieldsDelete(metafields: $stale) { deletedMetafields { key } userErrors { field message } }
}
"""
PRINT_KEYS = ("pictorem_collection_id", "print_file_url")

# A quote more than this far above the pricing rule's implied cost needs the owner's say-so.
QUOTE_TOLERANCE = 1.10


def purchase_order(order_name: str) -> str:
    """Our Pictorem PO for a Shopify order. Pictorem rejects a reused PO, so retries never double-print."""
    return "VW-" + order_name.lstrip("#")


def already_placed(placed: dict, po: str) -> str:
    return (f'already placed with Pictorem as order {placed.get("orderid")} (PO {po}): do not order again; '
            f'tag the Shopify order with record_pictorem_submission(order_id, "{placed.get("orderid")}") if it has no pictorem: tag')


def approval_code(po: str, delivery: dict, lines: list[dict], total: float) -> str:
    """Fingerprint of exactly what will be ordered. The owner approves a preview carrying this code,
    and confirm must present it, so an order that changed since the preview is never charged."""
    blob = json.dumps({"po": po, "delivery": delivery, "lines": lines, "total": round(total, 2)}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def print_source(line_item: dict) -> dict | None:
    """Where Pictorem gets the print file: a Pictorem artwork (collection ID) or a public https file,
    stored on the Shopify product as vividwalls.pictorem_collection_id / vividwalls.print_file_url."""
    product = line_item.get("product") or {}
    collection = ((product.get("printCollection") or {}).get("value") or "").strip()
    file_url = ((product.get("printFileUrl") or {}).get("value") or "").strip()
    if collection:
        return {"collectionID": collection}
    if file_url:
        return {"fileurl": file_url}
    return None


def delivery_info(addr: dict) -> dict:
    parts = (addr.get("name") or "").split()
    return {
        "firstname": parts[0] if parts else "", "lastname": " ".join(parts[1:]) or (parts[0] if parts else ""),
        "address1": addr.get("address1"), "address2": addr.get("address2"), "city": addr.get("city"),
        "province": addr.get("provinceCode"), "country": addr.get("countryCodeV2"),
        "cp": addr.get("zip"), "phone": addr.get("phone"),
    }


def _find_order(shop: Shopify, order_name: str) -> tuple[dict | None, list[str]]:
    match = ORDER_NAME.match(str(order_name).strip())
    if not match:
        return None, [f'"{order_name}" is not an order number like #1009']
    name = f"#{match.group(1)}"
    exact = [o for o in shop.run(UNFULFILLED_QUERY, {"q": f"name:{name}"})["orders"]["nodes"] if o["name"] == name]
    return (exact[0], []) if exact else (None, [f"order {name} not found"])


def quote_order(shop: Shopify, pic: Pictorem, order_name: str, accept_quote: bool = False,
                allow_test: bool = False) -> dict:
    """Validate and price an order with Pictorem without placing it. `ready` is false with `problems`
    when it must not be submitted. A quote above the expected cost is a problem unless accept_quote.
    allow_test lets a test order through, only for sandbox rehearsals (nothing is created or charged)."""
    order, problems = _find_order(shop, order_name)
    if not order:
        return {"ready": False, "problems": problems}
    sheet = pictorem_order_sheet(order, test_names(shop))
    problems = [p for p in sheet["problems"] if not (allow_test and p == TEST_ORDER_PROBLEM)]
    rehearsal = allow_test and TEST_ORDER_PROBLEM in sheet["problems"]
    sent = [t for t in order.get("tags", []) if re.fullmatch(r"pictorem:\S+", t, re.I)]
    if sent:
        problems.append(f"already sent to Pictorem ({sent[0]}): do not order another print")
    elif placed := pictorem.find_order_by_po(pic, purchase_order(sheet["order"])):
        # Pictorem accepted it but the Shopify tag never landed (crash, lost reply, failed tag).
        problems.append(already_placed(placed, purchase_order(sheet["order"])))
    addr = order.get("shippingAddress") or {}
    country = addr.get("countryCodeV2") or ""
    if country and country not in pictorem.FREE_SHIPPING_COUNTRIES:
        problems.append(f"ships to {country}: only US and Canada orders ship without a quote; submit it by hand")
    art_orientation = {}
    lines, total, expected_total = [], 0.0, 0.0
    for sheet_line, li in zip(sheet["lines"], order["lineItems"]["nodes"]):
        line = dict(sheet_line)
        source = print_source(li)
        if not source:
            problems.append(f'no print file for "{li["title"]}": set one with set_print_file')
        elif "fileurl" in source and not file_type(source["fileurl"]):
            problems.append(f'"{li["title"]}": print file must end in .jpg, .png or .tif (Pictorem needs the file type)')
        elif "fileurl" in source and (file_issue := pic.file_problem(source["fileurl"])):
            problems.append(f'"{li["title"]}": {file_issue}')
        if not (sheet_line["size"] and sheet_line["format"]):
            lines.append(line)
            continue
        if source and "collectionID" in source and not art_orientation:
            art_orientation = {a["collection_id"]: a["orientation"] for a in pictorem.artworks(pic)}
        if source and "collectionID" in source and source["collectionID"] not in art_orientation:
            problems.append(f'"{li["title"]}": Pictorem artwork {source["collectionID"]} not found on the account')
        try:
            code = pictorem.canonical_code(pic, pictorem.product_code(
                li["quantity"], sheet_line["format"], sheet_line["size"],
                art_orientation.get((source or {}).get("collectionID", ""))))
            cost = pictorem.price(pic, code, addr.get("provinceCode") or "", country)
        except (pictorem.PictoremError, ValueError) as e:
            problems.append(f'"{li["title"]}": {e}')
            lines.append(line)
            continue
        expected = round(sheet_line["expected_pictorem_cost_each"] * li["quantity"], 2)
        line.update({"code": code, "source": source, "pictorem_cost": cost["total"], "expected_cost": expected})
        if cost["total"] > expected * QUOTE_TOLERANCE and not accept_quote:
            problems.append(f'"{li["title"]}": Pictorem quotes ${cost["total"]:.2f}, more than 10% above the '
                            f'expected ${expected:.2f}; check the price, then pass accept_quote=true to proceed')
        total += cost["total"]
        expected_total += expected
        lines.append(line)
    po = purchase_order(sheet["order"])
    quote = {
        "order": sheet["order"], "order_id": sheet["order_id"], "po": po,
        "ready": not problems, "problems": problems, "ship_to": addr, "lines": lines,
        "pictorem_total": round(total, 2), "expected_total": round(expected_total, 2),
        "shipping": "free (US/Canada, no quote sent)",
    }
    if rehearsal:
        quote["rehearsal"] = "test order: accepted for a sandbox rehearsal only, never for a real submit"
    if quote["ready"]:
        quote["approval_code"] = approval_code(po, delivery_info(addr), _order_lines(quote), total)
    return quote


FILE_TYPES = {"jpg": "jpg", "jpeg": "jpg", "png": "png", "tif": "tiff", "tiff": "tiff"}


def file_type(url: str) -> str | None:
    """Pictorem's filetype for a print-file URL (required with fileurl): jpg, png or tiff."""
    ext = urlparse(url).path.rsplit(".", 1)[-1].lower() if "." in urlparse(url).path else ""
    return FILE_TYPES.get(ext)


def _order_lines(quote: dict) -> list[dict]:
    lines = []
    for ln in quote["lines"]:
        line = {"code": ln["code"], **ln["source"], "comment": ln.get("print_file") or ln["artwork"]}
        if "fileurl" in line:
            line["filetype"] = file_type(line["fileurl"])
        lines.append(line)
    return lines


def submit_order(shop: Shopify, pic: Pictorem, order_name: str, confirm: bool = False,
                 sandbox: bool = False, accept_quote: bool = False, approval_code: str = "") -> dict:
    """Place a Shopify order with Pictorem through the ArtFlow API, then tag the Shopify order.
    sandbox=true runs Pictorem's full pipeline in test mode (nothing created, charged or emailed); it
    also accepts test orders, so the flow can be rehearsed on one.
    A real order previews unless confirm=true and writes are switched on, because it charges the card.
    confirm must carry the approval_code from the preview the owner approved; if anything changed
    since (address, items, print file, Pictorem price), the codes differ and nothing is ordered."""
    # Test orders may be rehearsed in Pictorem's test mode (nothing created or charged), never placed.
    quote = quote_order(shop, pic, order_name, accept_quote, allow_test=sandbox)
    if not quote["ready"]:
        return {"applied": False, "errors": quote["problems"], "quote": quote}
    delivery = delivery_info(quote["ship_to"])
    lines = _order_lines(quote)
    comment = f'VividWalls Shopify order {quote["order"]}'
    if sandbox:
        result = pictorem.send_order(pic, quote["po"], delivery, lines, comment, testmode=True)
        return {"applied": False, "sandbox": True, "accepted_by_pictorem": True, "result": result, "quote": quote}
    change = {"po": quote["po"], "ship_to": delivery, "lines": lines, "pictorem_total": quote["pictorem_total"],
              "expected_total": quote["expected_total"], "approval_code": quote["approval_code"]}
    preview = blocked(confirm, f'order {quote["order"]} from Pictorem (charges about ${quote["pictorem_total"]:.2f})',
                      change)
    if preview:
        return preview
    if str(approval_code or "").strip() != quote["approval_code"]:
        return {"applied": False, "errors": [
            "approval_code does not match the current order: it changed since the preview, or no code was given. "
            "Show the owner this new preview and confirm with its approval_code."], "change": change}
    try:
        result = pictorem.send_order(pic, quote["po"], delivery, lines, comment)
    except pictorem.PictoremError as e:
        raise pictorem.PictoremError(
            f"{e}. If this was a network error the order may still have reached Pictorem: run "
            f"pictorem_order_status for {quote['order']} before trying again (the PO {quote['po']} blocks a duplicate)."
        ) from e
    tag = f'pictorem:{result["orderid"]}'
    out = {"applied": True, "pictorem_order_id": result["orderid"], "duplicate": result["duplicate"],
           "po": quote["po"], "tag": tag, "pictorem_total": quote["pictorem_total"]}
    try:
        shop.run(TAGS_ADD, {"id": quote["order_id"], "tags": [tag]})
    except Exception as e:  # the order is placed; never hide its ID behind a tagging error
        out["tag"] = None
        out["warning"] = (f"Pictorem order {result['orderid']} was placed but tagging Shopify failed ({e}); "
                          f'run record_pictorem_submission(order_id, "{result["orderid"]}")')
    return out


def pictorem_status(pic: Pictorem, order: str = "", pictorem_order_id: str = "") -> dict:
    """Pictorem status for a Shopify order number (looked up by our PO) or a Pictorem order ID.
    `ready_to_mark_fulfilled` is true once Pictorem has a tracking number."""
    if pictorem_order_id:
        data = pictorem.order_status(pic, orderid=str(pictorem_order_id).strip())
    else:
        match = ORDER_NAME.match(str(order).strip())
        if not match:
            return {"error": f'"{order}" is not an order number like #1009'}
        data = pictorem.order_status(pic, po=purchase_order(match.group(1)))
    return {
        "pictorem_order_id": data.get("orderid"), "po": data.get("po"),
        "order_status": data.get("order_status_label"), "production": data.get("production_status_label"),
        "progress_pct": data.get("production_progress"), "billing": data.get("billing_status_label"),
        "tracking_number": data.get("tracking_number"), "carrier": data.get("tracking_carrier"),
        "total": data.get("total"), "ready_to_mark_fulfilled": bool(data.get("tracking_number")),
    }


def set_print_file(shop: Shopify, product_id: str, collection_id: str = "", file_url: str = "",
                   confirm: bool = False) -> dict:
    """Store which file Pictorem prints for a product: a Pictorem artwork ID (from pictorem_artworks)
    or a public https print file. Exactly one. Previews unless confirm=true and writes are switched on."""
    collection_id, file_url = str(collection_id or "").strip(), str(file_url or "").strip()
    if bool(collection_id) == bool(file_url):
        return {"applied": False, "errors": ["give exactly one of collection_id or file_url"]}
    if collection_id and not collection_id.isdigit():
        return {"applied": False, "errors": ["collection_id must be the numeric Pictorem artwork ID"]}
    if file_url and (problem := pictorem.public_https_problem(file_url, resolve=True)):
        return {"applied": False, "errors": [problem]}
    if file_url and not file_type(file_url):
        return {"applied": False, "errors": ["file_url must end in .jpg, .png or .tif (Pictorem needs the file type)"]}
    key, value, kind = (("pictorem_collection_id", collection_id, "single_line_text_field") if collection_id
                        else ("print_file_url", file_url, "url"))
    fields = [{"ownerId": product_id, "namespace": config.METAFIELD_NAMESPACE, "key": key, "type": kind,
               "value": value}]
    preview = blocked(confirm, "set the product's Pictorem print file", {"product_id": product_id, key: value})
    if preview:
        return preview
    # Remove the other kind of print source: print_source prefers the collection ID, so a stale one
    # would keep printing the old artwork.
    other = next(k for k in PRINT_KEYS if k != key)
    stale = [{"ownerId": product_id, "namespace": config.METAFIELD_NAMESPACE, "key": other}]
    shop.run(PRINT_FILE_SET, {"metafields": fields, "stale": stale})
    return {"applied": True, "product_id": product_id, key: value, "cleared": other}
