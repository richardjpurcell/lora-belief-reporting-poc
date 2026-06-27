#!/usr/bin/env python3
"""
Create reporting schedules and compact firmware trace CSVs from a generic demand trace.

This script adds an explicit reporting-decision layer:

    generic demand-trace CSV
    -> reporting schedule CSV with SEND/SKIP rows
    -> compact firmware trace CSV containing SEND rows only
    -> scripts/make_trace_headers.py

It is intentionally separate from scripts/adapt_demand_trace.py so the v0.6/v0.7
adapter path remains stable.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


GENERIC_FIELDS = [
    "source_id",
    "source_time",
    "demand_index",
    "region_id",
    "event_type",
    "priority",
    "usefulness",
    "stale_after",
    "policy_hint",
    "source_policy",
    "source_note",
]

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

COMPACT_FIELDS = [
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
]

POLICY_CODES = {
    "fixed_all": "F",
    "usefulness_threshold": "U",
}


@dataclass(frozen=True)
class GenericDemandRow:
    source_id: str
    source_time: str
    demand_index: int
    region_id: str
    event_type: int
    priority: float
    usefulness: float
    stale_after: int
    policy_hint: str
    source_policy: str
    source_note: str


@dataclass(frozen=True)
class ScheduleRow:
    source_id: str
    source_time: str
    demand_index: int
    region_id: str
    event_type: int
    priority: float
    usefulness: float
    stale_after: int
    policy_name: str
    policy_code: str
    decision: str
    decision_reason: str


@dataclass(frozen=True)
class CompactTraceRow:
    seq: int
    region: str
    event: int
    priority: float
    usefulness: float
    stale_after: int
    policy: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create reporting schedules and SEND-only compact firmware traces "
            "from a generic demand trace."
        )
    )
    parser.add_argument(
        "--infile",
        required=True,
        type=Path,
        help="Generic adapter input CSV.",
    )
    parser.add_argument(
        "--out-prefix",
        required=True,
        type=Path,
        help="Output prefix for schedules, compact traces, and manifest.",
    )
    parser.add_argument(
        "--run-id",
        default="R22",
        help="Run identifier recorded in the manifest.",
    )
    parser.add_argument(
        "--txa-policy",
        default="fixed_all",
        choices=["fixed_all", "usefulness_threshold"],
        help="Reporting policy for TX-A.",
    )
    parser.add_argument(
        "--txb-policy",
        default="usefulness_threshold",
        choices=["fixed_all", "usefulness_threshold"],
        help="Reporting policy for TX-B.",
    )
    parser.add_argument(
        "--threshold",
        default=0.50,
        type=float,
        help="Usefulness threshold for usefulness_threshold policy.",
    )
    return parser.parse_args()


def require_fields(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("Input CSV has no header row.")

    missing = [field for field in GENERIC_FIELDS if field not in fieldnames]
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


def read_generic_rows(infile: Path) -> list[GenericDemandRow]:
    rows: list[GenericDemandRow] = []

    with infile.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_fields(reader.fieldnames)

        for row_number, raw in enumerate(reader, start=2):
            demand_index = parse_int(raw["demand_index"], "demand_index", row_number)
            event_type = parse_int(raw["event_type"], "event_type", row_number)
            priority = parse_float(raw["priority"], "priority", row_number)
            usefulness = parse_float(raw["usefulness"], "usefulness", row_number)
            stale_after = parse_int(raw["stale_after"], "stale_after", row_number)

            if event_type not in (0, 1):
                raise ValueError(
                    f"Row {row_number}: event_type must be 0 or 1; got {event_type}"
                )
            validate_unit_interval(priority, "priority", row_number)
            validate_unit_interval(usefulness, "usefulness", row_number)
            if stale_after < 0:
                raise ValueError(
                    f"Row {row_number}: stale_after must be non-negative; "
                    f"got {stale_after}"
                )

            policy_hint = raw["policy_hint"].strip()
            if len(policy_hint) != 1:
                raise ValueError(
                    f"Row {row_number}: policy_hint must be one character; "
                    f"got {policy_hint!r}"
                )

            rows.append(
                GenericDemandRow(
                    source_id=raw["source_id"].strip(),
                    source_time=raw["source_time"].strip(),
                    demand_index=demand_index,
                    region_id=raw["region_id"].strip(),
                    event_type=event_type,
                    priority=priority,
                    usefulness=usefulness,
                    stale_after=stale_after,
                    policy_hint=policy_hint,
                    source_policy=raw["source_policy"].strip(),
                    source_note=raw["source_note"].strip(),
                )
            )

    if not rows:
        raise ValueError(f"Input CSV contains no data rows: {infile}")

    return rows


def compact_region(region_id: str, row_number: int) -> str:
    cleaned = region_id.strip()
    if not cleaned:
        raise ValueError(f"Row {row_number}: region_id must not be empty.")
    if len(cleaned) != 1:
        raise ValueError(
            f"Row {row_number}: region_id must already be one character for "
            f"compact output; got {region_id!r}"
        )
    return cleaned


def decision_for_row(
    row: GenericDemandRow,
    *,
    policy_name: str,
    threshold: float,
) -> tuple[str, str]:
    if policy_name == "fixed_all":
        return "SEND", "fixed_all sends every demand row"

    if policy_name == "usefulness_threshold":
        if row.usefulness >= threshold:
            return "SEND", f"usefulness {row.usefulness:.3f} >= threshold {threshold:.3f}"
        return "SKIP", f"usefulness {row.usefulness:.3f} < threshold {threshold:.3f}"

    raise ValueError(f"Unsupported policy: {policy_name}")


def make_schedule_rows(
    rows: Iterable[GenericDemandRow],
    *,
    policy_name: str,
    threshold: float,
) -> list[ScheduleRow]:
    policy_code = POLICY_CODES[policy_name]
    schedule_rows: list[ScheduleRow] = []

    for row in rows:
        decision, decision_reason = decision_for_row(
            row,
            policy_name=policy_name,
            threshold=threshold,
        )
        schedule_rows.append(
            ScheduleRow(
                source_id=row.source_id,
                source_time=row.source_time,
                demand_index=row.demand_index,
                region_id=row.region_id,
                event_type=row.event_type,
                priority=row.priority,
                usefulness=row.usefulness,
                stale_after=row.stale_after,
                policy_name=policy_name,
                policy_code=policy_code,
                decision=decision,
                decision_reason=decision_reason,
            )
        )

    return schedule_rows


def schedule_to_compact_rows(schedule_rows: Iterable[ScheduleRow]) -> list[CompactTraceRow]:
    compact_rows: list[CompactTraceRow] = []

    for row in schedule_rows:
        if row.decision != "SEND":
            continue

        row_number = len(compact_rows) + 2
        compact_rows.append(
            CompactTraceRow(
                seq=len(compact_rows),
                region=compact_region(row.region_id, row_number),
                event=row.event_type,
                priority=row.priority,
                usefulness=row.usefulness,
                stale_after=row.stale_after,
                policy=row.policy_code,
            )
        )

    return compact_rows


def write_schedule_csv(outfile: Path, rows: list[ScheduleRow]) -> None:
    outfile.parent.mkdir(parents=True, exist_ok=True)

    with outfile.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCHEDULE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "source_id": row.source_id,
                    "source_time": row.source_time,
                    "demand_index": row.demand_index,
                    "region_id": row.region_id,
                    "event_type": row.event_type,
                    "priority": f"{row.priority:.3f}",
                    "usefulness": f"{row.usefulness:.3f}",
                    "stale_after": row.stale_after,
                    "policy_name": row.policy_name,
                    "policy_code": row.policy_code,
                    "decision": row.decision,
                    "decision_reason": row.decision_reason,
                }
            )


def write_compact_csv(outfile: Path, rows: list[CompactTraceRow]) -> None:
    outfile.parent.mkdir(parents=True, exist_ok=True)

    with outfile.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPACT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "seq": row.seq,
                    "region": row.region,
                    "event": row.event,
                    "priority": f"{row.priority:.3f}",
                    "usefulness": f"{row.usefulness:.3f}",
                    "stale_after": row.stale_after,
                    "policy": row.policy,
                }
            )


def summarize_schedule(rows: list[ScheduleRow]) -> dict[str, int | float]:
    send_rows = [row for row in rows if row.decision == "SEND"]
    skip_rows = [row for row in rows if row.decision == "SKIP"]

    total_usefulness = sum(row.usefulness for row in send_rows)
    mean_usefulness = total_usefulness / len(send_rows) if send_rows else 0.0

    return {
        "demand_rows": len(rows),
        "send_rows": len(send_rows),
        "skip_rows": len(skip_rows),
        "send_fraction": len(send_rows) / len(rows) if rows else 0.0,
        "scheduled_total_usefulness": round(total_usefulness, 6),
        "scheduled_mean_usefulness": round(mean_usefulness, 6),
    }


def write_manifest(
    outfile: Path,
    *,
    run_id: str,
    infile: Path,
    txa_schedule_file: Path,
    txb_schedule_file: Path,
    txa_compact_file: Path,
    txb_compact_file: Path,
    txa_policy: str,
    txb_policy: str,
    threshold: float,
    input_rows: int,
    txa_summary: dict[str, int | float],
    txb_summary: dict[str, int | float],
) -> None:
    manifest = {
        "run_id": run_id,
        "milestone": "v0.8-reporting-schedule-design",
        "description": (
            "Reporting schedule with SEND/SKIP decisions. Compact firmware "
            "trace outputs contain SEND rows only. No firmware or physical "
            "radio changes are implied by this design-stage output."
        ),
        "input": {
            "path": str(infile),
            "schema": GENERIC_FIELDS,
            "rows": input_rows,
        },
        "outputs": {
            "txa": {
                "policy": txa_policy,
                "schedule_path": str(txa_schedule_file),
                "compact_trace_path": str(txa_compact_file),
                "summary": txa_summary,
            },
            "txb": {
                "policy": txb_policy,
                "threshold": threshold,
                "schedule_path": str(txb_schedule_file),
                "compact_trace_path": str(txb_compact_file),
                "summary": txb_summary,
            },
        },
        "schedule_schema": SCHEDULE_FIELDS,
        "compact_schema": COMPACT_FIELDS,
        "cautions": [
            "This is a reporting-schedule design artifact, not a physical LoRa run.",
            "Compact trace outputs contain SEND rows only.",
            "Airtime-saving claims require firmware scheduling/skipping and physical validation.",
        ],
    }

    outfile.parent.mkdir(parents=True, exist_ok=True)
    with outfile.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")


def main() -> None:
    args = parse_args()

    if not 0.0 <= args.threshold <= 1.0:
        raise ValueError(f"--threshold must be in [0, 1]; got {args.threshold}")

    rows = read_generic_rows(args.infile)

    txa_schedule = make_schedule_rows(
        rows,
        policy_name=args.txa_policy,
        threshold=args.threshold,
    )
    txb_schedule = make_schedule_rows(
        rows,
        policy_name=args.txb_policy,
        threshold=args.threshold,
    )

    txa_compact = schedule_to_compact_rows(txa_schedule)
    txb_compact = schedule_to_compact_rows(txb_schedule)

    base = args.out_prefix.parent
    name = args.out_prefix.name

    txa_schedule_file = base / f"{name}_txa_{args.txa_policy}_schedule.csv"
    txb_schedule_file = base / f"{name}_txb_{args.txb_policy}_schedule.csv"
    txa_compact_file = base / f"{name}_txa_{args.txa_policy}_compact.csv"
    txb_compact_file = base / f"{name}_txb_{args.txb_policy}_compact.csv"
    manifest_file = base / f"{name}_reporting_schedule_manifest.json"

    write_schedule_csv(txa_schedule_file, txa_schedule)
    write_schedule_csv(txb_schedule_file, txb_schedule)
    write_compact_csv(txa_compact_file, txa_compact)
    write_compact_csv(txb_compact_file, txb_compact)

    txa_summary = summarize_schedule(txa_schedule)
    txb_summary = summarize_schedule(txb_schedule)

    write_manifest(
        manifest_file,
        run_id=args.run_id,
        infile=args.infile,
        txa_schedule_file=txa_schedule_file,
        txb_schedule_file=txb_schedule_file,
        txa_compact_file=txa_compact_file,
        txb_compact_file=txb_compact_file,
        txa_policy=args.txa_policy,
        txb_policy=args.txb_policy,
        threshold=args.threshold,
        input_rows=len(rows),
        txa_summary=txa_summary,
        txb_summary=txb_summary,
    )

    print(f"Read generic demand rows: {len(rows)}")
    print(
        f"Wrote TX-A schedule: {txa_schedule_file} "
        f"({txa_summary['send_rows']} SEND, {txa_summary['skip_rows']} SKIP)"
    )
    print(
        f"Wrote TX-B schedule: {txb_schedule_file} "
        f"({txb_summary['send_rows']} SEND, {txb_summary['skip_rows']} SKIP)"
    )
    print(f"Wrote TX-A SEND-only compact trace: {txa_compact_file} ({len(txa_compact)} rows)")
    print(f"Wrote TX-B SEND-only compact trace: {txb_compact_file} ({len(txb_compact)} rows)")
    print(f"Wrote reporting schedule manifest: {manifest_file}")


if __name__ == "__main__":
    main()