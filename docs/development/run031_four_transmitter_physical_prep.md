# Run 031 Four-Transmitter Physical Preparation

## Purpose

This milestone prepares the Run 031 four-transmitter physical replay setup.

It follows:

* `v4.0-four-transmitter-scale-design`
* `v4.1-run031-four-transmitter-schedule-prep`

This milestone is physical preparation only.

It does not copy schedules to SD cards.

It does not flash hardware.

It does not run the receiver logger.

It does not collect receiver logs.

It does not parse physical packets.

It does not report observed packet proportions.

It does not make four-transmitter physical replay claims.

The purpose is to prepare the repository-side identities, firmware configuration, and physical-prep documentation so that a later physical replay milestone can begin from a clean, documented setup.

## Current milestone

This note belongs to:

* `v4.2-run031-four-transmitter-physical-prep`

Branch:

* `exp060-run031-four-transmitter-physical-prep`

Status:

* Physical-preparation milestone

## Current basis

The v4.1 schedule-preparation milestone generated and validated four SD-facing all-slot schedules:

* TXA/N01: 64 rows, 64 SEND, 0 SKIP
* TXB/N16: 64 rows, 32 SEND, 32 SKIP
* TXC/N31: 64 rows, 16 SEND, 48 SKIP
* TXD/NXX: 64 rows, 8 SEND, 56 SKIP

At the start of v4.2, TXD had not yet been labeled or flashed.

The first v4.2 decision was to assign a physical node identity for TXD.

## TXD node identity assignment

The assigned TXD identity is:

* TXD/N46

This continues the existing node spacing pattern:

* TXA/N01
* TXB/N16
* TXC/N31
* TXD/N46

The Run 031 manifest was updated from `TXD/NXX` to `TXD/N46`:

* `traces/run031_reporting_reporting_schedule_manifest.json`

The Run 031 schedule-preparation documentation and README were also updated to remove stale placeholder wording.

After assigning TXD/N46, the four SD-facing schedules were revalidated with their expected row, SEND, and SKIP counts.

## Schedule validation after TXD identity assignment

The SD-facing schedules remained valid:

* `traces/run031_sd_txa_schedule.csv`: 64 rows, 64 SEND, 0 SKIP
* `traces/run031_sd_txb_schedule.csv`: 64 rows, 32 SEND, 32 SKIP
* `traces/run031_sd_txc_schedule.csv`: 64 rows, 16 SEND, 48 SKIP
* `traces/run031_sd_txd_schedule.csv`: 64 rows, 8 SEND, 56 SKIP

The TXD node identity change did not alter the schedule row structure.

## Firmware identity preparation

This milestone prepares explicit Run 031 firmware identities for all four transmitters.

Run 031 firmware identity set:

* TXA/N01: `RUN_ID = "R31"`
* TXB/N16: `RUN_ID = "R31"`
* TXC/N31: `RUN_ID = "R31"`
* TXD/N46: `RUN_ID = "R31"`

TXD firmware was added as:

* `firmware/first_radio_link_TX_D/first_radio_link_TX_D.ino`

The TXD firmware was created from the existing SD replay transmitter pattern and assigned:

* `TX_ID = "TXD"`
* `NODE_ID = "N46"`
* `RUN_ID = "R31"`

The TXD firmware directory contains only the TXD sketch and does not include stale copied TXC/TXB schedule-header artifacts.

## Startup offsets

Run 031 uses distinct startup offsets for the four transmitters:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 750 ms
* TXD/N46: 1000 ms

These offsets are practical bench-start staggering only.

They are not synchronized timing.

They are not collision-avoidance guarantees.

They are not latency measurements.

They are not MAC-layer coordination.

They should not be interpreted as evidence of collision avoidance or timing control.

## Expected physical-prep checklist

Before any later receiver-logging milestone, confirm:

