# Skill behavior tests

LLM-judged behavior verification for Catalyst skills. Sibling to
`skills/tests/` (deterministic Python unit tests of `skills/core/` and
`skills/clients/`); this suite drives actual `SKILL.md` prompts end-to-end
through `claude-agent-sdk`, captures what the agent does, and grades the
output.

Design rationale: `docs/superpowers/specs/2026-04-29-skill-behavior-tests-design.md`.

---

## Why this exists

When you change a skill's prompt, template, or dependencies, you want to
know:

1. **Does it still run?** (smoke)
2. **Did the output get worse?** (quality regression)
3. **Did the agent take the path you intended?** (architectural conformance)
4. **For orchestrators:** did it invoke the right sub-skills in the right
   order? (behavioral correctness)

This harness automates all four, so a one-line prompt change in
`skills/data-contract/SKILL.md` doesn't silently regress 5 downstream
phases.

---

## Setup (first time)

You need: Python 3.10+ (3.13 recommended — see `docs/install.md`), the repo's
`.venv`, and a `.env` with **test** Databricks credentials. **Do not point
the harness at production.**

1. **Install deps** (once):
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r skills/requirements.txt
   ```

2. **Copy and fill `.env`**:
   ```bash
   cp .env.example .env
   # Edit .env. The behavior tests need at minimum:
   #   TEST_CATALOG=<dev catalog with cg_employee_v4 or similar>
   #   TEST_SCHEMA=<schema in that catalog>
   #   TEST_DATABRICKS_HOST=https://<your-test-workspace>.cloud.databricks.com
   #   TEST_DATABRICKS_TOKEN=<PAT for the test workspace>
   #   TEST_DATABRICKS_WAREHOUSE_ID=<a SQL warehouse ID in that workspace>
   #   TEST_CONFLUENCE_PAGE_ID=143164794   # Index Data Product Proposal
   #   TEST_CONFLUENCE_PAGE_TITLE="Index Data Product Proposal"
   #   TEST_CONFLUENCE_SPACE=IIKF
   ```
   The harness refuses to run live unless `TEST_DATABRICKS_HOST` is set
   (override only with `--allow-prod-databricks` if you really mean it).

3. **Auth for the LLM runner.** Pick whichever applies to you:

   **A. Claude Code session** (default, Mac/Linux only). If you have Claude
   Code installed and signed in, `claude-agent-sdk` reuses that OAuth — no
   env vars needed.

   **B. Anthropic API direct.** Set `ANTHROPIC_API_KEY=<your-key>` in `.env`.
   Bills that account directly.

   **C. Databricks-hosted Claude** (default for Capital Group teammates
   when `TEST_DATABRICKS_HOST` + `TEST_DATABRICKS_TOKEN` are in `.env`).
   `bin/bt`'s `configure_databricks_gateway` automatically sets
   `ANTHROPIC_BASE_URL=<workspace>/serving-endpoints/anthropic` and
   `ANTHROPIC_AUTH_TOKEN=<test PAT>` for the run — one credential set
   drives both warehouse SQL traffic and LLM calls. No local proxy.
   You can also set the same env vars in `~/.claude/settings.json` and
   they take precedence (the harness checks `ANTHROPIC_BASE_URL` first
   and skips its own auto-config if already set).

4. **Windows users:** run from **Git Bash** as `bash bin/bt <subcommand>`
   (Windows `cmd.exe` doesn't honor the shebang). Everything else is portable.

---

## Quick start

The `bin/bt` wrapper auto-loads `.env` and points outputs at
`workspace/behavior-tests/`. All five subcommands accept extra flags
that pass through to the underlying CLI.

```bash
bin/bt list                           # enumerate all cases
bin/bt smoke                          # 1-case smoke (discover-data, ~2 min)
bin/bt smoke data-contract.case-01-happy-path
bin/bt cases A B C                    # run an explicit list of cases
bin/bt full                           # full live run, concurrency 4 (single-phase)
bin/bt execute                        # phase 1 — agent runs, transcripts cached, no grading
bin/bt evaluate                       # phase 2 — grade cached transcripts (no agent)
bin/bt rejudge                        # alias for `evaluate`
bin/bt issues [--create]              # stage / file one GitHub issue per completed case
bin/bt preview                        # render dashboard from synthetic data (no agent/judge)
bin/bt clean                          # wipe workspace/behavior-tests/
```

After any run, open the live HTML dashboard:

```
file://$(pwd)/workspace/behavior-tests/live-report/index.html
```

It auto-refreshes every 3s, has per-case detail (tool-call timeline,
per-criterion grades, full output), and persists open-state across reloads.

If you need raw CLI access, that still works:

```bash
python -m tests.behavior --case discover-data.case-01-happy-path \
    --live-report workspace/behavior-tests/live-report
