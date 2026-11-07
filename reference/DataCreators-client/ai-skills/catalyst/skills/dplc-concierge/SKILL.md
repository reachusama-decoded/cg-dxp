---
name: dplc-concierge
description: >-
  Entry point for the Data Product Lifecycle. Detects user intent and routes to
  the right stage orchestrator or individual skill. For users who are new or
  unsure, it guides them one step at a time and checks their environment is ready
  before handing off. Use when: "help me with a data product", "start a new
  product", "I need to create a data product", "where do I start", "I'm new to
  this", "walk me through building a data product", "help me get started",
  "guide me", "what is a data product", "am I set up", "which workspace should I
  use", "nothing works", "data product lifecycle", "DPLC".
allowed-tools: Read Grep Glob
metadata:
  tier: orchestrator
  lifecycle-phase: cross-cutting
  dependencies:
    - dplc-preflight
    - dplc-design-stage
    - dplc-build-stage
    - dplc-ship-stage
    - dplc-prereq
    - dplc-triage
    - dplc-discovery
    - dplc-design
    - setup-workspace
    - databricks-config
    - data-contract
    - data-profiling
    - marketplace-search
    - source-aligned
    - domain-aligned
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# DPLC Concierge

I help you build a data product. Tell me what you want to do and I will take you
to the right place. If you are not sure where to begin, I will walk you in one
step at a time.

The lifecycle has three stages, each with a group orchestrator:

| Stage | Phases | Orchestrator | When to use |
|:------|:-------|:-------------|:------------|
| **Define** | 0 Prereq, 1 Triage, 2 Discovery, 3 Design | `dplc-design-stage` | Starting a new data product or adding a major feature |
| **Deliver** | 4 Build, 5 Validate, 6 Publish | `dplc-build-stage` | Design is approved, ready to implement |
| **Sustain** | 7 Operate, 8 Evolve | `dplc-ship-stage` | Product is in production, needs monitoring or evolution |

Full lifecycle reference: `rfd/0002/README.md`.

---

## Step 0 — Pick the path

Two modes. **Check for a clear ask first** — the guided path is the fallback, not
the default.

### First: does the message name something actionable?

If it names a task, a capability, a phase, or a skill — even loosely — take the
**Fast path** and route. Work through the Routing Logic and One-Off Skill Routing
tables below before considering the guided path. Examples that are all clear asks:

| The user says | Route to — do **not** ask a guided question |
|:--------------|:--------------------------------------------|
| "set up my environment", "install the prerequisites", "get me ready to run Catalyst" | `setup-workspace` |
| "which workspace am I in", "do I have access", "am I set up", "nothing works" | `dplc-preflight` |
| "is usage reporting on", "is telemetry enabled", "check my otel config" | `dplc-preflight` |
| "turn on usage reporting", "enable telemetry", "set up otel" | `setup-workspace` |
| "start a new data product", "I have a request" | `dplc-design-stage` |
| "I'm ready to build", "deploy", "publish" | `dplc-build-stage` |
| "generate a data contract", "profile this table" | that skill directly |

A request phrased politely, or wrapped in "help me…", or ending in "where do I
start?", is **still a clear ask** if it names what the user wants. "Set up my
environment so I can run Catalyst" is an instruction, not an expression of
confusion — route it.

### Otherwise: Guided path

Use it only when the message names no task, capability, phase, or skill — the user
is genuinely unsure what they want ("I'm new to this", "what is a data product",
"help me get started" with nothing else). Then be directive, use plain language,
and check the environment before handing off.

An empty workspace *hints* the user may be new, but it never overrides someone who
told you what they want. Asking "what are you trying to build?" of a user who just
told you is the single most annoying failure this skill can commit.

---

## Fast path — routing logic

For a user who already knows what they want. Keep it short.

### Step 1 — Detect intent

Read the user's message and $ARGUMENTS. Classify into one of:

| Signal | Route |
|:-------|:------|
| "new data product", "start from scratch", "define", "I have a request" | `dplc-design-stage` |
| "build", "implement", "code", "deploy", "test", "publish" | `dplc-build-stage` |
| "monitor", "operate", "runbook", "incident", "deprecate", "evolve" | `dplc-ship-stage` |
| "am I set up", "which workspace", "do I have access", "nothing works" | `dplc-preflight` |
| "is usage reporting on", "is telemetry on", "check my otel config" | `dplc-preflight` |
| "set up my environment", "install the prerequisites", "get me ready to run Catalyst" | `setup-workspace` |
| "turn on usage reporting", "enable telemetry", "set up otel" | `setup-workspace` |
| Names a specific phase ("triage", "discovery", "design", "prereq") | Route directly to the per-phase orchestrator |
| Names a specific skill ("data-contract", "feasibility-report", etc.) | Invoke that skill directly |
| Names nothing actionable at all | Switch to the Guided path |

Unclear intent means the user is probably new. Do not interrogate them with a
lifecycle-vocabulary question — go to the Guided path instead.

### Step 2 — Check for existing work

Scan for existing artifacts to find where the user left off. Search in this
precedence order, matching `/build-preflight`: `$DPLC_DIR`, then `./.dplc/`, then
`./docs/.dplc/`, then the repository root.

