# Run 032 six-transmitter physical replay

## Purpose

This note records the Run 032 six-transmitter physical replay result.

The run extends the four-transmitter Run 031 physical replay work to a six-transmitter physical replay using the Run 032 TXF bridge candidate prepared in `v4.7-run032-six-transmitter-physical-prep`.

The purpose of this milestone is to validate that six physical transmitters can replay the prepared SD-card schedules and produce receiver-side packet proportions close to the scheduled SEND ratios.

## Milestone

* Branch: `exp066-run032-six-transmitter-physical-replay`
* Previous tag: `v4.7-run032-six-transmitter-physical-prep`
* Intended tag: `v4.8-run032-six-transmitter-physical-replay`

## Physical transmitter set

| Transmitter | Node | Role                                     | Startup offset ms | Scheduled SEND rows | Scheduled SKIP rows |
| ----------- | ---: | ---------------------------------------- | ----------------: | ------------------: | ------------------: |
| TXD         |  N46 | very-strict threshold scheduled skipping |                 0 |                   8 |                  56 |
| TXA         |  N01 | fixed-all anchor                         |               500 |                  64 |                   0 |
| TXF         |  N76 | strict threshold scheduled skipping      |              2000 |                  16 |                  48 |
| TXB         |  N16 | medium threshold scheduled skipping      |              2750 |                  32 |                  32 |
| TXC         |  N31 | strict threshold scheduled skipping      |              4250 |                  16 |                  48 |
| TXE         |  N61 | medium threshold scheduled skipping      |              7250 |                  32 |                  32 |

The physical phase order was:

TXD -> TXA -> TXF -> TXB -> TXC -> TXE

## SD-card preparation

Each transmitter SD card was updated with its Run 032 all-slot schedule as `/schedule.csv`.

| Card     | Source schedule                     | Verified rows | Verified SEND | Verified SKIP |
| -------- | ----------------------------------- | ------------: | ------------: | ------------: |
| LORA_TXA | `traces/run032_sd_txa_schedule.csv` |            64 |            64 |             0 |
| LORA_TXB | `traces/run032_sd_txb_schedule.csv` |            64 |            32 |            32 |
| LORA_TXC | `traces/run032_sd_txc_schedule.csv` |            64 |            16 |            48 |
| LORA_TXD | `traces/run032_sd_txd_schedule.csv` |            64 |             8 |            56 |
| LORA_TXE | `traces/run032_sd_txe_schedule.csv` |            64 |            32 |            32 |
| LORA_TXF | `traces/run032_sd_txf_schedule.csv` |            64 |            16 |            48 |

Two previously unnamed cards were renamed to the common naming pattern:

* `NO NAME` -> `LORA_TXE`
* `NO NAME` -> `LORA_TXF`

## Firmware startup checks

All six transmitters were flashed or confirmed with Run 032 firmware identity and their SD-card schedule counts.

| Transmitter | Node | Firmware RUN_ID | Startup offset ms | Rows loaded | SEND rows | SKIP rows |
| ----------- | ---: | --------------: | ----------------: | ----------: | --------: | --------: |
| TXD         |  N46 |             R32 |                 0 |          64 |         8 |        56 |
| TXA         |  N01 |             R32 |               500 |          64 |        64 |         0 |
| TXF         |  N76 |             R32 |              2000 |          64 |        16 |        48 |
| TXB         |  N16 |             R32 |              2750 |          64 |        32 |        32 |
| TXC         |  N31 |             R32 |              4250 |          64 |        16 |        48 |
| TXE         |  N61 |             R32 |              7250 |          64 |        32 |        32 |

A TXD startup check initially showed `R31` in transmitted packets. TXD was reflashed with the Run 032 sketch and then confirmed as `R32`.

TXE initially failed to upload because the ESP32 did not enter download mode. The upload was retried successfully, and TXE was then confirmed as `R32`.

## Receiver logging

Receiver serial port:

`/dev/cu.usbserial-576B0005451`

Raw receiver log:

`logs/rx_run_032_six_transmitter_sd_replay.csv`

Parsed receiver log:

`logs/parsed_run_032_six_transmitter_sd_replay.csv`

Reject log:

`logs/parsed_run_032_six_transmitter_sd_replay_rejects.csv`

Parser result:

* Valid packets: 1156
* Malformed packets: 0

## Receiver-side packet counts

| Transmitter | Node | Received valid packets | Observed sequence min | Observed sequence max | Missing observed transmitted sequences |
| ----------- | ---: | ---------------------: | --------------------: | --------------------: | -------------------------------------- |
| TXA         |  N01 |                    442 |                     0 |                   441 | none                                   |
| TXB         |  N16 |                    220 |                     0 |                   219 | none                                   |
| TXC         |  N31 |                    110 |                     0 |                   109 | none                                   |
| TXD         |  N46 |                     55 |                     0 |                    54 | none                                   |
| TXE         |  N61 |                    219 |                     0 |                   218 | none                                   |
| TXF         |  N76 |                    110 |                     0 |                   109 | none                                   |

## Expected-vs-observed receiver-side ratios

Ratios are reported relative to the fixed-all TXA anchor.

| Ratio   | Observed receiver-side ratio | Expected scheduled ratio | Difference |
| ------- | ---------------------------: | -----------------------: | ---------: |
| TXB/TXA |                       0.4977 |                   0.5000 |    -0.0023 |
| TXC/TXA |                       0.2489 |                   0.2500 |    -0.0011 |
| TXD/TXA |                       0.1244 |                   0.1250 |    -0.0006 |
| TXE/TXA |                       0.4955 |                   0.5000 |    -0.0045 |
| TXF/TXA |                       0.2489 |                   0.2500 |    -0.0011 |

## Manifest analysis and validation

Analyzer outputs:

* `outputs/run032_six_transmitter_manifest_replay_summary.json`
* `outputs/run032_six_transmitter_manifest_replay_summary.csv`

Validation output:

* `outputs/run032_six_transmitter_manifest_replay_validation.json`

The validator result after adding the validator-compatible `expected_scheduled_ratios` manifest key was:

* Validation summary: 171/171 checks passed; 0 failed.

## Interpretation

This run validates the Run 032 six-transmitter physical replay bundle at the receiver-log level.

The observed receiver-side packet counts closely follow the scheduled SEND-row ratios relative to TXA. No malformed packets were recorded, and no missing observed transmitted sequences were reported for any of the six transmitters.

This supports the limited claim that the prepared six-transmitter SD replay setup can produce receiver-side packet proportions consistent with the configured scheduled skipping ratios under this physical bench run.

## Interpretation boundaries

This result does not establish:

* exact physical transmitted-packet counts;
* confirmed RF collisions or absence of RF collisions;
* synchronized latency measurements;
* LoRaWAN behavior;
* airtime or energy optimization;
* live-controller behavior;
* behavior for eight or twelve transmitters;
* operational wildfire or deployment behavior.

Startup offsets are programmed bench-start phases for this replay setup. They should not be interpreted as synchronized MAC timing, collision avoidance guarantees, or latency coordination.
