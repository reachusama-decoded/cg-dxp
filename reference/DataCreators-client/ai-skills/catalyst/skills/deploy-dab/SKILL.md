---
name: deploy-dab
description: |
  Deploy a Databricks Asset Bundle for a single data product to the developer's
  own local dev space during the Phase 4 build inner loop. Scoped one data
  product per run (matching setup-databricks-asset-bundle). Checks the
  setup-databricks-asset-bundle precursor, confirms the per-user target schema on
  first deploy, runs `databricks bundle validate --target local` then
  `databricks bundle deploy --target local` against that product's bundle, and surfaces the
  deployed-asset URLs (job, pipeline) from `databricks bundle summary`. Local auth
  is U2M (user OAuth via `databricks auth login`), since the local target deploys
  into the developer's own per-user dev schema; M2M client-credentials
  (connect-databricks) is the CI/shared path, not local. Can also tear down the
  user's local deploy on request via the actuator's gated `--mode destroy`, which
  lists resources, hardcodes `--target local`, and requires explicit confirmation.
  Local target only; shared/prod deploys are CI/CD's job.
  Trigger phrases: "deploy my bundle", "deploy the DAB to local",
  "databricks bundle deploy", "push my dab to my dev space", "deploy-dab",
  "remove my local deploy", "destroy my dab", "tear down my local bundle".
allowed-tools: Read Bash(python:*)
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: [connect-databricks]
  consumes: [setup-databricks-asset-bundle]
  shared-components:
    core: []
    platforms: [databricks]
  standards: [DBX-BUNDLE-002, DBX-SEC-002]
---

# deploy-dab

Deploy a Databricks Asset Bundle to the **`local` target — the developer's own
dev space** — during the Phase 4 build inner loop, and show the developer links
to what was deployed. All deterministic work runs in
`scripts/deploy.py`; this body conducts the one interactive step (first-deploy
schema confirmation).

## Two modes — route on intent first

This skill has **two modes**; decide which one the user is asking for **before**
doing anything else:

- **DEPLOY** (default) — "deploy my bundle", "deploy the DAB to local", "push my
  dab to my dev space". Follow *Procedure* below.
- **REMOVE / teardown** — "remove my local deploy", "destroy my dab", "tear down
  my local bundle". Do **not** run the deploy precursor or deploy steps; go
  straight to *Removing a local deploy (on request)* and drive its gated
  `--mode destroy` flow (list resources → confirm → destroy, hardcoded to
  `--target local`).

## When to use

- After `/setup-databricks-asset-bundle` has authored the bundle, when iterating
  on a data product and you want to push it to your own dev space.
- Repeatedly through the inner loop, before anything merges to `main`.
- To **remove** a previously deployed local bundle when the user asks (e.g.
  "remove my local deploy", "destroy my dab") — see *Removing a local deploy* below.

## When NOT to use

- Deploying to `dev` / `sqa` / `prd` (+ DR) — that is CI/CD's job.
- Deploying more than one data product at a time — single-product-at-a-time
  only, matching `/setup-databricks-asset-bundle` (DBX-BUNDLE-002). Run the skill
  once per product.
- Running the deployed job (see the separate `run-dab` story), authoring bundle
  files (`/setup-databricks-asset-bundle`), or schema migration.

## Procedure

This is the **DEPLOY** path (see *Two modes* above; for teardown go to *Removing
a local deploy*).

