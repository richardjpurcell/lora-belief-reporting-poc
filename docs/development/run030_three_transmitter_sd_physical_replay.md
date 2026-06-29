# Run 030 three-transmitter SD physical replay

Milestone: v3.7-three-transmitter-sd-physical-replay
Branch: exp052-three-transmitter-sd-physical-replay
Status: Physical replay completed

## 1. Purpose

Run 030 is the first three-transmitter microSD-backed physical replay in the LoRa belief-reporting proof of concept.

It follows:

```
v3.4-three-transmitter-sd-replay-design
v3.5-three-transmitter-sd-schedule-prep
v3.6-three-transmitter-sd-physical-prep
```

The core question for this run is:

```
Can the SD-backed, manifest-bound replay workflow remain readable when we move from two transmitters to three transmitters?
```

This is a physical receiver-side replay result.

It is not a network-scaling result.

It is not a LoRaWAN result.

It is not an energy result.

It is not a live belief-controller result.

## 2. Run configuration

Run ID:

```
R30
```

Physical transmitter identities:

```
TXA/N01
TXB/N16
TXC/N31
```

Firmware configuration:

```
TXA: firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
TXB: firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
TXC: firmware/first_radio_link_TX_C/first_radio_link_TX_C.ino
```

Run 030 firmware identity and startup offset condition:

```
TXA: RUN_ID=R30, no startup offset
TXB: RUN_ID=R30, STARTUP_OFFSET_MS=500
TXC: RUN_ID=R30, STARTUP_OFFSET_MS=750
```

The TXC offset was changed from 500 ms to 750 ms before the physical replay so that TXC would not share TXB's startup offset. This reflects the practical bench observation that the receiver behaves better when transmitter starts are staggered.

## 3. SD schedule configuration

Each transmitter used an SD-facing all-slot schedule copied to its SD card as:

```
/schedule.csv
```

The SD card mapping was:

```
TXA/N01 -> traces/run030_sd_txa_schedule.csv copied as /schedule.csv
TXB/N16 -> traces/run030_sd_txb_schedule.csv copied as /schedule.csv
TXC/N31 -> traces/run030_sd_txc_schedule.csv copied as /schedule.csv
```

The SD card volume labels used during preparation were:

```
LORA_TXA
LORA_TXB
LORA_TXC
```

Each copied schedule was checked with:

```
ls -l
head -5
wc -l
```

Each SD-facing schedule had:

```
1 header row
64 schedule rows
65 total lines
```

The first rows confirmed the expected firmware-facing policy codes:

```
TXA: F policy code
TXB: U policy code
TXC: U policy code
```

The compact SEND-only CSVs were not copied to SD cards.

## 4. Expected schedule counts

The Run 030 schedules were:

```
TXA/N01: fixed-all baseline, 64/64 SEND
TXB/N16: medium threshold, 32/64 SEND
TXC/N31: strict threshold, 16/64 SEND
```

Expected scheduled SEND proportions:

```
TXB/TXA = 32/64 = 0.5000
TXC/TXA = 16/64 = 0.2500
TXC/TXB = 16/32 = 0.5000
```

These are scheduled-send proportions only.

They are not exact transmitted-packet counts.

They are not collision counts.

They are not energy measurements.

## 5. Startup verification

Before receiver logging, transmitter startup output confirmed that each board loaded the expected schedule.

TXA startup check:

```
tx_id=TXA
node_id=N01
rows_loaded=64
send_rows=64
skip_rows=0
replay_period_rows=64
packet_format=existing
```

TXB startup check:

```
tx_id=TXB
node_id=N16
rows_loaded=64
send_rows=32
skip_rows=32
replay_period_rows=64
packet_format=existing
```

TXC startup check:

```
tx_id=TXC
node_id=N31
rows_loaded=64
send_rows=16
skip_rows=48
replay_period_rows=64
packet_format=existing
```

The observed startup output confirmed that TXA, TXB, and TXC each read the intended `/schedule.csv` file and exposed the expected schedule counts before receiver logging.

## 6. Receiver log and parse commands

The receiver log was saved as:

```
logs/rx_run_030_three_transmitter_sd_replay.csv
```

The parsed output was generated with:

```
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_030_three_transmitter_sd_replay.csv \
  --out logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --seq-window 50
```

The parser wrote:

```
logs/parsed_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay_rejects.csv
```

## 7. Parser summary

The parser reported:

```
Valid packets:      685
Malformed packets:  1
```

Packets by node:

```
N01    393
N16    194
N31     98
```

Packets by transmitter and node:

```
TXA/N01    393
TXB/N16    194
TXC/N31     98
```

Sequence ranges by node:

```
N01: min 0, max 393, count 393
N16: min 0, max 196, count 194
N31: min 0, max 97,  count 98
```

Missing observed sequence numbers:

```
TXA/N01: missing 1 -> [78]
TXB/N16: missing 3 -> [10, 12, 89]
TXC/N31: none
```

These are observed sequence gaps only. They are not confirmed collision counts.

## 8. Observed packet proportions

Observed receiver-side packet counts:

```
TXA/N01: 393
TXB/N16: 194
TXC/N31: 98
```

Observed receiver-side ratios:

```
TXB/TXA = 194 / 393 = 0.4936
TXC/TXA =  98 / 393 = 0.2494
TXC/TXB =  98 / 194 = 0.5052
```

Scheduled SEND ratios:

