---
authors: Robert Walsh <robert.walsh@capgroup.com>, Ryan Ferrell <ryan.ferrell@capgroup.com>
state: abandoned
discussion: https://github.com/cg-open-itg/catalyst/pull/410
---

# RFD 0021 Catalyst Skill-Usage Telemetry

> **Abandoned — the problem was solved a different way.** Kept as a record rather
> than withdrawn, because the problem statement below is still the right one and the
> constraints it worked out still hold.
>
> **What happened to the mechanism.** This RFD proposed deriving skill usage from a
> VS Code `PreToolUse` hook that watched for `read_file` of `skills/<name>/SKILL.md`.
> That signal no longer exists: Copilot injects the skill catalogue into
> `gen_ai.system_instructions` instead, and across 274 trace payloads in the dev
> collector **no `read_file` span carries a `SKILL.md` path at all**. The hook's own
> documentation named this as its caveat. `scripts/hooks/` and
> `docs/skill-telemetry-hooks.md` were removed in
> [#441](https://github.com/cg-open-itg/catalyst/pull/441); the two PRs extending
> them, [#145](https://github.com/cg-open-itg/catalyst/pull/145) and
> [#414](https://github.com/cg-open-itg/catalyst/pull/414), were closed with their
> reasoning recorded.
>
> **What replaced it, for Claude Code.** Two parts, and the second was not expected.
> `agent.name`, `plugin.name` and `marketplace.name` are *unconditional* attributes on
> the `cost.usage` and `token.usage` metrics — no hook, no installer, and no content
> switch. `docs/telemetry/managed-settings-otel.json` configures the fleet and
> `/setup-workspace claude-otel` (AICAT-337,
> [#443](https://github.com/cg-open-itg/catalyst/pull/443)) configures one person.
>
> But `skill.name` is **redacted**. Claude Code sets it to the literal string
> `"third-party"` for any skill from a non-official marketplace, which is what Catalyst
> is — measured twice, across both a directory marketplace and a GitHub one: two
> distinct skills, one value (AICAT-339). So the platform reports *that* a third-party
> skill ran, what it cost, on which model, for which user — and withholds the one field
> the measurement exists for.
>
> **So derivation came back** — this RFD's central problem, one platform over.
> `scripts/emit_skill_usage.py` ([#443](https://github.com/cg-open-itg/catalyst/pull/443))
> recovers the name from the session transcript, where Claude Code records each
> invocation as a first-class tool call whose `input.skill` holds
> `"ai-catalyst:<skill>"`. The recovered names are emitted as `catalyst.skill` and
> `catalyst.plugin` on the **metrics** signal, namespaced so they are never confused
> with the platform's redacted `skill.name`, and nothing from `input.args` is ever
> read, logged, or sent.
>
> The difference from the hook is the distinction this RFD spent its life on:
> `input.skill` is a named field holding the answer, not a value inferred from a path.
> A field cannot stop containing its own value without the tool's input contract
> changing — whereas the hook died precisely because a path stopped appearing. The
> caveat is real and recorded in the script: the transcript is an internal format with
> no stability contract, unlike the documented hook API it replaced.
>
> **What is still open, for Copilot Chat.** Per-skill attribution is *not* currently
> collected. `catalyst-otel`'s `v_invocations` keys on `catalyst_*` tool calls, which
> came from the VS Code extension in
> [#97](https://github.com/cg-open-itg/catalyst/pull/97) — the PR closed in favour of
> the hook this RFD proposed. So the extension and the hook were each abandoned in
> favour of the other. Whether anything emits those tool names is unverified and
> tracked separately; it is the one open question this RFD leaves behind.
>
> ---
>
> ### The two harnesses are not symmetric, and that is most of the operational story
>
> | | VS Code Copilot Chat | Claude Code (DevNext / Coder) |
> |---|---|---|
> | Skill surface | `chat.agentSkillsLocations` in `.vscode/settings.json` | plugin install, then `~/.claude/settings.json` |
> | Telemetry config | four `github.copilot.chat.otel.*` keys, per user, hand-edited | an `env` block, written by `/setup-workspace claude-otel` |
> | Skill identity in telemetry | no skill concept at all — `gen_ai.tool.name` exists, `skill.name` does not | `skill.name` exists and is redacted to `third-party` |
> | Per-skill attribution today | **not collected** | **collected**, via the transcript emitter |
> | Content posture | `captureContent`, and conversation content *is* present in the dev bucket (AICAT-336) | metrics-only; no logs destination is ever written, so the collector cannot receive content |
> | Restart to take effect | window reload | a **new session** — the OTel SDK reads env once at process start |
>
> Two consequences worth stating rather than leaving to be rediscovered. The
> mechanisms share no code and no configuration, so a fix on one side is never a fix
> on the other. And the privacy properties differ in kind, not degree: the Claude Code
> path is structurally unable to carry content, while the Copilot path depends on a
> setting staying false.
>
> **Both surfaces were also found pointing at nothing, by two unrelated mechanisms.**
> VS Code's `chat.agentSkillsLocations` named four directories flattened away in
> April *and used an array where the setting is registered as an object map*, so the
> **folder-locator** path resolved none of the repo's 106 skills
> ([#428](https://github.com/cg-open-itg/catalyst/pull/428)). Scope matters here and
> an earlier revision of this line overstated it: plugin-contributed skills are read
> on a separate code path that never consults that setting, so anyone following
> `docs/install.md` was unaffected. The array form was the sharper half — it is
> *inert*, not merely wrong, because the reader guards on `!Array.isArray(...)` and
> then requires each value to be exactly `true`. Claude Code's plugin
> declared itself enabled in the repo's own `.claude/settings.json` and had never been
> installed, because project-scope enablement does not auto-install — it needed an
> explicit `claude plugin install ai-catalyst@catalyst`. Same silent outcome on both:
> a router that never matches anything Catalyst offers, with nothing reporting a
> fault. Neither was found by anyone noticing; both surfaced while looking at
> something else.
>
> ---
>
> ### Untested: the EC2 workspace
>
> Everything above was built and verified on a **Coder EKS** workspace. DevNext also
> offers an **EC2 VM** workspace, and that path is **untested**. The working
> assumption is that most of it carries over — the moving parts are a user-scope
> settings file, a local transcript directory, and an HTTPS POST, none of which is
> Kubernetes-specific — but that is an assumption, not a result, and should be read as
> one until somebody runs it there.
>
> One thing to settle *before* that test, because it otherwise makes the comparison
> impossible: **`workspace.kind` no longer distinguishes EC2 from EKS.** It originally
> derived `coder-eks` from `KUBERNETES_SERVICE_HOST`, and
> [#443](https://github.com/cg-open-itg/catalyst/pull/443) collapsed it to `coder`
> because that variable is visible inside a pod and absent in a host shell sharing the
> same `~/.claude` — so the value flipped with wherever the command ran, rewriting the
> settings file and dropping another timestamped backup on every alternate run.
> Stability was the right call; the cost is that the attribute
> `docs/telemetry/managed-settings-otel.json` still describes as separating "EC2 from
> EKS workspaces in the data" does no such thing.
>
> It cannot be recovered by detection. Every candidate — `KUBERNETES_SERVICE_HOST`,
> `CODER_PORT`, `CODER_SERVICE_HOST` — is Kubernetes service injection: present in the
> pod, absent outside it, the same instability in different clothing. And no
> `CODER_WORKSPACE_*` variable names the compute type; they carry id, name, owner and
> agent name only. So the value has to be **stated** rather than inferred: either the
> Coder template sets it, or `claude-otel` accepts it as an argument. Worth deciding
> before the EC2 run rather than discovering afterwards that both populations are
> labelled the same.
>
> **Three conclusions worth carrying forward**, all reached here and all still true: a
> mention of a skill is not a use of it (modelled downstream as `v_leakage` versus
> `v_invocations`); a signal that depends on another product naming a tool a particular
> way will break without warning — which is precisely how this one died; and deriving
> the skill name was not avoidable, only relocated. The platform that appeared to
> supply it redacts it, so the question this RFD opened is still the question, and
> `scripts/emit_skill_usage.py` is the current answer to it.
>
> ---
>
> **Everything below this line is preserved as written, in July 2026, and its present
> tense refers to that date.** It has deliberately not been rewritten: the
> value of an abandoned RFD is the reasoning as it stood, and editing the body to
> agree with today would destroy the record while appearing to improve it.
>
> Three of its statements are no longer true, and they are the ones a reader is most
> likely to act on:
>
> | The body says | Actually |
> |---|---|
> | `scripts/hooks/skill-telemetry.py` is "on `main`" (twice) | removed in [#441](https://github.com/cg-open-itg/catalyst/pull/441); not on `main` |
> | "PR #145, currently `CHANGES_REQUESTED`" | [#145](https://github.com/cg-open-itg/catalyst/pull/145) is **closed** |
> | "**PR #414** carries the hook's attribution hardening" | [#414](https://github.com/cg-open-itg/catalyst/pull/414) is **closed** |
> | the review fixes "landed in #414" | they never landed — #414 closed **unmerged**, so the hardening was designed and reviewed but never shipped |
>
> The last row is a different kind of error from the others. The rest are
> present-tense sentences that were true when written; that one asserts something
> that never became true, and no amount of elapsed time fixes it. Worth reading as
> the RFD's own illustration of its second conclusion — a signal that depends on
> another party's action will break without warning.
>
> Where this note and the body disagree, this note is current.

## Problem

We cannot measure AI Catalyst adoption. We do not know which skills are used,
how often, by how many people, with which model, or where they fail. Without
that signal we are guessing at what to invest in, what to deprecate, and whether
the plugin is delivering value.

There is no comprehensive usage log available today. The only adjacent data
(API token usage from the platform team) does not attribute usage to skills, and
a separate check for an alternative source is being pursued out-of-band. We
should not block on it.

Two capture mechanisms have grown up independently and now overlap:

- A client-side **PreToolUse hook** that regexes `SKILL.md` reads into a local
  JSONL file, with an optional OTLP push (in `main`; the push is proposed in
  PR #145, currently `CHANGES_REQUESTED`).
- A server-side **native-OTLP pipeline**, `catalyst-otel`, that ingests the
  OpenTelemetry signals VS Code Copilot already emits and lands them as Delta
  tables (working Rust implementation plus a design doc in the `catalyst-otel`
  repo).

This RFD records the decision on which mechanism is the telemetry backbone, how
the other fits (or is retired), and the failure-handling and privacy posture the
team asked to see settled before we commit to an MVP.

## Background

**Copilot emits OTLP natively.** In agent mode, VS Code Copilot Chat emits
OpenTelemetry traces (`invoke_agent` → `chat` → `execute_tool`), GenAI
semantic-convention metrics (token usage, operation duration), and chat events
(`copilot_chat.session.start`, `copilot_chat.tool.call`,
`copilot_chat.user.feedback`). By default the exporter redacts prompt content,
responses, and tool arguments — metadata only. Content capture is opt-in via
`github.copilot.chat.otel.captureContent`. Copilot's signals do **not** include
a `catalyst.skill_id`; deriving that identifier is the core original work.

**The hook mechanism (`scripts/hooks/skill-telemetry.py`, on `main`).** A
`PreToolUse` hook sees each tool call, extracts a skill name from
`/skills/<name>/SKILL.md` paths, and appends JSONL to
`~/.catalyst/skill-use.jsonl`. It was validated empirically (~81 fires → 40
skill hits → 4 skills). PR #145 adds an OTLP push on top. Its review (RBAP,
`CHANGES_REQUESTED`) surfaced correctness issues that are exactly the
failure-mode questions below: an `os.uname()` call that dies silently on
Windows, a non-daemon thread that can exceed the hook latency budget, and a
`{"continue": true}` that is not flushed before the join. PR #145 also adds
GitHub-username capture via `gh api user` on every fire; the hook on `main`
does not — it records no user identity today.

**PR #414** carries the hook's attribution hardening (read-gated capture,
skill-root discipline, recorded match rules, Windows path normalization,
offline contract tests). Its review is worth reading as evidence for the
decision below rather than as incidental cleanup: every defect it found was a
*silent under- or over-count*, never a crash or an error message. That is the
characteristic failure signature of client-side capture, and it is the main
reason this RFD puts the backbone server-side.

**The `catalyst-otel` pipeline (RBLW).** A separate repo already implements, in
Rust: a `receiver` (axum → Parquet → S3), a `transformer` (DataFusion +
delta-rs → bronze/silver/gold Delta), a `skill-registry` codegen tool that reads
the plugin's `plugin.json`, a `load-gen`, a `cli` query helper, plus Terraform,
Helm (per-env overlays), a Harness pipeline, and a full local loop on MinIO with
no cloud credentials. Its `docs/design.md` covers goals, architecture, schema,
skill derivation, privacy, auth, error handling, and open questions. This is the
more complete of the two mechanisms and is metadata-only by default.

**Standup direction (2026-07-22).** Revive the telemetry effort framed as
capture + privacy + technical feasibility; prefer a flexible, swappable store
(Databricks is a candidate but do not optimize for it); settle failure modes
explicitly; watch for sensitive-data capture and operational overhead; aim for
MVP alignment by end of week and brief stakeholders (Robin, Hiro).

## Proposal

Adopt **`catalyst-otel` (native Copilot OTLP → Rust receiver → S3 → Delta) as
the telemetry backbone.** The detailed engineering spec is the `catalyst-otel`
`docs/design.md`; this RFD records the decision and the cross-team commitments.

### Capture path

VS Code Copilot is configured (via distributed workspace/user settings) to
export OTLP over HTTPS to an internal receiver with a shared bearer token.
`captureContent` stays `false`. No per-skill `SKILL.md` change is required —
attribution is derived downstream, so the ~100 skills need no instrumentation.

**Scope: skills, not all tools.** Attribution targets *skill usage* — the ~100
Catalyst skills plus a user's own custom/third-party skills. Because we ride
Copilot's native OTLP emission, the raw stream inevitably contains non-skill
tool spans (`read_file`, `grep_search`, `run_in_terminal`, …); we cannot filter
those at source, but they are **incidental noise, not a capture goal** — not
attributed, not reported on, and dropped entirely by the local hook fallback
(see The hook's role). An earlier draft of this RFD proposed retaining *every*
tool call and slash command as first-class product scope; that was **rejected**.
In a typical session non-skill tools are the overwhelming majority of fires,
they carry no skill attribution, and treating them as signal would bury the
adoption metric in noise (and, for the local hook, grow the log without bound,
forcing rotation we'd rather not own). Custom/third-party skills *are* in scope:
custom-skill usage is itself a signal about unmet demand. All of this stays
metadata-only (names, not content).

### Skill attribution

`catalyst_skill_id` is derived in the transformer's silver step from a registry
generated off `plugin.json`, using two precedence-ordered rules:

1. **Slash-command match**, session-scoped (`/dplc-design`, `/data-contract`, …)
   — visible even with content capture off, because slash commands are explicit
   IDE actions, not free-text.
2. **Output-filename match**, span-scoped (a write tool whose basename matches a
   registry `output_filename_pattern`).

Unmatched spans get a `null` `catalyst_skill_id`. The unmatched percentage is a
useful health metric — a rising rate for *skill-shaped* spans tells us the
registry is stale (a skill we ship stopped matching) — but non-skill tool spans
are expected to dominate the unmatched bucket and are not themselves a reporting
target.

**Id canonicalization across the two mechanisms.** The `skill-registry` codegen
derives `skill_id` from the directory basename in `plugin.json`, verbatim.
Catalyst skill directories are lowercase-kebab by convention, so the ids the
local hook emits (lowercased) join the registry directly and no reconciliation
step is needed. The two vocabularies diverge in exactly one place, deliberately:
custom/third-party skills are not in `plugin.json` and therefore never join the
registry. They remain local-only signal, tagged `custom_skill_md` so they are
distinguishable rather than silently swelling the unmatched bucket. If the
convention ever admits mixed-case skill directories, the registry side must
lowercase too or the join fragments — a constraint worth asserting in the
codegen rather than discovering in a dashboard.

### Failure-handling posture (the questions the team asked to settle)

- **Fail open, never lose silently.** Client side: the OTLP export is
  fire-and-forget with a hard latency cap and must never block the agent; a
  local append-only log is always written first so an unreachable receiver is a
  non-issue for data retention. Server side: the receiver retries with backoff,
  spills to a PVC when S3 is unreachable, fails `readyz` so the load balancer
  drains it, and **never returns 2xx if it has lost the data**.
- **Silent to the user, loud to operators.** A telemetry failure must not
  surface to the person using Catalyst. It must surface to us via metrics
  (`flush_failures_total`, `pvc_overflow_bytes`, watermark lag) and the
  operator "loop" dashboard.
- **Breaks are recoverable, not fatal.** Bronze/silver are reproducible from raw
  within the 30-day retention window; the watermark only advances after all
  writes succeed, so a failed run re-processes rather than drops.
- **"Fail open" has to be tested, not asserted.** The hook's never-block
  guarantee was already false in a narrow case: a hook payload that parsed as
  valid JSON but was not an object (a top-level array) raised before the hook
  could print `{"continue": true}`, so the agent got no continue signal at all.
  It was caught by a test written for the review of #414, not in use — the
  failure is invisible precisely because a telemetry hook is supposed to be
  silent. Both client-side guarantees this RFD makes (never block, never lose
  silently) therefore carry an explicit test obligation: the packaged hook has
  offline contract tests covering malformed input, unwritable log targets, and
  the over-capture cases above, and the receiver's equivalents belong in its
  own suite.

### Privacy posture

Metadata-only in v1: model name, token counts, durations, tool names,
basename-only file paths (full paths dropped at bronze), and Catalyst +
custom/third-party skill names (metadata, not content). Capturing custom-skill
names is a deliberate scope choice — it's a demand signal — but it widens
collection to names a user chose, so if the privacy review flags custom-skill
names as sensitive the fallback is to hash or bucket the non-Catalyst skill ids
rather than drop them. Content capture is
out of scope and off by rollout; enabling it later is a separate proposal
gated on GRC/legal review, landing in a separate, access-restricted Delta table.
The identity question — whether we need the GitHub username (PII) or an
anonymous/hashed id is sufficient for adoption metrics — is decided here as
**metadata-only default; drop the `gh api user` username capture from the hook**
unless a named need survives the privacy review.

Two precisions on what "metadata-only" means for the local hook, so the claim
survives audit. First, "never records `tool_input` values" is not literally
true and should not be written that way: the skill id is *derived from* a
`tool_input` path, and for a custom skill that id is a directory name the user
chose — which may be a project codename. That single derived value is the only
`tool_input`-descended field written, and it is the same value the custom-skill
hashing fallback above already contemplates. Second, the local record includes
`cwd`, a full filesystem path that can embed a username or client name. That is
acceptable while the log stays on the developer's machine, but it is **not**
acceptable to forward as-is; any future tailer must drop or basename `cwd`
before shipping, matching the "full paths dropped at bronze" rule the pipeline
already applies.

### The hook's role

The native-OTLP pipeline supersedes the hook as the primary mechanism. The hook
is not deleted: it is repositioned as (a) a zero-infra local fallback for
developers, and (b) the reference for path-based attribution. Its hardened
implementation lands in **PR #414**.

Consistent with the skills-only scope above, the packaged hook records a fire
only when **both** conditions hold: `tool_name` is a read-like tool, *and* a
`tool_input` path resolves to a skill. The read gate is the load-bearing half.
An earlier revision keyed attribution off any skill-shaped string anywhere in
`tool_input`, which meant a `run_in_terminal` running `cat skills/foo/SKILL.md`
— or a file write whose *contents* quoted a skill path — was logged as skill
usage. That is the same class of false positive `catalyst-otel` had already hit
and solved: its `pivots.sql` keeps a hand-curated allowlist explicitly "to
avoid filename false positives," and models mentions (`v_leakage`) as a
*separate view* from real invocations (`v_invocations`). The hook now follows
that split rather than re-deriving the mistake — mentioning a skill is not
using it. Because gating on a tool name is itself a silent-failure risk (a
Copilot rename would zero the signal), the list is overridable via
`CATALYST_SKILL_READ_TOOLS`, and a sudden drop to zero is documented as this
failure mode until ruled out.

Attribution requires a **skill root**, and each record carries the rule that
matched (`catalyst_skill_md`, `catalyst_dir`, `custom_skill_md`) so consumers
filter by confidence rather than trusting every match equally — the local
parallel to the pipeline's `skill_match_rule` column. Without that discipline a
nested `/skills/foo/reference/SKILL.md` minted a phantom skill named
`reference`, a bare `/skills/SKILL.md` minted one named `skills`, and an
ordinary `design/skill.md` doc minted one named `design`. Phantom ids are worse
than missing ones: they pollute the registry-staleness metric this RFD relies
on as a health signal, because they look exactly like a skill that stopped
matching.

**PR #145's OTLP-push scope is paused** in favor of the receiver; its review
fixes (Windows portability, `daemon=True` + flush-before-join, drop username
capture) are folded into the hook's local-only path. We do not run two competing
push paths.

### MVP for end-of-week alignment

Local + dev-cluster receiver landing raw Parquet and the bronze/silver Delta
tables, queryable via the `cli` and Databricks SQL, with the loop dashboard.
Gold-to-Delta persistence, per-user JWT, and content capture are explicitly
deferred.

## Alternatives

- **PreToolUse hook as the backbone (PR #145).** Zero infrastructure, but
  per-OS fragility, activation ≠ enactment (~90% fidelity), a Preview platform
  dependency (`chat.useClaudeHooks`), and it re-derives signal Copilot already
  emits cleanly over OTLP. The OS fragility is not hypothetical and not
  confined to #145's `os.uname()` call: the attribution regexes themselves
  anchored on `/`, so on Windows — a primary VS Code Copilot platform — a
  native path like `C:\Users\me\skills\data-contract\SKILL.md` matched nothing
  and the hook recorded **zero** skill usage. It failed the way client-side
  capture always fails, by under-reporting silently rather than erroring, and
  was found by inspection during the #414 review rather than by anyone noticing
  missing data. Fixed there by normalizing separators, but the pattern is the
  argument: a mechanism whose failure mode is an empty dataset is a poor
  backbone for a metric we intend to make investment decisions on. Kept as a
  local fallback, not the backbone.
- **VS Code extension (PR #97, closed).** Registered each skill as a tool for
  OTLP telemetry. Higher attack surface, extension-lifecycle maintenance, and
  per-release sideload review. Superseded by riding Copilot's own
  `chat.useAgentSkills` path; preserved on `feat/vscode-extension`.
- **Reuse platform API token-usage data.** No skill attribution and no
  per-skill breakdown. Being checked out-of-band, but insufficient on its own.
- **Databricks/Spark-native ingestion.** Higher compute cost and couples the
  capture path to Databricks. Rejected in favor of Rust + DataFusion + delta-rs,
  which keeps compute cheap and the store swappable (S3/Delta, local MinIO loop),
  while still queryable from Databricks SQL.

## Impact

**Who is affected.** The Catalyst working group (consumers of the metrics); each
Catalyst user (a one-time settings/token addition, no per-skill change);
whoever operates the receiver/transformer on EKS.

**Infrastructure.** Requires a CG ECR mirror and EKS cluster, an S3 bucket per
environment with a 30-day raw lifecycle rule, IRSA roles for receiver and
transformer, a receiver token in AWS Secrets Manager via External Secrets, and
a Unity Catalog schema (`catalyst_otel.*`) with grants scoped to the working
group. The specific ECR/EKS targets, bucket-naming convention, UC name and
grants policy, and transformer cadence (15 min is a placeholder) are to be
confirmed with the infra team during discussion. CI system (GitHub Actions vs
Harness) is governed by RFD 0004 and should align with it.

**Rollout / migration.** Distribute Copilot OTLP settings and the bearer token
via settings sync or a setup step (dovetails with the `setup-workspace` skill,
AICAT-278). Migrating off the hook: keep the local JSONL path, retire the
in-flight OTLP-push scope in PR #145, and adopt the review fixes on the
local-only path (landed in #414, which also adds the contract tests that keep
the fail-open and skills-only guarantees honest). Per-user JWT replaces the
shared token before any broad (beyond-working-group) rollout — until then
attribution trusts Copilot's `user.id` attribute, which is already a bronze
column, so the schema is forward-compatible.

**Operational.** Both services expose Prometheus metrics and JSON logs; the
first dashboard is the operator loop (flush rate, transformer success, watermark
lag, unmatched-skill percentage). Known v1 simplifications to accept or fix
before wider use: gold aggregates are computed but not yet persisted to Delta;
the watermark is a single lexicographic key (late-arriving partitions can be
skipped under multi-pod deployment); the `preStop` hook is a timed sleep rather
than a flush trigger; JSON OTLP attribute decoding drops non-string types.

**Decision point.** Team alignment on this MVP by end of week; brief Robin and
Hiro on direction and outcome. Tracked in AICAT-276 (RFD), with AICAT-162
(epic), AICAT-148 (hook expansion), and AICAT-219 (OTEL for Copilot sessions).
