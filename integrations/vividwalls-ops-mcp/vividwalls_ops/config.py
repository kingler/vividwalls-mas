"""Settings read from environment variables. No secrets live in this repo."""
import os

SHOPIFY_API_VERSION = "2026-10"
METAFIELD_NAMESPACE = "vividwalls"

# Pricing rule from business/catalog-and-pricing.md
MARKUP = 2.065
PRICE_FLOOR_MULTIPLE = 1.8


def shopify_domain() -> str:
    return os.environ.get("SHOPIFY_STORE_DOMAIN", "vividwalls-2.myshopify.com")


def shopify_token() -> str:
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
    if not token:
        raise RuntimeError("SHOPIFY_ADMIN_TOKEN is not set (Shopify custom app Admin API token).")
    return token


def writes_allowed() -> bool:
    """Store-changing functions only run when the owner has switched writes on."""
    return os.environ.get("VIVIDWALLS_ALLOW_WRITES") == "1"


def test_customer_names() -> set[str]:
    """Customers whose orders are tests (CLAUDE.md rule 3). Comma-separated, case-insensitive."""
    raw = os.environ.get("VIVIDWALLS_TEST_CUSTOMERS", "Test User")
    return {n.strip().lower() for n in raw.split(",") if n.strip()}
