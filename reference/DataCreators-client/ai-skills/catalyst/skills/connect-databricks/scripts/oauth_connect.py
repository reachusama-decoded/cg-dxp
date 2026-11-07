"""OAuth client-credentials connector for Databricks (DBX-SEC-002)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


def fail(code: int, message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def main() -> None:
    if os.environ.get("DATABRICKS_TOKEN"):
        fail(
            3,
            "DATABRICKS_TOKEN detected. PAT authentication is forbidden by "
            "DBX-SEC-002. Unset DATABRICKS_TOKEN and use OAuth client "
            "credentials (DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET).",
        )

    required = ["DATABRICKS_HOST", "DATABRICKS_CLIENT_ID", "DATABRICKS_CLIENT_SECRET"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        fail(2, f"Missing required environment variables: {missing}")

    try:
        client = WorkspaceClient(
            host=os.environ["DATABRICKS_HOST"],
            client_id=os.environ["DATABRICKS_CLIENT_ID"],
            client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
        )
    except Exception as exc:
        fail(4, f"OAuth token exchange failed: {exc}")

    warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID")
    if not warehouse_id:
        warehouses = list(client.warehouses.list())
        if not warehouses:
            fail(5, "No SQL warehouses available in workspace.")
        warehouse_id = warehouses[0].id

    try:
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement="SELECT 1",
            wait_timeout="30s",
        )
        if statement.status.state != StatementState.SUCCEEDED:
            fail(5, f"SELECT 1 failed: {statement.status.error}")
    except Exception as exc:
        fail(5, f"SELECT 1 execution failed: {exc}")

    session_path = Path.home() / ".databricks" / "last_oauth_session.json"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(
        json.dumps(
            {
                "host": os.environ["DATABRICKS_HOST"],
                "client_id": os.environ["DATABRICKS_CLIENT_ID"],
                "warehouse_id": warehouse_id,
                "auth_type": "oauth-m2m",
            },
            indent=2,
        )
    )

    print(f"Connected to {os.environ['DATABRICKS_HOST']} via OAuth M2M.")
    print(f"Warehouse: {warehouse_id}")
    print(f"Session metadata: {session_path}")


if __name__ == "__main__":
    main()
