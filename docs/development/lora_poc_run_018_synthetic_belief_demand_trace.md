# LoRa POC Run 018: Synthetic Belief-Demand Trace Generator

## Purpose

Run 018 is the first synthetic belief-demand trace generator experiment in the LoRa belief-reporting proof of concept.

Runs 015–017 established trace-driven metadata replay:

synthetic trace CSV
→ generated firmware header
→ LoRa packet metadata
→ receiver log
→ delivery-versus-usefulness analysis

Run 018 moves the source of the trace from a manually assembled phase table to a reusable Python generator:

`scripts/generate_belief_demand_trace.py`

This is the first v0.4 step toward the longer-term paper direction:

belief-maintenance model / synthetic demand trace
→ packet metadata emitted by LoRa transmitters
→ physical LoRa delivery outcomes
→ delivery-versus-usefulness analysis

The generator is intentionally simple. It does not simulate wildfire, run AWSRT, or implement a full belief-maintenance model. Instead, it creates reproducible packet metadata traces that stand in for changing belief-maintenance demand over time.

## Branch and Commit

Branch:

`exp018-synthetic-belief-demand-traces`

Initial generator commit:

`3d06c36 Add Run 018 synthetic belief-demand trace generator`

Base checkpoint:

`v0.3-trace-driven-metadata`

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
* `scripts/generate_belief_demand_trace.py`

## Generator Design

Run 018 adds:

`scripts/generate_belief_demand_trace.py`

The generator writes trace CSV files with the existing trace schema:

`seq,region,event,priority,usefulness,stale_after,policy`

The generator produces two trace roles:

| Trace | Role                                |
| ----- | ----------------------------------- |
| TX-A  | Low-value baseline                  |
| TX-B  | Synthetic belief-demand phase trace |

TX-A/N01 remains a low-value baseline stream:

| Field       | Value |
| ----------- | ----- |
| region      | A     |
| event       | 0     |
| priority    | 0.25  |
| usefulness  | 0.275 |
| stale_after | 30    |
| policy      | B     |

TX-B/N16 is generated from named synthetic demand phases:

| Phase          | Length | Region | Event | Priority | Usefulness | Policy |
| -------------- | -----: | ------ | ----: | -------: | ---------: | ------ |
| low_background |     50 | B      |     1 |     0.20 |       0.20 | U      |
| high_demand    |     50 | B      |     1 |     0.85 |       0.85 | U      |
| recovering     |     50 | B      |     1 |     0.30 |       0.30 | U      |
| urgent_demand  |     50 | B      |     1 |     0.90 |       0.90 | U      |
| low_background |     50 | B      |     1 |     0.20 |       0.20 | U      |

For Run 018, the generator was run with one cycle, producing 250 trace rows plus a header row for each transmitter.

## Trace and Header Files

Run 018 trace files:

* `traces/run_018_txa_trace.csv`
* `traces/run_018_txb_trace.csv`

The trace files were converted into sketch-local firmware headers:

* `firmware/first_radio_link_TX-A/trace_data_TXA.h`
* `firmware/first_radio_link_TX_B/trace_data_TXB.h`

Header generation used:

`python scripts/make_trace_headers.py --infile traces/run_018_txa_trace.csv --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h`

`python scripts/make_trace_headers.py --infile traces/run_018_txb_trace.csv --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h`

The transmitter sketches replay trace metadata using:

`TRACE_ROWS[trace_index % TRACE_ROW_COUNT]`

The transmitted packet sequence number remains monotonic using:

`packet_seq`

This preserves the v0.3 improvement that separates transmitted packet sequence from cyclic trace replay.

## Packet Schema

The transmitted packet schema remains:

`run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy`

The receiver appends:

`rssi,snr`

The resulting receiver row schema remains:

`RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr`

Timing caution:

