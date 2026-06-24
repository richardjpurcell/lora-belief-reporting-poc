# LoRa PoC Run 013: Dynamic Usefulness at 750 ms

## Purpose

Run 013 repeats the dynamic-usefulness experiment at a higher reporting rate.

Runs 011 and 012 showed that the LoRa proof-of-concept pipeline can carry and recover time-varying usefulness metadata. Run 012 was the clean-reset 1000 ms result: it showed nearly equal packet delivery counts but substantially different delivered usefulness, with the intended TXB/N16 low/high/low/high usefulness phases recovered by sequence-window analysis.

Run 013 keeps the same dynamic usefulness pattern but reduces the reporting interval from 1000 ms to 750 ms. The purpose is to test whether the temporal usefulness pattern remains recoverable under higher reporting pressure, where observed sequence gaps may begin to appear.

## Project stage

Run 013 extends the v0.2 dynamic-usefulness stage of the project.

The project arc is:

* v0.1: fixed usefulness metadata and reporting-rate ladder
* v0.2: dynamic usefulness metadata generated directly in firmware
* v0.3: trace-file-driven synthetic packet metadata
* v0.4: synthetic belief-demand trace generator
* v0.5: LoRa testbed replay of belief-demand traces
* v0.6: policy comparison under constrained LoRa airtime

Run 013 is not yet a policy-comparison experiment. It is a stress repeat of the dynamic metadata pipeline.

## Hardware and setup

The run used three LilyGO LoRa32 T3 V1.6.1 boards in point-to-point LoRa mode at 915 MHz:

* one receiver board
* one TX-A board
* one TX-B board

The experiment used point-to-point LoRa, not LoRaWAN. Antennas were attached. Firmware was uploaded using Arduino IDE.

The receiver logger was started first. The transmitter boards were then reset so that the observed packet sequences began at sequence zero.

## Firmware configuration

Run identifier:

* `R13`

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

`logs/rx_run_013_dynamic_usefulness_750ms.csv`

The parser was run with a 50-packet sequence-window summary:

`python scripts/parse_receiver_log.py --infile logs/rx_run_013_dynamic_usefulness_750ms.csv --out logs/parsed_run_013_dynamic_usefulness_750ms.csv --seq-window 50`

The parsed valid packets were written to:

`logs/parsed_run_013_dynamic_usefulness_750ms.csv`

Malformed or rejected rows were written to:

`logs/parsed_run_013_dynamic_usefulness_750ms_rejects.csv`

## Whole-run results

Run 013 produced 529 valid packets and 0 malformed packets.

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     266 |
| N16  |     263 |

Packets by transmitter and node:

| Transmitter | Node | Packets |
| ----------- | ---- | ------: |
| TXA         | N01  |     266 |
| TXB         | N16  |     263 |

Sequence ranges:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     266 |   266 |
| N16  |       0 |     263 |   263 |

Observed sequence gaps:

| Stream  | Missing sequences   |
| ------- | ------------------- |
| TXA/N01 | 1 observed gap: 261 |
| TXB/N16 | 1 observed gap: 146 |

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     266 |            73.10 |           0.275 |           86.4 |         0.325 |
| N16  |     263 |           134.10 |           0.510 |          157.9 |         0.600 |

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -45.39 |    -58.0 |    -43.0 |     9.69 |    8.75 |   10.50 |
| N16  |    -49.72 |    -60.0 |    -46.0 |     9.72 |    7.00 |   10.75 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min |   Max |
| ---- | ----: | ----: | ----: |
| N01  | 0.839 | 0.833 | 1.676 |
| N16  | 0.839 | 0.833 | 1.676 |

## Sequence-window usefulness results

The parser option `--seq-window 50` summarizes usefulness and priority by transmitter, node, and sequence window.

TX-A/N01 remained a stable lower-value baseline stream across the observed sequence windows:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: |
| TXA | N01  |       0–49 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |      50–99 |      50 |             0 |           0.277 |         0.327 |
| TXA | N01  |    100–149 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |    150–199 |      50 |             0 |           0.277 |         0.327 |
| TXA | N01  |    200–249 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |    250–299 |      16 |             1 |           0.278 |         0.328 |

