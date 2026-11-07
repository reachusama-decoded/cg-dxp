#!/usr/bin/env bash
# Keep local Airflow's Databricks connections supplied with a fresh short-lived
# OAuth token. Runs in the devcontainer, where the OAuth session lives.
#
#   databricks-oauth-refresh.sh --once   # single refresh pass
#   databricks-oauth-refresh.sh --loop   # expiry-driven daemon
#
# No-op unless DPC_DATABRICKS_AUTH_MODE=oauth. Never launches a browser: it only
# calls the non-interactive `databricks auth token`.

set -u

CONFIG_FILE="$HOME/.config/dpc/databricks.env"
STATUS_FILE="$HOME/.config/dpc/oauth-refresh-status.json"
LOG_FILE="/var/log/dbx-oauth-refresh.log"
CONN_IDS="databricks_default caspian-training-databricks"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG_FILE" 2>/dev/null || true
}

write_status() {
  local state=$1 expiry=${2:-}
  mkdir -p "$(dirname "$STATUS_FILE")" 2>/dev/null || true
  printf '{"state": "%s", "last_refresh": "%s", "token_expiry": "%s"}\n' \
    "$state" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$expiry" >"$STATUS_FILE" 2>/dev/null || true
}

load_contract() {
  # shellcheck disable=SC1090
  [ -f "$CONFIG_FILE" ] && . "$CONFIG_FILE"
}

_resolve_databricks_bin() {
  local candidate
  if [ -n "${DATABRICKS_BIN:-}" ] && [ -x "$DATABRICKS_BIN" ]; then
    printf '%s\n' "$DATABRICKS_BIN"
    return 0
  fi
  candidate="$(find "$HOME/.local/share/mise/installs/databricks-cli" -type f -name databricks 2>/dev/null | sort -V | tail -n 1 || true)"
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    printf '%s\n' "$candidate"
    return 0
  fi
  if command -v databricks >/dev/null 2>&1; then
    printf '%s\n' "$(command -v databricks)"
    return 0
  fi
  return 1
}

resolve_scheduler() {
  # Return the container ID (not the stable name) for the first matching scheduler
  # container so we can detect container recreation (ID changes) rather than
  # relying on names which are stable across restarts.
  # Scheduler name pattern: ^edo-training.*-scheduler-1$
  docker ps --format '{{.ID}} {{.Names}}' 2>/dev/null | grep -E ' edo-training.*-scheduler-1$' | awk '{print $1}' | head -1
}

mint_payload() {
  local bin
  bin="$(_resolve_databricks_bin)" || return 1
  "$bin" auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json 2>/dev/null
}

_json_field() {
  # _json_field <field>  (reads JSON from stdin)
  python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get(sys.argv[1], ""))
except Exception:
    print("")' "$1" 2>/dev/null
}

seconds_until_refresh() {
  # Echo seconds to sleep before the next refresh: (expiry - 120s), floored to
  # 30s. Falls back to 3300s (55 min) when expiry is empty/unparseable.
  local expiry=$1
  if [ -z "$expiry" ]; then
    echo 3300
    return 0
  fi
  python3 -c '
import sys, datetime
raw = sys.argv[1]
try:
    exp = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    secs = int((exp - now).total_seconds()) - 120
    print(max(secs, 30))
except Exception:
    print(3300)
' "$expiry" 2>/dev/null || echo 3300
}

upsert_connection() {
  local sched=$1 conn_id=$2 host=$3 token=$4 conn_json
  # Bearer shape: EMPTY login + token in password. An OAuth access token is only
  # accepted as Authorization: Bearer; a non-empty login makes the provider use
  # HTTP Basic auth, which OAuth rejects (verified: 401 vs 200 via DatabricksHook).
  conn_json=$(printf '{"conn_type": "databricks", "host": "%s", "login": "", "password": "%s"}' "$host" "$token")
  docker exec "$sched" airflow connections delete "$conn_id" >/dev/null 2>&1 || true
  docker exec -e CONN_JSON="$conn_json" "$sched" sh -c 'airflow connections add "$0" --conn-json "$CONN_JSON"' "$conn_id" >/dev/null 2>&1
}