**Scope: one data product.** First ask the user which data product to deploy
(or infer it from context if unambiguous), exactly as
`/setup-databricks-asset-bundle` is scoped — one bundle per data product. Resolve
its bundle directory as `data_products/<product>/` (the folder containing that
product's `databricks.yml`). **Every step below operates only on that one
product's bundle**; never deploy multiple products in one run. Then:

1. **Precursor check.** Run:
   `python skills/deploy-dab/scripts/deploy.py --bundle-path <bundle> --mode precheck`
   - Exit `2`: the bundle is missing/incomplete (no `databricks.yml`, no `local`
     target, no `local` `target_schema`, or no `datasets/**/bundle/*.job.yml`
     resources) — tell the user to run `/setup-databricks-asset-bundle`, and stop.

2. **Schema confirmation.** Run:
   `python skills/deploy-dab/scripts/deploy.py --bundle-path <bundle> --mode resolve-schema`
   This prints JSON `{"bundle", "schema", "confirmed"}` (`bundle` is the
   repo-relative bundle path used as the confirmation key).
   - If `confirmed` is `true`, go to step 3 with no extra flag.
   - Otherwise show the `schema` value to the user (note that
     `${workspace.current_user.short_name}` resolves to their own per-user dev
     schema) and ask: "Deploy into schema `<schema>` — correct?"
     - If they decline, stop and point them at `/setup-databricks-asset-bundle`
       to fix the target.
     - If they confirm **and** ask not to be prompted again, persist it:
       `... --mode remember-schema --schema '<schema>'` (then go to step 3 with
       no extra flag).
     - If they confirm just this once, go to step 3 passing
       `--confirmed-schema '<schema>'` (one-shot, not persisted). The deploy is
       **blocked with exit `2`** unless a stored confirmation matches or this
       flag is supplied, so the schema gate cannot be skipped accidentally.

3. **Deploy.** Run:
   `python skills/deploy-dab/scripts/deploy.py --bundle-path <bundle> [--confirmed-schema '<schema>']`
   (add `--dry-run` to validate without deploying; `--dry-run` does not require
   confirmation). Interpret the exit code:
   - `2`: schema not confirmed — return to step 2.
   - `4`: not authenticated, CLI not installed, **or** `databricks bundle validate`/`deploy`
     failed authenticating to the workspace (e.g. a 403 on `/scim/v2/Me` from a
     stale token) — log in with U2M user OAuth `databricks auth login --host <host>`
     (or select the matching `~/.databrickscfg` profile), then retry. M2M
     client-credentials (`/connect-databricks`) is the CI/shared path, not local.
   - `5`: `databricks bundle validate`/`deploy` failed for a non-auth reason — show the
     (already token-redacted) output and stop.
   - `0`: deployed. Relay the printed list of deployed-resource URLs so the user
     can open and check them.

## Removing a local deploy (on request)

Only when the user explicitly asks to remove/destroy/tear down their local
deploy. Teardown runs through the **`deploy.py` actuator's `--mode destroy`**, not
ad-hoc `databricks` calls: the actuator hardcodes `--target local` (it cannot be
pointed at `dev`/`sqa`/`prd`), lists the resources first, redacts all CLI output,
and refuses to destroy without an explicit confirmation that matches the bundle's
per-user `target_schema`. Teardown only requires a valid `databricks.yml` with a
`local` target + `target_schema` (not the `datasets/**/bundle/*.job.yml` source
files the deploy precursor checks) — you can tear a deploy down even after the
local sources have been restructured or removed.

1. **List + gate (no confirmation yet).** Run:
   `python skills/deploy-dab/scripts/deploy.py --bundle-path <bundle> --mode destroy`
   The actuator lists the resources it would remove, then interpret the exit code:
   - `2`: listing succeeded but destroy is not confirmed (`"destroy … is not
     confirmed"`). Relay that exact resource inventory to the user.
   - `4`: not authenticated, or `bundle summary` hit a workspace auth error —
     log in with U2M (`databricks auth login --host <host>`) and retry.
   - `5`: `bundle summary` failed for a non-auth reason, so the inventory could
     not be listed — surface the (token-redacted) output and stop. Destroy never
     proceeds without a reviewable inventory.
2. **Get explicit confirmation.** Show the user the listed resources, name the
   schema being torn down, and warn that deleting data assets (schemas,
   pipelines, volumes) may cause permanent data loss. Do **not** proceed without a
   clear yes.
3. **Destroy (confirmed).** Only after the user confirms, run:
   `python skills/deploy-dab/scripts/deploy.py --bundle-path <bundle> --mode destroy --confirm-destroy '<schema>'`
   where `<schema>` is the exact `target_schema` from step 1 (e.g.
   `${workspace.current_user.short_name}`). The actuator re-lists, then runs
   `databricks bundle destroy --target local --auto-approve` and exits `0`.
   Interpret the exit code like deploy: `2` not confirmed / schema mismatch (return
   to step 2), `4` not authenticated (U2M `databricks auth login --host <host>`),
   `5` listing or destroy failed for a non-auth reason — surface the output and stop.
4. **Confirm cleanup.** Relay the actuator's printed confirmation line verbatim
   (`deploy-dab: local deploy destroyed.`). Optionally re-run
   `--mode destroy` (unconfirmed) to show the inventory is now empty/not-deployed.

## Exit codes

`0` deployed/destroyed (or dry-run validated) · `2` precursor/input — bundle
incomplete, schema missing, or deploy/destroy not confirmed · `4` Databricks CLI
not authenticated (not installed, or a validate/deploy/summary/destroy call hit a
workspace auth error) · `5` a `databricks bundle validate`/`deploy`/`summary`/`destroy`
call failed for a non-auth reason (includes the destroy pre-list `bundle summary`).

## Anti-goals

- No shared/prod deploy, no PAT enforcement of its own, no bundle authoring, no
  job execution, no `promotions.yml` routing, no marker emission.

## See also

- `references/deploy-contract.md` — the local-deploy contract.
- `/setup-databricks-asset-bundle` — authors the bundle this skill deploys.
- `databricks auth login --host <host>` — U2M user OAuth for your local dev space.
- `/connect-databricks` — M2M client-credentials OAuth, for CI/shared deploys (not local).
