# tests/behavior/tests/test_claude_agent.py
"""Tests for ClaudeAgentRunner.

Mocks claude-agent-sdk's query() with an async generator that yields the
SDK's actual message types — keeps tests honest while staying offline.
"""
from pathlib import Path
import pytest

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

from tests.behavior.config import Config
from tests.behavior.runner.base import MaxStepsExceeded
from tests.behavior.runner.claude_agent import ClaudeAgentRunner

FIXTURES = Path(__file__).parent / "fixtures"


def _make_query_yielding(*messages):
    """Return an async iterator factory that yields the given messages."""
    async def fake_query(prompt, options=None):  # noqa: ARG001
        for m in messages:
            yield m
    return fake_query


def _assistant_text(text: str, *, in_tok=10, out_tok=5):
    return AssistantMessage(
        content=[TextBlock(text=text)],
        model="test",
        usage={"input_tokens": in_tok, "output_tokens": out_tok},
    )


def _assistant_tool_use(name: str, args: dict, tool_id: str = "tu_1"):
    return AssistantMessage(
        content=[ToolUseBlock(id=tool_id, name=name, input=args)],
        model="test",
        usage={"input_tokens": 5, "output_tokens": 5},
    )


class TestClaudeAgentRunner:
    def test_runs_no_tool_skill_to_completion(self):
        fake_q = _make_query_yielding(_assistant_text("final answer", in_tok=100, out_tok=20))
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)

        result = runner.run(FIXTURES / "tiny_skill.md", arguments="hi")

        assert result.output == "final answer"
        assert result.tool_calls == []
        assert result.sub_skills == []
        assert result.input_tokens == 100
        assert result.output_tokens == 20
        assert result.error is None

    def test_captures_tool_use_blocks(self):
        fake_q = _make_query_yielding(
            _assistant_tool_use("Bash", {"command": "ls"}),
            _assistant_text("done"),
        )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)

        result = runner.run(FIXTURES / "tiny_skill.md", arguments="hi")

        assert result.output == "done"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "Bash"
        assert result.tool_calls[0].args == {"command": "ls"}

    def test_max_steps_raised_when_sdk_signals_truncation(self):
        # claude-agent-sdk enforces max_turns server-side. We surface its
        # error string as MaxStepsExceeded for behavior cases.
        async def fake_q(prompt, options=None):  # noqa: ARG001
            yield _assistant_tool_use("Bash", {"command": "x"})
            yield ResultMessage(
                subtype="error",
                duration_ms=1, duration_api_ms=1, is_error=True,
                num_turns=1, session_id="s", total_cost_usd=0.0,
                usage={"input_tokens": 1, "output_tokens": 1},
                result="max_turns reached",
            )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)

        with pytest.raises(MaxStepsExceeded) as exc_info:
            runner.run(FIXTURES / "tiny_skill.md", arguments="hi", max_steps=1)
        assert exc_info.value.result.tool_calls
        assert exc_info.value.result.error and "max_turns" in exc_info.value.result.error

    def test_passes_max_turns_into_options(self):
        captured = {}

        async def fake_q(prompt, options=None):
            captured["options"] = options
            yield _assistant_text("ok")

        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        runner.run(FIXTURES / "tiny_skill.md", arguments="x", max_steps=7)
        assert isinstance(captured["options"], ClaudeAgentOptions)
        assert captured["options"].max_turns == 7


