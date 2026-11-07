"""Top-findings ranking and impact parsing.

Splits the small set of pure-data helpers used by ``evaluate()`` to build
the ``top_findings`` array. No I/O, no rule logic.
"""

from __future__ import annotations

import re
from typing import Any

from .common import _CONFIDENCE_RANK, _SEVERITY_RANK, TOP_FINDINGS_LIMIT


def _impact_or_zero(finding: dict[str, Any]) -> float:
    """Best-effort numeric impact parser for top-findings tie-breaking."""
    def _extract(raw: Any) -> float:
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str):
            m = re.search(r"-?\d+(?:\.\d+)?", raw.replace(",", ""))
            if m:
                return float(m.group(0))
        return 0.0

    top_level = _extract(finding.get("estimated_impact"))
    if top_level > 0:
        return top_level
    evidence = finding.get("evidence") or {}
    if isinstance(evidence, dict):
        return _extract(evidence.get("estimated_impact"))
    return 0.0


def _rank_top_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order by severity, estimated impact, then confidence."""
    def key(f: dict[str, Any]) -> tuple[int, float, int]:
        return (
            _SEVERITY_RANK.get(f.get("severity"), 99),
            -_impact_or_zero(f),
            _CONFIDENCE_RANK.get(f.get("confidence"), 99),
        )

    return sorted(findings, key=key)[:TOP_FINDINGS_LIMIT]
