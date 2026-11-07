# Training-Challenge Testing Framework — Design

> Status: **DRAFT — pending review.** Design only; no implementation.
> Scope: a portable, reproducible way to test challenges 00–04 so a green result on
> one machine predicts a green run on **any Mac (arm64) or Windows (amd64) with Docker
> Desktop + Dev Containers**. Targets the maintainer's CI platform (**Harness**), not
> GitHub Actions.

## Context

The challenges pass when the maintainer runs them, yet fail for other people on fresh
machines. The most recent field failure: a **segmentation fault on
`mise run challenge:dbt 02 -- debug`** on another laptop. A segfault there is almost
never the challenge SQL — it is a **native-dependency / CPU-architecture** problem (a
wheel such as `thrift`, `pyarrow`, or `databricks-sql-connector` built or resolved for
the wrong arch, or an unpinned version resolving differently on that host).

This class of failure is invisible to the way testing happens today, for two structural
reasons:

1. **Every "verification" this program has run happened inside the maintainer's
   already-warmed devcontainer** — cached OAuth token, seeded schemas, installed
   `dbt_packages/`, an Astro metadata DB, and existing `target/` directories. That is
   the *opposite* of a fresh clone. Accumulated state hides missing-prereq failures.
2. **No automated test runs any challenge at all.** There is no `.github/workflows`, and
   the repo's Harness pipeline (`.harness/edo-training-data-products-pipeline.yaml`) is
   **deploy-only** (Detect Changes → Git Tag → Terraform → `build_image` → Deploy
   Databricks DAB → Astro deploy → approvals). Nothing runs the offline suites, the
   `verify.sh` gates, or a cold end-to-end trainee flow.

### Why "works on my machine" happens here (evidence)

| Failure surface | Evidence | Why a warmed container hides it |
|---|---|---|
| **Native wheels / arch** | `postCreateCommand: mise trust && mise install && mise run setup` (`.devcontainer/devcontainer.json`) installs the toolchain **at build time on the host's architecture**. The devcontainer image is **built locally on each laptop** from `.devcontainer/Dockerfile`; nothing builds/tests an arm64 devcontainer centrally. | The maintainer's arm64 (or amd64) wheels already resolved once and work; a fresh install on a different arch can resolve a broken/mismatched wheel → segfault. |
| **Auth token timing** | `.mise/env.sh` exports `DBT_ACCESS_TOKEN` (OAuth refresh or `~/.databrickscfg`) **only on the mise prompt-hook or inside a `mise run` task**; a bare non-interactive shell has an empty token and dbt-databricks falls back to OAuth (`auth_type: oauth is required…`). | The maintainer's interactive shell always has a fresh token; scripts/CI and "run a command too early" do not. |
| **Cold-start race** | The `postCreateCommand` chain (`mise install` + `mise run setup`) is the multi-minute one-time build; DBT env vars are not ready until it finishes. | The maintainer waits it out once; a new user who runs `challenge:*` mid-setup gets "no catalog"/empty-env failures. |
| **Per-user / workspace coupling** | Schema is derived as `training_${USER:-root}` (`.devcontainer/utils/setup-databricks-config.sh:75-77`); profiles carry **hardcoded workspace defaults** — warehouse `a0e57263293aee36`, host `cg-db-aa00003661-dev-…` (`data_products/atlas_elt/dbt_profiles/profiles.yml`). | The maintainer's `training_<user>` schema is provisioned and the defaults match their workspace; a new user in a different workspace, or without a provisioned schema, fails deep inside a dbt run. |
| **Accumulated Airflow state** | The Astro dags folder is a **live bind mount** (`docker-compose.override.yml`: `./data_products:/usr/local/airflow/dags`); the metadata DB retains DAGs across runs. | The maintainer's scheduler already parsed everything; a fresh clone parses from scratch and surfaces import/order issues the warmed DB masked. |

Two facts make a portable framework tractable: (1) the repo **already ships offline,
credential-free structural tests** (`tests/challenges/offline` — 81 passing;
`tests/local_env/offline`); (2) Harness exposes a **native multi-arch build path** and
delegates for **both** arm64 and amd64 (see "Determinism" below), so the arch dimension
is testable in CI rather than only by hand.

## Goals

- A green test result on one machine **predicts** a green fresh-clone run on any
  supported Mac/Windows with Docker + Dev Containers.
- Catch the **native-arch / toolchain** class (the segfault) *before* a trainee hits it.
- Separate what can be tested **without Databricks credentials** (structure, toolchain,
  parse) from what needs a trainee's **real credentials** (end-to-end runs), so most
  regressions are caught cheaply and automatically.
