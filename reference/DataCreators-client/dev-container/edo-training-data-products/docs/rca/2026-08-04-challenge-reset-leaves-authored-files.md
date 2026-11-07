# RCA — `challenge:reset` silently did not reset: trainee-created files, and warehouse state, both survived it

| Field | Value |
|---|---|
| **Date** | 2026-08-04 |
| **Status** | Root causes proven; file-scope fix implemented and verified live; warehouse-scope gap now disclosed rather than hidden |
| **Severity** | Medium — corrupts the starting state of a retried challenge, and does so silently |
| **Components** | `.mise.toml` task `challenge:reset` |
| **Discovered while** | Restoring the working tree after reproducing the Challenge 02 Phase 2 Challenge 2 failure (defect 1), and during a full beginner-trainee walkthrough of Challenge 02 (defect 2) |
| **Related** | `docs/rca/2026-08-04-challenge-02-eager-indirect-selection.md` (the investigation that surfaced this) |

---

## 1. Summary

`mise run challenge:reset <NN>` is documented as *"Reset all stubs to blank"* and is the trainee's
only way to start a challenge over. It has **two** independent gaps, both silent:

1. **It did not delete files the trainee creates from scratch.** The restore was a `cp` of the stub
   tree, and a copy can only overwrite paths that exist in the source. Challenge 02 asks the trainee
   to *create* three files that deliberately have no stub counterpart, so `cp` never touched them.
2. **It cannot reset the warehouse at all.** It is a file operation. Tables and views built by a
   previous attempt persist in the trainee's Databricks schema, and dbt **tests read those stored
   relations** — so a test on a model the trainee has not rebuilt in this attempt can pass against the
   previous attempt's data.

Both gaps share a failure mode: the command printed
`Reset challenges/02-dbt-pipeline/dbt working files to stubs.` and exited 0, so nothing signalled that
the reset was partial.

---

## 2. Impact / who was affected

**Defect 1 — surviving files.**

- **Any trainee who resets challenge 02 after reaching Section 8 or later.** They believe they are
  starting from a blank slate; in fact their previous answers to Section 8 and Challenge 10 are still
  present.
- The stale files are *live dbt nodes*, not inert leftovers. A surviving `staging/schema.yml` adds
  five tests to every subsequent `dbt build --select staging`, so the guide's stated
  `Done. PASS=5 ... TOTAL=5` becomes `TOTAL=10` and the trainee cannot match the documented output.
- A surviving capstone mart makes the project eleven models instead of ten, which contradicts the
  Section 2 reading exercise and changes the Challenge 7 full-build totals.

**Defect 2 — surviving warehouse state.**

- **Any trainee reusing the same Databricks schema across attempts**, which is everyone: the schema
  (`training_dev.training_<username>`) is pre-provisioned and personal, so it is the *same* schema on
  every attempt forever.
- Observed concretely during the walkthrough: at Challenge 2, `fct_portfolio_returns` was still a stub
  file, yet `describe table` showed the **full solution schema** (`fund_id`, `calc_nav_per_unit`, …)
  left behind by an earlier attempt. The `relationships` test therefore **passed** where a clean
  schema would have failed.
- The harm is specific and bounded: dbt *models* are recomputed from source at build time, so `dbt
  show --select <stub>` correctly returns `placeholder`. It is **tests** that read persisted relations,
  so tests are the surface where a previous attempt's data can produce a false green.

Both defects are **silent**. The task reports success, so the divergence is attributed to the user.

---

## 3. Symptoms

| What you see | What it actually means |
|---|---|
| Reset prints success, but `dbt build --select staging` reports `TOTAL=10` not `TOTAL=5` | A previous `models/staging/schema.yml` survived and is contributing 5 tests |
| `dbt ls` shows eleven models after a reset | The Challenge 10 capstone mart survived |
| Offline test `test_staging_schema_is_authored_solution_only` fails right after a reset | The file the test forbids in `dbt/` is still there |
| A test passes against a model whose file is still `select 1 as placeholder` | The **table** from a previous attempt is still in the warehouse; the test read that, not your stub |
| A second attempt at a challenge behaves differently from the first | The second attempt did not actually start clean |

---

## 4. Root cause

