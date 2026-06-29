#!/usr/bin/env python3
"""
Create a firmware-facing microSD schedule CSV from a full analysis-facing
scheduled replay CSV.

The output preserves all schedule slots, including both SEND and SKIP rows.
This is different from the existing compact CSVs, which are SEND-only packet
streams used for earlier compiled-header workflows.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


OUTPUT_FIELDS = [
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
    "send",
]


def decision_to_send(value: str) -> str:
    normalized = value.strip().upper()

    if normalized == "SEND":
        return "1"
    if normalized == "SKIP":
        return "0"

    raise ValueError(f"Unsupported decision value: {value!r}")


def convert_schedule(infile: Path, outfile: Path) -> tuple[int, int, int]:
    total_rows = 0
    send_rows = 0
    skip_rows = 0

    with infile.open("r", newline="") as f_in, outfile.open("w", newline="") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        required = {
            "demand_index",
            "region_id",
            "event_type",
            "priority",
            "usefulness",
            "stale_after",
            "policy_code",
            "decision",
        }

        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Input schedule is missing required columns: {sorted(missing)}"
            )

        for row in reader:
            send = decision_to_send(row["decision"])

            if send == "1":
                send_rows += 1
            else:
                skip_rows += 1

            writer.writerow(
                {
                    "seq": row["demand_index"],
                    "region": row["region_id"],
                    "event": row["event_type"],
                    "priority": row["priority"],
                    "usefulness": row["usefulness"],
                    "stale_after": row["stale_after"],
                    "policy": row["policy_code"],
                    "send": send,
                }
            )

            total_rows += 1

    return total_rows, send_rows, skip_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a firmware-facing all-slots microSD replay CSV from a "
            "full schedule CSV."
        )
    )
    parser.add_argument("--infile", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    total_rows, send_rows, skip_rows = convert_schedule(args.infile, args.out)

    print(f"Wrote SD schedule CSV: {args.out}")
    print(f"Rows: {total_rows}")
    print(f"SEND rows: {send_rows}")
    print(f"SKIP rows: {skip_rows}")


if __name__ == "__main__":
    main()