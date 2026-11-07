---
name: dplc-preflight
description: >-
  Pre-flight check before any Data Product Lifecycle work. Answers the zero-to-one
  questions: can I run Catalyst, which Databricks workspace am I pointed at (and
  which others are available), do I actually have access, where would my data
  product go, and is Copilot Chat usage reporting on and set safely. Detects
  workspaces rather than assuming the user knows theirs. Use when: "am I set up",
  "which workspace am I in", "what workspaces do I have", "do I have access",
  "check my environment", "am I ready to start", "pre-flight", "nothing works",
  "where does my data product go", "is usage reporting on", "is telemetry
  enabled", "check my otel config".
allowed-tools: Read Bash Grep
metadata:
  tier: workflow
  lifecycle-phase: cross-cutting
  dependencies:
    - setup-workspace
    - databricks-config
    - connect-databricks
    - configure-sql-warehouse
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-SEC-002
---

# DPLC Pre-flight

Establish whether the user is set up for success **before** they start authoring
artifacts. This is the "zero-to-one" gate: it assumes nothing about what the user
already knows, and it detects rather than asks wherever detection is possible.

## When to use

- The concierge routes a new or unsure user here before any stage handoff.
- The user says nothing works, or asks which workspace they should use.
- A skill failed with an auth or access error and the cause is unclear.
- Directly, as `/dplc-preflight`, any time.

If `.catalyst-env.yml` exists and is current, report the cached verdict and offer
to re-run rather than re-probing.

## What it answers

| # | Question | How it is answered |
|:--|:---------|:-------------------|
| 1 | Can I run Catalyst at all? | Python version + core imports, standard library only |
| 2 | Which workspace am I pointed at? | Env vars, then `~/.databrickscfg`; **lists every profile found** |
| 3 | Do I have access? | Live `current_user.me()`, warehouse list, catalog list |
| 4 | Where would my product go? | The catalogs the identity can actually see |
| 5 | Is usage reporting on, and safe? | The four `github.copilot.chat.otel.*` keys in **User** `settings.json`, **plus `resourceAttributes.user.id`** — without it the exporter works and every report is anonymous, so `ON` requires it |

Question 2 is the one users most often cannot answer themselves. The script reads
`~/.databrickscfg` directly, so it can list available workspaces even when nothing
is installed yet.

Question 5 is **advisory and never changes the exit code.** Telemetry is not a
prerequisite for building a data product, so a machine with reporting off is still
`READY`. It is reported because the settings are easy to get subtly wrong and
there is no confirmation anywhere in the VS Code UI — by design — so a user
cannot otherwise tell.

Its verdicts:

| Verdict | Meaning |
|---|---|
| `NOT_CONFIGURED` | None of the four keys are set, or no User `settings.json` exists yet |
| `ON` | All four correct, and the file was not edited in the last 10 minutes |
| `ON_PENDING_RESTART` | Correct, but edited moments ago — the exporter starts on a window reload, and a script cannot observe a reload, so recent edits are reported as probably-pending |
| `MISCONFIGURED` | Some keys set, one or more wrong or missing; each is named |
| `EXPLICITLY_OFF` | `enabled: false`, a deliberate opt-out rather than a mistake |
| `CAPTURE_CONTENT_ENABLED` | `captureContent: true`. **Outranks every other verdict.** Conversation text would be sent, which requires a Governance, Risk and Compliance review |
| `SETTINGS_UNREADABLE` | A settings file exists but will not parse — usually a comma |

**Either Catalyst collector is accepted**, `prd` or `dev` — not `prd` alone. Pointing
Copilot Chat at dev is a legitimate override, and `/setup-workspace otel --endpoint dev`
is how to ask for it. Checking against prd alone meant a machine deliberately set to dev
was called `MISCONFIGURED` directly above `Reachable: yes` for that same endpoint, and a
check that contradicts itself in adjacent lines is one people learn to skip.

Accepted is not the same as unremarked: dev is reported as a **note** naming the
collector, because a laptop that has been reporting into dev for a month because someone
forgot is the failure the note exists to prevent. The note never changes the verdict.
Any endpoint that is neither collector is still a problem.

### Question 5b — the same question for Claude Code

Claude Code telemetry is a *different mechanism* and gets its own report when the
skill is running under that harness (detected from `CLAUDECODE` /
`CLAUDE_CODE_ENTRYPOINT`, never assumed). Env vars rather than settings keys, and
**four** content switches instead of one.

