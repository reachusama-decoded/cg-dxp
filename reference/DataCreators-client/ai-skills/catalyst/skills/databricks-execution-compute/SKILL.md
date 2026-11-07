---
name: databricks-execution-compute
description: |
  Execute code and manage compute on Databricks. Use this skill when the user
  mentions: "run code", "execute", "run on databricks", "serverless", "no
  cluster", "run python", "run scala", "run sql", "run R", "run file", "push
  and run", "notebook run", "batch script", "model training", "run script on
  cluster", "create cluster", "new cluster", "resize cluster", "modify cluster",
  "delete cluster", "terminate cluster", "create warehouse", "new warehouse",
  "resize warehouse", "delete warehouse", "node types", "runtime versions",
  "DBR versions", "spin up compute", "provision cluster".
  Catalyst trigger phrases: "set up Databricks job cluster", "configure execution compute", "pick cluster size".
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
    - DBX-COMPUTE-001
    - DBX-COMPUTE-002
    - DBX-COMPUTE-004
  upstream-source: databricks-solutions/ai-dev-kit/databricks-skills/databricks-execution-compute
  upstream-commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
  upstream-license: Databricks (custom — see third-party/LICENSE-databricks.md)
  catalyst-modifications: |
    Modified by Capital Group on 2026-05-14:
    - dropped MCP tool references (Catalyst policy); replaced with Python function
      calls in skills/clients/databricks_tools_core/
    - added metadata.standards citations (RFD 0008)
    - added Catalyst trigger phrases in description
---

> _Modified from `databricks-solutions/ai-dev-kit/databricks-skills/databricks-execution-compute` by Capital Group on 2026-05-14. See `metadata.catalyst-modifications` for the change set._

# Databricks Execution & Compute

Run code on Databricks. Three execution modes—choose based on workload.

## Execution Mode Decision Matrix

| Aspect | [Databricks Connect](references/1-databricks-connect.md) ⭐ | [Serverless Job](references/2-serverless-job.md) | [Interactive Cluster](references/3-interactive-cluster.md) |
|--------|-------------------|----------------|---------------------|
| **Use for** | Spark code (ETL, data gen) | Heavy processing (ML) | State across tool calls, Scala/R |
| **Startup** | Instant | ~25-50s cold start | ~5min if stopped |
| **State** | Within Python process | None | Via context_id |
| **Languages** | Python (PySpark) | Python, SQL | Python, Scala, SQL, R |
| **Dependencies** | `withDependencies()` | CLI with environments spec | Install on cluster |

### Decision Flow

```
Spark-based code? → Databricks Connect (fastest)
  └─ Python 3.12 missing? → Install it + databricks-connect
  └─ Install fails? → Ask user (don't auto-switch modes)

Heavy/long-running (ML)? → Serverless Job (independent)
Need state across calls? → Interactive Cluster (list and ask which one to use)
Scala/R? → Interactive Cluster (list and ask which one to use)
```


## How to Run Code

**Read the reference file for your chosen mode before proceeding.**

### Databricks Connect (run locally) → [reference](references/1-databricks-connect.md)

```bash
python my_spark_script.py
```

### Serverless Job → [reference](references/2-serverless-job.md)

Invoke the corresponding Python function in `skills/clients/databricks_tools_core/`:

```python
from skills.clients.databricks_tools_core.jobs import execute_code
execute_code(file_path="/path/to/script.py", compute_type="serverless")
```

### Interactive Cluster → [reference](references/3-interactive-cluster.md)

Invoke the corresponding Python function in `skills/clients/databricks_tools_core/`:

```python
from skills.clients.databricks_tools_core.compute import list_compute, manage_cluster
from skills.clients.databricks_tools_core.jobs import execute_code

# Check for running clusters first (or use the one instructed)
list_compute(resource="clusters")
# Ask the user which one to use

# Run code, reuse context_id for follow-up calls
result = execute_code(code="...", compute_type="cluster", cluster_id="...")
execute_code(code="...", context_id=result["context_id"], cluster_id=result["cluster_id"])
```

## Compute Management Functions

| Function | Module | Purpose |
|------|-----|---------|
| `execute_code` | `databricks_tools_core.jobs` | Run code remotely (serverless or interactive) |
| `list_compute` | `databricks_tools_core.compute` | List clusters, check status |
| `manage_cluster` | `databricks_tools_core.compute` | Create, start, terminate, delete. **COSTLY:** `start` takes 3-8 min—ask user |
| `manage_sql_warehouse` | `databricks_tools_core.sql` | Create, modify, delete SQL warehouses |

## Capital Group Standards (RFD 0008)

- **DBX-COMPUTE-001**: Use cluster policies defined by the platform team; do not bypass policy guardrails.
- **DBX-COMPUTE-002**: Right-size compute — choose the smallest node type that meets the workload's memory/CPU requirements. Document sizing rationale in `.catalyst-build.yml`.
- **DBX-COMPUTE-004**: Prefer serverless compute (serverless SQL warehouse, serverless jobs) over always-on clusters for cost efficiency. Reserve persistent clusters for stateful or Scala/R workloads only.

## Related Skills

- **[databricks-jobs](../databricks-jobs/SKILL.md)** — Production job orchestration
- **[databricks-dbsql](../databricks-dbsql/SKILL.md)** — SQL warehouse and AI functions
