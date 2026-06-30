# v3.10 Multi-Transmitter Bundle Validation

## Purpose

This milestone adds validation support for the list-valued, N-transmitter manifest replay bundle introduced for Run 030.

The immediate goal is to validate that the Run 030 three-transmitter analysis artifacts are structurally coherent and reproducible from the manifest-bound replay workflow.

This is a validation/tooling milestone. It does not add a new physical run, firmware change, schedule change, or analysis interpretation.

## Context

Run 030 moved the SD-backed physical replay workflow from two transmitters to three transmitters:

* TXA/N01: fixed-all baseline
* TXB/N16: medium-threshold scheduled skipping
* TXC/N31: strict-threshold scheduled skipping

The v3.9 milestone added a list-valued N-transmitter analyzer:

* `scripts/analyze_scheduled_replay_manifest_multi.py`

That analyzer reads:

* `--manifest`
* `--parsed`
* `--out-json`
* `--out-csv`

and produces Run 030 summary artifacts:

* `outputs/run030_three_transmitter_manifest_replay_summary.json`
* `outputs/run030_three_transmitter_manifest_replay_summary.csv`

The v3.10 milestone adds a matching validation layer for those N-transmitter outputs.

## Added artifact

This milestone adds:

* `scripts/validate_manifest_replay_bundle_multi.py`

The validator is intentionally separate from the older two-transmitter validator:

* `scripts/validate_run_bundle.py`

The older validator remains useful for legacy two-transmitter manifest structures that use `transmitters.a` and `transmitters.b`.

The new validator targets list-valued manifests such as Run 030, where transmitters are represented as:

* TXA/N01
* TXB/N16
* TXC/N31

## Validation command

The Run 030 validation command is:

```
python scripts/validate_manifest_replay_bundle_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --summary-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --summary-csv outputs/run030_three_transmitter_manifest_replay_summary.csv \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_validation.json
```

## Confirmed validation result

The validator completed successfully:

```
Validation summary: 101/101 checks passed; 0 failed.
```

The validation report was written to:

* `outputs/run030_three_transmitter_manifest_replay_validation.json`

## What the validator checks

The validator checks that the manifest exists and is readable JSON.

It checks that the manifest has a non-empty list-valued `transmitters` field.

For each transmitter, it checks that required fields are present:

* `tx_id`
* `node_id`
* `schedule_csv`
* `expected_rows`
* `expected_send_rows`
* `expected_skip_rows`

It checks that each transmitter has a unique `tx_id`/`node_id` pair.

It checks that each schedule CSV exists and has readable SEND/SKIP structure.

It compares each schedule CSV against the manifest expectations:

* demand rows
* scheduled SEND rows
* scheduled SKIP rows

It checks that the parsed receiver CSV exists and is readable.

It checks that the summary JSON exists, is readable, and contains a `per_transmitter` list.

It checks that the summary CSV exists, is readable, and has one row per manifest transmitter.

It verifies that all manifest transmitters appear in both the summary JSON and summary CSV.

It checks that summary values match the manifest expectations:

* `demand_rows`
* `scheduled_send_rows`
* `scheduled_skip_rows`

It checks that the summary JSON echoes the manifest expected counts:

* `expected_rows_manifest`
* `expected_send_rows_manifest`
* `expected_skip_rows_manifest`

It checks that ratio comparisons exist for the manifest’s expected scheduled ratios.

It checks that ratio comparison values are present and numeric:

* scheduled expected ratio
* observed receiver-side packet ratio
* observed-minus-expected difference

It checks that the summary JSON includes interpretation-boundary text covering the main caution categories.

## What the validator does not check

The validator does not infer exact transmitted-packet counts.

It does not infer confirmed collisions.

It does not treat sequence gaps as confirmed collisions.

It does not treat `recv_ms` and `tx_ms` as synchronized board clocks.

It does not validate true latency.

It does not validate LoRaWAN behavior.

It does not validate airtime optimization.

It does not validate energy savings.

It does not validate scaling behavior beyond this three-transmitter lab replay.

It does not validate live-controller behavior.

It does not validate operational wildfire behavior.

## Interpretation

The Run 030 manifest, schedule CSVs, parsed receiver CSV, summary JSON, and summary CSV now form a coherent N-transmitter validation bundle for this three-transmitter lab replay.

The validation result supports the following bounded interpretation:

The SD-backed, manifest-bound replay workflow remained structurally reproducible and validation-readable when moving from two transmitters to three transmitters under this lab condition.

This remains evidence about artifact consistency, scheduled replay structure, and receiver-side replay readability. It is not evidence of exact transmitted-packet counts, confirmed collision behavior, synchronized latency, energy savings, LoRaWAN behavior, live belief-maintenance control, or 12-transmitter behavior.

## Relationship to the longer-term project

This milestone strengthens the reproducibility layer around SD-backed, manifest-bound replay.

The broader project direction remains:

1. Stabilize schedule generation.
2. Stabilize SD-card replay.
3. Stabilize physical replay parsing.
4. Stabilize manifest-bound multi-transmitter analysis.
5. Stabilize validation and reproducibility bundles.
6. Then cautiously scale transmitter count and/or move closer to AWSRT-derived belief-demand traces.

The next immediate value of v3.10 is that future multi-transmitter replay runs can be checked against a validation pattern before additional physical scaling or AWSRT-derived trace integration.
