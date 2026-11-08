import json
import re
from datetime import datetime, timezone

import pytest

from vividwalls_ops import catalog, gate, marketing, orders, pricing
from vividwalls_ops.shopify import Shopify, ShopifyError

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def order(name, customer="Jane Buyer", created="2026-11-08T08:00:00Z", status="PAID", tags=(), variant="36x48 / Gallery Wrapped Stretched Canvas", price="315.94", cancelled=None):
    return {
        "id": f"gid://shopify/Order/{name}", "name": f"#{name}", "createdAt": created, "cancelledAt": cancelled, "tags": list(tags),
        "displayFinancialStatus": status, "displayFulfillmentStatus": "UNFULFILLED",
        "customer": {"displayName": customer},
        "shippingAddress": {"name": customer, "address1": "1 Main St", "address2": None, "city": "Newark",
                            "provinceCode": "NJ", "zip": "07102", "countryCodeV2": "US", "phone": None},
        "lineItems": {"nodes": [{"title": "Noir Mosaic no1", "quantity": 1, "variantTitle": variant,
                                 "product": {"handle": "noir-mosaic-no1"},
                                 "originalUnitPriceSet": {"shopMoney": {"amount": price}}}]},
    }


class FakeShop(Shopify):
    """Records calls and answers from a canned response per operation name."""
    def __init__(self, responses):
        self.calls = []
        super().__init__(transport=self._answer)
        self.responses = {"Owner": {"data": {"shop": {"shopOwnerName": "Store Owner"}}}, **responses}

    def _answer(self, query, variables):
        op = re.search(r"(?:query|mutation)\s+(\w+)", query).group(1)
        self.calls.append((op, variables))
        return self.responses[op]


# --- pricing -------------------------------------------------------------
def test_pricing_rule_and_floor():
    assert pricing.retail_price(98.79) == 204.0
    assert pricing.implied_cost(204.0) == 98.79
    assert pricing.check_price(204, 98.79)["meets_floor"] is True
    low = pricing.check_price(150, 98.79)
    assert low["meets_floor"] is False and low["standard_price"] == 204.0


