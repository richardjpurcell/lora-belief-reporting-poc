# Run 029 longer SD physical preparation

## 1. Purpose

This note documents the physical-preparation checkpoint for Run 029.

Milestone:

```
v3.1-run029-longer-sd-physical-prep
```

Branch:

```
exp046-run029-longer-sd-physical-prep
```

This milestone prepares the two-transmitter Run 029 longer SD replay for receiver logging. It does not yet document the receiver-side physical replay result.

## 2. Relationship to Run 029 schedule preparation

The previous milestone prepared and validated the Run 029 schedule artifacts:

```
v3.0-run029-longer-sd-schedule-prep
```

Run 029 target:

| TX  | Node | Rows | SEND rows | SKIP rows | Send fraction |
| --- | ---- | ---: | --------: | --------: | ------------: |
| TXA | N01  |   64 |        64 |         0 |        1.0000 |
| TXB | N16  |   64 |        32 |        32 |        0.5000 |

Expected scheduled TXB/TXA ratio:

```
0.5000
```

The validated SD schedule files are:

```
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
```

## 3. SD-card preparation

The validated SD schedules were copied to the board-oriented SD cards as `/schedule.csv`.

Expected card mapping:

| TX  | Node | SD volume  | Source file                         | SD destination  |
| --- | ---- | ---------- | ----------------------------------- | --------------- |
| TXA | N01  | `LORA_TXA` | `traces/run029_sd_txa_schedule.csv` | `/schedule.csv` |
| TXB | N16  | `LORA_TXB` | `traces/run029_sd_txb_schedule.csv` | `/schedule.csv` |

The repository remains the source of reproducible truth. The SD card is the physical replay medium.

## 4. Firmware run ID update

The transmitter firmware was updated for Run 029:

```
R28 -> R29
```

Firmware files:

```
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
```

The packet format remains unchanged.

The only intended firmware change for this prep milestone is the run identifier.

## 5. TXA startup check

TXA was booted with the Run 029 TXA SD card inserted.

Observed startup:

```
=== TX-A: LilyGO LoRa32 sender ===
LoRa init OK.
Initializing microSD replay schedule...
SD replay mode.
schedule_file=/schedule.csv
tx_id=TXA
node_id=N01
rows_loaded=64
send_rows=64
skip_rows=0
replay_period_rows=64
packet_format=existing
```

Example packets:

```
slot 0 demand_index 0 SEND sending: R29,TXA,N01,0,1627,A,1,0.75,0.72,5,F
slot 1 demand_index 1 SEND sending: R29,TXA,N01,1,2627,B,0,0.20,0.18,5,F
slot 2 demand_index 2 SEND sending: R29,TXA,N01,2,3627,C,1,0.81,0.78,5,F
```

TXA confirmed:

| Field              | Observed |
| ------------------ | -------: |
| rows loaded        |       64 |
| SEND rows          |       64 |
| SKIP rows          |        0 |
| replay period rows |       64 |
| run ID             |      R29 |

## 6. TXB startup check

TXB was booted with the Run 029 TXB SD card inserted.

Observed startup included:

```
skip_rows=32
replay_period_rows=64
packet_format=existing
```

Example slots:

```
slot 0 demand_index 0 SEND sending: R29,TXB,N16,0,2142,A,1,0.75,0.72,5,U
slot 1 demand_index 1 SKIP
slot 2 demand_index 2 SEND sending: R29,TXB,N16,1,4142,C,1,0.81,0.78,5,U
```

TXB confirmed:

| Field              | Observed |
| ------------------ | -------: |
| rows loaded        |       64 |
| SEND rows          |       32 |
| SKIP rows          |       32 |
| replay period rows |       64 |
| run ID             |      R29 |

## 7. Prep conclusion

Run 029 physical preparation is ready.

Confirmed startup target:

| TX  | Node | Rows loaded | SEND rows | SKIP rows |
| --- | ---- | ----------: | --------: | --------: |
| TXA | N01  |          64 |        64 |         0 |
| TXB | N16  |          64 |        32 |        32 |

The next step is receiver-side physical replay logging.

Expected later receiver log path:

```
logs/rx_run_029_longer_sd_replay.csv
```

Expected parsed outputs:

```
logs/parsed_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay_rejects.csv
```

Expected later manifest-bound analysis:

```
reports/run029_schedule_aware_manifest.json
reports/run029_schedule_aware_summary.csv
reports/run029_schedule_aware_summary.json
```

## 8. Cautions

This milestone confirms SD-card copying, firmware run ID, and transmitter startup row counts. It does not yet provide receiver-side delivery results.

The usual cautions remain:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analyzer compares schedule proportions and observed packet proportions.
* The analyzer does not infer exact transmitted-packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
* Do not claim energy savings unless current or power measurements are added.
