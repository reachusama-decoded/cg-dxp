# tests/behavior/judge/structural.py
from __future__ import annotations
import inspect
import re
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from tests.behavior.cases import StructuralCheck
from tests.behavior.runner.base import ToolCall
from tests.behavior.runner.component_match import missing_components


class StructuralCheckFailure(AssertionError):
    """Raised when a structural pre-check fails. Includes the check name."""


# Placeholder syntax that means "the agent didn't fill this in." Alternation
# in one pass over the cleaned text — was 6 separate regex.search calls
# previously; this is N times faster as the list grows.
#
# `[X]` was previously included as a weak placeholder signal but caused
# too many false positives once the corpus grew: agents legitimately
# emit `[x]` as a "checked" indicator in markdown task lists
# (`- [x] Done`) and inside markdown table cells (`| [x] |` for a
# Confirmed column). Both are valid output. The remaining patterns are
# strong, unambiguous placeholder markers.
PLACEHOLDER_PATTERN = re.compile(
    r"\[TBD\]|\[fill in\]|<placeholder>|lorem ipsum|\[Name\]",
    re.IGNORECASE,
)

MARKDOWN_TABLE_RE = re.compile(r"^\|.+\|\s*\n\|[\s:|]*-[\s\-:|]*\|\s*\n", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# Separator row must contain at least one dash; otherwise an empty | | | | row
# (sometimes used as a visual gap inside a markdown table) gets mis-detected
# as a table separator and the row above it is treated as a header.
TABLE_HEADER_RE = re.compile(r"^\|(.+)\|\s*\n\|[\s:|]*-[\s\-:|]*\|\s*$", re.MULTILINE)


def _non_empty_output(text: str) -> None:
    if not text.strip():
        raise StructuralCheckFailure("non_empty_output: output was empty or whitespace")


def _min_length(text: str, value: int) -> None:
    if len(text) < value:
        raise StructuralCheckFailure(f"min_length: {len(text)} < {value}")


def _contains_section(text: str, name: str) -> None:
    # Match "# Name", "## Name — suffix", "### Name (foo)", etc.
    # Heading must START with the name; trailing context after a separator
    # (space, dash, em-dash, colon, paren) is OK.
    pattern = re.compile(
        rf"^#{{1,6}}\s+{re.escape(name)}(\s|$|[—\-:(])",
        re.MULTILINE,
    )
    if not pattern.search(text):
        raise StructuralCheckFailure(f"contains_section: no heading {name!r} found")


def _has_markdown_table(text: str) -> None:
    if not MARKDOWN_TABLE_RE.search(text):
        raise StructuralCheckFailure("has_markdown_table: no markdown table found")


def _has_yaml_frontmatter(text: str) -> None:
    if not text.lstrip().startswith("---"):
        raise StructuralCheckFailure("has_yaml_frontmatter: missing leading ---")


def _strip_code_spans(text: str) -> str:
    """Remove fenced code blocks and inline backtick spans. Agents commonly
    discuss placeholder syntax in self-verification tables (e.g. "No
    placeholder text (\`[TBD]\`, \`[fill in]\`) | ✅"); those mentions are
    in inline code spans and are NOT actual uses of the placeholder."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def _no_placeholder_text(text: str) -> None:
    m = PLACEHOLDER_PATTERN.search(_strip_code_spans(text))
    if m:
        raise StructuralCheckFailure(f"no_placeholder_text: found placeholder {m.group(0)!r}")


def _valid_markdown(text: str) -> None:
    fences = text.count("```")
    if fences % 2 != 0:
        raise StructuralCheckFailure("valid_markdown: unbalanced ``` code fences")


def _output_contains(text: str, value: str = "") -> None:
    # `value` defaults to "" so the bare-string YAML form (`- output_contains`
    # with no argument) parses to args={} and surfaces here as an empty value,
    # rather than a TypeError on a missing kwarg.
    if not value:
        raise StructuralCheckFailure("output_contains: value must be non-empty")
    if not isinstance(value, str):
        raise StructuralCheckFailure(
            f"output_contains: value must be a string, got {type(value).__name__}"
        )
    if value not in text:
        raise StructuralCheckFailure(f"output_contains: {value!r} not found in output")


# Template-heading placeholder syntax. Anything from the first occurrence
# of one of these markers onward is treated as a wildcard — the agent fills
# it in with real content.
#
# Two flavors:
# 1) Explicit markers: [foo], <foo>, `[bar]`, ${FOO}
# 2) Illustrative role placeholders: a Capitalized word followed by a single
#    uppercase letter or digit at a word boundary — "Source A", "Consumer B",
#    "Example 1", "Phase X". Templates use this convention generically; the
#    agent substitutes real names ("Workday HCM", "HR Analytics", etc).
#    Detected structurally so we don't have to enumerate every noun (the
#    previous 22-word allowlist was a Christmas-tree of special cases that
#    grew every time a template introduced a new domain).
PLACEHOLDER_MARKER_RE = re.compile(
    r"[\[<`]"          # explicit bracket / backtick markers
    r"|\$\{"           # ${VAR}
    r"|\b[A-Z][a-z]+\s+[A-Z0-9]\b"  # "Source A" / "Phase 1" — role + token
)


def _heading_scaffold(name: str) -> str:
    """Template headings often look like `## UC-1: [use case name]` or
    `## 3.1 \\`[schema].[table_name_a]\\``. Take everything BEFORE the first
    placeholder marker — that's the literal scaffolding the agent must keep.

    `## UC-1: [use case name]`         → `uc-1:`
    `## 3.1 \\`[schema].[table_name_a]\\`` → `3.1`
    `## Discovered Tables`             → `discovered tables`
    `## [Outcome name]`                → `` (empty — pure placeholder, matches anything)
    `## Source A -> Data Product`      → `` (arrow flow — both sides illustrative)
    """
    # Arrow-flow headings ("Source A -> Data Product", "Data Product -> Consumer B")
    # describe a relationship where both sides are variable. Treat the whole
    # heading as a placeholder.
    if re.search(r"\s+(?:->|→|-->)\s+", name):
        return ""
    m = PLACEHOLDER_MARKER_RE.search(name)
    scaffold = name[:m.start()] if m else name
    # Drop trailing whitespace + connector punctuation so a scaffold ending in
    # ": " or "— " doesn't accidentally require the same separator literally.
    scaffold = scaffold.rstrip(" \t.,;-—–")
    return scaffold.strip().lower()


def _heading_normal(name: str) -> str:
    """Output heading: lowercase, trim. Don't strip anything else — we need
    the full text to do prefix matching against the template scaffold."""
    return name.strip().lower()


def _heading_matches(scaffold: str, output_heading: str) -> bool:
    """Scaffold matches output heading if scaffold is a prefix of output AND
    the next character is non-alphanumeric (or the output ends there). This
    keeps `3.1` from matching `3.10` and `uc-1` from matching `uc-10`, while
    still allowing `uc-1: hr analytics` (next char `:`) and `3.1 \\`gold...\\``
    (next char space)."""
    if not scaffold:
        return True
    if output_heading == scaffold:
        return True
    if not output_heading.startswith(scaffold):
        return False
    return not output_heading[len(scaffold)].isalnum()


def _normalize_column_name(c: str) -> str:
    """Loose comparison key for table column headers. Real-world divergence
    between template and agent output:
    - Agent qualifies columns: `Current Period` → `Current Period (Apr 2026)`
    - Agent appends alternates: `Source Table` → `Source Table / Endpoint`
    - Unicode dash variants: `(0-100)` vs `(0–100)`
    The check should still treat all of these as matching.
    """
    c = c.strip().lstrip("*").strip()
    # Drop parenthetical qualifiers: "Current Period (Apr 2026)" -> "Current Period"
    c = re.sub(r"\s*\([^)]*\)", "", c)
    # Take the first option in slash-separated alternatives: "Source Table / Endpoint"
    c = c.split("/")[0]
    # Normalize Unicode dashes
    c = c.replace("–", "-").replace("—", "-")
    # Collapse whitespace + lowercase
    c = re.sub(r"\s+", " ", c).strip().lower()
    return c


def _parse_template_tables(template: str) -> list[set[str]]:
    tables: list[set[str]] = []
    for m in TABLE_HEADER_RE.finditer(template):
        cells = {_normalize_column_name(c) for c in m.group(1).split("|")}
        cells = {c for c in cells if c}
        if cells:
            tables.append(cells)
    return tables


def _matches_template(text: str, path: str) -> None:
    """Verify `text` has every H2+ heading from the template + a table whose
    columns cover each table's columns in the template.

    Heading matching is scaffold-prefix: a template heading like
    `## UC-1: [use case name]` matches any output heading starting with
    `UC-1:` (boundary-aware so `UC-1` does not match `UC-10`). Pure-placeholder
    headings (e.g. `## [Outcome name]`) match anything.

    Content is NOT compared (rubric handles that).
    """
    template_path = Path(path)
    if not template_path.exists():
        raise StructuralCheckFailure(f"matches_template: template not found at {path}")
    template = template_path.read_text()

    # Pure-numeric scaffolds (e.g. `3.1`, `3.2`) come from templates with
    # repeated "fill in once per X" example sections like `### 3.1
    # \`[schema].[table_name_a]\``. We do require at least the first one (3.1)
    # to anchor section ordering, but subsequent same-depth numeric siblings
    # are example placeholders — drop them. Same idea for letters: `Source A`
    # / `Source B` template headings are illustrative.
    NUMERIC_RE = re.compile(r"^\d+(\.\d+)*$")
    expected_scaffolds: list[str] = []
    for m in HEADING_RE.finditer(template):
        if len(m.group(1)) < 2:
            continue
        s = _heading_scaffold(m.group(2))
        if NUMERIC_RE.match(s) and any(
            NUMERIC_RE.match(prev) and prev.split(".")[:-1] == s.split(".")[:-1]
            for prev in expected_scaffolds
        ):
            continue  # sibling of an already-required numeric scaffold
        expected_scaffolds.append(s)
    actual_headings = [
        _heading_normal(m.group(2))
        for m in HEADING_RE.finditer(text)
        if len(m.group(1)) >= 2
    ]

    missing: list[str] = []
    for scaffold in expected_scaffolds:
        if not any(_heading_matches(scaffold, h) for h in actual_headings):
            missing.append(scaffold)
    if missing:
        # Numeric-sibling dedup is non-obvious: a template with `### 3.1`,
        # `### 3.2`, `### 3.3` only requires the first; any sibling missing
        # in the output means the agent never produced *any* heading at
        # that depth. Hint when the missing list looks numeric.
        hint = ""
        if any(NUMERIC_RE.match(m) for m in missing):
            hint = (
                " (note: numeric-sibling scaffolds like 3.1 / 3.2 / 3.3 are "
                "deduped — only the first per group is required, so a "
                "missing one means no heading at that depth was produced)"
            )
        raise StructuralCheckFailure(
            f"matches_template: missing template headings {sorted(set(missing))} "
            f"(template={path}){hint}"
        )

    # Every template table's column set must be covered by some actual table.
    # "Covered" means: for each template column, there's an actual column whose
    # word-set is a superset of the template column's word-set. This handles
    # agent enrichment ("Budget" template → "Monthly Budget" actual) without
    # false-matching on substring overlap ("score" should not match "subscore").
    expected_tables = _parse_template_tables(template)
    actual_tables = _parse_template_tables(text)
    for i, want_cols in enumerate(expected_tables):
        if not any(_cols_covered_by(want_cols, have_cols) for have_cols in actual_tables):
            raise StructuralCheckFailure(
                f"matches_template: no output table has columns {sorted(want_cols)} "
                f"(template table #{i + 1} at {path})"
            )


def _cols_covered_by(template_cols: set[str], actual_cols: set[str]) -> bool:
    """Each template column must have an actual column whose words contain
    all of the template column's words. Word-level subset, not string subset."""
    actual_word_sets = [set(c.split()) for c in actual_cols]
    for tc in template_cols:
        tc_words = set(tc.split())
        if not any(tc_words.issubset(aws) for aws in actual_word_sets):
            return False
    return True


def _uses_components(
    text: str,
    components: Sequence[str],
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
) -> None:
    """Verify each component path was referenced by the agent.

    "Referenced" means the path string appears in the agent's output
    text or in a tool-call argument (Bash command, Read path, etc.).
    Tool-call *results* are intentionally excluded — those are external
    content the agent didn't choose, so a `Glob` whose result list
    contains the path doesn't prove the agent invoked it.

    Delegates to `runner.component_match.missing_components` so the
    structural check and the dashboard's coverage column agree on what
    "used" means.
    """
    if not components:
        return
    missing = missing_components(components, tool_calls=tool_calls, output_text=text)
    if missing:
        raise StructuralCheckFailure(
            f"uses_components: agent did not invoke expected components: {missing}"
        )


def _reads_exemplar(
    text: str,
    paths: Sequence[str],
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
) -> None:
    """Verify the agent read at least one exemplar file.

    Skills that ship a `templates/example-*.md` exemplar instruct the
    agent (via SKILL.md step 2) to read it before drafting. This check
    asserts the agent actually did — at least one of `paths` must show
    up as a Read tool call argument.

    If no `paths` are supplied (skill has no exemplar), the check is a
    no-op — auto-synthesis in `_augment_structural_checks` only adds
    this check when at least one example file exists on disk.
    """
    if not paths:
        return
    haystack: list[str] = []
    for tc in tool_calls or []:
        if tc.name != "Read":
            continue
        try:
            haystack.append(str(tc.args))
        except Exception:
            pass
    blob = "\n".join(haystack)
    if not any(p in blob for p in paths):
        raise StructuralCheckFailure(
            f"reads_exemplar: agent did not Read any of the skill's exemplars: {list(paths)}"
        )


CHECKS: dict[str, Callable[..., None]] = {
    "non_empty_output": _non_empty_output,
    "min_length": _min_length,
    "contains_section": _contains_section,
    "has_markdown_table": _has_markdown_table,
    "has_yaml_frontmatter": _has_yaml_frontmatter,
    "no_placeholder_text": _no_placeholder_text,
    "valid_markdown": _valid_markdown,
    "output_contains": _output_contains,
    "matches_template": _matches_template,
    "uses_components": _uses_components,
    "reads_exemplar": _reads_exemplar,
}


def run_check(
    check: StructuralCheck,
    output: str,
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
) -> None:
    fn = CHECKS.get(check.name)
    if fn is None:
        raise ValueError(f"Unknown structural check: {check.name!r}")
    sig = inspect.signature(fn)
    kwargs: dict[str, Any] = dict(check.args)
    # Pass tool_calls only if the predicate accepts it.
    if "tool_calls" in sig.parameters:
        kwargs["tool_calls"] = tool_calls
    fn(output, **kwargs)


def run_all(
    checks: list[StructuralCheck],
    output: str,
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
) -> None:
    for c in checks:
        run_check(c, output, tool_calls=tool_calls)
