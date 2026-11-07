# RCA — an expired OAuth token gets stranded in a long-lived shell, so `dbt` fails while `databricks auth describe` says you are authenticated

| Field | Value |
|---|---|
| **Date** | 2026-08-04 |
| **Status** | Root cause proven; fix implemented and verified live |
| **Severity** | High — intermittently breaks every raw `dbt` command in an open terminal, with a misleading "you are authenticated" signal |
| **Components** | `.mise/env.sh` (OAuth token mint) · mise `_.source` / `hook-env` semantics · challenge `profiles.yml` token sentinel |
| **Discovered while** | Investigating a report that `dbt debug` for Challenge 02 failed even though `databricks auth describe` reported an authenticated session — and that the same shell started working again later |
| **Related** | `docs/rca/2026-08-03-dbt-databricks-auth-hang.md` (introduced the sentinel this RCA repairs) · `docs/rca/2026-08-03-airflow-blank-databricks-env-at-boot.md` (same empty-vs-unset failure class) |

---

## 1. Summary

The repo authenticates dbt with a short-lived Databricks OAuth access token, minted into the shell by
`.mise/env.sh`. The file's own header says it is *"Evaluated by mise on every shell prompt via
hook-env"*, and the whole design rests on that claim.

**The claim is false, and that is the root cause.**

> **mise executes a `_.source` script ONCE per shell session and caches the result. It re-runs the
> script only when the file's mtime changes — not on every prompt.**

So the OAuth token is minted once, when the terminal is created, and then **never refreshed**. Access
tokens live about an hour. Any terminal left open longer than that is holding an **expired** token, and
nothing in the system can replace it.

A second, compounding defect made the intended safety net inert:

> **mise also cannot propagate an `unset` from a `_.source` script back into an existing shell.**

`.mise/env.sh` signalled "the mint failed" by *unsetting* `DBT_ACCESS_TOKEN`, so even on the rare
occasions the script did re-run and the mint failed, the shell kept the previous expired token instead of
falling back to the non-empty sentinel (`MISSING_run__mise_run_setup_databricks`) that exists precisely to
produce an actionable error.

dbt therefore sends an expired credential and dies with an opaque `401`/`403`, while
`databricks auth describe` keeps reporting success — because it reads the CLI profile and refresh token in
`~/.databrickscfg`, **not** the stale token sitting in your shell's environment. The CLI says
authenticated, dbt says unauthorized, and both are telling the truth about different things.

---

## 2. Impact / who was affected

- **Any trainee with a terminal open longer than the OAuth access-token lifetime (~1 hour).** The first
  dbt command after a failed mint fails, and **keeps failing for the life of that terminal**, because the
  expired token can never be replaced by the failure path.
- The error is `401`/`403` from `OpenSession` — it names no cause and suggests no action.
- The designed recovery affordance (sentinel → *"run `mise run setup:databricks`"*) was **dead code** in
  exactly the scenario it existed for.
- Highly confusing to diagnose: the natural check, `databricks auth describe`, reports green.

---

## 3. Symptoms

| What you see | What it actually means |
|---|---|
| `dbt debug` fails, `databricks auth describe` succeeds | Shell holds an expired token; CLI profile is fine |
| `Error during request to server`, `http-code=403`/`401`, `method=OpenSession` | Databricks rejected the token dbt sent |
| It worked an hour ago in this same terminal, now it does not | The token was minted once at shell start and never refreshed; it has expired |
| A **new** terminal works immediately | New shell = a fresh (one-time) mint |
| Later, the **old** terminal starts working again | Something changed `.mise/env.sh`'s mtime, invalidating mise's cache and forcing a re-mint |

The "works in a new terminal, not this one" pattern is the signature of this bug, and it is fully
explained by §4.

---

## 4. Root cause

### 4.1 The mechanism, as designed

1. `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml` reads the token from the environment:
   `token: "{{ env_var('DBT_ACCESS_TOKEN', env_var('DATABRICKS_TOKEN', 'MISSING_run__mise_run_setup_databricks')) }}"`
2. `.mise.toml` wires `_.source = ".mise/env.sh"`.
3. `.mise/env.sh` mints a fresh OAuth access token with `databricks auth token` and exports it.

The design assumes step 3 happens on **every prompt**, via `mise activate` → `PROMPT_COMMAND` →
`mise hook-env`. That assumption is the bug.

### 4.2 Primary defect: the mint runs ONCE per shell session

Measured with a counter that appends one line per script execution:

```
after hook1: PROBE_TOKEN=token_1  script_executions=1
after hook2: PROBE_TOKEN=token_1  script_executions=1
after hook3: PROBE_TOKEN=token_1  script_executions=1
after hook4: PROBE_TOKEN=token_1  script_executions=1
```

