#!/usr/bin/env bash
# Interactive OAuth-first setup for Databricks CLI + dbt env contract.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fallback_script="$script_dir/utils/setup-databricks-config.sh"
airflow_setup_script="$script_dir/utils/setup-airflow-settings.sh"
config_dir="$HOME/.config/dpc"
config_file="$config_dir/databricks.env"
env_file="$script_dir/.env"
databrickscfg="$HOME/.databrickscfg"
use_pat_setup=0
DEFAULT_TRAINING_DATABRICKS_HOST="https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com"

color() { printf '\033[1;36m%s\033[0m\n' "$*"; }
warn()  { printf '\033[1;33m%s\033[0m\n' "$*" >&2; }

setup_airflow_databricks_connections() {
  if [ ! -x "$airflow_setup_script" ]; then
    warn "Skipping Airflow Databricks connection setup: $airflow_setup_script is missing or not executable."
    return 0
  fi
  color "Setting up Airflow Databricks connections..."
  "$airflow_setup_script"
}

read_required() {
  local var=$1 prompt=$2 default=${3:-}
  local val
  while :; do
    if [ -n "$default" ]; then
      read -r -p "$prompt [$default]: " val || exit 1
      val="${val:-$default}"
    else
      read -r -p "$prompt: " val || exit 1
    fi
    if [ -n "$val" ]; then
      printf -v "$var" '%s' "$val"
      return 0
    fi
    warn "  (required)"
  done
}

read_secret_required() {
  local var=$1 prompt=$2
  local val
  while :; do
    read -r -s -p "$prompt: " val || exit 1
    echo
    if [ -n "$val" ]; then
      printf -v "$var" '%s' "$val"
      return 0
    fi
    warn "  (required)"
  done
}

_resolve_databricks_bin() {
  local candidate
  if [ -n "${DATABRICKS_BIN:-}" ] && [ -x "$DATABRICKS_BIN" ]; then
    printf '%s\n' "$DATABRICKS_BIN"
    return 0
  fi

  if command -v databricks >/dev/null 2>&1; then
    candidate="$(command -v databricks)"
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi

  candidate="$(find "$HOME/.local/share/mise/installs/databricks-cli" -type f -path '*/bin/databricks' 2>/dev/null | sort | tail -n 1 || true)"
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    printf '%s\n' "$candidate"
    return 0
  fi

  return 1
}

