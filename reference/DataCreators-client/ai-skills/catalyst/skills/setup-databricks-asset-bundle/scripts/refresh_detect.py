#!/usr/bin/env python3
"""Refresh-mode hand-edit detector for setup-databricks-asset-bundle.

The skill emits files with a ``# Catalyst-version: N`` header (within the
first 5 lines). To decide whether an on-disk file is safe to regenerate, the
skill records a SHA-256 baseline (computed with the header line stripped) at
``.catalyst/baselines/<relative-path>.sha256``. This script performs the
hash check and emits a JSON verdict on stdout.

Contract:

* Bootstrap mode (``--bootstrap``): write the baseline from the current
  on-disk file and report ``bootstrapped``.
* Normal mode: compare on-disk hash to the recorded baseline and to the
  expected (template-rendered) hash supplied by the caller. Verdict is one
  of ``safe-to-regenerate``, ``skip-hand-edited``, ``bootstrapped``, or
  ``missing``.

Exit code is ``0`` for every verdict; non-zero only for hard errors (file
missing when expected, unreadable baseline, etc.). On hard errors the JSON
is written to stderr instead of stdout.

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Intentionally integer-only: Catalyst-version values are whole-number template
# epochs (for example `1`, `2`), not semver strings.
HEADER_RE = re.compile(r"^#\s*Catalyst-version:\s*(\d+)(?:\s|$)")
HEADER_SEARCH_LINES = 5


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_header_version(text: str) -> Optional[int]:
    """Return the Catalyst-version integer if found within the first
    ``HEADER_SEARCH_LINES`` lines, else None."""
    for line in text.splitlines()[:HEADER_SEARCH_LINES]:
        m = HEADER_RE.match(line)
        if m:
            return int(m.group(1))
    return None


def strip_header(text: str) -> str:
    """Return ``text`` with the first ``# Catalyst-version: N`` line
    removed (search within the first ``HEADER_SEARCH_LINES`` lines).

    Preserves the trailing newline behavior of the original text so the
    resulting hash is stable.
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines[:HEADER_SEARCH_LINES]):
        # match against the line without its trailing newline
        bare = line.rstrip("\n").rstrip("\r")
        if HEADER_RE.match(bare):
            del lines[i]
            break
    return "".join(lines)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_diff_lines(a: str, b: str) -> int:
    """Cheap line-difference count for the diff_summary string. Not a
    semantic diff — just ``len(symmetric difference)`` over lines, which is
    good enough for a one-liner."""
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    # use a multiset-style count of mismatched positions plus length delta
    pairs = zip(a_lines, b_lines)
    differing = sum(1 for x, y in pairs if x != y)
    differing += abs(len(a_lines) - len(b_lines))
    return differing


def baseline_path_for(repo_root: Path, rel_file: str) -> Path:
    return repo_root / ".catalyst" / "baselines" / (rel_file + ".sha256")


def write_json(obj: dict, stream=None) -> None:
    # Resolve sys.stdout lazily so unittest's redirect_stdout works.
    if stream is None:
        stream = sys.stdout
    json.dump(obj, stream, indent=2, sort_keys=True)
    stream.write("\n")


def hard_error(msg: str, file_arg: str, baseline_rel: str) -> int:
    payload = {
        "file": file_arg,
        "verdict": "error",
        "reason": msg,
        "header_version": None,
        "expected_version": None,
        "on_disk_hash": None,
        "expected_hash": None,
        "baseline_path": baseline_rel,
        "diff_summary": None,
    }
    # Resolve sys.stderr lazily so unittest's redirect_stderr works.
    write_json(payload, stream=sys.stderr)
    return 2


