"""Marketing helpers: consistent UTM links and Pinterest pin drafts for the campaign playbook."""
import re
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def utm_link(url: str, source: str, campaign: str, medium: str = "social", content: str = "") -> str:
    parts = urlparse(url)
    q = dict(parse_qsl(parts.query))
    q.update({"utm_source": slugify(source), "utm_medium": slugify(medium), "utm_campaign": slugify(campaign)})
    if content:
        q["utm_content"] = slugify(content)
    return urlunparse(parts._replace(query=urlencode(q)))


def pin_drafts(title: str, product_url: str, campaign: str, rooms: list[str], image_url: str,
               board_id: str = "") -> list[dict]:
    """One pin per room angle, with the arguments the Pinterest server's create_pin takes.
    image_url must be a public https image (e.g. the product's room mockup on cdn.shopify.com)."""
    if urlparse(image_url).scheme != "https":
        raise ValueError("image_url must be a public https image URL")
    drafts = []
    for room in rooms[:5]:
        pin_title = f"{title}: large abstract wall art for the {room}"[:100]
        drafts.append({
            "board_id": board_id or "<choose with get_boards>",
            "title": pin_title,
            "description": (f"{title} on gallery-wrapped canvas, ready to hang. Modern abstract wall art "
                            f"for the {room}. Shop sizes 24x36 to 53x72 at VividWalls.")[:500],
            "link": utm_link(product_url, "pinterest", campaign, medium="social", content=room),
            "image_url": image_url,
            "alt_text": f"{title} canvas wall art in a modern {room}",
        })
    return drafts
