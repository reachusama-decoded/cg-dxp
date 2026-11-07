---
name: deploy-airflow-local
description: |
  Bring up a local Airflow environment with the Astronomer CLI
  (`astro dev start`) for any Astro-based data product, so a developer can
  see their YAML-defined DAGs render and run them against Databricks.
  Covers pre-steps (settings file, Airflow Variables, Databricks
  connection), the start, loading objects host-side without `mise`, and
  known gotchas (health-check timeout, settings-file auto-import,
  platform-plugin import errors, port conflicts, blocked public base
  image). Environment-specific values (conn_id, catalog, schema) should
  match what the project's DAGs expect. Local only — not Astronomer Cloud
  (see connect-astro).
  Trigger phrases: "start airflow locally", "run airflow locally",
  "astro dev start", "spin up local airflow", "bring up local airflow",
  "deploy airflow locally", "test my dags locally".
allowed-tools: Read Bash Write Edit Grep
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies:
    - connect-databricks  # optional — only needed to run tasks, not to parse DAGs
  consumes:
    - docker-compose.override.yml
    - .astro/config.yaml
    - .airflow/airflow_settings.yaml.example
    - .airflow/airflow_settings.yaml  # produced by Step 1, git-ignored
    - .env                            # optional, git-ignored — token alternative
    - Dockerfile
  shared-components:
    core: []
    platforms: [astronomer, databricks]
  standards:
    - PY-AIRFLOW-021   # No secrets in operator args — token via connection/env (provisional; RFD 0011 is prediscussion, source will resolve when it merges)
---

# deploy-airflow-local

Bring up a **local** Airflow environment via the Astronomer CLI
(`astro dev start`) for any Astro-based data product, validate
that the dynamically generated DAGs parse and appear, and wire up a
Databricks connection so tasks can run.

This is the *local developer loop* — `astro dev start` spins up Airflow in
Docker on your machine. It is **not** a deployment to Astronomer Cloud; for
authenticating/deploying to a hosted Astro deployment, use `connect-astro`.

> Validated against `edo-ig-data-products@main` with Astro CLI 1.38.1.
> Examples below use that project's conventions; adapt conn_id, catalog,
> and schema to your project.

## When to use

- You want to see the DAGs generated from your
  `data_products/**/airflow/*.dag.yml` files render in a real Airflow UI
  before pushing.
- You changed a DAG YAML, a blueprint, or `dags_loader.py` /
  `blueprints_loader.py` and want to confirm it still parses.
- You want to trigger a dataset's job against Databricks from a local
  scheduler.

## Project shape this skill assumes

An Astro project at the repo root (e.g. `edo-ig-data-products`):

- `Dockerfile` — `FROM quay.io/astronomer/astro-runtime:<ver>-base` (see the
  build note in Troubleshooting).
- `.astro/config.yaml` — Astro project config.
- `docker-compose.override.yml` — bind-mounts the repo's `data_products/`
  to `/usr/local/airflow/dags`, plus `.airflow/{plugins,include,tests}` and
  `.airflow/airflow_settings.yaml`. Paths use `${HOST_WORKSPACE_PATH:-.}`.
- `data_products/dags_loader.py` + `data_products/blueprints_loader.py` —
  generate Airflow DAGs **dynamically** from each dataset's YAML at parse
  time. There are no hand-written DAG `.py` files for datasets.
- `.airflow/airflow_settings.yaml.example` — committed template for the
  Airflow connections / variables / pools. The real
  `.airflow/airflow_settings.yaml` is **git-ignored**.

## Prerequisites

- **Docker Desktop** installed and running. (At Capital Group this needs the
  `CPZ_INF_BB00000003_Docker_Desktop_User` role.)
- **Astro CLI** installed: `astro version`.
- You are at the **repo root** of the Astro project.
- (Only to *run* tasks, not to *parse* DAGs) Databricks credentials. DAGs
  render from Airflow **Variables**, so a real token is only needed when you
  actually trigger a task that talks to Databricks.

> The documented repo workflow uses `mise run …` because it is written for
> the dev container, where `mise` is pre-installed. **On a plain host `mise`
> is usually not available.** This skill therefore uses `astro` CLI commands
> directly, which work the same in or out of the dev container.

