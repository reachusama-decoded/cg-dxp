---
name: write-dbt-wrapper
description: |
  Writes the repo-root `dbt_wrapper.py` — a dispatcher script that drives dbt from a Databricks
  Python task (deps / seed / run / test), hydrates ambient job-context credentials, and handles
  the cgrepo CA certificate for SSL on dbt deps. The single wrapper is shared across all data
  products in the repo and is synced into each product bundle via `sync.paths: ../../dbt_wrapper.py`.
  Use when scaffolding a new data product that runs dbt via a Databricks Asset Bundle job.
  Trigger phrases: "write dbt wrapper", "create dbt_wrapper.py", "scaffold the dbt Python wrapper", "set up dbt for Databricks jobs".
allowed-tools: Read Bash Write Edit
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies: [databricks-python-sdk]
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012 cross-ref)
    - DBX-SEC-002              # no hard-coded tokens — wrapper uses ambient job-context identity
    - SQL-DBSQL-001            # OAuth-aware dbt invocation
    # Proposed (PR 94 prose → IDs; awaiting RFD 0008)
    - DBX-SEC-003              # cgrepo Nexus mirror for dbt deps
    - DBX-SEC-005              # cgrepo CA cert handling for dbt deps SSL
---

# Write dbt Wrapper

Scaffold the repo-root `dbt_wrapper.py` — the single Python entry-point that Databricks job
tasks call to drive dbt across **all** data products in the repo. Each product bundle pulls
the wrapper into its sync set via `sync.paths: ../../dbt_wrapper.py` and invokes it through
`spark_python_task`. The wrapper handles four dispatch modes, platform auth hydration via
ambient job-context identity, and the corporate CA certificate requirement for `dbt deps`.

This matches the production exemplar at `cg-open-itg/edo-ig-data-products/dbt_wrapper.py`.

> **Depends on:** `skills/databricks-python-sdk/SKILL.md` for credential-handling patterns
> (DBX-SEC-002: no hard-coded tokens).

---

## Why a wrapper?

Databricks job tasks run Python scripts, not shell commands. The wrapper:

1. **Dispatches** to the right dbt sub-command based on the first task argument (`deps` / `seed` /
   `run` / `test`). This lets the DAB define separate tasks with separate retry/timeout policies
   per dbt phase.
2. **Hydrates auth** from the **ambient Databricks job-context identity** (the same OAuth token
   the runtime hands every task — `dbt_task`, `spark_python_task`, `notebook_task` — for free).
   No pre-provisioned secrets scope required. This is the trust model `dbt_task` uses internally,
   surfaced through the public notebook-context API. Credentials are never hard-coded
   (DBX-SEC-002).
3. **Handles the cgrepo CA bundle** for `dbt deps` only. `dbt deps` fetches packages via HTTPS
   from the internal Nexus proxy (`cgrepo-aws.capgroup.com`). The corporate network requires the
   internal CA certificate to establish the TLS connection. Without `REQUESTS_CA_BUNDLE` set,
   `dbt deps` fails with an SSL verification error against the proxy.
4. **Does not set `REQUESTS_CA_BUNDLE` for `dbt run` / `dbt test` / `dbt seed`** — those
   sub-commands do not make outbound HTTPS calls that need the CA bundle, so setting it globally
   would mask legitimate SSL errors.
5. **Persists logs to a UC Volume** via a `FileHandler` + `sys.stdout`/`sys.stderr` tee. On
   serverless there is no native log-shipping config — `cluster_log_conf` is rejected, and
   `runs/get-output` caps captured output around 10 MB per task. The wrapper writes a
   per-run, per-task file at `/Volumes/<catalog>/<schema>/dbt_logs/<run_id>/<task_key>.log`
   so dbt's full output survives the cap and stays grep-able across runs. Per-run/per-task
   partitioning is required, not optional — Databricks' serverless docs explicitly warn that
   "task logs are not isolated per task run; logs will contain the output from multiple
   tasks" if you reuse a path.

---

## Step 1 — Confirm location

The wrapper lives at the **repo root**: `/dbt_wrapper.py`. One copy, shared across every data
product in the repo. Each product bundle pulls it in via `sync.paths`:

```yaml
# data_products/<product>/databricks.yml (excerpt)
sync:
  paths:
    - ../../dbt_wrapper.py
```

If `/dbt_wrapper.py` already exists at the repo root (lift-and-shift scenario), diff it against
the template below and apply the missing pieces with the `Edit` tool. Otherwise write a new file
at the repo root.

