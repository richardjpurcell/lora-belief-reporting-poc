# Run 033 eight-transmitter synthesis

## Purpose

This note synthesizes the Run 033 eight-transmitter physical replay milestone.

Run 033 was designed as a cautious bridge between the validated Run 032 six-transmitter replay and a future larger physical replay platform. It was not intended to jump directly to twelve transmitters or to make a general claim about arbitrary LoRa network scaling.

The central question was:

Can an eight-transmitter SD-backed scheduled replay preserve manifest-defined scheduled SEND ratios in receiver-side packet counts under a bounded physical bench condition?

The answer is yes, with an important method caveat: startup phase must be treated as part of the physical replay method.

## Position in the scaling ladder

The current physical replay ladder is:

| Run | Scale | Main result |
| --- | ---: | --- |
| Run 030 | 3 transmitters | Multi-transmitter manifest-bound replay became practical. |
| Run 031 | 4 transmitters | Startup-phase sensitivity became visible and was validated. |
| Run 032 | 6 transmitters | Clean six-transmitter SD-backed replay validated the next scale point. |
| Run 033 | 8 transmitters | Eight-transmitter replay succeeded after deterministic startup-phase deconfliction. |

Run 033 therefore extends the validated scale point from six to eight physical transmitters, but it also changes the method: phase-aware startup planning is now required for larger physical replay runs.

## What Run 033 showed

The final phase-shifted Run 033 candidate produced:

- 1192 valid packets
- 0 malformed packets
- all eight transmitters receiver-visible
- observed receiver-side ratios close to manifest-defined scheduled SEND ratios
- 221/221 manifest replay validation checks passed

Per-transmitter received packet counts:

| TX | Node | Received packets | Scheduled SEND rows |
| --- | --- | ---: | ---: |
| TXA | N01 | 427 | 64/64 |
| TXB | N16 | 214 | 32/64 |
| TXC | N31 | 106 | 16/64 |
| TXD | N46 | 53 | 8/64 |
| TXE | N61 | 211 | 32/64 |
| TXF | N76 | 102 | 16/64 |
| TXG | N91 | 52 | 8/64 |
| TXH | N106 | 27 | 4/64 |

Expected-vs-observed receiver-side ratios:

| Ratio | Observed | Expected | Difference |
| --- | ---: | ---: | ---: |
| TXB/TXA | 0.5012 | 0.5000 | 0.0012 |
| TXC/TXA | 0.2482 | 0.2500 | -0.0018 |
| TXD/TXA | 0.1241 | 0.1250 | -0.0009 |
| TXE/TXA | 0.4941 | 0.5000 | -0.0059 |
| TXF/TXA | 0.2389 | 0.2500 | -0.0111 |
| TXG/TXA | 0.1218 | 0.1250 | -0.0032 |
| TXH/TXA | 0.0632 | 0.0625 | 0.0007 |

This supports the claim that the scheduled replay method can remain interpretable at eight physical transmitters when startup phase is deconflicted.

## What Run 033 did not show

Run 033 does not establish:

- exact transmitted-packet counts
- confirmed RF collision mechanisms
- absence of collisions
- synchronized latency
- LoRaWAN behavior
- energy savings
- airtime optimization
- live-controller behavior
- twelve-transmitter behavior
- general eight-node behavior across arbitrary physical layouts
- operational wildfire deployment behavior

These boundaries remain important. The project is still validating a bounded physical replay method, not proving a general radio-network scaling law.

## The key method lesson

The first full Run 033 attempts were not clean validation runs. TXH was absent in the first two full-group attempts, and TXD was weak or absent under denser group conditions.

Diagnostic testing showed that TXH was not broken. The receiver could hear TXH by itself, and subset tests showed that individual transmitter/card/receiver paths were viable.

The failure pattern pointed to repeated exact phase coincidences among structured scheduled SEND rows.

The most direct example was TXD and TXF in the earlier phase state: TXD's sparse scheduled SEND opportunities aligned with a subset of TXF's scheduled SEND opportunities. Under that condition, TXD could disappear from the receiver log when TXF and the denser group were active.

Run 033 therefore exposed a phase-scheduling artifact:

Repeated exact schedule-time coincidences can suppress sparse scheduled transmitters in the receiver-side packet log under this bench condition.

This is not stated as a confirmed RF collision mechanism. The receiver log does not prove the exact RF event. The bounded claim is that repeated exact phase coincidence was associated with receiver-side suppression of sparse transmitters, and deterministic deconfliction restored receiver visibility and interpretable ratios.

## Phase deconfliction result

The final phase-shifted offset state was:

| TX | Node | Startup offset, ms |
| --- | --- | ---: |
| TXH | N106 | 100 |
| TXD | N46 | 900 |
| TXA | N01 | 1000 |
| TXF | N76 | 2500 |
| TXB | N16 | 3250 |
| TXC | N31 | 4750 |
| TXE | N61 | 7750 |
| TXG | N91 | 9450 |

This offset state removed exact same-ms scheduled SEND coincidences among scheduled transmitters while preserving:

- the same SD-backed schedules
- the same manifest-defined SEND fractions
- the same fixed slot interval
- the same receiver-side manifest analysis tools

The successful result came from deterministic startup-phase deconfliction, not from changing the schedules or introducing random jitter.

## Interpretation

Run 033 is a successful eight-transmitter bridge result, but it is also a methodological warning.

The simple interpretation would be:

Eight transmitters worked.

The more accurate interpretation is:

Eight transmitters produced interpretable receiver-side packet proportions after startup-phase deconfliction removed repeated exact scheduled SEND coincidences.

This distinction matters because it affects the next scale step. Larger physical replay runs should not simply add transmitters. They should first apply phase-aware startup planning and verify that structured scheduled SEND rows do not create repeated exact coincidences.

## Recommended next milestone

The next recommended milestone is not an immediate ten- or twelve-transmitter replay.

The recommended next milestone is:

v5.5 phase-aware replay method freeze

The goal should be to formalize deterministic startup-phase deconfliction as a reusable part of the physical replay method.

That milestone should define:

- how startup offsets are represented
- how scheduled SEND timing overlaps are checked
- what counts as an exact scheduled SEND coincidence
- what near-coincidence windows should be reported
- how phase plans should be documented before flashing
- how phase plans should be preserved in outputs
- how diagnostics should be named when phase artifacts appear
- when a phase-shifted candidate can become the canonical replay evidence

Only after this method is frozen should the project proceed to a larger bridge, such as ten transmitters or a carefully designed twelve-transmitter replay.

## Recommendation for jitter

Random slot jitter should not be introduced into the primary validation ladder yet.

For the primary ladder, deterministic startup-phase offsets are preferred because they preserve reproducibility. They also keep the fixed slot interval intact, which makes the manifest-bound analysis easier to interpret.

Jitter may be useful later as a separate robustness experiment. Two possible future variants are:

- seeded deterministic startup jitter
- bounded seeded slot-interval jitter

Those should be treated as robustness diagnostics, not as replacements for the canonical deterministic replay condition.

## Bottom line

Run 033 advances the validated physical replay scale point from six to eight transmitters.

Its main contribution is twofold:

1. An eight-transmitter SD-backed scheduled replay can preserve manifest-defined scheduled SEND ratios in receiver-side packet counts under a bounded bench condition.
2. Startup-phase deconfliction is now a required part of the physical replay method for larger N-transmitter runs.

The project should therefore freeze the phase-aware replay method before attempting the next scale jump.