**It checks the metrics signal only, and that is the whole policy.** Catalyst needs
to know which skills and agents ran. Those ride on `skill.name`, `agent.name`,
`plugin.name` and `marketplace.name`, which are attributes on the `cost.usage` and
`token.usage` **metrics** — so metrics alone are sufficient. Prompts, assistant
responses, tool content and command lines are *only ever* log records, never metric
attributes. Requiring a logs exporter would have pushed operators toward shipping
the one signal that can carry content, to obtain something metrics already provide.

So the content switches are **not** this skill's to judge — prompt logging may be
required for enterprise security monitoring, and switching it off is not Catalyst's
call. What is judged is where that content is *routed*.

| Verdict | Meaning |
|---|---|
| `NOT_APPLICABLE` | Not running under Claude Code |
| `OFF` | `CLAUDE_CODE_ENABLE_TELEMETRY` is not set |
| `ON` | Enabled, with a destination and a metrics exporter. A content switch being on does **not** disqualify this |
| `ON_BUT_NO_DESTINATION` | Enabled, but no OTLP endpoint is set *and* nothing is listening on the local default — data is produced and discarded |
| `ON_BUT_MISCONFIGURED` | Enabled with an endpoint set, but something about the configuration is wrong: no metrics exporter, a protocol the collector does not speak, or a per-signal endpoint missing its `/v1/metrics` path. **Read the named problem before assuming data is arriving** — some cases lose part of it and some lose all of it. A missing signal path in particular means every batch POSTs to `/` and is rejected, which is total loss that looks like a healthy configuration |
| `CONTENT_CAPTURE_ENABLED` | A content switch is on **and** the logs signal resolves to the Catalyst collector **and** a logs exporter is actually enabled — so content is arriving here. **Outranks everything.** All three conditions are required: a switch alone is the enterprise's business, and an endpoint with `OTEL_LOGS_EXPORTER=none` exports nothing |

Two things are recorded as **notes** rather than problems, because neither is a
fault and neither changes the verdict: a content switch on with logs routed
somewhere else, and a missing `/s/<source>` segment. The segment is not a defect
today — `cg-open-itg/catalyst-otel#12` adds that partition and is not deployed, so
flagging it would fail the very endpoint this repo publishes.

The one configuration that *would* break the guarantee is setting the generic
`OTEL_EXPORTER_OTLP_ENDPOINT` to the Catalyst collector: it is the fallback for
every unset signal, so logs would follow it. Per-signal variables are read in
preference to the generic one for both the endpoint and the protocol.

The report names **which settings layer** set each value — managed
(`/etc/claude-code/managed-settings.json`), user (`~/.claude/settings.json`), or
the process environment. That matters because managed settings outrank the user:
telling someone to change a value they cannot change wastes their time, so the
`OFF` remediation says to ask the DevNext team rather than to edit it locally.

The four content switches are `OTEL_LOG_USER_PROMPTS`,
`OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_CONTENT` and
`OTEL_LOG_RAW_API_BODIES` — all ship disabled, and each sends conversation or
code content, so each needs a GRC review.

`OTEL_LOG_TOOL_DETAILS` is recorded but **not reported as a problem**, and it is
easy to assume the opposite: it does *not* supply skill names. `skill.name`,
`agent.name`, `plugin.name` and `marketplace.name` are **unconditional** attributes
on `claude_code.api_request` and on the `cost.usage` / `token.usage` metrics, so
attribution needs no switch at all. What this one adds is serialized tool arguments
and bash command lines — and since those are log records, they cannot reach a
metrics-only collector or dilute what Catalyst measures. Also the enterprise's call.

**This skill does not write the settings.** It is read-only by contract;
`/setup-workspace otel` owns the edit. `preflight.py otel --probe-endpoint` is the
only call that contacts a *collector* — the background pass makes others, and says
so below. It probes **both** endpoints — the Copilot Chat
one and the Claude Code metrics one — and distinguishes "off the corporate network"
from "on VPN but this endpoint will not accept a connection"; the second is worth
reporting to the EDO team rather than retrying.

Probing our own endpoint matters more than it looks. The published fragment targets
the **production** collector, which is not routable from an oz-dev Coder workspace
(TCP 443 opens, TLS resets — network isolation, not an outage). When that happens
every metric is dropped and *every local check still says `ON`*, because the
configuration is correct; only the network is not. One command should surface that.

## Background checks — the quiet pass

```bash
python3 scripts/preflight.py background          # once a session; silent when clean
python3 scripts/preflight.py background --force   # ignore the once-a-session marker
```

Questions 1–5b answer *"can I build a data product here"*. This answers a
different one: **"is something about to fail for a reason I will not recognise"** —
the failures that surface as a cryptic error halfway through a task rather than as
a setup problem at the start.

