"""SkillRunner that drives Claude via claude-agent-sdk.

Auth comes from the bundled `claude` CLI (Claude Code's OAuth session) or
from ANTHROPIC_API_KEY if set — claude-agent-sdk handles both paths.

No MCP: we don't register any custom MCP servers. The agent uses Claude
Code's built-in tools (Bash, Read, Grep, etc.). Sub-skill recursion happens
natively via Claude Code's skill system rather than via an `invoke_skill`
tool we expose.
"""
from __future__ import annotations
import os
import shutil
import subprocess as _sp
import tempfile
import time
from contextlib import aclosing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import anyio
from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

from tests.behavior.config import Config
from tests.behavior.runner.base import (
    MaxStepsExceeded,
    RunResult,
    SkillRunner,
    ToolCall,
)
from tests.behavior.runner.redaction import build_redactor, collect_secrets
from tests.behavior.runner.skill_loader import load_skill
from tests.behavior.runner.sub_skill_detection import (
    detect_sub_skill,
    is_self_invocation,
)


# ----------------------------------------------------------------- module config

def _build_sandbox_settings(allowed_domains: tuple[str, ...]) -> dict:
    """Sandbox profile applied to every case.

    macOS's bash sandbox restricts process isolation; FS write isolation is
    partial (skills can still write anywhere via Bash python3, so we rely
    on cwd-redirection + .gitignore for repo cleanliness). Network is
    allowlisted so Databricks SDK and Confluence work — the default is to
    block everything outbound.
    """
    return {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "excludedCommands": ["git", "databricks"],
        "network": {
            "allowedDomains": list(allowed_domains),
            "allowLocalBinding": True,
        },
    }

# Prepended to every test-run system prompt. The skills are designed to be
# interactive (Claude Code asks the user follow-up questions when context is
# missing); in this harness there is no human in the loop, so the agent must
# produce the full artifact end-to-end using reasonable inferred defaults.
# Domain-neutral so this works for any test scenario, not just HR analytics.
_TEST_MODE_PREAMBLE = (
    "You are running in an automated behavior-test harness. There is no "
    "interactive user. Do not ask clarifying questions and do not stop to "
    "request more information. Infer the most reasonable defaults from the "
    "request and any context already available, and produce the full "
    "requested artifact end-to-end. Where a fact is genuinely unknown "
    "(e.g. a person's name, team name, system identifier), invent a plausible "
    "value consistent with the scenario rather than stopping or emitting "
    "[TBD] / [fill in] / lorem-ipsum stubs.\n\n"
    "Your final output is the assistant message text you produce — not a "
    "file on disk. If the skill body says to 'produce' or 'write' an "
    "artifact, return its full contents in your reply. Do not mkdir or "
    "Write into `skills/`, `docs/`, or anywhere else in the source tree; "
    "those paths are read-only at test time and a write attempt will be "
    "killed by the sandbox. If you genuinely need a scratch file (rare), "
    "write it inside your current working directory.\n\n---\n\n"
)

_REPO_ROOT = Path(__file__).resolve().parents[3]


# ----------------------------------------------------------------- drive state

@dataclass
class _DriveState:
    """Mutable state populated as SDK messages stream in. Held outside the
    async loop so partial state survives wall-clock-timeout cancellation."""
    text_chunks: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    sub_skills: list[str] = field(default_factory=list)
    # Orchestrator self-invocations — Skill({skill: <self>}) tool calls.
    # Surfaced to RunResult so SequenceFailure can name the anti-pattern.
    self_invocations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None
    _tool_id_to_index: dict[str, int] = field(default_factory=dict)
    skill_under_test: Optional[str] = None


def _consume_message(msg: Any, state: _DriveState) -> None:
    """Process one SDK message into state."""
    if isinstance(msg, AssistantMessage):
        if msg.usage:
            state.input_tokens += int(msg.usage.get("input_tokens", 0) or 0)
            state.output_tokens += int(msg.usage.get("output_tokens", 0) or 0)
        for block in msg.content:
            if isinstance(block, TextBlock):
                state.text_chunks.append(block.text)
            elif isinstance(block, ToolUseBlock):
                _record_tool_use(block, state)
    elif isinstance(msg, UserMessage):
        # Tool results come back as content blocks on a UserMessage.
        if isinstance(msg.content, list):
            for block in msg.content:
                _link_tool_result(block, state)
    elif isinstance(msg, ResultMessage):
        if getattr(msg, "is_error", False):
            state.error = getattr(msg, "result", None) or "agent reported error"
        # Final accumulated counts when present.
        usage = getattr(msg, "usage", None)
        if usage:
            state.input_tokens = int(usage.get("input_tokens", state.input_tokens) or state.input_tokens)
            state.output_tokens = int(usage.get("output_tokens", state.output_tokens) or state.output_tokens)
    elif isinstance(msg, SystemMessage):
        pass  # init / metadata


