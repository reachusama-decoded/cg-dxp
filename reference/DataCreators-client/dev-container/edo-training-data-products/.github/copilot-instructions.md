# Copilot Instructions for This Repo

This repository is used by people with a wide range of technical backgrounds.
Optimize for simplicity first across all repo questions.

## Execution Environment — Run In The Devcontainer, Not The Host (Agents/Automation)

**The repo toolchain (`mise`, dbt-core at `/opt/venv`, the `databricks` CLI, `astro`) exists ONLY inside the VS Code devcontainer — not on the host.** The host may only have the dbt Cloud CLI and will make `mise run …`, `dbt`, `astro`, and `mise run challenge:*` commands fail or mislead.

- **Detect where you are.** If your shell is on the host (e.g. macOS/Windows, cwd not under `/workspaces/…`, or `command -v dbt` resolves to a non-`/opt/venv` path), you are NOT in the devcontainer.
- **Exec into the running devcontainer for every repo command.** Find it with `docker ps` (image `vsc-edo-training-data-products-*`) and run, e.g.:
  ```bash
  docker exec <container> bash -lc 'cd /workspaces/edo-training-data-products && mise run challenge:verify 03'
  ```
  or `devcontainer exec --workspace-folder <repo-path> bash -lc '<command>'`.
- The container **bind-mounts the repo** at `/workspaces/edo-training-data-products`, so your host-side commits/edits are visible inside immediately (no copy needed).
- **Databricks runs happen in the container too.** Before any dbt/challenge/DAG run, verify auth there: `databricks auth describe --profile DEFAULT`. If it fails, set up auth in the container (OAuth: `mise run setup:databricks`; when an automated agent has no browser for OAuth, use the PAT fallback `mise run setup:databricks --pat`, which reads `DATABRICKS_HOST/TOKEN/HTTP_PATH` from env or `.devcontainer/.env`).
- **`challenge:verify NN` is the challenge gate** (not a bare `bash verify.sh`), and the live Airflow steps need the astro stack up (`astro dev start`) — both run inside the container.

## Core Behavior

- Default to the simplest working path.
- Give the minimum number of steps needed to help the user succeed.
- Add complexity only when it is necessary to unblock the next step.
- Prefer one recommended path over multiple alternatives unless the first path is blocked.
- Explain jargon only when it appears in the answer and is needed to continue.

## Adapting to the User

- Do not start by asking the user to rate their technical skill unless that choice will materially change the next step.
- Start with a simple answer that works for a broad audience.
- If the user seems blocked, confused, or asks for more detail, then increase the level of explanation gradually.
- When a user asks for simplicity, avoid giving advanced background unless they ask for it.

## Response Style

- Use short, direct language.
- Keep explanations brief and practical.
- Prefer short prose over long lists when possible.
- Internally keep the reason for choosing a path, but do not include that reason unless the user asks for it.
- When giving steps, keep them ordered and copy-pasteable.
- Prefer UI-based guidance when that is clearly the easier path for less technical users.
- Prefer a simple command-line workflow when it is more reliable or simpler than the UI.
- Say where a command should be run.
- If a prerequisite is missing, say exactly what is missing and the next action to take.

## Repo-Specific Guidance

- For a first dbt example, prefer the `asset_reference_data` data product.
- For the smallest first run, prefer the `currency` models before suggesting a full project run.
- Prefer the repo's supported dev container workflow before suggesting a custom local machine setup.
- Use the repo's documented commands and entrypoints from `GETTING_STARTED.md`, `.devcontainer/README.md`, and `.mise.toml`.
- Do not present multiple setup paths unless the recommended path is blocked in the user's environment.

## Databricks Auth Contract (Agent Default)

### Prove the user is deauthenticated BEFORE prompting them

**Do not ask the user to re-authenticate until you have shown they actually need to.** Most
"auth failures" in this repo are *delivery* bugs — the user is authenticated, but the token
never reached the shell, container or process that failed. Prompting them then is wrong, it
wastes their time, and it hides the real defect. Run this three-step check first:

```bash
# 1. Does the CLI have a valid profile?  (must go through `mise exec --`)
mise exec -- databricks auth describe --profile DEFAULT

# 2. DECISIVE: can it mint a token RIGHT NOW? This exercises the refresh token.
mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json'

# 3. What did the failing process actually receive?
mise exec -- sh -c 'echo "${DBT_ACCESS_TOKEN:-<EMPTY>}"' | cut -c1-8
```

Interpretation:

| Observation | Meaning | Action |
|---|---|---|
| Step 2 returns an `access_token` | **User IS authenticated** | **Do NOT prompt.** Fix delivery. |
| Step 2 fails with a login/expiry error | Genuinely deauthenticated | Prompt (below) |
| Step 3 is `MISSING_run__mise_run_setup_databricks` or empty, but step 2 works | Delivery bug | Fix delivery, do not prompt |
| `databricks: command not found` / `No version is set for shim` | **Not an auth failure at all** — you omitted `mise exec --` | Re-run the command correctly |

