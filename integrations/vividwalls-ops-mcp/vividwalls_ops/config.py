"""Settings read from environment variables. No secrets live in this repo."""
import os

SHOPIFY_API_VERSION = "2026-10"
METAFIELD_NAMESPACE = "vividwalls"

# Pricing rule from business/catalog-and-pricing.md
MARKUP = 2.065
PRICE_FLOOR_MULTIPLE = 1.8


def shopify_domain() -> str:
    return os.environ.get("SHOPIFY_STORE_DOMAIN", "vividwalls-2.myshopify.com")


# macOS Keychain items for Shopify (account = the store's admin domain, so another store's
# credentials are never used). A Dev Dashboard app stores its Client ID and Client secret:
#   security add-generic-password -U -s vividwalls-shopify-client-id -a <store domain> -w
#   security add-generic-password -U -s vividwalls-shopify-client-secret -a <store domain> -w
# An older admin-created custom app stores its fixed Admin API token instead:
#   security add-generic-password -U -s vividwalls-shopify-admin -a <store domain> -w
SHOPIFY_KEYCHAIN_SERVICE = "vividwalls-shopify-admin"
SHOPIFY_CLIENT_ID_SERVICE = "vividwalls-shopify-client-id"
SHOPIFY_CLIENT_SECRET_SERVICE = "vividwalls-shopify-client-secret"
TOKEN_REFRESH_MARGIN = 300  # seconds before expiry when a new token is requested


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


# Access tokens issued from client credentials, per store: {domain: (token, expires_at)}.
_issued_tokens: dict[str, tuple[str, float]] = {}


def forget_shopify_token() -> None:
    """Drop cached access tokens, e.g. after Shopify rejects one, so the next call asks again."""
    _issued_tokens.clear()


def _exchange_client_credentials(domain: str, client_id: str, client_secret: str) -> tuple[str, float]:
    """Ask the store for an access token with the app's client credentials (Dev Dashboard apps
    installed on the store). Returns the token and how many seconds it lasts."""
    import httpx
    resp = httpx.post(
        f"https://{domain}/admin/oauth/access_token",
        data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
        timeout=30,
    )
    if resp.status_code != 200:
        # Shopify's error text names the problem (wrong secret, app not installed); it holds no secret.
        raise RuntimeError(f"Shopify token request failed (HTTP {resp.status_code}): {resp.text[:300]}")
    body = resp.json()
    token = body.get("access_token") or ""
    if not token:
        raise RuntimeError("Shopify token request returned no access token.")
    return token, float(body.get("expires_in") or 0)


def shopify_token() -> str:
    """Admin API access token, from the first of:
    1. SHOPIFY_ADMIN_TOKEN;
    2. client credentials (SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET, else this store's Keychain
       items), exchanged for a short-lived token that is cached until shortly before it expires;
    3. this store's Keychain item holding a fixed Admin API token.
    Returned only to the Shopify client that authenticates requests; never logged or included
    in tool results."""
    import time
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "").strip()
    if token:
        return token
    domain = shopify_domain()
    cached = _issued_tokens.get(domain)
    if cached and time.time() < cached[1]:
        return cached[0]
    client_id = os.environ.get("SHOPIFY_CLIENT_ID", "").strip() or keychain_secret(
        SHOPIFY_CLIENT_ID_SERVICE, account=domain)
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET", "").strip() or keychain_secret(
        SHOPIFY_CLIENT_SECRET_SERVICE, account=domain)
    if client_id and client_secret:
        token, lasts = _exchange_client_credentials(domain, client_id, client_secret)
        _issued_tokens[domain] = (token, time.time() + max(lasts - TOKEN_REFRESH_MARGIN, 0))
        return token
    if client_id or client_secret:
        raise RuntimeError(
            "Shopify client credentials are incomplete: both the Client ID and the Client secret are needed "
            f'(SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET, or Keychain services "{SHOPIFY_CLIENT_ID_SERVICE}" '
            f'and "{SHOPIFY_CLIENT_SECRET_SERVICE}" with account "{domain}").')
    token = keychain_secret(SHOPIFY_KEYCHAIN_SERVICE, account=domain)
    if not token:
        raise RuntimeError(
            "Shopify credentials not found: store the app's Client ID and Client secret in the macOS Keychain "
            f'as services "{SHOPIFY_CLIENT_ID_SERVICE}" and "{SHOPIFY_CLIENT_SECRET_SERVICE}" with account '
            f'"{domain}" (or set SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET), or set SHOPIFY_ADMIN_TOKEN.')
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
