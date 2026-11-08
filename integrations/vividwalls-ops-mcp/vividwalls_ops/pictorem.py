"""Pictorem ArtFlow API client: validate and price product codes, place orders, track them.

Docs: https://www.pictorem.com/artflow/0.1/docs (OpenAPI at /artflow/0.1/openapi/).
Every endpoint is an HTTPS POST with multipart form fields and an ArtFlowKey header."""
import re
from typing import Any, Callable

import httpx

from . import config


class PictoremError(RuntimeError):
    pass


# (endpoint, form fields) -> (HTTP status, JSON body). Pass one in tests to avoid the network.
Transport = Callable[[str, dict[str, str]], tuple[int, dict[str, Any]]]

# Shopify variant format (from orders.parse_variant) -> Pictorem product code body.
# imagewrap: the image continues around the 1.5in (c15) stretcher edges.
FORMAT_CODES = {
    "Canvas, stretched, 1.5in gallery wrap": "canvas|stretched|{o}|{w}|{h}|c15|imagewrap",
    "Canvas, rolled": "canvas|canvasroll|{o}|{w}|{h}",
}

# Free shipping with no quote only covers these countries (Shopify ISO codes).
FREE_SHIPPING_COUNTRIES = {"US", "CA"}


class Pictorem:
    def __init__(self, transport: Transport | None = None):
        self._transport = transport or self._http

    def _http(self, endpoint: str, fields: dict[str, str]) -> tuple[int, dict[str, Any]]:
        try:
            resp = httpx.post(
                f"{config.PICTOREM_API_BASE}/{endpoint}/",
                headers={"ArtFlowKey": config.pictorem_api_key()},
                files={k: (None, v) for k, v in fields.items()},
                timeout=60,
            )
        except httpx.HTTPError as e:
            raise PictoremError(f"Pictorem request failed: {e}") from e
        try:
            return resp.status_code, resp.json()
        except ValueError:
            raise PictoremError(f"Pictorem {endpoint} answered HTTP {resp.status_code} without JSON")

    def call(self, endpoint: str, fields: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        clean = {k: str(v) for k, v in (fields or {}).items() if v is not None and v != ""}
        return self._transport(endpoint, clean)


def errors_of(body: dict[str, Any]) -> list[str]:
    msg = body.get("msg")
    if isinstance(msg, dict):
        return [str(e) for e in msg.get("error", [])]
    if isinstance(msg, list):
        return [str(e) for e in msg]
    return [str(msg)] if msg else []


def orientation(width: int, height: int) -> str:
    return "vertical" if width < height else "horizontal" if width > height else "square"


def product_code(quantity: int, fmt: str, size: str, artwork_orientation: str | None = None) -> str:
    """Raw Pictorem code for a Shopify line, e.g. 1|canvas|stretched|vertical|36|48|c15|imagewrap.
    Shopify sizes are written short side first; a horizontal artwork prints the long side across."""
    match = re.fullmatch(r"(\d+)x(\d+)", size or "")
    if fmt not in FORMAT_CODES or not match:
        raise ValueError(f"no Pictorem product for format {fmt!r} size {size!r}")
    w, h = int(match.group(1)), int(match.group(2))
    if artwork_orientation == "horizontal" and w < h or artwork_orientation == "vertical" and w > h:
        w, h = h, w
    return f"{int(quantity)}|" + FORMAT_CODES[fmt].format(o=orientation(w, h), w=w, h=h)


def canonical_code(pic: Pictorem, code: str) -> str:
    """Run a code through Pictorem's sanitizer and return the exact code it accepts.
    validatepreorder is only true when the code comes back unchanged, so a code that the
    sanitizer merely completed (adding hanging wire, reordering fields) is re-checked."""
    for _ in range(2):
        status, body = pic.call("validatepreorder", {"preordercode": code})
        data = body.get("data") or {}
        if status == 200 and body.get("status") is True:
            return code
        sanitized, problems = data.get("preordersanitize"), data.get("errorlist") or []
        if problems or not sanitized:
            raise PictoremError(f"Pictorem rejected product code {code}: {problems or errors_of(body)}")
        code = sanitized
    raise PictoremError(f"Pictorem kept changing product code {code}")


def price(pic: Pictorem, code: str, province: str = "", country: str = "") -> dict:
    """Your cost for one code in USD (pro discount applied, taxes included)."""
    status, body = pic.call("getprice", {"preordercode": code, "deliveryprovince": province,
                                         "deliverycountry": country})
    sheet = (body.get("worksheet") or {}).get("price") if isinstance(body.get("worksheet"), dict) else None
    if status != 200 or not body.get("status") or not sheet:
        raise PictoremError(f"Pictorem could not price {code}: {errors_of(body)}")
    return {"list": sheet.get("listTotal"), "discount": sheet.get("discountTotal"),
            "subtotal": sheet.get("subTotal"), "total": sheet.get("total")}


def artworks(pic: Pictorem) -> list[dict]:
    """All artworks on the Pictorem account, private albums included (VividWalls keeps them private)."""
    out, page = [], 1
    while True:
        status, body = pic.call("getartworklist", {"limit": 100, "page": page, "includeprivate": 1})
        if status != 200 or not body.get("status"):
            raise PictoremError(f"Pictorem artwork list failed: {errors_of(body)}")
        data = body.get("data") or {}
        for a in data.get("artworks") or []:
            out.append({"collection_id": str(a["id"]), "name": (a.get("name") or "").strip(),
                        "orientation": a.get("orientation"), "ratio": a.get("ratio"),
                        "preview": (a.get("image") or {}).get("preview")})
        if page >= int(data.get("pages") or 1):
            return out
        page += 1


def order_fields(po: str, delivery: dict, lines: list[dict], comment: str = "", testmode: bool = False) -> dict:
    """Flatten an order into the bracketed multipart fields sendorder expects."""
    fields: dict[str, Any] = {"po": po, "ordercomment": comment, "testmode": 1 if testmode else None}
    for k, v in delivery.items():
        fields[f"deliveryInfo[{k}]"] = v
    for i, line in enumerate(lines):
        for k, v in line.items():
            fields[f"orderList[{i}][{k}]"] = v
    return fields


def send_order(pic: Pictorem, po: str, delivery: dict, lines: list[dict], comment: str = "",
               testmode: bool = False) -> dict:
    """Place (or, with testmode, dry-run) an order. A reused PO returns the existing order."""
    status, body = pic.call("sendorder", order_fields(po, delivery, lines, comment, testmode))
    if status == 409 and body.get("duplicate"):
        return {"orderid": body.get("orderid"), "duplicate": True, "message": errors_of(body)}
    if status != 200 or not body.get("status"):
        detail = (body.get("msg") or {}).get("detail") if isinstance(body.get("msg"), dict) else None
        raise PictoremError(f"Pictorem refused the order ({body.get('failedstep') or status}): "
                            f"{errors_of(body)}{f' {detail}' if detail else ''}")
    return {"orderid": body.get("orderid"), "duplicate": False, "testmode": testmode}


def order_status(pic: Pictorem, orderid: str = "", po: str = "") -> dict:
    status, body = pic.call("getorderstatus", {"orderid": orderid, "po": po})
    order = body.get("order")
    if status != 200 or not body.get("status") or not order:
        raise PictoremError(f"Pictorem has no order {orderid or po}: {errors_of(body)}")
    return order
