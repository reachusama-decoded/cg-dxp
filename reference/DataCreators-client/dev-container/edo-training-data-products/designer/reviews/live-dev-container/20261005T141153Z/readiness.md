# Session 1 readiness record, run 20261005T141153Z

Authoring dev container, Chainguard aarch64 (18 CPUs, 7.7 GiB memory, 774 GiB
free disk), 5 October 2026. After the 6 October rebuild: 15 GiB memory (`free -g`), Postgres on
`localhost:12286`. Sanitized: no tokens, hosts reduced to the
workspace ID where needed.

## Roots

| Root | Path | Check |
|---|---|---|
| `CLIENT_ROOT` | `/workspaces/edo-training-data-products` | holds `.mise.toml`, `.devcontainer/`, `scripts/challenge-v2.py`, `challenges/v2/manifest.json`; no `.git` |
| `COURSE_ROOT` | `/workspaces/ts-cg-datacreators` | `git rev-parse --show-toplevel`; `./build-pdf` builds, no CwBuilder needed |
| `TS_BUILDER_ROOT` | `/workspaces/ts-builder` | `make test pyz` passes |

All three are virtiofs bind mounts from the macOS host. The VS Code window for
this run was opened on the course-mount copy of the client
(`$COURSE_ROOT/reference/DataCreators-client/...`), not on `CLIENT_ROOT`; a
login shell started in `CLIENT_ROOT` behaves as documented.

## Starting state

- Course `93e1eb2`, clean; ts-builder `2307b3d`, clean.
- During the session the owner pushed parallel work. Course: another agent
  merged `origin/main` (`933fed3`). ts-builder: the two local commits were
  rebased onto `origin/main` `52bf171` (now `5edbb72`, `74aa711`).
- Source tree hashes at course `ab115ae` (Git tree IDs, client-relative):
  `challenges/v2` 77ca17e8, `challenges/v2-solutions` 93988bfe, `scripts`
  1a11f0b2, `tests/challenges` 381caa92, `data_products` a42c4711,
  `.devcontainer` 6abd386f; course `learner` 9b93d509, `builder.toml` aedd7d89,
  `build-pdf` 21dac199. sha256 prefixes: `manifest.json` cc730327...,
  `challenge-v2.py` e4b2c01c....

## Scope from the current manifest

`scope.tsv`: seven tools, 14 phases, **12 offered** (60 tasks, all `core`).
Not offered: `databricks-cli/phase-two-proficient`,
`kafka/phase-two-proficient`. `kafka/phase-one-certified` is offered and
optional. The manifest's `source_revision` is `working-tree`.

## Toolchain

`toolchain.txt`: Docker 29.8.2 client and server (context `default`, nested
dockerd in the privileged dev container), Compose v5.6.0, mise 2026.4.20,
Python 3.13.0 (`/opt/venv`), uv 0.11.2, dbt-core 1.11.8 with dbt-databricks
1.11.7 and dbt-spark 1.10.3, Databricks CLI 0.236.0, Astro CLI 1.46.0, Java 17,
Git 2.56.0, gh 2.102.0.

PDF toolchain (section 0):

| Tool | State |
|---|---|
| pandoc 3.1.11 | fetched by `build-pdf setup` from GitHub through the proxy (`SSL_CERT_FILE=/cacert.pem`) |
| tectonic 0.17.0 | fetched the same way; used as the engine |
| xelatex | **missing**: the Chainguard apk mirror has no TeX Live or pandoc packages |
| poppler-utils 26.10.0 | apk; now installed at post-create by the authoring config |
| Node 22.23.3, npm, chromium 153 | apk; same |
| mermaid-cli 11.17.0 | `npm ci --prefix build` via `cgnpm`; public npm returns 403 for `zod`, `stylis`, `webdriver-bidi-protocol`; Puppeteer has no arm64 Chrome, so `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium` |

`./build-pdf doctor`: "usable, 1 warning(s)" (xelatex). Candidate
`releases/261005v150929-PUB-DataCreators-v4`: 375 pages, 9 diagrams rendered
and cached, gates passed, engine tectonic.

