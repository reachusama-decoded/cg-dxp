#!/bin/bash
# Initialize mise environment management
# Creates /etc/profile.d/mise-init.sh which is sourced by all shells

set -e

# Trust the .mise.toml config file (required by mise security feature)
# The project root is two levels up; the container mounts it under the host folder's name.
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
if command -v mise &> /dev/null; then
    mise trust .mise.toml 2>/dev/null || true
fi

# Create mise initialization script for all shells
cat > /etc/profile.d/mise-init.sh <<'MISE_INIT'
# Auto-generated mise initialization script
# Ensure temp dir used by sandboxed shells exists before tools like mise run.
if [ -n "${TMPDIR:-}" ]; then
    mkdir -p "$TMPDIR" 2>/dev/null || export TMPDIR=/tmp
fi
if [ -z "${TMPDIR:-}" ]; then
    export TMPDIR=/tmp
fi
mkdir -p "$TMPDIR" 2>/dev/null || true

if [ -d "$HOME/.config/mise" ] || command -v mise &> /dev/null; then
    eval "$(mise activate bash 2>/dev/null || mise activate zsh 2>/dev/null || true)"
fi

# Keep bundle vars in sync with the current branch on every prompt.
_sanitize_branch_name() {
    printf '%s' "$1" | sed -E 's|[/.[:space:]-]+|_|g; s/[^[:alnum:]_]/_/g; s/^_+//; s/_+$//'
}

_update_bundle_branch_vars() {
    local branch sanitized_branch

    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
    sanitized_branch=$(_sanitize_branch_name "$branch")
    if [ -z "$sanitized_branch" ]; then
        sanitized_branch="main"
    fi
    export BUNDLE_VAR_git_branch="$sanitized_branch"
}

# Keep the short-lived Databricks OAuth token fresh in THIS shell on every prompt.
#
# Why this lives here and not in .mise/env.sh: mise executes a `_.source` script
# ONCE per shell session and caches the resulting environment -- it re-runs the script
# only when the file's mtime changes, NOT on every prompt. So a token minted by
# .mise/env.sh at shell start is never refreshed, and any terminal left open longer
# than the ~1h OAuth access-token lifetime ends up holding an EXPIRED token. dbt then
# fails with an opaque 401/403 while `databricks auth describe` still reports
# "authenticated" (it reads the CLI profile, not this shell's export).
# Refreshing from PROMPT_COMMAND runs inside the shell itself, so `export` applies
# directly and raw `dbt` always sends a live credential.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.
_DPC_TOKEN_SENTINEL="MISSING_run__mise_run_setup_databricks"
_DPC_TOKEN_NEXT_CHECK=0

_dpc_resolve_databricks_bin() {
    local bin
    bin=$(command -v databricks 2>/dev/null || true)
    # The mise shim is not always usable during shell startup; fall back to the
    # real installed binary (same resolution strategy as .mise/env.sh).
    case "$bin" in
        "" | */shims/databricks)
            bin=$(find "$HOME/.local/share/mise/installs/databricks-cli" -mindepth 2 -maxdepth 2 -type f -name databricks 2>/dev/null | sort -V | tail -n 1)
            ;;
    esac
    if [ -n "$bin" ] && [ -x "$bin" ]; then
        printf '%s' "$bin"
        return 0
    fi
    return 1
}