class TestSubSkillDetection:
    """Sub-skill routing detection — load-bearing for every dplc-* behavior case."""

    def test_skill_tool_use_records_sub_skill(self):
        fake_q = _make_query_yielding(
            _assistant_tool_use("Skill", {"skill": "data-modeling"}),
            _assistant_text("done"),
        )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        assert result.sub_skills == ["data-modeling"]

    def test_read_of_skill_md_counts_as_routing(self):
        """When orchestrators can't invoke Catalyst skills via the Skill tool
        directly (they're not in Claude Code's registry), they "route" by
        reading the sub-skill's SKILL.md and following inline. Treat that
        as a sub-skill invocation."""
        fake_q = _make_query_yielding(
            _assistant_tool_use("Read",
                                {"file_path": "/abs/path/skills/discover-data/SKILL.md"}),
            _assistant_text("done"),
        )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        assert result.sub_skills == ["discover-data"]

    def test_read_of_other_files_does_not_count(self):
        fake_q = _make_query_yielding(
            _assistant_tool_use("Read", {"file_path": "/abs/path/skills/discover-data/templates/foo.md"}),
            _assistant_text("done"),
        )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        assert result.sub_skills == []

    def test_self_invocation_excluded_and_counted(self, tmp_path: Path):
        """AICAT-127 / AICAT-74 anti-pattern: orchestrator calls
        `Skill({skill: <itself>})`. Must be excluded from sub_skills
        (it isn't routing) AND counted in self_invocations so failure
        messages can name the cause.

        Uses a directory-style fixture (`tmp_path/dplc-build-stage/SKILL.md`)
        so the runner's `skill_under_test` derivation (parent.name when the
        skill is a directory) sees "dplc-build-stage" — which is what makes
        the self-call self-recognized.
        """
        skill_dir = tmp_path / "dplc-build-stage"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: dplc-build-stage\ndescription: stub\nallowed-tools: Read\n---\n"
        )
        fake_q = _make_query_yielding(
            _assistant_tool_use("Skill", {"skill": "dplc-build-stage"}, tool_id="tu_1"),
            _assistant_tool_use("Skill", {"skill": "source-aligned"}, tool_id="tu_2"),
            _assistant_text("done"),
        )
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        result = runner.run(skill_dir, arguments="x")
        assert result.sub_skills == ["source-aligned"]
        assert result.self_invocations == 1


class TestWallClockTimeout:
    """Verify the move_on_after / aclosing path returns within bound and
    surfaces a timeout error. A regression here means cases hang indefinitely."""

    def test_timeout_returns_within_bound_with_partial_state(self, tmp_path, monkeypatch):
        import anyio

        # Fake query that yields one message, then awaits forever.
        async def fake_q(prompt, options=None):  # noqa: ARG001
            yield _assistant_tool_use("Bash", {"command": "echo hi"})
            await anyio.sleep_forever()

        # Tight timeout so the test is fast.
        monkeypatch.setenv("BEHAVIOR_TESTS_CASE_TIMEOUT_S", "1")
        cfg = Config.from_env()
        runner = ClaudeAgentRunner(config=cfg, query_fn=fake_q)

        import time as _t
        start = _t.monotonic()
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        elapsed = _t.monotonic() - start

        assert elapsed < 5, f"timeout did not fire within 5s; elapsed={elapsed:.1f}s"
        assert result.error and "wall-clock timeout" in result.error
        # Partial state preserved — we got at least the first tool call.
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "Bash"