```

---

## What gets tested (three tiers)

Every artifact case runs three tiers in order. The judge runs only if all
deterministic pre-checks pass — saves tokens on obvious failures.

### Tier 1 — Structural pre-checks (deterministic, free)

Pure-Python predicates over the runner's output. Fast, reproducible.

| Check | Catches |
|---|---|
| `non_empty_output` | Agent produced nothing |
| `contains_section: "Name"` | Required heading missing (matches `## Name — suffix` too) |
| `has_markdown_table` | Agent prose-only when a table was expected |
| `no_placeholder_text` | Output still has `[TBD]`, `[fill in]`, `<placeholder>`, `lorem ipsum` |
| `min_length: N` | Truncated output |
| `valid_markdown` | Unbalanced fences |
| **`matches_template: <path>`** | Output structure deviates from the canonical template |
| **`uses_components: [paths]`** | Agent didn't invoke the components you expected |

### Tier 2 — LLM-as-judge with weighted rubric

A second Claude call grades the output against per-criterion questions you
write. Each criterion gets `score ∈ [0, 1]` and a one-sentence rationale;
the weighted sum must clear the rubric's `threshold`.

This is where domain knowledge lives. For `discover-data` we ask things
like *"Does the output reference cg_employee_v4 (the canonical test
table) and are all listed columns real Unity Catalog objects?"*

### Tier 3 — Behavior assertion (orchestrators only)

Behavior cases declare an `expected_sequence` of sub-skill paths. The
runner captures every `Skill` tool invocation; the assertion checks the
agent invoked them in order (with `strict_order` / `allow_extra` knobs).

---

## Two-phase pipeline: `execute` then `evaluate`

A test "case" and an "agent run" are separate things in this harness.

  - **A run** is what the agent does end-to-end with a `(skill, arguments)` pair.
  - **A case** is one evaluation against a run's transcript — its own structural
    checks + rubric + threshold.

That split lets you grade the *same* output along multiple dimensions
without re-invoking the agent. Cases that share an input share a
transcript automatically; the cache is content-addressed by `(skill,
arguments)` so the second case to run hits the cache instead of the
agent.

### Running in two phases

```bash
# Phase 1 — run the agent for every case, cache the transcript, skip
# structural checks and the LLM judge. Cases sharing a (skill, args)
# tuple invoke the agent only once; the rest hit cache.
bin/bt execute --case A --case B --case C

# Phase 2 — grade each cached transcript against its case's rubric.
# No agent calls; just structural checks + the judge.
bin/bt evaluate --case A --case B --case C
```

`bin/bt full` is the single-phase shortcut (run + grade combined).
Use it when you don't care about the split.

### Sharing a transcript across cases — the `Run` primitive

Multiple cases share a transcript by referencing the same `Run`. Two
files: one Run, N cases.

```yaml
# tests/behavior/cases/discover-data/run-01-happy-path.yaml
type: run
id: discover-data.run-01-happy-path
skill: skills/discover-data
input:
  arguments: "Inventory tables in ${TEST_CATALOG}.${TEST_SCHEMA} ..."
environment:
  databricks: live
```

