#!/usr/bin/env python3
"""Detect header/footer markers and report skip rows.

Usage:
    python plugins/casper/skills/source-aligned/scripts/header_footer_markers.py /path/to/file
    python plugins/casper/skills/source-aligned/scripts/header_footer_markers.py /path/to/file \
        --start-marker START-OF-DATA --end-marker END-OF-DATA

If no markers are provided (or none are found), skip counts are 0.
"""
from __future__ import annotations

import argparse
import gzip
from pathlib import Path


def _open_text(file_path: Path):
    if file_path.suffix == ".gz":
        return gzip.open(file_path, "rt", encoding="utf-8", errors="ignore")
    return file_path.open("rt", encoding="utf-8", errors="ignore")


def detect_header_footer(
    file_path: Path,
    start_markers: list[str] | None,
    end_markers: list[str] | None,
) -> tuple[int | None, int | None, int]:
    start_of_data = None
    end_of_data = None
    total_lines = 0
    with _open_text(file_path) as f:
        for idx, line in enumerate(f, 1):
            stripped = line.strip()
            if start_markers and stripped in start_markers:
                start_of_data = idx
            if end_markers and stripped in end_markers:
                end_of_data = idx
            total_lines = idx
    return start_of_data, end_of_data, total_lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)
    parser.add_argument("--start-marker", action="append", default=None)
    parser.add_argument("--end-marker", action="append", default=None)
    args = parser.parse_args()

    start_of_data, end_of_data, total_lines = detect_header_footer(
        args.file_path, args.start_marker, args.end_marker
    )
    skip_header_rows = start_of_data if start_of_data else 0
    skip_footer_rows = (
        (total_lines - end_of_data) if end_of_data and total_lines > end_of_data else 0
    )

    print(f"START-OF-DATA line: {start_of_data}")
    print(f"END-OF-DATA line: {end_of_data}")
    print(f"total lines: {total_lines}")
    print(f"skip_header_rows: {skip_header_rows}")
    print(f"skip_footer_rows: {skip_footer_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
