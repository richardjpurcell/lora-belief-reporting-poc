# microSD replay synthesis

## 1. Purpose

This note synthesizes the first microSD-backed replay phase in the `lora-belief-reporting-poc` repository.

The phase spans:

| Milestone                             | Role                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------- |
| `v2.3-microsd-replay-design`          | General design for conservative microSD-backed scheduled replay           |
| `v2.4-run028-microsd-replay-design`   | Run 028-specific design for replaying the Run 027-style schedule          |
| `v2.5-run028-microsd-firmware-prep`   | SD schedule generation, SD probe sketch, and TXA/TXB firmware preparation |
| `v2.6-run028-microsd-physical-replay` | First physical microSD-backed replay and manifest-bound analysis          |

The purpose of this synthesis is to clarify what was achieved, what was corrected, what the result supports, and what the next development route should be.

## 2. Current confirmed repository state

At the end of Run 028:

```
branch: main
origin/main up to date
working tree clean
HEAD: 8599fca Merge Run 028 microSD physical replay
tag: v2.6-run028-microsd-physical-replay
```

The first microSD-backed physical replay phase is now closed.

## 3. What changed

Before this phase, scheduled replay used compiled firmware headers:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

The transmitter sketches included those headers at compile time. To change a schedule, the schedule header had to be regenerated and the firmware had to be recompiled and reflashed.

After this phase, the TXA and TXB transmitter sketches can load a schedule from a microSD card:

```
/schedule.csv
```

The transmitter firmware now:

1. initializes LoRa;
2. initializes microSD;
3. opens `/schedule.csv`;
4. validates the expected SD CSV header;
5. loads schedule rows into RAM;
6. prints row counts at startup;
7. loops through the schedule rows;
8. sends only on `send=1`;
9. remains silent on `send=0`;
10. preserves the existing parser-facing packet format.

This changes the replay storage mechanism, not the packet format or analysis pipeline.

## 4. Important correction: compact CSV versus all-slot SD CSV

A key correction emerged during the phase.

The existing Run 027 compact CSVs:

