import json
import subprocess
import sys
from unittest.mock import patch

import pytest

from skills.clients.marketplace import cli


def _run_main(argv, monkeypatch):
    """Invoke cli.main(argv) and return (exit_code, captured_stdout, captured_stderr)."""
    import io
    monkeypatch.setattr(sys, "argv", ["marketplace"] + argv)
    out, err = io.StringIO(), io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    try:
        rc = cli.main()
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


# ----- whoami -----------------------------------------------------------------

def test_whoami_no_token_exits_3(isolated_config_dir, monkeypatch):
    rc, out, err = _run_main(["whoami"], monkeypatch)
    assert rc == 3
    assert "no token" in err.lower() or "missing" in err.lower()


def test_whoami_valid_exits_0(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": True, "reason": None},
    ):
        rc, out, err = _run_main(["whoami"], monkeypatch)
    assert rc == 0
    data = json.loads(out)
    assert data["valid"] is True


def test_whoami_expired_exits_2(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": False, "reason": "expired"},
    ):
        rc, out, err = _run_main(["whoami"], monkeypatch)
    assert rc == 2


def test_help_lists_all_subcommands(monkeypatch):
    rc, out, err = _run_main(["--help"], monkeypatch)
    text = out + err
    for sub in ("whoami", "login", "search", "details"):
        assert sub in text, f"subcommand {sub} missing from help"


# ----- login ------------------------------------------------------------------

def test_login_invokes_bootstrap(isolated_config_dir, monkeypatch):
    with patch("skills.clients.marketplace.bootstrap.login") as mock_login:
        rc, out, err = _run_main(["login"], monkeypatch)
    assert mock_login.called
    assert rc == 0


def test_login_propagates_keyboard_interrupt_as_exit_3(isolated_config_dir, monkeypatch):
    """User Ctrl-C during login → exit 3 (cancelled)."""
    with patch("skills.clients.marketplace.bootstrap.login", side_effect=KeyboardInterrupt):
        rc, out, err = _run_main(["login"], monkeypatch)
    assert rc == 3


# ----- search -----------------------------------------------------------------

def test_search_no_token_exits_3(isolated_config_dir, monkeypatch):
    rc, out, err = _run_main(["search", "client risk", "--json"], monkeypatch)
    assert rc == 3


def test_search_emits_json_with_flag(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth, models
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    fake_results = models.SearchResults(
        items=[],
        total_count=0,
        current_page=1,
        page_size=25,
        total_pages=0,
    )
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": True, "reason": None},
    ), patch(
        "skills.clients.marketplace.client.MarketplaceClient.search",
        return_value=fake_results,
    ):
        rc, out, err = _run_main(["search", "client risk", "--json"], monkeypatch)
    assert rc == 0
    data = json.loads(out)
    assert data["total_count"] == 0


def test_search_human_table_without_json_flag(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth, models
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    fake_results = models.SearchResults(
        items=[
            models.Entity(
                entity_id=1, name="Foo", description="bar",
                type=models.EntityType.from_code("dataset"),
                platform=models.Platform.from_code("CSPN"),
                validated=True,
                health=models.Health(rating=None),
                ancestry=[],
                detail_url="https://x/entity/1",
                search_rank=0.5,
            ),
        ],
        total_count=1, current_page=1, page_size=25, total_pages=1,
    )
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": True, "reason": None},
    ), patch(
        "skills.clients.marketplace.client.MarketplaceClient.search",
        return_value=fake_results,
    ):
        rc, out, err = _run_main(["search", "foo"], monkeypatch)
    assert rc == 0
    assert "Foo" in out
    assert "dataset" in out.lower() or "Dataset" in out


def test_search_token_expired_exits_2(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": False, "reason": "expired"},
    ):
        rc, out, err = _run_main(["search", "x", "--json"], monkeypatch)
    assert rc == 2


def test_search_propagates_types_flag(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth, models
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    fake_results = models.SearchResults(
        items=[], total_count=0, current_page=1, page_size=25, total_pages=0,
    )
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": True, "reason": None},
    ), patch(
        "skills.clients.marketplace.client.MarketplaceClient.search",
        return_value=fake_results,
    ) as mock_search:
        _run_main(
            ["search", "x", "--types", "dataset,data_product", "--json"], monkeypatch,
        )
    assert mock_search.call_args.kwargs["types"] == ["dataset", "data_product"]


# ----- details ----------------------------------------------------------------

def test_details_emits_json_with_meta(isolated_config_dir, monkeypatch):
    from skills.clients.marketplace import auth, models
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    fake_entity = models.Entity(
        entity_id=683, name="X", description="",
        type=models.EntityType.from_code("dataset_table"),
        platform=models.Platform.from_code("CSPN"),
        validated=True,
        health=models.Health(rating=None),
        ancestry=[],
        detail_url="https://x/entity/683",
        sources={"dremio": ["a.b.c"]},
        access=models.AccessInfo(
            has_access=True, entitlements=["X_READ"],
            request_access_url="https://x/entity/683/request-access",
            platform_code="CSPN",
        ),
    )
    with patch(
        "skills.clients.marketplace.client.MarketplaceClient.whoami",
        return_value={"valid": True, "reason": None},
    ), patch(
        "skills.clients.marketplace.client.MarketplaceClient.details",
        return_value=fake_entity,
    ):
        rc, out, err = _run_main(["details", "683", "--json"], monkeypatch)
    assert rc == 0
    data = json.loads(out)
    assert data["entity"]["entity_id"] == 683
    assert "_meta" in data
    assert data["_meta"]["endpoints_called"] == 6


# ----- --schema ---------------------------------------------------------------

def test_schema_flag_emits_json_schema(monkeypatch):
    rc, out, err = _run_main(["--schema", "details"], monkeypatch)
    assert rc == 0
    schema = json.loads(out)
    assert "$defs" in schema or "properties" in schema
    assert "entity" in json.dumps(schema)
