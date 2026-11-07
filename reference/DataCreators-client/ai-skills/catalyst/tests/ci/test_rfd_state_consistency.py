"""An RFD's declared state must match where its discussion actually is.

RFD 0001 defines the lifecycle:

    discussion  PR is open, actively soliciting feedback
    published   Merged to `main`, decision is recorded
    abandoned   Withdrawn by the author, kept for historical record

and the Publish step says "when discussion converges, set the state to
``published`` **and** merge the PR" — in that order. Nothing enforced the order,
so an RFD could land on ``main`` still claiming ``discussion`` while the PR it
names as the discussion venue was closed. The state then points at a conversation
that cannot be joined: the document reads as provisional forever, and a reader
has no way to tell "still being argued" from "merged and nobody updated the
header".

Two of fifteen RFDs were in exactly that state when this test was written —
0024 (fixed in the same commit) and 0019 (see the waiver below). This is the kind
of defect that is invisible on inspection: the frontmatter looks fine, the index
looks fine, and only cross-referencing every ``discussion:`` URL against the
GitHub API reveals it. So it gets a test rather than a sentence in CONTRIBUTING.

**Offline by construction.** The PR state is not fetched — that would make the
suite network-dependent and fail for anyone without a token, which is how a check
becomes something people skip. Instead the test uses the one fact available
locally and for free: presence **on the base ref**. An RFD whose directory already
exists on ``origin/main`` got there by a merge, so its discussion PR is closed.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
RFD_DIR = REPO_ROOT / "rfd"

# States that are coherent for a document that has already landed on `main`.
#
# `committed` is included because RFD 0001's Commit step transitions a *published*
# RFD to it once implemented ("At that point the document describes how the system
# works, not a proposal"). Omitting it, as the first revision did, would have failed
# the first RFD anyone marked implemented -- a document in its most-settled state
# rejected for not being settled.
#
# `abandoned` is included deliberately: a withdrawn RFD is kept for the historical
# record, so its presence here is intended and its discussion being closed is the
# whole point.
#
# `ideation` and `prediscussion` are absent because a draft-in-progress has no
# business on a base branch at all -- if one appears, that is worth failing on for
# a different reason than this test's headline.
LANDED_STATES = frozenset({"published", "committed", "abandoned"})

# Every state RFD 0001 defines, so an unrecognised value fails as a typo rather
# than being silently treated as non-landed.
VALID_STATES = frozenset(
    {"ideation", "prediscussion", "discussion", "published", "committed", "abandoned"}
)

# ---------------------------------------------------------------------------
# Waivers
# ---------------------------------------------------------------------------
# A waiver is a named exception with a reason and an owner, not a silent pass. If
# this dict is ever empty, delete it rather than leaving an empty hook.
#
# 0019 is NKV's. It merged inside a *skill* PR -- #415, "AICAT-281:
# data-quality-controls-plan skill (EDGC-aligned) + RFD 0019" -- rather than
# through its own convergence, so `discussion` may well be deliberate: the
# document rode along with a delivery while the argument continued. Whether it
# converged is the author's call, not this test's, and not the call of whoever
# happens to be fixing their own RFD in the same commit. Asked on #415.
WAIVED: dict[str, str] = {
    "0019": (
        "NKV's RFD, merged inside skill PR #415 rather than on its own "
        "convergence; whether it is converged is the author's call. Asked on "
        "#415. Remove this waiver when he answers."
    ),
}

# `0000` is the RFD template. It is a real directory with real frontmatter, so it
# is checked like any other, but it is deliberately absent from the index.
_INDEX_EXEMPT = frozenset({"0000"})

_STATE_RE = re.compile(r"^state:\s*(\S+)\s*$", re.MULTILINE)

# The leading `---` fenced block, and nothing else. Searching the whole document
# meant a `state:` line quoted in the body -- in a YAML example, say -- satisfied
# the guard while the real header was missing or misspelled. Demonstrated: renaming
# the header to `stateX:` and adding a fenced ```yaml state: published``` block to
# the body left all 44 assertions green, so the test passed against a README with
# no valid state at all.
_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\s*$", re.DOTALL | re.MULTILINE)


def _rfd_readmes() -> list[pathlib.Path]:
    """Every numbered RFD on disk, in order."""
    return sorted(
        p / "README.md"
        for p in RFD_DIR.iterdir()
        if p.is_dir() and re.fullmatch(r"\d{4}", p.name) and (p / "README.md").is_file()
    )


def _frontmatter_of(readme: pathlib.Path) -> str | None:
    """The leading `---` block only, or None when the file has no frontmatter."""
    match = _FRONTMATTER_RE.search(readme.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def _state_of(readme: pathlib.Path) -> str | None:
    """`state:` as declared in the frontmatter, never from the body."""
    frontmatter = _frontmatter_of(readme)
    if frontmatter is None:
        return None
    match = _STATE_RE.search(frontmatter)
    return match.group(1) if match else None


def _landed_on_base(readme: pathlib.Path) -> bool | None:
    """Does this RFD already exist on the base branch?

    The whole discriminator. `True` means it arrived by a merge, so its discussion
    PR is closed. `False` means this branch introduces it and `discussion` is the
    correct state. `None` means no base ref could be resolved, so the question
    cannot be answered offline and the caller must skip rather than guess.
    """
    if _BASE_REF is None:
        return None
    rel = readme.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{_BASE_REF}:{rel}"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def _resolve_base_ref() -> str | None:
    """First of `origin/main` / `main` that resolves, else None."""
    for ref in ("origin/main", "main"):
        ok = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        if ok.returncode == 0:
            return ref
    return None


_BASE_REF = _resolve_base_ref()


def test_there_are_rfds_to_check() -> None:
    """Without this the checks below are a no-op that reports as a pass.

    The same shape as the defect they exist to catch, and the same guard
    ``test_no_legacy_skill_references.py`` carries for the same reason.
    """
    found = _rfd_readmes()
    assert len(found) > 5, (
        f"only {len(found)} RFD README(s) discovered under {RFD_DIR} — the glob is "
        f"probably wrong, and every assertion below would vacuously pass"
    )


@pytest.mark.parametrize("readme", _rfd_readmes(), ids=lambda p: p.parent.name)
def test_state_is_a_state_rfd_0001_defines(readme: pathlib.Path) -> None:
    """A typo'd state is worse than a wrong one: it reads as intentional."""
    state = _state_of(readme)
    assert state is not None, (
        f"{readme.relative_to(REPO_ROOT)} has no `state:` in its frontmatter. "
        f"RFD 0001 requires one."
    )
    assert state in VALID_STATES, (
        f"{readme.relative_to(REPO_ROOT)} declares state {state!r}, which RFD 0001 "
        f"does not define. Valid: {', '.join(sorted(VALID_STATES))}"
    )


