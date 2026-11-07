"""Catalyst core functions — deterministic, reusable building blocks.

Each function is a pure (or near-pure) operation that does one thing well
and requires no LLM judgment.  Platform clients are injected by callers.

Imports are lazy (PEP 562) so a consumer needing only one submodule (e.g.
``skills.core.sql_identifiers``) does not pay the import cost — or the
transitive dependency surface — of unrelated submodules like
``marketplace`` (which requires ``platformdirs``).
"""

from typing import Any

_LAZY_EXPORTS: dict[str, str] = {
    # symbol name -> submodule name
    "AuthNotConfigured": "databricks_raw_client",
    "RETRY_AFTER_MAX_SECONDS": "databricks_raw_client",
    "RawRequestsClient": "databricks_raw_client",
    "should_retry_databricks": "databricks_raw_client",
    "discover_tables": "discover",
    "fetch_confluence_page": "confluence",
    "profile_table": "profile",
    "query_mentions_object": "sql_identifiers",
    "search_marketplace": "marketplace",
    "strip_sql_noise": "sql_identifiers",
    "trace_lineage": "lineage",
}

__all__ = sorted(_LAZY_EXPORTS.keys())


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module 'skills.core' has no attribute {name!r}")
    import importlib

    submodule = importlib.import_module(f".{_LAZY_EXPORTS[name]}", __name__)
    value = getattr(submodule, name)
    globals()[name] = value  # cache so subsequent lookups skip the lazy path
    return value
