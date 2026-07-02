#!/usr/bin/env python3
"""Analyze transmitter startup phase plans.

This script is a design diagnostic for SD-backed point-to-point LoRa replay
experiments. It reports phase groupings and repeated SEND/SEND phase alignments
under a simplified schedule-class model.

It does not estimate collision probability.
It does not infer exact transmitted-packet counts.
It does not establish synchronized latency.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


PERIOD_BY_FRACTION = {
    1.0: 1000,
    0.5: 2000,
    0.25: 4000,
    0.125: 8000,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze startup phases for a multi-transmitter replay plan."
    )
    parser.add_argument("--phase-plan", required=True, help="Input phase-plan CSV.")
    parser.add_argument("--out-json", required=True, help="Output JSON summary.")
    parser.add_argument("--out-csv", required=True, help="Output per-transmitter CSV summary.")
    parser.add_argument("--slot-ms", type=int, default=1000, help="Slot interval in ms. Default: 1000.")
    parser.add_argument("--superframe-ms", type=int, default=8000, help="Diagnostic superframe in ms. Default: 8000.")
    parser.add_argument(
        "--residue-windows-ms",
        default="1000,2000,4000,8000",
        help="Comma-separated residue windows in ms. Default: 1000,2000,4000,8000.",
    )
    parser.add_argument(
        "--co-phase-tolerance-ms",
        type=int,
        default=75,
        help="Tolerance for reporting repeated SEND/SEND co-phase opportunities. Default: 75.",
    )
    return parser.parse_args()


def read_phase_plan(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    required = {
        "tx_id",
        "node_id",
        "role",
        "policy",
        "threshold_family",
        "startup_offset_ms",
        "expected_send_fraction",
    }
    if not rows:
        raise SystemExit(f"Phase plan has no rows: {path}")

    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(f"Phase plan missing required columns: {sorted(missing)}")

    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["startup_offset_ms"] = int(float(item["startup_offset_ms"]))
        item["expected_send_fraction"] = float(item["expected_send_fraction"])
        item["tx_node"] = f"{item['tx_id']}/{item['node_id']}"
        frac = item["expected_send_fraction"]
        if frac not in PERIOD_BY_FRACTION:
            raise SystemExit(
                f"Unsupported expected_send_fraction for {item['tx_node']}: {frac}. "
                f"Supported: {sorted(PERIOD_BY_FRACTION)}"
            )
        item["modeled_send_period_ms"] = PERIOD_BY_FRACTION[frac]
        out.append(item)

    tx_ids = [r["tx_id"] for r in out]
    node_ids = [r["node_id"] for r in out]
    if len(tx_ids) != len(set(tx_ids)):
        raise SystemExit("Duplicate tx_id values in phase plan.")
    if len(node_ids) != len(set(node_ids)):
        raise SystemExit("Duplicate node_id values in phase plan.")

    return out


def circular_distance_ms(a: int, b: int, modulo: int) -> int:
    d = abs((a - b) % modulo)
    return min(d, modulo - d)


def modeled_send_times(row: dict[str, Any], superframe_ms: int) -> list[int]:
    offset = row["startup_offset_ms"] % superframe_ms
    period = row["modeled_send_period_ms"]

    times: list[int] = []
    t = offset
    seen = set()
    # The modeled periods divide the default 8000 ms superframe. Keep this robust
    # in case a later superframe is used.
    while t not in seen:
        seen.add(t)
        times.append(t)
        t = (t + period) % superframe_ms
        if len(times) > 10_000:
            raise SystemExit(f"Unexpected send-time cycle for {row['tx_node']}")
    return sorted(times)


def main() -> None:
    args = parse_args()

    phase_plan = Path(args.phase_plan)
    out_json = Path(args.out_json)
    out_csv = Path(args.out_csv)

    residue_windows = [
        int(x.strip())
        for x in args.residue_windows_ms.split(",")
        if x.strip()
    ]

    rows = read_phase_plan(phase_plan)

    per_tx: list[dict[str, Any]] = []
    residue_groups: dict[str, dict[str, list[str]]] = {}

    for window in residue_windows:
        groups: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            residue = row["startup_offset_ms"] % window
            groups[str(residue)].append(row["tx_node"])
        residue_groups[str(window)] = dict(sorted(groups.items(), key=lambda kv: int(kv[0])))

    fixed_all = [
        row for row in rows
        if row["expected_send_fraction"] == 1.0 or row["policy"] == "fixed_all"
    ]

    modeled_times_by_tx = {
        row["tx_node"]: modeled_send_times(row, args.superframe_ms)
        for row in rows
    }

    for row in rows:
        tx_node = row["tx_node"]
        item = {
            "tx_node": tx_node,
            "tx_id": row["tx_id"],
            "node_id": row["node_id"],
            "role": row["role"],
            "policy": row["policy"],
            "threshold_family": row["threshold_family"],
            "startup_offset_ms": row["startup_offset_ms"],
            "expected_send_fraction": row["expected_send_fraction"],
            "modeled_send_period_ms": row["modeled_send_period_ms"],
            "modeled_send_times_ms": modeled_times_by_tx[tx_node],
        }

        for window in residue_windows:
            item[f"offset_mod_{window}_ms"] = row["startup_offset_ms"] % window

        fixed_alignment = []
        for fixed in fixed_all:
            if fixed["tx_node"] == tx_node:
                continue
            dist = circular_distance_ms(
                row["startup_offset_ms"] % args.slot_ms,
                fixed["startup_offset_ms"] % args.slot_ms,
                args.slot_ms,
            )
            if dist <= args.co_phase_tolerance_ms:
                fixed_alignment.append(
                    {
                        "fixed_anchor": fixed["tx_node"],
                        "modulo_ms": args.slot_ms,
                        "phase_distance_ms": dist,
                    }
                )
        item["fixed_anchor_mod_slot_alignment_flags"] = fixed_alignment

        per_tx.append(item)

    pairwise: list[dict[str, Any]] = []
    repeated_alignments: list[dict[str, Any]] = []

    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            left_node = left["tx_node"]
            right_node = right["tx_node"]

            diffs = {
                f"phase_distance_mod_{window}_ms": circular_distance_ms(
                    left["startup_offset_ms"] % window,
                    right["startup_offset_ms"] % window,
                    window,
                )
                for window in residue_windows
            }

            pair_item = {
                "left": left_node,
                "right": right_node,
                "left_offset_ms": left["startup_offset_ms"],
                "right_offset_ms": right["startup_offset_ms"],
                **diffs,
            }
            pairwise.append(pair_item)

            left_times = modeled_times_by_tx[left_node]
            right_times = modeled_times_by_tx[right_node]

            close_events = []
            for lt in left_times:
                for rt in right_times:
                    dist = circular_distance_ms(lt, rt, args.superframe_ms)
                    if dist <= args.co_phase_tolerance_ms:
                        close_events.append(
                            {
                                "left_time_ms": lt,
                                "right_time_ms": rt,
                                "distance_ms": dist,
                            }
                        )

            if close_events:
                repeated_alignments.append(
                    {
                        "left": left_node,
                        "right": right_node,
                        "left_expected_send_fraction": left["expected_send_fraction"],
                        "right_expected_send_fraction": right["expected_send_fraction"],
                        "close_event_count": len(close_events),
                        "close_events": close_events,
                    }
                )

    risk_flags: list[dict[str, Any]] = []

    for item in per_tx:
        if item["fixed_anchor_mod_slot_alignment_flags"]:
            risk_flags.append(
                {
                    "severity": "moderate",
                    "tx_node": item["tx_node"],
                    "flag": "shares modulo-slot phase with fixed-all anchor",
                    "details": item["fixed_anchor_mod_slot_alignment_flags"],
                }
            )

    for event in repeated_alignments:
        left_frac = event["left_expected_send_fraction"]
        right_frac = event["right_expected_send_fraction"]
        if left_frac == 1.0 or right_frac == 1.0:
            severity = "moderate"
        elif left_frac <= 0.25 or right_frac <= 0.25:
            severity = "needs physical validation"
        else:
            severity = "low"
        risk_flags.append(
            {
                "severity": severity,
                "tx_node": f"{event['left']} <-> {event['right']}",
                "flag": "modeled repeated SEND/SEND co-phase opportunity",
                "details": {
                    "close_event_count": event["close_event_count"],
                    "tolerance_ms": args.co_phase_tolerance_ms,
                },
            }
        )

    summary = {
        "description": (
            "Phase-plan design diagnostic. Results are based on startup offsets "
            "and simplified expected send fractions. This does not prove collisions, "
            "exact transmitted-packet counts, synchronized latency, LoRaWAN behavior, "
            "airtime optimization, or energy savings."
        ),
        "phase_plan": str(phase_plan),
        "slot_ms": args.slot_ms,
        "superframe_ms": args.superframe_ms,
        "residue_windows_ms": residue_windows,
        "co_phase_tolerance_ms": args.co_phase_tolerance_ms,
        "transmitter_count": len(rows),
        "fixed_all_count": len(fixed_all),
        "residue_groups": residue_groups,
        "per_transmitter": per_tx,
        "pairwise_phase_distances": pairwise,
        "repeated_send_send_alignments": repeated_alignments,
        "risk_flags": risk_flags,
    }

    out_json.write_text(json.dumps(summary, indent=2) + "\n")

    with out_csv.open("w", newline="") as f:
        fieldnames = [
            "tx_node",
            "role",
            "policy",
            "threshold_family",
            "startup_offset_ms",
            "expected_send_fraction",
            "modeled_send_period_ms",
            "offset_mod_1000_ms",
            "offset_mod_2000_ms",
            "offset_mod_4000_ms",
            "offset_mod_8000_ms",
            "modeled_send_times_ms",
            "fixed_anchor_mod_slot_alignment_flag_count",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in per_tx:
            writer.writerow(
                {
                    "tx_node": item["tx_node"],
                    "role": item["role"],
                    "policy": item["policy"],
                    "threshold_family": item["threshold_family"],
                    "startup_offset_ms": item["startup_offset_ms"],
                    "expected_send_fraction": item["expected_send_fraction"],
                    "modeled_send_period_ms": item["modeled_send_period_ms"],
                    "offset_mod_1000_ms": item.get("offset_mod_1000_ms"),
                    "offset_mod_2000_ms": item.get("offset_mod_2000_ms"),
                    "offset_mod_4000_ms": item.get("offset_mod_4000_ms"),
                    "offset_mod_8000_ms": item.get("offset_mod_8000_ms"),
                    "modeled_send_times_ms": json.dumps(item["modeled_send_times_ms"]),
                    "fixed_anchor_mod_slot_alignment_flag_count": len(item["fixed_anchor_mod_slot_alignment_flags"]),
                }
            )

    print(f"Wrote JSON summary: {out_json}")
    print(f"Wrote CSV summary:  {out_csv}")
    print()
    print(f"Transmitters: {len(rows)}")
    print(f"Fixed-all anchors: {len(fixed_all)}")
    print(f"Risk flags: {len(risk_flags)}")
    print()
    print("Residue groups modulo 1000 ms:")
    for residue, members in residue_groups.get("1000", {}).items():
        print(f"  {residue} ms: {', '.join(members)}")


if __name__ == "__main__":
    main()
