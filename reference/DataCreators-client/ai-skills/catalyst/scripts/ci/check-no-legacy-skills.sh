#!/usr/bin/env bash
# CI wrapper: fails if legacy skill names appear outside the allowlist.
# Backs scripts/ci/legacy-skill-allowlist.txt and the pytest guard at
# tests/ci/test_no_legacy_skill_references.py.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec pytest tests/ci/test_no_legacy_skill_references.py -v
