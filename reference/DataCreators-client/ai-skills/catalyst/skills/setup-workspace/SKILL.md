---
name: setup-workspace
description: >-
  Prepares a local machine to run AI Catalyst.  Detects an existing package
  manager and, if one is present, installs a compatible Python (3.13) and the
  Catalyst dependencies through cgrepo, then verifies the toolchain.  If no
  package manager is present, it guides the user instead of installing one.
  Also turns on Copilot Chat usage reporting, editing User settings.json in place
  and preserving existing settings and comments.
  Use when: "set up my workspace", "set up the environment", "install the
  prerequisites", "get me ready to run Catalyst", "my environment is not ready",
  "turn on usage reporting", "enable telemetry", "set up otel".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# setup-workspace

Prepares a local machine to run AI Catalyst.  It automates the toolchain steps
from `docs/install.md` that an agent can safely perform, and guides the rest.

## When to use

Run this when the concierge judges a user to be new (no data-product artifacts
and no `.env`), when a user asks to set up their environment, or when a skill
cannot run because Python or the Catalyst dependencies are missing.  A user can
also invoke it directly.  When the workspace is already ready, confirm that
quickly and hand back.

## Source of truth

`docs/install.md` is authoritative for the required versions and settings:
Python 3.10 minimum, Python 3.13 recommended (never the newest release), the
cgrepo index URL, and the dependency file `skills/requirements.txt`.  install.md
also documents human-only steps such as the VS Code and Copilot Chat plugin
toggles.  This skill does not attempt those, since the assistant is already
running inside that host.

## Two scripts, split by what needs Python

- `scripts/bootstrap.sh` (macOS, Linux) and `scripts/bootstrap.ps1` (Windows)
  need no Python.  Each ensures a compatible Python: it installs Python 3.13
  through a package manager that is present (Homebrew or uv on the shell side;
  winget, choco, or uv on the PowerShell side), and otherwise guides the user to
  the Capital Group self-service app or app store.  This is the part that must
  work on a machine that has no Python yet.
- `scripts/setup_workspace.py` runs only after Python exists.  It points pip at
  cgrepo, installs the dependencies, and reports readiness.

## What this skill does and does not do

Does:

- Ensure Python 3.10+ (recommended 3.13) via `bootstrap.sh`.
- Point pip at the cgrepo internal mirror, which is required for installs to
  succeed on the corporate network.
- Install the core Catalyst dependencies through cgrepo, and attempt the
  tested-against extras (dbt, the legacy databricks-cli) best-effort so a stale
  pin cannot block a working setup.
- Offer to install the important extra tools, git and gh.
- Verify the result at each stage and report plainly.

Does not:

- Install a package manager.  On a Capital Group machine the standard
  installers run remote scripts from the public internet, which the corporate
  network blocks and the supply-chain policy forbids.  When no package manager
  is present, this skill guides the user to the sanctioned source instead.
- Set up Databricks, Confluence, or Astronomer.  Those are optional
  integrations owned by other skills.
- Provision credentials or entitlements.  Those are not self-serve.

## Readiness check

The workspace is ready when all of the following pass.  git and gh are reported
but do not block readiness; they feed the optional-tools step.

| Check | Good when | Action on a gap |
|:------|:----------|:----------------|
| Python present | An interpreter 3.10 or newer is on PATH | `bootstrap.sh` installs 3.13, or guides to the sanctioned source |
| Python not too new | Version is 3.10 to 3.13 | If newer, report it and warn that dependency wheels may lag; do not force a change |
| pip works | `python -m pip --version` runs | pip ships with Python; if it is broken, reinstall Python |
| pip points at cgrepo | The effective index URL is the cgrepo mirror | Set `index-url` in the user's existing pip config (merged, not overwritten; timestamped backup first) |
| Dependencies installed | The core deps import (pydantic, pyyaml, requests, databricks-sdk) | Install from `skills/requirements.txt` through cgrepo |

## Procedure

Steps that are not automatic are multi-turn: guide the user, end the turn, and
re-check when the user returns and says it is done.

> **On a Capital Group managed machine, expect Step 1 to guide rather than
> install.** `brew install python@3.13` and `uv python install` both fetch from
> ghcr.io / GitHub, which the corporate network blocks. The script degrades
> correctly to printed guidance (exit 3), but on a CG-managed laptop that branch
> is the **normal** path, not an edge case. Treat "install it from the
> self-service app, then re-run" as the expected outcome, and do not read exit 3
> as a script failure.

### Step 1 — Ensure Python (needs no Python)

