# Run 031 Startup-Phase Validation

## Purpose

This milestone tests whether relative transmitter startup timing, and therefore replay phase, contributed to the successful Run 031 four-transmitter physical replay.

The motivation is that the first two four-transmitter attempts showed poor TXD/N46 reception, while TXD-only reception was healthy. The successful adjusted-position attempt used both changed TXD placement and a manual startup order in which TXD was started first before TXA, TXB, and TXC were added later.

Because physical relocation alone did not immediately explain the improvement, this milestone tests startup-phase conditions more directly.

## Current milestone

This note belongs to:

* `v4.4-run031-startup-phase-validation`

Branch:

* `exp062-run031-startup-phase-validation`

## Fixed conditions

The validation should keep the following fixed as much as practical:

* Same Run 031 SD schedules.
* Same four board identities.
* Same receiver.
* Same receiver logger.
* Same parser.
* Same multi-transmitter analyzer.
* Same physical placement as the successful v4.3 adjusted-position attempt.
* Same point-to-point LoRa setup.
* Same schedule period of 64 rows.

The intended variable is the programmed startup offset pattern.

## Validation conditions

### Condition A: current baseline phase

This condition uses the current Run 031 firmware offset pattern:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 750 ms
* TXD/N46: 1000 ms

Purpose:

* Test the current physical-prep offset pattern under the successful physical placement.

### Condition B: TXD-first programmed phase

This condition gives TXD the first startup phase:

* TXD/N46: 0 ms
* TXA/N01: 500 ms
* TXB/N16: 750 ms
* TXC/N31: 1000 ms

Purpose:

* Test whether making TXD first improves TXD reception under four-transmitter operation.

### Condition C: TXA-first stretched programmed phase

This condition keeps TXA first but stretches the phase spacing:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 1000 ms
* TXD/N46: 1500 ms

Purpose:

* Test whether a longer programmed phase spread helps without making TXD first.

## Primary comparison

The primary comparison is the TXD receiver-side packet ratio.

Expected scheduled ratio:

* TXD/TXA = 0.1250

Secondary ratios:

* TXB/TXA = 0.5000
* TXC/TXA = 0.2500
* TXC/TXB = 0.5000
* TXD/TXB = 0.2500
* TXD/TXC = 0.5000

## Condition A result: current baseline phase

Condition A was captured using the current baseline programmed phase pattern:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 750 ms
* TXD/N46: 1000 ms

Capture and analysis files:

* Raw receiver log: `logs/rx_run_031_phase_validation_A_near_simultaneous.csv`
* Parsed valid packets: `logs/parsed_run_031_phase_validation_A_near_simultaneous.csv`
* Parsed rejects: `logs/parsed_run_031_phase_validation_A_near_simultaneous_rejects.csv`
* Summary JSON: `outputs/run031_phase_validation_A_near_simultaneous_summary.json`
* Summary CSV: `outputs/run031_phase_validation_A_near_simultaneous_summary.csv`
* Validation JSON: `outputs/run031_phase_validation_A_near_simultaneous_validation.json`

Observed receiver-side packet counts:

* TXA/N01: 354
* TXB/N16: 180
* TXC/N31: 90
* TXD/N46: 0

Observed receiver-side ratios:

* TXB/TXA: expected 0.5000, observed 0.5085
* TXC/TXA: expected 0.2500, observed 0.2542
* TXD/TXA: expected 0.1250, observed 0.0000
* TXC/TXB: expected 0.5000, observed 0.5000
* TXD/TXB: expected 0.2500, observed 0.0000
* TXD/TXC: expected 0.5000, observed 0.0000

Validation result:

* checks_total: 136
* checks_passed: 136
* checks_failed: 0

Condition A is therefore a TXD reception failure under the current near-simultaneous baseline programmed phase. TXA, TXB, and TXC remained close to their expected receiver-side scheduled ratios, while TXD had no received packets in the raw receiver log or parsed output.

This supports proceeding to Condition B, the TXD-first programmed phase test.

## Interpretation plan

If Condition A fails but Condition B succeeds, startup phase is likely important.

If Conditions A and B both succeed, the adjusted physical placement may be sufficient.

If Condition B succeeds but Condition C does not, TXD-first phase may matter specifically.

If Condition C succeeds, longer phase separation may matter even without TXD-first ordering.

If all conditions fail, the previous v4.3 success may have depended on another uncontrolled bench condition.

## Interpretation boundary

This validation tests startup-phase sensitivity in a four-transmitter point-to-point LoRa bench setup.

It does not infer exact transmitted-packet counts.

It does not confirm collisions.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish energy savings.

It does not establish airtime optimization.

It does not use a live belief-maintenance controller.

It does not evaluate operational wildfire behavior.

Observed ratios are receiver-side packet proportions.

Observed sequence gaps are not confirmed collisions.
