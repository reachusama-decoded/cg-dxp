# Task 2 Report: Challenge 03 → raw dbt peeks

## Summary
Successfully converted challenge 03's four `mise run challenge:dbt 03` peek commands to raw `dbt` commands per TDD.

## Implementation Steps Completed

### Step 1: Write the failing test ✓
Added `test_ch03_guide_uses_raw_dbt_for_peeks()` to `tests/challenges/offline/test_ch03.py` with assertions:
- `"mise run challenge:dbt 03" not in text` — the wrapper is gone
- `"dbt debug" in text` — raw debug peek present
- `"dbt source freshness" in text` — raw source freshness peek present
- `"mise run challenge:seed 02" in text` — cross-challenge seed provisioning kept
- `"mise run challenge:verify 03" in text` — verify gate present
- `"mise run challenge:reset 03" in text` — reset gate present

### Step 2: Run the test to verify it fails (RED) ✓
```
FAILED tests/challenges/offline/test_ch03.py::test_ch03_guide_uses_raw_dbt_for_peeks - AssertionError: assert 'mise run challenge:dbt 03' not in '# Portfolio...'
```
Test correctly fails because the README still contains `mise run challenge:dbt 03`.

### Step 3: Convert the 4 dbt peeks to raw dbt (bulk) ✓
Ran perl conversion:
```bash
F=challenges/v1/03-airflow-orchestration/README.md
perl -0pi -e 's/\Qmise run challenge:dbt 03 -- \E/dbt /g' "$F"
```

This replaced all 4 occurrences:
- Line 286: `dbt debug` 
- Line 709: `dbt show --select fct_portfolio_returns --limit 5`
- Line 729: `dbt show --select fct_portfolio_returns --limit 5`
- Line 1138: `dbt source freshness --select source:custodian`

Verified: `grep -c "mise run challenge:dbt 03"` → 0

### Step 4: Add the project-dir note before the first dbt peek ✓
Inserted immediately before the first `dbt debug` code block (line 286):

```markdown
Run these dbt peeks from the dbt project folder — `cd data_products/portfolio_analytics/dbt` once, then run the `dbt` commands below. (`mise run challenge:seed 02` and the `mise run challenge:*` gate/reset commands run from anywhere in the repo.)

> **dbt can't find your credentials?** (e.g. `Runtime Error ... auth_type: oauth is required when not using access token`.) Your shell environment is not loaded. Open a fresh terminal so mise initializes the environment, or re-run `mise run setup:databricks`, then retry.
```

The note teaches trainees where to run the dbt commands and provides a troubleshooting path for auth failures.

### Step 5: Verify the conversion mechanically ✓
All checks passed:
```
mise run challenge:dbt: 0 found (OK)
mise run challenge:seed 02: 2 found (OK - cross-challenge seed provisioning kept)
mise run challenge:verify 03: 9 found (OK - verify gates present)
--inline: 0 found (OK)
astro dev run: 15 found (OK - Airflow commands unchanged)
File size: 63024 bytes (OK - >= 6000 bytes)
```

### Step 6: Run the offline suite for challenge 03 (GREEN) ✓
```
======================== 33 passed in 0.05s =========================
```

All 33 tests in `test_ch03.py` pass, including:
- The new `test_ch03_guide_uses_raw_dbt_for_peeks` test
- All 32 pre-existing assertions (vacuous `astro dev parse` absence, `DatabricksTokenProfileMapping` presence, `astro dev run` presence, etc.)

Full offline suite (84 tests total):
```
======================== 84 passed in 0.45s =========================
```

