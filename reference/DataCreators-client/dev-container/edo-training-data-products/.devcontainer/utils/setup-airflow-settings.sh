#!/bin/bash
# Create airflow_settings.yaml from template and auto-inject the local Databricks
# settings that Astro reads for local dev.

set -e

SETTINGS_FILE="airflow_settings.yaml"
LEGACY_SETTINGS_FILE=".airflow/airflow_settings.yaml"
EXAMPLE_FILE=".airflow/airflow_settings.yaml.example"
CONFIG_FILE="$HOME/.config/dpc/databricks.env"

# Docker creates a placeholder directory when astro dev start runs before this
# script (bind-mount source auto-created as a dir if it doesn't exist yet).
if [ -d "$SETTINGS_FILE" ]; then
  rm -rf "$SETTINGS_FILE"
  echo "Removed Docker-created placeholder directory at $SETTINGS_FILE"
fi

if [ ! -f "$SETTINGS_FILE" ]; then
  if [ -f "$LEGACY_SETTINGS_FILE" ]; then
    cp "$LEGACY_SETTINGS_FILE" "$SETTINGS_FILE"
    echo "Migrated $LEGACY_SETTINGS_FILE to $SETTINGS_FILE"
  elif [ ! -f "$EXAMPLE_FILE" ]; then
    echo "Airflow settings template not found at $EXAMPLE_FILE; skipping optional settings setup"
    exit 0
  else
    cp "$EXAMPLE_FILE" "$SETTINGS_FILE"
    echo "Created $SETTINGS_FILE from template"
  fi
else
  echo "Airflow settings already exist, checking Databricks connections"
fi

if [ -f "$CONFIG_FILE" ]; then
  # shellcheck disable=SC1090
  . "$CONFIG_FILE"
fi

if [ -z "${DATABRICKS_HOST:-}" ] && [ -f "$HOME/.databrickscfg" ]; then
  DATABRICKS_HOST=$(awk '/^\[DEFAULT\]/{found=1} found && /^host/{print $3; exit}' "$HOME/.databrickscfg")
fi
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "pat" ] && [ -z "${DATABRICKS_TOKEN:-}" ] && [ -f "$HOME/.databrickscfg" ]; then
  DATABRICKS_TOKEN=$(awk '/^\[DEFAULT\]/{found=1} found && /^token/{print $3; exit}' "$HOME/.databrickscfg")
