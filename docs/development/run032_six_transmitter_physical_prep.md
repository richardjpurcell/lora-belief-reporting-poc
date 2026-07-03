# Run 032 Six-Transmitter Physical Preparation

## Purpose

This milestone prepares a six-transmitter Run 032 physical replay candidate.

It follows:

* `v4.6-run032-six-transmitter-phase-bridge`

This milestone is physical preparation only.

It does not copy schedules to SD cards.

It does not flash hardware.

It does not run the receiver logger.

It does not collect receiver logs.

It does not parse physical packets.

It does not report observed receiver-side packet proportions.

It does not make six-transmitter physical replay claims.

The purpose is to prepare the repository-side schedules, phase-plan choice, firmware identities, and physical-prep checklist so that a later physical replay milestone can begin from a clean, documented setup.

## Current milestone

This note belongs to:

* `v4.7-run032-six-transmitter-physical-prep`

Branch:

* `exp065-run032-six-transmitter-physical-prep`

Status:

* Physical-preparation milestone

## Basis

The v4.6 milestone created a six-transmitter bridge from the optimized 250 ms-grid twelve-transmitter phase-plan candidate.

The original v4.6 bridge used:

* TXD/N46
* TXA/N01
* TXB/N16
* TXG/N91
* TXC/N31
* TXE/N61

During v4.7 preparation, a second six-transmitter bridge candidate was created using TXF instead of TXG:

* `traces/run032_six_tx_phase_plan_bridge_txf.csv`
* `outputs/run032_six_tx_phase_plan_bridge_txf_summary.json`
* `outputs/run032_six_tx_phase_plan_bridge_txf_summary.csv`

Both the TXG and TXF six-transmitter bridge candidates produced zero analyzer risk flags under the current simplified phase-plan diagnostic.

The TXF candidate was selected for physical preparation because it preserves a more natural physical identity sequence:

* TXA/N01
* TXB/N16
* TXC/N31
* TXD/N46
* TXE/N61
* TXF/N76

The TXF choice is a physical-prep convenience and does not imply that TXF is physically validated.

## Selected six-transmitter physical-prep candidate

The selected physical-prep candidate is:

| Transmitter | Node | Role                                     | Startup offset |
| ----------- | ---: | ---------------------------------------- | -------------: |
| TXD         |  N46 | very-strict threshold scheduled skipping |           0 ms |
| TXA         |  N01 | fixed-all anchor                         |         500 ms |
| TXF         |  N76 | strict threshold scheduled skipping      |        2000 ms |
| TXB         |  N16 | medium threshold scheduled skipping      |        2750 ms |
| TXC         |  N31 | strict threshold scheduled skipping      |        4250 ms |
| TXE         |  N61 | medium threshold scheduled skipping      |        7250 ms |

Composition:

| Group                          | Count |
| ------------------------------ | ----: |
| fixed-all anchor               |     1 |
| medium scheduled skipping      |     2 |
| strict scheduled skipping      |     2 |
| very-strict scheduled skipping |     1 |
| total transmitters             |     6 |

Analyzer summary for the TXF candidate:

| Diagnostic             | Result |
| ---------------------- | -----: |
| transmitter count      |      6 |
| fixed-all anchor count |      1 |
| risk flags             |      0 |

## Schedule preparation

Run 032 six-transmitter schedules are prepared by:

* `scripts/prepare_run032_six_tx_schedules.py`

The script is Run-032-specific. It extends the Run 031 four-transmitter schedule-preparation pattern while keeping the SD-facing replay convention unchanged.

The SD-facing files remain all-slot CSVs with schema:

`seq,region,event,priority,usefulness,stale_after,policy,send`

The SD-facing CSVs are intentionally all-slot files, not compact SEND-only files.

Generated manifest:

* `traces/run032_reporting_reporting_schedule_manifest.json`

Generated base schedule copy:

* `traces/run032_six_tx_base_schedule.csv`

Generated SD-facing schedules:

