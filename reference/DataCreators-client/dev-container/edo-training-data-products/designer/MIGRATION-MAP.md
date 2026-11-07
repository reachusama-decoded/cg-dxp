# Migration to challenges/v1 and challenges/v2

Planning only, 5 October 2026. No relocation has been performed. See [PLAN.md](PLAN.md) for sequence and gates.

## Preserve the existing route

| Current maintained path | Future location | Preservation / v2 reuse |
|---|---|---|
| `challenges/README.md` | `challenges/v1/README.md` | Preserve numbered-route explanation; create a new version selector at the old root. |
| `challenges/CHANGES.md` | `challenges/v1/CHANGES.md` | Preserve historical change narrative. |
| `challenges/00-environment-check/` | `challenges/v1/00-environment-check/` | Preserve readiness; expose a version-aware entry for v2 without duplicating checks. |
| `challenges/01-docker-intro/` | `challenges/v1/01-docker-intro/` | Preserve starter/app/solution/verifier; derive Docker Phase 1 and extend Phase 2. |
| `challenges/02-dbt-pipeline/` | `challenges/v1/02-dbt-pipeline/` | Preserve dbt project, profiles, stubs and solutions; derive improved two-phase dbt pack. |
| `challenges/03-airflow-orchestration/` | `challenges/v1/03-airflow-orchestration/` | Preserve guides, stubs, solution and support assets; split by concepts/proof. |
| `challenges/04-atlas-capstone/` | `challenges/v1/04-atlas-capstone/` | Preserve both phases, 14 extensions and from-scratch/review modes. |
| `data_products/portfolio_analytics/` | Existing product path | Preserve during v1 migration; isolate v2 edits through explicit workspace manifests. |
| `data_products/atlas_elt/` | Existing product path | Same; do not nest or silently duplicate the authoritative product because guides move. |
| Supplied Catalyst tree | Existing client sibling tree | Reference selected skills/templates; no migration or bulk modification. |

Inventory unlisted root files before moving; do not assume the five numbered directories are every maintained artifact. V1 is a preserved curriculum with compatibility path fixes, not a promise that every byte in an executable can remain identical after relocation. Capture original hashes and record path fixes separately from pedagogical changes. Never alter dated historical execution evidence to look like it used the new paths.

## Dependencies that a folder move would break

| Surface | Current evidence | Required implementation work |
|---|---|---|
| Mise dispatch | `.mise.toml` `challenge:verify`, `verify-all`, `dbt`, `seed`, `reset` use `challenges/<NN>-*` or numbered glob loops. | Resolve a version explicitly. Retain legacy numeric entry points routed to v1. Separate “verify all v1” from “all offered v2 core phases.” |
| Script root calculation | Atlas verifier uses `SCRIPT_DIR/../..` for repo root. Other verifiers/helpers also need inventory. | Relocation adds depth; use a shared tested repo locator or pass an explicit root. Review dbt packages/profiles and copy-relative paths. |
| Reset destinations | 03 resets `data_products/portfolio_analytics`; 04 resets Atlas datasets; 02 resets its local `dbt/`. Solution-only files are removed. | Preserve known reset semantics; use manifests for v2 authored files and isolated destinations. Never let a v2 reset erase v1 work or vice versa. |
| Shared seed/model references | Portfolio Airflow uses the dbt challenge fixture/project; Atlas uses `shared` packages. | Resolve through declared version-aware fixture paths. Keep package-relative topology when making disposable copies. |
| Product guide links | Product README headers point back to numbered challenge guides. | Update current links to v1 and provide explicit v2 links where appropriate. |
| Offline/live test helpers | `tests/challenges/conftest.py` and tests hardcode numbered paths and five-directory discovery. | Add version-aware discovery; keep legacy suite coverage and separate v2 inventories. Avoid recursively collecting inactive phases or solutions. |
| Stub synchronization | `test_ch03_stub_sync.py` depends on indexed source blobs and destination assets. | Update paths/fixtures in a disposable indexed checkout; do not relax the assertion to mask a mismatch. |
| Guide checks | `test_wiring.py` currently scans `challenges/*/README.md`; verifies direct dbt commands. | Traverse offered phases and nested learner READMEs explicitly; preserve direct-tool instruction checks. |
| Ignore/discovery rules | `.dbtignore` expects `challenges/**/solution/**`; SQL lint ignores `challenges/`. | Exclude central `v2-solutions` and generated runtime directories from dbt/Airflow/learner extraction, while checking solutions separately. |
| Development-container entry points | Getting-started, readiness check, helper installation/home-link definitions and VS Code settings are possible path consumers. | Inventory actual references and generated links; recreate shortcuts to the intended version and test Windows/WSL path behavior. Do not commit platform-specific symlinks. |
| DAG discovery/generation | Airflow artifacts live under product paths and generated configuration has its own runtime layout. | Keep one intended runtime copy per selected route; prevent v1 and v2 DAG-ID collisions and solution DAG discovery. |
| Course adapters | The course's `scripts/integrate-client.py` (repository root; formerly `Capital/DataCreators-v4/`) explicitly reads the five old guide paths and applies v4 scope adaptations. | A future course adapter selects challenge version via manifest. Preserve v4's archived source binding and released pack; do not reuse its Phase 2 truncation rule for v2. |
| Current docs vs historic docs | Root/current guides and dated RCAs both contain old paths. | Update operational/current guidance; leave historical command evidence dated, with a migration note if needed. |

