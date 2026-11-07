#!/usr/bin/env sh

set -eu

log_file="/var/log/dockerd.log"
pid_file="/var/run/docker.pid"
containerd_pid_file="/var/run/docker/containerd/containerd.pid"
lock_dir="/var/run/dockerd-start.lock"
no_wait=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --restart) ;;
    --no-wait) no_wait=1 ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
  shift
done

mkdir -p /var/log /var/run/docker

acquire_lock() {
  if mkdir "$lock_dir" 2>/dev/null; then
    echo "$$" >"$lock_dir/pid"
    return 0
  fi

  lock_pid="$(cat "$lock_dir/pid" 2>/dev/null || true)"
  if [ -z "$lock_pid" ] || ! kill -0 "$lock_pid" 2>/dev/null; then
    rm -rf "$lock_dir"
    if mkdir "$lock_dir" 2>/dev/null; then
      echo "$$" >"$lock_dir/pid"
      return 0
    fi
  fi

  return 1
}

if ! acquire_lock; then
  if [ "$no_wait" -eq 1 ]; then
    echo "dockerd start or recovery is already in progress" >&2
    exit 0
  fi

  attempts=0
  while [ "$attempts" -lt 60 ]; do
    if docker info >/dev/null 2>&1; then
      exit 0
    fi
    attempts=$((attempts + 1))
    sleep 1
  done

  echo "timed out waiting for the existing dockerd start" >&2
  exit 1
fi

trap 'rm -rf "$lock_dir"' EXIT HUP INT TERM

if docker info >/dev/null 2>&1; then
  exit 0
fi

daemon_pids="$(ps -ef | grep -E '[ /](dockerd|containerd)([ ]|$)' | grep -v '[g]rep' | awk '{print $2}')"
if [ -n "$daemon_pids" ]; then
  for pid in $daemon_pids; do
    kill "$pid" >/dev/null 2>&1 || true
  done

  attempts=0
  while [ "$attempts" -lt 10 ]; do
    remaining=0
    for pid in $daemon_pids; do
      if kill -0 "$pid" 2>/dev/null; then
        remaining=1
      fi
    done
    [ "$remaining" -eq 0 ] && break
    attempts=$((attempts + 1))
    sleep 1
  done

  for pid in $daemon_pids; do
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
  done
fi

rm -f "$pid_file" "$containerd_pid_file"

nohup dockerd >"$log_file" 2>&1 </dev/null &
dockerd_pid=$!

attempts=0
while [ "$attempts" -lt 60 ]; do
  if docker info >/dev/null 2>&1; then
    exit 0
  fi
  if ! kill -0 "$dockerd_pid" 2>/dev/null; then
    echo "dockerd exited before becoming ready; see $log_file" >&2
    exit 1
  fi
  attempts=$((attempts + 1))
  sleep 1
done

echo "dockerd failed to become ready" >&2
exit 1
