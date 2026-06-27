# v1.0 Skipped-Slot Firmware Design

## Purpose

The v1.0 milestone introduces the design for true skipped-slot firmware replay.

Previous milestones established a staged path from generic belief-maintenance demand traces to physical LoRa replay:

```text
generic belief-maintenance demand trace
→ adapter
→ SEND/SKIP reporting schedule
→ SEND-only compact firmware trace
→ physical LoRa replay
→ parsed delivery-versus-usefulness analysis
```

However, v0.9 still used the existing once-per-second transmitter firmware. The compact replay trace contained only `SEND` rows, so the firmware transmitted once per second and cycled through selected metadata rows. This was a physical replay of scheduled-SEND compact traces, but it was not yet true packet skipping.

The v1.0 goal is to preserve skipped demand slots as silent intervals in firmware.

## Key Difference from v0.9

In v0.9, skipped rows were removed before firmware replay:

```text
SEND/SKIP schedule
→ SEND-only compact trace
→ transmit every second
```

In v1.0, skipped rows should remain in the firmware schedule:

```text
SEND/SKIP schedule
→ full schedule header
→ advance one slot at a time
→ SEND transmits
→ SKIP remains silent
```

This distinction matters because airtime reduction requires changing physical transmission behavior, not only changing metadata content.

## Slot Semantics

Each schedule row represents one reporting opportunity or demand slot.

The firmware should advance through schedule rows at a fixed slot interval, initially one second per slot.

For each slot:

```text
decision == SEND  → transmit one LoRa packet
decision == SKIP  → transmit nothing and wait until the next slot
```

The transmitter should still advance its schedule index on both `SEND` and `SKIP`.

This preserves the original demand timeline.

## Proposed Firmware Schedule Header Schema

The current compact trace header uses:

```cpp
struct TraceRow {
  uint16_t seq;
  char region;
  uint8_t event;
  float priority;
  float usefulness;
  uint16_t stale_after;
  char policy;
};
```

For skipped-slot replay, the firmware needs an explicit decision field.

Proposed schedule-row structure:

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

Where:

```text
send = 1  → SEND
send = 0  → SKIP
```

The firmware packet sequence number should remain a transmitted-packet sequence number, not a demand-slot index.

That means:

```text
slot index advances every schedule row
packet seq increments only when a packet is transmitted
```

This preserves two different counters:

```text
demand_index / slot index = source-side reporting opportunity
seq = transmitted packet sequence
```

## Packet Schema

The existing transmitted receiver-row packet schema should remain unchanged:

```text
RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr
```

Skipped slots are not transmitted, so they do not appear as receiver rows.

The skipped-slot schedule and manifest are therefore required to interpret how many reporting opportunities were skipped.

## Firmware Behavior

The transmitter loop should be conceptually:

```cpp
const ScheduleRow& row = SCHEDULE_ROWS[schedule_index];

if (row.send) {
  transmit packet using row metadata;
  packet_seq++;
} else {
  // silent slot: no LoRa packet
}

schedule_index = (schedule_index + 1) % SCHEDULE_ROW_COUNT;
wait until next slot;
```

Important:

* `schedule_index` advances on both `SEND` and `SKIP`.
* `packet_seq` advances only on `SEND`.
* `tx_ms` should record the local transmitter time for transmitted packets only.
* skipped slots should not create placeholder receiver rows.

## Expected Physical Consequence

If TX-A uses `fixed_all` and TX-B uses `usefulness_threshold`, then:

```text
TX-A schedule: 16 SEND, 0 SKIP
TX-B schedule: 8 SEND, 8 SKIP
```

With one-second slots, TX-B should attempt approximately half as many transmissions as TX-A over the same schedule duration.

This is the first milestone where airtime-saving behavior can be physically tested.

## Analysis Implications

For skipped-slot runs, receiver packet counts should be interpreted together with schedule counts.

Useful quantities include:

```text
demand rows
scheduled SEND rows
scheduled SKIP rows
send fraction
received valid packets
malformed packets
observed sequence gaps among transmitted packet sequence numbers
total delivered usefulness
mean delivered usefulness per received packet
delivered usefulness per scheduled demand row
delivered usefulness per scheduled SEND row
```

The parser currently sees only received packets. Therefore, schedule-aware analysis may need a later script that combines:

```text
reporting schedule manifest
parsed receiver rows
```

## Airtime Claims

A skipped-slot physical run may support limited airtime-reduction claims if:

1. TX-B is scheduled to send fewer packets than TX-A.
2. Firmware actually remains silent on `SKIP` rows.
3. Receiver packet counts are consistent with fewer TX-B transmissions.
4. The run documentation reports schedule counts and received packet counts together.

Even then, the wording should remain careful:

```text
The run demonstrates reduced transmission attempts under scheduled skipping.
```

Avoid overclaiming:

```text
The run proves collision reduction.
The run measures true latency.
The run optimizes LoRaWAN airtime.
```

The setup remains point-to-point LoRa, not LoRaWAN.

## Non-Goals

v1.0 does not require SD-card replay.

v1.0 does not require AWSRT integration.

v1.0 does not require changing the receiver packet schema.

v1.0 does not prove collision reduction.

v1.0 does not measure transmitter-to-receiver latency, because clocks are not synchronized.

## Proposed Files

The first implementation should add a schedule-header generator, for example:

```text
scripts/make_schedule_headers.py
```

This script should convert full reporting schedule CSVs into firmware schedule headers containing both `SEND` and `SKIP` rows.

Future generated headers might be:

```text
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

The firmware can then be modified to include `schedule_data_TXA.h` or `schedule_data_TXB.h` instead of the current compact `trace_data` headers.

## Summary

v1.0 changes the meaning of reporting policy from metadata selection to physical transmission scheduling.

The key design principle is:

```text
A skipped demand row is not deleted. It becomes a silent firmware slot.
```

This is the missing step between delivered-usefulness replay and constrained-airtime reporting.
