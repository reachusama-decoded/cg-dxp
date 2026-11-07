#!/usr/bin/env python3
"""
Clone source tables for user-scoped isolation.

Auto-discovers all data products under data_products/ and shallow-clones their
declared dbt sources into user-scoped schemas in the original source catalogs.

Usage:
    python clone_sources_engine.py                        # clone all products
    python clone_sources_engine.py --cleanup              # drop user clone schemas
    python clone_sources_engine.py --databricks-profile DEFAULT
"""

import argparse
import configparser
import json
import logging
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

for noisy_logger in [
    "databricks",
    "databricks.sql",
    "databricks.sdk",
    "thrift",
    "urllib3",
]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PRODUCTS_DIR = REPO_ROOT / "data_products"


def configure_logging(verbose: bool = False) -> None:
    """Set runtime log level for this tool and selected noisy dependencies."""
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_data_products() -> List[Path]:
    """Return paths to every data product that has a dbt_project.yml."""
    products = sorted(DATA_PRODUCTS_DIR.glob("*/dbt_project.yml"))
    return [p.parent for p in products]


def discover_sources(dbt_project_dir: Path) -> List[Dict[str, Any]]:
    """Run `dbt ls` in a data-product directory and return declared sources."""
    profiles_dir = dbt_project_dir / "dbt_profiles"
    cmd = [
        "dbt",
        "ls",
        "--resource-type",
        "source",
        "--output",
        "json",
        "--quiet",
        "--profiles-dir",
        str(profiles_dir),
        "--vars",
        "{catalog: 'fake_catalog', schema: 'fake_schema', http_path: 'fake_path'}",
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(dbt_project_dir),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(_format_dbt_ls_failure(dbt_project_dir, cmd, exc)) from exc

    sources: List[Dict[str, Any]] = []
    non_json_lines: List[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            sources.append(json.loads(line))
        except json.JSONDecodeError:
            non_json_lines.append(line)

    # dbt 1.11 source JSON may omit database/schema; recover from manifest nodes.
    manifest_sources = _load_manifest_sources(dbt_project_dir)
    enriched = 0
    for src in sources:
        if src.get("database") and src.get("schema"):
            continue
        metadata = manifest_sources.get(str(src.get("unique_id", "")))
        if metadata:
            if not src.get("database") and metadata.get("database"):
                src["database"] = metadata["database"]
            if not src.get("schema") and metadata.get("schema"):
                src["schema"] = metadata["schema"]
            # Prefer the physical identifier if present.
            if metadata.get("identifier"):
                src["name"] = metadata["identifier"]
            enriched += 1

    if enriched:
        logger.info("Recovered source metadata from manifest for %d node(s)", enriched)

    if non_json_lines:
        logger.debug(
            "Ignored %d non-JSON dbt ls output line(s) for %s",
            len(non_json_lines),
            dbt_project_dir.name,
        )

    logger.info(
        "[%s] dbt ls returned %d source node(s)", dbt_project_dir.name, len(sources)
    )

    return sources


def _tail_lines(path: Path, max_lines: int = 40) -> str:
    """Return the last max_lines from path, or empty string if unavailable."""
    if not path.exists():
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        return ""
    return "".join(lines[-max_lines:]).strip()


def _format_dbt_ls_failure(
    dbt_project_dir: Path,
    cmd: List[str],
    exc: subprocess.CalledProcessError,
) -> str:
    """Build a detailed, actionable dbt ls failure message."""
    cmd_str = " ".join(shlex.quote(part) for part in cmd)
    stderr = (exc.stderr or "").strip()
    stdout = (exc.stdout or "").strip()

    # Keep logs readable while preserving enough context to diagnose quickly.
    stdout_tail = "\n".join(stdout.splitlines()[-30:]).strip()
    dbt_log_tail = _tail_lines(dbt_project_dir / "logs" / "dbt.log", max_lines=40)

    summary = _extract_dbt_failure_summary(stderr=stderr, stdout=stdout)
    if not logger.isEnabledFor(logging.DEBUG):
        reason = summary or f"dbt ls exited with code {exc.returncode}"
        return f"{reason}. Rerun with --verbose for command, stdout/stderr, and dbt.log tail"

    details: List[str] = [
        f"dbt ls command failed (exit code {exc.returncode})",
        f"project_dir: {dbt_project_dir}",
        f"command: {cmd_str}",
    ]
    if summary:
        details.append(f"reason: {summary}")

    if stderr:
        details.extend(["stderr:", stderr])
    if stdout_tail:
        details.extend(["stdout (last 30 lines):", stdout_tail])
    if dbt_log_tail:
        details.extend(
            [f"dbt log tail ({dbt_project_dir / 'logs' / 'dbt.log'}):", dbt_log_tail]
        )

    return "\n".join(details)


def _extract_dbt_failure_summary(stderr: str, stdout: str) -> str:
    """Extract a short human-readable failure reason from dbt output."""
    combined = "\n".join(part for part in [stderr, stdout] if part).strip()
    if not combined:
        return "No dbt stderr/stdout captured"

    missing_env = re.search(r"Env var required but not provided: '([^']+)'", combined)
    if missing_env:
        return f"Missing required environment variable: {missing_env.group(1)}"

    # Prefer the first explicit dbt error line, then fall back to the final non-empty line.
    for line in combined.splitlines():
        text = line.strip()
        if text.lower().startswith("parsing error"):
            return text
        if "encountered an error" in text.lower():
            return text

    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    return lines[-1] if lines else "Unknown dbt error"


def _load_manifest_sources(dbt_project_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load source node metadata from dbt target/manifest.json."""
    manifest_path = dbt_project_dir / "target" / "manifest.json"
    if not manifest_path.exists():
        return {}

    try:
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read dbt manifest at %s: %s", manifest_path, exc)
        return {}

    source_nodes = manifest.get("sources", {})
    if not isinstance(source_nodes, dict):
        return {}

    resolved: Dict[str, Dict[str, Any]] = {}
    for unique_id, node in source_nodes.items():
        if not isinstance(node, dict):
            continue
        resolved[str(unique_id)] = {
            "database": node.get("database"),
            "schema": node.get("schema"),
            "identifier": node.get("identifier") or node.get("name"),
        }
    return resolved


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sanitize_branch_name(branch: str) -> str:
    sanitized = re.sub(r"[/\-\.\s]+", "_", branch)
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", sanitized).strip("_")
    if not sanitized:
        raise ValueError(f"Branch name '{branch}' sanitizes to empty string")
    return sanitized


def _quote_identifier_part(identifier: str) -> str:
    """Safely quote a single SQL identifier part for Databricks SQL."""
    value = str(identifier).strip()
    if not value:
        raise ValueError("Identifier component cannot be empty")
    if "\x00" in value:
        raise ValueError("Identifier contains null byte")
    return f"`{value.replace('`', '``')}`"


def quote_fqn(catalog: str, schema: str, name: str) -> str:
    """Return a safely quoted fully qualified name."""
    return ".".join(
        [
            _quote_identifier_part(catalog),
            _quote_identifier_part(schema),
            _quote_identifier_part(name),
        ]
    )


def sql_string_literal(value: str) -> str:
    """Return a safely quoted SQL string literal."""
    text = str(value)
    if "\x00" in text:
        raise ValueError("String literal contains null byte")
    return "'" + text.replace("'", "''") + "'"


def build_clone_source_schema(namespace: str, source_schema: str) -> str:
    """Build target schema for a source as <namespace>__<schema>."""
    return "__".join(
        [
            sanitize_branch_name(namespace),
            sanitize_branch_name(source_schema),
        ]
    )


def extract_clone_namespace_from_principal(principal: str) -> str:
    """Convert current_user() principal into a stable schema namespace."""
    # For users in email form, prefer the local part as the namespace seed.
    base = principal.split("@", 1)[0] if "@" in principal else principal
    return sanitize_branch_name(base)


# ---------------------------------------------------------------------------
# Databricks operations
# ---------------------------------------------------------------------------


def _get_http_path(profile: Optional[str] = None) -> str:
    """
    Resolve the SQL Warehouse http_path.
    Checks (in order):
      1. Named profile section in ~/.databrickscfg (or [DEFAULT] if no profile given)
      2. DATABRICKS_HTTP_PATH env var
    """
    cfg_path = Path.home() / ".databrickscfg"
    if cfg_path.exists():
        cfg = configparser.ConfigParser()
        cfg.read(cfg_path)
        if profile and profile not in cfg:
            raise EnvironmentError(
                f"Databricks profile '{profile}' was requested but not found in {cfg_path}"
            )
        # Use the named profile if given; otherwise fall back to DEFAULT.
        section = profile if profile else "DEFAULT"
        if "http_path" in cfg[section]:
            value = cfg[section]["http_path"].strip()
            if value:
                logger.debug(
                    "http_path resolved from [%s] in ~/.databrickscfg", section
                )
                return value
    from_env = os.getenv("DATABRICKS_HTTP_PATH", "").strip()
    if from_env:
        logger.debug("http_path resolved from DATABRICKS_HTTP_PATH env var")
        return from_env
    raise EnvironmentError(
        "http_path not found. Add it to your ~/.databrickscfg profile or [DEFAULT] section:\n"
        "  http_path = /sql/1.0/warehouses/<warehouse-id>\n"
        "or set the DATABRICKS_HTTP_PATH environment variable."
    )


def _log_connection_auth_resolution(
    profile_arg: Optional[str],
    resolved_profile: Optional[str],
    server_hostname: str,
    http_path: str,
) -> None:
    """Log the resolved Databricks auth context from the actual connection path."""
    if profile_arg:
        profile_context = f"explicit profile '{profile_arg}'"
    else:
        env_profile = os.getenv("DATABRICKS_CONFIG_PROFILE", "").strip()
        if env_profile:
            profile_context = f"DATABRICKS_CONFIG_PROFILE '{env_profile}'"
        elif resolved_profile:
            profile_context = f"SDK resolved profile '{resolved_profile}'"
        else:
            profile_context = "default SDK env/config resolution"

    logger.info(
        "Databricks connect auth context: %s; host=%s; http_path=%s",
        profile_context,
        server_hostname,
        http_path,
    )


def _get_connection_params(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve connection params using the Databricks SDK Config.
    Supports all auth types: PAT, OAuth (databricks-cli), etc.
    """
    config_module = __import__("databricks.sdk.config", fromlist=["Config"])
    Config = config_module.Config

    resolved_profile = profile or os.getenv("DATABRICKS_CONFIG_PROFILE")
    sdk_config = Config(profile=resolved_profile) if resolved_profile else Config()

    # authenticate() returns e.g. {"Authorization": "Bearer <token>"} for any auth type
    headers = sdk_config.authenticate()
    token = headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise EnvironmentError(
            "Databricks SDK could not obtain an access token for this profile/auth config"
        )

    server_hostname = re.sub(r"^https?://", "", sdk_config.host).rstrip("/")
    http_path = _get_http_path(resolved_profile)

    _log_connection_auth_resolution(
        profile_arg=profile,
        resolved_profile=resolved_profile,
        server_hostname=server_hostname,
        http_path=http_path,
    )

    return {
        "server_hostname": server_hostname,
        "http_path": http_path,
        "access_token": token,
    }


def get_databricks_connection(profile: Optional[str] = None) -> Any:
    databricks_sql = __import__("databricks.sql", fromlist=["connect"])
    params = _get_connection_params(profile)
    conn = databricks_sql.connect(**params)
    try:
        principal = get_current_databricks_principal(conn)
        logger.info("Databricks connection verified as current_user()='%s'", principal)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning(
            "Databricks connection established, but could not verify current_user(): %s",
            exc,
        )
    return conn


def get_current_databricks_principal(conn: Any) -> str:
    """Return Databricks principal reported by current_user()."""
    cursor = conn.cursor()
    cursor.execute("SELECT current_user()")
    row = cursor.fetchone()
    principal = str(row[0]).strip() if row and row[0] else ""
    if not principal:
        raise RuntimeError("Could not resolve Databricks principal from current_user()")
    return principal


def resolve_clone_namespace(conn: Any) -> str:
    """
    Resolve clone namespace from Databricks principal.

    The Databricks principal is the same identity used to deploy DABs.
    """
    principal = get_current_databricks_principal(conn)
    namespace = extract_clone_namespace_from_principal(principal)
    logger.info(
        "Clone namespace resolved from Databricks principal '%s' -> '%s'",
        principal,
        namespace,
    )
    return namespace


def resolve_workspace_default_catalog(conn: Any) -> str:
    """Resolve the Databricks session default catalog via current_catalog()."""
    cursor = conn.cursor()
    cursor.execute("SELECT current_catalog()")
    row = cursor.fetchone()
    catalog = str(row[0]).strip() if row and row[0] else ""
    if not catalog:
        raise RuntimeError(
            "Could not resolve workspace default catalog from current_catalog(). "
            "Set a Unity Catalog default in the workspace and retry."
        )
    if catalog.lower() == "hive_metastore":
        raise RuntimeError(
            "Workspace default catalog resolved to 'hive_metastore', which is not a supported clone target. "
            "Set a Unity Catalog default catalog in the workspace and retry."
        )
    logger.info(
        "Workspace default target catalog resolved from current_catalog(): %s", catalog
    )
    return catalog


def table_exists(conn: Any, catalog: str, schema: str, table: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM system.information_schema.tables "
        f"WHERE table_catalog = {sql_string_literal(catalog)} "
        f"AND table_schema = {sql_string_literal(schema)} "
        f"AND table_name = {sql_string_literal(table)})"
    )
    row = cursor.fetchone()
    return bool(row and row[0])


def get_table_type(conn: Any, catalog: str, schema: str, table: str) -> str:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT table_type FROM system.information_schema.tables "
        f"WHERE table_catalog = {sql_string_literal(catalog)} "
        f"AND table_schema = {sql_string_literal(schema)} "
        f"AND table_name = {sql_string_literal(table)}"
    )
    row = cursor.fetchone()
    if not row or not row[0]:
        return "UNKNOWN"
    return str(row[0]).upper()


def is_delta_table(conn: Any, catalog: str, schema: str, table: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE TABLE EXTENDED {quote_fqn(catalog, schema, table)}")
    for row in cursor.fetchall():
        if row and row[0] and "Provider" in str(row[0]):
            return "delta" in str(row[1]).lower()
    return False


def create_schema_if_not_exists(conn: Any, catalog: str, schema: str) -> None:
    cursor = conn.cursor()
    logger.debug("Ensuring target schema exists: %s.%s", catalog, schema)
    cursor.execute(
        "CREATE SCHEMA IF NOT EXISTS "
        f"{_quote_identifier_part(catalog)}.{_quote_identifier_part(schema)}"
    )


def schema_exists(conn: Any, catalog: str, schema: str) -> bool:
    """Return whether a schema exists in a given catalog."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM system.information_schema.schemata "
        f"WHERE catalog_name = {sql_string_literal(catalog)} "
        f"AND schema_name = {sql_string_literal(schema)})"
    )
    row = cursor.fetchone()
    return bool(row and row[0])


def clone_table(
    conn: Any,
    source_catalog: str,
    source_schema: str,
    source_table: str,
    target_catalog: str,
    target_schema: str,
) -> bool:
    if not table_exists(conn, source_catalog, source_schema, source_table):
        logger.warning(
            "Missing source: %s.%s.%s", source_catalog, source_schema, source_table
        )
        return False

    target_fqn = quote_fqn(target_catalog, target_schema, source_table)
    source_fqn = quote_fqn(source_catalog, source_schema, source_table)
    cursor = conn.cursor()
    table_type = get_table_type(conn, source_catalog, source_schema, source_table)

    if "VIEW" in table_type:
        # Materialize upstream views into isolated tables in the target schema.
        sql = f"CREATE OR REPLACE TABLE {target_fqn} AS SELECT * FROM {source_fqn}"
        mode = "VIEW_TO_TABLE_CTAS"
    elif is_delta_table(conn, source_catalog, source_schema, source_table):
        sql = f"CREATE OR REPLACE TABLE {target_fqn} SHALLOW CLONE {source_fqn}"
        mode = "SHALLOW_CLONE"
    else:
        sql = f"CREATE OR REPLACE TABLE {target_fqn} AS SELECT * FROM {source_fqn}"
        mode = "CTAS"

    logger.debug("  %s -> %s (%s)", source_fqn, target_fqn, mode)
    cursor.execute(sql)
    return True


# ---------------------------------------------------------------------------
# High-level operations
# ---------------------------------------------------------------------------


def clone_product_sources(
    conn: Any,
    product_dir: Path,
    clone_namespace: str,
    target_catalog: str,
) -> int:
    """Clone sources for a single data product. Returns success count."""
    product_name = product_dir.name
    logger.info("[%s] Discovering dbt sources", product_name)
    try:
        sources = discover_sources(product_dir)
    except RuntimeError as exc:
        logger.error("[%s] dbt ls failed: %s", product_name, exc)
        return 0

    if not sources:
        logger.info(
            "[%s] dbt ls returned no source nodes; skipping clone step", product_name
        )
        return 0

    logger.info("[%s] Cloning %d source(s)", product_name, len(sources))
    success = 0
    for src in sources:
        src_catalog = src.get("database")
        src_schema = src.get("schema")
        src_table = src.get("name")
        if not all([src_catalog, src_schema, src_table]):
            logger.warning("Skipping malformed source: %s", src)
            continue
        target_schema = build_clone_source_schema(clone_namespace, str(src_schema))
        try:
            create_schema_if_not_exists(conn, target_catalog, target_schema)
            if clone_table(
                conn,
                str(src_catalog),
                str(src_schema),
                str(src_table),
                target_catalog,
                target_schema,
            ):
                success += 1
        except (
            Exception
        ) as exc:  # Continue cloning other sources on per-source failure.
            logger.error(
                "[%s] Failed cloning source %s.%s.%s -> %s.%s: %s",
                product_name,
                src_catalog,
                src_schema,
                src_table,
                target_catalog,
                target_schema,
                exc,
            )
    logger.info("[%s] Cloned %d/%d source(s)", product_name, success, len(sources))
    return success


def export_dbt_env_vars(catalog: str, schema: str) -> None:
    """Write DBT_CATALOG, DBT_SCHEMA and DBT_HTTP_PATH to /etc/profile.d so all shells pick them up."""
    http_path = os.environ.get("DATABRICKS_HTTP_PATH", "")
    env_file = Path("/etc/profile.d/dbt-env.sh")
    try:
        env_file.write_text(
            f"# Auto-generated by clone_sources_engine.py\n"
            f"export DBT_CATALOG={catalog}\n"
            f"export DBT_SCHEMA={schema}\n"
            f"export DBT_HTTP_PATH={http_path}\n"
        )
        env_file.chmod(0o644)
        # Also export immediately for the current process
        os.environ["DBT_CATALOG"] = catalog
        os.environ["DBT_SCHEMA"] = schema
        os.environ["DBT_HTTP_PATH"] = http_path
        logger.info(
            "DBT env vars set: DBT_CATALOG=%s DBT_SCHEMA=%s DBT_HTTP_PATH=%s",
            catalog,
            schema,
            http_path,
        )
    except PermissionError:
        logger.warning(
            "Could not write to /etc/profile.d/dbt-env.sh — run as root or set DBT_CATALOG/DBT_SCHEMA/DBT_HTTP_PATH manually"
        )


def clone_all(databricks_profile: Optional[str] = None) -> int:
    """Iterate over every data product and clone its sources."""
    products = discover_data_products()
    logger.info(
        "Found %d data product(s): %s",
        len(products),
        ", ".join(p.name for p in products),
    )

    total = 0
    with get_databricks_connection(databricks_profile) as conn:
        clone_namespace = resolve_clone_namespace(conn)
        target_catalog = resolve_workspace_default_catalog(conn)
        logger.info(
            "Target clone schema pattern: %s.%s__<source_schema>",
            target_catalog,
            clone_namespace,
        )
        for product_dir in products:
            total += clone_product_sources(
                conn, product_dir, clone_namespace, target_catalog
            )

    export_dbt_env_vars(target_catalog, clone_namespace)
    logger.info(
        "Done — %d source(s) cloned with namespace prefix %s", total, clone_namespace
    )
    return total


def cleanup(databricks_profile: Optional[str] = None) -> None:
    products = discover_data_products()
    source_schemas: Set[str] = set()
    for product_dir in products:
        try:
            sources = discover_sources(product_dir)
        except RuntimeError as exc:
            logger.error(
                "[%s] dbt ls failed during cleanup discovery: %s", product_dir.name, exc
            )
            continue

        for src in sources:
            src_schema = src.get("schema")
            if src_schema:
                source_schemas.add(str(src_schema))

    if not source_schemas:
        logger.info("No source schemas discovered; nothing to clean up")
        return

    dropped = 0
    with get_databricks_connection(databricks_profile) as conn:
        clone_prefix = resolve_clone_namespace(conn)
        target_catalog = resolve_workspace_default_catalog(conn)
        expected_schemas = {
            build_clone_source_schema(clone_prefix, source_schema)
            for source_schema in source_schemas
        }
        logger.info(
            "Cleanup candidates in catalog %s (%d schema(s)): %s",
            target_catalog,
            len(expected_schemas),
            ", ".join(sorted(expected_schemas)),
        )

        for schema_name in sorted(expected_schemas):
            if not schema_exists(conn, target_catalog, schema_name):
                continue

            cursor = conn.cursor()
            logger.info("Dropping schema %s.%s", target_catalog, schema_name)
            cursor.execute(
                "DROP SCHEMA IF EXISTS "
                f"{_quote_identifier_part(target_catalog)}.{_quote_identifier_part(schema_name)} CASCADE"
            )
            dropped += 1

    if dropped:
        logger.info(
            "Dropped %d schema(s) for clone namespace prefix %s", dropped, clone_prefix
        )
    else:
        logger.info(
            "No schemas found for clone namespace prefix %s in target catalog",
            clone_prefix,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clone dbt sources for all data products into user-scoped source schemas in the workspace default catalog",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Drop user-prefixed clone schemas instead of cloning",
    )
    parser.add_argument(
        "--databricks-profile",
        help="Databricks profile name from ~/.databrickscfg to use for authentication",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose diagnostics (debug logs and full dbt failure context)",
    )
    args = parser.parse_args()
    configure_logging(args.verbose)

    try:
        if args.cleanup:
            cleanup(args.databricks_profile)
        else:
            clone_all(args.databricks_profile)
        return 0
    except subprocess.CalledProcessError as exc:
        logger.error("Command failed: %s", exc)
        if exc.stderr:
            logger.error(exc.stderr)
        return 1
    except ImportError as exc:
        if getattr(exc, "name", "") in {
            "databricks",
            "databricks.sql",
            "databricks.sdk.config",
        }:
            logger.error(
                "Clone failed: missing Databricks dependency '%s'. Install the Databricks client libraries in this environment.",
                exc.name,
            )
        else:
            logger.error("Clone failed: %s", exc)
        return 1
    except (EnvironmentError, OSError, RuntimeError, TypeError, ValueError) as exc:
        logger.error("Clone failed: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error during clone operation: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
