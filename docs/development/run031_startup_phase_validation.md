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

## Condition B result: TXD-first programmed phase

Condition B was captured using the TXD-first programmed phase pattern:

* TXD/N46: 0 ms
* TXA/N01: 500 ms
* TXB/N16: 750 ms
* TXC/N31: 1000 ms

Capture and analysis files:

* Raw receiver log: `logs/rx_run_031_phase_validation_B_txd_first.csv`
* Parsed valid packets: `logs/parsed_run_031_phase_validation_B_txd_first.csv`
* Parsed rejects: `logs/parsed_run_031_phase_validation_B_txd_first_rejects.csv`
* Summary JSON: `outputs/run031_phase_validation_B_txd_first_summary.json`
* Summary CSV: `outputs/run031_phase_validation_B_txd_first_summary.csv`
* Validation JSON: `outputs/run031_phase_validation_B_txd_first_validation.json`

Observed receiver-side packet counts:

* TXA/N01: 399
* TXB/N16: 200
* TXC/N31: 97
* TXD/N46: 50

Observed receiver-side ratios:

* TXB/TXA: expected 0.5000, observed 0.5013
* TXC/TXA: expected 0.2500, observed 0.2431
* TXD/TXA: expected 0.1250, observed 0.1253
* TXC/TXB: expected 0.5000, observed 0.4850
* TXD/TXB: expected 0.2500, observed 0.2500
* TXD/TXC: expected 0.5000, observed 0.5155

Observed sequence gaps:

* TXA/N01: none
* TXB/N16: none
* TXC/N31: 2 missing observed transmitted sequences: `[41, 77]`
* TXD/N46: none

Validation result:

* checks_total: 136
* checks_passed: 136
* checks_failed: 0

Condition B is therefore a successful TXD reception case under four-transmitter operation. TXD returned to the expected receiver-side scheduled ratio, with TXD/TXA observed at 0.1253 against the expected 0.1250.

Together, Conditions A and B support the interpretation that programmed startup phase is likely important in this bench setup. Condition C is still useful because it can test whether longer phase separation helps without making TXD first.

## Condition C result: TXA-first stretched programmed phase

Condition C was captured using the TXA-first stretched programmed phase pattern:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 1000 ms
* TXD/N46: 1500 ms

Capture and analysis files:

* Raw receiver log: `logs/rx_run_031_phase_validation_C_txa_first_stretched.csv`
* Parsed valid packets: `logs/parsed_run_031_phase_validation_C_txa_first_stretched.csv`
* Parsed rejects: `logs/parsed_run_031_phase_validation_C_txa_first_stretched_rejects.csv`
* Summary JSON: `outputs/run031_phase_validation_C_txa_first_stretched_summary.json`
* Summary CSV: `outputs/run031_phase_validation_C_txa_first_stretched_summary.csv`
* Validation JSON: `outputs/run031_phase_validation_C_txa_first_stretched_validation.json`

Observed receiver-side packet counts:

* TXA/N01: 372
* TXB/N16: 187
* TXC/N31: 1
* TXD/N46: 46

Observed receiver-side ratios:

* TXB/TXA: expected 0.5000, observed 0.5027
* TXC/TXA: expected 0.2500, observed 0.0027
* TXD/TXA: expected 0.1250, observed 0.1237
* TXC/TXB: expected 0.5000, observed 0.0053
* TXD/TXB: expected 0.2500, observed 0.2460
* TXD/TXC: expected 0.5000, observed 46.0000

Observed sequence gaps:

* TXA/N01: 2 missing observed transmitted sequences: `[157, 239]`
* TXB/N16: none
* TXC/N31: none, but only one TXC packet was received
* TXD/N46: none

Validation result:

* checks_total: 136
* checks_passed: 136
* checks_failed: 0

Condition C is therefore not a full four-transmitter success. TXD reception remained close to its expected receiver-side ratio, but TXC nearly disappeared.

## Receiver-side phase-residue diagnostic

A receiver-side phase-residue check was run across Conditions A, B, and C using received packet times relative to the first received packet in each capture. This diagnostic does not establish synchronized transmit latency, exact transmitted-packet counts, or confirmed collisions. It is only a receiver-side check for repeated phase structure in the received logs.

The A/B/C pattern suggests that the reception problem may depend on relative phase alignment with TXA's fixed-all 1 s rhythm:

* In Condition A, TXA used 0 ms and TXD used 1000 ms. TXD produced zero received packets.
* In Condition B, TXD used 0 ms while TXA used 500 ms. TXD was received successfully, with TXD/TXA observed at 0.1253 against the expected 0.1250.
* In Condition C, TXA used 0 ms and TXC used 1000 ms. TXC produced only one received packet.
* In Condition C, TXD used 1500 ms and was received successfully, with TXD/TXA observed at 0.1237 against the expected 0.1250.

This suggests that the issue is not TXD identity alone and not a standalone 1000 ms startup offset defect. A more precise hypothesis is that sparse scheduled transmitters can be poorly received when their programmed replay phase aligns with TXA's fixed-all 1 s rhythm modulo the slot interval.

This remains a phase/schedule-interaction hypothesis. The current receiver-side logs do not prove packet collisions or exact transmitted-packet counts.

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