| Family | Checks | Why it is silent otherwise |
|---|---|---|
| **Usage reporting** | questions 5 and 5b, reusing their probes — no *egress*; one 1s loopback connect, which is what lets it distinguish "no endpoint at all" from "misconfigured" | **the only one that is invisible by design.** There is no UI confirmation of Copilot Chat reporting anywhere, so a machine that has never reported looks identical to one reporting correctly. Everything else here degrades loudly and eventually; this degrades silently and forever |
| Credentials | `keeper-env doctor`, `gh auth status --json hosts` — **these leave the machine**; liveness cannot be established any other way | both expire with no warning; a dead `gh` token surfaces as *skills appear broken* |
| Tool versions | `databricks` against the range in `skills/requirements.txt` | drift either way — below the floor is unsupported, at or above the ceiling means the tool moved on or our own docs are stale |
| Identity | `git user.email`, and the `gh` login **reused from the call above** rather than a second `gh api user` | unset or disagreeing means telemetry attributes work to the wrong person, or to nobody |

Three rules, all deliberate:

- **Advisory only.** Never changes an exit code, never blocks — the same contract
  as questions 5 and 5b.
- **Silent when clean.** Prints nothing when there is nothing wrong, so a healthy
  session pays no attention cost.
- **Once per session.** A marker in `~/.cache/catalyst/` suppresses repeats for
  eight hours. A check that nags is one people learn to skip.

**The `gh` check reads the active account only, via `--json`.** Plain `gh auth
status` exits 1 if *any* configured account fails — so a stale keyring entry
sitting beside a perfectly healthy login made the pass report "gh is not
authenticated", which is a false alarm in the one check whose whole value is being
silent when clean. `--json hosts` is documented to always exit zero and returns
`state`, `active`, `login` and `tokenSource` as fields, so nothing here parses
another product's prose. A payload it cannot read at all — a `gh` too old for
`--json` — is reported as **nothing**, because an unknown is not a finding.

**One honest limitation.** keeper-env liveness cannot be determined locally: its
config carries a device token and a private key but **no expiry**, so `doctor`
reports "Session credentials: present" while fetches fail. This check reports
structure and says so — it cannot promise the session works. Only an actual fetch
can, and that is a network call this pass deliberately avoids.

Run it at the start of a session, or when the user's first message suggests they
are getting set up. Do not run it repeatedly — the marker exists for a reason.

## Procedure

### Step 1 — Run the check

The script is `scripts/preflight.py`, resolved under your skill home — i.e.
`skills/dplc-preflight/scripts/preflight.py` relative to the repository root.

**Locate it before running it.** Your working directory is not necessarily the
repository root, so a bare relative path may not resolve. Find the file first, then
run it with the path that worked:

```bash
# Resolve the script wherever the repo is checked out, then run it.
PF=$(ls skills/dplc-preflight/scripts/preflight.py 2>/dev/null \
     || git rev-parse --show-toplevel 2>/dev/null | sed 's|$|/skills/dplc-preflight/scripts/preflight.py|' \
     | grep -m1 . )
python3 "$PF" check
```

If that shell form is awkward in your environment, any equivalent is fine — glob
for `**/dplc-preflight/scripts/preflight.py`, or use the absolute path under the
skill home the harness gave you. What matters is that you run **this** script.

This prints a four-part report, writes `.catalyst-env.yml`, and exits with the
top-priority blocker. Report the output to the user as-is; it is written to be
read directly. Do not paraphrase it into a summary — the user needs the specifics.

To list workspaces alone (no live probing, no cache write):

```bash
python3 skills/dplc-preflight/scripts/preflight.py workspaces
```

> **Never reimplement this script, and never inline its logic.**
> `scripts/preflight.py` *is* this skill; the prose above only describes it. If the
> path does not resolve from your working directory, it is a path problem — resolve
> it under the skill home (`skills/dplc-preflight/scripts/`) or use an absolute
> path. **Say the script could not be found and stop.** Do not write your own
> version into a scratch directory and run that: a hand-rolled probe silently drops
> this skill's guarantees — that no secret is ever printed, that a permission
> failure is an answer rather than a crash, and that a failed lookup is never
> reported as an entitlement gap. An improvised replacement that looks right is
> worse than an honest "I could not run the check."

### Step 2 — Route on the exit code

Fix one blocker at a time, in this order. Each is a hand-off, not something to
solve inline:

| Exit | Meaning | Route to |
|:-----|:--------|:---------|
| 0 | Ready to build | Continue to the stage the user wanted |
| 2 | Local toolchain not ready | `/setup-workspace` |
| 3 | No Databricks connection | `/databricks-config` |
| 4 | Authenticated, but no catalogs visible | **Not self-serve** — see below |
| 5 | No SQL warehouse reachable | `/configure-sql-warehouse` |
| 6 | A lookup failed — access **undetermined** | Read the error, re-run. **Do not** send the user to request access |

Exit 6 deliberately outranks 4 and 5. A transient 5xx, a token expiring mid-run,
or a network blip all leave the catalog list empty without meaning the user lacks
access — and telling someone to file an entitlement request they may already hold
wastes their time and their platform team's. Section 3 of the report prints the
actual error; quote it rather than summarising.

After the routed skill completes, re-run `check` to confirm before continuing.
This is multi-turn: some fixes need the user to act outside the session.

### Step 3 — Confirm the workspace with the user

When more than one profile exists, **do not guess**. Show the list and ask:

> "I found these Databricks workspaces configured on your machine: [list].
> You are currently pointed at [host or 'none selected']. Is that the right one
> for this data product?"

This is the one question this skill should always ask, because being in the wrong
workspace produces confusing failures much later. Once confirmed, note the choice
so downstream skills do not re-ask.

### Step 4 — Hand back

State the verdict, the workspace, and the single next step. Then return control to
whatever the user was trying to do.

## Entitlements are not setup

Exit code 4 means the user authenticated successfully, the catalog lookup
**succeeded**, and Unity Catalog showed them nothing. That is an **access grant
they do not have**, not a misconfiguration, and no amount of local setup fixes it.
Say so plainly and point them at their data platform team. Do not loop them
through setup skills.

Check the exit code before saying any of that. An empty catalog list with
`catalogs_error` set is exit **6**, not 4 — the lookup never completed, so nothing
is known about their entitlements. Both states print differently in section 3
(`LOOKUP FAILED` vs a count) and both are recorded in `.catalyst-env.yml`.

## The PAT trap (DBX-SEC-002)

`docs/install.md` tells new users to set `DATABRICKS_HOST` and `DATABRICKS_TOKEN`,
but `connect-databricks` **refuses** PATs per DBX-SEC-002 and exits 3. A user who
followed the install guide exactly lands in a state the connection skill will not
run in.

When `DATABRICKS_TOKEN` is set without OAuth credentials, the script prints an
explicit warning. Surface it — this is the single most common zero-to-one dead end.
Guidance to give:

- Interactive human work: `databricks auth login --host <workspace-url>`
- Service principal / CI: `DATABRICKS_CLIENT_ID` + `DATABRICKS_CLIENT_SECRET`

This skill reports the collision rather than resolving it; the underlying policy
inconsistency across `install.md`, `.env.example`, and `connect-databricks` is
tracked separately.

## Safety rails

- **Read-only.** This skill probes and reports. It never installs, never writes
  credentials, and never mutates `~/.databrickscfg`. Fixes are delegated to the
  skills that own them.
- **Never print secrets.** The script reports which auth *style* a profile uses,
  never a token or secret value.
- **Never claim ready unless `check` exits 0.**
- **Degrade, do not crash.** A missing dependency is a finding to report. The
  script works on a machine where nothing is installed yet — that is the point.

## Outputs

`.catalyst-env.yml` in the working directory:

```yaml
verdict: READY
exit_code: 0
toolchain:
  python_version: "3.13"
  python_ok: true
  deps_ok: true
workspace:
  host: "https://<workspace>.cloud.databricks.com"
  profile: "DEFAULT"
  resolved_from: "~/.databrickscfg [DEFAULT]"
  identity: "user@capgroup.com"
  reachable: true
access:
  catalog_count: 4
  catalogs:
    - "sandbox"
    - "investments_app_dev"
  warehouses:
    - "shared-serverless"  # RUNNING
next_step: "Ready to build."
```

Downstream skills read this instead of re-asking. `/build-preflight` consumes the
workspace and catalog list when it resolves SAP / DAP / CAP / Sandbox placement.

## Relationship to the other readiness skills

| Skill | Scope | Answers |
|:------|:------|:--------|
| `setup-workspace` | The machine | Python, pip → cgrepo, dependencies, git/gh |
| **`dplc-preflight`** | **The platform** | **Workspace, identity, access, placement** |
| `phase-zero-checklist` | The organisation | Roles, demand tracker, pattern registry |
| `build-preflight` | The build | Mode, catalog target, DPLC artifacts, grants |

`dplc-preflight` runs first and is the only one that can be run knowing nothing.
