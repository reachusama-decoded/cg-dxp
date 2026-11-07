#!/bin/sh
# Auto-configure Databricks CLI and DBT from environment variables
#
# This script creates ~/.databrickscfg from environment variables set in .env
# It runs automatically when the devcontainer starts (via postCreateCommand)
#
# Required environment variables:
#   - DATABRICKS_HOST: Your Databricks workspace URL
#   - DATABRICKS_TOKEN: Your personal access token
#   - DATABRICKS_HTTP_PATH: SQL Warehouse or cluster HTTP path
#   - DBT_STATE_NAMESPACE: Subdirectory under /Volumes/platform_dev/_platform/dbt_state/ for your team (e.g. asset_reference_data)

set -e

echo ""
echo "Setting up Databricks configuration..."
echo "---------------------------------------"

# Check if required environment variables are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo ""
    echo "   Warning: Databricks credentials not configured"
    echo ""
    echo "To enable Databricks CLI and DBT:"
    echo "  1. Copy .devcontainer/utils/.env.example to .devcontainer/.env"
    echo "  2. Edit .env and add your Databricks credentials"
    echo "  3. Rebuild the devcontainer"
    echo ""
    echo "For now, skipping Databricks configuration..."
    echo ""
    exit 0
fi

# Create .databricks directory if it doesn't exist
mkdir -p ~/.databricks
mkdir -p "$HOME/.config/dpc"

# Generate the .databrickscfg file
# Note: Environment variables have already been normalized by normalize-env.sh
cat > ~/.databrickscfg <<EOF
[DEFAULT]
host = $DATABRICKS_HOST
token = $DATABRICKS_TOKEN
EOF

# Add http_path if provided
if [ -n "$DATABRICKS_HTTP_PATH" ]; then
    echo "http_path = $DATABRICKS_HTTP_PATH" >> ~/.databrickscfg
fi

# Set secure permissions (read/write for owner only)
chmod 600 ~/.databrickscfg

DBX_USERNAME=$(databricks current-user me --profile DEFAULT --output json 2>/dev/null | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    print("")
    raise SystemExit(0)
username = payload.get("userName", "")
if "@" in username:
    username = username.split("@")[0]
print(username)
' || true)
if [ -z "$DBX_USERNAME" ]; then
    DBX_USERNAME="${USER:-root}"
fi

cat > "$HOME/.config/dpc/databricks.env" <<EOF
export DPC_DATABRICKS_AUTH_MODE=pat
export DATABRICKS_HOST=$DATABRICKS_HOST
export DATABRICKS_HTTP_PATH=$DATABRICKS_HTTP_PATH
export DATABRICKS_CATALOG=${DATABRICKS_CATALOG:-${DBT_CATALOG:-training_dev}}
export DATABRICKS_SCHEMA=${DATABRICKS_SCHEMA:-${DBT_SCHEMA:-training_${USER:-root}}}
export DBT_CATALOG=${DBT_CATALOG:-training_dev}
export DBT_SCHEMA=${DBT_SCHEMA:-training_${USER:-root}}
export DBT_HOST=$DATABRICKS_HOST
export DBT_HTTP_PATH=$DATABRICKS_HTTP_PATH
export DBT_ACCESS_TOKEN=$DATABRICKS_TOKEN
export DATABRICKS_TOKEN=$DATABRICKS_TOKEN
# Why: Airflow 3 task-time metastore variable reads can fail under SDK sandboxing.
# Keep the Databricks job-name prefix available through env-backed Airflow vars.
export AIRFLOW_VAR_DATABRICKS_JOB_PREFIX="[dev ${DBX_USERNAME}] "
EOF

chmod 600 "$HOME/.config/dpc/databricks.env"

echo ""
echo "Databricks configuration created at ~/.databrickscfg"
echo "OAuth/PAT env contract created at ~/.config/dpc/databricks.env"
echo ""
echo "You can now use:"
echo "  * Databricks CLI: databricks workspace list"
echo "  * DBT: dbt run (credentials auto-loaded)"
echo ""

# Download latest dbt state manifest from Databricks Volume for local --defer runs
MANIFEST_VOLUME_PATH="dbfs:/Volumes/platform_dev/_platform/dbt_state/${DBT_STATE_NAMESPACE}/manifest.json"
MANIFEST_LOCAL_PATH="/workspaces/${WORKSPACE_BASENAME}/dags/asset_reference_data/state/manifest.json"

echo "Fetching dbt state manifest from Databricks Volume..."
if [ -z "$DBT_STATE_NAMESPACE" ]; then
    echo "Warning: DBT_STATE_NAMESPACE not set in .env. Using committed manifest."
elif databricks fs cp --overwrite "$MANIFEST_VOLUME_PATH" "$MANIFEST_LOCAL_PATH" 2>/dev/null; then
    echo "dbt state manifest updated at $MANIFEST_LOCAL_PATH"
else
    echo "Warning: Could not fetch dbt manifest from Volume. Using committed manifest."
fi

echo ""
echo "------------------------------------------"
echo ""
