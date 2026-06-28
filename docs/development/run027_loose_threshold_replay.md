# Run 027 Loose-Threshold Scheduled Replay

## Purpose

Run 027 tests a loose usefulness-threshold scheduled replay condition.

Runs 024 and 025 used a medium usefulness-threshold schedule where TXB/N16 had 8 SEND rows out of 16 schedule rows. Run 026 used a stricter threshold where TXB/N16 had 4 SEND rows out of 16 schedule rows. Run 027 adds the looser condition, where TXB/N16 has 12 SEND rows out of 16 schedule rows.

The purpose is to fill in the upper part of the threshold-family ladder and test whether a looser threshold produces an observed TXB/TXA received-packet ratio close to the scheduled send-fraction ratio of 0.7500 while still preserving higher mean delivered usefulness per received packet than the fixed-all TXA stream.

## Branch and Milestone Context

Run 027 physical replay branch:

```
exp036-run027-loose-threshold-replay
```

Design milestone:

```
v2.0-run027-loose-threshold-design
```

Planned replay milestone:

```
v2.1-run027-loose-threshold-replay
```

## Schedule Design

Run 027 uses the following scheduled replay structure:

```
TXA/N01: fixed-all schedule
TXB/N16: usefulness-threshold schedule
```

Schedule rows:

```
TXA: 16/16 SEND rows
TXB: 12/16 SEND rows
```

TXB usefulness threshold:

```
0.36
```

Scheduled TXB/TXA send-fraction ratio:

```
12 / 16 = 0.7500
```

Generated schedule files:

```
traces/run027_reporting_txa_fixed_all_schedule.csv
traces/run027_reporting_txb_usefulness_threshold_schedule.csv
```

Generated compact firmware traces:

```
traces/run027_reporting_txa_fixed_all_compact.csv
traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

Schedule-generation manifest:

```
traces/run027_reporting_reporting_schedule_manifest.json
```

Firmware schedule headers:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

## Physical Replay Log

Raw receiver log:

```
logs/rx_run_027_loose_threshold_replay.csv
```

Parsed valid packets:

```
logs/parsed_run_027_loose_threshold_replay.csv
```

Parsed malformed packets:

```
logs/parsed_run_027_loose_threshold_replay_rejects.csv
```

Parser command:

```
python scripts/parse_receiver_log.py \
    --infile logs/rx_run_027_loose_threshold_replay.csv \
    --out logs/parsed_run_027_loose_threshold_replay.csv \
    --seq-window 50
```

## Packet-Centric Parser Summary

The packet parser reported:

```
Valid packets:      699
Malformed packets:  0
```

Packets by node:

```
N01: 400
N16: 299
```

Packets by transmitter and node:

```
TXA/N01: 400
TXB/N16: 299
```

Sequence ranges:

```
N01: min 0, max 399, count 400
N16: min 0, max 298, count 299
```

Observed sequence gaps:

```
TXA/N01: none
TXB/N16: none
```

The absence of observed sequence gaps is a useful run-quality observation, but it should not be generalized beyond this run.

## Radio Metadata

Radio metadata by node:

```
N01:
  mean RSSI: -48.40
  min RSSI:  -54.0
  max RSSI:  -44.0
  mean SNR:    9.61
  min SNR:     9.0
  max SNR:    11.0

N16:
  mean RSSI: -52.62
  min RSSI:  -58.0
  max RSSI:  -49.0
  mean SNR:    9.69
  min SNR:     9.0
  max SNR:    10.5
```

## Packet-Centric Usefulness Summary

Usefulness by node:

```
N01:
  packets:             400
  total usefulness:    215.50
  mean usefulness:       0.539
  total priority:      216.75
  mean priority:         0.542

N16:
  packets:             299
  total usefulness:    199.54
  mean usefulness:       0.667
  total priority:      200.31
  mean priority:         0.670
```

Approximate receiver inter-arrival time by node:

```
N01:
  mean: 1.000 s
  min:  0.987 s
  max:  1.006 s

N16:
  mean: 1.336 s
  min:  0.999 s
  max:  2.001 s
```

The inter-arrival values are receiver-observed timing summaries. They should not be interpreted as true latency because transmitter and receiver clocks are not synchronized.

## Schedule-Aware Analysis

Schedule-aware analysis command:

```
python scripts/analyze_scheduled_replay.py \
    --parsed logs/parsed_run_027_loose_threshold_replay.csv \
    --schedule-a traces/run027_reporting_txa_fixed_all_schedule.csv \
    --schedule-b traces/run027_reporting_txb_usefulness_threshold_schedule.csv \
    --out-json reports/run027_schedule_aware_summary.json \
    --out-csv reports/run027_schedule_aware_summary.csv
