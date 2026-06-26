# Run 019 — Policy-Controlled Synthetic Trace Replay

## Purpose

Run 019 is the first v0.5 policy-controlled synthetic trace replay.

The goal is to preserve the working compiled-in trace replay workflow from v0.4 while adding a small, reversible policy layer to the synthetic belief-demand trace generator.

The experiment asks whether two LoRa transmitters with similar physical delivery counts can carry substantially different delivered usefulness when their metadata traces are generated from different reporting policies over the same synthetic demand substrate.

## Repository state

Branch:

```text
exp019-policy-controlled-traces
```

Relevant commits:

```text
77fe717 Add Run 019 policy-controlled synthetic traces
829c861 Prepare Run 019 policy trace firmware replay
```

Run ID:

```text
R19
```

## Trace design

Run 019 uses one shared synthetic belief-demand substrate with 320 base rows.

The phase schedule is:

| Base row range | Usefulness |
| -------------: | ---------: |
|           0–49 |       0.20 |
|          50–99 |       0.85 |
|        100–149 |       0.30 |
|        150–199 |       0.90 |
|        200–249 |       0.20 |
|        250–299 |       0.20 |
|        300–319 |       0.85 |

Two policy-conditioned traces are generated from this shared substrate:

| Transmitter | Node | Policy                                 | Policy code | Trace rows | Generated total usefulness | Generated mean usefulness |
| ----------- | ---- | -------------------------------------- | ----------: | ---------: | -------------------------: | ------------------------: |
| TXA         | N01  | fixed_all                              |           F |        320 |                     149.50 |                     0.467 |
| TXB         | N16  | usefulness_threshold, threshold = 0.50 |           U |        120 |                     104.50 |                     0.871 |

The generated trace CSVs use the existing compiled-header input schema:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

The trace headers were generated with:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run019_txa_fixed_all.csv \
  --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h

python scripts/make_trace_headers.py \
  --infile traces/run019_txb_usefulness_threshold.csv \
  --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h
```

Header row counts:

```text
TX-A TRACE_ROW_COUNT = 320
TX-B TRACE_ROW_COUNT = 120
```

## Physical setup

Hardware:

```text
RX:   LilyGO LoRa32 T3 V1.6.1
TX-A: LilyGO LoRa32 T3 V1.6.1
TX-B: LilyGO LoRa32 T3 V1.6.1
```

Radio mode:

```text
Point-to-point LoRa at 915 MHz, not LoRaWAN.
```

Firmware:

```text
RX unchanged from prior runs.
TX-A RUN_ID = R19.
TX-B RUN_ID = R19.
TX-B retains the 500 ms startup offset.
```

## Parser command

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_019_policy_controlled.csv \
  --out logs/parsed_run_019_policy_controlled.csv \
  --seq-window 50
```

## Receiver summary

```text
Valid packets:      979
Malformed packets:  3
```

Packets by transmitter and node:

| TX  | Node | Valid packets |
| --- | ---- | ------------: |
| TXA | N01  |           490 |
| TXB | N16  |           489 |

Observed sequence gaps:

| TX  | Node | Missing count | Missing sequence values |
| --- | ---- | ------------: | ----------------------- |
| TXA | N01  |             1 | [209]                   |
| TXB | N16  |             1 | [186]                   |

Radio metadata:

| Node | Mean RSSI | Min RSSI | Max RSSI | Mean SNR | Min SNR | Max SNR |
| ---- | --------: | -------: | -------: | -------: | ------: | ------: |
| N01  |    -46.56 |    -55.0 |    -42.0 |    10.17 |     9.0 |   13.00 |
| N16  |    -51.76 |    -58.0 |    -48.0 |     9.90 |     9.0 |   10.75 |

Usefulness by node:

| Node | Packets | Total usefulness | Mean usefulness | Total priority | Mean priority |
| ---- | ------: | ---------------: | --------------: | -------------: | ------------: |
| N01  |     490 |            235.7 |           0.481 |         246.65 |         0.503 |
| N16  |     489 |            425.6 |           0.870 |         440.10 |         0.900 |

Approximate receiver inter-arrival time:

