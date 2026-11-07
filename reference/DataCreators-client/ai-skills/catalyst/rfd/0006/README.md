---
authors: RBAP
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/10
labels: skills, contribution, governance
---

# RFD 0006 Skill Contribution Strategy

## Problem

We're building AI skills as a product for the enterprise. These skills are a
mix of natural language instructions, Python tooling, and templates. Today
they're spread across two repos with no shared definition of what "ready to
ship" means, no consistent layering of shared components, and no clear process
for how a skill moves from experimentation to production.

As we scale — more skills, more consumers, more contributors on our team — we
need a contribution strategy that keeps velocity high while ensuring what we
ship is layered, reusable, composable, and maintainable.

This RFD defines where skills are developed, what quality bar they must meet,
how their components are layered for reuse, and how skills move from
experimentation to production.

## Background

### What We're Building

The Data Product Lifecycle (RFD 0002) defines 9 phases that guide a data
product from initial request through production operation to retirement. Skills
accelerate this lifecycle — generating artifacts, scaffolding pipelines,
enforcing quality standards — so data product creators can focus on the
decisions that matter.

The audience is data product creators across the firm. The skills accelerate
the lifecycle regardless of the creator's background.

### Where Skills Live Today

**edo-ai-skills** (`cg-edo/edo-ai-skills`) — where skills are developed
rapidly to solve immediate problems. ~50+ skills across data platform,
planning, integrations, and document generation. Quality varies. This is where
we learn what's useful.

**Catalyst** (`cg-open-itg/catalyst`) — the home for productized skills that
are part of the Data Product Lifecycle. Skills here need to be well-built,
well-tested, and well-documented. This is what we ship to the enterprise.

### What's Missing

1. **No shared quality standard** — no definition of what "ready to ship" means
2. **No layering strategy** — shared logic is copy-pasted across skills instead
   of composed from reusable components
3. **No graduation process** — useful skills sit in edo-ai-skills indefinitely
   because there's no path to production
4. **No contribution process** — contributors don't know where to put things or
   what bar applies

## Proposal

### Skill Specification

Catalyst skills follow Anthropic's published Skills standard ("The Complete
Guide to Building Skills for Claude"). The standard defines the shape of a
skill — file structure, frontmatter, naming, and how content is loaded into
the model. RFD 0006 layers org-specific concerns (graduation, shared
components, dependencies) on top of this baseline.

#### File structure

A skill is a folder containing:

```
{skill-name}/
├── SKILL.md          # required — instructions in Markdown with YAML frontmatter
├── scripts/          # optional — executable code (Python, Bash)
├── references/       # optional — documentation loaded on demand
└── templates/        # optional — artifact templates referenced by the skill
```

`SKILL.md` must be exactly that filename, case-sensitive. No `README.md`
inside a skill folder — repo-level READMEs for human visitors live at the
repo root.

We deviate from Anthropic's spec on one point: the standard specifies an
`assets/` directory for templates, fonts, icons. Our skills primarily produce
structured artifacts (data contracts, runbooks, deployment records) from
templates, so we use the more semantic `templates/` name. Anthropic's
`assets/` is also acceptable when a skill genuinely needs fonts or icons.

#### Folder and skill naming

- kebab-case only (`data-contract` ✅, `Data Contract` ❌, `data_contract` ❌)
- folder name matches the `name` field in frontmatter
- no `claude` or `anthropic` prefix (reserved by Anthropic)

#### Frontmatter

Required fields:

```yaml
---
name: skill-name              # kebab-case, matches folder
description: |                # WHAT it does + WHEN to use it + trigger phrases
  Generate a producer-consumer data contract for a data product. Use when
  user asks to "create a data contract", "define SLAs", "write the schema
  contract", or mentions data product onboarding.
---
```

The `description` field carries the entire load of the first level of
progressive disclosure (see below). It must include both *what the skill
does* and *when to use it*, with concrete trigger phrases users would
actually say. Maximum 1024 characters. No XML angle brackets (`<` `>`) —
they break frontmatter security parsing.

