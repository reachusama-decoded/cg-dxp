# RCA — Challenge 04's verify gate rewrites a tracked file with a machine-specific absolute path

| Field | Value |
|---|---|
| **Date** | 2026-08-05 |
| **Status** | Root cause proven; fix implemented and verified |
| **Severity** | Medium — the gate dirties every trainee's checkout, and the diff breaks other people's clones if committed |
| **Components** | `challenges/04-atlas-capstone/verify.sh` · `data_products/atlas_elt/package-lock.yml` · dbt `deps` local-package resolution |
| **Discovered while** | A trainee-simulation run of challenge 04 on Windows 11 (WSL2), 2026-08-05 |

---

## 1. Summary

Running the challenge's own gate —

```bash
mise run challenge:verify 04
```

— left the trainee's working tree dirty:

```diff
 packages:
-  - local: ../../shared
+  - local: /workspaces/edo-training-data-products/shared
   name: edo_shared
-sha1_hash: d874e1599002cfac1b84b82d24d286b1b1f58be4
+sha1_hash: bcbe7c4ef351e6ee5f907a32acf3dffbe86d29a7
```

> **Root cause: `verify.sh` invokes `dbt deps` with an absolute `--project-dir`. dbt resolves the
> `local: ../../shared` package relative to that argument and writes the *resolved absolute path*
> back into `package-lock.yml` — a tracked file.**

`package-lock.yml` is committed with a portable relative path. The gate replaces it with a path
that is only valid inside this one devcontainer.

---

## 2. Impact

- **Every trainee, every time they run the gate.** The gate is documented twice as the way to
  check your work, so essentially everyone hits it.
- The trainee sees an unexplained modification to a file they never touched, mixed into the
  `git status` of their real work.
- If committed, the absolute path breaks anyone whose checkout is not at
  `/workspaces/edo-training-data-products` — including every host-side clone. This is the same
  class of portability defect as the tracked symlink in
  `docs/rca/2026-08-03-profiles-symlink-windows.md`.
- The guide had **normalised** the breakage rather than fixing it: a Quick Start note read
  "**`git status` dirty after `dbt deps`?** Expected." Training a trainee to ignore unexpected
  diffs is worse than the diff.

---

## 3. Root cause

`verify.sh` supports two modes and only one of them is sandboxed:

```bash
WORK_ROOT="$PRODUCT_ROOT"          # the real directory, by default
...
if [[ -n "$MODELS_ROOT" ]]; then   # only when ATLAS_ELT_MODELS_ROOT is set
  TMP_ROOT="$(mktemp -d)"
  cp -R "$PRODUCT_ROOT/." "$TMP_ROOT/"
  WORK_ROOT="$TMP_ROOT"
fi

"$DBT_PY" "$REPO_ROOT/dbt_wrapper.py" deps --project-dir "$WORK_ROOT" ...
```

`ATLAS_ELT_MODELS_ROOT` is a CI-only variable never mentioned to trainees, so the default trainee
path runs `dbt deps` directly against `data_products/atlas_elt` with an absolute `--project-dir`,
and dbt rewrites the lock file in place.

### 3.1 Why the guide's claim was false

Two places in the README stated the gate "runs … against a **throwaway copy** of the project".
That is only true in the `ATLAS_ELT_MODELS_ROOT` branch. In the trainee path there is no copy at
all — which the polluted lock file proves directly.

### 3.2 Why running `dbt deps` by hand does *not* do this

The guide's own Quick Start tells the trainee to `cd data_products/atlas_elt && dbt deps`. Run
that way there is no `--project-dir`, dbt keeps the relative path, and the lock file is untouched
(verified: `git status` clean afterwards). So the note blaming `dbt deps` was pointing at the
wrong command — it was always the gate.

---

## 4. How to reproduce

```bash
git checkout -- data_products/atlas_elt/package-lock.yml
mise run challenge:verify 04
git status --porcelain data_products/atlas_elt/package-lock.yml   # dirty, before the fix
```

---

## 5. The fix

`verify.sh` now snapshots `package-lock.yml` before `dbt deps` and restores it from the existing
`trap cleanup EXIT` handler, so the gate cannot leave the checkout dirty however it exits:

```bash
if [[ -z "$TMP_ROOT" && -f "$WORK_ROOT/package-lock.yml" ]]; then
  LOCK_FILE="$WORK_ROOT/package-lock.yml"
  LOCK_BACKUP="$(mktemp)"
  cp "$LOCK_FILE" "$LOCK_BACKUP"
fi
```

The two README claims about a "throwaway copy" now describe what the gate actually does, and the
misleading "**dirty after `dbt deps`?** Expected" note has been corrected to say it should *not*
be dirty, with the real cause (`--project-dir <absolute>`) named for anyone who still sees it.

### 5.1 Alternatives considered and rejected

| Option | Why not |
|---|---|
| Always sandbox into a temp copy, making the original doc claim true | `local: ../../shared` is resolved relative to the project dir; from `/tmp/tmp.XXXX` it resolves to `/shared`, which does not exist. The existing sandbox branch only works because a previously-polluted lock file already held an absolute path. Fixing the docs this way would have introduced a real breakage. |
| Untrack `package-lock.yml` / add to `.gitignore` | It is a lock file — pinning the dependency is its job, and the repo intends it committed. |
| Leave it and keep documenting it as expected | This is what the guide already did, and it trains trainees to ignore unexplained diffs to tracked files. |

---

## 6. Verification (evidence)

| Check | Result |
|---|---|
| `mise run challenge:verify 04` before fix | `[pass] offline checks complete`, `package-lock.yml` **modified** to an absolute path |
| `cd data_products/atlas_elt && dbt deps` (manual, as guide instructs) | lock file **unchanged**, `git status` clean — proves the gate, not `dbt deps`, was the cause |
| `mise run challenge:verify 04` after fix | `[pass] offline checks complete`, `package-lock.yml` **unchanged**, `git status` clean |
| Lock file content after fixed gate | `local: ../../shared`, `sha1_hash: d874e15…` — identical to committed |

---

## 7. Lessons

1. **A verification gate must not mutate the tree it is verifying.** Anything it writes has to go
   to a temp location or be restored; otherwise the gate becomes a source of diffs.
2. **A code path that only runs in CI is a path that is not really tested.** The sandbox branch
   existed and looked like the normal case; nobody ran the default branch and checked
   `git status`.
3. **When documentation explains away a defect, treat the explanation as the bug.** "Expected"
   in a troubleshooting note was the strongest available signal that something was wrong, and it
   had been there long enough to look intentional.
4. **Relative paths in lock files are load-bearing.** The tempting fix (always sandbox) would have
   broken package resolution — verify assumptions about path resolution before restructuring.
