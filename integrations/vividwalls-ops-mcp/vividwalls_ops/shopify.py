"""Minimal Shopify Admin GraphQL client."""
from typing import Any, Callable

import httpx

from . import config


class ShopifyError(RuntimeError):
    pass


Transport = Callable[[str, dict[str, Any]], dict[str, Any]]


class Shopify:
    """Runs GraphQL against the Admin API. Pass `transport` in tests to avoid network calls."""

    def __init__(self, transport: Transport | None = None):
        self._transport = transport or self._http

    def _http(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        url = f"https://{config.shopify_domain()}/admin/api/{config.SHOPIFY_API_VERSION}/graphql.json"

        def post(token: str) -> httpx.Response:
            return httpx.post(
                url,
                json={"query": query, "variables": variables},
                headers={"X-Shopify-Access-Token": token},
                timeout=30,
            )

        token = config.shopify_token()
        resp = post(token)
        if resp.status_code == 401 and config.forget_shopify_token(token):
            # A cached short-lived token was revoked or expired early: ask for a new one, once.
            # Fixed tokens are not retried, since asking again would return the same token.
            resp = post(config.shopify_token())
        resp.raise_for_status()
        return resp.json()

    def run(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        body = self._transport(query, variables or {})
        if body.get("errors"):
            raise ShopifyError(str(body["errors"]))
        data = body.get("data") or {}
        for value in data.values():
            if isinstance(value, dict) and value.get("userErrors"):
                raise ShopifyError(str(value["userErrors"]))
        return data
