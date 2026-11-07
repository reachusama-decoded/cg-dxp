"""Shared utilities for optimize-* capability skills.

Provides a common Finding shape plus report/apply mode plumbing used by
optimize-dbt-model, optimize-dbsql-query, and optimize-databricks-job.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Optional

Severity = Literal["info", "warning", "error"]


@dataclass
class Finding:
    rule_id: str
    severity: Severity
    target: str
    message: str
    suggestion: str
    before: Optional[str] = None
    after: Optional[str] = None
    applied: bool = False


# Token-shaped patterns scrubbed from output. Mirrors deploy-dab:
# prefix-anchored only (Bearer, dapi*, dsapi*), NOT bare 32-hex.
_TOKEN_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"\bdapi[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bdsapi[A-Za-z0-9]{16,}\b"),
]


def redact_tokens(text: str) -> str:
    """Scrub token-shaped substrings (Bearer/dapi/dsapi prefix-anchored)."""
    if not text:
        return text
    for pat in _TOKEN_PATTERNS:
        text = pat.sub("***", text)
    return text


def format_text(findings: list[Finding]) -> str:
    """Render findings as a human-readable plain text report."""
    if not findings:
        return "No findings."
    lines = []
    for f in findings:
        lines.append(
            f"[{f.severity.upper()}] {f.rule_id} {f.target}: {f.message}"
        )
        if f.suggestion:
            lines.append(f"  suggestion: {f.suggestion}")
        if f.applied:
            lines.append("  applied: yes")
    return "\n".join(lines)


def format_json(findings: list[Finding]) -> str:
    """Render findings as a JSON list of dicts."""
    return json.dumps([asdict(f) for f in findings])


def apply_finding(finding: Finding, dry_run: bool = False) -> bool:
    """Apply a finding by replacing `before` with `after` in target file.

    Returns True if replacement succeeded (or would succeed for dry_run).
    Returns False if before-text not found in file, or before/after absent,
    or target file missing. Sets finding.applied=True only on actual write.
    """
    if finding.before is None or finding.after is None:
        return False
    path = Path(finding.target)
    if not path.is_file():
        return False
    content = path.read_text()
    if finding.before not in content:
        return False
    if dry_run:
        return True
    path.write_text(content.replace(finding.before, finding.after))
    finding.applied = True
    return True


def parse_mode(argv_mode: str) -> tuple[bool, bool]:
    """Convert --mode value into (apply, dry_run) booleans."""
    if argv_mode == "report":
        return (False, False)
    if argv_mode == "apply":
        return (True, False)
    if argv_mode == "dry-run":
        return (False, True)
    raise ValueError(f"unknown mode: {argv_mode!r}")
