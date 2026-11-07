#!/usr/bin/env bash
# Re-prepare starter journeys from the current starters, then rerun the whole suite on final sources.
set -euo pipefail
cd /workspaces/edo-training-data-products
R=.local/live/20261005T141153Z
python3 -m py_compile scripts/challenge-v2.py
[[ -f $R/suite.tsv ]] && mv $R/suite.tsv "$R/suite-run3-$(date -u +%H%M%S).tsv"
python3 scripts/challenge-v2.py list | while read -r tool phase state; do
  [[ $state == offered ]] || continue
  rm -rf "$R/journeys/starter/$tool-$phase"
  python3 scripts/challenge-v2.py prepare "$tool" "$phase" --workspace "$R/journeys/starter/$tool-$phase" >/dev/null
done
rm -f $R/journeys/solution/*/.solution-applied
mise run databricks:oauth-refresh >/dev/null 2>&1 || true
python3 $R/run-suite.py suite.tsv