_refresh_databricks_token() {
    local now bin host json token expiry next
    now=${EPOCHSECONDS:-$(date +%s)}

    # Fast path: pure builtins, zero subprocesses, until the next scheduled check.
    if [ "$now" -lt "$_DPC_TOKEN_NEXT_CHECK" ]; then
        return 0
    fi

    # Re-read the auth contract on each check instead of trusting what this shell captured
    # at startup.
    #
    # Why: the devcontainer's postCreate runs `mise run setup`, which does NOT authenticate
    # -- Databricks auth is a separate, interactive `mise run setup:databricks`. So every
    # terminal the devcontainer opens for you at creation predates authentication and has
    # no DPC_DATABRICKS_AUTH_MODE. This function used to test that variable first and
    # return immediately, and mise executes .mise/env.sh only ONCE per shell session, so
    # such a terminal could never obtain DBT_ACCESS_TOKEN for its entire life -- while a
    # terminal opened after authenticating worked fine. That is the "sometimes the token is
    # defined, sometimes it is not" inconsistency, and dbt and Airflow both depend on it.
    # Sourcing here makes authenticating take effect in terminals that are ALREADY OPEN,
    # and in PAT mode it delivers the stored long-lived token directly.
    if [ -r "$HOME/.config/dpc/databricks.env" ]; then
        . "$HOME/.config/dpc/databricks.env" 2>/dev/null || true
    fi

    if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then
        # Not OAuth, or not authenticated yet. Re-check in a minute so authenticating later
        # still reaches this shell, without re-reading the file on every command.
        _DPC_TOKEN_NEXT_CHECK=$((now + 60))
        return 0
    fi

    bin=$(_dpc_resolve_databricks_bin) || return 0
    host="${DATABRICKS_HOST:-${DBT_HOST:-}}"
    [ -n "$host" ] || return 0

    json=$(timeout 10 "$bin" auth token --profile DEFAULT --host "$host" --output json 2>/dev/null || true)
    token=$(printf '%s' "$json" | python3 -c 'import json, sys
try:
    print(json.load(sys.stdin).get("access_token", ""))
except Exception:
    pass' 2>/dev/null || true)

    if [ -n "$token" ]; then
        export DBT_ACCESS_TOKEN="$token"
        expiry=$(printf '%s' "$json" | python3 -c 'import json, sys, datetime
try:
    raw = json.load(sys.stdin).get("expiry", "")
    raw = raw.split(".")[0].rstrip("Z")
    stamp = datetime.datetime.fromisoformat(raw).replace(tzinfo=datetime.timezone.utc)
    print(int(stamp.timestamp()))
except Exception:
    print(0)' 2>/dev/null || echo 0)
        if [ "${expiry:-0}" -gt 0 ]; then
            # Re-check 5 min before expiry so a long dbt command cannot straddle it.
            next=$((expiry - 300))
        else
            next=$((now + 600))
        fi
        # Why the floor: the Databricks CLI serves a cached token until it is nearly
        # expired, so once inside the 5 min margin every prompt would otherwise mint
        # again and make the shell visibly slow. Never re-check more than once a minute.
        if [ "$next" -lt "$((now + 60))" ]; then
            next=$((now + 60))
        fi
        _DPC_TOKEN_NEXT_CHECK=$next
    else
        # Why: never leave an expired token behind. Overwrite with the sentinel so the
        # next dbt command fails fast with the profile's actionable auth error instead
        # of silently replaying a dead credential.
        export DBT_ACCESS_TOKEN="$_DPC_TOKEN_SENTINEL"
        # Retry periodically rather than on every prompt.
        _DPC_TOKEN_NEXT_CHECK=$((now + 60))
    fi
    return 0
}

PROMPT_COMMAND="_refresh_databricks_token;_update_bundle_branch_vars${PROMPT_COMMAND:+;$PROMPT_COMMAND}"

# Why a DEBUG trap in addition to PROMPT_COMMAND: PROMPT_COMMAND runs when the prompt
# is DRAWN -- i.e. after the previous command finished. The shell then sits idle at
# that prompt, possibly for hours. If the token expires during that idle window, the
# next command the user types still runs with the STALE token and fails with a 403;
# the refresh only happens afterwards, which is why re-running the same command
# appears to "fix" it. A DEBUG trap fires immediately BEFORE each command, so the
# credential is guaranteed live at the moment it is actually used.
# See docs/rca/2026-08-04-challenge-02-oauth-token-refresh-gap.md.
_dpc_preexec() {
    # Skip completion expansion and the PROMPT_COMMAND invocation itself.
    if [ -n "${COMP_LINE:-}" ]; then
        return 0
    fi
    if [ "$BASH_COMMAND" = "$PROMPT_COMMAND" ]; then
        return 0
    fi
    _refresh_databricks_token
    # Always succeed: under `shopt -s extdebug` a non-zero return would cancel the
    # user's command.
    return 0
}

# Interactive shells only; the trap is not inherited by functions or subshells
# (functrace is off by default), so this costs one cheap guarded call per command.
case $- in
    *i*) trap '_dpc_preexec' DEBUG ;;
esac
MISE_INIT

chmod 644 /etc/profile.d/mise-init.sh

echo "✓ Mise environment initialization configured"
