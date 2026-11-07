"""DBX-WASTE-005: materialization vs read-count observations (info-only)."""

from __future__ import annotations

import re
from typing import Any

from .common import (
    Finding,
    WAREHOUSE_QUERY_HISTORY_DAYS,
)


def evaluate_dbx_waste_005(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> list[Finding]:
    """Info-only diagnostic: surface read-count observations per the catalog.

    Per critic verdict (2): this rule is demoted to info-only. We emit the
    read-count signal but no recommendation. ``apply_mode_supported: False``,
    ``severity: info``, no ``config_delta`` - evidence-only.
    """
    findings: list[Finding] = []
    manifest = (dbt_config or {}).get("manifest") or {}
    if manifest.get("status") != "merged":
        return findings
    models = manifest.get("models") or {}

    queries = runs.get("warehouse_query_history") or []
    if not models or not queries:
        return findings

    # Per-object read counts: derive from bounded identifier matches.
    # We still avoid full SQL parsing here, but we require identifier
    # boundaries to reduce alias/prefix false positives, and we strip
    # comments + single-quoted string literals so an alias mentioned in
    # a comment or a SQL string constant doesn't count as a read.
    reads_per_day: dict[str, float] = {}

    def _strip_sql_noise(text: str) -> str:
        # /* block comments */ (non-greedy, multiline)
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
        # -- line comments through end of line
        text = re.sub(r"--[^\n]*", " ", text)
        # 'single-quoted strings' with doubled-quote escapes
        text = re.sub(r"'(?:[^']|'')*'", " ", text)
        # Double-quoted content: ANSI-mode treats "name" as a quoted
        # identifier (and the FQN matcher below understands that via the
        # [`"]? wrapper), but default-mode treats "..." as a string
        # literal where an embedded FQN must NOT count as a read. Only
        # strip when the content has whitespace (true string literal);
        # leave identifier-shaped content intact so `"analytics"."fct"`
        # still matches.
        def _maybe_strip_dq(m: re.Match) -> str:
            content = m.group(0)[1:-1]
            if not content or re.search(r"\s", content):
                return " "
            return m.group(0)
        text = re.sub(r'"(?:[^"]|"")*"', _maybe_strip_dq, text)
        return text

    def _query_mentions_model(query_text: str, schema: str, alias: str) -> bool:
        if not alias:
            return False
        alias_re = re.escape(alias)
        quoted_alias = rf'(?:[`\"]?{alias_re}[`\"]?)'
        if schema:
            schema_re = re.escape(schema)
            quoted_schema = rf'(?:[`\"]?{schema_re}[`\"]?)'
            # Require schema-qualified identifier with boundaries.
            fqn_pat = rf'(?<![\w]){quoted_schema}\s*\.\s*{quoted_alias}(?![\w])'
            return re.search(fqn_pat, query_text) is not None

        # Schema is missing: only count conservative table-position refs
        # to avoid broad alias collisions in SELECT lists/CTEs/comments.
        from_join_pat = rf'\b(from|join|update|into|table)\s+{quoted_alias}(?![\w])'
        return re.search(from_join_pat, query_text) is not None

    for unique_id, info in models.items():
        schema = info.get("schema") or ""
        alias = info.get("alias") or unique_id.split(".")[-1]
        alias_norm = alias.lower()
        schema_norm = schema.lower()
        if not alias_norm:
            continue
        hits = 0
        for q in queries:
            raw = (q.get("query_text") or q.get("statement") or "").lower()
            qtext = _strip_sql_noise(raw)
            if _query_mentions_model(qtext, schema_norm, alias_norm):
                hits += 1
        reads_per_day[unique_id] = round(
            hits / max(WAREHOUSE_QUERY_HISTORY_DAYS, 1), 3
        )

    flagged: dict[str, dict[str, Any]] = {}
    for unique_id, info in models.items():
        mat = (info.get("materialized") or "").lower()
        rpd = reads_per_day.get(unique_id, 0.0)
        if mat == "table" and 0 < rpd < 3:
            flagged[unique_id] = {"materialized": mat, "reads_per_day": rpd, "hint": "table with low reads"}
        elif mat == "view" and rpd > 20:
            flagged[unique_id] = {"materialized": mat, "reads_per_day": rpd, "hint": "view with high reads"}

    if not flagged:
        return findings

    findings.append(
        Finding(
            rule_id="DBX-WASTE-005",
            severity="info",
            title="Materialization vs read-count observations",
            evidence={
                "models_flagged_count": len(flagged),
                "samples": dict(list(flagged.items())[:10]),
                "note": (
                    "Info-only diagnostic per findings-catalog.md DBX-WASTE-005. "
                    "Read count is an observation; the engineer decides whether "
                    "to change materialization based on refresh cost, SLA, view "
                    "body complexity, and downstream tooling."
                ),
            },
            remediation={
                "summary": (
                    "Diagnostic only - no automated recommendation. See evidence "
                    "for the list of models and their observed read counts."
                ),
                "config_delta": {},
                "affected_files": [],
            },
            apply_mode_supported=False,
            confidence="low",
        )
    )
    return findings


# DBX-WASTE-006 (Incremental-candidate runtime-growth diagnostic) is
# withdrawn. The signal requires a 14-point per-model runtime history
# (slope over time), which the bundled collector has no reliable way
# to produce - dbt's run_results.json carries one run at a time and the
# skill is not stateful. The catalog entry remains for historical
# reference; the rule ID is reserved per RFD 0008's stable-ID rule and
# must not be reused. See references/findings-catalog.md for rationale.
