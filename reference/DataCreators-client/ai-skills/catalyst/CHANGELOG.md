## [Unreleased]

## 2026-09-23 — v1.13.0

**Catalyst finally checks whether you can actually build anything — and starts measuring whether any of it gets used.** Three themes in one release. The entry point gains a guided path for new or unsure users and, for the first time, knows something about the platform it sits in front of: `/dplc-preflight` detects which Databricks workspace you are pointed at, which others you have, whether you actually have access, and where your product would go, before you author a single artifact. Usage reporting becomes self-serve on both harnesses, and per-skill attribution — which Claude Code redacts for marketplace installs — is recovered rather than given up on. And Catalyst now installs as a Claude Code plugin marketplace, not just a folder of files.

Along the way, blockers that stopped new users cold: `pip install -r skills/requirements.txt` installed *nothing*, the only skill that verified platform access called three functions that did not exist, and `.vscode/settings.json` had pointed at a directory layout deleted four months earlier.

106 skills (from 103), 134 behavior cases (from 124). Three RFDs move state.

### New: Catalyst installs as a Claude Code plugin marketplace (PR #438)

The repo now ships `.claude-plugin/marketplace.json` and `plugin.json`, so Catalyst is added with `/plugin marketplace add cg-open-itg/catalyst` rather than by copying a directory. Version metadata is generated from `plugin.json` by `scripts/sync_plugin_version.py` — `marketplace.json` is never hand-edited — and `.githooks/pre-commit` keeps the two in step.

_Thanks to @AGGB_capgroup for this contribution._

### New: usage reporting that sets itself up (PR #439, PR #441, PR #443)

Catalyst can now answer "is anyone using this?", on both harnesses, without anyone filing a ticket.

- **`/dplc-concierge` configures Copilot Chat reporting** and verifies it, instead of pointing at a wiki page. It writes the four `github.copilot.chat.otel.*` keys plus `resourceAttributes.user.id` — without which the exporter works and every report is anonymous.
- **`/dplc-preflight` reports whether reporting is on, and whether it is *safe*** — question 5 for Copilot Chat, 5b for Claude Code. Advisory by contract: telemetry is not a prerequisite for building a data product, so a machine with reporting off is still `READY`. It is reported because there is no confirmation anywhere in the VS Code UI, by design, so a machine that has never reported looks identical to one reporting correctly.
- **Background checks** — a quiet once-per-session pass for the failures that surface as a cryptic error halfway through a task rather than as a setup problem at the start: credential liveness, tool-version drift, identity agreement. Silent when clean, advisory always, suppressed for eight hours by a marker so it never nags.

**Metrics only, and that is the whole privacy design.** Catalyst points *only* the metrics signal at its collector. Prompts, assistant responses, tool content and command lines are only ever emitted as **log records** — never metric attributes — so a metrics-only destination is *structurally* incapable of receiving conversation text. Not "configured not to": incapable, because the signal that carries content is not sent there at all. That guarantee survives someone later turning a content switch on, which a policy of four zeroes would not. The published fragment therefore sets none of `OTEL_LOG_USER_PROMPTS` / `_ASSISTANT_RESPONSES` / `_TOOL_CONTENT` / `_RAW_API_BODIES` — those are the enterprise's call, not Catalyst's.

Verified three ways: the collector holds 992 log rows and **zero** mention Claude Code; the managed policy sets `OTEL_LOG_USER_PROMPTS=1` with no logs endpoint, so it falls back to `127.0.0.1:4318` and is refused; and a hand-built OTLP payload was POSTed and read back out of S3 with its attributes intact.

**Per-skill attribution is recovered, not abandoned.** An earlier claim in this repo held that `skill.name` reaches the collector verbatim. Measured three times — a directory marketplace, a GitHub marketplace, and this repo's own skills — it does **not**: `skill.name` and `plugin.name` are both replaced with `"third-party"` and `marketplace.name` is absent entirely. Since PR #438 Catalyst *is* a marketplace, so the distribution path decided whether a skill was nameable at all. `scripts/emit_skill_usage.py` closes that by reading the session transcript, where the skill is a named field rather than an inference, and emitting `catalyst.skill.invocation` with `catalyst.skill` and `catalyst.plugin` — deliberately namespaced so they can never be confused with Claude Code's redacted attributes — and `session.id` left un-namespaced because it is the join key. It never reads `input.args`, which is user text; two tests seed a secret and assert it reaches neither the payload nor the state file. The incorrect claim is recorded in AICAT-339 rather than quietly deleted.

_Thanks to @KXY_capgroup and @RBLW_capgroup for the telemetry work this builds on._

### New: `/astronomer-update-base-deployment` (PR #436)

Updates an Astronomer base deployment. Apply requires an explicit opt-in rather than defaulting to act.

_Thanks to @MSTP_capgroup for this contribution._

### Docs: onboarding that survives a clean checkout (PR #434, PR #437)

- **Getting Started FAQ** (`docs/getting-started-faq.html`), published to the docs site and mirrored to Confluence by `scripts/publish_faq_to_confluence.py` — which converts rather than uploads, since Confluence storage format drops `<style>`, `class` and inline `style` and renders callouts through its own macros.
- **A guide for turning on Copilot Chat usage reporting** (`docs/catalyst-otel-getting-started.md`) — five minutes, one settings file, no software to install, and honest about the one caveat still under investigation.
- Two things that made a clean checkout look broken are fixed.


### RFDs

