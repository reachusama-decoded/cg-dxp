#!/bin/bash
# Seeds this shell's environment. mise evaluates a `_.source` script ONCE per shell
# session and caches the result -- it re-runs this file only when the file's mtime
# changes, NOT on every prompt. Do not rely on this script to refresh anything
# short-lived: the Databricks OAuth token is kept current by _refresh_databricks_token
# in /etc/profile.d/mise-init.sh, which runs from PROMPT_COMMAND inside the shell.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.
_sanitize_branch_name() {
	printf '%s' "$1" | sed -E 's|[/.[:space:]-]+|_|g; s/[^[:alnum:]_]/_/g; s/^_+//; s/_+$//'
}

_update_bundle_branch_vars() {
	local branch sanitized_branch

	branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
	sanitized_branch=$(_sanitize_branch_name "$branch")
	if [[ -z "$sanitized_branch" ]]; then
		sanitized_branch="main"
	fi
	export BUNDLE_VAR_git_branch="$sanitized_branch"
}

_update_bundle_branch_vars

# Fix CA bundle path for this container (overrides incorrect /etc/environment value)
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Databricks/dbt environment variables for local development.
# Prefer the generated shell normalization script first, then the OAuth/PAT contract file.
if [ -f "/etc/profile.d/databricks-env.sh" ]; then
  source /etc/profile.d/databricks-env.sh
fi
if [ -f "$HOME/.config/dpc/databricks.env" ]; then
  source "$HOME/.config/dpc/databricks.env"
fi

_resolve_databricks_bin() {
  local databricks_bin install_bin
  databricks_bin=$(command -v databricks 2>/dev/null || true)

  # Why: during mise's env evaluation (hook-env, which populates the interactive
  # terminal) the databricks shim is not yet on PATH, so `command -v databricks` is
  # empty and the shim itself fails ("No version is set for shim"). Resolve the real
  # installed binary directly in both the empty and shim cases so the OAuth token mints
  # in the terminal too — not only inside `mise run` tasks, where the shim is already
  # active. Without this, raw `dbt` in the terminal has no token and fails to connect.
  case "$databricks_bin" in
    "" | */shims/databricks)
      install_bin=$(find "$HOME/.local/share/mise/installs/databricks-cli" -mindepth 2 -maxdepth 2 -type f -name databricks 2>/dev/null | sort -V | tail -n 1)
      if [ -n "$install_bin" ] && [ -x "$install_bin" ]; then
        printf '%s' "$install_bin"
        return 0
      fi
      ;;
  esac

  if [ -n "$databricks_bin" ]; then
    printf '%s' "$databricks_bin"
    return 0
  fi
  return 1
}

