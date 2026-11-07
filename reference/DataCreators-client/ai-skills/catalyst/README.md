# AI Catalyst

AI-powered acceleration for the [Data Product Lifecycle (RFD 0002)](rfd/0002/README.md). AI Catalyst gives you AI skills that guide you through every phase of building, validating, and operating data products — from initial triage through production and retirement.

## VS Code Plugin

A library of AI skills organized around the Data Product Lifecycle's 9 phases (0–8), delivered as a VS Code plugin. Ask questions or describe what you need in Copilot Chat, and the right skill activates automatically. 

Skills come in four types:
- **Orchestrators**: guide you through an entire stage or phase, calling other skills as needed
- **Workflows**: walk you through a multi-step process (e.g. discovering data sources, setting up a project)
- **Capabilities**: do one specific thing (e.g. connect to Databricks, profile a table, query a catalog)
- **Document skills**: each skill generates a specific lifecycle deliverable (data contract, runbook, architecture diagram, etc.)

For the full skill list, see [`skills/README.md`](skills/README.md). For an
interactive map of how the skills connect, see the
[skills graph](docs/skills-graph/README.md).

### Install

#### Use skills in your project (no clone required)

Add the marketplace to your VS Code settings — takes 2 minutes. See [`docs/install.md`](docs/install.md) for the one-time setup.

On **Claude Code**, the same repo is a plugin marketplace:

```bash
claude plugin marketplace add cg-open-itg/catalyst
claude plugin install ai-catalyst@catalyst
```

#### Edit or add skills (for contributors)

Clone this repo and open it as your workspace in VS Code. Skills are available in Copilot Chat as long as the repo is open. Edit under [`skills/`](skills/) — changes go live on the next refresh, no build step.

New contributor? Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) — the cookbook for adding, updating, and evolving skills.

Full walkthrough: [`docs/install.md`](docs/install.md). Release notes: [`CHANGELOG.md`](CHANGELOG.md).

### How to use

Just describe what you need in Copilot Chat. You don't have to know skill names — Copilot matches your request to the right skill. Examples:

- "I need to plan a new data product" → routes you to the concierge
- "Help me design a data contract" → generates a data contract
- "Connect me to Databricks" → runs the connection setup
- "What's in this table?" → profiles the columns

If you do want to call a skill directly, use its name: `dplc-concierge`, `data-contract`, `connect-databricks`, etc.

### Feedback

Have an idea, found a bug, or want to tell us something worked well? Just say "I have feedback" in Copilot Chat — the `catalyst-feedback` skill will guide you through it. It captures context from your session, shows you a preview, and files a GitHub Issue only after you approve.

For details on how feedback is handled, see [`docs/feedback.md`](docs/feedback.md).

### Credentials (optional, unlocks live integrations)

| Credential | Unlocks |
|---|---|
| `DATABRICKS_HOST`, `DATABRICKS_TOKEN` | Live `discover-data`, `data-profiling`, `query-table`, `profile-columns`, `query-catalog`, `connect-databricks`, etc. |
| `CONFLUENCE_BASE_URL`, `CONFLUENCE_TOKEN` | Live `load-confluence-context`, `fetch-confluence` |
| `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` | Live Jira integrations |

Without credentials, skills still run — they ask you for context that would otherwise come from live systems.

**Building or shipping needs more than `.env`.** The skills that drive Databricks Asset Bundles, jobs, SQL warehouses, and dbt-on-Databricks shell out to `databricks bundle …`, so they need the **`databricks` CLI installed** (0.218+, below 1.0), not just environment variables. Authenticate it with `databricks auth login --host <your-workspace>` — interactive OAuth, no secret in a file — which writes a profile to `~/.databrickscfg` that the SDK, the VS Code extension, dbt, and the CLI all read, so one setup covers every route. **Prefer OAuth to a PAT:** DBX-SEC-002 asks for it and `/connect-databricks` refuses `DATABRICKS_TOKEN` outright. See [`docs/install.md`](docs/install.md#does-my-task-need-the-databricks-cli-installed) for which tasks need which.

### Editing skills

Edit under [`skills/`](skills/) at the repo root. Skills live in a flat layout: `skills/<skill-name>/SKILL.md`. [`plugin.json`](plugin.json) points at those directories.

All changes require a pull request and at least one approval before merging. Once merged, changes are picked up on the next Copilot marketplace refresh — no build step.

To add a new skill, add one entry to the `skills` array in [`plugin.json`](plugin.json):

```json
"skills/<skill-name>"
```

Claude Code needs no equivalent entry — it auto-discovers `skills/<name>/SKILL.md`.

Then refresh the [skills graph](docs/skills-graph/README.md) so it picks up the
new skill and its dependencies:

```bash
python scripts/build_skills_graph.py
```

The offline test suite fails if you forget, so this is checked, not remembered.

### Versioning

See [`CHANGELOG.md`](CHANGELOG.md) for the full history, or [GitHub Releases](https://github.com/cg-open-itg/catalyst/releases) for published versions with notes.

## RFDs (Requests for Discussion)

RFDs are how we propose, discuss, and record decisions. The process is modeled
on the [Oxide Computer Company RFD process](https://rfd.shared.oxide.computer/rfd/0001).

1. **Reserve** an RFD number and create a branch (`rfd/NNNN`)
2. **Write** your RFD in `rfd/NNNN/README.md` (state: `prediscussion`)
3. **Open a PR** to `main` when ready for feedback (state: `discussion`)
4. **Discuss** on the PR — line-by-line review, threaded comments
5. **Merge** when discussion converges (state: `published`)

The RFD itself is the permanent record. No separate decision documents needed.

See [RFD 1](rfd/0001/README.md) for the full process, or use the
[template](rfd/0000/README.md) to get started.

## Directory Structure

```
.
├── .github/
│   ├── copilot-settings.json        # Team-wide marketplace auto-registration
│   └── plugin/marketplace.json      # VS Code marketplace registry (source: ".")
├── .claude-plugin/                  # Claude Code manifests — static; skills auto-discovered,
│   ├── marketplace.json             #   and no `version` field (see docs/install.md)
│   └── plugin.json                  #   Claude Code marketplace registry + plugin manifest
├── .claude/settings.json            # Claude Code marketplace auto-registration
├── plugin.json                      # Plugin manifest — lists skills by relative path
├── skills/                          # Source of truth for AI Catalyst skills
├── scripts/
│   ├── build_skills_graph.py        # Regenerates docs/skills-graph/graph.json
│   └── sync_plugin_version.py       # Syncs version into .github/plugin/marketplace.json
├── rfd/
│   ├── README.md                    # Process overview + index
│   ├── 0000/README.md               # RFD template (copy this)
│   ├── 0001/README.md               # Requests for Discussion
│   ├── 0002/README.md               # Data Product Lifecycle
│   └── 0006/README.md               # Skill Contribution Strategy
├── docs/
│   ├── install.md                   # Install guide (VS Code + Claude Code)
│   ├── feedback.md                  # How the feedback skill works
│   └── skills-graph/                # Interactive skills map (generated data)
├── CHANGELOG.md                     # AI Catalyst release notes
└── README.md                        # This file
```
