from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_setup_task_points_to_oauth_script() -> None:
    mise = _read(".mise.toml")
    assert 'setup-databricks-dbt.sh' in mise
    assert '[tasks."setup:databricks"]' in mise
    assert 'flag "--pat"' in mise

def test_setup_script_exists_and_mise_references_it() -> None:
    script = REPO_ROOT / ".devcontainer" / "setup-databricks-dbt.sh"
    assert script.exists()
    assert "setup-databricks-dbt.sh" in _read(".mise.toml")

def test_setup_script_ignores_template_tokens() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "your-token-here" in script
    assert "replace-with-your-token" in script
    assert 'if is_placeholder_token "${DATABRICKS_TOKEN:-}"; then' in script
    assert "FORCE_PAT_SETUP" in script
    assert "--pat" in script
    assert 'if [ -n "${DATABRICKS_TOKEN:-}" ]; then' not in script

def test_setup_script_keeps_real_training_defaults() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "DATABRICKS_HOST:https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com" not in script
    assert "DATABRICKS_HTTP_PATH:/sql/1.0/warehouses/267dd55b7f7395ce" not in script
    assert "read_required" in script
    assert "Databricks workspace URL" in script

def test_host_prompt_defaults_to_training_workspace_for_pat_and_oauth() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'DEFAULT_TRAINING_DATABRICKS_HOST="https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com"' in script
    assert script.count('read_required DATABRICKS_HOST "Databricks workspace URL (e.g. https://cg-db-...cloud.databricks.com)" "$DEFAULT_TRAINING_DATABRICKS_HOST"') == 2

def test_pat_setup_prompts_for_missing_values() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'if [ "$use_pat_setup" -eq 1 ]; then' in script
    assert 'read_required DATABRICKS_HOST "Databricks workspace URL' in script
    assert 'pick_warehouse || read_required DATABRICKS_HTTP_PATH' in script
    assert 'read_secret_required DATABRICKS_TOKEN "Databricks PAT token"' in script
    assert 'Databricks PAT setup requires DATABRICKS_HOST' not in script

def test_pat_setup_validates_token_before_writing_config() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'if [ -z "${DATABRICKS_BIN:-}" ] || [ ! -x "$DATABRICKS_BIN" ]; then' in script
    assert '_resolve_databricks_bin()' in script
    assert 'find "$HOME/.local/share/mise/installs/databricks-cli"' in script
    assert 'DATABRICKS_BIN=$(_resolve_databricks_bin)' in script
    assert 'DATABRICKS_AUTH_TYPE=pat' not in script
    assert 'curl -sS -o /tmp/databricks-pat-validate.json -w "%{http_code}"' in script
    assert 'Authorization: Bearer $DATABRICKS_TOKEN' in script
    assert '$DATABRICKS_HOST/api/2.0/preview/scim/v2/Me' in script
    assert 'Databricks PAT token authentication failed' in script
    assert 'PAT validation details:' in script
    assert 'Set DATABRICKS_TOKEN to a valid PAT and rerun setup with --pat.' in script
    assert '"${DATABRICKS_BIN:-databricks}" warehouses list --output json' in script
    assert 'if ! validate_pat_token; then' in script
    assert 'read_secret_required DATABRICKS_TOKEN "Databricks PAT token (retry)"' in script

def test_pat_setup_prompts_token_before_warehouse_pick() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    token_prompt = script.index('read_secret_required DATABRICKS_TOKEN "Databricks PAT token"')
    warehouse_pick = script.index('pick_warehouse || read_required DATABRICKS_HTTP_PATH')
    assert token_prompt < warehouse_pick

def test_setup_script_handles_databrickscfg_directory_collision() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'ensure_databrickscfg_path' in script
    assert 'exists as a directory, but Databricks CLI requires it to be a file.' in script
    assert 'rmdir "$databrickscfg"' in script

def test_oauth_tokens_are_refreshed_without_disk_persistence() -> None:
    setup = _read(".devcontainer/setup-databricks-dbt.sh")
    mise_env = _read(".mise/env.sh")

    assert 'export DPC_DATABRICKS_AUTH_MODE=oauth' in setup
    assert 'export DATABRICKS_AUTH_TYPE=' not in setup
    assert 'export DBT_ACCESS_TOKEN=' not in setup
    assert 'export DATABRICKS_TOKEN=' not in setup
    assert 'databricks auth token' not in setup
    assert 'if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then' in mise_env
    assert 'auth token --profile DEFAULT' in mise_env

