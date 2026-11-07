---
name: run-dbt-on-databricks
description: |
  Execute dbt models against a Databricks warehouse or cluster using three
  invocation modes: local developer iteration, bundle-deploy (DAB push), and
  bundle-run (job execution). Use when you need to run, deploy, or trigger a
  dbt pipeline on Databricks.
  Trigger phrases: "run dbt on Databricks", "deploy dbt to Databricks",
  "trigger dbt job", "dbt run with --select".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards: [DBX-WORKFLOW-001, DBX-SEC-002]
---

# Run dbt on Databricks

Execute dbt models against a Databricks SQL warehouse or all-purpose cluster
using one of three modes, depending on the stage of the development loop.

---

## Choosing a Mode

| Mode | When to use | Entry point |
|---|---|---|
| **Local** | Inner dev loop — iterating on model SQL, testing against a sandbox warehouse | `dbt run` CLI (local machine or dev cluster) |
| **Bundle-deploy** | Pushing the pipeline DAB to Databricks, after code is ready to promote | `databricks bundle deploy` |
| **Bundle-run** | Triggering an already-deployed DAB job on Databricks, e.g. to validate end-to-end | `databricks bundle run` |

Work through the modes in order during development: local → bundle-deploy → bundle-run.

---

## Prerequisites

Before running any mode, ensure the following are in place:

1. **`profiles.yml`** — configured with a `databricks` target pointing to your
   sandbox warehouse. Typically lives at `~/.dbt/profiles.yml`.
2. **`dbt_wrapper.py`** — the task-runner shim used in DAB jobs.
   See `/write-dbt-wrapper` for what this file does and how it is generated.
3. **Databricks CLI authenticated** — run `databricks auth login` and confirm
   with `databricks auth env` before bundle operations.
4. **`databricks.yml`** — DAB manifest at the repo root.
   See `/databricks-bundles` for scaffolding guidance.

---

## Mode 1: Local Run

Use this mode for rapid iteration on model SQL. dbt talks directly to a
Databricks SQL warehouse over ODBC/HTTP.

### Basic run

```bash
dbt run --target local
```

This runs all models in the default compilation order against the `local`
target in `profiles.yml`.

### Run a subset of models with `--select`

```bash
# Run a single model
dbt run --target local --select stg_employee__records

# Run a model and all its downstream dependents
dbt run --target local --select stg_employee__records+

# Run a tag group
dbt run --target local --select tag:employee_domain

# Run everything in a directory
dbt run --target local --select models/staging/employee/
```

The `--select` selector syntax follows the standard dbt node-selection grammar.
See `/fetching-dbt-docs` to pull the official dbt selector reference.

### Full-refresh (rebuild from scratch)

```bash
dbt run --target local --full-refresh
```

Add `--full-refresh` to truncate and recreate incremental models. This is
especially important for bitemporal_load_v2 models where watermarks could
otherwise cause partial updates during iteration.

### Inspect compile output without running

```bash
dbt compile --target local --select stg_employee__records
```

The compiled SQL lands in `target/compiled/`. Useful for reviewing what dbt
will actually execute before touching the warehouse.

### Run with debug logging

```bash
dbt --debug run --target local --select stg_employee__records
```

`--debug` prints full Jinja rendering and connection traces — the fastest way
to diagnose macro errors or auth issues locally.

---

## Mode 2: Bundle-Deploy

Bundle-deploy packages the dbt project and all supporting Python files into a
Databricks Asset Bundle (DAB) and syncs them to your workspace. This is a
pre-condition for bundle-run.

### Deploy to dev

```bash
databricks bundle deploy --target dev
```

This command:
1. Validates `databricks.yml` against the target environment.
2. Uploads all files in `include` (models, macros, seeds, `dbt_wrapper.py`).
3. Creates or updates Jobs and DLT pipelines declared in `resources/`.

### Deploy a specific resource

```bash
databricks bundle deploy --target dev --resource jobs.dbt_employee_pipeline
```

Useful when iterating on a single job definition without re-deploying
unrelated resources.

