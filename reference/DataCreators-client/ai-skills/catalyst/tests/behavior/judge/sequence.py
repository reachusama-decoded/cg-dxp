from __future__ import annotations


class SequenceFailure(AssertionError):
    """Raised when an actual sub-skill sequence fails to match the expected one."""


def normalize_skill(name: str) -> str:
    """Normalize a sub-skill identifier for comparison.

    Case YAMLs use `skills/<name>` to match the on-disk path, but Claude Code's
    Skill tool invokes by bare name (e.g. `dplc-design-stage`). Strip the
    `skills/` prefix and any trailing slash so both forms compare equal.
    """
    n = name.strip()
    if n.startswith("skills/"):
        n = n[len("skills/"):]
    return n.rstrip("/").lower()


# Internal alias retained for the existing call sites in this module.
_normalize = normalize_skill


def _self_invocation_suffix(self_invocations: int) -> str:
    """Append a diagnostic phrase when the orchestrator called itself.

    AICAT-127 / AICAT-74 anti-pattern: orchestrator's SKILL.md describes
    its slash command in a way that prompts the model to call
    `Skill({skill: <itself>})` first. The harness already excludes that
    from `sub_skills` (it isn't routing anywhere), but the resulting
    failure message ("missing expected sub-skills: [...]") doesn't tell
    the user *why* sub-skills are missing. This suffix names the cause.
    """
    if self_invocations <= 0:
        return ""
    times = "time" if self_invocations == 1 else "times"
    return (
        f"; orchestrator self-invoked via Skill tool {self_invocations} {times} — "
        f"likely cause (see AICAT-127 / AICAT-74)"
    )


def assert_sub_skill_sequence(
    actual: list[str],
    expected: list[str],
    *,
    strict_order: bool,
    allow_extra: bool,
    self_invocations: int = 0,
) -> None:
    actual_n = [_normalize(s) for s in actual]
    expected_n = [_normalize(s) for s in expected]
    suffix = _self_invocation_suffix(self_invocations)

    if not allow_extra:
        unexpected = [s for s in actual_n if s not in expected_n]
        if unexpected:
            raise SequenceFailure(f"unexpected sub-skills present: {unexpected}{suffix}")

    if strict_order:
        i = 0
        for skill in actual_n:
            if i < len(expected_n) and skill == expected_n[i]:
                i += 1
        if i < len(expected_n):
            missing = expected_n[i:]
            present_but_misordered = [s for s in missing if s in actual_n]
            if present_but_misordered:
                raise SequenceFailure(
                    f"sub-skill order mismatch: expected {expected_n}, got {actual_n}{suffix}"
                )
            raise SequenceFailure(f"missing expected sub-skills: {missing}{suffix}")
    else:
        missing = [s for s in expected_n if s not in actual_n]
        if missing:
            raise SequenceFailure(f"missing expected sub-skills: {missing}{suffix}")
