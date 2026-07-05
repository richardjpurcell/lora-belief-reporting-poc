# Run 033 eight-transmitter physical replay

## Purpose

Run 033 extends the scheduled physical replay scaling ladder from six transmitters to eight transmitters.

The goal was not to claim general eight-node LoRa behavior. The goal was to test whether the manifest-bound scheduled replay method still produced interpretable receiver-side packet proportions when eight physical transmitters replayed SD-backed schedules with different scheduled SEND fractions.

## Input schedule design

Run 033 used eight transmitters over a 64-row scheduled replay window.

| TX  | Node | Role                   | Scheduled SEND rows |
| --- | ---- | ---------------------- | ------------------: |
| TXA | N01  | fixed-all anchor       |               64/64 |
| TXB | N16  | medium threshold       |               32/64 |
| TXC | N31  | strict threshold       |               16/64 |
| TXD | N46  | very-strict threshold  |                8/64 |
| TXE | N61  | medium threshold       |               32/64 |
| TXF | N76  | strict threshold       |               16/64 |
| TXG | N91  | very-strict threshold  |                8/64 |
| TXH | N106 | ultra-strict threshold |                4/64 |

The expected receiver-side ratios relative to TXA were therefore:

| Ratio   | Expected |
| ------- | -------: |
| TXB/TXA |   0.5000 |
| TXC/TXA |   0.2500 |
| TXD/TXA |   0.1250 |
| TXE/TXA |   0.5000 |
| TXF/TXA |   0.2500 |
| TXG/TXA |   0.1250 |
| TXH/TXA |   0.0625 |

## Initial full-group attempts

The first full eight-transmitter capture was not treated as a clean replay result. It showed TXH absent from the receiver log:

* logs/rx_run_033_eight_transmitter_sd_replay_attempt1_txh_absent.csv

A second full-group attempt again showed TXH absent, with TXD also weak:

* logs/rx_run_033_eight_transmitter_sd_replay_attempt2_txh_absent_txd_weak.csv

These attempts were preserved as diagnostic evidence rather than used as the canonical Run 033 physical replay.

## Diagnostic probes

TXH was tested by itself and confirmed receiver-visible:

* logs/rx_run_033_txh_receiver_probe.csv

Additional subset testing showed that the issue was not a simple bad card, firmware image, antenna path, or receiver incompatibility. TXH could be heard under reduced group conditions, and TXD could appear under some subset conditions.

The failure pattern pointed to a group-level timing interaction.

## Phase artifact

The original startup-phase plan produced repeated exact scheduled SEND coincidences among structured schedules.

The most direct example was TXD and TXF. TXD's scheduled SEND opportunities were a subset of TXF's scheduled SEND opportunities under the original phase state, so every TXD scheduled SEND could land at the same schedule-relative time as a TXF scheduled SEND.

This is interpreted as a physical replay phase artifact. It is not treated as a confirmed RF collision claim, because the receiver log alone does not prove the exact RF event. The bounded claim is that repeated exact phase coincidence among structured scheduled SEND rows can suppress sparse transmitters in the receiver-side packet log under this bench condition.

## Phase-shifted startup plan

A deterministic startup-phase deconfliction was used. The schedules and fixed slot interval were preserved; only startup offsets were changed.

Final phase-shifted offsets:

| TX  | Node | Startup offset, ms |
| --- | ---- | -----------------: |
| TXH | N106 |                100 |
| TXD | N46  |                900 |
| TXA | N01  |               1000 |
| TXF | N76  |               2500 |
| TXB | N16  |               3250 |
| TXC | N31  |               4750 |
| TXE | N61  |               7750 |
| TXG | N91  |               9450 |

Under this offset state, the schedule-time overlap check reported no exact same-ms scheduled SEND coincidences among the scheduled transmitters.

## Candidate phase-shifted replay result

Canonical candidate log:

* logs/rx_run_033_eight_transmitter_sd_replay_phase_shifted_candidate.csv

Parsed valid-packet log:

* logs/parsed_run_033_eight_transmitter_sd_replay_phase_shifted_candidate.csv

Malformed/reject log:

* logs/parsed_run_033_eight_transmitter_sd_replay_phase_shifted_candidate_rejects.csv

Analyzer outputs:

* outputs/run033_eight_transmitter_manifest_replay_phase_shifted_candidate_summary.json
* outputs/run033_eight_transmitter_manifest_replay_phase_shifted_candidate_summary.csv

Validation output:

* outputs/run033_eight_transmitter_manifest_replay_phase_shifted_candidate_validation.json

The candidate replay produced:

* 1192 valid packets
* 0 malformed packets
* all eight transmitters receiver-visible
* 221/221 validation checks passed

Per-transmitter received packet counts:

| TX  | Node | Received packets | Scheduled SEND rows |
| --- | ---- | ---------------: | ------------------: |
| TXA | N01  |              427 |               64/64 |
| TXB | N16  |              214 |               32/64 |
| TXC | N31  |              106 |               16/64 |
| TXD | N46  |               53 |                8/64 |
| TXE | N61  |              211 |               32/64 |
| TXF | N76  |              102 |               16/64 |
| TXG | N91  |               52 |                8/64 |
| TXH | N106 |               27 |                4/64 |

Expected-vs-observed receiver-side ratios:

| Ratio   | Observed | Expected | Difference |
| ------- | -------: | -------: | ---------: |
| TXB/TXA |   0.5012 |   0.5000 |     0.0012 |
| TXC/TXA |   0.2482 |   0.2500 |    -0.0018 |
| TXD/TXA |   0.1241 |   0.1250 |    -0.0009 |
| TXE/TXA |   0.4941 |   0.5000 |    -0.0059 |
| TXF/TXA |   0.2389 |   0.2500 |    -0.0111 |
| TXG/TXA |   0.1218 |   0.1250 |    -0.0032 |
| TXH/TXA |   0.0632 |   0.0625 |     0.0007 |

## Interpretation

Run 033 supports the eight-transmitter bridge step, with an important caveat: startup phase is now part of the physical replay method.

The result is not simply that eight transmitters worked. The run exposed a phase-scheduling artifact, then showed that deterministic phase deconfliction could restore interpretable receiver-side packet proportions without changing the schedules or the fixed slot interval.

The main result is therefore:

> Under this bench condition, an eight-transmitter SD-backed scheduled replay produced receiver-side packet proportions close to the manifest-defined scheduled SEND ratios after deterministic startup-phase deconfliction removed exact repeated scheduled SEND coincidences.

## Interpretation boundaries

This result does not establish:

* exact transmitted-packet counts
* confirmed RF collision mechanisms
* synchronized latency
* LoRaWAN behavior
* energy savings
* live-controller behavior
* operational wildfire deployment behavior
* general eight-node behavior across arbitrary physical layouts

It does support:

* manifest-bound analysis of an eight-transmitter physical replay
* preservation of scheduled SEND ratio structure in receiver-side packet counts
* phase-aware physical replay setup as a requirement for larger N-transmitter runs
* a cautious path toward the next scaling step

## Implication for future runs

Future N-transmitter physical replay runs should avoid repeated exact schedule-time coincidences among structured scheduled transmitters.

For the primary validation ladder, deterministic startup-phase offsets are preferred over random slot jitter because they preserve reproducibility and keep the fixed slot interval intact.

Seeded startup jitter or bounded slot jitter may still be useful later as a separate robustness experiment, but should not replace the deterministic replay condition used for milestone validation.