---

## Step 2 — Auth mode (default: ambient)

The default auth mode is **ambient** — the wrapper reads the Databricks-minted token directly
from `dbutils.notebook.entry_point.getDbutils().notebook().getContext()`. This works in any
workspace the job can be deployed to, with zero pre-provisioning. The token is bound to whatever
identity the job runs as (developer in prototype mode, service principal in production).

For **non-job contexts** (local dev, ad-hoc invocation outside a Databricks
job), the wrapper short-circuits the ambient lookup when `DATABRICKS_TOKEN`
is already set in the environment — set `DATABRICKS_HOST` + `DATABRICKS_TOKEN`
(or rely on `~/.databrickscfg`) and the wrapper uses those instead. That's
the only documented alternative to ambient; if a future compliance
requirement forces a secrets-scope pattern, design that branch
deliberately at the time rather than reserving a flag name for it now.

---

## Step 3 — Write dbt_wrapper.py

Write the following file verbatim to the repo root:

```python
#!/usr/bin/env python3
"""
dbt_wrapper.py — Databricks job entry-point for dbt dispatch.

Location: repo root (single shared wrapper across all data products in the
repo). Each product bundle pulls this file into its sync set via
`sync.paths: ../../dbt_wrapper.py`.

Usage (as a Databricks spark_python_task):
    python dbt_wrapper.py <command> [extra dbt flags...]

Commands:
    deps   — install dbt packages (sets REQUESTS_CA_BUNDLE for cgrepo TLS)
    seed   — load seed CSV files
    run    — execute dbt models
    test   — run dbt tests

Credential hydration (ambient, default):
    Every Databricks job task — dbt_task, spark_python_task, notebook_task —
    runs inside the same execution context with the same ambient OAuth
    credentials attached to the job's run_as identity. The runtime exposes
    that token through the notebook-context API; the wrapper reads it
    directly and exports it as DATABRICKS_TOKEN / DBT_ENV_SECRET_DATABRICKS_TOKEN
    for dbt to consume.

    This is the same trust model the platform-managed dbt_task uses internally —
    just surfaced through the public API. Zero pre-provisioning; works in any
    workspace the job can be deployed to, against whatever identity the job
    runs as (developer in prototype mode, service principal in production).

    For non-job contexts (local dev), set DATABRICKS_HOST and DATABRICKS_TOKEN
    explicitly via shell env vars or ~/.databrickscfg — the wrapper short-circuits
    out of the ambient lookup when DATABRICKS_TOKEN is already set.

    DBX-SEC-002: no hard-coded tokens. Ambient tokens are minted by Databricks
    for the job's run_as identity at task start — never stored on disk.

cgrepo CA bundle (deps only):
    Capital Group's corporate network proxies outbound HTTPS through
    cgrepo-aws.capgroup.com, which presents an internal CA certificate.
    dbt deps fetches package archives over HTTPS and must trust this CA.
    REQUESTS_CA_BUNDLE is set only for the deps sub-process; other commands
    do not make outbound HTTPS calls through the proxy and must NOT have the
    var set (it would suppress legitimate SSL errors).

    The CA bundle path is read from the environment variable CGREPO_CA_BUNDLE_PATH.
    On Databricks, the bundle is typically pre-installed at
    /etc/ssl/certs/ca-certificates.crt or injected via an init script.
    Override by setting CGREPO_CA_BUNDLE_PATH in the job environment.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Path to the Capital Group internal CA bundle used by cgrepo.
#: On Databricks, the platform typically provides this in /etc/ssl/certs/.
#: Override if your init script places it elsewhere.
CGREPO_CA_BUNDLE_PATH: str = os.environ.get(
    "CGREPO_CA_BUNDLE_PATH",
    "/etc/ssl/certs/ca-certificates.crt",
)

# ---------------------------------------------------------------------------
# Repo / project root resolution
# ---------------------------------------------------------------------------
# spark_python_task on Databricks may exec the script content without defining
# __file__ in the resulting namespace. Resolve defensively.

if "__file__" in globals():
    _repo_root = os.path.dirname(os.path.abspath(__file__))
    _script_dir = _repo_root
else:
    # Databricks spark_python_task may exec script content without defining __file__.
    _repo_root = os.environ.get("PROJECT_HOME", os.getcwd())
    _script_dir = _repo_root

#: Absolute path to the dbt project root (directory containing dbt_project.yml).
#: Defaults to the wrapper's directory (repo root), overridable via DBT_PROJECT_DIR
#: env var for the multi-product case where each product carries its own dbt project.
DBT_PROJECT_DIR: Path = Path(os.environ.get("DBT_PROJECT_DIR", _repo_root)).resolve()


# ---------------------------------------------------------------------------
# Auth hydration — ambient job-context identity (default)
# ---------------------------------------------------------------------------


def _is_on_databricks() -> bool:
    """Return True when running inside a Databricks execution environment."""
    return (
        "DATABRICKS_RUNTIME_VERSION" in os.environ
        or Path("/databricks").exists()
    )


def hydrate_auth() -> None:
    """
    Populate DATABRICKS_HOST and DATABRICKS_TOKEN from the ambient Databricks
    job-context identity when running on Databricks and credentials are not
    already injected.

    DBX-SEC-002: credentials are never hard-coded; they come from the
    Databricks-minted runtime token bound to the job's run_as identity.
    """
    if os.environ.get("DBT_ENV_SECRET_DATABRICKS_TOKEN") or os.environ.get("DATABRICKS_TOKEN"):
        # Already injected by the job environment or local shell — nothing to do.
        return

    if not _is_on_databricks():
        # Running locally; assume ~/.databrickscfg or env vars are configured.
        return

    try:
        # dbutils is injected into the Python task namespace by the Databricks
        # runtime. Import here to avoid ImportError in local environments.
        from pyspark.dbutils import DBUtils  # type: ignore[import]
        from pyspark.sql import SparkSession  # type: ignore[import]

        spark = SparkSession.builder.getOrCreate()
        dbutils = DBUtils(spark)

        # Pull the ambient OAuth token + workspace URL the runtime hands the
        # task for free — same identity dbt_task uses internally.
        ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
        host = ctx.apiUrl().get()
        token = ctx.apiToken().get()

        os.environ.setdefault("DATABRICKS_HOST", host)
        # dbt-databricks reads DATABRICKS_TOKEN; set both for compatibility.
        os.environ["DATABRICKS_TOKEN"] = token
        os.environ["DBT_ENV_SECRET_DATABRICKS_TOKEN"] = token

        print("[dbt_wrapper] auth hydrated from ambient job-context identity")
    except Exception as exc:  # noqa: BLE001
        # Surface as a clear error rather than a confusing dbt auth failure.
        print(
            f"[dbt_wrapper] ERROR: could not hydrate auth from ambient "
            f"job-context identity: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Log capture — tee stdout/stderr + Python logging to a UC Volume per task
# ---------------------------------------------------------------------------
#
# Why: on serverless, the task's local filesystem is ephemeral and the
# Jobs API runs/get-output endpoint caps captured stdout/stderr around
# 10 MB per task (community reports of "output too large" failures
# above that). For dbt jobs of any non-trivial size we need a
# persistent destination that survives past the API cap.
#
# Pattern: per Databricks' own guidance for serverless logging (no
# native log-shipping config exists; cluster_log_conf is rejected on
# serverless), write to a UC Volume via the standard Python logging
# FileHandler. The wrapper additionally tees raw sys.stdout/sys.stderr
# so dbt's own output — which uses print(), not the logging module —
# also lands in the file.
#
# Path convention:
#   /Volumes/<catalog>/<schema>/dbt_logs/<run_id>/<task_key>.log
#
# This MUST be per-run AND per-task. Per Databricks serverless docs,
# "task logs are not isolated per task run; logs will contain the
# output from multiple tasks" — so two concurrent tasks writing to the
# same path will interleave. The run_id/task_key partitioning prevents
# that.
#
# Env vars consumed:
#   DATABRICKS_DEFAULT_CATALOG / DATABRICKS_DEFAULT_SCHEMA
#       — root of the dbt_logs volume
#   DATABRICKS_RUN_ID / DATABRICKS_TASK_KEY
#       — populated by the Databricks runtime for every task
#
# When any of these is missing (e.g. local dev) the wrapper falls
# through to console-only output and never raises. Logging-setup
# problems should never fail the job.

import logging


class _Tee:
    """File-like object that writes to several underlying streams.

    Mirrors sys.stdout / sys.stderr into a UC Volume file while still
    emitting to the original console (so runs/get-output remains the
    fast path for live debugging).
    """

    def __init__(self, *streams):
        self._streams = streams

    def write(self, s):
        for stream in self._streams:
            try:
                stream.write(s)
            except Exception:
                pass  # never let a logging failure crash dbt

    def flush(self):
        for stream in self._streams:
            try:
                stream.flush()
            except Exception:
                pass


def setup_log_capture() -> str | None:
    """Wire FileHandler + sys.stdout/stderr tee to a UC Volume file.

    Returns the log path when capture is active, ``None`` when the
    necessary context is missing (local dev) — in which case the
    wrapper falls through to console-only output.

    Failure of the volume write (volume doesn't exist, no grants,
    network blip) is downgraded to a warning on stderr and capture is
    skipped; never raises.
    """
    catalog = os.environ.get("DATABRICKS_DEFAULT_CATALOG")
    schema = os.environ.get("DATABRICKS_DEFAULT_SCHEMA")
    run_id = os.environ.get("DATABRICKS_RUN_ID")
    task_key = os.environ.get("DATABRICKS_TASK_KEY")

    if not all([catalog, schema, run_id, task_key]):
        # Likely local dev. Console-only.
        return None

    log_dir = f"/Volumes/{catalog}/{schema}/dbt_logs/{run_id}"
    log_path = f"{log_dir}/{task_key}.log"

    try:
        os.makedirs(log_dir, exist_ok=True)
        # Line-buffered so partial output is visible during a hang.
        log_file = open(log_path, "a", buffering=1)
    except OSError as exc:
        print(
            f"[dbt_wrapper] WARNING: could not open log path {log_path!r}: {exc}. "
            "Falling back to console-only. Ensure the catalog/schema has a "
            "`dbt_logs` UC Volume the run-as identity can write to.",
            file=sys.stderr,
        )
        return None

    # Tee sys.stdout/sys.stderr so dbt's own print() output is captured.
    sys.stdout = _Tee(sys.__stdout__, log_file)
    sys.stderr = _Tee(sys.__stderr__, log_file)

    # FileHandler for any logging.* calls in this wrapper or its imports.
    handler = logging.FileHandler(log_path)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    print(f"[dbt_wrapper] log capture: {log_path}")
    return log_path


# ---------------------------------------------------------------------------
# dbt target-path (where dbt writes run_results.json, manifest.json, logs/)
# ---------------------------------------------------------------------------
#
# By default dbt writes artifacts to <project_dir>/target/. On a serverless
# spark_python_task the project dir is ephemeral and the artifacts evaporate
# before any downstream capture step can read them. The wrapper sets a stable,
# project-relative target-path so /setup-monitoring-and-logging (AICAT-136) and
# any analyst poking at last-run results can find them.
#
# Override via DBT_TARGET_PATH env var (e.g. a UC Volume path in prod, a
# per-user /tmp path in local dev).
DBT_TARGET_PATH: str = os.environ.get(
    "DBT_TARGET_PATH",
    str(DBT_PROJECT_DIR / "target"),
)


# ---------------------------------------------------------------------------
# sys.path protection (dbt 1.11+ plugin auto-discovery)
# ---------------------------------------------------------------------------


def _scrub_sys_path_for_dbt() -> None:
    """
    Remove the wrapper's own directory (and the dbt project root) from
    sys.path before invoking dbt as a subprocess.

    dbt 1.11+ scans for Python plugin modules on import. If this wrapper file
    sits on sys.path, dbt may try to auto-load it as a plugin module, evaluate
    its top-level code in an unexpected context, and crash with a misleading
    error. Scrubbing these entries pre-emptively neutralizes that.
    """
    to_remove = {_script_dir, _repo_root, str(DBT_PROJECT_DIR)}
    sys.path[:] = [p for p in sys.path if p and p not in to_remove]
    # Propagate to the subprocess via PYTHONPATH so a child Python interpreter
    # invoked by dbt doesn't re-introduce these entries.
    pythonpath = os.environ.get("PYTHONPATH", "")
    parts = [p for p in pythonpath.split(os.pathsep) if p and p not in to_remove]
    os.environ["PYTHONPATH"] = os.pathsep.join(parts)


# ---------------------------------------------------------------------------
# dbt sub-command dispatch
# ---------------------------------------------------------------------------


def run_dbt(
    subcommand: str,
    extra_args: list[str],
    extra_env: dict[str, str] | None = None,
) -> None:
    """
    Invoke dbt as a subprocess.

    dbt 1.10+ moved --project-dir / --profiles-dir / --target-path to
    subcommand-level flags. The argv is built as:

        dbt <subcommand> --project-dir <DBT_PROJECT_DIR> --target-path <DBT_TARGET_PATH> [extra...]

    Args:
        subcommand: dbt subcommand (e.g. "run", "deps", "seed", "test").
        extra_args: additional flags/selectors passed through (e.g.
                    ["--select", "marts+"] or ["--full-refresh"]).
        extra_env: Additional environment variables to merge into the subprocess
                   environment. Merged ON TOP of the current process environment
                   so callers can set REQUESTS_CA_BUNDLE without affecting other
                   sub-commands.

    Raises:
        SystemExit: with dbt's return code if non-zero.
    """
    _scrub_sys_path_for_dbt()

    env = {**os.environ}
    if extra_env:
        env.update(extra_env)

    cmd = [
        "dbt",
        subcommand,
        "--project-dir", str(DBT_PROJECT_DIR),
        "--target-path", DBT_TARGET_PATH,
        *extra_args,
    ]
    print(f"[dbt_wrapper] running: {' '.join(cmd)}")

    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(
            f"[dbt_wrapper] dbt exited with code {result.returncode}",
            file=sys.stderr,
        )
        sys.exit(result.returncode)


def dispatch(command: str, extra_args: list[str]) -> None:
    """
    Route <command> to the appropriate dbt sub-command.

    Args:
        command: one of "deps", "seed", "run", "test".
        extra_args: any additional flags/selectors passed through (e.g.
                    ["--select", "marts+"] or ["--full-refresh"]).
    """
    if command == "deps":
        # dbt deps fetches packages from the cgrepo Nexus proxy over HTTPS.
        # Set REQUESTS_CA_BUNDLE so the internal CA is trusted.
        # This is the ONLY sub-command that needs the CA bundle.
        ca_bundle = CGREPO_CA_BUNDLE_PATH
        if not Path(ca_bundle).exists():
            print(
                f"[dbt_wrapper] WARNING: CGREPO_CA_BUNDLE_PATH='{ca_bundle}' not found. "
                "dbt deps may fail with SSL errors. "
                "Set CGREPO_CA_BUNDLE_PATH to the correct path or ensure the "
                "CA bundle is installed via an init script.",
                file=sys.stderr,
            )
        run_dbt("deps", extra_args, extra_env={"REQUESTS_CA_BUNDLE": ca_bundle})

    elif command == "seed":
        run_dbt("seed", extra_args)

    elif command == "run":
        run_dbt("run", extra_args)

    elif command == "test":
        run_dbt("test", extra_args)

    else:
        print(
            f"[dbt_wrapper] ERROR: unknown command '{command}'. "
            "Expected one of: deps, seed, run, test.",
            file=sys.stderr,
        )
        sys.exit(2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: dbt_wrapper.py <command> [extra dbt flags...]\n"
            "Commands: deps | seed | run | test",
            file=sys.stderr,
        )
        sys.exit(2)

    command = sys.argv[1]
    extra_args = sys.argv[2:]

    # Wire log capture FIRST so all subsequent output — including
    # hydrate_auth() diagnostics and any subprocess output we surface —
    # lands in the per-run/per-task UC Volume file.
    setup_log_capture()

    # Hydrate credentials before any dbt call.
    hydrate_auth()

    dispatch(command, extra_args)


if __name__ == "__main__":
    main()
```

