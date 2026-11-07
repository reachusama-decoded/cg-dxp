# tests/behavior/tests/test_rubric.py
"""Tests for RubricJudge.

The judge wraps claude-agent-sdk's query(); tests inject a fake async
iterator that yields AssistantMessage with a JSON text block, the same
shape the real SDK delivers.
"""
import json
import pytest

from claude_agent_sdk import AssistantMessage, TextBlock

from tests.behavior.cases import Criterion, Rubric
from tests.behavior.config import Config
from tests.behavior.judge.rubric import RubricJudge, Verdict


def _fake_query_with_scores(scores: dict[str, float]):
    """Async iterator factory: yields one AssistantMessage with the JSON the
    judge expects. Scores arrive in the order given.
    """
    payload = {
        "criteria": [
            {"id": k, "score": v, "rationale": f"r-{k}"} for k, v in scores.items()
        ]
    }

    async def fake_query(prompt, options=None):  # noqa: ARG001
        yield AssistantMessage(
            content=[TextBlock(text=json.dumps(payload))],
            model="test",
            usage={"input_tokens": 50, "output_tokens": 20},
        )

    return fake_query


def _rubric() -> Rubric:
    return Rubric(
        threshold=0.75,
        criteria=[
            Criterion(id="a", weight=0.5, prompt="A?"),
            Criterion(id="b", weight=0.5, prompt="B?"),
        ],
    )


class TestRubricJudge:
    def test_pass_when_weighted_score_clears_threshold(self):
        judge = RubricJudge(
            config=Config.from_env(),
            query_fn=_fake_query_with_scores({"a": 0.9, "b": 0.8}),
        )
        verdict = judge.score(rubric=_rubric(), output="some output", skill_description="A skill")
        assert verdict.passed
        assert verdict.weighted_score == pytest.approx(0.85)

    def test_fail_when_weighted_score_below_threshold(self):
        judge = RubricJudge(
            config=Config.from_env(),
            query_fn=_fake_query_with_scores({"a": 0.5, "b": 0.4}),
        )
        verdict = judge.score(rubric=_rubric(), output="bad", skill_description="A skill")
        assert not verdict.passed

    def test_per_criterion_grades_present(self):
        judge = RubricJudge(
            config=Config.from_env(),
            query_fn=_fake_query_with_scores({"a": 0.7, "b": 0.9}),
        )
        verdict = judge.score(rubric=_rubric(), output="x", skill_description="A skill")
        ids = {g.id for g in verdict.grades}
        assert ids == {"a", "b"}
        a_grade = next(g for g in verdict.grades if g.id == "a")
        assert a_grade.score == 0.7
        assert a_grade.rationale == "r-a"

    def test_judge_token_counts_recorded(self):
        judge = RubricJudge(
            config=Config.from_env(),
            query_fn=_fake_query_with_scores({"a": 1.0, "b": 1.0}),
        )
        verdict = judge.score(rubric=_rubric(), output="x", skill_description="d")
        assert verdict.judge_input_tokens == 50
        assert verdict.judge_output_tokens == 20

    def test_missing_criterion_in_response_raises(self):
        judge = RubricJudge(
            config=Config.from_env(),
            query_fn=_fake_query_with_scores({"a": 0.9}),  # missing 'b'
        )
        with pytest.raises(ValueError, match="missing criterion 'b'"):
            judge.score(rubric=_rubric(), output="x", skill_description="d")
