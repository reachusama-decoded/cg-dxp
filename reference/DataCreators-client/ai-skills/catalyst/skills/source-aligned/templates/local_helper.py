#!/usr/bin/env python3
"""Workspace-local helper for non-flat-CSV source formats.

Scaffold copied from skills/source-aligned/templates/local_helper.py by
the source-aligned skill when the profile step detects a format the
standard ingestion path can't handle (e.g. Bloomberg .out.gz with
marker framing, request-response prefix columns, multi-block headers).

This is YOUR code now — product-specific, lives next to the data
product. Iterate locally. Promote to a first-class skill adapter only
when the same shape recurs across multiple products (see
references/local_helpers.md for the graduation criteria).

Pattern (concrete examples in references/local_helpers.md):
  1. detect_shape: read first/last N lines; locate START-/END- markers,
     metadata blocks, request-response prefix columns
  2. parse_file:  open the raw file, skip non-data rows, yield records
     as a normalized pandas DataFrame
  3. write_output: emit a flat CSV the standard ingestion pipeline can
     consume (or attach the DataFrame to a Spark load directly)
  4. wiring:      point ingestion.yml's l2r.file_pattern at the helper's
     output, not the raw file

Replace every TODO before running. Drop helpers you don't need.
"""
from __future__ import annotations

import argparse
import gzip
from pathlib import Path
from typing import Iterator

import pandas as pd


# ---------------------------------------------------------------------------
# 1. Detect shape — confirm the file looks like what you expect.
# ---------------------------------------------------------------------------
def detect_shape(path: Path, *, scan_lines: int = 200) -> dict:
    """Return a shape descriptor: markers found, header/footer offsets,
    declared field list, prefix columns."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        head = [next(f, "") for _ in range(scan_lines)]
    # TODO: find your start/end markers, FIELDS block, prefix columns.
    return {
        "start_of_data_line": None,   # TODO: line index of START-OF-DATA marker
        "end_of_data_line": None,     # TODO: line index of END-OF-DATA marker
        "fields": [],                 # TODO: column names parsed from header
        "prefix_columns": [],         # TODO: request-response prefix cols
    }


# ---------------------------------------------------------------------------
# 2. Parse — yield normalized rows into a DataFrame.
# ---------------------------------------------------------------------------
def parse_records(path: Path, shape: dict) -> Iterator[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    in_data = False
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not in_data:
                # TODO: flip in_data = True once you see your start marker
                continue
            # TODO: break on end marker; skip comment lines (#...) and blanks
            # TODO: split on your delimiter; map to dict using shape["fields"]
            yield {}


def to_dataframe(path: Path) -> pd.DataFrame:
    shape = detect_shape(path)
    df = pd.DataFrame(list(parse_records(path, shape)))
    # TODO: cast known numeric/date columns; drop or assert on prefix cols
    return df


# ---------------------------------------------------------------------------
# 3. Write a flat CSV the standard ingestion pipeline can consume.
# ---------------------------------------------------------------------------
def write_flat_csv(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path,
                        help="Flat CSV the standard ingestion pipeline will pick up")
    args = parser.parse_args()
    df = to_dataframe(args.input)
    write_flat_csv(df, args.output)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
