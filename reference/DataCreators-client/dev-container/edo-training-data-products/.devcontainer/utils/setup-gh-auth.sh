#!/bin/bash
# Configure automatic GitHub CLI auth using existing git credentials.
# This mirrors the current git push experience: no manual gh login step.

set -e

cat > /etc/profile.d/gh-auth.sh <<'GH_AUTH'
# Auto-generated GitHub CLI auth bootstrap.
# Use git's existing credential helper to seed gh auth non-interactively.
#
# Why GIT_TERMINAL_PROMPT=0 on every `git credential fill` below: this runs from
# /etc/profile.d on EVERY login shell. If no credential helper can answer -- e.g.
# the VS Code Dev Containers helper forwards to a host-side binary that does not
# exist in this container, or the shell is not a VS Code one -- git falls back to
# asking for a username and password. It writes that prompt to /dev/tty, so a
# caller's `2>/dev/null` does not hide it and the login shell BLOCKS waiting for
# input. That is how a `mise run setup:databricks` ends up asking GitHub
# questions: it spawns `bash -lc` to verify env propagation, which sources this
# file. This bootstrap is best-effort by design -- every call site below already
# tolerates failure -- so it must fail silently rather than prompt.
_set_github_token_from_git_credentials() {
    if [ -z "${BASH_VERSION:-}" ]; then
        echo "gh auth bootstrap expects bash; skipping for non-bash shell" >&2
        return 0
    fi

    # Respect explicit caller-provided token env vars.
    if [ -n "${GH_TOKEN:-}" ] || [ -n "${GITHUB_TOKEN:-}" ]; then
        return 0
    fi

    if ! command -v git >/dev/null 2>&1; then
        return 0
    fi

    local gh_host gh_path creds token
    gh_host="github.com"
    gh_path=""

    # Try to infer host from origin if present.
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local remote_url
        remote_url="$(git remote get-url origin 2>/dev/null || true)"
        if [ -n "$remote_url" ]; then
            if [[ "$remote_url" =~ ^https?://([^/]+)/(.+)$ ]]; then
                gh_host="${BASH_REMATCH[1]}"
                gh_path="${BASH_REMATCH[2]}"
            elif [[ "$remote_url" =~ ^git@([^:]+):(.+)$ ]]; then
                gh_host="${BASH_REMATCH[1]}"
                gh_path="${BASH_REMATCH[2]}"
            fi

            # Normalize for credential helper lookups.
            if [ -n "$gh_path" ]; then
                gh_path="${gh_path#/}"
            fi
        fi
    fi

    # Prefer repo-scoped lookup first (matches git push behavior when multiple
    # github.com credentials exist), then fall back to host-scoped lookup.
    if [ -n "$gh_path" ]; then
        creds="$(printf 'protocol=https\nhost=%s\npath=%s\n\n' "$gh_host" "$gh_path" | GIT_TERMINAL_PROMPT=0 git credential fill 2>/dev/null || true)"
        token="$(printf '%s\n' "$creds" | sed -n 's/^password=//p' | head -n 1)"

        if [ -z "$token" ] && [[ "$gh_path" == *.git ]]; then
            creds="$(printf 'protocol=https\nhost=%s\npath=%s\n\n' "$gh_host" "${gh_path%.git}" | GIT_TERMINAL_PROMPT=0 git credential fill 2>/dev/null || true)"
            token="$(printf '%s\n' "$creds" | sed -n 's/^password=//p' | head -n 1)"
        fi
    fi

    if [ -z "$token" ]; then
        creds="$(printf 'protocol=https\nhost=%s\n\n' "$gh_host" | GIT_TERMINAL_PROMPT=0 git credential fill 2>/dev/null || true)"
        token="$(printf '%s\n' "$creds" | sed -n 's/^password=//p' | head -n 1)"
    fi

    if [ -n "$token" ] && command -v gh >/dev/null 2>&1; then
        export GH_HOST="$gh_host"
        if ! gh auth status -h "$gh_host" >/dev/null 2>&1; then
            printf '%s\n' "$token" | gh auth login --hostname "$gh_host" --with-token >/dev/null 2>&1 || true
        fi
    fi
}

_set_github_token_from_git_credentials
GH_AUTH

chmod 644 /etc/profile.d/gh-auth.sh

echo "✓ GitHub CLI auth bootstrap configured"
