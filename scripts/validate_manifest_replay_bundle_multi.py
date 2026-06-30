#!/usr/bin/env python3
"""
Validate a manifest-bound N-transmitter scheduled replay analysis bundle.

This validator is intended for Run 030 and later list-valued transmitter
manifests. It checks that the manifest, schedules, parsed receiver CSV, summary
JSON, and summary CSV agree on the bundle structure and scheduled replay
headline values.

It does not infer exact transmitted-packet counts, confirmed collisions,
synchronized latency, LoRaWAN behavior, airtime optimization, energy savings,
live-controller behavior, or operational wildfire behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


TOL = 1e-9


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def norm_col(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [norm_col(c) for c in out.columns]
    return out


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def infer_action_series(df: pd.DataFrame) -> pd.Series:
    explicit = first_existing(
        list(df.columns),
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

    boolean_col = first_existing(
        list(df.columns),
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


def schedule_counts(path: Path) -> dict[str, int]:
    df = normalise_columns(pd.read_csv(path))
    action = infer_action_series(df)
    return {
        "expected_rows": int(len(df)),
        "expected_send_rows": int(action.eq("SEND").sum()),
        "expected_skip_rows": int(action.eq("SKIP").sum()),
    }


def as_number(value: Any) -> float | None:
    try:
        number = float(value)
    except Exception:
        return None
    if not math.isfinite(number):
        return None
    return number


def load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[CheckResult]]:
    results: list[CheckResult] = []
    if not path.exists():
        return None, [CheckResult("manifest exists", False, str(path))]

    results.append(CheckResult("manifest exists", True, str(path)))

    try:
        obj = read_json(path)
    except Exception as exc:
        return None, [*results, CheckResult("manifest is readable JSON", False, str(exc))]

    if not isinstance(obj, dict):
        return None, [*results, CheckResult("manifest root is object", False, type(obj).__name__)]

    results.append(CheckResult("manifest is readable JSON", True, str(path)))
    results.append(CheckResult("manifest root is object", True, "object"))
    return obj, results


def load_summary_json(path: Path) -> tuple[dict[str, Any] | None, list[CheckResult]]:
    results: list[CheckResult] = []
    if not path.exists():
        return None, [CheckResult("summary JSON exists", False, str(path))]

    results.append(CheckResult("summary JSON exists", True, str(path)))

    try:
        obj = read_json(path)
    except Exception as exc:
        return None, [*results, CheckResult("summary JSON is readable", False, str(exc))]

    if not isinstance(obj, dict):
        return None, [*results, CheckResult("summary JSON root is object", False, type(obj).__name__)]

    results.append(CheckResult("summary JSON is readable", True, str(path)))
    results.append(CheckResult("summary JSON root is object", True, "object"))
    return obj, results


def load_csv(path: Path, label: str) -> tuple[pd.DataFrame | None, list[CheckResult]]:
    results: list[CheckResult] = []
    if not path.exists():
        return None, [CheckResult(f"{label} exists", False, str(path))]

    results.append(CheckResult(f"{label} exists", True, str(path)))

    try:
        df = normalise_columns(pd.read_csv(path))
    except Exception as exc:
        return None, [*results, CheckResult(f"{label} is readable CSV", False, str(exc))]

    results.append(
        CheckResult(
            f"{label} is readable CSV",
            True,
            f"rows={len(df)} cols={len(df.columns)}",
        )
    )
    return df, results


def manifest_transmitter_key(tx: dict[str, Any]) -> str:
    return f"{tx.get('tx_id')}/{tx.get('node_id')}"


def validate_transmitters(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[CheckResult]]:
    results: list[CheckResult] = []
    transmitters = manifest.get("transmitters")

    if not isinstance(transmitters, list) or not transmitters:
        return [], [CheckResult("manifest has non-empty list transmitters", False, type(transmitters).__name__)]

    results.append(
        CheckResult(
            "manifest has non-empty list transmitters",
            True,
            f"count={len(transmitters)}",
        )
    )

    required = [
        "tx_id",
        "node_id",
        "schedule_csv",
        "expected_rows",
        "expected_send_rows",
        "expected_skip_rows",
    ]

    valid: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for index, tx in enumerate(transmitters):
        if not isinstance(tx, dict):
            results.append(CheckResult(f"transmitters[{index}] is object", False, type(tx).__name__))
            continue

        results.append(CheckResult(f"transmitters[{index}] is object", True, "object"))

        missing = [key for key in required if key not in tx or tx[key] in (None, "")]
        if missing:
            results.append(
                CheckResult(
                    f"transmitters[{index}] required fields",
                    False,
                    f"missing/empty={missing}",
                )
            )
            continue

        tx_id = str(tx["tx_id"])
        node_id = str(tx["node_id"])
        key = (tx_id, node_id)

        if key in seen:
            results.append(
                CheckResult(
                    f"transmitters[{index}] unique tx_id/node_id",
                    False,
                    f"{tx_id}/{node_id}",
                )
            )
            continue

        seen.add(key)
        results.append(
            CheckResult(
                f"transmitters[{index}] required fields",
                True,
                manifest_transmitter_key(tx),
            )
        )
        results.append(
            CheckResult(
                f"transmitters[{index}] unique tx_id/node_id",
                True,
                manifest_transmitter_key(tx),
            )
        )
        valid.append(tx)

    return valid, results


def validate_schedule_csvs(transmitters: list[dict[str, Any]]) -> list[CheckResult]:
    results: list[CheckResult] = []

    for tx in transmitters:
        label = manifest_transmitter_key(tx)
        schedule_path = Path(str(tx["schedule_csv"]))

        if not schedule_path.exists():
            results.append(CheckResult(f"schedule CSV exists: {label}", False, str(schedule_path)))
            continue

        results.append(CheckResult(f"schedule CSV exists: {label}", True, str(schedule_path)))

        try:
            counts = schedule_counts(schedule_path)
        except Exception as exc:
            results.append(CheckResult(f"schedule CSV counts readable: {label}", False, str(exc)))
            continue

        results.append(
            CheckResult(
                f"schedule CSV counts readable: {label}",
                True,
                str(counts),
            )
        )

        for key in ["expected_rows", "expected_send_rows", "expected_skip_rows"]:
            expected = int(tx[key])
            actual = counts[key]
            results.append(
                CheckResult(
                    f"schedule {key} matches manifest: {label}",
                    actual == expected,
                    f"actual={actual} expected={expected}",
                )
            )

    return results


def summary_json_rows(summary_json: dict[str, Any]) -> tuple[dict[tuple[str, str], dict[str, Any]], list[CheckResult]]:
    results: list[CheckResult] = []
    rows = summary_json.get("per_transmitter")

    if not isinstance(rows, list):
        return {}, [CheckResult("summary JSON has per_transmitter list", False, type(rows).__name__)]

    results.append(CheckResult("summary JSON has per_transmitter list", True, f"count={len(rows)}"))

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            results.append(CheckResult(f"summary JSON per_transmitter[{index}] is object", False, type(row).__name__))
            continue

        tx_id = row.get("tx_id")
        node_id = row.get("node_id")
        if not isinstance(tx_id, str) or not isinstance(node_id, str):
            results.append(
                CheckResult(
                    f"summary JSON per_transmitter[{index}] has tx_id/node_id",
                    False,
                    str(row),
                )
            )
            continue

        key = (tx_id, node_id)
        out[key] = row
        results.append(
            CheckResult(
                f"summary JSON per_transmitter[{index}] has tx_id/node_id",
                True,
                f"{tx_id}/{node_id}",
            )
        )

    return out, results


def summary_csv_rows(summary_csv: pd.DataFrame | None) -> tuple[dict[tuple[str, str], dict[str, Any]], list[CheckResult]]:
    if summary_csv is None:
        return {}, []

    results: list[CheckResult] = []
    required = {"tx_id", "node_id"}
    missing = sorted(required - set(summary_csv.columns))
    if missing:
        return {}, [CheckResult("summary CSV has tx_id/node_id columns", False, f"missing={missing}")]

    results.append(CheckResult("summary CSV has tx_id/node_id columns", True, str(list(summary_csv.columns))))

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in summary_csv.iterrows():
        tx_id = str(row["tx_id"])
        node_id = str(row["node_id"])
        out[(tx_id, node_id)] = row.to_dict()

    results.append(CheckResult("summary CSV row count", True, f"rows={len(out)}"))
    return out, results


def validate_summary_alignment(
    transmitters: list[dict[str, Any]],
    summary_json: dict[str, Any],
    summary_csv: pd.DataFrame | None,
) -> list[CheckResult]:
    results: list[CheckResult] = []

    json_rows, json_results = summary_json_rows(summary_json)
    csv_rows, csv_results = summary_csv_rows(summary_csv)
    results.extend(json_results)
    results.extend(csv_results)

    results.append(
        CheckResult(
            "summary JSON transmitter count matches manifest",
            len(json_rows) == len(transmitters),
            f"summary={len(json_rows)} manifest={len(transmitters)}",
        )
    )

    if summary_csv is not None:
        results.append(
            CheckResult(
                "summary CSV transmitter count matches manifest",
                len(csv_rows) == len(transmitters),
                f"summary={len(csv_rows)} manifest={len(transmitters)}",
            )
        )

    checks = [
        ("demand_rows", "expected_rows"),
        ("scheduled_send_rows", "expected_send_rows"),
        ("scheduled_skip_rows", "expected_skip_rows"),
    ]

    for tx in transmitters:
        key = (str(tx["tx_id"]), str(tx["node_id"]))
        label = f"{key[0]}/{key[1]}"

        results.append(
            CheckResult(
                f"summary JSON has manifest transmitter: {label}",
                key in json_rows,
                label,
            )
        )
        if summary_csv is not None:
            results.append(
                CheckResult(
                    f"summary CSV has manifest transmitter: {label}",
                    key in csv_rows,
                    label,
                )
            )

        if key not in json_rows:
            continue

        json_row = json_rows[key]
        csv_row = csv_rows.get(key)

        for summary_key, manifest_key in checks:
            expected = int(tx[manifest_key])
            actual = int(json_row.get(summary_key, -1))
            results.append(
                CheckResult(
                    f"summary JSON {summary_key} matches manifest: {label}",
                    actual == expected,
                    f"actual={actual} expected={expected}",
                )
            )

            manifest_echo_key = f"{manifest_key}_manifest"
            if manifest_echo_key in json_row:
                echoed = int(json_row.get(manifest_echo_key, -1))
                results.append(
                    CheckResult(
                        f"summary JSON echoes {manifest_key}: {label}",
                        echoed == expected,
                        f"actual={echoed} expected={expected}",
                    )
                )

            if csv_row is not None:
                csv_actual = int(float(csv_row.get(summary_key, -1)))
                results.append(
                    CheckResult(
                        f"summary CSV {summary_key} matches manifest: {label}",
                        csv_actual == expected,
                        f"actual={csv_actual} expected={expected}",
                    )
                )

    return results


def validate_ratio_comparisons(
    manifest: dict[str, Any],
    summary_json: dict[str, Any],
) -> list[CheckResult]:
    results: list[CheckResult] = []
    expected = manifest.get("expected_scheduled_ratios")
    comparisons = summary_json.get("ratio_comparisons")

    if not isinstance(expected, dict) or not expected:
        return [CheckResult("manifest has expected_scheduled_ratios", False, type(expected).__name__)]

    results.append(
        CheckResult(
            "manifest has expected_scheduled_ratios",
            True,
            f"count={len(expected)}",
        )
    )

    if not isinstance(comparisons, dict):
        return [*results, CheckResult("summary JSON has ratio_comparisons", False, type(comparisons).__name__)]

    results.append(
        CheckResult(
            "summary JSON has ratio_comparisons",
            True,
            f"count={len(comparisons)}",
        )
    )

    for label, expected_value in expected.items():
        results.append(
            CheckResult(
                f"ratio comparison exists: {label}",
                label in comparisons,
                label,
            )
        )

        if label not in comparisons:
            continue

        row = comparisons[label]
        if not isinstance(row, dict):
            results.append(CheckResult(f"ratio comparison is object: {label}", False, type(row).__name__))
            continue

        scheduled = as_number(row.get("scheduled_expected_ratio"))
        observed = as_number(row.get("observed_received_packet_ratio"))
        diff = as_number(row.get("observed_minus_expected"))

        results.append(
            CheckResult(
                f"ratio scheduled_expected_ratio numeric: {label}",
                scheduled is not None,
                str(row.get("scheduled_expected_ratio")),
            )
        )
        results.append(
            CheckResult(
                f"ratio observed_received_packet_ratio numeric: {label}",
                observed is not None,
                str(row.get("observed_received_packet_ratio")),
            )
        )
        results.append(
            CheckResult(
                f"ratio observed_minus_expected numeric: {label}",
                diff is not None,
                str(row.get("observed_minus_expected")),
            )
        )

        if scheduled is not None:
            expected_number = as_number(expected_value)
            results.append(
                CheckResult(
                    f"ratio scheduled_expected_ratio matches manifest: {label}",
                    expected_number is not None and abs(scheduled - expected_number) <= TOL,
                    f"actual={scheduled} expected={expected_number}",
                )
            )

    return results


def validate_interpretation_boundary(summary_json: dict[str, Any]) -> list[CheckResult]:
    boundary = summary_json.get("interpretation_boundary")
    if not isinstance(boundary, list) or not boundary:
        return [CheckResult("summary JSON has interpretation_boundary list", False, type(boundary).__name__)]

    joined = " ".join(str(item).lower() for item in boundary)

    required_concepts = {
        "exact transmitted-packet counts": [
            "not infer exact transmitted",
            "does not infer exact transmitted",
            "exact transmitted-packet counts",
            "exact transmitted packet counts",
        ],
        "confirmed collisions": [
            "confirmed collisions",
            "not confirmed collisions",
        ],
        "synchronized latency": [
            "synchronized latency",
            "true latency",
            "not true latency",
            "not synchronized",
        ],
        "LoRaWAN behavior": [
            "lorawan",
            "not lorawan",
        ],
        "energy savings": [
            "energy savings",
            "energy-saving",
            "energy saving",
            "claim energy savings",
            "do not claim energy",
            "not an energy",
            "not energy",
            "power measurements",
            "current measurements",
            "current or power measurements",
        ],
        "live-controller behavior": [
            "live controller",
            "live-controller",
            "live belief-maintenance controller",
            "not yet use a live",
        ],
    }

    results = [
        CheckResult(
            "summary JSON has interpretation_boundary list",
            True,
            f"count={len(boundary)}",
        )
    ]

    for concept, phrases in required_concepts.items():
        matched = [phrase for phrase in phrases if phrase in joined]
        results.append(
            CheckResult(
                f"interpretation boundary covers: {concept}",
                bool(matched),
                f"matched={matched}" if matched else f"tried={phrases}",
            )
        )

    return results


def write_validation_json(path: Path, results: list[CheckResult]) -> None:
    payload = {
        "passed": all(result.passed for result in results),
        "checks_total": len(results),
        "checks_passed": sum(1 for result in results if result.passed),
        "checks_failed": sum(1 for result in results if not result.passed),
        "checks": [
            {
                "name": result.name,
                "passed": result.passed,
                "detail": result.detail,
            }
            for result in results
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def print_results(results: list[CheckResult]) -> None:
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        detail = f" -- {result.detail}" if result.detail else ""
        print(f"{status} {result.name}{detail}")

    total = len(results)
    passed = sum(1 for result in results if result.passed)
    failed = total - passed
    print()
    print(f"Validation summary: {passed}/{total} checks passed; {failed} failed.")


def validate(args: argparse.Namespace) -> list[CheckResult]:
    results: list[CheckResult] = []

    manifest, manifest_results = load_manifest(Path(args.manifest))
    results.extend(manifest_results)
    if manifest is None:
        return results

    transmitters, tx_results = validate_transmitters(manifest)
    results.extend(tx_results)
    results.extend(validate_schedule_csvs(transmitters))

    parsed_df, parsed_results = load_csv(Path(args.parsed), "parsed receiver CSV")
    results.extend(parsed_results)
    if parsed_df is not None:
        results.append(
            CheckResult(
                "parsed receiver CSV has rows",
                len(parsed_df) > 0,
                f"rows={len(parsed_df)}",
            )
        )

    summary_json, summary_json_results = load_summary_json(Path(args.summary_json))
    results.extend(summary_json_results)

    summary_csv, summary_csv_results = load_csv(Path(args.summary_csv), "summary CSV")
    results.extend(summary_csv_results)

    if summary_json is not None:
        results.extend(validate_summary_alignment(transmitters, summary_json, summary_csv))
        results.extend(validate_ratio_comparisons(manifest, summary_json))
        results.extend(validate_interpretation_boundary(summary_json))

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a list-valued N-transmitter manifest replay bundle."
    )
    parser.add_argument("--manifest", required=True, help="Run manifest JSON path.")
    parser.add_argument("--summary-json", required=True, help="Analyzer summary JSON path.")
    parser.add_argument("--summary-csv", required=True, help="Analyzer summary CSV path.")
    parser.add_argument("--parsed", required=True, help="Parsed receiver valid-packet CSV path.")
    parser.add_argument(
        "--out-json",
        default=None,
        help="Optional validation report JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = validate(args)
    print_results(results)

    if args.out_json:
        write_validation_json(Path(args.out_json), results)
        print(f"Wrote validation JSON: {args.out_json}")

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
