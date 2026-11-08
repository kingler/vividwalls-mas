"""Settings read from environment variables. No secrets live in this repo."""
import os

SHOPIFY_API_VERSION = "2026-10"
METAFIELD_NAMESPACE = "vividwalls"

# Pricing rule from business/catalog-and-pricing.md
MARKUP = 2.065
PRICE_FLOOR_MULTIPLE = 1.8


def shopify_domain() -> str:
    return os.environ.get("SHOPIFY_STORE_DOMAIN", "vividwalls-2.myshopify.com")


# macOS Keychain item holding the Shopify Admin API token (created by the owner with
# `security add-generic-password -U -s vividwalls-shopify-admin -a <store domain> -w`).
SHOPIFY_KEYCHAIN_SERVICE = "vividwalls-shopify-admin"


def keychain_secret(service: str) -> str:
    """A generic password from the macOS Keychain, or "" when absent (or not on macOS)."""
    try:
        import subprocess
        return subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                              capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def shopify_token() -> str:
    """Admin API token from SHOPIFY_ADMIN_TOKEN, else the macOS Keychain. Never logged or returned."""
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "").strip() or keychain_secret(SHOPIFY_KEYCHAIN_SERVICE)
    if not token:
        raise RuntimeError(
            "Shopify Admin API token not found: set SHOPIFY_ADMIN_TOKEN or store it in the macOS Keychain "
            f'as service "{SHOPIFY_KEYCHAIN_SERVICE}".')
    return token


def writes_allowed() -> bool:
    """Store-changing functions only run when the owner has switched writes on."""
    return os.environ.get("VIVIDWALLS_ALLOW_WRITES") == "1"


PICTOREM_API_BASE = "https://www.pictorem.com/artflow/0.1"
# macOS Keychain item holding the Pictorem ArtFlow API token (created by the owner with
# `security add-generic-password -U -s vividwalls-pictorem-api -a <email> -w`).
PICTOREM_KEYCHAIN_SERVICE = "vividwalls-pictorem-api"


def pictorem_api_key() -> str:
    """ArtFlow token from PICTOREM_ARTFLOW_KEY, else the macOS Keychain. Never logged or returned."""
    key = os.environ.get("PICTOREM_ARTFLOW_KEY", "").strip() or keychain_secret(PICTOREM_KEYCHAIN_SERVICE)
    if not key:
        raise RuntimeError(
            "Pictorem API token not found: set PICTOREM_ARTFLOW_KEY or store it in the macOS Keychain "
            f'as service "{PICTOREM_KEYCHAIN_SERVICE}".')
    return key


def test_customer_names() -> set[str]:
    """Customers whose orders are tests (CLAUDE.md rule 3). Comma-separated, case-insensitive."""
    raw = os.environ.get("VIVIDWALLS_TEST_CUSTOMERS", "Test User")
    return {n.strip().lower() for n in raw.split(",") if n.strip()}