- **RFD 0024: Agents + Skills — a portable DPLC harness** is `published` (PR #429). Catalyst is a skills-only harness today: every unit is a `SKILL.md` describing *what* to do, and nothing describes *who* does it, *which model* they run on, or *what they are allowed to touch*. 0024 proposes `agents/<name>.md` as a first-class contract with the runtime adapters generated from it, and lands eight open questions rather than pretending they are settled.
- **RFD 0022: Catalog Topology, Access Model, and Read Routing** is `published` (PR #416). Answers three questions that had no shared answer: which Unity Catalog catalog a new data product goes in (today that needs a synchronous decision with the platform team), who may read and write a given catalog and at what grain (access is granted per-product rather than per-tier, so the same privilege shape differs across domains), and whether a consumer should read from the lakehouse or straight from the Book of Record. Enumerating concrete integration patterns is explicitly out of scope.
- **RFD 0021: Catalyst Skill-Usage Telemetry** is `abandoned` (PR #410), superseded by the native-OTLP pipeline above. Kept for the historical record per RFD 0001.

_Thanks to @CPTS_capgroup for RFD 0022._

### Removed: the VS Code skill-telemetry hook

The `PreToolUse` hook shipped in PR #107 is gone: `scripts/hooks/skill-telemetry.py`,
`scripts/hooks/install-skill-hooks.sh` and `docs/skill-telemetry-hooks.md` are all deleted.
Two reasons, and the second is the decisive one.

**One mechanism per question.** Claude Code reports skill use natively — `skill.name`,
`agent.name`, `plugin.name` and `marketplace.name` are unconditional attributes on the
`cost.usage` and `token.usage` metrics, needing no hook, no installer and no content switch.
Keeping a second, differently-shaped source for the same question means two numbers that
disagree and no way to say which is right.

**The hook's premise no longer holds.** It inferred the skill by regexing
`skills/<name>/SKILL.md` out of a `read_file` tool call. Its own documentation listed the
failure mode: *"If Copilot later changes `chat.useAgentSkills` to inject skill content
directly into the agent's system prompt without a `read_file`, hooks won't see it."* That is
now what happens. Across 274 trace payloads in the dev collector, every skill path appears in
`gen_ai.system_instructions` — the injected catalogue, present identically on every chat span —
and **no `read_file` span carries a `SKILL.md` path at all**. The signal the hook keys on is
not being produced.

It was also never a reporting path in the sense people assumed. The hook had no network code:
it appended to `~/.catalyst/skill-use.jsonl` and stopped, and the repo deliberately shipped no
sink. So nothing is lost from the collector by removing it, because nothing ever arrived from it.

**If you installed it, uninstall it** — deleting the repo files does not stop a hook already
registered on your machine, and an orphaned hook is exactly the duplicate path this removal is
meant to end:

```sh
python3 - <<'EOF'
import json, pathlib
d = pathlib.Path.home() / ".copilot/hooks"
(d / "skill-telemetry.py").unlink(missing_ok=True)
f = d / "hooks.json"
if f.exists():
    cfg = json.loads(f.read_text())
    pre = cfg.get("hooks", {}).get("PreToolUse", [])
    kept = [h for h in pre if not str(h.get("command", "")).endswith("skill-telemetry.py")]
    if kept: cfg["hooks"]["PreToolUse"] = kept
    else: cfg.get("hooks", {}).pop("PreToolUse", None)
    if cfg.get("hooks"): f.write_text(json.dumps(cfg, indent=2) + "\n")
    else: f.unlink()
EOF
```

**Why not `rm`.** An earlier revision of this note said
`rm -rf ~/.copilot/hooks/skill-telemetry.py ~/.copilot/hooks/hooks.json`.
`hooks.json` is Copilot's per-user hooks file, not Catalyst's, and the installer
**skipped writing it when it already existed** (`install-skill-hooks.sh`:
`skip: $DEST_HOOKS_JSON already exists`) -- so the users most likely to have other
hooks in that file were exactly the ones the `rm` would have wiped. The snippet
above removes only our `PreToolUse` entry, and deletes the file only when nothing
else is left. Caught in review by @CONNMS_capgroup; verified against
Catalyst-only, mixed, user-only and nothing-installed states.

Then remove `chat.useClaudeHooks` and the `chat.hookFilesLocations` entry from your VS Code
User `settings.json` and reload the window. Leave `chat.useAgentSkills` alone — that is
Copilot's own skill loading, not ours. `~/.catalyst/skill-use.jsonl` is yours to keep or
delete; nothing reads it.

Per-skill attribution for VS Code Copilot Chat is consequently **not currently collected**.
That is a known gap rather than an oversight, tracked in AICAT-335, and the native
`gen_ai.*` span attributes are the place to solve it if it is worth solving.

The removed work is recoverable from git history if hooks turn out to be needed again.

### New: `/dplc-preflight` — the zero-to-one gate

Answers the four questions new Data Product Creators most often cannot answer themselves, by detecting rather than asking:

1. Can I run Catalyst at all? 2. Which Databricks workspace am I pointed at, and which others are configured? 3. Do I actually have access? 4. Where would my data product go?

- **Works on a machine where nothing is installed yet** — that is the point of a pre-flight. The toolchain probe is standard-library only, workspace discovery reads `~/.databrickscfg` directly, and every Databricks import sits behind a guard. A missing dependency is a finding to report, never a traceback.
- **Exit codes route to the owning skill** — 2 → `/setup-workspace`, 3 → `/databricks-config`, 5 → `/configure-sql-warehouse`. Exit 4 (authenticated but no catalogs visible) is called out as an **entitlement gap, not a setup gap**, so users are not looped through setup skills for something no local fix resolves.
- **Surfaces the PAT trap.** `docs/install.md` tells new users to set `DATABRICKS_TOKEN`; `connect-databricks` refuses PATs per DBX-SEC-002 and exits 3. Preflight reports the collision explicitly instead of letting users hit it opaquely later. The underlying policy inconsistency is tracked separately.
- **Read-only.** Probes and reports; never installs, authenticates, or mutates `~/.databrickscfg`. Reports which auth *style* a profile uses, never a secret. Caches to `.catalyst-env.yml` so downstream skills stop re-asking.

### Changed: `/dplc-concierge` — two paths instead of one

- **Guided path** for new or unsure users: asks in plain words what they want to build (never "which phase"), offers orientation without forcing it, **checks the environment before handing off**, and moves one step at a time. Unclear intent now routes here instead of asking a clarifying question made entirely of lifecycle jargon.
- **Fast path stays fast.** Brevity is correct for someone who knows what they want; `case-05-fast-path-stays-fast` is the regression guard against over-correcting.
- **The concierge now knows the platform exists.** It previously never mentioned Databricks and had no route for "which workspace should I use" — it now routes environment questions to `dplc-preflight`, `setup-workspace`, and `databricks-config`.
- **Resume detection de-duplicated.** The concierge and `dplc-design-stage` kept separate, disagreeing tables, so a user who finished Phase 0 was told "starting at Phase 0" by one and "Phase 1" by the other. Both now share one table and one search precedence (`$DPLC_DIR`, `./.dplc/`, `./docs/.dplc/`, repo root) matching `/build-preflight`. Gained `Glob` so the scan can actually enumerate a directory.
- Behavior cases go from 1 to 5.

_Thanks to @NKV_capgroup, who originated the guided onboarding and the `/dplc-preflight` gate in PR #427._

### New: `/setup-workspace` — machine-level setup

Prepares a local machine to run Catalyst: ensures Python 3.13 through a package manager that is already present, points pip at cgrepo, installs dependencies, and offers `git`/`gh`. Never installs a package manager, never runs a `curl | bash` installer, never overwrites `pip.conf` without a timestamped backup. Guides instead of installing when no sanctioned path exists.

_Thanks to @SMRDLP_capgroup for this contribution._

### Fixed

- **`pip install -r skills/requirements.txt` installed nothing** — the command in `docs/install.md`. The pin `databricks-cli>=0.218.0,<1.0.0` asked PyPI for a version scheme belonging to the **Go** CLI (v0.2xx); the PyPI package of that name is the deprecated legacy Python CLI and stops at **0.18.0**. Because pip fails the whole transaction rather than one line, every dependency silently failed to install. The range stays in the file as a comment (`/build-preflight` greps it for drift detection) with a test asserting both halves of that contract.
- **`/build-preflight`'s access checks called functions that did not exist** — Step 5 instructed the agent to import `check_catalog_access`, `check_schema_grants`, and `check_volume_exists` from `unity_catalog`; none were implemented, so the readiness routine raised `ImportError` and the agent improvised. Now implemented in `unity_catalog/readiness.py`, where a permission failure is an **answer** (`False`), not an exception. Accepts `CREATE TABLE` or `CREATE_TABLE`, and both `/Volumes/c/s/v` and `c.s.v` volume forms.
- **The client package could not be imported at all** — `sqlglot` is imported at module scope by `databricks_tools_core/sql/sql_utils/dependency_analyzer.py`, which `unity_catalog` pulls in transitively, but was never pinned. Two `test_submodule_imports` cases were failing as a result.
- **`plugin.json` admitted a Python that cannot work** — declared `>=3.9` while `docs/install.md` documents 3.9 as incompatible (past EOL; `markitdown` ships no 3.9 wheels). Now `>=3.10`, so the gate fails at install time rather than confusingly at dependency resolution.
- **`dplc-build-stage` told itself to use a tool it had not declared** — its artifact fallback instructs `Glob`/`Read` while `allowed-tools` listed only `Read Grep`, so the check silently could not run. `Glob` added.
- **`.vscode/settings.json` named a directory layout deleted in April, in the wrong shape.** `chat.agentSkillsLocations` pointed at `skills/concierge`, `skills/orchestrators`, `skills/execution` and `skills/document` — a nesting the four-tier refactor flattened to `skills/<name>/SKILL.md` (PR #31, 2026-04-30) — and the setting had not been touched since PR #14 introduced it. So the **folder-locator** path resolved none of the four, and no folder-located skill reached the VS Code surface for roughly four months, silently: there is no error, the skills simply never appear.

  Now `{"skills": true}`, an **object map**, which is the shape the setting is registered with. An array is not merely unidiomatic here, it is inert — the reader guards on `!Array.isArray(...)` and then requires each value to be exactly `true`, so `["skills"]` resolves to no paths at all and, because a workspace value is present, suppresses the six built-in defaults rather than merging with them. Caught in review by @CONNMS_capgroup against the shipped bundle, and confirmed here in `extensions/copilot/dist/extension.js`. Glob metacharacters are rejected by the schema's `propertyNames` pattern, so a bare directory is the only workable form.

  Scoped deliberately: this governs folder-located skills only. Plugin-contributed skills — how `docs/install.md` Path A and Path B both install Catalyst — are read on a separate code path that never consults this setting, so anyone following the documented install was unaffected. The mirror-image fault on the Claude Code side was different again: the plugin declared itself enabled in `.claude/settings.json` but never appeared in `~/.claude/plugins/installed_plugins.json`, because project-scope enablement does not auto-install.

### Fixed in review

- **`/setup-workspace` disabled TLS verification for cgrepo.** `ensure_pip_cgrepo` wrote `trusted-host = cgrepo-aws.capgroup.com` alongside the index URL, which would have silently removed certificate validation for the one host all corporate installs flow through — hardening the supply chain at the registry while opening it at the transport. `docs/install.md` documents `index-url` and nothing else. The line is gone; a new `verify_cgrepo_tls()` probes the certificate against the system trust store and, on failure, names `cert = <corporate CA bundle>` as the fix (which keeps the connection verified) rather than turning verification off.
- **`/setup-workspace` wrote the wrong pip config path, and overwrote it wholesale.** `_pip_conf_path()` returned `~/.config/pip/pip.conf` while `install.md` documents `~/.pip/pip.conf`, so a user who followed the docs had their real config neither inspected nor backed up — and gained a second competing config. `path.write_text()` also destroyed every other key: `cert`, `proxy`, `extra-index-url`, `timeout`. Now a `configparser` read-modify-write that sets `index-url` only, merges into whichever documented config already exists, and refuses (rather than guesses) on a malformed file.
- **`/dplc-preflight` reported a failed lookup as an entitlement gap.** A transient 5xx, a token expiring mid-run, or a network blip left the catalog list empty, which yielded exit 4 — whose remediation tells the user to go request Unity Catalog access they may already hold. The exception text was captured and then never printed, and the warehouse error was overwritten by the catalog one. Errors are now tracked separately, surfaced in the report as `LOOKUP FAILED`, cached in `.catalyst-env.yml`, and given a distinct exit code **6** that outranks both 4 and 5.
- **`/dplc-preflight` could mark the wrong profile active** — it defaulted `profile` to `DEFAULT` whenever `DATABRICKS_CONFIG_PROFILE` was unset, so a host resolved from `DATABRICKS_HOST` printed `<- active` beside a `DEFAULT` profile whose host contradicted the `Host:` line above it.
- **`/build-preflight` prescribed an install this release proves is impossible** — it suggested `pip install 'databricks-cli<1.0.0'` and read the version from Python dist metadata. It now reads `databricks --version` from the Go binary and explains why the PyPI package is a different artifact on a different version scheme.
- **`.catalyst-env.yml` and `.catalyst-build.yml` are now gitignored** — the former records the user's email, workspace host, profile names, and catalog names, one `git add -A` from being committed in a product repo.
- Dead `_run()` helper and its `subprocess` import removed from `preflight.py`; `check` no longer advertises a package manager that `tool` will refuse to use; catalog and warehouse listings bound with `islice` instead of paginating fully and discarding; the `requirements.txt` core/extras boundary anchored to `# Tested-against` at line start rather than a bare substring anywhere in a line.

### Fixed in review — round two (PR #444, #445, #446, #447, #449, #450, #451)

Most of these are tests that could not fail, which is the class this release spent the most effort on.

- **The vendored Databricks client reported a version upstream never shipped.** `identity._load_version()` walks up from its own directory, so a repo-root `VERSION` generated from `plugin.json` made every SDK call send `databricks-ai-dev-kit/1.12.0` in the User-Agent that lands in `system.access.audit` — Catalyst's release number stamped onto a third party's software, renumbered every release. The file now lives *inside* the package at its own `0.1.0`, found at hop 0 of the search, and the release process is untouched. Worth separating what shipped from what did not: the repo-root `VERSION` was reverted before merge, so no release ever attributed calls to `1.12.0` — but at v1.12.0 no `VERSION` existed anywhere the client could find, so every SDK call did report `databricks-ai-dev-kit/0.0.0-unknown`. That part was real and is what this fixes.
- **Ten mutation-tested defects in the preflight suite.** Pinning `in_coder_workspace` for determinism removed the only coverage of it: replacing its whole body with `return True` **or** `return False` left all 231 tests green. Also uncovered: the third term of the `/s/<source>` gate (flagging *every* Coder endpoint was green), `cmd_otel`'s note loop (deleting it failed nothing), and both ends of the advisory gate. The probes are now pinned by a module-level autouse fixture *and* covered at their boundary, so the seam is deterministic and the function is still tested.
- **A guard against environment-dependence that was itself environment-dependent.** Its "ambient" side used `monkeypatch.setenv` before a call that swaps `os.environ` wholesale, so the setenv silently no-opped; it appeared to work only because this machine has `/etc/claude-code/managed-settings.json`. On a laptop it passed with the pin removed.
- **A stale-path guard that could not see the repo's own dominant spelling.** `_SKILL_PATH_RE` required a double quote, so all 136 unquoted YAML behavior cases were invisible: `.json` 19 files / 106 refs matched, `.yaml` 138 / **0**. Now parsed rather than pattern-matched, and `test_every_format_family_actually_yields_paths` asserts per format family — because the prior sanity check counted *files*, which 19 JSON files satisfied on their own while the YAML half contributed nothing.
- **A behavior rubric that passed an answer recommending public PyPI.** `setup-workspace/case-01` weighted `keeps_the_index_url` at 0.05 against a 0.8 threshold, so zeroing it still scored 0.95. Rebalanced so every substantive criterion is individually decisive. The general defect — the 0.70 default threshold makes per-criterion decisiveness arithmetically impossible above three criteria, affecting 102 of 114 cases including `no_hardcoded_credentials` — is tracked in AICAT-344.
- **RFD 0024 landed still declaring `state: discussion`,** so its state pointed at a closed PR, and §2 contradicted itself eighteen lines apart about whether a config file belongs. Both fixed, and `tests/ci/test_rfd_state_consistency.py` now makes the first unrepeatable: a landed RFD may not claim `discussion`, its state must be one RFD 0001 defines, and the frontmatter must agree with the index row.
- Preflight reads `gh`'s active account per host rather than trusting JSON key order; the OTEL check accepts either Catalyst collector rather than production alone; four dead skill paths left by the `.vscode` fix are removed.

### Known issues

- `tests/behavior/tests/test_claude_agent.py::TestOptionsAssembly::test_all_bounds_present_in_options` fails on `main` and on this release. Pre-existing and unrelated to this work — confirmed identical with the release diff stashed.
- Nine Databricks-SDK import failures and three `test_connect_databricks_oauth` collection errors appear on machines without the optional SDK extras installed. Also pre-existing.

_Thanks to @CONNMS_capgroup and @NKV_capgroup for the review work on this release. Between them they found the `.vscode` array-vs-object inertness, the ten surviving mutants in the preflight suite, the audit-attribution defect in the vendored client, the rubric-weighting defect now tracked as AICAT-344, and the reachability defect in the RFD state guard — most of which were tests that could not fail, and none of which a linter would have caught._

---

## 2026-08-11 — v1.12.0

**Data quality control planning lands in Phase 3 Design.** The new `/data-quality-controls-plan` skill turns profiling findings and business requirements into a short, enforceable set of DQ controls — each mapped to a named EDGC rule pattern, given a monitoring action and a rationale, and expressed as a DQ Next (DQF) check that feeds the data contract. Alongside it, Catalyst gets its first browsable documentation site: an interactive map of all 103 skills, derived from the skills' own frontmatter and kept honest by the offline suite.

### New: `/data-quality-controls-plan` — DQ control planning in Phase 3 Design (AICAT-281, PR #415)

Reconciles the EDG `dq-control-planning` skill (cg-edo/edo-ai-skills **PR #119**) into Catalyst as a Phase-3 Design document leaf, aligned to the EDGC **DQ Rule Patterns Guidance** and feeding the data contract + DQF.

- **New `/data-quality-controls-plan`** (AICAT-282, AICAT-285) — proposes a focused, prioritised set of DQ controls from `data-profiling` findings + business requirements. Each control maps to a named **EDGC rule pattern**, a DQ dimension, a monitoring **action** (STOP / WARN / At-Rest) with a rationale, and a **DQ Next (DQF) check** — so it is enforceable. Deterministic patterns only; anti-proliferation by design (a rule with no action + rationale is not added). Reclassified the external orchestrator as a `document` leaf (Catalyst orchestrators only delegate) and wired into `/dplc-design` Step 4 (before the contract). Markdown-first.
- **`data-contract` §4 handoff** (AICAT-284) — the approved plan is codified into §4 (single source of truth) using the existing columns; the DQ dimension is carried in the rule description. §4's structure is unchanged.
- Behavior test: `data-quality-controls-plan/case-01-happy-path`.

_Thanks to ARVS, who authored the upstream `dq-control-planning` skill this reconciles, and to LQXA and NKV for the data quality contributions._

### New: interactive skills graph + documentation site (PR #420, PR #421)

Catalyst now publishes a browsable map of every skill, banded by DPLC lifecycle phase and wired by the dependencies each skill declares in its own frontmatter — 103 nodes, 237 edges.

- **`docs/skills-graph/`** — zero-dependency vanilla JS/SVG (no CDN, no npm, no build step, nothing to re-point at the internal mirrors). Filters by stage, tier, and edge type; search; hover/focus highlights a skill's neighbours; a detail panel walks dependencies in both directions; a table view for non-visual access.
- **Nothing is hand-maintained.** `scripts/build_skills_graph.py` derives `graph.json` from `SKILL.md` frontmatter, and `tests/ci/test_skills_graph.py` fails the offline suite if the committed copy drifts — naming the specific skill rather than emitting a 100-node diff.
- **`docs/` landing page** (PR #421) — an index page plus `.nojekyll`, so the docs render from the branch source. Replaces the short-lived publish workflow from PR #420, which never ran (repository Actions are disabled at the org level).

_Thanks to CONNMS for the skills graph contribution._

### Also shipped

- **`CONTRIBUTING.md` cookbook** (PR #419) — the repo's first root contribution guide, so GitHub renders the **Contributing** link next to the README. Covers scope, skill anatomy and the enforced frontmatter contract, step-by-steps for add / update / evolve-or-retire a skill, and the offline `pytest tests/ci tests/skills` gate. Adds a pre-submit checklist to the PR template. Documentation only (Catalyst dev team).
- **Release process documented end to end** (PR #413) — `docs/release-process.md` records versioning, annotated unprefixed tags, scoping from the last *published* tag, contributor credit, recovering a missed tag, and the `gh` REST-vs-GraphQL scope gotcha. Written after v1.10.0 was bumped and changelogged but never tagged. Documentation only (Catalyst dev team).

### Fixed

- Fork attribution and skill frontmatter now satisfy their contracts — added the missing `upstream-license` on three dbt forks, completed `dbt-unit-test`'s provenance triplet, and repaired frontmatter on the feedback skills. Cleared all 15 pre-existing offline-suite failures (PR #418). _Thanks to NKV._
- `skills/rfd-authoring` is registered in `plugin.json`, so `/rfd-authoring` loads (PR #418; supersedes PR #417). `plugin.json` now registers **103** skills.
- Renamed the `stdout_contains` structural check to `output_contains` — it was always passing the agent's text reply, never subprocess stdout — and it now fails cleanly on an empty, non-string, or absent value instead of passing vacuously or raising `TypeError` (AICAT-207, PR #406). _Thanks to SMRDLP._
- `data-quality-controls-plan` declared an external Confluence reference in `metadata.standards`, which binds to RFD 0008 rule IDs; the reference lives in the skill body instead (PR #423).

### Proposed (RFD 0019): DQ RACI/DQMS artifact & data-contract DQ Dimension column

Per the DG working session, two governance decisions from AICAT-281/283 are routed to discussion rather than shipped: whether a **DQ RACI/DQMS** stakeholder artifact belongs in the DPLC, and whether **`data-contract` §4 should carry a DQ Dimension column**. Drafted as `rfd/0019` (discussion); the proposed RACI artifact is carried there.

> **Follow-ups:** RFD 0009 (ODCS / Data Contract Standard) remains unwritten — RFD 0019's §4-dimension question should be resolved alongside it; `register-data-contract` would need a `dq_dimension` field only if that column is adopted.

### Upgrade / setup notes

- No breaking changes. `plugin.json` bumps to `1.12.0`; it now registers **103** skills (adds `data-quality-controls-plan` and `rfd-authoring`).
- `.github/plugin/marketplace.json` synced via `scripts/sync_plugin_version.py` (`--check` passes).
- **Behavior-case authors:** `stdout_contains` is renamed to `output_contains`. Any case YAML outside this repo still using the old name will now fail loudly with `Unknown structural check` rather than silently passing.
- No reinstall needed — reload the VS Code window or refresh the Agent Plugins panel.

---

## 2026-07-27 — v1.11.0

**dbt unit testing.** The new `/dbt-unit-test` skill generates unit tests for a dbt model — mocking upstream inputs and asserting expected outputs — so builders can cover model logic without hand-writing fixtures. It is the practical companion to the tiered testing strategy ratified in RFD 0018 (v1.10.0), landing test generation directly in the Phase 4 build loop.

### New: `/dbt-unit-test` skill — generate unit tests for dbt models (PR #389)

Analyzes a dbt model and generates a unit-test suite for it, so model logic is covered without hand-writing fixtures.

- Inspects the model's SQL and upstream `ref()` / `source()` dependencies to synthesize input fixtures and expected results
- Emits pytest-based tests via a self-contained generation engine under `scripts/engine/`
- Registered in `plugin.json` (101 marketplace skills); ships a `case-01-trigger` behavior test

_Thanks to @AGGB_capgroup for this contribution._

### Also shipped

- **All ratified RFDs published on `main`** (PR #407) — every accepted RFD is now rendered on `main`, with author initials normalized to uppercase. Documentation/governance only (Catalyst dev team).

### Upgrade / setup notes

- No breaking changes. `plugin.json` bumps to `1.11.0`; it now registers 101 skills (adds `dbt-unit-test`).
- `.github/plugin/marketplace.json` synced via `scripts/sync_plugin_version.py` (`--check` passes).
- No reinstall needed — reload the VS Code window or refresh the Agent Plugins panel.

---

## 2026-07-13 — v1.10.0

**Local Airflow orchestration plus two ratified pipeline standards.** The new `/deploy-airflow-local` skill extends the Phase 4 (Build) inner loop from Databricks bundles to Airflow, letting you stand up a DAG locally with `astro dev start` without leaving Copilot Chat. Alongside it, RFD 0018 (Testing Strategy) and the RFD 0008 containerization language guide land as published standards, and a contributor-facing `rfd-authoring` skill makes authoring new RFDs repeatable.

### New: `/deploy-airflow-local` skill — local Airflow deploy (PR #394)

The Airflow counterpart to `/deploy-dab`. Runs a data product's DAG locally via `astro dev start` so you can iterate on orchestration in your own environment during the build inner loop.

- Stands up the local Astronomer/Airflow runtime and triggers the DAG for a single data product
- Complements the Phase 4 build loop (author → validate → deploy) with a local orchestration step
- **Scope boundary** — local dev only; the shared/remote Astronomer deploy action `/deploy-astro` (AICAT-169) remains a separate, in-progress skill
- Registered in `plugin.json` (100 marketplace skills); ships a `case-01-happy-path` behavior test

### Published: RFD 0018 — Testing Strategy for Data Pipelines (PR #132)

Ratifies a tiered testing strategy for data pipelines — unit, integration, and data-quality coverage — and maps each tier to the AI skills that produce it. Gives builders a single reference for what to test, at which layer, and with which Catalyst skill.

_Thanks to @DMRS_capgroup for this contribution._

### Standards: RFD 0008 — containerization language guide (PR #139)

Adds a containerization language guide to the RFD 0008 coding standards, including the requirement to source base images and packages from the internal mirrors (`cgregistry` / `cgrepo`) rather than public registries.

_Thanks to @GPLN_capgroup for this contribution._

### Also shipped

- **`rfd-authoring` skill** (PR #377) — a contributor-facing skill that scaffolds RFDs with correct frontmatter and structure. Not a marketplace/data-product skill (Catalyst dev team).

### Known limitations

- **Airflow deploy is local-only.** `/deploy-airflow-local` targets your own environment; the shared/remote Astronomer deploy (`/deploy-astro`, AICAT-169) is still in progress.
- **Phases 7 (Operate) & 8 (Evolve)** still have leaf skills but no GA phase orchestrator yet (epics AICAT-160 / AICAT-161).
- **Platform coverage** — validated primarily on macOS; Windows users may hit prerequisite gaps in some skills.

### Upgrade / setup notes

- No breaking changes. `plugin.json` gains `deploy-airflow-local` (100 registered skills); `rfd-authoring` ships as a repo-local contributor skill.
- `.github/plugin/marketplace.json` synced via `scripts/sync_plugin_version.py` (`--check` passes).
- No reinstall needed — reload the VS Code window or refresh the Agent Plugins panel.

---

## 2026-06-29 — v1.9.0

**GA release — end-to-end Data Product Lifecycle.** Every required phase to take a data product from intake through discovery, design, build, validate, and publish now has a live orchestrator, and the new `/deploy-dab` skill closes the Phase 4 build inner loop with a local Databricks Asset Bundle deploy.
- `/deploy-dab` adds the Phase 4 (Build) local deploy action — validate, deploy, and surface deployed-asset links for a single data product's bundle to the developer's own dev space (build → validate → deploy now runs entirely in Copilot Chat).
- RFD 0011 (Airflow DAG Standards) is published; `/generate-dag` and `/validate-dag` are aligned to the ratified rule set.
- Reliability and standards hardening: Confluence publishing fix, behavior-test harness `stdout_contains` check, RFD 0006 published, and `/validate-dbt` documentation polish.

### New: `/deploy-dab` skill — local Databricks Asset Bundle deploy (PR #390 — AICAT-167)

The Phase 4 (Build) deploy action that pairs with the `/validate-dbt` gate shipped in v1.8.0. Deploys a single data product's Databricks Asset Bundle to the **`local` target — the developer's own dev space** — during the build inner loop.

- **Two modes, routed on intent:** DEPLOY (default) and REMOVE / teardown (gated `--mode destroy`, explicit confirmation required)
- **DEPLOY flow** — checks the `/setup-databricks-asset-bundle` precursor, confirms the per-user target schema on first deploy, runs `databricks bundle validate --target local` then `databricks bundle deploy --target local`, and surfaces deployed-asset URLs (job, pipeline) from `databricks bundle summary`
- **Auth** — local target uses U2M (user OAuth via `databricks auth login`); M2M client-credentials (`connect-databricks`) remains the CI/shared path
- All deterministic work runs in `scripts/deploy.py`; the SKILL.md body conducts only the one interactive first-deploy schema confirmation
- Aligned with **DBX-BUNDLE-002** (single product per run) and **DBX-SEC-002**; ships `case-01-happy-path` behavior test
- **Scope boundary** — `local` target only; shared/prod deploys (`dev` / `sqa` / `prd` + DR) are CI/CD's job. The Astronomer deploy action `/deploy-astro` (AICAT-169) is a separate, future skill and is **not** in this release

### Published: RFD 0011 — Airflow DAG Standards (PR #87 — AICAT-101)

Ratifies the Airflow DAG standard and aligns the DAG skills to it:

- Publishes `rfd/0011` and the `PY-AIRFLOW-*` rule family (`rfd/0008/python/airflow.md`, `standards.yaml`)
- `/generate-dag` and `/validate-dag` cite the same ratified rule set, so generated scaffolding and audit findings stay in lockstep
- Refreshes `/generate-dag` and `/setup-databricks-asset-bundle` references and templates against the published standard

### Fixed

- **Confluence publishing** — `confluence-client._content_url_v1` was missing the `/wiki/` path segment, breaking `update_page()`; now fixed, unblocking the `behavior-test-triage` Confluence step (AICAT-200, PR #375)
- **Confluence client** — removed an unused `urljoin` import (AICAT-205, PR #396)
- **Behavior-test harness** — implemented the `stdout_contains` structural check for more precise skill-output assertions (AICAT-181, PR #392)
- **RFD 0006** — frontmatter state synced from `discussion` to `published` to match the live four-tier model (PR #386)
- **`/validate-dbt`** — doc-correctness follow-ups (dbt-empty semantics, matrix-row gap) and remaining PR #380 review nits (`bin/bt` symmetry, SKILL.md wording) (PR #384, PR #385)

### Known limitations

- **Phase 4 deploy is local-only.** `/deploy-dab` targets the developer's own dev space. Shared/prod deploys remain CI/CD's responsibility, and the Astronomer deploy action `/deploy-astro` (AICAT-169) is still in progress.
- **Phases 7 (Operate) & 8 (Evolve)** have leaf skills (`runbook`, `incident-log`, `deprecation-notice`, `usage-analytics-report`) but no GA phase orchestrator yet (epics AICAT-160 / AICAT-161).
- **Platform coverage** — this GA release is validated primarily on macOS. Windows users may encounter gaps in technical prerequisites for some skills — for example, available laptop memory and compute, local tooling setup, and environment configuration.

### Upgrade / setup notes

- No breaking changes to existing skills. `plugin.json` gains `deploy-dab` (99 registered skills).
- No reinstall needed — reload the VS Code window or refresh the Agent Plugins panel.

---

## 2026-06-22 — v1.8.0

**A pre-deploy dbt validation gate, repo-native release communications, and a closed feedback-to-Jira loop.**
- `/validate-dbt` adds a read-only Phase 4 (Build) pre-deploy gate for Databricks data products — compile, schema-diff, and test-resolution checks behind a single grep-able `VERDICT:` line.
- Release communications become repo-native and repeatable (guide + canonical HTML template + reference example).
- The feedback loop now runs end-to-end: `catalyst-feedback` GitHub issues are imported, prioritized, promoted to Jira **AICAT** Stories, and the reporter is linked back to their ticket.

### New: `/validate-dbt` skill — pre-deploy dbt validation gate (PR #380, PR #381 — AICAT-166)

A read-only validation gate that runs **before** deploy and pairs with the planned `/deploy-dab`. It never runs, builds, materializes, deploys, or edits a model.

- **Three gates against the resolved target:**
  1. **Compile** — `dbt parse` + `dbt compile` (Jinja, `ref()`/`source()`, macros, catalog/schema vars)
  2. **Schema diff** — additive vs. **breaking** (dropped / renamed / narrowed columns) via the SQL Statement Execution API
  3. **Test resolution** — data tests compile and resolve; declared PKs carry `not_null` + `unique`
- Emits a single machine-grep-able `VERDICT:` line (e.g. `DEPLOY_READY — 0 blocker, 0 advisory, 3 ok, 3 n-a`) that CI and the future `/deploy-dab` can consume
- Aligned with **RFD 0013** (binding; `SQL-DBSQL-*`) and **RFD 0006** metadata; modeled on the sibling `/validate-dag`
- Ships `case-01-happy-path` (artifact case, threshold 0.70); passed a live LLM smoke run
- PR #381 cleared three non-blocking review nits (RBAP)
- **Scope boundary** — adds `/validate-dbt` only; its exit-gate partner `/deploy-dab` (AICAT-167) is a separate, future skill and is **not** in this release

### New: Standardized release communications (PR #374 — AICAT-199)

Moves release comms out of SharePoint and tribal memory into the repo, alongside `docs/release-notes-guide.md`:

- `docs/catalyst-release-comms-guide.md` — process doc (artifacts, content rules, review checklist, send steps)
- `docs/release-comms/template.html` — canonical HTML email template with placeholders and inline comments
- `docs/release-comms/releases/v1.7.0.html` — first reference example
- Fixes a `load-confluence-context` naming regression in the v1.7.0 CHANGELOG entry

### New: Feedback loop → Jira with status-back (PR #141 — AICAT-154, builds on AICAT-149)

Closes the loop from captured feedback to actioned ticket:

```
catalyst-feedback → import_github_feedback → parse_feedback → create_jira_stories → implement-feedback
(GitHub issues)      pull + dedup            priority + sort   Story + status-back    branch → PR → link
```

- **`import_github_feedback.sh`** (intake) — pulls open `feedback`-labeled issues into the pipeline carrying the source issue #/URL; skips already-`promoted` items; dedup via the `promoted` label
- **status-back** in `create_jira_stories.sh` — after each Story: comment the AICAT link on the issue, label it `promoted`, add a Jira→GitHub remote link. Includes `--dry-run`
- Registers `process-feedback` + `implement-feedback` in `plugin.json`; docs under `docs/feedback*`

**Bug fixes in the adopted prototype**

- `.env` was sourced *after* the assignee lookup → Stories created **unassigned**. Now loaded first.
- The `---` entry separator bled into parsed descriptions. Fixed.

**Validation** — live end-to-end (GH #133 → AICAT-173, assigned, with Source + remote link; re-import correctly skips promoted); `--dry-run` full chain; `bash -n` on all scripts; cgrepo-compliance: 188 passed.

### Known limitations

- **Phase 4 is not yet end-to-end.** `/validate-dbt` is the pre-deploy gate; the deploy leaves `/deploy-dab` (AICAT-167) and `/deploy-astro` (AICAT-169) are still in progress (targeting v1.9.0). A product cannot yet be built **and** deployed entirely in Catalyst.
- **Confluence `update_page()` 404** (AICAT-200) is Dev Complete but not yet released; the `behavior-test-triage` Confluence step depends on it.
- **No GitHub Actions** in the org — `process-feedback` is run by a maintainer during the weekly triage sweep rather than on a trigger.
- A pre-existing, unrelated test failure (`tests/skills/test_skill_metadata_standards.py`, malformed YAML in `rfd/0008`) is tracked separately.

### Upgrade / setup notes

- One-time: the `promoted` label was created on the feedback repo (done).
- No breaking changes to existing skills. `plugin.json` gains `validate-dbt`, `process-feedback`, and `implement-feedback`.

---

## 2026-06-15 — v1.7.0

**Two new skills, a major Databricks Asset Bundle refactor, and behavior test triage automation.** 
- `/validate-dag` adds read-only RFD 0011 compliance auditing as a counterpart to `/generate-dag`; 
- `/behavior-test-triage` closes the loop from test run to Jira triage epic in one skill invocation. 
- `/setup-databricks-asset-bundle` is rebuilt against the `edo-ig-data-products` shape that actually deploys. 
- `/dplc-publish` gains RFD 0002 conditional necessity logic so Phase 6 no longer forces artifacts the data product doesn't need.

### New: `/validate-dag` skill — RFD 0011 DAG compliance auditor (PR #372 — AICAT-168)

Read-only auditor counterpart to `/generate-dag`:

- Applies full RFD 0011 rule set (PY-AIRFLOW-001..022 + DBX-DAB-001/-003) to an existing DAG file
- Produces a Markdown compliance report with a grep-able `VERDICT:` line
- Covers all three DAG patterns: dag-factory, astro-blueprints, pure-Python TaskFlow
- Covers all four modes: production, prototype, lift-and-shift, multi-carrier short-circuit
- Ships 11 behavior test cases
- **Explicit scope boundary** — DBX-DAB-002/-004 (bundle-internal composition) and DBX-SEC-001/-002 (workspace posture) are out of scope; a static DAG file cannot carry signal for these

### New: `/behavior-test-triage` skill — post-run triage automation (PR #146, PR #147 — AICAT-164, AICAT-165)

Automates the full post-run behavior test triage loop in one skill invocation:

- **Infrastructure (AICAT-164 / PR #146):** `ConfluenceClient.update_page()` (storage-format PUT, version increment) and `bin/bt triage` subcommand
  - Reads cached behavior-test results, classifies failures into the AICAT-78 taxonomy
  - Taxonomy: orchestrator-delegation, template-conformance, shared-code, quick-fix, harness
  - Emits structured JSON
- **Skill (AICAT-165 / PR #147):** 7-step orchestration loop
  - Cache gate → `bin/bt triage --version` → init `JiraClient` + `ConfluenceClient`
  - Custom field IDs discovered at runtime via `discover_field_ids()` — no hard-coded `customfield_NNNNN`
  - Create per-release triage epic → create per-finding tickets (severity-tiered by category)
  - Back-link GitHub issues via `gh issue comment` → update Confluence triage page via `update_page()`
  - `allowed-tools` narrowed to `Bash(python3:*) Bash(bin/bt:*) Bash(gh:*) Read`

### `/setup-databricks-asset-bundle` refactor for `edo-ig-data-products` shape (PR #123 — AICAT-105)

Rebuilt to match the `edo-ig-data-products` DAB shape that actually deploys today. Key changes from the v1.5.0 skill:

- **Layout** — `references/` + `templates/` split matching `/generate-dag`; SKILL.md is orchestration-only
- **Variables** — `variables/` directory with `variables.yml` declarations + per-env overrides + `clusters.yml` for complex cluster shapes (`small_cluster`, `dqf_cluster`)
- **Jobs** — two jobs per dataset: `<dataset>.job.yml` (dbt on persistent `existing_cluster_id`) + `<dataset>_dq.job.yml` (Deequ notebook on ephemeral `job_cluster`)
- **Targets** — `local` / `dev` / `sqa` / `prd` + DR variants; sandbox target and `dev7` removed
- **Placeholders** — all `caspian_*` / `EDOIG` literals replaced with env-prefixed `{{PLACEHOLDER}}`s
- **Standards** — RFD 0012 deferrals tracked inline as `# TODO DBX-…` comments, authoritative map in `references/rfd-0012-citations.md`; structural test (`tests/dab/test_*_dab_structural.py`) enforces 8 currently-in-scope rules

### `/dplc-publish` — honor RFD 0002 conditional necessity for Phase 6 leaf artifacts (PR #371 — AICAT-86)

Previously treated all three Phase 6 leaf artifacts as Required. RFD 0002 necessity:

- **Catalog / marketplace listing** — Required
- **Deployment record** — Recommended
- **Consumer onboarding guide** — Optional (required only if external consumers)
- **Release notes** — Optional (required only if versioned or multi-team)

Changes:
- Orchestrator now branches on product attributes at Step 1
- Skips non-applicable optional artifacts with a stated reason recorded in the deployment record
- Phase 6 gate passes without forcing artifacts the RFD wouldn't require
- New behavior test `dplc-publish.case-02-internal-single-team` validates the skip path at 1.00; case-01 (all three applicable) remains passing

### DPLC skill architecture reference doc (PR #41 — AICAT-176)

New `docs/dplc-skill-architecture.html`:

- Self-contained, drift-resistant reference for the 4-layer skill orchestration model (Concierge → Stage Orchestrator → Phase Sub-Orchestrator → Leaf Skills)
- Pure HTML/CSS — no CDN or Mermaid dependencies
- Phase skill lists are illustrative with a breadcrumb to the authoritative `skills/` directory on GitHub
- No hardcoded skill counts or version badges
- Leaf skill type table documents the Capability / Document / Workflow distinction

### Consolidate the Confluence skills: `load-confluence-context` wraps `fetch-confluence` (AICAT-172)

Resolves the near-duplication flagged as follow-up to PR #140 (AICAT-128): the two Confluence skills shared the same `fetch_confluence_page()` call, the same components, and near-identical SKILL.md bodies.

- **Architecture decision — workflow wraps capability.** `load-confluence-context` (workflow tier) now delegates to `fetch-confluence` (capability tier) instead of reimplementing the fetch, per the layering rule in `skills/README.md` ("higher tiers compose lower tiers") and the Composition note `fetch-confluence` already declared. `fetch-confluence` is the single owner of the fetch logic — the `fetch_confluence_page()` call, HTML→Markdown conversion, child-page handling, and the not-configured / 404 / 401 error paths.
- **Renamed the workflow skill `confluence-fetch` → `load-confluence-context`** so it is no longer a near-homophone of the `fetch-confluence` capability and follows the verb-first convention. Updated all callers (`dplc-discovery`, `dplc-design-stage`), `plugin.json`, and the behavior case.
- `load-confluence-context` keeps only its cross-phase lifecycle framing (the phase→artifact table) and hands the page IDs and `--children` flag to `fetch-confluence`.
- Behavior tests: `load-confluence-context.case-01` asserts the delegation (`expected_components: [skills/fetch-confluence]`) rather than the core/client modules the wrapper no longer references directly; `fetch-confluence.case-01` is unchanged. Both continue to pass the 0.70 artifact rubric.

### Fixed

- **`optimize-compute` — `DBX-WASTE-001..010` correctness pass (commit `2c6ddf9` + follow-up).**
  - `DBX-WASTE-008` (SQL warehouse oversized): tightened gating to avoid double-firing alongside `DBX-WASTE-009`; serverless warehouses and warehouses with fewer than 7 days of query history are now skipped (surfaced in `insufficient_data.skipped_rules`).
  - `DBX-WASTE-004` (dbt `threads` vs. cluster cores): the `--override-cores` escape hatch now resolves worker count from `resolved_compute.<cluster_id>.worker_count` when the job_cluster spec doesn't carry one, and falls back to `worker_count = 1` when the override is the only signal available — previously the rule short-circuited and skipped silently in either case, leaving the override functionally inert. May produce findings on jobs that previously yielded none; intended behavior per the catalog.
  - `DBX-WASTE-002` (autoscale floor never relaxes): corrected the estimated worker-minute impact math (previously double-counted floor minutes).
  - `DBX-WASTE-007` (stale Spark/driver config keys, DBR 13+): no longer fires when the override matches the current Databricks default (skip-on-default).
  - `DBX-WASTE-005` (materialization-vs-reads diagnostic): model-query matcher now strips SQL comments and quoted string literals (single and double) and requires identifier boundaries before matching FQNs — previously over-matched on FQNs mentioned in comments or string literals.
  - `DBX-WASTE-010` (dbt target points at all-purpose cluster): fixed an over-fire on `DEV_TARGET`-style catalog drift.
  - Schema hardening: findings JSON now validates against `templates/compute-optimization-findings.json` (null `window`, `_runs_span_days`, and other drift fixed); `rfd/0008/standards.yaml` registers `DBX-WASTE-001..010` so contract checks are wired in.
  - Docs: `SKILL.md` updated to make explicit that the calling model — not a Jinja runtime in `scripts/` — renders `templates/compute-optimization-report.md`.

- **`optimize-compute` — truncation envelopes prevent silent partial-window findings.**
  - `collect_run_history.py` now emits `*_meta` siblings (`cluster_events_meta`, `warehouse_events_meta`, `warehouse_query_history_meta`) carrying `{truncated, count, cap}`
  - Evaluator gates DBX-WASTE-001, -002, -005, -008, -009 with `insufficient_data` when underlying data was truncated (surfaced in `insufficient_data.skipped_rules`)
  - `fetch_warehouse_events` now paginates against `/api/2.0/sql/warehouses/{id}/events` — was a single-shot `limit: 1000` call that could silently drop events

- **`optimize-compute` — narrower exception handling and surfaced soft-fail bugs.**
  - Bare `except` in `_build_client` narrowed to specific auth/network exceptions raised by the SDK
  - Latent `Optional` type annotation in `evaluate_findings.py` now properly imported from `typing`
  - Soft-fail rule loop: severity bumped to `warning` with `evaluator bug:` prefix — was swallowing per-rule exceptions silently at `info`

### Security

- **`optimize-compute` — `query_text` redaction in run-history snapshots.**
  - `collect_run_history.py` now redacts SQL literals from `query_text` before writing to disk
  - String constants → `<str>`, numeric constants → `<num>`; identifiers, table/column names, and SQL structure preserved
  - Rationale: query history can carry customer identifiers (account numbers, names, emails) in WHERE clauses; snapshot lives as plain JSON on the user's local disk

### Changed

- **`optimize-compute` — `rfd/0008/standards.yaml` strictness aftermath (known-state acknowledgement).**
  - Wrapping the rule list under a top-level `rules:` key makes `test_skill_metadata_standards.py::_load_known_ids` actually populate — was silently returning empty before
  - `optimize-compute`'s own rule citations are clean against the new check
  - Exposes pre-existing rule-citation drift in 10 unrelated skills: `write-dbt-wrapper`, `write-dbt-source`, `write-dbt-model`, `setup-dbt-project`, `setup-databricks-asset-bundle`, `setup-monitoring-and-logging`, `troubleshoot-dbt-on-databricks`, `optimize-databricks-job`, `optimize-dbsql-query`, `generate-dag` — drift was always there, test simply couldn't see it; follow-up scoped separately

### Removed

- **`optimize-compute` — `DBX-WASTE-006` withdrawn.**
  - Rule required a 14-point per-model runtime history the bundled collector couldn't reliably assemble
  - Was info-only with no automated recommendation
  - Rule ID marked `status: withdrawn` in `rfd/0008/standards.yaml` and reserved (will not be reused)
  - `references/findings-catalog.md` retains original rule text and withdrawal rationale

### Skills landing-doc Phase 6 phase-home fix (PR #368 — docs, AICAT-87)

Corrects stage→phase ownership drift in the skills landing docs so they match the architecture diagram (`docs/dplc-skill-architecture.html`), the `dplc-build-stage` / `dplc-ship-stage` / `dplc-publish` SKILL.md files, and `dplc-concierge`:

- `dplc-build-stage` is now shown as **Phases 4 – 6** (Build, Validate, **Publish**) — the Phase 6 Publish row (`deployment-record`, `consumer-onboarding-guide`, `release-notes`) moves out of Ship.
- `dplc-ship-stage` is now shown as **Phases 7 – 8** (Operate, Evolve).
- Applied across `skills/README.md` and the embedded `skills/assets/landing-page.svg`.

### Retire stale `skills/index.html` landing page (AICAT-198)

Removed `skills/index.html` (the Wave-1 landing page):

- Never served (GitHub Pages not enabled), not linked from anywhere
- Badly drifted: Build/Ship showed "0 skills available / Coming in Wave 2–3", listed the deleted `data-product-classification` skill, used pre-refactor vocabulary ("Define", "execution skills")
- Superseded by `skills/README.md`, `skills/assets/landing-page.svg`, and `docs/dplc-skill-architecture.html` (PR #41)
- Builds on AICAT-87, which corrected Phase 6 phase-ownership labels and deferred this broader cleanup

---

## 2026-06-08 — v1.6.0

**RFD 0011 alignment for `/generate-dag`, README overhaul, and three behavior-test quality fixes.** The DAG generation skill is updated to track the discussion-state RFD 0011 spec, the README is rebuilt around the DPLC framework with separate consumer and contributor install paths, and the behavior-test harness gains named anti-pattern detection for orchestrator self-invocation.

### /generate-dag — RFD 0011 Discussion-State Alignment (PR #122 — DAG skill update, AICAT-104)

Updates `generate-dag` to match the discussion-state RFD 0011 spec:

- MDS tag set updated: `l1_domain`, `l1_xmatters_group`, `lifecycle_phase`, `data_classification`, `criticality` (optional `l2`/`l3` xMatters groups); routing tags threaded through Datadog event payload
- Datadog as the auto-alert sink; xMatters paging remains manual, driven by the Datadog event payload
- New directives PY-AIRFLOW-016..022: deterministic fail-fast, deferrability + bounded waits, bounded parallelism, Asset-driven default, no-secrets-in-operator-args, `doc_md` local-dev guidance, shared `assert_dag_compliant(dag)` helper
- Pure-Python TaskFlow emission pattern added alongside YAML and Astro Blueprints
- Existing-blueprints support: skill references the consuming repo's `.blueprints/` vocabularies instead of vendoring its own
- Compliance-checklist reference added

### README Overhaul (PR #138 — docs, AICAT-147)

Full rebuild of the top-level README:

- Repositioned around the DPLC lifecycle (prereq → triage → discovery → design → build → validate → ship) with RFD-anchored skill framing
- Separate install paths for consumers (plugin install flow) and contributors (dev setup)
- Evergreen skill framing: skills described by what they do at each DPLC phase, not by release vintage

### Behavior Test Harness Quality (PR #137, PR #136, PR #140)

Three fixes that sharpen failure signals in the behavior-test harness:

- **Orchestrator self-invocation detection** (PR #137 — test harness, AICAT-74) — self-invocations are now tracked as a distinct signal on `RunResult` and named in `SequenceFailure` messages with a pointer to the root cause, rather than surfacing only as missing expected sub-skills
- **`/dplc-build-stage` delegation fix** (PR #136 — orchestrator bug, AICAT-127) — orchestrator now correctly delegates to Phase 4–6 sub-skills; behavior-test cache auto-invalidates on skill content change
- **`/fetch-confluence` case-01 fix** (PR #140 — behavior test, AICAT-128) — behavior test case given a concrete fetch argument, resolving a score of 0.59 below the 0.70 threshold

---

## 2026-06-01 — v1.5.0

**Phase 4 Build Suite generally available, quality hardened from real prototype runs, and field-mapping consolidation around ODCS + dbt.** Three headline changes: the Phase 4 Build skills move from Preview to GA, 13 correctness bugs found during the bloomberg-corp-pfd-asia bootstrap are fixed across five skills and one shared library, and the source-to-target mapping story consolidates around dbt SQL and ODCS data contracts (removing the sttm skill and trimming three others).

### Phase 4 Build Suite — Out of Preview (PR #95)

Previously shipped in v1.4.0 as `Preview (Internal)`, the Phase 4 Build skills are now announced and actively supported. All skills have happy-path behavior test coverage (added in PR #121) and are validated against the bloomberg-corp-pfd-asia prototype.

**Phase 4 orchestrator + Catalyst leaves:**

- **`/dplc-build`** — mode-aware Phase 4 orchestrator (prototype / production / lift-and-shift)
- **`/build-preflight`** — pre-build environment and tool-version drift check; Step 5 reads `skills/requirements.txt` pins and emits a warning on mismatch
- **`/setup-dbt-project`** — `dbt_project.yml` with `datasets/` + `shared/` structure; OAuth U2M dev target, M2M production target; tool-version pins enforced by `/build-preflight`
- **`/configure-sql-warehouse`** — SQL warehouse configuration for DBSQL
- **`/write-dbt-wrapper`** — `dbt_wrapper.py` at repo root; `sys.path` scrub before dbt, `--project-dir` position fix (dbt 1.10+), `__file__` fallback for `PROJECT_HOME`
- **`/setup-databricks-asset-bundle`** — per-env variables inlined under `targets.<env>.variables:`; cluster spec deliberately omitted (Lakeflow Jobs Serverless auto-routing); prototype-mode defaults
- **`/setup-monitoring-and-logging`** — serverless: wrapper tees stdout/stderr to UC Volume at `dbt_logs/<run_id>/<task_key>.log`; sink-agnostic notification standard; cross-run search via `system.lakeflow.*`
- **`/run-dbt-on-databricks`** — executes dbt jobs on Databricks via the Catalyst wrapper
- **`/dbt-best-practices`** — dbt coding standards and conventions
- **`/troubleshoot-dbt-on-databricks`** — debugging guide for dbt on Databricks
- **`/scaffold-repo-structure`** — canonical Catalyst data product repo layout; `data_products/` (underscore), `shared/`; referenced by setup and generate skills for path resolution
- **`/generate-dag`** — RFD 0011-anchored Airflow DAG generator; dag-factory (default) and astro-blueprints (opt-in); mode-aware

**Databricks developer skills (ai-dev-kit forks — Databricks custom license):** `/databricks-bundles`, `/databricks-jobs`, `/databricks-dbsql`, `/databricks-config`, `/databricks-execution-compute`, `/databricks-unity-catalog`, `/databricks-python-sdk`, `/databricks-docs`

**dbt developer skills (dbt-labs forks — Apache 2.0):** `/adding-dbt-unit-test`, `/working-with-dbt-mesh`, `/fetching-dbt-docs`

### Build-Phase Skill Repairs (PR #121, AICAT-130..143)

13 correctness bugs fixed across the Build suite after running against a real prototype. Every touched skill ships a happy-path behavior test case; 4 of 5 pass through the LLM-judged harness end-to-end.

| Ticket | Skill | Fix |
|---|---|---|
| AICAT-130 | `source-aligned` | Syntax error in `generate_ingestion_from_profile.py` (malformed double-escape) — couldn't be imported |
| AICAT-132 | `source-aligned` | Stripped `\n` and `\"` escapes in `databricks_local_ingest.py` — serverless spark_python_task failing at parse time |
| AICAT-133 | `source-aligned` | SDK drift fix in `submit_serverless_raw_to_standard.py` (`Environment(environment_version=…)` → `client=…`); `COI_DBX_STANDARD_*` env honored; `landing-base` forwarded to task |
| AICAT-134 | `source-aligned` | Vendored production `cspn_*_overrides.sql` macros from `edo-ig-data-products`; retired contradictory stubs |
| AICAT-142 | `source-aligned` | Non-CSV scaffold (`local_helper.py`), live-data verification step, `.catalyst-build.yml#mode` awareness |
| AICAT-131 | `skills/core/jira.py` | `create_epic_with_stories()` discovers and populates the Acceptance Criteria custom field (ADF bulletList shape); `JIRA_ACCEPTANCE_CRITERIA_FIELD_ID` env override; graceful fall-back when field isn't present |
| AICAT-135 | `setup-databricks-asset-bundle` | Drop `variables_*.yml` include glob (inline per-env vars under `targets.<env>.variables:`); drop `cluster_log_conf` (rejected on serverless) |
| AICAT-136 | `setup-monitoring-and-logging` | Full rewrite for serverless: wrapper tee to UC Volume, wrapper-driven artifact capture to `dbt_artifacts/`, sink-agnostic notification |
| AICAT-137 | `write-dbt-wrapper`, `scaffold-repo-structure` | Wrapper location → repo-root `/dbt_wrapper.py`; standardize on `data_products/` (underscore); ambient job-context identity |
| AICAT-138 | `write-dbt-wrapper` | `__file__` fallback for `PROJECT_HOME`; `sys.path` scrub before dbt; `--project-dir` position fix (dbt 1.10+) |
| AICAT-140 | `setup-dbt-project` | `dbt_project.yml` layout aligned with `datasets/` + `shared/`; mode-aware `target-path` and per-layer schemas |
| AICAT-141 | `setup-dbt-project` | OAuth U2M (browser-flow) `dev` target in `profiles.yml`; M2M kept for production; user-PAT ban preserved |
| AICAT-143 | `skills/requirements.txt` | Pin `dbt-core`, `dbt-databricks`, `databricks-cli`, `databricks-sdk` to tested ranges; `/build-preflight` Step 5 grows tool-version drift check |

Cross-cutting: `docs/design-divergences-from-edo-ig.md` (AICAT-139) records four deliberate Catalyst-vs-edo-ig design choices (wrapper location, dbt phase chaining, DQ strategy, default compute) with rationale and downstream consequences.

### ODCS Field-Mapping Consolidation (PR #120)

Collapses four overlapping field-mapping artifacts (sttm CSV, data-modeling S2T table, transformation-spec logic summary, dbt SQL) to two canonical owners: **ODCS data contract** owns target schema + quality rules (RFD 0009); **dbt SQL** (`write-dbt-model`) owns field-level transformations. Three skills trimmed; `sttm` removed entirely.

### Removed

- **`skills/sttm/`** — the standalone STTM generation skill (added in v1.4.0 via PR #113) is removed. Field-level source-to-target transformations now live in dbt SQL (owned by `write-dbt-model`); target schema and quality rules live in the ODCS data contract. The corresponding behavior test case at `tests/behavior/cases/sttm/` is removed.

### Changed

- **`skills/data-modeling/`** — output trimmed to conceptual modeling only. The DDL Statements and Source-to-Target Mapping sections are removed; target schema (DDL) owned by data contract, field mappings owned by dbt SQL. ER diagram and Design Rationale stay.
- **`skills/transformation-spec/`** — template trimmed to architectural concerns only. Per-model Logic Summary / Business Rules / Edge Cases subsections and the §5 Testing Requirements section are removed. Cross-reference notes point at data contract (quality), dbt schema.yml (tests), and dbt SQL (logic). Model Map and Backfill Strategy stay.
- **`skills/source-aligned/`** — the `generate-sttm` workflow step and `### Mode: generate-sttm` section are removed. Workflow flows directly from DDL generation to dbt model generation; source-to-target mapping is captured in dbt SQL.

### Fixed

- **`plugin.json`** — synced with `skills/` directory (pre-existing drift from PR #95). Removed stale entries for `generate-dbt-model` and `validate-sql`; added `connect-astro`, `optimize-databricks-job`, `optimize-dbsql-query`, `register-data-contract`, `scaffold-data-product`, `write-dbt-model`, `write-dbt-source`. Restores `tests/ci/test_plugin_json_consistency.py` to green.
- **`cspn_*_overrides.sql` macros (PR #127)** — two correctness bugs in macros vendored from `edo-ig-data-products` via AICAT-134: `cspn_strategy_overrides.sql` referenced undefined `end_date_col` in the `bitemporal_load`/`full` branch; `cspn_validate_overrides.sql` had a second bug surfaced during PR #120 review. Fixed in a follow-up commit.
- **Behavior test harness: self-read false positive in sub-skill detection (AICAT-122, PR #125)** — `sub_skill_detection.py` counted any `Read skills/<name>/SKILL.md` as a sub-skill invocation, including when the orchestrator under test reads its own SKILL.md at startup. Added `skill_under_test` parameter to `detect_sub_skill` and `collect_sub_skills`; self-reads now excluded. Threaded through `claude_agent.py` (live runs) and `cache.py` (re-judging). Fixes `dplc-design.case-02-no-sql` which failed with `unexpected sub-skills present: ['dplc-design']` despite correct delegation behavior. 16 unit tests.

---

## 2026-05-26 — v1.4.0

**Phase 3 Design coverage complete, template quality, telemetry, and discover-data reliability.** Four areas improved: Phase 3 now has full skill coverage with data modeling and STTM generation, template conformance fixed across 14 skills spanning Phases 0–6, shared skill components properly wired, and per-skill usage telemetry available for the first time.

### Data Modeling (PR #115, AICAT-71/72/77)

`skills/data-modeling/` now produces three Phase 3 artifacts in one pass: an ER diagram (Mermaid), DDL statements (Delta table definitions with typing, comments, and table properties), and a source-to-target mapping with per-column lineage. SCD type, grain, and materialization decisions are explained in a Design Rationale section so reviewers understand the choices, not just the output.

The lineage module was previously a dead import — now wired to `skills/core/lineage.py` and live. This v1.0 covers net-new model design; support for modeling against existing entities is scoped for v1.5.0.

**Impact:** design artifacts from `/data-modeling` now feed directly into `/data-contract`, `/transformation-spec`, and `/column-lineage` — the full Phase 3 output is automatable end-to-end.

### STTM Generation (PR #113, AICAT-94)

New standalone skill at `skills/sttm/` generates Source-to-Target Mapping documentation as a Phase 3 artifact without re-running full data modeling. Covers the common case where the model already exists and only the STTM document needs to be produced or updated.

### Template Conformance — 14 Skills Across Phases 0–6 (PRs #105, #106, #108, #109, #116)

Required H2 headings embedded directly in SKILL.md files for 14 skills, addressing the highest-priority findings from the v1.1.0 behavior test run. Skills fixed by phase:

- **Phase 0 — Prereq:** `phase-zero-checklist`, `business-case`, `outcome-kpi-statement`
- **Phase 1 — Triage:** `demand-tracker-entry`, `consumer-use-case-map`
- **Phase 2 — Discovery:** `privacy-impact-assessment`
- **Phase 3 — Design:** `architecture-diagram`, `data-contract`, `nfr-specification`, `security-design`, `integration-blueprint`
- **Phase 4 — Build:** `generate-dbt-model`, `schedule-backfill-plan`
- **Phase 6 — Publish:** `release-notes`

Remaining conformance fixes continuing in v1.5.0.

### Shared Component Wiring (PR #115)

Three skills connected to shared modules they were always meant to use:

- `data-profiling` → `skills/clients/databricks.py` (was using inline connection logic)
- `data-modeling` → `skills/core/lineage.py` for column tracing (was a dead import)
- `requirements-acceptance-criteria` → `[x]` placeholder removed from generated output

### Per-Skill Usage Telemetry (PR #107)

Opt-in telemetry captures which Catalyst skills are invoked in Copilot Chat sessions. One-time install: `scripts/hooks/install-skill-hooks.sh` + three VS Code settings keys. Invocations logged to `~/.catalyst/skill-use.jsonl` — local only, nothing sent externally. Note: `chat.useClaudeHooks` is currently in VS Code Preview; config format could change.

> **Removed since.** This hook no longer exists — see *Removed: the VS Code skill-telemetry hook* under `[Unreleased]`, which also carries uninstall steps. This entry is left as written because it accurately records what shipped at the time.

### Discover Data: Credential Check at Startup (PR #114, AICAT-125)

`discover-data` now validates Databricks credentials at Step 1 before attempting any catalog queries. Missing or misconfigured credentials stop the skill immediately with a clear message and a pointer to `/connect-databricks`. Previously caused a silent mid-run failure after the agent had already started querying.

### Known Issues

- **`dplc-design` self-invocation on no-SQL branch** — orchestrator incorrectly re-invokes itself when no SQL model is in scope. Workaround: invoke design sub-skills directly (`data-contract`, `transformation-spec`, etc.). Fix targeting v1.5.0.
- **Behavior test coverage gaps (3 skills)** — `marketplace-search` requires a live auth mock not yet in place; orchestrator delegation detection needs a trace-based approach. Both targeting v1.5.0.

### Removed (PR #95)

Skills removed and superseded by the Phase 4 Build suite:

- **`/generate-dbt-model`** — superseded by `/write-dbt-model`, which binds to enumerated `SQL-DBSQL-*` and `PY-NAMING-*` rule IDs and produces RFD 0003-compliant paths
- **`/validate-sql`** — superseded by CI-side `sqlfluff` + `/optimize-dbsql-query` for advisory `SQL-PERF-DBSQL-*` findings
- **15 overlapping skills** superseded by the Phase 4 Build suite (`/authoring-airflow-on-astronomer`, `/authoring-databricks-bundles`, `/authoring-dbt-on-dbsql`, `/write-astro-dag`, `/write-dab-resource`, `/write-dbt-test`, `/validate-astro-dag`, `/validate-dab`, `/validate-dbt`, `/deploy-astro`, `/deploy-dab`, `/scaffold-dbt-project`, `/scaffold-domain-repo`, `/run-dbt`, `/optimize-dbt-model`)

### Preview (Internal) — Phase 4 Build Skills (PR #95)

Registered in `plugin.json` for internal pressure-testing and early adopter refinement. Not in user-facing release notes. Will graduate to GA in a future release.

- **Phase 4 orchestrator + 9 Catalyst leaves:** `dplc-build` (mode-aware: prototype / production / lift-and-shift), `build-preflight`, `setup-dbt-project`, `configure-sql-warehouse`, `write-dbt-wrapper`, `setup-databricks-asset-bundle`, `setup-monitoring-and-logging`, `run-dbt-on-databricks`, `dbt-best-practices`, `troubleshoot-dbt-on-databricks`
- **8 ai-dev-kit forks** (Databricks custom license — see `third-party/LICENSE-databricks.md`): `databricks-bundles`, `databricks-jobs`, `databricks-dbsql`, `databricks-config`, `databricks-execution-compute`, `databricks-unity-catalog`, `databricks-python-sdk`, `databricks-docs`
- **3 dbt-labs forks** (from `dbt-labs/dbt-agent-skills`): `adding-dbt-unit-test`, `working-with-dbt-mesh`, `fetching-dbt-docs`
- **`scaffold-repo-structure`** — canonical Catalyst data product repo layout; cited by setup and generate skills for path resolution
- **`generate-dag`** — full RFD 0011-anchored Airflow DAG generator replacing the prior stub; dag-factory (default) and astro-blueprints (opt-in) emission patterns; mode-aware
- **Vendored Python:** `skills/clients/databricks_tools_core/` — 41 files from `databricks-solutions/ai-dev-kit @ 8cb44565`

---

## 2026-05-18 — v1.3.0

**Phase 6 Publish sub-orchestrator + orchestrator reliability fixes across Phases 0–5.** Three improvements: the Publish orchestrator ships data products to production with the right documentation and verification, orchestrator delegation fixes ensure Phases 0–4 work as designed, and Phase 5 doc skills are promoted to operational status.

### Added

- **`dplc-publish`** (`skills/dplc-publish/`, PR #85, AICAT-20, AICAT-40) — Phase 6 sub-orchestrator. Sequences `deployment-record`, `consumer-onboarding-guide`, and `release-notes`; confirms marketplace registration (`marketplace.capgroup.com` → "Register Data"; manual today, EDO Data Producer authorized); and verifies the listing programmatically via `marketplace-search` (`validated == true`, healthy, expected target data domain in `ancestry`). Reports Phase 6 gate (*Production validated?*) with five criteria. Automated registration deferred to a future `marketplace-register` skill when the marketplace exposes a write API.

### Fixed

- **Orchestrator delegation** — `dplc-prereq` → `phase-zero-checklist` (PR #88, AICAT-57); `dplc-triage` → Phase 1 sub-skills (PR #89, AICAT-56); `dplc-discovery` → Phase 2 sub-skills (PR #90, AICAT-58); `dplc-design` → Phase 3 sub-skills (PR #91, AICAT-59). Fixes silent failures where orchestrators produced incomplete or missing artifacts.
- **Phase 5 doc skills promoted** — `uat-sign-off` and `data-quality-sign-off` now operational Phase 5 leaves with `lifecycle-phase: phase-5-validate` frontmatter; invoked by `dplc-validate` (PR #93, AICAT-38).
- **pip installs** re-pointed at internal cgrepo Nexus proxy (PR #82)
- **Python prereq** bumped to 3.10+ (3.13 recommended); 3.9 flagged incompatible (PR #92)

---

## 2026-05-13 — v1.2.0 (continued)

**DPLC — Phase 5 Validate sub-orchestrator + doc-skill promotion.** Released alongside the Jira Client work in v1.2.0 (PR #77, merged 2026-05-13).

### What's in it

- **`dplc-validate`** (`skills/dplc-validate/SKILL.md`) — new Phase 5 sub-orchestrator. Sequences the four validate-phase leaves (`data-quality-sign-off`, `uat-sign-off`, `integration-test-report`, `dataops-handoff-draft`), reconciles roster against the data contract, and renders the gate decision (RFD-0002 wording: *UAT Passed & Accepted?*). Mirrors `dplc-discovery` structure.
- **Phase 5 doc-skill promotion** — `uat-sign-off` and `data-quality-sign-off` are now operational Phase 5 leaves with `lifecycle-phase: phase-5-validate` frontmatter. Both are invoked by `dplc-validate` (Steps 3 & 4) and produce sign-off artifacts grounded in the contract + build outputs.
- **Marketplace / counts** — `plugin.json` registers the new skill; `.github/plugin/marketplace.json` synced via `scripts/sync_plugin_version.py`. README counts updated: 4 → 5 orchestrators, 34 → 35 skills.
- **Behavior-test coverage** — added `tests/behavior/cases/dplc-validate/case-01-behavior.yaml` (artifact-rubric type, mirrors `dplc-discovery` rubric).

### Live-run measurements

`dplc-validate` end-to-end: 20 tool calls / 22.7k tokens / 214.6s wall-clock. Above the RFD-0006 first-cut targets (~15 calls / ~16k tokens / ~5 min) on calls and tokens, under on wall-clock. See AICAT-19 / AICAT-38 for the runtime-budget follow-up.

### Related tickets

- **AICAT-19** — Build dplc-validate sub-orchestrator (Resolved)
- **AICAT-38** — Promote Phase 5 doc skills (`uat-sign-off`, `data-quality-sign-off`)
- **AICAT-88** — Standardize artifact output paths to `phase-{N}-{phase_name}/` folders (backlog)

---

## 2026-05-11 — v1.2.0

**Tool Utils — Phase 1: Jira Client.** Complete Jira Cloud REST API integration for Catalyst skills, with interactive credential setup and comprehensive testing.

### What's in it

- **Jira Client** (`skills/clients/jira.py`) — Full Jira Cloud REST API v3 wrapper
  - JQL search with auto-pagination (`iter_search_issues`)
  - Issue creation, updating, and linking
  - Epic and story management
  - Field ID auto-discovery (Epic Name, Epic Link, Sprint)
  - ADF (Atlassian Document Format) support
  - Rate-limit handling with exponential backoff + jitter
  - Comprehensive error handling (9 specialized exceptions)

- **Higher-level helpers** (`skills/core/jira.py`)
  - `create_epic_with_stories()` — Orchestrates epic + story creation with linking and sprint assignment
  - `fetch_sprint_backlog()` — Retrieve all issues in a sprint
  - `check_jira_connectivity()` — Health check validation

- **Shared exception hierarchy** (`skills/clients/exceptions.py`)
  - `CatalystClientError` base class
  - 9 specialized exceptions (AuthError, RateLimitError, NotFoundError, ValidationError, ConflictError, ServerError, NetworkError, RequestTimeoutError, SSLError)
  - Ready for GitHub, Confluence, Databricks clients (Phases 2-3)

- **Interactive credential setup** (`scripts/setup.py`)
  - `check_integration()` — Validate service credentials
  - `guide_setup()` — Browser-based token generation with inline instructions
  - Supports Jira, Confluence, GitHub, Databricks
  - Creates/updates `.env` file with restrictive permissions (0600 on POSIX)

- **Comprehensive testing** (`skills/tests/test_jira_client.py`)
  - 12 passing unit tests (mocked, fast)
  - 2 integration tests (live credentials)
  - pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`
  - Coverage: initialization, ADF conversion, field discovery, HTTP error mapping, rate-limit retry, pagination

- **Documentation** (`skills/clients/README.md`)
  - Usage examples for all clients
  - Auth patterns, error handling guide
  - Integration setup instructions

### Technical details

- Explicit auth pattern (credentials passed to `__init__`, no env var magic)
- `requests.Session` for connection pooling
- Retry logic honors Retry-After header
- TODO: Connection pool tuning for bulk operations (see AICAT-54)
- TODO: Jitter cap optimization for long delays (see AICAT-54)

### Related tickets

- **AICAT-35** — Jira Client Phase 1 (completed)
- **AICAT-52** — ServiceNow connector (R3 backlog)
- **AICAT-53** — Teams integration (R3 backlog)
- **AICAT-54** — Jira Client Phase 2: Bulk operations & integration tests (R2 backlog)

---

## 2026-04-30 — v1.1.0

### Four-tier skill architecture
- **Capability skills** (10 new): `connect-databricks`, `query-table`, `profile-columns`, `query-catalog`, `parse-lineage`, `generate-dbt-model`, `validate-sql`, `generate-dag`, `fetch-confluence`, `search-marketplace`
- **Document skills** (35): Templates moved into each skill's `templates/` directory. 16 staged skills graduated from `_staged/` to `document/`. All enriched with trigger phrases, quality checks, lifecycle context.
- **Orchestrators** (3 new): `dplc-define` (Phases 0-3), `dplc-deliver` (Phases 4-6), `dplc-sustain` (Phases 7-8)
- **Concierge** moved to `skills/orchestrators/dplc-concierge/`

### Structural fixes
- `prompts/` → `references/` in execution skills (Anthropic guide convention)
- Bare path references fixed with `references/` and `scripts/` prefixes
- Dead references to non-existent files resolved
- `_staged/` directory removed (promoted versions are canonical)
- `plugin.json` updated with all 63 skills

# AI Catalyst — Changelog

Release notes for the AI Catalyst VS Code Copilot plugin. Users always pull
the latest from `main`; entries below describe what landed at each notable
milestone.

Cadence: ad-hoc — released whenever something ships that users should know about.

---

## 2026-04-29 — v1.1.0

Two features land together in v1.1.0: a real marketplace search backend, and a feedback loop for getting actionable signal back from users.

### Marketplace skill rewrite

Replaces the placeholder marketplace search with a real implementation backed by the marketplace's actual API. Adds `details` subcommand surfacing AD entitlement info. Removes the duplicate `capability/search-marketplace` skill.

- `python -m skills.clients.marketplace {whoami,login,search,details}` CLI
- Okta SSO bootstrap via Playwright (one-time per profile)
- Caspian + LASR access lookup with platform branching
- Structured output with code-label pairs for safe agent consumption

**Migration:**
- Skill name `marketplace-search` is unchanged.
- The `capability/search-marketplace` entry in `plugin.json` has been removed.
- New token cache lives at `~/.config/catalyst/marketplace.json` (mode 0600).

### Feedback loop

Users can give substantive feedback on any AI Catalyst skill, which becomes a GitHub issue on the catalyst repo. Zero user setup — if `gh` is authenticated (it is, because that's how Copilot works), the skill just works. No ratings — just words. Silence means satisfied.

**Added:**
- **New skill: `catalyst-feedback`** (`skills/catalyst-feedback/`) — asks two optional questions (*"what worked?"* + *"what didn't?"*). Either/both can be skipped. If both empty, nothing files. Otherwise classifies the reply as win / gap / mixed and runs `gh issue create` against `cg-open-itg/catalyst`.
- **End-of-orchestrator feedback prompt** on all 4 orchestrators (`dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design`): *"Anything to flag about this run? Hit enter to skip, or tell me what worked / what didn't."* Substantive reply → orchestrator invokes `catalyst-feedback` with the reply verbatim, which classifies, captures session context, shows a preview, and files. Silence → nothing files.
- **`docs/feedback.md`** — documents the loop: four ways to trigger feedback, tips for writing useful feedback, six worked prompt → filed-issue examples, labels, admin setup, review process, guardrails, graceful-failure behavior.

**Issue format:**
- **Title:** `[feedback] <skill> — <first 6 words of the substantive content>`
- **Labels:** `feedback` + one of `feedback-win` / `feedback-gap` / `feedback-mixed`
- **Body** includes a **Context** section auto-captured from the conversation (skill invocation input, sub-skills that ran with 1-line outcomes, current phase/step, errors surfaced, plugin version) plus **What worked** / **What didn't** sections (omitted if empty).
- **Preview-before-file** is mandatory: the skill always shows the user the full draft. They reply `file` / `edit <request>` / `cancel`. Natural-language edits regenerate the draft for re-review.
- **Hard exclusions:** credentials, full schemas, full artifact contents, client/customer identifiers, paths outside the repo, vendor records — never captured, even if they appear in conversation.
- **Mechanical credential scrub:** before showing the preview, the skill runs a regex pass for `[A-Za-z0-9_]{20,}` substrings within 30 chars of `token` / `key` / `bearer` / `secret` / `auth` / `password` / `credential` / `api` (case-insensitive). Matches are auto-redacted with `<REDACTED: token-like string near "<keyword>">` and the preview is prefixed with a `⚠ Auto-redacted N token-like string(s)` banner. Backstop for credential leakage; preview review remains the primary safeguard.

**Admin one-time setup** — four GitHub labels on the repo:
```bash
gh label create feedback       --color 0075ca
gh label create feedback-gap   --color c5100b
gh label create feedback-win   --color 2e7d32
gh label create feedback-mixed --color e8a803
```

**User setup:** none.

**Graceful failure:** if `gh` fails (not installed, not auth'd, offline, label missing, rate-limited), the skill saves the body to `.catalyst/feedback/<timestamp>_<skill>.md` locally and shows a link to the repo's "new issue" form. Nothing lost.

**Design evolution:** went through five iterations before settling on the current design — local JSONL → SharePoint-synced OneDrive → GitHub Issues with 1–5 ratings → words only → words + auto-context + preview + scrub.

**Intentionally deferred:**
- Passive telemetry / usage counts / error rates / abandonment — needs enterprise privacy review. Would answer "which skills get used at all," complementing the word-based signal we have now.
- Copilot's native 👍👎 integration — admin-access-dependent.
- Auto-conversion of feedback issues to Jira tickets — manual promotion for now.

---

## 2026-04-24 — v1.0.0

**Initial release.** AI Catalyst ships as a VS Code Copilot marketplace plugin covering the Define stage (Phases 0–3) of the Data Product Lifecycle.

### What's in it

- **1 concierge** — `dplc-concierge` routes users to the right phase
- **4 phase orchestrators** — `dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design`
- **9 execution skills** — `discover-data`, `data-profiling`, `data-modeling`, `column-lineage`, `confluence-fetch`, `marketplace-search`, `source-aligned`, `domain-aligned`, `consumer-aligned`
- **20 document skills** — Phase 0–3 artifacts aligned to [RFD 0002](rfd/0002/README.md) templates

### Plugin structure

- `plugin.json` (repo root) — references skills directly under `skills/` (single source of truth; no mirror, no build step)
- `.github/plugin/marketplace.json` — marketplace registry
- `.github/copilot-settings.json` — team-wide auto-registration when the repo is opened in VS Code

### Integrations

- Live Databricks integration (discover / profile) with graceful fallback when credentials not configured
- Live Confluence v2 API integration

### Not yet included

- Phases 4–8 (Build, Validate, Publish, Operate, Evolve) — skills for these are staged at `skills/_staged/` and will land in future releases

### Install

See [`docs/install.md`](docs/install.md).
