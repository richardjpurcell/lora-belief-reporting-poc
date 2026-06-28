#!/usr/bin/env python3
"""
Validate a manifest-bound scheduled replay analysis bundle.

This validator checks that a run manifest points to existing artifacts and
that the generated schedule-aware summaries agree with the manifest's
expected headline values.

It does not re-parse raw receiver logs and does not infer exact transmitted
packet counts, confirmed collisions, true latency, or airtime optimization.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


TOL = 1e-3


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
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dotted_get(obj: dict[str, Any], dotted_key: str) -> Any:
    current: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def optional_dotted_get(obj: dict[str, Any], dotted_key: str) -> Any | None:
    current: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def check_required_keys(manifest: dict[str, Any]) -> list[CheckResult]:
    required = [
        "run_id",
        "milestone",
        "transmitters.a.tx_id",
        "transmitters.a.schedule_csv",
        "transmitters.a.schedule_header",
        "transmitters.b.tx_id",
        "transmitters.b.schedule_csv",
        "transmitters.b.schedule_header",
        "receiver_logs.raw",
        "receiver_logs.parsed_valid",
        "receiver_logs.parsed_rejects",
        "outputs.summary_json",
        "outputs.summary_csv",
        "expected_headline",
        "interpretation",
        "cautions",
    ]

    results: list[CheckResult] = []
    for key in required:
        try:
            value = dotted_get(manifest, key)
            ok = value is not None and value != ""
            results.append(CheckResult(f"required key: {key}", ok, "present" if ok else "empty"))
        except KeyError:
            results.append(CheckResult(f"required key: {key}", False, "missing"))

    return results


def check_file_exists(path_str: str, label: str) -> CheckResult:
    path = Path(path_str)
    return CheckResult(
        f"file exists: {label}",
        path.exists(),
        str(path),
    )


def check_csv_readable(path_str: str, label: str) -> CheckResult:
    path = Path(path_str)
    try:
        df = pd.read_csv(path)
        return CheckResult(
            f"csv readable: {label}",
            True,
            f"{path} rows={len(df)} cols={len(df.columns)}",
        )
    except Exception as exc:
        return CheckResult(
            f"csv readable: {label}",
            False,
            f"{path}: {exc}",
        )


def check_json_readable(path_str: str, label: str) -> CheckResult:
    path = Path(path_str)
    try:
        _ = read_json(path)
        return CheckResult(f"json readable: {label}", True, str(path))
    except Exception as exc:
        return CheckResult(f"json readable: {label}", False, f"{path}: {exc}")


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
            lambda v: "SEND" if v in truthy else "SKIP"
        )

    raise ValueError(f"no SEND/SKIP action column found; columns={list(df.columns)}")


def schedule_counts(path_str: str) -> dict[str, int | float]:
    df = normalise_columns(pd.read_csv(path_str))
    action = infer_action_series(df)
    send_rows = int(action.eq("SEND").sum())
    skip_rows = int(action.eq("SKIP").sum())
    demand_rows = int(len(df))
    send_fraction = float(send_rows / demand_rows) if demand_rows else 0.0
    return {
        "demand_rows": demand_rows,
        "scheduled_send_rows": send_rows,
        "scheduled_skip_rows": skip_rows,
        "send_fraction": send_fraction,
    }


def load_summary_json(path_str: str) -> dict[str, Any]:
    obj = read_json(Path(path_str))
    if not isinstance(obj, dict):
        raise ValueError("summary JSON root must be an object")
    return obj


def load_summary_csv(path_str: str) -> pd.DataFrame:
    return normalise_columns(pd.read_csv(path_str))


def rows_by_tx(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = summary.get("per_transmitter")
    if not isinstance(rows, list):
        raise ValueError("summary JSON missing per_transmitter list")

    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("summary per_transmitter row is not an object")
        tx_id = row.get("tx_id")
        if not isinstance(tx_id, str):
            raise ValueError("summary per_transmitter row missing tx_id")
        out[tx_id] = row
    return out


def approx_equal(a: Any, b: Any, tol: float = TOL) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def check_summary_consistency(
    manifest: dict[str, Any],
    summary_json: dict[str, Any],
    summary_csv: pd.DataFrame,
) -> list[CheckResult]:
    results: list[CheckResult] = []

    txa = dotted_get(manifest, "transmitters.a.tx_id")
    txb = dotted_get(manifest, "transmitters.b.tx_id")

    json_rows = rows_by_tx(summary_json)
    results.append(CheckResult("summary JSON has TXA row", txa in json_rows, str(txa)))
    results.append(CheckResult("summary JSON has TXB row", txb in json_rows, str(txb)))

    if "tx_id" not in summary_csv.columns:
        results.append(CheckResult("summary CSV has tx_id column", False, str(list(summary_csv.columns))))
        return results

    csv_by_tx = {
        str(row["tx_id"]): row
        for _, row in summary_csv.iterrows()
    }

    results.append(CheckResult("summary CSV has TXA row", txa in csv_by_tx, str(txa)))
    results.append(CheckResult("summary CSV has TXB row", txb in csv_by_tx, str(txb)))

    for tx in [txa, txb]:
        if tx not in json_rows or tx not in csv_by_tx:
            continue

        json_row = json_rows[tx]
        csv_row = csv_by_tx[tx]

        for key in [
            "demand_rows",
            "scheduled_send_rows",
            "scheduled_skip_rows",
            "received_valid_packets",
        ]:
            if key not in summary_csv.columns:
                results.append(CheckResult(f"summary CSV has {key}", False))
                continue

            results.append(
                CheckResult(
                    f"summary JSON/CSV agree: {tx} {key}",
                    approx_equal(json_row.get(key), csv_row[key]),
                    f"json={json_row.get(key)} csv={csv_row[key]}",
                )
            )

        key = "delivered_usefulness_mean_per_received_packet"
        if key in summary_csv.columns:
            results.append(
                CheckResult(
                    f"summary JSON/CSV agree: {tx} mean delivered usefulness",
                    approx_equal(json_row.get(key), csv_row[key]),
                    f"json={json_row.get(key)} csv={csv_row[key]}",
                )
            )

    comparison = summary_json.get("comparison", {})
    if isinstance(comparison, dict):
        results.append(
            CheckResult(
                "summary JSON has observed received-packet ratio",
                comparison.get("observed_received_packet_ratio_comparison_over_baseline") is not None,
                str(comparison.get("observed_received_packet_ratio_comparison_over_baseline")),
            )
        )
        results.append(
            CheckResult(
                "summary JSON has scheduled send-fraction ratio",
                comparison.get("scheduled_send_fraction_ratio_comparison_over_baseline") is not None,
                str(comparison.get("scheduled_send_fraction_ratio_comparison_over_baseline")),
            )
        )
    else:
        results.append(CheckResult("summary JSON comparison is object", False))

    return results


def extract_headline_values(headline: str) -> dict[str, float]:
    """
    Parse headline strings such as:
    TXA/N01: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
    """
    pattern = (
        r"(?P<send>\d+)\s*/\s*(?P<demand>\d+)\s+schedule rows SEND;\s+"
        r"(?P<received>\d+)\s+received packets;\s+"
        r"mean (?:delivered )?usefulness\s+(?P<mean>[0-9.]+)"
    )
    match = re.search(pattern, headline)
    if not match:
        raise ValueError(f"could not parse headline: {headline}")

    return {
        "scheduled_send_rows": float(match.group("send")),
        "demand_rows": float(match.group("demand")),
        "received_valid_packets": float(match.group("received")),
        "delivered_usefulness_mean_per_received_packet": float(match.group("mean")),
    }


def extract_ratio_values(headline: str) -> dict[str, float]:
    pattern = (
        r"Observed received-packet ratio\s+(?P<observed>\d+(?:\.\d+)?);\s+"
        r"scheduled send-fraction ratio\s+(?P<scheduled>\d+(?:\.\d+)?)"
    )
    match = re.search(pattern, headline)
    if not match:
        raise ValueError(f"could not parse ratio headline: {headline}")

    return {
        "observed_received_packet_ratio_comparison_over_baseline": float(match.group("observed")),
        "scheduled_send_fraction_ratio_comparison_over_baseline": float(match.group("scheduled")),
    }


def check_expected_headline(
    manifest: dict[str, Any],
    summary_json: dict[str, Any],
) -> list[CheckResult]:
    results: list[CheckResult] = []

    expected = manifest.get("expected_headline")
    if not isinstance(expected, dict):
        return [CheckResult("expected_headline is object", False)]

    json_rows = rows_by_tx(summary_json)

    headline_map = {
        "txa": dotted_get(manifest, "transmitters.a.tx_id"),
        "txb": dotted_get(manifest, "transmitters.b.tx_id"),
    }

    for headline_key, tx_id in headline_map.items():
        text = expected.get(headline_key)
        if not isinstance(text, str):
            results.append(CheckResult(f"expected headline present: {headline_key}", False))
            continue

        try:
            parsed = extract_headline_values(text)
        except ValueError as exc:
            results.append(CheckResult(f"expected headline parse: {headline_key}", False, str(exc)))
            continue

        row = json_rows.get(tx_id)
        if row is None:
            results.append(CheckResult(f"expected headline tx exists: {tx_id}", False))
            continue

        for key, expected_value in parsed.items():
            results.append(
                CheckResult(
                    f"expected headline agrees: {tx_id} {key}",
                    approx_equal(row.get(key), expected_value),
                    f"summary={row.get(key)} expected={expected_value}",
                )
            )

    ratio_text = expected.get("ratio")
    if isinstance(ratio_text, str):
        try:
            ratio_expected = extract_ratio_values(ratio_text)
            comparison = summary_json.get("comparison", {})
            for key, expected_value in ratio_expected.items():
                results.append(
                    CheckResult(
                        f"expected ratio agrees: {key}",
                        approx_equal(comparison.get(key), expected_value),
                        f"summary={comparison.get(key)} expected={expected_value}",
                    )
                )
        except ValueError as exc:
            results.append(CheckResult("expected ratio parse", False, str(exc)))
    else:
        results.append(CheckResult("expected ratio headline present", False))

    return results


def check_schedule_against_summary(
    manifest: dict[str, Any],
    summary_json: dict[str, Any],
) -> list[CheckResult]:
    results: list[CheckResult] = []

    json_rows = rows_by_tx(summary_json)

    for side in ["a", "b"]:
        tx_id = dotted_get(manifest, f"transmitters.{side}.tx_id")
        schedule_csv = dotted_get(manifest, f"transmitters.{side}.schedule_csv")
        counts = schedule_counts(schedule_csv)
        row = json_rows.get(tx_id)

        if row is None:
            results.append(CheckResult(f"schedule summary row exists: {tx_id}", False))
            continue

        for key in [
            "demand_rows",
            "scheduled_send_rows",
            "scheduled_skip_rows",
            "send_fraction",
        ]:
            results.append(
                CheckResult(
                    f"schedule agrees with summary: {tx_id} {key}",
                    approx_equal(counts[key], row.get(key)),
                    f"schedule={counts[key]} summary={row.get(key)}",
                )
            )

    return results


def check_parsed_labels(manifest: dict[str, Any]) -> list[CheckResult]:
    parsed_path = dotted_get(manifest, "receiver_logs.parsed_valid")
    parsed = normalise_columns(pd.read_csv(parsed_path))

    results: list[CheckResult] = []

    if "tx_id" not in parsed.columns:
        return [CheckResult("parsed valid CSV has tx_id column", False, str(list(parsed.columns)))]

    expected_txs = [
        dotted_get(manifest, "transmitters.a.tx_id"),
        dotted_get(manifest, "transmitters.b.tx_id"),
    ]

    tx_values = set(parsed["tx_id"].astype(str).unique())
    for tx in expected_txs:
        results.append(
            CheckResult(
                f"parsed valid CSV contains transmitter {tx}",
                tx in tx_values,
                f"available={sorted(tx_values)}",
            )
        )

    if "node_id" in parsed.columns:
        node_values = set(parsed["node_id"].astype(str).unique())
        for side in ["a", "b"]:
            node = optional_dotted_get(manifest, f"transmitters.{side}.node_id")
            if node:
                results.append(
                    CheckResult(
                        f"parsed valid CSV contains node {node}",
                        node in node_values,
                        f"available={sorted(node_values)}",
                    )
                )

    return results


def run_validation(manifest_path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        return [CheckResult("manifest JSON readable", False, str(exc))]

    if not isinstance(manifest, dict):
        return [CheckResult("manifest root is object", False)]

    results.append(CheckResult("manifest JSON readable", True, str(manifest_path)))
    results.extend(check_required_keys(manifest))

    file_keys = [
        ("transmitters.a.schedule_csv", "schedule A CSV"),
        ("transmitters.a.schedule_header", "schedule A header"),
        ("transmitters.b.schedule_csv", "schedule B CSV"),
        ("transmitters.b.schedule_header", "schedule B header"),
        ("receiver_logs.raw", "raw receiver log"),
        ("receiver_logs.parsed_valid", "parsed valid receiver log"),
        ("receiver_logs.parsed_rejects", "parsed rejects receiver log"),
        ("outputs.summary_json", "summary JSON"),
        ("outputs.summary_csv", "summary CSV"),
    ]

    for key, label in file_keys:
        try:
            path = dotted_get(manifest, key)
            results.append(check_file_exists(path, label))
        except KeyError:
            pass

    csv_keys = [
        ("transmitters.a.schedule_csv", "schedule A CSV"),
        ("transmitters.b.schedule_csv", "schedule B CSV"),
        ("receiver_logs.parsed_valid", "parsed valid receiver log"),
        ("receiver_logs.parsed_rejects", "parsed rejects receiver log"),
        ("outputs.summary_csv", "summary CSV"),
    ]

    for key, label in csv_keys:
        try:
            path = dotted_get(manifest, key)
            results.append(check_csv_readable(path, label))
        except KeyError:
            pass

    try:
        summary_json_path = dotted_get(manifest, "outputs.summary_json")
        results.append(check_json_readable(summary_json_path, "summary JSON"))

        summary_json = load_summary_json(summary_json_path)
        summary_csv = load_summary_csv(dotted_get(manifest, "outputs.summary_csv"))

        results.extend(check_summary_consistency(manifest, summary_json, summary_csv))
        results.extend(check_schedule_against_summary(manifest, summary_json))
        results.extend(check_parsed_labels(manifest))
        results.extend(check_expected_headline(manifest, summary_json))
    except Exception as exc:
        results.append(CheckResult("semantic consistency checks", False, str(exc)))

    return results


def print_results(results: list[CheckResult], manifest_path: Path) -> int:
    failed = [r for r in results if not r.passed]

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        if result.detail:
            print(f"[{status}] {result.name} -- {result.detail}")
        else:
            print(f"[{status}] {result.name}")

    if failed:
        print(f"\nBundle validation FAILED: {manifest_path}")
        print(f"Failed checks: {len(failed)} / {len(results)}")
        return 1

    print(f"\nBundle validation PASSED: {manifest_path}")
    print(f"Checks passed: {len(results)} / {len(results)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a manifest-bound scheduled replay analysis bundle."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to replay-analysis manifest JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_validation(args.manifest)
    exit_code = print_results(results, args.manifest)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
