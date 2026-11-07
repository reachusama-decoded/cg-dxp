from tests.behavior.runner.base import (
    ToolCall, RunResult, MaxStepsExceeded,
)

class TestToolCall:
    def test_round_trip(self):
        tc = ToolCall(name="discover_tables", args={"catalog": "x"}, result=[1, 2, 3])
        assert tc.name == "discover_tables"
        assert tc.model_dump()["args"] == {"catalog": "x"}

class TestRunResult:
    def test_minimal_construction(self):
        r = RunResult(
            output="hello", tool_calls=[], sub_skills=[],
            duration_s=0.5, input_tokens=10, output_tokens=20,
        )
        assert r.error is None
        assert r.total_tokens == 30

    def test_total_tokens_property(self):
        r = RunResult(output="", tool_calls=[], sub_skills=[],
                      duration_s=0, input_tokens=100, output_tokens=50)
        assert r.total_tokens == 150

class TestMaxStepsExceeded:
    def test_carries_partial_result(self):
        partial = RunResult(output="incomplete", tool_calls=[], sub_skills=[],
                            duration_s=1, input_tokens=5, output_tokens=5)
        exc = MaxStepsExceeded("hit 25", result=partial)
        assert exc.result is partial