Write this file to the **repo root** as `dbt_wrapper.py`. If you're writing it for the first
time, use the `Write` tool. If a file already exists (lift-and-shift scenario), diff it against
this template and apply the missing pieces with the `Edit` tool.

---

## Step 4 — Wire the wrapper into the DAB job YAML

Each dbt phase becomes a separate task in the job YAML. Each product bundle pulls the repo-root
wrapper into its sync set, then references the synced relative path. Example for a `pricing`
product:

```yaml
# data_products/pricing/databricks.yml (excerpt)
sync:
  paths:
    - ../../dbt_wrapper.py

# data_products/pricing/datasets/pricing/bundle/pricing.job.yml
# (pipeline DAB — managed by /setup-databricks-asset-bundle)
resources:
  jobs:
    pricing_dbt:
      name: pricing-dbt-${bundle.target}
      tasks:
        - task_key: deps
          spark_python_task:
            python_file: ../../../../dbt_wrapper.py
            parameters: ["deps"]
          # No depends_on — first task

        - task_key: seed
          depends_on: [{task_key: deps}]
          spark_python_task:
            python_file: ../../../../dbt_wrapper.py
            parameters: ["seed"]

        - task_key: run
          depends_on: [{task_key: seed}]
          spark_python_task:
            python_file: ../../../../dbt_wrapper.py
            parameters: ["run", "--select", "tag:pricing"]

        - task_key: test
          depends_on: [{task_key: run}]
          spark_python_task:
            python_file: ../../../../dbt_wrapper.py
            parameters: ["test", "--select", "tag:pricing"]
```

