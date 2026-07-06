#!/usr/bin/env python3
"""
Prepare the Run 034 ten-transmitter deterministic startup phase plan.

This is a Run-034-specific analysis/design script.

It reads the generated Run 034 schedule manifest and schedules, assigns the
candidate deterministic startup offsets, computes exact same-ms scheduled SEND
coincidences, computes near scheduled SEND coincidences, writes phase-plan
outputs, and records the assigned offsets in the Run 034 manifest.

It does not modify firmware, copy schedules to SD cards, flash transmitters,
run hardware, collect receiver logs, or make physical replay claims.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any


MANIFEST = Path("traces/run034_reporting_reporting_schedule_manifest.json")

SUMMARY_JSON = Path("outputs/run034_ten_tx_phase_plan_summary.json")
EXACT_CSV = Path("outputs/run034_ten_tx_phase_plan_exact_coincidences.csv")
NEAR_CSV = Path("outputs/run034_ten_tx_phase_plan_near_coincidences.csv")

RUN_ID = "run034_ten_transmitter_phase_plan"
MILESTONE = "v5.8-run034-ten-transmitter-phase-plan"

SLOT_INTERVAL_MS = 10_000
NEAR_COINCIDENCE_WINDOW_MS = 150

# Candidate from the Run 034 bridge design:
# keep the successful Run 033 shifted offsets and add TXI/TXJ.
STARTUP_OFFSETS_MS = {
    "TXH": 100,
    "TXD": 800,
    "TXA": 1000,
    "TXF": 2500,
    "TXB": 3250,
    "TXC": 4750,
    "TXI": 5850,
    "TXE": 7750,
    "TXG": 9450,
    "TXJ": 10650,
}


EXACT_COLUMNS = [
    "event_time_ms",
    "tx_a",
    "node_a",
    "seq_a",
    "tx_b",
    "node_b",
    "seq_b",
    "delta_ms",
]

NEAR_COLUMNS = [
    "event_time_ms_a",
    "event_time_ms_b",
    "delta_ms",
    "tx_a",
    "node_a",
    "seq_a",
    "tx_b",
    "node_b",
    "seq_b",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_send_rows(path: Path) -> list[int]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"seq", "send"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing required columns: {sorted(missing)}")

        send_rows = []
        for row in reader:
            if row["send"] == "1":
                send_rows.append(int(row["seq"]))

    return sorted(send_rows)


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_events(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    manifest_txs = manifest.get("transmitters", [])
    manifest_tx_ids = {tx["tx_id"] for tx in manifest_txs}
    offset_tx_ids = set(STARTUP_OFFSETS_MS)

    missing_offsets = sorted(manifest_tx_ids - offset_tx_ids)
    extra_offsets = sorted(offset_tx_ids - manifest_tx_ids)

    if missing_offsets:
        raise ValueError(f"Missing startup offsets for: {missing_offsets}")
    if extra_offsets:
        raise ValueError(f"Startup offsets contain unknown TX IDs: {extra_offsets}")

    for tx in manifest_txs:
        tx_id = tx["tx_id"]
        node_id = tx["node_id"]
        schedule_csv = Path(tx["schedule_csv"])
        offset_ms = STARTUP_OFFSETS_MS[tx_id]

        send_rows = read_send_rows(schedule_csv)
        expected_send_rows = int(tx["expected_send_rows"])
        if len(send_rows) != expected_send_rows:
            raise ValueError(
                f"{tx_id} has {len(send_rows)} SEND rows; "
                f"expected {expected_send_rows}"
            )

        for seq in send_rows:
            event_time_ms = offset_ms + SLOT_INTERVAL_MS * seq
            events.append(
                {
                    "tx_id": tx_id,
                    "node_id": node_id,
                    "seq": seq,
                    "startup_offset_ms": offset_ms,
                    "event_time_ms": event_time_ms,
                }
            )

    return sorted(events, key=lambda e: (e["event_time_ms"], e["tx_id"], e["seq"]))


def exact_coincidences(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_time: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_time[int(event["event_time_ms"])].append(event)

    rows: list[dict[str, Any]] = []
    for event_time_ms, same_time_events in sorted(by_time.items()):
        cross_tx_events = same_time_events
        if len({e["tx_id"] for e in cross_tx_events}) < 2:
            continue

        for a, b in combinations(cross_tx_events, 2):
            if a["tx_id"] == b["tx_id"]:
                continue
            rows.append(
                {
                    "event_time_ms": event_time_ms,
                    "tx_a": a["tx_id"],
                    "node_a": a["node_id"],
                    "seq_a": a["seq"],
                    "tx_b": b["tx_id"],
                    "node_b": b["node_id"],
                    "seq_b": b["seq"],
                    "delta_ms": 0,
                }
            )
    return rows


def near_coincidences(
    events: list[dict[str, Any]],
    *,
    window_ms: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for i, a in enumerate(events):
        for b in events[i + 1 :]:
            delta = int(b["event_time_ms"]) - int(a["event_time_ms"])
            if delta > window_ms:
                break
            if delta <= 0:
                continue
            if a["tx_id"] == b["tx_id"]:
                continue

            rows.append(
                {
                    "event_time_ms_a": a["event_time_ms"],
                    "event_time_ms_b": b["event_time_ms"],
                    "delta_ms": delta,
                    "tx_a": a["tx_id"],
                    "node_a": a["node_id"],
                    "seq_a": a["seq"],
                    "tx_b": b["tx_id"],
                    "node_b": b["node_id"],
                    "seq_b": b["seq"],
                }
            )

    return rows


def pairwise_min_deltas(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_tx: dict[str, list[dict[str, Any]]] = defaultdict(list)
    node_by_tx: dict[str, str] = {}

    for event in events:
        by_tx[event["tx_id"]].append(event)
        node_by_tx[event["tx_id"]] = event["node_id"]

    rows: list[dict[str, Any]] = []

    for tx_a, tx_b in combinations(sorted(by_tx), 2):
        best: tuple[int, dict[str, Any], dict[str, Any]] | None = None

        for a in by_tx[tx_a]:
            for b in by_tx[tx_b]:
                delta = abs(int(a["event_time_ms"]) - int(b["event_time_ms"]))
                if best is None or delta < best[0]:
                    best = (delta, a, b)

        if best is None:
            continue

        delta, a, b = best
        rows.append(
            {
                "tx_a": tx_a,
                "node_a": node_by_tx[tx_a],
                "tx_b": tx_b,
                "node_b": node_by_tx[tx_b],
                "min_delta_ms": delta,
                "seq_a_at_min_delta": a["seq"],
                "seq_b_at_min_delta": b["seq"],
                "event_time_ms_a": a["event_time_ms"],
                "event_time_ms_b": b["event_time_ms"],
            }
        )

    return rows


def update_manifest(
    manifest: dict[str, Any],
    *,
    exact_count: int,
    near_count: int,
    total_send_events: int,
) -> dict[str, Any]:
    for tx in manifest["transmitters"]:
        tx_id = tx["tx_id"]
        tx["startup_offset_ms"] = STARTUP_OFFSETS_MS[tx_id]
        tx["startup_offset_status"] = (
            "assigned by v5.8-run034-ten-transmitter-phase-plan"
        )

    manifest["phase_plan_status"] = (
        "assigned by v5.8-run034-ten-transmitter-phase-plan; "
        "exact and near scheduled SEND coincidence checks written to outputs"
    )

    manifest["phase_plan"] = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "slot_interval_ms": SLOT_INTERVAL_MS,
        "near_coincidence_window_ms": NEAR_COINCIDENCE_WINDOW_MS,
        "startup_offsets_ms": STARTUP_OFFSETS_MS,
        "total_scheduled_send_events": total_send_events,
        "exact_same_ms_coincidence_count": exact_count,
        "near_coincidence_count": near_count,
        "status": "pass" if exact_count == 0 and near_count == 0 else "review",
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "exact_coincidences_csv": str(EXACT_CSV),
            "near_coincidences_csv": str(NEAR_CSV),
        },
        "interpretation_boundary": [
            "Phase-plan analysis only; no physical replay has been run.",
            "Startup offsets are deterministic design values for later physical prep.",
            "Coincidence checks are schedule-time checks, not RF collision observations.",
            "Does not confirm RF collisions or absence of collisions.",
            "Does not establish synchronized latency.",
            "Does not evaluate LoRaWAN behavior.",
            "Does not establish energy savings or airtime optimization.",
            "Does not use a live belief-maintenance controller.",
            "Does not evaluate operational wildfire behavior.",
        ],
    }

    return manifest


def main() -> None:
    manifest = read_json(MANIFEST)
    events = build_events(manifest)

    exact_rows = exact_coincidences(events)
    near_rows = near_coincidences(
        events,
        window_ms=NEAR_COINCIDENCE_WINDOW_MS,
    )
    pairwise_rows = pairwise_min_deltas(events)

    offset_rows = []
    for tx in manifest["transmitters"]:
        tx_id = tx["tx_id"]
        offset_rows.append(
            {
                "tx_id": tx_id,
                "node_id": tx["node_id"],
                "startup_offset_ms": STARTUP_OFFSETS_MS[tx_id],
                "expected_send_rows": tx["expected_send_rows"],
                "schedule_csv": tx["schedule_csv"],
                "sd_csv": tx["sd_csv"],
            }
        )

    min_pairwise_delta_ms = (
        min(row["min_delta_ms"] for row in pairwise_rows) if pairwise_rows else None
    )

    summary = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "source_manifest": str(MANIFEST),
        "slot_interval_ms": SLOT_INTERVAL_MS,
        "near_coincidence_window_ms": NEAR_COINCIDENCE_WINDOW_MS,
        "transmitter_count": len(manifest["transmitters"]),
        "total_scheduled_send_events": len(events),
        "startup_offsets_ms": STARTUP_OFFSETS_MS,
        "startup_offsets_by_transmitter": offset_rows,
        "exact_same_ms_coincidence_count": len(exact_rows),
        "near_coincidence_count": len(near_rows),
        "min_pairwise_delta_ms": min_pairwise_delta_ms,
        "pairwise_min_deltas": pairwise_rows,
        "status": "pass" if len(exact_rows) == 0 and len(near_rows) == 0 else "review",
        "outputs": {
            "exact_coincidences_csv": str(EXACT_CSV),
            "near_coincidences_csv": str(NEAR_CSV),
        },
        "interpretation_boundary": [
            "Phase-plan analysis only; no physical replay has been run.",
            "Startup offsets are deterministic design values for later physical prep.",
            "Coincidence checks are schedule-time checks, not RF collision observations.",
            "Does not confirm RF collisions or absence of collisions.",
            "Does not establish synchronized latency.",
            "Does not evaluate LoRaWAN behavior.",
            "Does not establish energy savings or airtime optimization.",
            "Does not use a live belief-maintenance controller.",
            "Does not evaluate operational wildfire behavior.",
        ],
    }

    write_csv(EXACT_CSV, EXACT_COLUMNS, exact_rows)
    write_csv(NEAR_CSV, NEAR_COLUMNS, near_rows)
    write_json(SUMMARY_JSON, summary)

    updated_manifest = update_manifest(
        manifest,
        exact_count=len(exact_rows),
        near_count=len(near_rows),
        total_send_events=len(events),
    )
    write_json(MANIFEST, updated_manifest)

    print(f"Wrote summary: {SUMMARY_JSON}")
    print(f"Wrote exact coincidences: {EXACT_CSV}")
    print(f"Wrote near coincidences: {NEAR_CSV}")
    print(f"Updated manifest: {MANIFEST}")
    print()
    print("Run 034 startup offsets:")
    for row in offset_rows:
        print(
            f"  {row['tx_id']}/{row['node_id']}: "
            f"{row['startup_offset_ms']} ms, "
            f"{row['expected_send_rows']} scheduled SEND rows"
        )

    print()
    print(f"Total scheduled SEND events: {len(events)}")
    print(f"Exact same-ms scheduled SEND coincidences: {len(exact_rows)}")
    print(
        f"Near scheduled SEND coincidences "
        f"(<= {NEAR_COINCIDENCE_WINDOW_MS} ms): {len(near_rows)}"
    )
    print(f"Minimum pairwise scheduled SEND separation: {min_pairwise_delta_ms} ms")
    print(f"Status: {summary['status']}")


if __name__ == "__main__":
    main()
