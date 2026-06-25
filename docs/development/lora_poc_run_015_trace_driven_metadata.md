# LoRa POC Run 015: Trace-Driven Metadata Replay at 1000 ms

## Purpose

Run 015 is the first trace-driven metadata replay experiment in the LoRa belief-reporting proof of concept.

Previous dynamic-usefulness runs generated usefulness and priority metadata directly in transmitter firmware using hard-coded phase logic. Run 015 moves that metadata source into laptop-generated trace CSV files, which are converted into compiled-in C/C++ firmware headers and replayed by sequence index on the transmitters.

This is the first v0.3 step toward the longer-term goal:

belief-maintenance model / synthetic demand trace
→ packet metadata emitted by LoRa transmitters
→ physical LoRa delivery outcomes
→ delivery-versus-usefulness analysis

This run does not yet use SD-card replay. The LilyGO LoRa32 T3 V1.6.1 boards appear to support microSD / TF card use, but Run 015 intentionally keeps replay simple and reproducible by compiling generated traces into transmitter firmware.

## Branch and Commit

Branch:

`exp015-trace-driven-metadata`

Initial trace-driven firmware commit:

`2f439eb Add Run 015 trace-driven metadata replay`

## Hardware and Radio Setup

Hardware:

* 3 LilyGO LoRa32 T3 V1.6.1 boards, 868/915 MHz
* One board configured as RX
* One board configured as TX-A
* One board configured as TX-B
* Antennas attached
* Point-to-point LoRa at 915 MHz
* Arduino IDE used for firmware upload

This is not a LoRaWAN experiment.

## Software Environment

Python environment:

`dcoss-lora-poc`

Known package versions:

* Python 3.11.15
* pyserial 3.5
* pandas 3.0.3

Relevant scripts:

* `scripts/receiver_logger.py`
* `scripts/parse_receiver_log.py`
* `scripts/make_trace_headers.py`

## Trace Files

Run 015 introduced two trace CSV files:

* `traces/run_015_txa_trace.csv`
* `traces/run_015_txb_trace.csv`

Each trace has 250 metadata rows plus a header row.

Trace fields:

`seq,region,event,priority,usefulness,stale_after,policy`

TX-A is a low-value baseline stream:

* `region = A`
* `event = 0`
* `priority = 0.25`
* `usefulness = 0.275`
* `stale_after = 30`
* `policy = B`

TX-B is a demand-like stream with sequence-window phases:

| Sequence range | Priority | Usefulness | Interpretation                    |
| -------------: | -------: | ---------: | --------------------------------- |
|           0–49 |     0.20 |       0.20 | Low demand/usefulness phase       |
|          50–99 |     0.85 |       0.85 | High demand/usefulness phase      |
|        100–149 |     0.30 |       0.30 | Mid-low demand/usefulness phase   |
|        150–199 |     0.90 |       0.90 | Very high demand/usefulness phase |
|        200–249 |     0.20 |       0.20 | Low demand/usefulness phase       |

The trace CSV files were converted into sketch-local headers:

* `firmware/first_radio_link_TX-A/trace_data_TXA.h`
* `firmware/first_radio_link_TX_B/trace_data_TXB.h`

The transmitter sketches include the appropriate header and replay rows from:

`TRACE_ROWS[trace_index % TRACE_ROW_COUNT]`

## Packet Schema

The transmitted packet schema remained unchanged from the v0.2 dynamic-usefulness runs:

`run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy`

The receiver appends radio metadata:

`rssi,snr`

The resulting receiver row schema is:

`RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr`

Example intended TX-B payload structure:

`R15,TXB,N16,50,<tx_ms>,B,1,0.85,0.85,30,U`

Important timing caution:

`recv_ms` and `tx_ms` are not synchronized across boards. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency. Receiver inter-arrival time and observed sequence gaps remain meaningful.

## Run Configuration

Run ID:

`R15`

Transmit interval:

`1000 ms`

Transmitters:

| Transmitter | Logical node | Trace role               |
| ----------- | ------------ | ------------------------ |
| TX-A        | N01          | Low-value baseline       |
| TX-B        | N16          | Demand-like trace phases |

Logger output:

`logs/rx_run_015_trace_driven_1000ms.csv`

Parsed output:

`logs/parsed_run_015_trace_driven_1000ms.csv`

Reject output:

`logs/parsed_run_015_trace_driven_1000ms_rejects.csv`

Parser command:

`python scripts/parse_receiver_log.py --infile logs/rx_run_015_trace_driven_1000ms.csv --out logs/parsed_run_015_trace_driven_1000ms.csv --seq-window 50`

## Parser Summary

Valid packets:

`642`

Malformed packets:

`0`

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     324 |
| N16  |     318 |

Packets by transmitter and node:

| TX ID | Node | Packets |
| ----- | ---- | ------: |
| TXA   | N01  |     324 |
| TXB   | N16  |     318 |

Sequence range by node:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     249 |   324 |
| N16  |       0 |     249 |   318 |

Observed sequence gaps:

| Stream  | Observed gaps       |
| ------- | ------------------- |
| TXA/N01 | none                |
| TXB/N16 | 1 observed gap: 176 |

The observed sequence gap should be interpreted as a packet not received or not logged within the observed sequence range. It should not be treated as direct evidence of collision.

