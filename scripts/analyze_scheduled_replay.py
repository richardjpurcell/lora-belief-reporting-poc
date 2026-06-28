#!/usr/bin/env python3
"""
Schedule-aware analysis for skipped-slot physical replay runs.

This script combines:
  1. reporting schedules that define SEND/SKIP demand rows; and
  2. parsed receiver logs that contain valid received packets.

The receiver parser remains packet-centric. This analyzer is schedule-aware.

Important interpretation boundary:
  Schedule CSVs usually define one schedule period that firmware loops over.
  Therefore this script compares schedule proportions with observed packet
  proportions. It does not infer exact transmitted packet counts unless that
  information is provided elsewhere.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


TX_A_DEFAULT = "TXA"
TX_B_DEFAULT = "TXB"


def _norm_col(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [_norm_col(c) for c in out.columns]
    return out


def _first_existing(columns: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _require_col(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    col = _first_existing(list(df.columns), candidates)
    if col is None:
        raise ValueError(
            f"Could not find {label} column. Tried {candidates}. "
            f"Available columns: {list(df.columns)}"
        )
    return col


def _optional_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    return _first_existing(list(df.columns), candidates)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return _normalise_columns(pd.read_csv(path))


def _infer_action_series(df: pd.DataFrame) -> pd.Series:
    """
    Return an uppercase SEND/SKIP-like action series.

    Supports explicit schedule columns such as:
      action, decision, report_action, schedule_action, should_send, send
    """
    explicit = _optional_col(
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

    boolean_col = _optional_col(
        df,
        [
            "should_send",
            "send",
            "is_send",
            "transmit",
            "scheduled_send",
        ],
    )
    if boolean_col is not None:
        truthy = {"1", "true", "t", "yes", "y", "send"}
        return df[boolean_col].astype(str).str.strip().str.lower().map(
            lambda v: "SEND" if v in truthy else "SKIP"
        )

    raise ValueError(
        "Could not infer schedule SEND/SKIP action column. "
        f"Available columns: {list(df.columns)}"
    )


def _extract_tx_node_from_schedule(
    df: pd.DataFrame,
    fallback_tx: str,
    fallback_node: str | None,
) -> tuple[str, str | None]:
    tx_col = _optional_col(df, ["tx_id", "tx", "transmitter", "transmitter_id"])
    node_col = _optional_col(df, ["node_id", "node", "nodeid"])

    if tx_col is not None and df[tx_col].notna().any():
        tx_id = str(df[tx_col].dropna().iloc[0])
    else:
        tx_id = fallback_tx

    if node_col is not None and df[node_col].notna().any():
        node_id = str(df[node_col].dropna().iloc[0])
    else:
        node_id = fallback_node

    return tx_id, node_id


def _seq_set(series: pd.Series) -> set[int]:
    numeric = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    return set(numeric.tolist())


def _missing_in_range(observed: set[int]) -> list[int]:
    if not observed:
        return []
    lo = min(observed)
    hi = max(observed)
    return [x for x in range(lo, hi + 1) if x not in observed]


def _mean_interarrival_ms(df: pd.DataFrame, recv_col: str | None) -> float | None:
    if recv_col is None or df.empty:
        return None
    recv = pd.to_numeric(df[recv_col], errors="coerce").dropna().sort_values()
    if len(recv) < 2:
        return None
    return float(recv.diff().dropna().mean())


def _safe_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def _schedule_summary(
    schedule_df: pd.DataFrame,
    fallback_tx: str,
    fallback_node: str | None,
) -> dict[str, Any]:
    tx_id, node_id = _extract_tx_node_from_schedule(
        schedule_df,
        fallback_tx=fallback_tx,
        fallback_node=fallback_node,
    )

    action = _infer_action_series(schedule_df)
    send_mask = action.eq("SEND")
    skip_mask = action.eq("SKIP")

    usefulness_col = _optional_col(
        schedule_df,
        [
            "usefulness",
            "useful",
            "utility",
            "belief_usefulness",
            "scheduled_usefulness",
        ],
    )

    if usefulness_col is not None:
        usefulness = pd.to_numeric(schedule_df[usefulness_col], errors="coerce")
        send_usefulness = usefulness[send_mask]
        scheduled_send_usefulness_total = float(send_usefulness.sum())
        scheduled_send_usefulness_mean = _safe_float(send_usefulness.mean())
    else:
        scheduled_send_usefulness_total = None
        scheduled_send_usefulness_mean = None

    seq_col = _optional_col(schedule_df, ["seq", "sequence", "sequence_number"])

    return {
        "tx_id": tx_id,
        "node_id": node_id,
        "demand_rows": int(len(schedule_df)),
        "scheduled_send_rows": int(send_mask.sum()),
        "scheduled_skip_rows": int(skip_mask.sum()),
        "send_fraction": (
            float(send_mask.sum() / len(schedule_df)) if len(schedule_df) else None
        ),
        "scheduled_send_usefulness_total": scheduled_send_usefulness_total,
        "scheduled_send_usefulness_mean": scheduled_send_usefulness_mean,
        "schedule_sequence_column": seq_col,
        "usefulness_column": usefulness_col,
    }


def _receiver_summary(
    parsed_df: pd.DataFrame,
    tx_id: str,
    node_id: str | None,
) -> dict[str, Any]:
    tx_col = _require_col(parsed_df, ["tx_id", "tx", "transmitter", "transmitter_id"], "parsed tx_id")
    node_col = _optional_col(parsed_df, ["node_id", "node", "nodeid"])
    seq_col = _require_col(parsed_df, ["seq", "sequence", "sequence_number"], "parsed sequence")
    recv_col = _optional_col(parsed_df, ["recv_ms", "receiver_ms", "rx_ms"])

    usefulness_col = _optional_col(
        parsed_df,
        [
            "usefulness",
            "useful",
            "utility",
            "belief_usefulness",
            "delivered_usefulness",
        ],
    )

    subset = parsed_df[parsed_df[tx_col].astype(str).eq(str(tx_id))].copy()

    if node_id is not None and node_col is not None:
        subset = subset[subset[node_col].astype(str).eq(str(node_id))].copy()

    observed_seqs = _seq_set(subset[seq_col])
    missing = _missing_in_range(observed_seqs)

    if usefulness_col is not None and not subset.empty:
        delivered_usefulness = pd.to_numeric(subset[usefulness_col], errors="coerce")
        delivered_total = float(delivered_usefulness.sum())
        delivered_mean = _safe_float(delivered_usefulness.mean())
    else:
        delivered_total = None
        delivered_mean = None

    return {
        "received_valid_packets": int(len(subset)),
        "observed_sequence_min": min(observed_seqs) if observed_seqs else None,
        "observed_sequence_max": max(observed_seqs) if observed_seqs else None,
        "observed_missing_transmitted_sequences": missing,
        "observed_missing_transmitted_sequence_count": int(len(missing)),
        "delivered_usefulness_total": delivered_total,
        "delivered_usefulness_mean_per_received_packet": delivered_mean,
        "mean_receiver_interarrival_ms": _mean_interarrival_ms(subset, recv_col),
        "parsed_sequence_column": seq_col,
        "parsed_usefulness_column": usefulness_col,
        "parsed_receiver_time_column": recv_col,
    }


def _combine_summary(schedule: dict[str, Any], receiver: dict[str, Any]) -> dict[str, Any]:
    demand_rows = schedule["demand_rows"]
    send_rows = schedule["scheduled_send_rows"]
    received = receiver["received_valid_packets"]
    delivered_total = receiver["delivered_usefulness_total"]

    combined = {
        **schedule,
        **receiver,
        "received_packets_per_scheduled_send_row": (
            float(received / send_rows) if send_rows else None
        ),
        "delivered_usefulness_per_scheduled_demand_row": (
            float(delivered_total / demand_rows)
            if delivered_total is not None and demand_rows
            else None
        ),
        "delivered_usefulness_per_scheduled_send_row": (
            float(delivered_total / send_rows)
            if delivered_total is not None and send_rows
            else None
        ),
    }
    return combined


def _comparison(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 2:
        return {}

    a, b = rows[0], rows[1]

    a_send_fraction = a.get("send_fraction")
    b_send_fraction = b.get("send_fraction")
    a_received = a.get("received_valid_packets", 0)
    b_received = b.get("received_valid_packets", 0)

    scheduled_send_fraction_ratio = (
        float(b_send_fraction / a_send_fraction)
        if a_send_fraction not in (None, 0) and b_send_fraction is not None
        else None
    )

    observed_received_packet_ratio = (
        float(b_received / a_received) if a_received else None
    )

    return {
        "baseline_tx_id": a.get("tx_id"),
        "comparison_tx_id": b.get("tx_id"),
        "scheduled_send_fraction_ratio_comparison_over_baseline": scheduled_send_fraction_ratio,
        "observed_received_packet_ratio_comparison_over_baseline": observed_received_packet_ratio,
        "interpretation": (
            "Observed received-packet ratio should be interpreted as a proportion "
            "consistent with scheduled skipping, not as a confirmed transmitted-packet "
            "or collision count."
        ),
    }


def _csv_ready(rows: list[dict[str, Any]]) -> pd.DataFrame:
    flat_rows = []
    for row in rows:
        out = row.copy()
        missing = out.get("observed_missing_transmitted_sequences")
        if isinstance(missing, list):
            out["observed_missing_transmitted_sequences"] = " ".join(map(str, missing))
        flat_rows.append(out)
    return pd.DataFrame(flat_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine reporting schedules with parsed receiver logs."
    )
    parser.add_argument("--schedule-a", required=True, type=Path)
    parser.add_argument("--schedule-b", required=True, type=Path)
    parser.add_argument("--parsed", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--tx-a-label", default=TX_A_DEFAULT)
    parser.add_argument("--tx-b-label", default=TX_B_DEFAULT)
    parser.add_argument("--node-a-label", default=None)
    parser.add_argument("--node-b-label", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    schedule_a = _read_csv(args.schedule_a)
    schedule_b = _read_csv(args.schedule_b)
    parsed = _read_csv(args.parsed)

    schedule_summary_a = _schedule_summary(
        schedule_a,
        fallback_tx=args.tx_a_label,
        fallback_node=args.node_a_label,
    )
    schedule_summary_b = _schedule_summary(
        schedule_b,
        fallback_tx=args.tx_b_label,
        fallback_node=args.node_b_label,
    )

    receiver_summary_a = _receiver_summary(
        parsed,
        tx_id=schedule_summary_a["tx_id"],
        node_id=schedule_summary_a["node_id"],
    )
    receiver_summary_b = _receiver_summary(
        parsed,
        tx_id=schedule_summary_b["tx_id"],
        node_id=schedule_summary_b["node_id"],
    )

    rows = [
        _combine_summary(schedule_summary_a, receiver_summary_a),
        _combine_summary(schedule_summary_b, receiver_summary_b),
    ]

    result = {
        "analysis_note": (
            "Schedule rows define one schedule period that firmware may loop over. "
            "Use schedule fractions and observed packet-count ratios for interpretation. "
            "Do not infer exact transmitted packet counts without explicit run-duration "
            "and schedule-cycle information."
        ),
        "inputs": {
            "schedule_a": str(args.schedule_a),
            "schedule_b": str(args.schedule_b),
            "parsed": str(args.parsed),
        },
        "per_transmitter": rows,
        "comparison": _comparison(rows),
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)

    args.out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _csv_ready(rows).to_csv(args.out_csv, index=False)

    print(f"Wrote JSON summary: {args.out_json}")
    print(f"Wrote CSV summary:  {args.out_csv}")

    for row in rows:
        print(
            f"{row['tx_id']}"
            f"{('/' + row['node_id']) if row.get('node_id') else ''}: "
            f"{row['scheduled_send_rows']}/{row['demand_rows']} schedule rows SEND; "
            f"{row['received_valid_packets']} received packets; "
            f"mean delivered usefulness "
            f"{row['delivered_usefulness_mean_per_received_packet']:.3f}"
        )

    comparison = result["comparison"]
    if comparison:
        print(
            "Observed received-packet ratio "
            f"{comparison['observed_received_packet_ratio_comparison_over_baseline']:.4f}; "
            "scheduled send-fraction ratio "
            f"{comparison['scheduled_send_fraction_ratio_comparison_over_baseline']:.4f}."
        )
        print(
            "Interpretation: received packet ratio is consistent with scheduled "
            "skipping, not proof of exact transmitted-packet or collision counts."
        )


if __name__ == "__main__":
    main()