class TestCleanupCascadeFix:
    """Regression: with --concurrency N, every concurrent ClaudeAgentRunner
    shares the same Python parent process. The post-timeout cleanup used
    to scan ps for 'my children running bundled/claude' and SIGKILL them,
    which nuked concurrent siblings spawned by other cases. Now we
    snapshot pre-existing PIDs and exclude them.

    These tests stub the underlying ps subprocess so we can verify the
    snapshot/exclude diff logic without spawning real subprocesses.
    """

    def test_kill_excludes_pids_present_at_snapshot(self, monkeypatch):
        from tests.behavior.runner import claude_agent as ca

        ps_output = (
            "111 99999 /_bundled/claude\n"  # sibling spawned by another case
            "222 99999 /_bundled/claude\n"  # spawned by THIS case
            "333 99999 /usr/bin/python\n"  # not bundled-claude
        )
        # Make _kill think we're pid 99999 (the parent of the bundled procs).
        monkeypatch.setattr(ca.os, "getpid", lambda: 99999)

        class FakeRun:
            def __init__(self, stdout): self.stdout = stdout
        monkeypatch.setattr(ca._sp, "run",
                            lambda *a, **k: FakeRun(ps_output))

        killed: list[int] = []
        monkeypatch.setattr(ca.os, "kill", lambda pid, sig: killed.append(pid))

        # 111 was the snapshot — it should NOT be killed; 222 should.
        ca._kill_bundled_claude_children(exclude={111})
        assert killed == [222]

    def test_snapshot_only_returns_my_bundled_children(self, monkeypatch):
        from tests.behavior.runner import claude_agent as ca

        ps_output = (
            "111 99999 /_bundled/claude\n"        # mine + bundled — include
            "222 88888 /_bundled/claude\n"        # someone else's child — skip
            "333 99999 /bundled/something_else\n"  # mine but not bundled-claude — skip
            "444 99999 /_bundled/claude --x\n"    # mine + bundled — include
        )
        monkeypatch.setattr(ca.os, "getpid", lambda: 99999)
        class FakeRun:
            def __init__(self, stdout): self.stdout = stdout
        monkeypatch.setattr(ca._sp, "run",
                            lambda *a, **k: FakeRun(ps_output))

        snap = ca._snapshot_bundled_claude_pids()
        assert snap == {111, 444}


class TestSandboxCleanup:
    """The per-case tempdir is scratch; nothing should leak."""

    def test_sandbox_dir_removed_after_run(self, tmp_path, monkeypatch):
        sandbox_root = tmp_path / "sandboxes"
        monkeypatch.setenv("BEHAVIOR_TESTS_SANDBOX_ROOT", str(sandbox_root))

        fake_q = _make_query_yielding(_assistant_text("ok"))
        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        runner.run(FIXTURES / "tiny_skill.md", arguments="x")

        # The sandbox root may exist (mkdir at start) but no behavior-test-* leftover.
        leftovers = list(sandbox_root.glob("behavior-test-*"))
        assert leftovers == [], f"leaked sandbox dirs: {leftovers}"


class TestOptionsAssembly:
    """Confirm every defense layer reaches ClaudeAgentOptions, not just max_turns."""

    def test_all_bounds_present_in_options(self):
        captured = {}

        async def fake_q(prompt, options=None):
            captured["options"] = options
            yield _assistant_text("ok")

        cfg = Config.from_env()
        runner = ClaudeAgentRunner(config=cfg, query_fn=fake_q)
        runner.run(FIXTURES / "tiny_skill.md", arguments="x", max_steps=10)
        opts = captured["options"]

        assert opts.max_turns == 10
        # Sandbox profile applied
        assert opts.sandbox is not None
        assert opts.sandbox.get("enabled") is True
        # Sub-agent bounded
        assert opts.agents and "general-purpose" in opts.agents
        sub = opts.agents["general-purpose"]
        assert sub.maxTurns == cfg.max_turns_ceiling
        assert "Agent" in (sub.disallowedTools or [])
        # Dollar cap applied (default $5)
        assert opts.max_budget_usd == cfg.max_budget_usd
        # Repo on add_dirs so reads of skills/ work
        assert opts.add_dirs and any("catalyst" in d for d in opts.add_dirs)


