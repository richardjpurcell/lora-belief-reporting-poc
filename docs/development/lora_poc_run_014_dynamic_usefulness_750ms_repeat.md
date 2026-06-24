# LoRa PoC Run 014: Dynamic Usefulness at 750 ms Repeat

## Purpose

Run 014 repeats the Run 013 dynamic-usefulness stress condition.

Run 013 reduced the reporting interval from 1000 ms to 750 ms while preserving the same dynamic usefulness pattern. It showed that the TXB/N16 temporal usefulness pattern remained recoverable under higher reporting pressure, even with light observed sequence gaps.

Run 014 repeats the 750 ms condition to check whether the same qualitative result appears again: nearly balanced packet delivery, substantially different delivered usefulness, and recoverable sequence-window usefulness phases.

The purpose is reproducibility, not a new policy comparison.

## Project stage

Run 014 extends the v0.2 dynamic-usefulness stage of the project.

The project arc is:

* v0.1: fixed usefulness metadata and reporting-rate ladder
* v0.2: dynamic usefulness metadata generated directly in firmware
* v0.3: trace-file-driven synthetic packet metadata
* v0.4: synthetic belief-demand trace generator
* v0.5: LoRa testbed replay of belief-demand traces
* v0.6: policy comparison under constrained LoRa airtime

Run 014 remains a hand-coded dynamic metadata experiment. It is not yet trace-file-driven and not yet a usefulness-aware reporting policy.

## Hardware and setup

The run used three LilyGO LoRa32 T3 V1.6.1 boards in point-to-point LoRa mode at 915 MHz:

* one receiver board
* one TX-A board
* one TX-B board

The experiment used point-to-point LoRa, not LoRaWAN. Antennas were attached. Firmware was uploaded using Arduino IDE.

The receiver logger was started first. The transmitter boards were then reset so that the observed packet sequences began at sequence zero.

## Firmware configuration

Run identifier:

* `R14`

Reporting interval:

* TXA/N01: 750 ms delay
* TXB/N16: 750 ms delay

Packet schema:

`RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr`

TX-A/N01 was configured as a lower-value baseline stream with mild deterministic variation:

* usefulness approximately 0.20–0.35
* priority approximately 0.25–0.40
* policy `R`

TX-B/N16 was configured as a demand-like stream whose usefulness and priority change by sequence phase:

* sequence phase 0: usefulness 0.20, priority 0.30
* sequence phase 1: usefulness 0.85, priority 0.95
* sequence phase 2: usefulness 0.30, priority 0.40
* sequence phase 3: usefulness 0.90, priority 0.95

Each phase lasts 50 sequence numbers and repeats by modulo arithmetic.

## Logging and parser command

The receiver log was saved as:

`logs/rx_run_014_dynamic_usefulness_750ms_repeat.csv`

The parser was run with a 50-packet sequence-window summary:

`python scripts/parse_receiver_log.py --infile logs/rx_run_014_dynamic_usefulness_750ms_repeat.csv --out logs/parsed_run_014_dynamic_usefulness_750ms_repeat.csv --seq-window 50`

The parsed valid packets were written to:

`logs/parsed_run_014_dynamic_usefulness_750ms_repeat.csv`

Malformed or rejected rows were written to:

`logs/parsed_run_014_dynamic_usefulness_750ms_repeat_rejects.csv`

## Whole-run results

Run 014 produced 725 valid packets and 0 malformed packets.

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     363 |
| N16  |     362 |

Packets by transmitter and node:

| Transmitter | Node | Packets |
| ----------- | ---- | ------: |
| TXA         | N01  |     363 |
| TXB         | N16  |     362 |

Sequence ranges:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     367 |   363 |
| N16  |       0 |     363 |   362 |

Observed sequence gaps:

| Stream  | Missing sequences                      |
| ------- | -------------------------------------- |
| TXA/N01 | 5 observed gaps: 40, 57, 237, 328, 329 |
| TXB/N16 | 2 observed gaps: 118, 326              |

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     363 |           100.05 |           0.276 |          118.2 |         0.326 |
| N16  |     362 |           192.00 |           0.530 |          225.0 |         0.622 |

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -46.53 |    -66.0 |    -43.0 |     9.69 |    7.25 |   10.75 |
| N16  |    -50.37 |    -53.0 |    -47.0 |     9.77 |    9.00 |   12.00 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min |   Max |
| ---- | ----: | ----: | ----: |
| N01  | 0.848 | 0.832 | 2.514 |
| N16  | 0.841 | 0.832 | 1.676 |

## Sequence-window usefulness results

The parser option `--seq-window 50` summarizes usefulness and priority by transmitter, node, and sequence window.

TX-A/N01 remained a stable lower-value baseline stream across the observed sequence windows:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: |
| TXA | N01  |       0–49 |      49 |             1 |           0.274 |         0.324 |
| TXA | N01  |      50–99 |      49 |             1 |           0.278 |         0.328 |
| TXA | N01  |    100–149 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |    150–199 |      50 |             0 |           0.277 |         0.327 |
| TXA | N01  |    200–249 |      49 |             1 |           0.273 |         0.323 |
| TXA | N01  |    250–299 |      50 |             0 |           0.277 |         0.327 |
| TXA | N01  |    300–349 |      48 |             2 |           0.275 |         0.325 |
| TXA | N01  |    350–399 |      18 |             0 |           0.281 |         0.331 |