Each task can be retried or have its own timeout independently — which is why the dispatcher
pattern (one wrapper, four task entries) is preferred over a single "deps then run" script.

---

## Step 5 — Local development usage

For local iteration (running dbt against a sandbox warehouse):

```bash
# Set credentials in your shell (never commit these)
export DATABRICKS_HOST=https://adb-<workspace-id>.azuredatabricks.net
export DATABRICKS_TOKEN=<your-pat>
export DBT_CATALOG=sandbox
export DBT_SCHEMA=<your_username>_dev

# Run individual phases — invoke the repo-root wrapper, pointing at a product's dbt project
export DBT_PROJECT_DIR=data_products/pricing
python ./dbt_wrapper.py deps
python ./dbt_wrapper.py seed
python ./dbt_wrapper.py run --select +my_new_model
python ./dbt_wrapper.py test --select my_new_model
```

`CGREPO_CA_BUNDLE_PATH` is not required for local runs if your machine already trusts the
cgrepo CA (added via corporate MDM/cert policy). Set it if `dbt deps` fails with SSL errors:

```bash
export CGREPO_CA_BUNDLE_PATH=/path/to/capgroup-ca-bundle.crt
python ./dbt_wrapper.py deps
```

---

## Step 6 — Validate the wrapper

Verify the file was written correctly:

