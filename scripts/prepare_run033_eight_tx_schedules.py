#!/usr/bin/env python3
"""
Prepare Run 033 eight-transmitter SD replay schedules.

This is intentionally Run-033-specific. It extends the validated Run 032
six-transmitter schedule-preparation pattern to an eight-transmitter bridge.

This script prepares repository-side schedule artifacts only.

It does not copy schedules to SD cards, flash firmware, run hardware, collect
receiver logs, or make physical replay claims.
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
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
]


INPUT = Path("traces/run032_reporting_txa_fixed_all_schedule.csv")
RUN033_BASE_SCHEDULE = Path("traces/run033_eight_tx_base_schedule.csv")
MANIFEST = Path("traces/run033_reporting_reporting_schedule_manifest.json")

RUN_ID = "run033_eight_transmitter_schedule_prep"
MILESTONE = "v5.1-run033-eight-transmitter-schedule-prep"
SCHEDULE_PERIOD_ROWS = 64


TRANSMITTERS = [
    {
        "tx_id": "TXA",
        "node_id": "N01",
        "role": "fixed-all anchor",
        "policy": "fixed_all",
        "policy_code": "F",
        "threshold_family": None,
        "send_rows": None,
    },
    {
        "tx_id": "TXB",
        "node_id": "N16",
        "role": "medium threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "medium",
        "send_rows": 32,
    },
    {
        "tx_id": "TXC",
        "node_id": "N31",
        "role": "strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "strict",
        "send_rows": 16,
    },
    {
        "tx_id": "TXD",
        "node_id": "N46",
        "role": "very-strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "very_strict",
        "send_rows": 8,
    },
    {
        "tx_id": "TXE",
        "node_id": "N61",
        "role": "medium threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "medium",
        "send_rows": 32,
    },
    {
        "tx_id": "TXF",
        "node_id": "N76",
        "role": "strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "strict",
        "send_rows": 16,
    },
    {
        "tx_id": "TXG",
        "node_id": "N91",
        "role": "very-strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "very_strict",
        "send_rows": 8,
    },
    {
        "tx_id": "TXH",
        "node_id": "N106",
        "role": "ultra-strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "ultra_strict",
        "send_rows": 4,
    },
]


LABELS = {
    "TXA": "txa_fixed_all",
    "TXB": "txb_medium_threshold",
    "TXC": "txc_strict_threshold",
    "TXD": "txd_very_strict_threshold",
    "TXE": "txe_medium_threshold",
    "TXF": "txf_strict_threshold",
    "TXG": "txg_very_strict_threshold",
    "TXH": "txh_ultra_strict_threshold",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path} missing required columns: {missing}")
        rows = list(reader)

    if len(rows) != SCHEDULE_PERIOD_ROWS:
        raise ValueError(
            f"{path} has {len(rows)} rows; expected {SCHEDULE_PERIOD_ROWS}"
        )

    seqs = [int(r["seq"]) for r in rows]
    if len(seqs) != len(set(seqs)):
        raise ValueError(f"{path} contains duplicate seq values")

    return rows


def usefulness_sorted(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda r: (-float(r["usefulness"]), int(r["seq"])),
    )


def schedule_rows(
    base_rows: list[dict[str, str]],
    *,
    policy_code: str,
    send_rows: int | None,
) -> list[dict[str, str]]:
    if send_rows is None:
        send_seq = {int(r["seq"]) for r in base_rows}
    else:
        selected = usefulness_sorted(base_rows)[:send_rows]
        send_seq = {int(r["seq"]) for r in selected}

    out = []
    for row in sorted(base_rows, key=lambda r: int(r["seq"])):
        seq = int(row["seq"])
        out.append(
            {
                "seq": row["seq"],
                "region": row["region"],
                "event": row["event"],
                "priority": row["priority"],
                "usefulness": row["usefulness"],
                "stale_after": row["stale_after"],
                "policy": policy_code,
                "send": "1" if seq in send_seq else "0",
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEDULE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def transmitter_paths(tx_id: str) -> dict[str, Path]:
    label = LABELS[tx_id]
    return {
        "schedule_csv": Path(f"traces/run033_reporting_{label}_schedule.csv"),
        "compact_csv": Path(f"traces/run033_reporting_{label}_compact.csv"),
        "sd_csv": Path(f"traces/run033_sd_{tx_id.lower()}_schedule.csv"),
    }


def main() -> None:
    base_rows = read_rows(INPUT)

    shutil.copyfile(INPUT, RUN033_BASE_SCHEDULE)

    manifest_txs = []
    generated_files = [str(RUN033_BASE_SCHEDULE)]

    for tx in TRANSMITTERS:
        send_rows = tx["send_rows"]
        expected_send_rows = SCHEDULE_PERIOD_ROWS if send_rows is None else send_rows
        expected_skip_rows = SCHEDULE_PERIOD_ROWS - expected_send_rows

        rows = schedule_rows(
            base_rows,
            policy_code=tx["policy_code"],
            send_rows=send_rows,
        )
        compact = [r for r in rows if r["send"] == "1"]

        paths = transmitter_paths(tx["tx_id"])
        write_csv(paths["schedule_csv"], rows)
        write_csv(paths["compact_csv"], compact)
        write_csv(paths["sd_csv"], rows)

        generated_files.extend(str(p) for p in paths.values())

        manifest_row = {
            "tx_id": tx["tx_id"],
            "node_id": tx["node_id"],
            "role": tx["role"],
            "policy": tx["policy"],
            "policy_code": tx["policy_code"],
            "threshold_family": tx["threshold_family"],
            "startup_offset_ms": None,
            "startup_offset_status": "deferred to Run 033 physical-prep milestone",
            "expected_send_fraction": expected_send_rows / SCHEDULE_PERIOD_ROWS,
            "schedule_csv": str(paths["schedule_csv"]),
            "compact_csv": str(paths["compact_csv"]),
            "sd_csv": str(paths["sd_csv"]),
            "expected_rows": SCHEDULE_PERIOD_ROWS,
            "expected_send_rows": expected_send_rows,
            "expected_skip_rows": expected_skip_rows,
        }

        if tx["policy"] == "usefulness_threshold":
            manifest_row["selection_rule"] = (
                f"top {expected_send_rows} rows by usefulness, "
                "sequence ascending for ties"
            )

        manifest_txs.append(manifest_row)

    expected_ratios = {}
    for tx in manifest_txs:
        if tx["tx_id"] == "TXA":
            continue
        expected_ratios[f"{tx['tx_id']}/TXA"] = (
            tx["expected_send_rows"] / SCHEDULE_PERIOD_ROWS
        )

    manifest = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "purpose": (
            "Prepare manifest-bound eight-transmitter all-slot SD schedules "
            "for a later physical preparation milestone."
        ),
        "source_schedule": str(INPUT),
        "run033_base_schedule_copy": str(RUN033_BASE_SCHEDULE),
        "schedule_period_rows": SCHEDULE_PERIOD_ROWS,
        "sd_schedule_schema": SCHEDULE_COLUMNS,
        "transmitters": manifest_txs,
        "expected_scheduled_ratios": expected_ratios,
        "sd_card_convention": (
            "Repository-side SD CSVs are prepared here only. Copying to physical "
            "SD cards is deferred to the Run 033 physical-prep milestone."
        ),
        "phase_plan_status": (
            "Startup offsets and phase strategy are intentionally deferred to "
            "the Run 033 physical-prep milestone."
        ),
        "generated_files": generated_files + [str(MANIFEST)],
        "interpretation_boundary": (
            "Schedule-prep artifact only; no hardware was flashed, no SD cards "
            "were prepared, no receiver was run, no packets were collected, and "
            "no physical replay claim is made."
        ),
    }

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {RUN033_BASE_SCHEDULE}")
    for tx in manifest_txs:
        print(
            f"{tx['tx_id']}/{tx['node_id']}: "
            f"{tx['expected_send_rows']}/{tx['expected_rows']} SEND rows"
        )
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