pick_warehouse() {
  local json rows max pick id
  if ! json=$("${DATABRICKS_BIN:-databricks}" warehouses list --output json 2>/dev/null); then
    return 1
  fi

  rows=$(printf '%s' "$json" | jq -r '
    (if type == "array" then . else (.warehouses // []) end)
    | sort_by(.name)
    | to_entries[]
    | "\(.key + 1)\t\(.value.id)\t\(.value.name)\t\(.value.state // "?")"
  ' 2>/dev/null) || return 1

  [ -z "$rows" ] && return 1

  color "Available SQL warehouses:"
  printf '    %-4s %-30s %-10s\n' "#" "Name" "State"
  printf "%s\n" "$rows" | awk -F'\t' '{ printf "    %-4s %-30s %-10s\n", $1")", $3, $4 }'
  echo

  max=$(printf "%s\n" "$rows" | wc -l | tr -d ' ')
  while :; do
    read -r -p "Pick a warehouse [1-$max] (or m for manual): " pick || exit 1
    if [[ "$pick" =~ ^[Mm]$ ]]; then
      return 1
    fi
    if [[ "$pick" =~ ^[0-9]+$ ]] && [ "$pick" -ge 1 ] && [ "$pick" -le "$max" ]; then
      id=$(printf "%s\n" "$rows" | awk -F'\t' -v n="$pick" 'NR==n {print $2}')
      DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/$id"
      color "Selected warehouse http_path: $DATABRICKS_HTTP_PATH"
      return 0
    fi
    warn "  Enter a number from 1 to $max, or 'm' for manual."
  done
}

clear_oauth_callback_port() {
  local line pid cmd
  line=$(ss -ltnp 2>/dev/null | awk '/127\.0\.0\.1:8020/ {print; exit}')
  [ -z "$line" ] && return 0

  pid=$(printf '%s' "$line" | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p')
  if [ -z "$pid" ]; then
    warn "OAuth callback port 8020 is in use by an unknown process. Free it and rerun."
    return 1
  fi

  cmd=$(ps -o args= -p "$pid" 2>/dev/null || true)
  if printf '%s' "$cmd" | grep -q "databricks auth login"; then
    warn "Found stale Databricks OAuth listener on 8020 (pid $pid); stopping it."
    kill "$pid" >/dev/null 2>&1 || true
    sleep 1
    return 0
  fi

  warn "OAuth callback port 8020 is already in use by pid $pid ($cmd)."
  warn "Close that process or free port 8020, then rerun setup."
  return 1
}

is_placeholder_token() {
  case "$1" in
    dapi1234567890abcdef|dapi1234567890abcdefg|your-token-here|YOUR_TOKEN_HERE|replace-me|replace-with-your-token|paste-your-token-here|token) return 0 ;;
  esac
  return 1
}

ensure_databrickscfg_path() {
  if [ ! -d "$databrickscfg" ]; then
    return 0
  fi

  warn "$databrickscfg exists as a directory, but Databricks CLI requires it to be a file."
  if rmdir "$databrickscfg" 2>/dev/null; then
    warn "Removed empty directory at $databrickscfg so Databricks CLI can create the auth file."
    return 0
  fi

  warn "Directory $databrickscfg is not empty. Move or remove it, then rerun setup."
  return 1
}

read_parent_env_var() {
  local key=$1
  [ -r "/proc/$PPID/environ" ] || return 1
  tr '\0' '\n' <"/proc/$PPID/environ" | awk -F= -v key="$key" '$1 == key {sub(/^[^=]*=/, "", $0); print; exit}'
}

validate_pat_token() {
  local probe_file http_code token_hint
  probe_file="/tmp/databricks-pat-validate.json"
  if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ]; then
    token_hint="${DATABRICKS_TOKEN:0:4}...${DATABRICKS_TOKEN: -4}"
    warn "PAT debug: host=$DATABRICKS_HOST token_len=${#DATABRICKS_TOKEN} token_hint=$token_hint"
  fi
  if ! http_code=$(curl -sS -o /tmp/databricks-pat-validate.json -w "%{http_code}" \
    -H "Authorization: Bearer $DATABRICKS_TOKEN" \
    "$DATABRICKS_HOST/api/2.0/preview/scim/v2/Me"); then
    warn "Databricks PAT token authentication failed for $DATABRICKS_HOST."
    warn "PAT validation details: unable to reach Databricks API."
    warn "Set DATABRICKS_TOKEN to a valid PAT and rerun setup with --pat."
    return 1
  fi

  if [ "$http_code" != "200" ]; then
    local details
    details="$(tr -d '\r\n' <"$probe_file" | cut -c1-300)"
    if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ]; then
      warn "PAT debug: http_code=$http_code"
    fi
    warn "Databricks PAT token authentication failed for $DATABRICKS_HOST."
    [ -n "$details" ] && warn "PAT validation details: $details"
    warn "Set DATABRICKS_TOKEN to a valid PAT and rerun setup with --pat."
    return 1
  fi

  return 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    --pat)
      use_pat_setup=1
      ;;
    --oauth)
      use_pat_setup=0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

if [ "${FORCE_PAT_SETUP:-0}" = "1" ]; then
  use_pat_setup=1
fi

mkdir -p "$config_dir"

saved_host="${DATABRICKS_HOST-__UNSET__}"
saved_token="${DATABRICKS_TOKEN-__UNSET__}"
saved_http_path="${DATABRICKS_HTTP_PATH-__UNSET__}"
if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ] && [ "$saved_token" != "__UNSET__" ]; then
  warn "PAT debug: saved_token_hint=${saved_token:0:4}...${saved_token: -4}"
