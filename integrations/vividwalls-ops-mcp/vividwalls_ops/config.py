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


KEYCHAIN_ITEM_NOT_FOUND = 44  # `security` exit status when no item matches


def keychain_secret(service: str, account: str | None = None) -> str:
    """A generic password from the macOS Keychain, or "" when there is no such item (or no
    Keychain, e.g. not on macOS). A Keychain that exists but cannot be read (locked, access
    denied, timed out) raises instead, so it is not mistaken for a missing token."""
    import re
    import subprocess
    # Only plain identifiers (our service names, a store domain or email) reach the command line,
    # and none may start with "-", which `security` would read as an option.
    for value in (service, account or "x"):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._@-]{0,127}", value):
            raise ValueError(f"invalid Keychain service or account: {value!r}")
    cmd = ["security", "find-generic-password", "-s", service, *(["-a", account] if account else []), "-w"]
    try:
        # argv list with no shell, and both values validated above: nothing is interpreted.
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=10)  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        raise RuntimeError(f'Keychain read for "{service}" timed out; unlock the Keychain and try again.')
    if done.returncode == 0:
        return done.stdout.strip()
    if done.returncode == KEYCHAIN_ITEM_NOT_FOUND:
        return ""
    raise RuntimeError(f'Keychain read for "{service}" failed (exit {done.returncode}): {done.stderr.strip()}')


def shopify_token() -> str:
    """Admin API token from SHOPIFY_ADMIN_TOKEN, else the Keychain item for this store
    (service vividwalls-shopify-admin, account = the store's admin domain), so another store's
    token is never used. Returned only to the Shopify client that authenticates requests; never
    logged or included in tool results."""
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "").strip() or keychain_secret(
        SHOPIFY_KEYCHAIN_SERVICE, account=shopify_domain())
    if not token:
        raise RuntimeError(
            "Shopify Admin API token not found: set SHOPIFY_ADMIN_TOKEN or store it in the macOS Keychain "
            f'as service "{SHOPIFY_KEYCHAIN_SERVICE}" with account "{shopify_domain()}".')
    return token


def writes_allowed() -> bool:
    """Store-changing functions only run when the owner has switched writes on."""
    return os.environ.get("VIVIDWALLS_ALLOW_WRITES") == "1"


PICTOREM_API_BASE = "https://www.pictorem.com/artflow/0.1"
# macOS Keychain item holding the Pictorem ArtFlow API token (created by the owner with
# `security add-generic-password -U -s vividwalls-pictorem-api -a <email> -w`).
PICTOREM_KEYCHAIN_SERVICE = "vividwalls-pictorem-api"


def pictorem_api_key() -> str:
    """ArtFlow token from PICTOREM_ARTFLOW_KEY, else the macOS Keychain. Returned only to the
    Pictorem client that authenticates requests; never logged or included in tool results."""
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
