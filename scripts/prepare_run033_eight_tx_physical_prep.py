#!/usr/bin/env python3
"""
Prepare Run 033 eight-transmitter physical-prep artifacts.

This is a physical-preparation milestone only. It records the proposed startup
offsets, board identity mapping, SD schedule file mapping, receiver checklist,
bench checklist, and post-run analysis checklist.

It does not copy files to SD cards, flash firmware, run hardware, collect
receiver logs, parse packets, or make physical replay claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


MANIFEST = Path("traces/run033_reporting_reporting_schedule_manifest.json")
PHASE_PLAN_CSV = Path("traces/run033_eight_tx_phase_plan_physical_prep.csv")
SUMMARY_JSON = Path("outputs/run033_eight_tx_physical_prep_summary.json")
SUMMARY_CSV = Path("outputs/run033_eight_tx_physical_prep_summary.csv")


# This preserves the successful Run 032 TXF-bridge ordering for the first six
# transmitters and appends TXG/TXH as the new lower-rate bridge transmitters.
STARTUP_PLAN = [
    ("TXD", 0),
    ("TXA", 500),
    ("TXF", 2000),
    ("TXB", 2750),
    ("TXC", 4250),
    ("TXE", 7250),
    ("TXG", 8750),
    ("TXH", 10250),
]


def load_manifest() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def main() -> None:
    manifest = load_manifest()
    tx_by_id = {tx["tx_id"]: tx for tx in manifest["transmitters"]}

    missing = [tx_id for tx_id, _ in STARTUP_PLAN if tx_id not in tx_by_id]
    if missing:
        raise ValueError(f"Startup plan references missing transmitters: {missing}")

    extra = sorted(set(tx_by_id) - {tx_id for tx_id, _ in STARTUP_PLAN})
    if extra:
        raise ValueError(f"Manifest has transmitters missing from startup plan: {extra}")

    phase_rows = []
    for order, (tx_id, offset_ms) in enumerate(STARTUP_PLAN, start=1):
        tx = tx_by_id[tx_id]
        expected_ratio = (
            None if tx_id == "TXA" else tx["expected_send_rows"] / 64
        )

        phase_rows.append(
            {
                "startup_order": order,
                "tx_id": tx_id,
                "node_id": tx["node_id"],
                "role": tx["role"],
                "expected_send_rows": tx["expected_send_rows"],
                "expected_send_fraction": f"{tx['expected_send_fraction']:.6f}",
                "expected_ratio_to_txa": (
                    "" if expected_ratio is None else f"{expected_ratio:.6f}"
                ),
                "startup_offset_ms": offset_ms,
                "sd_schedule_csv": tx["sd_csv"],
                "recommended_sd_filename": "SCHEDULE.CSV",
                "board_identity_label": f"{tx_id}_{tx['node_id']}",
                "physical_status": "prepared for later bench setup",
                "notes": (
                    "startup offset is a programmed bench-prep value, "
                    "not a synchronization or latency claim"
                ),
            }
        )

    PHASE_PLAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PHASE_PLAN_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(phase_rows[0].keys()))
        writer.writeheader()
        writer.writerows(phase_rows)

    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "run_id": "run033_eight_transmitter_physical_prep",
        "milestone": "v5.2-run033-eight-transmitter-physical-prep",
        "source_manifest": str(MANIFEST),
        "phase_plan_csv": str(PHASE_PLAN_CSV),
        "transmitter_count": len(phase_rows),
        "startup_plan": phase_rows,
        "receiver_log_target": "logs/rx_run_033_eight_transmitter_sd_replay.csv",
        "parsed_log_target": "logs/parsed_run_033_eight_transmitter_sd_replay.csv",
        "rejects_log_target": "logs/parsed_run_033_eight_transmitter_sd_replay_rejects.csv",
        "expected_summary_json": "outputs/run033_eight_transmitter_manifest_replay_summary.json",
        "expected_summary_csv": "outputs/run033_eight_transmitter_manifest_replay_summary.csv",
        "expected_validation_json": "outputs/run033_eight_transmitter_manifest_replay_validation.json",
        "sd_copy_checklist": [
            {
                "tx_id": row["tx_id"],
                "node_id": row["node_id"],
                "source": row["sd_schedule_csv"],
                "destination_filename": row["recommended_sd_filename"],
                "action": "copy during physical-prep bench setup, not in this script",
            }
            for row in phase_rows
        ],
        "receiver_checklist": [
            "confirm receiver firmware and serial port before replay",
            "start receiver logging before powering transmitters",
            "record absolute start time in lab notes",
            "save raw receiver log using the Run 033 target filename",
            "do not edit the raw receiver log after capture",
        ],
        "bench_checklist": [
            "confirm each board identity label TXA through TXH",
            "confirm node identity N01 through N106",
            "confirm each SD card receives the matching Run 033 schedule file",
            "confirm programmed startup offsets match the phase-plan CSV",
            "preserve transmitter placement order in lab notes",
            "preserve receiver placement in lab notes",
            "record antenna and power conditions",
        ],
        "post_run_analysis_checklist": [
            "parse the raw receiver log",
            "write parsed valid-packet CSV",
            "write rejects CSV",
            "generate manifest-bound summary JSON and CSV",
            "generate manifest-bound validation JSON",
            "report receiver-side packet proportions relative to TXA",
            "report malformed/rejected rows explicitly",
            "report observed sequence gaps explicitly",
        ],
        "interpretation_boundary": (
            "Physical-prep artifact only. No SD cards were copied by this script, "
            "no firmware was flashed, no receiver was run, no packets were collected, "
            "and no physical replay claim is made."
        ),
    }

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "startup_order",
                "tx_id",
                "node_id",
                "expected_send_rows",
                "expected_ratio_to_txa",
                "startup_offset_ms",
                "sd_schedule_csv",
            ],
        )
        writer.writeheader()
        for row in phase_rows:
            writer.writerow(
                {
                    "startup_order": row["startup_order"],
                    "tx_id": row["tx_id"],
                    "node_id": row["node_id"],
                    "expected_send_rows": row["expected_send_rows"],
                    "expected_ratio_to_txa": row["expected_ratio_to_txa"],
                    "startup_offset_ms": row["startup_offset_ms"],
                    "sd_schedule_csv": row["sd_schedule_csv"],
                }
            )

    print(f"Wrote {PHASE_PLAN_CSV}")
    print(f"Wrote {SUMMARY_JSON}")
    print(f"Wrote {SUMMARY_CSV}")
    print()
    for row in phase_rows:
        print(
            f"{row['startup_order']}: {row['tx_id']}/{row['node_id']} "
            f"offset={row['startup_offset_ms']} ms "
            f"SEND={row['expected_send_rows']}/64"
        )


if __name__ == "__main__":
    main()