- Make failures **loud and early** with actionable messages instead of a crash deep in a
  later challenge.
- Fit the maintainer's **Harness** platform and reuse its existing conventions.

## Non-goals

- Not replacing the deploy pipeline; the challenge-testing pipeline is separate.
- Not testing every OS/Docker permutation exhaustively; the target is the two supported
  paths (Mac arm64, Windows amd64) plus the Linux CI delegate.
- Not automating interactive browser OAuth; CI uses a service-principal token (see Risks).

## Root-cause analysis: the five reproducibility surfaces

Each surface below names the failure, its root cause, and the layer (defined next) that
guards it. This framing exists because a single "run the challenges" test cannot isolate
*why* a fresh machine fails — the guards must be layered by cause.

- **A. Toolchain / native arch.** Unpinned or arch-variant native wheels installed
  per-machine at `mise install`. → **L0** (pin + prebuilt multi-arch image), verified by
  **L2** on both arches. The 2026-07-29 field fix — `connection_parameters:
  {_disable_pandas: true}` added to `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml`
  (commit `ce106cb`) — **confirms** the crash was in the connector's pandas/pyarrow
  **native** path, i.e. an arch/native-wheel fault, not challenge SQL. That commit also
  added `scripts/runtime-compat-fingerprint.sh`, which captures the wheel arch tags and
  versions that differ across machines (used by L0/L2/Challenge 00 below).
- **B. Auth / token.** Empty `DBT_ACCESS_TOKEN` outside the mise task/prompt env. →
  **Challenge 00 preflight** + running dbt only through `mise run` (as challenges 02–04
  already do after the 2026-07-29 verify-path fix).
- **C. Schema / workspace provisioning.** `training_<user>` missing, or hardcoded
  workspace defaults wrong for the user. → **Challenge 00 preflight** (assert the schema
  is reachable *and writable*) + **L3** using an explicit throwaway CI schema.
- **D. Cold-start timing / state.** Commands run before setup completes; stale build
  artifacts. → **L3 cold harness** waits for readiness and wipes state.
- **E. Platform (Mac/Windows).** CRLF, Docker Desktop, arch. → `.gitattributes` already
  forces `eol=lf` on shell scripts (mitigated); arch handled by L0/L2; residual Docker
  Desktop behavior by **L4**.

## Design: the testing pyramid

Structure rationale: the layers are ordered by **cost and credential-dependence** —
cheap/credential-free at the base (runs on every change), expensive/credentialed at the
top (runs on demand). Each layer catches what the one below it cannot.

| Layer | Catches | Where it runs (Harness) | Creds |
|---|---|---|---|
| **L0 Determinism** | Root of the segfault: unpinned/arch-variant native wheels | Pin versions; build the **devcontainer image multi-arch** via `account.CGContainerMultiArchBuild`; pin `devcontainer.json` to that image | none |
| **L1 Offline structural** | Guide/scaffold/wiring/config regressions | New CI stage on the Linux delegate, Nexus python image: `pytest tests/challenges/offline tests/local_env/offline` | none |
| **L2 Cold toolchain + parse** | "Fresh install → broken toolchain" (segfault class) | In the prebuilt image, **matrix over amd64 + arm64**: `mise install` + per-project `dbt deps/parse` + `astro dev parse` | none |
| **L3 Cold end-to-end** | Full trainee path from scratch | New stage reusing the deploy stages' `DATABRICKS_HOST`/`DATABRICKS_TOKEN` secrets + a throwaway `training_ci_*` schema: `mise run test:cold` | reuses existing |
| **L4 Manual laptop check** | Real Docker Desktop behavior on a physical Mac/Windows | Documented checklist on a fresh clone + "Rebuild Container (No Cache)" | trainee's own |

**Keystone — Challenge 00 as a loud preflight.** Every layer runs Challenge 00 first; if
00 is green the environment is ready and 02–04 should work. This converts silent deep
failures into one early, actionable check (see "Challenge 00" below).

### L0 — Determinism and the multi-arch devcontainer image

L0 is the *root fix* for the reported segfault, because a test is only portable if the
environment is deterministic. Two parts:

1. **Pin the toolchain.** Pin exact versions in `.mise.toml` (Python, `dbt-core`,
   `dbt-databricks`) and pin Python dependencies with a hashed lockfile, so every host
   resolves **identical** binaries rather than re-resolving wheels per machine. Verify
   determinism with the existing `scripts/runtime-compat-fingerprint.sh`, which emits a
   comparable JSON of Python/platform, package versions, and **wheel arch tags**;
   matching fingerprints across arches and machines is the pass condition (mismatched
   arch tags are the fingerprint of the segfault class).
