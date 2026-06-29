# Run 028 microSD-backed physical replay

## 1. Purpose

Run 028 is the first physical replay in this repository to use microSD-backed schedule storage instead of compiled firmware schedule headers.

The purpose of this run is narrow and conservative:

> Test whether the Run 027-style loose-threshold schedule semantics can be replayed from microSD while preserving the existing scheduled-skipping interpretation, packet format, receiver logger, parser, and manifest-bound analysis pipeline.

Run 028 changes the storage and replay mechanism only. It does not change the underlying schedule semantics.

Milestone:

```
v2.6-run028-microsd-physical-replay
```

Branch:

```
exp041-run028-microsd-physical-replay
```

## 2. Relationship to previous milestones

The preceding milestones established the design and firmware preparation path:

| Milestone                             | Role                                                                 |
| ------------------------------------- | -------------------------------------------------------------------- |
| `v2.3-microsd-replay-design`          | General design for conservative microSD-backed replay                |
| `v2.4-run028-microsd-replay-design`   | Run 028-specific design for replaying the Run 027-style schedule     |
| `v2.5-run028-microsd-firmware-prep`   | SD CSV generation, SD probe sketch, and TXA/TXB firmware preparation |
| `v2.6-run028-microsd-physical-replay` | First physical receiver-side Run 028 replay and analysis             |

Run 028 builds directly on Run 027.

Run 027 used compiled firmware headers:

| Run     | Replay mechanism          | TXA schedule          | TXB schedule                           |
| ------- | ------------------------- | --------------------- | -------------------------------------- |
| Run 027 | compiled firmware headers | fixed-all, 16/16 SEND | loose usefulness threshold, 12/16 SEND |

Run 028 uses microSD-backed schedule CSVs:

| Run     | Replay mechanism        | TXA schedule          | TXB schedule                           |
| ------- | ----------------------- | --------------------- | -------------------------------------- |
| Run 028 | microSD `/schedule.csv` | fixed-all, 16/16 SEND | loose usefulness threshold, 12/16 SEND |

The intended comparison is therefore not a new threshold-family point. It is a storage/replay-mechanism check.

## 3. Important correction from the design phase

During firmware preparation, the existing Run 027 compact CSVs were inspected and found to be SEND-only compact packet streams.

Those files are useful for earlier workflows, but they are not suitable as `/schedule.csv` files for SD replay because they omit SKIP rows.

The correct microSD replay source files are the newly generated all-slot SD schedule CSVs:

```
traces/run028_sd_txa_schedule.csv
traces/run028_sd_txb_schedule.csv
```

These preserve all 16 schedule slots.

TXA SD schedule:

| Rows | SEND rows | SKIP rows |
| ---: | --------: | --------: |
|   16 |        16 |         0 |

TXB SD schedule:

| Rows | SEND rows | SKIP rows |
| ---: | --------: | --------: |
|   16 |        12 |         4 |

TXB SKIP demand indices:

```
1, 5, 9, 13
```

This correction matters because microSD replay must preserve scheduled silence, not merely replay the transmitted packet stream.

## 4. SD card preparation

Two SD cards were prepared.

### TXA card

| Field                | Value                               |
| -------------------- | ----------------------------------- |
| Physical transmitter | TXA                                 |
| Node                 | N01                                 |
| Volume name          | `LORA_TXA`                          |
| SD path              | `/schedule.csv`                     |
| Repository source    | `traces/run028_sd_txa_schedule.csv` |
| Expected rows        | 16                                  |
| Expected SEND rows   | 16                                  |
| Expected SKIP rows   | 0                                   |

### TXB card

| Field                | Value                               |
| -------------------- | ----------------------------------- |
| Physical transmitter | TXB                                 |
| Node                 | N16                                 |
| Volume name          | `LORA_TXB`                          |
| SD path              | `/schedule.csv`                     |
| Repository source    | `traces/run028_sd_txb_schedule.csv` |
| Expected rows        | 16                                  |
| Expected SEND rows   | 12                                  |
| Expected SKIP rows   | 4                                   |

The card-volume naming convention is board-oriented rather than run-oriented:

| Convention      | Meaning                                       |
| --------------- | --------------------------------------------- |
| `LORA_TXA`      | SD card assigned to TXA                       |
| `LORA_TXB`      | SD card assigned to TXB                       |
| `/schedule.csv` | Board-local schedule file for the current run |

This keeps the physical card identity stable while allowing `/schedule.csv` to change across runs.

## 5. SD probe results

A small SD schedule probe sketch was added during firmware preparation:

```
firmware/sd_schedule_probe/sd_schedule_probe.ino
```

The probe confirmed that each board could initialize the SD card, open `/schedule.csv`, and read the expected rows.

TXA probe confirmed that the TXA card was readable and contained the fixed-all `F` policy rows.

