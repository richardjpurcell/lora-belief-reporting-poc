#!/usr/bin/env python3
"""
Prepare Run 032 six-transmitter SD replay schedules.

This is intentionally Run-032-specific. It extends the Run 031 four-transmitter
schedule-preparation pattern to a six-transmitter physical-prep candidate.

The physical-prep candidate uses the TXF sequential bridge:

    TXD/N46, TXA/N01, TXF/N76, TXB/N16, TXC/N31, TXE/N61

This preserves the optimized 250 ms-grid phase logic while keeping the physical
board identity sequence TXA through TXF.

Design:

The SD-facing files remain all-slot CSVs with schema:

    seq,region,event,priority,usefulness,stale_after,policy,send

The firmware-facing policy field is a single-character code.

This script prepares repository-side schedule artifacts only. It does not copy
schedules to SD cards, flash firmware, run hardware, or collect receiver logs.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Iterable


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

REQUIRED_COLUMNS = [
    "priority",
    "usefulness",
    "stale_after",
]


INPUT = Path("traces/run031_four_tx_base_schedule.csv")
RUN032_BASE_SCHEDULE = Path("traces/run032_six_tx_base_schedule.csv")
PHASE_PLAN = Path("traces/run032_six_tx_phase_plan_bridge_txf.csv")

MANIFEST = Path("traces/run032_reporting_reporting_schedule_manifest.json")


TRANSMITTERS = [
    {
        "tx_id": "TXD",
        "node_id": "N46",
        "role": "very-strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "very_strict",
        "startup_offset_ms": 0,
        "send_rows": 8,
    },
    {
        "tx_id": "TXA",
        "node_id": "N01",
        "role": "fixed-all anchor",
        "policy": "fixed_all",
        "policy_code": "F",
        "threshold_family": None,
        "startup_offset_ms": 500,
        "send_rows": None,
    },
    {
        "tx_id": "TXF",
        "node_id": "N76",
        "role": "strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "strict",
        "startup_offset_ms": 2000,
        "send_rows": 16,
    },
    {
        "tx_id": "TXB",
        "node_id": "N16",
        "role": "medium threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "medium",
        "startup_offset_ms": 2750,
        "send_rows": 32,
    },
    {
        "tx_id": "TXC",
        "node_id": "N31",
        "role": "strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "strict",
        "startup_offset_ms": 4250,
        "send_rows": 16,
    },
    {
        "tx_id": "TXE",
        "node_id": "N61",
        "role": "medium threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "medium",
        "startup_offset_ms": 7250,
        "send_rows": 32,
    },
]


def schedule_stem(tx_id: str, threshold_family: str | None) -> str:
    tx_lower = tx_id.lower()
    if threshold_family is None:
        return f"run032_reporting_{tx_lower}_fixed_all"
    return f"run032_reporting_{tx_lower}_{threshold_family}_threshold"


def schedule_path(tx_id: str, threshold_family: str | None) -> Path:
    return Path("traces") / f"{schedule_stem(tx_id, threshold_family)}_schedule.csv"


def compact_path(tx_id: str, threshold_family: str | None) -> Path:
    return Path("traces") / f"{schedule_stem(tx_id, threshold_family)}_compact.csv"


def sd_path(tx_id: str) -> Path:
    return Path("traces") / f"run032_sd_{tx_id.lower()}_schedule.csv"


def first_present(row: dict[str, str], candidates: list[str]) -> str | None:
    """Return the first non-empty value from a list of possible column names."""
    for name in candidates:
        if name in row and str(row[name]).strip() != "":
            return str(row[name]).strip()
    return None


def normalize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Normalize a schedule-like CSV into the SD replay schema."""
    normalized: list[dict[str, str]] = []

    for idx, row in enumerate(rows):
        seq = first_present(
            row,
            ["seq", "sequence", "slot", "row", "t", "time", "time_step", "step"],
        )
        region = first_present(
            row,
            ["region", "region_id", "cell", "cell_id", "node_region"],
        )
        event = first_present(row, ["event", "event_type", "label", "state"])
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
    schedule_path_: Path,
    compact_path_: Path,
    sd_path_: Path,
    rows: list[dict[str, str]],
) -> tuple[int, int, int]:
    write_csv(schedule_path_, rows)

    compact_rows = [row for row in rows if row["send"] == "1"]
    write_csv(compact_path_, compact_rows)

    # SD-facing schedule is intentionally all-slot, not compact.
    write_csv(sd_path_, rows)

    send_count = len(compact_rows)
    skip_count = len(rows) - send_count
    return len(rows), send_count, skip_count


