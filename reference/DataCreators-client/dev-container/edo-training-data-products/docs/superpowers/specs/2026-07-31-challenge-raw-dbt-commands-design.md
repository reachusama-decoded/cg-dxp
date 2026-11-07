# Raw dbt Commands in the Training Challenges — Design

> Status: **IMPLEMENTED, with two design decisions superseded during live testing.**
> Scope: replace the `mise`-wrapped dbt *teaching* commands in challenges 02, 03, and 04
> with **raw `dbt` commands** a trainee types directly, so trainees build muscle memory
> with real dbt. The automated verify gate, reset, and Databricks setup stay on `mise`.
>
> **Amendments (2026-08-03), from an end-to-end trainee walkthrough on a Windows host:**
> 1. **§3 profile discovery: symlinks replaced by committed copies.** The documented
>    Windows risk materialized as a hard blocker. See §3 and Risks.
> 2. **The blanket `--inline` ban is lifted** (it was a `mise`-wrapper constraint that this
>    very design removes). See "Constraints".
>
> RCAs: `docs/rca/2026-08-03-profiles-symlink-windows.md`,
> `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md`,
> `docs/rca/2026-08-03-challenge-04-dbt-segfault.md`.

## Context

The challenges were ported from `../preflight` into this repo. The preflight guides used
**raw dbt** (`dbt build`, `dbt debug`, `dbt docs generate`) run from inside each
challenge's dbt project directory (`preflight/02-dbt-pipeline/README.md:40-41`). During the
port they were rewrapped as `mise run challenge:dbt <NN> -- <args>` and
`mise run challenge:seed <NN>`, which invoke `dbt_wrapper.py` with an explicitly resolved
interpreter and fixed `--project-dir` / `--profiles-dir` / `--target local`
(`.mise.toml` `[tasks."challenge:dbt"]`; porting design as-built note
`docs/superpowers/specs/2026-07-27-training-challenges-and-atlas-capstone-design.md:437-440`).

The training goal is for business users new to Databricks/dbt/Airflow to **get comfortable
using dbt itself**. A wrapper named `mise run challenge:dbt 02 -- build` hides the tool
they are meant to learn. This design converts the commands trainees type back to raw dbt
while preserving everything the port and the testing-framework design deliberately fixed.