| Transmitter | SD-facing schedule                  | Rows | SEND | SKIP |
| ----------- | ----------------------------------- | ---: | ---: | ---: |
| TXA/N01     | `traces/run032_sd_txa_schedule.csv` |   64 |   64 |    0 |
| TXB/N16     | `traces/run032_sd_txb_schedule.csv` |   64 |   32 |   32 |
| TXC/N31     | `traces/run032_sd_txc_schedule.csv` |   64 |   16 |   48 |
| TXD/N46     | `traces/run032_sd_txd_schedule.csv` |   64 |    8 |   56 |
| TXE/N61     | `traces/run032_sd_txe_schedule.csv` |   64 |   32 |   32 |
| TXF/N76     | `traces/run032_sd_txf_schedule.csv` |   64 |   16 |   48 |

Compact SEND-only CSVs were also generated for analysis and inspection, but they are not SD replay files and should not be copied as `/schedule.csv`.

## Firmware identity preparation

This milestone prepares explicit Run 032 firmware identities for six transmitters.

Run 032 firmware identity set:

| Transmitter | Node | Firmware sketch                                            | RUN_ID | STARTUP_OFFSET_MS |
| ----------- | ---: | ---------------------------------------------------------- | ------ | ----------------: |
| TXA         |  N01 | `firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino` | R32    |               500 |
| TXB         |  N16 | `firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino` | R32    |              2750 |
| TXC         |  N31 | `firmware/first_radio_link_TX_C/first_radio_link_TX_C.ino` | R32    |              4250 |
| TXD         |  N46 | `firmware/first_radio_link_TX_D/first_radio_link_TX_D.ino` | R32    |                 0 |
| TXE         |  N61 | `firmware/first_radio_link_TX_E/first_radio_link_TX_E.ino` | R32    |              7250 |
| TXF         |  N76 | `firmware/first_radio_link_TX_F/first_radio_link_TX_F.ino` | R32    |              2000 |

TXE and TXF firmware sketches were created from the existing SD replay transmitter pattern.

After normalizing identity, node, startup offset, and serial banner text, all six transmitter sketches match. This supports treating the six sketches as the same replay firmware pattern with different repository-side identities and startup phases.

## Expected physical-prep checklist

Before any later receiver-logging milestone, confirm:

* TXA physical board is labeled TXA/N01.
* TXB physical board is labeled TXB/N16.
* TXC physical board is labeled TXC/N31.
* TXD physical board is labeled TXD/N46.
* TXE physical board is labeled TXE/N61.
* TXF physical board is labeled TXF/N76.
* TXA is flashed with `firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino`.
* TXB is flashed with `firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino`.
* TXC is flashed with `firmware/first_radio_link_TX_C/first_radio_link_TX_C.ino`.
* TXD is flashed with `firmware/first_radio_link_TX_D/first_radio_link_TX_D.ino`.
* TXE is flashed with `firmware/first_radio_link_TX_E/first_radio_link_TX_E.ino`.
* TXF is flashed with `firmware/first_radio_link_TX_F/first_radio_link_TX_F.ino`.
* TXA SD card contains `traces/run032_sd_txa_schedule.csv` copied as `/schedule.csv`.
* TXB SD card contains `traces/run032_sd_txb_schedule.csv` copied as `/schedule.csv`.
* TXC SD card contains `traces/run032_sd_txc_schedule.csv` copied as `/schedule.csv`.
* TXD SD card contains `traces/run032_sd_txd_schedule.csv` copied as `/schedule.csv`.
* TXE SD card contains `traces/run032_sd_txe_schedule.csv` copied as `/schedule.csv`.
* TXF SD card contains `traces/run032_sd_txf_schedule.csv` copied as `/schedule.csv`.
* No compact SEND-only CSV is copied as `/schedule.csv`.
* All six boards initialize SD successfully.
* All six boards open `/schedule.csv` successfully.
* All six boards report 64 schedule rows.
* TXA reports 64 SEND rows and 0 SKIP rows.
* TXB reports 32 SEND rows and 32 SKIP rows.
* TXC reports 16 SEND rows and 48 SKIP rows.
* TXD reports 8 SEND rows and 56 SKIP rows.
* TXE reports 32 SEND rows and 32 SKIP rows.
* TXF reports 16 SEND rows and 48 SKIP rows.
* Receiver firmware is unchanged unless explicitly documented.
* Receiver logging command is ready but not yet run as part of this milestone.

