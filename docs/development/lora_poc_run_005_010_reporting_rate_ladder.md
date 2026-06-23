# LoRa PoC Runs 005–010: Reporting-Rate Ladder and Delivered Usefulness

## Purpose

Runs 005–010 form the first reporting-rate ladder for the ESP32/LilyGO LoRa proof of concept.

The goal was to test whether a small point-to-point LoRa testbed can carry synthetic epistemic/usefulness metadata alongside real physical delivery outcomes, and whether packet delivery count can be separated from delivered usefulness under increasing reporting pressure.

The broader paper direction is belief-maintenance-aware reporting under constrained LoRa airtime. These runs remain a miniature laboratory proof of concept. They should not yet be framed as an operational policy result or as a definitive collision experiment.

The central demonstration is:

```text
Information delivery is not the same as information usefulness.
```

In these runs, both streams were given similar communication opportunity, but different synthetic usefulness metadata. The physical testbed supplied real received packet counts, sequence-gap behaviour, RSSI, SNR, and receiver inter-arrival timing.

## Hardware and setup

- Platform: LilyGO LoRa32 T3 V1.6.1 boards
- Radio mode: point-to-point LoRa, not LoRaWAN
- Frequency: 915 MHz
- Boards:
  - one receiver board
  - one TX-A board
  - one TX-B board
- Antennas: attached
- Firmware environment: Arduino IDE
- Python environment: `dcoss-lora-poc`
- Python version: 3.11.15
- Main Python packages:
  - `pyserial`
  - `pandas`

The receiver firmware was left unchanged across this ladder after the packet schema had stabilized. The transmitter firmware was modified by changing the run identifier and the reporting delay.

## Packet schema

Receiver rows used the 15-field schema:

```text
RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr
```

The transmitted payload contains:

```text
run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy
```

The receiver adds:

```text
RX,recv_ms,rssi,snr
```

Important timing caution: `recv_ms` and `tx_ms` are not synchronized across boards. Therefore, `recv_ms - tx_ms` should not be interpreted as true end-to-end latency. Receiver inter-arrival time and sequence-gap analysis are meaningful within the limits of this setup.

## Synthetic stream configuration

Across Runs 005–010, the synthetic metadata split was held constant.

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

The experiment does not claim that these usefulness values were inferred from an operational belief-maintenance controller. They are synthetic metadata assigned for proof-of-concept testing.

## Reporting-rate ladder

The reporting interval was controlled in the transmitter sketches using `delay(...)`.

The ladder was:

```text
Run 005: delay(5000)
Run 006: delay(2000)
Run 007: delay(1000)
Run 008: delay(1000), repeat
Run 009: delay(750)
Run 010: delay(750), repeat
```

Because `LoRa.endPacket()` and loop overhead take time, the observed receiver inter-arrival times are slightly longer than the nominal delay values.

## Logging and parsing workflow

The parser was run with commands of this form:

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_XXX_*.csv \
  --out logs/parsed_run_XXX_*.csv
```

The parser writes:

- a parsed valid-packet CSV;
- a rejects CSV for malformed rows;
- a terminal summary with packet counts, missing sequence numbers, radio metadata, usefulness totals, priority totals, and approximate receiver inter-arrival times.

## Summary table

| Run | Nominal TX delay | TXA/N01 packets | TXA/N01 missing | TXA usefulness | TXB/N16 packets | TXB/N16 missing | TXB usefulness | Malformed |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 005 | 5000 ms | 37 | 0 | 9.25 | 37 | 0 | 29.60 | 0 |
| 006 | 2000 ms | 99 | 0 | 24.75 | 100 | 0 | 80.00 | 0 |
| 007 | 1000 ms | 178 | 2 | 44.50 | 179 | 0 | 143.20 | 0 |
| 008 | 1000 ms | 218 | 1 | 54.50 | 219 | 0 | 175.20 | 0 |
| 009 | 750 ms | 263 | 8 | 65.75 | 269 | 2 | 215.20 | 0 |
| 010 | 750 ms | 284 | 1 | 71.00 | 282 | 2 | 225.60 | 0 |

## Run 005: 5-second clean baseline

Run 005 was the first miniature delivery-versus-usefulness demonstration.

Parser summary:

```text
Valid packets:      74
Malformed packets:  0

