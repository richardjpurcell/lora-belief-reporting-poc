# Run 026 Strict-Threshold Scheduled Replay

## Purpose

Run 026 tests a stricter usefulness-threshold scheduled replay condition.

Runs 024 and 025 used the same Run 022 reporting schedules, where TXA used a fixed-all schedule and TXB used a usefulness-threshold schedule with 8 SEND rows out of 16 schedule rows. Run 026 keeps TXA fixed-all but raises the TXB usefulness threshold to 0.79, producing 4 SEND rows out of 16 schedule rows.

The purpose is to test whether a stricter usefulness-threshold schedule further reduces observed physical packet arrivals while preserving higher mean delivered usefulness per received packet.

## Branch and Milestone Context

Run 026 physical replay branch:

```
exp033-run026-threshold-variant-replay
```

Design milestone:

```
v1.7-run026-threshold-variant-design
```

Planned replay milestone:

```
v1.8-run026-threshold-variant-replay
```

## Schedule Design

Run 026 uses the following scheduled replay structure:

```
TXA/N01: fixed-all schedule
TXB/N16: usefulness-threshold schedule
```

Schedule rows:

```
TXA: 16/16 SEND rows
TXB: 4/16 SEND rows
```

TXB usefulness threshold:

```
0.79
```

Scheduled TXB/TXA send-fraction ratio:

```
4 / 16 = 0.2500
```

Generated schedule files:

```
traces/run026_reporting_txa_fixed_all_schedule.csv
traces/run026_reporting_txb_usefulness_threshold_schedule.csv
```

Generated compact firmware traces:

```
traces/run026_reporting_txa_fixed_all_compact.csv
traces/run026_reporting_txb_usefulness_threshold_compact.csv
```

Schedule-generation manifest:

```
traces/run026_reporting_reporting_schedule_manifest.json
```

Firmware schedule headers:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

## Physical Replay Log

Raw receiver log:

```
logs/rx_run_026_strict_threshold_replay.csv
```

Parsed valid packets:

```
logs/parsed_run_026_strict_threshold_replay.csv
```

Parsed malformed packets:

```
logs/parsed_run_026_strict_threshold_replay_rejects.csv
```

Parser command:

```
python scripts/parse_receiver_log.py \
    --infile logs/rx_run_026_strict_threshold_replay.csv \
    --out logs/parsed_run_026_strict_threshold_replay.csv \
    --seq-window 50
```

## Packet-Centric Parser Summary

The packet parser reported:

```
Valid packets:      631
Malformed packets:  2
```

Packets by node:

```
N01: 504
N16: 127
```

Packets by transmitter and node:

```
TXA/N01: 504
TXB/N16: 127
```

Sequence ranges:

```
N01: min 0, max 506, count 504
N16: min 0, max 127, count 127
```

Observed sequence gaps:

```
TXA/N01: missing 3 -> [206, 426, 490]
TXB/N16: missing 1 -> [14]
```

These are observed sequence gaps, not confirmed collisions.

## Radio Metadata

Radio metadata by node:

```
N01:
  mean RSSI: -49.62
  min RSSI:  -57.0
  max RSSI:  -46.0
  mean SNR:    9.65
  min SNR:     9.00
  max SNR:    10.50

N16:
  mean RSSI: -54.15
  min RSSI:  -55.0
  max RSSI:  -51.0
  mean SNR:    9.66
  min SNR:     9.25
  max SNR:    10.25
```

## Packet-Centric Usefulness Summary

Usefulness by node:

```
N01:
  packets:             504
  total usefulness:    271.33
  mean usefulness:       0.538
  total priority:      272.74
  mean priority:         0.541

N16:
  packets:             127
  total usefulness:    109.93
  mean usefulness:       0.866
  total priority:      110.61
  mean priority:         0.871
```

Approximate receiver inter-arrival time by node:

```
N01:
  mean: 1.006 s
  min:  0.988 s
  max:  2.000 s

N16:
  mean: 4.000 s
  min:  1.988 s
  max:  8.001 s
```

The inter-arrival values are receiver-observed timing summaries. They should not be interpreted as true latency because transmitter and receiver clocks are not synchronized.

## Schedule-Aware Analysis

Schedule-aware analysis command:

```
python scripts/analyze_scheduled_replay.py \
    --parsed logs/parsed_run_026_strict_threshold_replay.csv \
    --schedule-a traces/run026_reporting_txa_fixed_all_schedule.csv \
    --schedule-b traces/run026_reporting_txb_usefulness_threshold_schedule.csv \
    --out-json reports/run026_schedule_aware_summary.json \
    --out-csv reports/run026_schedule_aware_summary.csv
```

Schedule-aware analysis output:

```
TXA: 16/16 schedule rows SEND; 504 received packets; mean delivered usefulness 0.538
TXB: 4/16 schedule rows SEND; 127 received packets; mean delivered usefulness 0.866
Observed received-packet ratio 0.2520; scheduled send-fraction ratio 0.2500.
```

The analysis script reported:

```
Interpretation: received packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.
```

## Manifest-Bound Reproduction

Run 026 manifest:

```
reports/run026_schedule_aware_manifest.json
```

Manifest-bound reproduction command:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
    --manifest reports/run026_schedule_aware_manifest.json
