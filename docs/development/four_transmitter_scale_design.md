# Four-Transmitter Scale Design

## Purpose

This milestone designs the smallest careful move from the validated three-transmitter SD replay workflow toward a four-transmitter SD replay workflow.

This is a design-only milestone.

It does not generate schedules.

It does not copy files to SD cards.

It does not flash firmware.

It does not change transmitter firmware.

It does not run the receiver logger.

It does not collect or parse a physical replay log.

It does not create new analysis or validation outputs.

The purpose is to define a clean, bounded Run 031 four-transmitter design before any schedule-preparation or physical-preparation work begins.

## Current milestone

This note belongs to:

* `v4.0-four-transmitter-scale-design`

It follows the completed cleanup and stabilization chain:

* `v3.9-three-transmitter-analysis-generalization`
* `v3.10-multi-transmitter-bundle-validation`
* `v3.11-multi-transmitter-repro-cleanup`
* `v3.12-legacy-tool-status-cleanup`

## Current basis

Run 030 established a validated three-transmitter SD-backed replay workflow.

The Run 030 transmitter set was:

* TXA/N01
* TXB/N16
* TXC/N31

The Run 030 schedule design was:

* TXA/N01: fixed-all baseline, 64/64 SEND
* TXB/N16: medium threshold, 32/64 SEND
* TXC/N31: strict threshold, 16/64 SEND

The schedule period was:

* 64 rows

The Run 030 expected scheduled SEND ratios were:

* TXB/TXA = 32/64 = 0.5000
* TXC/TXA = 16/64 = 0.2500
* TXC/TXB = 16/32 = 0.5000

Run 030 physical receiver/parser result:

* Valid packets: 685
* Malformed packets: 1
* TXA/N01: 393 packets, mean usefulness 0.524
* TXB/N16: 194 packets, mean usefulness 0.810
* TXC/N31: 98 packets, mean usefulness 0.870

Run 030 observed receiver-side ratios were close to the expected scheduled ratios:

* TXB/TXA observed 0.4936, expected 0.5000
* TXC/TXA observed 0.2494, expected 0.2500
* TXC/TXB observed 0.5052, expected 0.5000

The careful Run 030 synthesis was:

The SD-backed, manifest-bound replay workflow remained readable when moving from two transmitters to three transmitters under this lab condition.

## Why v4.0 is design-only

The project has just completed a stabilization sequence around Run 030:

1. N-transmitter manifest analysis.
2. N-transmitter bundle validation.
3. Reproduction commands.
4. Legacy versus N-transmitter tool-status documentation.

The next uncertainty is no longer whether the Run 030 artifacts can be regenerated and validated. The next uncertainty is how to scale the physical replay workflow by one more transmitter while preserving readable design, bounded claims, and reproducible artifact structure.

A design-only milestone keeps the next scale step from mixing too many changes at once.

## Proposed Run 031 four-transmitter design

The recommended next physical run should be:

* Run 031

The proposed transmitter set is:

* TXA/N01
* TXB/N16
* TXC/N31
* TXD/Nxx

The fourth transmitter node ID should be confirmed from the physical board label before schedule preparation. If the physical board already has a label or node convention, that label should take precedence over the placeholder `Nxx`.

The proposed schedule period should remain:

* 64 rows

The proposed schedule design is:

* TXA/N01: fixed-all baseline, 64/64 SEND
* TXB/N16: medium threshold, 32/64 SEND
* TXC/N31: strict threshold, 16/64 SEND
* TXD/Nxx: very-strict threshold, 8/64 SEND

This gives a simple halving ladder:

* TXA: 1.000
* TXB: 0.500
* TXC: 0.250
* TXD: 0.125

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

They are not exact transmitted-packet counts.

They are not collision counts.

They are not energy measurements.

They are not airtime measurements.

## Why use an 8/64 fourth transmitter

The fourth transmitter should introduce only one new physical transmitter identity while preserving the interpretability of the schedule structure.

An 8/64 very-strict stream has several advantages:

