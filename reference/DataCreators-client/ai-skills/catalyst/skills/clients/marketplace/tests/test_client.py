import json
from pathlib import Path

import pytest
import responses

from skills.clients.marketplace import client, exceptions as exc, models

API = "https://marketplace-service.datalake.aws.capgroup.com"


@pytest.fixture
def cli(monkeypatch):
    """Build a client with a known bearer + API base URL — no env reads."""
    return client.MarketplaceClient(
        bearer="Bearer eyTEST",
        api_base_url=API,
    )


def _load_fixture(fixtures_dir, name):
    return json.loads((fixtures_dir / name).read_text())


@responses.activate
def test_search_minimal_request(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
        content_type="application/json",
    )
    results = cli.search("client risk")
    assert isinstance(results, models.SearchResults)
    assert results.total_count >= 0
    if results.items:
        assert isinstance(results.items[0], models.Entity)
        assert results.items[0].entity_id > 0


@responses.activate
def test_search_post_body_carries_keyword_and_default_types(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
    )
    cli.search("client risk")
    sent_body = json.loads(responses.calls[0].request.body)
    assert sent_body["keyword"] == "client risk"
    assert "data_product" in sent_body["levelTypes"]
    assert "dataset" in sent_body["levelTypes"]


@responses.activate
def test_search_pagination_query_string(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
    )
    cli.search("client risk", page=2, page_size=50)
    qs = responses.calls[0].request.url
    assert "page=2" in qs
    assert "pageSize=50" in qs


@responses.activate
def test_search_with_parent_id_in_body(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
    )
    cli.search("client risk", parent_id=1832)
    sent = json.loads(responses.calls[0].request.body)
    assert sent["parents"] == [{"parentId": 1832}]


@responses.activate
def test_search_authorization_header_sent(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
    )
    cli.search("client risk")
    auth_header = responses.calls[0].request.headers["Authorization"]
    assert auth_header == "Bearer eyTEST"


@responses.activate
def test_search_401_raises_token_expired(cli):
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        json={"error": "Unauthorized"},
        status=401,
    )
    with pytest.raises(exc.TokenExpiredError):
        cli.search("client risk")


@responses.activate
def test_search_500_raises_marketplace_error(cli):
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body="server error",
        status=500,
    )
    with pytest.raises(exc.MarketplaceError):
        cli.search("client risk")


@responses.activate
def test_search_empty_results(cli):
    empty = {
        "stats": {"totalCount": 0, "types": [], "currentPage": 1, "pageSize": 25, "totalPages": 0},
        "items": [],
    }
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        json=empty,
        status=200,
    )
    results = cli.search("xyzzy123nothere")
    assert results.total_count == 0
    assert results.items == []


@responses.activate
def test_search_unicode_keyword(cli, fixtures_dir):
    fix = _load_fixture(fixtures_dir, "search_response.json")
    responses.add(
        responses.POST,
        f"{API}/api/v1/marketplace/search/entities",
        body=fix["response"]["body"],
        status=200,
    )
    cli.search("résumé naïve")
    sent = json.loads(responses.calls[0].request.body)
    assert sent["keyword"] == "résumé naïve"


def test_from_cache_raises_token_missing_when_absent(isolated_config_dir):
    with pytest.raises(exc.TokenMissingError):
        client.MarketplaceClient.from_cache()


def test_from_cache_uses_token(isolated_config_dir):
    from skills.clients.marketplace import auth
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    cli = client.MarketplaceClient.from_cache()
    assert cli._bearer == "Bearer eyXXX"
    assert cli._api_base_url == "https://example.com"


# ===== details() tests ========================================================

@responses.activate
def test_details_calls_six_endpoints_for_caspian(cli, fixtures_dir):
    """details() aggregates: entity, consumable, fields, business-terms, preview, access."""
    entity_fix = _load_fixture(fixtures_dir, "entity_detail_response.json")
    consumable_fix = _load_fixture(fixtures_dir, "consumable_response.json")
    fields_fix = _load_fixture(fixtures_dir, "fields_response.json")
    bt_fix = _load_fixture(fixtures_dir, "business_terms_response.json")
    preview_fix = _load_fixture(fixtures_dir, "preview_response.json")
    access_fix = _load_fixture(fixtures_dir, "view_access_response.json")

    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/entities/683",
        body=entity_fix["response"]["body"], status=200,
    )
    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/entities/683/consumable",
        body=consumable_fix["response"]["body"], status=200,
    )
    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/table/fields/search",
        body=fields_fix["response"]["body"], status=200,
    )
    responses.add(
        responses.POST, f"{API}/api/v1/marketplace/business-terms/by-tables",
        body=bt_fix["response"]["body"], status=200,
    )
    responses.add(
        responses.POST, f"{API}/api/v1/marketplace/datadelivery/preview/by-views",
        body=preview_fix["response"]["body"], status=200,
    )
    responses.add(
        responses.POST, f"{API}/api/v1/marketplace/table/view-access",
        body=access_fix["response"]["body"], status=200,
    )

    entity = cli.details(683)
    assert entity.entity_id == 683
    assert entity.sources is not None
    assert entity.access is not None
    assert entity.access.platform_code == "CSPN" or entity.access.platform_code == "CASPIAN"
    assert entity.field_schema is not None
    assert entity.business_terms is not None
    assert entity.preview is not None


