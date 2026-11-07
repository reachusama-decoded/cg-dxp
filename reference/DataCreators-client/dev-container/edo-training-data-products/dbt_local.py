#!/usr/bin/env python
"""
dbt entry-point for local warehouse runs and Databricks shared-cluster bundle jobs.

Responsibilities:
- Injects caspian.dbt.dbt_modules so `modules.get('caspian')` resolves in Jinja (required for bitemporal_load_v2).
- Hydrates DBT_ACCESS_TOKEN / DBT_HOST from the Spark/dbutils context on shared clusters where they are not auto-injected.
- Sets CA cert env vars (REQUESTS_CA_BUNDLE etc.) for shared clusters that skip the per-task init script.
- Removes the script directory from sys.path to prevent dbt 1.11 auto-discovering this file as a plugin module.
- Purges any pip-installed `caspian` from sys.modules so the local shared/ version (with .dbt submodule) takes precedence.
- Accepts `deps_then_run` as first arg to run `dbt deps` then `dbt run` in one task, relying on the CA
  bundle wiring for HTTPS traffic in both steps.

Usage:
  Local:   python ../../dbt_local.py run --project-dir . --profiles-dir ./dbt_profiles ...
  Bundle:  python dbt_local.py deps_then_run --project-dir ... --profiles-dir ... --vars ...
"""
import sys
import os


def _get_project_dir(argv: list[str]) -> str | None:
    for i, arg in enumerate(argv):
        if arg == "--project-dir" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--project-dir="):
            return arg.split("=", 1)[1]
    return None


def _get_option_value(argv: list[str], flag: str) -> str | None:
    for i, arg in enumerate(argv):
        if arg == flag and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith(f"{flag}="):
            return arg.split("=", 1)[1]
    return None


def _hydrate_databricks_auth_env() -> None:
    """Populate dbt auth env vars from Databricks runtime context when available."""
    if os.environ.get("DBT_ACCESS_TOKEN") and os.environ.get("DBT_HOST"):
        return

    token = os.environ.get("DBT_ACCESS_TOKEN") or os.environ.get("DATABRICKS_TOKEN")
    host = os.environ.get("DBT_HOST") or os.environ.get("DATABRICKS_HOST")

    if not token or not host:
        try:
            from pyspark.sql import SparkSession
            from pyspark.dbutils import DBUtils

            spark = SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()
            dbutils = DBUtils(spark)
            ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()

            if not host:
                host = ctx.apiUrl().get()
            if not token:
                token = ctx.apiToken().get()
        except Exception:
            # Local runs may not have a Spark context / dbutils available.
            pass

    if host:
        os.environ.setdefault("DATABRICKS_HOST", host)
        os.environ.setdefault("DBT_HOST", host)
    if token:
        os.environ.setdefault("DATABRICKS_TOKEN", token)
        os.environ.setdefault("DBT_ACCESS_TOKEN", token)

# Make the shared/ caspian package importable
if "__file__" in globals():
    _repo_root = os.path.dirname(os.path.abspath(__file__))
    _script_dir = os.path.dirname(os.path.abspath(__file__))
else:
    # Databricks spark_python_task may exec script content without defining __file__.
    _repo_root = os.environ.get("PROJECT_HOME", os.getcwd())
    _script_dir = _repo_root

_shared_path = os.path.join(_repo_root, "shared")
sys.path.insert(0, _shared_path)

# Ensure PROJECT_HOME is set so that packages.yml env_var('PROJECT_HOME') resolves correctly.
# The small_cluster spark_env_vars set this; on a shared cluster it may be absent.
os.environ.setdefault("PROJECT_HOME", _repo_root)

# Trust CG CA certificates for outbound HTTPS (e.g. dbt deps downloading packages).\n# On a new_cluster the init_script installs certs; on a shared cluster we set the env vars directly.
for _cert_var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
    if not os.environ.get(_cert_var):
        for _cert_path in (
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/pki/tls/certs/ca-bundle.crt",
            "/etc/ssl/ca-bundle.pem",
        ):
            if os.path.exists(_cert_path):
                os.environ[_cert_var] = _cert_path
                break

# Also inject the CG custom CA cert if bundled alongside this script.
_custom_cert = os.path.join(_repo_root, "data_products", "asset_reference_data", "init_scripts", "certs", "cacert.pem")
if not os.path.exists(_custom_cert):
    _custom_cert = os.path.join(_repo_root, "init_scripts", "certs", "cacert.pem")
if os.path.exists(_custom_cert):
    os.environ["REQUESTS_CA_BUNDLE"] = _custom_cert
    os.environ["SSL_CERT_FILE"] = _custom_cert

# dbt 1.11 scans importable modules prefixed with `dbt_` for plugins.
# Ensure the wrapper's own filename (`dbt_local.py`) is not discovered as a plugin module.
sys.path = [
    p for p in sys.path
    if p not in ("", _repo_root, _script_dir)
]

# The shared cluster may have a pip-installed `caspian` package (without the .dbt submodule)
# cached in sys.modules before this script runs. Purge it so the shared/ version takes precedence.
for _key in list(sys.modules.keys()):
    if _key == "caspian" or _key.startswith("caspian."):
        del sys.modules[_key]

# Import dbt_modules – its module-level code patches dbt.context.base.get_context_modules
# so that `modules.get('caspian')` returns the local extension inside Jinja templates.
import caspian.dbt.dbt_modules  # noqa: F401  (side-effect import)

from dbt.cli.main import cli


def _run_cli(args: list[str]) -> int:
    try:
        cli(args=args, standalone_mode=False)
        return 0
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        return code
    except Exception as exc:
        # Databricks IPython can fail to render some dbt click exceptions (e.g. ResultExit).
        # Emit a safe representation here so the real dbt failure is still visible in task logs.
        print(
            f"dbt wrapper caught exception type={type(exc).__name__}: {repr(exc)}",
            file=sys.stderr,
        )
        result = getattr(exc, "result", None)
        if result is not None:
            print(f"dbt wrapper result payload: {repr(result)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    _hydrate_databricks_auth_env()

    project_dir = _get_project_dir(sys.argv[1:])
    if project_dir:
        os.makedirs(os.path.join(project_dir, "logs"), exist_ok=True)

    os.environ.setdefault("DBT_LOG_PATH", f"/tmp/dbt_logs_{os.getuid()}")
    os.makedirs(os.environ["DBT_LOG_PATH"], exist_ok=True)

    argv = sys.argv[1:]
    if argv and argv[0] == "deps_then_run":
        run_args = argv[1:]
        project_dir = _get_option_value(run_args, "--project-dir")
        profiles_dir = _get_option_value(run_args, "--profiles-dir")

        if not project_dir or not profiles_dir:
            raise SystemExit("deps_then_run requires --project-dir and --profiles-dir")

        deps_args = [
            "deps",
            "--project-dir", project_dir,
            "--profiles-dir", profiles_dir,
        ]
        deps_code = _run_cli(deps_args)
        if deps_code != 0:
            raise SystemExit(deps_code)

        run_code = _run_cli(run_args)
        if run_code != 0:
            raise SystemExit(run_code)
    else:
        code = _run_cli(argv)
        if code != 0:
            raise SystemExit(code)