Delivery fixes, none of which need the user: `/etc/profile.d/mise-init.sh` missing →
`mise run setup:mise`; `/etc/profile.d/databricks-env.sh` missing →
`mise run setup:databricks`; shell opened before authentication, or cwd outside the repo
(mise's env is directory-scoped) → `exec bash -l` or `cd` into the repo. Background:
`docs/rca/2026-08-04-databricks-env-not-propagated-to-shells.md` and
`docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md`.

Note that `databricks auth describe` reads `~/.databrickscfg`, **not** the variable dbt uses,
so it can report success while dbt fails — and vice versa. Step 2 is the one that settles it.

### If the check shows they really are deauthenticated

- **STOP and prompt the user immediately — do not abandon, skip, or defer the task, and never treat auth as the reason the work "can't be done."** Agents tend to blame authentication to get out of their intended work; that is not acceptable here. Tell the user exactly how to fix it and wait for them:
	- OAuth (default): ask them to run `mise run setup:databricks` and complete the browser login pop-up.
	- PAT fallback: ask them to run `mise run setup:databricks --pat` and paste a valid token.
	- Then verify with `databricks auth describe --profile DEFAULT` and resume the original task.
	- Only after you have prompted the user and given them a chance to fix it may auth be called a blocker. Prompting the user is the FIRST action on any auth failure, before any other troubleshooting.
- Treat Databricks OAuth as the required default path for this repo.
- Before any dbt command, ensure auth is configured and valid by running `mise exec -- databricks auth describe --profile DEFAULT`. Remember this checks the CLI profile, not the token dbt will send.
- If credentials are missing, run `mise run setup:databricks` in the dev container before continuing.
- Do not require `.devcontainer/.env` for OAuth bootstrap. It is optional and may prefill prompts only.
- During OAuth bootstrap, collect non-secret workspace settings interactively when prompted (`DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_CATALOG`, `DATABRICKS_SCHEMA`).
- For local Airflow usage, require Databricks setup before `astro dev start` so `AIRFLOW_VAR_DATABRICKS_JOB_PREFIX` is captured at container startup.
- If Astro was started before Databricks setup, rerun `mise run setup:databricks` and then `astro dev restart --wait 5m` before DAG troubleshooting.
- Do not suggest PAT/token-first setup unless OAuth is blocked in the user's environment.
- Use PAT fallback only when the user explicitly requests it or OAuth is unavailable, via `mise run setup:databricks --pat`.
- When dbt fails with auth-related errors, run the three-step check at the top of this section first, then prompt only if step 2 fails; fix auth, and rerun; do not proceed to unrelated troubleshooting, and do not silently give up on the task, until auth is healthy.
- For first-run validation after auth setup, use this sequence:
	1. `databricks auth describe --profile DEFAULT`
	2. `dpc-check`
	3. `bash scripts/verify-with-databricks.sh`
	4. `mise run dbt:run asset_reference_data -- --select currency`

## When Helping Someone Run dbt

- Start with the shortest path to a successful first run.
- Check only the prerequisites required for the immediate next step.
- Avoid dumping every possible setup detail up front.
- Introduce Databricks credentials, dev containers, `mise`, or source cloning only when needed for the next action.
- Prefer a small validation step before suggesting a broader run.

## Good Defaults

- Recommend one next command at a time when the user is onboarding.
- Briefly explain why a step matters only when the user is likely to be confused or asks for the reason.
- Treat low-friction tools like `gh` CLI as acceptable defaults when they are more consistent than a GUI and the command is simple.
- If the user asks for brainstorming or process design, prioritize clarity, user friction reduction, and progressive disclosure.

## Decision Rule

- Choose the lowest-friction path that is likely to work.
- Prefer the UI when it is the clearest and simplest option.
- Prefer a short command when it is easier to follow or more reliable than the UI.
- Do not surface the tradeoff analysis unless the user asks.

## Example Patterns

- For a first dbt run, start with the repo's recommended path, prefer the dev container workflow, and suggest the smallest example before a full project run.
- For GitHub authentication, prefer the path that is most reliable for this repo's users. A short `gh` CLI flow is acceptable when it is more consistent than GitHub Desktop.
- For setup help, give the next single action first. Only introduce follow-on prerequisites after the user completes or confirms the current step.

## Avoid

- Large walls of setup text.
- Multiple competing recommendations in the same answer.
- Unnecessary acronyms without explanation.
- Asking several questions before providing any useful direction.
- Giving advanced troubleshooting before the basic path has been tried.
## Challenges — Helping vs Validating

### When someone is working through a challenge

- Help them **in place**. Debug their code, explain the error, point at the guide section.
- **Never run `mise run challenge:reset <NN>`** to "start clean". It deletes their authored
  work, including files they created from scratch. Suggest it only if they explicitly ask to
  start over, and say what it will delete.

### When the maintainer asks to validate the challenges

Phrases like "test the challenges", "run challenge 03 as a trainee", or "check the challenges
still work" mean the maintainer workflow: use the `challenge-trainee-runs` skill
(`.github/skills/challenge-trainee-runs/SKILL.md`). It covers the subagent brief, the artifact-based
audit, the run ledger, and the one-at-a-time resource limits.

If it is ambiguous which of the two is being asked for, ask before doing anything destructive.