def _record_tool_use(block: ToolUseBlock, state: _DriveState) -> None:
    """Append a tool-use to state and capture sub-skill routing.

    Sub-skill detection rule lives in sub_skill_detection.detect_sub_skill —
    one function, two callers (here for live runs, cache.py for re-judging
    old transcripts).
    """
    args = dict(block.input or {})
    state.tool_calls.append(ToolCall(name=block.name, args=args, result=None))
    state._tool_id_to_index[block.id] = len(state.tool_calls) - 1
    sub = detect_sub_skill(block.name, args, skill_under_test=state.skill_under_test)
    if sub:
        state.sub_skills.append(sub)
    elif is_self_invocation(block.name, args, state.skill_under_test):
        state.self_invocations += 1


def _link_tool_result(block: Any, state: _DriveState) -> None:
    """Pair a tool-result block with its originating ToolCall."""
    tu_id = getattr(block, "tool_use_id", None)
    if tu_id is None or tu_id not in state._tool_id_to_index:
        return
    idx = state._tool_id_to_index[tu_id]
    prev = state.tool_calls[idx]
    state.tool_calls[idx] = ToolCall(
        name=prev.name,
        args=prev.args,
        result=getattr(block, "content", None),
        is_error=bool(getattr(block, "is_error", False)),
    )


def _state_to_result(state: _DriveState, *, duration_s: float, error_override: Optional[str] = None) -> RunResult:
    # Redact known secret values from tool-call args/results and the output
    # text before anything is persisted. The agent has access to env vars
    # like CONFLUENCE_API_TOKEN inside the sandbox; if it pipes one into a
    # Bash command we'd otherwise serialize it to disk. See redaction.py.
    redact = build_redactor(collect_secrets())
    redacted_calls = [
        ToolCall(
            name=tc.name,
            args=redact(tc.args) if isinstance(tc.args, dict) else tc.args,
            result=redact(tc.result),
            is_error=tc.is_error,
        )
        for tc in state.tool_calls
    ]
    return RunResult(
        output=redact("".join(state.text_chunks)),
        tool_calls=redacted_calls,
        sub_skills=state.sub_skills,
        self_invocations=state.self_invocations,
        duration_s=duration_s,
        input_tokens=state.input_tokens,
        output_tokens=state.output_tokens,
        error=error_override or _annotate_error(state.error, redacted_calls),
    )


def _annotate_error(err: Optional[str], tool_calls: list[ToolCall]) -> Optional[str]:
    """Rewrite opaque SDK errors into something actionable.

    The SDK surfaces bash-sandbox kills as `Command failed with exit code
    -9 (exit code: -9)\\nError output: Check stderr output for details` —
    useless without context. When we see -9, dig into the last Bash
    tool-call to surface what command got killed, so the failure reason
    in the dashboard / cache file points at the actual cause.
    """
    if not err or "exit code -9" not in err:
        return err
    # Find the most recent Bash call — usually the one that got SIGKILL'd.
    last_bash = next(
        (tc for tc in reversed(tool_calls) if tc.name == "Bash"),
        None,
    )
    if last_bash is None:
        return f"sandbox killed agent subprocess (SIGKILL); no bash context. raw: {err.splitlines()[0]}"
    cmd = ""
    if isinstance(last_bash.args, dict):
        cmd = str(last_bash.args.get("command", ""))[:200]
    return (
        f"sandbox killed Bash command (SIGKILL): {cmd!r}. "
        f"Likely cause: write attempted outside cwd. "
        f"Skills should produce artifacts in their reply text, not by writing to disk."
    )


# ----------------------------------------------------------------- safety net