# OAuth access tokens are short-lived. Refresh one into this shell instead of
# writing it to databricks.env or reusing a token inherited from an older hook.
#
# Why this block must ALWAYS export a value: mise cannot propagate an `unset` from a
# `_.source` script back into an already-initialised shell. A variable mise exported
# once keeps its old value for the life of that shell, no matter what this script does
# later. So clearing the token on a failed mint does NOT clear it -- it strands the
# PREVIOUS, now-expired token in the shell. dbt then sends that expired token and dies
# with an opaque 401/403 while `databricks auth describe` still reports "authenticated"
# (it reads the CLI profile, not this shell's export). Exporting an explicit sentinel
# instead makes the profile's actionable auth error fire as designed.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then
  _oauth_token=""
  if command -v python3 >/dev/null 2>&1; then
    _databricks_bin=$(_resolve_databricks_bin || true)
    _oauth_host="${DATABRICKS_HOST:-${DBT_HOST:-}}"
    if [ -n "$_oauth_host" ] && [ -n "$_databricks_bin" ]; then
      # Why: the mint is a network call. A single transient failure used to leave the
      # shell holding an expired token for the rest of the session (see above), so
      # retry briefly before falling back to the sentinel.
      for _mint_attempt in 1 2 3; do
        if command -v timeout >/dev/null 2>&1; then
          _oauth_json=$(timeout 10 "$_databricks_bin" auth token --profile DEFAULT --host "$_oauth_host" --output json 2>/dev/null || true)
        else
          _oauth_json=$("$_databricks_bin" auth token --profile DEFAULT --host "$_oauth_host" --output json 2>/dev/null || true)
        fi
        _oauth_token=$(printf '%s' "$_oauth_json" | python3 -c 'import json, sys
try:
    print(json.load(sys.stdin).get("access_token", ""))
except (json.JSONDecodeError, AttributeError):
    pass' 2>/dev/null || true)
        if [ -n "$_oauth_token" ]; then
          break
        fi
        if [ "$_mint_attempt" -lt 3 ]; then
          sleep 1
        fi
      done
    fi
    unset _oauth_host _oauth_json _databricks_bin _mint_attempt
  fi

  if [ -n "$_oauth_token" ]; then
    # Keep CLI auth on databricks-cli/OAuth. Setting DATABRICKS_TOKEN forces
    # unified auth down the PAT path (auth_type: pat), which is incorrect here.
    export DBT_ACCESS_TOKEN="$_oauth_token"
  else
    # Why: overwrite rather than unset (see the block comment above). This is what
    # guarantees a stale token can never outlive its OAuth session in a long-lived
    # terminal -- the next dbt command fails fast with an actionable error instead of
    # replaying an expired credential.
    export DBT_ACCESS_TOKEN="MISSING_run__mise_run_setup_databricks"
    if [ -t 2 ]; then
      # Why: the OAuth session (refresh token) has lapsed, so no access token could
      # be minted non-interactively. The trainee still needs to re-authenticate to
      # actually run dbt, so warn loudly on a real terminal (throttled to once / 5 min).
      _dpc_oauth_warn="${TMPDIR:-/tmp}/.dpc_oauth_expired_warn"
      if [ ! -e "$_dpc_oauth_warn" ] || [ -n "$(find "$_dpc_oauth_warn" -mmin +5 2>/dev/null)" ]; then
        printf '\033[1;33m⚠ Databricks OAuth session expired — run: mise run setup:databricks to re-authenticate (dbt will fail with an auth error until you do)\033[0m\n' >&2
        : >"$_dpc_oauth_warn" 2>/dev/null || true
      fi
      unset _dpc_oauth_warn
    fi
  fi
  unset _oauth_token
fi

# These are read from ~/.databrickscfg [DEFAULT] profile if not already set.
if [ -z "$DBT_HOST" ] && [ -f "$HOME/.databrickscfg" ]; then
  export DBT_HOST=$(awk '/^\[DEFAULT\]/{found=1} found && /^host/{print $3; exit}' "$HOME/.databrickscfg")
fi
if [ -z "$DBT_ACCESS_TOKEN" ] && [ -f "$HOME/.databrickscfg" ]; then
  # Why: on OAuth setups .databrickscfg has no `token` line, so this awk yields an
  # empty string. Exporting an empty DBT_ACCESS_TOKEN is worse than leaving it unset
  # (see the normalization note below), so only export when a real token was found.
  _cfg_token=$(awk '/^\[DEFAULT\]/{found=1} found && /^token/{print $3; exit}' "$HOME/.databrickscfg")
  if [ -n "$_cfg_token" ]; then
    export DBT_ACCESS_TOKEN="$_cfg_token"
  fi
  unset _cfg_token
fi
# Load DBT vars written by clone-sources (catalog, schema, http_path)
if [ -f "/etc/profile.d/dbt-env.sh" ]; then
  source /etc/profile.d/dbt-env.sh
fi

# Why: dbt's Jinja env_var('DBT_ACCESS_TOKEN', <sentinel>) only returns <sentinel> when
# the variable is UNSET, and mise cannot propagate an unset from this script into an
# already-initialised shell. So export the sentinel EXPLICITLY: a SET-but-empty value
# would otherwise resolve to "" and send dbt-databricks down
# authenticate_with_external_browser() -> an infinite silent hang on the 8020 OAuth
# callback. Exporting it guarantees dbt always fails fast with a clear auth error.
[ -n "${DBT_ACCESS_TOKEN:-}" ] || export DBT_ACCESS_TOKEN="MISSING_run__mise_run_setup_databricks"
[ -n "${DATABRICKS_TOKEN:-}" ] || unset DATABRICKS_TOKEN
