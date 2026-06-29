# Longer SD replay synthesis

## 1. Purpose

This note synthesizes the microSD-backed replay phase through Run 029.

Milestone:

```
v3.3-longer-sd-replay-synthesis
```

Branch:

```
exp048-longer-sd-replay-synthesis
```

The purpose is to summarize what Runs 028 and 029 establish, clarify what remains unproven, and identify the next scaling step.

This is a synthesis milestone only. It does not add a new physical LoRa run.

## 2. Context

The project has moved from compiled schedule replay to microSD-backed schedule replay.

Earlier threshold-family runs established that scheduled skipping changes the observed received-packet proportion in the expected direction while preserving higher mean delivered usefulness per received packet for the threshold-selected stream.

The microSD phase asks a narrower implementation question:

> Can the same scheduled-skipping semantics be moved from compiled firmware artifacts to board-local `/schedule.csv` files on microSD?

Runs 028 and 029 answer this under bounded two-transmitter lab conditions.

## 3. MicroSD replay mechanism

The SD replay mechanism uses an all-slot schedule file:

```
/schedule.csv
```

Expected schema:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

The `send` column controls whether a schedule row produces a transmission:

| send value | Meaning                     |
| ---------: | --------------------------- |
|          1 | transmit this slot          |
|          0 | remain silent for this slot |

This is the key distinction from SEND-only compact traces.

The SD schedule CSV is the firmware-facing replay artifact. The SEND-only compact CSVs remain analysis or compatibility artifacts and should not be copied to the SD card as `/schedule.csv`.

## 4. Run 028 result

Run 028 was the first successful microSD-backed physical replay.

Run 028 target:

| TX  | Node | Schedule        | SEND rows | SKIP rows | Send fraction |
| --- | ---- | --------------- | --------: | --------: | ------------: |
| TXA | N01  | fixed-all       |     16/16 |      0/16 |        1.0000 |
| TXB | N16  | loose threshold |     12/16 |      4/16 |        0.7500 |

Run 028 result:

| TX  | Node | Received packets | Mean delivered usefulness |
| --- | ---- | ---------------: | ------------------------: |
| TXA | N01  |              378 |                     0.539 |
| TXB | N16  |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

Careful Run 028 interpretation:

> Run 028 supports that Run 027-style scheduled-skipping semantics can move from compiled firmware headers to microSD-backed replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.

## 5. Run 029 result

Run 029 extended the microSD-backed replay from a 16-row schedule to a 64-row schedule while keeping the physical setup two-transmitter.

Run 029 target:

| TX  | Node | Schedule         | SEND rows | SKIP rows | Send fraction |
| --- | ---- | ---------------- | --------: | --------: | ------------: |
| TXA | N01  | fixed-all        |     64/64 |      0/64 |        1.0000 |
| TXB | N16  | medium threshold |     32/64 |     32/64 |        0.5000 |

Run 029 result:

| TX  | Node | Received packets | Mean delivered usefulness |
| --- | ---- | ---------------: | ------------------------: |
| TXA | N01  |              478 |                     0.526 |
| TXB | N16  |              241 |                     0.810 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.5000 |
| Observed TXB/TXA ratio  | 0.5042 |

Parser result:

| Quantity          | Value |
| ----------------- | ----: |
| Valid packets     |   719 |
| Malformed packets |     0 |

Receiver inter-arrival summaries:

| Node | Mean receiver inter-arrival |
| ---- | --------------------------: |
| N01  |                     1.008 s |
| N16  |                     2.000 s |

These timing values are receiver-side observations only. They are not synchronized latency measurements.

Careful Run 029 interpretation:

> Run 029 supports that the microSD-backed replay path can carry a longer 64-row scheduled-skipping replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.

## 6. Comparison through Run 029

The scheduled replay comparison now covers Runs 024--029.

| Run    | TX  | Node | Schedule SEND rows | Received packets | Mean delivered usefulness |
| ------ | --- | ---- | -----------------: | ---------------: | ------------------------: |
| run024 | TXA | N01  |              16/16 |              361 |                     0.540 |
| run024 | TXB | N16  |               8/16 |              176 |                     0.786 |
| run025 | TXA | N01  |              16/16 |              368 |                     0.539 |
| run025 | TXB | N16  |               8/16 |              184 |                     0.785 |
| run026 | TXA | N01  |              16/16 |              504 |                     0.538 |
| run026 | TXB | N16  |               4/16 |              127 |                     0.866 |
| run027 | TXA | N01  |              16/16 |              400 |                     0.539 |
| run027 | TXB | N16  |              12/16 |              299 |                     0.667 |
| run028 | TXA | N01  |              16/16 |              378 |                     0.539 |
| run028 | TXB | N16  |              12/16 |              284 |                     0.668 |
| run029 | TXA | N01  |              64/64 |              478 |                     0.526 |
| run029 | TXB | N16  |              32/64 |              241 |                     0.810 |

