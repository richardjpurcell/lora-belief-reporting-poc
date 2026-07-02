# Run 031 Four-Transmitter SD Schedule Preparation

## Purpose

This milestone prepares the schedule artifacts for the first four-transmitter microSD-backed replay design.

It follows the design milestone:

* `v4.0-four-transmitter-scale-design`

The core design question carried forward from v4.0 is:

Can the SD-backed, manifest-bound replay workflow remain readable when moving from three transmitters to four transmitters, while preserving a simple scheduled-send ladder and bounded interpretation language?

This milestone is schedule-preparation only.

It does not copy files to SD cards.

It does not flash firmware.

It does not create TXD firmware.

It does not perform physical startup checks.

It does not run the receiver logger.

It does not collect or parse a physical replay log.

It does not make four-transmitter physical replay claims.

Those steps are deferred to later milestones.

## Current milestone

This note belongs to:

* `v4.1-run031-four-transmitter-schedule-prep`

Branch:

* `exp059-run031-four-transmitter-schedule-prep`

Status:

* Schedule-preparation milestone

## Current basis

Run 030 established a validated three-transmitter SD-backed replay workflow with:

* TXA/N01: fixed-all baseline, 64/64 SEND
* TXB/N16: medium threshold, 32/64 SEND
* TXC/N31: strict threshold, 16/64 SEND

The v4.0 design milestone recommended extending that structure by one halving step:

* TXD/N46: very-strict threshold, 8/64 SEND

The TXD node ID has been assigned in this schedule-preparation milestone:

* `NXX`

The physical TXD node ID should be confirmed from the board label during a later physical-preparation milestone.

## Added schedule-preparation script

This milestone adds:

* `scripts/prepare_run031_four_tx_schedules.py`

The script is intentionally Run-031-specific.

It follows the same explicit style as the Run 030 schedule-preparation script rather than prematurely generalizing the scheduler.

The script reads the existing 64-row source schedule:

* `traces/run029_reporting_txa_fixed_all_schedule.csv`

It writes a Run 031 base schedule copy:

* `traces/run031_four_tx_base_schedule.csv`

It then prepares four transmitter schedules:

* TXA: all 64 rows SEND
* TXB: top 32 rows by usefulness
* TXC: top 16 rows by usefulness
* TXD: top 8 rows by usefulness

For usefulness-threshold selections, ties are resolved by sequence order.

## Generated manifest

This milestone adds the Run 031 list-valued manifest:

* `traces/run031_reporting_reporting_schedule_manifest.json`

The manifest uses the current N-transmitter structure with a list-valued `transmitters` field.

It does not use the legacy `transmitters.a` / `transmitters.b` structure.

Manifest transmitter entries:

* TXA/N01
* TXB/N16
* TXC/N31
* TXD/N46

## Generated schedule artifacts

Analysis-facing full schedules:

* `traces/run031_reporting_txa_fixed_all_schedule.csv`
* `traces/run031_reporting_txb_medium_threshold_schedule.csv`
* `traces/run031_reporting_txc_strict_threshold_schedule.csv`
* `traces/run031_reporting_txd_very_strict_threshold_schedule.csv`

Compact SEND-only reference CSVs:

* `traces/run031_reporting_txa_fixed_all_compact.csv`
* `traces/run031_reporting_txb_medium_threshold_compact.csv`
* `traces/run031_reporting_txc_strict_threshold_compact.csv`
* `traces/run031_reporting_txd_very_strict_threshold_compact.csv`

SD-facing all-slot CSVs:

* `traces/run031_sd_txa_schedule.csv`
* `traces/run031_sd_txb_schedule.csv`
* `traces/run031_sd_txc_schedule.csv`
* `traces/run031_sd_txd_schedule.csv`

The SD-facing files are the files that should later be copied to each transmitter SD card as:

* `/schedule.csv`

The compact SEND-only reference CSVs are not SD replay files and should not be copied to SD cards as `/schedule.csv`.