| Found | Suggested start |
|:------|:----------------|
| Nothing | Define, Phase 0 |
| `phase-zero-checklist.md` | Define, Phase 1 Triage |
| `demand-tracker-entry.md` | Define, Phase 2 Discovery |
| `feasibility-report.md` | Define, Phase 3 Design |
| `data-contract.md` | Deliver stage |

This table is shared with `dplc-design-stage` — the two must agree. Tell the user
what was detected and confirm before routing. Do not silently skip phases.

### Step 3 — Hand off

Invoke the selected orchestrator or skill. Pass all user context forward,
including anything `dplc-preflight` established, so nothing is re-asked.

On the fast path, keep it to one question and one handoff. The guided path is the
deliberate exception.

---

## One-off skill routing

Users can bypass the lifecycle entirely. If they ask for a specific document or
capability, route directly:

- "Generate a data contract" -> `data-contract`
- "Profile this table" -> `data-profiling`
- "Search the marketplace" -> `marketplace-search`
- "Build a source-aligned pipeline" -> `source-aligned`
- "Build a domain-aligned product" -> `domain-aligned`
- "Check my environment", "am I ready" -> `dplc-preflight`
- "Is usage reporting on?", "check my telemetry" -> `dplc-preflight`
- "Set up my machine", "install the prerequisites" -> `setup-workspace`
- "Turn on usage reporting", "enable telemetry" -> `setup-workspace`
- "Which workspace am I in", "switch workspace" -> `databricks-config`

Do not force users through the full lifecycle when they know what they need.

---

## Guided path — new or unsure users

Be directive and reduce what the user has to decide. Handle the logistics you can
handle for them. Never assume they know which workspace they are in, whether they
have access, or what a "phase" is.

**One step per turn. G1 is the whole of your first reply.** Do not run the
environment check, produce a readiness table, explain the lifecycle, or route in
the same turn as the opening question. A newcomer's first reply from Catalyst
should be two short things: a welcome and one question. Everything else waits for
their answer.

### G1 — Ask what they want, in plain words, then stop

Ask one plain question and **end the turn**. Do not ask which phase, which stage,
or which orchestrator — working that out is your job, not theirs:

> "What are you trying to build or figure out? A sentence is enough."

Pair it with the orientation offer (G2) if you like — those two together are still
one short turn. Then stop and wait.

Accept any answer. "I have a spreadsheet of holdings and need it in Databricks" is
a perfectly good answer, and it maps to Define.

If the user gave a vague direction *and* said they are unsure ("I want to build
something with my data, not sure where to start"), still ask — invite them to say a
little more about what the data is and who needs it. Do not infer a stage from a
sentence that thin and start routing; that is the assumption this path exists to
avoid.

### G2 — Offer orientation, do not force it

> "Want a short overview of how this works, or should we just start?"

Give it only if they say yes, and keep it to a few sentences. Most people want to
start.

### G3 — Check the environment before you hand off (a later turn, never the first)

This is the step that matters most and the one most often skipped. A new user who
gets routed into Define will author documents for hours and only discover at Phase
4 that they cannot reach Databricks.

Invoke `dplc-preflight`. It answers four things the user usually cannot answer
themselves:

1. Can they run Catalyst at all?
2. Which Databricks workspace are they pointed at, and which others exist?
3. Do they actually have access?
4. Where would their data product go?

Surface its report and its single next step. If it exits non-zero, resolve that
before continuing — `dplc-preflight` owns the routing to `setup-workspace`,
`databricks-config`, or `configure-sql-warehouse`. This is multi-turn: the user may
need to act outside the session and come back.

**When several workspaces exist, confirm which one before routing.** Being in the
wrong workspace fails confusingly and late.

Skip G3 only when `.catalyst-env.yml` already reports `verdict: READY`.

### G4 — Tell them the one next step, and take them there

Name the single next action, say plainly what will happen, then route. Never leave
them to guess what comes next.

### G5 — Go one step at a time

After each handoff, say what is next and that they can pause whenever they want.

### G6 — Invite feedback once

At the end of the guided walk-in only, append:

> "Anything about getting started that was confusing? Hit enter to skip."

If they reply with anything substantive, invoke `catalyst-feedback` with
`$ARGUMENTS = "dplc-concierge reply=<their reply verbatim>"`. If they skip, do
nothing. Ask this on the guided path only — never on the fast path.

---

## Notes

- **Two modes, and the fast path stays fast.** Brevity is correct for someone who
  knows what they want. Hand-holding is correct for someone who does not. The
  failure mode this skill exists to prevent is applying the wrong one.
- On the fast path, do not explain the lifecycle — link `rfd/0002/README.md` for
  depth. On the guided path, offer a short overview only if the user asks.
- **Never assume environment knowledge.** Which workspace, whether access exists,
  and where a product belongs are the things new users most often cannot answer.
  Detect them via `dplc-preflight` instead of asking.
- Experienced users who invoke a phase orchestrator directly (e.g.
  `/dplc-triage`) bypass this concierge entirely. That is expected and correct.
- This skill routes and detects. It does not install, authenticate, or configure
  anything — those belong to `setup-workspace`, `databricks-config`, and
  `connect-databricks`.
