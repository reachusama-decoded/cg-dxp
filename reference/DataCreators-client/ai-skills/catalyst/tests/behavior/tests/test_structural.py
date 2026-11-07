# tests/behavior/tests/test_structural.py
from pathlib import Path
import pytest

from tests.behavior.judge.structural import (
    run_check, StructuralCheckFailure,
)
from tests.behavior.cases import StructuralCheck
from tests.behavior.runner.base import ToolCall


class TestNonEmptyOutput:
    def test_passes_for_non_empty(self):
        run_check(StructuralCheck(name="non_empty_output"), "hello")

    def test_fails_for_empty(self):
        with pytest.raises(StructuralCheckFailure, match="non_empty_output"):
            run_check(StructuralCheck(name="non_empty_output"), "")

    def test_fails_for_whitespace_only(self):
        with pytest.raises(StructuralCheckFailure):
            run_check(StructuralCheck(name="non_empty_output"), "   \n\n  ")


class TestContainsSection:
    def test_passes_when_heading_present(self):
        text = "# Title\n\n## Discovered Tables\n\nbody"
        run_check(StructuralCheck(name="contains_section", args={"name": "Discovered Tables"}), text)

    def test_fails_when_heading_absent(self):
        with pytest.raises(StructuralCheckFailure, match="Discovered Tables"):
            run_check(StructuralCheck(name="contains_section", args={"name": "Discovered Tables"}), "no heading")


class TestHasMarkdownTable:
    def test_passes_for_table(self):
        text = "| a | b |\n|---|---|\n| 1 | 2 |\n"
        run_check(StructuralCheck(name="has_markdown_table"), text)

    def test_fails_when_no_table(self):
        with pytest.raises(StructuralCheckFailure):
            run_check(StructuralCheck(name="has_markdown_table"), "just prose")


class TestNoPlaceholderText:
    @pytest.mark.parametrize("placeholder", ["[TBD]", "[fill in]", "[Name]", "<placeholder>", "lorem ipsum"])
    def test_fails_for_placeholder(self, placeholder: str):
        with pytest.raises(StructuralCheckFailure, match="placeholder"):
            run_check(StructuralCheck(name="no_placeholder_text"), f"prefix {placeholder} suffix")

    def test_placeholder_in_inline_code_does_not_count(self):
        """Agents often include self-verification tables that name the
        placeholder syntax in inline code, e.g. 'No placeholder text
        (`[TBD]`, `[fill in]`) | ✅'. Those are mentions, not uses."""
        text = (
            "## Self-check\n\n"
            "| Check | Status |\n|---|---|\n"
            "| No placeholder text (`[TBD]`, `[fill in]`) | ✅ All filled |\n"
        )
        run_check(StructuralCheck(name="no_placeholder_text"), text)

    def test_placeholder_in_fenced_code_block_does_not_count(self):
        text = (
            "Example output:\n\n"
            "```\nUse [TBD] when unknown\n```\n\n"
            "Actual content above is fully populated.\n"
        )
        run_check(StructuralCheck(name="no_placeholder_text"), text)

    def test_markdown_checkbox_does_not_count_as_placeholder(self):
        """`- [x]` / `- [ ]` are GitHub-flavored task-list checkboxes, not
        placeholder syntax. Skills like phase-zero-checklist legitimately
        emit them; we shouldn't flag valid output as placeholder leakage."""
        text = (
            "## Pre-flight checklist\n\n"
            "- [x] Source data identified\n"
            "- [x] Stakeholders aligned\n"
            "- [ ] Open: regulatory review\n"
            "  - [x] Indented checked item\n"
            "* [X] Asterisk-marker, capital X\n"
        )
        run_check(StructuralCheck(name="no_placeholder_text"), text)

    def test_table_cell_checked_marker_does_not_count(self):
        """Agents emit `| [x] |` and `| [x]  |` inside markdown table cells
        as a 'checked / Yes' indicator. Skills like deployment-record and
        warranty-handoff-sign-off do this in their sign-off tables; not
        placeholder leakage."""
        text = (
            "| Step | Confirmed |\n"
            "|------|-----------|\n"
            "| Source data identified | [x] |\n"
            "| Stakeholders aligned    | [x]  |\n"
        )
        run_check(StructuralCheck(name="no_placeholder_text"), text)

    def test_real_placeholder_outside_code_still_fails(self):
        text = "## Phase 1\nOwner: [TBD]\n"
        with pytest.raises(StructuralCheckFailure, match="no_placeholder_text"):
            run_check(StructuralCheck(name="no_placeholder_text"), text)

    def test_passes_when_clean(self):
        run_check(StructuralCheck(name="no_placeholder_text"), "real content")


