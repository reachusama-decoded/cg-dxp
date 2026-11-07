# Databricks Authentication Strategy (Repo-Wide) — Design

Status: Proposed
Date: 2026-07-21
Supersedes: `2026-07-21-airflow-databricks-oauth-multi-workspace-design.md` (its multi-workspace
registry/control-plane is deferred to "Future scope" below; this document generalizes the goal to
all Databricks auth surfaces in the repo for a single workspace).

## 1. Goal

Provide one coherent way to authenticate to Databricks from every surface in this repo — local dbt,
local Airflow (Astro), and Databricks Asset Bundles (DAB) deployed/run from the local CLI — so a
learner authenticates once and every surface works, with a reliable fallback when the primary path
fails.

## 2. Core Decision: Two Mutually-Exclusive Modes

The repo supports exactly two authentication modes, and exactly one is active at a time:

- **OAuth (primary, default):** Databricks user-to-machine (U2M) OAuth. A single browser login.
- **PAT (backup / break-glass):** a Databricks personal access token, used when OAuth is unavailable
  or the OAuth→Airflow refresh path is broken and a learner must be unblocked quickly.

There is no mixed state. When a learner is in OAuth mode, *all three surfaces* use OAuth; when in PAT
mode, all three use the PAT. This is deliberate: mixing auth types across surfaces makes failures
hard to diagnose, because a learner cannot reason about which credential a given error came from.
Keeping the whole system on one credential type means "what am I authenticated as?" always has one
answer.

The single source of truth is `DPC_DATABRICKS_AUTH_MODE` (values: `oauth` | `pat`) in
`~/.config/dpc/databricks.env`. Every surface and the refresher read this one value.

## 3. Decision Framework

The choice of OAuth-primary / PAT-backup is not a preference; it is derived from a weighted
evaluation against the project's stated priorities, in order: (1) lowest onboarding friction for a
mixed-skill training audience, (2) security posture / parity with Databricks guidance, (3)
reliability for long-running local Airflow.

| Criterion (weight) | OAuth U2M | PAT | Evidence |
|---|---|---|---|
| Onboarding friction (high) | One browser login, no secret to create/copy/store | Manual token creation in the UI, copy/paste, store | DAB attended guidance recommends U2M for local dev |
| Ongoing friction (high) | Auto-refresh for dbt + DAB; Airflow needs a refresher (platform-owned) | None (long-lived) | Unified auth auto-refreshes access tokens |
| Security posture (medium) | Recommended; short-lived | "Legacy"; 730-day default max, weaker | Databricks labels PAT "(legacy)" and recommends migrating to OAuth |
| Airflow fit (medium) | No native U2M path in the provider → requires a bridge | Works directly (token in connection) | Airflow provider hook supports PAT / M2M / Azure / OIDC only |

**Outcome:** OAuth wins on the two highest-weighted criteria (onboarding + ongoing friction for
dbt/DAB) and on security posture. Its single weakness — no native U2M path in the Airflow provider —
is a bounded, platform-engineer-owned problem (the refresher, Section 6). PAT wins only on "works
directly in Airflow" and long-lived simplicity, which is exactly the property that makes it the right
*backup*: zero moving parts when the OAuth path is down.

**Machine-to-machine (M2M) service principal is explicitly deferred, not chosen.** M2M is the
Databricks-recommended path for unattended/production orchestration and would authenticate all three
surfaces natively (including Airflow, via `service_principal_oauth`). It is rejected for this repo's
current goal because it requires provisioning a service principal and distributing a `client_secret`
per learner — high onboarding friction that contradicts priority (1). It is recorded as the intended
production/CI direction in "Future scope."

### Evidence sources

- Databricks unified client authentication (credential precedence; access token auto-refresh):
  https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth
- OAuth U2M (access token lifetime = 3600s; refresh handled by SDK/CLI):
  https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m
