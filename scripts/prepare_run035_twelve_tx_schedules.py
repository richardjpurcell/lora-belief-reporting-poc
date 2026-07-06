#!/usr/bin/env python3
"""
Prepare Run 035 twelve-transmitter SD replay schedules.

This is intentionally Run-035-specific. It extends the validated Run 034
ten-transmitter bridge to a cautious twelve-transmitter bridge.

This script prepares repository-side schedule artifacts only.

It does not copy schedules to SD cards, flash firmware, run hardware, collect
receiver logs, compute phase plans, or make physical replay claims.
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


INPUT = Path("traces/run034_reporting_txa_fixed_all_schedule.csv")
RUN035_BASE_SCHEDULE = Path("traces/run035_twelve_tx_base_schedule.csv")
MANIFEST = Path("traces/run035_reporting_reporting_schedule_manifest.json")

RUN_ID = "run035_twelve_transmitter_schedule_prep"
MILESTONE = "v5.13-run035-twelve-transmitter-schedule-prep"
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
    {
        "tx_id": "TXI",
        "node_id": "N121",
        "role": "strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "strict",
        "send_rows": 16,
    },
    {
        "tx_id": "TXJ",
        "node_id": "N136",
        "role": "very-strict threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "very_strict",
        "send_rows": 8,
    },
    {
        "tx_id": "TXK",
        "node_id": "N151",
        "role": "medium threshold scheduled skipping",
        "policy": "usefulness_threshold",
        "policy_code": "U",
        "threshold_family": "medium",
        "send_rows": 32,
    },
    {
        "tx_id": "TXL",
        "node_id": "N166",
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
    "TXI": "txi_strict_threshold",
    "TXJ": "txj_very_strict_threshold",
    "TXK": "txk_medium_threshold",
    "TXL": "txl_ultra_strict_threshold",
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
        "schedule_csv": Path(f"traces/run035_reporting_{label}_schedule.csv"),
        "compact_csv": Path(f"traces/run035_reporting_{label}_compact.csv"),
        "sd_csv": Path(f"traces/run035_sd_{tx_id.lower()}_schedule.csv"),
    }


def main() -> None:
    base_rows = read_rows(INPUT)

    shutil.copyfile(INPUT, RUN035_BASE_SCHEDULE)

    manifest_txs = []
    generated_files = [str(RUN035_BASE_SCHEDULE)]

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

        manifest_txs.append(
            {
                "tx_id": tx["tx_id"],
                "node_id": tx["node_id"],
                "role": tx["role"],
                "policy": tx["policy"],
                "policy_code": tx["policy_code"],
                "threshold_family": tx["threshold_family"],
                "startup_offset_ms": None,
                "startup_offset_status": (
                    "deferred to v5.14-run035-twelve-transmitter-phase-plan"
                ),
                "expected_send_fraction": expected_send_rows / SCHEDULE_PERIOD_ROWS,
                "schedule_csv": str(paths["schedule_csv"]),
                "compact_csv": str(paths["compact_csv"]),
                "sd_csv": str(paths["sd_csv"]),
                "expected_rows": SCHEDULE_PERIOD_ROWS,
                "expected_send_rows": expected_send_rows,
                "expected_skip_rows": expected_skip_rows,
            }
        )

    txa = manifest_txs[0]
    expected_scheduled_ratios = []
    for tx in manifest_txs[1:]:
        expected_scheduled_ratios.append(
            {
                "numerator_tx_id": tx["tx_id"],
                "numerator_node_id": tx["node_id"],
                "denominator_tx_id": txa["tx_id"],
                "denominator_node_id": txa["node_id"],
                "scheduled_expected_ratio": (
                    tx["expected_send_rows"] / txa["expected_send_rows"]
                ),
            }
        )

    manifest = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "purpose": (
            "Prepare Run 035 twelve-transmitter scheduled replay artifacts. "
            "This is schedule preparation only; phase planning is deferred."
        ),
        "source_schedule": str(INPUT),
        "run035_base_schedule_copy": str(RUN035_BASE_SCHEDULE),
        "schedule_period_rows": SCHEDULE_PERIOD_ROWS,
        "phase_plan_status": (
            "deferred to v5.14-run035-twelve-transmitter-phase-plan; "
            "deterministic startup offsets and exact/near scheduled SEND "
            "coincidence checks must be computed before physical prep"
        ),
        "sd_card_convention": (
            "Copy each traces/run035_sd_<tx>_schedule.csv to the corresponding "
            "transmitter SD card as schedule.csv during physical prep."
        ),
        "sd_schedule_schema": SCHEDULE_COLUMNS,
        "transmitters": manifest_txs,
        "expected_scheduled_ratios": expected_scheduled_ratios,
        "generated_files": generated_files,
        "validation": {
            "transmitter_count": len(manifest_txs),
            "expected_transmitter_count": 12,
            "schedule_row_count": SCHEDULE_PERIOD_ROWS,
            "all_startup_offsets_deferred": all(
                tx["startup_offset_ms"] is None for tx in manifest_txs
            ),
            "claims": {
                "schedule_prep_only": True,
                "phase_plan_computed": False,
                "physical_prep_performed": False,
                "physical_replay_performed": False,
            },
        },
    }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Self-check generated files.
    failures: list[str] = []

    if len(manifest_txs) != 12:
        failures.append(f"expected 12 transmitters, found {len(manifest_txs)}")

    for tx in manifest_txs:
        schedule_rows_read = read_rows(Path(tx["schedule_csv"]))
        sd_rows_read = read_rows(Path(tx["sd_csv"]))

        send_count = sum(1 for r in schedule_rows_read if r["send"] == "1")
        skip_count = sum(1 for r in schedule_rows_read if r["send"] == "0")

        if send_count != tx["expected_send_rows"]:
            failures.append(
                f"{tx['tx_id']} send count {send_count}; "
                f"expected {tx['expected_send_rows']}"
            )

        if skip_count != tx["expected_skip_rows"]:
            failures.append(
                f"{tx['tx_id']} skip count {skip_count}; "
                f"expected {tx['expected_skip_rows']}"
            )

        if len(sd_rows_read) != len(schedule_rows_read):
            failures.append(f"{tx['tx_id']} SD schedule row-count mismatch")

        compact_rows = list(csv.DictReader(Path(tx["compact_csv"]).open(encoding="utf-8")))
        if len(compact_rows) != tx["expected_send_rows"]:
            failures.append(
                f"{tx['tx_id']} compact rows {len(compact_rows)}; "
                f"expected {tx['expected_send_rows']}"
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print(f"Wrote {MANIFEST}")
    print(f"Generated {len(generated_files)} schedule artifacts")
    print("Validation passed")
    for tx in manifest_txs:
        print(
            f"{tx['tx_id']}/{tx['node_id']}: "
            f"{tx['expected_send_rows']}/{SCHEDULE_PERIOD_ROWS} SEND rows"
        )


if __name__ == "__main__":
    main()