Runtimes, measured separately:

| Runtime | Versions | Source |
|---|---|---|
| Astro local stack (`astro dev start --wait 5m`, 31 s with a cached image) | Airflow 3.1.8+astro.4, Python 3.12.13, providers databricks 7.7.4, standard 1.13.1, common-sql 1.36.0; astronomer-cosmos 1.15.0; dag-factory 1.1.0; confluent-kafka 2.15.0 | scheduler container |
| v2 dbt route (`.local/v2-tools`) | Python 3.11.15, dbt-core 1.10.13, dbt-duckdb 1.9.6, duckdb 1.4.1 | `scripts/setup-v2-tools.sh` |
| v2 Airflow/Kafka bridge (`.local/v2-airflow`) | Airflow 3.1.0, confluent-kafka 2.11.1 (as the Kafka README states) | same |
| Kafka broker | `apache/kafka:4.1.0`, pulled in 34 s; compose binds `127.0.0.1:19092` | Kafka phase 1 starter |
| Browser | Chromium 153 (apk). Playwright isn't installed; section 3 adds it as an isolated capture dependency | |

## Readiness checks

- `dpc-check` (`dpc-check.txt`): OK 41, FAIL 0, WARN 4. All four WARNs are
  Astro not running (scheduler, api-server, OAuth refresher heartbeat,
  `databricks_default` connection), expected before `astro dev start`. An
  earlier run during a VPN outage also warned on `databricks current-user me`.
- Databricks three-step check: profile valid; `auth token` mints a token
  (expiry about an hour); `DBT_ACCESS_TOKEN` is delivered to mise shells.
  Identity: the owner's account, active. No re-authentication was needed.
- `scripts/verify-with-databricks.sh` (`verify-with-databricks.txt`): exit 1
  after 110 s, PASS 35, ERROR 5. See finding F-01.
- Offline tests (`offline-tests-before.txt`, `offline-tests-after.txt`): 127
  pass in the course mount with pandoc on PATH.
- Authoring container (`authoring-container.txt`): mounts, courseware links,
  Docker-in-Docker (`hello-world`) and the pre-push hooks (dry-run blocked in
  both repositories) confirmed.
- With Astro up (`dpc-check-astro-up.txt`): OK 45, FAIL 0, WARN 0. 13 DAGs
  load with no import errors (11 `atlas_elt_*`, 2 `portfolio_analytics_*`).

## Topology

- Developer terminal and Docker daemon share the dev container; nested
  containers attach to `bridge` (172.18/16) or the Astro project network.
- Astro project `edo-training` (compose prefix `edo-training_06858d`) mounts
  `./data_products` as the DAGs folder and `$HOME/.databrickscfg` into the
  workers. Paths are resolved by the nested daemon against the dev container's
  filesystem, so a worker sees `/usr/local/airflow/dags`, never
  `/workspaces/...`. A stopped stack from about five weeks ago persists in the
  Docker volume (`edo-training-docker-data-*`); it isn't this run's.
- Forwarded ports 8020 (OAuth callback), 8080 (Airflow UI), 8081 (dbt docs),
  6563; none were listening at the time of the check.
- With Astro up: the api-server publishes `127.0.0.1:8080` (`/api/v2/monitor/health`
  200) and the Astro proxy serves `http://edo-training-data-products.localhost:6563`
  and `http://localhost:6563` (200). Postgres is on `127.0.0.1:5432`. The
  workers run as `astro` (uid 50000) and see the client's `data_products/` at
  `/usr/local/airflow/dags`; the run-scoped workspaces under `.local/` are
  **not** visible to them.
- The v2 Kafka route is separate: a compose project `v2-kafka` with the
  broker on `127.0.0.1:19092`, and its own Airflow 3.1.0 in
  `.local/v2-airflow`, not the Astro stack.

## Assigned resources