Optional fields:

- `license` — for open-source skills (MIT, Apache-2.0)
- `compatibility` — environment requirements (1–500 chars)
- `allowed-tools` — restrict tool access using permission patterns
  (e.g., `"Bash(python:*) WebFetch"`)
- `metadata` — custom key-value pairs. We use this for org-specific fields:
  `lifecycle-phase`, `dependencies`, `consumes`, `shared-components`,
  `eval-results`, `version`, `author`.

#### Progressive disclosure

Skills load content into the model in three levels:

1. **Frontmatter** — always loaded into the system prompt. Provides just
   enough information for the model to know *whether* to load this skill.
   Keep it tight.
2. **`SKILL.md` body** — loaded when the model decides the skill is relevant
   to the current task. Contains the workflow and core instructions.
3. **`references/` files** — loaded only when the skill instructs the model
   to consult them. This is where long-form documentation, API patterns,
   exhaustive examples, and edge-case guidance live.

This three-level structure minimizes token usage while keeping specialized
knowledge available. The "Keep skills thin" principle in our Layering
Strategy is the same idea applied at the skill-content level: orchestration
in `SKILL.md`, detail in `references/`.

Keep `SKILL.md` under 5,000 words. If you're past that, content belongs in
`references/`.

#### Relationship to existing Catalyst skills

The 35 skills already in `rfd/0002/skills/` predate this spec. They use a
slightly different frontmatter shape — most notably an `argument-hint:`
field (a Claude Code slash-command convention, not part of the Anthropic
Skills spec) and `description:` values that state what the skill does
without WHEN/trigger phrases. This RFD locks the spec going forward; a
follow-up PR retrofits the existing skills to match. Concrete differences
between today's 35 skills and the spec above:

- `argument-hint:` is dropped (Claude Code slash-command field, not part
  of the Skills spec).
- `description:` gains trigger phrases so the skill auto-loads on relevant
  prompts.
- Per-skill org-specific metadata (`lifecycle-phase`, `dependencies`,
  `consumes`, `shared-components`) gets filled in under the `metadata`
  block.
- Long-form documentation moves into `references/` if it would push
  `SKILL.md` past the 5,000-word ceiling.

Treat the existing 35 skills as the starting point for the retrofit, not
as the target format.

### Contribution Tracks

**Track 1: edo-ai-skills (R&D)**

Where we prototype, experiment, and solve problems fast. A skill here needs to
work, but it doesn't need to be polished. No RFD required. Eval framework
available but not mandatory. This is where we learn what's useful before
investing in packaging.

**Track 2: Catalyst (Production)**

Where skills ship to the enterprise as part of the Data Product Lifecycle.
A skill here must meet the production quality standard defined below.
Contribution requires an RFD to think through: what part of the lifecycle does
this skill accelerate, and how does it compose with what's already there?

The RFD process isn't bureaucracy — it's how we force ourselves to articulate
why a skill exists and who it's for. That thinking is what makes the difference
between a tool that works for its author and a product that works for the
enterprise.

**The expected flow is R&D → Production.** Most skills start in edo-ai-skills
where we can iterate fast, prove value on real projects, and learn what works.
When a skill demonstrates value and fits the lifecycle, it graduates to
Catalyst through the graduation process defined below. This is how the skill
set grows — experimentation feeds production.

**Direct contribution to Catalyst** is welcome when a skill is clearly
lifecycle-specific and doesn't need an R&D phase, but you still write the RFD.

### Production Quality Standard

This is what a skill must meet before it ships. Can we look at the whole
thing — the prompt, the scripts, the templates, the naming, the lifecycle
fit — and stand behind it?

Four pillars:

#### 1. Is It the Right Thing?