```
TXB/TXA = 0.5000
TXC/TXA = 0.2500
TXC/TXB = 0.5000
```

The observed receiver-side packet proportions were close to the scheduled SEND proportions.

Careful interpretation:

```
Run 030 supports that the SD-backed, manifest-bound replay workflow remained readable after adding a third transmitter under this lab condition.
```

This should not be restated as exact transmitted-packet measurement, confirmed collision behavior, synchronized latency, energy saving, or general network scaling.

## 9. Radio metadata

Radio metadata by node:

```
N01: mean RSSI -45.90, min RSSI -50.0, max RSSI -41.0, mean SNR 9.73
N16: mean RSSI -52.26, min RSSI -57.0, max RSSI -45.0, mean SNR 9.70
N31: mean RSSI -44.98, min RSSI -48.0, max RSSI -42.0, mean SNR 9.66
```

These are receiver-side observations for this bench run.

They should not be overgeneralized.

## 10. Usefulness result

Usefulness by node:

```
TXA/N01: packets 393, total usefulness 205.80, mean usefulness 0.524
TXB/N16: packets 194, total usefulness 157.14, mean usefulness 0.810
TXC/N31: packets  98, total usefulness  85.26, mean usefulness 0.870
```

Priority by node:

```
TXA/N01: total priority 215.62, mean priority 0.549
TXB/N16: total priority 162.96, mean priority 0.840
TXC/N31: total priority  88.20, mean priority 0.900
```

The intended mean-usefulness ordering was preserved:

```
TXA fixed-all baseline < TXB medium threshold < TXC strict threshold
```

This is consistent with the scheduled-skipping design: the threshold-selected streams sent fewer packets while retaining higher mean delivered usefulness per received packet.

The usefulness and priority values remain synthetic metadata.

## 11. Receiver inter-arrival observations

Approximate receiver inter-arrival times by node:

```
N01: mean 1.003 s, min 0.999 s, max 2.000 s
N16: mean 2.031 s, min 1.999 s, max 4.000 s
N31: mean 3.979 s, min 2.000 s, max 6.005 s
```

These receiver-side inter-arrival summaries are consistent with the expected schedule pattern:

```
TXA sends every slot
TXB sends approximately every second slot
TXC sends less frequently under the strict threshold schedule
```

These are receiver-side observations only.

They are not synchronized latency measurements.

## 12. Malformed packet

The reject file contained one malformed raw line:

```
RX,6877399,#����?c�U,'�̪9""Gp`�%d`٦�96�h�8|��ޏ�Zg^����-��1
```

The parse error was:

```
expected 15 fields, got 4
```

This single malformed packet should be documented as part of the physical receiver-side run. It does not prevent the Run 030 stream from being readable, because 685 valid packets were recovered and all three transmitter identities were present with the expected relative proportions.

## 13. Windowed usefulness summary

Using a sequence window of 50, the parsed summary showed stable usefulness patterns across the received stream.

TXA/N01 windows had mean usefulness near 0.52.

TXB/N16 windows had mean usefulness near 0.81.

TXC/N31 windows had mean usefulness near 0.87.

This supports the interpretation that the receiver/parser recovered the intended metadata pattern across all three transmitter streams.

## 14. Careful result statement

Run 030 provides the first three-transmitter SD-backed physical replay result.

Under this bench condition, TXA/N01, TXB/N16, and TXC/N31 were all recovered by the receiver/parser. The observed receiver-side packet proportions were close to the scheduled SEND proportions:

```
TXB/TXA observed 0.4936 vs scheduled 0.5000
TXC/TXA observed 0.2494 vs scheduled 0.2500
TXC/TXB observed 0.5052 vs scheduled 0.5000
```

The intended usefulness ordering was also preserved:

```
TXA mean usefulness 0.524
TXB mean usefulness 0.810
TXC mean usefulness 0.870
```

Therefore, Run 030 supports a bounded workflow-readability claim:

```
The SD-backed, manifest-bound replay workflow remained readable when moving from two transmitters to three transmitters under this lab condition.
```

## 15. Interpretation boundary

This is a three-transmitter point-to-point LoRa bench result.

It does not establish:

```
12-transmitter behavior
exact transmitted-packet counts
confirmed collision counts
synchronized latency
LoRaWAN behavior
airtime optimization
energy savings
live belief-controller behavior
operational wildfire behavior
```

Continue to preserve these cautions:

```
This is point-to-point LoRa at 915 MHz, not LoRaWAN.
The schedule CSVs define one repeated schedule period.
The analyzer compares schedule proportions and observed packet proportions.
The analyzer does not infer exact transmitted-packet counts.
Missing sequence numbers are observed sequence gaps only, not confirmed collisions.
recv_ms and tx_ms are not synchronized across boards and are not true latency.
Receiver inter-arrival summaries are receiver-side observations only.
Usefulness and priority are synthetic metadata.
The run does not yet use a live belief-maintenance controller.
Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
Do not claim energy savings unless current or power measurements are added.
Do not overgeneralize from this three-transmitter lab run.
```

## 16. Completion status

Run 030 physical replay produced:

```
logs/rx_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay_rejects.csv
```

The parser accepted TXC/N31 cleanly as a third transmitter identity.

The receiver-side stream was readable across all three transmitters.

One malformed raw packet was observed and documented.

The milestone is ready for commit once this note and the log artifacts are staged.
