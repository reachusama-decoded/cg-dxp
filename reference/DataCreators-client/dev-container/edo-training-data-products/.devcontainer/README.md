# Dev Container Configuration

The VS Code dev container supplies the training tools and setup tasks. Complete authentication and inspect readiness before assigned practice; tool presence alone does not establish runtime access.

## Assigned v2 route

Start with [Getting started](../GETTING_STARTED.md#assigned-v2-practice), then prepare the selected [v2 phase](../challenges/v2/README.md). Portfolio Analytics uses dbt-databricks/Astro and the [CG capstone](../challenges/cg-public-products/README.md) uses a distinct public-product snapshot. Each copied attempt owns prefixed relations in the approved namespace. The native product, source-clone and YAML DAG workflows below are platform reference, not extra v2 prerequisites.

## Quick Navigation

Select a setup or reference section:

### Getting Started
- [What's Included](#whats-included) - View all pre-installed tools
- [Prerequisites](#prerequisites) - System requirements
- [Step 1: Open in Container](#step-1-open-the-repository-in-the-dev-container) - Build, start, and authenticate
- [Step 2: Verify Setup](#step-2-verify-your-setup) - Test your configuration

### Development Guides
- [Running DBT](#running-dbt) - Using the DBT project with Databricks
- [Working with Airflow DAGs](#working-with-airflow-dags) - Assigned Python DAGs and platform YAML reference
- [User-scoped source clones](#user-scoped-source-clones) - Shallow-clone upstream sources for isolated local/dbt workflows
- [Common Development Workflows](#common-development-workflows) - Databricks CLI, Python, Airflow
  - [Working with Databricks](#working-with-databricks)
  - [Python Development](#python-development)
  - [Working with Airflow](#optional-airflow-workflow-details)
  - [Configuring Airflow Connections](#configuring-airflow-connections-and-settings)

### Configuration & Management
- [Workspace Setup](#workspace-setup) - Container startup process
- [Managing the Dev Container](#managing-the-dev-container) - Rebuild, close, reopen, Docker access
- [Python Environment](#python-environment) - Virtual environment details

### Troubleshooting & Info
- [Troubleshooting](#troubleshooting) - Common issues and solutions
- [Notes](#notes) - General information
- [VSCode Sessions](#vscode-sessions) - Known limitations
- [Databricks Auth](#databricks-auth) - PAT and OAuth information

---

## What's Included

### Core Data Engineering Tools
- **Databricks CLI** - for interacting with Databricks workspaces
- **DBT Core** - for running DBT workflows
- **Docker & Docker Compose** - for containerized data workflows; used for optional Airflow environment
- **Astro CLI** - for provisioning a local Airflow environment
- **Python 3.13** - with a pre-configured virtual environment

## Getting Started

### Prerequisites
- Docker Desktop installed and running
- Visual Studio Code with the Dev Containers extension installed
- A Databricks workspace (OAuth preferred; PAT fallback supported)

### Step 1: Open the Repository in the Dev Container

Open the workspace folder in VS Code, then choose **Dev Containers: Rebuild and Reopen in Container**. On a fresh clone, startup creates `.devcontainer/.env` from the tracked safe template and launches the Databricks OAuth login. No pre-existing `.env` file is required.

Startup timing note:

- Initial devcontainer setup can take several minutes.
- Wait until `dpc-check` runs in the devcontainer terminal and prints its results.
- Read the gate results. Resolve failed or warning prerequisites for the affected activity before running its commands.

If OAuth setup was interrupted, rerun it inside the container:

```bash
mise run setup:databricks
```

The generated `.devcontainer/.env` supplies these non-secret training defaults:
- `DATABRICKS_HOST` - Your workspace URL
- `DATABRICKS_HTTP_PATH` - Your SQL Warehouse HTTP path

OAuth is the default and does not store an access token in the repository or generated environment contract. The setup does not persist OAuth access tokens in airflow_settings.yaml; live OAuth access tokens are written to Airflow metastore connections by the OAuth refresher and are not persisted in local settings files. If you must use a PAT, run `mise run setup:databricks --pat` inside the container.

### Environment Variables

The generated `.env` file is git-ignored. Setup reads it after the container starts, so a missing untracked file cannot block the initial container launch. OAuth-derived shell tokens are short-lived and refreshed by `.mise/env.sh`; PAT values are only used when the explicit `--pat` fallback is selected.

### Step 2: Verify Your Setup

Run the local health check first (fast deterministic checks):

```bash
# Fast local checks
dpc-check
pytest tests/local_env/offline
# Optional: run live integration checks (set CERT_INTEGRATION_TESTS=1 to enable)
# CERT_INTEGRATION_TESTS=1 pytest tests/local_env/live -m integration

# End-to-end Databricks gate
bash scripts/verify-with-databricks.sh

# Or run umbrella verifier (recommended):
mise run verify:local-dev
```

These checks cover different boundaries. Inspect each result and verify the assigned namespace and worker separately before connected practice.

## Running DBT

Each product has its own dbt configuration. Portfolio Analytics uses `data_products/portfolio_analytics/`. The [CG capstone](../challenges/cg-public-products/project/README.md#your-working-folder) uses the instructor-assigned product folder and explicit project/profile helper; check the workspace before each product switch.

### How It Works

Each data product's `dbt_profiles/profiles.yml` reads credentials from environment variables:

- `DBT_HOST` -- Databricks workspace URL (e.g. `https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com`)
- `DBT_ACCESS_TOKEN` -- short-lived OAuth token, or PAT in explicit fallback mode
- `DBT_HTTP_PATH` -- SQL Warehouse HTTP path (copied from `DATABRICKS_HTTP_PATH` by setup)

If you have `mise` activated and a `[DEFAULT]` profile in `~/.databrickscfg`, these are set automatically via `.mise/env.sh`. Otherwise, export them manually.

dbt vars (`catalog`, `schema`, `http_path`) are defined per data product in `variables/variables.yml` and passed at runtime via `--vars` or picked up from the profile's `local` target.

### Running dbt with mise

For native platform products, these mise tasks run from the project root with the product name. Assigned v2 direct dbt commands run inside the copied attempt using its local profile.

```bash
# Install dbt package dependencies
mise run dbt:deps orders

# Run all models for a data product
mise run dbt:run orders

# Run a specific model
mise run dbt:run orders -- --select orders_daily

# Test models
mise run dbt:test orders

# Run for a different data product
mise run dbt:run YOUR_PRODUCT_NAME
```

These tasks default to `--target local` and `--profiles-dir dbt_profiles`. You can pass additional dbt flags after `--`.

### Running dbt without mise

```bash
cd data_products/orders
dbt deps --profiles-dir dbt_profiles
dbt run --profiles-dir dbt_profiles --target local
```

## User-scoped source clones

This optional platform route creates user-scoped schemas; it is not required for v2, whose supplied fixtures use prefixed relations in one approved schema.

The `clone-sources` mise task shallow-clones the upstream dbt source tables declared by each data product into user-scoped schemas in the workspace default catalog (`current_catalog()`). The schema prefix is derived from the authenticated Databricks identity (`current_user()`), which matches the user deploying the DAB. This lets each deployer work with isolated source copies without touching shared dev/sqa/prd tables.

### Prerequisites

Each data product's `dbt_profiles/profiles.yml` reads two DBT-specific environment variables for authentication:

| Variable | Description |
|---|---|
| `DBT_HOST` | Your Databricks workspace URL (same value as `DATABRICKS_HOST`) |
| `DBT_ACCESS_TOKEN` | Short-lived OAuth token, or the explicit fallback PAT |

> **Caveat — `DBT_HOST` is an overloaded name.** dbt-core also reserves `DBT_HOST` as the
> default for `dbt docs serve --host` (the local bind address). Because this repo sets it to
> the Databricks workspace URL, a bare `dbt docs serve` tries to bind a socket to
> `https://…databricks.com` and fails with `socket.gaierror: [Errno -2] Name or service not
> known`. Always pass the flag explicitly: `dbt docs serve --host 127.0.0.1 --port 8081`
> (8080 is the Airflow UI). See `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md`.

**For clone-sources**: These variables are automatically populated from your `~/.databrickscfg` file if you have a `[DEFAULT]` profile configured. No additional setup is required unless you prefer to explicitly set them in `.devcontainer/.env`.

**For local dbt runs**: Complete the default OAuth setup. It exports `DBT_HOST` and `DBT_HTTP_PATH` from the configured Databricks values and refreshes `DBT_ACCESS_TOKEN` in each mise-managed shell. Use the explicit `--pat` fallback only when OAuth is unavailable.

### Running clone-sources

```bash
# Create (or refresh) user-scoped source clones for all data products
mise run clone-sources

# Show available flags for the underlying CLI
mise run clone-sources:help

# Pass through Python CLI flags after '--'
mise run clone-sources -- --databricks-profile DEFAULT

# Remove the clone schemas when you're done
mise run clone-sources:cleanup

# Cleanup with an explicit Databricks profile
mise run clone-sources:cleanup -- --databricks-profile DEFAULT
```

For clone-sources, schemas resolve to:
- **default** -> `<workspace_default_catalog>.<databricks_user>__<source_schema>`

`clone-sources` fails fast when `current_catalog()` is unresolved or resolves to `hive_metastore`. In that case, set a Unity Catalog default catalog in your Databricks workspace and rerun.

For dbt source resolution in local development, sources resolve to:
- **local target** -> `<workspace_default_catalog>.<databricks_user>__<source_schema>`
- **non-local targets** -> original upstream locations (unaffected)

See the repository-level [README.md](../README.md) for details on how sources are resolved across targets.

## Working with Airflow DAGs

Assigned v2 work uses the Python DAG in its copied starter; stage that attempt using [shared setup](../challenges/v2/runtime/portfolio/SETUP.md). The platform examples below use YAML definitions rendered by `dags_loader.py`.

### How It Works

Platform products can contain dataset folders with YAML orchestration declarations. The CG capstone supplies its own custom DAG and workflow-template instructions.

- `{dataset}.dag.yml` - Defines the DAG structure, tasks, and dependencies
- `{dataset}.dq.yml` - (Optional) Defines data quality rules

The `dags_loader.py` at the repository root parses these YAML files and generates Airflow DAGs dynamically. To create a new DAG, simply add or modify the corresponding YAML files in your data product's `datasets/{dataset}/airflow/` folder.

### Running Airflow

Important: run `mise run setup:databricks` before `astro dev start`. This setup writes `AIRFLOW_VAR_DATABRICKS_JOB_PREFIX`, which must be present when Astro containers start.

If Astro was started first, run:

```bash
mise run setup:databricks
astro dev restart --wait 5m
```

```bash
cd /workspaces/<workspace-name>

# Start the local Airflow environment
astro dev start

# View logs
astro dev logs

# Stop the environment
astro dev stop
```

Once Airflow is running, access the UI at `localhost:8080`.

If you access the UI while `astro dev start` is still building/initializing, you may briefly see an **Unauthorized** page. Wait for startup to complete, then refresh.

If you have more than one Astro environment on your machine, confirm you are using the one started **inside this devcontainer** before debugging DAG failures:

```bash
# Run in the devcontainer terminal
docker ps --format '{{.Names}}' | grep 'edo-training.*-scheduler-1'
```

If a platform-reference task cannot resolve its Databricks job name, check the job prefix at task runtime. Run:

```bash
mise run setup:databricks
astro dev restart --wait 5m
```

This repopulates local Airflow Databricks settings (including `databricks_job_prefix`) and refreshes OAuth-backed connections used by the DAG.

## Workspace Setup

On container startup, the `postCreateCommand` performs the following:
1. Trusts `.mise.toml`, installs toolchain dependencies, and initializes Python dependencies
2. Configures mise shell wiring and GitHub authentication bootstrap
3. Leaves Databricks authentication as an explicit interactive step (`mise run setup:databricks`)
4. Creates `airflow_settings.yaml` only when you run the post-auth setup command (`mise run setup:airflow-settings`)

**Credential Configuration:**
- OAuth is the default for the Databricks CLI and dbt.
- If setup was interrupted, run `mise run setup:databricks` inside the container.
- A PAT is used only when you explicitly run `mise run setup:databricks --pat`.

## Managing the Dev Container

### Rebuild the Container
If you modify the `Dockerfile`, `devcontainer.json`, or `.env`:
1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Search for `Dev Containers: Rebuild Container`
3. Click to rebuild

Rebuild when the image or container configuration changes. A refreshed OAuth session or edited runtime metadata usually needs setup and a fresh terminal instead.


### Reopen in Container
To close and reopen the container:
1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Search for `Dev Containers: Reopen Folder Locally` to exit
3. Use `Reopen in Container` to restart

Reopening changes the VS Code connection; it does not reset warehouse data or an attempt.

### Close the Container
To completely exit the dev container and return to your local environment:

1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Search for `Dev Containers: Reopen Folder Locally`
3. Click to close the container and return to local development

This closes VS Code's connection to the container. The container itself may continue running in the background.

**To stop the container completely (optional):**
```bash
# Find the container ID
docker ps

# Stop the container
docker stop <container-id>
```

### Docker Daemon Access
The dev container runs its own Docker daemon (DinD) inside the container. `postStartCommand` starts `dockerd`, runs a recovery probe, and then runs `dpc-check`; `postAttachCommand` heals it if it becomes unhealthy. `dpc-check` verifies the daemon, CLI tools, TLS wiring, and Databricks readiness. This allows:
- Running Docker commands from within the container
- Building and managing containers without mounting the host socket
- Access to `docker-compose` for orchestration

**Platform support notes:**
- Linux hosts: supported.
- Windows hosts: supported when Docker Desktop is running in **Linux containers** mode.
- Windows containers mode is not supported by this devcontainer/Astro workflow.

## Python Environment

A virtual environment is pre-configured at `/opt/venv`:
- Automatically activated when the container starts
- Contains `pip`, `setuptools`, `wheel`, and `uv`
- Python path: `/usr/local/bin/python`
- Some common packages are pre-installed, but you may need to install additional dependencies for your specific work

## Common Development Workflows

### Working with Databricks

After OAuth setup, the Databricks CLI uses its configured profile. The following platform examples require access to their respective objects:

```bash
# List workspace contents
databricks workspace list /

# Work with jobs, clusters, and notebooks
databricks jobs list
databricks clusters list
databricks secrets list-scopes

# Upload files
databricks fs cp local-file.csv dbfs:/path/to/file.csv
```

**Configuration:** OAuth login writes the Databricks CLI profile to `~/.databrickscfg`. Setup stores only non-secret host/path metadata in `~/.config/dpc/databricks.env`, while `.mise/env.sh` refreshes short-lived tokens for dbt and Python tools.

If `docker login cgregistry-aws.capgroup.com` starts failing with auth errors, run:

```bash
docker logout cgregistry-aws.capgroup.com
```

Then rerun the OAuth-first setup.



### Python Development

Use Python directly for data analysis, scripting, or library development:

```bash
python -c "import pandas; print(pandas.__version__)"

pip install <package-name>

# Or use the faster uv package manager
uv pip install <package-name>
```

### (Optional) Airflow Workflow Details

For advanced Airflow operations or detailed workflow information:

```bash
cd /workspaces/<workspace-name>

# Restart Airflow (useful after code changes)
astro dev restart

# View scheduler logs
astro dev logs --scheduler

# View webserver logs
astro dev logs --webserver
```

### Configuring Airflow Connections and Settings

The local `airflow_settings.yaml` file defines Airflow Connections, Variables, and Pools.

**Key files:**
- `.airflow/airflow_settings.yaml.example` - tracked, secret-free template
- `airflow_settings.yaml` - generated local settings file (git-ignored)

The devcontainer setup copies the tracked template and sets `databricks_job_prefix` from your authenticated Databricks identity. To rerun it:

```bash
mise run setup:airflow-settings
```

OAuth setup for the Databricks CLI and dbt does not persist its short-lived user token into Airflow settings. If a local DAG needs the `caspian-training-databricks` connection, create it in the Airflow UI with an authentication method supported by the Airflow Databricks provider. Do not put credentials in the tracked example.

## Troubleshooting

Encountering issues with the dev container? Refer to the comprehensive [Troubleshooting Guide](./TROUBLESHOOTING.md) for solutions to common problems including:

- **Setup & Configuration Issues** - `.env` file problems, environment variables
- **Container Build & Startup Issues** - Build failures, startup timeouts, missing credentials
- **Databricks Connectivity Issues** - Authentication errors, timeouts, permission issues
- **DBT Issues** - Connection failures, timeouts, variable substitution
- **Airflow Issues** - Startup problems, webserver errors, DAG parsing
- **Docker & System Issues** - Port conflicts, permissions, Docker daemon
- **Python & Package Issues** - Import failures, slow installations
- **Git & SSL Issues** - Certificate errors
- **Debugging Tips** - Logging, container inspection, file system checks

## Notes

- The container runs as `root` user.
- File permissions on the host are preserved through the Docker mount
- All paths reference the workspace as `/workspaces/<workspace-name>`
- Use the assigned runtime and environment for practice; ask the instructor to resolve missing prerequisites.

## VSCode Sessions

Host and dev-container editor sessions can use separate storage. Before rebuilding, preserve changes and evidence in repository files rather than relying on a chat session.

## Databricks Auth

The supported default is Databricks user-to-machine OAuth. `mise run setup:databricks` authenticates the CLI, writes only non-secret host/path metadata to `~/.config/dpc/databricks.env`, and refreshes short-lived shell tokens through `.mise/env.sh`.

PAT authentication is an explicit fallback: run `mise run setup:databricks --pat`. It prompts for the workspace host and token (or reuses `DATABRICKS_TOKEN` if already set), validates the token before writing config, and lets you pick a SQL warehouse. The underlying script still accepts `--pat` directly, but the `mise` task is the preferred entrypoint.

### Databricks auth: one mode at a time (OAuth primary, PAT backup)

This repo uses a single active auth mode, recorded in `~/.config/dpc/databricks.env`
as `DPC_DATABRICKS_AUTH_MODE` (`oauth` or `pat`). Every surface — local dbt,
Databricks Asset Bundles, and local Airflow — uses that one mode. You do not mix
OAuth and PAT.

- **OAuth (default, recommended):** one browser login. Run
  `mise run setup:databricks` (i.e. `.devcontainer/setup-databricks-dbt.sh`
  without `--pat`). dbt and bundles refresh automatically. Local Airflow cannot use
  the browser session directly, so a background **token refresher**
  (`.devcontainer/utils/databricks-oauth-refresh.sh`) keeps the `databricks_default`
  and `caspian-training-databricks` connections supplied with a fresh token. It starts
  automatically in OAuth mode; restart it with `mise run databricks:oauth-refresh`.
  Disable it with `DPC_SKIP_OAUTH_REFRESH=1`.

- **PAT (backup):** if OAuth (or the Airflow refresher) is broken and you need in
  quickly, run `mise run setup:databricks --pat` and paste a token from the
  Databricks UI. This switches the whole system to the PAT.

**Check health / recover:** run `dpc-check`. It prints the active mode and, in OAuth
mode, whether the refresher heartbeat is fresh. If it is stale, re-run
`mise run setup:databricks`, or switch to the PAT backup above.

For the local Airflow connections to resolve at all, the compose override sets the
secrets backend to `MetastoreBackend` (the Astro image otherwise defaults to AWS
Secrets Manager). The connections use an **empty login** with the token in the
password field so the provider sends `Authorization: Bearer` — an OAuth token is
rejected over HTTP Basic (which a non-empty login would trigger).
