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

        def post() -> httpx.Response:
            return httpx.post(
                url,
                json={"query": query, "variables": variables},
                headers={"X-Shopify-Access-Token": config.shopify_token()},
                timeout=30,
            )

        resp = post()
        if resp.status_code == 401:
            # A cached short-lived token was revoked or expired early: ask for a new one, once.
            config.forget_shopify_token()
            resp = post()
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