@pytest.mark.parametrize("readme", _rfd_readmes(), ids=lambda p: p.parent.name)
def test_a_landed_rfd_does_not_still_claim_discussion(readme: pathlib.Path) -> None:
    """Being on ``main`` means the discussion PR closed, so ``discussion`` is stale.

    This is the check that would have caught 0024. It needs no network call --
    ``git cat-file -e <base>:<path>`` answers it locally.

    Note what the evidence is **not**: presence in the working tree. That was the
    first revision's premise and it is false in any PR checkout, which is why
    ``_landed_on_base`` exists. Do not simplify it away.
    """
    number = readme.parent.name
    state = _state_of(readme)

    if number in WAIVED:
        pytest.skip(f"RFD {number} waived: {WAIVED[number]}")

    landed = _landed_on_base(readme)
    if landed is None:
        pytest.skip(
            "neither `origin/main` nor `main` resolves, so whether this RFD has "
            "landed cannot be determined offline"
        )
    if not landed:
        # Introduced by this branch. `discussion` is what RFD 0001 requires here,
        # so there is nothing to check until it merges.
        pytest.skip(
            f"RFD {number} is not on {_BASE_REF} — this branch adds it, so "
            f"`state: {state}` is correct for an open RFD PR"
        )

    assert state in LANDED_STATES, (
        f"RFD {number} exists on {_BASE_REF} but declares `state: {state}`.\n\n"
        f"RFD 0001's Publish step is 'set the state to published, *then* merge the "
        f"PR'. Once it is merged, the PR named in `discussion:` is closed, so "
        f"`{state}` points at a conversation nobody can join.\n\n"
        f"Fix: set `state: published` in {readme.relative_to(REPO_ROOT)} and update "
        f"the matching row in rfd/README.md. If the RFD genuinely has not converged, "
        f"it should not have merged — and if it merged for an unrelated reason (it "
        f"rode along with a skill PR, say), add it to WAIVED with a reason and an "
        f"owner rather than loosening this check.\n\n"
        f"Note `published` does not mean every question is settled: 0003 and 0018 "
        f"are published and carry open-questions sections. It means the decision is "
        f"recorded."
    )


