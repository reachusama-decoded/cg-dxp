"""
dbt-unit-test — Markdown report generator.

Parses the JUnit XML produced by pytest and the test-cases JSON,
then writes a human-readable ``<model>_report.md`` file under the
same output directory.

Report structure
----------------
# dbt-unit-test Report — <model_name>

## Summary
| Metric | Count |
...

## TC001 — <description>
**Category** | **Scenario** | **Expected behaviour**
### Assertions
| Test | Status | Detail |
...
### Input data (seed tables)
### Expected output
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Internal data structures
# ---------------------------------------------------------------------------

@dataclass
class AssertionResult:
    name: str              # short assertion name, e.g. test_tc001_non_empty_output
    status: str            # passed | failed | skipped
    message: str = ""      # failure/skip message


@dataclass
class TCResult:
    tc_id: str             # TC001, TC002 …
    description: str
    category: str
    scenario: str
    expected_behavior: str
    tags: list[str]
    input_data: dict[str, list[dict[str, Any]]]
    expected_output: list[dict[str, Any]]
    pandas_query: str
    assertions: list[AssertionResult] = field(default_factory=list)

    @property
    def overall_status(self) -> str:
        statuses = {a.status for a in self.assertions}
        if "failed" in statuses:
            return "❌ FAILED"
        if statuses == {"skipped"}:
            return "⏭ SKIPPED"
        if "skipped" in statuses:
            return "⚠️ PARTIAL"
        return "✅ PASSED"

    @property
    def status_icon(self) -> str:
        s = self.overall_status
        return s.split()[0]   # just the emoji


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class MarkdownReportGenerator:
    """
    Generate a Markdown test report from JUnit XML + test-cases JSON.

    Parameters
    ----------
    xml_path:        Path to the pytest JUnit XML file.
    json_path:       Path to the dbt-unit-test test-cases JSON.
    model_name:      DBT model being tested.
    output_path:     Where to write the Markdown report.
    """

    def __init__(
        self,
        xml_path: Path | str,
        json_path: Path | str,
        model_name: str,
        output_path: Path | str,
    ) -> None:
        self.xml_path    = Path(xml_path)
        self.json_path   = Path(json_path)
        self.model_name  = model_name
        self.output_path = Path(output_path)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def generate(self) -> Path:
        """Parse sources and write Markdown. Returns output_path."""
        tc_defs   = self._load_test_cases()
        xml_data  = self._parse_xml()
        results   = self._merge(tc_defs, xml_data)
        md        = self._render(results)
        self.output_path.write_text(md, encoding="utf-8")
        return self.output_path

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _load_test_cases(self) -> list[dict[str, Any]]:
        with self.json_path.open(encoding="utf-8") as fh:
            return json.load(fh)

    def _parse_xml(self) -> dict[str, list[AssertionResult]]:
        """
        Returns mapping: classname (e.g. 'Test_TC001_Cast') →
                         list[AssertionResult].
        """
        if not self.xml_path.exists():
            return {}

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # JUnit XML may be wrapped in <testsuites> or start at <testsuite>
        testcases = root.findall(".//testcase")

        groups: dict[str, list[AssertionResult]] = {}
        for tc in testcases:
            classname = tc.get("classname", "")
            # strip module prefix:  module.path.ClassName → ClassName
            classname = classname.split(".")[-1]
            name      = tc.get("name", "")

            failure  = tc.find("failure")
            skipped  = tc.find("skipped")
            error    = tc.find("error")

            if failure is not None:
                status  = "failed"
                message = _trim(failure.get("message") or failure.text or "")
            elif error is not None:
                status  = "failed"
                message = _trim(error.get("message") or error.text or "")
            elif skipped is not None:
                status  = "skipped"
                message = _trim(skipped.get("message") or skipped.text or "")
            else:
                status  = "passed"
                message = ""

            ar = AssertionResult(name=name, status=status, message=message)
            groups.setdefault(classname, []).append(ar)

        return groups

    def _merge(
        self,
        tc_defs: list[dict[str, Any]],
        xml_data: dict[str, list[AssertionResult]],
    ) -> list[TCResult]:
        results: list[TCResult] = []

        for tc in tc_defs:
            tc_id    = tc.get("test_id", "TC???")
            category = tc.get("category", "")

            # Find matching XML class — class name pattern:
            # Test_TC001_Cast, Test_TC001_Filter, …
            # Look for any class that contains the tc_id (case-insensitive).
            assertions: list[AssertionResult] = []
            for classname, ars in xml_data.items():
                if tc_id.lower() in classname.lower():
                    assertions = ars
                    break

            results.append(TCResult(
                tc_id            = tc_id,
                description      = tc.get("description", ""),
                category         = category,
                scenario         = tc.get("input_scenario", tc.get("scenario", "")),
                expected_behavior= tc.get("expected_behavior", ""),
                tags             = tc.get("tags", []),
                input_data       = tc.get("input_data", {}),
                expected_output  = tc.get("expected_output", []),
                pandas_query     = tc.get("pandas_query", ""),
                assertions       = assertions,
            ))

        return results

    # ------------------------------------------------------------------
    # Markdown renderer
    # ------------------------------------------------------------------

    def _render(self, results: list[TCResult]) -> str:
        now      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        total    = len(results)
        passed   = sum(1 for r in results if "PASSED" in r.overall_status)
        failed   = sum(1 for r in results if "FAILED" in r.overall_status)
        skipped  = sum(1 for r in results if r.overall_status == "⏭ SKIPPED")
        partial  = sum(1 for r in results if "PARTIAL" in r.overall_status)

        lines: list[str] = []

        # ── Header ──────────────────────────────────────────────────────
        lines += [
            f"# dbt-unit-test Report — `{self.model_name}`",
            "",
            f"**Generated:** {now}  ",
            f"**Model:** `{self.model_name}`  ",
            "",
        ]

        # ── Summary table ───────────────────────────────────────────────
        lines += [
            "## Summary",
            "",
            "| Status | Count |",
            "|--------|-------|",
            f"| ✅ Passed  | {passed} |",
            f"| ❌ Failed  | {failed} |",
            f"| ⚠️ Partial | {partial} |",
            f"| ⏭ Skipped | {skipped} |",
            f"| **Total**  | **{total}** |",
            "",
        ]

        # Overall result line
        if failed == 0 and partial == 0:
            lines.append("**Overall: ✅ ALL TESTS PASSED**")
        elif failed > 0:
            lines.append(f"**Overall: ❌ {failed} TEST CASE(S) FAILED**")
        else:
            lines.append("**Overall: ⚠️ SOME TESTS PARTIALLY SKIPPED**")
        lines.append("")

        # ── Quick-navigation index ───────────────────────────────────────
        lines += ["## Test Cases", ""]
        for r in results:
            anchor = _md_anchor(f"{r.tc_id} — {r.description}")
            lines.append(f"- {r.status_icon} [{r.tc_id} — {r.description}](#{anchor})")
        lines.append("")

        # ── Per-test-case sections ───────────────────────────────────────
        lines.append("---")
        lines.append("")
        for r in results:
            lines += self._render_tc(r)

        return "\n".join(lines)

    def _render_tc(self, r: TCResult) -> list[str]:
        lines: list[str] = []

        # Section heading
        lines += [
            f"## {r.status_icon} {r.tc_id} — {r.description}",
            "",
        ]

        # Meta table
        lines += [
            "| Field | Value |",
            "|-------|-------|",
            f"| **Category** | `{r.category}` |",
            f"| **Tags** | {', '.join(f'`{t}`' for t in r.tags) if r.tags else '—'} |",
            f"| **Scenario** | {_escape_pipe(r.scenario)} |",
            f"| **Expected behaviour** | {_escape_pipe(r.expected_behavior)} |",
            f"| **Overall** | {r.overall_status} |",
            "",
        ]

        # ── Assertion results ────────────────────────────────────────────
        if r.assertions:
            lines += [
                "### Assertions",
                "",
                "| Assertion | Status | Detail |",
                "|-----------|--------|--------|",
            ]
            for a in r.assertions:
                icon   = _status_icon(a.status)
                name   = _friendly_assertion_name(a.name)
                detail = _escape_pipe(_truncate(a.message, 200))
                lines.append(f"| `{name}` | {icon} | {detail} |")
            lines.append("")
        else:
            lines += [
                "### Assertions",
                "",
                "> ⚠️ No assertion results found (tests may not have been run yet).",
                "",
            ]

        # ── Pandas query ─────────────────────────────────────────────────
        if r.pandas_query and r.pandas_query.strip().lower() not in ("", "false"):
            lines += [
                "### Pandas Query",
                "",
                "```python",
                r.pandas_query,
                "```",
                "",
            ]

        # ── Input data ───────────────────────────────────────────────────
        lines += ["### Input Data (Seed Tables)", ""]
        if r.input_data:
            for table_name, rows in r.input_data.items():
                lines += [f"**`{table_name}`**", ""]
                if rows:
                    headers = list(rows[0].keys())
                    lines.append("| " + " | ".join(headers) + " |")
                    lines.append("| " + " | ".join("---" for _ in headers) + " |")
                    for row in rows:
                        vals = [_escape_pipe(str(row.get(h, ""))) for h in headers]
                        lines.append("| " + " | ".join(vals) + " |")
                    lines.append("")
                else:
                    lines += ["> *(no rows)*", ""]
        else:
            lines += ["> *(no input data defined)*", ""]

        # ── Expected output ──────────────────────────────────────────────
        lines += ["### Expected Output", ""]
        if r.expected_output:
            headers = list(r.expected_output[0].keys())
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in r.expected_output:
                vals = [_escape_pipe(str(row.get(h, ""))) for h in headers]
                lines.append("| " + " | ".join(vals) + " |")
            lines.append("")
        else:
            lines += ["> *(empty — model should produce no output for this scenario)*", ""]

        lines += ["---", ""]
        return lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _status_icon(status: str) -> str:
    return {"passed": "✅ passed", "failed": "❌ failed", "skipped": "⏭ skipped"}.get(
        status, status
    )


def _friendly_assertion_name(name: str) -> str:
    """
    Convert test_tc001_non_empty_output → non_empty_output
    """
    m = re.match(r"test_tc\d+_(.*)", name, re.IGNORECASE)
    return m.group(1) if m else name


def _escape_pipe(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + " …"


def _trim(text: str) -> str:
    return text.strip() if text else ""


def _md_anchor(heading: str) -> str:
    """
    Approximate GitHub-flavoured Markdown anchor generation.
    """
    anchor = heading.lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = re.sub(r"[\s]+", "-", anchor)
    anchor = anchor.strip("-")
    return anchor