def test_oauth_shell_refresh_does_not_export_databricks_token_env() -> None:
    mise_env = _read(".mise/env.sh")
    assert 'export DBT_ACCESS_TOKEN="$_oauth_token"' in mise_env
    assert 'export DATABRICKS_TOKEN="$_oauth_token"' not in mise_env

def test_mise_env_avoids_databricks_shim_recursion() -> None:
    mise_env = _read(".mise/env.sh")
    assert '_resolve_databricks_bin()' in mise_env
    assert '/shims/databricks' in mise_env
    assert 'installs/databricks-cli' in mise_env
    assert '"$_databricks_bin" auth token' in mise_env

# Why: mise cannot propagate an `unset` from a `_.source` script back into an
# already-initialised shell (proven live: a var mise previously exported keeps its
# old value forever once the script stops exporting it). So a failed OAuth mint that
# merely unsets DBT_ACCESS_TOKEN leaves the PREVIOUS, now-EXPIRED token in the shell.
# dbt then sends the expired token and fails with an opaque 401/403 instead of hitting
# the profile's actionable sentinel. The mint must therefore always EXPORT an explicit
# value -- never rely on unset to signal failure.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.

DBT_TOKEN_SENTINEL = "MISSING_run__mise_run_setup_databricks"

def test_failed_oauth_mint_exports_sentinel_instead_of_unsetting() -> None:
    mise_env = _read(".mise/env.sh")
    assert f'export DBT_ACCESS_TOKEN="{DBT_TOKEN_SENTINEL}"' in mise_env, (
        "a failed OAuth mint must overwrite DBT_ACCESS_TOKEN with the sentinel; "
        "unset cannot be propagated by mise and would strand an expired token"
    )

def test_mise_env_never_relies_on_unset_to_clear_the_dbt_token() -> None:
    mise_env = _read(".mise/env.sh")
    for stranding in (
        "[ -n \"${DBT_ACCESS_TOKEN:-}\" ] || unset DBT_ACCESS_TOKEN",
        "unset DBT_ACCESS_TOKEN DATABRICKS_TOKEN",
    ):
        assert stranding not in mise_env, (
            f"{stranding!r} cannot clear a stale token: mise ignores unset from "
            "_.source scripts, so the previous expired token survives"
        )

def test_oauth_mint_retries_before_giving_up() -> None:
    mise_env = _read(".mise/env.sh")
    assert "_mint_attempt" in mise_env, "the OAuth mint must retry transient failures"

def test_profiles_sentinel_matches_mise_env_sentinel() -> None:
    profile = _read("challenges/v1/02-dbt-pipeline/dbt_profiles/profiles.yml")
    assert DBT_TOKEN_SENTINEL in profile, (
        "the challenge profile sentinel must match the one .mise/env.sh exports"
    )

# Why: mise executes a `_.source` script ONCE per shell session and caches the result;
# it re-runs only when the file's mtime changes, NOT on every prompt (proven live:
# 4 prompt hooks -> 1 execution; `touch env.sh` -> 2). So .mise/env.sh alone can never
# keep a ~1h OAuth token fresh in a long-lived terminal. The refresh must run from the
# shell's own PROMPT_COMMAND, where `export` applies directly.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.

def test_shell_prompt_refreshes_databricks_oauth_token() -> None:
    setup = _read(".devcontainer/utils/setup-mise.sh")
    assert "_refresh_databricks_token" in setup, (
        "shells must refresh the OAuth token from PROMPT_COMMAND; mise's cached "
        "_.source evaluation cannot do it"
    )
    assert "PROMPT_COMMAND=\"_refresh_databricks_token" in setup, (
        "the refresh must be wired into PROMPT_COMMAND so it runs on every prompt"
    )
    assert "auth token --profile DEFAULT" in setup

