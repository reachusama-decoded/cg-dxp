"""
databricks_tools_core — vendored from databricks-solutions/ai-dev-kit.

Upstream: https://github.com/databricks-solutions/ai-dev-kit/tree/8cb4456543d6413e8a12923d4d4b5394fea89b25/databricks-tools-core/databricks_tools_core
Upstream commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
License: Databricks custom — see third-party/LICENSE-databricks.md.

Modified by Capital Group on 2026-05-14:
- Removed subdirectories out of scope for DPLC Phase 4 build skills:
  agent_bricks, aibi_dashboards, apps, lakebase, lakebase_autoscale,
  pdf, serving, spark_declarative_pipelines, vector_search.
- No code changes to retained modules.

---

Databricks Tools Core Library

High-level, AI-assistant-friendly functions for building Databricks projects.
Organized by product line for scalability.
"""

__version__ = "0.1.0"

# Auth utilities
from .auth import get_workspace_client, set_databricks_auth, clear_databricks_auth, get_current_username

__all__ = [
    "get_workspace_client",
    "set_databricks_auth",
    "clear_databricks_auth",
    "get_current_username",
]