## SD schedule schema

The SD-facing schedule schema remains:

* `seq`
* `region`
* `event`
* `priority`
* `usefulness`
* `stale_after`
* `policy`
* `send`

The firmware-facing `policy` field remains a single-character code.

Run 031 uses:

* `F` for TXA fixed-all rows
* `U` for TXB usefulness-threshold rows
* `U` for TXC usefulness-threshold rows
* `U` for TXD usefulness-threshold rows

## Expected schedule counts

Expected all-slot row counts:

* TXA/N01: 64 rows
* TXB/N16: 64 rows
* TXC/N31: 64 rows
* TXD/N46: 64 rows

Expected SEND counts:

* TXA/N01: 64/64 SEND
* TXB/N16: 32/64 SEND
* TXC/N31: 16/64 SEND
* TXD/N46: 8/64 SEND

Expected SKIP counts:

* TXA/N01: 0/64 SKIP
* TXB/N16: 32/64 SKIP
* TXC/N31: 48/64 SKIP
* TXD/N46: 56/64 SKIP

## Expected scheduled ratios

Expected scheduled ratios against TXA:

* TXB/TXA = 32/64 = 0.5000
* TXC/TXA = 16/64 = 0.2500
* TXD/TXA = 8/64 = 0.1250

Expected scheduled ratios among thresholded transmitters:

* TXC/TXB = 16/32 = 0.5000
* TXD/TXB = 8/32 = 0.2500
* TXD/TXC = 8/16 = 0.5000

These are scheduled SEND proportions only.

They are not transmitted-packet counts.

They are not collision counts.

They are not latency measurements.

They are not energy measurements.

They are not airtime measurements.

## Commands used

The schedule artifacts were generated with:

```
python scripts/prepare_run031_four_tx_schedules.py
```

The generated manifest reported:

```
run_id: run031_four_transmitter_sd_schedule_prep
milestone: v4.1-run031-four-transmitter-schedule-prep
schedule_period_rows: 64

TXA/N01: rows=64 send=64 skip=0 threshold=None
TXB/N16: rows=64 send=32 skip=32 threshold=medium
TXC/N31: rows=64 send=16 skip=48 threshold=strict
TXD/N46: rows=64 send=8 skip=56 threshold=very_strict

TXB/TXA: 0.5000
TXC/TXA: 0.2500
TXD/TXA: 0.1250
TXC/TXB: 0.5000
TXD/TXB: 0.2500
TXD/TXC: 0.5000
```

The schedule-preparation script was syntax-checked with:

```
python -m py_compile scripts/prepare_run031_four_tx_schedules.py
```

The SD-facing schedules were validated with expected row, SEND, and SKIP counts using:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run031_sd_txa_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 64 \
  --expected-skip-rows 0

python scripts/validate_sd_schedule.py \
  --infile traces/run031_sd_txb_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 32 \
  --expected-skip-rows 32

python scripts/validate_sd_schedule.py \
  --infile traces/run031_sd_txc_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 16 \
  --expected-skip-rows 48

python scripts/validate_sd_schedule.py \
  --infile traces/run031_sd_txd_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 8 \
  --expected-skip-rows 56
```

## Interpretation boundary

This milestone is schedule preparation only.

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

Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”

Do not claim energy savings unless current or power measurements are added.

Do not overgeneralize from the schedule design to physical behavior.

## Deferred next steps

The next milestone should be physical preparation only:

* `v4.2-run031-four-transmitter-physical-prep`

That later milestone should:

1. Confirm the physical TXD board label and node ID.
2. Decide whether `NXX` should be replaced in schedule artifacts before physical replay.
3. Prepare or copy an explicit TXD firmware configuration.
4. Confirm all four transmitter firmware identities.
5. Copy each SD-facing all-slot CSV to the correct SD card as `/schedule.csv`.
6. Confirm startup row counts and SEND counts for all four transmitters.
7. Stop before collecting receiver logs.

The physical replay itself should remain a later milestone.
