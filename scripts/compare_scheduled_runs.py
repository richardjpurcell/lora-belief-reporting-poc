#!/usr/bin/env python3
"""
Compare one or more manifest-bound scheduled replay summaries.

This script aggregates existing schedule-aware summary JSON files referenced
by run manifests. It does not re-parse raw receiver logs and does not infer
exact transmitted-packet counts, confirmed collisions, true latency, or
airtime optimization.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dotted_get(obj: dict[str, Any], dotted_key: str) -> Any:
    current: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Missing required key: {dotted_key}")
        current = current[part]
    return current


def optional_dotted_get(obj: dict[str, Any], dotted_key: str) -> Any | None:
    current: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def validate_manifest(manifest_path: Path) -> None:
    cmd = [
        sys.executable,
        "scripts/validate_run_bundle.py",
        "--manifest",
        str(manifest_path),
    ]
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Validation failed for manifest: {manifest_path}")


def tx_metadata(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    transmitters = manifest.get("transmitters", {})
    if not isinstance(transmitters, dict):
        return out

    for _, tx_info in transmitters.items():
        if not isinstance(tx_info, dict):
            continue
        tx_id = tx_info.get("tx_id")
        if not isinstance(tx_id, str):
            continue
        out[tx_id] = {
            "node_id": tx_info.get("node_id"),
            "role": tx_info.get("role"),
            "schedule_csv": tx_info.get("schedule_csv"),
            "schedule_header": tx_info.get("schedule_header"),
        }
    return out


def flatten_manifest_summary(manifest_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest root must be an object: {manifest_path}")

    summary_path = Path(dotted_get(manifest, "outputs.summary_json"))
    summary = read_json(summary_path)
    if not isinstance(summary, dict):
        raise ValueError(f"Summary root must be an object: {summary_path}")

    run_id = dotted_get(manifest, "run_id")
    milestone = manifest.get("milestone")
    analysis_type = manifest.get("analysis_type")
    metadata_by_tx = tx_metadata(manifest)

    per_transmitter = summary.get("per_transmitter")
    if not isinstance(per_transmitter, list):
        raise ValueError(f"Summary missing per_transmitter list: {summary_path}")

    rows: list[dict[str, Any]] = []
    for row in per_transmitter:
        if not isinstance(row, dict):
            raise ValueError(f"Invalid per_transmitter row in {summary_path}")

        tx_id = row.get("tx_id")
        tx_meta = metadata_by_tx.get(str(tx_id), {})

        rows.append(
            {
                "run_id": run_id,
                "manifest": str(manifest_path),
                "milestone": milestone,
                "analysis_type": analysis_type,
                "tx_id": tx_id,
                "node_id": row.get("node_id") or tx_meta.get("node_id"),
                "role": tx_meta.get("role"),
                "schedule_csv": tx_meta.get("schedule_csv"),
                "schedule_header": tx_meta.get("schedule_header"),
                "demand_rows": row.get("demand_rows"),
                "scheduled_send_rows": row.get("scheduled_send_rows"),
                "scheduled_skip_rows": row.get("scheduled_skip_rows"),
                "send_fraction": row.get("send_fraction"),
                "received_valid_packets": row.get("received_valid_packets"),
                "observed_sequence_min": row.get("observed_sequence_min"),
                "observed_sequence_max": row.get("observed_sequence_max"),
                "observed_missing_transmitted_sequence_count": row.get(
                    "observed_missing_transmitted_sequence_count"
                ),
                "delivered_usefulness_total": row.get("delivered_usefulness_total"),
                "delivered_usefulness_mean_per_received_packet": row.get(
                    "delivered_usefulness_mean_per_received_packet"
                ),
                "received_packets_per_scheduled_send_row": row.get(
                    "received_packets_per_scheduled_send_row"
                ),
                "delivered_usefulness_per_scheduled_demand_row": row.get(
                    "delivered_usefulness_per_scheduled_demand_row"
                ),
                "delivered_usefulness_per_scheduled_send_row": row.get(
                    "delivered_usefulness_per_scheduled_send_row"
                ),
                "mean_receiver_interarrival_ms": row.get("mean_receiver_interarrival_ms"),
            }
        )

    comparison = summary.get("comparison", {})
    if not isinstance(comparison, dict):
        comparison = {}

    run_summary = {
        "run_id": run_id,
        "manifest": str(manifest_path),
        "summary_json": str(summary_path),
        "comparison": comparison,
        "interpretation": manifest.get("interpretation"),
        "cautions": manifest.get("cautions", []),
    }

    return rows, run_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare one or more manifest-bound scheduled replay summaries."
    )
    parser.add_argument(
        "--manifest",
        action="append",
        required=True,
        type=Path,
        help="Path to a run manifest JSON. May be supplied multiple times.",
    )
    parser.add_argument(
        "--out-csv",
        required=True,
        type=Path,
        help="Output comparison CSV path.",
    )
    parser.add_argument(
        "--out-json",
        required=True,
        type=Path,
        help="Output comparison JSON path.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate each manifest bundle before comparison.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    all_rows: list[dict[str, Any]] = []
    run_summaries: list[dict[str, Any]] = []

    for manifest_path in args.manifest:
        if args.validate:
            validate_manifest(manifest_path)

        rows, run_summary = flatten_manifest_summary(manifest_path)
        all_rows.extend(rows)
        run_summaries.append(run_summary)

    if not all_rows:
        raise SystemExit("No transmitter rows found.")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(all_rows)
    df.to_csv(args.out_csv, index=False)

    result = {
        "analysis_note": (
            "This comparison aggregates existing manifest-bound scheduled replay "
            "summaries. It does not re-parse raw receiver logs or infer exact "
            "transmitted-packet counts, confirmed collisions, true latency, live "
            "belief-controller behavior, or airtime optimization."
        ),
        "input_manifests": [str(p) for p in args.manifest],
        "run_count": len(run_summaries),
        "transmitter_row_count": len(all_rows),
        "per_transmitter": all_rows,
        "per_run": run_summaries,
    }

    args.out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Wrote comparison CSV:  {args.out_csv}")
    print(f"Wrote comparison JSON: {args.out_json}")
    print(f"Runs summarized: {len(run_summaries)}")
    print(f"Transmitter rows: {len(all_rows)}")

    for row in all_rows:
        node = f"/{row['node_id']}" if row.get("node_id") else ""
        mean_usefulness = row.get("delivered_usefulness_mean_per_received_packet")
        if mean_usefulness is None:
            mean_text = "NA"
        else:
            mean_text = f"{float(mean_usefulness):.3f}"

        print(
            f"{row['run_id']} {row['tx_id']}{node}: "
            f"{row['scheduled_send_rows']}/{row['demand_rows']} SEND rows; "
            f"{row['received_valid_packets']} received packets; "
            f"mean delivered usefulness {mean_text}"
        )


if __name__ == "__main__":
    main()
