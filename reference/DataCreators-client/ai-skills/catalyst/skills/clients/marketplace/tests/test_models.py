import pytest
from pydantic import ValidationError

from skills.clients.marketplace import models


def test_entity_type_pairs_code_with_label():
    et = models.EntityType(code="dataset_table", label="Dataset Table")
    assert et.code == "dataset_table"
    assert et.label == "Dataset Table"


def test_entity_type_label_inferred_from_known_code():
    """Common codes get a sensible default label."""
    et = models.EntityType.from_code("data_domain")
    assert et.label == "Data Domain"


def test_entity_type_unknown_code_uses_titlecased_label():
    et = models.EntityType.from_code("zz_unknown_type")
    assert et.label == "Zz Unknown Type"


def test_platform_known_codes_get_names():
    assert models.Platform.from_code("CSPN").name == "Caspian"
    assert models.Platform.from_code("CASPIAN").name == "Caspian"
    assert models.Platform.from_code("LASR").name == "LASR"


def test_platform_unknown_code_uses_code_as_name():
    p = models.Platform.from_code("ZZ_NEW")
    assert p.code == "ZZ_NEW"
    assert p.name == "ZZ_NEW"


def test_health_unrated_when_rating_null():
    h = models.Health(rating=None)
    assert h.status == "unrated"


def test_health_status_when_rating_present():
    h = models.Health(rating="Good")
    assert h.status == "Good"


def test_access_info_with_entitlement():
    a = models.AccessInfo(
        has_access=True,
        entitlements=["CPZ_PRD_AA00002933_IM_MGRTRANSPOS_READ"],
        request_access_url="https://marketplace.capgroup.com/entity/683/request-access",
        platform_code="CSPN",
    )
    assert a.has_access is True
    assert a.entitlements == ["CPZ_PRD_AA00002933_IM_MGRTRANSPOS_READ"]


def test_access_info_no_entitlement_means_publicly_accessible():
    a = models.AccessInfo(
        has_access=True, entitlements=[], request_access_url="...", platform_code="CSPN"
    )
    # Empty list is intentional — meaning is "no entitlement required."
    assert a.entitlements == []


def test_entity_minimal_fields():
    e = models.Entity(
        entity_id=683,
        name="CG Positions",
        description="...",
        type=models.EntityType(code="dataset_table", label="Dataset Table"),
        platform=models.Platform(code="CSPN", name="Caspian"),
        validated=True,
        health=models.Health(rating=None),
        ancestry=["Investment Management"],
        detail_url="https://marketplace.capgroup.com/entity/683",
    )
    assert e.entity_id == 683
    assert e.sources is None
    assert e.access is None


def test_entity_serializes_to_json_with_explicit_nulls():
    """Null fields must be present in the output, not omitted."""
    e = models.Entity(
        entity_id=683,
        name="CG Positions",
        description="...",
        type=models.EntityType(code="dataset_table", label="Dataset Table"),
        platform=models.Platform(code="CSPN", name="Caspian"),
        validated=True,
        health=models.Health(rating=None),
        ancestry=[],
        detail_url="https://marketplace.capgroup.com/entity/683",
    )
    data = e.model_dump(mode="json")
    assert data["sources"] is None  # not omitted
    assert data["access"] is None
    assert data["health"]["rating"] is None
    assert data["health"]["status"] == "unrated"


def test_search_results_pagination_fields():
    sr = models.SearchResults(
        items=[],
        total_count=0,
        current_page=1,
        page_size=25,
        total_pages=0,
    )
    assert sr.total_count == 0


def test_details_response_meta_block():
    """The full details response includes _meta provenance."""
    # We'll just verify the model accepts a _meta dict.
    meta = models.ResponseMeta(
        fetched_at="2026-04-29T18:30:00Z",
        endpoints_called=6,
        schema_version="1.0",
    )
    assert meta.endpoints_called == 6


def test_details_response_serializes_meta_with_underscore_key():
    """DetailsResponse must emit `_meta` (alias), not `meta` (attribute name).

    The CLI at Task 13 relies on `data["_meta"]` being present in JSON output.
    """
    minimal_entity = models.Entity(
        entity_id=1,
        name="x",
        description="",
        type=models.EntityType(code="dataset", label="Dataset"),
        platform=models.Platform(code="CSPN", name="Caspian"),
        validated=True,
        health=models.Health(rating=None),
        ancestry=[],
        detail_url="https://x/entity/1",
    )
    dr = models.DetailsResponse(
        entity=minimal_entity,
        _meta=models.ResponseMeta(
            fetched_at="2026-04-29T18:00:00Z",
            endpoints_called=2,
        ),
    )
    data = dr.model_dump(by_alias=True, mode="json")
    assert "_meta" in data, f"expected '_meta' in keys, got {list(data.keys())}"
    assert "meta" not in data
    assert data["_meta"]["endpoints_called"] == 2
