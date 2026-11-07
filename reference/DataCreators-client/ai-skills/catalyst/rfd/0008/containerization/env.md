# CONT-ENV: Environment

Environment-variable handling inside containerized development environments:
persisting normalized values for every shell, normalizing quoted input, and
keeping per-repo differences in configuration rather than script logic.

## CONT-ENV-001 — Persist normalized environment to /etc/profile.d for all shells

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + shellcheck

**Decision.** Environment values computed during setup (normalized Databricks
credentials, derived host paths) must be written to a profile script under
`/etc/profile.d/` (or a documented user-owned fallback) so every login shell
sources them. Do not rely on an `export` inside a single task subshell.

**Why.** A value `export`ed inside a mise/poe task exists only for that task's
subshell. A plain terminal, an editor task that bypasses the task runner, and the
dbt / Databricks CLI then see the un-normalized (or absent) value. Persisting to
`/etc/profile.d/` makes behavior identical no matter how the shell was started.

**Exception.** Values that are genuinely scoped to a single command invocation.

**Examples.**
```sh
# ✗ — visible only inside this task's subshell
export DATABRICKS_HOST="$clean_host"

# ✓ — persisted so every shell and process sees it. The heredoc is deliberately
#     unquoted (<<EOF, not <<'EOF') so ${clean_host} expands once at write time
#     and the resolved value is baked into the profile script
cat > /etc/profile.d/databricks-env.sh <<EOF
export DATABRICKS_HOST="${clean_host}"
EOF
chmod 644 /etc/profile.d/databricks-env.sh
```

## CONT-ENV-002 — Normalize quoted environment values once during setup

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory + shellcheck

**Decision.** A single setup step strips a surrounding layer of single or double
quotes from environment values sourced from `.env` files, then persists the clean
values (see `CONT-ENV-001`). Downstream scripts and tasks consume the normalized
values and must not re-strip.

**Why.** Users optionally quote values in `.env` (`DATABRICKS_HOST="https://..."`).
Some tools read the raw value and break on the embedded quotes. Normalizing once,
centrally, removes a class of intermittent failures instead of scattering
quote-stripping through every consumer.

**Exception.** None.

**Examples.**
```sh
# ✓ — strip one layer of surrounding quotes, once, for a known key set
strip_quotes() { printf '%s' "$1" | sed "s/^['\"]//;s/['\"]\$//"; }
clean="$(strip_quotes "$raw")"
```

## CONT-ENV-003 — Per-repo differences live in env/config metadata, not script logic

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Repository-specific values — product name, dbt profiles directory,
catalyst mount path, catalog — are expressed as variables in `.env`, container
environment metadata such as `remoteEnv` or Compose `environment`, or the
task-runner `[env]` block. The vended setup scripts read those variables and
must be byte-for-byte identical across repos.

**Why.** When a repo encodes its differences by editing the shared scripts, the
scripts fork. Forked scripts cannot be re-vended or centrally patched, and the
next platform update silently diverges. Parameterizing keeps one canonical script
set and isolates per-repo data to configuration.

**Exception.** None.

**Examples.**
```jsonc
// ✓ — the repo's identity is data, not a script edit. Each value is set
//     literally: remoteEnv entries are not guaranteed to resolve references to
//     sibling remoteEnv keys, so DBT_PROFILES_DIR does not interpolate DBT_PRODUCT
"remoteEnv": {
  "DBT_PRODUCT": "my_data_product",
  "DBT_PROFILES_DIR": "/workspace/data_products/my_data_product/dbt_profiles"
}
```
```dockerfile
# ✓ — production runtime image: one shared Dockerfile across images; the
#     registry/environment difference is a build ARG, not a fork
ARG repo
FROM ${repo}pyspark-base:5.2.0-a2
# built per environment with:  docker build --build-arg repo=<registry>/ .
```