fi
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ] && command -v databricks >/dev/null 2>&1; then
  DATABRICKS_TOKEN=$(databricks auth token --profile DEFAULT --output json 2>/dev/null | python3 -c "
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    print('')
    raise SystemExit(0)
print(payload.get('access_token', ''))
" || true)
fi

# Why: keep the token available to this shell for file rendering, but prevent
# child processes from inheriting it unless we pass it explicitly.
export -n DATABRICKS_TOKEN

# Ensure the Python renderer sees shell-derived values (for example a token we
# just minted above, or a PAT read from ~/.databrickscfg in explicit PAT mode).
DPC_DATABRICKS_AUTH_MODE="$DPC_DATABRICKS_AUTH_MODE" \
DATABRICKS_HOST="$DATABRICKS_HOST" \
DBT_HOST="$DBT_HOST" \
DATABRICKS_TOKEN="$DATABRICKS_TOKEN" \
python3 - "$SETTINGS_FILE" << 'PYEOF'
from pathlib import Path
import os
import re
import sys

filepath = Path(sys.argv[1])
content = filepath.read_text()


def yaml_scalar(value: str) -> str:
    return repr(value or "")


def connection_block(conn_id: str, host: str, password: str) -> str:
    return (
        f"    - conn_id: {conn_id!r}\n"
        "      conn_type: 'databricks'\n"
        f"      conn_host: {yaml_scalar(host)}\n"
        "      conn_login: ''\n"
        f"      conn_password: {yaml_scalar(password)}\n"
    )


def replace_connection_block(content: str, conn_id: str, block: str) -> tuple[str, bool]:
    pattern = (
        rf"(?ms)^    - conn_id: {conn_id!r}\n"
        r"      conn_type: 'databricks'\n"
        r"      conn_host: .*?\n"
        r"      conn_login: .*?\n"
        r"      conn_password: .*?\n"
    )
    new_content, count = re.subn(pattern, block, content, count=1)
    return new_content, count > 0


def insert_connection_block(content: str, block: str) -> str:
    if "connections: []" in content:
        return content.replace("  connections: []", "  connections:\n" + block.rstrip("\n"), 1)
    if "  connections:\n" in content:
        return content.replace("  connections:\n", "  connections:\n" + block, 1)
    raise RuntimeError("Could not locate connections section in airflow settings")


auth_mode = os.environ.get("DPC_DATABRICKS_AUTH_MODE", "").strip().lower()
host_value = os.environ.get("DATABRICKS_HOST") or os.environ.get("DBT_HOST") or ""
if auth_mode == "pat":
    token_value = os.environ.get("DATABRICKS_TOKEN", "")
elif auth_mode == "oauth":
    token_value = ""  # Why: OAuth token state must live only in metastore via refresher.
else:
    token_value = ""

# If we have a host, we should ensure connection blocks reflect the host/login shape
# even when a short-lived OAuth token is not present. However, we must not
# clobber existing persisted conn_password values when no token is available.
# We'll update host/login for connections when host_value is set. If a token is
# present (PAT or freshly minted OAuth), replace the whole connection block and
# set conn_password to the token. If token is empty, update only host/login and
# preserve the existing conn_password line in the file.
should_update_connections = bool(host_value)


def _replace_host_login_preserve_password(content: str, conn_id: str, host: str) -> tuple[str, bool]:
    # Replace conn_host and conn_login for a matching conn_id but keep the
    # existing conn_password line untouched.
    pattern = (
        rf"(?ms)^    - conn_id: {conn_id!r}\n"
        r"      conn_type: 'databricks'\n"
        r"      conn_host: .*?\n"
        r"      conn_login: .*?\n"
        r"(      conn_password: .*?\n)"
    )

    def _repl(m: re.Match) -> str:
        return (
            f"    - conn_id: {conn_id!r}\n"
            "      conn_type: 'databricks'\n"
            f"      conn_host: {yaml_scalar(host)}\n"
            "      conn_login: ''\n"
            + m.group(1)
        )

    new_content, count = re.subn(pattern, _repl, content, count=1)
    return new_content, count > 0


for conn_id in ("caspian-training-databricks", "databricks_default"):
    if not should_update_connections:
        continue
    if token_value:
        # Token present (PAT or minted OAuth) -> replace full block including password
        block = connection_block(conn_id, host_value, token_value)
        content, replaced = replace_connection_block(content, conn_id, block)
        if not replaced:
            content = insert_connection_block(content, block)
    elif auth_mode == "oauth":
        # OAuth mode without a minted token -> explicitly scrub conn_password to avoid
        # persisting any previously stored tokens. Update host/login shape and set
        # conn_password to empty.
        block = connection_block(conn_id, host_value, "")
        content, replaced = replace_connection_block(content, conn_id, block)
        if not replaced:
            content = insert_connection_block(content, block)
    else:
        # Non-OAuth mode and no token (e.g., unset auth mode) -> preserve existing
        # conn_password to avoid accidental clobbering in non-OAuth flows.
        content, replaced = _replace_host_login_preserve_password(content, conn_id, host_value)
        if not replaced:
            # No existing block to preserve; insert a shaped block with empty password
            block = connection_block(conn_id, host_value, token_value)
            content = insert_connection_block(content, block)

filepath.write_text(content)
PYEOF

if ! command -v databricks >/dev/null 2>&1; then
  echo "  databricks CLI not found -- set databricks_job_prefix manually in $SETTINGS_FILE"
  exit 0
fi

if [ ! -f "$HOME/.databrickscfg" ]; then
  echo "  ~/.databrickscfg not found -- set databricks_job_prefix manually in $SETTINGS_FILE"
  exit 0
fi

# In OAuth mode, keep the Airflow Databricks connections fresh with a background
# refresher (same nohup self-heal pattern as ensure-dockerd.sh). No-op in PAT mode
# (PAT is long-lived) and when the learner opts out.
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ] && [ -z "${DPC_SKIP_OAUTH_REFRESH:-}" ]; then
  REFRESHER="$(cd "$(dirname "$0")" && pwd)/databricks-oauth-refresh.sh"
  if [ -x "$REFRESHER" ]; then
    # Why: the refresher must not inherit a shell token, or Databricks can
    # choose a PAT-style auth path instead of the intended OAuth refresh flow.
    env -u DATABRICKS_TOKEN nohup "$REFRESHER" --loop >/var/log/dbx-oauth-refresh.log 2>&1 </dev/null &
    echo "  Started OAuth->Airflow token refresher (background). Check: dpc-check"
  fi
fi

DBX_JSON=$(databricks current-user me --profile DEFAULT --output json 2>/dev/null || true)
if [ -z "$DBX_JSON" ]; then
  echo "  Could not fetch Databricks identity -- set databricks_job_prefix manually in $SETTINGS_FILE"
  exit 0
fi

DBX_USERNAME=$(echo "$DBX_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
username = data.get('userName', '')
if '@' in username:
    username = username.split('@')[0]
print(username)
")

if [ -z "$DBX_USERNAME" ]; then
  echo "  Could not parse Databricks username -- set databricks_job_prefix manually in $SETTINGS_FILE"
  exit 0
fi

python3 - "$DBX_USERNAME" "$SETTINGS_FILE" << 'PYEOF'
import re
import sys
from pathlib import Path

username = sys.argv[1]
filepath = Path(sys.argv[2])
content = filepath.read_text()
prefix_value = repr(f"[dev {username}] ")
content = re.sub(r'(?m)^(\s*variable_value:\s*)""$', rf'\1{prefix_value}', content, count=1)
filepath.write_text(content)
PYEOF

if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "pat" ]; then
  if [ -n "${DATABRICKS_TOKEN:-}" ]; then
    echo "  PAT mode detected; wrote both Databricks connection passwords"
  else
    echo "  PAT mode detected, but DATABRICKS_TOKEN was missing; kept existing Airflow connection credentials"
  fi
elif [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then
  if [ -n "${DATABRICKS_TOKEN:-}" ]; then
    echo "  OAuth mode detected; refreshed Airflow connection passwords with a short-lived token"
  else
    echo "  OAuth mode detected, but no token was available; kept existing Airflow connection credentials"
  fi
else
  echo "  Databricks auth mode not set; kept existing Airflow connection credentials"
fi

echo "  Set databricks_job_prefix to \"[dev $DBX_USERNAME] \""

# In OAuth mode, keep the Airflow Databricks connections fresh with a background
# refresher (same nohup self-heal pattern as ensure-dockerd.sh). No-op in PAT mode
# (PAT is long-lived) and when the learner opts out.