def run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    rel_file = args.file
    on_disk_path = repo_root / rel_file
    baseline_path = baseline_path_for(repo_root, rel_file)
    baseline_rel = str(baseline_path.relative_to(repo_root))

    if not on_disk_path.exists():
        return hard_error(
            f"on-disk file not found: {on_disk_path}",
            rel_file,
            baseline_rel,
        )

    try:
        on_disk_text = _read_text(on_disk_path)
    except OSError as exc:
        return hard_error(
            f"could not read on-disk file: {exc}", rel_file, baseline_rel
        )

    header_version = find_header_version(on_disk_text)
    stripped = strip_header(on_disk_text)
    on_disk_hash = sha256_hex(stripped)

    payload = {
        "file": rel_file,
        "verdict": None,
        "reason": None,
        "header_version": header_version,
        "expected_version": args.template_version,
        "on_disk_hash": on_disk_hash,
        "expected_hash": args.template_hash,
        "baseline_path": baseline_rel,
        "diff_summary": None,
    }

    if args.bootstrap:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(on_disk_hash + "\n", encoding="utf-8")
        payload["verdict"] = "bootstrapped"
        payload["reason"] = "wrote baseline from current on-disk file"
        write_json(payload)
        return 0

    if not baseline_path.exists():
        payload["verdict"] = "missing"
        payload["reason"] = "no baseline; run with --bootstrap first"
        write_json(payload)
        return 0

    # Normal mode — we need template-version + template-hash from caller.
    if args.template_version is None or args.template_hash is None:
        return hard_error(
            "normal mode requires --template-version and --template-hash",
            rel_file,
            baseline_rel,
        )

    try:
        baseline_hash = _read_text(baseline_path).strip()
    except OSError as exc:
        return hard_error(
            f"could not read baseline: {exc}", rel_file, baseline_rel
        )

    if not baseline_hash:
        return hard_error(
            f"baseline file is empty: {baseline_path}",
            rel_file,
            baseline_rel,
        )

    if header_version != args.template_version:
        payload["verdict"] = "skip-hand-edited"
        payload["reason"] = "template version drifted from baseline"
        payload["diff_summary"] = (
            f"header version {header_version} != expected "
            f"{args.template_version}"
        )
        write_json(payload)
        return 0

    if on_disk_hash != baseline_hash:
        # Hand-edited. Diff line count for the summary.
        # We don't have the original baseline content, only its hash —
        # so the summary describes the situation rather than a true diff.
        payload["verdict"] = "skip-hand-edited"
        payload["reason"] = "on-disk file differs from baseline (hand-edited)"
        payload["diff_summary"] = (
            "on-disk content hash differs from emitted baseline"
        )
        write_json(payload)
        return 0

    if on_disk_hash == args.template_hash:
        payload["verdict"] = "safe-to-regenerate"
        payload["reason"] = "matches baseline; no template change"
        write_json(payload)
        return 0

    # On-disk matches baseline (no hand-edit) but doesn't match the new
    # template hash → template legitimately changed, safe to regenerate.
    payload["verdict"] = "safe-to-regenerate"
    payload["reason"] = "matches baseline; template changed — regenerating"
    write_json(payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="refresh_detect.py",
        description=(
            "Detect whether a Catalyst-emitted file has been hand-edited "
            "since the baseline was recorded."
        ),
    )
    p.add_argument(
        "--repo-root",
        required=True,
        help="Root of the product repo (where .catalyst/baselines/ lives).",
    )
    p.add_argument(
        "--file",
        required=True,
        help="Path of the emitted file, relative to --repo-root.",
    )
    p.add_argument(
        "--template-version",
        type=int,
        default=None,
        help="Expected Catalyst-version header value for this template.",
    )
    p.add_argument(
        "--template-hash",
        default=None,
        help=(
            "Expected SHA-256 (hex) of the current template rendered with "
            "the file's recorded inputs, header stripped."
        ),
    )
    p.add_argument(
        "--bootstrap",
        action="store_true",
        help=(
            "Write the baseline from the current on-disk file and skip "
            "diff comparison this run."
        ),
    )
    return p


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
