# LoRa PoC Run 012: Dynamic Usefulness Clean-Reset Repeat

## Purpose

Run 012 is a clean-reset repeat of the Run 011 dynamic-usefulness experiment.

Run 011 confirmed that the LoRa proof-of-concept pipeline can carry and recover time-varying usefulness metadata. However, Run 011 began after both transmitters had already been running, so the observed sequence windows started mid-stream rather than near zero.

Run 012 repeats the same dynamic-usefulness firmware logic with freshly reset transmitters so that the sequence-window summaries begin at sequence zero. This makes the low/high/low/high usefulness pattern easier to inspect, document, and eventually plot.

The purpose is to test whether the receiver/logger/parser pipeline can show not only which node delivered more usefulness, but also when useful packets were delivered.

## Project stage

Run 012 belongs to the v0.2 stage of the project arc:

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

The receiver logger was started first. The transmitter boards were then reset so that the observed packet sequences began near zero.

## Firmware configuration

Run identifier:

* `R12`

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

* sequence phase 0: usefulness 0.20, priority 0.30
* sequence phase 1: usefulness 0.85, priority 0.95
* sequence phase 2: usefulness 0.30, priority 0.40
* sequence phase 3: usefulness 0.90, priority 0.95

Each phase lasts 50 sequence numbers and repeats by modulo arithmetic.

## Logging and parser command

The receiver log was saved as:

`logs/rx_run_012_dynamic_usefulness_clean_reset.csv`

The parser was run with a 50-packet sequence-window summary:

`python scripts/parse_receiver_log.py --infile logs/rx_run_012_dynamic_usefulness_clean_reset.csv --out logs/parsed_run_012_dynamic_usefulness_clean_reset.csv --seq-window 50`

The parsed valid packets were written to:

`logs/parsed_run_012_dynamic_usefulness_clean_reset.csv`

Malformed or rejected rows were written to:

`logs/parsed_run_012_dynamic_usefulness_clean_reset_rejects.csv`

## Whole-run results

Run 012 produced 492 valid packets and 0 malformed packets.

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     245 |
| N16  |     247 |

Packets by transmitter and node:

| Transmitter | Node | Packets |
| ----------- | ---- | ------: |
| TXA         | N01  |     245 |
| TXB         | N16  |     247 |

Sequence ranges:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     248 |   245 |
| N16  |       0 |     246 |   247 |

Observed sequence gaps:

| Stream  | Missing sequences               |
| ------- | ------------------------------- |
| TXA/N01 | 4 observed gaps: 50, 81, 84, 86 |
| TXB/N16 | none                            |

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     245 |            67.35 |           0.275 |           79.6 |         0.325 |
| N16  |     247 |           121.90 |           0.494 |          144.1 |         0.583 |

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -46.68 |    -59.0 |    -43.0 |     9.78 |    9.00 |   10.75 |
| N16  |    -47.46 |    -59.0 |    -44.0 |     9.83 |    9.25 |   10.50 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min |   Max |
| ---- | ----: | ----: | ----: |
| N01  | 1.104 | 1.082 | 2.166 |
| N16  | 1.086 | 1.082 | 1.088 |

## Sequence-window usefulness results

The parser option `--seq-window 50` summarizes usefulness and priority by transmitter, node, and sequence window.

TX-A/N01 remained a stable lower-value baseline stream across the observed sequence windows:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: |
| TXA | N01  |       0–49 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |      50–99 |      46 |             3 |           0.278 |         0.328 |
| TXA | N01  |    100–149 |      50 |             0 |           0.273 |         0.323 |
| TXA | N01  |    150–199 |      50 |             0 |           0.277 |         0.327 |
| TXA | N01  |    200–249 |      49 |             0 |           0.273 |         0.323 |

TX-B/N16 showed the intended dynamic usefulness pattern:

| TX  | Node | Seq window | Packets | Missing count | Mean usefulness | Mean priority | Interpretation                |
| --- | ---- | ---------: | ------: | ------------: | --------------: | ------------: | ----------------------------- |
| TXB | N16  |       0–49 |      50 |             0 |           0.200 |         0.300 | low-usefulness phase          |
| TXB | N16  |      50–99 |      50 |             0 |           0.850 |         0.950 | high-usefulness phase         |
| TXB | N16  |    100–149 |      50 |             0 |           0.300 |         0.400 | moderate/low-usefulness phase |
| TXB | N16  |    150–199 |      50 |             0 |           0.900 |         0.950 | high-usefulness phase         |
| TXB | N16  |    200–249 |      47 |             0 |           0.200 |         0.300 | partial low-usefulness phase  |

## Interpretation

Run 012 provides a clean-reset dynamic-usefulness result.

The two streams delivered nearly the same number of packets:

* TXA/N01: 245 packets
* TXB/N16: 247 packets

However, their delivered usefulness differed substantially:

* TXA/N01 total usefulness: 67.35
* TXB/N16 total usefulness: 121.90

This supports the central proof-of-concept claim that delivery count and delivered usefulness are not equivalent. In this run, physical delivery counts were very similar, but the usefulness metadata produced different total usefulness values and a clearly recoverable temporal usefulness pattern.

The sequence-window summary is the key result. TXB/N16 alternated between low-usefulness and high-usefulness phases, and the parser recovered that pattern directly from the received LoRa packet stream:

* 0–49: low usefulness
* 50–99: high usefulness
* 100–149: moderate/low usefulness
* 150–199: high usefulness
* 200–246: partial low-usefulness phase

TXA/N01 remained stable near mean usefulness 0.275 across all observed windows, making it a useful lower-value baseline.

## Cautions

The receiver and transmitter clocks are not synchronized. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency.

TXA/N01 showed four observed sequence gaps. TXB/N16 showed none. These should be described as observed sequence gaps only. They are not interpreted as collisions because this run was not designed to isolate collision effects.

The final sequence window for TXB/N16 was partial because the run ended at sequence 246.

## Significance for the project

Run 012 strengthens the v0.2 milestone.

Run 011 showed that dynamic usefulness metadata works. Run 012 improves presentation clarity by starting the observed sequence windows at zero and recovering the intended demand-like phase structure cleanly.

This run provides a concrete bridge from the fixed metadata reporting-rate ladder toward later trace-driven experiments. It shows that a physical LoRa testbed can carry synthetic epistemic metadata and that the analysis pipeline can distinguish packet delivery from usefulness delivery over time.

## Next step

The next useful step is to update the README with a short v0.2 progress note.

After that, there are two reasonable paths:

1. preserve this clean 1000 ms dynamic-usefulness result as the v0.2 checkpoint, or
2. repeat the dynamic-usefulness experiment at a higher reporting rate, such as 750 ms, to test whether the temporal usefulness pattern remains recoverable when observed sequence gaps begin to appear.

The recommended next experimental run is a 750 ms dynamic-usefulness stress repeat, using the same phase logic but a shorter reporting interval.
