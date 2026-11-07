#!/usr/bin/env sh

set -eu

workspace="${1:-}"

if [ -n "$workspace" ] && [ -d "$workspace" ]; then
  cd "$workspace"
fi

export PATH="/root/.local/share/mise/shims:$PATH"

sanitize_docker_credstore() {
  cfg="${HOME}/.docker/config.json"
  [ -f "$cfg" ] || return 0
  command -v jq >/dev/null 2>&1 || return 0

  creds_store="$(jq -r '.credsStore // ""' "$cfg" 2>/dev/null || true)"
  case "$creds_store" in
    dev-containers-*)
      tmp="${cfg}.tmp"
      if jq 'del(.credsStore)' "$cfg" >"$tmp"; then
        mv "$tmp" "$cfg"
      else
        rm -f "$tmp"
      fi
      ;;
  esac
}

/usr/local/bin/start-dockerd.sh
/usr/local/bin/ensure-dockerd.sh
sanitize_docker_credstore
/usr/local/bin/dpc-check || true