```

Manifest-bound reproduction output:

```
TXA/N01: 16/16 schedule rows SEND; 504 received packets; mean delivered usefulness 0.538
TXB/N16: 4/16 schedule rows SEND; 127 received packets; mean delivered usefulness 0.866
Observed received-packet ratio 0.2520; scheduled send-fraction ratio 0.2500.
```

## Bundle Validation Note

The first Run 026 bundle validation failed because the Run 026 manifest had been copied from the Run 025 manifest and still contained Run 025 expected-headline values.

The stale Run 025 expected values were:

```
TXA received packets: 368
TXB scheduled SEND rows: 8
TXB received packets: 184
TXB mean delivered usefulness: 0.785
observed received-packet ratio: 0.5000
scheduled send-fraction ratio: 0.5000
```

The actual Run 026 values are:

```
TXA received packets: 504
TXB scheduled SEND rows: 4
TXB received packets: 127
TXB mean delivered usefulness: 0.866
observed received-packet ratio: 0.2520
scheduled send-fraction ratio: 0.2500
```

This validation failure was useful because it confirmed that the validator checks manifest expectations against the generated summary. The manifest should be updated with the Run 026 expected headline values before re-running validation.

Corrected expected headline:

```
TXA/N01: 16/16 schedule rows SEND; 504 received packets; mean delivered usefulness 0.538
TXB/N16: 4/16 schedule rows SEND; 127 received packets; mean delivered usefulness 0.866
Observed received-packet ratio 0.2520; scheduled send-fraction ratio 0.2500.
```

Bundle validation command:

```
python scripts/validate_run_bundle.py \
    --manifest reports/run026_schedule_aware_manifest.json
```

## Main Result

Run 026 behaved as expected for the stricter threshold condition.

The observed TXB/TXA received-packet ratio was:

```
127 / 504 = 0.2520
```

The scheduled TXB/TXA send-fraction ratio was:

```
4 / 16 = 0.2500
```

TXB retained substantially higher mean delivered usefulness per received packet:

```
TXA mean delivered usefulness: 0.538
TXB mean delivered usefulness: 0.866
```

Careful interpretation:

```
Under the stricter 0.79 usefulness-threshold schedule, TXB produced approximately one quarter as many received packets as TXA while retaining substantially higher mean delivered usefulness per received packet. The observed received-packet ratio was close to the scheduled send-fraction ratio, which is consistent with scheduled skipping under similar lab conditions.
```

## Relationship to Runs 024 and 025

Runs 024 and 025 used the earlier 8/16 TXB usefulness-threshold schedule.

Run 024:

```
TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
Observed TXB/TXA received-packet ratio: 0.4875
Scheduled TXB/TXA send-fraction ratio: 0.5000
```

Run 025:

```
TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785
Observed TXB/TXA received-packet ratio: 0.5000
Scheduled TXB/TXA send-fraction ratio: 0.5000
```

Run 026:

```
TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866
Observed TXB/TXA received-packet ratio: 0.2520
Scheduled TXB/TXA send-fraction ratio: 0.2500
```

Together, Runs 024, 025, and 026 support a threshold-family interpretation: stricter scheduled skipping reduced the observed TXB/TXA received-packet ratio while preserving higher mean delivered usefulness for TXB.

## Multi-Run Comparison

The multi-run comparison should include Run 024, Run 025, and Run 026.

The comparison script expects repeated singular `--manifest` arguments:

```
python scripts/compare_scheduled_runs.py \
    --manifest reports/run024_schedule_aware_manifest.json \
    --manifest reports/run025_schedule_aware_manifest.json \
    --manifest reports/run026_schedule_aware_manifest.json \
    --out-csv reports/scheduled_replay_comparison.csv \
    --out-json reports/scheduled_replay_comparison.json
```

If validation is desired during comparison:

```
python scripts/compare_scheduled_runs.py \
    --manifest reports/run024_schedule_aware_manifest.json \
    --manifest reports/run025_schedule_aware_manifest.json \
    --manifest reports/run026_schedule_aware_manifest.json \
    --out-csv reports/scheduled_replay_comparison.csv \
    --out-json reports/scheduled_replay_comparison.json \
    --validate
```

## Interpretation Boundaries

This remains a bounded physical scheduled replay.

Preserve the following cautions:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period; firmware loops over it repeatedly.
* The analysis compares schedule proportions and observed packet proportions.
* Do not infer exact transmitted-packet counts unless firmware-side transmission counts are instrumented.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and must not be interpreted as true latency.
* Usefulness and priority are synthetic metadata at this stage.
* The run does not yet use a live belief-maintenance controller.
* Avoid airtime-optimization claims.
* Use “reduced physical transmission attempts under scheduled skipping” rather than broader optimization language.
* Do not overgeneralize from three lab runs.

## Planned Commit

Files expected for the Run 026 replay milestone include:

```
logs/rx_run_026_strict_threshold_replay.csv
logs/parsed_run_026_strict_threshold_replay.csv
logs/parsed_run_026_strict_threshold_replay_rejects.csv
reports/run026_schedule_aware_summary.json
reports/run026_schedule_aware_summary.csv
reports/run026_schedule_aware_manifest.json
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
docs/development/run026_strict_threshold_replay.md
```

Commit message:

```
Document Run 026 strict-threshold physical replay
```

Tag:

```
v1.8-run026-threshold-variant-replay
```