- PAT "(legacy)", 730-day default, 90-day inactivity revoke, "migrate to OAuth":
  https://docs.databricks.com/aws/en/dev-tools/auth/pat ,
  https://docs.databricks.com/aws/en/admin/access-control/tokens
- DAB authentication (U2M recommended for attended/local; M2M then PAT for unattended):
  https://docs.databricks.com/aws/en/dev-tools/bundles/authentication
- Airflow Databricks provider supported auth (PAT / M2M / Azure / OIDC; no U2M; ignores
  `~/.databrickscfg`): `apache/airflow` `providers/databricks/.../hooks/databricks_base.py`
  `_get_token` (SHA `ad48f09a9360b1afa10313ef95215f8285ffe6a6`)
- dbt-databricks supported auth (`token` PAT, `auth_type: oauth` U2M, `client_id`/`client_secret`
  M2M): `databricks/dbt-databricks` `dbt/adapters/databricks/credentials.py`
  (SHA `0085d576548c4676a302d462d77ea6d8e2986714`)
- CLI ≥ 1.0.0 relocates U2M session to OS-native secure storage:
  https://docs.databricks.com/aws/en/dev-tools/cli/authentication

## 4. Per-Surface Behavior

The mode changes *only how a token is sourced*; surface configuration stays uniform so learners see
one shape regardless of mode.

### 4.1 Local dbt (`data_products/*/dbt_profiles/profiles.yml`)

No profile change. Profiles keep reading a bearer token from `DBT_ACCESS_TOKEN` / `DATABRICKS_TOKEN`.
The mode determines what fills those variables:

- **OAuth:** `.mise/env.sh` mints a short-lived U2M access token via
  `databricks auth token --profile DEFAULT` on shell start and exports it. Already implemented.
- **PAT:** the PAT is exported into the same variables by the mode contract.

Rationale for keeping `token:` (rather than switching profiles to `auth_type: oauth`): a single
profile shape works for both modes, so switching modes never edits `profiles.yml`. This keeps the
mode switch to one place (the contract) and avoids per-mode profile variants.

### 4.2 DAB local (`data_products/*/databricks.yml` + `databricks bundle …`)

DAB is invoked directly with the CLI (e.g. `databricks bundle validate|deploy|run -t local|dev`, as
documented in `data_products/shared_ref/datasets/currency/cspn_migration.md`; there are no mise
wrapper tasks). It resolves credentials through Databricks unified auth (env vars → `DEFAULT`
profile).

- **OAuth:** the `DEFAULT` profile's U2M session is used and auto-refreshed by the CLI; no token is
  handled manually. Bundle targets already set `host`, so profile/default resolution applies.
- **PAT:** `DATABRICKS_TOKEN` in the shell (exported by the contract) takes precedence per unified
  auth ordering, so the same commands work unchanged.

No change to `databricks.yml` is required; this surface works in both modes via unified auth.

### 4.3 Local Airflow (Astro; connections `databricks_default`, `caspian-training-databricks`)

Note: In OAuth mode, `airflow_settings.yaml` is intended as a bootstrap shape only (host + empty login). Live OAuth access tokens are written to the Airflow metastore connections by the OAuth refresher and are not persisted to `airflow_settings.yaml` or other local settings files.

The `apache-airflow-providers-databricks` hook authenticates *only* from Airflow Connection fields —
it has no U2M code path and does not read `~/.databrickscfg`. Therefore a token must live in the
connection.

**Prerequisite: the local secrets backend must be `MetastoreBackend` (empirically verified).** Before
the connection shape even matters, the hook must be able to *find* the connection. In this repo that
was silently broken. The Astro base image defaults the secrets backend to **AWS Secrets Manager**
(`airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend`), and the tracked root
`.env` (a rendered dev1 deployment config that `astro dev` loads for local dev) supplies its AWS
kwargs. To escape that, `docker-compose.override.yml` had set the backend to
`EnvironmentVariablesBackend` — but that **drops the metastore from the search path**, so every
DB-stored connection (imported from `airflow_settings.yaml`, or written by `airflow connections add`)
is invisible to hooks/operators. Verified across a real `astro dev restart`:

| `docker-compose.override.yml` secrets backend | Effective backend | Hook resolving a DB connection |
|---|---|---|
| `EnvironmentVariablesBackend` (prior) | env vars only | `(False, "conn isn't defined")` |
| removed (falls back to image default) | AWS Secrets Manager | `(False, "conn isn't defined")` |
| `airflow.secrets.metastore.MetastoreBackend` | metastore | `(True, 'Connection successfully tested')` |

Therefore the design **sets** `AIRFLOW__SECRETS__BACKEND: "airflow.secrets.metastore.MetastoreBackend"`
in `docker-compose.override.yml` (it wins over the root `.env`, confirmed after restart).
`MetastoreBackend` is fully local, keeps the stack off AWS Secrets Manager, and makes DB connections
resolve — which is what lets the refresher's `airflow connections add` (Section 6) actually take
effect. Note: removing the override is **not** a valid fix (it re-exposes the AWS Secrets Manager
default). This also fixes a latent bug: with the prior backend, **no** Databricks operator/hook could
authenticate against these connections at all.

**Critical connection-shape requirement (empirically verified).** How the provider transmits the
token depends on the connection's `login` field (`databricks_base.py` `_do_api_call`): when `login`
is **empty** (or the token is placed in `extra.token`), the hook sends `Authorization: Bearer
<token>`; when `login` is **non-empty** (e.g. the legacy `login: 'token'`), the hook falls back to
**HTTP Basic** auth (`HTTPBasicAuth(login, password)`). A Databricks **OAuth** access token is only
accepted as `Bearer`; it is rejected over HTTP Basic. This was proven against the live workspace with
provider 7.7.4 and a real U2M token minted from the OAuth session, using `DatabricksHook.test_connection()`:

| Connection shape | Transport | Result |
|---|---|---|
| `login: 'token'`, `password: <oauth>` (repo's prior shape) | HTTP Basic | **401 Unauthorized** |
| empty `login`, `password: <oauth>` | Bearer | **Connection successfully tested** |
| `extra: {"token": <oauth>}` | Bearer | **Connection successfully tested** |

Therefore, for OAuth the connections **must** be written with an **empty `login`** and the token in
`password` (Bearer shape). A PAT is also a bearer token and works over the same Bearer shape, so this
shape is used for **both** modes — removing any per-mode transport difference. (This corrects the
prior `conn_login: 'token'` template, which only worked because PATs tolerate HTTP Basic.)

**How this was verified (reproducible).** In the running devcontainer, with an active OAuth session:

1. Mint a real U2M access token from the OAuth session (non-interactive; no browser):
   `databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json` → take
   `.access_token`. Observed a ~870-char JWT (OAuth), versus a ~40-char `dapi…` string for a PAT.
2. Discover the running Astro scheduler container:
   `docker ps --format '{{.Names}}' | grep -E '^edo-training.*-scheduler-1$'`.
3. Inside the scheduler, exercise the **real provider hook** (not curl) for each connection shape:
   ```python
   import os, json
   from airflow.models import Connection
   from airflow.providers.databricks.hooks.databricks import DatabricksHook
   def probe(label, **kw):
       c = Connection(conn_id="probe", conn_type="databricks", host=HOST, **kw)
       os.environ["AIRFLOW_CONN_PROBE"] = c.get_uri()
       print(label, DatabricksHook(databricks_conn_id="probe").test_connection())
   probe("A login=token", login="token", password=TOKEN)   # -> (False, '... 401 Unauthorized')
   probe("B empty login", login="",      password=TOKEN)   # -> (True, 'Connection successfully tested')
   probe("C extra.token", extra=json.dumps({"token": TOKEN}))  # -> (True, 'Connection successfully tested')
   ```
   `DatabricksHook.test_connection()` calls the `/api/2.0/clusters/spark-versions` endpoint through the
   provider's own auth path, so the result reflects exactly how a real operator/hook would authenticate.

**Why the shapes differ (installed-source evidence, provider 7.7.4).** In
`airflow/providers/databricks/hooks/databricks_base.py`:
- `_get_token()` returns the connection password as the bearer token **only when `login` is empty**:
  `if not self.databricks_conn.login and self.databricks_conn.password:` (line 586). A non-empty login
  (e.g. `'token'`) makes `_get_token()` return `None` for a plain token connection.
- `_do_api_call()` then chooses the transport: `if token: auth = _TokenAuth(token)` (line 678) else
  `auth = HTTPBasicAuth(self.databricks_conn.login, self.databricks_conn.password)` (line 681).
- `_TokenAuth.__call__` sets `r.headers["Authorization"] = "Bearer " + self.token` (line ~833).

So empty login → `_TokenAuth` → `Authorization: Bearer`; non-empty login → `HTTPBasicAuth`. An OAuth
access token is a bearer credential and is rejected over HTTP Basic (401), which is exactly what the
probe shows.

**Documentation support.**
- Airflow Databricks provider connection docs recommend putting the token in the **Password field**
  ("Consider to switch to specification of PAT in the Password field as it's more secure"):
  https://airflow.apache.org/docs/apache-airflow-providers-databricks/stable/connections/databricks.html
- Databricks OAuth U2M access tokens are bearer tokens presented as `Authorization: Bearer <token>`
  against the REST API: https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m and
  https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth

- **PAT:** `.devcontainer/utils/setup-airflow-settings.sh` injects the long-lived PAT into both
  connection passwords once at setup (Bearer shape, empty login). No refresh needed.
- **OAuth:** the connection password is a short-lived U2M token that must be kept fresh by the
  **refresher** (Section 6), also written in the Bearer shape.

**Note on the dpc-academy pattern (dbt-only alternative).** The `dpc-academy` repo avoids the
connection-auth question entirely: its Airflow tasks shell out to `dbt` (profile `auth_type: oauth`),
which delegates to the Databricks SDK, which reads the OAuth session from the mounted `~/.databrickscfg`
(`DATABRICKS_CONFIG_FILE`) and auto-refreshes it. That works for **dbt tasks only**. Because this
repo's goal explicitly includes arbitrary Databricks operators/hooks (e.g. `DatabricksSubmitRunOperator`)
— not just dbt — the connection must carry a working token, so the Bearer-shape refresher above is
required for the general case. The mounted-`.databrickscfg` path still covers dbt tasks for free and
is complementary, not a replacement.


## 5. Topology Constraint (Why the Refresher Lives in the Devcontainer)

The devcontainer runs docker-in-docker (`--privileged`, inner `dockerd` via
`.devcontainer/ensure-dockerd.sh`, `/var/lib/docker` on a named volume). Astro's containers are
children of the **inner** daemon, so their bind mounts (`$HOME/.databrickscfg`) resolve against the
devcontainer's own Linux filesystem — not the Mac/Windows host. Consequences:

- Host OS filesystem quirks (path translation, CRLF, permissions) do not affect the mounted config;
  the only genuine host touchpoint is the browser OAuth callback on `127.0.0.1:8020`, which VS Code
  port-forwards identically on Mac and Windows (and `setup-databricks-dbt.sh` already frees the
  port).
- `databricks auth login` runs in the devcontainer, so the OAuth **session/refresh token** exists
  there. Minting fresh access tokens must happen where that session lives.

This is why minting runs in the devcontainer (Section 6) rather than inside an Astro worker: it keeps
the refresh token in one place, and it survives the CLI ≥ 1.0.0 change that relocates the session
from a mountable plaintext file (`~/.databricks/token-cache.json`) into per-container OS secure
storage (which a separate worker container cannot read). A worker-side minting design would break on
that upgrade unless pinned to legacy plaintext storage and given the refresh token via mount.

## 6. Component: OAuth → Airflow Refresher (Bridge B)

A new devcontainer-side component keeps the Airflow connections' OAuth token fresh. It is the only
net-new moving part.

**Artifact:** `.devcontainer/utils/databricks-oauth-refresh.sh` (invoked directly and as a loop).

**Trigger paths for setup wiring (`.devcontainer/utils/setup-airflow-settings.sh`):**
- **Automatic during Databricks setup:** `.devcontainer/setup-databricks-dbt.sh` invokes
  `setup_airflow_databricks_connections` at the end of both OAuth and PAT flows, so connection wiring
  happens in the same setup run.
- **Task entrypoint:** `mise run setup:airflow-settings` runs the same script and is configured to
  depend on `setup:databricks` (renamed from `setup:databricks-oauth`), so it can be rerun as a one-command recovery flow.
- **Direct/manual:** the script can be invoked directly (`bash .devcontainer/utils/setup-airflow-settings.sh`)
  to re-render `airflow_settings.yaml` and restart the OAuth refresher hook.

**Behavior (one pass):**
1. Source `~/.config/dpc/databricks.env`. If `DPC_DATABRICKS_AUTH_MODE` != `oauth`, exit 0
   immediately (no-op in PAT mode — the PAT is static and needs no refresh).
2. Mint a fresh access token: `databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST"`
   (auto-refreshes from the cached session; no browser prompt within the refresh window).
3. Upsert the token into each target connection by exec-ing the Astro scheduler container and running
   the Airflow CLI: `airflow connections delete <id>` then `airflow connections add <id>
   --conn-json '{"conn_type":"databricks","host":"<host>","login":"","password":"<token>"}'`,
   for `databricks_default` and `caspian-training-databricks`. The **empty `login`** is required
   (Bearer shape, per Section 4.3); a non-empty login downgrades to HTTP Basic and rejects the
   OAuth token. Rationale for using the CLI: it writes the metadata DB directly and needs no REST
   credentials; the devcontainer already controls the inner dockerd, so it can exec into the
   scheduler. (Airflow stable REST API on `localhost:8080` is the documented fallback.)
4. Write a heartbeat (last-refresh timestamp + token `exp`) to a known path
   (`~/.config/dpc/oauth-refresh-status.json`) and append to a log
   (`/var/log/dbx-oauth-refresh.log`).

**Bootstrap vs rotation responsibilities (operational clarity):**
- **Bootstrap (initial/default wiring):** Databricks setup must provision Airflow connection state
  immediately (template + settings import path), even before Airflow is running.
- **Rotation (ongoing freshness):** the refresher maintains token freshness for already-provisioned
  connections once the scheduler exists.
- If Airflow is down during setup, this is still valid: desired connection state is written first, and
  the refresher reports `scheduler_down` and retries until the scheduler appears. The refresher is not a
  substitute for bootstrap; it is the steady-state maintainer.
- Bootstrap must also be **non-destructive**: if no fresh token is currently mintable, setup must keep
  existing working connection credentials rather than rewriting them to blank values.
- Bootstrap must propagate token values across process boundaries: if setup mints an OAuth token in the
  shell, that value must be exported to the Python renderer before it rewrites
  `airflow_settings.yaml`. Otherwise setup can report "wrote short-lived token" while silently leaving a
  stale PAT in the file (observed in this repo before the export fix).

**Scheduling & lifecycle (expiry-driven, not fixed-interval):**
- Runs once at setup and once after `astro dev start` for immediate freshness.
- Then loops **expiry-driven**: each iteration reads the current access token's `exp`, sleeps until
  `exp - lead` (lead ≈ 120s, matching the provider's `TOKEN_REFRESH_LEAD_TIME`), then mints and
  upserts. Because U2M access tokens live exactly 3600s, this settles into refreshing roughly hourly,
  right before expiry — the connection token is proactively replaced and is never stale, with no
  wasteful fixed-interval polling. The `exp` is re-read every iteration so laptop sleep/clock jumps
  self-correct on the next wake.
- On a mint failure, retry with short backoff (a few attempts); if minting still fails, stop looping
  and record the failure to the heartbeat/log so `dpc-check` can surface it (see below). It does
  **not** fall back to a browser (see "Browser behavior").
- Runs as a background loop (`nohup`), mirroring the existing `ensure-dockerd.sh` `nohup` pattern.
- Single-instance guard via a pidfile; opt-out via an env var (e.g. `DPC_SKIP_OAUTH_REFRESH`),
  consistent with `DPC_SKIP_DOCKERD_HEAL`.

**Browser behavior (never surprise the user):** the refresher only ever calls the *non-interactive*
`databricks auth token`, which mints a new access token silently from the cached **refresh token** —
no browser. A browser is launched **only** by the *interactive* OAuth login, which the refresher never
calls. So the normal ~hourly refresh is invisible. If the refresh token/session itself has expired or
consent was revoked, `databricks auth token` **fails with an error** (it does not pop a browser from a
background loop); the refresher records the failure and `dpc-check` tells the learner to re-run the
OAuth setup entrypoint — `mise run setup:databricks` (renamed from `setup:databricks-oauth`; i.e. `.devcontainer/setup-databricks-dbt.sh`
**without** `--pat`) — which performs the browser login *and* rewrites the OAuth env contract so every
surface stays consistent. (Raw `databricks auth login` would restore only the session, not the
contract, so it is not the documented remediation.) This guarantees a background process never hijacks
the learner's screen with a login window.

**Health surfacing (`dpc-check`):** `dpc-check` reports the active mode and, in OAuth mode, whether
the refresher heartbeat is recent and the connection token is present and unexpired. On staleness or a
recorded mint failure it prints concrete remediation: re-run the OAuth setup entrypoint
`mise run setup:databricks` (renamed from `setup:databricks-oauth`; i.e. `.devcontainer/setup-databricks-dbt.sh` without `--pat`), or
switch to the PAT backup with `.devcontainer/setup-databricks-dbt.sh --pat`. This keeps "one place to
debug" = run `dpc-check`.

### Re-authentication frequency (how often a learner sees a browser)

- **Access token (1 hour):** refreshed silently by the loop via `databricks auth token` — **never a
  browser**. The CLI/SDK itself proactively refreshes within ~5 minutes of expiry.
- **Refresh token / OAuth session:** the browser reappears only when this expires or consent is
  revoked. **Databricks does not publish a numeric lifetime for the U2M refresh token, and there is
  no account-level setting that controls it** — it is enforced server-side and is not knowable by the
  client in advance (the SDK stores whatever refresh token the server last returned and only learns
  of expiry when the server rejects it). Because the value is unpublished, this design does **not**
  predict refresh-token expiry; it **detects** it: when `databricks auth token` fails with
  "refresh token is invalid," the refresher records the failure and `dpc-check` tells the learner to
  re-run the OAuth setup entrypoint (`mise run setup:databricks`, renamed from `setup:databricks-oauth`; i.e.
  `.devcontainer/setup-databricks-dbt.sh` without `--pat`), which wraps the browser login and re-syncs
  the OAuth env contract. That re-login is the *only* moment a browser appears, and PAT backup covers
  any moment that is inconvenient.

Evidence: the U2M docs state only the access token's `expires_in: 3600` with no refresh-token lifetime
field; the PAT-only `maxTokenLifetimeDays` admin setting has no OAuth equivalent; and the CLI defines
`databricks auth token` as a cache-only refresh that "only works with U2M authentication" and emits a
"run `databricks auth login`" error (never a browser) when the refresh token is invalid. See the
evidence sources in Section 3 plus `databricks/cli` `cmd/auth/token.go` and `databricks/databricks-sdk-go`
`credentials/u2m/persistent_auth.go` (proactive-refresh buffer = 5 min; `InvalidRefreshTokenError`).

## 7. Mid-Run Expiry and the Backup

Between refreshes the injected OAuth token is static, so an Airflow operation that polls or runs
longer than the remaining token lifetime can receive a 401/403 until the next refresh. Mitigations:
the loop refreshes proactively ~120s before each expiry, keeping a fresh token in the connection;
Databricks provider operators submit server-side jobs and Airflow only polls with the connection token
(each poll re-reads the connection, which the refresher keeps current). Residual risk remains only for
a single operation that both holds one token for its entire duration and spans the ~hourly refresh
boundary.

This residual risk is the reason PAT exists as a first-class backup: `--pat` yields a long-lived
token on every surface with no refresher dependency, unblocking a learner immediately if the OAuth
path misbehaves.

## 8. Idempotency and Mode Switching

- `DPC_DATABRICKS_AUTH_MODE` is authoritative; setup writes exactly one mode.
- Re-running setup in the same mode is idempotent (it rewrites the same artifacts).
- Switching modes rewrites the contract and reconfigures all three surfaces coherently; the refresher
  self-gates on the mode, so no stale mixed state can persist. Switching requires re-running setup
  (`--oauth` or `--pat`); Airflow picks up new connection values on the next refresher pass (OAuth) or
  at the next `astro dev` connection import (PAT).
- The earlier concern that "OAuth setup must preserve a PAT for Airflow" is dissolved: in OAuth mode
  Airflow uses OAuth via the refresher, so no PAT needs to coexist. One mode, one credential type.

## 9. Testing Strategy

TDD, extending `data_products/test_devcontainer_dind_wiring.py` (script-content and behavior tests)
plus the live gate `scripts/verify-with-databricks.sh`.

- **Mode contract:** setup writes exactly one `DPC_DATABRICKS_AUTH_MODE`; OAuth mode persists no
  long-lived token; PAT mode validates the token before writing config (existing REST `/Me` probe).
- **Refresher:** no-op when mode=pat; constructs the correct `databricks auth token` invocation;
  upserts both connection IDs; writes the heartbeat; honors the single-instance guard and the opt-out
  env var.
- **dpc-check:** reports mode; warns when the OAuth refresher heartbeat is stale/missing or the
  connection token is expired; prints the documented remediation.
- **Airflow settings:** OAuth vs PAT produce the correct connection-password source, including stale-state
  edge cases: setup preserves existing credentials when no fresh token is available, rewrites stale PAT
  values to a freshly minted OAuth token when minting succeeds, and rewrites stale values to the PAT from
  `~/.databrickscfg` when mode=`pat`.
- **Idempotency/switching:** re-running the same mode is stable; switching flips all surfaces with no
  residual mixed state.
- **Live gate (both modes):** OAuth — after login, the refresher yields a working connection token, a
  minimal Databricks provider call succeeds, local dbt runs, and `databricks bundle validate`
  succeeds. PAT — the same surfaces succeed with the PAT.
- **Cross-platform:** Windows cannot be automated here; document a manual check that the browser
  callback and `astro dev start` refresh path work on a Windows host.

## 10. Scope and Non-Goals (YAGNI)

- **In scope:** single Databricks workspace; OAuth-primary + PAT-backup across dbt, DAB, Airflow; the
  devcontainer refresher; idempotent mode switching; `dpc-check` health.
- **Non-goals now:** the Airflow provider is not patched; no file-watcher sidecar; no per-mode
  `profiles.yml` variants.

## 11. Future Scope

- **Multi-workspace:** reintroduce a workspace registry (`workspace_key → conn_id + host + profile`)
  and per-connection refresh when more than one workspace is needed (from the superseded
  multi-workspace design).
- **M2M service principal for unattended/CI:** adopt `service_principal_oauth` for Airflow and
  `client_id`/`client_secret` for dbt/DAB in automated environments, per Databricks' unattended
  guidance.
- **CLI ≥ 1.0.0 adoption:** when the pinned `databricks-cli` is upgraded, set
  `DATABRICKS_AUTH_STORAGE=plaintext` in the devcontainer if OS secure storage is unavailable there;
  because minting is co-located with login (Section 5), this stays contained to the devcontainer.