TX-B/N16 showed the intended dynamic usefulness pattern despite two observed sequence gaps:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority | Interpretation                                      |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: | --------------------------------------------------- |
| TXB | N16  |       0–49 |      50 |             0 |           0.200 |         0.300 | low-usefulness phase                                |
| TXB | N16  |      50–99 |      50 |             0 |           0.850 |         0.950 | high-usefulness phase                               |
| TXB | N16  |    100–149 |      49 |             1 |           0.300 |         0.400 | moderate/low-usefulness phase with one observed gap |
| TXB | N16  |    150–199 |      50 |             0 |           0.900 |         0.950 | high-usefulness phase                               |
| TXB | N16  |    200–249 |      50 |             0 |           0.200 |         0.300 | low-usefulness phase                                |
| TXB | N16  |    250–299 |      50 |             0 |           0.850 |         0.950 | high-usefulness phase                               |
| TXB | N16  |    300–349 |      49 |             1 |           0.300 |         0.400 | moderate/low-usefulness phase with one observed gap |
| TXB | N16  |    350–399 |      14 |             0 |           0.900 |         0.950 | partial high-usefulness phase                       |

## Interpretation

Run 014 confirms the main Run 013 stress-result pattern.

The two streams delivered nearly equal numbers of packets:

* TXA/N01: 363 packets
* TXB/N16: 362 packets

Both streams showed observed sequence gaps:

* TXA/N01: 5 observed sequence gaps
* TXB/N16: 2 observed sequence gaps

Despite nearly equal delivery counts, TXB/N16 delivered substantially more total usefulness:

* TXA/N01 total usefulness: 100.05
* TXB/N16 total usefulness: 192.00

This supports the proof-of-concept claim that delivery count and delivered usefulness are not equivalent. It also shows that the temporal usefulness structure can remain recoverable under higher reporting pressure.

The sequence-window summary is the key result. TXB/N16 preserved the intended repeating usefulness pattern:

* 0–49: low usefulness
* 50–99: high usefulness
* 100–149: moderate/low usefulness, with one observed gap
* 150–199: high usefulness
* 200–249: low usefulness
* 250–299: high usefulness
* 300–349: moderate/low usefulness, with one observed gap
* 350–363: partial high-usefulness phase

The observed gaps in TXB/N16 occurred at sequences 118 and 326. Both were inside moderate/low-usefulness phase windows. The window means remained 0.300, matching the intended phase. This shows that light observed sequence gaps did not obscure the phase-level usefulness pattern.

TXA/N01 remained stable near mean usefulness 0.275 across all observed windows, making it a useful lower-value baseline.

## Comparison with Run 013

Run 013 was the first 750 ms dynamic-usefulness stress run. Run 014 repeats the same condition.

| Run     | Interval | TXA packets | TXB packets | TXA observed gaps | TXB observed gaps | TXA total usefulness | TXB total usefulness |
| ------- | -------: | ----------: | ----------: | ----------------: | ----------------: | -------------------: | -------------------: |
| Run 013 |   750 ms |         266 |         263 |                 1 |                 1 |                73.10 |               134.10 |
| Run 014 |   750 ms |         363 |         362 |                 5 |                 2 |               100.05 |               192.00 |

Run 014 was longer than Run 013, so the higher absolute packet counts, usefulness totals, and observed gap counts are expected. The important comparison is qualitative: both runs preserved the delivery/usefulness separation, and both runs recovered the TXB/N16 dynamic usefulness phases.

## Cautions

The receiver and transmitter clocks are not synchronized. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency.

Observed sequence gaps should be described as observed sequence gaps only. They indicate packets not received or not logged within the observed sequence range. They are not interpreted as collisions because this run was not designed to isolate collision effects.

The final sequence windows are partial because the run ended at TXA/N01 sequence 367 and TXB/N16 sequence 363.

## Significance for the project

Run 014 strengthens the dynamic-usefulness stress result by repeating the 750 ms condition.

Together, Runs 013 and 014 show that under higher reporting pressure:

* packet delivery count remains distinct from delivered usefulness;
* synthetic usefulness metadata can be carried by physical LoRa packets;
* sequence-window analysis can recover temporal usefulness structure from received packet streams;
* observed sequence gaps, when light, do not necessarily erase the phase-level usefulness pattern.

This provides a practical bridge toward later trace-driven experiments, where usefulness and priority will be generated from a synthetic belief-demand trace rather than hand-coded firmware phases.

## Next step

The next useful step is to commit this Run 014 documentation and then preserve the branch as a repeat stress checkpoint.

After that, the project can move in one of two directions:

1. perform a more aggressive reporting-rate stress test, such as 500 ms, or
2. begin v0.3 by replacing hand-coded usefulness phases with a small trace-file-driven metadata sequence.

The recommended next conceptual step is v0.3 trace-file-driven metadata, because Runs 012–014 already provide a coherent dynamic-usefulness result set.
