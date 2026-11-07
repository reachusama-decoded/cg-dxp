# Raw dbt Commands in the Training Challenges — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `mise`-wrapped dbt *teaching* commands (`mise run challenge:dbt`, `mise run challenge:seed`) in challenges 02, 03, and 04 with raw `dbt` commands a trainee types from inside the dbt project, so trainees build muscle memory with real dbt.

**Architecture:** Trainees `cd` into each challenge's dbt project once, then run bare `dbt ...` commands. Bare `dbt` finds `profiles.yml` in the current directory; challenge 03 already ships it there, so challenges 02 and 04 get a `profiles.yml` symlink into their project dir pointing at the existing `dbt_profiles/profiles.yml`. The learner gate (`challenge:verify`), `challenge:reset`, and `setup:databricks` stay on `mise` and are unchanged. Each README change is locked by new assertions in the existing `tests/challenges/offline` suite (TDD: assertion first, then edit the README to green).

**Tech Stack:** Markdown guides, dbt-core 1.11 / dbt-databricks 1.11, `mise` tasks, `pytest` (`tests/challenges/offline`), git worktrees. Design spec: `docs/superpowers/specs/2026-07-31-challenge-raw-dbt-commands-design.md`.

> **Post-implementation note (2026-08-03).** This plan executed as written. A subsequent
> end-to-end trainee walkthrough on a **Windows** host then found that two of its Global
> Constraints were themselves wrong, and both have since been reversed. The plan text below
> is kept as the historical record of what was executed; the corrected decisions live in the
> design spec (§3, Constraints, Risks) and in the RCAs.
>
> 1. **The `profiles.yml` symlinks are now committed copies.** Git for Windows defaults to
>    `core.symlinks=false`, so the tracked symlinks were checked out as plain text files
>    containing the target path. `dbt debug` — the *first* command of Challenge 02 — died
>    with `AttributeError: 'str' object has no attribute 'get'`. Challenge 04 failed the same
>    way. The design spec's own named fallback (a committed copy per project dir) was
>    adopted; drift is now covered by tests, and a repo-wide guard bans tracked symlinks.
>    → `docs/rca/2026-08-03-profiles-symlink-windows.md`
>
> 2. **"No `--inline` anywhere in any README" is lifted.** That constraint was inherited from
>    the `mise` wrapper, which word-splits variadic args — the very wrapper this plan removes
>    from the guides. Raw `dbt show --inline "..."` works correctly. The test is rescoped to
>    ban `--inline` only when paired with `challenge:dbt`. Challenge 02's raw-data peek now
>    uses `--inline` with `source()`, because the previous `dbt show --select holdings_raw`
>    silently **re-ran the seed** and ignored `--limit`.
>    → `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md`
>
> Also note: the constraint **"Do not change … the content of any `profiles.yml`"** was
> correct in scope for this plan but concealed a latent defect it could not see —
> `data_products/atlas_elt`'s profile was missing `_disable_pandas: true`, so every
> row-returning dbt command in Challenge 04 segfaulted (exit 139, frequently silent). Fixed
> and now enforced by `tests/local_env/offline/tooling/test_dbt_profiles_disable_pandas.py`.
> → `docs/rca/2026-08-03-challenge-04-dbt-segfault.md`

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from the design spec; they are the parity contract enforced by `tests/challenges/offline`.

