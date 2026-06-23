# LoRa PoC Runs 006–008: Reporting-Rate Stress and Delivered Usefulness

## Purpose

Runs 006–008 extended the Run 005 delivery-versus-usefulness demonstration by increasing the reporting rate while preserving the same synthetic usefulness split between two LoRa transmitter streams.

The goal was to test whether packet delivery count, sequence-gap behaviour, radio metadata, and delivered usefulness remain aligned as reporting pressure increases. These runs are part of a small-scale ESP32/LilyGO LoRa proof of concept for belief-maintenance-aware reporting under constrained LoRa airtime.

The runs should be interpreted cautiously. They are not yet operational policy results and should not be described as definitive collision experiments. The usefulness and priority values are synthetic epistemic metadata assigned by the experimenter. The physical LoRa testbed supplies real delivery outcomes, RSSI/SNR values, receiver inter-arrival timing, and observed sequence-gap behaviour.

## Hardware and setup

- Platform: LilyGO LoRa32 T3 V1.6.1 boards
- Radio mode: point-to-point LoRa, not LoRaWAN
- Frequency: 915 MHz
- CRC: enabled in firmware using `LoRa.enableCrc();`
- Receiver: one LilyGO LoRa32 board
- Transmitters:
  - TXA, logical node N01
  - TXB, logical node N16
- Antennas: attached
- Firmware environment: Arduino IDE
- Python environment: `dcoss-lora-poc`
- Parser: `scripts/parse_receiver_log.py`

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

Across Runs 006–008, the same synthetic usefulness split was preserved.

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

The transmitters used the same reporting interval within each run. The intended experimental control was to keep communication opportunity approximately equal while varying synthetic epistemic/usefulness metadata.

## Run configurations

| Run | Run ID | TX delay setting | Purpose |
|---|---:|---:|---|
| Run 006 | R6 | 2000 ms | Higher-rate clean baseline after Run 005 |
| Run 007 | R7 | 1000 ms | First 1-second reporting-rate stress run |
| Run 008 | R8 | 1000 ms | Repeat of Run 007 to check pattern stability |

The true transmission period is slightly longer than the configured `delay()` value because `LoRa.endPacket()` takes time to transmit the packet. This is acceptable for these runs because both transmitters used the same configuration.

## Logging and parsing files

Run 006:

```text
logs/rx_run_006_stress_delivery_usefulness.csv
logs/parsed_run_006_stress_delivery_usefulness.csv
logs/parsed_run_006_stress_delivery_usefulness_rejects.csv
```

Run 007:

```text
logs/rx_run_007_1s_delivery_usefulness.csv
logs/parsed_run_007_1s_delivery_usefulness.csv
logs/parsed_run_007_1s_delivery_usefulness_rejects.csv
```

Run 008:

```text
logs/rx_run_008_1s_repeat_delivery_usefulness.csv
logs/parsed_run_008_1s_repeat_delivery_usefulness.csv
logs/parsed_run_008_1s_repeat_delivery_usefulness_rejects.csv
```

Example parser command:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_008_1s_repeat_delivery_usefulness.csv \
  --out logs/parsed_run_008_1s_repeat_delivery_usefulness.csv
```

## Summary table

| Run | Delay setting | Valid packets | Malformed packets | TXA/N01 packets | TXB/N16 packets | TXA/N01 missing sequences | TXB/N16 missing sequences | TXA/N01 usefulness | TXB/N16 usefulness |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| 006 | 2000 ms | 199 | 0 | 99 | 100 | none | none | 24.75 | 80.00 |
| 007 | 1000 ms | 357 | 0 | 178 | 179 | 2: `[89, 104]` | none | 44.50 | 143.20 |
| 008 | 1000 ms | 437 | 0 | 218 | 219 | 1: `[149]` | none | 54.50 | 175.20 |

## Run 006 parser summary

```text
Valid packets:      199
Malformed packets:  0

Packets by node:
N01     99
N16    100

Packets by transmitter and node:
TXA/N01     99
TXB/N16    100

Sequence range by node:
N01: min 44, max 142, count 99
N16: min 27, max 126, count 100