class TestMinLength:
    def test_passes_when_long_enough(self):
        run_check(StructuralCheck(name="min_length", args={"value": 5}), "abcdef")

    def test_fails_when_too_short(self):
        with pytest.raises(StructuralCheckFailure):
            run_check(StructuralCheck(name="min_length", args={"value": 5}), "abc")


class TestOutputContains:
    def test_passes_when_substring_present(self):
        run_check(StructuralCheck(name="output_contains", args={"value": "Connected to"}), "Connected to workspace.azuredatabricks.net")

    @pytest.mark.parametrize(
        "output",
        [
            "Authentication failed",   # substring absent
            "connected to workspace",  # present but wrong case (match is case-sensitive)
        ],
    )
    def test_fails_when_substring_absent(self, output: str):
        with pytest.raises(StructuralCheckFailure, match="output_contains"):
            run_check(StructuralCheck(name="output_contains", args={"value": "Connected to"}), output)

    def test_empty_value_rejected(self):
        with pytest.raises(StructuralCheckFailure, match="output_contains"):
            run_check(StructuralCheck(name="output_contains", args={"value": ""}), "anything")

    def test_non_string_value_rejected(self):
        # e.g. `- output_contains: 404` in YAML — the substring "404" is present,
        # but a non-string value must fail cleanly rather than raise TypeError.
        with pytest.raises(StructuralCheckFailure, match="output_contains"):
            run_check(StructuralCheck(name="output_contains", args={"value": 404}), "error 404 encountered")

    def test_bare_string_yaml_form_surfaces_cleanly(self):
        # `- output_contains` with no value parses to args={}; must raise a
        # StructuralCheckFailure, not a TypeError on the missing kwarg.
        check = StructuralCheck.from_yaml("output_contains")
        assert check.args == {}
        with pytest.raises(StructuralCheckFailure, match="output_contains"):
            run_check(check, "any output")

    def test_from_yaml_round_trip(self):
        check = StructuralCheck.from_yaml({"output_contains": "Connected to"})
        assert check.name == "output_contains"
        assert check.args == {"value": "Connected to"}
        run_check(check, "Connected to workspace.azuredatabricks.net")


