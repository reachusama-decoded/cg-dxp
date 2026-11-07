#!/usr/bin/env python3
"""optimize-dbsql-query: static SQL performance scanner.

Scans `.sql` files (compiled dbt models or hand-written DBSQL queries)
for SQL-PERF-DBSQL-* findings. No SQL execution, no auto-fix.

Exit codes:
    0  success (report or apply)
    2  input error (bad --path, bad --mode)
    5  apply failure
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
_OPTIMIZE_HELPER = REPO_ROOT / "skills" / "_lib" / "optimize.py"


def _load_optimize_helper():
    spec = importlib.util.spec_from_file_location(
        "catalyst_lib_optimize", _OPTIMIZE_HELPER
    )
    assert spec and spec.loader, (
        f"could not load optimize helper at {_OPTIMIZE_HELPER}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_lib = _load_optimize_helper()
Finding = _lib.Finding
redact_tokens = _lib.redact_tokens
format_text = _lib.format_text
format_json = _lib.format_json
parse_mode = _lib.parse_mode


# --- Detection helpers ----------------------------------------------------

_SELECT_STAR_RE = re.compile(
    r"\bselect\s+\*\s+from\b", re.IGNORECASE | re.DOTALL
)
_WHERE_FN_RE = re.compile(
    r"\bwhere\b[^;]*?\b(UPPER|LOWER|DATE|CAST|SUBSTR|SUBSTRING|YEAR|MONTH|DAY)\s*\(\s*[A-Za-z_][A-Za-z0-9_\.]*\s*\)",
    re.IGNORECASE,
)
_FROM_COMMA_RE = re.compile(
    r"\bfrom\s+([A-Za-z_][A-Za-z0-9_\.]*(?:\s+\w+)?)\s*,\s*([A-Za-z_][A-Za-z0-9_\.]*(?:\s+\w+)?)",
    re.IGNORECASE,
)
_JOIN_NO_ON_RE = re.compile(
    r"\bjoin\s+[A-Za-z_][A-Za-z0-9_\.]*(?:\s+\w+)?\b(?![^;]*?\bon\b)",
    re.IGNORECASE,
)
_CREATE_DELTA_RE = re.compile(
    r"\bcreate\s+(?:or\s+replace\s+)?table\b[^;]*?\busing\s+delta\b[^;]*",
    re.IGNORECASE | re.DOTALL,
)


def _detect_select_star(target: str, sql: str) -> list:
    findings = []
    for m in _SELECT_STAR_RE.finditer(sql):
        findings.append(
            Finding(
                rule_id="SQL-PERF-DBSQL-001",
                severity="warning",
                target=target,
                message="SELECT * may scan more columns than needed",
                suggestion="enumerate required columns explicitly",
            )
        )
    return findings


def _detect_cross_join(target: str, sql: str) -> list:
    findings = []
    # Strip line comments to reduce noise
    cleaned = re.sub(r"--[^\n]*", "", sql)
    if _FROM_COMMA_RE.search(cleaned):
        findings.append(
            Finding(
                rule_id="SQL-PERF-DBSQL-002",
                severity="error",
                target=target,
                message="cross join detected (comma-separated FROM tables, no ON clause)",
                suggestion="use explicit JOIN ... ON <key> to avoid Cartesian product",
            )
        )
    # JOIN without ON: scan each JOIN segment
    for m in re.finditer(r"\bjoin\b", cleaned, re.IGNORECASE):
        tail = cleaned[m.end(): m.end() + 400]
        # find next JOIN or end-of-stmt
        next_join = re.search(r"\b(join|where|group\s+by|order\s+by|having|limit|;)\b", tail, re.IGNORECASE)
        segment = tail[: next_join.start()] if next_join else tail
        if not re.search(r"\bon\b|\busing\b", segment, re.IGNORECASE):
            findings.append(
                Finding(
                    rule_id="SQL-PERF-DBSQL-002",
                    severity="error",
                    target=target,
                    message="JOIN without ON clause (implicit cross join)",
                    suggestion="add ON <join_predicate> or USING (<col>)",
                )
            )
            break
    return findings


def _detect_where_function(target: str, sql: str) -> list:
    findings = []
    for m in _WHERE_FN_RE.finditer(sql):
        findings.append(
            Finding(
                rule_id="SQL-PERF-DBSQL-003",
                severity="warning",
                target=target,
                message=f"WHERE wraps column in {m.group(1).upper()}() - defeats data skipping",
                suggestion="rewrite predicate so the bare column appears on one side",
            )
        )
    return findings


def _detect_orderby_no_limit_subquery(target: str, sql: str) -> list:
    """Find ORDER BY inside a parenthesized subquery without LIMIT."""
    findings = []
    # Scan all parenthesized regions; primitive depth tracker.
    stack = []
    for i, ch in enumerate(sql):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            start = stack.pop()
            inner = sql[start + 1: i]
            if re.search(r"\border\s+by\b", inner, re.IGNORECASE) and not re.search(
                r"\blimit\b", inner, re.IGNORECASE
            ):
                # Only count if inner looks like a SELECT statement
                if re.search(r"\bselect\b", inner, re.IGNORECASE):
                    findings.append(
                        Finding(
                            rule_id="SQL-PERF-DBSQL-004",
                            severity="info",
                            target=target,
                            message="ORDER BY inside subquery without LIMIT - sort may be discarded",
                            suggestion="add LIMIT or move ORDER BY to the outer query",
                        )
                    )
    return findings


def _detect_missing_cluster_by(target: str, sql: str) -> list:
    findings = []
    for m in _CREATE_DELTA_RE.finditer(sql):
        stmt = m.group(0)
        if not re.search(r"\bcluster\s+by\b", stmt, re.IGNORECASE):
            findings.append(
                Finding(
                    rule_id="SQL-PERF-DBSQL-005",
                    severity="info",
                    target=target,
                    message="Delta CREATE TABLE missing CLUSTER BY hint",
                    suggestion="add CLUSTER BY (<col>) for liquid clustering",
                )
            )
    return findings


_DETECTORS = [
    _detect_select_star,
    _detect_cross_join,
    _detect_where_function,
    _detect_orderby_no_limit_subquery,
    _detect_missing_cluster_by,
]


def scan_sql(target: str, sql: str) -> list:
    findings = []
    for det in _DETECTORS:
        findings.extend(det(target, sql))
    return findings


def scan_path(path: Path) -> list:
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.rglob("*.sql"))
    findings = []
    for f in files:
        try:
            sql = f.read_text()
        except OSError:
            continue
        findings.extend(scan_sql(str(f), sql))
    return findings


# --- CLI ------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="optimize-dbsql-query",
        description="Scan SQL files for DBSQL performance issues.",
    )
    p.add_argument("--path", required=True, help="file or directory to scan")
    p.add_argument(
        "--mode",
        choices=["report", "apply", "dry-run"],
        default="report",
    )
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(redact_tokens(f"error: path not found: {args.path}"), file=sys.stderr)
        return 2

    try:
        apply, dry_run = parse_mode(args.mode)
    except ValueError as e:
        print(redact_tokens(f"error: {e}"), file=sys.stderr)
        return 2

    findings = scan_path(path)

    if args.format == "json":
        out = format_json(findings)
    else:
        out = format_text(findings)
    print(redact_tokens(out))

    # No auto-fix rules today; apply/dry-run are no-ops that succeed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
