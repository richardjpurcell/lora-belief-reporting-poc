# Run 029 longer SD physical replay

## 1. Purpose

This note documents the Run 029 longer two-transmitter microSD-backed physical replay.

Milestone:

```
v3.2-run029-longer-sd-physical-replay
```

Branch:

```
exp047-run029-longer-sd-physical-replay
```

Run 029 tests whether the microSD-backed replay path continues to preserve scheduled-skipping behavior when the schedule length increases from 16 rows to 64 rows.

## 2. Relationship to previous milestones

Run 028 was the first successful microSD-backed physical replay. It used a 16-row loose-threshold schedule:

| TX  | Node | Rows | SEND rows | SKIP rows | Send fraction |
| --- | ---- | ---: | --------: | --------: | ------------: |
| TXA | N01  |   16 |        16 |         0 |        1.0000 |
| TXB | N16  |   16 |        12 |         4 |        0.7500 |

Run 029 extends the SD-backed workflow to a longer 64-row schedule while keeping the physical setup two-transmitter.

Run 029 target:

| TX  | Node | Rows | SEND rows | SKIP rows | Send fraction |
| --- | ---- | ---: | --------: | --------: | ------------: |
| TXA | N01  |   64 |        64 |         0 |        1.0000 |
| TXB | N16  |   64 |        32 |        32 |        0.5000 |

Expected scheduled TXB/TXA ratio:

```
0.5000
```

This run changes schedule length relative to Run 028. It does not change transmitter count.

## 3. Prepared schedule artifacts

Run 029 schedule artifacts were prepared in the preceding milestone:

```
v3.0-run029-longer-sd-schedule-prep
```

Full analysis-facing schedules:

```
traces/run029_reporting_txa_fixed_all_schedule.csv
traces/run029_reporting_txb_usefulness_threshold_schedule.csv
```

All-slot SD schedules:

```
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
```

The SD schedules passed validation:

| TX  | Rows | SEND rows | SKIP rows |
| --- | ---: | --------: | --------: |
| TXA |   64 |        64 |         0 |
| TXB |   64 |        32 |        32 |

The SD-card preparation and startup checks were documented in:

```
docs/development/run029_longer_sd_physical_prep.md
```

Confirmed startup target:

| TX  | Node | Rows loaded | SEND rows | SKIP rows | Run ID |
| --- | ---- | ----------: | --------: | --------: | ------ |
| TXA | N01  |          64 |        64 |         0 | R29    |
| TXB | N16  |          64 |        32 |        32 | R29    |

## 4. Receiver logging and parsing

Receiver log:

```
logs/rx_run_029_longer_sd_replay.csv
```

Parsed valid packets:

```
logs/parsed_run_029_longer_sd_replay.csv
```

Parsed rejects:

```
logs/parsed_run_029_longer_sd_replay_rejects.csv
```

Parser command:

```
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_029_longer_sd_replay.csv \
  --out logs/parsed_run_029_longer_sd_replay.csv \
  --seq-window 50
```

Parser summary:

| Quantity          | Value |
| ----------------- | ----: |
| Valid packets     |   719 |
| Malformed packets |     0 |
| TXA/N01 packets   |   478 |
| TXB/N16 packets   |   241 |

Packets by transmitter and node:

| TX  | Node | Received packets |
| --- | ---- | ---------------: |
| TXA | N01  |              478 |
| TXB | N16  |              241 |

Observed TXB/TXA received-packet ratio:

```
241 / 478 = 0.5042
```

This is close to the scheduled send-fraction ratio:

```
32 / 64 = 0.5000
```

## 5. Sequence gaps

Parser sequence summary:

| TX  | Node | Observed sequence range | Observed missing sequences |
| --- | ---- | ----------------------- | -------------------------- |
| TXA | N01  | 0--481                  | 123, 229, 260, 281         |
| TXB | N16  | 0--240                  | none                       |

These are observed sequence gaps only. They are not confirmed collisions and should not be interpreted as exact transmitted-packet loss.

## 6. Radio metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -43.35 |    -46.0 |    -41.0 |     9.63 |    8.75 |   10.50 |
| N16  |    -49.74 |    -56.0 |    -47.0 |     9.67 |    8.75 |   11.00 |

Approximate receiver inter-arrival time:

| Node | Mean seconds | Min seconds | Max seconds |
| ---- | -----------: | ----------: | ----------: |
| N01  |        1.008 |       0.999 |       2.001 |
| N16  |        2.000 |       1.999 |       2.005 |

The receiver inter-arrival summary is consistent with TXA sending every slot and TXB sending every other slot. It remains a receiver-side timing observation only. It is not a true synchronized latency measurement.

## 7. Usefulness summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     478 |           251.40 |           0.526 |         263.36 |         0.551 |
| N16  |     241 |           195.12 |           0.810 |         202.35 |         0.840 |

TXB/N16 delivered fewer packets than TXA/N01, as expected from the 32/64 schedule, while retaining higher mean delivered usefulness per received packet.

## 8. Manifest-bound schedule-aware analysis

