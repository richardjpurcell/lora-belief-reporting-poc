# Run 024 run-bundle validation

## Purpose

The v1.3 milestone adds validation for manifest-bound replay-analysis bundles.

Run 024 already has:

* skipped-slot physical replay from v1.0;
* schedule-aware analysis from v1.1;
* manifest-bound reproduction from v1.2.

This note documents the v1.3 validation step for the Run 024 bundle.

## Validator

The validator is:

* `scripts/validate_run_bundle.py`

It checks whether the Run 024 manifest-bound bundle is internally consistent.

The validator does not re-parse raw receiver logs. It also does not infer exact transmitted-packet counts, confirmed collisions, true latency, airtime optimization, or live belief-controller behavior.

## Manifest

The validated manifest is:

* `reports/run024_schedule_aware_manifest.json`

## Command

```
python scripts/validate_run_bundle.py \
  --manifest reports/run024_schedule_aware_manifest.json
```

## Result

The Run 024 bundle passed validation:

```
Bundle validation PASSED: reports/run024_schedule_aware_manifest.json
Checks passed: 70 / 70
```

## What was checked

The validator confirmed that required manifest keys are present, including:

* run ID;
* milestone;
* transmitter labels;
* schedule CSV paths;
* firmware schedule-header paths;
* raw receiver log path;
* parsed valid receiver log path;
* parsed rejects path;
* output summary paths;
* expected headline;
* interpretation;
* caution notes.

It confirmed that referenced files exist, including:

* schedule CSVs;
* firmware schedule headers;
* raw receiver log;
* parsed valid receiver log;
* parsed rejects log;
* generated summary JSON;
* generated summary CSV.

It confirmed CSV and JSON readability for the relevant files.

It confirmed consistency among:

* schedule CSV counts;
* summary JSON;
* summary CSV;
* parsed receiver transmitter labels;
* parsed receiver node labels;
* manifest expected headline values.

## Key validated values

The validated Run 024 values are:

| Transmitter/node | Demand rows | SEND rows | SKIP rows | Received valid packets | Mean delivered usefulness |
| ---------------- | ----------: | --------: | --------: | ---------------------: | ------------------------: |
| TXA/N01          |          16 |        16 |         0 |                    361 |                     0.540 |
| TXB/N16          |          16 |         8 |         8 |                    176 |                     0.786 |

The validator also confirmed:

```
observed TXB/TXA received-packet ratio ≈ 0.4875
scheduled TXB/TXA send-fraction ratio = 0.5000
```

## Interpretation

The validated bundle supports the existing careful interpretation:

> The observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, consistent with scheduled skipping, while TXB retained higher mean delivered usefulness per received packet.

This remains a proportional interpretation of a repeated schedule period. It is not an exact transmitted-packet count, collision measurement, true-latency measurement, airtime-optimization result, or live-controller result.

## Milestone contribution

v1.3 strengthens the evidence path by checking that the manifest-bound Run 024 bundle is internally consistent.

The progression is now:

* v1.0: skipped-slot physical replay;
* v1.1: schedule-aware analysis;
* v1.2: manifest-bound reproduction;
* v1.3: run-bundle validation.

This makes Run 024 more suitable as a reproducible reference checkpoint before adding additional scheduled replay runs or multi-run comparisons.
