#!/usr/bin/env python3
"""
Prepare Run 030 three-transmitter SD replay schedules.

This is intentionally Run-030-specific. It avoids changing the existing
two-transmitter make_reporting_schedule.py path while producing explicit
TXA/TXB/TXC schedule artifacts for the first three-transmitter SD replay.

Design:

The SD-facing files remain all-slot CSVs with schema:

    seq,region,event,priority,usefulness,stale_after,policy,send

The firmware-facing policy field is a single-character code.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = [
    "priority",
    "usefulness",
    "stale_after",
]

SCHEDULE_COLUMNS = [
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
    "send",
]


INPUT = Path("traces/run029_reporting_txa_fixed_all_schedule.csv")
RUN030_BASE_SCHEDULE = Path("traces/run030_three_tx_base_schedule.csv")

MANIFEST = Path("traces/run030_reporting_reporting_schedule_manifest.json")

TXA_SCHEDULE = Path("traces/run030_reporting_txa_fixed_all_schedule.csv")
TXA_COMPACT = Path("traces/run030_reporting_txa_fixed_all_compact.csv")
TXA_SD = Path("traces/run030_sd_txa_schedule.csv")

TXB_SCHEDULE = Path("traces/run030_reporting_txb_medium_threshold_schedule.csv")
TXB_COMPACT = Path("traces/run030_reporting_txb_medium_threshold_compact.csv")
TXB_SD = Path("traces/run030_sd_txb_schedule.csv")

TXC_SCHEDULE = Path("traces/run030_reporting_txc_strict_threshold_schedule.csv")
TXC_COMPACT = Path("traces/run030_reporting_txc_strict_threshold_compact.csv")
TXC_SD = Path("traces/run030_sd_txc_schedule.csv")

def first_present(row: dict[str, str], candidates: list[str]) -> str | None:
    """Return the first non-empty value from a list of possible column names."""
    for name in candidates:
        if name in row and str(row[name]).strip() != "":
            return str(row[name]).strip()
    return None


def normalize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Normalize a Run 029 schedule-like CSV into the SD replay schema.

    Earlier schedule artifacts were not all written with the exact SD-facing
    schema. For Run 030, we normalize the source rows into:

        seq,region,event,priority,usefulness,stale_after,policy,send

    This keeps the Run 030 generator explicit without requiring a broader
    rewrite of the older schedule-generation scripts.
    """
    normalized: list[dict[str, str]] = []

    for idx, row in enumerate(rows):
        seq = first_present(
            row,
            [
                "seq",
                "sequence",
                "slot",
                "row",
                "t",
                "time",
                "time_step",
                "step",
            ],
        )
        region = first_present(
            row,
            [
                "region",
                "region_id",
                "cell",
                "cell_id",
                "node_region",
            ],
        )
        event = first_present(
            row,
            [
                "event",
                "event_type",
                "label",
                "state",
            ],
        )
        priority = first_present(row, ["priority", "prio"])
        usefulness_value = first_present(row, ["usefulness", "utility", "u"])
        stale_after = first_present(row, ["stale_after", "ttl", "expires_after"])

        if priority is None:
            raise ValueError(f"source row {idx} is missing priority/prio")
        if usefulness_value is None:
            raise ValueError(f"source row {idx} is missing usefulness/utility/u")
        if stale_after is None:
            raise ValueError(f"source row {idx} is missing stale_after/ttl/expires_after")

        normalized.append(
            {
                "seq": seq if seq is not None else str(idx),
                "region": region if region is not None else "R0",
                "event": event if event is not None else "A",
                "priority": priority,
                "usefulness": usefulness_value,
                "stale_after": stale_after,
                "policy": first_present(row, ["policy"]) or "source_schedule",
                "send": first_present(row, ["send"]) or "1",
            }
        )

    return normalized


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) != 64:
        raise ValueError(f"expected 64 rows in {path}, found {len(rows)}")

    rows = normalize_rows(rows)

    missing = [col for col in REQUIRED_COLUMNS if col not in rows[0]]
    if missing:
        raise ValueError(f"{path} could not be normalized; missing columns: {missing}")

    return rows


def usefulness(row: dict[str, str]) -> float:
    return float(row["usefulness"])


def seq_value(row: dict[str, str]) -> int:
    return int(row["seq"])


def top_n_seq_set(rows: list[dict[str, str]], n: int) -> set[str]:
    selected = sorted(rows, key=lambda r: (-usefulness(r), seq_value(r)))[:n]
    return {str(row["seq"]) for row in selected}


def build_schedule(
    rows: list[dict[str, str]],
    *,
    policy_code: str,
    send_seq_set: set[str] | None,
) -> list[dict[str, str]]:
    if len(policy_code) != 1:
        raise ValueError(f"policy_code must be a single character, got {policy_code!r}")

    schedule_rows: list[dict[str, str]] = []

    for row in rows:
        send = "1" if send_seq_set is None or str(row["seq"]) in send_seq_set else "0"
        schedule_rows.append(
            {
                "seq": row["seq"],
                "region": row["region"],
                "event": row["event"],
                "priority": row["priority"],
                "usefulness": row["usefulness"],
                "stale_after": row["stale_after"],
                "policy": policy_code,
                "send": send,
            }
        )

    return schedule_rows