fi

if [ -f "$env_file" ]; then
  # shellcheck disable=SC1090
  . "$env_file"
fi

if [ "$saved_host" != "__UNSET__" ]; then
  DATABRICKS_HOST="$saved_host"
fi
if [ "$saved_token" != "__UNSET__" ]; then
  DATABRICKS_TOKEN="$saved_token"
fi
if [ "$saved_http_path" != "__UNSET__" ]; then
  DATABRICKS_HTTP_PATH="$saved_http_path"
fi

parent_host="$(read_parent_env_var DATABRICKS_HOST || true)"
parent_token="$(read_parent_env_var DATABRICKS_TOKEN || true)"
parent_http_path="$(read_parent_env_var DATABRICKS_HTTP_PATH || true)"
if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ] && [ -n "$parent_token" ]; then
  warn "PAT debug: parent_token_hint=${parent_token:0:4}...${parent_token: -4}"
fi
if [ -n "$parent_host" ]; then
  DATABRICKS_HOST="$parent_host"
fi
if [ -n "$parent_token" ]; then
  DATABRICKS_TOKEN="$parent_token"
fi
if [ -n "$parent_http_path" ]; then
  DATABRICKS_HTTP_PATH="$parent_http_path"
fi
if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ] && [ -n "${DATABRICKS_TOKEN:-}" ]; then
  warn "PAT debug: effective_token_hint=${DATABRICKS_TOKEN:0:4}...${DATABRICKS_TOKEN: -4}"
fi

if is_placeholder_token "${DATABRICKS_TOKEN:-}"; then
  unset DATABRICKS_TOKEN
fi

if [ "$use_pat_setup" -eq 1 ]; then
  if ! command -v databricks >/dev/null 2>&1; then
    echo "Databricks PAT setup requires the databricks CLI." >&2
    exit 1
  fi
  DATABRICKS_BIN=$(_resolve_databricks_bin)
  if [ -z "${DATABRICKS_BIN:-}" ] || [ ! -x "$DATABRICKS_BIN" ]; then
    echo "Databricks PAT setup requires an executable databricks CLI binary." >&2
    exit 1
  fi
  if [ -z "${DATABRICKS_HOST:-}" ]; then
    read_required DATABRICKS_HOST "Databricks workspace URL (e.g. https://cg-db-...cloud.databricks.com)" "$DEFAULT_TRAINING_DATABRICKS_HOST"
  fi
  DATABRICKS_HOST="${DATABRICKS_HOST%/}"
  case "$DATABRICKS_HOST" in
    https://*|http://*) : ;;
    *) DATABRICKS_HOST="https://$DATABRICKS_HOST" ;;
  esac
  if [ -z "${DATABRICKS_TOKEN:-}" ]; then
    read_secret_required DATABRICKS_TOKEN "Databricks PAT token"
  fi
  export DATABRICKS_BIN DATABRICKS_HOST DATABRICKS_TOKEN
  if ! validate_pat_token; then
    read_secret_required DATABRICKS_TOKEN "Databricks PAT token (retry)"
    export DATABRICKS_TOKEN
    validate_pat_token
  fi
  if [ -z "${DATABRICKS_HTTP_PATH:-}" ]; then
    pick_warehouse || read_required DATABRICKS_HTTP_PATH "SQL warehouse HTTP path (e.g. /sql/1.0/warehouses/abc123)"
  fi
  export DATABRICKS_HTTP_PATH
  "$fallback_script"
  # Why: PAT/OAuth selection only changes credential source; both modes must
  # provision Airflow's Databricks connections in the same setup flow so local
  # DAGs work immediately.
  setup_airflow_databricks_connections
  exit 0
fi

if ! command -v databricks >/dev/null 2>&1; then
  echo "Databricks OAuth setup requires the databricks CLI." >&2
  exit 1
