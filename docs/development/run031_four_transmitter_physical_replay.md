# Run 031 Four-Transmitter Physical Replay

## Purpose

This milestone records the first successful four-transmitter SD-backed physical replay for Run 031.

It follows:

* `v4.0-four-transmitter-scale-design`
* `v4.1-run031-four-transmitter-schedule-prep`
* `v4.2-run031-four-transmitter-physical-prep`

This milestone records physical replay artifacts, parser outputs, manifest-bound analysis outputs, and bundle validation for the successful adjusted-position replay attempt.

## Current milestone

This note belongs to:

* `v4.3-run031-four-transmitter-physical-replay`

Branch:

* `exp061-run031-four-transmitter-physical-replay`

## Run 031 transmitter set

Run 031 used four transmitters:

* TXA/N01: fixed-all baseline, 64/64 scheduled SEND
* TXB/N16: medium threshold scheduled skipping, 32/64 scheduled SEND
* TXC/N31: strict threshold scheduled skipping, 16/64 scheduled SEND
* TXD/N46: very-strict threshold scheduled skipping, 8/64 scheduled SEND

Expected scheduled-send ladder:

* TXA = 1.000
* TXB = 0.500
* TXC = 0.250
* TXD = 0.125

Expected scheduled ratios:

* TXB/TXA = 0.5000
* TXC/TXA = 0.2500
* TXD/TXA = 0.1250
* TXC/TXB = 0.5000
* TXD/TXB = 0.2500
* TXD/TXC = 0.5000

## Physical setup notes

All four SD-facing schedules were copied to SD cards as `/schedule.csv`.

The four firmware identities were prepared as:

* TXA/N01: `RUN_ID = "R31"`
* TXB/N16: `RUN_ID = "R31"`
* TXC/N31: `RUN_ID = "R31"`
* TXD/N46: `RUN_ID = "R31"`

Startup offsets:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 750 ms
* TXD/N46: 1000 ms

These offsets are practical bench-start staggering only.

They are not synchronized timing.

They are not collision-avoidance guarantees.

They are not latency measurements.

They are not MAC-layer coordination.

## Startup checks

All four transmitters were startup-checked before the successful replay attempt.

Observed startup checks confirmed:

* TXA/N01: 64 rows, 64 SEND, 0 SKIP
* TXB/N16: 64 rows, 32 SEND, 32 SKIP
* TXC/N31: 64 rows, 16 SEND, 48 SKIP
* TXD/N46: 64 rows, 8 SEND, 56 SKIP

The TXD/N46 board was also checked alone after early poor four-transmitter reception. TXD-only reception was healthy, with continuous TXD/N46 packets and good receiver-side RSSI/SNR.

## Replay attempts

Several physical attempts were made.

The first two four-transmitter attempts showed good TXA/TXB/TXC proportions but poor TXD reception. Those files were retained locally as bench diagnostics and were not committed as primary reproduction artifacts.

A TXD-only diagnostic capture confirmed that TXD/N46 itself was functioning correctly.

The successful replay was the adjusted-position attempt:

* `logs/rx_run_031_four_transmitter_sd_replay_attempt3.csv`
* `logs/parsed_run_031_four_transmitter_sd_replay_attempt3.csv`
* `logs/parsed_run_031_four_transmitter_sd_replay_attempt3_rejects.csv`

This attempt used adjusted TXD placement and manual startup order with TXD started first, followed by TXA, TXB, and TXC. Therefore, it should be described as a successful adjusted-position four-transmitter replay attempt, not as a synchronized or identical-start replay.

## Successful replay result

The successful adjusted-position attempt produced:

* Valid packets: 800
* Rejects: empty
* Run IDs: R31 only

Received valid packets by transmitter:

* TXA/N01: 433
* TXB/N16: 212
* TXC/N31: 102
* TXD/N46: 53

RSSI/SNR summaries showed all four transmitters were received with healthy receiver-side SNR in the successful attempt.

## Observed receiver-side ratios

Expected versus observed receiver-side packet ratios:

| Ratio   | Expected scheduled ratio | Observed receiver-side ratio | Observed minus expected |
| ------- | -----------------------: | ---------------------------: | ----------------------: |
| TXB/TXA |                   0.5000 |                       0.4896 |                 -0.0104 |
| TXC/TXA |                   0.2500 |                       0.2356 |                 -0.0144 |
| TXD/TXA |                   0.1250 |                       0.1224 |                 -0.0026 |
| TXC/TXB |                   0.5000 |                       0.4811 |                 -0.0189 |
| TXD/TXB |                   0.2500 |                       0.2500 |                  0.0000 |
| TXD/TXC |                   0.5000 |                       0.5196 |                  0.0196 |

The observed receiver-side ratios were close to the expected scheduled-send ladder for the successful adjusted-position attempt.

## Observed sequence gaps

The analyzer reported the following observed sequence gaps:

* TXA/N01: `[85]`
* TXB/N16: `[]`
* TXC/N31: `[]`
* TXD/N46: `[25, 44, 45]`

These are observed sequence gaps only.

They are not confirmed collisions.

They are not exact transmitted-packet loss counts.

They are not synchronized latency measurements.

## Manifest-bound analysis outputs

The successful attempt was analyzed with the multi-transmitter manifest analyzer:

* Script: `scripts/analyze_scheduled_replay_manifest_multi.py`
* Manifest: `traces/run031_reporting_reporting_schedule_manifest.json`
* Parsed input: `logs/parsed_run_031_four_transmitter_sd_replay_attempt3.csv`
* JSON output: `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.json`
* CSV output: `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.csv`

Analysis outputs:

* `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.json`
* `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.csv`

## Bundle validation

The successful attempt bundle was validated with the multi-transmitter manifest replay bundle validator:

* Script: `scripts/validate_manifest_replay_bundle_multi.py`
* Manifest: `traces/run031_reporting_reporting_schedule_manifest.json`
* Summary JSON: `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.json`
* Summary CSV: `outputs/run031_four_transmitter_manifest_replay_attempt3_summary.csv`
* Parsed input: `logs/parsed_run_031_four_transmitter_sd_replay_attempt3.csv`
* Validation output: `outputs/run031_four_transmitter_manifest_replay_attempt3_validation.json`

Validation result:

* Passed: true
* Checks total: 136
* Checks passed: 136
* Checks failed: 0

Validation output:

* `outputs/run031_four_transmitter_manifest_replay_attempt3_validation.json`

## Interpretation boundary

This milestone demonstrates that the SD-backed, manifest-bound replay workflow can be extended from three transmitters to four transmitters under this adjusted lab condition.

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

Observed packet ratios are receiver-side proportions.

Observed sequence gaps are not confirmed collisions.

Receiver inter-arrival summaries are receiver-side observations only.

Usefulness and priority remain synthetic metadata.

## Recommended next milestone

The next milestone should be a four-transmitter synthesis note:

* `v4.4-run031-four-transmitter-replay-synthesis`

That synthesis should compare the successful adjusted-position Run 031 result against the earlier Run 030 three-transmitter result and preserve the physical-procedure caveat for attempt 3.
