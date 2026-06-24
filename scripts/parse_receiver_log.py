#!/usr/bin/env python3
"""
Parse ESP32 LoRa receiver logs.

Input CSV format from receiver_logger.py:

wall_time_utc,serial_port,raw_line
2026-06-22T18:40:09.794+00:00,/dev/cu.usbserial-...,"RX,238068,R0,N01,6,31967,A,1,0.82,0.74,30,U,-25,9.25"

Expected raw_line format:

RX,recv_ms,run_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr

This parser is deliberately tolerant:
- valid packet rows are parsed into columns;
- malformed rows are written to a reject file;
- summary metrics are printed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


EXPECTED_FIELDS = [
    "rx_role",
    "recv_ms",
    "run_id",
    "tx_id",
    "node_id",
    "seq",
    "tx_ms",
    "region",
    "event",
    "priority",
    "usefulness",
    "stale_after",
    "policy",
    "rssi",
    "snr",
]


def parse_raw_line(raw_line: str) -> dict:
    parts = raw_line.split(",")

    if len(parts) != len(EXPECTED_FIELDS):
        return {
            "parse_ok": False,
            "parse_error": f"expected {len(EXPECTED_FIELDS)} fields, got {len(parts)}",
            "raw_line": raw_line,
        }

    row = dict(zip(EXPECTED_FIELDS, parts))
    row["parse_ok"] = True
    row["parse_error"] = ""

    try:
        row["recv_ms"] = int(row["recv_ms"])
        row["seq"] = int(row["seq"])
        row["tx_ms"] = int(row["tx_ms"])
        row["event"] = int(row["event"])
        row["priority"] = float(row["priority"])
        row["usefulness"] = float(row["usefulness"])
        row["stale_after"] = float(row["stale_after"])
        row["rssi"] = float(row["rssi"])
        row["snr"] = float(row["snr"])
    except ValueError as exc:
        return {
            "parse_ok": False,
            "parse_error": f"type conversion error: {exc}",
            "raw_line": raw_line,
        }

    if row["rx_role"] != "RX":
        row["parse_ok"] = False
        row["parse_error"] = "rx_role is not RX"

    return row


def summarize(valid: pd.DataFrame, malformed: pd.DataFrame) -> None:
    print()
    print("=== LoRa receiver log summary ===")
    print(f"Valid packets:      {len(valid)}")
    print(f"Malformed packets:  {len(malformed)}")

    if valid.empty:
        print("No valid packets to summarize.")
        return

    print()
    print("Packets by node:")
    print(valid.groupby("node_id")["seq"].count().to_string())

    print()
    print("Packets by transmitter and node:")
    print(valid.groupby(["tx_id", "node_id"])["seq"].count().to_string())

    print()
    print("Sequence range by node:")
    seq_summary = valid.groupby("node_id")["seq"].agg(["min", "max", "count"])
    print(seq_summary.to_string())

    print()
    print("Missing sequences by transmitter and node:")
    for (tx_id, node_id), group in valid.groupby(["tx_id", "node_id"]):
        seqs = sorted(group["seq"].astype(int).unique())
        if not seqs:
            continue

        expected = set(range(min(seqs), max(seqs) + 1))
        observed = set(seqs)
        missing = sorted(expected - observed)

        label = f"{tx_id}/{node_id}"
        if missing:
            print(f"{label}: missing {len(missing)} -> {missing}")
        else:
            print(f"{label}: none")    

    print()
    print("Radio metadata by node:")
    radio_summary = valid.groupby("node_id").agg(
        mean_rssi=("rssi", "mean"),
        min_rssi=("rssi", "min"),
        max_rssi=("rssi", "max"),
        mean_snr=("snr", "mean"),
        min_snr=("snr", "min"),
        max_snr=("snr", "max"),
    )
    print(radio_summary.round(2).to_string())

    print()
    print("Usefulness by node:")
    useful_summary = valid.groupby("node_id").agg(
        packets=("seq", "count"),
        total_usefulness=("usefulness", "sum"),
        mean_usefulness=("usefulness", "mean"),
        total_priority=("priority", "sum"),
        mean_priority=("priority", "mean"),
    )
    print(useful_summary.round(3).to_string())

    print()
    print("Approximate receiver inter-arrival time by node, seconds:")
    tmp = valid.sort_values(["node_id", "recv_ms"]).copy()
    tmp["interarrival_s"] = tmp.groupby("node_id")["recv_ms"].diff() / 1000.0
    interarrival = tmp.groupby("node_id")["interarrival_s"].agg(["mean", "min", "max"])
    print(interarrival.round(3).to_string())


def summarize_seq_windows(valid: pd.DataFrame, seq_window: int) -> None:
    if seq_window <= 0 or valid.empty:
        return

    tmp = valid.copy()
    tmp["seq_window"] = (tmp["seq"].astype(int) // seq_window) * seq_window

    rows = []

    for (tx_id, node_id, seq_window_start), group in tmp.groupby(
        ["tx_id", "node_id", "seq_window"]
    ):
        seqs = sorted(group["seq"].astype(int).unique())
        expected = set(range(min(seqs), max(seqs) + 1))
        observed = set(seqs)
        missing = sorted(expected - observed)

        sorted_group = group.sort_values("recv_ms").copy()
        interarrival_s = sorted_group["recv_ms"].diff() / 1000.0

        rows.append(
            {
                "tx_id": tx_id,
                "node_id": node_id,
                "seq_window_start": int(seq_window_start),
                "seq_window_end": int(seq_window_start + seq_window - 1),
                "packets": int(group["seq"].count()),
                "seq_min": int(group["seq"].min()),
                "seq_max": int(group["seq"].max()),
                "missing_count": int(len(missing)),
                "total_usefulness": float(group["usefulness"].sum()),
                "mean_usefulness": float(group["usefulness"].mean()),
                "total_priority": float(group["priority"].sum()),
                "mean_priority": float(group["priority"].mean()),
                "mean_rssi": float(group["rssi"].mean()),
                "mean_snr": float(group["snr"].mean()),
                "mean_interarrival_s": float(interarrival_s.mean()),
                "min_interarrival_s": float(interarrival_s.min()),
                "max_interarrival_s": float(interarrival_s.max()),
            }
        )

    summary = pd.DataFrame(rows).sort_values(
        ["tx_id", "node_id", "seq_window_start"]
    )

    print()
    print(f"Usefulness by node and sequence window, window={seq_window}:")
    display_cols = [
        "tx_id",
        "node_id",
        "seq_window_start",
        "seq_window_end",
        "packets",
        "seq_min",
        "seq_max",
        "missing_count",
        "total_usefulness",
        "mean_usefulness",
        "total_priority",
        "mean_priority",
        "mean_rssi",
        "mean_snr",
        "mean_interarrival_s",
    ]
    print(summary[display_cols].round(3).to_string(index=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse ESP32 LoRa receiver CSV logs.")
    parser.add_argument("--infile", required=True, help="Input CSV from receiver_logger.py")
    parser.add_argument("--out", required=True, help="Parsed valid packet CSV")
    parser.add_argument(
        "--rejects",
        default=None,
        help="Malformed/rejected packet CSV. Default: <out> with _rejects suffix.",
    )
    parser.add_argument(
        "--seq-window",
        type=int,
        default=None,
        help="Optional sequence-window size for usefulness summaries, e.g. 50.",
    )
    args = parser.parse_args()

    infile = Path(args.infile)
    out = Path(args.out)
    rejects = Path(args.rejects) if args.rejects else out.with_name(out.stem + "_rejects.csv")

    df = pd.read_csv(infile)

    parsed_rows = []
    reject_rows = []

    for _, input_row in df.iterrows():
        raw_line = str(input_row["raw_line"])
        parsed = parse_raw_line(raw_line)

        if parsed.get("parse_ok"):
            parsed["wall_time_utc"] = input_row["wall_time_utc"]
            parsed["serial_port"] = input_row["serial_port"]
            parsed["raw_line"] = raw_line
            parsed_rows.append(parsed)
        else:
            reject = {
                "wall_time_utc": input_row.get("wall_time_utc", ""),
                "serial_port": input_row.get("serial_port", ""),
                "raw_line": raw_line,
                "parse_error": parsed.get("parse_error", "unknown parse error"),
            }
            reject_rows.append(reject)

    valid = pd.DataFrame(parsed_rows)
    malformed = pd.DataFrame(reject_rows)

    out.parent.mkdir(parents=True, exist_ok=True)
    rejects.parent.mkdir(parents=True, exist_ok=True)

    valid.to_csv(out, index=False)
    malformed.to_csv(rejects, index=False)

    print(f"Wrote valid packets to: {out}")
    print(f"Wrote malformed packets to: {rejects}")

    summarize(valid, malformed)

    if args.seq_window:
        summarize_seq_windows(valid, args.seq_window)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
