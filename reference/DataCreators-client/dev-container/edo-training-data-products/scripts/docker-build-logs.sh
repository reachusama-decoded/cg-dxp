#!/usr/bin/env bash

set -euo pipefail

# Fetch build history as NDJSON so we can parse status and ref.
history_output="$(docker buildx history ls --format json 2>/dev/null || true)"

if [[ -z "${history_output}" ]]; then
  echo "No docker build history found or Docker is unavailable."
  exit 1
fi

declare -a running_refs=()
declare -a running_build_ids=()
declare -a running_labels=()

while IFS= read -r line; do
  [[ -z "${line}" ]] && continue

  status="$(printf '%s\n' "${line}" | sed -n 's/.*"status":"\([^"]*\)".*/\1/p')"
  ref="$(printf '%s\n' "${line}" | sed -n 's/.*"ref":"\([^"]*\)".*/\1/p')"
  name="$(printf '%s\n' "${line}" | sed -n 's/.*"name":"\([^"]*\)".*/\1/p')"
  created_at="$(printf '%s\n' "${line}" | sed -n 's/.*"created_at":"\([^"]*\)".*/\1/p')"
  completed_steps="$(printf '%s\n' "${line}" | sed -n 's/.*"completed_steps":\([0-9][0-9]*\).*/\1/p')"
  total_steps="$(printf '%s\n' "${line}" | sed -n 's/.*"total_steps":\([0-9][0-9]*\).*/\1/p')"

  if [[ -z "${status}" || -z "${ref}" ]]; then
    continue
  fi

  case "${status}" in
    Running|running|InProgress|inprogress|"In Progress"|Queued|queued)
      running_refs+=("${ref}")
      build_id="${ref##*/}"
      running_build_ids+=("${build_id}")
      running_labels+=("${status} | ${name:-unknown} | ${completed_steps:-0}/${total_steps:-0} steps | ${created_at:-unknown}")
      ;;
  esac
done <<< "${history_output}"

if [[ ${#running_refs[@]} -eq 0 ]]; then
  echo "No currently running docker builds were found."
  echo "Tip: use 'docker buildx history ls --no-trunc' to inspect recent builds."
  exit 1
fi

selected_index=0

if [[ ${#running_refs[@]} -gt 1 ]]; then
  echo "Multiple running builds detected:"
  for i in "${!running_refs[@]}"; do
    num=$((i + 1))
    echo "  ${num}) ${running_build_ids[$i]} (${running_labels[$i]})"
  done

  read -r -p "Choose a build number to open logs: " selection
  if ! [[ "${selection}" =~ ^[0-9]+$ ]] || (( selection < 1 || selection > ${#running_refs[@]} )); then
    echo "Invalid selection."
    exit 1
  fi
  selected_index=$((selection - 1))
fi

selected_ref="${running_refs[$selected_index]}"
selected_build_id="${running_build_ids[$selected_index]}"
echo "Opening full build logs for: ${selected_build_id}"

exec docker buildx history logs "${selected_build_id}" --progress=plain