def test_shell_token_refresh_is_gated_on_expiry() -> None:
    setup = _read(".devcontainer/utils/setup-mise.sh")
    # A network call on every prompt would make the shell visibly slow; the refresh
    # must short-circuit on a cheap local comparison, and must keep a minimum
    # re-check interval so it cannot mint on every prompt once inside the expiry
    # margin (the Databricks CLI serves a cached token until it is nearly expired).
    assert "_DPC_TOKEN_NEXT_CHECK" in setup
    assert "EPOCHSECONDS" in setup
    assert 'if [ "$next" -lt "$((now + 60))" ]; then' in setup, (
        "the refresh must floor its re-check interval to avoid minting every prompt"
    )

def test_shell_token_refresh_never_leaves_an_expired_token() -> None:
    setup = _read(".devcontainer/utils/setup-mise.sh")
    assert f'export DBT_ACCESS_TOKEN="$_DPC_TOKEN_SENTINEL"' in setup, (
        "a failed refresh must overwrite the token with the sentinel, never leave the "
        "previous expired credential in the shell"
    )
    assert f'_DPC_TOKEN_SENTINEL="{DBT_TOKEN_SENTINEL}"' in setup


def _refresher_code(setup: str) -> str:
    """Body of _refresh_databricks_token with comment lines removed.

    Why: the function's comments mention the same identifiers as its code, so a raw
    ``index()`` finds the prose first and produces a false ordering result.
    """
    body = setup.split("_refresh_databricks_token() {", 1)[1].split("\n}", 1)[0]
    return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))


def test_shell_token_refresh_is_oauth_only() -> None:
    # The OAuth mint must no-op in PAT mode. The guard is no longer the first statement --
    # the contract file is re-read before it, so a terminal opened before authentication
    # can recover (see test_token_refresher_recovers_terminals_opened_before_authentication)
    # -- so assert the behaviour rather than a literal line position.
    setup = _read(".devcontainer/utils/setup-mise.sh")
    body = _refresher_code(setup)
    assert 'DPC_DATABRICKS_AUTH_MODE:-}" != "oauth"' in body, (
        "the refresh must no-op when the auth mode is not oauth (PAT)"
    )
    guard = body.split('DPC_DATABRICKS_AUTH_MODE:-}" != "oauth"', 1)[1]
    assert "return 0" in guard.split("fi", 1)[0], "the non-oauth branch must return early"
    assert "databricks auth token" in body or "auth token" in body

# Why: PROMPT_COMMAND fires when the prompt is DRAWN, i.e. after the previous command
# finished. A shell then sits idle at that prompt, and if the token expires during
# that window the next command the user types still runs with the stale token and
# fails 403 -- re-running it then "works" because the refresh happened in between.
# A DEBUG trap fires immediately BEFORE each command, closing that gap.

def test_token_refresh_runs_before_each_command_not_only_after() -> None:
    setup = _read(".devcontainer/utils/setup-mise.sh")
    assert "trap '_dpc_preexec' DEBUG" in setup, (
        "the refresh must run BEFORE a command via a DEBUG trap; PROMPT_COMMAND alone "
        "leaves the first command after an idle prompt using an expired token"
    )
    assert "_dpc_preexec()" in setup
    # Must not cancel the user's command under `shopt -s extdebug`, where a non-zero
    # return from the DEBUG trap skips the command.
    body = setup.split("_dpc_preexec() {", 1)[1].split("\n}", 1)[0]
    assert "return 0" in body

def test_preexec_skips_completion_and_prompt_command() -> None:
    setup = _read(".devcontainer/utils/setup-mise.sh")
    body = setup.split("_dpc_preexec()", 1)[1]
    assert 'COMP_LINE' in body, "preexec must not fire during completion"
    assert '"$BASH_COMMAND" = "$PROMPT_COMMAND"' in body, (
        "preexec must not re-enter on the PROMPT_COMMAND invocation"
    )

def test_setup_wires_databricks_http_path_to_dbt() -> None:
    for path in (
        ".devcontainer/setup-databricks-dbt.sh",
        ".devcontainer/utils/setup-databricks-config.sh",
        ".devcontainer/utils/normalize-env.sh",
    ):
        assert 'DBT_HTTP_PATH' in _read(path), f'{path} must export DBT_HTTP_PATH'

