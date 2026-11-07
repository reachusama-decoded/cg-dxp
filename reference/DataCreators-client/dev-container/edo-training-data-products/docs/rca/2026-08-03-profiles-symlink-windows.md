# RCA — `profiles.yml` symlinks break every dbt challenge on Windows

| Field | Value |
|---|---|
| **Date** | 2026-08-03 |
| **Status** | Resolved on `feature/improvements` |
| **Severity** | Critical — Challenge 02 and Challenge 04 were dead on arrival for every Windows trainee, at the *first* command |
| **Components** | `challenges/02-dbt-pipeline/dbt/profiles.yml` · `data_products/atlas_elt/profiles.yml` · Git for Windows (`core.symlinks`) · `dbt-core` 1.11.8 profile loading |
| **Discovered while** | Testing the raw-`dbt` challenge conversion on a Windows host running the repo devcontainer |
| **Related** | `docs/rca/2026-08-03-dbt-databricks-auth-hang.md` (same raw-`dbt` conversion) |

---

## 1. Summary

The raw-`dbt` conversion needed `dbt` to find its connection settings (`profiles.yml`) when a trainee
`cd`s into the dbt project folder and types a bare `dbt build`. The change added a `profiles.yml`
inside each project folder as a **symlink** ("shortcut") pointing at the real file next door.

Symlinks work fine on macOS and Linux. **On Windows they usually do not get created at all.** Git for
Windows disables them by default, and instead of a shortcut it writes an ordinary text file whose
entire contents are the shortcut's target path — 28 characters of text where a config file should be.

`dbt` then read `../dbt_profiles/profiles.yml` as if it were the config itself. That is valid YAML (a
plain string), so nothing flagged it as malformed; `dbt` simply crashed deep inside its own startup
code with a Python traceback that names neither the file nor the real problem.

The result: a Windows trainee who followed the guide exactly hit an unreadable crash on the very first
command of Challenge 02, before writing a single line of SQL.

The fix is to **commit a real copy of the file instead of a symlink**, and to add tests that keep the
copy in sync and ban tracked symlinks repo-wide.

---

## 2. Impact / who was affected

- **Every trainee on Windows** — which is the majority of this audience. macOS/Linux trainees were
  unaffected, so the problem was invisible to whoever authored and reviewed the change.
- **Challenge 02** was blocked at guide line 22 (`dbt debug`), the first command in the challenge.
- **Challenge 04** was blocked the same way, since `data_products/atlas_elt/profiles.yml` had the
  identical problem.
- The devcontainer did **not** rescue this. The container bind-mounts the Windows working tree, so it
  faithfully sees the broken text file that Git checked out on the host. Being "inside Linux" does not
  help when the file itself was written wrong on the host.
- **Failure mode was maximally discouraging**: a raw Python traceback with no mention of a challenge,
  a profile, or a fix. A beginner has no path forward from it.

---

## 3. Symptoms

From `challenges/02-dbt-pipeline/dbt`, the guide's first command:

```console
$ dbt debug
Encountered an error:
'str' object has no attribute 'get'
Traceback (most recent call last):
  File "/opt/venv/lib/python3.13/site-packages/dbt/cli/requires.py", line 89, in wrapper
    flags = Flags(ctx)
  File "/opt/venv/lib/python3.13/site-packages/dbt/config/project.py", line 845, in read_project_flags
    profile_project_flags = coerce_dict_str(profile.get("config", {}))
                                            ^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'
```

Note what the message does **not** say: no filename, no "profiles.yml", no "symlink", no next step.

The tell, inside the container:

```console
$ ls -la challenges/02-dbt-pipeline/dbt/profiles.yml
-rwxr-xr-x 1 root root 28 Aug  4 00:29 challenges/02-dbt-pipeline/dbt/profiles.yml
$ cat challenges/02-dbt-pipeline/dbt/profiles.yml
../dbt_profiles/profiles.yml
```

A real symlink would show as `lrwxrwxrwx ... profiles.yml -> ../dbt_profiles/profiles.yml`. Here it is
`-rwxr-xr-x`, a **regular file** of 28 bytes — the length of the path string.

---

## 4. Root cause

Three layers had to line up.

### 4.1 The change committed symlinks

Git records a symlink as file mode `120000`, with the link target stored as the blob contents:

```console
$ git ls-files -s challenges/02-dbt-pipeline/dbt/profiles.yml
120000 b26b45c2d018e8ee96892a94c600c10c53888e03 0  challenges/02-dbt-pipeline/dbt/profiles.yml
```