Four prompt hooks, **one** execution. mise caches the environment computed from a `_.source` script for
the life of the shell session. The only observed invalidator is a change to the script file itself:

```
hook2: token=token_3 execs=3
--- touch env.sh (mtime change) ---
hook3: token=token_4 execs=4      <-- re-executed, new value applied
--- touch again ---
hook4: token=token_5 execs=5      <-- re-executed again
```

Note what this also proves: when the script *does* re-run, a changed value **is** applied to the running
shell. Propagation works. The mint simply never happens again.

Consequence: a terminal opened at `10:00` mints a token valid until `~11:00`, and then holds that
**expired** token for as long as it stays open — hours or days.

### 4.3 Secondary defect: `unset` cannot signal failure across the mise boundary

Even in the rare case where the script re-ran (an edit to `.mise/env.sh`, a config change) and the mint
failed, the failure path could not clear the bad token. Proven with a minimal, isolated repro (no
Databricks involved):

```bash
# env.sh: exports PROBE_TOKEN=good_token_v1, unless /tmp/misetest/FAIL exists -> then it unsets it
step1_PROBE_TOKEN=good_token_v1          # first hook: mise exports it
touch /tmp/misetest/FAIL                 # now the script unsets instead of exporting
step2_after_mint_failure=good_token_v1   # <-- unchanged
step3_after_more_hooks=good_token_v1     # <-- still unchanged, forever
VERDICT=MISE_DOES_NOT_PROPAGATE_UNSET__STALE_VALUE_PERSISTS
```

`.mise/env.sh` used `unset` as its failure signal in two places:

```bash
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then
  unset DBT_ACCESS_TOKEN DATABRICKS_TOKEN          # (a) clear before minting
  ...
  if [ -n "$_oauth_token" ]; then
    export DBT_ACCESS_TOKEN="$_oauth_token"        # success path only
  elif [ -t 2 ]; then
    ...warn...                                     # failure path exports NOTHING
  fi
fi
...
[ -n "${DBT_ACCESS_TOKEN:-}" ] || unset DBT_ACCESS_TOKEN   # (b) empty -> unset
```

So the sentinel and the "re-authenticate" warning were both **dead code in the scenario they were
written for**.

### 4.4 Why the symptoms look random

| Observation | Explanation |
|---|---|
| A new terminal always works | New shell = first (and only) mint = fresh token |
| The same terminal fails after ~1 h | The one-time token expired and is never re-minted |
| An old terminal later starts working again | Something changed `.mise/env.sh`'s mtime (an edit, a tooling write), which invalidated mise's cache and forced a re-mint |
| `databricks auth describe` stays green | It mints on demand from the refresh token; it never inspects the shell's `DBT_ACCESS_TOKEN` |

### 4.5 Why the previous RCA's safety net did not cover this

`docs/rca/2026-08-03-dbt-databricks-auth-hang.md` added the non-empty sentinel so a *missing* token would
fail fast instead of hanging on the browser login. That reasoning is correct, but it depends on
`env_var()` seeing the variable **unset** — which §4.3 shows the script cannot achieve in a running shell,
and §4.2 shows it rarely even gets the chance to try.

### 4.6 Contributing factor: no retry on a network call

The mint is a network round-trip wrapped in `timeout 10` with no retry, so a single transient blip was
enough to enter the (broken) failure path.

---

## 5. How to reproduce

**The refresh gap (§4.2)** — a counter proves the script runs once per session:

```bash
mkdir -p /tmp/misetest && cd /tmp/misetest
printf 'echo exec >> /tmp/misetest/COUNTER\nexport PROBE_TOKEN="token_$(wc -l < /tmp/misetest/COUNTER)"\n' > env.sh
printf '[env]\n_.source = "env.sh"\n' > .mise.toml
: > COUNTER; mise trust .mise.toml
eval "$(mise activate bash)"; cd /tmp/misetest
_mise_hook; echo "execs=$(wc -l < COUNTER)"   # 1
_mise_hook; echo "execs=$(wc -l < COUNTER)"   # still 1
touch env.sh
_mise_hook; echo "execs=$(wc -l < COUNTER)"   # 2  -- only an mtime change re-runs it
```

**The unset gap (§4.3)** — run `.mise/env.sh` the way mise runs it, with a stale token present and no
reachable OAuth token cache:

```bash
mkdir -p /tmp/fakehome/.config/dpc
cp "$HOME/.config/dpc/databricks.env" /tmp/fakehome/.config/dpc/databricks.env

env -i HOME=/tmp/fakehome PATH=/usr/bin:/bin TMPDIR=/tmp \
  DBT_ACCESS_TOKEN=STALE_EXPIRED_TOKEN \
  bash --noprofile -c '. .mise/env.sh; echo "final_token=${DBT_ACCESS_TOKEN:-<UNSET>}"'
```

