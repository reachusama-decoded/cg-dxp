# Install AI Catalyst

The same skills ship to two hosts from this one repo:

| Host | Manifests | Install |
|---|---|---|
| VS Code + GitHub Copilot Chat | `plugin.json` + `.github/plugin/marketplace.json` | Path A / Path B below |
| Claude Code | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` | Path C below |

## Prerequisites

- **VS Code 1.90+** *(Paths A and B)*
- **GitHub Copilot Chat** extension, signed in with your Capital Group account *(Paths A and B)*
- **Claude Code 2.1+** *(Path C)* — `claude --version`
- **Python 3.10+** on your PATH (minimum — `skills/requirements.txt` pulls `markitdown` which requires 3.10+). **Python 3.13 recommended** — it's the only Python currently receiving both bug-fix and security backports (3.10–3.12 are in security-only mode). **Python 3.9 is incompatible**: past end-of-life (October 2025), and `pip install -r skills/requirements.txt` fails on it because `markitdown` no longer ships wheels for 3.9.

## Path A — Install as a plugin (recommended for most users)

Add the marketplace to your VS Code settings. Open **Settings → JSON** (`Ctrl+Shift+P` / `⌘⇧P` → *"Preferences: Open User Settings (JSON)"*) and add:

```jsonc
{
  "chat.plugins.enabled": true,
  "chat.useAgentSkills": true,
  "chat.plugins.marketplaces": [
    "https://github.com/cg-open-itg/catalyst.git"
  ]
}
```

Reload VS Code. Open Copilot Chat (`Ctrl+Shift+I` / `⌘⇧I`) → `/plugins` → enable **AI Catalyst**. Done.

No clone required. VS Code pulls skills directly from the repo — you always get the latest `main`.

## Path B — Clone the repo (for contributors editing or adding skills)

```bash
git clone https://github.com/cg-open-itg/catalyst.git
cd catalyst
code .
```

When VS Code opens the folder, Copilot Chat reads `.github/copilot-settings.json` and auto-registers the **AI Catalyst** marketplace. Reload the window if prompted (`Ctrl+Shift+P` / `⌘⇧P` → *"Developer: Reload Window"*).

Open Copilot Chat (`Ctrl+Shift+I` / `⌘⇧I`) → `/plugins` → toggle **AI Catalyst** on.

Editing skills under `skills/` takes effect on the next marketplace refresh — no build step.

## Path C — Claude Code

This repo is also a Claude Code plugin marketplace. Register it once, then install the plugin:

```bash
claude plugin marketplace add cg-open-itg/catalyst
claude plugin install ai-catalyst@catalyst
```

Or from inside a Claude Code session:

```
/plugin marketplace add cg-open-itg/catalyst
/plugin install ai-catalyst@catalyst
```

To enable it for a whole team or repo, commit this to that project's `.claude/settings.json` instead — no per-developer command needed:

```json
{
  "extraKnownMarketplaces": {
    "catalyst": {
      "source": {
        "source": "github",
        "repo": "cg-open-itg/catalyst"
      }
    }
  },
  "enabledPlugins": {
    "ai-catalyst@catalyst": true
  }
}
```

Skills land namespaced as `ai-catalyst:<skill-name>` (e.g. `ai-catalyst:dplc-concierge`). As with Copilot, you don't need to name them — Claude matches natural language to the right skill.

This repo ships exactly that block in its own [`.claude/settings.json`](../.claude/settings.json), so opening the catalyst repo in Claude Code registers and enables the plugin for you — the Claude Code counterpart of Path B. Note it resolves from published `main`, **not** your working tree: if you're editing a skill locally, point the marketplace at your checkout instead (`claude plugin marketplace add /path/to/catalyst`) so you exercise your edits.

Pin to a tag or branch by appending it to the marketplace ref: `claude plugin marketplace add cg-open-itg/catalyst@1.12.0`. Release tags in this repo are **unprefixed** (`1.12.0`, not `v1.12.0`) — see [`release-process.md`](release-process.md#versioning).

> **Why `.claude-plugin/` carries no `version` field — don't add one.**
> Setting `version` in a Claude Code manifest *pins* the plugin: users stop
> receiving updates until that string changes, even as `main` advances. This repo
> ships from `main` with no version pinning (see *Upgrading* below), so both
> `.claude-plugin/` files deliberately omit it and Claude Code tracks the resolved
> commit instead. Adding a `version` would silently freeze every installed copy at
> the last release. Pin via the marketplace ref above instead, which is opt-in per
> user. (Claude Code also reads `plugin.json`'s `version` in preference to the
> marketplace entry's without warning, so setting both is its own trap.)

## Verify

In Copilot Chat (or a Claude Code session), try:

```
I need to plan a new data product
```

The agent should route to the `dplc-concierge` skill and reply with orienting questions. You don't need to name skills explicitly — natural language is matched to the right skill automatically.

## Credentials (optional — unlocks live integrations)

Without credentials the skills still run; they prompt you for context that would otherwise come from live systems. To enable live integration:

1. From the catalyst repo root:
   ```bash
   cp .env.example .env    # if .env.example exists; otherwise create .env
   ```
2. Authenticate to Databricks. **Prefer an interactive OAuth login over a PAT** — it
   is self-serve, needs no secret in a file, and satisfies DBX-SEC-002's preference
   for OAuth:
   ```bash
   databricks auth login --host https://<your-workspace>.cloud.databricks.com
   ```
   This writes a profile to `~/.databrickscfg`, which the Databricks SDK picks up
   automatically — most skills need nothing further. Not sure which workspace is
   yours, or whether you have access? Run `/dplc-preflight`; it lists every
   workspace configured on your machine and verifies access.

   For **non-interactive** use (CI, service-to-service, Model Serving), DBX-SEC-002
   requires OAuth client credentials for a service principal — `DATABRICKS_CLIENT_ID`
   and `DATABRICKS_CLIENT_SECRET`, never a PAT. `/connect-databricks` implements
   this path and will refuse `DATABRICKS_TOKEN` if it is set.

3. Fill in any remaining `.env` values:
   | Variable | Unlocks |
   |---|---|
   | `DATABRICKS_CONFIG_PROFILE` | Selects which `~/.databrickscfg` profile to use |
   | `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET` | Non-interactive / service-principal auth (CI) |
   | `CONFLUENCE_BASE_URL`, `CONFLUENCE_TOKEN` | Live `load-confluence-context` |
4. Install Python deps. `skills/requirements.txt` pins the Capital Group internal PyPI proxy (`cgrepo-aws.capgroup.com`) via `--index-url`, which is **required** — public PyPI is blocked on the corporate network to mitigate supply-chain attacks. All Python deps must resolve through cgrepo.
   ```bash
   pip install -r skills/requirements.txt
   ```

   Configure pip globally so every install on your machine goes through cgrepo (do this once). Add to `~/.pip/pip.conf` (Linux/macOS) or `%APPDATA%\pip\pip.ini` (Windows):
   ```ini
   [global]
   index-url = https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/
   ```

### Does my task need the Databricks CLI installed?

Authenticating (above) is not the whole story. Some skills shell out to the
`databricks` binary, so for those the CLI must actually be **installed**, not just
configured:

| If you are… | You need |
|---|---|
| Exploring or profiling data, or generating documents — `discover-data`, `data-profiling`, `query-table`, `query-catalog`, `profile-columns` | An authenticated profile (or `.env`). No CLI binary required — these go through the SDK. |
| Building or shipping — Asset Bundles, jobs, SQL warehouses, dbt-on-Databricks: `deploy-dab`, `databricks-bundles`, `databricks-jobs`, `configure-sql-warehouse`, `run-dbt-on-databricks`, `setup-databricks-asset-bundle` | **The `databricks` CLI installed.** These invoke `databricks bundle …`; credentials alone will not satisfy them. |
| Running non-interactively — CI, or a Databricks App | OAuth service-principal credentials. No CLI, no interactive login. |

Catalyst targets the **Databricks CLI 0.218 or newer** — the Go binary, whose
`databricks --version` reports `v0.2xx`. Install it with `brew install databricks`
(macOS) or `winget install Databricks.DatabricksCLI` (Windows). If `winget` is
blocked on your machine, see the [Databricks Extension (Windows)](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/405809567) guide.

> **Not a pip install.** The PyPI package named `databricks-cli` is the
> *deprecated legacy* Python CLI and stops at 0.18.0 — a different artifact on a
> different version scheme. Do not try to satisfy this requirement with pip.

Unsure what you have? Run `/dplc-preflight` — it reports your toolchain, every
workspace configured on your machine, whether you have access, and which catalogs
you can see.

Per-system connection guides live in Confluence under [Tool Connection Guides](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/404922470/Tool+Connection+Guides)
— including [Databricks CLI](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/404889380/Databricks+CLI),
[Confluence](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/404922031/Confluence),
and [Jira](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/404987416/Jira).
**Dremio is not supported** by Catalyst — the Dremio guide in that space describes
legacy infrastructure and should be ignored.

## Internal artifact registries (required)

Public package repositories are **blocked on the Capital Group corporate network** to mitigate supply-chain attacks against open-source registries. Every install command, Dockerfile `FROM`, package config file, and CI step — whether installing this repo's own deps or anything emitted by a skill — must route through the internal Nexus mirrors below.

| Ecosystem | Internal URL |
|---|---|
| pip (PyPI) | `https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` *(also reachable as `https://cgrepo.capgroup.com/repository/cgpypi/simple/` — same Nexus, mirrored hostnames)* |
| conda | `https://cgrepo-aws.capgroup.com/repository/conda-proxy/` |
| npm | `https://cgrepo-aws.capgroup.com/repository/cgnpm/` |
| Maven (releases) | `https://cgrepo-aws.capgroup.com/repository/cgmaven/` |
| Maven (snapshots) | `https://cgrepo-aws.capgroup.com/repository/maven-snapshots/` |
| NuGet | `https://cgrepo-aws.capgroup.com/repository/cgnuget-v3/` |
| Docker | `cgregistry-aws.capgroup.com/<image>:<tag>` |

