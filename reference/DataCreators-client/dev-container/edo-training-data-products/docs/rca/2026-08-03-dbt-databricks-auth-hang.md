# RCA — dbt/Databricks auth hang in the training challenges

| Field | Value |
|---|---|
| **Date** | 2026-08-03 |
| **Status** | Resolved on `feature/improvements` (PR #12) |
| **Severity** | High — blocked every raw-`dbt` command in the training challenges; intermittently blocked the `mise run` wrapper flow too |
| **Components** | `dbt-databricks` (1.11.7) credential resolution · `.mise/env.sh` (OAuth token mint) · challenge dbt `profiles.yml` · `.devcontainer/devcontainer.json` |
| **Discovered while** | Converting the challenge teaching commands from `mise run challenge:dbt <NN> -- …` to raw `dbt …` and running the live per-command E2E |
| **Fix commits** | `af74103` (sentinel + empty→unset), `fe1f168` (terminal mint resolver), `b5e8a81` (loud re-auth warning), `5dc336e` (design-spec §4a) |

---

## 1. Summary

Running `dbt` against Databricks inside the devcontainer could **hang forever with no output**. The
immediate trigger was an **empty `DBT_ACCESS_TOKEN`** — the token `dbt` uses to log in to Databricks.
When that token is empty, `dbt-databricks` falls back to an interactive login that tries to open a web
browser and then waits — forever — for someone to complete the sign-in. The devcontainer has no web
browser, so the sign-in never happens; and the one on-screen message that would have told the user how
to proceed had been switched off.

Separately, raw `dbt` typed in the terminal **never received a token at all**, because the step that
produces the token could not find the `databricks` command-line tool while the shell was still starting
up.

The bug was **three independently reasonable changes lining up**, none harmful on its own:

1. The challenge dbt config switched from a browser-based login (`auth_type: oauth`) to a login token
   (`DBT_ACCESS_TOKEN`).
2. The on-screen browser-login message was switched off in the devcontainer.
3. The token-producing step only looked for the `databricks` tool in a spot that was empty while the
   shell was still starting up.

The fix has three parts: give the token a **non-empty placeholder default** (so a missing token
produces a clear 2–3 second error instead of an endless hang), **treat an empty token as if it were
unset** in `.mise/env.sh` (so that placeholder actually takes effect), and **fix the tool lookup** so a
fresh terminal produces a real token on its own. All three are verified live.

---

## 2. Impact / who was affected

- **Every trainee (human or business-user subagent) cloning the repo** and running the converted
  challenges: raw `dbt build` / `dbt debug` / `dbt seed` would hang silently with no error, no progress
  bar, and no timeout. The natural response is to kill the terminal and give up.
- The failure was **intermittent for the retained `mise run` flow** (the OAuth token mint occasionally
  returned empty), which produced classic "works on my machine" reports and made it hard to diagnose.
- **Net effect:** the raw-`dbt` training initiative was effectively unusable, and the challenges were
  fragile even before the conversion.

---

## 3. Symptoms

- `dbt debug` (or any connecting command) prints its banner, then **hangs with no further output**.
  It ignores a normal stop request (`SIGTERM`, e.g. Ctrl-C); only a force-kill (`SIGKILL`) stops it.
- A stuck `dbt` process keeps local port **`8020`** open (the address the browser login waits on) for
  as long as it hangs. Observed live: one hung `dbt debug` held port 8020 for 18+ minutes.
- No error is shown, because the process is simply stuck waiting for a web browser to sign in.
- Intermittently, a fresh terminal has an **empty `DBT_ACCESS_TOKEN`** even though
  `DPC_DATABRICKS_AUTH_MODE=oauth` is set.

---

## 4. Root cause

### 4.1 The credential-resolution trap in `dbt-databricks`

`DatabricksCredentialManager.__post_init__`
(`dbt/adapters/databricks/credentials.py:333`, dbt-databricks 1.11.7) selects the auth method by a
simple `if/elif`:

```python
if self.token:                       # line 340
    self._config = self.authenticate_with_pat()          # fast, non-interactive
elif self.azure_client_id and self.azure_client_secret:
    self._config = self.authenticate_with_azure_client_secret()
elif not self.client_secret:         # line 344 — reached when token is EMPTY
    self._config = self.authenticate_with_external_browser()   # BLOCKS on the OAuth callback
```

There is **no cached-session fast path** for the empty-token case. An empty token therefore always
routes to `authenticate_with_external_browser()`, which opens a local callback listener (port 8020)
and blocks until a browser completes the OAuth round-trip. `validate_creds()` (line 135) would raise a
clear error — *"The config `auth_type: oauth` is required when not using access token"* — but it runs
**after** `__post_init__` has already hung, so it never gets the chance.

> Key property proven live: **any non-empty token** takes the PAT path (PAT = *personal access token*,
> a saved credential that needs no browser) and returns in ~2–3 s (a valid token connects; a bogus
> token gets a fast 401/403). Only an *empty* token hangs.

### 4.2 How two merged PRs turned this latent trap into a silent hang

- **PR #14 (`ecacaa1`, "Stabilize portfolio DAG execution and dbt auth in Airflow 3")** converted the
  `portfolio_analytics` `local`/`dev` targets from `auth_type: oauth` to a token
  (`token: "{{ env_var('DBT_ACCESS_TOKEN', …) }}"`). This was **correct for the DAG** — `auth_type: oauth`
  tries to open a browser and hangs in the headless astro worker (headless = no screen or browser
  attached, so a browser login can never complete) — but it made *interactive* dbt depend on the
  token being present, exposing the empty-token trap in §4.1.
- **PR #13 (`5539f11`, "silent the databricks oauth automatic pop up")** set the port-8020 callback to
  `onAutoForward: silent` in `.devcontainer/devcontainer.json`. This removed the **only visible signal**
  that dbt was waiting for a browser login, converting a *recoverable, visible* prompt into a *silent,
  invisible* hang.

Neither PR is "wrong" in isolation; the failure is their **interaction**.

### 4.3 The token supply chain (why the token was empty)

The profiles read `token: "{{ env_var('DBT_ACCESS_TOKEN', env_var('DATABRICKS_TOKEN', '')) }}"`.
`DBT_ACCESS_TOKEN` is minted from the OAuth session by `.mise/env.sh`, which calls
`databricks auth token …`. That mint could return empty (a lapsed session, or transient contention),
and — critically — see §4.4.

### 4.4 The interactive-terminal mint gap (why raw `dbt` never got a token)

This is the second, independent root cause and the one that made the raw-`dbt` conversion unusable even
when the OAuth session was healthy.

`.mise/env.sh` mints the token only if it can locate the `databricks` binary via
`_resolve_databricks_bin()`. The original helper returned early (`return 1`) whenever
`command -v databricks` was empty. But `.mise/env.sh` is sourced by **mise's environment evaluation**
(`_.source` in `.mise.toml`), which runs *while the shell environment is still being built* — before
mise has put the `databricks` **shim** on `PATH` (a shim is the small stand-in launcher mise adds to
`PATH` so a command runs the tool version mise manages). So in the interactive-terminal path,
`command -v databricks` was empty, the resolver bailed, and **no token was minted**.

The asymmetry that made this confusing:

| Context | `databricks` shim on PATH during mint? | Token minted? |
|---|---|---|
| `mise run <task>` (e.g. the old `challenge:dbt`) | Yes (tools already active) | Yes → worked |
| Interactive terminal / `mise hook-env` (raw `dbt`) | **No** (env still being evaluated) | **No** → empty → hang |

So the *old* wrapper flow got a token and worked, while the *new* raw-`dbt` flow silently did not — which
is exactly why the conversion appeared to "break" auth.

### 4.5 Why the profile's `env_var` default did not save us

`env_var('DBT_ACCESS_TOKEN', '<default>')` in dbt returns `<default>` **only when the variable is
unset**. A variable that is *set but empty* (`DBT_ACCESS_TOKEN=""`) resolves to `""`, bypassing any
default. `.mise/env.sh`'s `.databrickscfg` fallback could `export DBT_ACCESS_TOKEN=$(…)` to an **empty
string** (OAuth `.databrickscfg` has no `token` line), and a failed mint left it empty — so even a
non-empty profile default would have been bypassed without the normalization in §6.2.

---

## 5. How to reproduce

In the devcontainer, from the repo root:

```bash
# Reproduce the empty-token path deterministically
cd challenges/02-dbt-pipeline/dbt
env -u DBT_ACCESS_TOKEN -u DATABRICKS_TOKEN dbt debug
```

- **Before the fix** (profile default `''`, port 8020 silent): `dbt debug` prints its banner and **hangs
  indefinitely**; `ss -ltnp | grep :8020` shows the hung `dbt` holding port 8020 (the browser-login port).
- **After the fix** (non-empty sentinel default): `dbt debug` fails in ~2–3 s with
  `Connection test: [ERROR]` / HTTP 401 *"Credential was not sent or was of an unsupported type"*.

To reproduce the **mint gap** (§4.4) specifically:

```bash
# Non-interactive shell mimics mise env-eval (databricks shim not yet on PATH)
docker exec <container> bash -lc 'echo "token len=${#DBT_ACCESS_TOKEN}"'   # before fix: 0
```

---

## 6. The fix

### 6.1 Non-empty sentinel token default — the anti-hang guarantee (`af74103`)

Every challenge profile now defaults the token to a non-empty **sentinel** — a fixed placeholder value
that is obviously not a real token — instead of `''`:

```yaml
token: "{{ env_var('DBT_ACCESS_TOKEN', env_var('DATABRICKS_TOKEN', 'MISSING_run__mise_run_setup_databricks')) }}"
```

Because the token is **never empty**, `dbt-databricks` always takes the fast PAT path (§4.1) — so the
external-browser hang **can never trigger**. A missing/invalid token becomes a clear 401/403 in ~2–3 s.
Applied to `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml`,
`data_products/atlas_elt/dbt_profiles/profiles.yml`,
`data_products/portfolio_analytics/dbt/profiles.yml`, and the challenge-03 stub/solution copies.

### 6.2 Empty→unset normalization in `.mise/env.sh` (`af74103`)

`.mise/env.sh` now (a) never exports an empty token from `.databrickscfg`, and (b) normalizes an empty
`DBT_ACCESS_TOKEN`/`DATABRICKS_TOKEN` to *unset* so the sentinel default in §6.1 actually applies (see
§4.5).

### 6.3 Interactive-terminal token-mint resolver fix (`fe1f168`)

`_resolve_databricks_bin()` now falls back to the installed binary under
`~/.local/share/mise/installs/databricks-cli/**/databricks` when `command -v databricks` is empty (the
mise env-eval case), not only when it resolves to a shim. A fresh terminal now auto-mints a real token,
so raw `dbt debug` connects with no manual auth.

### 6.4 Loud re-auth warning + agent policy (`b5e8a81`, `d60a227`)

When the mint fails, `.mise/env.sh` prints a throttled, loud warning telling the trainee to run
`mise run setup:databricks`. `.github/copilot-instructions.md` and `docs/agent-runbook.md` require agents
to prompt the user on auth failure rather than abandon the task.

---

## 7. Verification (evidence)

All verified live in the devcontainer against Databricks:

| Scenario | Result |
|---|---|
| Fresh interactive terminal → raw `dbt debug` (no manual auth) | `Connection test: [OK]` / **All checks passed!** in ~4 s |
| Missing/empty token → `dbt debug` | `Connection test: [ERROR]` (HTTP 401) in ~2 s — **no hang** |
| `mise run challenge:dbt 02 -- debug` (regression) | still connects |
| Offline suite | 88 passing (`tests/challenges/offline` + atlas local-runtime contract) |

---

## 8. Consequences of not fixing

- **Silent, unbounded hang for every trainee.** No error, no timeout, no progress — the worst possible
  failure mode for a beginner audience, who cannot distinguish "slow" from "wedged." Expected outcome:
  abandonment of the challenge and of the raw-dbt initiative.
- **Non-deterministic reproduction.** The mint's intermittent emptiness produced "works on my machine"
  reports, burning disproportionate diagnostic time (this RCA's investigation spanned dozens of live
  runs before the mechanism was pinned down).
- **Resource leak.** Each hang leaks a `dbt` process pinning port 8020; subsequent OAuth attempts then
  fail with `Address already in use`, compounding confusion.
- **False attribution.** Because the raw-`dbt` conversion surfaced the mint gap (§4.4), the conversion
  itself looked broken, risking a revert of otherwise-correct work.

---

## 9. Insights & lessons learned

1. **Latent-fault alignment.** Three individually defensible changes (token auth, a silenced port, a
   PATH-order assumption) combined into a severe outage. Review changes for how they interact with the
   *failure* modes of adjacent systems, not just the happy path.
2. **Never silence a recovery affordance.** PR #13 silenced the OAuth callback prompt for tidiness; that
   prompt was the only thing telling a user how to recover. Silencing it converted a self-healing prompt
   into a silent hang. Prefer making prompts *quieter*, not *invisible*.
3. **Fail fast and loud beats "correct but blocking."** The sentinel does not make auth succeed — it
   converts an infinite silent hang into a fast, clear error paired with an actionable message. For a
   beginner audience that trade is almost always right.
4. **`env_var(x, default)` only defaults when *unset*.** A set-but-empty variable silently defeats the
   default. Normalize empties to unset at the source.
5. **Anything a mise `_.source` script calls must resolve by absolute path.** mise evaluates the env
   *before* activating tool shims, so `command -v <tool>` is unreliable inside that script.
6. **`auth_type: oauth` vs token is an environment-specific choice, not a global one.** OAuth
   external-browsers (and hangs) in a headless worker; token auth hangs interactively when the token is
   empty. The token model is the right call here — it just needs the sentinel + a reliable mint to be
   safe on both paths. See related: `docs/superpowers/specs/2026-07-21-databricks-auth-strategy-design.md`
   and `…/2026-07-23-airflow-oauth-token-drift-prevention-design.md`.

---

## 10. Follow-ups / recommendations

- **Broaden the sentinel repo-wide.** Non-challenge data products (e.g. `asset_reference_data`,
  `shared_ref`) still default their profile token to `''` and remain exposed to the same hang. Apply the
  sentinel to all `profiles.yml` token defaults, or centralize the guarantee.
- **Harden the mint.** Consider a short bounded retry around `databricks auth token` in `.mise/env.sh`
  for transient emptiness (kept out of this fix to avoid slowing the shell prompt; the sentinel already
  removes the catastrophic hang).
- **Revisit PR #13's `onAutoForward: silent`.** With the sentinel in place the callback never fires for
  the challenge profiles, so it is moot there — but a visible-but-quiet setting would restore a
  self-healing prompt for any code path that still uses `auth_type: oauth`.
- **Upstream note.** `dbt-databricks` has no cached-OAuth-session fast path for an empty token; a
  bounded timeout on `authenticate_with_external_browser()` would prevent unbounded hangs for everyone.

---

## 11. References

- **Fix commits:** `af74103`, `fe1f168`, `b5e8a81`, `d60a227`, `5dc336e` (all on `feature/improvements`, PR #12).
- **Contributing PRs:** #14 `ecacaa1` (oauth→token), #13 `5539f11` (silent port 8020).
- **Code:** `dbt/adapters/databricks/credentials.py:333` (`__post_init__`), `:340` (PAT), `:344`
  (external-browser), `:135` (`validate_creds`); `.mise/env.sh` (`_resolve_databricks_bin`, mint block,
  empty→unset normalization); challenge `profiles.yml` token defaults; `.devcontainer/devcontainer.json`
  (port 8020 `onAutoForward`).
- **Design record:** `docs/superpowers/specs/2026-07-31-challenge-raw-dbt-commands-design.md` §4a.