Missing sequences by transmitter and node:
TXA/N01: none
TXB/N16: none
```

Radio metadata:

```text
N01 mean RSSI: -47.74 dBm
N01 RSSI range: -52.0 to -44.0 dBm
N01 mean SNR: 9.60
N01 SNR range: 9.25 to 10.25

N16 mean RSSI: -52.69 dBm
N16 RSSI range: -56.0 to -48.0 dBm
N16 mean SNR: 9.68
N16 SNR range: 8.75 to 10.50
```

Usefulness:

```text
N01 packets: 99
N01 total usefulness: 24.75
N01 mean usefulness: 0.25
N01 total priority: 29.7
N01 mean priority: 0.30

N16 packets: 100
N16 total usefulness: 80.00
N16 mean usefulness: 0.80
N16 total priority: 90.0
N16 mean priority: 0.90
```

Approximate receiver inter-arrival time:

```text
N01 mean: 2.083 s, min: 2.083 s, max: 2.083 s
N16 mean: 2.083 s, min: 2.082 s, max: 2.084 s
```

## Run 006 interpretation

Run 006 increased the reporting rate relative to Run 005 while preserving balanced delivery. The receiver logged 199 valid packets and no malformed rows. Packet counts were nearly identical: 99 packets from TXA/N01 and 100 packets from TXB/N16. No missing sequence numbers were observed for either stream within the observed sequence ranges.

The receiver inter-arrival times were also effectively identical, with both streams showing a mean inter-arrival time of approximately 2.083 seconds. This confirms that the intended higher-rate configuration was reflected in the received data.

The delivered-usefulness totals remained sharply separated. TXA/N01 delivered 24.75 usefulness units, while TXB/N16 delivered 80.00 usefulness units. Thus, under the 2-second reporting configuration, delivery count still treated the streams as nearly equivalent, while delivered usefulness separated them according to the synthetic epistemic metadata.

Run 006 is best framed as a higher-rate clean baseline, not as a loss or collision result.

## Run 007 parser summary

```text
Valid packets:      357
Malformed packets:  0

Packets by node:
N01    178
N16    179

Packets by transmitter and node:
TXA/N01    178
TXB/N16    179

Sequence range by node:
N01: min 44, max 223, count 178
N16: min 35, max 213, count 179

Missing sequences by transmitter and node:
TXA/N01: missing 2 -> [89, 104]
TXB/N16: none
```

Radio metadata:

```text
N01 mean RSSI: -47.38 dBm
N01 RSSI range: -61.0 to -42.0 dBm
N01 mean SNR: 9.61
N01 SNR range: 9.00 to 10.50

N16 mean RSSI: -53.60 dBm
N16 RSSI range: -60.0 to -47.0 dBm
N16 mean SNR: 9.72
N16 SNR range: 9.00 to 11.75
```

Usefulness:

```text
N01 packets: 178
N01 total usefulness: 44.50
N01 mean usefulness: 0.25
N01 total priority: 53.4
N01 mean priority: 0.30

N16 packets: 179
N16 total usefulness: 143.20
N16 mean usefulness: 0.80
N16 total priority: 161.1
N16 mean priority: 0.90
```

Approximate receiver inter-arrival time:

```text
N01 mean: 1.095 s, min: 1.082 s, max: 2.166 s
N16 mean: 1.083 s, min: 1.083 s, max: 1.084 s
```

## Run 007 interpretation

Run 007 was the first 1-second reporting-rate stress run. The parser logged 357 valid packets and no malformed rows, indicating that the logging and parsing pipeline remained stable at the higher packet volume.

Packet counts remained almost balanced: TXA/N01 delivered 178 packets, while TXB/N16 delivered 179 packets. Delivery count alone would therefore still make the two streams appear nearly equivalent.

However, TXA/N01 showed two missing sequence numbers within the observed sequence range, while TXB/N16 showed none. The N01 maximum receiver inter-arrival time was approximately 2.166 seconds, which is consistent with occasional skipped observations under a nominal one-second reporting configuration. TXB/N16 remained highly regular, with a maximum inter-arrival time of approximately 1.084 seconds.

Average RSSI alone did not explain the sequence-gap outcome. TXA/N01 had stronger mean RSSI than TXB/N16, yet TXA/N01 was the stream with observed sequence gaps. This cautions against interpreting average signal strength as a sufficient explanation for packet continuity.

Delivered usefulness remained strongly separated. TXA/N01 delivered 44.50 usefulness units, while TXB/N16 delivered 143.20 usefulness units. The packet-count difference was only one packet, but the delivered-usefulness difference was 98.70 usefulness units.

Run 007 should be framed as the first observed sequence-gap result under increased reporting pressure. It should not be described as proof of collisions.

## Run 008 parser summary

```text
Valid packets:      437
Malformed packets:  0

