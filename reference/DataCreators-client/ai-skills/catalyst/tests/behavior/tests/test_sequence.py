import pytest
from tests.behavior.judge.sequence import (
    SequenceFailure, assert_sub_skill_sequence,
)

class TestAssertSubSkillSequence:
    def test_strict_order_allow_extra_passes(self):
        actual = ["a", "x", "b", "y", "c"]
        expected = ["a", "b", "c"]
        assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=True)

    def test_strict_order_no_extras_passes_when_exact(self):
        actual = ["a", "b", "c"]
        expected = ["a", "b", "c"]
        assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=False)

    def test_strict_order_no_extras_fails_when_extra_present(self):
        actual = ["a", "x", "b", "c"]
        expected = ["a", "b", "c"]
        with pytest.raises(SequenceFailure, match="unexpected"):
            assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=False)

    def test_strict_order_fails_when_out_of_order(self):
        actual = ["b", "a", "c"]
        expected = ["a", "b", "c"]
        with pytest.raises(SequenceFailure, match="order"):
            assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=True)

    def test_unordered_passes_when_all_present(self):
        actual = ["c", "a", "b"]
        expected = ["a", "b", "c"]
        assert_sub_skill_sequence(actual, expected, strict_order=False, allow_extra=True)

    def test_missing_expected_fails(self):
        actual = ["a", "b"]
        expected = ["a", "b", "c"]
        with pytest.raises(SequenceFailure, match="missing"):
            assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=True)

    def test_skills_prefix_stripped_for_comparison(self):
        """Case YAMLs say `skills/foo`; Claude Code Skill tool invokes by bare
        name `foo`. Both forms should compare equal."""
        actual = ["foo", "bar", "baz"]
        expected = ["skills/foo", "skills/bar", "skills/baz"]
        assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=False)

    def test_normalization_works_in_either_direction(self):
        """`skills/foo` in actual and `foo` in expected also matches."""
        actual = ["skills/foo", "skills/bar"]
        expected = ["foo", "bar"]
        assert_sub_skill_sequence(actual, expected, strict_order=True, allow_extra=False)


class TestSelfInvocationDiagnostic:
    """When the failure cause is orchestrator self-invocation (AICAT-127),
    the failure message must name it so the user doesn't have to deduce
    'the orchestrator called itself' from absence of expected sub-skills.
    """

    def test_self_invocations_zero_omits_suffix(self):
        with pytest.raises(SequenceFailure) as exc:
            assert_sub_skill_sequence(
                [], ["a", "b"], strict_order=False, allow_extra=True,
                self_invocations=0,
            )
        assert "self-invoked" not in str(exc.value)

    def test_missing_with_self_invocation_appends_diagnostic(self):
        with pytest.raises(SequenceFailure) as exc:
            assert_sub_skill_sequence(
                [], ["a", "b"], strict_order=False, allow_extra=True,
                self_invocations=1,
            )
        msg = str(exc.value)
        assert "missing expected sub-skills" in msg
        assert "self-invoked via Skill tool 1 time" in msg
        assert "AICAT-127" in msg

    def test_self_invocations_pluralizes(self):
        with pytest.raises(SequenceFailure) as exc:
            assert_sub_skill_sequence(
                [], ["a"], strict_order=False, allow_extra=True,
                self_invocations=3,
            )
        assert "self-invoked via Skill tool 3 times" in str(exc.value)

    def test_strict_order_failure_includes_diagnostic(self):
        with pytest.raises(SequenceFailure) as exc:
            assert_sub_skill_sequence(
                ["b", "a"], ["a", "b"], strict_order=True, allow_extra=True,
                self_invocations=2,
            )
        msg = str(exc.value)
        assert "order mismatch" in msg
        assert "self-invoked" in msg

    def test_unexpected_present_failure_includes_diagnostic(self):
        with pytest.raises(SequenceFailure) as exc:
            assert_sub_skill_sequence(
                ["a", "x"], ["a"], strict_order=False, allow_extra=False,
                self_invocations=1,
            )
        msg = str(exc.value)
        assert "unexpected sub-skills present" in msg
        assert "self-invoked" in msg

    def test_default_self_invocations_param_is_back_compat(self):
        """Existing callers that don't pass self_invocations still work
        (param is keyword-only with a default of 0)."""
        with pytest.raises(SequenceFailure):
            assert_sub_skill_sequence(
                [], ["a"], strict_order=False, allow_extra=True,
            )