This comparison preserves the threshold-family pattern while adding evidence that the replay mechanism can be SD-backed.

## 7. What the SD replay phase establishes

The SD replay phase establishes three bounded points.

First, SD-backed schedule loading works for the original 16-row replay condition.

Run 028 loaded `/schedule.csv` from the TXA and TXB microSD cards and preserved the expected 12/16 versus 16/16 received-packet proportion.

Second, SD-backed schedule loading works for a longer 64-row replay condition.

Run 029 loaded 64-row schedules and preserved the expected 32/64 versus 64/64 received-packet proportion.

Third, the storage mechanism is no longer the main immediate uncertainty.

The next technical uncertainty is not whether a transmitter can replay an all-slot schedule from SD. The next uncertainty is how the physical LoRa link behaves when more transmitters participate.

## 8. What remains unproven

The SD replay phase does not establish broad scalability.

It does not yet show:

* three or more transmitters operating together;
* the planned 12-transmitter platform;
* exact transmitted-packet counts;
* confirmed collision counts;
* LoRaWAN behavior;
* synchronized latency;
* airtime optimization;
* energy savings;
* live belief-controller behavior;
* real adaptive policy behavior;
* operational wildfire or field deployment behavior.

The correct wording remains:

> reduced physical transmission attempts under scheduled skipping

not:

> airtime optimization

Energy claims should not be made unless current or power measurements are added.

## 9. Current interpretation boundary

The strongest safe statement after Run 029 is:

> Under similar two-transmitter lab conditions, microSD-backed all-slot schedule replay preserved the expected scheduled-skipping received-packet proportions for both a 16-row loose-threshold condition and a 64-row medium-threshold condition, while the threshold-selected stream retained higher mean delivered usefulness per received packet than the fixed-all stream.

This is a storage-and-replay result, not a network-scaling result.

## 10. Recommended next step

The next recommended experimental step is a small multi-transmitter expansion.

Do not jump immediately to the full 12-transmitter target.

A reasonable next physical step is:

```
three-transmitter SD-backed replay
```

Suggested structure:

| TX  | Role                                        | Schedule idea                            |
| --- | ------------------------------------------- | ---------------------------------------- |
| TXA | fixed-all baseline                          | 64/64 SEND                               |
| TXB | medium threshold                            | 32/64 SEND                               |
| TXC | strict threshold or phase-shifted threshold | lower SEND fraction or offset SEND slots |

The purpose should be to test whether the manifest-bound schedule-aware analysis and receiver logging remain readable when an additional transmitter is present.

The first multi-transmitter run should keep everything else conservative:

* same packet format;
* same receiver logger;
* same parser;
* same manifest-bound analyzer style;
* same 64-row schedule length;
* no live controller;
* no energy measurement;
* no claims about scalability beyond the run.

## 11. Proposed milestone sequence

Recommended next milestones:

```
v3.4-three-transmitter-sd-replay-design
v3.5-three-transmitter-sd-schedule-prep
v3.6-three-transmitter-sd-physical-prep
v3.7-three-transmitter-sd-physical-replay
```

This separates design, artifact preparation, physical startup checks, and receiver-side replay.

That separation has worked well for the Run 028 and Run 029 SD replay phase and should be kept for the first multi-transmitter expansion.

## 12. Summary

Runs 028 and 029 complete the first SD-backed replay phase.

Summary:

| Run     | Main question                                | Result                                    |
| ------- | -------------------------------------------- | ----------------------------------------- |
| Run 028 | Can the 16-row schedule move to SD replay?   | Yes, under two-transmitter lab conditions |
| Run 029 | Can a longer 64-row schedule replay from SD? | Yes, under two-transmitter lab conditions |

The main conclusion is:

> The project can now treat microSD-backed all-slot schedule replay as the preferred mechanism for the next physical experiments.

The next risk to study is multi-transmitter physical interaction, not basic SD schedule storage.
