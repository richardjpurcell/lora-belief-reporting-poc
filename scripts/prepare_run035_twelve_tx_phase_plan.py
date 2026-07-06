#!/usr/bin/env python3
"""
Prepare the Run 035 twelve-transmitter deterministic startup phase plan.

This is a Run-035-specific analysis/design script.

It reads the generated Run 035 schedule manifest and schedules, carries forward
the successful Run 034 A-J startup offsets, deterministically searches for TXK
and TXL startup offsets, computes exact same-ms scheduled SEND coincidences,
computes near scheduled SEND coincidences, writes phase-plan outputs, and records
the assigned offsets in the Run 035 manifest.

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


MANIFEST = Path("traces/run035_reporting_reporting_schedule_manifest.json")

PHASE_PLAN_CSV = Path("outputs/run035_twelve_tx_phase_plan.csv")
SUMMARY_JSON = Path("outputs/run035_twelve_tx_phase_plan_summary.json")
EXACT_CSV = Path("outputs/run035_twelve_tx_phase_plan_exact_coincidences.csv")
NEAR_CSV = Path("outputs/run035_twelve_tx_phase_plan_near_coincidences.csv")
PAIRWISE_MIN_CSV = Path("outputs/run035_twelve_tx_phase_plan_pairwise_min_deltas.csv")

RUN_ID = "run035_twelve_transmitter_phase_plan"
MILESTONE = "v5.14-run035-twelve-transmitter-phase-plan"

SLOT_INTERVAL_MS = 10_000
NEAR_COINCIDENCE_WINDOW_MS = 150

# Carry forward the successful Run 034 A-J phase-aware startup offsets.
BASE_STARTUP_OFFSETS_MS = {
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

# Search TXK then TXL deterministically. The search is deliberately bounded and
# coarse enough to remain practical while still preserving >150 ms separation.
SEARCH_TX_ORDER = ["TXK", "TXL"]
OFFSET_SEARCH_MIN_MS = 0
OFFSET_SEARCH_MAX_MS = 14_950
OFFSET_SEARCH_STEP_MS = 50


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

PHASE_PLAN_COLUMNS = [
    "tx_id",
    "node_id",
    "role",
    "policy",
    "threshold_family",
    "expected_send_fraction",
    "expected_send_rows",
    "startup_offset_ms",
    "startup_offset_source",
]

PAIRWISE_MIN_COLUMNS = [
    "tx_a",
    "node_a",
    "tx_b",
    "node_b",
    "min_delta_ms",
    "seq_a_at_min_delta",
    "seq_b_at_min_delta",
    "event_time_ms_a",
    "event_time_ms_b",
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


def tx_lookup(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    txs = manifest.get("transmitters", [])
    out = {tx["tx_id"]: tx for tx in txs}
    if len(out) != len(txs):
        raise ValueError("Manifest contains duplicate tx_id values")
    return out


def validate_manifest_shape(manifest: dict[str, Any]) -> None:
    txs = manifest.get("transmitters", [])
    tx_ids = [tx["tx_id"] for tx in txs]

    expected_tx_ids = [f"TX{letter}" for letter in "ABCDEFGHIJKL"]
    if tx_ids != expected_tx_ids:
        raise ValueError(f"Expected TX order {expected_tx_ids}, found {tx_ids}")

    base_missing = sorted(set(BASE_STARTUP_OFFSETS_MS) - set(tx_ids))
    base_extra = sorted(set(BASE_STARTUP_OFFSETS_MS) - set(expected_tx_ids))
    search_missing = sorted(set(SEARCH_TX_ORDER) - set(tx_ids))

    if base_missing:
        raise ValueError(f"Base startup offsets missing manifest TX IDs: {base_missing}")
    if base_extra:
        raise ValueError(f"Base startup offsets contain unexpected TX IDs: {base_extra}")
    if search_missing:
        raise ValueError(f"Search TX IDs missing from manifest: {search_missing}")


def build_events(
    manifest: dict[str, Any],
    startup_offsets_ms: dict[str, int],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    manifest_txs = manifest.get("transmitters", [])
    manifest_tx_ids = {tx["tx_id"] for tx in manifest_txs}
    offset_tx_ids = set(startup_offsets_ms)

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
        offset_ms = startup_offsets_ms[tx_id]

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
        if len({e["tx_id"] for e in same_time_events}) < 2:
            continue

        for a, b in combinations(same_time_events, 2):
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

    return sorted(rows, key=lambda r: (int(r["min_delta_ms"]), r["tx_a"], r["tx_b"]))


def min_delta_against_existing(
    candidate_events: list[dict[str, Any]],
    existing_events: list[dict[str, Any]],
) -> int:
    best: int | None = None
    for a in candidate_events:
        for b in existing_events:
            delta = abs(int(a["event_time_ms"]) - int(b["event_time_ms"]))
            if best is None or delta < best:
                best = delta
    if best is None:
        raise ValueError("Cannot compute min delta against empty event set")
    return best


def candidate_has_conflict(
    candidate_events: list[dict[str, Any]],
    existing_events: list[dict[str, Any]],
    *,
    window_ms: int,
) -> bool:
    for a in candidate_events:
        for b in existing_events:
            delta = abs(int(a["event_time_ms"]) - int(b["event_time_ms"]))
            if delta == 0:
                return True
            if 0 < delta <= window_ms:
                return True
    return False


def build_single_tx_events(tx: dict[str, Any], offset_ms: int) -> list[dict[str, Any]]:
    send_rows = read_send_rows(Path(tx["schedule_csv"]))
    expected_send_rows = int(tx["expected_send_rows"])
    if len(send_rows) != expected_send_rows:
        raise ValueError(
            f"{tx['tx_id']} has {len(send_rows)} SEND rows; "
            f"expected {expected_send_rows}"
        )

    return [
        {
            "tx_id": tx["tx_id"],
            "node_id": tx["node_id"],
            "seq": seq,
            "startup_offset_ms": offset_ms,
            "event_time_ms": offset_ms + SLOT_INTERVAL_MS * seq,
        }
        for seq in send_rows
    ]


def build_partial_events(
    manifest: dict[str, Any],
    startup_offsets_ms: dict[str, int],
) -> list[dict[str, Any]]:
    """Build events only for TX IDs that already have selected offsets.

    This is used during the incremental TXK/TXL search, before the full
    twelve-transmitter offset set exists.
    """

    events: list[dict[str, Any]] = []

    for tx in manifest.get("transmitters", []):
        tx_id = tx["tx_id"]
        if tx_id not in startup_offsets_ms:
            continue

        offset_ms = startup_offsets_ms[tx_id]
        send_rows = read_send_rows(Path(tx["schedule_csv"]))
        expected_send_rows = int(tx["expected_send_rows"])

        if len(send_rows) != expected_send_rows:
            raise ValueError(
                f"{tx_id} has {len(send_rows)} SEND rows; "
                f"expected {expected_send_rows}"
            )

        for seq in send_rows:
            events.append(
                {
                    "tx_id": tx_id,
                    "node_id": tx["node_id"],
                    "seq": seq,
                    "startup_offset_ms": offset_ms,
                    "event_time_ms": offset_ms + SLOT_INTERVAL_MS * seq,
                }
            )

    return sorted(events, key=lambda e: (e["event_time_ms"], e["tx_id"], e["seq"]))


def select_offsets(manifest: dict[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    lookup = tx_lookup(manifest)
    selected = dict(BASE_STARTUP_OFFSETS_MS)
    selection_trace: list[dict[str, Any]] = []

    for tx_id in SEARCH_TX_ORDER:
        tx = lookup[tx_id]
        existing_events = build_partial_events(manifest, selected)

        existing_max_offset = max(selected.values())
        valid_candidates: list[dict[str, Any]] = []

        for offset_ms in range(
            OFFSET_SEARCH_MIN_MS,
            OFFSET_SEARCH_MAX_MS + 1,
            OFFSET_SEARCH_STEP_MS,
        ):
            if offset_ms in selected.values():
                continue

            candidate_events = build_single_tx_events(tx, offset_ms)
            if candidate_has_conflict(
                candidate_events,
                existing_events,
                window_ms=NEAR_COINCIDENCE_WINDOW_MS,
            ):
                continue

            min_delta = min_delta_against_existing(candidate_events, existing_events)
            valid_candidates.append(
                {
                    "tx_id": tx_id,
                    "node_id": tx["node_id"],
                    "candidate_offset_ms": offset_ms,
                    "min_delta_ms": min_delta,
                    "after_existing_max_offset": offset_ms > existing_max_offset,
                }
            )

        if not valid_candidates:
            raise ValueError(f"No valid startup offset found for {tx_id}")

        # Prefer an appended startup offset after the existing maximum offset.
        # Within that constraint, maximize minimum schedule-time separation.
        # Final tie-breaker keeps the result deterministic and simple.
        chosen = sorted(
            valid_candidates,
            key=lambda c: (
                not c["after_existing_max_offset"],
                -int(c["min_delta_ms"]),
                int(c["candidate_offset_ms"]),
            ),
        )[0]

        selected[tx_id] = int(chosen["candidate_offset_ms"])
        selection_trace.append(
            {
                "tx_id": tx_id,
                "node_id": tx["node_id"],
                "selected_offset_ms": int(chosen["candidate_offset_ms"]),
                "min_delta_ms_against_prior_plan": int(chosen["min_delta_ms"]),
                "valid_candidate_count": len(valid_candidates),
                "selection_rule": (
                    "prefer offsets after the existing maximum; then maximize "
                    "minimum schedule-time separation; then choose smallest offset"
                ),
            }
        )

    return selected, selection_trace


def phase_plan_rows(
    manifest: dict[str, Any],
    startup_offsets_ms: dict[str, int],
) -> list[dict[str, Any]]:
    rows = []
    for tx in manifest["transmitters"]:
        tx_id = tx["tx_id"]
        rows.append(
            {
                "tx_id": tx_id,
                "node_id": tx["node_id"],
                "role": tx["role"],
                "policy": tx["policy"],
                "threshold_family": tx["threshold_family"],
                "expected_send_fraction": tx["expected_send_fraction"],
                "expected_send_rows": tx["expected_send_rows"],
                "startup_offset_ms": startup_offsets_ms[tx_id],
                "startup_offset_source": (
                    "carried forward from Run 034"
                    if tx_id in BASE_STARTUP_OFFSETS_MS
                    else "selected by Run 035 deterministic offset search"
                ),
            }
        )
    return rows


def update_manifest(
    manifest: dict[str, Any],
    *,
    startup_offsets_ms: dict[str, int],
    selection_trace: list[dict[str, Any]],
    exact_count: int,
    near_count: int,
    total_send_events: int,
    min_pairwise_delta_ms: int | None,
) -> dict[str, Any]:
    for tx in manifest["transmitters"]:
        tx_id = tx["tx_id"]
        tx["startup_offset_ms"] = startup_offsets_ms[tx_id]
        tx["startup_offset_status"] = (
            "assigned by v5.14-run035-twelve-transmitter-phase-plan"
        )

    manifest["phase_plan_status"] = (
        "assigned by v5.14-run035-twelve-transmitter-phase-plan; "
        "exact and near scheduled SEND coincidence checks written to outputs"
    )

    manifest["phase_plan"] = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "slot_interval_ms": SLOT_INTERVAL_MS,
        "near_coincidence_window_ms": NEAR_COINCIDENCE_WINDOW_MS,
        "total_scheduled_send_events": total_send_events,
        "startup_offsets_ms": {
            tx_id: startup_offsets_ms[tx_id]
            for tx_id in sorted(startup_offsets_ms)
        },
        "selection_trace": selection_trace,
        "exact_same_ms_scheduled_send_coincidences": exact_count,
        "near_scheduled_send_coincidences": near_count,
        "minimum_pairwise_scheduled_send_separation_ms": min_pairwise_delta_ms,
        "outputs": {
            "phase_plan_csv": str(PHASE_PLAN_CSV),
            "summary_json": str(SUMMARY_JSON),
            "exact_coincidences_csv": str(EXACT_CSV),
            "near_coincidences_csv": str(NEAR_CSV),
            "pairwise_min_deltas_csv": str(PAIRWISE_MIN_CSV),
        },
        "claims": {
            "phase_plan_computed": True,
            "physical_prep_performed": False,
            "physical_replay_performed": False,
            "rf_collision_mechanisms_inferred": False,
        },
    }

    if "validation" in manifest and isinstance(manifest["validation"], dict):
        claims = manifest["validation"].setdefault("claims", {})
        claims["phase_plan_computed"] = True
        claims["physical_prep_performed"] = False
        claims["physical_replay_performed"] = False
        manifest["validation"]["all_startup_offsets_deferred"] = False

    return manifest


def main() -> None:
    manifest = read_json(MANIFEST)
    validate_manifest_shape(manifest)

    startup_offsets_ms, selection_trace = select_offsets(manifest)
    events = build_events(manifest, startup_offsets_ms)
    exact_rows = exact_coincidences(events)
    near_rows = near_coincidences(
        events,
        window_ms=NEAR_COINCIDENCE_WINDOW_MS,
    )
    pairwise_rows = pairwise_min_deltas(events)

    exact_count = len(exact_rows)
    near_count = len(near_rows)
    min_pairwise_delta_ms = (
        int(pairwise_rows[0]["min_delta_ms"]) if pairwise_rows else None
    )

    if exact_count != 0:
        raise SystemExit(f"Exact same-ms scheduled SEND coincidences found: {exact_count}")

    if near_count != 0:
        raise SystemExit(
            f"Near scheduled SEND coincidences within "
            f"{NEAR_COINCIDENCE_WINDOW_MS} ms found: {near_count}"
        )

    write_csv(PHASE_PLAN_CSV, PHASE_PLAN_COLUMNS, phase_plan_rows(manifest, startup_offsets_ms))
    write_csv(EXACT_CSV, EXACT_COLUMNS, exact_rows)
    write_csv(NEAR_CSV, NEAR_COLUMNS, near_rows)
    write_csv(PAIRWISE_MIN_CSV, PAIRWISE_MIN_COLUMNS, pairwise_rows)

    summary = {
        "run_id": RUN_ID,
        "milestone": MILESTONE,
        "manifest": str(MANIFEST),
        "slot_interval_ms": SLOT_INTERVAL_MS,
        "near_coincidence_window_ms": NEAR_COINCIDENCE_WINDOW_MS,
        "offset_search": {
            "search_tx_order": SEARCH_TX_ORDER,
            "offset_search_min_ms": OFFSET_SEARCH_MIN_MS,
            "offset_search_max_ms": OFFSET_SEARCH_MAX_MS,
            "offset_search_step_ms": OFFSET_SEARCH_STEP_MS,
            "base_startup_offsets_ms": {
                tx_id: BASE_STARTUP_OFFSETS_MS[tx_id]
                for tx_id in sorted(BASE_STARTUP_OFFSETS_MS)
            },
            "selection_trace": selection_trace,
        },
        "startup_offsets_ms": {
            tx_id: startup_offsets_ms[tx_id]
            for tx_id in sorted(startup_offsets_ms)
        },
        "transmitter_count": len(manifest["transmitters"]),
        "total_scheduled_send_events": len(events),
        "exact_same_ms_scheduled_send_coincidences": exact_count,
        "near_scheduled_send_coincidences": near_count,
        "minimum_pairwise_scheduled_send_separation_ms": min_pairwise_delta_ms,
        "smallest_pairwise_separations": pairwise_rows[:12],
        "outputs": {
            "phase_plan_csv": str(PHASE_PLAN_CSV),
            "summary_json": str(SUMMARY_JSON),
            "exact_coincidences_csv": str(EXACT_CSV),
            "near_coincidences_csv": str(NEAR_CSV),
            "pairwise_min_deltas_csv": str(PAIRWISE_MIN_CSV),
        },
        "claims": {
            "phase_plan_only": True,
            "physical_prep_performed": False,
            "physical_replay_performed": False,
            "exact_transmitted_packet_counts_established": False,
            "rf_collision_mechanisms_inferred": False,
            "absence_of_collisions_established": False,
        },
    }

    write_json(SUMMARY_JSON, summary)

    updated_manifest = update_manifest(
        manifest,
        startup_offsets_ms=startup_offsets_ms,
        selection_trace=selection_trace,
        exact_count=exact_count,
        near_count=near_count,
        total_send_events=len(events),
        min_pairwise_delta_ms=min_pairwise_delta_ms,
    )
    write_json(MANIFEST, updated_manifest)

    print(f"Wrote {PHASE_PLAN_CSV}")
    print(f"Wrote {SUMMARY_JSON}")
    print(f"Wrote {EXACT_CSV}")
    print(f"Wrote {NEAR_CSV}")
    print(f"Wrote {PAIRWISE_MIN_CSV}")
    print(f"Updated {MANIFEST}")
    print()
    print("Assigned startup offsets:")
    for tx in updated_manifest["transmitters"]:
        print(f"{tx['tx_id']}/{tx['node_id']}: {tx['startup_offset_ms']} ms")
    print()
    print(f"Total scheduled SEND events: {len(events)}")
    print(f"Exact same-ms scheduled SEND coincidences: {exact_count}")
    print(f"Near scheduled SEND coincidences <= {NEAR_COINCIDENCE_WINDOW_MS} ms: {near_count}")
    print(f"Minimum pairwise scheduled SEND separation: {min_pairwise_delta_ms} ms")
    print()
    for item in selection_trace:
        print(
            f"{item['tx_id']}/{item['node_id']} selected offset "
            f"{item['selected_offset_ms']} ms "
            f"(min delta vs prior plan: {item['min_delta_ms_against_prior_plan']} ms; "
            f"valid candidates: {item['valid_candidate_count']})"
        )


if __name__ == "__main__":
    main()
