"""Tests for the single source of truth for sub-skill detection.

Both claude_agent.py (live runs) and cache.py (re-judging) call into
sub_skill_detection. If the rule changes here, both paths must agree."""
from tests.behavior.runner.base import ToolCall
from tests.behavior.runner.sub_skill_detection import (
    collect_sub_skills,
    count_self_invocations,
    detect_sub_skill,
    is_self_invocation,
)


class TestDetectSubSkill:
    def test_skill_tool_call_via_skill_arg(self):
        assert detect_sub_skill("Skill", {"skill": "data-modeling"}) == "data-modeling"

    def test_skill_tool_call_via_name_arg(self):
        # Some SDK versions use `name` instead of `skill`
        assert detect_sub_skill("Skill", {"name": "discover-data"}) == "discover-data"

    def test_skill_tool_call_via_command_arg(self):
        # Anthropic's canonical form
        assert detect_sub_skill("Skill", {"command": "feasibility-report"}) == "feasibility-report"

    def test_read_of_skill_md_with_absolute_path(self):
        assert detect_sub_skill(
            "Read", {"file_path": "/Users/x/code/catalyst/skills/foo/SKILL.md"}
        ) == "foo"

    def test_read_of_skill_md_with_relative_path(self):
        assert detect_sub_skill("Read", {"file_path": "skills/bar/SKILL.md"}) == "bar"

    def test_read_of_template_does_not_count(self):
        assert detect_sub_skill(
            "Read", {"file_path": "skills/foo/templates/foo.md"}
        ) is None

    def test_read_of_unrelated_file_does_not_count(self):
        assert detect_sub_skill("Read", {"file_path": "/tmp/scratch.md"}) is None

    def test_other_tool_calls_do_not_count(self):
        assert detect_sub_skill("Bash", {"command": "ls"}) is None
        assert detect_sub_skill("Glob", {"pattern": "**/*.py"}) is None

    def test_empty_skill_args_returns_none(self):
        assert detect_sub_skill("Skill", {}) is None
        assert detect_sub_skill("Read", {}) is None

    def test_self_read_excluded_when_skill_under_test_matches(self):
        # Orchestrator reading its own SKILL.md at startup must not count
        # as a sub-skill invocation (AICAT-122).
        assert detect_sub_skill(
            "Read",
            {"file_path": "/repo/skills/dplc-design/SKILL.md"},
            skill_under_test="dplc-design",
        ) is None

    def test_self_read_excluded_with_relative_path(self):
        # skill_under_test must match regardless of absolute vs relative path.
        assert detect_sub_skill(
            "Read",
            {"file_path": "skills/dplc-design/SKILL.md"},
            skill_under_test="dplc-design",
        ) is None

    def test_self_read_still_detected_without_skill_under_test(self):
        # Without the filter, the self-read is counted (existing behaviour).
        assert detect_sub_skill(
            "Read", {"file_path": "/repo/skills/dplc-design/SKILL.md"}
        ) == "dplc-design"

    def test_other_skill_read_not_filtered_by_skill_under_test(self):
        # skill_under_test only excludes the skill itself; sub-skills still count.
        assert detect_sub_skill(
            "Read",
            {"file_path": "/repo/skills/data-modeling/SKILL.md"},
            skill_under_test="dplc-design",
        ) == "data-modeling"

    def test_self_skill_invocation_excluded_via_skill_arg(self):
        # AICAT-127 / AICAT-74: orchestrator calls Skill({skill: <itself>}).
        # detect_sub_skill must return None so the self-call doesn't
        # pollute the sub_skills list (it isn't routing anywhere).
        assert detect_sub_skill(
            "Skill",
            {"skill": "dplc-build-stage"},
            skill_under_test="dplc-build-stage",
        ) is None

    def test_self_skill_invocation_excluded_via_name_arg(self):
        assert detect_sub_skill(
            "Skill",
            {"name": "dplc-build-stage"},
            skill_under_test="dplc-build-stage",
        ) is None

    def test_self_skill_invocation_excluded_via_command_arg(self):
        assert detect_sub_skill(
            "Skill",
            {"command": "dplc-build-stage"},
            skill_under_test="dplc-build-stage",
        ) is None

    def test_other_skill_invocation_not_excluded(self):
        # Real sub-skill delegation must still register.
        assert detect_sub_skill(
            "Skill",
            {"skill": "source-aligned"},
            skill_under_test="dplc-build-stage",
        ) == "source-aligned"

    def test_self_skill_invocation_still_detected_without_skill_under_test(self):
        # Without skill_under_test, the harness can't tell "self" from a
        # legitimate sub-skill — the call is treated as routing.
        assert detect_sub_skill(
            "Skill", {"skill": "dplc-build-stage"}
        ) == "dplc-build-stage"


