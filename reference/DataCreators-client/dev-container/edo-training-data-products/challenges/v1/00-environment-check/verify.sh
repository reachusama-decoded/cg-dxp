#!/usr/bin/env bash
# 00 — environment check: the devcontainer toolchain + Databricks auth + Astro are ready.
set -uo pipefail
fail() { echo "  environment check: FAIL — $1"; exit 1; }

command -v dpc-check >/dev/null 2>&1 && dpc-check || fail "dpc-check not green (run 'mise run setup:databricks')"
databricks auth describe --profile DEFAULT >/dev/null 2>&1 || fail "Databricks auth not configured (mise run setup:databricks)"
astro version >/dev/null 2>&1 || fail "astro CLI missing"
echo "  environment check: PASS"
