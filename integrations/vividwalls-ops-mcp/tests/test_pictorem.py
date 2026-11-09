import re

import pytest

from vividwalls_ops import config, orders, pictorem
from vividwalls_ops.pictorem import Pictorem, PictoremError
from vividwalls_ops.shopify import Shopify

WRAP = "36x48 / Gallery Wrapped Stretched Canvas"
RAW = "1|canvas|stretched|vertical|36|48|c15|imagewrap"
CANON = "1|canvas|cnvr|36|48|vertical|c15|imagewrap|wire"


def order(name="1009", variant=WRAP, price="315.94", tags=(), country="US", collection="1941630", file_url=None,
          customer="Jane Buyer"):
    return {
        "id": f"gid://shopify/Order/{name}", "name": f"#{name}", "createdAt": "2026-11-08T08:00:00Z",
        "cancelledAt": None, "tags": list(tags), "displayFinancialStatus": "PAID",
        "displayFulfillmentStatus": "UNFULFILLED", "customer": {"displayName": customer},
        "shippingAddress": {"name": "Jane Q Buyer", "address1": "1 Main St", "address2": None, "city": "Newark",
                            "provinceCode": "NJ", "zip": "07102", "countryCodeV2": country, "phone": "555-0100"},
        "lineItems": {"nodes": [{
            "title": "Vivid Mosaic no0", "quantity": 1, "variantTitle": variant,
            "originalUnitPriceSet": {"shopMoney": {"amount": price}},
            "product": {"id": "gid://shopify/Product/7", "handle": "vivid-mosaic-no0",
                        "printCollection": {"value": collection} if collection else None,
                        "printFileUrl": {"value": file_url} if file_url else None},
        }]},
    }


class FakeShop(Shopify):
    def __init__(self, orders_found):
        self.calls = []
        super().__init__(transport=self._answer)
        self.orders_found = orders_found

    def _answer(self, query, variables):
        op = re.search(r"(?:query|mutation)\s+(\w+)", query).group(1)
        self.calls.append((op, variables))
        if op == "Owner":
            return {"data": {"shop": {"shopOwnerName": "Store Owner"}}}
        if op == "Unfulfilled":
            return {"data": {"orders": {"nodes": self.orders_found}}}
        return {"data": {"x": {"userErrors": []}}}


class FakePictorem(Pictorem):
    """Answers like the ArtFlow API: the sanitizer completes RAW into CANON, CANON validates."""
    def __init__(self, cost=150.0, send=None, placed=None, file_issue=None):
        self.calls = []
        self.cost = cost
        self.send = send or (200, {"status": True, "msg": [], "orderid": 472175})
        self.placed = placed or {}          # PO -> order Pictorem already holds
        self.file_issue = file_issue
        super().__init__(transport=self._answer)

    def file_problem(self, url):
        return self.file_issue

    def _answer(self, endpoint, fields):
        self.calls.append((endpoint, fields))
        if endpoint == "getartworklist":
            return 200, {"status": True, "data": {"pages": 1, "artworks": [
                {"id": 1941630, "name": "vivid mosaic no0 canvas", "orientation": "vertical", "ratio": 0.74,
                 "image": {"preview": "https://www.pictorem.com/p.jpg"}}]}}
        if endpoint == "validatepreorder":
            code = fields["preordercode"]
            if code.endswith("|wire"):
                return 200, {"status": True, "data": {"preordercode": code, "preordersanitize": code}}
            return 200, {"status": False, "data": {"preordercode": code, "errorlist": [],
                                                   "preordersanitize": code.replace("stretched|vertical|36|48", "cnvr|36|48|vertical") + "|wire"}}
        if endpoint == "getprice":
            return 200, {"status": True, "worksheet": {"price": {"listTotal": self.cost * 1.18, "discountTotal": 1,
                                                                 "subTotal": self.cost, "total": self.cost}}}
        if endpoint == "sendorder":
            return self.send
        if endpoint == "getorderstatus":
            po = fields.get("po")
            if po and po not in self.placed and po != "VW-SHIPPED":
                return 200, {"status": False, "msg": {"error": ["Order not found."]}}
            return 200, {"status": True, "order": {"orderid": self.placed.get(po, 472175), "po": po,
                                                   "order_status_label": "Shipped", "production_status_label": "Shipped",
                                                   "production_progress": 100, "billing_status_label": "Paid",
                                                   "tracking_number": "1Z999", "tracking_carrier": "UPS", "total": 150.0}}
        raise AssertionError(endpoint)


