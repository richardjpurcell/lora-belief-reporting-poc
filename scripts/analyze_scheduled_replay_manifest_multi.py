#!/usr/bin/env python3
"""
Manifest-bound multi-transmitter schedule-aware replay analysis.

This script combines:
  1. a run manifest with a list-valued `transmitters` field;
  2. per-transmitter reporting schedules with SEND/SKIP rows; and
  3. a parsed receiver log containing valid received packets.

It is intended for Run 030 and later N-transmitter SD replay runs.

Interpretation boundary:
  Schedule CSVs define one repeated schedule period that firmware may loop over.
  This script compares scheduled SEND proportions with observed receiver-side
  packet proportions. It does not infer exact transmitted-packet counts,
  confirmed collisions, synchronized latency, LoRaWAN behavior, airtime
  optimization, energy savings, or live controller behavior.
"""

from __future__ import annotations

import argparse
import json
from itertools import permutations
from pathlib import Path
from typing import Any

import pandas as pd


def norm_col(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [norm_col(c) for c in out.columns]
    return out


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8") as handle:
        obj = json.load(handle)

    if not isinstance(obj, dict):
        raise ValueError("JSON root must be an object.")

    return obj


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def optional_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    return first_existing(list(df.columns), candidates)


def require_col(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    col = optional_col(df, candidates)
    if col is None:
        raise ValueError(
            f"Could not find {label} column. Tried {candidates}. "
            f"Available columns: {list(df.columns)}"
        )
    return col


def infer_action_series(df: pd.DataFrame) -> pd.Series:
    explicit = optional_col(
        df,
        [
            "action",
            "decision",
            "report_action",
            "reporting_action",
            "schedule_action",
            "send_skip",
            "policy_action",
        ],
    )
    if explicit is not None:
        return df[explicit].astype(str).str.strip().str.upper()

    boolean_col = optional_col(
        df,
        ["should_send", "send", "is_send", "transmit", "scheduled_send"],
    )
    if boolean_col is not None:
        truthy = {"1", "true", "t", "yes", "y", "send"}
        return df[boolean_col].astype(str).str.strip().str.lower().map(
            lambda value: "SEND" if value in truthy else "SKIP"
        )

    raise ValueError(
        "Could not infer schedule SEND/SKIP action column. "
        f"Available columns: {list(df.columns)}"
    )


def safe_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def seq_set(series: pd.Series) -> set[int]:
    numeric = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    return set(numeric.tolist())


def missing_in_range(observed: set[int]) -> list[int]:
    if not observed:
        return []
    low = min(observed)
    high = max(observed)
    return [value for value in range(low, high + 1) if value not in observed]


def mean_interarrival_ms(df: pd.DataFrame, recv_col: str | None) -> float | None:
    if recv_col is None or df.empty:
        return None
    recv = pd.to_numeric(df[recv_col], errors="coerce").dropna().sort_values()
    if len(recv) < 2:
        return None
    return float(recv.diff().dropna().mean())


def load_transmitters(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    transmitters = manifest.get("transmitters")
    if not isinstance(transmitters, list) or not transmitters:
        raise ValueError("Manifest must contain a non-empty list field: transmitters")

    out: list[dict[str, Any]] = []
    for index, tx in enumerate(transmitters):
        if not isinstance(tx, dict):
            raise ValueError(f"transmitters[{index}] is not an object")

        tx_id = tx.get("tx_id")
        schedule_csv = tx.get("schedule_csv")

        if not isinstance(tx_id, str) or not tx_id:
            raise ValueError(f"transmitters[{index}] missing non-empty tx_id")
        if not isinstance(schedule_csv, str) or not schedule_csv:
            raise ValueError(f"transmitters[{index}] missing non-empty schedule_csv")

        out.append(tx)

    return out


def summarize_schedule(tx: dict[str, Any]) -> dict[str, Any]:
    schedule_path = Path(str(tx["schedule_csv"]))
    if not schedule_path.exists():
        raise FileNotFoundError(f"Schedule CSV not found for {tx['tx_id']}: {schedule_path}")

    df = normalise_columns(pd.read_csv(schedule_path))
    action = infer_action_series(df)
    send_mask = action.eq("SEND")
    skip_mask = action.eq("SKIP")

    usefulness_col = optional_col(
        df,
        [
            "usefulness",
            "useful",
            "utility",
            "belief_usefulness",
            "scheduled_usefulness",
        ],
    )

    if usefulness_col is not None:
        usefulness = pd.to_numeric(df[usefulness_col], errors="coerce")
        send_usefulness = usefulness[send_mask]
        scheduled_send_usefulness_total = float(send_usefulness.sum())
        scheduled_send_usefulness_mean = safe_float(send_usefulness.mean())
    else:
        scheduled_send_usefulness_total = None
        scheduled_send_usefulness_mean = None

    demand_rows = int(len(df))
    send_rows = int(send_mask.sum())
    skip_rows = int(skip_mask.sum())

    return {
        "tx_id": tx["tx_id"],
        "node_id": tx.get("node_id"),
        "role": tx.get("role"),
        "policy": tx.get("policy"),
        "policy_code": tx.get("policy_code"),
        "threshold_family": tx.get("threshold_family"),
        "schedule_csv": str(schedule_path),
        "demand_rows": demand_rows,
        "scheduled_send_rows": send_rows,
        "scheduled_skip_rows": skip_rows,
        "send_fraction": float(send_rows / demand_rows) if demand_rows else None,
        "expected_rows_manifest": tx.get("expected_rows"),
        "expected_send_rows_manifest": tx.get("expected_send_rows"),
        "expected_skip_rows_manifest": tx.get("expected_skip_rows"),
        "scheduled_send_usefulness_total": scheduled_send_usefulness_total,
        "scheduled_send_usefulness_mean": scheduled_send_usefulness_mean,
        "usefulness_column": usefulness_col,
    }


def summarize_receiver(
    parsed_df: pd.DataFrame,
    tx_id: str,
    node_id: str | None,
) -> dict[str, Any]:
    tx_col = require_col(
        parsed_df,
        ["tx_id", "tx", "transmitter", "transmitter_id"],
        "parsed tx_id",
    )
    node_col = optional_col(parsed_df, ["node_id", "node", "nodeid"])
    seq_col = require_col(
        parsed_df,
        ["seq", "sequence", "sequence_number"],
        "parsed sequence",
    )
    recv_col = optional_col(parsed_df, ["recv_ms", "receiver_ms", "rx_ms"])

    usefulness_col = optional_col(
        parsed_df,
        [
            "usefulness",
            "useful",
            "utility",
            "belief_usefulness",
            "delivered_usefulness",
        ],
    )
    priority_col = optional_col(parsed_df, ["priority", "prio"])

    subset = parsed_df[parsed_df[tx_col].astype(str).eq(str(tx_id))].copy()
    if node_id is not None and node_col is not None:
        subset = subset[subset[node_col].astype(str).eq(str(node_id))].copy()

    observed = seq_set(subset[seq_col])
    missing = missing_in_range(observed)

    if usefulness_col is not None and not subset.empty:
        usefulness = pd.to_numeric(subset[usefulness_col], errors="coerce")
        delivered_usefulness_total = float(usefulness.sum())
        delivered_usefulness_mean = safe_float(usefulness.mean())
    else:
        delivered_usefulness_total = None
        delivered_usefulness_mean = None

    if priority_col is not None and not subset.empty:
        priority = pd.to_numeric(subset[priority_col], errors="coerce")
        delivered_priority_total = float(priority.sum())
        delivered_priority_mean = safe_float(priority.mean())
    else:
        delivered_priority_total = None
        delivered_priority_mean = None

    return {
        "received_valid_packets": int(len(subset)),
        "observed_sequence_min": min(observed) if observed else None,
        "observed_sequence_max": max(observed) if observed else None,
        "observed_missing_transmitted_sequences": missing,
        "observed_missing_transmitted_sequence_count": int(len(missing)),
        "delivered_usefulness_total": delivered_usefulness_total,
        "delivered_usefulness_mean_per_received_packet": delivered_usefulness_mean,
        "delivered_priority_total": delivered_priority_total,
        "delivered_priority_mean_per_received_packet": delivered_priority_mean,
        "mean_receiver_interarrival_ms": mean_interarrival_ms(subset, recv_col),
    }


def combine_summary(schedule: dict[str, Any], receiver: dict[str, Any]) -> dict[str, Any]:
    send_rows = schedule["scheduled_send_rows"]
    demand_rows = schedule["demand_rows"]
    packets = receiver["received_valid_packets"]
    delivered_total = receiver["delivered_usefulness_total"]

    return {
        **schedule,
        **receiver,
        "received_packets_per_scheduled_send_row": (
            float(packets / send_rows) if send_rows else None
        ),
        "received_packets_per_scheduled_demand_row": (
            float(packets / demand_rows) if demand_rows else None
        ),
        "delivered_usefulness_per_scheduled_send_row": (
            float(delivered_total / send_rows)
            if delivered_total is not None and send_rows
            else None
        ),
        "delivered_usefulness_per_scheduled_demand_row": (
            float(delivered_total / demand_rows)
            if delivered_total is not None and demand_rows
            else None
        ),
    }


def compute_observed_ratios(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    by_tx = {str(row["tx_id"]): row for row in rows}
    ratios: dict[str, float | None] = {}

    for numerator, denominator in permutations(by_tx.keys(), 2):
        n_packets = by_tx[numerator]["received_valid_packets"]
        d_packets = by_tx[denominator]["received_valid_packets"]
        key = f"{numerator}/{denominator}"
        ratios[key] = float(n_packets / d_packets) if d_packets else None

    return ratios


def compare_expected_ratios(
    expected: dict[str, Any],
    observed: dict[str, float | None],
) -> dict[str, dict[str, float | None]]:
    comparisons: dict[str, dict[str, float | None]] = {}

    for key, expected_value in expected.items():
        observed_value = observed.get(key)
        try:
            expected_float = float(expected_value)
        except Exception:
            expected_float = None

        if observed_value is not None and expected_float is not None:
            difference = float(observed_value - expected_float)
        else:
            difference = None

        comparisons[key] = {
            "scheduled_expected_ratio": expected_float,
            "observed_received_packet_ratio": observed_value,
            "observed_minus_expected": difference,
        }

    return comparisons


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)

    # Keep list-valued columns CSV-friendly.
    for col in df.columns:
        df[col] = df[col].map(
            lambda value: json.dumps(value) if isinstance(value, list) else value
        )

    df.to_csv(path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze scheduled replay from a list-valued transmitter manifest."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--parsed", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    manifest = read_json(args.manifest)
    transmitters = load_transmitters(manifest)

    if not args.parsed.exists():
        raise FileNotFoundError(args.parsed)

    parsed_df = normalise_columns(pd.read_csv(args.parsed))

    per_transmitter: list[dict[str, Any]] = []
    for tx in transmitters:
        schedule_summary = summarize_schedule(tx)
        receiver_summary = summarize_receiver(
            parsed_df,
            tx_id=str(tx["tx_id"]),
            node_id=tx.get("node_id"),
        )
        per_transmitter.append(combine_summary(schedule_summary, receiver_summary))

    observed_ratios = compute_observed_ratios(per_transmitter)
    expected_ratios = manifest.get("expected_scheduled_ratios", {})
    if not isinstance(expected_ratios, dict):
        expected_ratios = {}

    ratio_comparisons = compare_expected_ratios(expected_ratios, observed_ratios)

    result = {
        "run_id": manifest.get("run_id"),
        "milestone": manifest.get("milestone"),
        "manifest": str(args.manifest),
        "parsed_receiver_csv": str(args.parsed),
        "per_transmitter": per_transmitter,
        "expected_scheduled_ratios": expected_ratios,
        "observed_received_packet_ratios": observed_ratios,
        "ratio_comparisons": ratio_comparisons,
        "interpretation_boundary": [
            "Schedule CSVs define one repeated schedule period.",
            "Observed packet ratios are receiver-side proportions.",
            "This analysis does not infer exact transmitted-packet counts.",
            "Missing sequence numbers are observed sequence gaps only, not confirmed collisions.",
            "recv_ms and tx_ms are not synchronized across boards and are not true latency.",
            "Usefulness and priority are synthetic metadata.",
            "This is point-to-point LoRa, not LoRaWAN.",
            "This is not an energy, airtime-optimization, scaling, live-controller, or operational wildfire result.",
        ],
    }

    write_json(args.out_json, result)
    write_csv(args.out_csv, per_transmitter)

    print(f"Wrote JSON summary: {args.out_json}")
    print(f"Wrote CSV summary:  {args.out_csv}")
    print()
    print("Per-transmitter received packet counts:")
    for row in per_transmitter:
        print(
            f"  {row['tx_id']}/{row.get('node_id')}: "
            f"{row['received_valid_packets']} received, "
            f"{row['scheduled_send_rows']}/{row['demand_rows']} scheduled SEND"
        )

    if ratio_comparisons:
        print()
        print("Expected-vs-observed ratios:")
        for key, row in ratio_comparisons.items():
            print(
                f"  {key}: observed={row['observed_received_packet_ratio']:.4f}, "
                f"expected={row['scheduled_expected_ratio']:.4f}, "
                f"diff={row['observed_minus_expected']:.4f}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