| Script version | Output | Effect in a real shell |
|---|---|---|
| **Before fix** | `final_token=<UNSET>` | mise cannot apply an unset → shell keeps `STALE_EXPIRED_TOKEN` → opaque `401`/`403` |
| **After fix** | `final_token=MISSING_run__mise_run_setup_databricks` | mise applies the sentinel → dbt fails fast with an actionable error |

---

## 6. The fix

Two layers, because there are two defects.

### 6.1 Primary — refresh the token from the shell itself

`.devcontainer/utils/setup-mise.sh` now generates a `_refresh_databricks_token` function into
`/etc/profile.d/mise-init.sh` and invokes it from **two** places:

```bash
PROMPT_COMMAND="_refresh_databricks_token;_update_bundle_branch_vars${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
trap '_dpc_preexec' DEBUG     # interactive shells only
```

Because these run **inside the shell**, `export` applies directly — mise's cache and its unset semantics
are bypassed entirely. Raw `dbt` therefore always sends a live credential, with no wrapper.

**Why both hooks are needed.** `PROMPT_COMMAND` fires when the prompt is *drawn* — that is, after the
previous command finished. The shell then sits idle at that prompt, potentially for hours. If the token
expires during that idle window, the next command the user types **still runs with the stale token** and
fails `403`; the refresh only happens afterwards. That produces the signature symptom:

> "I got a 403, but then I re-ran it right now and it worked."

Measured ordering in an interactive bash:

```
PROMPT_COMMAND FIRED     <- prompt drawn; refresh happens here, then the shell idles
MY COMMAND RUNS          <- runs with whatever token was current at prompt-draw time
PROMPT_COMMAND FIRED

DEBUG TRAP FIRED         <- fires BEFORE the command
MY COMMAND RUNS
```

The `DEBUG` trap closes that gap by refreshing immediately before each command, so the credential is
guaranteed live at the moment it is actually used.

Design points:

- **OAuth only.** No-ops immediately in PAT mode.
- **Cheap fast path.** A pure-builtin comparison against `_DPC_TOKEN_NEXT_CHECK` using bash's
  `EPOCHSECONDS`; no subprocess, no network, on an ordinary command. Measured overhead of the DEBUG
  trap: **0.016 s for 300 commands** (~53 µs each).
- **Re-check 5 min before expiry**, so a long-running dbt command cannot straddle the boundary.
- **Minimum 60 s between mints.** The Databricks CLI serves a cached token until it is nearly expired, so
  without a floor every prompt inside the 5 min margin would mint again. This was caught in testing: the
  first implementation took **29 s for 200 prompts**; with the floor it takes **0.006 s**.
- **Failure never leaves a stale token.** A failed mint overwrites `DBT_ACCESS_TOKEN` with the sentinel
  and retries in 60 s.
