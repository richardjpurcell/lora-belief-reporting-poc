#!/usr/bin/env python3
"""
Generate small synthetic belief-demand traces for LoRa metadata replay.

This script is intentionally simple. It does not simulate wildfire or run a
full belief-maintenance model. Instead, it creates reproducible packet metadata
traces that stand in for changing belief-maintenance demand over time.

Output CSV fields:

    seq,region,event,priority,usefulness,stale_after,policy
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


FIELDS = ["seq", "region", "event", "priority", "usefulness", "stale_after", "policy"]


@dataclass(frozen=True)
class Phase:
    name: str
    length: int
    region: str
    event: int
    priority: float
    usefulness: float
    stale_after: int
    policy: str


def write_trace(path: Path, phases: list[Phase]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    seq = 0
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for phase in phases:
            for _ in range(phase.length):
                writer.writerow(
                    {
                        "seq": seq,
                        "region": phase.region,
                        "event": phase.event,
                        "priority": f"{phase.priority:.2f}",
                        "usefulness": f"{phase.usefulness:.3f}",
                        "stale_after": phase.stale_after,
                        "policy": phase.policy,
                    }
                )
                seq += 1


def baseline_phases(length: int) -> list[Phase]:
    return [
        Phase(
            name="baseline_low",
            length=length,
            region="A",
            event=0,
            priority=0.25,
            usefulness=0.275,
            stale_after=30,
            policy="B",
        )
    ]


def demand_phases(cycles: int) -> list[Phase]:
    one_cycle = [
        Phase("low_background", 50, "B", 1, 0.20, 0.20, 30, "U"),
        Phase("high_demand", 50, "B", 1, 0.85, 0.85, 30, "U"),
        Phase("recovering", 50, "B", 1, 0.30, 0.30, 30, "U"),
        Phase("urgent_demand", 50, "B", 1, 0.90, 0.90, 30, "U"),
        Phase("low_background", 50, "B", 1, 0.20, 0.20, 30, "U"),
    ]

    phases: list[Phase] = []
    for _ in range(cycles):
        phases.extend(one_cycle)
    return phases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="traces", type=Path)
    parser.add_argument("--run-id", default="018")
    parser.add_argument("--cycles", default=1, type=int)
    args = parser.parse_args()

    if args.cycles < 1:
        raise ValueError("--cycles must be at least 1")

    txb_phases = demand_phases(args.cycles)
    txb_length = sum(phase.length for phase in txb_phases)

    txa_path = args.outdir / f"run_{args.run_id}_txa_trace.csv"
    txb_path = args.outdir / f"run_{args.run_id}_txb_trace.csv"

    write_trace(txa_path, baseline_phases(txb_length))
    write_trace(txb_path, txb_phases)

    print(f"Wrote {txa_path}")
    print(f"Wrote {txb_path}")
    print(f"Rows per trace: {txb_length}")


if __name__ == "__main__":
    main()