def main() -> None:
    rows = read_rows(INPUT)

    RUN032_BASE_SCHEDULE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(INPUT, RUN032_BASE_SCHEDULE)

    send_sets = {
        None: None,
        "medium": top_n_seq_set(rows, 32),
        "strict": top_n_seq_set(rows, 16),
        "very_strict": top_n_seq_set(rows, 8),
    }

    manifest_transmitters = []

    for tx in TRANSMITTERS:
        threshold_family = tx["threshold_family"]
        rows_for_tx = build_schedule(
            rows,
            policy_code=tx["policy_code"],
            send_seq_set=send_sets[threshold_family],
        )

        sched = schedule_path(tx["tx_id"], threshold_family)
        compact = compact_path(tx["tx_id"], threshold_family)
        sd = sd_path(tx["tx_id"])

        counts = write_schedule_and_compact(sched, compact, sd, rows_for_tx)

        expected_send_rows = 64 if tx["send_rows"] is None else tx["send_rows"]
        if counts[1] != expected_send_rows:
            raise ValueError(
                f"{tx['tx_id']} expected {expected_send_rows} SEND rows, got {counts[1]}"
            )

        entry = {
            "tx_id": tx["tx_id"],
            "node_id": tx["node_id"],
            "role": tx["role"],
            "policy": tx["policy"],
            "policy_code": tx["policy_code"],
            "threshold_family": threshold_family,
            "startup_offset_ms": tx["startup_offset_ms"],
            "expected_send_fraction": counts[1] / counts[0],
            "schedule_csv": str(sched),
            "compact_csv": str(compact),
            "sd_csv": str(sd),
            "expected_rows": counts[0],
            "expected_send_rows": counts[1],
            "expected_skip_rows": counts[2],
        }

        if tx["send_rows"] is not None:
            entry["selection_rule"] = (
                f"top {tx['send_rows']} rows by usefulness, "
                "sequence ascending for ties"
            )

        manifest_transmitters.append(entry)

    manifest = {
        "run_id": "run032_six_transmitter_physical_prep",
        "milestone": "v4.7-run032-six-transmitter-physical-prep",
        "purpose": (
            "Prepare manifest-bound six-transmitter all-slot SD schedules "
            "for a later physical replay milestone."
        ),
        "source_schedule": str(INPUT),
        "run032_base_schedule_copy": str(RUN032_BASE_SCHEDULE),
        "phase_plan_source": str(PHASE_PLAN),
        "schedule_period_rows": 64,
        "sd_schedule_schema": SCHEDULE_COLUMNS,
        "transmitters": manifest_transmitters,
        "expected_scheduled_ratios": {
            "TXB/TXA": 32 / 64,
            "TXC/TXA": 16 / 64,
            "TXD/TXA": 8 / 64,
            "TXE/TXA": 32 / 64,
            "TXF/TXA": 16 / 64,
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
            "The same threshold family uses the same selected SEND rows; startup phase is handled separately by firmware configuration.",
            "No collision, latency, energy, scaling, or operational wildfire claims are made here.",
            "Usefulness and priority are synthetic metadata.",
        ],
    }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    print("Wrote Run 032 six-transmitter schedule artifacts")
    for tx in manifest_transmitters:
        print(
            f"{tx['tx_id']}/{tx['node_id']}: "
            f"rows={tx['expected_rows']}, "
            f"send={tx['expected_send_rows']}, "
            f"skip={tx['expected_skip_rows']}, "
            f"startup_offset_ms={tx['startup_offset_ms']}"
        )

    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