```
traces/run027_reporting_txa_fixed_all_compact.csv
traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

were inspected and found to be SEND-only packet streams. They are not suitable as direct `/schedule.csv` files for SD replay because they omit SKIP rows.

For SD-backed scheduled replay, the firmware needs all schedule slots, including both SEND and SKIP rows.

Therefore, a new converter was added:

```
scripts/make_sd_schedule_csv.py
```

It converts a full analysis-facing schedule CSV into an all-slot firmware-facing SD CSV.

The generated Run 028 SD schedule files are:

```
traces/run028_sd_txa_schedule.csv
traces/run028_sd_txb_schedule.csv
```

These use the schema:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

where:

| `send` value | Meaning                 |
| -----------: | ----------------------- |
|          `1` | transmit this slot      |
|          `0` | remain silent this slot |

This correction is important because microSD replay must preserve scheduled silence, not merely replay the transmitted packet stream.

## 5. SD card convention

Two microSD cards were prepared:

| Transmitter | Node | Volume name | Root file       | Source                              |
| ----------- | ---- | ----------- | --------------- | ----------------------------------- |
| TXA         | N01  | `LORA_TXA`  | `/schedule.csv` | `traces/run028_sd_txa_schedule.csv` |
| TXB         | N16  | `LORA_TXB`  | `/schedule.csv` | `traces/run028_sd_txb_schedule.csv` |

The adopted convention is board-oriented rather than run-oriented.

The card belongs to the transmitter:

```
LORA_TXA
LORA_TXB
```

The schedule file changes per run:

```
/schedule.csv
```

The manifest records which repository schedule file was copied to which physical card.

This convention should scale better than naming cards after runs. For later 12-transmitter scaling, a numbered convention may be preferable:

```
LORA_TX01
LORA_TX02
...
LORA_TX12
LORA_SP01
LORA_SP02
```

For the current TXA/TXB phase, `LORA_TXA` and `LORA_TXB` are adequate and consistent with the existing firmware naming.

## 6. SD probe result

A small SD probe sketch was added:

```
firmware/sd_schedule_probe/sd_schedule_probe.ino
```

The probe tested SD initialization and reading `/schedule.csv` without involving LoRa transmission.

Both TXA and TXB SD cards were successfully read.

TXA probe result:

* SD initialized;
* `/schedule.csv` opened;
* TXA fixed-all `F` rows were visible.

TXB probe result:

* SD initialized;
* `/schedule.csv` opened;
* TXB usefulness-threshold `U` rows were visible;
* SKIP rows were present at demand indices `1`, `5`, `9`, and `13`.

This probe step was important because the microSD pin mapping is board-specific and should not be assumed without a physical check.

## 7. Firmware preparation result

The TXA and TXB firmware were patched to load schedules from microSD.

Firmware files:

```
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
```

The patched firmware was tested on hardware before the physical replay.

TXA startup confirmed:

| Field       | Observed |
| ----------- | -------: |
| rows loaded |       16 |
| SEND rows   |       16 |
| SKIP rows   |        0 |

TXB startup confirmed:

| Field       | Observed |
| ----------- | -------: |
| rows loaded |       16 |
| SEND rows   |       12 |
| SKIP rows   |        4 |

TXB also showed the expected skipped slots:

```
demand_index 1
demand_index 5
demand_index 9
demand_index 13
```

The packet payload format remained compatible with the existing parser.

## 8. Run 028 physical replay result

Run 028 was the first receiver-side microSD-backed physical replay.

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

Manifest-bound analysis:

```
reports/run028_schedule_aware_manifest.json
reports/run028_schedule_aware_summary.csv
reports/run028_schedule_aware_summary.json
```

Headline parser result:

| Quantity          | Value |
| ----------------- | ----: |
| Valid packets     |   662 |
| Malformed packets |     0 |
| TXA/N01 packets   |   378 |
| TXB/N16 packets   |   284 |

Headline schedule-aware result:

| TX  | Node | Schedule                    | Received packets | Mean delivered usefulness |
| --- | ---- | --------------------------- | ---------------: | ------------------------: |
| TXA | N01  | fixed-all, 16/16 SEND       |              378 |                     0.539 |
| TXB | N16  | loose threshold, 12/16 SEND |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

This is close to the Run 027 compiled-header loose-threshold result.

## 9. Run 027 versus Run 028

Run 027 used compiled firmware headers.

Run 028 used microSD-backed `/schedule.csv`.

Both used the same schedule semantics:

| Run     | Replay mechanism | TXA schedule | TXB schedule |
| ------- | ---------------- | ------------ | ------------ |
| Run 027 | compiled header  | 16/16 SEND   | 12/16 SEND   |
| Run 028 | microSD          | 16/16 SEND   | 12/16 SEND   |

Comparison:

| Run     | TXA received | TXB received | Scheduled TXB/TXA ratio | Observed TXB/TXA ratio | TXB mean usefulness |
| ------- | -----------: | -----------: | ----------------------: | ---------------------: | ------------------: |
| Run 027 |          400 |          299 |                  0.7500 |                 0.7475 |               0.667 |
| Run 028 |          378 |          284 |                  0.7500 |                 0.7513 |               0.668 |

Run 028 therefore supports the intended storage-mechanism check.

It does not prove exact equivalence between compiled-header replay and microSD replay. Physical LoRa reception varies across runs. The correct interpretation is that the expected scheduled-skipping pattern and usefulness pattern were preserved under similar two-transmitter lab conditions.

## 10. Updated Runs 024--028 comparison

The scheduled replay comparison was regenerated to include Run 028:

```
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
```

The comparison now covers 5 runs and 10 transmitter rows.

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

The threshold-family interpretation remains intact, and Run 028 adds evidence that the loose-threshold replay can be reproduced from microSD.

## 11. What this phase supports

This phase supports a bounded storage-mechanism interpretation:

> The Run 027-style scheduled-skipping semantics can move from compiled firmware headers to microSD-backed replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.

More specifically:

* the SD card can carry an all-slot schedule;
* the firmware can load `/schedule.csv` at startup;
* SEND/SKIP decisions can be preserved;
* the packet format can remain unchanged;
* the receiver logger can remain unchanged;
* the parser can remain unchanged;
* manifest-bound schedule-aware analysis can remain unchanged;
* Run 028 aligns closely with the Run 027 loose-threshold result.

This makes longer traces and future transmitter scaling more practical than the compiled-header approach.

## 12. What this phase does not support

This phase does not support claims that:

* exact transmitted-packet counts are known;
* observed sequence gaps are confirmed collisions;
* `recv_ms` and `tx_ms` provide true latency;
* energy savings were measured;
* airtime optimization was demonstrated;
* LoRaWAN behavior was tested;
* a live belief-maintenance controller was used;
* AWSRT-derived traces have already been physically replayed;
* the result generalizes beyond this small lab-run family.

The careful language remains:

> reduced physical transmission attempts under scheduled skipping

not:

> airtime optimization

and not:

> measured energy savings

## 13. Why microSD now matters

The compiled-header approach was useful for the early 16-row two-transmitter runs, but it becomes cumbersome as the project moves toward:

* longer traces;
* repeated physical replays;
* AWSRT-derived schedules;
* 3-transmitter tests;
* 6-transmitter tests;
* eventual 12 active transmitters plus 2 spare boards.

The microSD path separates firmware flashing from schedule swapping.

This makes future runs operationally simpler:

1. generate schedule artifacts in the repository;
2. generate all-slot SD schedule CSVs;
3. copy each schedule to the appropriate card as `/schedule.csv`;
4. confirm card identity and startup row counts;
5. run receiver logging;
6. parse logs;
7. analyze against manifest-bound repository artifacts.

The repository remains the source of reproducible truth. The SD card is the physical replay medium.

## 14. Near-term next routes

There are three plausible next routes.

### Route A: SD replay cleanup and documentation

This route would improve the workflow before adding complexity.

Possible tasks:

* add a README subsection describing SD-card preparation;
* document the card naming convention;
* add a helper command or script for copying schedules to mounted SD cards;
* add a validation check for all-slot SD CSVs;
* clarify the difference between SEND-only compact CSVs and all-slot SD CSVs;
* optionally add SD schedule files to run manifests more systematically.

This is low-risk and would improve reproducibility.

### Route B: longer two-transmitter SD replay

This route would keep two transmitters but increase schedule length.

Possible target:

* generate a longer all-slot schedule;
* replay it from SD;
* verify that loading and looping still behave correctly;
* compare against the 16-row Run 028 baseline.

This would test the practical reason for microSD without adding multi-transmitter complexity.

### Route C: first three-transmitter design

This route would begin scaling beyond TXA/TXB.

Possible target:

* design TXC/Nxx schedule and firmware/card convention;
* avoid physical replay until design is clear;
* preserve the same all-slot SD CSV schema;
* update manifests and comparison scripts if needed.

This is more ambitious and should probably begin as design-only.

## 15. Recommended next step

Recommended next step:

> Route A first: SD replay cleanup and documentation.

Reason:

Run 028 succeeded, but it revealed workflow details that should be captured before the next physical expansion:

* compact CSVs can be SEND-only and should not be confused with all-slot SD schedules;
* SD cards need board-oriented naming;
* `/schedule.csv` is the board-local replay file;
* startup row counts are important experiment checks;
* manifests should record both analysis-facing schedule CSVs and SD-facing schedule CSVs;
* the physical SD card is a replay medium, not the analysis source of truth.

A small cleanup milestone would make the next longer or multi-transmitter run less error-prone.

Potential next milestone:

```
v2.8-microsd-workflow-cleanup
```

Potential branch:

```
exp043-microsd-workflow-cleanup
```

Potential files:

```
README.md
docs/development/microsd_workflow_cleanup.md
```

## 16. Future path toward AWSRT-derived traces

The microSD path is a necessary bridge toward AWSRT-derived traces, but Run 028 itself does not use AWSRT-derived packets.

A future AWSRT-derived replay path should be:

1. generate or adapt AWSRT-derived demand traces;
2. produce full analysis-facing schedule CSVs;
3. convert full schedules into all-slot SD schedule CSVs;
4. place SD schedules on transmitter cards as `/schedule.csv`;
5. run point-to-point LoRa replay;
6. parse receiver logs;
7. analyze delivered packets against manifest-bound schedules;
8. compare delivery/usefulness behavior across schedule families.

At that stage, careful language will still be required. Unless a live controller is added, the physical system is replaying a precomputed schedule, not performing live belief maintenance.

## 17. Future path toward 12 active transmitters

The current hardware planning target is:

```
12 active transmitters
2 spare boards
```

The SD card convention should eventually move from lettered to numbered naming:

```
LORA_TX01
LORA_TX02
...
LORA_TX12
LORA_SP01
LORA_SP02
```

Each card should contain:

```
/schedule.csv
```

Each run manifest should bind:

* physical transmitter;
* node ID;
* SD volume name;
* SD source CSV;
* repository full schedule CSV;
* expected row count;
* expected SEND count;
* expected SKIP count;
* raw receiver log;
* parsed receiver log;
* summary outputs.

The Run 028 two-transmitter phase shows that this pattern is viable in principle, but it does not yet solve timing, interference, or coordination issues at 12 transmitters.

## 18. Summary

The microSD replay phase achieved its immediate goal.

It moved the project from compiled-header scheduled replay to microSD-backed scheduled replay while preserving:

* schedule semantics;
* SEND/SKIP behavior;
* packet format;
* receiver logger;
* parser;
* manifest-bound schedule-aware analysis;
* bounded interpretation language.

Run 028 result:

| TX  | Node | Schedule                    | Received packets | Mean delivered usefulness |
| --- | ---- | --------------------------- | ---------------: | ------------------------: |
| TXA | N01  | fixed-all, 16/16 SEND       |              378 |                     0.539 |
| TXB | N16  | loose threshold, 12/16 SEND |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

Final bounded conclusion:

> The first microSD-backed replay supports that scheduled-skipping semantics can be moved from compiled firmware headers to SD-card schedule files without disrupting the expected two-transmitter scheduled replay pattern under similar lab conditions.

The recommended next step is a small workflow-cleanup milestone before increasing trace length or transmitter count.
