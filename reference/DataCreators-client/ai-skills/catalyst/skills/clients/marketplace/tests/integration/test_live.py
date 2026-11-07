"""Integration tests against the live marketplace API.

Skipped automatically if no token is cached. Run locally before shipping.
NOT run in CI.
"""

import pytest

pytestmark = pytest.mark.integration


def test_whoami_against_live_api(real_client):
    result = real_client.whoami()
    assert result["valid"] is True


def test_search_returns_results_for_known_query(real_client):
    """A query like 'client' should always have *some* results."""
    results = real_client.search("client")
    assert results.total_count > 0
    assert len(results.items) > 0
    first = results.items[0]
    assert first.entity_id > 0
    assert first.name
    assert first.type.code
    assert first.platform.code


def test_search_empty_results_for_known_garbage(real_client):
    results = real_client.search("xyzzy123nothere9999notavailable")
    assert results.total_count == 0
    assert results.items == []


def test_search_pagination(real_client):
    page1 = real_client.search("client", page=1, page_size=3)
    if page1.total_pages > 1:
        page2 = real_client.search("client", page=2, page_size=3)
        ids1 = {it.entity_id for it in page1.items}
        ids2 = {it.entity_id for it in page2.items}
        assert ids1 != ids2, "Page 1 and 2 returned identical results"


def test_details_round_trip_caspian(real_client):
    """Pick an entity from a search and run details() on it. Caspian-only."""
    results = real_client.search("client", page_size=20)
    cspn = next(
        (it for it in results.items if it.platform.code in ("CSPN", "CASPIAN")),
        None,
    )
    if cspn is None:
        pytest.skip("No Caspian entity in top results.")
    entity = real_client.details(cspn.entity_id)
    assert entity.entity_id == cspn.entity_id
    assert entity.access is not None
    assert entity.access.platform_code in ("CSPN", "CASPIAN")
    assert isinstance(entity.access.entitlements, list)