```bash
# Check the dispatcher is present
grep -n "def dispatch" ./dbt_wrapper.py

# Check REQUESTS_CA_BUNDLE is set only for deps
grep -n "REQUESTS_CA_BUNDLE" ./dbt_wrapper.py

# Check no hard-coded tokens (DBX-SEC-002)
grep -n "dapi[a-zA-Z0-9]" ./dbt_wrapper.py && echo "FAIL: token found" || echo "PASS: no tokens"

# Confirm ambient auth path is present
grep -n "apiToken" ./dbt_wrapper.py && echo "PASS: ambient auth wired"
```

---

## Checklist

Before calling this skill complete, verify:

- [ ] `dbt_wrapper.py` written at the **repo root** with the full template above
- [ ] Each product bundle has `sync.paths: ../../dbt_wrapper.py` in its `databricks.yml`
- [ ] `dispatch()` handles all four commands: `deps`, `seed`, `run`, `test`
- [ ] `REQUESTS_CA_BUNDLE` set **only** inside the `deps` branch of `dispatch()`
- [ ] `hydrate_auth()` reads credentials from the **ambient job-context API** (`ctx.apiToken()` / `ctx.apiUrl()`) when on Databricks
- [ ] No hard-coded tokens or hostnames in the file (DBX-SEC-002)
- [ ] `__file__` resolved defensively with `PROJECT_HOME` / `os.getcwd()` fallback (spark_python_task may exec without `__file__`)
- [ ] `_scrub_sys_path_for_dbt()` removes the wrapper's directory from `sys.path` and `PYTHONPATH` before invoking dbt (dbt 1.11+ plugin auto-discovery guard)
- [ ] `--target-path` configured (default `DBT_PROJECT_DIR/target`, overridable via `DBT_TARGET_PATH`) so artifacts persist for capture
- [ ] dbt argv uses subcommand-first ordering: `dbt run --project-dir ...` (dbt 1.10+); never `dbt --project-dir ... run`
- [ ] Wrapper wired into job YAML with four tasks (deps → seed → run → test) via `spark_python_task`

---

## Standards enforced

| Rule | What it requires |
|---|---|
| DBX-SEC-002 | Credentials from Databricks Secrets at runtime; no hard-coded tokens in source files |

---

## cgrepo CA bundle — why this matters

When `dbt deps` runs on Databricks, it fetches package tarballs from
`cgrepo-aws.capgroup.com`. Capital Group's corporate network terminates TLS at an internal
proxy that presents a private CA certificate. Python's `requests` library (which dbt uses) must
trust this CA. Setting `REQUESTS_CA_BUNDLE` points `requests` at the CA bundle file, allowing
the TLS handshake to succeed.

**If this is missing**, the error surfaces as:
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```
or as a connection timeout against `cgrepo-aws.capgroup.com`.

**The fix is NOT** to set `ssl_no_verify` or `--no-ssl` — that disables verification entirely
and would pass a security audit failure. The fix is to supply the correct CA bundle path.

See `/troubleshoot-dbt-on-databricks` for the full diagnostic checklist when `dbt deps` fails.