## Expected startup checks

Expected TXD startup identity:

* `RUN_ID = R32`
* `TX_ID = TXD`
* `NODE_ID = N46`
* `STARTUP_OFFSET_MS = 0`
* schedule rows = 64
* SEND rows = 8
* SKIP rows = 56

Expected TXA startup identity:

* `RUN_ID = R32`
* `TX_ID = TXA`
* `NODE_ID = N01`
* `STARTUP_OFFSET_MS = 500`
* schedule rows = 64
* SEND rows = 64
* SKIP rows = 0

Expected TXF startup identity:

* `RUN_ID = R32`
* `TX_ID = TXF`
* `NODE_ID = N76`
* `STARTUP_OFFSET_MS = 2000`
* schedule rows = 64
* SEND rows = 16
* SKIP rows = 48

Expected TXB startup identity:

* `RUN_ID = R32`
* `TX_ID = TXB`
* `NODE_ID = N16`
* `STARTUP_OFFSET_MS = 2750`
* schedule rows = 64
* SEND rows = 32
* SKIP rows = 32

Expected TXC startup identity:

* `RUN_ID = R32`
* `TX_ID = TXC`
* `NODE_ID = N31`
* `STARTUP_OFFSET_MS = 4250`
* schedule rows = 64
* SEND rows = 16
* SKIP rows = 48

Expected TXE startup identity:

* `RUN_ID = R32`
* `TX_ID = TXE`
* `NODE_ID = N61`
* `STARTUP_OFFSET_MS = 7250`
* schedule rows = 64
* SEND rows = 32
* SKIP rows = 32

Any mismatch in identity, row count, SEND count, SKIP count, startup offset, or SD-card mapping should stop physical preparation.

## Deferred physical replay outputs

A later physical replay milestone should produce receiver-side outputs such as:

* `logs/rx_run_032_six_transmitter_sd_replay.csv`
* `logs/parsed_run_032_six_transmitter_sd_replay.csv`
* `logs/parsed_run_032_six_transmitter_sd_replay_rejects.csv`

A later analysis/validation milestone should produce outputs such as:

* `outputs/run032_six_transmitter_manifest_replay_summary.json`
* `outputs/run032_six_transmitter_manifest_replay_summary.csv`
* `outputs/run032_six_transmitter_manifest_replay_validation.json`

Those files are not part of v4.7.

## Interpretation boundary

This milestone is physical preparation only.

It does not establish six-transmitter physical replay behavior.

It does not establish eight-transmitter behavior.

It does not establish twelve-transmitter behavior.

It does not infer exact transmitted-packet counts.

It does not confirm collisions.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish airtime optimization.

It does not establish energy savings.

It does not use a live belief-maintenance controller.

It does not evaluate operational wildfire behavior.

The startup offsets are programmed bench-start phases for replay preparation.

They are not synchronized timing.

They are not collision-avoidance guarantees.

They are not latency measurements.

They are not MAC-layer coordination.

Use receiver-side packet proportions when comparing any later physical replay results.

Use the wording “phase/schedule-interaction hypothesis,” not confirmed collisions.

Use the wording “reduced physical transmission attempts under scheduled skipping,” not energy savings.

Do not overgeneralize from six-transmitter physical preparation to physical replay behavior.

## Recommended next milestone

The next milestone should be:

* `v4.8-run032-six-transmitter-physical-replay`

That later milestone should collect and parse the first Run 032 six-transmitter physical receiver log.

It should not also introduce new schedule design, firmware identity changes, or analysis-tool changes unless a concrete problem is discovered.
