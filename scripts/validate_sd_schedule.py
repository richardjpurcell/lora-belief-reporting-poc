#!/usr/bin/env python3
"""
Validate an all-slot microSD replay schedule CSV.

This validator is intentionally narrow. It checks the SD-facing schedule format
used by the transmitter firmware:

    seq,region,event,priority,usefulness,stale_after,policy,send

It is meant to prevent accidentally copying a SEND-only compact CSV to an SD
card as /schedule.csv.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_HEADER = [
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
    "send",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an all-slot microSD replay schedule CSV."
    )
    parser.add_argument(
        "--infile",
        required=True,
        type=Path,
        help="SD-facing schedule CSV to validate.",
    )
    parser.add_argument(
        "--expected-rows",
        type=int,
        default=None,
        help="Optional expected total row count.",
    )
    parser.add_argument(
        "--expected-send-rows",
        type=int,
        default=None,
        help="Optional expected SEND row count.",
    )
    parser.add_argument(
        "--expected-skip-rows",
        type=int,
        default=None,
        help="Optional expected SKIP row count.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    args = parse_args()

    if not args.infile.exists():
        fail(f"input file does not exist: {args.infile}")

    with args.infile.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames != EXPECTED_HEADER:
            fail(
                "unexpected header.\n"
                f"Expected: {','.join(EXPECTED_HEADER)}\n"
                f"Found:    {','.join(reader.fieldnames or [])}"
            )

        rows = list(reader)

    if not rows:
        fail("schedule has no data rows")

    seq_values: list[int] = []
    send_rows = 0
    skip_rows = 0

    for line_number, row in enumerate(rows, start=2):
        try:
            seq = int(row["seq"])
        except ValueError:
            fail(f"line {line_number}: seq is not an integer: {row['seq']!r}")

        seq_values.append(seq)

        if len(row["region"]) != 1:
            fail(f"line {line_number}: region must be a single character")

        try:
            int(row["event"])
        except ValueError:
            fail(f"line {line_number}: event is not an integer: {row['event']!r}")

        try:
            float(row["priority"])
        except ValueError:
            fail(f"line {line_number}: priority is not numeric: {row['priority']!r}")

        try:
            float(row["usefulness"])
        except ValueError:
            fail(f"line {line_number}: usefulness is not numeric: {row['usefulness']!r}")

        try:
            int(row["stale_after"])
        except ValueError:
            fail(
                f"line {line_number}: stale_after is not an integer: "
                f"{row['stale_after']!r}"
            )

        if len(row["policy"]) != 1:
            fail(f"line {line_number}: policy must be a single character")

        if row["send"] == "1":
            send_rows += 1
        elif row["send"] == "0":
            skip_rows += 1
        else:
            fail(f"line {line_number}: send must be 0 or 1, got {row['send']!r}")

    expected_seq = list(range(len(rows)))
    if seq_values != expected_seq:
        fail(
            "seq column is not contiguous from 0.\n"
            f"Expected: {expected_seq}\n"
            f"Found:    {seq_values}"
        )

    if args.expected_rows is not None and len(rows) != args.expected_rows:
        fail(f"expected {args.expected_rows} rows, found {len(rows)}")

    if args.expected_send_rows is not None and send_rows != args.expected_send_rows:
        fail(f"expected {args.expected_send_rows} SEND rows, found {send_rows}")

    if args.expected_skip_rows is not None and skip_rows != args.expected_skip_rows:
        fail(f"expected {args.expected_skip_rows} SKIP rows, found {skip_rows}")

    print(f"SD schedule validation PASSED: {args.infile}")
    print(f"Rows:      {len(rows)}")
    print(f"SEND rows: {send_rows}")
    print(f"SKIP rows: {skip_rows}")


if __name__ == "__main__":
    main()