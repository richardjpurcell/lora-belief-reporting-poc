# Run 024 multi-run comparison scaffold

## Purpose

The v1.4 milestone adds a comparison scaffold for one or more manifest-bound scheduled replay runs.

At the time of this milestone, only Run 024 is included. Therefore, this is not yet a multi-run empirical comparison. It is a scaffold that summarizes the validated Run 024 bundle and prepares the repository to include future scheduled replay runs.

## Relationship to previous milestones

The v1 sequence is now:

* v1.0: skipped-slot physical replay;
* v1.1: schedule-aware analysis;
* v1.2: manifest-bound reproduction;
* v1.3: run-bundle validation;
* v1.4: comparison scaffold for one or more scheduled replay bundles.

The parser remains packet-centric.

The analyzer remains schedule-aware.

The manifest wrapper remains manifest-bound.

The validator checks each run bundle.

The comparison scaffold aggregates validated bundle summaries.

## Comparison script

The comparison script is:

* `scripts/compare_scheduled_runs.py`

It reads one or more run manifests, loads the schedule-aware summary JSON referenced by each manifest, and writes aggregate comparison outputs.

It does not re-parse raw receiver logs. It does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, or airtime optimization.

## Command

For the current Run 024-only comparison scaffold:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json \
  --validate
```

The `--validate` flag runs the v1.3 bundle validator before including the manifest in the comparison output.

## Outputs

The generated outputs are:

* `reports/scheduled_replay_comparison.csv`
* `reports/scheduled_replay_comparison.json`

## Validation and comparison output

The Run 024 bundle passed validation before comparison:

```
Bundle validation PASSED: reports/run024_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The comparison scaffold then produced:

```
Wrote comparison CSV:  reports/scheduled_replay_comparison.csv
Wrote comparison JSON: reports/scheduled_replay_comparison.json
Runs summarized: 1
Transmitter rows: 2
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
```

## Current comparison table

| Run    | Transmitter/node | SEND rows | Demand rows | Received packets | Mean delivered usefulness |
| ------ | ---------------- | --------: | ----------: | ---------------: | ------------------------: |
| run024 | TXA/N01          |        16 |          16 |              361 |                     0.540 |
| run024 | TXB/N16          |         8 |          16 |              176 |                     0.786 |

## Preserved Run 024 comparison summary

The scaffold preserves the existing Run 024 proportional comparison:

```
observed TXB/TXA received-packet ratio ≈ 0.4875
scheduled TXB/TXA send-fraction ratio = 0.5000
```

## Interpretation

With only Run 024 included, the careful interpretation is:

> The comparison scaffold summarizes the validated Run 024 bundle and prepares the repository for future multi-run comparison.

The existing Run 024 interpretation remains:

> The observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, consistent with scheduled skipping, while TXB retained higher mean delivered usefulness per received packet.

This remains a proportional interpretation of one physical replay run. It should not be interpreted as replicated evidence across runs.

## Cautions

The existing cautions remain in force.

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analysis compares schedule proportions and observed packet proportions.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* The appropriate wording is “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
* No replicated multi-run claim is made until additional physical runs are added.

## Milestone contribution

v1.4 prepares the repository for future multi-run scheduled replay analysis.

The lower-level evidence path does not need to be redesigned when future runs are added. A future run can add its own manifest, pass bundle validation, and then be included in the comparison scaffold through an additional `--manifest` argument.
