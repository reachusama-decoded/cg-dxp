---
authors: RBLW
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/95
labels: skills, databricks, bundles, standards
---

# RFD 0012 Databricks Asset Bundles Standards and Skills Suite

## Problem

Databricks deployments are drifting. Bundle resources are authored
with inline cluster definitions, PAT-based authentication, managed
tables in arbitrary catalogs, and workspace hosts hardcoded in YAML.
Each team's bundle looks different. There is no shared definition of
what a compliant bundle looks like, and no skill that produces one
by default.

This RFD records the standards for Databricks Asset Bundles (the
`DBX-BUNDLE-*` rule category in RFD 0008) and the skills suite that
authors, validates, and deploys them against those standards.

## Background

Catalyst already defines:

- RFD 0003 — repository layout
- RFD 0004 — trunk-based promotion via `promotions.yml`
- RFD 0006 — skill tiers and the production quality bar
- RFD 0008 — engineering standards as enumerated rule IDs, including
  `DBX-SEC-*` (OAuth M2M only, no PATs) and `DBX-UC-*` (Unity Catalog
  conventions, external tables only)
- RFD 0009 — ODCS data contracts

Databricks Asset Bundles (DAB) are the supported deployment unit for
jobs, pipelines, and ML workflows. The CLI command `databricks bundle
validate` and `databricks bundle deploy` are the canonical entry
points. Existing skills (`connect-databricks`, validators for SQL)
cover parts of the workflow but do not enforce bundle-specific rules
end to end.

## Proposal

### Standards: the `DBX-BUNDLE-*` rule category

Canonical home: `rfd/0008/databricks/bundles.md`, delivered in PR 1.

The category enumerates ten rules:

| ID | Rule |
|---|---|
| DBX-BUNDLE-001 | `bundle:` block declares `name` and `target` set |
| DBX-BUNDLE-002 | One bundle per data product; resources scoped to that product |
| DBX-BUNDLE-003 | Workspace host per target read from `promotions.yml` (RFD 0004); no inline hosts |
| DBX-BUNDLE-004 | T-shirt cluster profiles via shared `compute.yml`; no inline `node_type_id` |
| DBX-BUNDLE-005 | OAuth client credentials only (cross-ref DBX-SEC-002); no PATs |
| DBX-BUNDLE-006 | Notifications block wired to the standard alert sink |
| DBX-BUNDLE-007 | Tags include `data_product`, `owner`, `cost_center` |
| DBX-BUNDLE-008 | `permissions:` block declares run-as and reviewer groups explicitly |
| DBX-BUNDLE-009 | Job tasks reference DBR LTS runtime; no preview channels in prod targets |
| DBX-BUNDLE-010 | External tables only (cross-ref DBX-UC-003); no managed tables |

### Skills suite

- **`connect-databricks`** — OAuth M2M authentication, enforces
  DBX-SEC-002. Exposes the workspace host resolver used by deploy.
- **`setup-databricks-asset-bundle`** — authors a bundle resource
  (job, pipeline, ML workflow) against `DBX-BUNDLE-*`. Declares its
  rule coverage in metadata. Composes with `generate-dag` so the
  DAG and the bundle share cluster sizing.
- **`optimize-databricks-job`** — performance findings against the
  `DBX-PERF-*` category. Out-of-band from the deploy flow; produces
  findings rather than mutating bundles.
- **`dplc-build`** — orchestrator that drives bundle setup end-to-end
  for a data product.
- **Validate / deploy path** — `databricks bundle validate` and
  `databricks bundle deploy` run from CI using `promotions.yml`. There
  is no skill that wraps deploy in this PR. A `deploy-dab` skill is
  tracked as a follow-up (A1) once the promotions.yml resolver pattern
  is settled.

### Authoring vs deploying split

Same shape as RFD 0011: `setup-databricks-asset-bundle` is adaptive,
validate and deploy are deterministic and run from CI.

### Governance

- Owners: Platform team (Databricks track) and the Skills team.
- Review cadence: quarterly.
- Cross-RFD bindings: 0003, 0004, 0006, 0008, 0009.

## Alternatives

**Use Terraform instead of DAB.** Rejected: DAB is Databricks'
supported deployment unit, integrates with workspace permissions and
Unity Catalog natively, and matches the existing operational pattern.
Terraform would duplicate that surface area.

**Require PATs for service principals.** Rejected: DBX-SEC-002
forbids PATs. M2M OAuth is the only acceptable auth path.

**Allow managed tables under `dev` targets.** Rejected: DBX-UC-003
applies across targets; relaxing it for `dev` produces bundles that
do not promote cleanly to `prod`.

## Impact

- **Pipeline and ML authors** — get a rule set and a skills suite
  that produces a compliant bundle by default.
- **Platform team (Databricks track)** — owns the rules and the
  validate/deploy skills.
- **Existing bundles** — comply with `DBX-BUNDLE-*` on next touch.
  No big-bang migration.
- **Migration path** — PR 1 (rule file), PR 2 (skills:
  `setup-databricks-asset-bundle`, `optimize-databricks-job`,
  `dplc-build`), PR 3 (this RFD).
