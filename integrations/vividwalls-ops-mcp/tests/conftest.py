import pytest

from vividwalls_ops import config


@pytest.fixture(autouse=True)
def no_real_credentials(monkeypatch):
    """Tests never read the developer's Keychain or token environment, so a machine with real
    tokens installed cannot make live Shopify or Pictorem requests from the suite."""
    monkeypatch.setattr(config, "keychain_secret", lambda service, account=None: "")
    monkeypatch.delenv("SHOPIFY_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("PICTOREM_ARTFLOW_KEY", raising=False)
