# v1.3 Run-Bundle Validation Design

## Purpose

The v1.2 milestone added manifest-bound replay analysis. A Run 024 manifest now records the schedules, firmware headers, receiver logs, parsed logs, output reports, expected headline, interpretation, and cautions for the skipped-slot replay analysis.

The v1.3 milestone adds run-bundle validation.

The goal is to check whether the files and values referenced by a replay-analysis manifest are internally consistent before using the bundle as research evidence.

This is a reproducibility and integrity milestone, not a new physical experiment.

## Design principle

The parser remains packet-centric.

The schedule-aware analyzer remains schedule-aware.

The manifest-bound wrapper remains responsible for running analysis from a manifest.

The new validator checks the run bundle.

Responsibilities remain separated:

* `scripts/parse_receiver_log.py` parses receiver logs.
* `scripts/analyze_scheduled_replay.py` combines schedules with parsed receiver rows.
* `scripts/analyze_scheduled_replay_from_manifest.py` runs analysis from a manifest.
* `scripts/validate_run_bundle.py` checks that a manifest-bound bundle is internally consistent.

## Motivation

A manifest-bound analysis is only useful if the manifest points to the right artifacts and if those artifacts agree with the expected result.

For Run 024, the manifest references:

* schedule CSVs;
* firmware schedule headers;
* raw receiver log;
* parsed valid receiver log;
* parsed rejects log;
* generated JSON report;
* generated CSV report;
* expected headline strings;
* interpretation cautions.

The v1.3 validator should check these relationships directly.

## Proposed command

The validator should run as:

```
python scripts/validate_run_bundle.py \
  --manifest reports/run024_schedule_aware_manifest.json
```

It should also support a quieter machine-readable mode later if needed, but v1.3 can begin with readable terminal output and process exit codes.

## Required checks

The validator should check that required manifest keys exist:

* `run_id`;
* `milestone`;
* `transmitters.a.tx_id`;
* `transmitters.a.schedule_csv`;
* `transmitters.a.schedule_header`;
* `transmitters.b.tx_id`;
* `transmitters.b.schedule_csv`;
* `transmitters.b.schedule_header`;
* `receiver_logs.raw`;
* `receiver_logs.parsed_valid`;
* `receiver_logs.parsed_rejects`;
* `outputs.summary_json`;
* `outputs.summary_csv`;
* `expected_headline`;
* `interpretation`;
* `cautions`.

The validator should check that referenced input files exist:

* schedule CSVs;
* firmware schedule headers;
* raw receiver log;
* parsed valid receiver log;
* parsed rejects log;
* generated summary JSON;
* generated summary CSV.

The validator should check basic CSV readability for:

* schedule CSVs;
* parsed valid receiver log;
* parsed rejects log;
* summary CSV.

The validator should check JSON readability for:

* manifest JSON;
* summary JSON.

## Consistency checks

For Run 024-style schedule-aware bundles, the validator should check:

1. schedule row counts are readable;
2. each schedule has a valid SEND/SKIP action column;
3. scheduled SEND/SKIP counts can be computed;
4. parsed receiver rows contain expected transmitter labels;
5. summary JSON contains a `per_transmitter` section;
6. summary CSV contains one row per transmitter;
7. summary JSON and summary CSV agree on key headline values;
8. expected headline strings in the manifest are consistent with computed summary values.

The key values to compare are:

* scheduled SEND rows;
* demand rows;
* received valid packets;
* mean delivered usefulness per received packet;
* observed received-packet ratio;
* scheduled send-fraction ratio.

## Expected Run 024 validation

For Run 024, the validator should confirm:

* TXA has 16 demand rows and 16 scheduled SEND rows;
* TXB has 16 demand rows and 8 scheduled SEND rows;
* TXA has 361 received valid packets;
* TXB has 176 received valid packets;
* TXA mean delivered usefulness is approximately 0.540;
* TXB mean delivered usefulness is approximately 0.786;
* observed TXB/TXA received-packet ratio is approximately 0.4875;
* scheduled TXB/TXA send-fraction ratio is approximately 0.5000.

Because summaries use rounded headline text, comparisons should use a small tolerance for floating-point values.

## Output behavior

The validator should print clear PASS/FAIL lines.

A successful run should exit with status code 0.

A failed validation should exit with nonzero status.

Suggested success headline:

```
Bundle validation PASSED: reports/run024_schedule_aware_manifest.json
```

Suggested failure headline:

```
Bundle validation FAILED: reports/run024_schedule_aware_manifest.json
```

## Non-goals

The validator should not:

* re-parse raw receiver logs;
* alter generated reports;
* infer exact transmitted packet counts;
* infer confirmed collisions;
* infer true latency;
* evaluate airtime optimization;
* validate live belief-controller behavior.

## Milestone contribution

v1.3 improves trust in the manifest-bound analysis path.

v1.0 showed physical skipped-slot replay.

v1.1 added schedule-aware analysis.

v1.2 made the analysis manifest-bound.

v1.3 validates that the manifest-bound bundle is internally consistent.

This makes the Run 024 evidence path more robust before expanding to additional scheduled replay runs or multi-run comparisons.