TXA/N01: 37 packets
TXB/N16: 37 packets

TXA/N01 missing sequences: none
TXB/N16 missing sequences: none

TXA/N01 total usefulness: 9.25
TXB/N16 total usefulness: 29.60

N01 mean inter-arrival: 5.083 s
N16 mean inter-arrival: 5.083 s
```

Interpretation:

Run 005 showed identical received packet counts, no observed sequence gaps, and effectively identical receiver inter-arrival times. Delivery count treated the two streams as equivalent, while delivered usefulness separated them.

```text
TXA/N01: 37 × 0.25 = 9.25
TXB/N16: 37 × 0.80 = 29.60
```

TXB/N16 delivered approximately 3.2 times as much synthetic usefulness as TXA/N01 despite identical received packet count.

## Run 006: 2-second higher-rate clean baseline

Run 006 increased reporting pressure by changing the transmitter delay to 2000 ms.

Parser summary:

```text
Valid packets:      199
Malformed packets:  0

TXA/N01: 99 packets
TXB/N16: 100 packets

TXA/N01 missing sequences: none
TXB/N16 missing sequences: none

TXA/N01 total usefulness: 24.75
TXB/N16 total usefulness: 80.00

N01 mean inter-arrival: 2.083 s
N16 mean inter-arrival: 2.083 s
```

Interpretation:

Run 006 remained clean under the faster reporting cadence. Packet counts were nearly identical and no sequence gaps were observed. Delivered usefulness remained strongly separated because of the synthetic usefulness metadata.

```text
TXA/N01: 99 × 0.25 = 24.75
TXB/N16: 100 × 0.80 = 80.00
```

Run 006 is best described as a higher-rate clean baseline, not as a stressed or lossy result.

## Run 007: 1-second first sequence-gap run

Run 007 changed the transmitter delay to 1000 ms.

Parser summary:

```text
Valid packets:      357
Malformed packets:  0

TXA/N01: 178 packets
TXB/N16: 179 packets

TXA/N01 missing sequences: 2 -> [89, 104]
TXB/N16 missing sequences: none

TXA/N01 total usefulness: 44.50
TXB/N16 total usefulness: 143.20

N01 mean inter-arrival: 1.095 s
N01 max inter-arrival: 2.166 s

N16 mean inter-arrival: 1.083 s
N16 max inter-arrival: 1.084 s
```

Interpretation:

Run 007 was the first run where sequence-gap analysis became informative. TXA/N01 showed two missing sequence numbers within the observed sequence range, while TXB/N16 showed none.

Packet counts remained nearly equal:

```text
TXA/N01: 178 packets
TXB/N16: 179 packets
```

Delivered usefulness was sharply separated:

```text
TXA/N01: 178 × 0.25 = 44.50
TXB/N16: 179 × 0.80 = 143.20
```

The maximum N01 inter-arrival time was approximately two reporting intervals, consistent with occasional skipped observations rather than a general receiver or logger collapse.

## Run 008: 1-second repeat

Run 008 repeated the 1000 ms condition.

Parser summary:

```text
Valid packets:      437
Malformed packets:  0

TXA/N01: 218 packets
TXB/N16: 219 packets

TXA/N01 missing sequences: 1 -> [149]
TXB/N16 missing sequences: none

TXA/N01 total usefulness: 54.50
TXB/N16 total usefulness: 175.20

N01 mean inter-arrival: 1.088 s
N01 max inter-arrival: 2.166 s

N16 mean inter-arrival: 1.083 s
N16 max inter-arrival: 1.084 s
```

Interpretation:

Run 008 confirmed the Run 007 pattern. At the 1-second setting, packet counts remained nearly equal, TXA/N01 again showed a small sequence-gap event, and TXB/N16 again showed no observed sequence gaps.

This supports the cautious statement that the 1-second setting begins to show occasional sequence-gap behaviour while preserving balanced received packet counts.

## Run 009: corrected 750 ms two-transmitter run

An initial Run 009 attempt contained only TXA/N01 packets and was discarded/replaced. After reflashing TX-B, Run 009 was repeated as the corrected two-transmitter 750 ms run.

Parser summary:

```text
Valid packets:      532
Malformed packets:  0