### 4.1 Defect 1 — the mechanism

The task's restore step was a single recursive copy:

```sh
cp -R "$DIR/stubs/." "$DIR/dbt/"
```

`cp -R src/. dst/` is **additive**: it creates or overwrites every path present in `src`, and leaves
every other path in `dst` untouched. That is the correct and desired behaviour for the working tree
as a whole — `dbt/` also holds `profiles.yml`, `target/`, `logs/` and `dbt_packages/`, none of which
appear in `stubs/` and all of which must survive. The defect is that the same property silently
protects the trainee's own creations.

### 4.2 Why these three files have no stub

This is deliberate, and encoded in the offline suite. `tests/challenges/offline/test_ch02.py`
asserts that both files are absent from `dbt/` and `stubs/` and present only in `solution/`:

- `test_staging_schema_is_authored_solution_only` — *"S8 is an authoring task … so the file must NOT
  ship in dbt/ or stubs/"*
- `test_capstone_is_created_in_c10_not_shipped` — *"C10 says 'Create' the capstone mart + its
  reconcile test … They live in solution/ only."*

So the guide has two distinct kinds of authoring task — **complete this stub** and **create this
file** — and the reset only ever handled the first kind.

### 4.3 Why a naive "delete everything not in stubs" would be worse

The obvious repair — clear the destination before copying — is unsafe here. For challenge 02 the
destination is the dbt project root, which legitimately contains files with no stub counterpart:
`profiles.yml` (provisioned so trainees can run bare `dbt` from the project dir), plus generated
`target/`, `logs/` and `dbt_packages/`. Deleting those would break the next `dbt` command and, in
`profiles.yml`'s case, would not be recoverable by re-running the reset.

The fix therefore needs a *precise* deletion set, not a broad one.

### 4.4 Defect 2 — why the warehouse is out of reach

`challenge:reset` is a shell task that copies and deletes local files. It holds no Databricks
connection, and acquiring one would change it from an offline convenience into a command that needs
authentication, a warehouse, and the right to drop relations in a shared catalog.

The deeper reason the gap is invisible is dbt's own model: **dbt is declarative about models and
stateful about relations.** `dbt build` recreates a model's relation from its SQL, so a rebuilt model
is always in sync with its file. But nothing removes the relation of a model that is *no longer
built*, and a `dbt test` targets the stored relation rather than recomputing the model. The reset
restores the declarations; the warehouse keeps the last materialisation of them.

---

## 5. How to reproduce

**Defect 1:**

```bash
cd challenges/02-dbt-pipeline/dbt
echo "version: 2"  > models/staging/schema.yml
echo "select 1"    > models/marts/agg_fund_daily_exposure.sql
echo "select 1"    > tests/reconcile_daily_exposure.sql
cd -
mise run challenge:reset 02
ls challenges/02-dbt-pipeline/dbt/models/staging/ challenges/02-dbt-pipeline/dbt/tests/
```

| Task version | Result |
|---|---|
| **Before fix** | All three files still present; reset reported success |
| **After fix** | All three removed; `stg_holdings.sql` back to its stub; `profiles.yml` and `target/` untouched |

**Defect 2** — after completing challenge 02 once:

```bash
mise run challenge:reset 02          # fct_portfolio_returns.sql is a stub again
cd challenges/02-dbt-pipeline/dbt
dbt show --inline "describe table <your_schema>.fct_portfolio_returns"
```

The table still has the full solution schema, not the single `placeholder` column its stub would
produce.

---

## 6. The fix

### 6.1 Defect 1 — prune the solution-minus-stubs difference

The set of files a trainee creates from scratch is exactly **the files present in `solution/` but
absent from `stubs/`**. That difference is derived at run time, so it needs no hard-coded list and
stays correct automatically if a future challenge adds another "create this file" task.

After the existing copy, `challenge:reset` now prunes that difference:

```sh
if [ -d "$SOLN_ROOT" ]; then
  ( cd "$SOLN_ROOT" && find . -type f ) | while IFS= read -r REL; do
    [ -e "$STUB_ROOT/$REL" ] || rm -f "$DEST/$REL"
  done
fi
```