def sent(pic):
    return [f for e, f in pic.calls if e == "sendorder"]


# --- product codes -----------------------------------------------------------
@pytest.mark.parametrize("fmt,size,art,code", [
    ("Canvas, stretched, 1.5in gallery wrap", "36x48", None, RAW),
    ("Canvas, rolled", "24x36", "vertical", "1|canvas|canvasroll|vertical|24|36"),
    ("Canvas, stretched, 1.5in gallery wrap", "36x48", "horizontal", "1|canvas|stretched|horizontal|48|36|c15|imagewrap"),
])
def test_product_codes(fmt, size, art, code):
    assert pictorem.product_code(1, fmt, size, art) == code


def test_unknown_format_is_refused():
    with pytest.raises(ValueError):
        pictorem.product_code(1, None, "36x48")


def test_canonical_code_accepts_the_sanitized_code():
    pic = FakePictorem()
    assert pictorem.canonical_code(pic, RAW) == CANON
    assert [f["preordercode"] for e, f in pic.calls] == [RAW, CANON]


def test_canonical_code_raises_on_sanitizer_errors():
    pic = Pictorem(transport=lambda e, f: (200, {"status": False, "data": {
        "preordersanitize": "x", "errorlist": ["Error::7120::Border Color Hex is empty"]}}))
    with pytest.raises(PictoremError, match="7120"):
        pictorem.canonical_code(pic, RAW)


# --- quote --------------------------------------------------------------------
def test_quote_is_ready_with_codes_costs_and_po():
    q = orders.quote_order(FakeShop([order()]), FakePictorem(cost=150.0), "#1009")
    assert q["ready"], q["problems"]
    assert q["po"] == "VW-1009"
    line = q["lines"][0]
    assert line["code"] == CANON and line["source"] == {"collectionID": "1941630"}
    assert line["pictorem_cost"] == 150.0 and q["pictorem_total"] == 150.0


@pytest.mark.parametrize("kwargs,problem", [
    ({"collection": None}, "no print file"),
    ({"tags": ["pictorem:4711"]}, "already sent to Pictorem"),
    ({"country": "GB"}, "only US and Canada"),
    ({"collection": "999"}, "not found on the account"),
    ({"customer": "Test User"}, "test order"),
])
def test_quote_refuses_unsafe_orders(kwargs, problem):
    q = orders.quote_order(FakeShop([order(**kwargs)]), FakePictorem(), "#1009")
    assert not q["ready"] and any(problem in p for p in q["problems"]), q["problems"]


def test_quote_above_expected_cost_needs_accept_quote():
    # 315.94 retail implies a 153.00 cost; 178.51 is 16.7% above it.
    q = orders.quote_order(FakeShop([order()]), FakePictorem(cost=178.51), "#1009")
    assert not q["ready"] and "more than 10% above" in q["problems"][0]
    assert orders.quote_order(FakeShop([order()]), FakePictorem(cost=178.51), "#1009", accept_quote=True)["ready"]


def test_print_file_url_is_used_when_no_collection():
    q = orders.quote_order(FakeShop([order(collection=None, file_url="https://files.example/vm0.tif")]),
                           FakePictorem(), "#1009")
    assert q["ready"] and q["lines"][0]["source"] == {"fileurl": "https://files.example/vm0.tif"}