TX-B/N16 showed the intended dynamic usefulness pattern despite one observed sequence gap:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority | Interpretation                                      |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: | --------------------------------------------------- |
| TXB | N16  |       0–49 |      50 |             0 |           0.200 |         0.300 | low-usefulness phase                                |
| TXB | N16  |      50–99 |      50 |             0 |           0.850 |         0.950 | high-usefulness phase                               |
| TXB | N16  |    100–149 |      49 |             1 |           0.300 |         0.400 | moderate/low-usefulness phase with one observed gap |
| TXB | N16  |    150–199 |      50 |             0 |           0.900 |         0.950 | high-usefulness phase                               |
| TXB | N16  |    200–249 |      50 |             0 |           0.200 |         0.300 | low-usefulness phase                                |
| TXB | N16  |    250–299 |      14 |             0 |           0.850 |         0.950 | partial high-usefulness phase                       |

## Interpretation

Run 013 demonstrates that the dynamic usefulness pattern remains legible at a higher reporting rate.

The two streams delivered similar numbers of packets:

* TXA/N01: 266 packets
* TXB/N16: 263 packets

Both streams showed one observed sequence gap:

* TXA/N01: sequence 261
* TXB/N16: sequence 146

Despite similar delivery counts and light observed sequence gaps, the delivered usefulness differed substantially:

* TXA/N01 total usefulness: 73.10
* TXB/N16 total usefulness: 134.10

This supports the proof-of-concept claim that delivery count and delivered usefulness are not equivalent. It also shows that the temporal usefulness structure can remain recoverable under a higher reporting rate.

The sequence-window summary is the key result. TXB/N16 preserved the intended low/high/low/high usefulness phases:

* 0–49: low usefulness
* 50–99: high usefulness
* 100–149: moderate/low usefulness, with one observed gap
* 150–199: high usefulness
* 200–249: low usefulness
* 250–263: partial high-usefulness phase

The observed gap in TXB/N16 occurred at sequence 146, inside the 100–149 moderate/low-usefulness phase. The window mean usefulness remained 0.300, matching the intended phase. This is useful because it shows that a light observed sequence gap did not obscure the phase-level usefulness pattern.

TXA/N01 remained stable near mean usefulness 0.275 across all observed windows, making it a useful lower-value baseline.

## Comparison with Run 012

Run 012 was the clean-reset 1000 ms dynamic-usefulness result. Run 013 repeats the same dynamic usefulness pattern at 750 ms.

| Run     | Interval | TXA packets | TXB packets | TXA observed gaps | TXB observed gaps | TXA total usefulness | TXB total usefulness |
| ------- | -------: | ----------: | ----------: | ----------------: | ----------------: | -------------------: | -------------------: |
| Run 012 |  1000 ms |         245 |         247 |                 4 |                 0 |                67.35 |               121.90 |
| Run 013 |   750 ms |         266 |         263 |                 1 |                 1 |                73.10 |               134.10 |

Run 013 increased reporting pressure while preserving the dynamic usefulness signal. The run produced light observed sequence gaps, but the sequence-window analysis still recovered the intended TXB/N16 usefulness phases.

## Cautions

The receiver and transmitter clocks are not synchronized. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency.

Observed sequence gaps should be described as observed sequence gaps only. They indicate packets not received or not logged within the observed sequence range. They are not interpreted as collisions because this run was not designed to isolate collision effects.

The final sequence windows are partial because the run ended at TXA/N01 sequence 266 and TXB/N16 sequence 263.

## Significance for the project

Run 013 strengthens the dynamic-usefulness milestone by showing that the usefulness pattern remains recoverable under higher reporting pressure.

Together, Runs 012 and 013 support the project’s central claim:

* packet delivery count is not the same as delivered usefulness;
* synthetic usefulness metadata can be carried by physical LoRa packets;
* sequence-window analysis can recover temporal usefulness structure from received packet streams;
* observed sequence gaps, when light, do not necessarily erase the phase-level usefulness pattern.

This provides a practical bridge toward later trace-driven experiments, where usefulness and priority will be generated from a synthetic belief-demand trace rather than hand-coded firmware phases.

## Next step

The next useful step is to commit this Run 013 documentation and then decide whether to preserve the current result as a dynamic-usefulness stress checkpoint.

A reasonable follow-up experiment is a repeat of Run 013 at 750 ms to check reproducibility of the light-gap, recoverable-pattern result.

Another possible follow-up is a more aggressive reporting interval, such as 500 ms, but that should be treated as a stress test rather than the main dynamic-usefulness demonstration.