- **Work on branch `feature/improvements`** in the regular repo checkout (the design spec `e8dfab1` and this plan `56cef5f` are already on it; the earlier `.worktrees/improvements` worktree has been removed). Run all commands from the repo root unless a step says otherwise.
- **Keep all five `challenge:*` mise tasks defined** in `.mise.toml`: `challenge:verify`, `challenge:verify-all`, `challenge:dbt`, `challenge:seed`, `challenge:reset`. Do **not** delete or rename them (locked by `tests/challenges/offline/test_mise_tasks.py:16`, `test_verify_scripts.py:49,65`).
- **Do not change** `dbt_wrapper.py`, any `verify.sh`, the **content** of any `profiles.yml`, model SQL, seeds, stubs, or solutions.
- **Do not move** `dbt_profiles/profiles.yml` for challenge 02 or 04 — only *add* a `profiles.yml` symlink into the project dir (locked by `test_ch02.py:41`, `test_ch04_structure.py:10`). **[SUPERSEDED 2026-08-03 — now a committed copy, not a symlink; see the post-implementation note above.]**
- **Keep `mise run challenge:verify <NN>` and `mise run challenge:reset <NN>`** visible in each README. For challenge 04, `mise run challenge:verify 04` must be present and `bash verify.sh` must be absent (locked by `test_ch04_structure.py:72-83`).
- **No `--inline` anywhere in any README** (locked by `test_ch02.py`, `test_ch03.py`, `test_ch04_structure.py`). **[LIFTED 2026-08-03 — the ban was a `mise`-wrapper constraint; raw `dbt --inline` works. Test rescoped to `test_guide_never_pairs_inline_sql_with_the_mise_wrapper`; see the post-implementation note above.]**
- **READMEs stay ≥6000 bytes**, keep their key concept terms, and contain no preflight-runner framing tokens (`verify-with-databricks.sh`, `START_HERE`, `RUN.md`, `Preflight note`, `\newpage`) (locked by `test_guides.py`). Current sizes are 54 KB / 62 KB / 65 KB, so this is never at risk.
- **Drop `--target local`** from trainee commands (the wrapper added it; the profiles' default `target: dev` is byte-identical to `local`). `verify.sh` keeps `--target local` unchanged.
- **Challenge 03's seed step stays on mise.** It is `mise run challenge:seed 02` (line ~140) — a cross-challenge data-provisioning prerequisite that seeds *challenge 02's* project into the shared schema. Converting it would force a confusing cross-directory `cd`; it is not a dbt-authoring lesson. Keep it as-is (documented exception).
- **Auth prerequisite is unchanged:** trainees run `mise run setup:databricks` once; every `dbt` command assumes an interactive devcontainer shell where mise's prompt-hook has loaded the environment.
- **Test environment is the devcontainer.** Run `pytest tests/challenges/offline` there (credential-free; it only reads files and strings).
- **Per-command intent is the acceptance bar (Task 4).** Beyond a green `challenge:verify`, *every* command the guide tells a trainee to run must be verified to achieve its documented purpose: it fails when it is meant to fail (unsolved stub build/run/test, a data-quality test catching a broken model, a STALE freshness state, a deliberate "try a variation" break) and succeeds when it is meant to succeed, with observed output matching the guide — not merely exit 0.
- **Preserve expected-result prose.** The conversion changes only the command prefix (`mise run challenge:dbt <NN> -- ` → `dbt `); keep every surrounding "expected result" statement (e.g. "the build should report `PASS=4`", "returns five funds", "OK created sql view model") so Task 4 can check each command against a documented outcome. Where a command block states no expected outcome, Task 4 adds a one-line `Expected:` note as it verifies.

## File Structure

Files created or modified, by responsibility:

- `challenges/02-dbt-pipeline/dbt/profiles.yml` — **create** (symlink → `../dbt_profiles/profiles.yml`). Enables bare `dbt` from the 02 project dir.
- `challenges/02-dbt-pipeline/README.md` — **modify**. Convert 44 wrapped dbt/seed commands to raw dbt; add a `cd` + `dbt debug` setup block and a token-troubleshooting note.
- `tests/challenges/offline/test_ch02.py` — **modify**. Add two assertions (symlink discoverable; guide uses raw dbt, not the wrapper).
- `challenges/03-airflow-orchestration/README.md` — **modify**. Convert the 4 `challenge:dbt 03` peeks to raw dbt; add a `cd` note; keep the mise seed step; add a troubleshooting note.
- `tests/challenges/offline/test_ch03.py` — **modify**. Add one assertion (peeks use raw dbt; seed/gate/reset stay on mise).
- `data_products/atlas_elt/profiles.yml` — **create** (symlink → `dbt_profiles/profiles.yml`). Enables bare `dbt` from the 04 project dir.
- `challenges/04-atlas-capstone/README.md` — **modify**. Convert 36 wrapped dbt commands to raw dbt; replace the Quick start with a `cd` + `dbt deps` setup block; add a troubleshooting note.
- `tests/challenges/offline/test_ch04_structure.py` — **modify**. Add two assertions (symlink discoverable; guide uses raw dbt + `dbt deps`).

Tasks are ordered simplest→riskiest (02 → 03 → 04) so early tasks de-risk the mechanical recipe before the capstone. A final task runs the whole-repo parity gate and settles the one runtime unknown (mise task cwd) in the devcontainer.

---

### Task 1: Challenge 02 → raw dbt (symlink + guide + test lock)

**Files:**
- Create: `challenges/02-dbt-pipeline/dbt/profiles.yml` (symlink)
- Modify: `challenges/02-dbt-pipeline/README.md`
- Test: `tests/challenges/offline/test_ch02.py`

**Interfaces:**
- Consumes: existing `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml` (unchanged).
- Produces: the raw-dbt convention (`cd challenges/02-dbt-pipeline/dbt` then bare `dbt ...`) and the two new test names `test_ch02_profiles_discoverable_in_project_dir`, `test_ch02_guide_uses_raw_dbt_not_mise_wrapper` reused as the pattern for Tasks 2–3.

- [ ] **Step 1: Write the failing tests**

Append to `tests/challenges/offline/test_ch02.py` (the module already defines `CH = repo_root() / "challenges" / "02-dbt-pipeline"`):

```python
def test_ch02_profiles_discoverable_in_project_dir() -> None:
    # Why: trainees cd into dbt/ and run bare `dbt build`; dbt resolves profiles.yml
    # from the current directory. A profiles.yml in the project dir (a symlink to
    # ../dbt_profiles/profiles.yml) enables that, while dbt_profiles/profiles.yml stays
    # in place for verify.sh and the existing tests.
    proj = CH / "dbt" / "profiles.yml"
    canonical = CH / "dbt_profiles" / "profiles.yml"
    assert proj.exists(), "challenges/02-dbt-pipeline/dbt/profiles.yml must exist"
    assert proj.read_text() == canonical.read_text(), "project-dir profiles.yml must match dbt_profiles/profiles.yml"


def test_ch02_guide_uses_raw_dbt_not_mise_wrapper() -> None:
    # Why: the challenge teaches real dbt, so the guide's dbt/seed commands are raw
    # `dbt ...`, not the mise wrapper. The verify gate and reset stay on mise.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt" not in text
    assert "mise run challenge:seed" not in text
    assert "dbt debug" in text and "dbt seed" in text and "dbt build" in text
    assert "mise run challenge:verify 02" in text
    assert "mise run challenge:reset 02" in text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/challenges/offline/test_ch02.py -k "raw_dbt or discoverable" -q`
Expected: FAIL — `test_ch02_profiles_discoverable_in_project_dir` fails (no `dbt/profiles.yml`), and `test_ch02_guide_uses_raw_dbt_not_mise_wrapper` fails (`mise run challenge:dbt` still present).

- [ ] **Step 3: Create the profiles symlink**

Run:
```bash
ln -s ../dbt_profiles/profiles.yml challenges/02-dbt-pipeline/dbt/profiles.yml
readlink challenges/02-dbt-pipeline/dbt/profiles.yml    # expect: ../dbt_profiles/profiles.yml
head -1 challenges/02-dbt-pipeline/dbt/profiles.yml     # expect: portfolio_analytics_challenge:
```

- [ ] **Step 4: Convert the guide's dbt/seed commands to raw dbt (bulk)**

Run (from the repo root):
```bash
F=challenges/02-dbt-pipeline/README.md
perl -0pi -e 's/\Qmise run challenge:dbt 02 -- \E/dbt /g' "$F"
perl -0pi -e 's/\Qmise run challenge:seed 02\E/dbt seed/g' "$F"
```

- [ ] **Step 5: Apply the manual structural edits**

Edit 5a — remove the bare wrapper mention in the intro paragraph. Replace:
```
build individual models with `challenge:dbt` before your first verify.
```
with:
```
build individual models before your first verify.
```

Edit 5b — add the setup block. The intro paragraph ends with "…before your first verify." Immediately after that paragraph (before the `---` divider), insert:
```markdown

**Work from the dbt project folder.** Every `dbt` command in this guide runs from the challenge's dbt project. Move into it once per terminal session and check your connection:

```bash
cd challenges/02-dbt-pipeline/dbt
dbt debug          # confirms your Databricks connection
```

Run `mise run challenge:verify 02` and `mise run challenge:reset 02` from anywhere in the repo; run the raw `dbt` commands from this folder.

> **dbt can't find your credentials?** (e.g. `Runtime Error ... auth_type: oauth is required when not using access token`.) Your shell environment is not loaded. Open a fresh terminal so mise initializes the environment, or re-run `mise run setup:databricks`, then retry. Every `dbt` command assumes you ran `mise run setup:databricks` once.
```

- [ ] **Step 6: Verify the conversion mechanically**

Run:
```bash
F=challenges/02-dbt-pipeline/README.md
grep -c "mise run challenge:dbt" "$F"     # expect 0
grep -c "mise run challenge:seed" "$F"    # expect 0
grep -c "mise run challenge:verify 02" "$F"  # expect >= 1
grep -c "mise run challenge:reset 02" "$F"   # expect >= 1
grep -c -- "--inline" "$F"                # expect 0
test "$(wc -c < "$F")" -ge 6000 && echo "size ok"
```
Expected: the counts match the comments and `size ok` prints.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `pytest tests/challenges/offline/test_ch02.py -q`
Expected: PASS (all — the two new tests plus every pre-existing `test_ch02` assertion, confirming no parity regression).

- [ ] **Step 8: Commit**

```bash
git add challenges/02-dbt-pipeline/dbt/profiles.yml challenges/02-dbt-pipeline/README.md tests/challenges/offline/test_ch02.py
git commit -m "challenge-02: teach raw dbt instead of the mise wrapper

Add a project-dir profiles.yml symlink so bare 'dbt build' works after
cd into challenges/02-dbt-pipeline/dbt, convert the guide's dbt/seed
commands to raw dbt, and lock the convention in test_ch02.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Challenge 03 → raw dbt peeks (guide + test lock)

**Files:**
- Modify: `challenges/03-airflow-orchestration/README.md`
- Test: `tests/challenges/offline/test_ch03.py`

**Interfaces:**
- Consumes: the raw-dbt convention from Task 1. No symlink needed — challenge 03's `profiles.yml` already ships in its project dir (`data_products/portfolio_analytics/dbt/profiles.yml`).
- Produces: test name `test_ch03_guide_uses_raw_dbt_for_peeks`.

- [ ] **Step 1: Write the failing test**

Append to `tests/challenges/offline/test_ch03.py` (the module already defines `CH = repo_root() / "challenges" / "03-airflow-orchestration"`):

```python
def test_ch03_guide_uses_raw_dbt_for_peeks() -> None:
    # Why: challenge 03 is an Airflow challenge; its dbt commands are read-only peeks
    # (debug, show, source freshness) the trainee runs directly with raw dbt from
    # data_products/portfolio_analytics/dbt. The cross-challenge seed provisioning
    # (mise run challenge:seed 02) and the verify/reset gate stay on mise.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt 03" not in text
    assert "dbt debug" in text
    assert "dbt source freshness" in text
    assert "mise run challenge:seed 02" in text
    assert "mise run challenge:verify 03" in text
    assert "mise run challenge:reset 03" in text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch03.py::test_ch03_guide_uses_raw_dbt_for_peeks -q`
Expected: FAIL — `mise run challenge:dbt 03` is still present.

- [ ] **Step 3: Convert the 4 dbt peeks to raw dbt (bulk)**

Run:
```bash
F=challenges/03-airflow-orchestration/README.md
perl -0pi -e 's/\Qmise run challenge:dbt 03 -- \E/dbt /g' "$F"
```
Note: do **not** touch `mise run challenge:seed 02` (line ~140) — it stays on mise per Global Constraints.

- [ ] **Step 4: Add the project-dir note before the first dbt peek**

The first converted command is `dbt debug` (was `mise run challenge:dbt 03 -- debug`, ~line 286). Immediately before its fenced code block, insert this sentence on its own line:
```markdown
Run these dbt peeks from the dbt project folder — `cd data_products/portfolio_analytics/dbt` once, then run the `dbt` commands below. (`mise run challenge:seed 02` and the `mise run challenge:*` gate/reset commands run from anywhere in the repo.)

> **dbt can't find your credentials?** (e.g. `Runtime Error ... auth_type: oauth is required when not using access token`.) Your shell environment is not loaded. Open a fresh terminal so mise initializes the environment, or re-run `mise run setup:databricks`, then retry.
```

- [ ] **Step 5: Verify the conversion mechanically**

Run:
```bash
F=challenges/03-airflow-orchestration/README.md
grep -c "mise run challenge:dbt" "$F"       # expect 0
grep -c "mise run challenge:seed 02" "$F"   # expect 1 (kept)
grep -c "mise run challenge:verify 03" "$F" # expect >= 1
grep -c -- "--inline" "$F"                  # expect 0
grep -c "astro dev run" "$F"                # expect >= 1 (unchanged Airflow commands)
test "$(wc -c < "$F")" -ge 6000 && echo "size ok"
```
Expected: counts match; `size ok` prints.

- [ ] **Step 6: Run the offline suite for challenge 03**

Run: `pytest tests/challenges/offline/test_ch03.py -q`
Expected: PASS (new test plus all pre-existing ch03 assertions — `--inline` absence, `DatabricksTokenProfileMapping`, `astro dev run`, no `astro dev parse`, etc.).

- [ ] **Step 7: Commit**

```bash
git add challenges/03-airflow-orchestration/README.md tests/challenges/offline/test_ch03.py
git commit -m "challenge-03: teach raw dbt for the pipeline peeks

Convert the four challenge:dbt 03 peeks (debug/show/source freshness) to
raw dbt run from data_products/portfolio_analytics/dbt; keep the
cross-challenge seed provisioning and the verify/reset gate on mise.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Challenge 04 → raw dbt + `dbt deps` (symlink + guide + test lock)

**Files:**
- Create: `data_products/atlas_elt/profiles.yml` (symlink)
- Modify: `challenges/04-atlas-capstone/README.md`
- Test: `tests/challenges/offline/test_ch04_structure.py`

**Interfaces:**
- Consumes: the raw-dbt convention from Tasks 1–2.
- Produces: test names `test_ch04_profiles_discoverable_in_project_dir`, `test_ch04_guide_uses_raw_dbt_and_deps`.
- Note the module constants: `AE = data_products/atlas_elt` (the project dir + a separate mapping README), `CH = challenges/04-atlas-capstone` (the trainee guide being converted).

- [ ] **Step 1: Write the failing tests**

Append to `tests/challenges/offline/test_ch04_structure.py`:

```python
def test_ch04_profiles_discoverable_in_project_dir() -> None:
    # Why: trainees cd into data_products/atlas_elt and run bare `dbt build`; dbt
    # resolves profiles.yml from the current directory. A profiles.yml symlink into
    # the project dir enables that; dbt_profiles/profiles.yml stays for verify.sh,
    # the bundle, and mise run dbt:*.
    proj = AE / "profiles.yml"
    canonical = AE / "dbt_profiles" / "profiles.yml"
    assert proj.exists(), "data_products/atlas_elt/profiles.yml must exist"
    assert proj.read_text() == canonical.read_text(), "project-dir profiles.yml must match dbt_profiles/profiles.yml"


def test_ch04_guide_uses_raw_dbt_and_deps() -> None:
    # Why: the capstone teaches real dbt; the guide runs raw dbt from the project dir
    # and installs the local 'shared' package with `dbt deps`. The verify gate and
    # reset stay on mise.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt" not in text
    assert "mise run challenge:seed" not in text
    assert "dbt deps" in text
    assert "dbt build" in text
    assert "mise run challenge:verify 04" in text
    assert "mise run challenge:reset 04" in text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -k "raw_dbt or discoverable" -q`
Expected: FAIL — no `data_products/atlas_elt/profiles.yml`, and `mise run challenge:dbt` still present.

- [ ] **Step 3: Create the profiles symlink**

Run:
```bash
ln -s dbt_profiles/profiles.yml data_products/atlas_elt/profiles.yml
readlink data_products/atlas_elt/profiles.yml     # expect: dbt_profiles/profiles.yml
head -1 data_products/atlas_elt/profiles.yml       # expect: atlas_elt:
git status --short data_products/atlas_elt/profiles.yml   # expect: 'A' or '??' (not ignored); if ignored, use: git add -f
```

- [ ] **Step 4: Replace the Quick start block with a cd + `dbt deps` setup block**

Replace this exact block (it is the current Quick start, after the `perl` step it is unchanged because it will be replaced wholesale here — do this replacement **before** Step 5):
```bash
# Reset stubs to the original placeholder state:
mise run challenge:reset 04

# dbt commands — run these from the repo root:
mise run challenge:dbt 04 -- parse
mise run challenge:dbt 04 -- build
mise run challenge:dbt 04 -- test

# Verify your work:
mise run challenge:verify 04
```
with:
```bash
# 1. Reset stubs to the original placeholder state (from the repo root):
mise run challenge:reset 04

# 2. Move into the dbt project and install its local 'shared' package (first time only):
cd data_products/atlas_elt
dbt deps

# 3. Build and test the pipeline (run these from data_products/atlas_elt):
dbt parse
dbt build
dbt test

# 4. Verify your work (mise commands run from anywhere in the repo):
mise run challenge:verify 04
```

Then, immediately after that code block, add the troubleshooting note:
```markdown
> **dbt can't find your credentials?** (e.g. `Runtime Error ... auth_type: oauth is required when not using access token`.) Your shell environment is not loaded. Open a fresh terminal so mise initializes the environment, or re-run `mise run setup:databricks`, then retry. Every `dbt` command assumes you ran `mise run setup:databricks` once.
```

- [ ] **Step 5: Convert the remaining guided dbt commands to raw dbt (bulk)**

Run:
```bash
F=challenges/04-atlas-capstone/README.md
perl -0pi -e 's/\Qmise run challenge:dbt 04 -- \E/dbt /g' "$F"
```

- [ ] **Step 6: Verify the conversion mechanically**

Run:
```bash
F=challenges/04-atlas-capstone/README.md
grep -c "mise run challenge:dbt" "$F"        # expect 0
grep -c "mise run challenge:seed" "$F"       # expect 0
grep -c "mise run challenge:verify 04" "$F"  # expect >= 1
grep -c "bash verify.sh" "$F"                # expect 0
grep -c "dbt deps" "$F"                      # expect >= 1
grep -c -- "--inline" "$F"                   # expect 0
test "$(wc -c < "$F")" -ge 6000 && echo "size ok"
```
Expected: counts match; `size ok` prints.

- [ ] **Step 7: Run the offline suite for challenge 04**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -q`
Expected: PASS (new tests plus pre-existing ones, including `test_ch04_guide_verifies_only_via_mise` which requires `mise run challenge:verify 04` and forbids `bash verify.sh`).

- [ ] **Step 8: Commit**

```bash
git add data_products/atlas_elt/profiles.yml challenges/04-atlas-capstone/README.md tests/challenges/offline/test_ch04_structure.py
git commit -m "challenge-04: teach raw dbt with dbt deps instead of the mise wrapper

Add a project-dir profiles.yml symlink, replace the Quick start with a
cd + dbt deps setup block, convert the guided commands to raw dbt, and
lock the convention in test_ch04_structure. Verify gate stays on mise.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: Whole-repo parity gate + runtime confirmation + per-command E2E acceptance

**Files:** none created (except any `Expected:` notes added to READMEs in Step 4); this task verifies the change end-to-end and records the runtime confirmation. Runs in the **devcontainer**.

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: a green offline suite, a confirmed answer to the mise-task-cwd question, and a completed **per-command verification matrix** per challenge proving each command achieves its intended purpose (correct fail/succeed semantics), plus any guide fixes that matrix surfaces.

- [ ] **Step 1: Run the full offline challenge suite**

Run: `pytest tests/challenges/offline -q`
Expected: PASS — all tests (81 pre-existing + 5 new) green. If any pre-existing test fails, a Global Constraint was violated; fix the offending README/edit before proceeding.

- [ ] **Step 2: Run the native parity gates**

Run:
```bash
pre-commit run --all-files
mise run verify:local-dev
```
Expected: both green (unchanged from before the change). `verify:local-dev` needs Databricks auth — run `mise run setup:databricks` first if `dpc-check` is not green.

- [ ] **Step 3: Confirm mise tasks run correctly from a project subdirectory**

This settles the one runtime assumption in the guides (that `mise run challenge:verify`/`reset` work while the trainee is `cd`'d into a project dir). From the devcontainer:
```bash
cd challenges/02-dbt-pipeline/dbt
mise run challenge:reset 02      # copies stubs over the working tree; on a clean tree this is a no-op
cd -
git status --short               # expect: no unexpected changes
```
Expected: the task runs from the subdirectory without a path error (mise executes tasks from the config root).
- If it **succeeds**: the guides' "mise commands run from anywhere in the repo" wording is correct — no change needed.
- If it **fails** with a path error: edit the three READMEs so the `mise run challenge:verify/reset` steps say "run from the repo root (`cd` back first)", and re-run `pytest tests/challenges/offline -q`. Then commit the wording fix.

- [ ] **Step 4: Execute the business-user E2E validation with per-command intent checks (the acceptance test)**

Dispatch business-user-persona subagents (new to Databricks/dbt/Airflow) to work each challenge end-to-end in the devcontainer, typing **only** the commands printed in the converted READMEs, in order 02 → 03 → 04. A green `challenge:verify` is necessary but **not** sufficient — validate every command's intended purpose:

4a. **Build the per-command verification matrix.** Before running, walk the guide top to bottom and list *every* command the trainee runs (raw `dbt`, the retained `mise run challenge:*`, and the `astro`/shell commands in 03). For each, record its **intended purpose** and **expected signal** — the pass/fail outcome plus the key output the guide promises (e.g. `PASS=4`; `OK created sql view model` = a view; five rows; `dbt debug` "All checks passed"; `source freshness` PASS on fresh feeds; an unsolved model build = FAIL). Where the guide states no checkable outcome for a command, add a one-line `Expected:` note to that command block in the README as part of this task.

4b. **Run each command and confirm it matches — fail *and* pass.** Execute the guide in order and record the observed result against the matrix. A command passes verification only when its observed behavior matches its intent, including intended failures:
- Commands meant to succeed produce the promised output (not just exit 0).
- Commands meant to fail actually fail with the described signal. Exercise these explicitly using the shipped states: from a reset stub (`mise run challenge:reset <NN>`), confirm an unsolved `dbt build`/`run`/`test` goes **RED**; then reach the solved state (author the model per the guide, or copy the matching `solution/` files) and confirm the same command goes **GREEN**. Also run the guide's deliberate "try a variation" / break-it steps and the fresh-**non-mise**-shell credential check, confirming each fails as described and the troubleshooting note recovers it.

4c. **Fix every mismatch before sign-off.** Any command whose observed behavior does not match its documented purpose is a defect: correct the guide command, add/repair the `Expected:` note, or — only if a specific challenge-04 model genuinely requires the wrapper's caspian patch — keep that one command on `mise run challenge:dbt 04 -- …` as a documented, explained exception. Re-run the affected command after the fix.

Deliverable: the completed matrix per challenge (every command → intended purpose → expected → observed → PASS), plus `challenge:verify` green for 02, 03, 04.

- [ ] **Step 5: Commit any guide corrections from Steps 3–4**

```bash
git add -A
git commit -m "challenges: fix raw-dbt guide wording from devcontainer + E2E validation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**1. Spec coverage.** Every design-spec section maps to a task:
- §1 Scope / §2 command model → Tasks 1–3 (perl conversion + `cd` setup blocks; `--target local` dropped by construction since the wrapper added it, not the README).
- §3 Profile discovery → symlinks in Tasks 1 (02) and 3 (04); 03 needs none.
- §4 Auth/token reconciliation → `dbt debug` opener + troubleshooting note in each guide (Tasks 1–3); Challenge 00 preflight is pre-existing; the fresh-shell red→green check is Task 4 Step 4.
- §5 Challenge 04 `dbt deps` → Task 3 Step 4.
- §6 What stays on mise → enforced by Global Constraints + the "verify/reset" assertions in each test; 03 seed exception explicit.
- §7 Offline test parity → new locking assertions in Tasks 1–3; full suite gate in Task 4 Step 1.
- Goals "every command achieves its documented purpose" + Verification "per-command intent verification" + Acceptance per-command matrix → Global Constraints (per-command bar; preserve expected-result prose) and Task 4 Step 4 (matrix + red→green per command + fix mismatches).
- Verification strategy (L1/L2/L3/L4) → Task 4 (offline suite, native gates, E2E subagents with the per-command matrix).

**2. Placeholder scan.** No "TBD/TODO/handle edge cases/similar to Task N" — every step has the exact command, code, or edit text. (The literal string `# TODO` appears only inside quoted challenge-03 content, not as a plan instruction.)

**3. Type/name consistency.** New test names are distinct and referenced consistently: `test_ch02_profiles_discoverable_in_project_dir`, `test_ch02_guide_uses_raw_dbt_not_mise_wrapper`, `test_ch03_guide_uses_raw_dbt_for_peeks`, `test_ch04_profiles_discoverable_in_project_dir`, `test_ch04_guide_uses_raw_dbt_and_deps`. Module constants used match each test file (`CH` in ch02/ch03; `AE`+`CH` in ch04). Symlink relative targets are correct from each link's directory (`../dbt_profiles/profiles.yml` from `dbt/`; `dbt_profiles/profiles.yml` from `atlas_elt/`).