### 4.2 Git for Windows checks symlinks out as text files

Creating a symlink on Windows requires either Developer Mode or administrator rights, so Git for
Windows ships with `core.symlinks=false`. On this machine:

```console
$ git config --get core.symlinks
false
```

When `core.symlinks=false`, Git cannot honour mode `120000`, so it does the only thing it can: it
writes the blob out as an **ordinary file**. The blob contents are the link target, so the file's
contents become the literal text `../dbt_profiles/profiles.yml`.

Critically, this is silent. No warning, no checkout error, and `git status` stays clean — because from
Git's point of view the working tree matches what it intended to produce.

### 4.3 The corrupted file is still *valid YAML*, so it fails late and cryptically

`../dbt_profiles/profiles.yml` parses cleanly as a YAML scalar string. `dbt` therefore gets past
parsing and only fails later, when it assumes the parsed object is a dictionary and calls
`.get("config", {})` on it. Python raises `AttributeError: 'str' object has no attribute 'get'` from
inside `dbt/config/project.py`, far from the actual cause.

Had the file been invalid YAML, `dbt` would have reported a parse error naming the file, and this
would have been diagnosed in seconds.

### 4.4 Why review and CI did not catch it

The change shipped with tests that assert the two files have matching contents:

```python
assert proj.read_text() == canonical.read_text()
```

That assertion is exactly right, and it **does** fail on a Windows checkout. But it only ever ran on
Linux, where the symlink resolves and the contents genuinely match. The test encoded the correct
invariant and still could not see the bug, because the platform that breaks it was never exercised.

---

## 5. Fix

**Commit a real file instead of a symlink.** `profiles.yml` is a small, rarely-edited config; a
tracked copy costs nothing and works identically on every platform.

```console
# content copied from the canonical file, then the index mode flipped 120000 -> 100644
$ git ls-files -s challenges/02-dbt-pipeline/dbt/profiles.yml
100644 b4caad457828cdbefaba4a8dec2069c1ade266dd 0  challenges/02-dbt-pipeline/dbt/profiles.yml
```

Applied to both affected paths:

| Path | Before | After |
|---|---|---|
| `challenges/02-dbt-pipeline/dbt/profiles.yml` | symlink → `../dbt_profiles/profiles.yml` | real copy |
| `data_products/atlas_elt/profiles.yml` | symlink → `dbt_profiles/profiles.yml` | real copy |

The canonical files under `dbt_profiles/` are unchanged, so `verify.sh`, `mise run dbt:*`, the
Databricks bundle, and `clone_sources_engine.py` — all of which pass `--profiles-dir dbt_profiles`
explicitly — keep working untouched.

### Guardrails added

1. **Drift guard (already existed, now stronger).** The content-equality assertions in
   `tests/challenges/offline/test_ch02.py` and `test_ch04_structure.py` gain
   `assert not proj.is_symlink()`, so reintroducing a symlink fails the test on Linux *and* Windows
   rather than only on Windows.
2. **Repo-wide ban.** New `tests/local_env/offline/tooling/test_no_tracked_symlinks.py` scans
   `git ls-files -s` for any mode-`120000` entry and fails with an explanation. This catches the next
   symlink anywhere in the repo, not just these two files.

---

## 6. Verification

```console
$ docker exec <container> bash -lc 'cd /workspaces/edo-training-data-products/challenges/02-dbt-pipeline/dbt && dbt debug'
Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]
Connection:
  host: https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com
  catalog: training_dev
  schema: training_gqp
  Connection test: [OK connection ok]
All checks passed!
```

Offline suites: `test_no_tracked_symlinks.py`, `test_ch02.py`, `test_ch04_structure.py` — 31 passed.

---

## 7. Lessons

1. **Do not track symlinks in a repo with Windows users.** It is not a preference; Git for Windows
   cannot create them by default, and it fails silently. Prefer a committed copy plus a sync test.
2. **Silent checkout corruption is worse than a loud failure.** `git status` stayed clean the whole
   time, which removes the first thing anyone would check.
3. **A config that is valid-but-wrong YAML fails far from its cause.** When a config file's *type* is
   load-bearing, validate it is a mapping and name the file in the error.
4. **A correct test on one platform is not coverage.** The equality test here was well designed and
   still missed a critical bug, purely because Windows was never in the loop. Platform-specific
   failure modes need either a platform-specific check (the tracked-symlink scan) or CI on that
   platform.
5. **Test the first command a beginner runs, on the platform they actually use.** This bug sat at
   guide line 22 of the very first dbt challenge and would have stopped every Windows trainee cold.