The table identifies known examples and required searches; it does not claim every possible reference has been enumerated. Before implementation, run a repository-wide text/path inventory including `.mise`, `.devcontainer`, launch scripts, docs, tests, course generators and any packaging filters. Track each match as current consumer, historical record, generated artifact or unrelated file, with an explicit disposition.

## Version routing and compatibility contract

Legacy `mise run challenge:verify 02` continues to mean the preserved dbt challenge in v1. It must never select Git, a new second topic or an arbitrary phase in v2. The same rule applies to existing reset/dbt/seed wrappers. The root challenge README makes this clear while recommending explicit v2 navigation for the new route.

Proposed new interface: a distinct `challenge:v2:verify` task accepting tool and phase, and corresponding starter check/reset/review tasks. The exact Mise argument syntax is to be implemented and tested against the installed Mise version; these task names are proposals, not working commands. Use canonical tool IDs and `phase-one-certified` / `phase-two-proficient` values. Reject unknown versions/tools/phases, multiple glob matches and requests to verify an inactive phase. Never silently fall back to v1 on a v2 resolution error.

Record which phase baseline a reset restores. Explain that a file reset is distinct from remote data cleanup; previous tables can otherwise let tests pass against stale output. Treat workspace/schema/topic/DAG-run isolation as versioned resources. V2 should normally work in phase-specific disposable/learner workspaces derived from preserved shared assets; if it must author in a canonical product path, require an explicit selected-version workspace and prohibit simultaneous incompatible use.

## Implementation order and rollback

1. Freeze hashes, layout, symlink targets, source revision and current test evidence; identify migration edits.
2. Create v1 and move preserved assets in one isolated implementation checkout; patch path consumers and run offline compatibility checks.
3. Verify every existing numbered command resolves to v1 and scoped reset restores the correct files; check lock files and tracked diff.
4. Introduce the v2 schema/version selector and isolated workspaces before adding new learner runtime artifacts.
5. Author tool phases and mirrored solutions; add v2 tests tied to behavior and actual task evidence.
6. Rehearse the legacy route and the v2 route separately, then exercise switching/reset isolation.
7. Integrate a future course candidate using the manifest; preserve prior released course source snapshots and releases.

The rollback unit is the isolated implementation change set: restore source locations and path consumers together. Never “rollback” by resetting the user's unrelated working tree or deleting remote schemas. Keep a before/after migration map and source hash manifest so a failed relocation can be diagnosed without losing learner assets.

## Migration acceptance

Require path/link resolution, five preserved challenges, direct dbt guide commands, stub sync, profiles and shared package portability, offline suite, scoped reset and clean-tree verifier behavior. Then require live checks only at available execution boundaries: Docker, auth/warehouse, Astro/Cosmos and full Atlas. Keep source inspection, historical successful runs and new observed runs separate in the evidence ledger. A migrated offline pass does not certify the client-connected journey.
