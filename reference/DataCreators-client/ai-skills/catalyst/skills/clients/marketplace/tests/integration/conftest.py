"""Integration test fixtures — gated by token presence."""

import pytest

from skills.clients.marketplace import auth


def has_token() -> bool:
    return auth.load_token() is not None


@pytest.fixture(scope="session")
def real_client():
    if not has_token():
        pytest.skip("No marketplace token cached; run `marketplace login` to enable integration tests.")
    from skills.clients.marketplace import client
    return client.MarketplaceClient.from_cache()
