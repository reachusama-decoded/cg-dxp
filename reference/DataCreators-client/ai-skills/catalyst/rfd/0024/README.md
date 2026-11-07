---
authors: RYQF
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/429
labels: harness, agents, skills, model-selection, governance, telemetry, devnext
---

# RFD 0024 Agents + Skills: A Portable DPLC Harness for Claude Code and VS Code

## Problem

Catalyst is a skills-only harness. Every unit of the DPLC is a
`skills/<name>/SKILL.md` describing **what** to do, and nothing in the
repo describes **who** does it, **which model** they run on, or **what
they are allowed to touch**. That was the right shape when the harness
was a library of prompts a human drove one at a time. It is the wrong
shape now that DevNext is standing up containerized agentic development
sandboxes in oz-dev, and developers will build data products by
delegating to agents rather than by invoking skills.

The question our job aids answer today is *"How do I use skills to build
a data product?"* The question developers are about to ask is *"How do I
stand up, guide, and govern an agent that is building a data product?"*
The interesting split is not Claude Code versus VS Code — it is that
agentic development is becoming the operating model, and Catalyst has no
vocabulary for it.

Four concrete symptoms of the missing layer:

1. **Delegation is emulated in prose, next to a runtime that supports it.**
   `skills/dplc-design-stage/SKILL.md` spends ~40 lines teaching the model
   how to *pretend* to delegate: invoke via the `Skill` tool, fall back to
   reading the sub-orchestrator's `SKILL.md` when the runtime hasn't
   registered it, and — critically — "Do **not** follow the
   sub-orchestrator's instructions inline… Inline-execution cascades through
   every leaf in every phase and exhausts the turn budget before reaching
   the last phase." That is a context-isolation problem being solved with
   instructions. Subagents solve it structurally — and the mechanism is
   already wired up: `tests/behavior/runner/claude_agent.py` builds an
   `AgentDefinition(disallowedTools=["Agent", "Task"], maxTurns=ceiling)`
   and hands it to the SDK as `agents={"general-purpose": sub_agent}`. So
   the gap is not that delegation is unavailable. It is that the only agent
   the harness can spawn is one anonymous general-purpose worker with no
   phase identity, no model of its own, and no declared skill scope — which
   is exactly the layer this RFD proposes.
2. **Model selection is unexpressible.** The only model pins in the repo
   are the behaviour harness's -- `tests/behavior/config.py`
   (`runner_model` / `judge_model`) and `tests/behavior/preview.py:59-60`,
   which hard-codes `databricks-claude-sonnet-4-6` and
   `databricks-claude-haiku-4-5` for the synthetic dashboard -- at
   whole-harness scope, and they are previous-generation
   (`claude-sonnet-4-6`). A gate determination on a restricted data
   contract and a markdown lint should not run on the same model, and
   today there is nowhere to say so.
3. **Guardrails exist only for tests, and one of them is weaker than it
   looks.** `tests/behavior/config.py` already implements a turn ceiling, a
   wall-clock timeout, a dollar backstop, and a network-domain allowlist.
   `allowed_tools` is **pre-authorisation, not restriction** — its own comment
   says "anything outside this list still goes through the default permission
   flow", so it suppresses prompts rather than denying tools. Nothing here
   applies to an agent a developer actually runs, and nothing here *denies* a
   tool even under test. So the proposed agent boundary is not a port of an
   existing restriction; it would be the first one.
