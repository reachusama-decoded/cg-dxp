"""Print a one-line summary of the portfolio holdings in holdings.csv.

Standard library only (the csv module) so the image builds fast and needs no
network. This is the app you containerise — Docker is the lesson, not the code.
"""
from __future__ import annotations

import csv

CSV_PATH = "holdings.csv"


def main():
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))

    count = len(rows)
    total = sum(float(row["market_value"]) for row in rows)

    print("Portfolio summary")
    print(f"{count} holdings, total market value {total:,.2f}")


if __name__ == "__main__":
    main()