The believed-but-untested premise ("the original challenges have raw dbt commands but were
not tested thoroughly") is confirmed: the raw commands existed in preflight, and the two
hard blockers to running them here are already cleared (see "Feasibility evidence").

## Goals

- Trainees run **raw dbt** for the interactive teaching commands: `dbt debug`, `dbt seed`,
  `dbt build`, `dbt run`, `dbt test`, `dbt ls`, `dbt show`, `dbt compile`,
  `dbt source freshness`, `dbt snapshot`, and (challenge 04) `dbt deps`.
- Commands read cleanly — `dbt build --select stg_holdings`, not
  `mise run challenge:dbt 02 -- build --select stg_holdings` — via a one-time
  `cd <project-dir>` per challenge (the normal dbt working habit).
- The native flow stays green: `mise run verify:local-dev`, `pre-commit run --all-files`,
  and the `tests/challenges/offline` suite pass identically before and after (parity is a
  hard constraint carried from the porting plan
  `docs/superpowers/plans/2026-07-28-training-challenges-and-atlas-capstone-port.md:15`).
- The learner **gate** stays deterministic: `mise run challenge:verify <NN>` is unchanged.
- **Every command a trainee runs achieves its documented purpose** — it fails when it is
  meant to fail (an unsolved stub, a data-quality test catching a broken model, a STALE
  freshness state, a deliberate "try a variation" break) and succeeds when it is meant to
  succeed. A zero exit code or a green final `challenge:verify` is not sufficient evidence;
  each command's observed effect must match the outcome the guide describes.

## Non-goals

- No change to `dbt_wrapper.py`, `verify.sh`, the profiles.yml **content**, model SQL,
  seeds, stubs, or solutions.
- No change to the bundle / CI / `mise run dbt:*` / Harness deploy paths.
- Challenges 00 and 01 are out of scope (no dbt).
- Not removing the hardcoded workspace defaults in the profiles (a fail-fast question
  raised in the testing-framework design; cross-referenced under Risks, decided there).
- Not building the automated test harness itself — that is the separate
  `2026-07-29-training-challenge-testing-framework-design.md`. This design only states how
  the change will be verified within that framework.

## Feasibility evidence

Two risks would have made this hard; both are cleared by inspection:

1. **No caspian Jinja-macro dependency in challenge models.** `dbt_wrapper.py`'s primary
   job is a side-effect `import caspian.dbt.dbt_modules` so `modules.get('caspian')`
   resolves in Jinja (needed for `bitemporal_load_v2`) (`dbt_wrapper.py:10, 182-186`). A
   repo-wide grep for `caspian` / `modules.get` / `bitemporal` across the challenge model
   SQL (`challenges/02-dbt-pipeline/dbt`, `data_products/portfolio_analytics`,
   `data_products/atlas_elt`) returns matches **only** in bundle/airflow/variables YAML —
   **zero in any `.sql` model**. Challenge models therefore compile and run under plain
   `dbt` without the wrapper's patch.
2. **`dbt` is a real, on-PATH command in the devcontainer.**
   `.devcontainer/requirements.txt:4-5` pins `dbt-core==1.11.8` and
   `dbt-databricks==1.11.7`, installed into `/opt/venv` (on `PATH` via
   `.devcontainer/Dockerfile:52-53`) and `.venv` (`setup-python-deps.sh` installs into
   both). The dbt-core console script `dbt` is present in those venvs.

Auth reaches a raw shell the same way it reaches a `mise run` task: `mise run
setup:databricks` writes a non-secret env contract to `~/.config/dpc/databricks.env`
(`DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DBT_CATALOG`, `DBT_SCHEMA`, `DBT_HOST`,
`DBT_HTTP_PATH`; `.devcontainer/setup-databricks-dbt.sh` tail), and `.mise/env.sh` — sourced
on **every interactive prompt** by the mise activate hook — sources that file and refreshes
the short-lived OAuth `DBT_ACCESS_TOKEN` into the shell (`.mise/env.sh` OAuth block). Every
`env_var(...)` the profiles read (`challenges/02-dbt-pipeline/dbt_profiles/profiles.yml`,
`data_products/atlas_elt/dbt_profiles/profiles.yml`,
`data_products/portfolio_analytics/dbt/profiles.yml`) is satisfied in an interactive
devcontainer shell. The token caveat is addressed in "Auth and token reconciliation".

## Design

### 1. Scope and command inventory

Convert the interactive teaching commands only:

| mise command today | raw dbt equivalent | count (02 / 03 / 04) |
|---|---|---|
| `mise run challenge:dbt <NN> -- <args>` | `dbt <args>` (from project dir) | 39 / 4 / 36 |
| `mise run challenge:seed <NN>` | `dbt seed` | 5 / 1 / 0 |

Stay on `mise` (unchanged): `challenge:verify`, `challenge:verify-all`, `challenge:reset`,
`setup:databricks`. The `challenge:dbt` / `challenge:seed` **mise tasks remain defined** in
`.mise.toml` (they are locked by `tests/challenges/offline/test_mise_tasks.py:16` and
`test_verify_scripts.py:49,65`, and serve as a non-interactive fallback); only the READMEs
stop teaching them.

### 2. Trainee command model

Each challenge guide gains a one-time setup line, then clean commands:

- **02:** `cd challenges/02-dbt-pipeline/dbt`
- **03:** `cd data_products/portfolio_analytics/dbt`
- **04:** `cd data_products/atlas_elt`

Thereafter: `dbt debug`, `dbt seed`, `dbt build --select stg_holdings`,
`dbt test --select staging`, `dbt ls --resource-type model`,
`dbt show --select stg_funds --limit 5`, `dbt source freshness`, `dbt snapshot`,
`dbt compile --select dom_trading__trade`.

**Drop `--target local`.** Each profile's default is `target: dev`, and the `dev` and
`local` output blocks are byte-identical in all three profiles (02/04 token-based, 03
OAuth), so a bare `dbt build` uses an identical connection. Rationale: it is the cleanest
form and matches how dbt users run inside a single environment; `verify.sh` keeps
`--target local` unchanged (it is the deterministic gate, not a teaching command).

The "Common commands" table and inline steps in each README are rewritten accordingly;
the `challenge:verify` / `challenge:reset` rows are unchanged.

### 3. Profile discovery — the one enabling change

dbt resolves `profiles.yml` in this order: `--profiles-dir` flag → `DBT_PROFILES_DIR` →
**current working directory** → `~/.dbt/`. After the trainee `cd`s into the project dir:

- **03** already ships `profiles.yml` inside its project dir
  (`data_products/portfolio_analytics/dbt/profiles.yml`) → bare `dbt` finds it. No change.
- **02** and **04** keep `profiles.yml` in a `dbt_profiles/` subfolder, which is **not**
  the project dir, so bare `dbt` would not find it.

**Change:** add a `profiles.yml` in the 02 and 04 project dirs carrying the same content as
the existing `dbt_profiles/profiles.yml`:

- `challenges/02-dbt-pipeline/dbt/profiles.yml`
- `data_products/atlas_elt/profiles.yml`

> **SUPERSEDED 2026-08-03 — these were originally symlinks; they are now committed copies.**
>
> The original rationale for a symlink was a single source of truth (no drift), leaving
> `dbt_profiles/profiles.yml` in place and `verify.sh` / bundle / `dbt:run` tooling — which
> pass `--profiles-dir` explicitly — untouched. All of that still holds for a copy; only the
> no-drift property is lost, and it is now enforced by test instead.
>
> **Why the change:** the "Windows-native checkout" caveat filed under Risks was not a
> narrow edge case — it broke the challenges outright. Git for Windows defaults to
> `core.symlinks=false`, so a tracked symlink (mode `120000`, blob = the target path) is
> checked out as a **regular 28-byte text file containing `../dbt_profiles/profiles.yml`**.
> dbt then read that path string as the profile and died on the *first command of Challenge
> 02* with `AttributeError: 'str' object has no attribute 'get'` — no filename, no mention
> of profiles.yml. Challenge 04 failed identically. The devcontainer does not rescue this:
> it bind-mounts the Windows working tree, so it faithfully sees the broken file.
>
> This is the fallback the Risks section already named ("a committed copy of `profiles.yml`
> per project dir, accepts minor drift risk"). The drift risk is covered by the
> content-equality assertions in `test_ch02.py` / `test_ch04_structure.py`, now strengthened
> with `assert not proj.is_symlink()`, plus a repo-wide ban on tracked symlinks
> (`tests/local_env/offline/tooling/test_no_tracked_symlinks.py`).
>
> **Correction to the original rationale:** it claimed the symlink made hard-won profile
> fixes "apply identically — e.g. `_disable_pandas: true`". That was not true in practice:
> `atlas_elt`'s profile never carried `_disable_pandas` at all, and Challenge 04 segfaulted
> on every row-returning query (exit 139, silent). Sharing a file only propagates a fix that
> is actually in the file. That setting is now present on all targets and enforced by
> `tests/local_env/offline/tooling/test_dbt_profiles_disable_pandas.py`. See
> `docs/rca/2026-08-03-challenge-04-dbt-segfault.md`.

`challenge:reset` copies model stubs, not `profiles.yml`, so the project-dir copy survives
resets.

### 4. Auth and token reconciliation (the key correctness point)

The testing-framework design names **"running dbt only through `mise run`"** as the
mitigation for its failure surface **B** — an empty `DBT_ACCESS_TOKEN` outside the mise
env makes dbt-databricks fall back to interactive OAuth and error
(`2026-07-29-training-challenge-testing-framework-design.md`, "works on my machine" table,
row B; also `tests/challenges/offline/test_ch04_structure.py:72-83`). This design moves the
teaching commands **off** `mise run`, so it must reconcile that surface rather than ignore
it.

Reconciliation:

- The token is populated **on every interactive prompt**, not only inside `mise run`,
  because `.mise/env.sh` runs via the mise activate hook installed by `setup:mise`. A
  trainee typing `dbt build` at the integrated-terminal prompt has the **same** refreshed
  `DBT_ACCESS_TOKEN` a `mise run` task would. The documented failures (surface B) are for
  **non-interactive** shells (`bash verify.sh`) and commands run **mid-setup** — neither is
  the interactive teaching path. Note that this is precisely why `verify.sh` stays on
  `mise` (it is invoked as a subshell by the gate).
- **Challenge 00 is the loud preflight** that already asserts "a token is present in the
  mise env" and that "`dbt debug` succeeds" before a trainee reaches challenge 02
  (`2026-07-29-...-testing-framework-design.md`, "Challenge 00 as the preflight keystone").
- Each converted guide **opens with `dbt debug`**, so a missing token surfaces immediately
  with dbt's own connection error rather than deep in a build — this also restores the
  preflight's `dbt debug` habit.
- Add one **troubleshooting** line per converted guide: *if dbt reports missing
  credentials / `auth_type: oauth is required...`, open a fresh terminal so the mise
  environment loads (or re-run `mise run setup:databricks`), then retry.* The existing
  "run `mise run setup:databricks` once before any dbt command" prerequisite is kept.

#### 4a. The empty-token hang, and the sentinel that prevents it

The reconciliation above assumes a missing token surfaces as a fast **connection error**.
In practice it did not: with a token-based profile, an **empty** token made dbt hang
**silently and indefinitely**. Root cause, confirmed in the devcontainer:

- `dbt-databricks` resolves credentials in `DatabricksCredentialManager.__post_init__`
  (`dbt/adapters/databricks/credentials.py`): a present token → `authenticate_with_pat()`
  (fast); an **empty** token with no client secret →
  `authenticate_with_external_browser()`, which blocks forever on the OAuth callback
  (`select()` on port 8020). There is no cached-session fast path for the empty case.
- Two merged PRs turned that latent behaviour into a silent hang for trainees: PR #14
  (`ecacaa1`) converted the `portfolio_analytics` `local`/`dev` targets from
  `auth_type: oauth` to a `DBT_ACCESS_TOKEN` (correctly — `auth_type: oauth` hangs in the
  headless astro DAG container), and PR #13 (`5539f11`) set the port-8020 callback to
  `onAutoForward: silent` in `.devcontainer/devcontainer.json`, hiding the browser prompt.
- The token is minted from the OAuth session by `.mise/env.sh` (`databricks auth token`),
  which **intermittently returns empty**; an empty token then took the hang path.

Fix (makes §4's "fast error" assumption actually hold):

1. **Non-empty sentinel default** in every challenge profile — the token falls back to
   `MISSING_run__mise_run_setup_databricks` instead of `''` when unset. A non-empty token
   always routes dbt to the PAT path, so a failed mint yields a clear
   `Invalid access token` (401/403) in ~2–3s instead of an infinite browser hang. Applied
   to `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml`,
   `data_products/atlas_elt/dbt_profiles/profiles.yml`,
   `data_products/portfolio_analytics/dbt/profiles.yml`, and the challenge-03 stub/solution
   copies.
2. **Empty→unset normalization** in `.mise/env.sh` — dbt's `env_var(name, default)` only
   returns `default` when `name` is *unset*, so a SET-but-empty `DBT_ACCESS_TOKEN` (from a
   failed mint or a token-less `.databrickscfg`) would bypass the sentinel. `.mise/env.sh`
   now unsets an empty `DBT_ACCESS_TOKEN`/`DATABRICKS_TOKEN` and no longer exports an empty
   token from `.databrickscfg`.

Verified in the devcontainer: a valid minted token → `dbt debug` connects in ~4s; a missing
token → `Connection test: [ERROR]` (401) in ~2s, no hang. The paired `.mise/env.sh` warning
still tells the trainee to re-run `mise run setup:databricks`.

A full root-cause analysis — the credential-resolution trap, the interactive-terminal mint
gap, reproduction steps, the fix, and the consequences of not fixing — is in
`docs/rca/2026-08-03-dbt-databricks-auth-hang.md`.

### 5. Challenge 04 specifics

Challenge 04 is the highest-risk conversion and needs one extra step:

- **`dbt deps` is required.** `data_products/atlas_elt/packages.yml` declares a local
  package `{{ env_var('PROJECT_HOME', '../..') }}/shared`. The guide must add an explicit
  `dbt deps` step before the first build. This is a net teaching gain (trainees learn
  `dbt deps`). The `PROJECT_HOME` fallback `../..` resolves to the repo root's `shared/`
  when run from `data_products/atlas_elt`, so raw `dbt deps` works without the wrapper
  setting `PROJECT_HOME`.
- 04 also uses snapshots, incremental models, and `source freshness`; combined with the
  local package it is the guide most likely to surface an edge case, so it is tested first
  and most carefully (see Verification).
- `mise run challenge:verify 04` **must remain** in the 04 README and `bash verify.sh` must
  not appear (locked by `tests/challenges/offline/test_ch04_structure.py:72-83`); the
  design keeps the verify gate on mise, satisfying this.

### 6. What stays on mise, and why

| Command | Stays on mise because |
|---|---|
| `mise run challenge:verify <NN>` | Deterministic learner gate; runs `verify.sh` → `dbt_wrapper.py` with explicit dirs/target in a subshell that must load the env. Locked for 04 by `test_ch04_structure.py:83`. |
| `mise run challenge:reset <NN>` | File-copy of stubs; not a dbt command. |
| `mise run setup:databricks` | One-time OAuth/PAT auth bootstrap; not a dbt command. |

### 7. Parity with the offline test contract

`tests/challenges/offline` (81 tests) locks the current challenge contracts. The rewrite is
compatible **with essentially no test edits**, provided the constraints below hold — each is
an existing assertion:

- Keep the five `challenge:*` mise tasks defined (`test_mise_tasks.py:16`,
  `test_verify_scripts.py:49,65`).
- Keep `verify.sh` on the wrapper — no raw `dbt ... --profiles-dir` in verify scripts
  (`test_verify_scripts.py:9-10`).
- Keep `mise run challenge:verify 04` in the 04 README; no `bash verify.sh`
  (`test_ch04_structure.py:81-83`).
- Keep `dbt_profiles/profiles.yml` in place for 02 and 04 (`test_ch02.py:41`,
  `test_ch04_structure.py:10`) — the project-dir `profiles.yml` adds, never moves.
- ~~No `--inline` in any README~~ — **LIFTED 2026-08-03.** That ban existed because
  `mise run challenge:dbt 02 -- show --inline "<SQL>"` pushes the SQL through a mise
  variadic that word-splits on spaces (`UsageError("Got unexpected extra arguments (1 as a,
  2 as b')")`). Raw `dbt show --inline "..."` quotes correctly — verified side by side in
  one shell. Since this design removes the wrapper from the guides, the constraint no longer
  applies to them. The test is rescoped to
  `test_guide_never_pairs_inline_sql_with_the_mise_wrapper`, which bans `--inline` only on
  lines that also invoke `challenge:dbt`. Challenge 02 now uses
  `dbt show --inline "select * from {{ source('custodian', 'holdings_raw') }}" --limit 5`
  for its raw-data peek, because the previous `dbt show --select holdings_raw --limit 5`
  **re-ran the seed** (a write) and returned 8 rows instead of 5.
- READMEs stay ≥6000 bytes with their key concept terms and no preflight-runner framing
  (`test_guides.py`). Current sizes are 54 KB / 62 KB / 65 KB, so shortening commands is
  immaterial.

**No offline test asserts that a README *contains* `mise run challenge:dbt` or
`challenge:seed`** — `test_guides.py`'s "swap commands for `mise run`" is a code comment,
not an assertion — so replacing those commands with raw `dbt` needs no test change.
**Optional lock-in (recommended):** add assertions that each converted README contains raw
`dbt ` teaching commands and does **not** contain `mise run challenge:dbt` /
`challenge:seed`, converting the new convention into an enforced contract. This is an
enhancement, not required for parity.

## Verification strategy

Verification maps onto the existing testing pyramid
(`2026-07-29-training-challenge-testing-framework-design.md`), not a parallel scheme:

- **L1 (offline, no creds):** `pytest tests/challenges/offline tests/local_env/offline`
  stays green under the constraints in §7 (plus any optional new locks).
- **L2 (cold toolchain + parse):** per-project `dbt deps` / `dbt parse` already run raw dbt
  in CI; the converted commands reuse that exact path.
- **L3 / L4 (cold end-to-end / manual — the "business-user subagent" runs):** subagents
  with a business-user persona (new to Databricks/dbt/Airflow) work each challenge
  end-to-end in the devcontainer, typing **only** the commands from the guide, in order
  02 → 03 → 04 (04 last for `dbt deps` + snapshots + incrementals + local package).
  - **Per-command intent verification (the acceptance bar).** A green `challenge:verify` is
    necessary but not sufficient. For **every** command the guide tells a trainee to run —
    raw `dbt`, the retained `mise run challenge:*`, and the `astro`/shell commands in 03 —
    the agent confirms the command *achieves its documented purpose*: it fails when it is
    meant to fail and succeeds when it is meant to succeed, and the observed output matches
    what the guide says (not merely exit 0). The agent records a **per-command verification
    matrix**: command → intended purpose → expected signal (pass/fail plus the key output
    the guide promises, e.g. `PASS=4`, `OK created sql view model`, five rows, freshness
    PASS/STALE) → observed → verdict.
  - **Red→green per command, using the shipped states.** Where a command's correct outcome
    depends on solution state, the agent exercises **both**: run it against the unsolved
    stub and confirm the intended **RED** (an unsolved `dbt build`/`run`/`test` must fail —
    that is the learner signal), then reach the solved state (author per the guide, or copy
    the shipped `solution/`) and confirm the intended **GREEN**. `mise run challenge:reset
    <NN>` restores the stub state. This proves each command's fail *and* pass behavior,
    echoing the testing-framework principle that "a guard that has never gone red proves
    nothing."
  - **Exercise the negative steps.** The guides' deliberate "try a variation" / break-it
    steps and the fresh-non-mise-shell token check must be run and confirmed to fail with
    the described signal, then recovered.
  - Any command whose observed behavior does not match its intended purpose is a **defect**
    fixed before sign-off — by correcting the guide command, adding the missing
    expected-result note, or (only if a specific 04 model genuinely needs the wrapper's
    caspian patch) keeping that one command on `mise` as a documented, explained exception.

## Risks and mitigations

- **Empty token in a non-interactive / mid-setup shell (surface B).** Mitigated by the
  interactive prompt-hook populating the token, Challenge 00's preflight, the `dbt debug`
  first step, and the troubleshooting note. Residual: a trainee who opens a terminal before
  `postCreate` finishes; the note tells them to reopen the terminal.
- **Challenge 04 transitive caspian macro use.** Models grep clean, but the `shared`
  package is installed via `dbt deps`; an indirectly invoked macro needing
  `modules.get('caspian')` could fail under raw dbt. Mitigated by testing 04 first and the
  documented single-command mise fallback.
- **Symlink portability.** ~~Fine on the Linux devcontainer (the supported path). Windows
  *native* checkouts may not honor symlinks; trainees use the container, and the manual L4
  check covers it. Fallback if undesirable: a committed copy of `profiles.yml` per project
  dir (accepts minor drift risk).~~
  **THIS RISK MATERIALIZED — 2026-08-03, severity Critical.** The reasoning was wrong in one
  step: trainees use the container, but they *clone on Windows*, and the container
  bind-mounts that Windows working tree. Git for Windows checked the symlinks out as text
  files and both Challenge 02 and Challenge 04 died on their first command. The named
  fallback (committed copy per project dir) has been adopted, and the drift risk it accepts
  is now covered by tests rather than left implicit. A repo-wide guard bans tracked symlinks
  outright. See `docs/rca/2026-08-03-profiles-symlink-windows.md`.
  *Lesson for future designs in this repo: "the devcontainer is Linux" does not make a
  Windows checkout concern go away, because the source of truth on disk is the host's.*
- **`dbt` resolving to a venv without dbt-databricks.** Both `.venv` and `/opt/venv` are
  provisioned by `setup-python-deps.sh`; L2/L3 confirm on both arches.
- **Hardcoded workspace defaults in profiles.** With defaults present, a missing-env raw
  dbt could connect to the default workspace and fail deep rather than fast. This is a
  pre-existing condition; the testing-framework design already tracks removing the defaults
  as a Challenge-00 hardening item. Out of scope here; cross-referenced so it is not lost.

## Acceptance criteria

- Challenges 02, 03, 04 READMEs teach raw `dbt` for all previously `mise`-wrapped
  interactive dbt/seed commands; `dbt debug` opens each; 04 includes `dbt deps`.
- `profiles.yml` **copies** exist in the 02 and 04 project dirs and match the canonical
  `dbt_profiles/profiles.yml` byte for byte (originally specified as symlinks; superseded —
  see §3).
- `mise run challenge:verify <NN>`, `challenge:reset`, and `setup:databricks` are unchanged;
  the `challenge:dbt` / `challenge:seed` tasks remain defined.
- `pytest tests/challenges/offline`, `mise run verify:local-dev`, and
  `pre-commit run --all-files` are green.
- A business-user subagent completes 02, 03, and 04 following only the guide's commands and
  ends green on each `challenge:verify`; **and** its per-command verification matrix shows
  every command achieved its documented purpose — each intended-fail command went RED with
  the expected signal and each intended-pass command went GREEN with the promised output,
  evidenced by observed output rather than exit code alone.

## Rollout / sequencing (feeds the implementation plan)

1. Add the two project-dir `profiles.yml` copies (originally symlinks — see §3).
2. Convert the 02 README (largest dbt surface; self-contained seeds).
3. Convert the 03 README (only 4 dbt + 1 seed command; mostly Airflow).
4. Convert the 04 README (add `dbt deps`; snapshots/incrementals/local package).
5. (Optional) add offline-test locks for the raw-dbt convention.
6. Run L1 offline + `verify:local-dev` + `pre-commit`; then L3/L4 subagent runs 02→03→04.
