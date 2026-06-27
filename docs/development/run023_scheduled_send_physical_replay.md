# Run 023 Scheduled-SEND Physical Replay

## Purpose

Run 023 is a physical replay of compact traces produced from the v0.8 reporting-schedule workflow.

The v0.8 reporting schedule distinguishes source demand rows from reporting decisions. Demand rows can be marked `SEND` or `SKIP`, and only `SEND` rows are reduced into compact firmware trace CSVs.

Run 023 tests whether those SEND-only compact traces can be compiled into the existing ESP32/LilyGO transmitter firmware, replayed over the physical point-to-point LoRa setup, logged by the receiver, and parsed by the existing analysis workflow.

This is a physical replay of scheduled-SEND traces. It is not yet a true time-slotted packet-skipping experiment, because the firmware still transmits once per second and does not preserve skipped demand slots as silent intervals.

## Branch

```text
exp024-v09-scheduled-send-physical-replay
```

## Run ID

```text
R23
```

## Hardware

The run used the existing three-board setup:

* one LilyGO LoRa32 T3 V1.6.1 board as receiver;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-A;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-B.

The setup used point-to-point LoRa at 915 MHz, not LoRaWAN.

## Trace Preparation

The Run 023 firmware headers were generated from the v0.8 reporting-schedule compact outputs:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run022_reporting_txa_fixed_all_compact.csv \
  --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h

python scripts/make_trace_headers.py \
  --infile traces/run022_reporting_txb_usefulness_threshold_compact.csv \
  --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h
```

The generated trace headers had the following properties:

```text
TX-A TRACE_ROW_COUNT = 16
TX-A policy code = F

TX-B TRACE_ROW_COUNT = 8
TX-B policy code = U
```

The transmitter firmware run IDs were updated to `R23`.

## Logging and Parsing

Receiver log:

```text
logs/rx_run_023_scheduled_send_replay.csv
```

Parsed valid-packet output:

```text
logs/parsed_run_023_scheduled_send_replay.csv
```

Parsed malformed-packet output:

```text
logs/parsed_run_023_scheduled_send_replay_rejects.csv
```

Parsing command:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_023_scheduled_send_replay.csv \
  --out logs/parsed_run_023_scheduled_send_replay.csv \
  --seq-window 50
```

## Receiver Summary

Run 023 produced:

```text
Valid packets:      735
Malformed packets:  0
```

Packets by transmitter and node:

```text
TXA/N01: 366 packets
TXB/N16: 369 packets
```

Sequence ranges:

```text
N01: min 0, max 370, count 366
N16: min 0, max 369, count 369
```

Observed sequence gaps:

```text
TXA/N01: missing 5 -> [59, 93, 250, 294, 307]
TXB/N16: missing 1 -> [111]
```

These are observed sequence gaps only. They should not be interpreted as confirmed collisions. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB behaviour, and logger-side effects.

## Radio Metadata

Radio metadata by node:

```text
N01 mean RSSI: -36.83
N01 RSSI range: -41.0 to -35.0
N01 mean SNR: 9.62
N01 SNR range: 8.75 to 10.75

N16 mean RSSI: -46.40
N16 RSSI range: -51.0 to -44.0
N16 mean SNR: 9.77
N16 SNR range: 8.75 to 10.75
```

## Usefulness Summary

Usefulness by node:

```text
N01 packets: 366
N01 total usefulness: 197.83
N01 mean usefulness: 0.541
N01 total priority: 199.10
N01 mean priority: 0.544

N16 packets: 369
N16 total usefulness: 289.55
N16 mean usefulness: 0.785
N16 total priority: 293.70
N16 mean priority: 0.796
```

TXB/N16 delivered nearly the same number of packets as TXA/N01, but with substantially higher total and mean usefulness.

The total-usefulness difference was:

```text
289.55 - 197.83 = 91.72
```

The mean-usefulness difference was:

```text
0.785 - 0.541 = 0.244
```

Relative to TXA/N01, TXB/N16 had approximately 45% higher mean usefulness.

## Receiver Inter-Arrival Timing

Approximate receiver inter-arrival time by node:

```text
N01 mean: 1.014 s
N01 min:  0.999 s
N01 max:  2.000 s

N16 mean: 1.003 s
N16 min:  0.999 s
N16 max:  2.000 s
```

These are receiver-side inter-arrival measurements only.

`recv_ms` and `tx_ms` are not synchronized across boards, so `recv_ms - tx_ms` should not be interpreted as true packet latency.

## Interpretation

Run 023 confirms that the v0.8 reporting-schedule workflow can feed the existing physical LoRa replay workflow.

The demonstrated path is:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ SEND-only compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

The main result is that the two transmitters delivered nearly identical packet counts while carrying different usefulness profiles:

```text
TXA/N01: 366 packets, mean usefulness 0.541
TXB/N16: 369 packets, mean usefulness 0.785
```

This supports the repository's core proof-of-concept direction: physical packet delivery count and delivered belief-maintenance usefulness can separate.

## Cautions

Run 023 is not yet a true airtime-saving experiment.

The firmware still transmits once per second.

The TX-B stream has higher usefulness because the compact replay trace contains threshold-selected SEND rows, not because the firmware preserved skipped source-demand slots as silent airtime intervals.

Observed sequence gaps should not be overclaimed as collisions.

Receiver-side inter-arrival times are meaningful, but transmitter-to-receiver latency is not measured because board clocks are not synchronized.

## Summary

Run 023 is the first physical replay of compact traces produced from the v0.8 reporting-schedule workflow.

It extends v0.8 from a design-stage SEND/SKIP schedule artifact to a physical scheduled-SEND replay, while preserving the current firmware timing model.
