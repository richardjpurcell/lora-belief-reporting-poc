#!/usr/bin/env python3
"""
Serial receiver logger for the ESP32 LoRa proof-of-concept.

Reads lines from the RX board over USB serial and writes them to a CSV log.
The RX firmware is expected to print rows like:

RX,487004,R1,TXA,N01,9,47186,A,1,0.82,0.74,30,U,-28,9.25

For now, this script stores:
- local wall-clock time
- serial port
- raw line

Parsing is handled separately.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import serial


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Log serial output from the ESP32 LoRa RX board."
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Serial port, e.g. /dev/cu.usbserial-576B0005451",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Serial baud rate. Default: 115200",
    )
    parser.add_argument(
        "--out",
        "--outfile",
        dest="out",
        required=True,
        help="Output CSV path, e.g. logs/rx_run_001.csv. --outfile is accepted as an alias.",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Opening serial port: {args.port} at {args.baud} baud")
    print(f"Writing log to: {out_path}")
    print("Press Ctrl+C to stop.\n")

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser, out_path.open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "wall_time_utc",
                    "serial_port",
                    "raw_line",
                ],
            )
            writer.writeheader()

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()

                if not line:
                    continue

                row = {
                    "wall_time_utc": utc_now_iso(),
                    "serial_port": args.port,
                    "raw_line": line,
                }

                writer.writerow(row)
                f.flush()

                print(line)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        return 0
    except serial.SerialException as exc:
        print(f"Serial error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