### Step 7: Commit ✓
```
commit 8431a35 (HEAD -> feature/improvements)
Author: Copilot <223556219+Copilot@users.noreply.github.com>
Date:   Mon Aug 3 09:31:32 2026 -0700

    challenge-03: teach raw dbt for the pipeline peeks

    Convert the four challenge:dbt 03 peeks (debug/show/source freshness) to
    raw dbt run from data_products/portfolio_analytics/dbt; keep the
    cross-challenge seed provisioning and the verify/reset gate on mise.

    Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Files committed with explicit list:
- `challenges/v1/03-airflow-orchestration/README.md`
- `tests/challenges/offline/test_ch03.py`

## Changes Summary

### `challenges/v1/03-airflow-orchestration/README.md`
- **Before:** 4 commands using `mise run challenge:dbt 03 -- <cmd>`
- **After:** 4 commands using raw `dbt <cmd>`
- **Added:** cd + auth troubleshooting note before the first peek
- **Preserved:** Surrounding prose, expected-result statements, `mise run challenge:seed 02`, `mise run challenge:verify 03`, `mise run challenge:reset 03`
- **Diff stats:** +22 insertions, -4 deletions

### `tests/challenges/offline/test_ch03.py`
- **Added:** `test_ch03_guide_uses_raw_dbt_for_peeks()` function with 6 assertions

## Global Constraints Verification

✓ Branch: `feature/improvements`  
✓ No `mise` tasks deleted or renamed  
✓ No changes to `dbt_wrapper.py`, `verify.sh`, `profiles.yml` content, model SQL, seeds  
✓ No `profiles.yml` symlink created (challenge 03 already ships it)  
✓ `mise run challenge:verify 03` and `mise run challenge:reset 03` kept  
✓ No `--inline` anywhere in README  
✓ README size: 63024 bytes (> 6000 bytes)  
✓ No forbidden tokens: `verify-with-databricks.sh`, `START_HERE`, `RUN.md`, `Preflight note`, `\newpage`  
✓ `mise run challenge:seed 02` cross-challenge step kept (exception documented)  
✓ Auth prerequisite unchanged (trainee runs `mise run setup:databricks` once)  
✓ Expected-result prose preserved  
✓ Added cd/troubleshooting note is clear of forbidden strings

## Test Summary
- **TDD Flow:** RED → GREEN ✓
- **New test:** `test_ch03_guide_uses_raw_dbt_for_peeks` → PASS ✓
- **Pre-existing tests:** 33 ch03 tests → all PASS ✓
- **Full offline suite:** 84 tests → all PASS ✓
- **Regressions:** None detected ✓

## Self-Review

### What went well
1. **TDD discipline:** Wrote the failing test first, confirmed it failed, then fixed it.
2. **Exact adherence to brief:** Used the exact test code, perl command, and commit message from the brief.
3. **Mechanical verification:** All 6 mechanical checks passed before running tests.
4. **Comprehensive testing:** Ran the full offline suite to catch regressions (84 tests).
5. **Clean commit:** Used explicit file list, no `-A` or `.`; included proper trailers.

### Potential concerns
**None.** 

The change is surgical and low-risk:
- Perl conversion is atomic and idempotent
- Manual notes are inserted before the first command, not mid-sequence
- Cross-challenge seed provisioning (`mise run challenge:seed 02`) is untouched
- Verify/reset gates are preserved
- No forbidden strings introduced
- All 84 offline tests pass, confirming no regressions
- The new test specifically locks the raw-dbt convention for future edits

## Files Modified
1. `challenges/v1/03-airflow-orchestration/README.md` — 4 command conversions + cd/auth notes
2. `tests/challenges/offline/test_ch03.py` — 1 new test function

## Commit Details
- **SHA:** 8431a35
- **Message:** challenge-03: teach raw dbt for the pipeline peeks
- **Branch:** feature/improvements
- **Trailers:** Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

---

**Task Status:** ✓ COMPLETE  
**Verification:** All tests passing, all constraints satisfied, commit ready.

---

## Update: Fix Report for Subshell dbt Peeks (Current Session)

### Problem Statement
Challenge 03 is an Airflow challenge with dbt read-only peeks (debug, show, freshness) interleaved with `astro dev run` commands that run from the repo root. Bare `dbt` commands from repo root cannot find `dbt_project.yml` (the dbt project is a child dir: `data_products/portfolio_analytics/dbt/`). 

**Solution:** Wrap each dbt peek in a self-contained subshell: `(cd data_products/portfolio_analytics/dbt && dbt …)` so it runs in the project dir without changing the trainee's CWD.

### Edits Made

**Edit 1: Rewrite the "How to check" note (line 285)**
- **Old:** `Run these dbt peeks from the dbt project folder — `cd data_products/portfolio_analytics/dbt` once, then run the `dbt` commands below.`
- **New:** `Each dbt peek below is a self-contained `(cd data_products/portfolio_analytics/dbt && dbt …)` command, so you can run it while staying at the repo root — where the `astro` commands in this challenge run.`

**Edit 2: Wrap dbt debug in subshell (line 290)**
- **Old:** ` ```bash\ndbt debug\n``` `
- **New:** ` ```bash\n(cd data_products/portfolio_analytics/dbt && dbt debug)\n``` `

**Edit 3: Wrap standalone dbt show in subshell (line 713)**
- **Old:** ` ```bash\ndbt show --select fct_portfolio_returns --limit 5\n``` `
- **New:** ` ```bash\n(cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns --limit 5)\n``` `

**Edit 4: Wrap dbt show in Solution block in subshell (line 733)**
- **Old:** ` # after success:\ndbt show --select fct_portfolio_returns --limit 5`
- **New:** ` # after success (run dbt from its project folder):\n(cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns --limit 5)`

