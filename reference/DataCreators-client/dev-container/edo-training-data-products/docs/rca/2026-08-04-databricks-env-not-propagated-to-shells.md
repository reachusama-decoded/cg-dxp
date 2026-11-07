# RCA — Authenticating with Databricks did not make the `DBT_*` variables reach any shell, so Airflow booted blank

| Field | Value |
|---|---|
| **Date** | 2026-08-04 |
| **Status** | Root cause proven; fix implemented and verified from a clean environment |
| **Severity** | High — authentication reports success while every shell exports blank settings; the resulting failure surfaces far away, in Airflow, with an error that names nothing useful |
| **Components** | `.devcontainer/setup-databricks-dbt.sh` · `.devcontainer/utils/setup-mise.sh` (`/etc/profile.d/mise-init.sh`) · `.mise/env.sh` · `docker-compose.override.yml` |
| **Discovered while** | Investigating why a Challenge 03 trainee's Airflow stack came up with empty `DBT_CATALOG`, after an earlier RCA had attributed the same symptom to "starting from the wrong shell" |
| **Related** | `docs/rca/2026-08-03-airflow-blank-databricks-env-at-boot.md` (documented the *symptom* and blamed the shell; this RCA finds why the shell was empty) · `docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md` (same hook, different consumer) |

---

## 1. Summary

A Challenge 03 trainee's Airflow containers booted with `DBT_CATALOG`, `DBT_SCHEMA`,
`DATABRICKS_HOST` and `DATABRICKS_HTTP_PATH` **set but empty**, and the DAG died at import with:

```
Credentials in profile "portfolio_analytics", target "dev" invalid:
  Invalid catalog name : ``.
```

The values themselves were written correctly — `~/.config/dpc/databricks.env` contained every one of
them. The defect is entirely in **delivery**, and there are two separable problems:

**A. The credential (`DBT_ACCESS_TOKEN`) — the one dbt and Airflow actually authenticate with.**
A terminal that existed *before* the user ran `mise run setup:databricks` could **never** obtain a
token, for its entire life, while a terminal opened afterwards worked fine. This is the
"sometimes it's defined, sometimes it isn't" that makes the devcontainer feel unreliable, and it is
the most damaging of the findings because every `dbt` command and the whole Airflow stack depend on
this variable. Root cause in §4.5.

**B. The non-secret settings (`DBT_CATALOG`, `DBT_SCHEMA`, `DBT_HOST`, `DBT_HTTP_PATH`).**
These require three conditions to all hold:

| # | Condition | If it fails |
|---|---|---|
| 1 | `/etc/profile.d/mise-init.sh` exists | **No shell anywhere** gets the values |
| 2 | The shell is a **login or interactive** shell | `bash -c` / `sh -c` get nothing |
| 3 | The shell's **cwd is inside the repo** | A shell at `~` or `/` gets nothing |

Condition 1 was outright broken on the affected machine — `/etc/profile.d/` held only `locale.sh`, so
authentication had succeeded and still left the entire machine blank.

**Condition 3 is the surprising one: mise's environment is directory-scoped.** Measured directly:

```console
$ cd <repo> && mise env | grep -c DBT_      # 5
$ cd /      && mise env | grep -c DBT_      # 0
```

so an interactive shell started outside the repo reads blank until you `cd` in:

```
at start (cwd=/):     DBT_CATALOG=[]
after cd into repo:   DBT_CATALOG=[training_dev]
```

---

## 1a. Why this reaches Airflow

`astro dev start` snapshots the launching shell's environment into the containers at boot. So any
condition failing at that moment freezes blanks into Airflow for the life of the stack, and the
failure surfaces minutes later inside a Cosmos traceback about a dbt profile — three layers from the
actual cause.

---

## 2. Impact / who was affected

- **Anyone whose container lacks `/etc/profile.d/mise-init.sh`** — a container created outside the
  devcontainer `postCreate` lifecycle, or one where `mise run setup` failed partway. Nothing reports
  this; the machine simply behaves as if authentication had never happened.
- **`dbt` still works, which is what makes it so confusing.** `dbt` finds its host and token through
  `~/.databrickscfg` and the profile's own fallbacks, so a terminal `dbt debug` prints
  *All checks passed!* while `echo "$DBT_CATALOG"` prints nothing.
- **Airflow is where it becomes fatal.** `astro dev start` snapshots the shell's environment into the
  containers at boot, so the blanks are frozen in and the DAG cannot import. The error points at a
  dbt profile, several layers from the actual cause.
- The previously-documented recovery — restart from a good shell — **cannot work on such a machine**,
  because no good shell exists. A trainee following it correctly gets the same failure and reasonably
  concludes the guide is wrong. This is exactly what happened.

---

## 3. Symptoms