@pytest.mark.parametrize("readme", _rfd_readmes(), ids=lambda p: p.parent.name)
def test_the_index_row_agrees_with_the_frontmatter(readme: pathlib.Path) -> None:
    """Two places record the state, so they can disagree — and did.

    ``rfd/README.md`` is hand-maintained, so fixing the frontmatter without the
    index leaves the table lying to the one audience that reads it first.
    """
    number = readme.parent.name
    state = _state_of(readme)

    index = (RFD_DIR / "README.md").read_text(encoding="utf-8")

    # Rows look like: | [24](0024/README.md) | Title | published |
    row = re.search(
        rf"^\|\s*\[{int(number)}\]\({number}/README\.md\)\s*\|(.*)\|\s*(\S+)\s*\|\s*$",
        index,
        re.MULTILINE,
    )

    # The row is looked up *before* any landed-ness gate, because only the
    # *existence* requirement depends on having landed -- the agreement check does
    # not. Gating the whole body, as the previous revision did, meant a new RFD that
    # ships a row whose state disagrees with its frontmatter was skipped outright:
    # 0024's original defect (two places recording the state, disagreeing) passing
    # at the one moment it is cheapest to fix, then landing on `main` to be caught
    # on somebody else's next PR.
    if row is None:
        # RFD 0001 says nothing about `rfd/README.md` -- its Discuss step is "open a
        # PR, set the state to `discussion`, add the PR URL", and no step mentions
        # the index -- so the conformant new-RFD PR is README-only and must not be
        # failed for it. An RFD that has *landed* must be indexed.
        landed = _landed_on_base(readme)
        if landed is None:
            # Distinct from "not landed", and kept distinct on purpose: collapsing
            # them into `landed is not True` renders the skip reason as "not on
            # None — this branch adds it", which asserts something unknown as a
            # fact and buries the real cause. Same shape as the `""`-sentinel
            # conflations this repo keeps finding.
            pytest.skip(
                "neither `origin/main` nor `main` resolves, so whether this RFD "
                "has landed cannot be determined offline"
            )
        if not landed:
            pytest.skip(
                f"RFD {number} is not on {_BASE_REF} — this branch adds it, and RFD "
                f"0001 does not require the index row yet"
            )
        # `0000` is the template, deliberately unlisted -- an index row for it would
        # advertise a placeholder as an RFD. Every other landed number must be
        # listed: the index is how anyone finds an RFD, so an omission makes the
        # document exist without being discoverable.
        assert number in _INDEX_EXEMPT, (
            f"RFD {number} has no row in rfd/README.md. The index is hand-maintained "
            f"and is how RFDs are found, so a missing row makes this one invisible. "
            f"Add: | [{int(number)}]({number}/README.md) | <title> | {state} |"
        )
        pytest.skip(f"RFD {number} is the template, deliberately not indexed")

    assert row.group(2) == state, (
        f"RFD {number}: frontmatter says `{state}` but rfd/README.md says "
        f"`{row.group(2)}`. Both are hand-maintained; update them together."
    )