```

Schedule-aware analysis output:

```
TXA: 16/16 schedule rows SEND; 400 received packets; mean delivered usefulness 0.539
TXB: 12/16 schedule rows SEND; 299 received packets; mean delivered usefulness 0.667
Observed received-packet ratio 0.7475; scheduled send-fraction ratio 0.7500.
```

The analysis script reported:

```
Interpretation: received packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.
```

## Manifest-Bound Reproduction

Run 027 manifest:

```
reports/run027_schedule_aware_manifest.json
```

Manifest-bound reproduction command:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
    --manifest reports/run027_schedule_aware_manifest.json
```

Manifest-bound reproduction reproduces the schedule-aware headline:

```
TXA/N01: 16/16 schedule rows SEND; 400 received packets; mean delivered usefulness 0.539
TXB/N16: 12/16 schedule rows SEND; 299 received packets; mean delivered usefulness 0.667
Observed received-packet ratio 0.7475; scheduled send-fraction ratio 0.7500.
```

## Bundle Validation

Run 027 passed bundle validation:

```
Bundle validation PASSED: reports/run027_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The validator confirmed consistency among the manifest, schedule CSVs, firmware schedule headers, raw receiver log, parsed valid receiver log, parsed rejects log, summary JSON, summary CSV, expected headline values, transmitter labels, and node labels.

## Main Result

Run 027 behaved as expected for the loose-threshold condition.

The observed TXB/TXA received-packet ratio was:

```
299 / 400 = 0.7475
```

The scheduled TXB/TXA send-fraction ratio was:

```
12 / 16 = 0.7500
```

TXB retained higher mean delivered usefulness per received packet than TXA:

```
TXA mean delivered usefulness: 0.539
TXB mean delivered usefulness: 0.667
```

Careful interpretation:

```
Under the loose 0.36 usefulness-threshold schedule, TXB produced approximately three quarters as many received packets as TXA while retaining higher mean delivered usefulness per received packet. The observed received-packet ratio was close to the scheduled send-fraction ratio, which is consistent with scheduled skipping under similar lab conditions.
```

## Relationship to Runs 024--026

Runs 024, 025, 026, and 027 now form a clearer threshold-family ladder.

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

Run 027:

```
TXA/N01: 16/16 SEND rows; 400 received packets; mean delivered usefulness 0.539
TXB/N16: 12/16 SEND rows; 299 received packets; mean delivered usefulness 0.667
Observed TXB/TXA received-packet ratio: 0.7475
Scheduled TXB/TXA send-fraction ratio: 0.7500
```

Together, the current physical threshold family is:

```
12/16 loose threshold  → observed ratio 0.7475; TXB mean usefulness 0.667
 8/16 medium threshold → observed ratio 0.4875 and 0.5000; TXB mean usefulness approximately 0.785
 4/16 strict threshold → observed ratio 0.2520; TXB mean usefulness 0.866
```

This is consistent with the expected tradeoff:

```
looser threshold:
  more TXB packets
  lower TXB mean usefulness than stricter thresholds

stricter threshold:
  fewer TXB packets
  higher TXB mean usefulness
```

## Multi-Run Comparison

The multi-run comparison now includes Runs 024, 025, 026, and 027.

Comparison command:

```
python scripts/compare_scheduled_runs.py \
    --manifest reports/run024_schedule_aware_manifest.json \
    --manifest reports/run025_schedule_aware_manifest.json \
    --manifest reports/run026_schedule_aware_manifest.json \
    --manifest reports/run027_schedule_aware_manifest.json \
    --out-csv reports/scheduled_replay_comparison.csv \
    --out-json reports/scheduled_replay_comparison.json \
    --validate
```

The comparison reported:

```
Runs summarized: 4
Transmitter rows: 8
```

Comparison rows:

```
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785
run026 TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
run026 TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866
run027 TXA/N01: 16/16 SEND rows; 400 received packets; mean delivered usefulness 0.539
run027 TXB/N16: 12/16 SEND rows; 299 received packets; mean delivered usefulness 0.667
```

Generated comparison outputs:

```
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
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
* Do not claim energy savings unless current or power measurements are added.
* Do not overgeneralize from a small number of lab runs.

## Planned Commit

Files expected for the Run 027 replay milestone include:

```
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
firmware/first_radio_link_TX_B/schedule_data_TXB.h
logs/rx_run_027_loose_threshold_replay.csv
logs/parsed_run_027_loose_threshold_replay.csv
logs/parsed_run_027_loose_threshold_replay_rejects.csv
reports/run027_schedule_aware_summary.json
reports/run027_schedule_aware_summary.csv
reports/run027_schedule_aware_manifest.json
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
docs/development/run027_loose_threshold_replay.md
```

Commit message:

```
Document Run 027 loose-threshold physical replay
```

Tag:

```
v2.1-run027-loose-threshold-replay
```