4. **The VS Code path is stale.** `.vscode/settings.json` pointed
   `chat.agentSkillsLocations` at `skills/concierge`,
   `skills/orchestrators`, `skills/execution`, `skills/document` — the
   nested layout the four-tier refactor removed in PR #31 — and used an
   array where the setting is registered as an object map, so the value
   was inert rather than merely wrong. The **folder-locator** path
   therefore resolved nothing for four months. Scope matters and an
   earlier revision of this line overstated it: plugin-contributed
   skills are read on a separate code path that never consults this
   setting, so anyone following `docs/install.md` was unaffected.
   Repaired in [#428](https://github.com/cg-open-itg/catalyst/pull/428),
   separately from this proposal; it is cited here because nobody
   noticed for four months, which is the real signal — the VS Code
   surface has no agent layer, no tests, and no owner.

## Background

**Where the harness stands.** RFD 0002 defines the nine-phase DPLC in
three stages. RFD 0006 defines the four skill tiers (`orchestrator`,
`workflow`, `capability`, `document`) and the SKILL.md frontmatter
contract, enforced offline by `tests/ci/test_skill_frontmatter_contract.py`
(name matches directory, non-empty description, valid `metadata.tier`,
present `metadata.lifecycle-phase`, non-empty `allowed-tools`).
`plugin.json` ships a flat array of 106 registered skills (`skills/_lib`,
`assets`, `clients`, and `core` are shared libraries, not skills).

**The extension point is already reserved.** `scripts/build_skills_graph.py`
defines `AGENTS_DIR = REPO_ROOT / "agents"` and its docstring says plainly:
"Agents are picked up from `agents/<name>.md` if that directory ever
exists; today it does not, and the graph simply renders zero of them."
Agent *nodes* therefore render for free. Agent *edges* do not: `collect_nodes()`
harvests edges only from `metadata.dependencies` and `metadata.consumes`, so
the `metadata.skills` and `delegates-to` relations proposed below need new
harvesting code — a dozen lines in the same loop, but not zero.

**The guardrail prototype already exists, at two different scopes.**
`tests/behavior/config.py` pins `allowed_tools = ("Bash", "Read", "Glob",
"Grep")`, `max_turns_ceiling = 60`, `case_wall_clock_timeout_s = 360`,
`max_budget_usd = 5.00`, and `allowed_network_domains` scoped to
Databricks, Atlassian, and `*.capgroup.com`. Its comments record why each
bound exists ("we observed a 47-min, 34K-token failure mode"). Separately,
`claude_agent.py` already applies *per-agent* bounds — `maxTurns` and a
recursive-`Agent` ban — to the sub-agent it defines. So both scopes exist in
code today. Neither is declarative, and neither is reachable by a developer
running the harness outside the test suite.

**The runtime already models most of the proposed contract.** Claude Code
subagent files take `name`, `description`, `tools`, `disallowedTools`,
`model` (a family alias, a full model ID, or `inherit`), `effort`, `maxTurns`,
`skills`, `memory`, `hooks`,
`permissionMode`, `isolation`, and `mcpServers`. VS Code `.agent.md` files
take `name`, `description`, `tools`, `agents`, `model` (display names),
`user-invocable`, `handoffs`, and `mcp-servers` — and resolve from
`.github/agents` **or** `.claude/agents`. Two consequences: the canonical
layer proposed below is close to a superset of a schema one runtime already
parses, rather than a new vocabulary; and because VS Code reads
`.claude/agents` too, what has to be generated per runtime is the
frontmatter dialect, not a second directory tree.

**Model families, not versions.** The runtime exposes families through aliases
— `opus`, `sonnet`, `haiku` — and resolves each to the latest model in that
family at spawn time. This RFD names families only; it pins no versions and no
prices, both of which move faster than the document. The families differ in
capability ceiling and in latency, and those are separate axes from depth:
reasoning effort (`low`, `medium`, `high`, `xhigh`, `max`) controls how much
work an agent does within a
family's ceiling, and on the Opus family that lever moves quality more than a
family swap does.

**Distribution.** DevNext's containerized sandbox pattern is the delivery
vehicle in oz-dev. Anything we ship there installs under the corporate
registry block: pip via `cgrepo-aws.capgroup.com/repository/cgpypi/simple/`,
npm via `.../cgnpm/`, base images from `cgregistry-aws.capgroup.com`.

## Proposal

Adopt a three-layer harness and make the middle layer real.

| Layer | Artifact | Answers | Portable? |
|:------|:---------|:--------|:----------|
| Capability | `skills/<name>/SKILL.md` | What gets done | Yes — unchanged, runtime-agnostic |
| Responsibility | `agents/<name>.md` | Who owns it, with what model and boundaries | Yes — Catalyst's own contract |
| Execution | `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md` | How this runtime spawns it | No — generated, never hand-edited |

**Skills stay exactly as they are.** No `model:`, no `agent:`, no
`claude-agent:` key ever enters SKILL.md. A skill that names its executor
is no longer a portable capability, and RFD 0006's contract stays intact.
Model selection lives in the agent layer — which is precisely why the
agent layer has to exist.

Read that precisely: the objection is to a skill **naming its own executor**, in
its own frontmatter. It is an argument about where a *declaration* lives, not
about how a model gets chosen, and it does not extend to an external map keyed by
skill name — that map leaves SKILL.md untouched and portable. Which layer should
own the choice is argued in §2 and remains open.

### 1. `agents/<name>.md` — the specialist contract

Markdown with frontmatter, one file per agent, mirroring the SKILL.md
contract closely enough that reviewers do not need a second mental model:

```yaml
---
name: dplc-design-agent
description: >-
  Owns Phase 3 Design — data contract, data model, transformation spec,
  and architecture. Delegating orchestrator; does not author leaf artifacts.
model: opus
effort: xhigh
# Read Grep Glob Bash. `Bash` is not decoration: `data-modeling` declares
# `allowed-tools: Read Grep Bash` (skills/data-modeling/SKILL.md:4), so an agent
# scoped to this skill without it would be rejected by the tool-satisfiability
# check proposed in open question 6 -- by its own canonical example.
tools: Read Grep Glob Bash
metadata:
  role: orchestrator          # orchestrator | specialist
  lifecycle-phase: phase-3-design
  skills:                     # skills this agent may invoke
    - data-contract
    - data-modeling
    - transformation-spec
  delegates-to: []            # other agents it may spawn
  guardrails:
    max-turns: 40
    max-budget-usd: 5.00
    network: catalyst-default # named set from framework/boundaries.yaml
  approval-gates:
    - id: gate-3
      prompt: Design & contract approved?
      blocking: true
  memory:
    read: .catalyst/decisions.md
    write: .catalyst/decisions.md
---
```

Two deliberate choices in that block. **`metadata.role`, not
`metadata.tier`** — RFD 0006's `tier` vocabulary is `orchestrator | workflow |
capability | document`, enforced in two places
(`tests/ci/test_skill_frontmatter_contract.py` and, separately,
`VALID_TIERS` in `scripts/build_skills_graph.py`). Reusing the same key with a
different enum would either fail those checks or silently degrade an agent to
`unspecified` in the graph. Agents get their own key. **`lifecycle-phase` uses
the full `phase-N-name` form** the graph builder's `PHASE_TO_STAGE` requires; a
bare `3-design` raises `ValueError` on the next `build_skills_graph.py` run.

The top-level keys — `name`, `description`, `model`, `effort`, `tools` — are
Claude Code subagent fields verbatim, so they pass through the adapter
untranslated. Everything under `metadata` is Catalyst's own: it is what the
contract test validates and what the graph reads.

`metadata.skills` replaces the delegation prose in stage orchestrators:
the sub-agent gets its own context window, so "do not inline-execute"
stops being an instruction the model can ignore and starts being a
property of the runtime.

### 2. Model selection policy

`model:` takes a family alias — `opus`, `sonnet`, `haiku`, `inherit` — and
never a pinned version. On the Anthropic API the runtime resolves each alias to
the *latest* model in that family when it spawns the subagent: `opus` is
documented as "the latest Opus model," `sonnet` as "the latest Sonnet model."
An agent file therefore needs no maintenance across model releases, and Catalyst
needs no alias→ID mapping file of its own. A `framework/models.yaml` **translation
table** — one that maps `opus` to a pinned model ID — would re-create the
per-release edit chore this RFD rejects when it argues against `model:` in
SKILL.md, just centralized into one file instead of spread across 106. We should
not build that. Where "latest" gets decided is a deployment concern, discussed
next.

**That argument is narrower than it first reads, and the distinction matters.**
What it rejects is *version pinning*, wherever it lives. It says nothing about a
file that maps a **subject to a family alias** — `skill-name → sonnet`, say —
because such a file needs no edit when a new Opus ships. So "no config file"
is not a conclusion this RFD has earned, and it should not be read as one: the
per-release chore is an argument about pinning, not about centralization.

What this RFD does claim is separate and narrower: the model belongs to the
**agent**, because an agent is a *responsibility* — a scope, a set of tools, a
boundary — and the capability-to-model question is answered by who is accountable
for the work rather than by which task is being performed. A skill runs on
whatever the agent invoking it runs on. Whether that is the right layer, versus
routing per skill, is a genuine open question and not one this section settles.

**Claude Code is the resolution layer, and today it resolves to current
models.** Claude Code is the primary harness and our entry point to Bedrock, so
"what does `opus` mean" is answered by the harness and its environment, not by
anything Catalyst ships. On the deployment in use today the `/model` picker
offers Opus 5 as the default, with Sonnet 5 and Haiku 4.5 as the other
selectable families — the current generation across all three tiers. So the
aliases in `agents/*.md` resolve to the models we would have chosen anyway, and
**no alias→ID translation table, pin, or version list belongs in this repo.**

That sentence is deliberately narrower than an earlier revision's, which read "no
mapping file, pin, or version list belongs in this repo" and contradicted the
paragraph above it eighteen lines earlier — the one conceding that "no config
file" is not a conclusion this RFD has earned. What this RFD rejects is a file
that has to be *edited when a new model ships*: an `opus → claude-opus-4-8`
table. A file mapping a **subject to a family alias** (`skill-name → sonnet`) has
no such property and is not rejected here. Whether one belongs is
[RFD 0026](https://github.com/cg-open-itg/catalyst/pull/433)'s question, and this
section does not pre-empt it.

Two properties of that arrangement are worth recording, because they are the
reason the agent layer can stay this thin. Resolution is **late-bound**: the
agent file names a family, the harness picks the version at spawn time, so a new
Opus release is picked up by redeploying or reconfiguring the harness rather than
by editing 20 agent files. And it is **someone else's job**: model availability,
enablement, and provider defaults belong to whoever operates the harness and the
AWS account. Catalyst's contract is the family choice and the reasoning behind
it, which is what §2's table encodes.

**Resolution precedence, in full**, because "what model will this agent actually
run on" has four possible answers and only one of them is the agent file:

1. `CLAUDE_CODE_SUBAGENT_MODEL` — the environment variable
2. the `model` parameter passed at invocation time
3. the `model` field in the subagent's frontmatter
4. the main conversation's model, as fallback

**Verified on the deployment in use today: `CLAUDE_CODE_SUBAGENT_MODEL` is not set
in the DevNext managed policy (`/etc/claude-code/managed-settings.json`) and not
present in the process environment.** So step 1 is currently inert and frontmatter
decides, which is what this layer needs. That is a fact about today's image rather
than a guarantee — which is why it stays a step-1 preflight check. Set in an image
later, it would silently ignore every agent file's declaration and make the model
layer inert without erroring.

**So `model:` should be written explicitly on every agent, including where the
answer is `inherit`.** The argument is determinism, not cost:

- **An omitted field is not a stable default.** It resolves through the chain above,
  so the tier depends on who runs the agent, which session they are in, and which
  Claude Code version they have. The default has **already changed once** — older
  documentation said an unspecified `model` used the configured subagent default
  (sonnet), where current behaviour is that subagents inherit the main session's
  model. A suite shipped to a team should not vary with any of that.
- **`model:` is a capability contract, not a budget line.** It states the tier the
  agent was validated against. `opus` on a planner or reviewer encodes "this needs
  reasoning depth"; `haiku` on a grep-and-summarise worker encodes "this does not".
- **Explicit `inherit` documents intent.** It and a blank field behave identically
  today, but only one tells the next maintainer the choice was deliberate — and only
  one survives the default changing again.
- **Reproducibility.** Someone running a Sonnet session, or with a different
  `CLAUDE_CODE_SUBAGENT_MODEL`, does not silently degrade a reviewer agent — or
  silently upgrade a cheap one and mask a regression.
- **Debuggability.** When an agent underperforms, "wrong model" is ruled out by
  reading one line instead of tracing a four-step resolution chain across an image,
  an invocation and a session.
- **Portability.** Handed to a team or a domain that does care about spend, the
  routing is already right rather than retrofitted.

One caveat that belongs with the caveat above: there is an **open bug** where
`CLAUDE_CODE_SUBAGENT_MODEL=inherit` causes dispatched subagents to ignore the
per-call `model` parameter and run the main session's model regardless. So
"unset **or** `inherit`" is not quite interchangeable — a harness with a hard model
requirement should assume unset and say so in its README, not rely on `inherit`
being a no-op.

And the boundary this RFD already draws elsewhere is worth restating here, because
it is the most common confusion: **skills take no `model` field at all.** Model
selection is an agent-frontmatter concept; a skill runs in whatever context loads
it. That is why §1 keeps `model:` out of SKILL.md rather than adding it there.

Reference: [Claude Code subagents — model selection](https://docs.claude.com/en/docs/claude-code/sub-agents).

**A mixed harness is something we earn into, not something we default to.**
This is worth stating plainly, because "one model per agent class" reads like an
obvious efficiency and it is the wrong starting posture. The method we adopt
from Anthropic's Claude Code guidance is: pick one conservative baseline per
role, tune with effort, and move routine stretches down-tier only as you learn
your own patterns — treating a tier change as a general preference by work type,
not a task-by-task decision. Starting instead from a pre-committed spread of
three tiers inverts that. It fixes the routing before we have any evidence about
which legs of the DPLC are actually mechanical, and it makes failures ambiguous:
when a Haiku validator returns a bad determination on day one, we cannot tell
whether the model was under-powered or the harness handed it a bad prompt, an
unregistered skill, or a missing artifact. Distinguishing "didn't know enough"
from "didn't try hard enough" is the first diagnostic question, and a premature
down-tier destroys the ability to ask it.

Where we diverge from the general guidance is the baseline *tier*. That guidance
treats Sonnet as the generalist default and reserves larger models for genuinely
difficult problems — and the DPLC's orchestration and judgment work *is* that
reserved case, not the general one. A stage orchestrator deciding which phase to
route to, a gate determination on a restricted data contract, a design or
security review: these are ambiguity-heavy, multi-step, and expensive to get
wrong. So we start them on Opus rather than discovering by regression that Sonnet
was the wrong call. Sonnet is the baseline only for work that is already
well-specified when the agent receives it.

So the policy is: **start at the tier the reasoning demands, biased upward, then
descend on evidence.**

| Agent class | Initial alias | Descend to | Evidence that licenses the move |
|:------------|:--------------|:-----------|:--------------------------------|
| Stage and phase orchestrators (routing, sequencing, delegation) | `opus` | — | Stays put. Ambiguity-heavy and multi-step; a wrong route wastes a whole phase |
| Design, architecture, security, contract, gate determination | `opus` | — | Stays put. Wrong answers are expensive and land in approved artifacts |
| Document authoring, build/validate specialists | `sonnet` | — | Work is well-specified by the time the agent sees it. Descend only per-agent, with a behavior case demonstrating parity |
| Checklist validators, formatters, log/entity extractors | `sonnet` | `haiku` | Behavior-suite parity across the agent's cases, plus a measured wall-clock or throughput win |
| Developer-driven exploratory helpers | `inherit` | — | Intentionally scales with the session |

Three things to note about that table. **Orchestrators are on Opus, not Sonnet**
— routing under ambiguity is the reasoning-heaviest thing the harness does, and
it is also where a bad decision is most expensive, because it commits every leaf
beneath it. **No explicitly tiered DPLC role starts on Haiku**: even
mechanical-looking work begins on Sonnet and earns its way down, which is the
reverse of how these tables are usually written. The claim is scoped to the tiered
roles on purpose — an `inherit` helper launched from a Haiku session does start on
Haiku, and that is the trade accepted below rather than an exception to a blanket
rule. And `inherit` is a deliberate choice for a small class, not a default —
whatever we leave undeclared gets `inherit` from the runtime anyway, which is
precisely the drift an explicit alias prevents.

**Why mix at all, once cost is set aside.** Cost is the weakest argument for
this and should not be the one we lead with. Four stronger ones:

1. **Wall-clock time.** In a fan-out shape — a coordinator dispatching repo
   searches, test runs, log summaries — those legs sit on the critical path.
   Haiku is materially faster than Opus, so moving mechanical fan-out down-tier
   finishes the whole phase sooner even if every call were free. Speed is a
   feature independent of price, and for a nine-phase lifecycle it compounds.
2. **Parallel throughput and context isolation.** The useful shape is many
   cheap fast workers doing wide exploration plus one strong model reading their
   summaries and deciding. Each named subagent gets its own conversation, context
   window, and prompt cache, so eight explorers can run at once without flooding
   the parent's context — and without the cache invalidation a mid-session model
   switch would cause. That is an architecture property, not an economy.
3. **Quality stability.** `model:` defaults to `inherit`, so an agent that
   declares no alias silently tracks whatever the session happens to be on. Fine
   for a general helper; wrong for a security reviewer or a gate determination,
   whose judgment must not degrade because someone opened the session in Haiku.
   Declaring an alias cuts both ways: a test-runner set to `haiku` does not get
   slower and more elaborate because someone opened in Opus. An explicit family
   buys deterministic behavior per role.
4. **Task fit.** The counterintuitive one. On simple, precisely-specified work,
   a larger model is not measurably better and can be worse — adding abstraction,
   second-guessing a clean answer, reasoning itself past a straightforward
   lookup. The guardrails in §4 exist partly because over-elaboration burns turn
   budget. Matching tier to actual task difficulty is a reliability argument
   before it is a cost one.

**Model and effort are separate dials, and the escalation signals differ.**
Model sets the capability ceiling — a frozen set of weights. Effort controls how
much work the agent does within that ceiling: files read, tools called,
verification performed, how far it goes before checking in. The diagnostic
follows from the split:

| Symptom | Lever |
|:--------|:------|
| Agent had full context, clearly tried, still got it wrong | Raise the **model** |
| Agent skipped a file, didn't run the validator, bailed mid-phase | Raise the **effort** |
| Output is right but the phase takes too long | Lower the **model** on the mechanical legs |
| Can't tell which | Fix the context first — prompt, registered skills, available artifacts |

That last row is the common case early on, and it is why the conservative start
matters: a harness that begins on one tier makes the other three rows legible.

Anthropic ships this pattern in Claude Code itself. The `opusplan` alias "uses
`opus` during plan mode, then switches to `sonnet` for execution" — a strong
model doing the judgment-heavy planning and a cheaper one doing the mechanical
execution, inside a single session. Our design layer proposes the same division
across a phase boundary rather than a mode boundary, which is a reason to
believe the shape is sound, not a novel bet.

Two corollaries. First, `tests/behavior/config.py` should take aliases too —
`runner_model` / `judge_model` currently hard-code `claude-sonnet-4-6`, a
previous-generation pin that has to be hand-edited to stay current.
`ClaudeAgentOptions` accepts an alias, so the fix is to pass `sonnet` and let
the runtime resolve it, which also makes the behavior suite the instrument that
licenses every down-tier move in the table above. Second, reasoning effort is
declared alongside the model
(`effort: xhigh` on design agents, `low` on extractors) — on the Opus family
that lever moves quality more than a family swap does, which is another reason
to reach for effort before reaching for a tier change.

### 3. Generated runtime adapters

`scripts/build_agent_adapters.py` reads `agents/*.md` and emits
`.claude/agents/<name>.md` and `.github/agents/<name>.agent.md`.
Deterministic output with a `--check` mode — the same contract
`build_skills_graph.py` already uses, and subject to the same enforcement
caveat recorded in §7. Adapters are generated, never
hand-maintained; the failure mode we are avoiding is two divergent copies
of the harness.

The two adapters are not equal work. Because the canonical top-level keys are
Claude Code subagent fields, the Claude Code adapter is close to a passthrough:
strip `metadata`, keep the rest. The substantive translation is the Copilot
dialect — model alias to display name (`opus` → `Claude Opus`), `tools` string
to array, `metadata.delegates-to` to the `agents:` list, and
`metadata.approval-gates` to whatever VS Code's `handoffs` can express. Note
that VS Code resolves workspace agents from `.claude/agents` as well as
`.github/agents`, so emitting a second tree is a choice about frontmatter
dialect, not a requirement of the file layout.

**Open question, and the largest hole in this proposal: `metadata` carries the
controls, and the primary adapter strips it.** A Copilot review of this RFD arrived
at the same gap from five directions, which is a fair sign it is structural rather
than editorial:

| Declared | Named as | What survives "strip `metadata`, keep the rest" |
|---|---|---|
| `metadata.skills` | skill scope (§1) | nothing |
| `metadata.delegates-to` | agent scope, which step 3 depends on | nothing on Claude Code; mapped to `agents:` only for Copilot |
| `guardrails.max-turns` | the per-agent turn cap in §4 | nothing — the native field is `maxTurns` and no translation is specified |
| `metadata.memory` | a write capability | nothing, and the sample declares `memory.write` while scoping tools to `Read Grep Glob`, so the agent could not write even if it survived |

So as written, §§1 and 4 describe controls that the generated primary adapter
discards. Three ways out, and this RFD does not pick one:

1. **Promote them to native fields** where an equivalent exists (`guardrails.max-turns`
   → `maxTurns`, `metadata.skills` → `skills`), and define the mapping for the rest.
2. **Declare them metadata-only** — read by the contract test and the graph, never by
   a runtime — and delete the language implying they constrain execution.
3. **Make the harness the enforcement point**, so the declarations are read at launch
   rather than translated into a file the runtime interprets.

(1) is the least dishonest for the fields with native equivalents and says nothing
about the rest. (2) is the smallest change and costs the RFD its guardrails claim.
(3) is the most capable and the most work, and it is also the shape RFD 0006's target
runtime would need anyway.

Two smaller items from the same review, recorded rather than resolved: emitting both
`.claude/agents` and `.github/agents` while VS Code discovers from both means a
workspace can find two copies of each agent, so one tree or a stated precedence is
needed; and the canonical sample carries `effort` and a top-level `memory` block that
the VS Code field list does not include, which needs a per-runtime allowlist rather
than an implicit passthrough.

**Four further gaps from the same review, none of which this RFD resolves.** Recorded
here so a reviewer can weigh them rather than discover them during implementation:

- **"Graph support is free" is not true as written.** `collect_nodes()` does discover
  `agents/*.md`, but it derives gaps unconditionally from `metadata.tier` --
  `gaps = sorted(f for f in ("tier", "lifecycle-phase") if not meta.get(f))` -- and
  emits `tier`. The proposed contract uses `metadata.role` instead, so every new agent
  would render as `tier: unspecified` with a missing-tier warning rather than as a
  complete node. Agent-specific node handling is a prerequisite, not a follow-on. The
  published page also hard-codes the `composes` / `consumes` filters and their
  rendering, so new `skills` or `delegates-to` edge types would be generated and then
  hidden.
- **Concurrent writes to `.catalyst/decisions.md` are unspecified.** The design leans
  on parallel fan-out and also lets any agent append to one shared file.
  *Append-only* is not *atomic or ordered*: interleaved or lost decisions are possible
  before the next session reads it. Needs a serialised writer, or per-agent journals
  with a merge step.
- **The guardrail schema is ambiguous about scope.** §4 says an agent references a
  named guardrail set or inherits `catalyst-default`, the example declares inline
  `max-budget-usd` and `network`, and the table below says neither is declarable per
  agent and both only work at session or sandbox scope. A reader can reasonably
  conclude a per-agent declaration is enforced when it cannot be. One schema, one
  enforcement scope, stated once.

None of these are fatal and all are cheaper to settle in discussion than after the
adapters exist, which is the point of leaving them here.

**The two surfaces also differ in confidence, and the RFD should say so.**
Claude Code is the happy path: a subagent spawned by the main loop is expected to
honor the `model` declared in its frontmatter, which is what makes §2's routing
real. On the Copilot surface, `model` support in `.agent.md` is newer and version-
dependent — an older Copilot may ignore it, in which case that surface still gets
context isolation, tool scoping, and delegation structure, but tier routing
degrades to whatever the session is on. That is an acceptable asymmetry for now
(Copilot users lose an optimization, not correctness), but it means the model
layer should be justified on the Claude Code path and treated as
best-effort on Copilot until the version floor is confirmed. See §7 in the open
questions.

### 4. Guardrails as a declared, enforced contract

Promote `tests/behavior/config.py`'s bounds to a named-set file
(`framework/boundaries.yaml`) that both the behavior harness and runtime
hooks consume. Agents reference a set by name; an agent that declares no
`guardrails` block inherits `catalyst-default`.

The bounds do not all enforce at the same layer, and the frontmatter should not
pretend otherwise:

| Bound | Enforced by | Declarable per agent? |
|:------|:------------|:----------------------|
| `max-turns` | `maxTurns` in the adapter's frontmatter — **translation not specified yet; see below** | Native field, not yet wired |
| tool allowlist | `tools` / `disallowedTools` | Yes — native subagent field |
| reasoning depth | `effort` | Yes — native subagent field |
| `max-budget-usd` | `ClaudeAgentOptions(max_budget_usd=…)` at session scope | No — harness only |
| network allowlist | PreToolUse hook, plus the devcontainer at sandbox level | No — harness/sandbox only |

So `guardrails.max-turns` *targets* a real runtime field, while `max-budget-usd`
and `network` are declarations the *harness* reads when it launches an agent —
not something a subagent file can carry. That split is worth naming now, because
a reviewer who reads the frontmatter block above will reasonably assume all five
are enforced the same way.

**What this row does not settle.** An earlier revision said `guardrails.max-turns`
"round-trips into a real runtime field." §3's gap table says the opposite —
*"nothing — the native field is `maxTurns` and no translation is specified"* — and
§3 is the correct side: `guardrails` is nested under `metadata:` in the canonical
sample above, so a generator that strips `metadata` and keeps the rest discards it
along with `skills` and `delegates-to`. The field is declarable in principle and
unwired in fact. Since §3 comes first, a reader reaching this table has already
been told there is no translation, and two tables asserting opposite things about
one field is worse than either answer on its own. Resolving it is §3's open
choice — its option 1, "promote them to native fields where an equivalent exists
(`guardrails.max-turns` → `maxTurns`) and define the mapping for the rest," is the
one that makes this row true. Until that is picked, read the row as an intent.

### 5. Session memory

`.catalyst/decisions.md` in the product workspace is an append-only log of
decisions, assumptions, and open questions, written by whichever agent made
the call and read at the start of every session. Agents declare their
memory contract in frontmatter (above). This is the mechanism behind
"context must flow forward between phases" — a line that appears in
orchestrator skills today with no implementation.

### 6. Human review as a first-class object

Phase gates are currently prose inside orchestrator SKILL.md files, which
means a sufficiently confident agent can narrate past them. Declaring them
as `approval-gates` with `blocking: true` gives the harness — and the
behavior tests — something to assert on: the agent must stop, present the
determination, and receive explicit confirmation before advancing.

### 7. Checks and packaging

**First, the enforcement caveat, because it changes what every check below is
worth.** This RFD talks about "CI" the way the repo talks about it, but there is
no CI. `.github/workflows/` does not exist; the only hook, `.githooks/pre-commit`,
syncs `plugin.json` into `marketplace.json` and does not run tests.
`CONTRIBUTING.md` states the situation directly — "This run is the gate. No CI
workflow runs these checks for you when you open a PR… repo-owned GitHub Actions
are not enabled in this org" — and points at **RFD 0023 §5**, which proposes
wiring the offline suite into a workflow and records that doing so is *blocked on
repository Actions being enabled at the org level*.

One caveat on that pointer, because this section's whole hedge rests on it:
**RFD 0023 is not merged.** `rfd/0023/` does not exist on `main`, `rfd/README.md`
has no row for it, and [#404](https://github.com/cg-open-itg/catalyst/pull/404) is
`CONFLICTING` and untouched since 2026-08-10. `CONTRIBUTING.md` on `main` cites it
the same way, so this is a pre-existing repo-wide dangling reference rather than
something this RFD introduces — but it means every "until RFD 0023 §5 lands" below
is contingent on a stale PR, and §5 is itself blocked on an org-level setting
neither RFD controls. Unblocking #404 would help more than citing it.

So every check in this section is enforced by a contributor running `pytest`
before opening a PR, not by a gate that can refuse a merge. That is the same
footing RFD 0006's frontmatter contract already stands on, so the agent layer is
no weaker than the skill layer — but it is weaker than "CI validates it" implies,
and the difference matters wherever this RFD leans on a check to make a runtime
error impossible. **This RFD does not propose fixing that**; it depends on RFD
0023 §5 landing, and until it does, the checks below are conventions with test
coverage rather than enforced invariants.

- `tests/ci/test_agent_frontmatter_contract.py`, mirroring the skill
  contract test: name matches filename, non-empty description, valid
  `metadata.role`, `metadata.lifecycle-phase` present and a key of
  `PHASE_TO_STAGE`, `model` in the alias set, `effort` in the `low`/`medium`/`high`/`xhigh`/`max`
  set, every `metadata.skills` entry resolves to a real skill directory,
  every `delegates-to` entry resolves to a real agent, no `model:` key
  present in any SKILL.md.
- `scripts/build_skills_graph.py --check` picks up agent nodes for free;
  rendering `metadata.skills` / `delegates-to` as edges needs a small
  addition to `collect_nodes()`'s edge loop, which today reads only
  `dependencies` and `consumes`.
- Two distributions from one tree: a lightweight Copilot plugin
  (`skills/` + `.github/agents/`) and the DevNext devcontainer (full
  harness + hooks + MCP), the latter built `FROM cgregistry-aws.capgroup.com/…`
  with pip pinned to `https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`
  and npm to `https://cgrepo-aws.capgroup.com/repository/cgnpm/`.

### 8. Sequencing

| Step | Scope | Gate |
|:-----|:------|:-----|
| 1 | `agents/` + contract test + adapter generator; three agents only (`dplc-concierge`, `dplc-design-stage`, `dplc-design`) at their §2 tiers; confirm `CLAUDE_CODE_SUBAGENT_MODEL` is unset | Both runtimes launch the Design stage end to end, and a spawned agent demonstrably runs on its declared family |
| 2 | `framework/boundaries.yaml`; behavior harness takes aliases instead of pinned model IDs | Behavior suite green with no hard-coded model versions anywhere; the suite can now adjudicate a down-tier |
| 3 | Remaining stage and phase orchestrators; delegation prose deleted from SKILL.md bodies; behavior harness retargeted to real delegation | Turn-budget exhaustion no longer reproduces, and the behavior suite is green scoring `Agent`/`Task` calls rather than `Read(SKILL.md)` |
| 4 | Memory + approval-gate enforcement; devcontainer packaging for oz-dev | A DPLC run survives a session boundary with decisions intact |

Step 3 carries the one migration cost worth stating up front.
`tests/behavior/runner/sub_skill_detection.py` is the harness's single source
of truth for "what counts as invoking a sub-skill," and it deliberately counts
two forms: an explicit `Skill` call, and `Read(skills/<name>/SKILL.md)`. Its
docstring already anticipates the change — "When skills land in the registry,
drop case (2)" — but real subagent delegation emits neither form; it emits
`Agent` / `Task` calls. So `detect_sub_skill` gains a third case, and
`triage.py`'s `orchestrator-delegation` failure class needs to recognize it.
Roughly 30 lines across two files, but they gate every behavior case that
asserts on delegation, so the work belongs in step 3 rather than being
discovered during it.

## Alternatives

**Stay skills-only and keep encoding agent behavior in prose.** This is
the status quo and it is already failing: `dplc-design-stage` needs ~40
lines of anti-inlining instructions, and the behavior runner counts
`Read(skills/<name>/SKILL.md)` as a delegation because Catalyst skills
aren't registered in Claude Code's skill registry — a workaround its own
docstring flags as temporary. Prose cannot isolate a context window, cap a
turn budget, or pick a model. Rejected.

**Use one tier everywhere and tune only effort.** The strongest counter-argument
to §2, and it deserves a real answer rather than a cost objection: one tier
removes the whole routing question, makes failures unambiguous, and — per the
escalation table — effort is the lever we should reach for first anyway. Largely
accepted, in fact, and §2 concedes most of it: orchestration and judgment work
starts on Opus, nothing starts on Haiku, and effort is the first lever. Rejected
as the *end state* on three grounds that survive setting cost aside. It forfeits
the wall-clock and parallel-throughput wins that motivate fan-out at all, since a
uniform-Opus explorer pool is the slow configuration. It leaves `inherit` as the
effective default for anything we forget to declare, which is the drift the layer
exists to prevent. And it ignores task fit: on precisely-specified mechanical
work, the larger model is not better and sometimes over-elaborates. The honest
position is that near-uniform Opus is the right *starting* configuration and the
wrong *steady state*, which is what "start at the tier the reasoning demands,
then descend on evidence" encodes.

**Put `model:` in SKILL.md.** Simplest possible change and it directly
satisfies "model selection in frontmatter." Rejected: it couples a
portable capability to a vendor's model namespace, breaks the Copilot
surface (different model strings), and means every model release edits
all 106 skill files. The right home is the layer that already varies by
runtime.

**Hand-maintain `.claude/agents/` and `.github/agents/` directly, with no
canonical `agents/`.** Fewer moving parts, no generator. Rejected: two
copies of the same specialist inevitably diverge, and neither is the one
`build_skills_graph.py` reads. The generator is ~150 lines and removes
the whole class of drift.

**Make `framework/specialists.yaml` the source of truth instead of
markdown agent files.** YAML is easier to validate. Rejected: agents need
a prose body (that *is* the system prompt), so YAML would be a third
representation sitting between the contract and the runtime file, and
markdown-with-frontmatter is the format both runtimes already consume.
Validation is not hard enough to justify it.

**Fork the harness per runtime — a Claude Code repo and a Copilot repo.**
Each could then use its native format with no translation. Rejected on
RFD 0003 grounds and on substance: the DPLC content is 95% of the value
and 100% shared, and forking guarantees the two tools teach different
lifecycles within a quarter.

**Wait for DevNext to stabilize before changing the harness.** Tempting,
and it avoids building against a moving target. Rejected: the layering
proposed here is independent of DevNext specifics — only step 4
(devcontainer packaging) touches it, and steps 1–3 pay for themselves in
the Claude Code path we already ship. Waiting means teaching a skills-only
mental model to the first cohort of agentic developers and re-teaching it
later.

## Impact

**Skill authors** are largely unaffected: SKILL.md keeps its RFD 0006
contract and no existing skill needs a frontmatter change. What changes is
that orchestrator skills get *shorter* — the delegation and
anti-inlining prose moves into agent structure. Authors adding a new
orchestrator now write two files instead of one.

**Reviewers** gain a diffable statement of which model, tools, budget, and
approval gates apply to each piece of the lifecycle. Today that is
distributed across prose and unstated defaults.

**Users of the VS Code path** get a working surface for the first time
since the skills directory was flattened, plus context isolation, tool scoping,
and delegation structure — with per-agent model selection dependent on their
Copilot version (§7). **Users of the Claude Code path** — the surface we are
designing for — get all of that plus per-agent model selection, resolved by the
harness to whatever the current model in each family is.

**The offline check suite** gains one contract test, one `--check` invocation,
and a small edge-harvesting addition to the graph builder; all offline, no LLM
calls. `scripts/build_skills_graph.py` output changes the first time `agents/` is
populated, so the graph must be regenerated in the same PR — the existing rule
for new-skill PRs. Because `--check` is a byte comparison and the builder raises
on an unrecognized `lifecycle-phase`, the first agent file has to use a phase
value already in `PHASE_TO_STAGE` or the suite fails for whoever next runs it —
which, per §7, is a contributor rather than a merge gate.

**The behavior harness** carries the one non-additive change: its
delegation-detection rules currently score `Read(skills/<name>/SKILL.md)`, and
real subagents don't produce that call. See the note under Sequencing.

**Cost** is explicitly not the case for this change, and the RFD should not be
evaluated on it. It moves in both directions and should be measured, not
assumed: validation and extraction may descend to Haiku, while design work
rises to Opus at high effort — plausibly a net increase. The wins being claimed
are wall-clock time, parallel throughput, deterministic per-role quality, and
task fit. The per-case dollar backstop already in the behavior harness is the
instrument for watching the cost side so it does not surprise anyone.

**Migration** is additive. Nothing is deleted in step 1; existing skill
invocation paths keep working while agents are introduced stage by stage.
The one destructive edit is removing delegation prose from orchestrator
SKILL.md bodies in step 3, gated on the corresponding agents being live in
both runtimes.

### Open questions for discussion

Eight things this RFD deliberately does not settle. Recommendations are
starting positions, not decisions.

**1. Is `agents/` flat or grouped by stage?** *Recommendation: flat* —
symmetry with `skills/`, and `scripts/build_skills_graph.py` already
expects `agents/<name>.md` at that exact path. Grouping wins only if the
agent count approaches the skill count, which it should not: agents are
per-phase, skills are per-artifact.

**2. Does `plugin.json` declare agents alongside skills?** Today it ships
a flat array of 106 skill names. Either agents get a parallel `"agents"`
array (explicit, another list to keep in sync) or the generated adapter
directories are discovered implicitly by each runtime. *Recommendation:
implicit discovery*, since the adapters are generated and the contract test
verifies they match `agents/` — with the §7 caveat that the test only runs when a
contributor runs it. But this is the manifest, and whoever owns plugin
distribution should call it.

**3. Do approval gates block in an unattended run?** A `blocking: true`
gate is unambiguous in an interactive session. In a DevNext sandbox
running headless there is no human to confirm. Options: (a) unattended
runs halt at the gate and emit a pending-approval artifact; (b) a
distinct non-interactive policy lets non-critical gates auto-advance with
a logged determination; (c) unattended DPLC runs are simply unsupported.
*Recommendation: (a)* — but it makes overnight runs less useful, and that
trade is a product decision, not an engineering one.

**4. Who owns model policy, and what licenses a down-tier?** With aliases
resolving in the runtime there is no alias→ID mapping file to own, so *as this
RFD proposes it* the policy is the set of aliases across `agents/*.md`, reviewed
the way any other frontmatter change is. That is a claim about this proposal, not
about where model policy must live: [RFD 0026](https://github.com/cg-open-itg/catalyst/pull/433)
proposes a central `config/model-routing.yaml`, and if it lands, whoever owns
that file owns this answer. Along with §2, this is one of the two places the two
RFDs have to be reconciled, and neither sentence settles it. Is a tier change a Catalyst-maintainer decision, an
architecture-review decision, or a per-domain override? And since §2 assigns
conservatively and descends on evidence, someone
has to define what counts as evidence — behavior-suite parity alone, or parity
plus a measured wall-clock win? *Recommendation: Catalyst maintainers own the
defaults; domains may override per-agent in their own fork, and the contract test
does not forbid it. A down-tier needs behavior-suite parity on that agent's cases
and a stated reason from the four in §2 — not a cost argument.*

**5. Is `.catalyst/decisions.md` committed to the product repo?** A
decision log is only load-bearing if it survives, which argues for
committing it. But it will contain assumptions and rejected options that
teams may not want in a product repo's history, and it will conflict
constantly on shared branches. *Recommendation: committed*, on the
grounds that an uncommitted memory file is not memory. Worth arguing.

**6. Does an agent's `tools:` list bound the skills it invokes, or the
other way round?** A skill declares `allowed-tools`; an agent declares
`tools`. If an agent with `Read Grep` invokes a skill needing `Bash`, the
options are fail loudly, silently intersect, or let the skill widen the
agent. *Recommendation: fail loudly in the contract test* — it verifies every
skill in `metadata.skills` is satisfiable by the agent's tool list, so a mismatch
is caught before it reaches runtime *for anyone who runs the suite*. Per §7 that
is a contributor, not a merge gate, so this is the weakest of the eight
recommendations until RFD 0023 §5 lands: a check nothing forces is a convention,
and "never reaches runtime" would be overclaiming. Two runtime facts bear on the
answer: Claude Code resolves `disallowedTools` before `tools`, and an omitted
`tools` inherits everything the parent session has. So the permissive outcome is
the *default* unless the contract test forbids it — the choice here is whether to
leave that default in place, not whether to build a restriction from scratch. If
the answer needs to hold without a gate, the fallback is a runtime check: an
agent that discovers mid-run it cannot satisfy a skill's `allowed-tools` should
stop rather than silently skip the step.

**7. Does the Copilot surface honor `model:` at all?** Not a blocker, but it
bounds what we promise. The agent layer's value on VS Code depends on whether a
delegated agent respects the model declared in its own frontmatter. Copilot
documents a `model` field on `.agent.md`, but two behaviors we would be relying
on are undocumented: whether a subagent spawned through a parent's `agents:`
list uses its own `model` or inherits the session's, and whether an older
Copilot ignores an unrecognized field silently or complains about it. **Claude
Code is the happy path** — it is the primary harness, and the subagent it spawns
is expected to honor the frontmatter `model`. On Copilot, tier routing is
best-effort; the agent file still buys context isolation, tool scoping, and
delegation structure, so the degradation costs an optimization, not correctness.
*Recommendation: emit the field anyway and document a supported Copilot version
floor* — but confirm empirically that an unsupported version ignores it rather
than erroring, since "harmless where unsupported" is an assumption here, not a
documented guarantee.

**8. Is the agent layer measurable at all?** Catalyst's telemetry rests on
Claude Code's [OTEL attributes](https://code.claude.com/docs/en/monitoring-usage),
and their redaction rules are asymmetric in a way that lands directly on this
RFD. `agent.name` appears verbatim only for built-in agents and agents from
official-marketplace plugins; **other user-defined agent names are replaced with
`"custom"`.** Every agent this RFD proposes is user-defined by construction, so
on today's mechanics all of them report as `agent.name = "custom"`: one
indistinguishable label across the whole layer, and no way to answer which agent
ran, which delegated to which, or whether a declared tier was the tier that
executed. That cost is specifically incurred by step 3, which deletes the
delegation prose that is currently the only durable record of who was supposed to
run. It is far cheaper to instrument the agents at birth than to reconstruct
attribution after the prose is gone.

The second edge is no longer a hypothesis, and it is worse than this section
originally guessed. An earlier revision said `skill.name` "appears verbatim for
built-in, bundled, user-defined, and official-marketplace plugin skills — which
is why skill telemetry works today," and treated third-party redaction as a risk
to check. **Measured three times — a directory marketplace, a GitHub
marketplace, and this repo's own skills — `skill.name` and `plugin.name` are both
replaced with `"third-party"`, and `marketplace.name` is absent entirely.**
Corroborating, the docs say `marketplace.name` is "Only emitted for
official-marketplace plugins," so its absence is the documented signal that we
are third-party rather than an anomaly. So skill telemetry does **not** work
verbatim today for a marketplace install; the claim that it did was wrong and is
recorded as such in AICAT-339. Since PR #438 this repo ships as a marketplace, so
the distribution path decides whether a skill is nameable at all — a property
nobody chose.

That removes the asymmetry this question was built on: **both** layers are
redacted, not just agents. It also disposes of option (c) more firmly than
written — the beta span surface does not rescue attribution either, since
`query_source_safe` renders user-named agents as `agent.custom` too, so there is
no second surface to fall back to.

Options: (a) accept `"custom"` and `"third-party"` on the OTEL surface and carry
identity in a signal Catalyst controls, joined to the OTEL records on session id;
(b) treat verbatim attribution as a requirement and pursue whatever would qualify
these agents as non-user-defined; (c) infer identity indirectly from the skill
sequence a phase emits, accepting ambiguity wherever two agents share skills.
*Recommendation: (a)* — our own signal is the only lever we fully control, (b)
depends on Anthropic's definition of "official", and (c) degrades exactly where
the agent layer is densest and has no second surface to lean on.

**The implementation for skills already exists and is merged**, which is the part
this section previously mis-assigned. It said the work "belongs to RFD 0021";
`rfd/0021/README.md` is `state: abandoned`, and 0021 itself records the
native-OTLP pipeline as superseding its hook — so it is not producing adoption
numbers and cannot own this. The real owner is
[`scripts/emit_skill_usage.py`](../../scripts/emit_skill_usage.py) (merged in
#443), which reads the session transcript rather than a hook — a hook-based
emitter was written and then deliberately removed, so "Catalyst's own hook log",
as an earlier revision of this paragraph put it, names a mechanism that no longer
exists. It emits `catalyst.skill.invocation` carrying `catalyst.skill` and
`catalyst.plugin`, deliberately namespaced so they are never confused with Claude
Code's redacted `skill.name` / `plugin.name`, with `session.id` left un-namespaced
because it is the join key.

What remains open is therefore narrower than this question originally framed: the
skill half is solved and shipping, and **the agent half needs the same treatment**
— the transcript records `Task`/`Agent` invocations, so the same reader can
recover `agent.name` before step 3 deletes the prose. That is the work this RFD
should own, and it is the reason to instrument at birth rather than after.