class TestMatchesTemplate:
    def test_passes_when_headings_and_table_match(self, tmp_path: Path):
        template = tmp_path / "template.md"
        template.write_text(
            "# Title\n\n## Discovered Tables\n\n| Schema | Table | Relevance |\n|---|---|---|\n| x | y | HIGH |\n"
        )
        output = (
            "# Title\n\n## Discovered Tables — cspn_dev1\n\n"
            "| Schema | Table | Row Count | Relevance |\n|---|---|---|---|\n"
            "| s | t | 100 | HIGH |\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_fails_when_heading_missing(self, tmp_path: Path):
        template = tmp_path / "template.md"
        template.write_text("## Discovered Tables\n## SLAs\n")
        output = "## Discovered Tables — foo\n"
        with pytest.raises(StructuralCheckFailure, match="missing template headings"):
            run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_fails_when_table_columns_missing(self, tmp_path: Path):
        template = tmp_path / "template.md"
        template.write_text(
            "## Discovered Tables\n\n| Schema | Table | Relevance |\n|---|---|---|\n| x | y | z |\n"
        )
        output = (
            "## Discovered Tables\n\n| Schema | Table |\n|---|---|\n| s | t |\n"
        )
        with pytest.raises(StructuralCheckFailure, match="no output table has columns"):
            run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_fails_when_template_path_missing(self, tmp_path: Path):
        with pytest.raises(StructuralCheckFailure, match="template not found"):
            run_check(
                StructuralCheck(name="matches_template", args={"path": str(tmp_path / "nope.md")}),
                "any output",
            )

    def test_placeholder_in_template_heading_matches_filled_value(self, tmp_path: Path):
        """`## UC-1: [use case name]` in template should match `## UC-1: HR Analytics`
        in output — placeholder text is treated as a wildcard."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Use Cases\n\n## UC-1: [use case name]\n## UC-2: [use case name]\n"
        )
        output = (
            "## Use Cases\n\n## UC-1: HR Analytics Dashboard\n## UC-2: Workforce Planning\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_backtick_placeholder_in_heading_matches(self, tmp_path: Path):
        """`## 3.1 \\`[schema].[table_name_a]\\`` should match `## 3.1 \\`gold.dim_employee\\``."""
        template = tmp_path / "template.md"
        template.write_text("## 3.1 `[schema].[table_name_a]`\n## 3.2 `[schema].[table_name_b]`\n")
        output = "## 3.1 `gold.dim_employee`\n## 3.2 `gold.fact_assignment`\n"
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_scaffold_prefix_is_boundary_aware(self, tmp_path: Path):
        """Template `## 3.1` must not falsely match output `## 3.10`."""
        template = tmp_path / "template.md"
        template.write_text("## 3.1 `[schema].[table]`\n")
        output = "## 3.10 `gold.dim_other`\n"
        with pytest.raises(StructuralCheckFailure, match="missing template headings"):
            run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_column_qualifier_in_parens_matches(self, tmp_path: Path):
        """Agent often qualifies column names with units / dates / timezones
        in parens (e.g. `Current Period (Apr 2026)`). Should match template's
        bare `Current Period`."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Metrics\n\n| Metric | Current Period | Prior Period |\n|---|---|---|\n| x | 1 | 2 |\n"
        )
        output = (
            "## Metrics\n\n"
            "| Metric | Current Period (Apr 2026) | Prior Period |\n"
            "|---|---|---|\n"
            "| churn | 1.2% | 1.5% |\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_column_with_slash_alternative_matches(self, tmp_path: Path):
        """`Source Table` template column should match `Source Table / Endpoint`."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Lineage\n\n| Source Table | Source Column |\n|---|---|\n| t | c |\n"
        )
        output = (
            "## Lineage\n\n"
            "| Source Table / Endpoint | Source Column |\n|---|---|\n| api/foo | id |\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_column_word_subset_covers_enriched_actual(self, tmp_path: Path):
        """Template column `Budget` should match agent's `Monthly Budget` —
        template's word-set {budget} is a subset of actual's {monthly, budget}."""
        template = tmp_path / "template.md"
        template.write_text("## C\n\n| Cost Category | Budget |\n|---|---|\n| Compute | 100 |\n")
        output = "## C\n\n| Cost Category | Monthly Budget |\n|---|---|\n| Compute | 100 |\n"
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_column_word_subset_does_not_substring_match(self, tmp_path: Path):
        """`Score` template column must NOT match actual `Subscore` — substring
        overlap is rejected, only word-level subset counts."""
        template = tmp_path / "template.md"
        template.write_text("## S\n\n| Score | Weight |\n|---|---|\n| 1 | 1 |\n")
        output = "## S\n\n| Subscore | Weight |\n|---|---|\n| 1 | 1 |\n"
        with pytest.raises(StructuralCheckFailure, match="no output table has columns"):
            run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_unicode_dash_variants_in_column_names_match(self, tmp_path: Path):
        """`Score (0-100)` template should match `Score (0–100)` agent output (en-dash)."""
        template = tmp_path / "template.md"
        template.write_text("## S\n\n| Score (0-100) | Weight |\n|---|---|\n| 50 | 1 |\n")
        output = "## S\n\n| Score (0–100) | Weight |\n|---|---|\n| 50 | 1 |\n"
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_role_placeholder_pattern_works_for_new_nouns(self, tmp_path: Path):
        """The role-placeholder detector is structural — any
        Capitalized-Word + single capital letter pattern triggers, so new
        template nouns (Adapter A, Cluster 1, Workflow X) work without
        editing the regex."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Topology\n"
            "### Adapter A\n"
            "### Adapter B\n"
            "### Workflow 1\n"
        )
        output = (
            "## Topology\n"
            "### EmployeeIngest\n"
            "### ContractorIngest\n"
            "### NightlyMerge\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_role_placeholder_in_heading_matches_real_name(self, tmp_path: Path):
        """Template `## Source A -> Data Product` should match agent's
        `## Workday HCM -> Employee Directory`. 'Source A' / 'Consumer B' /
        'Example 1' are recognized placeholder names."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Inbound\n"
            "#### Source A -> Data Product\n"
            "#### Source B -> Data Product\n"
            "## Outbound\n"
            "#### Data Product -> Consumer A\n"
        )
        output = (
            "## Inbound\n"
            "#### Workday HCM -> Employee Directory\n"
            "#### Azure AD -> Employee Directory\n"
            "## Outbound\n"
            "#### Employee Directory -> HR Analytics\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_repeated_numeric_siblings_only_first_required(self, tmp_path: Path):
        """Templates often have `### 3.1`, `### 3.2`, `### 3.3` as repeated
        example sections — agent only needs to produce N=1 of them depending
        on the use case. Subsequent same-depth numeric siblings are dropped
        from the required list."""
        template = tmp_path / "template.md"
        template.write_text(
            "## 3. Models\n"
            "### 3.1 `[schema].[table_a]`\n"
            "### 3.2 `[schema].[table_b]`\n"
            "### 3.3 `[schema].[table_c]`\n"
            "## 4. Done\n"
        )
        # Output has only one model — 3.1
        output = (
            "## 3. Models\n"
            "### 3.1 `gold.dim_employee`\n"
            "## 4. Done\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_pure_placeholder_heading_matches_anything(self, tmp_path: Path):
        """`## [Outcome name]` is a pure placeholder — matches any heading at that level."""
        template = tmp_path / "template.md"
        template.write_text("## Goals\n## [Outcome name]\n")
        output = "## Goals\n## Improve HR Reporting Latency\n"
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)

    def test_empty_visual_separator_row_not_treated_as_table_header(self, tmp_path: Path):
        """Templates that include a `| | | | |` empty-row visual gap inside a
        table must not trigger a false 'header' detection on the data row above."""
        template = tmp_path / "template.md"
        template.write_text(
            "## Schema\n\n"
            "| Column | Type |\n|---|---|\n"
            "| id | STRING |\n"
            "| | |\n"   # empty visual gap — must NOT count as a separator
        )
        output = (
            "## Schema\n\n"
            "| Column | Type |\n|---|---|\n"
            "| id | STRING |\n"
        )
        run_check(StructuralCheck(name="matches_template", args={"path": str(template)}), output)


class TestUsesComponents:
    def _tc(self, command: str) -> ToolCall:
        return ToolCall(name="Bash", args={"command": command})

    def test_passes_when_path_in_bash_command(self):
        run_check(
            StructuralCheck(name="uses_components", args={"components": ["skills/core/discover.py"]}),
            output="(no relevant output)",
            tool_calls=[self._tc("python -c 'from skills.core.discover import discover_tables; ...'")],
        )

    def test_passes_with_dotted_form(self):
        # Agent imported via dotted name; the check accepts both forms.
        run_check(
            StructuralCheck(name="uses_components", args={"components": ["skills/core/discover.py"]}),
            output="x",
            tool_calls=[self._tc("python -m skills.core.discover")],
        )

    def test_fails_when_component_not_referenced(self):
        with pytest.raises(StructuralCheckFailure, match="did not invoke expected components"):
            run_check(
                StructuralCheck(name="uses_components", args={
                    "components": ["skills/core/discover.py", "skills/clients/databricks.py"],
                }),
                output="x",
                tool_calls=[self._tc("echo hello")],
            )

    def test_lists_only_missing_components(self):
        with pytest.raises(StructuralCheckFailure, match=r"databricks\.py"):
            run_check(
                StructuralCheck(name="uses_components", args={
                    "components": ["skills/core/discover.py", "skills/clients/databricks.py"],
                }),
                output="x",
                tool_calls=[self._tc("from skills.core.discover import x")],
            )

    def test_no_components_passes_without_tool_calls(self):
        # Empty components list short-circuits to pass.
        run_check(
            StructuralCheck(name="uses_components", args={"components": []}),
            output="x",
            tool_calls=None,
        )


class TestReadsExemplar:
    def _read_tc(self, path: str) -> ToolCall:
        return ToolCall(name="Read", args={"file_path": path})

    def test_passes_when_agent_reads_exemplar(self):
        run_check(
            StructuralCheck(name="reads_exemplar", args={
                "paths": ["skills/architecture-diagram/templates/example-index-data-product.md"],
            }),
            output="some output",
            tool_calls=[self._read_tc(
                "skills/architecture-diagram/templates/example-index-data-product.md",
            )],
        )

    def test_passes_when_agent_reads_one_of_multiple(self):
        run_check(
            StructuralCheck(name="reads_exemplar", args={
                "paths": [
                    "skills/data-contract/templates/example-index-data-product.md",
                    "skills/data-contract/templates/example-investment-product.md",
                ],
            }),
            output="x",
            tool_calls=[self._read_tc(
                "skills/data-contract/templates/example-investment-product.md",
            )],
        )

    def test_fails_when_agent_skipped_exemplar(self):
        with pytest.raises(StructuralCheckFailure, match="reads_exemplar"):
            run_check(
                StructuralCheck(name="reads_exemplar", args={
                    "paths": ["skills/architecture-diagram/templates/example-index-data-product.md"],
                }),
                output="x",
                tool_calls=[self._read_tc(
                    "skills/architecture-diagram/templates/architecture-diagram.md",
                )],
            )

    def test_only_read_tool_calls_count(self):
        """A Bash command that mentions the exemplar path doesn't satisfy
        the check — only an actual Read does."""
        with pytest.raises(StructuralCheckFailure):
            run_check(
                StructuralCheck(name="reads_exemplar", args={
                    "paths": ["skills/architecture-diagram/templates/example-index-data-product.md"],
                }),
                output="x",
                tool_calls=[ToolCall(name="Bash", args={
                    "command": "cat skills/architecture-diagram/templates/example-index-data-product.md",
                })],
            )

    def test_empty_paths_short_circuits_to_pass(self):
        # Skill has no exemplar yet — auto-synthesis is a no-op.
        run_check(
            StructuralCheck(name="reads_exemplar", args={"paths": []}),
            output="x",
            tool_calls=None,
        )


class TestUnknownCheck:
    def test_unknown_name_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown structural check"):
            run_check(StructuralCheck(name="not_a_real_check"), "anything")