Packets by node:
N01    218
N16    219

Packets by transmitter and node:
TXA/N01    218
TXB/N16    219

Sequence range by node:
N01: min 37, max 255, count 218
N16: min 29, max 247, count 219

Missing sequences by transmitter and node:
TXA/N01: missing 1 -> [149]
TXB/N16: none
```

Radio metadata:

```text
N01 mean RSSI: -41.94 dBm
N01 RSSI range: -47.0 to -37.0 dBm
N01 mean SNR: 9.54
N01 SNR range: 9.00 to 10.50

N16 mean RSSI: -52.15 dBm
N16 RSSI range: -78.0 to -49.0 dBm
N16 mean SNR: 9.63
N16 SNR range: 9.00 to 10.25
```

Usefulness:

```text
N01 packets: 218
N01 total usefulness: 54.50
N01 mean usefulness: 0.25
N01 total priority: 65.4
N01 mean priority: 0.30

N16 packets: 219
N16 total usefulness: 175.20
N16 mean usefulness: 0.80
N16 total priority: 197.1
N16 mean priority: 0.90
```

Approximate receiver inter-arrival time:

```text
N01 mean: 1.088 s, min: 1.083 s, max: 2.166 s
N16 mean: 1.083 s, min: 1.082 s, max: 1.084 s
```

## Run 008 interpretation

Run 008 repeated the 1-second reporting-rate condition from Run 007. It again produced a clean parser result, with 437 valid packets and no malformed rows.

The delivery counts were again nearly identical: TXA/N01 delivered 218 packets, while TXB/N16 delivered 219 packets. TXA/N01 showed one missing sequence number within the observed sequence range. TXB/N16 again showed no missing sequence numbers.

The receiver inter-arrival timing supports the sequence-gap observation. N01 had a maximum inter-arrival time of approximately 2.166 seconds, while N16 remained close to the nominal one-second reporting cadence throughout the observed range.

Run 008 also repeated the RSSI caution seen in Run 007. N01 had much stronger mean RSSI than N16, but N01 was still the stream with a sequence gap. N16 had a much lower minimum RSSI value but no observed sequence gaps. Average RSSI and packet continuity therefore need to be analyzed separately.

Delivered usefulness was again sharply separated. TXA/N01 delivered 54.50 usefulness units, while TXB/N16 delivered 175.20 usefulness units. The packet-count difference was one packet, while the delivered-usefulness difference was 120.70 usefulness units.

Run 008 supports the interpretation that the 1-second reporting configuration produces a mostly clean but mildly stressed regime, with occasional sequence gaps appearing in repeated runs.

## Cross-run observations

### 1. The logging and parsing pipeline remained stable

Across Runs 006–008, all parser summaries reported zero malformed packets:

```text
Run 006: 199 valid, 0 malformed
Run 007: 357 valid, 0 malformed
Run 008: 437 valid, 0 malformed
```

This supports the use of the current packet schema and parser for continued proof-of-concept experiments.

### 2. Packet counts remained nearly balanced

Across all three runs, the two streams delivered almost the same number of packets:

```text
Run 006: TXA/N01 99,  TXB/N16 100
Run 007: TXA/N01 178, TXB/N16 179
Run 008: TXA/N01 218, TXB/N16 219
```

Delivery count alone therefore treats the streams as approximately equivalent.

### 3. Delivered usefulness separated the streams sharply

The synthetic usefulness metadata produced large differences in delivered usefulness despite nearly identical delivery counts:

```text
Run 006: TXA/N01 24.75, TXB/N16 80.00
Run 007: TXA/N01 44.50, TXB/N16 143.20
Run 008: TXA/N01 54.50, TXB/N16 175.20
```

In each run, TXB/N16 delivered approximately 3.2 times as much usefulness as TXA/N01. This ratio is consistent with the assigned per-packet usefulness values:

```text
TXA/N01 usefulness per packet = 0.25
TXB/N16 usefulness per packet = 0.80
0.80 / 0.25 = 3.2
```

This directly supports the miniature proof-of-concept claim: information delivery and information usefulness are not the same measurement.

### 4. The 1-second configuration showed occasional sequence gaps

Run 006, with a 2-second delay setting, showed no missing sequences. Runs 007 and 008, both using a 1-second delay setting, showed occasional TXA/N01 sequence gaps:

```text
Run 006: TXA/N01 none, TXB/N16 none
Run 007: TXA/N01 missing [89, 104], TXB/N16 none
Run 008: TXA/N01 missing [149], TXB/N16 none
```

This suggests that the 1-second configuration may be entering a mild constrained-airtime or increased-reporting-pressure regime. However, this should be stated cautiously. The observed sequence gaps do not prove collisions.

### 5. Average RSSI alone did not explain sequence continuity

In Runs 007 and 008, TXA/N01 had stronger mean RSSI than TXB/N16, but TXA/N01 was the stream with observed sequence gaps. TXB/N16 had lower mean RSSI, and in Run 008 had a much lower minimum RSSI value, but showed no sequence gaps.

This suggests that average RSSI is not sufficient by itself to explain observed sequence continuity in these runs.

## Cautions

Missing sequence numbers should not be overclaimed as collisions. A missing sequence means only that a packet was not received or not logged within the observed sequence range. Possible causes include:

- LoRa packet loss;
- packet overlap;
- receiver timing effects;
- transmitter timing alignment;
- power or USB behaviour;
- serial logging effects;
- other bench-test artifacts.

The `recv_ms` and `tx_ms` values are not synchronized across boards. Therefore, `recv_ms - tx_ms` should not be interpreted as true latency. Receiver-side inter-arrival timing and missing sequence detection are meaningful within the current analysis.

The usefulness and priority values are synthetic. Runs 006–008 demonstrate that the testbed can carry, preserve, parse, and summarize epistemic/usefulness metadata alongside real delivery outcomes. They do not yet demonstrate a real adaptive reporting policy.

## Main takeaway

Runs 006–008 extend the initial delivery-versus-usefulness proof of concept. Under increased reporting rates, packet delivery counts remained nearly balanced between two streams, while delivered usefulness remained sharply separated by synthetic epistemic metadata. At the 1-second reporting configuration, repeated runs showed occasional sequence gaps for TXA/N01 while TXB/N16 remained continuous.

The key result is not that one stream is better than the other. The key result is that packet count, sequence gaps, radio metadata, and delivered usefulness tell different parts of the story. A belief-maintenance-aware reporting analysis should therefore consider not only whether packets arrived, but what usefulness those packets carried for the maintained belief state.

## Suggested next steps

1. Preserve Runs 006–008 as a documented reporting-rate ladder.
2. Commit the raw logs, parsed logs, reject files, and this development note.
3. Run a further stress step with a shorter delay, such as 750 ms, while preserving the same synthetic metadata split.
4. Consider adding a summary script that aggregates cross-run metrics into a single table.
5. Later, replace constant usefulness labels with time-varying synthetic belief-demand traces, so that delivered usefulness depends on changing epistemic demand rather than fixed per-stream metadata.

A suitable next run would be:

```text
Run 009
run_id = R9
delay(750)
same TXA/TXB metadata
same physical placement
same logger/parser workflow
```

This would test whether the mild sequence-gap pattern observed at the 1-second setting becomes more pronounced under a further increase in reporting pressure.