TXA/N01: 263 packets
TXB/N16: 269 packets

TXA/N01 missing sequences: 8 -> [605, 631, 666, 692, 701, 739, 749, 762]
TXB/N16 missing sequences: 2 -> [223, 248]

TXA/N01 total usefulness: 65.75
TXB/N16 total usefulness: 215.20

N01 mean inter-arrival: 0.858 s
N01 max inter-arrival: 1.666 s

N16 mean inter-arrival: 0.839 s
N16 max inter-arrival: 1.666 s
```

Interpretation:

Run 009 was the first corrected two-transmitter run in which both streams showed observed sequence gaps.

Packet counts remained broadly comparable:

```text
TXA/N01: 263 packets
TXB/N16: 269 packets
```

Delivered usefulness remained sharply separated:

```text
TXA/N01: 263 × 0.25 = 65.75
TXB/N16: 269 × 0.80 = 215.20
```

TXB/N16 delivered approximately 3.27 times as much synthetic usefulness as TXA/N01.

The maximum inter-arrival time for both nodes was approximately two reporting intervals, consistent with occasional skipped observations.

## Run 010: 750 ms repeat

Run 010 repeated the corrected 750 ms two-transmitter condition.

Parser summary:

```text
Valid packets:      566
Malformed packets:  0

TXA/N01: 284 packets
TXB/N16: 282 packets

TXA/N01 missing sequences: 1 -> [88]
TXB/N16 missing sequences: 2 -> [125, 221]

TXA/N01 total usefulness: 71.00
TXB/N16 total usefulness: 225.60

N01 mean inter-arrival: 0.840 s
N01 max inter-arrival: 1.665 s

N16 mean inter-arrival: 0.842 s
N16 max inter-arrival: 1.676 s
```

Interpretation:

Run 010 confirmed that the 750 ms setting is a useful stress condition. Both streams were present, the parser remained clean, and both streams showed observed sequence gaps.

Compared with Run 009, the exact distribution of missing sequences changed. Run 009 had more TXA/N01 gaps; Run 010 had low gap counts on both streams. This suggests that the 750 ms condition produces sequence-gap behaviour, but not a stable per-node loss pattern under the current setup.

Packet counts remained close:

```text
TXA/N01: 284 packets
TXB/N16: 282 packets
```

Delivered usefulness remained sharply separated:

```text
TXA/N01: 284 × 0.25 = 71.00
TXB/N16: 282 × 0.80 = 225.60
```

## Cross-run observations

### 1. Parser and schema stability

All runs in the ladder had zero malformed packets:

```text
Run 005: 0 malformed
Run 006: 0 malformed
Run 007: 0 malformed
Run 008: 0 malformed
Run 009: 0 malformed
Run 010: 0 malformed
```

This supports the current packet schema, receiver logger, and parser as a stable measurement pipeline for the proof of concept.

### 2. Delivery count stayed broadly balanced

Across all intended two-transmitter runs, received packet counts stayed close between streams.

This is useful experimentally because it allows the analysis to show that delivery count alone often treats the streams as similar or nearly equivalent.

### 3. Delivered usefulness remained sharply separated

Because usefulness was fixed at 0.25 for TXA/N01 and 0.80 for TXB/N16, delivered usefulness was strongly separated in every run.

Examples:

```text
Run 005:
TXA/N01 usefulness = 9.25
TXB/N16 usefulness = 29.60

