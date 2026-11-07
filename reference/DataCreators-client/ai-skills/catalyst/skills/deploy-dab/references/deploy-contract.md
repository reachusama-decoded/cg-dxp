# deploy-dab — local deploy contract

`deploy-dab` deploys the Databricks Asset Bundle for **one data product** to the
developer's `local` target and reports the deployed assets. Scope is a single
data product per run (one `data_products/<product>/` bundle), matching
`setup-databricks-asset-bundle` (DBX-BUNDLE-002). It is `local`-only;
shared/prod deploys are CI/CD's job.

## Flow

1. **Precursor** — `databricks.yml` exists, has a `local` target with a
   `target_schema` variable, and at least one `datasets/**/bundle/*.job.yml`
   resource. Else exit 2.
2. **Auth** — the Databricks CLI must be installed and authenticated
   (`databricks auth env`). Else exit 4. Local auth is **U2M (user-to-machine)
   OAuth**: the developer logs in as themselves with
   `databricks auth login --host <host>` (or selects a matching named
   `~/.databrickscfg` profile). This is required because the `local` target
   deploys into the developer's own per-user dev schema —
   `${workspace.current_user.short_name}` resolves the *real user's* identity via
   `/scim/v2/Me`, which a service principal would not satisfy. **M2M
   client-credentials** (`/connect-databricks`; PAT rejected there) is the
   CI/shared-deploy path, not the local one. A missing CLI binary also maps to
   exit 4.
   The gate is **host-aware**: when the `local` target declares a literal
   `workspace.host`, the check probes `databricks auth env --host <host>` so a
   named OAuth profile in `~/.databrickscfg` resolves the same way
   `databricks bundle deploy` resolves it. Bare `auth env` only sees the DEFAULT profile
   (it ignores `DATABRICKS_CONFIG_PROFILE` and named profiles), which would
   false-negative the common setup where only named profiles exist. It falls
   back to the bare check when no literal host is present.
   Because the `local` target resolves
   `${workspace.current_user.short_name}` via `/scim/v2/Me`, a configured but
   stale/invalid token passes the `auth env` gate yet fails at `validate` with a
   403 — that auth signature is detected and also mapped to exit 4 (not 5).
3. **Schema confirmation** — the `local` target's `target_schema` (per-user,
   e.g. `${workspace.current_user.short_name}`) must be confirmed before a real
   deploy: either a stored confirmation matches, or `--confirmed-schema
   '<schema>'` (one-shot) equals the resolved schema. Otherwise exit 2.
   `--dry-run` is exempt (validate only, no deploy).
4. **Validate → deploy** — `databricks bundle validate --target local` then
   `databricks bundle deploy --target local`. Either failure → exit 5.
5. **Asset links** — `databricks bundle summary --target local --output json` (stdout only)
   is parsed into a list of `[type] name: url` lines. A non-zero rc or
   unparseable output never fails the deploy — it falls back to a "deployed
   (could not read/parse summary)" message at exit 0.

## Teardown gate (`--mode destroy`)

Teardown is a **deterministic, gated actuator mode**, not an ad-hoc body command,
so the *list → confirm → destroy* guarantee and the `local`-only scope are
enforced in code rather than prose:

- **Hardcoded target.** Every CLI call uses `--target local`; the mode has no
  parameter to select another target, so it cannot be steered at `dev`/`sqa`/`prd`.
- **List first.** It always runs `databricks bundle summary --target local
  --output json`, prints the resource inventory (redacted), so the user sees what
  would be removed. If that summary call fails, destroy **aborts before any
  confirmation gate** — auth failure → exit 4, any other failure (non-zero rc or
  unparseable output) → exit 5 — so a destroy never proceeds without a reviewable
  inventory, even when `--confirm-destroy` was already supplied.
- **Explicit confirmation.** Destroy runs only when `--confirm-destroy '<schema>'`
  equals the resolved per-user `target_schema`. Unlike deploy there is **no
  stored-confirmation bypass** — every destroy requires the one-shot flag.
  Unconfirmed / mismatch → exit 2 (after listing).
- **Destroy.** `databricks bundle destroy --target local --auto-approve`
  (`--auto-approve` is required because the actuator runs non-interactively).
  Auth failure → exit 4; other failure → exit 5; success → exit 0.

### Testing the teardown gate

The teardown gate is verified by the actuator's unit tests
(`scripts/test_deploy.py` — local-only, unconfirmed-blocks, schema-mismatch,
listing-redaction, exit codes) and by the real-workspace deploy → destroy E2E.
It is **out of scope for the behavior-test harness (`bin/bt`)**: bt drives a
skill end-to-end through Claude with no human in the loop and a "produce the full
artifact" preamble, which always elicits the *primary* (deploy) flow and cannot
be steered into a secondary actuator mode like destroy. `bin/bt` therefore only
exercises the deploy *trigger* (`case-01-happy-path`); the destroy guarantees
live in the unit + E2E layers above.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | deployed/destroyed (or `--dry-run` validated) |
| 2 | input/config — precursor missing, schema absent, or deploy/destroy not confirmed |
| 4 | auth — CLI not authenticated, not installed, or a validate/deploy/summary/destroy call hit a workspace auth error |
| 5 | runtime — a `databricks bundle validate`/`deploy`/`summary`/`destroy` call failed for a non-auth reason (includes the destroy pre-list `bundle summary` failing) |

## Preferences file

`<repo-root>/.claude/markers/deploy-dab.user-preferences` (JSON, gitignored via
`.claude/markers/`), read/written only by `deploy.py`:

```json
{ "schema_confirmations": { "<repo-relative-bundle-path>": { "schema": "<value>", "confirmed": true } } }
```

Confirmations are keyed by the **repo-relative bundle path** (e.g.
`data_products/sales`), not the bundle name, so two products that share a
`bundle.name` do not share a confirmation. A confirmation is honored only while
the resolved schema string is unchanged; a changed schema re-prompts.

> Scope note: confirmation tracks the raw `target_schema` string. A templated
> value like `${workspace.current_user.short_name}` is intentionally treated as
> stable for the local dev loop; switching workspace/identity is out of scope
> for this local-only skill (shared/prod targets are CI/CD's job).

## Token redaction

All CLI output shown to the user — `databricks bundle validate`, `databricks bundle deploy`, the
parsed `databricks bundle summary` links, **and the teardown listing/`databricks
bundle destroy` output (`--mode destroy`)** — is scrubbed with the shared
`skills/_lib/optimize.py` `redact_tokens` (Bearer / dapi / dsapi patterns) via
`_emit`. Because teardown runs inside `deploy.py` (not the skill body), this
guarantee covers destroy as well as deploy.
