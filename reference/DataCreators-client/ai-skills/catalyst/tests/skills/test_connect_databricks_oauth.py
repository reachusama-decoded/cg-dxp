"""Unit tests for the OAuth connector (DBX-SEC-002).

Mocks the Databricks SDK; integration tests live under tests/integration/.

The skill directory uses a hyphen (`connect-databricks/`) which is not a
valid Python module name, so we load `oauth_connect.py` via importlib.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
OAUTH_CONNECT_PATH = (
    REPO_ROOT / "skills" / "connect-databricks" / "scripts" / "oauth_connect.py"
)


def _load_oauth_connect():
    spec = importlib.util.spec_from_file_location(
        "connect_databricks_oauth_connect", OAUTH_CONNECT_PATH
    )
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def oauth_connect():
    return _load_oauth_connect()


def test_pat_token_refused(oauth_connect, monkeypatch, capsys):
    monkeypatch.setenv("DATABRICKS_TOKEN", "dapi-x")
    monkeypatch.setenv("DATABRICKS_HOST", "https://x")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "id")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "s")
    with pytest.raises(SystemExit) as exc:
        oauth_connect.main()
    assert exc.value.code == 3
    err = capsys.readouterr().err
    assert "DBX-SEC-002" in err


def test_missing_env_vars(oauth_connect, monkeypatch):
    monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_CLIENT_ID", raising=False)
    monkeypatch.delenv("DATABRICKS_CLIENT_SECRET", raising=False)
    with pytest.raises(SystemExit) as exc:
        oauth_connect.main()
    assert exc.value.code == 2


def test_happy_path(oauth_connect, monkeypatch, tmp_path):
    monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
    monkeypatch.setenv("DATABRICKS_HOST", "https://x.cloud.databricks.com")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "client-id")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "secret")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "wh-1")
    monkeypatch.setenv("HOME", str(tmp_path))

    with patch.object(oauth_connect, "WorkspaceClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.statement_execution.execute_statement.return_value.status.state = (
            oauth_connect.StatementState.SUCCEEDED
        )
        mock_client_cls.return_value = mock_client

        oauth_connect.main()

    session_path = tmp_path / ".databricks" / "last_oauth_session.json"
    assert session_path.exists()
    import json

    data = json.loads(session_path.read_text())
    assert data["auth_type"] == "oauth-m2m"
    assert data["warehouse_id"] == "wh-1"
    assert data["host"] == "https://x.cloud.databricks.com"
    assert data["client_id"] == "client-id"