2. **Build the devcontainer image centrally, multi-arch, and pin to it.** Today the
   devcontainer is built on each laptop and installs tools at `postCreateCommand` — the
   exact step that produced the arm64 segfault. Instead, build the devcontainer/test
   image once for **both** arches and have `.devcontainer/devcontainer.json` reference
   that prebuilt `image:` (dropping the per-machine `mise install` from image build).
   Mac (arm64) and Windows/Linux (amd64) then pull the **same tested, pinned** image.

   The build path already exists: **`account.CGContainerMultiArchBuild` (v1.0)**, an
   account-level Custom stage template found via the Harness template API. It:
   - runs a **`Build_AMD`** group (`docker buildx build` → `:amd64-<APP_VERSION>`),
   - runs a **`Build_ARM`** group on a **native arm64 node** —
     `stepGroupInfra.nodeSelector: {arch: arm64}` with arm64 `NoSchedule` tolerations,
     *not* QEMU emulation — (`:arm64-<APP_VERSION>`),
   - publishes a single manifest with `crane` (reads both digests → one multi-arch tag),
   - caches layers in ECR (`--cache-from/--cache-to`) for fast rebuilds.

   Required inputs: `BRANCH_NAME`, `APP_VERSION`, `IMAGE_NAME` (required); `DOCKERFILE`
   (default `Dockerfile`), `CONTEXT`, and `BUILD_AMD_ARCH`/`BUILD_ARM_ARCH` toggles. The
   repo's current `build_image` stage uses the *single-arch* `account.caspian_build_image`
   with `BUILD_ARM_ARCH: false`, and it builds the **Astro runtime** image (root
   `Dockerfile`, `astro-runtime:3.1-17-base`) — a different image from the devcontainer.
   L0 adds a **devcontainer/test image** build with both arch toggles `true`.

### L1 — Offline structural tests

The credential-free base layer already exists and passes (81 in
`tests/challenges/offline`). L1 wires `pytest tests/challenges/offline
tests/local_env/offline` into a Harness CI stage on the Linux delegate using a Nexus
python image, gated by extending the existing **Detect Changes** convention with a
`CHALLENGES_CHANGED` flag. It guards guide/scaffold/wiring/config invariants in seconds
on every change. (Note: `tests/local_env/offline` currently has one **pre-existing,
unrelated** failure — `test_dpc_check_reports_auth_mode_and_refresher_health` asserts
`--pat` in `.devcontainer/check.sh`, absent across all commits — to be triaged separately
before L1 gates on this suite.)

### L2 — Cold toolchain + parse (amd64 **and** arm64)

L2 is the automated guard for the segfault class. In the prebuilt image, as a **matrix
over `[amd64, arm64]`** (arm64 leg using the same `nodeSelector: {arch: arm64}` trick as
the multi-arch template), run: `mise install` (proves the pinned toolchain installs
cleanly per arch), then per challenge project `dbt deps` + `dbt parse`, then `astro dev
parse`. No Databricks credentials are needed — parse/compile-without-connect only. Had
this existed, a fresh-install/arch toolchain break would have failed here, not on a
trainee's laptop.

### L3 — Cold end-to-end trainee run

L3 proves the full path from scratch with real credentials. A new `mise run test:cold`
harness (invoked by a Harness stage that reuses the deploy stages' `DATABRICKS_HOST`/
`DATABRICKS_TOKEN` secrets):

1. **Wipes accumulated state:** `docker compose down -v` (Astro metadata DB, volumes) and
   deletes `target/`, `dbt_packages/`, `logs/`, `__pycache__`.
2. **Uses a throwaway schema** (e.g. `DBT_SCHEMA=training_ci_<run-id>`) so it never
   depends on a warmed personal schema and cleans up after itself.
3. **Waits for readiness** — blocks until `mise run setup` completes and a readiness
   probe (Challenge 00 preflight) passes — closing the cold-start race.
4. **Runs each challenge from stubs:** `reset` → author the shipped `solution/` → `seed`
   → `build` → `verify`, asserting each gate goes green.

L3 can also run on the arm64 matrix leg to prove the *end-to-end* path (not just parse)
on Apple-silicon-equivalent hardware.

### L4 — Manual laptop check

Because hosted CI cannot fully reproduce Docker Desktop on a physical Mac/Windows
(volume-mount semantics, file sharing, interactive OAuth), a short **documented
checklist** run on a fresh clone + "Rebuild Container (No Cache)" remains the final
acceptance gate. With L0–L3 in place this shrinks from "the only arm64 guard" to a light
sanity check.

## Challenge 00 as the preflight keystone

Challenge 00 becomes the single early gate every layer runs first. It must **fail loudly
with a specific message** when any prerequisite is missing, checking:

