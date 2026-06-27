# Run 021 Adapter-Generated Physical Replay

## Purpose

Run 021 is the first physical replay of adapter-generated compact traces.

It follows the v0.6 adapter milestone, which introduced a generic belief-maintenance demand-trace adapter. The goal of Run 021 is to confirm that compact traces produced by the adapter path can be compiled into the existing ESP32/LilyGO LoRa transmitter firmware and replayed over the physical point-to-point LoRa setup.

This is a physical replay experiment, but it is not yet an airtime-saving experiment. The firmware still transmits once per second. The policy layer affects the metadata carried in packets, not the physical transmission schedule.

## Branch

```text
exp022-v07-adapter-physical-replay
```

## Run ID

```text
R21
```

## Hardware

The run used the existing three-board setup:

* one LilyGO LoRa32 T3 V1.6.1 board as receiver;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-A;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-B.

The setup used point-to-point LoRa at 915 MHz, not LoRaWAN.

## Trace Preparation

The Run 021 firmware headers were generated from the v0.6 adapter outputs:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txa_fixed_all.csv \
  --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h

python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txb_usefulness_threshold.csv \
  --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h
```

The generated trace headers had the following properties:

```text
TX-A TRACE_ROW_COUNT = 16
TX-A policy code = F

TX-B TRACE_ROW_COUNT = 8
TX-B policy code = U
```

The transmitter firmware run IDs were updated from `R19` to `R21`.

## Logging and Parsing

Receiver log:

```text
logs/rx_run_021_adapter_generated_replay.csv
```

Parsed valid-packet output:

```text
logs/parsed_run_021_adapter_generated_replay.csv
```

Parsed malformed-packet output:

```text
logs/parsed_run_021_adapter_generated_replay_rejects.csv
```

Parsing command:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_021_adapter_generated_replay.csv \
  --out logs/parsed_run_021_adapter_generated_replay.csv \
  --seq-window 50
```

## Receiver Summary

Run 021 produced:

```text
Valid packets:      731
Malformed packets:  0
```

Packets by transmitter and node:

```text
TXA/N01: 367 packets
TXB/N16: 364 packets
```

Sequence ranges:

```text
N01: min 0, max 367, count 367
N16: min 0, max 366, count 364
```

Observed sequence gaps:

```text
TXA/N01: missing 1 -> [9]
TXB/N16: missing 3 -> [30, 57, 228]
```

These are observed sequence gaps only. They should not be interpreted as confirmed collisions. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB behaviour, and logger-side effects.

## Radio Metadata

Radio metadata by node:

```text
N01 mean RSSI: -52.91
N01 RSSI range: -63.0 to -45.0
N01 mean SNR: 9.68
N01 SNR range: 7.25 to 10.5

N16 mean RSSI: -58.07
N16 RSSI range: -75.0 to -51.0
N16 mean SNR: 9.64
N16 SNR range: 3.25 to 10.5
```

## Usefulness Summary

Usefulness by node:

```text
N01 packets: 367
N01 total usefulness: 198.05
N01 mean usefulness: 0.540
N01 total priority: 199.19
N01 mean priority: 0.543

N16 packets: 364
N16 total usefulness: 285.30
N16 mean usefulness: 0.784
N16 total priority: 289.37
N16 mean priority: 0.795
```

TXB/N16 delivered nearly the same number of packets as TXA/N01, but with substantially higher total and mean usefulness.

The total-usefulness difference was:

```text
285.30 - 198.05 = 87.25
```

The mean-usefulness difference was:

```text
0.784 - 0.540 = 0.244
```

Relative to TXA/N01, TXB/N16 had approximately 45% higher mean usefulness.

## Receiver Inter-Arrival Timing

Approximate receiver inter-arrival time by node:

```text
N01 mean: 1.003 s
N01 min:  0.999 s
N01 max:  2.005 s

N16 mean: 1.008 s
N16 min:  0.999 s
N16 max:  2.000 s
```

These values are receiver-side inter-arrival measurements only.

`recv_ms` and `tx_ms` are not synchronized across boards, so `recv_ms - tx_ms` should not be interpreted as true packet latency.

## Interpretation

Run 021 confirms that the v0.6 adapter path can feed the existing physical LoRa replay workflow.

The demonstrated path is:

```text
generic belief-maintenance demand trace
→ adapter-generated compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

The main result is that the two transmitters delivered nearly identical packet counts while carrying different usefulness profiles:

```text
TXA/N01: 367 packets, mean usefulness 0.540
TXB/N16: 364 packets, mean usefulness 0.784
```

This supports the repository's core proof-of-concept direction: physical packet delivery count and delivered belief-maintenance usefulness can separate.

## Cautions

Run 021 is not an airtime-saving experiment.

The firmware still transmits once per second.

The TX-B stream has higher usefulness because the adapter-generated metadata trace is threshold-selected, not because TX-B transmits less often.

Observed sequence gaps should not be overclaimed as collisions.

Receiver-side inter-arrival times are meaningful, but transmitter-to-receiver latency is not measured because board clocks are not synchronized.

## Summary

Run 021 is the first physical replay of adapter-generated traces.

It extends v0.6 from an adapter-only trace-interface milestone to a physical LoRa replay milestone while preserving the current firmware and receiver-analysis workflow.
