#!/usr/bin/env bash
# Copy a teaching subset of the Catalyst skills into courseware/.claude/skills so that
# Claude Code, opened in the courseware/ folder, offers them as /product-requirements-document,
# /data-contract and so on. Learners get the same skills through the Catalyst Copilot plugin.
# Re-run after a Catalyst update. Source of truth: reference/DataCreators-client/ai-skills/catalyst/skills.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
SRC="$ROOT/reference/DataCreators-client/ai-skills/catalyst/skills"
DST="$ROOT/courseware/.claude/skills"
SKILLS=(
  dplc-concierge dplc-design dplc-build dplc-preflight
  consumer-use-case-map feasibility-report business-case requirements-acceptance-criteria
  product-requirements-document data-contract data-model transformation-spec architecture-diagram
  data-quality-controls-plan nfr-specification rfd-authoring
  setup-dbt-project write-dbt-source write-dbt-model validate-dbt adding-dbt-unit-test dbt-best-practices
  generate-dag validate-dag runbook sla-dashboard-spec consumer-onboarding-guide release-notes
)
mkdir -p "$DST"
for s in "${SKILLS[@]}"; do
  if [[ -d "$SRC/$s" ]]; then rm -rf "$DST/$s"; cp -R "$SRC/$s" "$DST/$s"; else echo "missing in Catalyst: $s" >&2; fi
done
cp -R "$SRC/_lib" "$DST/_lib" 2>/dev/null || true
echo "$(ls -d "$DST"/*/ | wc -l | tr -d ' ') skill folders in $DST"
ls "$DST"
