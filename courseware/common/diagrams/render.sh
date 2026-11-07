#!/usr/bin/env bash
# Render every src/*.mmd to png/<name>.png with mermaid-cli (same version as the sibling
# programme pins). The first run downloads mermaid-cli and a headless browser through npx.
# Usage: bash render.sh            all diagrams     bash render.sh d1-triage     one diagram
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:$PATH"
MMDC="npx -y -p @mermaid-js/mermaid-cli@11.17.0 mmdc"
mkdir -p png
fail=0
for f in src/*.mmd; do
  n="$(basename "${f%.mmd}")"
  if [[ $# -gt 0 && "$n" != "$1" ]]; then continue; fi
  if $MMDC -i "$f" -o "png/$n.png" -c mermaid-config.json -b white -s 2 >/dev/null 2>"/tmp/mmd-$n.log"; then
    echo "ok   $n"
  else
    echo "FAIL $n: $(grep -m1 -iE 'error|parse' "/tmp/mmd-$n.log" | cut -c1-140)"; fail=1
  fi
done
exit $fail