On macOS or Linux run `sh scripts/bootstrap.sh`; on Windows run
`pwsh scripts/bootstrap.ps1`.  Either reports the Python version, installs
Python 3.13 through a package manager that is present (Homebrew or uv on the
shell side; winget, choco, or uv on Windows), and otherwise guides.

- Exit 0: Python 3.10 or newer is ready.  Go to Step 2.
- Exit 3: Python could not be provisioned here (no usable package manager, or
  the install did not produce a usable Python).  Follow the printed guidance
  (the Capital Group self-service app on Mac, the app store or Company Portal on
  Windows), then re-run bootstrap.  This is multi-turn: the user installs,
  returns, and you re-run.

### Step 2 — Configure the Python toolchain

Once Python is ready, run `python3 scripts/setup_workspace.py configure`.  It
points pip at cgrepo (writing the configuration if needed) and installs the core
dependencies from `skills/requirements.txt` through cgrepo, attempting the
tested-against extras best-effort so a stale extra pin does not block a working
setup.

### Step 3 — Verify

Run `python3 scripts/setup_workspace.py check` and report the verdict.  Do not
claim the workspace is ready unless check exits 0.

### Step 4 — Offer the important extra tools

Present git and gh as optional installs, and nothing else.  If the user wants
them, install through the same logic: use the package manager if present,
otherwise guide to the sanctioned source.  gh additionally requires an
interactive `gh auth login --web`, which this skill cannot perform: guide the
user through it and re-check with `gh auth status`.

### Step 4b — Offer usage reporting

Optional, and unrelated to whether Catalyst runs. Ask whether the user wants to
turn on Copilot Chat usage reporting, which tells the EDO team which skills are
earning their keep and where people get stuck. Full explanation of what is and is
not reported: `docs/catalyst-otel-getting-started.md`.

```bash
python3 scripts/setup_workspace.py otel            # dry run: shows the diff
python3 scripts/setup_workspace.py otel --apply    # writes, after a backup
python3 scripts/setup_workspace.py otel --endpoint dev --apply   # report to dev
```

**`--endpoint` takes `prd` (the default) or `dev`, and nothing else.** Unlike
`claude-otel` below it defaults rather than asking, because prd is routable from the
laptops Copilot Chat runs on — there is a right answer. Use `dev` only when the user
asks for it, and say which collector you wrote. Names only, no free-form URL:
`/dplc-preflight` reports anything that is not one of the two known collectors as a
problem, so a URL here would write a state the checker rejects.

**Show the dry-run diff and get agreement before applying.** The diff is the
consent step — this edits a file full of the user's own preferences.

Three things to say when you report the result:

1. **They must reload the window** — `Developer: Reload Window`. That starts the
   exporter; a full quit works too but is not required. This is the step people
   miss and the reason reporting appears not to work.
2. **Nothing they type is reported.** `captureContent` is written `false`, which is
   what keeps conversation text out. Do not offer to change it — `true` requires a
   Governance, Risk and Compliance review, and the script refuses to write it.
3. **It needs the corporate network or VPN.** Use `/dplc-preflight otel
   --probe-endpoint` to check reachability if they are unsure.

If `captureContent` was already `true`, the plan flips it to `false` and says so.
Report that plainly — it means conversation text was being sent, and the EDO team
should know.

#### Step 4c — Claude Code reporting, if that is the harness

`otel` above configures **VS Code Copilot Chat**. Claude Code is a different
mechanism and needs its own command. Offer it only when running under Claude Code
(`CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT`) — on a machine without it there is nothing
to configure.

```bash
python3 scripts/setup_workspace.py claude-otel --endpoint dev            # dry run
python3 scripts/setup_workspace.py claude-otel --endpoint dev --apply    # writes
```

Writes an `env` block into `~/.claude/settings.json`. Every other setting keeps its
value — but note the file is re-serialised, so formatting and non-ASCII escaping may
change even where values do not. It is not a byte-for-byte edit, and a backup is taken
before writing.

Same consent-by-diff rule as `otel`: **show the output and get agreement before
applying.** What it prints is scoped to the keys being written, deliberately — a
whole-file diff would pull in neighbouring `env` entries, which are frequently
credentials, and this output is designed to be shown in chat.

Four things to say when reporting the result:

1. **`--endpoint` has no default, deliberately.** `prd` is not routable from an
   oz-dev Coder workspace (TCP 443 opens, TLS resets), so defaulting to it would
   configure something that drops every batch while every local check still reports
   `ON`. `dev` would be wrong on a laptop. Ask which; do not guess.