* TXA physical board is labeled TXA/N01.
* TXB physical board is labeled TXB/N16.
* TXC physical board is labeled TXC/N31.
* TXD physical board is labeled TXD/N46.
* TXA is flashed with `firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino`.
* TXB is flashed with `firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino`.
* TXC is flashed with `firmware/first_radio_link_TX_C/first_radio_link_TX_C.ino`.
* TXD is flashed with `firmware/first_radio_link_TX_D/first_radio_link_TX_D.ino`.
* TXA SD card contains `traces/run031_sd_txa_schedule.csv` copied as `/schedule.csv`.
* TXB SD card contains `traces/run031_sd_txb_schedule.csv` copied as `/schedule.csv`.
* TXC SD card contains `traces/run031_sd_txc_schedule.csv` copied as `/schedule.csv`.
* TXD SD card contains `traces/run031_sd_txd_schedule.csv` copied as `/schedule.csv`.
* No compact SEND-only CSV is copied as `/schedule.csv`.
* All four boards initialize SD successfully.
* All four boards open `/schedule.csv` successfully.
* All four boards report 64 schedule rows.
* TXA reports 64 SEND rows.
* TXB reports 32 SEND rows.
* TXC reports 16 SEND rows.
* TXD reports 8 SEND rows.
* Receiver firmware is unchanged unless explicitly documented.
* Receiver logging command is ready but not yet run as part of this milestone.

## Expected startup checks

Expected TXA startup identity:

* `RUN_ID = R31`
* `TX_ID = TXA`
* `NODE_ID = N01`
* schedule rows = 64
* SEND rows = 64
* SKIP rows = 0

Expected TXB startup identity:

* `RUN_ID = R31`
* `TX_ID = TXB`
* `NODE_ID = N16`
* `STARTUP_OFFSET_MS = 500`
* schedule rows = 64
* SEND rows = 32
* SKIP rows = 32

Expected TXC startup identity:

* `RUN_ID = R31`
* `TX_ID = TXC`
* `NODE_ID = N31`
* `STARTUP_OFFSET_MS = 750`
* schedule rows = 64
* SEND rows = 16
* SKIP rows = 48

Expected TXD startup identity:

* `RUN_ID = R31`
* `TX_ID = TXD`
* `NODE_ID = N46`
* `STARTUP_OFFSET_MS = 1000`
* schedule rows = 64
* SEND rows = 8
* SKIP rows = 56

Any mismatch in identity, row count, SEND count, or SD-card mapping should stop the physical preparation.

## Deferred physical replay outputs

A later physical replay milestone should produce receiver-side outputs such as:

* `logs/rx_run_031_four_transmitter_sd_replay.csv`
* `logs/parsed_run_031_four_transmitter_sd_replay.csv`
* `logs/parsed_run_031_four_transmitter_sd_replay_rejects.csv`

A later analysis/validation milestone should produce outputs such as:

* `outputs/run031_four_transmitter_manifest_replay_summary.json`
* `outputs/run031_four_transmitter_manifest_replay_summary.csv`
* `outputs/run031_four_transmitter_manifest_replay_validation.json`

Those files are not part of v4.2.

## Interpretation boundary

This milestone is physical preparation only.

It does not establish four-transmitter physical replay behavior.

It does not establish 12-transmitter behavior.

It does not infer exact transmitted-packet counts.

It does not confirm collisions.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish airtime optimization.

It does not establish energy savings.

It does not use a live belief-maintenance controller.

It does not evaluate operational wildfire behavior.

The startup offsets are bench-start staggering only.

Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”

Do not claim energy savings unless current or power measurements are added.

Do not overgeneralize from four-transmitter physical preparation to physical replay behavior.

## Recommended next milestone

The next milestone should be:

* `v4.3-run031-four-transmitter-physical-replay`

That later milestone should collect and parse the first Run 031 four-transmitter physical receiver log.

It should not also introduce new schedule design, firmware identity changes, or analysis-tool changes unless a concrete problem is discovered.