def test_setup_contract_exports_databricks_catalog_and_schema() -> None:
    for path in (
        ".devcontainer/setup-databricks-dbt.sh",
        ".devcontainer/utils/setup-databricks-config.sh",
    ):
        content = _read(path)
        assert 'DATABRICKS_CATALOG' in content, f'{path} must export DATABRICKS_CATALOG'
        assert 'DATABRICKS_SCHEMA' in content, f'{path} must export DATABRICKS_SCHEMA'

def test_setup_script_handles_oauth_callback_port_collisions() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'clear_oauth_callback_port' in script
    assert 'ss -ltnp' in script
    assert 'databricks auth login' in script


def test_databricks_setup_guarantees_env_reaches_shells() -> None:
    # Why: setup-databricks-dbt.sh writes ~/.config/dpc/databricks.env, but nothing loads
    # that file unless /etc/profile.d/mise-init.sh exists (mise activate -> .mise/env.sh ->
    # databricks.env). That hook is installed by the devcontainer postCreate, so
    # authenticating silently assumed it was present. When it was not, auth reported
    # success while every shell exported a BLANK DBT_CATALOG/DBT_SCHEMA -- and `astro dev
    # start` baked those blanks into Airflow, killing the DAG with `Invalid catalog name`.
    # Authentication must be sufficient on its own: install the hook if missing, then
    # PROVE a fresh login shell sees the values rather than assuming it.
    # See docs/rca/2026-08-04-databricks-env-not-propagated-to-shells.md.
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "/etc/profile.d/mise-init.sh" in script, (
        "setup must ensure the shell hook that loads databricks.env exists"
    )
    assert "utils/setup-mise.sh" in script, (
        "setup must install the hook itself when it is missing, not just warn"
    )
    # The verification probe must use a CLEAN shell. A plain `bash -lc` inherits the
    # parent's exports and would report success even with the hook absent.
    assert "env -i" in script, (
        "the propagation probe must run in a clean environment; a plain login shell "
        "inherits exported values and produces a false pass"
    )
    probe = script.split("# Verify the contract end to end", 1)[1]
    assert "DBT_CATALOG" in probe and "DBT_SCHEMA" in probe
    # The probe must run from OUTSIDE the repo. mise's environment is directory-scoped,
    # so a probe run inside the repo passes even when shells elsewhere are blank.
    assert "cd /" in probe, "the propagation probe must run from outside the repo"


def test_databricks_setup_writes_profile_d_for_any_directory() -> None:
    # Why: databricks.env is reachable only through mise, whose environment is
    # directory-scoped (measured: 5 DBT_ vars inside the repo, 0 outside). Publishing to
    # /etc/profile.d makes the settings present in every login/interactive shell in any
    # directory. It SOURCES databricks.env rather than copying its values: that file is
    # mode 600 and in PAT mode carries DBT_ACCESS_TOKEN, so copying would publish a
    # credential into a world-readable (644) file.
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "/etc/profile.d/databricks-env.sh" in script, (
        "setup must publish the settings outside mise's directory scope"
    )
    body = script.split("if profile_env=$(mktemp)", 1)[1].split("\nEOF\n", 1)[0]
    assert ".config/dpc/databricks.env" in body, (
        "profile.d must source the single source of truth, not duplicate it"
    )
    for secret in ("DBT_ACCESS_TOKEN=", "DATABRICKS_TOKEN="):
        assert secret not in body, (
            f"{secret} must not be written into the world-readable profile.d file"
        )


def test_token_refresher_recovers_terminals_opened_before_authentication() -> None:
    # Why: postCreate runs `mise run setup`, which does NOT authenticate -- Databricks auth
    # is a separate interactive `mise run setup:databricks`. So every terminal the
    # devcontainer opens at creation predates authentication and has no
    # DPC_DATABRICKS_AUTH_MODE. The refresher used to test that variable FIRST and return
    # immediately, and mise executes .mise/env.sh only once per shell session, so such a
    # terminal could never obtain DBT_ACCESS_TOKEN for its entire life while a terminal
    # opened later worked fine -- the "sometimes the token is defined, sometimes not"
    # inconsistency. Measured: pre-fix the token stayed <unset> after the user
    # authenticated; post-fix it became a real 795-char token in the same shell.
    setup = _read(".devcontainer/utils/setup-mise.sh")
    body = _refresher_code(setup)
    gate_idx = body.index("_DPC_TOKEN_NEXT_CHECK")
    source_idx = body.index(".config/dpc/databricks.env")
    mode_idx = body.index("DPC_DATABRICKS_AUTH_MODE")
    assert source_idx < mode_idx, (
        "the refresher must re-read databricks.env BEFORE testing the auth mode, or a "
        "terminal opened before authentication can never recover"
    )
    assert gate_idx < source_idx, (
        "the cheap time gate must stay first so the file is not re-read on every command"
    )