fi

ensure_databrickscfg_path

if [ -z "${DATABRICKS_HOST:-}" ]; then
  read_required DATABRICKS_HOST "Databricks workspace URL (e.g. https://cg-db-...cloud.databricks.com)" "$DEFAULT_TRAINING_DATABRICKS_HOST"
fi
DATABRICKS_HOST="${DATABRICKS_HOST%/}"
case "$DATABRICKS_HOST" in
  https://*|http://*) : ;;
  *) DATABRICKS_HOST="https://$DATABRICKS_HOST" ;;
esac

color "Launching Databricks OAuth login for DEFAULT profile..."
clear_oauth_callback_port
databricks auth login --profile DEFAULT --host "$DATABRICKS_HOST"
if ! databricks current-user me --profile DEFAULT >/dev/null; then
  echo "Databricks OAuth login completed, but the authentication probe failed." >&2
  exit 1
fi

DBX_USERNAME=$(databricks current-user me --profile DEFAULT --output json 2>/dev/null | python3 -c "
import json
import sys
try:
    payload = json.load(sys.stdin)
except Exception:
    print('')
    raise SystemExit(0)
username = payload.get('userName', '')
if '@' in username:
    username = username.split('@')[0]
print(username)
" || true)
if [ -z "${DBX_USERNAME:-}" ]; then
  DBX_USERNAME="${USER:-root}"
fi

if [ -z "${DATABRICKS_HTTP_PATH:-}" ]; then
  pick_warehouse || read_required DATABRICKS_HTTP_PATH "SQL warehouse HTTP path (e.g. /sql/1.0/warehouses/abc123)"
fi

default_catalog="${DATABRICKS_CATALOG:-${DBT_CATALOG:-training_dev}}"
default_schema_owner="${DBX_USERNAME:-${USER:-root}}"
default_schema="${DATABRICKS_SCHEMA:-${DBT_SCHEMA:-training_${default_schema_owner}}}"
read_required DATABRICKS_CATALOG "Default catalog" "$default_catalog"
read_required DATABRICKS_SCHEMA "Default schema (use training_<initials>, e.g. training_gqp)" "$default_schema"

cat >"$config_file" <<EOF
export DPC_DATABRICKS_AUTH_MODE=oauth
export DATABRICKS_HOST=${DATABRICKS_HOST}
export DATABRICKS_HTTP_PATH=${DATABRICKS_HTTP_PATH}
export DATABRICKS_CATALOG=${DATABRICKS_CATALOG}
export DATABRICKS_SCHEMA=${DATABRICKS_SCHEMA}
export DBT_CATALOG=${DATABRICKS_CATALOG}
export DBT_SCHEMA=${DATABRICKS_SCHEMA}
export DBT_HOST=${DATABRICKS_HOST}
export DBT_HTTP_PATH=${DATABRICKS_HTTP_PATH}
# Why: Airflow 3 task-time metastore variable reads can fail under SDK sandboxing.
# Exporting AIRFLOW_VAR_DATABRICKS_JOB_PREFIX keeps job_name templating stable via
# EnvironmentVariablesBackend without relying on ORM-backed variable fetches.
export AIRFLOW_VAR_DATABRICKS_JOB_PREFIX="[dev ${DBX_USERNAME}] "
EOF

chmod 600 "$config_file"

echo "Wrote non-secret OAuth Databricks env contract to $config_file"

# Why: databricks.env is only read through mise, and mise's environment is
# DIRECTORY-SCOPED -- `mise env` exports these inside the repo and nothing outside it.
# So a terminal opened at ~ or / has blank DBT_* until you cd into the repo, and anything
# it launches (notably `astro dev start`, which snapshots the environment into the Airflow
# containers at boot) inherits the blanks. Writing the same non-secret values to
# /etc/profile.d makes them present in every login and interactive shell regardless of cwd;
# .mise/env.sh already sources this exact path first, then layers databricks.env over it.
# Secrets are deliberately excluded: this file is world-readable, and the short-lived OAuth
# token is minted per-shell by /etc/profile.d/mise-init.sh instead.
# See docs/rca/2026-08-04-databricks-env-not-propagated-to-shells.md.
if profile_env=$(mktemp) && cat >"$profile_env" <<'EOF'
# Auto-generated by .devcontainer/setup-databricks-dbt.sh -- do not edit.
#
# Why this file exists: ~/.config/dpc/databricks.env is the single source of truth for
# Databricks settings, but it is normally loaded only through mise -- and mise's
# environment is DIRECTORY-SCOPED, so a shell whose cwd is outside the repo gets nothing.
# Sourcing it from /etc/profile.d makes it apply in every login and interactive shell, in
# any directory, which is what `astro dev start` and any ad-hoc `dbt` need.
#
# Why we source rather than copy the values: databricks.env is mode 600 and, in PAT mode,
# carries DBT_ACCESS_TOKEN. Copying it here would publish a credential into a
# world-readable file; sourcing reads it under the invoking user's own permissions and
# keeps exactly one source of truth.
#
# In OAuth mode no token is stored anywhere -- the short-lived token is minted per shell
# by /etc/profile.d/mise-init.sh, which is sourced after this file and therefore already
# has DATABRICKS_HOST available.
if [ -r "$HOME/.config/dpc/databricks.env" ]; then
  . "$HOME/.config/dpc/databricks.env"
fi
EOF
then
  if cp "$profile_env" /etc/profile.d/databricks-env.sh 2>/dev/null; then
    chmod 644 /etc/profile.d/databricks-env.sh
    echo "Wrote non-secret settings to /etc/profile.d/databricks-env.sh (available in any directory)"
  else
    echo "WARNING: could not write /etc/profile.d/databricks-env.sh (need root)." >&2
    echo "         DBT_* will only be set in shells whose directory is inside the repo." >&2
  fi
  rm -f "$profile_env"
fi

# Why: writing those files only helps if some shell actually loads them. The mise path is
# /etc/profile.d/mise-init.sh -> `mise activate` -> .mise/env.sh, and that hook also mints
# the short-lived OAuth token on every prompt. It is normally installed once by the
# devcontainer's postCreate (`mise run setup`), whose steps are chained with `&&` -- so an
# earlier failure silently skips it and authentication still reports success.
# Self-heal here so authenticating is sufficient on its own.
if [ ! -f /etc/profile.d/mise-init.sh ]; then
  echo "Shell hook /etc/profile.d/mise-init.sh is missing — installing it so these values reach your shells."
  if bash "$(dirname "$0")/utils/setup-mise.sh"; then
    echo "Installed /etc/profile.d/mise-init.sh"
  else
    echo "WARNING: could not install /etc/profile.d/mise-init.sh." >&2
    echo "         Run 'mise run setup:mise' before starting Airflow or running dbt." >&2
  fi
fi

# Verify the contract end to end rather than assuming it. Probe from OUTSIDE the repo:
# that is the case mise's directory scoping does not cover, so it is the one worth proving.
_probe=$(cd / && env -i HOME="$HOME" PATH="$PATH" bash -lc 'printf "%s|%s" "${DBT_CATALOG:-}" "${DBT_SCHEMA:-}"' 2>/dev/null || true)
_probe_catalog=${_probe%%|*}
_probe_schema=${_probe#*|}
if [ -z "$_probe_catalog" ] || [ -z "$_probe_schema" ]; then
  echo "WARNING: a new shell outside the repo still does not see DBT_CATALOG/DBT_SCHEMA." >&2
  echo "         Run 'mise run setup:mise', then open a new terminal." >&2
else
  echo "Verified: new shells export DBT_CATALOG=$_probe_catalog DBT_SCHEMA=$_probe_schema (from any directory)"
  echo "Open a new terminal (or run 'exec bash -l') so this shell picks them up too."
fi

setup_airflow_databricks_connections
