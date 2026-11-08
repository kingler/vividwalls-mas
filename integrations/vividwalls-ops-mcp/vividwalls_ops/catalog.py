"""Artwork profiles and search: replaces the n8n color-analysis, database-search and
prompt-chain image-retrieval workflows. The agent looks at the artwork and decides the
profile; these functions validate it, store it on the Shopify product, and search it."""
import json

from . import config
from .gate import blocked
from .shopify import Shopify

TEMPERATURES = {"warm", "cool", "neutral"}
MOODS = {"bold", "calm", "dramatic", "energetic", "minimal", "moody", "playful", "serene", "sophisticated", "warm"}
ROOMS = {"living room", "bedroom", "office", "dining room", "entryway", "hospitality", "kids room"}

PRODUCTS_QUERY = """
query Artworks($after: String) {
  products(first: 50, after: $after, query: "status:active") {
    pageInfo { hasNextPage endCursor }
    nodes {
      id title handle onlineStoreUrl
      priceRangeV2 { minVariantPrice { amount } maxVariantPrice { amount } }
      metafields(namespace: "vividwalls", first: 10) { nodes { key value } }
    }
  }
}
"""

METAFIELDS_SET = """
mutation SaveProfile($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) { metafields { key value } userErrors { field message } }
}
"""


def validate_profile(profile: dict) -> tuple[dict, list[str]]:
    """Normalise an artwork profile and list anything invalid."""
    errors = []
    colors = [str(c).strip().lower() for c in profile.get("dominant_colors", []) if str(c or "").strip()]
    if not 1 <= len(colors) <= 6:
        errors.append("dominant_colors needs 1-6 colour names")
    temp = str(profile.get("color_temperature", "")).strip().lower()
    if temp not in TEMPERATURES:
        errors.append(f"color_temperature must be one of {sorted(TEMPERATURES)}")
    moods = [str(m).strip().lower() for m in profile.get("moods", [])]
    if not 1 <= len(moods) <= 3 or set(moods) - MOODS:
        errors.append(f"moods needs 1-3 of {sorted(MOODS)}")
    rooms = [str(r).strip().lower() for r in profile.get("rooms", [])]
    if not 1 <= len(rooms) <= 4 or set(rooms) - ROOMS:
        errors.append(f"rooms needs 1-4 of {sorted(ROOMS)}")
    clean = {"dominant_colors": colors, "color_temperature": temp, "moods": moods, "rooms": rooms}
    return clean, errors


def _profile_metafields(product_id: str, p: dict) -> list[dict]:
    ns = config.METAFIELD_NAMESPACE
    lists = {"dominant_colors": p["dominant_colors"], "moods": p["moods"], "rooms": p["rooms"]}
    fields = [{"ownerId": product_id, "namespace": ns, "key": k, "type": "list.single_line_text_field",
               "value": json.dumps(v)} for k, v in lists.items()]
    fields.append({"ownerId": product_id, "namespace": ns, "key": "color_temperature",
                   "type": "single_line_text_field", "value": p["color_temperature"]})
    return fields


def save_artwork_profile(shop: Shopify, product_id: str, profile: dict, confirm: bool = False) -> dict:
    clean, errors = validate_profile(profile)
    if errors:
        return {"applied": False, "errors": errors}
    fields = _profile_metafields(product_id, clean)
    preview = blocked(confirm, "save artwork profile to product metafields", {"product_id": product_id, "profile": clean})
    if preview:
        return preview
    shop.run(METAFIELDS_SET, {"metafields": fields})
    return {"applied": True, "product_id": product_id, "profile": clean}


def _read_profile(node: dict) -> dict:
    raw = {m["key"]: m["value"] for m in node["metafields"]["nodes"]}
    out = {}
    for k in ("dominant_colors", "moods", "rooms"):
        try:
            out[k] = json.loads(raw[k]) if k in raw else []
        except json.JSONDecodeError:
            out[k] = []
    out["color_temperature"] = raw.get("color_temperature", "")
    return out


def list_artworks(shop: Shopify) -> list[dict]:
    items, after = [], None
    while True:
        data = shop.run(PRODUCTS_QUERY, {"after": after})["products"]
        for n in data["nodes"]:
            items.append({
                "product_id": n["id"], "title": n["title"], "handle": n["handle"], "url": n["onlineStoreUrl"],
                "price_from": float(n["priceRangeV2"]["minVariantPrice"]["amount"]),
                "price_to": float(n["priceRangeV2"]["maxVariantPrice"]["amount"]),
                "profile": _read_profile(n),
            })
        if not data["pageInfo"]["hasNextPage"]:
            return items
        after = data["pageInfo"]["endCursor"]


def unprofiled_artworks(shop: Shopify) -> list[dict]:
    """Artworks that still need the agent to analyse them."""
    return [{"product_id": a["product_id"], "title": a["title"], "url": a["url"]}
            for a in list_artworks(shop) if not a["profile"]["dominant_colors"]]


def score_artwork(artwork: dict, colors=(), moods=(), room: str = "", temperature: str = "") -> tuple[int, list[str]]:
    p = artwork["profile"]
    score, why = 0, []
    hit_colors = sorted(set(c.lower() for c in colors) & set(p["dominant_colors"]))
    if hit_colors:
        score += 2 * len(hit_colors)
        why.append("colors: " + ", ".join(hit_colors))
    hit_moods = sorted(set(m.lower() for m in moods) & set(p["moods"]))
    if hit_moods:
        score += 2 * len(hit_moods)
        why.append("mood: " + ", ".join(hit_moods))
    if room and room.lower() in p["rooms"]:
        score += 3
        why.append(f"suits {room.lower()}")
    if temperature and temperature.lower() == p["color_temperature"]:
        score += 1
        why.append(f"{p['color_temperature']} palette")
    return score, why


def search_artworks(shop: Shopify, colors: list[str] | None = None, moods: list[str] | None = None,
                    room: str = "", temperature: str = "", max_price: float | None = None, limit: int = 5) -> dict:
    artworks = list_artworks(shop)
    results = []
    for a in artworks:
        if max_price is not None and a["price_from"] > max_price:
            continue
        score, why = score_artwork(a, colors or (), moods or (), room, temperature)
        if score:
            results.append({"title": a["title"], "url": a["url"], "price_from": a["price_from"],
                            "score": score, "why": why})
    results.sort(key=lambda r: (-r["score"], r["price_from"]))
    return {"results": results[:limit],
            "unprofiled": sum(1 for a in artworks if not a["profile"]["dominant_colors"])}