| Node | Mean seconds | Min seconds | Max seconds |
| ---- | -----------: | ----------: | ----------: |
| N01  |        1.002 |       0.999 |         2.0 |
| N16  |        1.002 |       0.999 |         2.0 |

## Windowed usefulness recovery

The 50-sequence-window summary recovered the intended usefulness structure.

For TXA/N01, the fixed-all trace includes both low- and high-usefulness phases:

| Sequence window | Packets | Missing count | Total usefulness | Mean usefulness |
| --------------: | ------: | ------------: | ---------------: | --------------: |
|            0–49 |      50 |             0 |             10.0 |           0.200 |
|           50–99 |      50 |             0 |             42.5 |           0.850 |
|         100–149 |      50 |             0 |             15.0 |           0.300 |
|         150–199 |      50 |             0 |             45.0 |           0.900 |
|         200–249 |      49 |             1 |              9.8 |           0.200 |
|         250–299 |      50 |             0 |             10.0 |           0.200 |
|         300–349 |      50 |             0 |             23.0 |           0.460 |
|         350–399 |      50 |             0 |             29.5 |           0.590 |
|         400–449 |      50 |             0 |             26.0 |           0.520 |
|         450–490 |      41 |             0 |             24.9 |           0.607 |

For TXB/N16, the usefulness-threshold trace concentrates reported metadata in high-usefulness phases:

| Sequence window | Packets | Missing count | Total usefulness | Mean usefulness |
| --------------: | ------: | ------------: | ---------------: | --------------: |
|            0–49 |      50 |             0 |             42.5 |           0.850 |
|           50–99 |      50 |             0 |             45.0 |           0.900 |
|         100–149 |      50 |             0 |             42.5 |           0.850 |
|         150–199 |      49 |             1 |             43.1 |           0.880 |
|         200–249 |      50 |             0 |             43.5 |           0.870 |
|         250–299 |      50 |             0 |             43.0 |           0.860 |
|         300–349 |      50 |             0 |             44.5 |           0.890 |
|         350–399 |      50 |             0 |             42.5 |           0.850 |
|         400–449 |      50 |             0 |             44.5 |           0.890 |
|         450–489 |      40 |             0 |             34.5 |           0.862 |

## Interpretation

Run 019 confirms that the repository can generate policy-conditioned synthetic traces from a shared belief-demand substrate and replay them through the existing compiled-in LoRa metadata workflow.

The key result is that the two streams had nearly identical received packet counts but substantially different delivered usefulness:

```text
TXA/N01 fixed_all:            490 packets, total usefulness 235.7, mean usefulness 0.481
TXB/N16 usefulness_threshold: 489 packets, total usefulness 425.6, mean usefulness 0.870
```

This supports the project claim that information delivery is not equivalent to information usefulness. In this run, similar physical delivery counts carried different accumulated usefulness because the transmitted metadata streams were generated by different reporting policies.

Run 019 therefore strengthens the bridge from generator-driven metadata replay to belief-maintenance-aware reporting experiments.

## Important cautions

Run 019 should not be interpreted as an airtime-saving experiment. The firmware still transmits once per second. The v0.5 policy layer controls trace content and usefulness metadata, not physical transmission timing.

Observed sequence gaps should not be interpreted directly as collisions. They mean that a packet was not received or not logged within the observed sequence range. Possible causes include LoRa loss, overlap, receiver timing, power or USB behavior, or logger-side effects.

The `recv_ms` and `tx_ms` clocks are not synchronized across boards, so `recv_ms - tx_ms` should not be interpreted as true latency. Receiver inter-arrival time and observed sequence gaps are meaningful.

TX-B used a 120-row usefulness-threshold trace but produced 489 received packets because the firmware emits monotonic packet sequence numbers while cycling internally through the compiled-in trace rows.

## v0.5 status

Run 019 provides the first successful policy-controlled synthetic trace replay.

It is a bridge from v0.4 generator-driven traces toward later constrained-airtime experiments:

```text
v0.5: policy-controlled synthetic trace content
v0.6: AWSRT-inspired trace adapter/export
v0.7: physical replay of AWSRT-like or AWSRT-derived demand traces
```