Authoritative source: [`cg-open-itg/harness-hub` → `docs/technical-documentation/artifacts-repository/artifacts-consuming-examples.md`](https://github.com/cg-open-itg/harness-hub/blob/main/docs/technical-documentation/artifacts-repository/artifacts-consuming-examples.md).

### Patterns to use

- **`requirements.txt`** — first line: `--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`
- **`pip install` in shell/CI** — pass `--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` or rely on a configured `pip.conf`
- **`Dockerfile`** — `FROM cgregistry-aws.capgroup.com/python:3.11-slim` (never `FROM python:3.11-slim`)
- **`package.json` projects** — commit a `.npmrc` with `registry=https://cgrepo-aws.capgroup.com/repository/cgnpm/`
- **`pom.xml` / `build.gradle`** — declare the cgmaven repository (see harness-hub doc)
- **`.condarc`** — `channels: [https://cgrepo-aws.capgroup.com/repository/conda-proxy/]` with `default_channels: []`

### Diagnostic — how a missed re-pointing shows up

When a tool still points at a public registry, the corporate block surfaces as a **404 (or connection refused / connection timeout) against the public host** — not as a "package not found" error from the mirror:

- `pypi.org` / `files.pythonhosted.org` → 404 or timeout in pip output
- `registry.npmjs.org` → 404 or `ETIMEDOUT` in npm output
- `registry-1.docker.io` / `auth.docker.io` → 404 or `dial tcp: i/o timeout` in `docker pull`
- `repo.maven.apache.org` / `repo1.maven.org` → 404 or timeout in `mvn`
- `repo.anaconda.com` → 404 in `conda install`

If you see one of these against a public host, the fix is **not** to find a different package — it's to re-point the tool at cgrepo. Confirm by greping the failing config (`pip.conf`, `.npmrc`, `Dockerfile`, `pom.xml`, `.condarc`, `requirements.txt`, CI workflow) for `cgrepo` and the corresponding host above.

## Upgrading

- **VS Code (Paths A/B)** — refreshes the marketplace on window reload / plugin refresh. You always pull the latest `main`. No version pinning.
- **Claude Code (Path C)** — `claude plugin marketplace update catalyst` (or `/plugin marketplace update catalyst`) re-fetches the registry, then `claude plugin update ai-catalyst@catalyst`.

See [`CHANGELOG.md`](../CHANGELOG.md) for release notes.

## Troubleshooting

### Plugin doesn't appear in `/plugins`
- Confirm `chat.plugins.enabled: true` is in user settings (not workspace settings) — **Path A only**
- If using **Path B**, confirm `.github/copilot-settings.json` exists in the repo root and you opened the repo (not a parent/sibling folder) as the workspace
- Reload window (`Ctrl+Shift+P` / `⌘⇧P` → *"Developer: Reload Window"*)
- Check the Copilot / marketplace output channel for fetch errors

### Plugin doesn't appear in Claude Code
- `claude plugin marketplace list` — confirm `catalyst` is registered; if it isn't, `claude plugin marketplace add cg-open-itg/catalyst`
- `claude plugin list` — confirm `ai-catalyst@catalyst` is installed and enabled
- Restart the session: plugin installs and updates apply on restart, not mid-session
- Validate from a checkout — note the path selects *which* manifest is checked:
  - `claude plugin validate .` → the **marketplace** manifest
  - `claude plugin validate .claude-plugin/plugin.json` → the **plugin** manifest and its discovered skills (expect `Skills (103)`)
  - Both report *"Validation passed with warnings"*. The two warnings are expected and deliberate: `No version specified` (see the note in Path C — adding one would freeze updates) and `CLAUDE.md at the plugin root is not loaded as project context`. **Don't add `--strict`** to either form; it turns both advisories into failures.

### SSO redirect / 403 errors when marketplace tries to clone
- Capital Group enterprise SSO requires your GitHub credentials to be authorized for the `cg-open-itg` org. Easiest fix:
  ```bash
  gh auth login --hostname github.com --web
  gh auth setup-git
  git ls-remote https://github.com/cg-open-itg/catalyst.git   # should succeed silently
  ```

### Skills produce generic output instead of real data
- You don't have credentials configured — fill in `.env` (see Credentials section above)

### `pip install` returns 404 against `pypi.org` (or `files.pythonhosted.org`)
- That's the corporate network block firing, not a missing package. Public PyPI is blocked org-wide to mitigate supply-chain attacks. Re-point pip at the internal mirror — either pass `--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` on the command, or set it once in `~/.pip/pip.conf` (see step 3 of *Credentials* above).
- The same pattern applies to npm (`registry.npmjs.org`), Docker Hub (`registry-1.docker.io`), and Maven Central (`repo.maven.apache.org`) — a 404 / connection refused / timeout against the public host means the tool hasn't been re-pointed. See the *Internal artifact registries* section above for the full ecosystem mapping.

### Want to uninstall
- **Path A**: remove the entry from `chat.plugins.marketplaces` in settings.json and reload
- **Path B**: remove the catalyst repo from your workspace; VS Code stops loading skills
- **Path C**: `claude plugin uninstall ai-catalyst@catalyst`, then `claude plugin marketplace remove catalyst`

## Questions

Open an issue in [`cg-open-itg/catalyst`](https://github.com/cg-open-itg/catalyst/issues) or ping the EDO team.
