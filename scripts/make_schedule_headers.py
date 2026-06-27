#!/usr/bin/env python3
"""
Generate Arduino schedule headers from SEND/SKIP reporting schedule CSVs.

This script is for skipped-slot firmware replay. Unlike make_trace_headers.py,
which emits compact trace rows for transmitted packets only, this script emits
a full schedule containing both SEND and SKIP rows.

Input schedule CSV schema:

    source_id,source_time,demand_index,region_id,event_type,priority,usefulness,
    stale_after,policy_name,policy_code,decision,decision_reason

Output Arduino header structure:

    struct ScheduleRow {
      uint16_t demand_index;
      char region;
      uint8_t event;
      float priority;
      float usefulness;
      uint16_t stale_after;
      char policy;
      uint8_t send;
    };

The firmware should advance one schedule row per slot. It should transmit only
when send == 1.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


SCHEDULE_FIELDS = [
    "source_id",
    "source_time",
    "demand_index",
    "region_id",
    "event_type",
    "priority",
    "usefulness",
    "stale_after",
    "policy_name",
    "policy_code",
    "decision",
    "decision_reason",
]


@dataclass(frozen=True)
class ScheduleRow:
    demand_index: int
    region: str
    event: int
    priority: float
    usefulness: float
    stale_after: int
    policy: str
    send: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Arduino SEND/SKIP schedule headers from schedule CSVs."
    )
    parser.add_argument(
        "--infile",
        required=True,
        type=Path,
        help="Reporting schedule CSV containing SEND and SKIP rows.",
    )
    parser.add_argument(
        "--outfile",
        required=True,
        type=Path,
        help="Arduino schedule header output path.",
    )
    parser.add_argument(
        "--guard",
        default=None,
        help=(
            "Optional C/C++ include guard. If omitted, one is derived from "
            "the output filename."
        ),
    )
    return parser.parse_args()


def require_fields(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("Input CSV has no header row.")

    missing = [field for field in SCHEDULE_FIELDS if field not in fieldnames]
    if missing:
        raise ValueError(f"Input CSV is missing required fields: {missing}")


def parse_int(value: str, field: str, row_number: int) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_number}: field '{field}' must be an integer; got {value!r}"
        ) from exc


def parse_float(value: str, field: str, row_number: int) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_number}: field '{field}' must be a float; got {value!r}"
        ) from exc


def validate_unit_interval(value: float, field: str, row_number: int) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"Row {row_number}: field '{field}' must be in [0, 1]; got {value}"
        )


def parse_schedule_row(raw: dict[str, str], row_number: int) -> ScheduleRow:
    demand_index = parse_int(raw["demand_index"], "demand_index", row_number)
    event = parse_int(raw["event_type"], "event_type", row_number)
    priority = parse_float(raw["priority"], "priority", row_number)
    usefulness = parse_float(raw["usefulness"], "usefulness", row_number)
    stale_after = parse_int(raw["stale_after"], "stale_after", row_number)

    region = raw["region_id"].strip()
    policy = raw["policy_code"].strip()
    decision = raw["decision"].strip().upper()

    if demand_index < 0:
        raise ValueError(
            f"Row {row_number}: demand_index must be non-negative; got {demand_index}"
        )
    if len(region) != 1:
        raise ValueError(
            f"Row {row_number}: region_id must be one character; got {region!r}"
        )
    if event not in (0, 1):
        raise ValueError(f"Row {row_number}: event_type must be 0 or 1; got {event}")
    validate_unit_interval(priority, "priority", row_number)
    validate_unit_interval(usefulness, "usefulness", row_number)
    if stale_after < 0:
        raise ValueError(
            f"Row {row_number}: stale_after must be non-negative; got {stale_after}"
        )
    if len(policy) != 1:
        raise ValueError(
            f"Row {row_number}: policy_code must be one character; got {policy!r}"
        )
    if decision not in ("SEND", "SKIP"):
        raise ValueError(
            f"Row {row_number}: decision must be SEND or SKIP; got {decision!r}"
        )

    return ScheduleRow(
        demand_index=demand_index,
        region=region,
        event=event,
        priority=priority,
        usefulness=usefulness,
        stale_after=stale_after,
        policy=policy,
        send=1 if decision == "SEND" else 0,
    )


def read_schedule_rows(infile: Path) -> list[ScheduleRow]:
    rows: list[ScheduleRow] = []

    with infile.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_fields(reader.fieldnames)

        for row_number, raw in enumerate(reader, start=2):
            rows.append(parse_schedule_row(raw, row_number))

    if not rows:
        raise ValueError(f"Input CSV contains no data rows: {infile}")

    return rows


def make_include_guard(outfile: Path, explicit_guard: str | None) -> str:
    if explicit_guard:
        return explicit_guard

    stem = outfile.name.upper()
    guard_chars = []
    for char in stem:
        if char.isalnum():
            guard_chars.append(char)
        else:
            guard_chars.append("_")
    guard = "".join(guard_chars)
    if not guard.endswith("_"):
        guard += "_"
    return guard


def write_header(outfile: Path, rows: list[ScheduleRow], guard: str, source: Path) -> None:
    outfile.parent.mkdir(parents=True, exist_ok=True)

    send_count = sum(row.send for row in rows)
    skip_count = len(rows) - send_count

    with outfile.open("w", encoding="utf-8") as handle:
        handle.write("// Auto-generated by scripts/make_schedule_headers.py\n")
        handle.write(f"// Source schedule: {source}\n")
        handle.write("// Do not edit by hand; edit the schedule CSV and regenerate.\n")
        handle.write("// Contains both SEND and SKIP rows for skipped-slot replay.\n\n")

        handle.write(f"#ifndef {guard}\n")
        handle.write(f"#define {guard}\n\n")
        handle.write("#include <stdint.h>\n\n")

        handle.write("struct ScheduleRow {\n")
        handle.write("  uint16_t demand_index;\n")
        handle.write("  char region;\n")
        handle.write("  uint8_t event;\n")
        handle.write("  float priority;\n")
        handle.write("  float usefulness;\n")
        handle.write("  uint16_t stale_after;\n")
        handle.write("  char policy;\n")
        handle.write("  uint8_t send;\n")
        handle.write("};\n\n")

        handle.write(f"static const uint16_t SCHEDULE_ROW_COUNT = {len(rows)};\n")
        handle.write(f"static const uint16_t SCHEDULE_SEND_COUNT = {send_count};\n")
        handle.write(f"static const uint16_t SCHEDULE_SKIP_COUNT = {skip_count};\n\n")

        handle.write("static const ScheduleRow SCHEDULE_ROWS[] = {\n")
        for row in rows:
            handle.write(
                "  "
                f"{{{row.demand_index}, "
                f"'{row.region}', "
                f"{row.event}, "
                f"{row.priority:.3f}f, "
                f"{row.usefulness:.3f}f, "
                f"{row.stale_after}, "
                f"'{row.policy}', "
                f"{row.send}}},\n"
            )
        handle.write("};\n\n")

        handle.write(f"#endif  // {guard}\n")


def main() -> None:
    args = parse_args()

    rows = read_schedule_rows(args.infile)
    guard = make_include_guard(args.outfile, args.guard)
    write_header(args.outfile, rows, guard, args.infile)

    send_count = sum(row.send for row in rows)
    skip_count = len(rows) - send_count

    print(f"Read schedule rows: {len(rows)}")
    print(f"SEND rows:          {send_count}")
    print(f"SKIP rows:          {skip_count}")
    print(f"Wrote header:       {args.outfile}")


if __name__ == "__main__":
    main()