```yaml
# tests/behavior/cases/discover-data/case-01-happy-path.yaml
id: discover-data.case-01-happy-path
type: artifact
run: discover-data.run-01-happy-path     # ← reference; no inline skill/input
structural_checks: [non_empty_output, no_placeholder_text]
expected_components: [skills/core/discover.py, skills/clients/databricks.py]
rubric:
  threshold: 0.7
  criteria: [...]
```

```yaml
# tests/behavior/cases/discover-data/case-02-discovery-coverage.yaml
id: discover-data.case-02-discovery-coverage
type: artifact
run: discover-data.run-01-happy-path     # ← same run; shared transcript
structural_checks: [non_empty_output, has_markdown_table]
rubric:
  threshold: 0.7
  criteria: [...]                         # different criteria from case-01
```

The dashboard surfaces this directly with a "Shared transcripts" panel:
*"1 agent invocation saved — 1 transcript feeding 2 cases."*

You can also inline `skill` + `input` directly on a case (back-compat
with older cases). Inlined cases that *happen* to have byte-identical
arguments will still share a transcript via content-addressing —
explicit `Run` references are just less fragile.

### Testing skills that should detect missing creds

Some skills' interesting branches only fire when env vars are absent
(e.g., discover-data's "When Databricks Is Not Configured" path). Use
`BT_UNSET_VARS` to scrub specific vars *after* `.env` loads but before
the harness sees them. Per-invocation only — your shell, `.env`, and
the next `bin/bt` are unaffected.

```bash
BT_UNSET_VARS="DATABRICKS_HOST DATABRICKS_TOKEN DATABRICKS_WAREHOUSE_ID" \
  bin/bt execute --case discover-data.case-03-no-databricks
```

---

## Architectural conformance: `expected_template` and `expected_components`

Two case-level fields make architectural intent enforceable:

```yaml
# Document skills: verify the output covers the template's structure
expected_template: skills/data-contract/templates/data-contract.md

# Layered skills: verify the agent went through the canonical components
expected_components:
  - skills/core/discover.py
  - skills/clients/databricks.py
```

`matches_template` parses the template's H2+ headings and table column
sets and asserts the runner's output covers them — content is left for
the rubric to grade. `uses_components` scans tool-call args (Bash command
strings, Read paths, Glob/Grep patterns) for each path in either
forward-slash form (`skills/core/discover.py`) or dotted-import form
(`skills.core.discover`).

When a check fails, the per-case `.md` shows a Component-coverage table
(`✅`/`❌` per component) and a Tool-call timeline (every call with its
arg summary) — so a reviewer can see exactly where the agent went off-track.

---

## Authoring a new case

1. **Decide where it goes.** Cases mirror the skill tree:
   `tests/behavior/cases/<category>/<skill-name>/case-NN-<label>.yaml`.
2. **Copy a sibling case** as a starting point.
3. **Pick a type:**
   - `artifact` — judges output (`structural_checks` + `rubric`)
   - `behavior` — judges sub-skill sequence (`expected_sequence` + `max_steps`)
4. **Dry-run with the fake runner first** — validates schema and wiring
   without spending tokens or hitting Databricks:
   ```bash
   BEHAVIOR_TESTS_USE_FAKE_RUNNER=1 python -m tests.behavior --case <id>
   ```
5. **Run live and tune the rubric thresholds** based on observed scores.

### Example artifact case

```yaml
id: discover-data.case-01-happy-path
skill: skills/discover-data
type: artifact
description: Discovers tables related to employees in ${TEST_CATALOG}.

input:
  arguments: "${TEST_CATALOG} employee headcount"

structural_checks:
  - non_empty_output
  - contains_section: "Discovered Tables"
  - has_markdown_table
  - no_placeholder_text

expected_components:
  - skills/core/discover.py
  - skills/clients/databricks.py

rubric:
  threshold: 0.75
  criteria:
    - id: structure
      weight: 0.2
      prompt: |
        Does the output contain a markdown table with columns Schema,
        Table, Row Count, Key Columns, Relevance?
    - id: groundedness
      weight: 0.4
      prompt: |
        Does the output reference cg_employee_v4 and are all listed
        objects plausibly real Unity Catalog tables?
    - id: relevance_flagging
      weight: 0.3
      prompt: |
        Does at least one row carry a HIGH/MEDIUM/LOW relevance label
        with a justification tied to the keywords?
    - id: no_placeholders
      weight: 0.1
      prompt: Output free of [TBD], [fill in], lorem-ipsum stubs?
```

### Example behavior case

```yaml
id: dplc-discovery.case-01-behavior
skill: skills/dplc-discovery
type: behavior
description: Phase 2 orchestrator must invoke discover-data and data-profiling before any document skill.

input:
  arguments: "employee headcount product ${TEST_CATALOG}"

expected_sequence:
  - skills/discover-data
  - skills/data-profiling
  - skills/feasibility-report

strict_order: true
allow_extra: true
max_steps: 30
```

---

## Live HTML monitor

For long-running suites, `--live-report DIR` writes a self-refreshing
dashboard:

```bash
python -m tests.behavior \
    --case <case-id> \
    --live-report workspace/behavior-tests/live-report
# Open: file:///path/to/workspace/behavior-tests/live-report/index.html
```

Shows in real time:
- Plugin badge: `<plugin-name>@<version>` from `plugin.json` (so you know what was tested)
- Coverage panel: skills with vs without test cases (computed against `plugin.json`)
- **Shared transcripts panel**: groups of cases that share a transcript, with the agent-invocations-saved count
- Counts: planned / running / passed / failed / skipped / queued
- Per-case row with status badge, elapsed time (JS-clock, ticks every second)
- **Expected Related Skills coverage column**: per-case ✅/❌ pills for every expected sub-skill (behavior cases) or layered component (artifact cases)
- Expandable case details (description + arguments) — open state persists across the auto-refresh
- Once a case finishes, a link to its full `.md` (case definition + per-criterion grades + tool-call timeline + component coverage + runner output)

The dashboard is self-contained HTML — no server needed; safe to keep open
in a tab while you work.

---

## Filing GitHub issues per case (`bin/bt issues`)

After a run completes, `bin/bt issues` stages one markdown body per
finished case in `workspace/behavior-tests/issues/`, then `--create`
files them as GitHub issues with labels.

```bash
bin/bt issues                          # dry-run: stage bodies to disk
bin/bt issues --create                 # actually `gh issue create` each
bin/bt issues --first-release          # filter to skills listed in the
                                       # README's "What's inside" section
                                       # (excludes Phase 4-8 staged skills)
bin/bt issues --include-runner-errors  # include cases that hit the
                                       # harness wall-clock / SIGKILL
                                       # paths (default: skipped — they're
                                       # usually harness bugs, not skill signal)
bin/bt issues --case <id>              # restrict to one case
```

Two issue templates, distinguishable by label:

- **`behavior-test:passed`** — case review + seeded gap-analysis checklist
  ("what does this case *not* exercise?").
- **`behavior-test:failed`** — failure dossier with the verbatim reason,
  tool-call timeline, output excerpt, and a cause-tailored suggested-fixes
  checklist.

Both bodies include:
- "Run context" header with `<plugin>@<version>`, runner model, judge model
- Repo permalinks (case YAML, SKILL.md, template, expected components)
  pinned to the run's commit SHA so the links survive merges
- A `## How to re-run this case` section with copy-pasteable
  `bin/bt smoke <case-id>` / `--runs 3` / `rejudge` snippets
- A `version:<plugin>-<version>` label on every issue so you can filter
  the GitHub issue tracker by which version was tested

First-time use: ensure the labels exist on the repo:

```bash
gh label create behavior-test:passed -c '0e8a16'
gh label create behavior-test:failed -c 'b60205'
gh label create version:ai-catalyst-1.1.0 -c '1d76db'
```

---

## Configuration

### Env vars

| Var | Required | Purpose |
|---|---|---|
| `TEST_DATABRICKS_HOST`, `TEST_DATABRICKS_TOKEN`, `TEST_DATABRICKS_WAREHOUSE_ID` | for live runs | Test workspace creds; also auto-configures the Databricks Anthropic gateway (`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`) for the runner |
| `TEST_CATALOG`, `TEST_SCHEMA` | when case args reference `${TEST_CATALOG}` etc. | Substituted at run time |
| `ANTHROPIC_API_KEY` | optional | If set and TEST_DATABRICKS_HOST is unset, claude-agent-sdk uses it; otherwise falls back to Claude Code session |
| `BEHAVIOR_TESTS_USE_FAKE_RUNNER=1` | optional | Stub runner+judge with deterministic fake responses (CI smoke / dry runs) |
| `BEHAVIOR_TESTS_CASES_ROOT=<path>` | optional | Override case discovery root |
| `BEHAVIOR_TESTS_RUNNER_MODEL` | optional | Default model for the runner (default: `claude-sonnet-4-6`) |
| `BEHAVIOR_TESTS_JUDGE_MODEL` | optional | Default model for the judge (default: `claude-sonnet-4-6`) |
| `BEHAVIOR_TESTS_ALLOWED_TOOLS` | optional | Comma-separated allowlist (default: `Bash,Read,Glob,Grep`) |
| `BEHAVIOR_TESTS_MAX_BUFFER_BYTES` | optional | JSONL transport buffer (default: `33554432` = 32 MB) |
| `BEHAVIOR_TESTS_MAX_TURNS_CEILING` | optional | Hard cap on agent turns per case (default: `60`) |
| `BEHAVIOR_TESTS_SANDBOX_ROOT` | optional | Parent dir for per-case sandbox tempdirs (default: `workspace/behavior-tests/sandboxes`) |
| `BEHAVIOR_TESTS_REDACT_VARS` | optional | Extra env vars (comma-separated) whose values should be scrubbed from cached output. Defaults already redact ANTHROPIC_*, CONFLUENCE_API_TOKEN, JIRA_API_TOKEN, DATABRICKS_TOKEN, TEST_DATABRICKS_TOKEN. |
| `BT_UNSET_VARS` | optional | Space-separated list of env vars to **unset** after `.env` loads but before the harness runs. Per-invocation only. Use to test missing-creds branches. |

### CLI flags

```
--list                          enumerate cases and exit
--skill <path>                  filter to one skill (e.g. discover-data)
--case <id>                     run a single case
--report <path>                 markdown report
--live-report <dir>             self-refreshing HTML monitor
--benchmark-dir <dir>           skill-creator-compatible grading.json + benchmark.json
--runs N                        run each case N times (variance mode)
--baseline                      also run a without_skill configuration per artifact case
--concurrency N                 run up to N cases in parallel (default 1)
--cache-dir <dir>               record each case's runner output for later reuse
                                (cache is content-addressed; cases sharing a
                                (skill, args) tuple share a transcript)
--from-cache <dir>              re-judge cached outputs without re-running the agent
--execute-only                  Phase 1 of the two-phase pipeline: run + cache,
                                no structural checks, no judge
--runner-model <alias>          override runner model
--judge-model <alias>           override judge model (try claude-haiku-4-5 for speed)
--allowed-tools <csv>           override the runner's permission allowlist
```

---

## Permission model

The runner uses `permission_mode="default"` (Claude Code's built-in safety
flow stays intact) plus an explicit allowlist of tools that auto-approve:

```
Bash, Read, Glob, Grep
```

This is what the test harness needs to navigate the repo and run shell
commands (Databricks SDK lives behind Bash). Anything outside the
allowlist (Write, Edit, network fetches, Task spawning, etc.) still goes
through the standard prompt flow.

We do **not** use `permission_mode="bypassPermissions"`. Override the
allowlist via `--allowed-tools` if a case needs more.

---

## skill-creator viewer integration

When `--benchmark-dir` is set, behavior_tests writes `grading.json` (per
run) and `benchmark.json` (aggregate) in the schemas defined by the
official `skill-creator` plugin. Render in their browser viewer:

```bash
python ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/\
skill-creator/skills/skill-creator/eval-viewer/generate_review.py \
    workspace/behavior-tests/live-report \
    --skill-name "discover-data" \
    --benchmark workspace/behavior-tests/live-report/benchmark.json
```

Two tabs: Outputs (qualitative per-case review) and Benchmark
(quantitative deltas, with `with_skill` / `without_skill` if you ran
`--baseline`). Pass `--static <html>` for headless environments.

We don't host the viewer — it's reused as-is from skill-creator.

---

## Variance and baseline modes

| Flag | What it does |
|---|---|
| `--runs N` | run each case N times; emit benchmark.json with mean ± stddev |
| `--baseline` | for each artifact case, also run a `without_skill` configuration; emit delta |

LLM-judge is non-deterministic — variance mode tells you whether a
borderline pass/fail is real or noise. Baseline mode proves the skill is
adding value vs. a blank prompt.

`--runs 3 --baseline` is ~6× the per-case cost. Use deliberately.

---

## Cost and runtime

Per-case at Sonnet-4.6 list prices: roughly **$0.05–$0.15** (skill
execution ~5–15K input + ~1–4K output; judge ~3–6K input + ~0.5K output)
plus Databricks compute. Live runs typically take **1–6 minutes per case**
depending on how many tool round-trips the agent needs.

Speeding things up:
- **`--concurrency N`** — run cases in parallel via a thread pool. Each case spawns its own `claude-agent-sdk` session, so concurrency multiplies API + warehouse load. Modest values (4–8) are a good starting point.
- **`--judge-model claude-haiku-4-5`** — judge is JSON scoring; doesn't need a smart model.
- **Tighter SKILL.md prompts** — fewer exploration turns means less wall time.
- **`--cache-dir <dir>` then `--from-cache <dir>`** — record runner outputs once, then iterate on the rubric without re-executing the agent. Eliminates runner cost (and warehouse load) for rubric tuning. Cache files are content-addressed by `(skill, arguments)` and named `<safe_skill>__<sha8>__<mode>.json`; cases that share a `Run` (or just happen to have identical args) share a single transcript file.

---

## Open follow-ups

- **`bootstrap-cases.py`** — auto-emit a happy-path case for every skill in `plugin.json` (uses `argument-hint` + the SKILL.md's `Dependencies` section + any `templates/<name>.md`).
- **Transcript cache** — `--from-cache <dir>` re-judges saved runner outputs without re-executing the agent. Critical for iterating on rubrics cheaply.
- **Golden outputs** — `golden.md` per case + `matches_golden_structure` check (markdown structural diff, not text diff).
- **Separate `TEST_DATABRICKS_*` creds** — isolate test runs from skill-using sessions hitting the same warehouse.
- **CI / GitHub Actions** — designed-for; not wired.
- **`CopilotRunner`** — v2; uses `github/copilot-sdk` headless mode + a `SKILL.md → defineTool` adapter.
- **Full E2E orchestrator runs** — currently behavior-only.
- **Confluence-backed cases** — currently Databricks-only.

---

## Hard constraints

- **No MCP.** No `mcp_*` imports, no `claude-agent-sdk` MCP-server registration. The runner uses the SDK with `mcp_servers={}` and Claude Code's built-in tools only. The judge has no tools at all.
- **No `bypassPermissions`.** Allowlist-based pre-approval, not blanket bypass.
- **No SKILL.md mutations.** The harness reads `skills/<name>/SKILL.md` files; it never writes to them. Rubrics live in the parallel `cases/` tree to keep skill folders Anthropic-spec-compliant.
- **Live tests don't run in CI without explicit auth wiring.** They expect Claude Code's session or `ANTHROPIC_API_KEY` plus Databricks creds; absent those, they skip.
