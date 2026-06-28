#!/usr/bin/env python3
"""
Manifest-bound wrapper for schedule-aware replay analysis.

This script reads a run manifest and invokes the existing
scripts/analyze_scheduled_replay.py command with the paths and labels
recorded in that manifest.

It intentionally does not duplicate the schedule-aware analysis logic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not isinstance(manifest, dict):
        raise ValueError("Manifest root must be a JSON object.")

    return manifest


def require_path(manifest: dict[str, Any], dotted_key: str) -> str:
    current: Any = manifest
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Manifest is missing required key: {dotted_key}")
        current = current[part]

    if not isinstance(current, str) or not current:
        raise ValueError(f"Manifest key must be a non-empty string: {dotted_key}")

    return current


def optional_path(manifest: dict[str, Any], dotted_key: str) -> str | None:
    current: Any = manifest
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]

    if current is None:
        return None

    if not isinstance(current, str):
        raise ValueError(f"Manifest key must be a string if present: {dotted_key}")

    return current


def validate_input_file(path_str: str, label: str) -> None:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def build_command(manifest: dict[str, Any]) -> list[str]:
    schedule_a = require_path(manifest, "transmitters.a.schedule_csv")
    schedule_b = require_path(manifest, "transmitters.b.schedule_csv")
    parsed = require_path(manifest, "receiver_logs.parsed_valid")
    out_json = require_path(manifest, "outputs.summary_json")
    out_csv = require_path(manifest, "outputs.summary_csv")

    tx_a = require_path(manifest, "transmitters.a.tx_id")
    tx_b = require_path(manifest, "transmitters.b.tx_id")
    node_a = optional_path(manifest, "transmitters.a.node_id")
    node_b = optional_path(manifest, "transmitters.b.node_id")

    validate_input_file(schedule_a, "schedule A CSV")
    validate_input_file(schedule_b, "schedule B CSV")
    validate_input_file(parsed, "parsed receiver CSV")

    cmd = [
        sys.executable,
        "scripts/analyze_scheduled_replay.py",
        "--schedule-a",
        schedule_a,
        "--schedule-b",
        schedule_b,
        "--parsed",
        parsed,
        "--out-json",
        out_json,
        "--out-csv",
        out_csv,
        "--tx-a-label",
        tx_a,
        "--tx-b-label",
        tx_b,
    ]

    if node_a:
        cmd.extend(["--node-a-label", node_a])

    if node_b:
        cmd.extend(["--node-b-label", node_b])

    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run schedule-aware replay analysis from a manifest."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to schedule-aware replay analysis manifest JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the analyzer command without running it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = read_manifest(args.manifest)
    cmd = build_command(manifest)

    print(f"Manifest: {args.manifest}")
    print("Analyzer command:")
    print(" ".join(cmd))

    if args.dry_run:
        return

    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
