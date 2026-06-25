# LoRa POC Runs 016–017: Monotonic Trace Replay and Transmitter Startup Offset

## Purpose

Runs 016 and 017 extend the Run 015 trace-driven metadata replay experiment.

Run 015 established that packet metadata can be generated on the laptop, converted into compiled-in firmware headers, and replayed by the LoRa transmitters while preserving the existing receiver and parser workflow. However, Run 015 used trace-row sequence numbers directly as transmitted packet sequence numbers. Because the trace replay cycled after 250 rows, transmitted sequence numbers wrapped from 249 back to 0 when the run exceeded one trace cycle.

Runs 016 and 017 address that limitation.

Run 016 changes the transmitter firmware so that the transmitted packet sequence number is monotonic, while the trace metadata continues to cycle internally.

Run 017 then adds a small transmitter startup offset to TX-B after observing that simultaneous board startup often caused only one stream, usually TX-A, to be received consistently. The offset is a practical bench-test scheduling intervention, not a collision-specific protocol.

## Branch and Relevant Commits

Branch:

`exp015-trace-driven-metadata`

Relevant commits:

* `2f439eb Add Run 015 trace-driven metadata replay`
* `8ca3594 Document Run 015 trace-driven metadata results`
* `bc7d0b3 Use monotonic packet sequence for trace replay`

Run 017 also uses a later firmware change that sets the run ID to `R17` and adds a TX-B startup offset.

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

## Trace Replay Design

The trace files remain the same as Run 015:

* `traces/run_015_txa_trace.csv`
* `traces/run_015_txb_trace.csv`

Each trace has 250 metadata rows plus a header row.

Trace fields:

`seq,region,event,priority,usefulness,stale_after,policy`

The generated firmware headers remain:

* `firmware/first_radio_link_TX-A/trace_data_TXA.h`
* `firmware/first_radio_link_TX_B/trace_data_TXB.h`

The transmitter sketches replay trace metadata using:

`TRACE_ROWS[trace_index % TRACE_ROW_COUNT]`

The important refinement for Run 016 and later is that the transmitted packet `seq` no longer comes from `row.seq`. Instead, the firmware uses a separate monotonic counter:

`packet_seq`

This separates two concepts:

| Concept       | Meaning                                                |
| ------------- | ------------------------------------------------------ |
| `packet_seq`  | Monotonic transmitted packet sequence number           |
| `trace_index` | Local replay index used to choose a trace metadata row |
| `row.seq`     | Trace-row sequence field from the generated trace file |

This avoids the Run 015 ambiguity where sequence-window summaries aggregated repeated trace cycles under the same sequence numbers.

## Packet Schema

The transmitted packet schema remains:

`run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy`

The receiver appends:

`rssi,snr`

The resulting receiver row schema remains:

`RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr`

Timing caution:

`recv_ms` and `tx_ms` are not synchronized across boards. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency. Receiver inter-arrival time and observed sequence gaps remain meaningful.

## Run 016 Configuration

Run 016 tests monotonic packet sequence numbers under trace replay.

Logger output:

`logs/rx_run_016_trace_driven_monotonic_1000ms.csv`

Parsed output:

`logs/parsed_run_016_trace_driven_monotonic_1000ms.csv`

Reject output:

`logs/parsed_run_016_trace_driven_monotonic_1000ms_rejects.csv`

Parser command:

`python scripts/parse_receiver_log.py --infile logs/rx_run_016_trace_driven_monotonic_1000ms.csv --out logs/parsed_run_016_trace_driven_monotonic_1000ms.csv --seq-window 50`

Run 016 used:

* TX-A/N01: trace-driven low-value baseline
* TX-B/N16: trace-driven demand-like phase pattern
* 1000 ms transmit interval
* monotonic packet sequence numbers
* no intentional TX-B startup offset

## Run 016 Parser Summary

Valid packets:

`626`

Malformed packets:

`0`

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     316 |
| N16  |     310 |

Packets by transmitter and node:

| TX ID | Node | Packets |
| ----- | ---- | ------: |
| TXA   | N01  |     316 |
| TXB   | N16  |     310 |

Sequence range by node:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       3 |     320 |   316 |
| N16  |       0 |     311 |   310 |

Observed sequence gaps:

| Stream  | Observed gaps             |
| ------- | ------------------------- |
| TXA/N01 | 2 observed gaps: 151, 269 |
| TXB/N16 | 2 observed gaps: 78, 290  |

The TX-A minimum sequence of 3 indicates that receiver logging began after TX-A had already transmitted packets 0–2. This is not a failure.

Observed sequence gaps mean that packets were not received or not logged within the observed sequence range. They should not be treated as direct evidence of collision.

## Run 016 Usefulness Summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     316 |            88.48 |           0.280 |          79.00 |         0.250 |
| N16  |     310 |           141.65 |           0.457 |         141.65 |         0.457 |

Run 016 preserved the delivery-versus-usefulness separation:

TX-A/N01 and TX-B/N16 had broadly similar packet counts, but TX-B/N16 delivered substantially more total usefulness because its trace contained high-demand phases.

## Run 016 Sequence-Window Usefulness