class TestSecretsRedaction:
    """Regression: when the agent dumps a known secret into a tool-call arg
    or its response, the runner must scrub it before the result hits cache,
    dashboard, or report. Real incident: agent ran `env | grep CONFLUENCE`
    then `curl -u user:$TOKEN ...` and the token landed in the bash command
    string we'd persisted to disk."""

    def test_secret_in_bash_command_is_redacted(self, monkeypatch: pytest.MonkeyPatch):
        secret = "ATATT3xFfGF0SHR5EmNsyTDk-fake-test-value"
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", secret)
        bash = _assistant_tool_use(
            "Bash",
            {"command": f'curl -s -u "user:{secret}" https://example/'},
            tool_id="tu_1",
        )
        result_msg = ResultMessage(
            subtype="success", duration_ms=100, duration_api_ms=80,
            is_error=False, num_turns=1, session_id="s",
            total_cost_usd=0.0,
            usage={"input_tokens": 1, "output_tokens": 1},
        )
        runner = ClaudeAgentRunner(
            config=Config.from_env(), query_fn=_make_query_yielding(bash, result_msg),
        )
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        # The Bash tool call should still be there, but the secret value
        # replaced with the named placeholder.
        bash_calls = [tc for tc in result.tool_calls if tc.name == "Bash"]
        assert bash_calls, "expected a Bash tool call"
        assert secret not in bash_calls[0].args["command"]
        assert "<redacted:CONFLUENCE_API_TOKEN>" in bash_calls[0].args["command"]

    def test_secret_in_assistant_text_is_redacted(self, monkeypatch: pytest.MonkeyPatch):
        secret = "ATATT3xFfGF0SHR5EmNsyTDk-fake-test-value"
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", secret)
        # Agent echoes the token in its visible text (e.g., "I'll use TOKEN=xyz").
        msg = _assistant_text(f"using token {secret} for the request")
        result_msg = ResultMessage(
            subtype="success", duration_ms=10, duration_api_ms=8, is_error=False,
            num_turns=1, session_id="s", total_cost_usd=0.0,
            usage={"input_tokens": 1, "output_tokens": 1},
        )
        runner = ClaudeAgentRunner(
            config=Config.from_env(), query_fn=_make_query_yielding(msg, result_msg),
        )
        result = runner.run(FIXTURES / "tiny_skill.md", arguments="x")
        assert secret not in result.output
        assert "<redacted:CONFLUENCE_API_TOKEN>" in result.output


class TestAnnotateError:
    """The SDK surfaces bash-sandbox kills as 'Command failed with exit
    code -9' — opaque without context. The annotator should rewrite to
    point at the actual Bash command that got killed."""

    def _annotate(self, err, tool_calls):
        from tests.behavior.runner.claude_agent import _annotate_error
        return _annotate_error(err, tool_calls)

    def test_passes_through_normal_errors(self):
        from tests.behavior.runner.base import ToolCall
        out = self._annotate("max_turns reached", [ToolCall(name="Bash", args={"command": "ls"})])
        assert out == "max_turns reached"

    def test_passes_through_none(self):
        assert self._annotate(None, []) is None

    def test_rewrites_sigkill_with_last_bash(self):
        from tests.behavior.runner.base import ToolCall
        err = "Command failed with exit code -9 (exit code: -9)\nError output: Check stderr output for details"
        calls = [
            ToolCall(name="Read", args={"file_path": "/x"}),
            ToolCall(name="Bash", args={"command": "mkdir -p /Users/rbap/code/catalyst/skills/foo/output"}),
        ]
        out = self._annotate(err, calls)
        assert "SIGKILL" in out
        assert "mkdir -p" in out
        assert "skills should produce artifacts in their reply text" in out.lower()

    def test_rewrites_sigkill_with_no_bash_context(self):
        out = self._annotate("Command failed with exit code -9", [])
        assert "SIGKILL" in out
        assert "no bash context" in out


class TestSystemOverride:
    def test_system_override_replaces_skill_body(self):
        captured = {}

        async def fake_q(prompt, options=None):
            captured["options"] = options
            yield _assistant_text("baseline output")

        runner = ClaudeAgentRunner(config=Config.from_env(), query_fn=fake_q)
        runner.run(
            FIXTURES / "tiny_skill.md",
            arguments="hello",
            system_override="You are a helpful assistant. Respond to: $ARGUMENTS",
        )
        sp = captured["options"].system_prompt
        assert "Echo the argument" not in sp
        assert "helpful assistant" in sp
        assert "Respond to: hello" in sp
