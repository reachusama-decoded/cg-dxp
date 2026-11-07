#!/usr/bin/env python3
"""Find related ingestion configs and suggest dc_tag.

Searches caspian-pipelines ingestion YAMLs for similar process_name/domain or
file_pattern and reports matching configs + their file_tags.dc.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print("PyYAML is required to run this script.")
    raise


@dataclass
class Match:
    path: Path
    process_domain: Optional[str]
    process_name: Optional[str]
    file_pattern: Optional[str]
    dc_tag: Optional[str]
    score: int


def iter_yaml_files(root: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".yml") or name.endswith(".yaml"):
                yield Path(dirpath) / name


def load_yaml(path: Path) -> Optional[dict]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def score_match(
    cfg: dict,
    path: Path,
    process_domain: Optional[str],
    process_name: Optional[str],
    file_pattern: Optional[str],
) -> int:
    score = 0
    cfg_domain = str(cfg.get("process_domain") or "")
    cfg_name = str(cfg.get("process_name") or "")
    cfg_pattern = str(cfg.get("l2r", {}).get("file_pattern") or "")

    path_str = str(path).lower()

    if process_domain:
        if process_domain.lower() == cfg_domain.lower():
            score += 5
        if process_domain.lower() in cfg_name.lower():
            score += 2
        if process_domain.lower() in path_str:
            score += 1

    if process_name:
        if process_name.lower() == cfg_name.lower():
            score += 6
        if process_name.lower() in path_str:
            score += 2
        if process_name.lower() in cfg_pattern.lower():
            score += 2

    if file_pattern:
        if file_pattern.lower() == cfg_pattern.lower():
            score += 4
        if fnmatch.fnmatch(cfg_pattern.lower(), file_pattern.lower()):
            score += 2
        if fnmatch.fnmatch(file_pattern.lower(), cfg_pattern.lower()):
            score += 2

    return score


def collect_matches(
    root: Path,
    process_domain: Optional[str],
    process_name: Optional[str],
    file_pattern: Optional[str],
) -> List[Match]:
    matches: List[Match] = []
    for path in iter_yaml_files(root):
        cfg = load_yaml(path)
        if not cfg:
            continue
        score = score_match(cfg, path, process_domain, process_name, file_pattern)
        if score <= 0:
            continue
        dc_tag = cfg.get("file_tags", {}).get("dc")
        matches.append(
            Match(
                path=path,
                process_domain=cfg.get("process_domain"),
                process_name=cfg.get("process_name"),
                file_pattern=cfg.get("l2r", {}).get("file_pattern"),
                dc_tag=dc_tag,
                score=score,
            )
        )
    matches.sort(key=lambda m: (-m.score, str(m.path)))
    return matches


def format_match(m: Match) -> str:
    return (
        f"score={m.score} | dc_tag={m.dc_tag or 'UNKNOWN'} | "
        f"domain={m.process_domain or 'NA'} | name={m.process_name or 'NA'} | "
        f"pattern={m.file_pattern or 'NA'} | {m.path}"
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Find related ingestion configs and suggest dc_tag")
    parser.add_argument("--root", default="workspace/reference/repos/caspian-pipelines/dags/ingestion", help="Search root")
    parser.add_argument("--process-domain", help="Process domain to match")
    parser.add_argument("--process-name", help="Process name to match")
    parser.add_argument("--file-pattern", help="File pattern or filename to match")
    parser.add_argument("--top", type=int, default=10, help="Show top N matches")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.exists():
        print(f"Search root not found: {root}")
        return 2

    matches = collect_matches(root, args.process_domain, args.process_name, args.file_pattern)

    if not matches:
        print("No related ingestion configs found.")
        return 0

    print(f"Found {len(matches)} related configs. Top {min(args.top, len(matches))}:")
    for m in matches[: args.top]:
        print(format_match(m))

    best = matches[0]
    if best.dc_tag:
        print(f"
Suggested dc_tag: {best.dc_tag}")
    else:
        print("
Suggested dc_tag: UNKNOWN (no dc tag found in best match)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