- **The trap never cancels a command.** `_dpc_preexec` skips completion expansion and the
  `PROMPT_COMMAND` invocation, and always returns 0 (under `shopt -s extdebug` a non-zero return from a
  DEBUG trap would skip the user's command).

### 6.2 Secondary — `.mise/env.sh` never signals failure with `unset`

The initial mint at shell start keeps its role, but now always exports an explicit value:

```bash
if [ -n "$_oauth_token" ]; then
  export DBT_ACCESS_TOKEN="$_oauth_token"
else
  export DBT_ACCESS_TOKEN="MISSING_run__mise_run_setup_databricks"
  # ...throttled, loud "OAuth session expired" warning on a real terminal...
fi
```

plus a bounded retry (3 attempts, 1 s apart) around the mint, and a final normalization that **exports**
the sentinel instead of unsetting — preserving the anti-hang guarantee from the previous RCA (an *empty*
token sends dbt-databricks into `authenticate_with_external_browser()` and hangs forever).

### 6.3 Regression tests (`tests/local_env/offline/auth/test_auth_contracts.py`)

- `test_shell_prompt_refreshes_databricks_oauth_token`
- `test_shell_token_refresh_is_gated_on_expiry` (including the re-check floor)
- `test_shell_token_refresh_never_leaves_an_expired_token`
- `test_shell_token_refresh_is_oauth_only`
- `test_failed_oauth_mint_exports_sentinel_instead_of_unsetting`
- `test_mise_env_never_relies_on_unset_to_clear_the_dbt_token`
- `test_oauth_mint_retries_before_giving_up`
- `test_profiles_sentinel_matches_mise_env_sentinel`

---

## 7. Verification (evidence)

| Scenario | Result |
|---|---|
| Does `_.source` re-run per prompt? | **No** — 4 hooks, 1 execution; `touch` → re-runs |
| Isolated repro of mise unset semantics | `VERDICT=MISE_DOES_NOT_PROPAGATE_UNSET__STALE_VALUE_PERSISTS` |
| Pre-fix `.mise/env.sh`, stale token + failed mint | `final_token=<UNSET>` → stale token survives |
| Post-fix `.mise/env.sh`, stale token + failed mint | `final_token=MISSING_run__mise_run_setup_databricks` |
| Prompt hook, terminal holding an expired token | `RESULT=REFRESHED len=795` — live token restored |
| **Idle terminal, token expired, then a command is typed** | `VERDICT=FIXED_refreshed_before_command_ran` (pre-`DEBUG`-trap: the command ran with the stale token and 403'd) |
| Prompt hook, lapsed session (mint returns nothing) | `RESULT=SENTINEL__no_stale_replay` |
| Prompt hook cost, 200 prompts | `0.006 s` (first implementation: `29 s` — fixed with the re-check floor) |
| DEBUG trap cost, 300 commands | `0.016 s` (~53 µs per command) |
| Raw `dbt debug` (Challenge 02, healthy session) | `Connection test: [OK connection ok]` / `All checks passed!` |
| Raw `dbt debug` with the sentinel | `Connection test: [ERROR]` + HTTP 401 in ~4 s — fast and clear, **no hang** |
| Offline suite (`tests/local_env/offline`, `tests/challenges/offline`) | 203 passed, 1 pre-existing unrelated failure (`check.sh` `--pat` assertion) |

---

## 8. Applying the fix to a running container

No rebuild is required.

```bash
mise run setup:mise     # regenerates /etc/profile.d/mise-init.sh
```

Then open a new terminal (existing terminals keep the old `PROMPT_COMMAND` until they are restarted).
From then on, terminals refresh their own token indefinitely.

---

## 9. Why this was worth fixing

1. **It was guaranteed to happen, not merely possible.** The token was minted once per terminal and never
   refreshed, so *every* terminal older than the ~1 h token lifetime was broken. This was not a race or a
   flaky network — it was the designed behaviour.
2. **The failure is sticky.** Once expired, that terminal stayed broken until it was closed.
3. **It disabled the existing safety net.** The sentinel and the "re-authenticate" warning were both inert
   in the one scenario they were written for.
4. **The diagnostic signal actively misleads.** `databricks auth describe` says authenticated, so users
   and agents look everywhere except the real cause.
5. **The fix is small and local.** No change to the auth strategy, no wrapper, and raw `dbt` keeps working
   unchanged.

---

## 10. Lessons

1. **Verify the execution model before trusting a comment.** The header of `.mise/env.sh` claimed it was
   "evaluated on every shell prompt". A counter file disproved it in one minute. Every conclusion in the
   first pass of this investigation was wrong because that claim was taken at face value.
2. **mise `_.source` is evaluated once per session and keyed on file mtime.** It is a place to *seed* an
   environment, never a place to *refresh* a short-lived credential.
3. **`unset` does not cross a mise `_.source` boundary.** Signal failure by exporting an explicit
   sentinel, never by removing the variable.
4. **"Empty is not unset" now has a third sibling: "unset is not removed."** This repo has been bitten by
   the same family of bug three times (`DBT_ACCESS_TOKEN=""`, Compose `${VAR:-}`, and now this).
5. **Check credential *surfaces*, not credential *status*.** `databricks auth describe` validates the CLI
   profile; dbt uses a shell variable. Any check that does not read the exact credential the failing
   process used can produce a confident, wrong answer.
6. **Measure the cost of anything added to `PROMPT_COMMAND`.** The first version of the refresh minted on
   every prompt once inside the expiry margin — 145 ms per prompt. A cheap gate plus a minimum re-check
   interval brought it to ~30 µs.
7. **`PROMPT_COMMAND` is "after the command", not "before the next one".** It cannot protect a command
   typed after an idle prompt, which is exactly when a credential is most likely to have expired. The
   giveaway symptom is *"it failed, I re-ran it, it worked"* — the refresh happened between the two
   attempts. Use a `DEBUG` trap when something must be current at the moment a command starts.

---

## 11. Follow-ups

- Audit any other `_.source`-seeded value that is expected to stay fresh; the same one-shot caching
  applies to all of them.
- Consider a `dpc-check` probe that decodes the shell token's `exp` and reports drift between
  "CLI authenticated" and "token dbt would actually send" — the exact contradiction that made this hard
  to diagnose.
- Add the §3 symptom table to `.devcontainer/TROUBLESHOOTING.md` under the existing
  *"`dbt debug` fails even though Databricks CLI works"* entry.
- Correct the stale header comment in `.mise/env.sh` if it is ever reworded again — it is what sent this
  investigation down the wrong path initially.