Usefulness by node and sequence window, using `--seq-window 50`:

| TX ID | Node | Seq window | Packets | Missing count | Total usefulness | Mean usefulness |
| ----- | ---- | ---------: | ------: | ------------: | ---------------: | --------------: |
| TXA   | N01  |       0–49 |      47 |             0 |            13.16 |            0.28 |
| TXA   | N01  |      50–99 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    100–149 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    150–199 |      49 |             1 |            13.72 |            0.28 |
| TXA   | N01  |    200–249 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    250–299 |      49 |             1 |            13.72 |            0.28 |
| TXA   | N01  |    300–349 |      21 |             0 |             5.88 |            0.28 |
| TXB   | N16  |       0–49 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |      50–99 |      49 |             1 |            41.65 |            0.85 |
| TXB   | N16  |    100–149 |      50 |             0 |            15.00 |            0.30 |
| TXB   | N16  |    150–199 |      50 |             0 |            45.00 |            0.90 |
| TXB   | N16  |    200–249 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |    250–299 |      49 |             1 |             9.80 |            0.20 |
| TXB   | N16  |    300–349 |      12 |             0 |            10.20 |            0.85 |

Run 016 confirms that the trace metadata continues to cycle while the transmitted sequence number remains monotonic.

For TX-B/N16, the expected usefulness phases remain recoverable:

| Sequence window | Observed mean usefulness |
| --------------: | -----------------------: |
|            0–49 |                     0.20 |
|           50–99 |                     0.85 |
|         100–149 |                     0.30 |
|         150–199 |                     0.90 |
|         200–249 |                     0.20 |
|         250–299 |                     0.20 |
|         300–311 |                     0.85 |

## Run 016 Interpretation

Run 016 fixes the main Run 015 sequence-wraparound caveat.

The transmitted packet sequence is now monotonic, while trace metadata can still cycle internally. This allows observed sequence gaps and sequence-window summaries to be interpreted more cleanly.

Run 016 still had light observed sequence gaps:

* TXA/N01: 151, 269
* TXB/N16: 78, 290

These gaps are not direct evidence of collision. They indicate non-received or non-logged packets within the observed sequence range.

## Motivation for Run 017

During bench testing, simultaneous board startup showed a practical issue: when both transmitters were powered at the same time, often only one stream was received consistently, usually TX-A. When TX-B startup was manually staggered, both streams were received.

Run 017 tests a simple firmware-level version of that manual staggering by adding a TX-B startup offset.

The purpose is not to prove that the earlier problem was collision. The purpose is to test whether a simple transmitter startup offset improves simultaneous-start behavior in this bench setup.

## Run 017 Firmware Change

Run 017 changes the run ID to:

`R17`

TX-B adds:

`STARTUP_OFFSET_MS = 500`

After LoRa initialization, TX-B waits an additional 500 ms before beginning its transmit loop.

Conceptually:

| Transmitter | Startup behavior                                                       |
| ----------- | ---------------------------------------------------------------------- |
| TX-A        | Starts normal 1000 ms transmit rhythm                                  |
| TX-B        | Waits an additional 500 ms, then starts normal 1000 ms transmit rhythm |

This keeps both transmitters at the same 1000 ms period but offsets their transmissions by approximately half a period.

## Run 017 Configuration

Run 017 tests trace-driven monotonic replay with a TX-B startup offset.

Logger output:

`logs/rx_run_017_trace_driven_offset_1000ms.csv`

Parsed output:

`logs/parsed_run_017_trace_driven_offset_1000ms.csv`

Reject output:

`logs/parsed_run_017_trace_driven_offset_1000ms_rejects.csv`

Parser command:

`python scripts/parse_receiver_log.py --infile logs/rx_run_017_trace_driven_offset_1000ms.csv --out logs/parsed_run_017_trace_driven_offset_1000ms.csv --seq-window 50`

Run 017 used:

* TX-A/N01: trace-driven low-value baseline
* TX-B/N16: trace-driven demand-like phase pattern
* 1000 ms transmit interval
* monotonic packet sequence numbers
* 500 ms TX-B startup offset

## Run 017 Parser Summary

Valid packets:

`631`

Malformed packets:

`0`

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     316 |
| N16  |     315 |

Packets by transmitter and node:

| TX ID | Node | Packets |
| ----- | ---- | ------: |
| TXA   | N01  |     316 |
| TXB   | N16  |     315 |

Sequence range by node:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     315 |   316 |
| N16  |       0 |     314 |   315 |

Observed sequence gaps:

| Stream  | Observed gaps |
| ------- | ------------- |
| TXA/N01 | none          |
| TXB/N16 | none          |

Run 017 produced clean monotonic sequence ranges with no observed sequence gaps for either transmitter stream.

## Run 017 Radio Metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -46.08 |    -53.0 |    -42.0 |     9.69 |     9.0 |   10.50 |
| N16  |    -52.93 |    -61.0 |    -50.0 |     9.87 |     9.0 |   12.75 |

Approximate receiver inter-arrival time by node, seconds:

| Node | Mean |   Min |   Max |
| ---- | ---: | ----: | ----: |
| N01  |  1.0 | 0.999 | 1.005 |
| N16  |  1.0 | 0.999 | 1.005 |

The inter-arrival timing is consistent with stable 1000 ms periodic reporting from both streams.

## Run 017 Usefulness Summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     316 |            88.48 |           0.280 |          79.00 |         0.250 |
| N16  |     315 |           145.25 |           0.461 |         145.25 |         0.461 |

Run 017 again preserves the delivery-versus-usefulness separation:

TX-A/N01 and TX-B/N16 had nearly identical packet counts, but TX-B/N16 delivered substantially more total usefulness because its trace contained high-demand phases.

## Run 017 Sequence-Window Usefulness

Usefulness by node and sequence window, using `--seq-window 50`:

| TX ID | Node | Seq window | Packets | Missing count | Total usefulness | Mean usefulness |
| ----- | ---- | ---------: | ------: | ------------: | ---------------: | --------------: |
| TXA   | N01  |       0–49 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |      50–99 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    100–149 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    150–199 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    200–249 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    250–299 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    300–349 |      16 |             0 |             4.48 |            0.28 |
| TXB   | N16  |       0–49 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |      50–99 |      50 |             0 |            42.50 |            0.85 |
| TXB   | N16  |    100–149 |      50 |             0 |            15.00 |            0.30 |
| TXB   | N16  |    150–199 |      50 |             0 |            45.00 |            0.90 |
| TXB   | N16  |    200–249 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |    250–299 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |    300–349 |      15 |             0 |            12.75 |            0.85 |

Run 017 recovers the TX-B trace usefulness pattern cleanly:

| Sequence window | Observed mean usefulness |
| --------------: | -----------------------: |
|            0–49 |                     0.20 |
|           50–99 |                     0.85 |
|         100–149 |                     0.30 |
|         150–199 |                     0.90 |
|         200–249 |                     0.20 |
|         250–299 |                     0.20 |
|         300–314 |                     0.85 |

The 250–299 and 300–314 windows show the trace cycling internally while packet sequence remains monotonic.

## Run 016 versus Run 017

| Property                 |   Run 016 |   Run 017 |
| ------------------------ | --------: | --------: |
| Valid packets            |       626 |       631 |
| Malformed packets        |         0 |         0 |
| TXA/N01 packets          |       316 |       316 |
| TXB/N16 packets          |       310 |       315 |
| TXA/N01 observed gaps    |         2 |         0 |
| TXB/N16 observed gaps    |         2 |         0 |
| TXB startup offset       |      none |    500 ms |
| Packet sequence behavior | monotonic | monotonic |
| Trace metadata behavior  |    cyclic |    cyclic |

Run 017 is the cleaner of the two runs. It preserves the monotonic packet-sequence improvement from Run 016 and removes observed sequence gaps in this bench run by adding a 500 ms TX-B startup offset.

## Interpretation

Runs 016 and 017 together establish a cleaner v0.3 trace-replay workflow.

Run 016 demonstrates that trace-driven metadata replay can use monotonic transmitted packet sequence numbers while still cycling through finite trace metadata.

Run 017 demonstrates that a simple TX-B startup offset can make simultaneous board startup practical in this bench setup. With the offset, both streams were received with no observed sequence gaps in this run.

The careful interpretation is:

Run 017 supports the practical conclusion that synchronized periodic transmissions were problematic in this bench setup and that a small startup offset improved observed delivery. This should not be stated as direct proof of packet collision. The observed gaps and improvements could involve LoRa packet overlap, receiver timing, board startup timing, USB/power behavior, logger timing, or other bench-test effects.

## Scientific Takeaway

The main scientific result remains aligned with the broader project claim:

Information delivery is not the same as information usefulness.

In Run 017, TX-A/N01 and TX-B/N16 had almost identical delivery counts:

* TXA/N01: 316 packets
* TXB/N16: 315 packets

But their delivered usefulness differed substantially:

* TXA/N01: total usefulness 88.48
* TXB/N16: total usefulness 145.25

The receiver/parser also recovered the temporal usefulness phases in the TX-B trace. This shows that the physical LoRa testbed can preserve and expose usefulness structure embedded in synthetic packet metadata, even though the two streams have similar packet delivery counts.

## Conclusion

Run 016 fixed the Run 015 sequence-wraparound ambiguity by separating monotonic packet sequence from cyclic trace metadata replay.

Run 017 added a 500 ms TX-B startup offset and produced the cleanest trace-driven run so far:

* no malformed packets;
* no observed sequence gaps;
* nearly equal packet counts for TX-A and TX-B;
* clear delivered-usefulness separation;
* clean recovery of TX-B temporal usefulness phases.

Run 017 is the preferred v0.3 result to emphasize when describing trace-driven metadata replay under constrained LoRa airtime.

## Recommended Next Step

The next step is to commit the Run 016 and Run 017 logs, documentation, and Run 017 firmware changes.

After that, the branch can be merged back to `main` as the v0.3 trace-driven metadata checkpoint.

A future v0.4 step can replace hand-authored trace CSVs with a generic synthetic belief-demand trace generator, while keeping the same replay and parser workflow.