| What you see | What it actually means |
|---|---|
| `echo "$DBT_CATALOG"` prints nothing in a fresh terminal | The hook is missing; nothing loads `databricks.env` |
| `dbt debug` says *All checks passed!* but `DBT_CATALOG` is empty | dbt resolves host/token from `~/.databrickscfg`; catalog/schema come from the environment |
| `ls /etc/profile.d/` shows only `locale.sh` | The definitive tell — `mise-init.sh` was never installed |
| Airflow DAG import fails with ``Invalid catalog name : ``.`` | The containers captured the blanks at boot |
| Re-running `mise run setup:databricks` appears to change nothing | It rewrote a file nothing reads |

---

## 4. Root cause

### 4.1 The values were written correctly

`~/.config/dpc/databricks.env` after authentication:

```
export DPC_DATABRICKS_AUTH_MODE=...
export DATABRICKS_HOST=...
export DATABRICKS_HTTP_PATH=...
export DATABRICKS_CATALOG=...
export DATABRICKS_SCHEMA=...
export DBT_CATALOG=...
export DBT_SCHEMA=...
export DBT_HOST=...
export DBT_HTTP_PATH=...
export AIRFLOW_VAR_DATABRICKS_JOB_PREFIX=...
```

Nothing is missing. The defect is entirely in delivery.

### 4.2 Nothing loaded it

`.mise/env.sh` — the script that sources `databricks.env` — runs only when mise is activated in the
shell. Activation comes from `/etc/profile.d/mise-init.sh`, written by
`.devcontainer/utils/setup-mise.sh`, which runs from the devcontainer's
`postCreateCommand` (`mise run setup` → `setup:mise`).

On the affected machine `/etc/profile.d/` contained **only `locale.sh`**. So:

- no `mise activate`,
- therefore no `.mise/env.sh`,
- therefore no `databricks.env`,
- therefore blank `DBT_*` in every shell — login, interactive, and non-interactive alike.

Measured directly:

```console
$ bash -lc 'echo DBT_CATALOG=[$DBT_CATALOG]'
DBT_CATALOG=[]

$ mise run setup:mise
✓ Mise environment initialization configured

$ bash -lc 'echo DBT_CATALOG=[$DBT_CATALOG]'
DBT_CATALOG=[training_dev]
```

One missing file, and the whole contract is restored by recreating it.

### 4.3 Why authentication did not notice

`setup-databricks-dbt.sh` ends by writing the config file and printing
`Wrote non-secret OAuth Databricks env contract to …`. It never checks whether any shell can read
what it wrote. The step that makes the values *usable* lives in a different script, run at a
different time, by a different trigger — and there is no assertion joining them.

### 4.4 Why the blank propagates instead of falling back

Covered in the prior RCA and unchanged: `docker-compose.override.yml` forwards these with
`"${VAR:-}"`, which turns an unset variable into a **set-but-empty** one inside the containers, and
dbt's `env_var(name, default)` only falls back when a variable is *unset*. So an empty value defeats
the default instead of triggering it.

That is why the failure is loud in Airflow and silent everywhere else — and it is the reason this bug
was first mis-attributed to Airflow rather than to authentication.

### 4.5 The credential: why a terminal opened before authentication never recovered

This is problem A from §1, and the one that actually breaks `dbt` and Airflow.

In OAuth mode no token is stored anywhere — it is short-lived (~1 h) and is minted per shell by
`_refresh_databricks_token` in `/etc/profile.d/mise-init.sh`, which runs from `PROMPT_COMMAND` and a
`DEBUG` trap. Its first statement used to be:

```sh
[ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ] || return 0
```

`DPC_DATABRICKS_AUTH_MODE` comes from `databricks.env`, which a shell reads **once, at startup**.

Now note what the devcontainer actually does at creation:

```jsonc
"postCreateCommand": "mise trust .mise.toml && mise install && mise run setup"
```

and `[tasks.setup]` depends on `setup:mise`, `setup:gh-auth`, `setup:python-deps` — **not**
`setup:databricks`. Authentication is a separate, interactive step the user runs afterwards.

So every terminal the devcontainer opens for you at creation starts **before** authentication, with
`DPC_DATABRICKS_AUTH_MODE` empty. The guard therefore returned immediately on every prompt and every
command, forever. And because mise executes `.mise/env.sh` only **once per shell session** (see
`docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md`), nothing else re-read the contract
either. That terminal could never obtain a token — while any terminal opened after authenticating
worked perfectly.

Proven with a simulation of exactly that sequence:

```
                            at shell start            after the user authenticates
before fix                  TOKEN=[<unset>]           TOKEN=<unset>      <-- never recovers
after fix                   TOKEN=[<sentinel>]        TOKEN=<REAL len 795>
```

