# LoRa PoC Run 005: Delivery Count Versus Delivered Usefulness

## Purpose

Run 005 was the first miniature delivery-versus-usefulness demonstration for the ESP32/LilyGO LoRa proof of concept.

The goal was to keep the communication opportunity approximately the same for two synthetic sensing streams while assigning different synthetic epistemic metadata. This run was not intended to demonstrate an operational policy result. Instead, it tested whether the logging and parsing pipeline can distinguish packet delivery from delivered usefulness when physical delivery outcomes are supplied by the LoRa testbed.

## Hardware and setup

* Platform: LilyGO LoRa32 T3 V1.6.1 boards
* Radio mode: point-to-point LoRa, not LoRaWAN
* Frequency: 915 MHz
* CRC: enabled in firmware using `LoRa.enableCrc();`
* Receiver: one LilyGO LoRa32 board
* Transmitters:

  * TXA, logical node N01
  * TXB, logical node N16
* Antennas: attached
* Logger environment: `dcoss-lora-poc`

## Packet schema

Receiver rows used the 15-field schema:

```text
RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr
```

The transmitter payload fields were:

```text
run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy
```

The receiver added `RX`, `recv_ms`, `rssi`, and `snr`.

## Synthetic stream configuration

Run identifier:

```text
R5
```

TXA/N01 was configured as the lower-value/random baseline stream:

```text
tx_id = TXA
node_id = N01
region = A
event = 1
priority = 0.30
usefulness = 0.25
stale_after = 30
policy = R
```

TXB/N16 was configured as the higher-value/prioritized stream:

```text
tx_id = TXB
node_id = N16
region = B
event = 1
priority = 0.90
usefulness = 0.80
stale_after = 30
policy = U
```

Both transmitters used the same reporting interval. The intent was to hold communication opportunity approximately constant and vary only the synthetic usefulness metadata.

## Logging and parsing commands

The raw receiver log was saved as:

```text
logs/rx_run_005_delivery_usefulness.csv
```

The parser was run with:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_005_delivery_usefulness.csv \
  --out logs/parsed_run_005_delivery_usefulness.csv
```

The parsed output was written to:

```text
logs/parsed_run_005_delivery_usefulness.csv
```

Malformed or rejected rows were written to:

```text
logs/parsed_run_005_delivery_usefulness_rejects.csv
```

## Parser summary

```text
Valid packets:      74
Malformed packets:  0
```

Packets by node:

```text
N01    37
N16    37
```

Packets by transmitter and node:

```text
TXA/N01    37
TXB/N16    37
```

Sequence ranges:

```text
N01: 67 to 103, count 37
N16: 54 to 90,  count 37
```

Missing sequences:

```text
TXA/N01: none
TXB/N16: none
```

Radio metadata by node:

```text
N01 mean RSSI: -49.95 dBm
N01 RSSI range: -57.0 to -45.0 dBm
N01 mean SNR: 9.67
N01 SNR range: 9.00 to 10.50

N16 mean RSSI: -54.00 dBm
N16 RSSI range: -65.0 to -50.0 dBm
N16 mean SNR: 9.74
N16 SNR range: 9.25 to 10.00
```

Usefulness by node:

```text
N01 packets: 37
N01 total usefulness: 9.25
N01 mean usefulness: 0.25
N01 total priority: 11.1
N01 mean priority: 0.30

N16 packets: 37
N16 total usefulness: 29.60
N16 mean usefulness: 0.80
N16 total priority: 33.3
N16 mean priority: 0.90
```

Approximate receiver inter-arrival time by node:

```text
N01 mean: 5.083 s
N16 mean: 5.083 s
```

## Interpretation

Run 005 produced a clean miniature demonstration of delivery count versus delivered usefulness.

Both streams delivered exactly 37 packets. Neither stream had missing sequence numbers within the observed sequence range. Both streams also had effectively identical receiver inter-arrival times. This supports the interpretation that the two streams had comparable communication opportunity during the run.

The radio metadata showed broadly comparable link quality. TXB/N16 had lower mean RSSI than TXA/N01, but the mean SNR values were very similar. Since both streams delivered the same number of packets with no observed sequence gaps, the difference in delivered usefulness is not explained by packet count.

The key result is that packet delivery count alone treats the two streams as equivalent:

```text
TXA/N01: 37 received packets
TXB/N16: 37 received packets
```

However, delivered usefulness separates the streams:

```text
TXA/N01: 37 × 0.25 = 9.25 total delivered usefulness
TXB/N16: 37 × 0.80 = 29.60 total delivered usefulness
```

Thus, TXB/N16 delivered approximately 3.2 times as much synthetic usefulness as TXA/N01 despite having the same delivered packet count.

## Main takeaway

Run 005 demonstrates the proof-of-concept analysis idea: information delivery and information usefulness are not the same measurement. In this controlled miniature run, delivery count made the two streams appear equivalent, while delivered usefulness distinguished them.

This should be framed cautiously. The usefulness values in Run 005 were synthetic metadata assigned by the experimenter, not learned from a real belief-maintenance controller. The result is therefore not yet a policy result or an airtime-allocation result. It is evidence that the physical LoRa logging pipeline can carry, preserve, parse, and summarize epistemic/usefulness metadata alongside real delivery outcomes.

## Caution on missing sequences

No missing sequence numbers were observed in Run 005. This should not be overinterpreted as proof that no packet collisions or radio losses occurred. Missing sequence analysis only reports gaps within the observed sequence range. A missing sequence means a packet was not received or not logged within that range. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB issues, or logger-side effects.

## Implication for next runs

Run 005 establishes a clean baseline for delivery-versus-usefulness logging. A natural next step is to introduce controlled stress while preserving the same schema, for example:

1. increase reporting rate to create more contention;
2. run longer to observe whether sequence gaps appear;
3. introduce a third transmitter if available;
4. vary usefulness dynamically over time rather than holding it constant;
5. compute usefulness delivered per received packet, per minute, and per occupied airtime opportunity.

The next experimental step should still avoid overclaiming collision behavior unless the run is explicitly designed to test packet overlap or channel contention.