class TestIsSelfInvocation:
    def test_self_skill_call_is_self_invocation(self):
        assert is_self_invocation(
            "Skill", {"skill": "dplc-build-stage"}, "dplc-build-stage"
        )

    def test_self_skill_via_name_arg(self):
        assert is_self_invocation(
            "Skill", {"name": "dplc-build-stage"}, "dplc-build-stage"
        )

    def test_other_skill_call_is_not_self_invocation(self):
        assert not is_self_invocation(
            "Skill", {"skill": "source-aligned"}, "dplc-build-stage"
        )

    def test_self_read_is_not_self_invocation(self):
        # A self-Read is the harmless "load my own SKILL.md" pattern,
        # not the delegation anti-pattern. Only Skill-tool self-calls
        # count.
        assert not is_self_invocation(
            "Read",
            {"file_path": "skills/dplc-build-stage/SKILL.md"},
            "dplc-build-stage",
        )

    def test_no_skill_under_test_returns_false(self):
        # Without skill_under_test the harness can't define "self".
        assert not is_self_invocation(
            "Skill", {"skill": "dplc-build-stage"}, None
        )

    def test_unrelated_tool_call_returns_false(self):
        assert not is_self_invocation(
            "Bash", {"command": "ls"}, "dplc-build-stage"
        )


class TestCollectSubSkills:
    def test_collects_in_order(self):
        calls = [
            ToolCall(name="Skill", args={"skill": "a"}),
            ToolCall(name="Bash", args={"command": "ls"}),
            ToolCall(name="Read", args={"file_path": "skills/b/SKILL.md"}),
            ToolCall(name="Skill", args={"skill": "c"}),
        ]
        assert collect_sub_skills(calls) == ["a", "b", "c"]

    def test_empty_list(self):
        assert collect_sub_skills([]) == []

    def test_self_read_excluded_via_skill_under_test(self):
        # Simulates dplc-design reading its own SKILL.md, then delegating.
        calls = [
            ToolCall(name="Read", args={"file_path": "skills/dplc-design/SKILL.md"}),
            ToolCall(name="Skill", args={"skill": "data-modeling"}),
            ToolCall(name="Skill", args={"skill": "data-contract"}),
        ]
        result = collect_sub_skills(calls, skill_under_test="dplc-design")
        assert result == ["data-modeling", "data-contract"]
        assert "dplc-design" not in result

    def test_self_skill_invocation_excluded(self):
        # AICAT-127 trace shape: orchestrator first calls Skill on itself,
        # then proceeds to delegate to real sub-skills.
        calls = [
            ToolCall(name="Skill", args={"skill": "dplc-build-stage"}),
            ToolCall(name="Skill", args={"skill": "source-aligned"}),
            ToolCall(name="Skill", args={"skill": "build-checklist"}),
        ]
        result = collect_sub_skills(calls, skill_under_test="dplc-build-stage")
        assert result == ["source-aligned", "build-checklist"]
        assert "dplc-build-stage" not in result


class TestCountSelfInvocations:
    def test_no_self_calls_returns_zero(self):
        calls = [
            ToolCall(name="Skill", args={"skill": "source-aligned"}),
            ToolCall(name="Bash", args={"command": "ls"}),
        ]
        assert count_self_invocations(calls, "dplc-build-stage") == 0

    def test_counts_each_self_call(self):
        calls = [
            ToolCall(name="Skill", args={"skill": "dplc-build-stage"}),
            ToolCall(name="Skill", args={"skill": "source-aligned"}),
            ToolCall(name="Skill", args={"skill": "dplc-build-stage"}),
        ]
        assert count_self_invocations(calls, "dplc-build-stage") == 2

    def test_self_read_does_not_count(self):
        # Only Skill-tool self-calls count; a self-Read is harmless.
        calls = [
            ToolCall(name="Read", args={"file_path": "skills/dplc-build-stage/SKILL.md"}),
            ToolCall(name="Skill", args={"skill": "dplc-build-stage"}),
        ]
        assert count_self_invocations(calls, "dplc-build-stage") == 1

    def test_no_skill_under_test_returns_zero(self):
        calls = [ToolCall(name="Skill", args={"skill": "anything"})]
        assert count_self_invocations(calls, None) == 0