Run 010:
TXA/N01 usefulness = 71.00
TXB/N16 usefulness = 225.60
```

The core pattern is stable:

```text
similar delivery count
different delivered usefulness
```

### 4. Sequence gaps emerged as reporting rate increased

The sequence-gap pattern changed with reporting rate:

```text
5 s:    no sequence gaps
2 s:    no sequence gaps
1 s:    occasional TXA/N01 sequence gaps
750 ms: sequence gaps on both streams
```

This supports treating the ladder as a gradual movement from clean delivery toward a mildly constrained reporting regime.

### 5. RSSI alone did not explain sequence gaps

Across several runs, TXA/N01 had stronger mean RSSI than TXB/N16 but still showed sequence gaps. This cautions against explaining packet continuity using average RSSI alone.

Delivery outcomes should be interpreted using:

- received packet counts;
- missing sequence numbers;
- receiver inter-arrival timing;
- RSSI/SNR;
- delivered usefulness.

## Cautions

### Missing sequence is not the same as collision

A missing sequence means that a packet was not received or not logged within the observed sequence range.

It does not prove that a collision occurred.

Possible causes include:

- LoRa packet overlap;
- channel loss;
- receiver timing;
- radio configuration effects;
- power or USB issues;
- logger-side effects;
- board-specific timing differences.

The correct phrasing is:

```text
observed sequence gaps
```

not:

```text
collisions
```

unless a later experiment is explicitly designed to test collisions.

### Usefulness is synthetic

The usefulness and priority fields were assigned manually in the transmitter payloads. They were not generated by a live belief-maintenance controller in these runs.

The correct framing is:

```text
synthetic epistemic/usefulness metadata
```

not:

```text
operational policy usefulness
```

### This is not yet an airtime-allocation policy result

Runs 005–010 do not yet compare adaptive reporting policies. Both transmitters were given the same nominal reporting opportunity in each run.

The result is a proof of logging, parsing, and analysis concept:

```text
Physical delivery outcomes can be recorded alongside synthetic usefulness metadata,
allowing delivery and delivered usefulness to be analyzed separately.
```

## Implications for next experiments

Runs 005–010 establish a clean first reporting-rate ladder:

```text
5 s      -> clean balanced baseline
2 s      -> clean higher-rate baseline
1 s      -> first occasional sequence gaps
750 ms   -> repeatable sequence gaps on both streams
```

Natural next steps include:

1. repeat the 750 ms condition with changed physical placement;
2. add a 500 ms stress run;
3. introduce dynamic usefulness values rather than fixed per-node usefulness;
4. compute delivered usefulness per minute;
5. compute delivered usefulness per received packet;
6. compute missed usefulness due to missing sequence numbers;
7. design an explicit overlap/collision experiment with synchronized or intentionally offset transmit timing;
8. later introduce policy-controlled reporting where usefulness affects transmission decisions.

A particularly useful next research step would be a dynamic usefulness run in which one stream's usefulness changes over time. That would move the proof of concept closer to belief-maintenance-aware reporting while still keeping the hardware setup simple.

## Suggested repository placement

Suggested filename:

```text
docs/development/lora_poc_run_005_010_reporting_rate_ladder.md
```

Suggested commit message:

```bash
git add docs/development/lora_poc_run_005_010_reporting_rate_ladder.md \
        logs/rx_run_005_delivery_usefulness.csv \
        logs/parsed_run_005_delivery_usefulness.csv \
        logs/parsed_run_005_delivery_usefulness_rejects.csv \
        logs/rx_run_006_stress_delivery_usefulness.csv \
        logs/parsed_run_006_stress_delivery_usefulness.csv \
        logs/parsed_run_006_stress_delivery_usefulness_rejects.csv \
        logs/rx_run_007_1s_delivery_usefulness.csv \
        logs/parsed_run_007_1s_delivery_usefulness.csv \
        logs/parsed_run_007_1s_delivery_usefulness_rejects.csv \
        logs/rx_run_008_1s_repeat_delivery_usefulness.csv \
        logs/parsed_run_008_1s_repeat_delivery_usefulness.csv \
        logs/parsed_run_008_1s_repeat_delivery_usefulness_rejects.csv \
        logs/rx_run_009_750ms_delivery_usefulness.csv \
        logs/parsed_run_009_750ms_delivery_usefulness.csv \
        logs/parsed_run_009_750ms_delivery_usefulness_rejects.csv \
        logs/rx_run_010_750ms_repeat_delivery_usefulness.csv \
        logs/parsed_run_010_750ms_repeat_delivery_usefulness.csv \
        logs/parsed_run_010_750ms_repeat_delivery_usefulness_rejects.csv

git commit -m "Document LoRa reporting-rate ladder"
```