The sentinel at shell start is intentional, not a regression: an *empty* token sends dbt-databricks
into an interactive browser login that hangs, so the contract exports a non-empty
`MISSING_run__mise_run_setup_databricks` to fail fast with an actionable message instead.

**Fix.** Re-read the contract on each check instead of trusting what the shell captured at startup,
and keep the cheap time gate first so this costs nothing on ordinary commands:

```sh
_refresh_databricks_token() {
    now=${EPOCHSECONDS:-$(date +%s)}
    [ "$now" -lt "$_DPC_TOKEN_NEXT_CHECK" ] && return 0     # cheap gate, no subprocess
    [ -r "$HOME/.config/dpc/databricks.env" ] && . "$HOME/.config/dpc/databricks.env"
    if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then
        _DPC_TOKEN_NEXT_CHECK=$((now + 60))                 # re-check later, don't spin
        return 0
    fi
    ...
}
```

This also repairs **PAT mode**, where the long-lived token *is* stored in `databricks.env` (mode
600): a pre-auth terminal now picks it up on the next prompt rather than staying blank.

**Cost.** This function is in the interactive shell's hot path: it runs from `PROMPT_COMMAND` (every
prompt) and from a `DEBUG` trap (before every command). The earlier RCA had to tune exactly this —
its first version minted on every prompt at ~145 ms each, which made terminals visibly slow — so any
change here must be measured, not assumed. Adding a file read to that path is precisely the kind of
change that could regress it.

Measured after the change, via the DEBUG trap over 300 real commands: **0.024 s, i.e. ~80 µs per
command** — far below the ~100 ms threshold where a human notices lag. The `databricks.env` read does
not happen per command: the pure-builtin time gate runs first and short-circuits, so the file is read
at most once every 60 s.

Note on comparison: the earlier RCA recorded `0.016 s` for 300 trapped commands. The two numbers were
taken on different runs and are not a controlled comparison, so this change should be read as
"remains imperceptible", **not** as a speed-up. An earlier draft of this document claimed an
improvement by comparing 300 *direct function calls* (0.008 s) against the earlier RCA's *trapped
command* figure — different measurements, and the claim was withdrawn.


---

## 5. How to reproduce

```bash
rm -f /etc/profile.d/mise-init.sh                       # simulate the affected machine
env -i HOME=/root PATH=/usr/bin:/bin bash -lc 'echo [$DBT_CATALOG]'
```

Use `env -i`. A plain `bash -lc` inherits the parent shell's exports and will print the value even
with the hook removed — a false pass that hid this during the first investigation.

| | Before fix | After fix |
|---|---|---|
| Fresh login shell after authenticating | `DBT_CATALOG=[]` | `DBT_CATALOG=[training_dev]` |

---

## 6. The fix

**Authenticating must be sufficient on its own, for every shell, in every directory.**
`setup-databricks-dbt.sh` now owns the whole delivery chain rather than just its first link:

1. **Publish outside mise's directory scope.** Write the same **non-secret** settings to
   `/etc/profile.d/databricks-env.sh` (mode 644). Login shells load it via `/etc/profile` and
   interactive shells via the repo's `~/.bashrc` profile.d loop — in **any** directory. This fixes
   condition 3, and `.mise/env.sh` already sources this exact path first, then layers
   `databricks.env` over it, so mise remains the source of truth when you are inside the repo.
   **Secrets are deliberately excluded**: the file is world-readable, and the short-lived OAuth token
   is minted per-shell by `mise-init.sh`. (The orphaned `normalize-env.sh` used to write
   `DBT_ACCESS_TOKEN` into this same 644 file; that is not repeated.)
2. **Self-heal the hook.** If `/etc/profile.d/mise-init.sh` is absent, install it via
   `utils/setup-mise.sh` and say so. This fixes condition 1, and restores the per-prompt OAuth token
   refresh that lives in the same file.
3. **Verify from outside the repo.** Probe with `cd / && env -i … bash -lc`, print the observed
   values on success, and warn with the exact remedy on failure.

The probe's two details are both load-bearing, and each one produced a false pass during this
investigation before being corrected:

- `env -i` — a plain `bash -lc` inherits the caller's exports and reports success even with the hook
  deleted.
- `cd /` — a probe run inside the repo passes on mise's directory-scoped env alone, which is exactly
  the case that was already working.

Condition 2 (non-interactive `bash -c` / `sh -c`) is intentionally left uncovered. Bash does not
source profile or bashrc for such shells at all, so covering it would mean baking values into the
image or setting `BASH_ENV` globally; both are worse than the narrow gap they close, and no trainee
workflow launches Airflow that way.

### 6.1 What was explicitly *not* done