2. **A new session is required, not a reload.** The OTel SDK reads its environment
   once at process start, so the session that ran this keeps exporting nowhere no
   matter what the file now says. This is the step people miss, and unlike the VS
   Code path there is no reload that will do.
3. **Nothing they type is reported, and this is structural rather than a setting.**
   The command writes no logs exporter, no logs endpoint, no generic
   `OTEL_EXPORTER_OTLP_ENDPOINT`, and no content switch — and `apply_claude_otel`
   refuses to write any of them. Prompt text is only ever a *log* record, so a
   configuration that names no logs destination cannot carry it here. That guarantee
   survives someone later enabling a content switch; a policy of four zeroes does not.
4. **Confirm with `/dplc-preflight otel --probe-endpoint`**, which reports the
   verdict and whether the collector is actually reachable.

Why a user-scope file is enough: managed settings outrank user settings, and the
DevNext managed policy sets `CLAUDE_CODE_ENABLE_TELEMETRY`, a logs exporter and the
content switches — but none of the four keys this writes. There is nothing to
outrank. `docs/telemetry/managed-settings-otel.json` remains the artifact for a
fleet-wide rollout; this is the self-serve path for one person.

It refuses rather than guesses in three cases: a settings file containing comments
(a rewrite would delete them), one that will not parse, and one whose `env` is not
an object.

### Step 5 — Hand back

Report the final state and return control to the concierge's guided path so the
user can continue building.

## Safety rails

- Never install a package manager, and never run a `curl | bash` style
  installer.  Provision Python only through the bootstrap script, using a
  package manager that is already present (Homebrew or uv on macOS/Linux;
  winget, choco, or uv on Windows), otherwise guide.
- Install through cgrepo only.  Installing from public PyPI fails on the
  corporate network with a 403 on the package download.
- Target Python 3.13, not the newest release.  Newer releases often lack
  dependency wheels and force source builds that fail on the corporate network.
- If the machine already runs a Python newer than the recommended version and a
  dependency install fails on a missing wheel, report that clearly and
  recommend 3.13 rather than forcing a version change.
- **Set `index-url` and nothing else.** The pip config is a read-modify-write, not
  an overwrite: `cert`, `proxy`, `extra-index-url` and `timeout` are load-bearing,
  and clobbering `cert` on a machine behind corporate TLS interception would break
  pip for everything else the user does. A timestamped backup is taken first.
- **Merge into the config the user already has.** Both `~/.pip/pip.conf` (which
  `docs/install.md` documents) and `~/.config/pip/pip.conf` (which pip prefers when
  both exist) are checked, so this never creates a second competing config whose
  precedence the user has to reason about.
- **Never write `trusted-host`.** It disables certificate validation for the one
  host every corporate install flows through — hardening the supply chain at the
  registry while opening it at the transport. When TLS verification fails, that is
  corporate TLS interception: the fix is `cert = <corporate CA bundle>`, which keeps
  the connection verified. `verify_cgrepo_tls()` probes this and says so.
- **Never write `captureContent: true`.** It sends Copilot Chat conversation text,
  and turning it on requires a formal Governance, Risk and Compliance review. The
  script writes `false` and only `false`, has no parameter to request otherwise,
  and `apply_otel_settings` re-checks the assembled text and refuses to write it —
  so a future caller cannot route around the rule either. If a user asks for it,
  do not oblige; point them at GRC.
- **Edit settings.json textually, never parse-and-rewrite it.** It is JSONC.
  Round-tripping it through a JSON serializer silently deletes every comment and
  reflows the file — the same class of damage as overwriting `pip.conf`. Keys are
  patched in place and inserted as a block, and a timestamped backup is taken
  first.
- **User scope only for settings.json.** Workspace and folder settings do not
  enable the exporter, so writing one would look like success while doing nothing
  outside that folder.
- Do not claim the workspace is ready unless check exits 0.

## Failure modes

`bootstrap.sh` (macOS/Linux) and `bootstrap.ps1` (Windows):

| Exit code | Meaning | Response |
|:----------|:--------|:---------|
| 0 | Python 3.10+ is ready | Proceed to `configure` |
| 3 | Could not provision Python (no usable package manager, or the install did not produce a usable Python) | Guide to the self-service app or app store; multi-turn |

`setup_workspace.py check`:

| Exit code | Meaning | Response |
|:----------|:--------|:---------|
| 0 | Ready | Report success and hand back |
| 2 | Python missing or older than 3.10 | Run `bootstrap.sh` to provision Python |
| 4 | Dependencies missing | `configure` installs core deps (extras best-effort) |
| 5 | pip not pointed at cgrepo | `configure` writes the pip configuration |
