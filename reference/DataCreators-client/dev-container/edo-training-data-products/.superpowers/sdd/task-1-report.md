# Task 1 Report: Challenge 02 → raw dbt

> **Superseded in part (2026-08-03).** The `profiles.yml` symlink created by this task has
> since been replaced with a committed copy: on Windows (`core.symlinks=false`) it checked
> out as a text file and broke `dbt debug`, the first command of Challenge 02. The
> `--inline` ban verified below has also been lifted. This report is retained as the record
> of what was executed at the time. Current decisions:
> `docs/superpowers/specs/2026-07-31-challenge-raw-dbt-commands-design.md` §3 and
> `docs/rca/2026-08-03-profiles-symlink-windows.md`.

## Summary
Successfully completed Task 1 of the raw-dbt-commands implementation plan. Converted challenge 02's mise-wrapped dbt teaching commands to raw dbt, added a project-dir profiles.yml symlink, and locked the convention with two new test assertions.

## What Changed

### Files Modified/Created

1. **`challenges/v1/02-dbt-pipeline/dbt/profiles.yml`** (created)
   - Symlink: `../dbt_profiles/profiles.yml`
   - Enables bare `dbt build` after cd into the dbt project directory
   - Verified: readlink outputs `../dbt_profiles/profiles.yml`, first line is `portfolio_analytics_challenge:`

2. **`challenges/v1/02-dbt-pipeline/README.md`** (modified)
   - Converted 44 wrapped dbt/seed commands to raw dbt using perl substitutions
   - Removed `with \`challenge:dbt\`` fragment from intro paragraph
   - Added setup block with `cd challenges/v1/02-dbt-pipeline/dbt` and `dbt debug`
   - Added troubleshooting note for credential issues
   - Preserved all "expected result" statements (e.g., "build should report PASS=4")
   - Verified: size ≥6000 bytes, contains mise verify/reset but not mise dbt/seed, no --inline

3. **`tests/challenges/offline/test_ch02.py`** (modified)
   - Added `test_ch02_profiles_discoverable_in_project_dir()` — validates symlink exists and matches canonical
   - Added `test_ch02_guide_uses_raw_dbt_not_mise_wrapper()` — validates raw dbt in guide, mise verify/reset present

## TDD Verification

### RED Phase (Before Changes)
```
FAILED tests/challenges/offline/test_ch02.py::test_ch02_profiles_discoverable_in_project_dir
FAILED tests/challenges/offline/test_ch02.py::test_ch02_guide_uses_raw_dbt_not_mise_wrapper
2 failed, 16 deselected
```

Both tests failed as expected:
- Symlink didn't exist
- README still contained `mise run challenge:dbt` and `mise run challenge:seed`

### GREEN Phase (After Changes)
```
18 passed in test_ch02.py
83 passed in full offline suite
```

All tests pass, including:
- The two new test assertions
- All 16 pre-existing test_ch02 assertions (no parity regression)
- All 83 tests in the full offline suite

## Mechanical Verification
All constraints from the brief satisfied:
- `mise run challenge:dbt` count: 0 ✓
- `mise run challenge:seed` count: 0 ✓
- `mise run challenge:verify 02` count: 6 ✓
- `mise run challenge:reset 02` count: 2 ✓
- `--inline` count: 0 ✓
- README size: 54,077+ bytes ✓

## Symlink Verification
```
$ readlink challenges/v1/02-dbt-pipeline/dbt/profiles.yml
../dbt_profiles/profiles.yml
$ head -1 challenges/v1/02-dbt-pipeline/dbt/profiles.yml
portfolio_analytics_challenge:
```
Symlink is relative and correct.

## Git Commit
```
Commit: a3351e9
Subject: challenge-02: teach raw dbt instead of the mise wrapper

Add a project-dir profiles.yml symlink so bare 'dbt build' works after
cd into challenges/v1/02-dbt-pipeline/dbt, convert the guide's dbt/seed
commands to raw dbt, and lock the convention in test_ch02.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Self-Review Checklist
✓ Both test additions append to file without changing pre-existing tests
✓ Symlink is relative and uses correct path
✓ Perl commands applied exactly as specified (no modifications)
✓ Manual edits (5a, 5b) correctly placed in README
✓ All mechanical verification checks pass
✓ TDD cycle complete: RED → GREEN
✓ Full offline suite passes (no parity regression)
✓ Commit uses explicit file list (no `git add -A` or `-A`)
✓ No changes to `.mise.toml` (constraint: all five challenge:* tasks kept)
✓ No changes to `dbt_profiles/profiles.yml` (only symlink added)
✓ Preserved expected result statements in guide
✓ Setup block and troubleshooting note added in correct location

## Concerns
None. Task completed successfully according to all requirements in the brief and global constraints.
