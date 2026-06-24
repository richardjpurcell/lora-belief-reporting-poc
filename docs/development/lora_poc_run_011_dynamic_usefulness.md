# LoRa PoC Run 011: Dynamic Usefulness Metadata

## Purpose

Run 011 moves the LoRa proof of concept from fixed usefulness metadata to time-varying usefulness metadata while preserving the same packet schema used in the previous delivery/usefulness runs.

The purpose is to test whether the receiver/logger/parser pipeline can show not only which node delivered more usefulness over a run, but also when useful packets were delivered.

This is a v0.2 step in the project arc:

* v0.1: fixed usefulness metadata and reporting-rate ladder
* v0.2: dynamic usefulness metadata generated directly in firmware
* v0.3: trace-file-driven synthetic packet metadata
* v0.4: synthetic belief-demand trace generator
* v0.5: LoRa testbed replay of belief-demand traces
* v0.6: policy comparison under constrained LoRa airtime

## Hardware and setup

The run used three LilyGO LoRa32 T3 V1.6.1 boards in point-to-point LoRa mode at 915 MHz:

* one receiver board
* one TX-A board
* one TX-B board

The experiment used point-to-point LoRa, not LoRaWAN. Antennas were attached. Firmware was uploaded using Arduino IDE.

## Firmware configuration

Run identifier:

* `R11`

Reporting interval:

* TXA/N01: 1000 ms delay
* TXB/N16: 1000 ms delay

Packet schema:

`RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr`

TX-A/N01 was configured as a lower-value baseline stream with mild deterministic variation:

* usefulness approximately 0.20–0.35
* priority approximately 0.25–0.40
* policy `R`

TX-B/N16 was configured as a demand-like stream whose usefulness and priority change by sequence phase:

* phase 0: usefulness 0.20, priority 0.30
* phase 1: usefulness 0.85, priority 0.95
* phase 2: usefulness 0.30, priority 0.40
* phase 3: usefulness 0.90, priority 0.95

Each phase lasts 50 sequence numbers and repeats by modulo arithmetic.

## Logging and parser command

The receiver log was saved as:

`logs/rx_run_011_dynamic_usefulness.csv`

The parser was run with a 50-packet sequence-window summary:

`python scripts/parse_receiver_log.py --infile logs/rx_run_011_dynamic_usefulness.csv --out logs/parsed_run_011_dynamic_usefulness.csv --seq-window 50`

The parsed valid packets were written to:

`logs/parsed_run_011_dynamic_usefulness.csv`

Malformed or rejected rows were written to:

`logs/parsed_run_011_dynamic_usefulness_rejects.csv`

## Whole-run results

Run 011 produced 360 valid packets and 0 malformed packets.

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     180 |
| N16  |     180 |

Packets by transmitter and node:

| Transmitter | Node | Packets |
| ----------- | ---- | ------: |
| TXA         | N01  |     180 |
| TXB         | N16  |     180 |

Sequence ranges:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |     417 |     596 |   180 |
| N16  |     337 |     516 |   180 |

Observed sequence gaps:

| Stream  | Missing sequences |
| ------- | ----------------- |
| TXA/N01 | none              |
| TXB/N16 | none              |

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     180 |             49.5 |           0.275 |           58.5 |         0.325 |
| N16  |     180 |            106.5 |           0.592 |          122.0 |         0.678 |

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -42.42 |    -45.0 |    -39.0 |     9.55 |     7.5 |    10.5 |
| N16  |    -49.23 |    -70.0 |    -44.0 |     9.84 |     9.0 |    10.5 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min |   Max |
| ---- | ----: | ----: | ----: |
| N01  | 1.088 | 1.087 | 1.089 |
| N16  | 1.088 | 1.088 | 1.088 |

## Sequence-window usefulness results

The new parser option `--seq-window 50` summarizes usefulness and priority by transmitter, node, and sequence window.

TX-A/N01 remained a low-value baseline stream across all observed windows:

| TX  | Node | Seq window | Packets | Mean usefulness | Mean priority |
| --- | ---- | ---------: | ------: | --------------: | ------------: |
| TXA | N01  |    400–449 |      33 |           0.274 |         0.324 |
| TXA | N01  |    450–499 |      50 |           0.277 |         0.327 |
| TXA | N01  |    500–549 |      50 |           0.273 |         0.323 |
| TXA | N01  |    550–599 |      47 |           0.276 |         0.326 |

TX-B/N16 showed the intended dynamic usefulness pattern:

| TX  | Node | Seq window | Packets | Mean usefulness | Mean priority | Interpretation             |
| --- | ---- | ---------: | ------: | --------------: | ------------: | -------------------------- |
| TXB | N16  |    300–349 |      13 |           0.300 |         0.400 | partial low/moderate phase |
| TXB | N16  |    350–399 |      50 |           0.900 |         0.950 | high-usefulness phase      |
| TXB | N16  |    400–449 |      50 |           0.200 |         0.300 | low-usefulness phase       |
| TXB | N16  |    450–499 |      50 |           0.850 |         0.950 | high-usefulness phase      |
| TXB | N16  |    500–549 |      17 |           0.300 |         0.400 | partial low/moderate phase |

## Interpretation

Run 011 demonstrates that the LoRa proof-of-concept pipeline can carry and recover time-varying usefulness metadata.

The run is especially clean because TXA/N01 and TXB/N16 delivered the same number of packets:

* TXA/N01: 180 packets
* TXB/N16: 180 packets

Both streams also had no observed sequence gaps.

Despite equal received packet counts, the delivered usefulness differed substantially:

* TXA/N01 total usefulness: 49.5
* TXB/N16 total usefulness: 106.5

This supports the central project claim that delivery count and delivered usefulness are not equivalent. In this run, the physical delivery outcome was balanced, but the epistemic/usefulness metadata produced different usefulness totals and a visible temporal usefulness pattern.

The sequence-window summary is the main Run 011 addition. It shows that useful packets were not merely accumulated over the whole run; they arrived in identifiable high-usefulness and low-usefulness phases.

## Cautions

The run captured in-progress transmitter sequences rather than starting at sequence zero. Therefore, the observed sequence windows begin at TXA/N01 sequence 417 and TXB/N16 sequence 337. This does not affect the interpretation because the firmware phase logic is sequence-based and repeats by modulo arithmetic.

The receiver and transmitter clocks are not synchronized. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency.

There were no observed sequence gaps in this run. In other runs, sequence gaps should be described as observed sequence gaps, not as collisions, unless a later experiment is specifically designed to isolate collision effects.

## Next step

The next useful step is to repeat Run 011 from freshly reset transmitters so the observed sequence windows begin closer to zero. This would make the dynamic usefulness pattern easier to present in documentation and figures.

A second useful follow-up is to repeat the same dynamic usefulness pattern at a higher reporting rate, such as 750 ms, to test whether the temporal usefulness pattern remains recoverable when observed sequence gaps begin to appear.