`recv_ms` and `tx_ms` are not synchronized across boards. Therefore, `recv_ms - tx_ms` should not be interpreted as true packet latency. Receiver inter-arrival time and observed sequence gaps remain meaningful.

## Run Configuration

Run ID:

`R18`

Transmit interval:

`1000 ms`

TX-B startup offset:

`500 ms`

Transmitters:

| Transmitter | Logical node | Trace role                    |
| ----------- | ------------ | ----------------------------- |
| TX-A        | N01          | Low-value baseline            |
| TX-B        | N16          | Synthetic belief-demand trace |

Logger output:

`logs/rx_run_018_synthetic_belief_demand_1000ms.csv`

Parsed output:

`logs/parsed_run_018_synthetic_belief_demand_1000ms.csv`

Reject output:

`logs/parsed_run_018_synthetic_belief_demand_1000ms_rejects.csv`

Parser command:

`python scripts/parse_receiver_log.py --infile logs/rx_run_018_synthetic_belief_demand_1000ms.csv --out logs/parsed_run_018_synthetic_belief_demand_1000ms.csv --seq-window 50`

## Parser Summary

Valid packets:

`616`

Malformed packets:

`0`

Packets by node:

| Node | Packets |
| ---- | ------: |
| N01  |     306 |
| N16  |     310 |

Packets by transmitter and node:

| TX ID | Node | Packets |
| ----- | ---- | ------: |
| TXA   | N01  |     306 |
| TXB   | N16  |     310 |

Sequence range by node:

| Node | Min seq | Max seq | Count |
| ---- | ------: | ------: | ----: |
| N01  |       0 |     310 |   306 |
| N16  |       0 |     310 |   310 |

Observed sequence gaps:

| Stream  | Observed gaps                            |
| ------- | ---------------------------------------- |
| TXA/N01 | 5 observed gaps: 144, 164, 190, 201, 258 |
| TXB/N16 | 1 observed gap: 69                       |

Observed sequence gaps indicate packets not received or not logged within the observed sequence range. They should not be interpreted as direct evidence of collision.

## Radio Metadata

Radio metadata by node:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -49.77 |    -56.0 |    -46.0 |     9.70 |     9.0 |    10.5 |
| N16  |    -50.36 |    -57.0 |    -47.0 |     9.81 |     9.0 |    10.5 |

Approximate receiver inter-arrival time by node, seconds:

| Node |  Mean |   Min | Max |
| ---- | ----: | ----: | --: |
| N01  | 1.016 | 0.999 | 2.0 |
| N16  | 1.003 | 0.999 | 2.0 |

The maximum inter-arrival time of approximately 2 seconds is consistent with the observed sequence gaps.

## Usefulness Summary

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     306 |            85.68 |           0.280 |           76.5 |         0.250 |
| N16  |     310 |           141.00 |           0.455 |          141.0 |         0.455 |

Run 018 preserves the delivery-versus-usefulness separation:

TX-A/N01 and TX-B/N16 had broadly similar packet counts, but TX-B/N16 delivered substantially more total usefulness because its generated trace contained high-demand phases.

## Sequence-Window Usefulness

Usefulness by node and sequence window, using `--seq-window 50`:

| TX ID | Node | Seq window | Packets | Missing count | Total usefulness | Mean usefulness |
| ----- | ---- | ---------: | ------: | ------------: | ---------------: | --------------: |
| TXA   | N01  |       0–49 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |      50–99 |      50 |             0 |            14.00 |            0.28 |
| TXA   | N01  |    100–149 |      49 |             1 |            13.72 |            0.28 |
| TXA   | N01  |    150–199 |      48 |             2 |            13.44 |            0.28 |
| TXA   | N01  |    200–249 |      49 |             1 |            13.72 |            0.28 |
| TXA   | N01  |    250–299 |      49 |             1 |            13.72 |            0.28 |
| TXA   | N01  |    300–349 |      11 |             0 |             3.08 |            0.28 |
| TXB   | N16  |       0–49 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |      50–99 |      49 |             1 |            41.65 |            0.85 |
| TXB   | N16  |    100–149 |      50 |             0 |            15.00 |            0.30 |
| TXB   | N16  |    150–199 |      50 |             0 |            45.00 |            0.90 |
| TXB   | N16  |    200–249 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |    250–299 |      50 |             0 |            10.00 |            0.20 |
| TXB   | N16  |    300–349 |      11 |             0 |             9.35 |            0.85 |