## Procedure

### 1. Create the local settings file

`.airflow/airflow_settings.yaml` is git-ignored and ships only as
`.airflow/airflow_settings.yaml.example`. Copy it:

```bash
cp .airflow/airflow_settings.yaml.example .airflow/airflow_settings.yaml
```

This file is bind-mounted into the Airflow containers
(`docker-compose.override.yml`). **Never commit it and never hard-code a
real token in it** — keep the Databricks token out of the file (Step 4).

### 2. Fill in the required Airflow Variables

The DAG loader renders DAG templates from Airflow **Variables at parse
time**, so set these before relying on the UI (the repo docs warn that a
missing required variable can mean DAGs don't appear). Edit the `variables:`
block of `.airflow/airflow_settings.yaml` and set at least:

| Variable | What to set |
|---|---|
| `databricks_job_prefix` | `"[dev XX] "` — your initials; matches the DAB `mode:development` job-name prefix |
| `dev_cluster_id` | your personal cluster ID (Databricks → Compute → your cluster) |
| `root_path` | leave `""` for local; set by bundle deployment otherwise |
| `data_products_path` | `"/usr/local/airflow/dags"` (the in-container mount of `data_products/`) |
| `default_catalog` | your dev catalog (e.g. `caspian_ig_dev`) |
| `index_schema` | `"index"` (unless the index_summary schema was renamed) |
| `target_schema_local_override` | `"<catalog>.zz_<initials>"` for local dev; leave empty in shared envs |
| `http_path` | your SQL warehouse HTTP path (may be `""` for parse-only) |
| `aws_region` | e.g. `us-east-1` |

Your project may define additional namespaced variables (e.g.
`edo-ig-data-products/variables/app_catalog`). Check your
`.airflow/airflow_settings.yaml.example` for the full list.

The kafka/topic/arn variables (`data_notify_topic`, `kafka_secret_arn`,
`rootca_secret_arn`, `bootstrap_brokers`, `schema_registry_url`) can stay as
harmless placeholders unless you exercise the notify path. The `.example` is
the source of truth for the full list.

### 3. Start Airflow

The bind mounts in `docker-compose.override.yml` resolve from
`${HOST_WORKSPACE_PATH:-.}`. On a plain host (no dev-container startup
script) export it to the repo root before starting, so the `data_products/`
mount comes up populated:

```bash
export HOST_WORKSPACE_PATH="$(pwd)"   # plain host; the dev container sets this for you
astro dev start --wait 5m
```

The webserver health check may time out (default is 1m on Intel, 5m on
Apple Silicon). This is **benign** — the containers keep starting and are
usually reachable within 2–3 minutes. Confirm with `docker ps` and
`curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health`
(expect `200`).

> **Note:** DAGs won't render yet — variables haven't been loaded. This is
> expected. Step 4 imports them.

Open the UI at **http://localhost:8080** (login `admin` / `admin`). If you
changed the webserver port (Troubleshooting), use that port instead.

### 4. Load connections + variables (host-portable)

> **Why this is a real step, not automatic.** `astro dev start` auto-imports
> a settings file, but its default is `airflow_settings.yaml` at the
> **project root** — this repo keeps it under `.airflow/`, so the default
> import finds nothing and **no connections/variables are loaded by start**.
> (Verified: `airflow variables list` is empty right after `astro dev start`.)
> Load them explicitly against the now-running stack.

**Variables — import from the settings file in one shot:**

```bash
astro dev object import -s .airflow/airflow_settings.yaml -v
```

This works in or out of an interactive shell (verified: `Airflow objects
created from settings file`). Use `-v` only: the `.example` defines no real
pools (its `pools:` block is empty placeholders, so `-p` imports nothing),
and **don't** add `-c` — the connection import attaches to the container's
TTY (fails in a non-interactive shell) and would load the file's placeholder
token anyway. Handle the connection separately, below.

**Databricks connection — from an env var, so no token is persisted in a
file.** Keep the token out of the YAML (don't import the connection with
`-c`, which would load whatever token is sitting in the file). Source it from
`DATABRICKS_TOKEN` and create the connection — **including the internal-CA
`conn_extra`** the `.example` file carries, or tasks can fail TLS against
Databricks.

`DATABRICKS_TOKEN` must already be exported in your shell — the `:?` guard
below fails loudly if it isn't, instead of silently creating an
empty-password connection. The `delete` runs first (ignoring "not found")
so this block is idempotent: it works on the first run and on every re-run
without an `already exists` error.

Replace `<your-conn-id>` with the connection ID your project's DAGs expect
(check your `.airflow/airflow_settings.yaml.example` — for
edo-ig-data-products this is `caspian-ig-databricks`).

```bash
: "${DATABRICKS_TOKEN:?DATABRICKS_TOKEN is not set}"
astro dev run connections delete <your-conn-id> 2>/dev/null || true
astro dev run connections add <your-conn-id> \
  --conn-type databricks \
  --conn-host "<your-databricks-host>" \
  --conn-password "${DATABRICKS_TOKEN}" \
  --conn-extra '{"extra__databricks__client_parameters": "{\"verify\": \"/etc/ssl/certs/ca-certificates.crt\"}"}'
```

Set `<your-databricks-host>` to your Databricks workspace URL (e.g.
`https://cg-db-caspian-ig-dev-us-east-1.cloud.databricks.com/` for the IG
dev workspace).

> **Secret tradeoff (named, not hidden):** `--conn-password` expands the
> token onto the in-container process args (briefly visible to `ps`/`/proc`
> *inside the container*) — acceptable on a single-user laptop, but it is a
> real exposure. The no-argv alternative is to define the connection as an
> `AIRFLOW_CONN_*` variable in the git-ignored `.env` (Airflow resolves
> connection env vars natively at task time, no `add` command). **Gotcha
> (verified):** if the conn_id has hyphens, the variable must use
> `AIRFLOW_CONN_<YOUR-CONN-ID>` with literal hyphens — *not underscores*; the
> underscore form silently does not resolve (e.g.
> `AIRFLOW_CONN_CASPIAN-IG-DATABRICKS`, not `…_CASPIAN_IG_DATABRICKS`).
> Give it a JSON value:
> `{"conn_type":"databricks","host":"https://…","password":"<token>","extra":{"extra__databricks__client_parameters":"{\"verify\":\"/etc/ssl/certs/ca-certificates.crt\"}"}}`.
> The token is then at rest in `.env` (git-ignored — keep it that way)
> instead of on argv. **Important:** a hyphenated env-var name can't be
> `export`ed from a POSIX shell — this method ONLY works via the `.env` file
> that the Astro CLI loads into containers. Setting it via shell export or
> any other mechanism is not possible.

**To set or tweak individual variables** (instead of the bulk import), use
`astro dev run` — it targets *this* project (resolved from the current
directory), so it's safe even with several Astro stacks up:

```bash
astro dev run variables set dev_cluster_id "XXXX-XXXXXX-XXXXXXXX"
# …repeat per variable, or loop over the settings file.
```

If you must `docker exec` directly, don't blindly `grep scheduler` — with
multiple Astro projects running (the port-conflict scenario below) that can
hit the wrong container. List **your** project's containers with
`astro dev ps` and use that exact name:

```bash
# `astro dev ps` lists only THIS project's containers:
SCHED=$(astro dev ps | awk '/scheduler/{print $1; exit}')
docker exec "$SCHED" airflow variables set dev_cluster_id "XXXX-XXXXXX-XXXXXXXX"
```

After variables change, the scheduler re-parses DAGs within a few seconds —
no restart needed.

> **Note:** these connection/variable commands require Airflow to already be
> running, which is why this step comes **after** `astro dev start`.

### 5. Verify the DAGs parsed

```bash
astro dev run dags list -o plain
astro dev run dags list-import-errors -o plain
```

(These print Airflow plugin/deprecation log lines to stdout — ignore the
`{plugins.py}` / `RemovedInAirflow3Warning` noise and read the table.)

**What you should see:** your project's dataset DAGs listed. (For
edo-ig-data-products these are `currency`, `edo_ig_index_reference`,
`edo_ig_index_summary`, etc.) These are dynamically generated DAGs.