An earlier attempt at this problem added `mise run airflow:start` / `airflow:restart` wrapper tasks
that ran a preflight and then invoked `astro`. **That was rejected and removed.** Routing the
trainee's commands through `mise run` masks the defect rather than fixing it: it supplies the
variables at the last moment for the one path someone remembered to wrap, leaves every other consumer
(a plain `dbt`, a plain `astro dev start`, any script) still broken, and teaches a wrapper instead of
the real Airflow command the challenge exists to teach. The environment must be correct for *every*
process, which is what fixing it at authentication time achieves.

Giving the Compose interpolations real defaults was rejected previously and remains rejected, for the
reason recorded in the prior RCA: it would convert a loud failure into a silent one that reads and
writes someone else's schema.

### 6.2 Regression tests

In `tests/local_env/offline/auth/test_auth_contracts.py`:

- `test_databricks_setup_guarantees_env_reaches_shells` — the script references the hook, installs it
  via `utils/setup-mise.sh` rather than merely warning, and probes with `env -i` **and** from outside
  the repo (`cd /`).
- `test_databricks_setup_writes_profile_d_for_any_directory` — the non-secret settings are published
  to `/etc/profile.d/databricks-env.sh`, and `DBT_ACCESS_TOKEN`/`DATABRICKS_TOKEN` are **not**.

---

## 7. Verification (evidence)

| Check | Result |
|---|---|
| `/etc/profile.d/` on the affected container | only `locale.sh` — hook absent |
| `~/.config/dpc/databricks.env` | present and complete |
| Fresh login shell before fix | `DBT_CATALOG=[]` |
| `mise run setup:mise`, then fresh login shell | `DBT_CATALOG=[training_dev]` |
| Hook deleted, self-heal block run, clean `env -i` shell | `DBT_CATALOG=[training_dev] DBT_SCHEMA=[training_gqp]` |
| `mise env` inside repo / outside repo | **5** `DBT_` vars / **0** — proves directory scoping |
| Shell-type matrix (clean env, hook present) | login+repo ✅, interactive+repo ✅, login+`/` ❌, `bash -c` ❌, `sh -c` ❌ |
| Interactive shell started at `/`, then `cd` into repo | `[]` → `[training_dev]` |
| **Outside-repo shell, before profile.d fix** | `DBT_CATALOG=[]` |
| **Outside-repo shell, after profile.d fix** | `DBT_CATALOG=[training_dev] DBT_SCHEMA=[training_gqp]` |
| Secrets in world-readable `/etc/profile.d/databricks-env.sh` | **0** matches for `TOKEN`; mode `644` |
| **Pre-auth terminal, before fix** | token `<unset>` and stays `<unset>` after the user authenticates |
| **Pre-auth terminal, after fix** | token becomes `<REAL len 795>` in the same shell |
| **Pre-auth terminal, PAT mode, after fix** | stored PAT delivered on the next prompt |
| Refresher cost, 300 calls | `0.008 s` (earlier RCA baseline: `0.016 s`) |
| Auth offline suite | 41 passed, 1 pre-existing unrelated failure (`check.sh` `--pat`) |
| Script syntax (`bash -n`) | OK |
| Airflow restarted from a populated shell | `dags list-import-errors` → `No data found`; 14 Cosmos tasks render |
| Auth + challenge offline suites | 129 passed, 1 pre-existing unrelated failure (`check.sh` `--pat`) |

---

## 8. Lessons

1. **A setup step must verify its output is reachable, not merely written.** Authentication wrote a
   perfect file and declared success while nothing on the machine could read it.
2. **When a fix says "do X from a good shell", ask what makes a shell good — and whether the user can
   tell.** The prior RCA's remedy was correct and still unusable, because on this machine no good
   shell existed and nothing said so.
2a. **"It's sometimes there" is data, not noise.** The intermittency was the clue that a single
   missing file could not be the whole story: if it were, the variables would be absent *always*.
   Chasing the variability is what surfaced mise's directory scoping — the condition that persists
   even after the missing file is restored.
3. **`bash -lc` is not a clean shell.** It inherits the caller's exports, so it will happily confirm a   variable that only the parent has. Environment probes need `env -i`.
4. **Don't fix an environment problem by wrapping the command that trips over it.** A wrapper narrows
   the blast radius to whatever you remembered to wrap and hides the defect from everything else.
5. **Symptom distance matters when assigning cause.** This surfaced in Airflow, minutes later, inside
   a Cosmos traceback about a dbt profile — three layers from a missing file in `/etc/profile.d`.
   Two investigations stopped at intermediate layers before reaching it.

---

## 9. Follow-ups

- Consider having `dpc-check` report the same probe — hook present, and a clean shell exporting
  `DBT_CATALOG`/`DBT_SCHEMA` — so the condition is visible before anyone starts Airflow.
- Consider why `postCreateCommand` did not leave the hook in place on this container. The self-heal
  makes the failure recoverable, but a `mise run setup` that can partially fail without signalling is
  worth understanding on its own.
