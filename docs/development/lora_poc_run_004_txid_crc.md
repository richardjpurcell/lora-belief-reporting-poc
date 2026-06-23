# LoRa POC Run 004: TXID Schema and CRC-Enabled Receiver Log

## Date

2026-06-22

## Purpose

This run tested the revised packet schema with a separate physical transmitter identifier (`tx_id`) and logical sensing node identifier (`node_id`). The goal was to confirm that the receiver logger and parser can handle the upgraded 15-field schema while preserving communication metadata and synthetic usefulness metadata.

## Hardware

- RX: LilyGO LoRa32 T3 V1.6.1, running CRC-enabled receiver firmware
- TX-A: LilyGO LoRa32 T3 V1.6.1, sending logical node `N01` as physical transmitter `TXA`
- TX-B: LilyGO LoRa32 T3 V1.6.1, sending logical node `N16` as physical transmitter `TXB`
- Frequency: 915 MHz
- Antennas attached to all boards
- RX connected to laptop by USB
- TX boards powered separately or by USB

## Software

- Conda environment: `dcoss-lora-poc`
- Logger: `scripts/receiver_logger.py`
- Parser: `scripts/parse_receiver_log.py`
- Parser updated to support the 15-field schema with `tx_id`
- Parser updated to report missing sequence numbers by `tx_id` and `node_id`

## Input and Output Files

- Raw receiver log: `logs/rx_run_004_txid_crc.csv`
- Parsed valid packets: `logs/parsed_run_004_txid_crc.csv`
- Malformed/rejected packets: `logs/parsed_run_004_txid_crc_rejects.csv`

## Packet Format

Run 004 used the revised packet format:

```text
RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr
```

Example valid receiver rows:

```text
RX,1685219,R4,TXB,N16,42,215020,B,1,0.91,0.80,30,U,-49,10.00
RX,1688093,R4,TXA,N01,56,286167,A,1,0.82,0.74,30,U,-54,9.75
```

This schema separates the physical transmitter from the logical sensing node. This will be important when one physical board later replays packets for multiple logical nodes.

## Summary

The parser reported:

```text
Valid packets:      46
Malformed packets:  0
```

Packets by node:

```text
N01    22
N16    24
```

Packets by transmitter and node:

```text
tx_id  node_id
TXA    N01        22
TXB    N16        24
```

Sequence range by node:

```text
         min  max  count
node_id
N01       56   78     22
N16       42   65     24
```

Missing sequences by transmitter and node:

```text
TXA/N01: missing 1 -> [67]
TXB/N16: none
```

Radio metadata by node:

```text
         mean_rssi  min_rssi  max_rssi  mean_snr  min_snr  max_snr
node_id
N01         -55.05     -57.0     -49.0      9.78     9.25    12.00
N16         -50.67     -53.0     -49.0      9.71     9.25    11.25
```

Usefulness by node:

```text
         packets  total_usefulness  mean_usefulness  total_priority  mean_priority
node_id
N01           22             16.28             0.74           18.04           0.82
N16           24             19.20             0.80           21.84           0.91
```

Approximate receiver inter-arrival time by node:

```text
          mean    min     max
node_id
N01      5.325  5.082  10.167
N16      5.083  5.083   5.083
```

## Interpretation

Run 004 confirms that the revised packet schema is working. The receiver log now carries both the physical transmitter ID (`TXA`, `TXB`) and the logical node ID (`N01`, `N16`). The parser correctly reads the 15-field format, produces a clean parsed dataset, and reports zero malformed packets.

The run also demonstrates missing-sequence detection. The `TXA/N01` stream is missing sequence `67` within the observed range, while `TXB/N16` has no missing sequences. This should be interpreted cautiously: the missing sequence indicates that the packet was not received or not logged within the observed sequence range, but it does not by itself prove collision or a specific LoRa-layer failure mechanism.

The usefulness totals differ because the two streams have different static synthetic usefulness metadata. This is not yet a real policy comparison, but it confirms that delivery-side metrics and usefulness-side metadata can be reported together.

## Known Limitations

- The run does not yet implement a scheduled packet trace.
- The two transmitters were already running, so sequences did not begin at zero.
- `recv_ms` and `tx_ms` are not synchronized across boards, so their difference should not be interpreted as true latency.
- Usefulness and priority values are still static firmware payload values rather than trace-generated values.
- The single missing TXA sequence is useful as a delivery-side signal, but should not be overinterpreted as a collision result.

## Next Steps

1. Preserve Run 004 as the current clean schema baseline.
2. Begin Run 005 as the first miniature delivery-versus-usefulness demonstration.
3. For Run 005, keep the same delivery opportunity but assign different synthetic policy metadata:
   - `TXA/N01`: lower-value/random baseline stream, e.g., priority `0.30`, usefulness `0.25`, policy `R`
   - `TXB/N16`: higher-value/prioritized stream, e.g., priority `0.90`, usefulness `0.80`, policy `U`
4. Compare packet counts, missing sequences, and delivered usefulness across the two streams.
5. Later, replace static firmware payloads with scheduled packets generated from a CSV trace.

## Status

Milestone complete: CRC-enabled two-transmitter LoRa logging works with the revised `tx_id` packet schema, zero malformed rows, and missing-sequence reporting.
