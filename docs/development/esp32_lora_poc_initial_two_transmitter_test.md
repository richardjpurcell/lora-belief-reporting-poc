# ESP32 LoRa Proof-of-Concept: Initial Two-Transmitter Receiver Test

## Purpose

This note records the first successful small-scale proof-of-concept for the LoRa trace-replay experiment. The goal of this stage was to confirm that two LilyGO LoRa32 boards can transmit distinguishable synthetic sensing packets to a third LilyGO LoRa32 receiver board, and that the receiver can log packet metadata together with physical-layer measurements.

This is an early hardware validation step for the larger experiment on belief-maintenance-aware reporting under constrained LoRa airtime.

## Hardware

- 3 x LilyGO LoRa32 T3_V1.6.1 boards, labelled:
  - `RX`: receiver/logger
  - `TX-A`: transmitter for logical node `N01`
  - `TX-B`: transmitter for logical node `N16`
- 868/915 MHz antennas attached to all boards
- Laptop running Arduino IDE and Serial Monitor
- Point-to-point LoRa configuration, not LoRaWAN

## Firmware State

The receiver logs each received packet in a CSV-like format:

```text
RX,recv_ms,run_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr
```

The transmitter payload format is:

```text
run_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy
```

Current logical transmitter assignments:

| Physical board | Logical node | Region | Priority | Usefulness | Policy |
|---|---|---|---:|---:|---|
| TX-A | N01 | A | 0.82 | 0.74 | U |
| TX-B | N16 | B | 0.91 | 0.80 | U |

## Observed Receiver Log

The following receiver output confirms that packets from both transmitters are being received and distinguished by logical node ID:

```text
12:22:26.888 -> RX,461228,R0,N16,96,488552,B,1,0.91,0.80,30,U,-29,9.50
12:22:27.284 -> RX,461639,R0,N01,4,21821,A,1,0.82,0.74,30,U,-26,9.75
12:22:31.938 -> RX,466301,R0,N16,97,493625,B,1,0.91,0.80,30,U,-29,9.75
12:22:32.366 -> RX,466712,R0,N01,5,26894,A,1,0.82,0.74,30,U,-25,9.50
12:22:37.019 -> RX,471374,R0,N16,98,498698,B,1,0.91,0.80,30,U,-29,9.50
12:22:37.413 -> RX,471785,R0,N01,6,31967,A,1,0.82,0.74,30,U,-26,9.25
12:22:42.093 -> RX,476447,R0,N16,99,503771,B,1,0.91,0.80,30,U,-29,9.75
12:22:42.488 -> RX,476857,R0,N01,7,37040,A,1,0.82,0.74,30,U,-26,9.25
12:22:47.168 -> RX,481525,R0,N16,100,508844,B,1,0.91,0.80,30,U,-29,9.75
12:22:47.563 -> RX,481930,R0,N01,8,42113,A,1,0.82,0.74,30,U,-25,9.25
12:22:52.244 -> RX,486603,R0,N16,101,513922,B,1,0.91,0.80,30,U,-32,9.25
12:22:52.638 -> RX,487004,R0,N01,9,47186,A,1,0.82,0.74,30,U,-28,9.25
```

## Interpretation

This log is consistent with a successful two-transmitter, one-receiver LoRa proof-of-concept.

Key observations:

1. The receiver logs packets from both logical nodes, `N16` and `N01`.
2. The packets are distinguishable using the embedded `node_id` field.
3. Sequence numbers increase correctly for each logical transmitter:
   - `N16`: 96, 97, 98, 99, 100, 101
   - `N01`: 4, 5, 6, 7, 8, 9
4. The receiver records physical-layer metadata for each packet:
   - RSSI is approximately -25 to -32 dBm.
   - SNR is approximately 9.25 to 9.75 dB.
5. The received signal is strong, which is expected for a bench-top test with nearby boards.
6. Packets from the two transmitters are arriving close together but are both being decoded successfully in this test.

## Important Timing Note

The `tx_ms` and `recv_ms` values are generated on different ESP32 boards and are not synchronized. Therefore, `recv_ms - tx_ms` should not yet be interpreted as true end-to-end latency.

For now, useful timing measurements include:

- receiver-side inter-arrival time;
- missing sequence numbers;
- ordering of received packets;
- packet spacing observed at the receiver.

True latency measurement should be added later using a laptop-controlled scheduler, clock synchronization, or another shared timing reference.

## Milestone Confirmed

This run confirms the following milestone:

> Two ESP32/LilyGO LoRa transmitters can replay synthetic sensing packets to a single receiver, and the receiver can log packet identity, synthetic metadata, RSSI, and SNR.

This validates the basic hardware path for the trace-replay experiment:

```text
synthetic packet metadata -> LoRa transmitter -> wireless link -> LoRa receiver -> receiver log
```

## Next Development Steps

Suggested next steps:

1. Save receiver serial output directly to `receiver_log.csv` using a Python serial logger.
2. Create a small `scheduled_packets.csv` file representing the intended transmitted packets.
3. Join `scheduled_packets.csv` with `receiver_log.csv` by `run_id`, `node_id`, and `seq`.
4. Compute initial metrics:
   - packet delivery ratio;
   - received packet count by logical node;
   - missing sequence numbers;
   - RSSI and SNR summaries;
   - delivered priority sum;
   - delivered usefulness sum;
   - usefulness per delivered packet.
5. Add a simple policy comparison using two scheduled traces:
   - random budgeted reporting;
   - uncertainty-prioritized reporting.

## Scope Reminder

This proof of concept does not yet test LoRa overload, energy use, full belief-state updating, or real environmental sensing. Its purpose is narrower: to confirm that synthetic packet metadata can be physically transmitted and logged in a form suitable for later delivery-versus-usefulness analysis.
