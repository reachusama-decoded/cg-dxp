# Warehouse Not Running — Full Fix

## Symptoms to grep for

```
WAREHOUSE_NOT_RUNNING
HTTPError 404
dbt query timeout
Connection timed out
http_path 404
```

## Root cause

The Databricks SQL warehouse specified in `profiles.yml` is stopped
(auto-stop triggered) or the warehouse ID is incorrect.

## Diagnostic steps

1. Extract the warehouse ID from `profiles.yml` (`http_path` contains it,
   e.g., `/sql/1.0/warehouses/abc123`).
2. Check warehouse state:
   ```bash
   databricks sql warehouses get abc123
   ```
   Inspect the `state` field — expect `RUNNING`. If `STOPPED` or `DELETED`,
   proceed to fix.
3. Confirm the `http_path` is correct by listing available warehouses:
   ```bash
   databricks sql warehouses list
   ```

## Fix

Start the warehouse from the Databricks UI, or programmatically via the
Python SDK (e.g., in a pre-task or init notebook):

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
w.warehouses.start("abc123")
# Optionally wait for it to reach RUNNING state
w.warehouses.get_and_wait("abc123")
```

To avoid recurrence, set `auto_stop_mins` to a non-zero value (minimum 10)
in the warehouse configuration, or use a serverless warehouse that scales to
zero and back instantly.

See `/databricks-docs` to fetch the official SQL Warehouses API reference.
