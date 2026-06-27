#!/usr/bin/env python3
"""
Convert a generic belief-maintenance demand trace into compact firmware trace CSVs.

This script is intentionally independent of AWSRT and independent of firmware.
It provides a small adapter layer:

    generic demand-trace CSV
    -> compact firmware trace CSV
    -> scripts/make_trace_headers.py
    -> Arduino trace headers

The compact firmware trace CSV schema is:

    seq,region,event,priority,usefulness,stale_after,policy

The generic adapter input schema is:

    source_id,source_time,demand_index,region_id,event_type,priority,usefulness,
    stale_after,policy_hint,source_policy,source_note
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
            "Adapt a generic belief-maintenance demand trace into compact "
            "firmware trace CSVs."
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
        help=(
            "Output prefix. The script writes compact CSVs and a manifest "
            "using this prefix."
        ),
    )
    parser.add_argument(
        "--run-id",
        default="R20",
        help="Run identifier recorded in the manifest.",
    )
    parser.add_argument(
        "--txa-policy",
        default="fixed_all",
        choices=["fixed_all", "usefulness_threshold"],
        help="Policy used to produce the TX-A compact trace.",
    )
    parser.add_argument(
        "--txb-policy",
        default="usefulness_threshold",
        choices=["fixed_all", "usefulness_threshold"],
        help="Policy used to produce the TX-B compact trace.",
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

    # The compact firmware trace format only supports one-character regions.
    # For this first adapter milestone, keep the rule explicit and conservative.
    if len(cleaned) != 1:
        raise ValueError(
            f"Row {row_number}: region_id must already be one character for "
            f"compact output; got {region_id!r}"
        )
    return cleaned


def select_rows(
    rows: Iterable[GenericDemandRow],
    policy: str,
    threshold: float,
) -> list[GenericDemandRow]:
    if policy == "fixed_all":
        return list(rows)
    if policy == "usefulness_threshold":
        return [row for row in rows if row.usefulness >= threshold]
    raise ValueError(f"Unsupported policy: {policy}")


def to_compact_rows(
    rows: Iterable[GenericDemandRow],
    policy_code: str,
) -> list[CompactTraceRow]:
    compact_rows: list[CompactTraceRow] = []

    for seq, row in enumerate(rows):
        # Add 2 to approximate CSV line number after header for diagnostics.
        row_number = seq + 2
        compact_rows.append(
            CompactTraceRow(
                seq=seq,
                region=compact_region(row.region_id, row_number),
                event=row.event_type,
                priority=row.priority,
                usefulness=row.usefulness,
                stale_after=row.stale_after,
                policy=policy_code,
            )
        )

    return compact_rows


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


def write_manifest(
    outfile: Path,
    *,
    run_id: str,
    infile: Path,
    txa_file: Path,
    txb_file: Path,
    txa_policy: str,
    txb_policy: str,
    threshold: float,
    input_rows: int,
    txa_rows: int,
    txb_rows: int,
) -> None:
    manifest = {
        "run_id": run_id,
        "milestone": "v0.6-trace-adapter-design",
        "description": (
            "Generic belief-maintenance demand-trace adapter output. "
            "No firmware, timing, SD-card, or physical radio changes are implied."
        ),
        "input": {
            "path": str(infile),
            "schema": GENERIC_FIELDS,
            "rows": input_rows,
        },
        "outputs": {
            "txa": {
                "path": str(txa_file),
                "policy": txa_policy,
                "rows": txa_rows,
            },
            "txb": {
                "path": str(txb_file),
                "policy": txb_policy,
                "threshold": threshold,
                "rows": txb_rows,
            },
        },
        "compact_schema": COMPACT_FIELDS,
        "cautions": [
            "Adapter output is not a physical LoRa experiment.",
            "Adapter output does not demonstrate airtime reduction.",
            "Compact CSVs remain intended for the existing make_trace_headers.py path.",
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

    txa_selected = select_rows(rows, args.txa_policy, args.threshold)
    txb_selected = select_rows(rows, args.txb_policy, args.threshold)

    txa_compact = to_compact_rows(txa_selected, POLICY_CODES[args.txa_policy])
    txb_compact = to_compact_rows(txb_selected, POLICY_CODES[args.txb_policy])

    txa_file = args.out_prefix.parent / f"{args.out_prefix.name}_txa_{args.txa_policy}.csv"
    txb_file = args.out_prefix.parent / f"{args.out_prefix.name}_txb_{args.txb_policy}.csv"
    manifest_file = args.out_prefix.parent / f"{args.out_prefix.name}_manifest.json"

    write_compact_csv(txa_file, txa_compact)
    write_compact_csv(txb_file, txb_compact)
    write_manifest(
        manifest_file,
        run_id=args.run_id,
        infile=args.infile,
        txa_file=txa_file,
        txb_file=txb_file,
        txa_policy=args.txa_policy,
        txb_policy=args.txb_policy,
        threshold=args.threshold,
        input_rows=len(rows),
        txa_rows=len(txa_compact),
        txb_rows=len(txb_compact),
    )

    print(f"Read generic demand rows: {len(rows)}")
    print(f"Wrote TX-A compact trace: {txa_file} ({len(txa_compact)} rows)")
    print(f"Wrote TX-B compact trace: {txb_file} ({len(txb_compact)} rows)")
    print(f"Wrote adapter manifest:  {manifest_file}")


if __name__ == "__main__":
    main()