`STUB_ROOT`, `SOLN_ROOT` and `DEST` are set per challenge in the branch that already selects the
destination, because challenge 04's trees are rooted at `stubs/datasets/` and
`solution/datasets/` rather than at the challenge root.

**Why this is safe.** The deletion set is bounded by the solution tree, so it can only ever contain
files the challenge itself authors. `profiles.yml`, `target/`, `logs/` and `dbt_packages/` are absent
from `solution/` and therefore can never be selected for deletion — the property is structural, not a
list that has to be maintained.

### 6.2 Defect 2 — disclose the boundary instead of pretending it does not exist

The reset now states plainly what it does and does not cover:

```
Note: files only. Tables/views from earlier attempts remain in your Databricks
      schema until a build overwrites them, so a test can still read old data.
      Run the challenge's full build (or 'mise run challenge:verify 02') to bring the
      warehouse back in line with your current files.
```

**Why disclosure rather than a warehouse drop.** Clearing the warehouse means dropping relations in a
pre-provisioned, personal-but-shared-catalog schema. That turns an offline file operation into a
destructive, authenticated one, and a mis-scoped drop is unrecoverable. The message also names the
remedy that already exists and is non-destructive: a full build re-materialises every model in the
project, which is precisely what `challenge:verify <NN>` runs. Given that the guide's own gate ends
with a full build, disclosure plus a pointer resolves the confusion without adding a dangerous
command.

### 6.3 Regression test

`tests/challenges/offline/test_ch02.py::test_reset_removes_files_the_trainee_creates_from_scratch`
extracts the real `challenge:reset` script from `.mise.toml` with `tomllib` and executes it against a
sandbox tree in `tmp_path`. It asserts both halves of the contract:

- the three trainee-created files are deleted, and a modified stub is restored to its stub content;
- `dbt/profiles.yml` and `dbt/target/run_results.json` **survive**, pinning the safety property so a
  future "just delete the destination" simplification cannot regress it.

Running the task's own script — rather than asserting on strings in `.mise.toml` — means the test
verifies behaviour and cannot pass against a broken implementation that happens to contain the right
words.

---

## 7. Verification (evidence)

| Check | Result |
|---|---|
| Three trainee-created files present, then `mise run challenge:reset 02` | All three removed |
| `models/staging/stg_holdings.sql` overwritten, then reset | Restored to `-- TODO(...)` + `select 1 as placeholder` |
| `dbt/profiles.yml` after reset | Still present |
| `dbt/target/` after reset | Still present |
| Reset output | Now discloses the warehouse boundary and names the remedy |
| Offline suite | 89 passed (88 pre-existing + 1 new regression test) |

---

## 8. Lessons

1. **"Copy the good state over the bad state" only resets what the good state contains.** Any reset
   built on `cp` is incomplete the moment the workflow can create a file the source tree lacks.
2. **A reset that cannot fail is a reset you cannot trust.** This one always printed success. Silent
   partial success is worse than a loud failure, because the damage is later attributed to the user.
3. **Derive the deletion set, do not enumerate it.** Using `solution/` minus `stubs/` means the next
   "create this file" task is handled with no change to the reset and no chance of a forgotten entry.
4. **Test the task, not the file that declares it.** The pre-existing test asserted a literal `cp`
   line was present in `.mise.toml`, which would have kept passing throughout this bug. Executing the
   extracted script is barely more code and actually checks the behaviour.
5. **Name the scope a command actually has.** "Reset" implied a clean slate across every surface the
   trainee can see. When a command cannot reach one of those surfaces, saying so is a fix — the
   confusion came from the silence, not from the limitation.
6. **dbt is declarative about models but stateful about relations.** Restoring the files restores the
   declarations, not the materialisations, and tests read materialisations.

---

## 9. Follow-ups

- Challenges 03 and 04 currently have identical file sets in `stubs/` and `solution/`, so they have no
  create-from-scratch files today and the prune is a no-op for them. The fix is already general, so
  they are covered if that changes.
- If warehouse drift proves to cause real trainee confusion in practice, the next step would be an
  explicitly-named, opt-in task (for example `challenge:reset-warehouse`) that drops only the relations
  the challenge's own manifest declares — bounded by the manifest rather than by the schema.