Run 029 manifest:

```
reports/run029_schedule_aware_manifest.json
```

Manifest-bound analyzer command:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run029_schedule_aware_manifest.json
```

Generated outputs:

```
reports/run029_schedule_aware_summary.json
reports/run029_schedule_aware_summary.csv
```

Analyzer headline:

| TX  | Node | Schedule rows SEND | Received packets | Mean delivered usefulness |
| --- | ---- | -----------------: | ---------------: | ------------------------: |
| TXA | N01  |              64/64 |              478 |                     0.526 |
| TXB | N16  |              32/64 |              241 |                     0.810 |

Ratio result:

| Quantity                               |  Value |
| -------------------------------------- | -----: |
| Scheduled TXB/TXA send-fraction ratio  | 0.5000 |
| Observed TXB/TXA received-packet ratio | 0.5042 |

The analyzer interpretation was:

```
Observed received-packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.
```

## 9. Comparison through Run 029

The scheduled replay comparison was regenerated with Runs 024--029:

```
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
```

Comparison command:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --manifest reports/run025_schedule_aware_manifest.json \
  --manifest reports/run026_schedule_aware_manifest.json \
  --manifest reports/run027_schedule_aware_manifest.json \
  --manifest reports/run028_schedule_aware_manifest.json \
  --manifest reports/run029_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json
```

The comparison now summarizes 6 runs and 12 transmitter rows:

| Run    | TX  | Node | SEND rows | Received packets | Mean delivered usefulness |
| ------ | --- | ---- | --------: | ---------------: | ------------------------: |
| run024 | TXA | N01  |     16/16 |              361 |                     0.540 |
| run024 | TXB | N16  |      8/16 |              176 |                     0.786 |
| run025 | TXA | N01  |     16/16 |              368 |                     0.539 |
| run025 | TXB | N16  |      8/16 |              184 |                     0.785 |
| run026 | TXA | N01  |     16/16 |              504 |                     0.538 |
| run026 | TXB | N16  |      4/16 |              127 |                     0.866 |
| run027 | TXA | N01  |     16/16 |              400 |                     0.539 |
| run027 | TXB | N16  |     12/16 |              299 |                     0.667 |
| run028 | TXA | N01  |     16/16 |              378 |                     0.539 |
| run028 | TXB | N16  |     12/16 |              284 |                     0.668 |
| run029 | TXA | N01  |     64/64 |              478 |                     0.526 |
| run029 | TXB | N16  |     32/64 |              241 |                     0.810 |

Run 029 extends the medium 0.5 scheduled-ratio condition from a 16-row schedule to a 64-row SD-backed schedule.

## 10. Interpretation

Run 029 supports the following bounded interpretation:

> A longer 64-row microSD-backed schedule preserved the expected scheduled-skipping proportion under two-transmitter physical replay. TXB/N16 used a 32/64 usefulness-threshold schedule, produced an observed TXB/TXA received-packet ratio of 0.5042 against a scheduled ratio of 0.5000, and retained higher mean delivered usefulness per received packet than TXA/N01.

This is a longer-schedule SD replay result. It does not yet test transmitter-count scaling.

More specifically:

* TXA/N01 replayed a 64-row fixed-all schedule from microSD.
* TXB/N16 replayed a 64-row usefulness-threshold schedule from microSD.
* TXB/N16 had 32 SEND rows and 32 SKIP rows.
* The parser saw zero malformed packets.
* The observed TXB/TXA received-packet ratio was close to the scheduled send-fraction ratio.
* The receiver inter-arrival summaries matched the expected one-second versus two-second pattern.
* TXB/N16 retained higher mean delivered usefulness per received packet.

## 11. Cautions

The usual cautions remain important:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analyzer compares schedule proportions and observed packet proportions.
* The analyzer does not infer exact transmitted-packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Receiver inter-arrival summaries are receiver-side observations only.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
* Do not claim energy savings unless current or power measurements are added.
* Run 029 changes schedule length relative to Run 028, not transmitter count.
* Do not overgeneralize from this two-transmitter lab run.

## 12. Files added or updated

Run 029 physical replay artifacts:

```
logs/rx_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay_rejects.csv
reports/run029_schedule_aware_manifest.json
reports/run029_schedule_aware_summary.csv
reports/run029_schedule_aware_summary.json
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
docs/development/run029_longer_sd_physical_replay.md
```

## 13. Summary

Run 029 successfully completed the longer two-transmitter SD-backed physical replay.

Headline result:

| TX  | Node | Schedule                     | Received packets | Mean delivered usefulness |
| --- | ---- | ---------------------------- | ---------------: | ------------------------: |
| TXA | N01  | fixed-all, 64/64 SEND        |              478 |                     0.526 |
| TXB | N16  | medium threshold, 32/64 SEND |              241 |                     0.810 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.5000 |
| Observed TXB/TXA ratio  | 0.5042 |

Careful conclusion:

> Run 029 supports that the microSD-backed replay path can carry a longer 64-row scheduled-skipping replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.