def _snapshot_bundled_claude_pids() -> set[int]:
    """PIDs of bundled-claude subprocesses that are children of the current
    process *right now*. Used to fingerprint pre-existing siblings so the
    cleanup sweep doesn't kill them when a concurrent case hits a timeout.
    """
    me = os.getpid()
    pids: set[int] = set()
    try:
        out = _sp.run(
            ["ps", "-A", "-o", "pid=,ppid=,command="],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except Exception:
        return pids
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid_s, ppid_s, cmd = parts
        if ppid_s == str(me) and "_bundled/claude" in cmd:
            try:
                pids.add(int(pid_s))
            except ValueError:
                pass
    return pids


def _kill_bundled_claude_children(*, exclude: Optional[set[int]] = None) -> None:
    """Belt-and-suspenders cleanup after wall-clock cancellation.

    The proper cancellation path uses `aclosing()` + `move_on_after`: the
    SDK's aclose() chain should terminate the bundled-claude subprocess.
    But if that fails (e.g. the SDK shields a hung subprocess.wait), this
    sweeps `ps -A` for any direct child of the current process running
    the bundled CLI and SIGKILLs them.

    With ThreadPoolExecutor concurrency, every concurrent ClaudeAgentRunner
    shares the same Python parent process — so naively killing 'my children
    running bundled/claude' nukes the siblings too. `exclude` is the PID
    set captured *before* this case's SDK call, scoping the kill to PIDs
    that appeared during this case only. Cases spawn one bundled-claude
    each, so the diff is tight.
    """
    exclude = exclude or set()
    me = os.getpid()
    try:
        out = _sp.run(
            ["ps", "-A", "-o", "pid=,ppid=,command="],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except Exception:
        return
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid_s, ppid_s, cmd = parts
        if ppid_s != str(me) or "_bundled/claude" not in cmd:
            continue
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        if pid in exclude:
            continue
        try:
            os.kill(pid, 9)
        except (ProcessLookupError, PermissionError):
            pass


# ----------------------------------------------------------------- runner

class ClaudeAgentRunner(SkillRunner):
    """SkillRunner backed by claude-agent-sdk.

    Reuses Claude Code's auth automatically (no ANTHROPIC_API_KEY required).
    Set ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN to redirect through
    Databricks (or any Anthropic-compatible endpoint).
    """

    def __init__(self, *, config: Config, query_fn: Any = query):
        self.config = config
        # query_fn is injectable so tests can swap in a fake without monkeypatching.
        self._query_fn = query_fn

    def run(
        self,
        skill_path: Path,
        arguments: str,
        max_steps: Optional[int] = None,
        system_override: Optional[str] = None,
        cache_key: Any = None,  # only used by CachingRunner; ignored here
    ) -> RunResult:
        skill = load_skill(skill_path, arguments=arguments)
        system_prompt = (
            system_override.replace("$ARGUMENTS", arguments) if system_override is not None
            else self._build_system_prompt(skill)
        )
        case_cwd = self._make_sandbox_cwd()
        options = self._build_options(system_prompt, max_steps, case_cwd)

        # Fingerprint pre-existing bundled-claude siblings so the
        # post-cancellation cleanup doesn't kill them. (Concurrent runs
        # share the same Python parent process — without this, one case
        # timing out nukes its concurrent peers as 'my children'.)
        sibling_pids = _snapshot_bundled_claude_pids()

        try:
            state, completed, duration = anyio.run(
                self._drive,
                options,
                skill_path.parent.name if skill_path.suffix == ".md" else skill_path.name,
            )
        finally:
            # Per-case tempdir is intentionally scratch — outputs we care about
            # are captured via the final-text channel.
            shutil.rmtree(case_cwd, ignore_errors=True)

        if not completed:
            # Wall-clock cancellation. aclosing should have terminated the
            # subprocess via the SDK's aclose chain; the sweep is backup.
            _kill_bundled_claude_children(exclude=sibling_pids)
            return _state_to_result(
                state,
                duration_s=duration,
                error_override=f"wall-clock timeout after {self.config.case_wall_clock_timeout_s}s",
            )

        result = _state_to_result(state, duration_s=duration)
        # Surface max_steps-budget violations as the dedicated exception so
        # behavior cases can grab the partial result.
        if result.error and "max_turns" in result.error.lower():
            raise MaxStepsExceeded(result.error, result=result)
        return result

    # ----------------------------------------------------------- helpers

    def _make_sandbox_cwd(self) -> Path:
        """Create a per-case tempdir under workspace/behavior-tests/sandboxes/."""
        sandbox_root = Path(
            os.environ.get(
                "BEHAVIOR_TESTS_SANDBOX_ROOT",
                str(_REPO_ROOT / "workspace" / "behavior-tests" / "sandboxes"),
            )
        )
        sandbox_root.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="behavior-test-", dir=sandbox_root))

    def _build_options(
        self,
        system_prompt: str,
        max_steps: Optional[int],
        case_cwd: Path,
    ) -> ClaudeAgentOptions:
        """Assemble ClaudeAgentOptions including all defense layers (turns,
        sandbox, sub-agent bound, dollar cap)."""
        ceiling = self.config.max_turns_ceiling
        effective_max = min(max_steps, ceiling) if max_steps is not None else ceiling

        # Bound sub-agents the parent might spawn via the Agent tool. Without
        # this, sub-agents inherit the SDK's defaults (max_turns=None,
        # unbounded). Override only the bounds we care about — turn count
        # and recursive-Agent ban — and leave tools/prompt minimal so the
        # SDK's general-purpose default fills in everything else.
        sub_agent = AgentDefinition(
            description="General-purpose sub-agent (turn-bounded for behavior tests).",
            prompt="Complete the task the parent agent delegated to you.",
            disallowedTools=["Agent", "Task"],
            maxTurns=ceiling,
        )

        kwargs: dict[str, Any] = {
            "system_prompt": system_prompt,
            "permission_mode": "default",
            "allowed_tools": list(self.config.allowed_tools),
            "cwd": str(case_cwd),
            "add_dirs": [str(_REPO_ROOT)],
            "sandbox": _build_sandbox_settings(self.config.allowed_network_domains),
            "max_buffer_size": self.config.max_buffer_size,
            "max_turns": effective_max,
            "agents": {"general-purpose": sub_agent},
        }
        if self.config.max_budget_usd is not None:
            kwargs["max_budget_usd"] = self.config.max_budget_usd
        if self.config.runner_model:
            kwargs["model"] = self.config.runner_model
        return ClaudeAgentOptions(**kwargs)

    async def _drive(self, options: ClaudeAgentOptions, skill_under_test: Optional[str] = None) -> tuple[_DriveState, bool, float]:
        """Run the agent loop. Returns (state, completed, duration_s).

        completed=False means we exited via wall-clock timeout; partial
        state is preserved in `state` so the caller can build a useful
        RunResult instead of returning empty fields.
        """
        state = _DriveState(skill_under_test=skill_under_test)
        timeout = self.config.case_wall_clock_timeout_s
        start = time.monotonic()
        completed = True

        # `move_on_after` doesn't raise — it just exits the block on timeout.
        # `aclosing` ensures the SDK's aclose() runs on every exit path,
        # which terminates the bundled-claude subprocess. Without aclosing
        # the iterator may not get cleaned up on cancellation (PEP 533).
        with anyio.move_on_after(timeout) as scope:
            try:
                async with aclosing(self._query_fn(prompt="Begin.", options=options)) as stream:
                    async for msg in stream:
                        _consume_message(msg, state)
            except Exception as e:  # noqa: BLE001
                state.error = f"{type(e).__name__}: {e}"

        if scope.cancelled_caught:
            completed = False
        return state, completed, time.monotonic() - start

    def _build_system_prompt(self, skill) -> str:
        # The agent's cwd is a sandbox tempdir (write isolation). The skill's
        # SKILL.md typically uses relative paths like `templates/foo.md` that
        # only resolve when cwd is the skill directory. Tell the agent
        # explicitly where to find skill-internal files; the repo is in
        # `add_dirs` so reads from `skills/<name>/...` succeed.
        try:
            skill_dir = skill.path.parent.relative_to(_REPO_ROOT)
        except ValueError:
            # Skill outside repo (test fixture); fall back to dir as-is.
            skill_dir = skill.path.parent
        home_hint = (
            f"Your skill home is at `{skill_dir}/` (repo-rooted). When the "
            f"skill body below references relative paths like "
            f"`templates/foo.md` or `references/bar.md`, resolve them under "
            f"your skill home — e.g. `{skill_dir}/templates/foo.md`. Your "
            f"working directory is a sandbox tempdir for safe writes; the "
            f"repository root is on the read path so any `{skill_dir}/...` "
            f"file is reachable.\n\n---\n\n"
        )
        return _TEST_MODE_PREAMBLE + home_hint + skill.body
