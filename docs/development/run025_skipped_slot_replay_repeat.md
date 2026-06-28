# Run 025 skipped-slot replay repeat

## Purpose

Run 025 is a repeat skipped-slot physical replay using the same reporting schedules as Run 024.

The purpose is to add a second physical scheduled replay bundle under similar lab conditions so the comparison scaffold can summarize more than one validated run.

This is a repeat run, not a new reporting policy experiment.

## Relationship to previous milestones

The relevant evidence path is:

* v1.0: skipped-slot physical replay;
* v1.1: schedule-aware analysis;
* v1.2: manifest-bound reproduction;
* v1.3: run-bundle validation;
* v1.4: comparison scaffold;
* v1.5: Run 025 repeat-run design.

Run 025 exercises the same path with a second physical replay.

## Schedules

Run 025 used the same Run 022 schedules as Run 024:

* `traces/run022_reporting_txa_fixed_all_schedule.csv`
* `traces/run022_reporting_txb_usefulness_threshold_schedule.csv`

The corresponding firmware schedule headers were:

* `firmware/first_radio_link_TX-A/schedule_data_TXA.h`
* `firmware/first_radio_link_TX_B/schedule_data_TXB.h`

TXA/N01 used the fixed-all schedule.

TXB/N16 used the usefulness-threshold schedule.

## Logs and reports

Raw receiver log:

* `logs/rx_run_025_skipped_slot_replay_repeat.csv`

Parsed valid receiver log:

* `logs/parsed_run_025_skipped_slot_replay_repeat.csv`

Parsed rejects log:

* `logs/parsed_run_025_skipped_slot_replay_repeat_rejects.csv`

Schedule-aware reports:

* `reports/run025_schedule_aware_summary.json`
* `reports/run025_schedule_aware_summary.csv`

Manifest:

* `reports/run025_schedule_aware_manifest.json`

Updated multi-run comparison outputs:

* `reports/scheduled_replay_comparison.csv`
* `reports/scheduled_replay_comparison.json`

## Parser summary

The parser reported:

```
Valid packets:      552
Malformed packets:  0
```

Packets by transmitter and node:

| Transmitter | Node | Valid packets |
| ----------- | ---- | ------------: |
| TXA         | N01  |           368 |
| TXB         | N16  |           184 |

Sequence ranges:

| Node | Min sequence | Max sequence | Count |
| ---- | -----------: | -----------: | ----: |
| N01  |            0 |          369 |   368 |
| N16  |            0 |          184 |   184 |

Observed sequence gaps:

| Transmitter/node | Missing sequences |
| ---------------- | ----------------- |
| TXA/N01          | 71, 75            |
| TXB/N16          | 22                |

These are observed sequence gaps, not confirmed collisions.

## Radio metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -46.43 |    -52.0 |    -44.0 |     9.79 |     6.5 |   11.00 |
| N16  |    -51.64 |    -63.0 |    -48.0 |     9.74 |     9.0 |   10.75 |

## Usefulness summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     368 |           198.51 |           0.539 |         199.68 |         0.543 |
| N16  |     184 |           144.39 |           0.785 |         146.51 |         0.796 |

Approximate receiver inter-arrival time by node:

| Node | Mean seconds | Min seconds | Max seconds |
| ---- | -----------: | ----------: | ----------: |
| N01  |        1.005 |       0.987 |         2.0 |
| N16  |        2.011 |       1.988 |         4.0 |

These receiver inter-arrival values are useful for approximate observed spacing only. `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.

## Schedule-aware analysis

The manifest-bound schedule-aware analysis reproduced the Run 025 summary:

```
TXA/N01: 16/16 schedule rows SEND; 368 received packets; mean delivered usefulness 0.539
TXB/N16: 8/16 schedule rows SEND; 184 received packets; mean delivered usefulness 0.785
Observed received-packet ratio 0.5000; scheduled send-fraction ratio 0.5000.
Interpretation: received packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.
```

The observed TXB/TXA received-packet ratio was:

```
184 / 368 = 0.5000
```

The scheduled TXB/TXA send-fraction ratio was:

```
0.5 / 1.0 = 0.5000
```

## Bundle validation

Run 025 passed bundle validation:

```
Bundle validation PASSED: reports/run025_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The parsed rejects file contained no malformed packets. The validator was updated so an empty or whitespace-only rejects file is treated as zero malformed rows for rejects-file readability.

## Run 024 / Run 025 comparison

The comparison scaffold now summarizes two physical scheduled replay runs:

```
Runs summarized: 2
Transmitter rows: 4
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785
```

## Interpretation

Run 025 repeats the Run 024 skipped-slot pattern under similar lab conditions.

Across both runs, TXB used the usefulness-threshold schedule with half the scheduled SEND rows and produced about half the received packets of TXA, while retaining higher mean delivered usefulness per received packet.

The careful interpretation is:

> Run 025 provides a second physical scheduled replay consistent with the Run 024 skipped-slot pattern. In both runs, the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, while TXB retains higher mean delivered usefulness per received packet.

## Cautions

This result should not be overinterpreted.

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analysis compares schedule proportions and observed packet proportions.
* The analyzer does not infer exact transmitted packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* The appropriate wording is “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”

## Milestone contribution

Run 025 turns the v1.4 comparison scaffold from a single-run scaffold into a two-run comparison.

It strengthens the reproducible evidence path:

```
repeated physical scheduled replay
  → packet-centric parsing
  → schedule-aware analysis
  → manifest-bound reproduction
  → run-bundle validation
  → two-run comparison
```

The result remains bounded, but it is a stronger checkpoint than Run 024 alone.