**Edit 5: Wrap dbt source freshness in subshell (line 1142)**
- **Old:** ` ```bash\ndbt source freshness --select source:custodian\n``` `
- **New:** ` ```bash\n(cd data_products/portfolio_analytics/dbt && dbt source freshness --select source:custodian)\n``` `

### Test Enhancements

**In `tests/challenges/offline/test_ch03.py`, added 2 assertions to `test_ch03_guide_uses_raw_dbt_for_peeks`:**
```python
    # Interleaved peeks sit next to `astro dev run` (run from the repo root), so they
    # must be self-contained subshells that cd into the dbt project — otherwise bare
    # dbt fails to find dbt_project.yml from the repo root.
    assert "cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns" in text
    assert "cd data_products/portfolio_analytics/dbt && dbt source freshness" in text
```

### Verification

#### Test Results
```bash
$ python -m pytest tests/challenges/offline/test_ch03.py -q
33 passed in 0.05s

$ python -m pytest tests/challenges/offline -q
86 passed in 0.40s
```

**Status:** ✓ All 86 tests pass (including the 2 new assertions in test_ch03)

#### Count Check
```bash
$ grep -c "cd data_products/portfolio_analytics/dbt && dbt" challenges/v1/03-airflow-orchestration/README.md
6
```

**Notes on count:**
- The grep matches 6 occurrences total:
  - Line 177: Original prose reference (already existed)
  - Line 285: Template in prose ("Each dbt peek below is a self-contained `(cd data_products/portfolio_analytics/dbt && dbt …)` command...")
  - Line 290: `(cd data_products/portfolio_analytics/dbt && dbt debug)`
  - Line 713: `(cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns --limit 5)`
  - Line 733: `(cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns --limit 5)`
  - Line 1142: `(cd data_products/portfolio_analytics/dbt && dbt source freshness --select source:custodian)`

The 4 new executable blocks are correctly wrapped in subshells. Lines 177 and 285 are prose references/templates that include the pattern as examples.

#### File Integrity
```bash
$ wc -c challenges/v1/03-airflow-orchestration/README.md
63319 bytes
```

✓ README is 63,319 bytes (> 6000 bytes constraint met)

#### Constraints Satisfied
✓ No `mise run challenge:dbt` reintroduced (peeks use raw `dbt` inside subshell)  
✓ `mise run challenge:seed 02` kept  
✓ `mise run challenge:verify 03` and `mise run challenge:reset 03` kept  
✓ No `--inline` introduced  
✓ README >= 6000 bytes  
✓ Explicit file list used (no `git add -A`)  

### Commit
```
commit e22e279 (HEAD -> feature/improvements)
Author: Copilot <223556219+Copilot@users.noreply.github.com>
Date:   Mon Aug 3 10:10:29 2026 -0700

    fix(challenge-03): run dbt peeks in a subshell so they work from the repo root

    The ch03 dbt peeks are interleaved with `astro dev run` commands that require the
    repo root, where bare dbt cannot find dbt_project.yml (the project is a child dir).
    Wrap each peek in (cd data_products/portfolio_analytics/dbt && dbt ...) so it runs
    in the project dir without changing the trainee's CWD. Lock it in test_ch03.

    Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Files Modified
1. `challenges/v1/03-airflow-orchestration/README.md` — 5 edits to wrap dbt commands in subshells
2. `tests/challenges/offline/test_ch03.py` — 2 new assertions to lock the subshell pattern

**Session Status:** ✓ COMPLETE