| Resource | Value | Owner |
|---|---|---|
| Databricks workspace | `cg-db-aa00003661-dev-us-east-1` | shared, training |
| Catalog / schema | `training_dev` / `training_conmhab` | assigned to this identity |
| SQL warehouse | `267dd55b7f7395ce` | shared, not resized |
| Job/DAG prefix | `[dev conmhab]` | assigned |
| Shared cluster (Airflow default) | `0723-050014-ofggyaz4` | shared, not touched |
| Git training repository | **none assigned** | the remote Git route is blocked until one is |
| Kafka broker/topics | local `apache/kafka:4.1.0`, compose project `v2-kafka`; topic prefix supplied at run time | owned when started |
| Local ports | 8080, 6563, 5432 (Astro); 19092 (Kafka, when up) | owned |

## Owned-resource ledger

| Resource | Created by | Cleanup |
|---|---|---|
| dbt objects in `training_dev.training_conmhab` (35 nodes) | `verify-with-databricks.sh` | keep; it's the assigned schema |
| apk packages poppler-utils, nodejs-22, npm, chromium | this run | container-local; rebuilt at post-create |
| `$COURSE_ROOT/build/node_modules` | `npm ci` | ignored by Git |
| `releases/261005v142240`, `261005v143103` (interrupted), `261005v150929` | `./build-pdf` | ignored by Git; owner reviews or deletes |
| `hello-world` image | Docker check | `docker image rm hello-world` |
| `apache/kafka:4.1.0` image | Kafka prerequisite | keep for section 2 |
| Astro stack `edo-training_06858d` (running) | `astro dev start` | `astro dev stop` at the end of the work |
| `.local/v2-tools`, `.local/v2-airflow`; uv Python 3.11.15 | `setup-v2-tools.sh` | ignored by Git |
| 36 journey workspaces in `.local/live/20261005T141153Z/journeys/` | `challenge-v2.py prepare` | ignored by Git; listed in `workspaces.txt` |

The working data under `.local/v2-evidence/` and `.local/live/` that predates
this run is preserved.

## Findings

- **F-01. The documented first-run gate fails on the shipped starter.**
  `scripts/verify-with-databricks.sh` runs `dbt build` over `atlas_elt`,
  whose capstone models are intentionally `select 1 as placeholder`. The
  snapshot `portfolios_snapshot` and the singular tests
  `reconcile_advisor_book_aum`, `reconcile_segment_aum`,
  `reconcile_region_aum` and `reconcile_trade_counts` then fail on missing
  columns. The repo's Copilot instructions list this script as step 3 of
  first-run validation. Decide in section 2 whether the gate should exclude
  learner-authored nodes or target a finished product.
- **F-02. No xelatex in the container.** Builds use tectonic. The engine
  decision for a promotable candidate is the owner's (devc.md section 0).
- **F-03. npm needs the internal proxy.** Recorded in the authoring config;
  on the macOS host, `make pdf-deps` still uses public npm.
- **F-04. `scripts/setup-v2-tools.sh` failed in the container.** (a) uv's
  managed Python 3.11 download is cut off through the proxy (rustls
  "peer closed connection"); curl fetches the same file, and
  `UV_PYTHON_INSTALL_MIRROR=file://...` installs it. The apk `python-3.11`
  conflicts with the image's Python 3.13. (b) uv ignores `/etc/pip.conf`, and
  public PyPI returns 403 for the `dill` sdist. Repaired: the script now
  exports `UV_DEFAULT_INDEX` from the global pip config when unset; a clean
  rerun passes in 20 s. (a) is repaired too: when uv's install fails, the
  script fetches the same build from GitHub with curl (the
  `releases.astral.sh` copy truncates, then returns 403 on resume) into
  `.local/python-mirror` and installs it with `UV_PYTHON_INSTALL_MIRROR`.
  From nothing (uv's Python 3.11 uninstalled, both environments removed) the
  script passes in 99 s with `UV_HTTP_RETRIES=0`; with uv's default retries
  the failing download alone takes about 12 minutes.
- **F-05. Two Airflow versions.** The Astro stack runs 3.1.8 with
  confluent-kafka 2.15.0; the Kafka route's isolated runtime is 3.1.0 with
  2.11.1, as its README says. Keep their evidence separate in section 2.