@responses.activate
def test_details_uses_lasr_access_endpoint_for_lasr_platform(cli, fixtures_dir):
    """LASR platform uses /entities/table-access with tableName strings, not viewPath arrays."""
    entity_body = json.dumps({
        "entityId": 1234, "type": "dataset_table", "name": "Test", "description": "",
        "isValidated": True, "platform": "LASR",
        "hierarchyInfo": {"ancestry": []},
        "health": {"rating": None},
    })
    consumable_body = json.dumps({
        "id": 1234, "type": "dataset_table", "name": "Test", "description": "",
        "platform": "LASR", "technicalName": "lasr-sqldwdb-prd.MSS_S_CDM_NS.test_table",
        "sources": [{"system": "lasr", "values": ["lasr-sqldwdb-prd.MSS_S_CDM_NS.test_table"]}],
    })
    table_access_body = json.dumps({
        "items": [{
            "tableName": "lasr-sqldwdb-prd.MSS_S_CDM_NS.test_table",
            "access": False,
            "entitlements": [{"name": "LASR_PRD_TEST_READ", "displayName": None}],
        }],
    })

    responses.add(responses.GET, f"{API}/api/v1/marketplace/entities/1234",
                  body=entity_body, status=200)
    responses.add(responses.GET, f"{API}/api/v1/marketplace/entities/1234/consumable",
                  body=consumable_body, status=200)
    responses.add(responses.GET, f"{API}/api/v1/marketplace/table/fields/search",
                  json={"items": []}, status=200)
    responses.add(responses.POST, f"{API}/api/v1/marketplace/business-terms/by-tables",
                  json={"items": []}, status=200)
    responses.add(responses.POST, f"{API}/api/v1/marketplace/datadelivery/preview/by-views",
                  json={"rows": []}, status=200)
    responses.add(responses.POST, f"{API}/api/v1/marketplace/entities/table-access",
                  body=table_access_body, status=200)

    entity = cli.details(1234)
    assert entity.platform.code == "LASR"
    assert entity.access.has_access is False
    assert "LASR_PRD_TEST_READ" in entity.access.entitlements


@responses.activate
def test_details_unknown_platform_raises_unsupported(cli):
    entity_body = json.dumps({
        "entityId": 1, "type": "dataset_table", "name": "Z", "description": "",
        "isValidated": False, "platform": "SNOWFLAKE",
        "hierarchyInfo": {"ancestry": []}, "health": {"rating": None},
    })
    consumable_body = json.dumps({
        "id": 1, "type": "dataset_table", "name": "Z", "description": "",
        "platform": "SNOWFLAKE", "technicalName": "snowflake.x", "sources": [],
    })
    responses.add(responses.GET, f"{API}/api/v1/marketplace/entities/1",
                  body=entity_body, status=200)
    responses.add(responses.GET, f"{API}/api/v1/marketplace/entities/1/consumable",
                  body=consumable_body, status=200)
    responses.add(responses.GET, f"{API}/api/v1/marketplace/table/fields/search",
                  json={"items": []}, status=200)
    responses.add(responses.POST, f"{API}/api/v1/marketplace/business-terms/by-tables",
                  json={"items": []}, status=200)
    responses.add(responses.POST, f"{API}/api/v1/marketplace/datadelivery/preview/by-views",
                  json={"rows": []}, status=200)

    with pytest.raises(exc.UnsupportedPlatformError) as ei:
        cli.details(1)
    assert ei.value.platform == "SNOWFLAKE"


# ===== whoami() tests =========================================================

@responses.activate
def test_whoami_200_returns_valid(cli):
    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/labels",
        json={"items": []}, status=200,
    )
    result = cli.whoami()
    assert result["valid"] is True


@responses.activate
def test_whoami_401_returns_expired(cli):
    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/labels",
        json={"error": "Unauthorized"}, status=401,
    )
    result = cli.whoami()
    assert result["valid"] is False
    assert result["reason"] == "expired"


@responses.activate
def test_whoami_5xx_returns_unknown(cli):
    """Server error doesn't mean the token is bad."""
    responses.add(
        responses.GET, f"{API}/api/v1/marketplace/labels",
        body="oops", status=503,
    )
    result = cli.whoami()
    assert result["valid"] is False
    assert result["reason"] == "unknown"