# Echoes nothing; sets REFRESH_EXPIRY. Returns 0 ok, 2 scheduler down or
# retryable connection-upsert failure, 3 mint/misconfig.
refresh_once() {
  load_contract
  if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then
    log "mode=${DPC_DATABRICKS_AUTH_MODE:-unset}; not oauth, no-op"
    REFRESH_EXPIRY=""
    return 0
  fi

  if [ -z "${DATABRICKS_HOST:-}" ]; then
    log "DATABRICKS_HOST unset; cannot refresh"
    write_status "misconfigured" ""
    REFRESH_EXPIRY=""
    return 3
  fi

  local sched
  sched=$(resolve_scheduler)
  if [ -z "$sched" ]; then
    log "scheduler not running yet; skipping this pass"
    write_status "scheduler_down" ""
    REFRESH_EXPIRY=""
    return 2
  fi

  local payload token expiry
  payload=$(mint_payload)
  token=$(printf '%s' "$payload" | _json_field access_token)
  expiry=$(printf '%s' "$payload" | _json_field expiry)
  if [ -z "$token" ]; then
    log "databricks auth token returned no access_token (session likely expired)"
    write_status "session_expired" ""
    REFRESH_EXPIRY=""
    return 3
  fi

  local cid
  for cid in $CONN_IDS; do
    if ! upsert_connection "$sched" "$cid" "$DATABRICKS_HOST" "$token"; then
      # Why: a partial refresh must not be reported as healthy, or the loop will
      # sleep as if both Airflow connections were updated successfully.
      log "failed to refresh Databricks connection $cid"
      write_status "connection_update_failed" ""
      REFRESH_EXPIRY=""
      return 2
    fi
  done

  log "refreshed connections ($CONN_IDS) token_expiry=$expiry"
  write_status "ok" "$expiry"
  REFRESH_EXPIRY="$expiry"
  return 0
}

run_loop() {
  if [ -n "${DPC_SKIP_OAUTH_REFRESH:-}" ]; then
    log "DPC_SKIP_OAUTH_REFRESH set; loop disabled"
    exit 0
  fi

  local pidfile="$HOME/.config/dpc/oauth-refresh.pid"
  mkdir -p "$(dirname "$pidfile")" 2>/dev/null || true
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile" 2>/dev/null)" 2>/dev/null; then
    log "refresher already running (pid $(cat "$pidfile")); exiting"
    exit 0
  fi
  echo $$ >"$pidfile"
  trap 'rm -f "$pidfile"' EXIT

  local sleep_s last_scheduler="" current_scheduler=""
  while :; do
    # Track scheduler identity so we can force an immediate refresh when a
    # previously-missing scheduler reappears or the scheduler container changes.
    current_scheduler="$(resolve_scheduler || true)"
    scheduler_changed=0
    if [ -n "$current_scheduler" ] && [ "$current_scheduler" != "$last_scheduler" ]; then
      scheduler_changed=1
    fi

    refresh_once
    rc=$?
    last_scheduler="$current_scheduler"

    case $rc in
      0)
        if [ "$scheduler_changed" -eq 1 ]; then
          sleep_s=1
        else
          sleep_s=$(seconds_until_refresh "${REFRESH_EXPIRY:-}")
        fi
        ;;
      2) sleep_s=30 ;;                                               # scheduler down or refresh failure; retry soon
      *) sleep_s=60 ;;                                               # mint/misconfig failure; back off
    esac
    log "sleeping ${sleep_s}s before next refresh (chunked)"
    remaining=$sleep_s
    # Sleep in 30s chunks so we can detect scheduler identity changes and refresh early.
    while [ "$remaining" -gt 0 ]; do
      chunk=30
      if [ "$remaining" -lt "$chunk" ]; then
        chunk=$remaining
      fi
      sleep "$chunk"
      # After each chunk, check if scheduler identity changed/appeared; if so, break to refresh.
      current_scheduler="$(resolve_scheduler || true)"
      if [ -n "$current_scheduler" ] && [ "$current_scheduler" != "$last_scheduler" ]; then
        log "scheduler identity changed during wait; breaking early to refresh"
        break
      fi
      remaining=$((remaining - chunk))
    done
  done
}

main() {
  local mode=${1:---once}
  case "$mode" in
    --once)
      refresh_once
      exit $?
      ;;
    --loop)
      run_loop
      ;;
    --source-only)
      return 0
      ;;
    *)
      echo "usage: databricks-oauth-refresh.sh [--once|--loop]" >&2
      exit 64
      ;;
  esac
}

main "$@"
