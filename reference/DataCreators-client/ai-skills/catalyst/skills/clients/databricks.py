"""Databricks client for Catalyst skills.

Wraps the Databricks SDK for SQL statement execution and catalog exploration.
Auth is OAuth client-credentials (M2M) per DBX-SEC-002. Callers are
responsible for loading credentials from environment or config before
constructing the client.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DatabricksClient:
    """Unified client wrapping the Databricks SDK for common operations.

    Authenticates via OAuth client credentials (M2M) per DBX-SEC-002.
    PAT authentication is not supported.
    """

    def __init__(
        self,
        host: str,
        client_id: str,
        client_secret: str,
        warehouse_id: str | None = None,
    ):
        """Initialize the Databricks client.

        Args:
            host: Databricks workspace URL (e.g. https://adb-xxx.azuredatabricks.net).
            client_id: OAuth M2M client ID (service principal application ID).
            client_secret: OAuth M2M client secret.
            warehouse_id: SQL Warehouse ID for statement execution. If provided,
                          it is validated to be a non-empty string immediately so
                          callers get a clear error at construction time rather
                          than at first query.

        Raises:
            ValueError: If host, client_id, or client_secret are empty, or if
                        warehouse_id is provided but is an empty string.
            RuntimeError: If DATABRICKS_TOKEN is set in the environment. PAT
                          authentication is forbidden by DBX-SEC-002.
        """
        if not host:
            raise ValueError("host must be a non-empty string")
        if not client_id:
            raise ValueError("client_id must be a non-empty string")
        if not client_secret:
            raise ValueError("client_secret must be a non-empty string")
        if warehouse_id is not None and not warehouse_id.strip():
            raise ValueError(
                "warehouse_id must be a non-empty string when provided"
            )

        if os.environ.get("DATABRICKS_TOKEN"):
            raise RuntimeError(
                "DATABRICKS_TOKEN detected. PAT authentication is forbidden "
                "by DBX-SEC-002. Unset DATABRICKS_TOKEN and use OAuth client "
                "credentials (DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET)."
            )

        self._host = host
        self._client_id = client_id
        self._client_secret = client_secret
        self._warehouse_id: str | None = warehouse_id
        self._client: Any = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def host(self) -> str:
        return self._host

    @property
    def warehouse_id(self) -> str:
        """Return the configured warehouse ID.

        Raises:
            ValueError: If no warehouse_id was supplied at construction time.
        """
        if not self._warehouse_id:
            raise ValueError(
                "warehouse_id is required for SQL execution. "
                "Pass warehouse_id to DatabricksClient.__init__."
            )
        return self._warehouse_id

    @property
    def client(self) -> Any:
        """Lazily initialise and return the Databricks WorkspaceClient (OAuth M2M)."""
        if self._client is None:
            from databricks.sdk import WorkspaceClient  # type: ignore[import]

            self._client = WorkspaceClient(
                host=self._host,
                client_id=self._client_id,
                client_secret=self._client_secret,
                auth_type="oauth-m2m",
            )
            logger.info(
                "Databricks client initialised (host=%s, auth=oauth-m2m)",
                self._client.config.host,
            )
        return self._client

    # ------------------------------------------------------------------
    # SQL execution
    # ------------------------------------------------------------------

    def execute_sql(
        self,
        sql: str,
        warehouse_id: str | None = None,
        wait_timeout: str = "50s",
    ) -> dict[str, Any]:
        """Execute SQL via the Statement Execution API.

        Args:
            sql: SQL statement to execute.
            warehouse_id: Override the instance-level warehouse ID for this call.
            wait_timeout: Timeout for synchronous results (0 or 5-50 s).

        Returns:
            Response dict from the API.

        Raises:
            ValueError: If no warehouse_id is available or sql is empty.
        """
        wid = warehouse_id or self.warehouse_id  # raises if not set
        sql = sql.strip()
        if not sql:
            raise ValueError("SQL statement is empty")

        logger.debug("Executing SQL on warehouse %s: %.100s...", wid, sql)

        try:
            resp = self.client.statement_execution.execute_statement(
                warehouse_id=wid,
                statement=sql,
                wait_timeout=wait_timeout,
            )
        except AttributeError:
            # Fallback for older SDK versions that expose a raw API client.
            payload = {
                "warehouse_id": wid,
                "statement": sql,
                "wait_timeout": wait_timeout,
            }
            resp = self.client.api_client.do(
                "POST", "/api/2.0/sql/statements/", body=payload
            )

        if hasattr(resp, "as_dict"):
            return resp.as_dict()
        elif hasattr(resp, "to_dict"):
            return resp.to_dict()
        return resp

    def execute_sql_file(
        self,
        sql_file: str | Path,
        warehouse_id: str | None = None,
        wait_timeout: str = "50s",
    ) -> dict[str, Any]:
        """Execute SQL read from a file.

        Args:
            sql_file: Path to a .sql file.
            warehouse_id: Override the instance-level warehouse ID.
            wait_timeout: Timeout for synchronous results.
        """
        sql = Path(sql_file).read_text(encoding="utf-8")
        return self.execute_sql(sql, warehouse_id=warehouse_id, wait_timeout=wait_timeout)

    # ------------------------------------------------------------------
    # Catalog helpers
    # ------------------------------------------------------------------

    def list_catalogs(self) -> list[str]:
        """List Unity Catalog catalogs visible to this workspace."""
        resp = self.execute_sql("SHOW CATALOGS")
        return _extract_column(resp, 0)

    def list_schemas(self, catalog: str) -> list[str]:
        """List schemas inside *catalog*."""
        resp = self.execute_sql(f"SHOW SCHEMAS IN `{catalog}`")
        return _extract_column(resp, 0)

    def list_tables(self, catalog: str, schema: str) -> list[str]:
        """List tables inside *catalog*.*schema*."""
        resp = self.execute_sql(f"SHOW TABLES IN `{catalog}`.`{schema}`")
        return _extract_column(resp, 1)  # tableName is column index 1

    def describe_table(self, full_table_name: str) -> list[dict[str, str]]:
        """Describe a table's columns.

        Args:
            full_table_name: Fully qualified name (catalog.schema.table).

        Returns:
            List of dicts with col_name, data_type, comment keys.
        """
        resp = self.execute_sql(f"DESCRIBE TABLE `{full_table_name}`")
        rows = resp.get("result", {}).get("data_array", [])
        return [
            {
                "col_name": r[0],
                "data_type": r[1],
                "comment": r[2] if len(r) > 2 else "",
            }
            for r in rows
        ]

    def sample_table(self, full_table_name: str, limit: int = 10) -> dict[str, Any]:
        """Return up to *limit* rows from a table."""
        return self.execute_sql(f"SELECT * FROM `{full_table_name}` LIMIT {limit}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_column(resp: dict[str, Any], col_index: int) -> list[str]:
    """Extract a single column from a statement-execution response data array."""
    rows = resp.get("result", {}).get("data_array", [])
    return [row[col_index] for row in rows if len(row) > col_index]


def _parse_data_array(resp: dict) -> list[list]:
    """Extract the data_array rows from a statement-execution response."""
    return resp.get("result", {}).get("data_array", [])