Does this skill belong in the lifecycle? Does it solve a real problem for data
product creators? Is it the right abstraction — not too narrow (only useful for
one team's workflow) and not too broad (tries to do everything)?

This is a judgment call that comes from the RFD process and peer review. No
checklist replaces thinking through whether the skill should exist in its
proposed form.

#### 2. Is It Well-Built?

The skill complies with the Skill Specification above — file structure,
frontmatter rules, progressive disclosure. The prompt is clear and explains
the _why_ so the model can adapt. Scripts follow the layering strategy and
are composed from shared components, not copy-pasted. Templates are
referenced, not embedded. Platform-specific implementations sit behind common
interfaces.

#### 3. Is It Well-Tested?

Three test categories cover a production skill:

- **Triggering tests.** The skill auto-loads on relevant queries (target
  ≥90%) and stays out of the way on unrelated ones. Tested by running 10–20
  representative prompts and checking which load the skill.
- **Functional tests.** Scripts have unit and integration tests — the Python
  code is software and gets tested like software. The skill as a whole is
  evaluated against realistic scenarios with documented results.
- **Performance comparison.** A baseline measurement against running the same
  task without the skill. Quantitative metrics: tool calls, tokens, success
  rate. Qualitative: does the skill reduce back-and-forth and user
  corrections?

Someone on the team has reviewed the actual outputs and confirmed they're
useful — eval scores alone don't capture user value.

#### 4. Is It Well-Documented?

Someone who's never seen this skill can find it, understand when to use it,
know what it depends on, and follow the workflow without reading the source.
Long-form documentation lives in `references/` and is loaded on demand
rather than inflating `SKILL.md`.

### Production Runtime Target

This section describes a runtime that does not exist yet. It is the
architecture we're targeting for graduated skills, not a system in
production today.

The plan is to run Catalyst skills inside a hosted runtime that executes
them via the Claude Agent SDK. A prototype landed in PR #6 of this repo
and the work is being picked up in catalyst-app, but neither is shipping.
The benefit of writing skills against the target runtime shape now is
that they won't need to be rewritten once it does ship.

What's pinned down here is the **shape** of how a skill will run. Specific
numbers are first-cut targets from the PR #6 prototype and will move.
Transport and platform-integration specifics (e.g., streaming protocol,
proxy behavior, hosting platform) are deliberately left out because
they're implementation choices for the runtime to make, not contracts on
the skill.

| Constraint | Shape | First-cut target | What it means for skill design |
|---|---|---|---|
| Tool-use turns | bounded | ~15 | Skills should converge in a small number of round-trips, not loop indefinitely. |
| Output size | bounded | ~16k tokens | Plan artifact size accordingly; large content goes into `references/` or files. |
| Wall-clock timeout | bounded | ~5 minutes | No long-running synchronous calls; break long work into separate invocations. |
| Concurrency within a phase | sequential | 1 | Don't assume sibling skills are running in parallel. |

A skill that works fine in Claude Code but assumes unbounded turns,
interactive CLI tooling, or long-running synchronous work would not fit
this shape cleanly. If a skill genuinely needs to diverge — say a
research-style skill that legitimately needs more turns — that divergence
should be called out in the skill's RFD with rationale, and we'd decide
whether to relax the constraint, accommodate the skill specially when the
runtime is built, or keep it Claude-Code-only.

### Layering Strategy

Skills are not monoliths. They're composed from layers, and each layer has a
clear responsibility. This is how we get reuse, composability, and
maintainability.

```
                        ┌──────────────┐
          ┌────────────►│  Templates   │
          │  references │  (data, not  │
          │             │   code)      │
          │             └──────────────┘
          │
┌─────────┴───────────────────────────────────┐
│              Skills (SKILL.md)               │
│  Prompt + orchestration + judgment. The      │◄──── can invoke
│  agent decides what to ask, when to call     │      other skills
│  scripts, how to adapt to context.           │
├─────────────────────────────────────────────┤
│         Skill Scripts (optional)             │
│  Deterministic workflows that don't need     │
│  LLM judgment. Fixed sequences of core       │
│  function calls.                             │
├─────────────────────────────────────────────┤
│              Core Functions                   │
│  Reusable actions that do one thing well.    │
│  Profile a table. Generate a dbt model.      │
│  Trace lineage. Resolve IDs.                 │
├─────────────────────────────────────────────┤
│              Platform Clients                 │
│  API wrappers and connection management.     │
│  No business logic. Databricks, Dremio,      │
│  Jira, Confluence.                           │
└─────────────────────────────────────────────┘
```

**Platform clients** are API wrappers. They know how to connect to Databricks,
run a SQL query, authenticate to Jira. They don't know anything about the
lifecycle or data products. One shared library per platform, used by everything
above.

**Core functions** are reusable building blocks. Each one does a single thing
well: profile a table's columns, generate a dbt staging model, trace
column-level lineage, validate a data quality rule. They use platform clients
but add the operational logic. These are the components that get composed and
reused across skills.

**Skill scripts** are an optional layer for deterministic workflows — fixed
sequences of core function calls where the agent doesn't need to make judgment
calls. A pipeline scaffolding script might call profiling, then dbt generation,
then DAG creation, then DQ rule generation — in order, every time. If the
workflow needs the agent to look at intermediate results and decide what to do
next, that decision-making stays in the skill, not the script.

A concrete example of what a skill script looks like — Python invoked from
`SKILL.md` via the Bash tool:

```python
# scripts/scaffold_pipeline.py
from catalyst.core import profile_table, generate_staging_model, create_dag, generate_dq_rules

def main(source_table: str, target_schema: str) -> dict:
    profile = profile_table(source_table)
    model = generate_staging_model(profile, target_schema)
    dag = create_dag(model)
    rules = generate_dq_rules(profile)
    return {"profile": profile, "model": model, "dag": dag, "rules": rules}
```

The skill calls this with `python scripts/scaffold_pipeline.py {source} {target}`
and consumes the JSON output. No LLM judgment in the script — every invocation
runs the same four core functions in the same order.

**Skills** are the SKILL.md files — natural language instructions that bring
judgment and adaptability. The skill decides what to ask the user, when to call
which scripts or core functions, and how to adapt based on context. A skill can
call core functions directly or through a skill script, depending on whether
the workflow is deterministic. Skills can also invoke other skills — a
discovery skill might call a data profiling skill as a sub-agent, or a
lifecycle workflow skill might chain through multiple phase-specific skills.
This is the thinnest layer by design — orchestration and context, not business
logic.

**Templates** sit alongside the stack, not beneath it. They're data, not code —
they define the structure of outputs (e.g., a data contract, a runbook, a
deployment record). Skills reference them. Templates live in the `templates/`
directory and are the single source of truth for artifact structure.

#### Layering Principles

- **Don't duplicate.** If two skills need the same logic, it belongs in core
  functions, not copy-pasted into two scripts.
- **Compose, don't monolith.** An 800-line script is doing too much. Break it
  into core function calls.
- **Test at the right layer.** Unit test core functions. Integration test skill
  scripts. Eval test skills. Don't test the LLM orchestration with unit tests
  or the Python logic with eval prompts.
- **Interfaces over implementations.** Core functions and platform clients
  define clear interfaces. Platform-specific behavior lives behind those
  interfaces.
- **Keep skills thin.** The SKILL.md should be orchestration, judgment, and
  context — not business logic. If you're writing a deterministic sequence
  in the prompt, that's a skill script. If you're encoding complex logic,
  that's a core function.
- **Script when deterministic, skill when adaptive.** If every invocation
  follows the same steps in the same order, use a skill script. If the agent
  needs to look at results and decide what to do next, keep that in the skill.

#### Where layers live on disk

Skills, shared Python code, templates, and references all live in this
repo (catalyst), under a single top-level `skills/` directory. The
intended consumption model — once a hosted runtime exists — is for
catalyst-app to pull this code at CI/CD build time, with this repo as the
single source of truth rather than a copy that drifts. By default the
consumer would use the skill as-is; if a specific skill needed to behave
differently in the hosted runtime (for example, adapted for WebSocket
streaming or stricter resource limits), the consumer would maintain a
local fork of just that skill. Forking would be the exception, not the
rule. None of this consumer-side machinery exists today; what exists is
the layout below in this repo.

```
catalyst/
└── skills/
    ├── core/                        # shared core functions (Python package)
    ├── clients/                     # platform clients (Python package)
    ├── tests/                       # tests for core/ and clients/
    └── {skill-name}/                # one folder per skill, per Anthropic spec
        ├── SKILL.md                 # required — frontmatter + instructions
        ├── scripts/                 # optional — skill scripts that import from core/clients
        ├── references/              # optional — on-demand docs the model consults
        └── templates/               # optional — artifact templates this skill produces
```

| Layer | Location |
|---|---|
| Skill folder | `skills/{skill-name}/` (one per skill; graduating off `rfd/0002/skills/` as the retrofit lands) |
| Skill scripts | `skills/{skill-name}/scripts/` (per-skill) |
| References | `skills/{skill-name}/references/` (per-skill, on-demand docs — see Skill Specification) |
| Templates | `skills/{skill-name}/templates/` (per-skill artifact templates) |
| Core functions | `skills/core/` (shared Python package, importable across skills) |
| Platform clients | `skills/clients/` (one module per platform: `databricks`, `dremio`, `jira`, `confluence`) |
| Tests | `skills/tests/` (for shared core and clients; per-skill tests live alongside their `scripts/`) |

The split between per-skill and shared is the only split that matters.
Per-skill content (SKILL.md, scripts, references, templates) lives inside
the skill's folder and follows the Anthropic spec exactly. Shared Python
code (core functions, platform clients) lives at the top of `skills/` and
is imported by skill scripts.

Skills do not import other skills' scripts, templates, or references
directly. They invoke other skills via the skill-to-skill mechanism (see
Skill Dependencies). All cross-skill code reuse goes through core functions
and platform clients.

### Skill Dependencies

Skills don't exist in isolation. They relate to each other in three ways:

#### Skill-to-skill invocation

One skill calls another skill during execution. A discovery skill might invoke
a data profiling skill as a sub-agent, use its output to assess source quality,
then populate a feasibility report. A lifecycle workflow skill might chain
through multiple phase-specific skills in sequence. Dependencies should be
declared explicitly and skills should depend on what the called skill produces,
not how it produces it.

#### Artifact handoff

Skills consume artifacts produced by earlier skills in the lifecycle. A Phase 3
design skill reads the requirements and feasibility report from Phase 2. A
Phase 7 runbook references the SLAs defined in the Phase 3 data contract.
The template defines the contract — if a downstream skill expects a certain
section, that expectation is grounded in the template structure. Skills should
work with whatever artifacts are available and reference prior work rather than
asking users to re-enter information.

#### Shared components

Multiple skills may depend on the same core functions or platform clients.
Changes to shared components affect every skill that uses them, so interfaces
need to be stable and breaking changes need a migration path.

#### Dependency graph

All three types of dependency form a graph. The graph is declared, not
discovered after the fact: each skill records its dependencies in `SKILL.md`
frontmatter under the `metadata` block. The Anthropic Skills spec leaves
`metadata` open for custom key-value pairs, so this is our org-specific
extension of the spec, not a deviation from it.

```yaml
metadata:
  dependencies: [data-profiling, source-aligned]   # skills this skill invokes
  consumes: [feasibility-report, requirements]      # artifacts this skill reads
  shared-components:                                # core functions / platform clients used
    core: [profile_table, generate_staging_model]
    platforms: [databricks, jira]
```

The SKILL.md is the source of truth. There is no separate aggregated graph
file to keep in sync — that's how Python packages, npm packages, and Bazel
targets all handle dependencies. The graph is computable from the per-skill
declarations whenever someone needs it (`grep -rA5 'metadata:' skills/` or
a one-shot script).

What does need to be enforced is that the metadata block is actually filled
in — a discipline problem, not a tooling problem. A SKILL.md schema check
in CI is enough: it parses each skill's frontmatter, verifies the required
fields are present, and fails the build if a skill is missing
`metadata.dependencies`, `metadata.consumes`, or `metadata.shared-components`
when those apply. Anything more elaborate is over-engineering.

### Graduation: Moving Skills from edo-ai-skills to Catalyst

Graduation is the process of taking a skill that works in R&D and making it
production-ready for the enterprise. This is not a copy-paste — it's a
deliberate product decision followed by engineering work.

#### When to graduate

A skill is a graduation candidate when:

1. **Demonstrated value.** It's been used on a real project and the output was
   useful — not just "it ran without errors."
2. **Lifecycle fit.** Someone can articulate which DPLC phase(s) the skill
   serves and how it composes with existing Catalyst skills.

Not every useful skill needs to graduate. If it's working well in
edo-ai-skills and doesn't serve the lifecycle, it can stay there.

#### How graduation works

1. **Write an RFD in the Catalyst repo.** The RFD covers what the skill does,
   which phase it serves, how it composes with existing skills, and how it
   will be evaluated. This is where we think through the product strategy —
   naming, packaging, what the user sees.

2. **Refactor to meet the production quality standard.** This is usually the
   bulk of the work. It may involve:
   - Extracting shared logic from the skill into core functions
   - Adding unit and integration tests for scripts
   - Restructuring to follow the layering strategy
   - Running the eval framework and documenting results
   - Writing documentation (lifecycle phase, dependencies, examples)

3. **Build the skill in Catalyst.** The Catalyst version is built to the
   production standard — it's not a fork of the edo-ai-skills version, it's
   a new implementation informed by what was learned in R&D. It may share
   core functions and platform clients, but the skill itself and its scripts
   are authored for Catalyst's conventions and quality bar.

4. **Peer review.** The team reviews the RFD and the skill together. The
   question is not just "does it work" but "can we stand behind this."

5. **Decide what happens in edo-ai-skills.** Once the Catalyst version ships:
   - The edo-ai-skills version can stay as-is (if teams still use it directly)
   - Or it can be deprecated with a pointer to the Catalyst version
   - Either way, the Catalyst version is the one we stand behind for the
     enterprise

#### What changes during graduation

| Aspect | edo-ai-skills (R&D) | Catalyst (Production) |
|--------|--------------------|-----------------------|
| Quality bar | Works for the author | Meets all four pillars |
| Scripts | May be monolithic, inline | Layered: core functions + optional skill scripts |
| Tests | Optional | Unit tests, integration tests, eval coverage |
| Templates | May embed structure | References shared templates |
| Dependencies | Implicit | Declared in metadata, part of dependency graph |
| Documentation | README at best | Lifecycle phase, dependencies, examples |
| Naming | Technical (`source-aligned`) | Default `{artifact-slug}` (e.g. `data-contract`, `runbook`) matching existing 35 skills; deviation requires RFD justification |

## Alternatives

### Single repo for everything

Put all skills in Catalyst with different quality tiers. Rejected because it
removes the iteration speed advantage of edo-ai-skills. R&D benefits from
lower friction — requiring an RFD to try something new would slow
experimentation.

### No graduation — keep repos independent

Keep contributing to both repos separately. Rejected because it leads to
duplication, inconsistent quality, and useful skills never reaching the
enterprise.

### Automated graduation based on eval scores

Auto-promote skills that pass eval thresholds. Rejected because eval scores
measure structural correctness, not user value or lifecycle fit. A skill can
score 100% on assertions and still be the wrong abstraction. Human judgment —
via the RFD process — is required.

## Impact

### Who Is Affected

- **Our team** (product/engineering) — this is our contribution process.
  Everyone building skills follows these tracks and standards.
- **Data product creators** (the enterprise) — they benefit from
  better-packaged, more reliable skills in Catalyst.
- **edo-ai-skills contributors** — no immediate process change, but
  contributors should be aware of the production quality standard. Skills
  built with the layering strategy in mind are easier to graduate later.

### Next Steps

1. Merge this RFD after discussion
2. Refactor existing shared logic into the layering structure (platform
   clients → core functions → skill scripts → skills)
3. Identify the first batch of edo-ai-skills candidates for graduation
4. Write individual RFDs for each graduation candidate
