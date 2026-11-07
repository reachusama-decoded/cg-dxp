"""Component-reference predicate tests.

Regression target: `fetch-confluence.case-01-happy-path` from the first
full run. The agent ran three Globs that surfaced the expected component
paths in their *results* but never typed those paths in any tool arg or
output. The structural check used to count this as "used"; the dashboard
correctly counted it as 0/2. The helper now agrees with the dashboard.
"""
from __future__ import annotations

from tests.behavior.runner.base import ToolCall
from tests.behavior.runner.component_match import (
    component_referenced,
    coverage,
    missing_components,
)


def _glob_with_result(pattern: str, result_files: list[str]) -> ToolCall:
    """Glob tool call whose args reference `pattern` and whose result
    string contains `result_files` joined."""
    return ToolCall(
        name="Glob",
        args={"pattern": pattern},
        result=[{"type": "tool_result", "content": "\n".join(result_files)}],
    )


class TestComponentReferenced:
    def test_path_in_bash_command_arg_counts(self):
        bash = ToolCall(name="Bash", args={"command": "python -c 'from skills.core.discover import x'"})
        assert component_referenced("skills/core/discover.py", tool_calls=[bash])

    def test_path_in_read_arg_counts(self):
        read = ToolCall(name="Read", args={"file_path": "/abs/path/skills/core/discover.py"})
        assert component_referenced("skills/core/discover.py", tool_calls=[read])

    def test_path_in_output_text_counts(self):
        # Agent prose that explicitly names the component.
        assert component_referenced(
            "skills/clients/databricks.py",
            tool_calls=[],
            output_text="I'll route through skills/clients/databricks.py for the SQL.",
        )

    def test_path_only_in_tool_result_does_not_count(self):
        # The regression: Glob pattern is `skills/**/*.py`, result happens
        # to surface `skills/core/discover.py`. Agent never typed the path.
        # Old _uses_components rule: passes. New rule: fails (correctly).
        glob = _glob_with_result(
            "skills/**/*.py",
            ["skills/core/discover.py", "skills/clients/databricks.py"],
        )
        assert not component_referenced(
            "skills/core/discover.py",
            tool_calls=[glob],
            output_text="",
        )

    def test_dotted_import_form_also_counts(self):
        bash = ToolCall(name="Bash", args={"command": "from skills.core.discover import find"})
        # Same component expressed in dotted form
        assert component_referenced("skills/core/discover.py", tool_calls=[bash])

    def test_missing_component_returns_false(self):
        assert not component_referenced(
            "skills/core/nowhere.py",
            tool_calls=[ToolCall(name="Bash", args={"command": "echo hi"})],
            output_text="",
        )

    def test_no_tool_calls_no_output(self):
        assert not component_referenced("skills/core/x.py")


class TestCoverage:
    def test_per_component_verdict_in_declaration_order(self):
        components = ["skills/core/discover.py", "skills/clients/databricks.py", "skills/core/profiling.py"]
        bash = ToolCall(name="Bash", args={"command": "from skills.core.discover import x"})
        out = coverage(components, tool_calls=[bash], output_text="also touched skills.clients.databricks here")
        assert [c["component"] for c in out] == components
        assert out[0]["matched"] is True
        assert out[1]["matched"] is True
        assert out[2]["matched"] is False

    def test_empty_components_yields_empty(self):
        assert coverage([], tool_calls=[], output_text="anything") == []


class TestMissingComponents:
    def test_returns_only_unreferenced(self):
        components = ["skills/core/a.py", "skills/core/b.py"]
        bash = ToolCall(name="Bash", args={"command": "from skills.core.a import x"})
        assert missing_components(components, tool_calls=[bash]) == ["skills/core/b.py"]

    def test_empty_when_all_present(self):
        bash = ToolCall(
            name="Bash",
            args={"command": "from skills.core.a import x; from skills.core.b import y"},
        )
        assert missing_components(["skills/core/a.py", "skills/core/b.py"], tool_calls=[bash]) == []