def write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEDULE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_schedule_and_compact(
    schedule_path: Path,
    compact_path: Path,
    sd_path: Path,
    rows: list[dict[str, str]],
) -> tuple[int, int, int]:
    write_csv(schedule_path, rows)

    compact_rows = [row for row in rows if row["send"] == "1"]
    write_csv(compact_path, compact_rows)

    # SD-facing schedule is intentionally all-slot, not compact.
    write_csv(sd_path, rows)

    send_count = len(compact_rows)
    skip_count = len(rows) - send_count
    return len(rows), send_count, skip_count


def main() -> None:
    rows = read_rows(INPUT)

    RUN030_BASE_SCHEDULE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(INPUT, RUN030_BASE_SCHEDULE)

    txb_send = top_n_seq_set(rows, 32)
    txc_send = top_n_seq_set(rows, 16)

    txa_rows = build_schedule(rows, policy_code="F", send_seq_set=None)
    txb_rows = build_schedule(rows, policy_code="U", send_seq_set=txb_send)
    txc_rows = build_schedule(rows, policy_code="U", send_seq_set=txc_send)

    txa_counts = write_schedule_and_compact(TXA_SCHEDULE, TXA_COMPACT, TXA_SD, txa_rows)
    txb_counts = write_schedule_and_compact(TXB_SCHEDULE, TXB_COMPACT, TXB_SD, txb_rows)
    txc_counts = write_schedule_and_compact(TXC_SCHEDULE, TXC_COMPACT, TXC_SD, txc_rows)

    manifest = {
        "run_id": "run030_three_transmitter_sd_schedule_prep",
        "milestone": "v3.5-three-transmitter-sd-schedule-prep",
        "purpose": (
            "Prepare manifest-bound three-transmitter all-slot SD schedules "
            "for a later physical replay milestone."
        ),
        "source_schedule": str(INPUT),
        "run030_base_schedule_copy": str(RUN030_BASE_SCHEDULE),
        "schedule_period_rows": 64,
        "sd_schedule_schema": SCHEDULE_COLUMNS,
        "transmitters": [
            {
                "tx_id": "TXA",
                "node_id": "N01",
                "role": "fixed-all baseline",
                "policy": "fixed_all",
                "policy_code": "F",
                "threshold_family": None,
                "schedule_csv": str(TXA_SCHEDULE),
                "compact_csv": str(TXA_COMPACT),
                "sd_csv": str(TXA_SD),
                "expected_rows": txa_counts[0],
                "expected_send_rows": txa_counts[1],
                "expected_skip_rows": txa_counts[2],
            },
            {
                "tx_id": "TXB",
                "node_id": "N16",
                "role": "medium threshold scheduled skipping",
                "policy": "usefulness_threshold",
                "policy_code": "U",
                "threshold_family": "medium",
                "selection_rule": "top 32 rows by usefulness, sequence ascending for ties",
                "schedule_csv": str(TXB_SCHEDULE),
                "compact_csv": str(TXB_COMPACT),
                "sd_csv": str(TXB_SD),
                "expected_rows": txb_counts[0],
                "expected_send_rows": txb_counts[1],
                "expected_skip_rows": txb_counts[2],
            },
            {
                "tx_id": "TXC",
                "node_id": "N31",
                "role": "strict threshold scheduled skipping",
                "policy": "usefulness_threshold",
                "policy_code": "U",
                "threshold_family": "strict",
                "selection_rule": "top 16 rows by usefulness, sequence ascending for ties",
                "schedule_csv": str(TXC_SCHEDULE),
                "compact_csv": str(TXC_COMPACT),
                "sd_csv": str(TXC_SD),
                "expected_rows": txc_counts[0],
                "expected_send_rows": txc_counts[1],
                "expected_skip_rows": txc_counts[2],
            },
        ],
        "expected_scheduled_ratios": {
            "TXB/TXA": 32 / 64,
            "TXC/TXA": 16 / 64,
            "TXC/TXB": 16 / 32,
        },
        "sd_card_convention": (
            "Each transmitter SD-facing all-slot CSV should later be copied "
            "to that board's SD card as /schedule.csv. Compact SEND-only CSVs "
            "are not SD replay files."
        ),
        "interpretation_cautions": [
            "This is schedule preparation only, not a physical replay.",
            "This is point-to-point LoRa at 915 MHz, not LoRaWAN.",
            "The schedule CSVs define one repeated schedule period.",
            "Scheduled SEND counts are not measured transmitted-packet counts.",
            "No collision, latency, energy, scaling, or operational wildfire claims are made here.",
            "Usefulness and priority are synthetic metadata.",
        ],
    }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    print("Wrote Run 030 three-transmitter schedule artifacts")
    for label, counts in [
        ("TXA/N01", txa_counts),
        ("TXB/N16", txb_counts),
        ("TXC/N31", txc_counts),
    ]:
        rows_n, send_n, skip_n = counts
        print(f"{label}: rows={rows_n}, send={send_n}, skip={skip_n}")

    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()