**Expected import errors that are NOT your problem:** the
`healthchecks/*.dag.py` and `utils/autosys_scrape_calendar.dag.py` DAGs fail
with `ModuleNotFoundError: No module named 'cimon'`. These are **platform**
DAGs whose plugins (`cimon`, `scaphe`) are commented out in
`requirements.txt`, so
they cannot import locally. Ignore them — they are not the dataset DAGs you
author. If one of *your* dataset DAGs shows an import error, that's real:
check the message and Step 4 variables.

### 6. Logs / restart / stop

```bash
astro dev logs --scheduler      # or --webserver
astro dev restart               # after dependency/Dockerfile changes
astro dev stop                  # stop containers (keeps the DB volume)
astro dev kill                  # tear down including the DB volume
```

## Troubleshooting

**"The webserver health check timed out after 1m0s".** Benign. The stack
keeps booting; re-run with `astro dev start --wait 5m` and confirm with
`docker ps` / the `/health` curl.

**No DAGs / variables after start.** Expected — the settings file is under
`.airflow/`, not the project root astro auto-imports. Do Step 4. Then
`astro dev run dags list-import-errors -o plain` and `astro dev logs
--scheduler` will show any remaining (real) parse errors.

**`cannot attach stdin to a TTY-enabled container`** from
`astro dev object import -c` (the **connections** import) in a non-interactive
shell. Don't import connections from the file — create the connection with
`astro dev run connections add …` (Step 4) instead. Variable import (`-v`)
and `astro dev run …` do not have this problem.

