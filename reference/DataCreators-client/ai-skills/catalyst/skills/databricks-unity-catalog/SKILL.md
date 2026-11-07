---
name: databricks-unity-catalog
description: |
  Unity Catalog system tables and volumes. Use when querying system tables
  (audit, lineage, billing) or working with volume file operations
  (upload, download, list files in /Volumes/).
  Catalyst trigger phrases: "set up Unity Catalog schema", "create UC volume", "grant on catalog".
allowed-tools: Read Bash Write Edit
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-UC-001
    - DBX-UC-002
    - DBX-UC-003
  upstream-source: databricks-solutions/ai-dev-kit/databricks-skills/databricks-unity-catalog
  upstream-commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
  upstream-license: Databricks (custom — see third-party/LICENSE-databricks.md)
  catalyst-modifications: |
    Modified by Capital Group on 2026-05-14:
    - dropped MCP tool references (Catalyst policy); replaced with Python function
      calls in skills/clients/databricks_tools_core/unity_catalog/ and sql/
    - added metadata.standards citations (RFD 0008)
    - added Catalyst trigger phrases in description
---

> _Modified from `databricks-solutions/ai-dev-kit/databricks-skills/databricks-unity-catalog` by Capital Group on 2026-05-14. See `metadata.catalyst-modifications` for the change set._

# Unity Catalog

Guidance for Unity Catalog system tables, volumes, and governance.

## When to Use This Skill

Use this skill when:
- Working with **volumes** (upload, download, list files in `/Volumes/`)
- Querying **lineage** (table dependencies, column-level lineage)
- Analyzing **audit logs** (who accessed what, permission changes)
- Monitoring **billing and usage** (DBU consumption, cost analysis)
- Tracking **compute resources** (cluster usage, warehouse metrics)
- Reviewing **job execution** (run history, success rates, failures)
- Analyzing **query performance** (slow queries, warehouse utilization)
- Profiling **data quality** (data profiling, drift detection, metric tables)

## Reference Files

| Topic | File | Description |
|-------|------|-------------|
| System Tables | [5-system-tables.md](5-system-tables.md) | Lineage, audit, billing, compute, jobs, query history |
| Volumes | [6-volumes.md](6-volumes.md) | Volume file operations, permissions, best practices |
| Data Profiling | [7-data-profiling.md](7-data-profiling.md) | Data profiling, drift detection, profile metrics |

## Quick Start

### Volume File Operations

Invoke the corresponding Python functions in `skills/clients/databricks_tools_core/`:

```python
from skills.clients.databricks_tools_core.file import (
    list_volume_files,
    get_volume_folder_details,
    upload_to_volume,
    download_from_volume,
    create_volume_directory,
)

# List files in a volume path
list_volume_files(volume_path="/Volumes/catalog/schema/volume/path/")

# Get folder details (schema, row counts, stats)
get_volume_folder_details(volume_path="catalog/schema/volume/path", format="parquet")

# Upload files
upload_to_volume(local_path="/tmp/data/*", volume_path="/Volumes/.../dest")

# Download a file
download_from_volume(volume_path="/Volumes/.../file.csv", local_path="/tmp/file.csv")

# Create a directory
create_volume_directory(volume_path="/Volumes/.../new_folder")
```

### Enable System Tables Access

```sql
-- Grant access to system tables
GRANT USE CATALOG ON CATALOG system TO `data_engineers`;
GRANT USE SCHEMA ON SCHEMA system.access TO `data_engineers`;
GRANT SELECT ON SCHEMA system.access TO `data_engineers`;
```

### Common Queries

```sql
-- Table lineage: What tables feed into this table?
SELECT source_table_full_name, source_column_name
FROM system.access.table_lineage
WHERE target_table_full_name = 'catalog.schema.table'
  AND event_date >= current_date() - 7;

-- Audit: Recent permission changes
SELECT event_time, user_identity.email, action_name, request_params
FROM system.access.audit
WHERE action_name LIKE '%GRANT%' OR action_name LIKE '%REVOKE%'
ORDER BY event_time DESC
LIMIT 100;

-- Billing: DBU usage by workspace
SELECT workspace_id, sku_name, SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - 30
GROUP BY workspace_id, sku_name;
```

## SQL Execution via Python SDK

Use `skills/clients/databricks_tools_core/sql` to execute system table queries:

```python
from skills.clients.databricks_tools_core.sql import execute_sql

# Query lineage
execute_sql(
    sql_query="""
        SELECT source_table_full_name, target_table_full_name
        FROM system.access.table_lineage
        WHERE event_date >= current_date() - 7
    """,
    catalog="system"
)
```

## Capital Group Standards (RFD 0008)

- **DBX-UC-001**: All data assets must be registered in Unity Catalog. Do not write to DBFS paths outside of `/Volumes/` for governed data.
- **DBX-UC-002**: Apply least-privilege grants — grant `SELECT` on specific schemas rather than `USE CATALOG` on the entire catalog where possible. Document grant rationale in the security-design artifact.
- **DBX-UC-003**: Use UC Volumes (`/Volumes/<catalog>/<schema>/<volume>/`) for all file I/O in Databricks jobs. Do not use legacy DBFS (`dbfs:/`) for new data product files.

## Best Practices

1. **Filter by date** - System tables can be large; always use date filters
2. **Use appropriate retention** - Check your workspace's retention settings
3. **Grant minimal access** - System tables contain sensitive metadata
4. **Schedule reports** - Create scheduled queries for regular monitoring

## Related Skills

- **[databricks-jobs](../databricks-jobs/SKILL.md)** — for job execution data visible in system tables
- **[databricks-python-sdk](../databricks-python-sdk/SKILL.md)** — for programmatic Unity Catalog access via SDK

## Resources

- [Unity Catalog System Tables](https://docs.databricks.com/administration-guide/system-tables/)
- [Audit Log Reference](https://docs.databricks.com/administration-guide/account-settings/audit-logs.html)
