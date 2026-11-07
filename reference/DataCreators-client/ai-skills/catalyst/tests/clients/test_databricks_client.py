"""Unit tests for skills.clients.databricks.DatabricksClient.

All tests are offline -- no live Databricks connection is required.
The Databricks SDK import is patched at the property level so the tests
don't need the package installed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from skills.clients.databricks import DatabricksClient


# ---------------------------------------------------------------------------
# Construction tests
# ---------------------------------------------------------------------------


class TestInit:
    def test_init_requires_host(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        with pytest.raises(ValueError, match="host"):
            DatabricksClient(host="", client_id="cid", client_secret="csec")

    def test_init_requires_client_id(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        with pytest.raises(ValueError, match="client_id"):
            DatabricksClient(
                host="https://adb-1.azuredatabricks.net",
                client_id="",
                client_secret="csec",
            )

    def test_init_requires_client_secret(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        with pytest.raises(ValueError, match="client_secret"):
            DatabricksClient(
                host="https://adb-1.azuredatabricks.net",
                client_id="cid",
                client_secret="",
            )

    def test_init_refuses_when_pat_env_set(self, monkeypatch):
        """PAT auth is forbidden by DBX-SEC-002 -- refuse if DATABRICKS_TOKEN set."""
        monkeypatch.setenv("DATABRICKS_TOKEN", "dapi-leftover")
        with pytest.raises(RuntimeError, match="DBX-SEC-002"):
            DatabricksClient(
                host="https://adb-1.azuredatabricks.net",
                client_id="cid",
                client_secret="csec",
            )

    def test_init_stores_config(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        client = DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid-abc",
            client_secret="sec-xyz",
            warehouse_id="wh-xyz",
        )
        assert client.host == "https://adb-1.azuredatabricks.net"
        assert client._client_id == "cid-abc"
        assert client._client_secret == "sec-xyz"
        assert client._warehouse_id == "wh-xyz"

    def test_init_validates_warehouse_id_when_provided(self, monkeypatch):
        """Warehouse ID validation must happen at __init__, not lazily."""
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        with pytest.raises(ValueError, match="warehouse_id"):
            DatabricksClient(
                host="https://adb-1.azuredatabricks.net",
                client_id="cid",
                client_secret="csec",
                warehouse_id="   ",
            )

    def test_init_accepts_no_warehouse_id(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        client = DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid",
            client_secret="csec",
        )
        assert client._warehouse_id is None

    def test_warehouse_id_property_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        client = DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid",
            client_secret="csec",
        )
        with pytest.raises(ValueError, match="warehouse_id"):
            _ = client.warehouse_id

    def test_warehouse_id_property_returns_value_when_set(self, monkeypatch):
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        client = DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid",
            client_secret="csec",
            warehouse_id="wh-999",
        )
        assert client.warehouse_id == "wh-999"

    def test_client_property_uses_oauth_m2m(self, monkeypatch):
        """Lazy WorkspaceClient construction must use OAuth M2M auth."""
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        client = DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid-abc",
            client_secret="sec-xyz",
        )
        fake_ws = MagicMock()
        fake_ws.config.host = "https://adb-1.azuredatabricks.net"
        with patch("databricks.sdk.WorkspaceClient", return_value=fake_ws) as ctor:
            _ = client.client
            ctor.assert_called_once_with(
                host="https://adb-1.azuredatabricks.net",
                client_id="cid-abc",
                client_secret="sec-xyz",
                auth_type="oauth-m2m",
            )


# ---------------------------------------------------------------------------
# execute_sql tests
# ---------------------------------------------------------------------------


class TestExecuteSql:
    def _make_client(
        self, monkeypatch, warehouse_id: str | None = "wh-default"
    ) -> DatabricksClient:
        monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
        return DatabricksClient(
            host="https://adb-1.azuredatabricks.net",
            client_id="cid-abc",
            client_secret="sec-xyz",
            warehouse_id=warehouse_id,
        )

    def test_execute_sql_requires_warehouse_id(self, monkeypatch):
        client = self._make_client(monkeypatch, warehouse_id=None)
        with pytest.raises(ValueError, match="warehouse_id"):
            client.execute_sql("SELECT 1")

    def test_execute_sql_raises_on_empty_sql(self, monkeypatch):
        client = self._make_client(monkeypatch)
        with pytest.raises(ValueError, match="empty"):
            client.execute_sql("   ")

    def test_execute_sql_calls_sdk(self, monkeypatch):
        client = self._make_client(monkeypatch)

        mock_resp = MagicMock()
        mock_resp.as_dict.return_value = {"status": {"state": "SUCCEEDED"}}

        mock_sdk = MagicMock()
        mock_sdk.statement_execution.execute_statement.return_value = mock_resp
        client._client = mock_sdk

        result = client.execute_sql("SELECT 1", warehouse_id="wh-test")

        mock_sdk.statement_execution.execute_statement.assert_called_once_with(
            warehouse_id="wh-test",
            statement="SELECT 1",
            wait_timeout="50s",
        )
        assert result == {"status": {"state": "SUCCEEDED"}}

    def test_execute_sql_uses_instance_warehouse_id_by_default(self, monkeypatch):
        client = self._make_client(monkeypatch, warehouse_id="wh-instance")

        mock_resp = MagicMock()
        mock_resp.as_dict.return_value = {}
        mock_sdk = MagicMock()
        mock_sdk.statement_execution.execute_statement.return_value = mock_resp
        client._client = mock_sdk

        client.execute_sql("SELECT 1")

        call_kwargs = mock_sdk.statement_execution.execute_statement.call_args.kwargs
        assert call_kwargs["warehouse_id"] == "wh-instance"

    def test_execute_sql_sdk_fallback(self, monkeypatch):
        client = self._make_client(monkeypatch, warehouse_id="wh-fallback")

        mock_sdk = MagicMock()
        mock_sdk.statement_execution.execute_statement.side_effect = AttributeError
        mock_sdk.api_client.do.return_value = {"result": {}}
        client._client = mock_sdk

        result = client.execute_sql("SELECT 1")

        mock_sdk.api_client.do.assert_called_once()
        assert result == {"result": {}}

    def test_execute_sql_override_warehouse_id(self, monkeypatch):
        client = self._make_client(monkeypatch, warehouse_id="wh-default")

        mock_resp = MagicMock()
        mock_resp.as_dict.return_value = {}
        mock_sdk = MagicMock()
        mock_sdk.statement_execution.execute_statement.return_value = mock_resp
        client._client = mock_sdk

        client.execute_sql("SELECT 1", warehouse_id="wh-override")

        call_kwargs = mock_sdk.statement_execution.execute_statement.call_args.kwargs
        assert call_kwargs["warehouse_id"] == "wh-override"
