#!/usr/bin/env python3
"""
Generate policy-controlled synthetic belief-demand traces for Run 019.

v0.5 goal:
- Build one shared synthetic belief-demand substrate.
- Emit two policy-conditioned traces:
    TX-A: fixed_all baseline
    TX-B: usefulness_threshold
- Preserve the existing packet schema:
    seq,region,event,priority,usefulness,stale_after,policy
- seq is the emitted packet sequence, not the original base-demand row index.
- This avoids treating intentional policy filtering as observed sequence gaps.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


RUN_ID = "R19"
OUT_DIR = Path("traces")

BASE_TRACE = OUT_DIR / "run019_base_demand.csv"
TXA_TRACE = OUT_DIR / "run019_txa_fixed_all.csv"
TXB_TRACE = OUT_DIR / "run019_txb_usefulness_threshold.csv"
MANIFEST = OUT_DIR / "run019_policy_manifest.json"

FIELDNAMES = [
    "seq",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
]

# Shared demand substrate.
# The phase pattern intentionally resembles Run 018 for interpretability.
PHASE_SCHEDULE = [
    {"start": 0, "end": 49, "usefulness": 0.20},
    {"start": 50, "end": 99, "usefulness": 0.85},
    {"start": 100, "end": 149, "usefulness": 0.30},
    {"start": 150, "end": 199, "usefulness": 0.90},
    {"start": 200, "end": 249, "usefulness": 0.20},
    {"start": 250, "end": 299, "usefulness": 0.20},
    {"start": 300, "end": 319, "usefulness": 0.85},
]

BASE_ROWS = 320
TX_INTERVAL_MS = 1000
STALE_AFTER = 30
THRESHOLD = 0.50


def priority_from_usefulness(usefulness: float) -> float:
    """Map usefulness to the existing trace priority scale."""
    if usefulness >= 0.85:
        return 0.90
    if usefulness >= 0.50:
        return 0.60
    return 0.25


def usefulness_for_index(index: int) -> float:
    """Return usefulness from the configured phase schedule."""
    for phase in PHASE_SCHEDULE:
        if phase["start"] <= index <= phase["end"]:
            return float(phase["usefulness"])
    raise ValueError(f"No usefulness phase defined for index {index}")


def build_base_demand_rows() -> list[dict[str, Any]]:
    """Build the shared synthetic demand substrate."""
    rows: list[dict[str, Any]] = []

    for idx in range(BASE_ROWS):
        usefulness = usefulness_for_index(idx)
        rows.append(
            {
                "base_index": idx,
                "tx_ms": idx * TX_INTERVAL_MS,
                "region": "A",
                "event": "0",
                "priority": priority_from_usefulness(usefulness),
                "usefulness": usefulness,
                "stale_after": STALE_AFTER,
            }
        )

    return rows


def emit_policy_rows(
    base_rows: list[dict[str, Any]],
    *,
    tx_id: str,
    node_id: str,
    policy: str,
    threshold: float | None = None,
) -> list[dict[str, Any]]:
    """Apply a reporting policy and return transmitted packet rows."""
    emitted: list[dict[str, Any]] = []

    for row in base_rows:
        usefulness = float(row["usefulness"])

        if policy == "fixed_all":
            should_emit = True
        elif policy == "usefulness_threshold":
            if threshold is None:
                raise ValueError("usefulness_threshold policy requires threshold")
            should_emit = usefulness >= threshold
        else:
            raise ValueError(f"Unknown policy: {policy}")

        if not should_emit:
            continue

        policy_code = "F" if policy == "fixed_all" else "U"

        emitted.append(
            {
                "seq": len(emitted),
                "region": row["region"],
                "event": row["event"],
                "priority": f'{float(row["priority"]):.3f}',
                "usefulness": f"{usefulness:.3f}",
                "stale_after": row["stale_after"],
                "policy": policy_code,
            }
        )

    return emitted


def write_packet_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a packet trace using the current firmware packet schema."""
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_base_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the base demand substrate, including base_index for inspection."""
    fieldnames = [
        "base_index",
        "tx_ms",
        "region",
        "event",
        "priority",
        "usefulness",
        "stale_after",
    ]

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def total_usefulness(rows: list[dict[str, Any]]) -> float:
    return sum(float(row["usefulness"]) for row in rows)


def mean_usefulness(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return total_usefulness(rows) / len(rows)


def write_manifest(
    path: Path,
    *,
    base_rows: list[dict[str, Any]],
    txa_rows: list[dict[str, Any]],
    txb_rows: list[dict[str, Any]],
) -> None:
    manifest = {
        "run_id": RUN_ID,
        "milestone": "v0.5-policy-controlled-synthetic-traces",
        "generator": {
            "name": "generate_policy_traces.py",
            "version": "0.1",
        },
        "base_demand": {
            "source": "synthetic",
            "rows": len(base_rows),
            "phase_schedule": PHASE_SCHEDULE,
            "region_codes": {
                "A": "synthetic region A",
            },
            "event_codes": {
                "0": "belief-demand metadata event",
            },
            "policy_codes": {
                "F": "fixed_all",
                "U": "usefulness_threshold",
            },
        },
        "policies": [
            {
                "tx_id": "TXA",
                "node_id": "N01",
                "policy": "fixed_all",
                "rule": "emit every base demand row",
                "threshold": None,
                "emitted_rows": len(txa_rows),
                "generated_total_usefulness": round(total_usefulness(txa_rows), 3),
                "generated_mean_usefulness": round(mean_usefulness(txa_rows), 3),
            },
            {
                "tx_id": "TXB",
                "node_id": "N16",
                "policy": "usefulness_threshold",
                "rule": "emit rows with usefulness >= threshold",
                "threshold": THRESHOLD,
                "emitted_rows": len(txb_rows),
                "generated_total_usefulness": round(total_usefulness(txb_rows), 3),
                "generated_mean_usefulness": round(mean_usefulness(txb_rows), 3),
            },
        ],
        "firmware": {
            "replay_mode": "compiled_in_trace_header",
            "send_interval_ms": TX_INTERVAL_MS,
            "txb_startup_offset_ms": 500,
        },
        "interpretation_cautions": [
            "recv_ms and tx_ms are not synchronized across boards",
            "observed sequence gaps are not direct collision evidence",
            "v0.5 controls trace content, not yet true LoRa airtime scheduling",
            "seq is the emitted packet sequence, not the original base-demand row index",
            "CSV traces use the existing compiled-header input schema",
        ],
    }

    with path.open("w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    base_rows = build_base_demand_rows()

    txa_rows = emit_policy_rows(
        base_rows,
        tx_id="TXA",
        node_id="N01",
        policy="fixed_all",
    )

    txb_rows = emit_policy_rows(
        base_rows,
        tx_id="TXB",
        node_id="N16",
        policy="usefulness_threshold",
        threshold=THRESHOLD,
    )

    write_base_trace(BASE_TRACE, base_rows)
    write_packet_trace(TXA_TRACE, txa_rows)
    write_packet_trace(TXB_TRACE, txb_rows)
    write_manifest(
        MANIFEST,
        base_rows=base_rows,
        txa_rows=txa_rows,
        txb_rows=txb_rows,
    )

    print("Generated Run 019 policy-controlled traces")
    print()
    print(f"Base demand rows: {len(base_rows)}")
    print()
    print(
        "TXA/N01 fixed_all: "
        f"{len(txa_rows)} rows, "
        f"total usefulness={total_usefulness(txa_rows):.2f}, "
        f"mean usefulness={mean_usefulness(txa_rows):.3f}"
    )
    print(
        "TXB/N16 usefulness_threshold: "
        f"{len(txb_rows)} rows, "
        f"threshold={THRESHOLD:.2f}, "
        f"total usefulness={total_usefulness(txb_rows):.2f}, "
        f"mean usefulness={mean_usefulness(txb_rows):.3f}"
    )
    print()
    print(f"Wrote {BASE_TRACE}")
    print(f"Wrote {TXA_TRACE}")
    print(f"Wrote {TXB_TRACE}")
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()