## Radio Metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -44.17 |    -60.0 |    -40.0 |     9.71 |    7.25 |    11.0 |
| N16  |    -58.73 |    -79.0 |    -48.0 |     9.72 |    9.00 |    10.5 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min |   Max |
| ---- | ----: | ----: | ----: |
| N01  | 1.000 | 0.994 | 1.005 |
| N16  | 1.003 | 0.995 | 2.000 |

The TXB/N16 maximum inter-arrival time of approximately 2 seconds is consistent with the single observed sequence gap at sequence 176.

## Usefulness Summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     324 |            90.72 |           0.280 |          81.00 |         0.250 |
| N16  |     318 |           147.75 |           0.465 |         147.75 |         0.465 |

This preserves the main delivery-versus-usefulness separation:

TX-A/N01 and TX-B/N16 had broadly similar delivery counts, but TX-B/N16 delivered substantially more total usefulness because its trace contained high-demand phases.

## Sequence-Window Usefulness

Usefulness by node and sequence window, using `--seq-window 50`:

| TX ID | Node | Seq window | Packets | Missing count | Total usefulness | Mean usefulness |
| ----- | ---- | ---------: | ------: | ------------: | ---------------: | --------------: |
| TXA   | N01  |       0–49 |     100 |             0 |            28.00 |            0.28 |
| TXA   | N01  |      50–99 |      74 |             0 |            20.72 |            0.28 |
| TXA   | N01  |    100–149 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    150–199 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    200–249 |      50 |             0 |            14.00 |            0.28 |
| TXB   | N16  |       0–49 |     100 |             0 |            20.00 |            0.20 |
| TXB   | N16  |      50–99 |      69 |             0 |            58.65 |            0.85 |
| TXB   | N16  |    100–149 |      50 |             0 |            15.00 |            0.30 |
| TXB   | N16  |    150–199 |      49 |             1 |            44.10 |            0.90 |
| TXB   | N16  |    200–249 |      50 |             0 |            10.00 |            0.20 |

TX-B/N16 recovered the intended trace-file phase pattern:

| Sequence range | Expected usefulness | Observed mean usefulness |
| -------------: | ------------------: | -----------------------: |
|           0–49 |                0.20 |                     0.20 |
|          50–99 |                0.85 |                     0.85 |
|        100–149 |                0.30 |                     0.30 |
|        150–199 |                0.90 |                     0.90 |
|        200–249 |                0.20 |                     0.20 |

This is the key Run 015 result.

## Interpretation

Run 015 confirms that LoRa packet metadata can be replayed from laptop-generated trace files compiled into transmitter firmware while preserving the existing packet schema and receiver/parser workflow.

The run demonstrates that:

1. Trace CSVs can be generated on the laptop.
2. Trace CSVs can be converted into firmware headers.
3. TX-A and TX-B can replay trace rows into LoRa packet metadata.
4. The receiver can log the unchanged packet schema.
5. The existing parser can recover transmitter/node summaries, observed sequence gaps, radio metadata, usefulness totals, and sequence-window usefulness phases.
6. The TX-B demand-like usefulness phase pattern remains recoverable from physically received LoRa packets.

The main scientific interpretation remains:

Similar packet delivery counts can carry substantially different delivered usefulness, and sequence-window summaries can recover temporal usefulness phases even when light observed sequence gaps appear.

## Important Caveat: Trace Sequence Wraparound

Run 015 used 250-row trace files and firmware replay logic of the form:

`TRACE_ROWS[trace_index % TRACE_ROW_COUNT]`

Therefore, after sequence 249, the transmitted trace sequence wraps back to sequence 0.

The run captured more than one trace cycle. This is why some sequence windows contain more than 50 packets:

* TXA/N01 sequence window 0–49 contains 100 packets.
* TXB/N16 sequence window 0–49 contains 100 packets.

This is not a firmware failure. It means Run 015 demonstrates cyclic trace replay. However, it makes sequence-window summaries aggregate repeated trace cycles when the run extends past one complete 250-row cycle.

For future runs, a cleaner design would separate:

* transmitted packet sequence number, monotonically increasing, from
* trace row index or trace sequence number, which may repeat cyclically.

That change would remove wraparound ambiguity while preserving trace replay.

## Conclusion

Run 015 successfully establishes v0.3 trace-driven metadata replay.

The experiment moves usefulness and priority metadata out of hard-coded transmitter phase logic and into generated trace files. The LoRa testbed then physically transmits those trace-derived metadata rows, and the existing receiver/parser workflow recovers the intended delivered-usefulness pattern.

This is a useful bridge between the earlier dynamic-usefulness firmware experiments and later synthetic belief-demand trace experiments.

## Recommended Next Step

The recommended next step is a small v0.3.1 firmware/schema refinement:

* keep replaying metadata from trace rows;
* add or preserve a monotonically increasing transmitted packet sequence number;
* optionally include a separate trace index or trace sequence field later;
* avoid interpreting repeated trace-row sequence numbers as repeated packet sequence numbers.

A simpler immediate alternative is to run a shorter single-cycle Run 016 and stop before sequence wraparound, but the more robust path is to patch the firmware so transmitted packet sequence remains monotonic while trace metadata can cycle independently.
