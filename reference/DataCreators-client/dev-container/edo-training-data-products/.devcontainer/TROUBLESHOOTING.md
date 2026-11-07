# Troubleshooting Guide

## Quick Navigation

Start with the first failing operation. Use [assigned v2 setup](../challenges/v2/runtime/portfolio/SETUP.md) for the active route; the native product examples below retain separate profiles and loaders.

### Setup & Credential Issues
- [OAuth-first setup does not create credentials](#oauth-first-setup-does-not-create-credentials)
- [`.env` file not found or not being read](#env-file-not-found-or-not-being-read)
- [Environment variables have quotes or extra spaces](#environment-variables-have-quotes-or-extra-spaces)
- [`utils/.env.example` file not found](#utilsenvexample-file-not-found)

### Container Build & Startup
- [Container fails to build](#container-fails-to-build)
- [Container builds but never finishes starting](#container-builds-but-never-finishes-starting)
- [Container starts but credentials aren't available](#container-starts-but-credentials-arent-available)

### Databricks Connectivity
- [Databricks CLI returns permission errors](#databricks-cli-works-but-returns-permission-errors)
- [`databricks auth describe` shows "No credentials"](#databricks-auth-describe-shows-no-credentials)
- [Connection timeout when reaching Databricks](#connection-timeout-when-reaching-databricks)

### DBT Issues
- [`dbt` fails with `'str' object has no attribute 'get'` (Windows)](#dbt-fails-with-str-object-has-no-attribute-get-windows)
- [`dbt` dies with no error (exit 139 / segmentation fault)](#dbt-dies-with-no-error-exit-139--segmentation-fault)
- [`dbt debug` fails even though Databricks CLI works](#dbt-debug-fails-even-though-databricks-cli-works)
- [DBT runs but operations timeout](#dbt-runs-but-operations-timeout)
- [Environment variables not being substituted in `profiles.yml`](#environment-variables-not-being-substituted-in-profilesyml)

### Airflow Issues
- [`astro dev start` times out](#astro-dev-start-times-out)
- [DAG import fails with `Invalid catalog name`](#dag-import-fails-with-invalid-catalog-name-)
- [Airflow webserver shows 502 Bad Gateway](#airflow-webserver-shows-502-bad-gateway)
- [Airflow Databricks connection fails](#airflow-databricks-connection-fails)
- [Cannot access Airflow UI on localhost:8080](#cannot-access-airflow-ui-on-localhost8080)
- [DAG not appearing in Airflow UI](#dag-not-appearing-in-airflow-ui)

### Container Health Checks
- [`dpc-check` fails](#dpc-check-fails)
- [Cannot run Docker commands from within container](#cannot-run-docker-commands-from-within-container)
- [Port conflicts with Postgres (5432) or other services](#port-conflicts-with-postgres-5432-or-other-services)
- [File permission issues when editing files](#file-permission-issues-when-editing-files)

### Python & Package Issues
- [Package import fails after installation](#package-import-fails-after-installation)
- [Slow package installation with pip](#slow-package-installation-with-pip)

### Git & SSL Issues
- [Git SSL certificate errors](#git-ssl-certificate-errors)

### Debugging Tips
- [Enable verbose logging](#enable-verbose-logging)
- [Check container environment](#check-container-environment)
- [Inspect running containers](#inspect-running-containers)
- [Check file system](#check-file-system)

---

## Setup & Configuration Issues

### OAuth-first setup does not create credentials

**Symptoms:** setup stops before a usable session is available.

Check the assigned host and warehouse path, then rerun interactive setup from the project root:

```bash
mise run setup:databricks
dpc-check
```

Use `--pat` only when the instructor supplies the explicit fallback. Re-authentication does not normally require an image rebuild.

### `.env` file not found or not being read

**Symptoms:** a tool reports missing configuration.

Run `pwd` to confirm the project root, then check the generated file exists:

```bash
ls -la .devcontainer/.env
```

`mise run setup:databricks` creates it from the tracked template when needed. Open a fresh terminal after setup and recheck the failing command. OAuth requires host/path metadata and a valid session; it does not require a stored token in `.env`.

### Environment variables have quotes or extra spaces

**Symptoms:** a setting is empty or resolves to an unexpected host or path.

Inspect the relevant non-secret setting and compare it with the assigned value. Remove unintended whitespace; use the format supplied by `.devcontainer/utils/.env.example`. Rerun setup and open a fresh terminal. Check resolved values at the process boundary instead of assuming every tool interprets an environment file identically.

### `utils/.env.example` file not found

The tracked template is `.devcontainer/utils/.env.example`, relative to the project root. Check `pwd` before using a relative path:

```bash
ls -la .devcontainer/utils/.env.example
```

Use the setup task to create `.devcontainer/.env`. If the tracked template is absent, ask the instructor to repair the supplied project rather than inventing credential settings.

## Container Build & Startup Issues

### Container fails to build
**Symptoms:** Build log shows errors, process hangs or exits early

**Solutions:**
1. **Check Docker Desktop is running:** `docker --version` (run on host machine)
2. **Review build logs in VS Code:** Click the "Build" output panel
   - Build logs are also available in docker desktop
3. **Check network connectivity:** Base image might be unreachable, SSL cert issues
   - Try rebuilding with: `Dev Containers: Rebuild Container`
   - Make sure you're on VPN and/or CG Network, if so a reset can fix networking issues
4. **Disk space:** Ensure at least 20GB free on your machine: `df -h`
5. **Docker daemon:** Restart Docker Desktop and try again

### Container builds but never finishes starting
**Symptoms:** Build completes but container doesn't respond

**Solutions:**
1. Check Docker Desktop UI for container status and logs or use the CLI to do it.
   - Commands:
      - List all containers (and their IDs): `docker ps`
      - View container logs: `docker logs <container-id>`
2. If it shows that there's an error with your configuration, fix it as needed.
3. If it isn't, try and kill the container, then reset it (using the UI or CLI)
   - Kill container command: `docker kill <container-id>`
4. Common causes:
   - **Network issues:** Check if you're behind a proxy or firewall
   - **Resource constraints:** Container may need more RAM/CPU in Docker Desktop settings
   - **Port conflicts:** Check if ports 8080 (Airflow) or 5432 (Postgres) are already in use: `lsof -i :8080`

### Container starts but credentials aren't available

**Symptoms:** a CLI or dbt command lacks a usable identity.

Confirm the command is running inside the training container and that setup completed. Rerun `mise run setup:databricks`, open a fresh terminal and inspect `dpc-check`. Check the presence and permissions of `~/.databrickscfg` with `ls -la`; avoid copying its contents into evidence. Shell authentication and the Astro worker connection are separate checks.

## Databricks Connectivity Issues

### Databricks CLI works but returns permission errors

A `401` indicates an authentication problem; a `403` means the selected operation is forbidden. Check the host, identity and exact object or action. Refresh an expired session through `mise run setup:databricks`. For a forbidden action, ask the namespace or workspace owner to confirm assigned access. Replacing a valid credential does not grant missing permissions.

### `databricks auth describe` shows "No credentials"

Confirm the CLI is available in the mise-managed shell:

```bash
mise exec -- databricks --version
mise exec -- databricks auth describe
dpc-check
```

CLI profile readiness and the token delivered to dbt are distinct boundaries. If identity is unavailable, rerun OAuth setup. If the CLI works but dbt fails, check the copied attempt’s profile and open a fresh terminal. Record only non-secret status, not a minted access token. See `docs/rca/2026-08-04-databricks-env-not-propagated-to-shells.md` for the historical shell-delivery diagnosis.

### Connection timeout when reaching Databricks
**Symptoms:** "Failed to connect" or "timeout" errors when running Databricks commands

**Solutions:**
1. Check your internet connection
2. Verify the host URL is accessible from your network (both in the devcontainer and on the host):
   ```bash
   curl -I https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com
   ```
     - If the host can access it via curl, but the container can't, the issue may lie in the container's network settings
3. Check if you're behind a corporate proxy:
   - Configure Docker Desktop proxy settings
   - Update container environment if needed
4. Verify the URL doesn't have trailing slashes: `echo $DATABRICKS_HOST`

## DBT Issues

### `dbt` fails with `'str' object has no attribute 'get'` (Windows)
**Symptoms:** The first `dbt` command in a challenge (e.g. `dbt debug` in `challenges/v1/02-dbt-pipeline/dbt`) exits with a Python traceback ending in:
```
AttributeError: 'str' object has no attribute 'get'
  File ".../dbt/config/project.py", line 845, in read_project_flags
    profile_project_flags = coerce_dict_str(profile.get("config", {}))
```

**Root cause:** `profiles.yml` was checked out as a *broken symlink placeholder*. Git for Windows defaults to `core.symlinks=false`, so a tracked symlink is written to disk as a plain text file whose contents are the link target path. dbt reads that path string as if it were the profile, and crashes when it turns out to be text instead of a config block.

**Check:**
```bash
cat challenges/v1/02-dbt-pipeline/dbt/profiles.yml
```
If the whole file is a single path like `../dbt_profiles/profiles.yml`, this is the bug.

**Fix:** Update to a revision where these are real files (no tracked symlinks remain in this repo), then restore the file:
```bash
git checkout -- challenges/v1/02-dbt-pipeline/dbt/profiles.yml
```
Full analysis: `docs/rca/2026-08-03-profiles-symlink-windows.md`.

### `dbt` dies with no error (exit 139 / segmentation fault)
**Symptoms:** A dbt command that reads data (`seed`, `run`, `build`, `test`, `compile`, `show`) stops after the `Concurrency: 1 threads` line. You may see `Fatal Python error: Segmentation fault` with a pandas/pyarrow stack, or **no output at all and exit code 0**. `dbt debug` passes.

**Root cause:** dbt-databricks converts result sets through pandas by default, and that conversion segfaults on this image (Python 3.13 + `databricks-sql-connector` + pyarrow). `dbt debug` only performs a handshake and returns no rows, so it never hits the faulting path — a green `dbt debug` does not mean dbt can read data.

**Check** which profile the project uses, and confirm every `databricks` target sets:
```yaml
      connection_parameters:
        _disable_pandas: true
```

**Quick smoke test** (two seconds, no side effects) — run from the dbt project directory:
```bash
dbt show --inline "select 1 as a" --limit 1
```
If that segfaults, the profile is missing `_disable_pandas`. If it prints a one-row table, result handling is healthy.

Full analysis: `docs/rca/2026-08-03-challenge-04-dbt-segfault.md`.

### `dbt debug` fails even though Databricks CLI works

Run from the assigned copied dbt attempt:

```bash
dbt --version
dbt debug --project-dir . --profiles-dir . --target local
```

Compare the profile’s host, warehouse path, catalog/schema and prefix with the assigned values. Verify that token delivery is configured without printing its value. A CLI login does not prove warehouse or object access. Ask the owner to resolve missing rights rather than creating another schema.

### DBT runs but operations timeout
**Symptoms:** `dbt run` takes 10+ minutes or hangs

**Solutions:**
1. Check SQL Warehouse status in Databricks: Is it running?
2. Check query logs: Run a simple test query in Databricks UI
3. Look at dbt logs:
   ```bash
   cat logs/dbt.log | tail -50
   ```
4. Increase threads in `profiles.yml` if warehouse is underutilized:
   ```yaml
   threads: 4  # or higher
   ```
5. Check SQL Warehouse size - may need to scale up for large models

### Environment variables not being substituted in `profiles.yml`

Confirm you are using the copied attempt’s profile with `--profiles-dir .`. Check the named variables at that boundary without exposing their values:

```bash
for name in DBT_HOST DBT_HTTP_PATH DBT_CATALOG DBT_SCHEMA DBT_ACCESS_TOKEN; do
  if [ -n "${!name}" ]; then
    printf '%s: set\n' "$name"
  else
    printf '%s: missing or empty\n' "$name"
  fi
done
```

Rerun setup for missing authentication metadata and open a fresh terminal. The assigned `runtime/lab.py ready .` checks conflicting namespace aliases and missing settings. Rebuilding the image does not repair a profile pointing at the wrong environment.

## Airflow Issues

### `astro dev start` times out
**Symptoms:** Error message about webserver health check timeout after 1m0s

**Solutions:**
1. This is **not necessarily** a failure - Airflow is still starting
2. Use `astro dev logs --follow` to monitor startup from the repository root:
   ```bash
   astro dev logs --follow
   ```
3. Wait 2-3 minutes and check if webserver responds: `curl localhost:8080`
4. If still failing after 3 minutes:
   - Check Docker Desktop for container resource issues
   - View detailed logs: `astro dev logs --webserver` or `--scheduler`
5. To increase timeout: `astro dev start --wait 3m` (3 minutes)
6. Common startup blockers:
   - Missing airflow_settings.yaml
   - Database migration issues
   - Scheduler getting stuck on DAG parsing

### `astro dev start` fails with TLS `UnknownIssuer` / dependency fetch errors

**Symptoms:** the runtime image fails during HTTPS dependency installation.

Read the failing host and installer from the build log. The root `requirements.txt` supplies package-index directives; inspect the actual image/configuration rather than assuming the dev shell’s trust store is available during an image build:

```bash
rg -n -- 'ASTRO_RUNTIME_USE_PIP|--trusted-host|--index-url' Dockerfile requirements.txt
```

Ask the instructor or platform owner to confirm the approved index and certificate wiring. Changing installer versions or downgrading the runtime is not a substitute for identifying the failing trust boundary. Once repaired, retry the same build from the project root.

### Airflow webserver shows 502 Bad Gateway

Inspect the Astro services from the project root:

```bash
docker ps
astro dev logs
```

Identify the actual UI/API service and its failure before restarting. Check whether startup is still completing and whether the metadata database is healthy. If configuration was repaired, restart from the project root; `data_products/` is the mounted DAG directory, not the Astro project root.

### `airflow_settings.yaml` is a directory instead of a file

Starting Astro before setup can leave a Docker-created placeholder directory where the settings file should be. Inspect that path, then rerun setup:

```bash
ls -ld airflow_settings.yaml
mise run setup:databricks
```

The supplied setup detects the placeholder. If it contains unexpected work, preserve that work and ask the instructor to repair it. Complete setup before `astro dev start`.

### DAG import fails with ``Invalid catalog name : ``.``
**Symptoms:** `astro dev run dags list-import-errors` is non-empty and shows a Cosmos `CosmosLoadDbtException` ending in:
```
Credentials in profile "portfolio_analytics", target "dev" invalid:
  Invalid catalog name : ``.
```
Meanwhile `dbt debug` in your devcontainer terminal says **All checks passed**.

**Root cause:** The Airflow containers captured their environment **at boot**. `docker-compose.override.yml` forwards the Databricks settings with `"${DBT_CATALOG:-}"`-style interpolation, which resolves against the shell that ran `astro dev start`. If that shell did not have the variables loaded, Compose sets them to the **empty string** inside every container — not unset. dbt's `env_var('DBT_CATALOG', 'training_dev')` only falls back to the default when a variable is *unset*, so an empty value wins and produces the blank catalog name.

Fixing your shell afterwards does not help the already-running containers.

**Check** the shell you are about to start Astro from:
```bash
for v in DATABRICKS_HOST DATABRICKS_HTTP_PATH DBT_CATALOG DBT_SCHEMA; do
  eval "val=\$$v"
  if   [ -z "${val+x}" ]; then s="UNSET"
  elif [ -z "$val" ];    then s="SET-BUT-EMPTY"
  else                        s="$val"; fi
  printf '%-24s %s\n' "$v" "$s"
done
```
Anything `UNSET` or `SET-BUT-EMPTY` means open a fresh terminal at the repo root first (mise loads these per-directory on the shell prompt).

**Fix:**
```bash
mise run setup:databricks          # only if not yet authenticated
astro dev restart --wait 5m        # from a terminal at the repo root
astro dev run dags list-import-errors   # expect: No data found
```

**Prevention:** always run `mise run setup:databricks` **before** `astro dev start`.

Full analysis: `docs/rca/2026-08-03-airflow-blank-databricks-env-at-boot.md`.

### Airflow Databricks connection fails

Check whether `databricks_default` exists in the running Astro environment. OAuth setup supplies the worker connection through the refresher rather than storing its short-lived token in the tracked settings template:

```bash
mise run databricks:oauth-refresh
dpc-check
```

Inspect the selected task’s connection and error. A new shell token alone does not authenticate an existing worker. After changing startup environment values, restart the prepared Astro project conditionally. Missing native-platform job names belong to the retained YAML/DAB route; assigned v2 runs dbt on the worker and uses its owned DAG and project.

### Cannot access Airflow UI on localhost:8080
**Symptoms:** Connection refused, port already in use, or temporary `Unauthorized` while startup is still in progress

**Solutions:**
1. If you see `Unauthorized` right after `astro dev start`, wait for the build/startup to finish and refresh the UI.
2. Monitor startup status from repo root:
   ```bash
   astro dev logs --follow
   ```
3. Confirm the webserver is responding:
   ```bash
   curl -I localhost:8080
   ```
4. Check if port 8080 is in use:
   ```bash
   lsof -i :8080  # macOS/Linux
   netstat -ano | findstr :8080  # Windows
   ```
4. If Airflow is running on a different port:
   - Check logs: `astro dev logs | grep "Running on"`
5. If port is blocked by another application:
   - Stop the conflicting service
   - Or configure Airflow to use different port (advanced)
6. Verify Airflow container is running: `docker ps | grep airflow`

### DAG not appearing in Airflow UI

For assigned v2, confirm the completed attempt was staged into a fresh owned `data_products/<prefix>` directory using `stage-astro`. The worker must see that path through the configured mount; the Python filename and DAG ID need not be identical.

From the prepared Astro project root:

```bash
astro dev run dags list-import-errors
astro dev logs
```

Check the authored syntax, required worker dependencies and the expected `<prefix>_portfolio_daily` ID. Python compilation alone does not load the DAG in Airflow. The retained platform YAML loader is a separate route.

## Container Health Checks

### Cannot run Docker commands from within container
**Symptoms:** `docker ps` or `docker build` fails with "Cannot connect to Docker daemon"

**Solutions:**
1. Ask the dev container to recover its inner Docker daemon: `/usr/local/bin/ensure-dockerd.sh`
2. Wait a few seconds, then check readiness: `docker info`
3. If it is still unavailable, inspect `/var/log/dockerd-heal.log` and `/var/log/dockerd.log`
4. Reopen the dev container so the inner daemon starts cleanly
5. On Windows, also confirm Docker Desktop is using **Linux containers** mode

### Port conflicts with Postgres (5432) or other services
**Symptoms:** Container won't start or Airflow can't connect to database

**Solutions:**
1. Check what's using the port:
   ```bash
   lsof -i :5432  # on host machine
   ```
2. Stop the conflicting service or change Docker Desktop port mappings
3. Check docker-compose.override.yml for custom port configurations

### File permission issues when editing files

Inspect the specific host-mounted path and the process that needs access. The user, mount mode and permissions all affect write access; running the dev container as root does not guarantee a worker can write.

For a staged v2 attempt, check ownership metadata and the project target/log/evidence directories. Keep source fixtures and code at their supplied permissions. Ask the instructor to repair an unexpected mount rather than applying broad recursive permission changes.

## Python & Package Issues

### Package import fails after installation

Identify the executable and dependency environment:

```bash
command -v python
python --version
python -m pip show <package-name>
```

Installing into the dev shell does not install into Astro. Declare worker dependencies in the supplied runtime requirements and rebuild through the approved project process when needed. Do not install packages during DAG parsing.

### Slow package installation with pip
**Symptoms:** `pip install` takes minutes or stalls

**Solutions:**
1. Use faster package manager `uv`:
   ```bash
   uv pip install <package-name>
   ```
2. Check PyPI connectivity: `pip index versions <package-name>`
3. If behind proxy, configure pip in `~/.pip/pip.conf`

## Git & SSL Issues

### Git SSL certificate errors
**Symptoms:** `fatal: unable to access repository: SSL certificate problem`

**Solutions:**
1. Verify certificate is installed: `cat /cacert.pem` (should exist)
2. Check git config: `git config --global http.sslCAInfo`
3. Should point to: `/cacert.pem`
4. Add to git config if missing:
   ```bash
   git config --global http.sslCAInfo /cacert.pem
   ```
5. Rebuild container if changes don't take effect

### Docker registry auth needs a reset
**Symptoms:** `docker login cgregistry-aws.capgroup.com` keeps failing after auth changes.

**Solutions:**
1. Clear the stale login first: `docker logout cgregistry-aws.capgroup.com`
2. Rerun the OAuth-first setup: `mise run setup:databricks`
3. If needed, use the PAT fallback explicitly: `mise run setup:databricks --pat`

## Docker & System Issues

### `dpc-check` fails
**Symptoms:** The health check exits non-zero or reports dockerd/Databricks problems.

**Solutions:**
1. Check Docker Desktop is running on the host.
2. Reopen the dev container so DinD can restart cleanly.
3. Verify the Databricks CLI can authenticate: `databricks auth describe`
4. Re-run the end-to-end gate: `bash scripts/verify-with-databricks.sh`

## Debugging Tips

### Enable verbose logging
For most tools, use `--debug` or `--verbose` flags:
```bash
dbt debug --debug
databricks --debug workspace list
astro dev logs --follow
```

### Check container environment

Check only the variables required by the failing command. Use the presence-only loop in [profile troubleshooting](#environment-variables-not-being-substituted-in-profilesyml); a full environment dump can contain credentials.

### Inspect running containers
```bash
docker ps  # List running containers
docker logs <container-id>  # View logs
docker exec -it <container-id> bash  # Open shell
```

### Check file system

Check locations and permissions without dumping credential-bearing files:

```bash
ls -la ~/.databrickscfg .devcontainer/.env
ls -la data_products/
```

Record the relevant path, ownership and error in evidence.