def test_agents_must_prove_deauthentication_before_prompting() -> None:
    # Why: agents have repeatedly asked the user to re-authenticate when the user was already
    # authenticated and the real fault was delivery -- the token never reached the shell,
    # container or process that failed (missing /etc/profile.d hook, a terminal opened before
    # `setup:databricks`, or a cwd outside the repo, since mise's env is directory-scoped).
    # `databricks auth describe` reads ~/.databrickscfg, NOT the variable dbt sends, so it can
    # report success while dbt fails and vice versa. Only `databricks auth token` exercises the
    # refresh token and settles whether the user is really deauthenticated.
    instructions = _read(".github/copilot-instructions.md")
    assert "databricks auth token" in instructions, (
        "the auth contract must include the decisive mint check before prompting the user"
    )
    probe = instructions.split("Prove the user is deauthenticated BEFORE prompting", 1)
    assert len(probe) == 2, "the auth contract must lead with the prove-before-prompting rule"
    body = probe[1]
    # A shim/PATH error is not an auth failure; agents have misread it as one.
    assert "command not found" in body or "No version is set for shim" in body, (
        "must tell agents that a missing `databricks` binary is not an auth failure"
    )
    # The delivery fixes must be named, or 'do not prompt' leaves the agent stuck.
    assert "setup:mise" in body and "directory-scoped" in body, (
        "must name the delivery fixes that resolve this without involving the user"
    )


def test_no_doc_still_tells_agents_to_prompt_first_on_any_auth_failure() -> None:
    # Why: the rule only works if nothing contradicts it. docs/agent-runbook.md carried the old
    # "prompt the user FIRST on any auth-stage failure" wording long after the contract changed,
    # so an agent reading the runbook got exactly the behaviour the contract forbids. Documenting
    # a rule in one place is not enough when several docs advise agents on the same topic.
    for path in ("docs/agent-runbook.md", ".devcontainer/TROUBLESHOOTING.md"):
        text = _read(path)
        assert "prompt the user FIRST — do not skip or abandon the task, and do not blame auth to avoid the work. It is almost always" not in text, (
            f"{path} still tells agents to prompt before proving deauthentication"
        )
        assert "databricks auth token" in text, (
            f"{path} must point at the decisive mint check, not `auth describe` alone"
        )


def test_gh_auth_bootstrap_can_never_prompt() -> None:
    # Why: setup-gh-auth.sh writes /etc/profile.d/gh-auth.sh, which runs on EVERY login
    # shell. `git credential fill` falls back to asking for a username/password when no
    # credential helper can answer -- which is the normal case in this container, because
    # the VS Code Dev Containers helper proxies to a host-side binary that does not exist
    # here. git writes that prompt to /dev/tty, so a caller's `2>/dev/null` does not
    # suppress it and the login shell blocks on input.
    #
    # That is why `mise run setup:databricks` asked GitHub questions: it spawns `bash -lc`
    # to verify env propagation, which sources this file. The bootstrap is best-effort --
    # every call site tolerates failure -- so it must fail silently, never prompt.
    script = _read(".devcontainer/utils/setup-gh-auth.sh")
    code_lines = [
        line for line in script.splitlines() if not line.lstrip().startswith("#")
    ]
    fill_calls = sum(line.count("git credential fill") for line in code_lines)
    assert fill_calls > 0, "expected setup-gh-auth.sh to seed gh from git credentials"
    guarded = sum(
        line.count("GIT_TERMINAL_PROMPT=0 git credential fill") for line in code_lines
    )
    assert guarded == fill_calls, (
        f"{fill_calls - guarded} of {fill_calls} `git credential fill` calls in "
        "setup-gh-auth.sh are missing the GIT_TERMINAL_PROMPT=0 guard; an unguarded call "
        "will block every login shell on a GitHub username prompt"
    )