# --- submit -------------------------------------------------------------------
def test_submit_previews_without_confirm_and_sends_nothing(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem()
    out = orders.submit_order(FakeShop([order()]), pic, "#1009")
    assert out["applied"] is False and "preview only" in out["reason"]
    assert out["change"]["po"] == "VW-1009" and out["change"]["pictorem_total"] == 150.0
    assert sent(pic) == []


def test_submit_needs_the_writes_switch(monkeypatch):
    monkeypatch.delenv("VIVIDWALLS_ALLOW_WRITES", raising=False)
    pic = FakePictorem()
    out = orders.submit_order(FakeShop([order()]), pic, "#1009", confirm=True)
    assert out["applied"] is False and "switched off" in out["reason"] and sent(pic) == []


def approve(shop, pic, name="#1009", **kw):
    """Preview first, then confirm with the preview's approval code, as the owner flow does."""
    code = orders.submit_order(shop, pic, name, **kw)["change"]["approval_code"]
    return orders.submit_order(shop, pic, name, confirm=True, approval_code=code, **kw)


def test_confirmed_submit_places_the_order_and_tags_shopify(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    shop, pic = FakeShop([order()]), FakePictorem()
    out = approve(shop, pic)
    assert out["applied"] and out["pictorem_order_id"] == 472175 and out["tag"] == "pictorem:472175"
    fields = sent(pic)[0]
    assert fields["po"] == "VW-1009" and "testmode" not in fields
    assert fields["orderList[0][code]"] == CANON and fields["orderList[0][collectionID]"] == "1941630"
    assert fields["deliveryInfo[firstname]"] == "Jane" and fields["deliveryInfo[lastname]"] == "Q Buyer"
    assert fields["deliveryInfo[cp]"] == "07102" and fields["deliveryInfo[country]"] == "US"
    assert ("TagOrder", {"id": "gid://shopify/Order/1009", "tags": ["pictorem:472175"]}) in shop.calls


def test_sandbox_submit_uses_test_mode_and_changes_nothing(monkeypatch):
    monkeypatch.delenv("VIVIDWALLS_ALLOW_WRITES", raising=False)
    shop, pic = FakeShop([order()]), FakePictorem()
    out = orders.submit_order(shop, pic, "#1009", sandbox=True)
    assert out["sandbox"] and out["applied"] is False
    assert sent(pic)[0]["testmode"] == "1"
    assert not any(op == "TagOrder" for op, _ in shop.calls)


def test_retry_with_same_po_returns_the_existing_order(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    dup = (409, {"status": False, "duplicate": True, "orderid": 472174,
                 "msg": {"error": ['PO "VW-1009" was already used on order 472174.']}})
    pic = FakePictorem(send=dup)
    out = approve(FakeShop([order()]), pic)
    assert out["applied"] and out["duplicate"] and out["pictorem_order_id"] == 472174
    assert sent(pic)[0]["po"] == "VW-1009"


def test_refused_order_raises_with_pictorem_reason(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    bad = (422, {"status": False, "failedstep": "sanitizePreOrderList",
                 "msg": {"error": ["deliveryInfo[cp] is required."]}})
    with pytest.raises(PictoremError, match="cp] is required"):
        approve(FakeShop([order()]), FakePictorem(send=bad))


def test_unready_order_is_never_sent(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem()
    out = orders.submit_order(FakeShop([order(collection=None)]), pic, "#1009", confirm=True)
    assert out["applied"] is False and out["errors"] and sent(pic) == []


# --- status and print files ----------------------------------------------------
def test_status_by_shopify_order_uses_our_po():
    pic = FakePictorem(placed={"VW-1009": 472175})
    st = orders.pictorem_status(pic, order="#1009")
    assert ("getorderstatus", {"po": "VW-1009"}) in pic.calls
    assert st["tracking_number"] == "1Z999" and st["ready_to_mark_fulfilled"]


@pytest.mark.parametrize("kwargs,error", [
    ({}, "exactly one"),
    ({"collection_id": "1", "file_url": "https://x"}, "exactly one"),
    ({"collection_id": "abc"}, "numeric"),
    ({"file_url": "http://insecure.example/a.tif"}, "https"),
    ({"file_url": "https://192.168.1.20/a.tif"}, "not a public address"),
    ({"file_url": "https://localhost/a.tif"}, "not public"),
])
def test_set_print_file_validation(kwargs, error):
    shop = FakeShop([])
    out = orders.set_print_file(shop, "gid://shopify/Product/7", confirm=True, **kwargs)
    assert out["applied"] is False and error in out["errors"][0]
    assert not any(op == "SetPrintFile" for op, _ in shop.calls)


def test_set_print_file_previews_then_writes(monkeypatch):
    shop = FakeShop([])
    monkeypatch.delenv("VIVIDWALLS_ALLOW_WRITES", raising=False)
    assert orders.set_print_file(shop, "gid://shopify/Product/7", collection_id="1941630")["applied"] is False
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    out = orders.set_print_file(shop, "gid://shopify/Product/7", collection_id="1941630", confirm=True)
    assert out["applied"]
    op, variables = shop.calls[-1]
    assert op == "SetPrintFile" and variables["metafields"][0]["key"] == "pictorem_collection_id"
    # the other kind of print source is cleared so it cannot keep printing the old artwork
    assert variables["stale"] == [{"ownerId": "gid://shopify/Product/7", "namespace": "vividwalls",
                                   "key": "print_file_url"}]


def test_api_key_comes_from_env_first(monkeypatch):
    monkeypatch.setenv("PICTOREM_ARTFLOW_KEY", "  k123  ")
    assert config.pictorem_api_key() == "k123"


# --- review fixes: approval code, discounts, size limit, duplicates ---------------
def test_confirm_without_the_preview_code_orders_nothing(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem()
    out = orders.submit_order(FakeShop([order()]), pic, "#1009", confirm=True)
    assert out["applied"] is False and "approval_code" in out["errors"][0] and sent(pic) == []


def test_order_changed_after_preview_is_not_charged(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem(cost=150.0)
    code = orders.submit_order(FakeShop([order()]), pic, "#1009")["change"]["approval_code"]
    moved = order()
    moved["shippingAddress"]["address1"] = "99 Other Rd"
    out = orders.submit_order(FakeShop([moved]), pic, "#1009", confirm=True, approval_code=code)
    assert out["applied"] is False and "changed since the preview" in out["errors"][0]
    assert sent(pic) == []
    pricier = FakePictorem(cost=160.0)
    out = orders.submit_order(FakeShop([order()]), pricier, "#1009", confirm=True, approval_code=code)
    assert out["applied"] is False and sent(pricier) == []


def test_cost_check_uses_the_discounted_price():
    discounted = order(price="315.94")
    discounted["lineItems"]["nodes"][0]["discountedUnitPriceAfterAllDiscountsSet"] = {"shopMoney": {"amount": "250.00"}}
    q = orders.quote_order(FakeShop([discounted]), FakePictorem(cost=150.0), "#1009")
    # 250 paid implies a 121.07 cost; Pictorem's 150 is 24% above it
    assert not q["ready"] and "more than 10% above" in q["problems"][0]
    assert q["lines"][0]["paid_each"] == 250.0


def test_orders_with_more_items_than_fetched_are_refused():
    big = order()
    big["lineItems"]["pageInfo"] = {"hasNextPage": True}
    q = orders.quote_order(FakeShop([big]), FakePictorem(), "#1009")
    assert not q["ready"] and any("more than 50 line items" in p for p in q["problems"])


def test_order_pictorem_already_holds_is_not_ordered_again(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem(placed={"VW-1009": 480001})
    q = orders.quote_order(FakeShop([order()]), pic, "#1009")
    assert not q["ready"] and "already placed with Pictorem as order 480001" in q["problems"][0]
    assert orders.submit_order(FakeShop([order()]), pic, "#1009", confirm=True)["applied"] is False
    assert sent(pic) == []


def test_unreachable_print_file_blocks_the_quote():
    q = orders.quote_order(FakeShop([order(collection=None, file_url="https://files.example/x.tif")]),
                           FakePictorem(file_issue="print file https://files.example/x.tif answered HTTP 403"),
                           "#1009")
    assert not q["ready"] and any("HTTP 403" in p for p in q["problems"])


def test_failed_shopify_tag_still_reports_the_pictorem_order(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")

    class TagFails(FakeShop):
        def _answer(self, query, variables):
            if "mutation TagOrder" in query:
                return {"errors": [{"message": "throttled"}]}
            return super()._answer(query, variables)

    out = approve(TagFails([order()]), FakePictorem())
    assert out["applied"] and out["pictorem_order_id"] == 472175 and out["tag"] is None
    assert "record_pictorem_submission" in out["warning"]


def test_manual_sheet_carries_the_po_and_refuses_placed_orders():
    sheet = orders.get_order_sheet(FakeShop([order()]), "#1009", FakePictorem(placed={"VW-1009": 480001}))
    assert sheet["po"] == "VW-1009" and not sheet["ready"]
    assert orders.get_order_sheet(FakeShop([order()]), "#1009", FakePictorem())["ready"]


def test_public_https_rule():
    assert pictorem.public_https_problem("https://cdn.shopify.com/a.png") is None
    assert pictorem.public_https_problem("https://10.0.0.5/a.tif")
    assert pictorem.public_https_problem("https://nas.local/a.tif")
    assert pictorem.public_https_problem("ftp://cdn.example/a.tif")


# Pictorem rejects a fileurl line without filetype ("orderList[0][filetype] is required and must be
# jpg / png / tiff"), found by a sandbox order on 2026-11-08.
@pytest.mark.parametrize("url,kind", [
    ("https://cdn.shopify.com/files/Deep.png", "png"), ("https://x.example/a.JPEG", "jpg"),
    ("https://x.example/a.tif?v=3", "tiff"), ("https://x.example/print", None)])
def test_file_type_from_url(url, kind):
    assert orders.file_type(url) == kind


def test_file_url_orders_send_the_file_type(monkeypatch):
    monkeypatch.setenv("VIVIDWALLS_ALLOW_WRITES", "1")
    pic = FakePictorem()
    shop = FakeShop([order(collection=None, file_url="https://cdn.shopify.com/files/Deep.png?v=1")])
    approve(shop, pic)
    assert sent(pic)[0]["orderList[0][filetype]"] == "png"
    assert sent(pic)[0]["orderList[0][fileurl]"] == "https://cdn.shopify.com/files/Deep.png?v=1"


def test_file_url_without_a_known_type_is_refused():
    q = orders.quote_order(FakeShop([order(collection=None, file_url="https://files.example/print")]),
                           FakePictorem(), "#1009")
    assert not q["ready"] and any(".jpg, .png or .tif" in p for p in q["problems"])


# --- second review: resolve hostnames, refuse untyped links at setup -------------
def test_set_print_file_refuses_a_link_orders_would_reject(monkeypatch):
    monkeypatch.setattr(pictorem.socket, "getaddrinfo", lambda h, p: [(0, 0, 0, "", ("151.101.1.1", 443))])
    shop = FakeShop([])
    out = orders.set_print_file(shop, "gid://shopify/Product/7", file_url="https://files.example/print", confirm=True)
    assert out["applied"] is False and ".jpg, .png or .tif" in out["errors"][0]
    assert not any(op == "SetPrintFile" for op, _ in shop.calls)


def test_hostname_pointing_at_a_private_address_is_refused(monkeypatch):
    monkeypatch.setattr(pictorem.socket, "getaddrinfo", lambda h, p: [(0, 0, 0, "", ("10.1.2.3", 443))])
    assert "not a public address" in pictorem.public_https_problem("https://files.example/a.png", resolve=True)
    shop = FakeShop([])
    out = orders.set_print_file(shop, "gid://shopify/Product/7", file_url="https://files.example/a.png", confirm=True)
    assert out["applied"] is False and not shop.calls


def test_redirect_to_a_private_host_is_refused(monkeypatch):
    import httpx

    def fake_resolve(host, port):
        return [(0, 0, 0, "", ("10.0.0.9" if host == "internal.example" else "151.101.1.1", 443))]

    monkeypatch.setattr(pictorem.socket, "getaddrinfo", fake_resolve)
    hop = httpx.Response(302, request=httpx.Request("HEAD", "https://cdn.example/a.png"))
    final = httpx.Response(200, headers={"content-type": "image/png"},
                           request=httpx.Request("HEAD", "https://internal.example/a.png"), history=[hop])
    monkeypatch.setattr(pictorem.httpx, "head", lambda *a, **k: final)
    problem = Pictorem(transport=lambda e, f: (200, {})).file_problem("https://cdn.example/a.png")
    assert problem and "redirects to a non-public address" in problem


def test_shopify_token_comes_from_env_then_this_stores_keychain_item(monkeypatch):
    monkeypatch.setenv("SHOPIFY_ADMIN_TOKEN", " shpat_env ")
    assert config.shopify_token() == "shpat_env"
    monkeypatch.delenv("SHOPIFY_ADMIN_TOKEN")
    seen = []

    def fake(service, account=None):
        seen.append((service, account))
        return "shpat_kc" if (service, account) == ("vividwalls-shopify-admin", "vividwalls-2.myshopify.com") else ""

    monkeypatch.setattr(config, "keychain_secret", fake)
    assert config.shopify_token() == "shpat_kc"
    assert seen == [("vividwalls-shopify-client-id", "vividwalls-2.myshopify.com"),
                    ("vividwalls-shopify-client-secret", "vividwalls-2.myshopify.com"),
                    ("vividwalls-shopify-admin", "vividwalls-2.myshopify.com")]
    monkeypatch.setenv("SHOPIFY_STORE_DOMAIN", "other-store.myshopify.com")
    with pytest.raises(RuntimeError, match='account "other-store.myshopify.com"'):
        config.shopify_token()


class _TokenResp:
    def __init__(self, status, body):
        self.status_code, self._body, self.text = status, body, str(body)

    def json(self):
        return self._body


def _client_credentials_keychain(monkeypatch, domain="vividwalls-2.myshopify.com"):
    items = {("vividwalls-shopify-client-id", domain): "cid",
             ("vividwalls-shopify-client-secret", domain): "shpss_secret"}
    monkeypatch.setattr(config, "keychain_secret", lambda service, account=None: items.get((service, account), ""))


def test_shopify_token_from_client_credentials_is_exchanged_and_cached(monkeypatch):
    import httpx
    _client_credentials_keychain(monkeypatch)
    calls = []

    def fake_post(url, data=None, timeout=None, **k):
        calls.append((url, data))
        return _TokenResp(200, {"access_token": f"shpat_{len(calls)}", "expires_in": 86399})

    monkeypatch.setattr(httpx, "post", fake_post)
    assert config.shopify_token() == "shpat_1"
    assert config.shopify_token() == "shpat_1"  # cached, no second exchange
    assert calls == [("https://vividwalls-2.myshopify.com/admin/oauth/access_token",
                      {"grant_type": "client_credentials", "client_id": "cid", "client_secret": "shpss_secret"})]
    config.forget_shopify_token()
    assert config.shopify_token() == "shpat_2"


def test_shopify_token_is_refreshed_before_it_expires(monkeypatch):
    import httpx
    import time
    _client_credentials_keychain(monkeypatch)
    n = []
    monkeypatch.setattr(httpx, "post", lambda *a, **k: (n.append(1), _TokenResp(
        200, {"access_token": f"shpat_{len(n)}", "expires_in": 86399}))[1])
    now = [1_000_000.0]
    monkeypatch.setattr(time, "time", lambda: now[0])
    assert config.shopify_token() == "shpat_1"
    now[0] += 86399 - config.TOKEN_REFRESH_MARGIN - 1
    assert config.shopify_token() == "shpat_1"
    now[0] += 2
    assert config.shopify_token() == "shpat_2"


def test_shopify_client_credentials_env_wins_over_keychain_and_errors_are_clear(monkeypatch):
    import httpx
    _client_credentials_keychain(monkeypatch)
    monkeypatch.setenv("SHOPIFY_CLIENT_ID", "env-id")
    monkeypatch.setenv("SHOPIFY_CLIENT_SECRET", "env-secret")
    seen = []
    monkeypatch.setattr(httpx, "post", lambda url, data=None, **k: (seen.append(data), _TokenResp(
        400, {"error": "invalid_client"}))[1])
    with pytest.raises(RuntimeError, match=r"token request failed \(HTTP 400\)") as err:
        config.shopify_token()
    assert seen[0]["client_id"] == "env-id" and "env-secret" not in str(err.value)
    monkeypatch.delenv("SHOPIFY_CLIENT_SECRET")
    monkeypatch.setattr(config, "keychain_secret", lambda service, account=None: "")
    with pytest.raises(RuntimeError, match="incomplete"):
        config.shopify_token()


def test_shopify_client_retries_once_with_a_new_token_after_401(monkeypatch):
    import httpx
    from vividwalls_ops.shopify import Shopify
    tokens = iter(["shpat_old", "shpat_new"])
    monkeypatch.setattr(config, "shopify_token", lambda: next(tokens))
    forgot = []
    monkeypatch.setattr(config, "forget_shopify_token", lambda: forgot.append(1))
    sent = []

    def fake_post(url, json=None, headers=None, timeout=None):
        sent.append(headers["X-Shopify-Access-Token"])
        status = 401 if len(sent) == 1 else 200
        return httpx.Response(status, json={"data": {"shop": {"name": "VividWalls"}}},
                              request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    assert Shopify().run("{ shop { name } }") == {"shop": {"name": "VividWalls"}}
    assert sent == ["shpat_old", "shpat_new"] and forgot == [1]


class _Done:
    def __init__(self, rc, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


@pytest.mark.parametrize("outcome,expect", [
    (_Done(0, "secret\n"), "secret"),
    (_Done(44, err="The specified item could not be found in the keychain."), ""),
])
def test_keychain_secret_found_or_missing(monkeypatch, outcome, expect):
    import importlib, subprocess
    real = importlib.reload(config)  # undo the autouse stub for this test
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: calls.append(cmd) or outcome)
    assert real.keychain_secret("svc", account="acct") == expect
    assert calls[0][:6] == ["security", "find-generic-password", "-s", "svc", "-a", "acct"]


def test_keychain_read_failures_are_not_reported_as_missing(monkeypatch):
    import importlib, subprocess
    real = importlib.reload(config)
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: _Done(51, err="User interaction is not allowed."))
    with pytest.raises(RuntimeError, match="failed .exit 51.: User interaction is not allowed"):
        real.keychain_secret("svc")

    def timeout(cmd, **k):
        raise subprocess.TimeoutExpired(cmd, 10)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        real.keychain_secret("svc")


def test_keychain_lookup_rejects_unsafe_values(monkeypatch):
    import importlib, subprocess
    real = importlib.reload(config)
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: (_ for _ in ()).throw(AssertionError("must not run")))
    for bad in ("svc; rm -rf ~", "-w", "a b", ""):
        with pytest.raises(ValueError, match="invalid Keychain"):
            real.keychain_secret(bad)
    with pytest.raises(ValueError):
        real.keychain_secret("vividwalls-shopify-admin", account="store.myshopify.com && x")