TXB probe confirmed that the TXB card was readable and contained the loose-threshold `U` policy rows, including SKIP rows at demand indices:

```
1, 5, 9, 13
```

This confirmed the SD read path before using the full LoRa transmitter firmware.

## 6. Firmware behavior

The TXA and TXB firmware were patched during `v2.5-run028-microsd-firmware-prep`.

The transmitter firmware now:

1. initializes LoRa;
2. initializes microSD;
3. opens `/schedule.csv`;
4. validates the expected SD CSV header;
5. loads schedule rows into RAM;
6. prints row counts at startup;
7. loops through the schedule rows;
8. sends only on rows with `send=1`;
9. remains silent on rows with `send=0`;
10. preserves the existing parser-facing packet format.

The SD schedule schema is:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

The packet payload format remains:

```
RUN_ID,TX_ID,NODE_ID,seq,tx_ms,region,event,priority,usefulness,stale_after,policy
```

For Run 028, `RUN_ID` is:

```
R28
```

## 7. Transmitter startup checks

### TXA startup

TXA loaded the microSD schedule successfully:

| Field                | Observed value |
| -------------------- | -------------- |
| `tx_id`              | `TXA`          |
| `node_id`            | `N01`          |
| `rows_loaded`        | 16             |
| `send_rows`          | 16             |
| `skip_rows`          | 0              |
| `replay_period_rows` | 16             |

Example TXA packet output:

```
R28,TXA,N01,0,1604,A,1,0.95,0.92,5,F
R28,TXA,N01,1,2604,B,0,0.20,0.18,5,F
R28,TXA,N01,2,3604,C,1,0.88,0.84,5,F
```

### TXB startup

TXB loaded the microSD schedule successfully:

| Field                | Observed value |
| -------------------- | -------------- |
| `tx_id`              | `TXB`          |
| `node_id`            | `N16`          |
| `rows_loaded`        | 16             |
| `send_rows`          | 12             |
| `skip_rows`          | 4              |
| `replay_period_rows` | 16             |

TXB showed the expected SEND/SKIP behavior:

```
slot 0 demand_index 0 SEND
slot 1 demand_index 1 SKIP
slot 2 demand_index 2 SEND
slot 3 demand_index 3 SEND
slot 4 demand_index 4 SEND
slot 5 demand_index 5 SKIP
slot 9 demand_index 9 SKIP
slot 13 demand_index 13 SKIP
```

TXB also wrapped correctly after the 16-row schedule period.

## 8. Receiver log and parser output

Receiver log:

```
logs/rx_run_028_microsd_replay.csv
```

Parsed valid packets:

```
logs/parsed_run_028_microsd_replay.csv
```

Parsed rejects:

```
logs/parsed_run_028_microsd_replay_rejects.csv
```

Parser command:

```
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_028_microsd_replay.csv \
  --out logs/parsed_run_028_microsd_replay.csv \
  --seq-window 50
```

Parser summary:

| Quantity          | Value |
| ----------------- | ----: |
| Valid packets     |   662 |
| Malformed packets |     0 |
| TXA/N01 packets   |   378 |
| TXB/N16 packets   |   284 |

Packets by transmitter and node:

| TX  | Node | Received packets |
| --- | ---- | ---------------: |
| TXA | N01  |              378 |
| TXB | N16  |              284 |

Sequence gaps:

| TX  | Node | Observed missing sequences |
| --- | ---- | -------------------------- |
| TXA | N01  | `170`                      |
| TXB | N16  | none                       |

The TXA sequence gap is an observed sequence gap only. It is not evidence of a confirmed collision or exact transmitted-packet loss.

## 9. Radio metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -54.17 |    -74.0 |    -43.0 |     9.68 |    8.75 |   11.75 |
| N16  |    -59.15 |    -81.0 |    -46.0 |     9.72 |    9.00 |   10.50 |

Approximate receiver inter-arrival time:

| Node | Mean seconds | Min seconds | Max seconds |
| ---- | -----------: | ----------: | ----------: |
| N01  |        1.003 |       0.999 |       2.000 |
| N16  |        1.336 |       0.999 |       2.001 |

These inter-arrival values are receiver-side observations. They should not be interpreted as true latency because `recv_ms` and `tx_ms` are not synchronized across boards.

## 10. Usefulness summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     378 |           203.77 |           0.539 |         204.89 |         0.542 |
| N16  |     284 |           189.81 |           0.668 |         190.47 |         0.671 |

As expected, TXB delivered fewer packets than TXA but retained higher mean delivered usefulness per received packet.

## 11. Manifest-bound schedule-aware analysis

Run 028 manifest:

```
reports/run028_schedule_aware_manifest.json
```