TX-B/N16 recovered the generator-defined usefulness phases:

| Sequence window | Expected phase | Observed mean usefulness |
| --------------: | -------------- | -----------------------: |
|            0–49 | low_background |                     0.20 |
|           50–99 | high_demand    |                     0.85 |
|         100–149 | recovering     |                     0.30 |
|         150–199 | urgent_demand  |                     0.90 |
|         200–249 | low_background |                     0.20 |
|         250–299 | low_background |                     0.20 |
|         300–310 | high_demand    |                     0.85 |

The final two windows show that trace metadata continues to cycle internally while the transmitted packet sequence remains monotonic.

## Interpretation

Run 018 is successful as the first generator-driven trace replay experiment.

It confirms that:

1. A reusable Python script can generate synthetic belief-demand traces.
2. Generated traces can be converted into firmware headers.
3. The transmitter firmware can replay those generated traces without changing the packet schema.
4. The receiver and parser workflow continues to work unchanged.
5. The physical LoRa testbed preserves enough metadata structure to recover usefulness phases from received packets.
6. Similar packet delivery counts can still carry substantially different delivered usefulness.

The main scientific takeaway is:

Information delivery is not the same as information usefulness.

In Run 018, TX-A/N01 and TX-B/N16 had similar delivery counts:

* TXA/N01: 306 packets
* TXB/N16: 310 packets

But TX-B/N16 delivered much more total usefulness:

* TXA/N01: total usefulness 85.68
* TXB/N16: total usefulness 141.00

This supports the broader proof-of-concept claim that physical packet delivery outcomes and usefulness-weighted information outcomes should be analyzed separately.

## Comparison to Run 017

Run 017 remains the cleanest delivery run so far because it had no observed sequence gaps.

Run 018 is less clean as a delivery run because it had light observed gaps:

* TXA/N01: 5 observed gaps
* TXB/N16: 1 observed gap

However, Run 018 is scientifically important because it changes the source of the trace. The packet metadata now comes from a reusable synthetic belief-demand trace generator rather than from a manually assembled trace.

Therefore:

| Run     | Main value                                                           |
| ------- | -------------------------------------------------------------------- |
| Run 017 | Cleanest trace-driven delivery result with no observed sequence gaps |
| Run 018 | First reusable synthetic belief-demand trace generator result        |

Both runs are useful. Run 017 is the cleanest physical replay result. Run 018 is the stronger architectural bridge toward generated belief-demand traces.

## Conclusion

Run 018 establishes the v0.4 synthetic belief-demand trace generator milestone.

The experiment moves the project from trace-driven replay to generator-driven trace replay while preserving the same firmware, receiver, parser, and analysis structure.

This creates a clean path toward future experiments where traces are generated from richer belief-maintenance models, while the LoRa testbed continues to supply real physical delivery outcomes.

## Recommended Next Step

The next step is to commit the Run 018 logs and documentation.

After that, the branch can be merged to `main` and tagged as the v0.4 generator-driven trace checkpoint.

A future v0.5 step can make the generator more explicitly belief-maintenance-aware by adding one or more of the following:

* separate demand, uncertainty, and usefulness fields before projection into packet metadata;
* configurable phase schedules;
* random seeds;
* multiple logical nodes;
* event onset and decay;
* trace manifests recording generator parameters;
* comparison of fixed-interval versus usefulness-aware reporting policies under constrained airtime.
