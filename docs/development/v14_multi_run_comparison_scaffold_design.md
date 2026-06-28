# v1.4 Multi-Run Comparison Scaffold Design

## Purpose

The v1.3 milestone validates a single manifest-bound replay-analysis bundle. Run 024 now has a reproducible evidence path:

* skipped-slot physical replay;
* schedule-aware analysis;
* manifest-bound reproduction;
* run-bundle validation.

The v1.4 milestone adds a comparison scaffold for one or more validated replay-analysis manifests.

This is not a new physical experiment. It prepares the repository to compare Run 024 with future scheduled replay runs such as Run 025, Run 026, and later multi-node experiments.

## Design principle

The parser remains packet-centric.

The schedule-aware analyzer remains schedule-aware.

The manifest-bound wrapper runs analysis from a manifest.

The validator checks each manifest-bound bundle.

The new comparison tool aggregates validated bundle summaries.

Responsibilities remain separated:

* `scripts/parse_receiver_log.py` parses receiver logs.
* `scripts/analyze_scheduled_replay.py` combines schedules with parsed receiver rows.
* `scripts/analyze_scheduled_replay_from_manifest.py` runs analysis from a manifest.
* `scripts/validate_run_bundle.py` checks a manifest-bound bundle.
* `scripts/compare_scheduled_runs.py` summarizes one or more manifest-bound run bundles.

## Motivation

A single run can show that a specific scheduled replay behaved consistently with its schedule. A later research claim will require comparing across repeated runs or across experimental conditions.

Examples of future comparisons include:

* repeated Run 024-style tests;
* different usefulness thresholds;
* different schedule lengths;
* different slot intervals;
* more transmitters;
* different physical layouts;
* different LoRa parameters.

The comparison scaffold should support those future comparisons without changing the lower-level parser or analyzer.

## Proposed command

For the current repository state, the comparison can run on one manifest:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json
```

Later, it should support multiple manifests:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --manifest reports/run025_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json
```

## Inputs

Each input manifest should already point to:

* schedule CSVs;
* parsed receiver log;
* summary JSON;
* summary CSV;
* expected headline;
* interpretation cautions.

The comparison tool should read the manifest and the associated summary JSON. It should not re-run the analyzer by default.

## Optional validation

The comparison tool should support:

```
--validate
```

When enabled, it should call the existing validator on each manifest before adding it to the comparison table.

If validation fails for any manifest, the comparison should fail with a nonzero exit code.

## Outputs

The comparison CSV should include one row per transmitter per run.

Suggested columns:

* run ID;
* milestone;
* analysis type;
* transmitter label;
* node label;
* transmitter role;
* demand rows;
* scheduled SEND rows;
* scheduled SKIP rows;
* send fraction;
* received valid packets;
* delivered usefulness mean per received packet;
* delivered usefulness total;
* received packets per scheduled SEND row;
* delivered usefulness per scheduled demand row;
* delivered usefulness per scheduled SEND row;
* observed sequence minimum;
* observed sequence maximum;
* observed missing transmitted sequence count;
* mean receiver inter-arrival in milliseconds.

The comparison JSON should include:

* input manifests;
* number of runs;
* number of transmitter rows;
* per-transmitter rows;
* per-run comparison summaries from the schedule-aware summary JSON.

## Current Run 024 expected result

With only Run 024, the comparison table should contain two transmitter rows:

| Run    | Transmitter/node | SEND rows | Demand rows | Received packets | Mean delivered usefulness |
| ------ | ---------------- | --------: | ----------: | ---------------: | ------------------------: |
| run024 | TXA/N01          |        16 |          16 |              361 |                     0.540 |
| run024 | TXB/N16          |         8 |          16 |              176 |                     0.786 |

The Run 024 comparison summary should preserve:

```
observed TXB/TXA received-packet ratio ≈ 0.4875
scheduled TXB/TXA send-fraction ratio = 0.5000
```

## Interpretation boundary

The comparison scaffold should not turn a single run into a generalized result.

With only Run 024, the careful wording is:

> The comparison scaffold summarizes the validated Run 024 bundle and prepares the repository for future multi-run comparison.

It should not claim replicated evidence until additional physical runs are added.

The existing cautions still apply:

* point-to-point LoRa at 915 MHz, not LoRaWAN;
* observed sequence gaps are not confirmed collisions;
* `recv_ms` and `tx_ms` are not synchronized latency;
* usefulness and priority are synthetic metadata;
* no live belief-maintenance controller is active yet;
* no airtime-optimization claim is made.

## Milestone contribution

v1.4 prepares the repository for multi-run scheduled replay analysis.

The progression becomes:

* v1.0: skipped-slot physical replay;
* v1.1: schedule-aware analysis;
* v1.2: manifest-bound reproduction;
* v1.3: run-bundle validation;
* v1.4: comparison scaffold for one or more validated scheduled-replay bundles.

This is a useful stopping point before collecting another physical run because future run manifests can be added to the comparison tool without changing the lower-level evidence path.