**Port 8080 (or the DB port) already in use.** Another Astro project is
running. Check `docker ps`; either `astro dev stop` the other project, or
give this one different ports (run from the project root — writes to the
project `.astro/config.yaml`):

```bash
astro config set webserver.port 8088
astro config set postgres.port 5456
```

**`mise: command not found`.** Expected on a plain host — `mise` is only in
the dev container. Use the `astro dev …` / `docker exec … airflow …`
equivalents above instead of `mise run airflow:load-vars`.

**No DAGs at all / the dags folder looks empty inside the container.** The
mounts use `${HOST_WORKSPACE_PATH:-.}` (see Step 3). If you started without
exporting it and the mount came up empty, set it and restart:
`export HOST_WORKSPACE_PATH="$(pwd)"` (or put it in `.env`), then
`astro dev restart`.

**DQ task fails immediately with `Volume … dqf_libs does not exist`.** Only
affects *running* DQ tasks, not starting Airflow. Create the Unity Catalog
volume once in Databricks SQL:

```sql
CREATE SCHEMA IF NOT EXISTS <your_dev_catalog>.<your_short_name>;
CREATE VOLUME IF NOT EXISTS <your_dev_catalog>.<your_short_name>.dqf_libs;
```

**`astro dev start` fails pulling the base image
(`quay.io/astronomer/astro-runtime:<ver>-base`).** `quay.io` is a public
registry; on the Capital Group network public registries are blocked
(per the repo `CLAUDE.md`), so a fresh build can 404/time-out at the `FROM`
step. Options, in order:

1. Build on the dev container / a network where the base layer is reachable,
   or rely on a previously-cached base image.
2. Start from an already-built project image, skipping the build:
   `astro dev start -i <existing-astro-image>:latest`. The DAG code still
   comes from the bind-mounted `data_products/`, so this faithfully exercises
   your DAGs. (This is how this skill was validated when the base pull was
   blocked.)
3. If you own the Dockerfile, point `FROM` at the internal mirror
   (`cgregistry-aws.capgroup.com/...`) per `CLAUDE.md` — but do not change a
   repo's `Dockerfile` as a side effect of this skill without being asked.

## Out of scope

- Deploying to a hosted Astronomer Cloud deployment → use `connect-astro`
  and the Astro deploy workflow.
- Authoring DAG YAML / blueprints → use `generate-dag`.
- Building/deploying the Databricks Asset Bundle the DAGs orchestrate.

## Notes on secrets & registries

- Tokens are sourced from environment variables only; never hard-code or
  commit a Databricks token. `.airflow/airflow_settings.yaml` and `.env` are
  git-ignored — keep them that way.
- Any package/Docker artifacts this workflow touches must route through the
  internal Nexus mirrors per the repo `CLAUDE.md`; this skill runs CLI
  commands and does not add public-registry install lines.
