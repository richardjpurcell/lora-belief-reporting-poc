# Run 024 Skipped-Slot Physical Replay

## Purpose

Run 024 is the first physical skipped-slot replay.

Previous runs replayed selected metadata traces while the firmware continued to transmit once per second. In contrast, Run 024 uses a full SEND/SKIP schedule in firmware. The transmitter advances one schedule slot at a time. `SEND` rows produce LoRa packets, while `SKIP` rows remain silent.

This is the first run in the repository where reporting decisions change physical transmission behavior.

## Branch

```text
exp025-v10-skipped-slot-firmware-design
```

## Run ID

```text
R24
```

## Hardware

The run used the existing three-board setup:

* one LilyGO LoRa32 T3 V1.6.1 board as receiver;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-A;
* one LilyGO LoRa32 T3 V1.6.1 board as TX-B.

The setup used point-to-point LoRa at 915 MHz, not LoRaWAN.

## Firmware Behavior

The transmitter firmware now uses schedule headers rather than compact SEND-only trace headers.

The schedule row structure includes both metadata and a `send` decision:

```cpp
struct ScheduleRow {
  uint16_t demand_index;
  char region;
  uint8_t event;
  float priority;
  float usefulness;
  uint16_t stale_after;
  char policy;
  uint8_t send;
};
```

For each one-second slot:

```text
send == 1  -> transmit one LoRa packet
send == 0  -> remain silent
```

The schedule index advances on both SEND and SKIP rows. The transmitted packet sequence number advances only when a packet is sent.

## Schedule Inputs

Run 024 used the v0.8 reporting schedules:

```text
traces/run022_reporting_txa_fixed_all_schedule.csv
traces/run022_reporting_txb_usefulness_threshold_schedule.csv
```

The generated firmware schedule headers were:

```text
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

Schedule counts:

```text
TX-A: 16 schedule rows, 16 SEND, 0 SKIP
TX-B: 16 schedule rows, 8 SEND, 8 SKIP
```

Therefore, over the same number of schedule slots, TX-B is expected to attempt approximately half as many transmissions as TX-A.

## Logging and Parsing

Receiver log:

```text
logs/rx_run_024_skipped_slot_replay.csv
```

Parsed valid-packet output:

```text
logs/parsed_run_024_skipped_slot_replay.csv
```

Parsed malformed-packet output:

```text
logs/parsed_run_024_skipped_slot_replay_rejects.csv
```

Parsing command:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_024_skipped_slot_replay.csv \
  --out logs/parsed_run_024_skipped_slot_replay.csv \
  --seq-window 50
```

## Receiver Summary

Run 024 produced:

```text
Valid packets:      537
Malformed packets:  1
```

Packets by transmitter and node:

```text
TXA/N01: 361 packets
TXB/N16: 176 packets
```

This is consistent with the expected skipped-slot behavior: TX-B transmitted approximately half as often as TX-A because its schedule contains 8 SEND rows and 8 SKIP rows.

Sequence ranges:

```text
N01: min 0, max 363, count 361
N16: min 0, max 181, count 176
```

Observed sequence gaps:

```text
TXA/N01: missing 3 -> [22, 183, 221]
TXB/N16: missing 6 -> [53, 62, 66, 83, 104, 155]
```

These are observed sequence gaps only. They should not be interpreted as confirmed collisions. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB behavior, and logger-side effects.

## Malformed Packet

One malformed/deformed packet appeared mid-run and was written to the rejects file.

This malformed row should not be interpreted as a valid TX-A or TX-B packet. It should also not be treated as proof of a collision. It is recorded as a malformed packet and excluded from the valid-packet analysis.

## Radio Metadata

Radio metadata by node:

```text
N01 mean RSSI: -37.66
N01 RSSI range: -42.0 to -35.0
N01 mean SNR: 9.42
N01 SNR range: 4.75 to 10.50

N16 mean RSSI: -47.44
N16 RSSI range: -49.0 to -44.0
N16 mean SNR: 9.76
N16 SNR range: 8.75 to 12.25
```

## Usefulness Summary

Usefulness by node:

```text
N01 packets: 361
N01 total usefulness: 194.97
N01 mean usefulness: 0.540
N01 total priority: 196.19
N01 mean priority: 0.543

N16 packets: 176
N16 total usefulness: 138.28
N16 mean usefulness: 0.786
N16 total priority: 140.33
N16 mean priority: 0.797
```

TXB/N16 delivered fewer packets, as expected under scheduled skipping, but those received packets had substantially higher mean usefulness.

The mean-usefulness difference was:

```text
0.786 - 0.540 = 0.246
```

Relative to TXA/N01, TXB/N16 had approximately 46% higher mean usefulness per received packet.

## Receiver Inter-Arrival Timing

Approximate receiver inter-arrival time by node:

```text
N01 mean: 1.008 s
N01 min:  0.988 s
N01 max:  2.000 s

N16 mean: 2.069 s
N16 min:  1.988 s
N16 max:  4.000 s
```

This is an important Run 024 result. TX-A continued to appear at approximately one-second intervals, while TX-B appeared at approximately two-second intervals because alternate schedule slots were skipped.

These are receiver-side inter-arrival measurements only. `recv_ms` and `tx_ms` are not synchronized across boards, so `recv_ms - tx_ms` should not be interpreted as true packet latency.

## Interpretation

Run 024 demonstrates the full skipped-slot path:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ Arduino schedule header
→ firmware slot loop
→ SEND transmits
→ SKIP remains silent
→ receiver log
→ parsed delivery-versus-usefulness analysis
```

The main result is that scheduled skipping changed physical transmission behavior:

```text
TXA/N01: 361 received packets, mean inter-arrival 1.008 s
TXB/N16: 176 received packets, mean inter-arrival 2.069 s
```

At the same time, TXB/N16 preserved higher mean delivered usefulness:

```text
TXA/N01 mean usefulness: 0.540
TXB/N16 mean usefulness: 0.786
```

This is the first run that supports a limited airtime-relevant claim: scheduled skipping reduced transmission attempts for the usefulness-threshold stream while preserving higher usefulness per received packet.

## Cautions

Run 024 does not prove collision reduction.

Run 024 does not measure true transmitter-to-receiver latency because board clocks are not synchronized.

Run 024 is point-to-point LoRa, not LoRaWAN.

Observed sequence gaps should not be overclaimed as collisions.

The malformed packet is recorded and excluded from valid-packet analysis.

## Summary

Run 024 is the first true skipped-slot physical replay in the repository.

It demonstrates that a usefulness-threshold schedule can reduce physical transmissions while maintaining higher mean delivered usefulness among received packets.