- devcontainer setup **completed** (not mid-`postCreate`);
- Databricks auth valid (a token is present in the mise env; OAuth refresher healthy);
- catalog **and** the personal schema are reachable **and writable** (not just that a
  default resolved) — this is what catches surface **C**;
- the SQL warehouse is reachable and `dbt debug` succeeds — surfacing a toolchain/arch
  problem here (surface **A**) with a clear message instead of a segfault in Challenge 02;
- the runtime matches a known-good baseline — run `scripts/runtime-compat-fingerprint.sh`
  and compare wheel arch tags/versions, failing loud on drift (this is the earliest,
  cheapest catch for surface **A**).

## Harness integration

The framework maps onto existing pipeline conventions, so it reuses infrastructure rather
than inventing it:

- **Delegate/infra:** `KubernetesDirect` on `datacreatoracademyaa00003661_kubernetes_shared`
  (namespace `…-delegate-oz-dev`, `os: Linux`); org `capgroupedo`, project
  `datacreatoracademyaa00003661`.
- **Images:** pulled via the Nexus connector `account.acct_cgdevregistry_aws_nexus_publish`.
- **Gating:** extend the `Detect Changes` step (`check_directory_changes`) with a
  `CHALLENGES_CHANGED` output to run challenge stages only when relevant paths change.
- **Secrets:** L3 reuses the `DATABRICKS_HOST`/`DATABRICKS_TOKEN` secrets the
  `Deploy_Databricks_*` stages already inject.
- **Multi-arch:** L0 uses `account.CGContainerMultiArchBuild`; L2/L3 reuse its arm64
  `nodeSelector` for the arm leg of the matrix.

Recommended placement: a **separate `challenge-tests` Harness pipeline** (or a gated
pre-deploy stage group) triggered on PRs/pushes, kept independent of the heavy
Terraform/DAB/Astro deploy stages so feedback is fast.

## What is automatable vs. manual

| Concern | Automatable in Harness? | Layer |
|---|---|---|
| Guide/scaffold/wiring regressions | Yes, no creds | L1 |
| Toolchain installs cleanly (amd64) | Yes, no creds | L2 |
| Toolchain installs cleanly (**arm64**) | **Yes** — native arm64 delegate exists | L2 |
| DAGs/projects parse | Yes, no creds | L2 |
| Full trainee E2E (seed→build→verify) | Yes, with service-principal creds | L3 |
| Real Mac/Windows Docker Desktop | No — physical laptop only | L4 |

The honest caveat the native arm delegate resolves: previously arm64 could only be caught
by hand; with `CGContainerMultiArchBuild`'s arm64 node path, arm64 is now testable in CI.

## Validating the framework itself (meta)

Each guard must be proven with a red→green check, not assumed: introduce a known break
(e.g., an unpinned/downgraded adapter, an unauthored stub, a wrong warehouse id) and
confirm the corresponding layer **fails**, then confirm it **passes** on the fixed input.
A guard that has never gone red proves nothing.

## Risks & open questions

- **CI credential model.** L3 needs a non-interactive credential. Options: a Databricks
  **service principal PAT** stored as a Harness secret + a dedicated **CI catalog/schema**
  (`training_ci`), provisioned once. Interactive OAuth cannot run unattended.
- **CI schema provisioning.** Surface C means the CI schema must be pre-provisioned and
  writable by the service principal; otherwise L3 fails for the same reason trainees do.
- **arm64 delegate availability/cost.** The matrix's arm64 leg depends on arm64 nodes in
  the shared delegate pool remaining available; confirm capacity and scheduling.
- **Devcontainer image publish cadence.** Pinning `devcontainer.json` to a prebuilt image
  means image rebuilds (on dependency changes) must be published before trainees pull;
  define the tag/version and rebuild trigger.
- **Hardcoded profile defaults.** The workspace defaults in `profiles.yml` should arguably
  be removed (fail-fast when env is unset) rather than silently used; decide as part of
  strengthening Challenge 00.

## Success criteria

- A fresh clone on a supported Mac (arm64) and Windows (amd64) completes challenges 00–04
  following only the guides.
- L1 + L2 run on every relevant change in Harness and fail on a deliberately broken
  toolchain or scaffold, on **both** arches.
- L3 runs on demand and proves the seed→build→verify path from a wiped state against a
  throwaway CI schema.
- The reported class of failure (arch/native-wheel segfault) is caught by L0/L2, not by a
  trainee.

## Out of scope / future

- Multi-arch build of the **Astro runtime** image (separate from the devcontainer image).
- Load/performance testing of the challenges.
- Automated provisioning of trainee personal schemas (an onboarding concern, not testing).