* It preserves the 64-row Run 030 schedule period.
* It extends the existing 64, 32, 16 pattern by one more halving step.
* It produces simple expected ratios.
* It avoids introducing a new schedule length.
* It avoids introducing phase-shift or randomized scheduling as an additional variable.
* It keeps the fourth-transmitter contribution small enough to inspect manually.
* It preserves the distinction between scheduled SEND proportions and receiver-side observed packet proportions.

Alternative fourth-transmitter choices are possible, but less clean for the first four-transmitter design.

A second 16/64 strict transmitter would test repeatability, but it would not extend the scheduled-skipping ladder.

A second 32/64 medium transmitter would test duplication under similar demand, but it would introduce ambiguity about whether the run is testing transmitter count or replicate behavior.

A phase-shifted transmitter might be useful later, but it introduces another schedule design variable.

For the first four-transmitter scale step, the smallest clean design is to add TXD as an 8/64 very-strict scheduled-skipping transmitter.

## Expected artifact pattern for a later schedule-prep milestone

A later Run 031 schedule-preparation milestone should create explicit four-transmitter artifacts.

Expected manifest:

* `traces/run031_reporting_reporting_schedule_manifest.json`

Expected analysis-facing full schedules:

* `traces/run031_reporting_txa_fixed_all_schedule.csv`
* `traces/run031_reporting_txb_medium_threshold_schedule.csv`
* `traces/run031_reporting_txc_strict_threshold_schedule.csv`
* `traces/run031_reporting_txd_very_strict_threshold_schedule.csv`

Expected compact SEND-only reference CSVs:

* `traces/run031_reporting_txa_fixed_all_compact.csv`
* `traces/run031_reporting_txb_medium_threshold_compact.csv`
* `traces/run031_reporting_txc_strict_threshold_compact.csv`
* `traces/run031_reporting_txd_very_strict_threshold_compact.csv`

Expected SD-facing all-slot CSVs:

* `traces/run031_sd_txa_schedule.csv`
* `traces/run031_sd_txb_schedule.csv`
* `traces/run031_sd_txc_schedule.csv`
* `traces/run031_sd_txd_schedule.csv`

Expected development note:

* `docs/development/run031_four_transmitter_sd_schedule_prep.md`

The SD-facing files should remain all-slot CSVs copied to each transmitter SD card as:

* `/schedule.csv`

The compact SEND-only CSVs should remain analysis/reference artifacts only.

They should not be copied to SD cards as `/schedule.csv`.

## Expected manifest structure

The Run 031 manifest should use the list-valued transmitter structure, not the legacy `transmitters.a` and `transmitters.b` structure.

Expected transmitter entries:

* TXA/N01
* TXB/N16
* TXC/N31
* TXD/Nxx

Each transmitter entry should include at least:

* `tx_id`
* `node_id`
* `role`
* `policy`
* `policy_code`
* `threshold_family`
* `schedule_csv`
* `compact_csv`
* `sd_csv`
* `expected_rows`
* `expected_send_rows`
* `expected_skip_rows`

The manifest should also include expected scheduled ratios for all useful pairwise comparisons.

## Expected SD schedule schema

The firmware-facing SD schedule schema should remain:

* `seq`
* `region`
* `event`
* `priority`
* `usefulness`
* `stale_after`
* `policy`
* `send`

The `policy` field should remain a single-character firmware-facing code.

Current recommended codes:

* `F` for fixed-all baseline rows
* `U` for usefulness-threshold rows

The later schedule-preparation milestone should validate that each SD-facing CSV has:

* one header row
* 64 schedule rows
* the expected SEND count
* the expected SKIP count
* the expected schema
* a single-character policy code

## Firmware implications

Run 030 already has explicit firmware directories for:

* TXA
* TXB
* TXC

A later physical-preparation milestone will likely need an explicit TXD firmware configuration.

Expected TXD preparation approach:

1. Copy the existing SD replay transmitter sketch from the closest current transmitter template.
2. Change only the TXD identity fields and serial banner.
3. Preserve the same SD replay behavior.
4. Remove stale copied headers or misleading TXA/TXB/TXC artifacts from the TXD firmware directory.
5. Confirm that TXD reads `/schedule.csv`.
6. Confirm that TXD reports the expected row and SEND counts.

The v4.0 design milestone should not create TXD firmware yet.

That belongs in a later physical-preparation milestone.

## Startup offset implications

Run 030 used staggered transmitter startup offsets, with TXC adjusted so it would not share TXB’s startup offset.

For Run 031, the physical-preparation milestone should define and document distinct startup offsets for all four transmitters.

A possible simple pattern is:

* TXA: 0 ms
* TXB: 500 ms
* TXC: 750 ms
* TXD: 1000 ms

This is only a design placeholder.

The actual offsets should be confirmed during physical preparation based on bench behavior and current firmware conventions.

Startup offsets should not be interpreted as collision avoidance guarantees.

They are practical bench-start staggering only.

## Analysis and validation implications

The current preferred analysis and validation path is already list-valued and N-transmitter-oriented:

* `scripts/analyze_scheduled_replay_manifest_multi.py`
* `scripts/validate_manifest_replay_bundle_multi.py`

A later Run 031 analysis milestone should use those N-transmitter tools.

The legacy tools should not be expanded for Run 031:

* `scripts/analyze_scheduled_replay.py`
* `scripts/analyze_scheduled_replay_from_manifest.py`
* `scripts/validate_run_bundle.py`

Those tools remain available for earlier two-transmitter artifacts.

Run 031 should build from the list-valued manifest path.

## Later milestone sequence

The recommended sequence after v4.0 is:

1. `v4.1-run031-four-transmitter-schedule-prep`
2. `v4.2-run031-four-transmitter-physical-prep`
3. `v4.3-run031-four-transmitter-physical-replay`
4. `v4.4-run031-four-transmitter-analysis-validation`
5. `v4.5-run031-four-transmitter-synthesis`

This preserves the current discipline:

* design
* schedule preparation
* physical preparation
* physical replay
* analysis and validation
* synthesis

## Out of scope for v4.0

This milestone does not create Run 031 schedules.

It does not create a Run 031 manifest.

It does not create TXD firmware.

It does not copy schedules to SD cards.

It does not run the receiver.

It does not parse logs.

It does not produce Run 031 analysis outputs.

It does not produce Run 031 validation outputs.

It does not generalize the schedule-preparation script.

It does not attempt a 12-transmitter run.

It does not integrate AWSRT-derived traces.

It does not introduce live belief-maintenance control.

## Interpretation boundary

This is point-to-point LoRa at 915 MHz, not LoRaWAN.

The proposed schedule CSVs would define one repeated schedule period.

Expected scheduled ratios are design targets, not measured transmitted-packet ratios.

Future observed packet ratios would be receiver-side proportions.

Missing sequence numbers would be observed sequence gaps only, not confirmed collisions.

`recv_ms` and `tx_ms` are not synchronized across boards and should not be treated as true latency.

Receiver inter-arrival summaries are receiver-side observations only.

Usefulness and priority remain synthetic metadata unless a later milestone explicitly changes the trace source.

The workflow does not yet use a live belief-maintenance controller.

Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”

Do not claim energy savings unless current or power measurements are added.

Do not overgeneralize from three-transmitter or later four-transmitter lab runs.

Do not claim 12-transmitter behavior from a four-transmitter design or run.

## Recommended v4.0 conclusion

The next scale step should be a bounded Run 031 four-transmitter design that preserves the Run 030 structure while adding one transmitter.

The recommended Run 031 design is:

* TXA/N01: 64/64 SEND, fixed-all baseline
* TXB/N16: 32/64 SEND, medium threshold
* TXC/N31: 16/64 SEND, strict threshold
* TXD/Nxx: 8/64 SEND, very-strict threshold

This gives a clean expected scheduled-send ladder while keeping the schedule period, SD replay schema, manifest style, and interpretation boundaries stable.

The next milestone should be schedule preparation only.