# --- orders --------------------------------------------------------------
def test_test_orders_are_excluded(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_TEST_CUSTOMERS", "Test User, Store Owner")
    assert orders.is_test_order(order("1", customer="Test User"))
    assert orders.is_test_order(order("2", customer="store owner"))
    assert orders.is_test_order(order("3", tags=["test"]))
    assert not orders.is_test_order(order("4"))


def test_fulfillment_queue_marks_urgent_and_skips_tests(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_TEST_CUSTOMERS", "Test User")
    shop = FakeShop({"Unfulfilled": {"data": {"orders": {"nodes": [   # newest first on purpose
        order("11", created="2026-11-08T10:00:00Z", tags=["pictorem:PX-1"]),
        order("10", created="2026-11-06T08:00:00Z"),
        order("12", customer="Test User"),
        order("13", customer="Store Owner"),          # shop owner: always a test order
        order("14", cancelled="2026-11-07T00:00:00Z"),
    ]}}}})
    q = orders.fulfillment_queue(shop, now=NOW)
    assert [o["order"] for o in q] == ["#10", "#11"]
    assert q[0]["urgent"] and not q[1]["urgent"]
    assert q[1]["sent_to_pictorem"] and not q[0]["sent_to_pictorem"]
    assert ("Unfulfilled", {"q": "financial_status:paid fulfillment_status:unfulfilled"}) in shop.calls


@pytest.mark.parametrize("title,size,fmt", [
    ("36x48 / Gallery Wrapped Stretched Canvas", "36x48", "Canvas, stretched, 1.5in gallery wrap"),
    ("24x36 / Canvas Roll", "24x36", "Canvas, rolled"),
    ("53 x 72 / Gallery Wrapped Stretched Canvas", "53x72", "Canvas, stretched, 1.5in gallery wrap"),
    ("Default Title", None, None),
])
def test_parse_variant(title, size, fmt):
    assert orders.parse_variant(title) == (size, fmt)


def test_order_sheet_ready_and_cost_check():
    sheet = orders.pictorem_order_sheet(order("20"))
    assert sheet["ready"] and not sheet["problems"]
    line = sheet["lines"][0]
    assert line["size"] == "36x48" and line["print_file"] == "noir-mosaic-no1"
    assert line["expected_pictorem_cost_each"] == 153.0


def test_order_sheet_flags_problems(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_TEST_CUSTOMERS", "Test User")
    bad = order("21", customer="Test User", status="PENDING", variant="Default Title")
    bad["shippingAddress"]["zip"] = ""
    problems = " | ".join(orders.pictorem_order_sheet(bad)["problems"])
    for expected in ("test order", "PENDING", "zip", "size/format"):
        assert expected in problems


def test_order_sheet_refuses_already_fulfilled_order():
    done = order("22")
    done["displayFulfillmentStatus"] = "FULFILLED"
    sheet = orders.pictorem_order_sheet(done)
    assert not sheet["ready"] and any("already fulfilled" in p for p in sheet["problems"])


# --- approval gate -------------------------------------------------------
def test_writes_need_confirm_and_switch(monkeypatch):
    shop = FakeShop({"TagOrder": {"data": {"tagsAdd": {"node": {"id": "x"}, "userErrors": []}}}})
    monkeypatch.delenv("VIVIDWALLS_ALLOW_WRITES", raising=False)
    r = orders.record_pictorem_submission(shop, "gid://shopify/Order/1", "PX-9")
    assert r["applied"] is False and "preview" in r["reason"]
    r = orders.record_pictorem_submission(shop, "gid://shopify/Order/1", "PX-9", confirm=True)
    assert r["applied"] is False and "switched off" in r["reason"]
    assert shop.calls == []
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    r = orders.record_pictorem_submission(shop, "gid://shopify/Order/1", "PX-9", confirm=True)
    assert r["applied"] and shop.calls == [("TagOrder", {"id": "gid://shopify/Order/1", "tags": ["pictorem:PX-9"]})]


def order_with_fos(o):
    return {"data": {"order": {**o, "fulfillmentOrders": {"nodes": [
        {"id": "FO1", "status": "OPEN"}, {"id": "FO2", "status": "CLOSED"}]}}}}


def test_mark_fulfilled_uses_open_fulfillment_orders(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    shop = FakeShop({
        "OrderById": order_with_fos(order("30")),
        "Fulfill": {"data": {"fulfillmentCreate": {"fulfillment": {"id": "F1", "status": "SUCCESS",
                    "trackingInfo": [{"number": "1Z9"}]}, "userErrors": []}}},
    })
    r = orders.mark_fulfilled(shop, "gid://shopify/Order/30", "1Z9", carrier="UPS", confirm=True)
    assert r["applied"]
    sent = [v for op, v in shop.calls if op == "Fulfill"][0]["fulfillment"]
    assert sent["lineItemsByFulfillmentOrder"] == [{"fulfillmentOrderId": "FO1"}]
    assert sent["trackingInfo"] == {"number": "1Z9", "company": "UPS"} and sent["notifyCustomer"] is True


def test_shopify_user_errors_raise():
    shop = FakeShop({"TagOrder": {"data": {"tagsAdd": {"node": None, "userErrors": [{"message": "bad id"}]}}}})
    with pytest.raises(ShopifyError):
        shop.run(orders.TAGS_ADD, {})


# --- catalog -------------------------------------------------------------
GOOD_PROFILE = {"dominant_colors": ["Black", "White"], "color_temperature": "Neutral",
                "moods": ["minimal", "sophisticated"], "rooms": ["office", "living room"]}


def test_profile_validation():
    clean, errors = catalog.validate_profile(GOOD_PROFILE)
    assert not errors and clean["dominant_colors"] == ["black", "white"] and clean["color_temperature"] == "neutral"
    _, errors = catalog.validate_profile({"dominant_colors": [], "color_temperature": "hot",
                                          "moods": ["angry"], "rooms": ["garage"]})
    assert len(errors) == 4


def test_save_profile_writes_four_metafields(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    shop = FakeShop({"SaveProfile": {"data": {"metafieldsSet": {"metafields": [], "userErrors": []}}}})
    r = catalog.save_artwork_profile(shop, "gid://shopify/Product/1", GOOD_PROFILE, confirm=True)
    assert r["applied"]
    fields = {f["key"]: f for f in shop.calls[0][1]["metafields"]}
    assert set(fields) == {"dominant_colors", "moods", "rooms", "color_temperature"}
    assert json.loads(fields["rooms"]["value"]) == ["office", "living room"]
    assert fields["rooms"]["type"] == "list.single_line_text_field"


def product(pid, title, price, profile=None):
    mfs = [] if profile is None else [
        {"key": "dominant_colors", "value": json.dumps(profile["dominant_colors"])},
        {"key": "moods", "value": json.dumps(profile["moods"])},
        {"key": "rooms", "value": json.dumps(profile["rooms"])},
        {"key": "color_temperature", "value": profile["color_temperature"]}]
    return {"id": pid, "title": title, "handle": title.lower().replace(" ", "-"), "onlineStoreUrl": f"https://x/{pid}",
            "priceRangeV2": {"minVariantPrice": {"amount": str(price)}, "maxVariantPrice": {"amount": "550.92"}},
            "metafields": {"nodes": mfs}}


def test_search_ranks_by_fit_and_counts_unprofiled():
    noir = {"dominant_colors": ["black", "white"], "color_temperature": "neutral", "moods": ["minimal"], "rooms": ["office"]}
    red = {"dominant_colors": ["red", "orange"], "color_temperature": "warm", "moods": ["bold"], "rooms": ["living room"]}
    pages = {"Artworks": {"data": {"products": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [
        product("1", "Noir Mosaic", 153, noir), product("2", "Fractal Red", 153, red), product("3", "New Piece", 153)]}}}}
    r = catalog.search_artworks(FakeShop(pages), colors=["black"], moods=["minimal"], room="office")
    assert [x["title"] for x in r["results"]] == ["Noir Mosaic"]
    assert r["results"][0]["score"] == 7 and r["unprofiled"] == 1
    r = catalog.search_artworks(FakeShop(pages), room="office", max_price=100)
    assert r["results"] == []


def test_list_artworks_follows_pages():
    first = {"data": {"products": {"pageInfo": {"hasNextPage": True, "endCursor": "c1"}, "nodes": [product("1", "A", 153)]}}}
    second = {"data": {"products": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [product("2", "B", 153)]}}}
    answers = iter([first, second])
    shop = Shopify(transport=lambda q, v: next(answers))
    assert [a["title"] for a in catalog.list_artworks(shop)] == ["A", "B"]


# --- marketing -----------------------------------------------------------
def test_utm_and_pin_drafts():
    link = marketing.utm_link("https://vividwalls.co/products/noir-mosaic-no1?variant=1", "Pinterest", "Holiday 2026", content="Living Room")
    assert "variant=1" in link and "utm_source=pinterest" in link and "utm_campaign=holiday-2026" in link
    assert "utm_content=living-room" in link
    pins = marketing.pin_drafts("Noir Mosaic no1", "https://vividwalls.co/products/noir-mosaic-no1", "holiday",
                                ["living room", "office"], "https://cdn.shopify.com/s/files/room.png")
    assert len(pins) == 2 and all(len(p["title"]) <= 100 for p in pins)
    assert {"board_id", "title", "description", "image_url", "link", "alt_text"} == set(pins[0])
    with pytest.raises(ValueError):
        marketing.pin_drafts("x", "https://vividwalls.co/p", "c", ["office"], "<placeholder>")
    assert "utm_content=office" in pins[1]["link"]


def test_server_tools_return_errors_instead_of_crashing(monkeypatch):
    import httpx
    import server
    def boom(*a, **k):
        raise httpx.ConnectError("no route")
    monkeypatch.setattr(server, "_shop", Shopify(transport=boom))
    assert "Shopify request failed" in server.fulfillment_queue()["error"]
    monkeypatch.setattr(server, "_shop", None)
    monkeypatch.delenv("SHOPIFY_ADMIN_TOKEN", raising=False)
    assert "SHOPIFY_ADMIN_TOKEN" in server.unprofiled_artworks()["error"]


# --- review fixes: eligibility, lookups and link safety -------------------
@pytest.mark.parametrize("bad,reason", [
    (dict(status="PENDING"), "not PAID"),
    (dict(customer="Store Owner"), "test order"),
    (dict(cancelled="2026-11-07T00:00:00Z"), "cancelled"),
])
def test_mark_fulfilled_refuses_ineligible_orders(monkeypatch, bad, reason):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    shop = FakeShop({"OrderById": order_with_fos(order("40", **bad))})
    r = orders.mark_fulfilled(shop, "gid://shopify/Order/40", "1Z9", confirm=True)
    assert not r["applied"] and any(reason in e for e in r["errors"])
    assert "Fulfill" not in [op for op, _ in shop.calls]


@pytest.mark.parametrize("url,ok", [
    ("https://www.ups.com/track?tracknum=1Z9", True),
    ("https://tools.usps.com/go/TrackConfirmAction?tLabels=9", True),
    ("http://www.ups.com/track", False),
    ("https://ups.com.evil.example/track", False),
    ("https://bit.ly/abc", False),
])
def test_tracking_url_policy(url, ok):
    assert (orders.tracking_url_problem(url) is None) == ok


def test_bad_tracking_url_is_rejected_before_any_lookup():
    shop = FakeShop({})
    r = orders.mark_fulfilled(shop, "gid://shopify/Order/1", "1Z9", tracking_url="https://bit.ly/x", confirm=True)
    assert not r["applied"] and shop.calls == []


def test_order_sheet_lookup_is_strict():
    shop = FakeShop({"Unfulfilled": {"data": {"orders": {"nodes": [order("1009"), order("10090")]}}}})
    assert "not an order number" in orders.get_order_sheet(shop, "1009 OR name:#1")["problems"][0]
    assert shop.calls == []
    sheet = orders.get_order_sheet(shop, "1009")
    assert sheet["order"] == "#1009" and ("Unfulfilled", {"q": "name:#1009"}) in shop.calls


def test_order_sheet_flags_cancelled_and_owner_orders():
    shop = FakeShop({"Unfulfilled": {"data": {"orders": {"nodes": [order("50", cancelled="2026-11-07T00:00:00Z")]}}}})
    assert "order was cancelled" in orders.get_order_sheet(shop, "#50")["problems"]
    shop = FakeShop({"Unfulfilled": {"data": {"orders": {"nodes": [order("51", customer="Store Owner")]}}}})
    assert any("test order" in p for p in orders.get_order_sheet(shop, "#51")["problems"])


@pytest.mark.parametrize("pid", ["", "   ", "has space", "a" * 70])
def test_blank_or_malformed_pictorem_ids_are_rejected(pid):
    shop = FakeShop({})
    r = orders.record_pictorem_submission(shop, "gid://shopify/Order/1", pid, confirm=True)
    assert not r["applied"] and shop.calls == []