### Check what would be deployed (dry-run)

```bash
databricks bundle validate --target dev
```

Resolves variable substitutions and prints the effective bundle manifest
without making API calls. Run this before every deploy to catch YAML errors.

### Confirm the deploy succeeded

After `databricks bundle deploy`, list the workspace path to verify files are
present:

```bash
databricks workspace ls /Workspace/Repos/dev/<bundle-name>/
```

---

## Mode 3: Bundle-Run

Bundle-run triggers an already-deployed DAB job on Databricks. The job calls
`dbt_wrapper.py` at task time, which in turn invokes `dbt run` with the
correct environment, catalog target, and secrets.

### Run a job end-to-end

```bash
databricks bundle run <job-key> --target dev
```

Where `<job-key>` matches the job identifier in `databricks.yml` under
`resources.jobs`.

Example — if your `databricks.yml` defines:

```yaml
resources:
  jobs:
    dbt_employee_pipeline:
      name: dbt-employee-pipeline-dev
```

Then:

```bash
databricks bundle run dbt_employee_pipeline --target dev
```

### Pass dbt CLI arguments through the wrapper

`dbt_wrapper.py` reads its arguments positionally via `sys.argv`: the first
argument is the dbt sub-command, and any subsequent arguments are passed
through to dbt as-is. Use `--python-params` (a JSON array) to supply
positional arguments to a Python task in a bundle-run job.

Plain run (no extra flags):

```bash
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["run"]'
```

Run with a dbt node selector:

```bash
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["run", "--select", "stg_employee__records+"]'
```

Full refresh:

```bash
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["run", "--full-refresh"]'
```

Run a specific dbt sub-command (e.g. test):

```bash
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["test", "--select", "tag:my_tag"]'
```

### Stream run output

```bash
databricks bundle run dbt_employee_pipeline --target dev --no-wait
```

`--no-wait` returns immediately with a run URL. Monitor progress in the
Databricks UI or with:

```bash
databricks jobs get-run <run-id>
```

### Full-refresh via bundle-run

When a job's dbt task needs a full-refresh (e.g., resetting incremental
watermarks after a schema change), pass positional args via `--python-params`:

```bash
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["run", "--full-refresh", "--select", "int_employee_v4+"]'
```

---

## Environment Targets

| Target | Purpose | Warehouse / Compute |
|---|---|---|
| `local` | Developer iteration | Sandbox shared SQL warehouse |
| `dev` | Integration testing | Dev SQL warehouse or dev cluster |
| `staging` | Pre-production validation | Staging cluster (mirrors prod config) |
| `prod` | Production run | Production SQL warehouse |

The `--target` flag for `dbt` maps to a profile entry in `~/.dbt/profiles.yml`.
The `--target` flag for `databricks bundle` maps to a `targets:` entry in
`databricks.yml`. Both must be configured consistently.

---

## Quick Reference

```bash
# Local iteration on a single model
dbt run --target local --select stg_employee__records

# Local full-refresh
dbt run --target local --full-refresh

# Deploy the bundle to dev
databricks bundle deploy --target dev

# Validate bundle before deploy
databricks bundle validate --target dev

# Trigger the deployed job
databricks bundle run dbt_employee_pipeline --target dev

# Trigger with custom dbt selector
databricks bundle run dbt_employee_pipeline --target dev \
  --python-params '["run", "--select", "tag:employee_domain"]'
```

---

## Related Skills

- `/write-dbt-wrapper` — generates the `dbt_wrapper.py` shim and explains
  its task-time behavior (auth hydration from dbutils, env var injection,
  exit-code propagation).
- `/databricks-bundles` — scaffolds `databricks.yml`, target configs, and
  resource definitions.
- `/databricks-jobs` — configures job YAML, cluster specs, and task ordering.
- `/troubleshoot-dbt-on-databricks` — failure-mode reference for SSL errors,
  auth failures, materialization issues, and cold-start timeouts.
- `/dbt-best-practices` — coding conventions and generation-time guidance for
  dbt models in the Catalyst DPLC.