Manifest-bound analyzer command:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run028_schedule_aware_manifest.json
```

Generated outputs:

```
reports/run028_schedule_aware_summary.json
reports/run028_schedule_aware_summary.csv
```

Analyzer summary:

| Transmitter | Node | Schedule rows SEND | Received packets | Mean delivered usefulness |
| ----------- | ---- | -----------------: | ---------------: | ------------------------: |
| TXA         | N01  |              16/16 |              378 |                     0.539 |
| TXB         | N16  |              12/16 |              284 |                     0.668 |

Observed and scheduled ratios:

| Quantity                               |  Value |
| -------------------------------------- | -----: |
| Scheduled TXB/TXA send-fraction ratio  | 0.7500 |
| Observed TXB/TXA received-packet ratio | 0.7513 |

The analyzer interpretation was:

> Observed received-packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.

## 12. Comparison with Runs 024--028

The scheduled replay comparison was regenerated to include Run 028.

Comparison command:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --manifest reports/run025_schedule_aware_manifest.json \
  --manifest reports/run026_schedule_aware_manifest.json \
  --manifest reports/run027_schedule_aware_manifest.json \
  --manifest reports/run028_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json
```

Generated outputs:

```
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
```

The comparison summarized 5 runs and 10 transmitter rows.

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

Run 028 aligns closely with the Run 027 loose-threshold point while changing the replay mechanism from compiled headers to microSD.

## 13. Run 027 versus Run 028

Run 027:

| TX      | Schedule   | Received packets | Mean delivered usefulness |
| ------- | ---------- | ---------------: | ------------------------: |
| TXA/N01 | 16/16 SEND |              400 |                     0.539 |
| TXB/N16 | 12/16 SEND |              299 |                     0.667 |

Run 028:

| TX      | Schedule   | Received packets | Mean delivered usefulness |
| ------- | ---------- | ---------------: | ------------------------: |
| TXA/N01 | 16/16 SEND |              378 |                     0.539 |
| TXB/N16 | 12/16 SEND |              284 |                     0.668 |

Ratio comparison:

| Run     | Scheduled TXB/TXA ratio | Observed TXB/TXA ratio |
| ------- | ----------------------: | ---------------------: |
| Run 027 |                  0.7500 |                 0.7475 |
| Run 028 |                  0.7500 |                 0.7513 |

This supports the intended storage-mechanism check.

Run 028 should be interpreted as a successful microSD-backed replay of the Run 027-style schedule semantics under similar two-transmitter lab conditions.

## 14. Interpretation

Run 028 supports the following bounded interpretation:

> The Run 027-style loose-threshold schedule semantics can be replayed from microSD while preserving the expected scheduled-skipping ratio and parser-facing packet format under similar two-transmitter lab conditions.

More specifically:

* TXA/N01 replayed the fixed-all schedule from microSD with 16/16 SEND rows.
* TXB/N16 replayed the loose-threshold schedule from microSD with 12/16 SEND rows.
* The observed TXB/TXA received-packet ratio was 0.7513, close to the scheduled send-fraction ratio of 0.7500.
* TXB retained higher mean delivered usefulness per received packet than TXA.
* The parser and manifest-bound analyzer required no SD-specific packet-format changes.

This is a useful bridge toward longer traces, AWSRT-derived schedules, and future 3 → 6 → 12 transmitter scaling.

## 15. Cautions

The following cautions remain important:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analyzer compares schedule proportions and observed packet proportions.
* The analyzer does not infer exact transmitted-packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* Run 028 changes the storage and replay mechanism, not the underlying schedule semantics.
* Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
* Do not claim energy savings unless current or power measurements are added.
* Do not overgeneralize from this small two-transmitter lab-run family.

## 16. Files added or updated

Run 028 physical replay artifacts:

```
logs/rx_run_028_microsd_replay.csv
logs/parsed_run_028_microsd_replay.csv
logs/parsed_run_028_microsd_replay_rejects.csv
reports/run028_schedule_aware_manifest.json
reports/run028_schedule_aware_summary.csv
reports/run028_schedule_aware_summary.json
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
docs/development/run028_microsd_replay.md
```

Earlier firmware-prep artifacts used by this run:

```
scripts/make_sd_schedule_csv.py
traces/run028_sd_txa_schedule.csv
traces/run028_sd_txb_schedule.csv
firmware/sd_schedule_probe/sd_schedule_probe.ino
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
```

## 17. Summary

Run 028 successfully completed the first microSD-backed physical scheduled replay.

Headline result:

| TX  | Node | Schedule                    | Received packets | Mean delivered usefulness |
| --- | ---- | --------------------------- | ---------------: | ------------------------: |
| TXA | N01  | fixed-all, 16/16 SEND       |              378 |                     0.539 |
| TXB | N16  | loose threshold, 12/16 SEND |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

Careful conclusion:

> Run 028 supports a bounded storage-mechanism interpretation: the Run 027-style scheduled-skipping semantics can move from compiled firmware headers to microSD-backed replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.

This completes the first SD-card replay bridge and prepares the project for longer schedule traces and future transmitter scaling.
