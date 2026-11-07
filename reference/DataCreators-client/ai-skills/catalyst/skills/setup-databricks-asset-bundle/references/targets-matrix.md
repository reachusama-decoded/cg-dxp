# Targets matrix

The default emission ships seven bundle targets. The matrix below maps
each to its purpose, mode, and where its env-specific values live.

| Target | `mode` | `default` | Variables source | Purpose |
|---|---|---|---|---|
| `local` | development | true | `targets.local.variables` | Per-user dev space — `databricks bundle deploy` with no `--target` lands here. Default target. Authors iterate here; deploy to `dev` only when sharing is needed. |
| `dev` | (default) | false | `targets.dev.variables` | Shared dev environment — first integration env. |
| `sqa` | (default) | false | `targets.sqa.variables` | System QA — promoted from `dev`. |
| `prd` | production | false | `targets.prd.variables` | Production. |
| `dev_dr` | (default) | false | `targets.dev_dr.variables` | DR-region mirror of `dev`. |
| `sqa_dr` | (default) | false | `targets.sqa_dr.variables` | DR-region mirror of `sqa`. |
| `prd_dr` | production | false | `targets.prd_dr.variables` | DR-region mirror of `prd`. |

## Modes

| Mode | DAB behavior |
|---|---|
| `development` | Suffixes resource names with the deployer's username; pauses schedules by default. Used for `local`. |
| `production` | Strict permissions, no name suffixing, schedules unpaused unless overridden. Used for `prd` + `prd_dr`. |
| (default — no `mode:` declared) | Standard behavior; used for `dev`, `sqa`, and DR variants. |

## Per-target variable resolution

Variables resolve in this order (lowest wins, latest highest):

1. `variables.yml` declarations + defaults.
2. `databricks.yml#targets.<target>.variables` (inline per-target overrides).
3. CLI `--var key=value` (rare; ad-hoc deploys only).

The inline `targets.<target>.variables` block in `databricks.yml` is
the source of truth for env-specific values in the emitted template
(e.g. `app_catalog`, `target_schema`, `cluster_id`, Kafka/warehouse IDs).
Per-target `include:` is **not** used — the DAB schema doesn't allow it
(`config.Target.additionalProperties: false`; `include` is root-only).

## DR variants

DR targets typically diverge from their base target only in
`workspace.host` (different region) and `app_catalog` / `target_schema`
(DR-scoped). Most other variables (kafka, warehouse, secret scope) repeat
the base env's values. Keeping them as separate targets (rather than CLI
flags) lets DR-deploy state survive a re-deploy of the primary region.

## `variables_<env>.yml` files

The skill emits `variables_dev.yml`, `variables_sqa.yml`, and
`variables_prd.yml` as scaffolding for the real dev / sqa / prd
environments. They mirror what's in the matching
`targets.<env>.variables:` block. The bundle does **not** rely on
per-target `include:` to load them (DAB schema rejects it —
`config.Target.additionalProperties: false`). Treat them as reference
artifacts that document each env's variable values; the source of truth
at deploy time is `targets.<env>.variables:` in `databricks.yml`.

## Adding a new target

1. Block in `databricks.yml#targets` with at least `workspace.host` +
   `workspace.root_path` + a full `variables:` block of per-target overrides.
2. (Optional, for real envs) Create `variables/variables_<env>.yml`
   mirroring the per-target block.
3. `databricks bundle validate --target <env>`.
4. Add the target to the `promotions.yml` resolver (once DBX-BUNDLE-003
   is adopted — see `rfd-0012-citations.md`).

## Refresh-mode contract — what the skill touches

The skill's emitted target set is `{local, dev, sqa, prd, dev_dr,
sqa_dr, prd_dr}`. `mode=refresh` preserves any target block the user
has hand-added outside that set:

- **Targets the skill owns** (any in the emitted set): regenerated from
  templates. Fields the skill knows about are rewritten; user-added keys
  on the same target block are left alone.
- **Targets the skill doesn't own** (e.g. a team-specific `staging`):
  left entirely untouched.
- **Removal**: the skill never deletes a target block. Removing a target
  is a hand-edit by the author, not a refresh side effect.

Same contract applies to `variables/` files: variables the skill
declares are refreshed; user-added variables stay.
