# Run 030 three-transmitter SD physical preparation

Milestone: v3.6-three-transmitter-sd-physical-prep
Branch: exp051-three-transmitter-sd-physical-prep
Status: Physical-preparation milestone

## 1. Purpose

This milestone prepares the first three-transmitter microSD-backed Run 030 replay for later receiver logging.

It follows:

```
v3.4-three-transmitter-sd-replay-design
v3.5-three-transmitter-sd-schedule-prep
```

This milestone does not collect a receiver log.

It does not parse physical packets.

It does not report observed packet proportions.

It does not make three-transmitter physical replay claims.

The purpose is to prepare the firmware and SD-card mapping so that the later physical replay milestone can begin from a clean, documented setup.

## 2. Current confirmed basis

The v3.5 schedule-preparation milestone generated and validated three SD-facing all-slot schedules:

```
TXA/N01: 64 rows, 64 SEND, 0 SKIP
TXB/N16: 64 rows, 32 SEND, 32 SKIP
TXC/N31: 64 rows, 16 SEND, 48 SKIP
```

The SD-facing files are:

```
traces/run030_sd_txa_schedule.csv
traces/run030_sd_txb_schedule.csv
traces/run030_sd_txc_schedule.csv
```

Each file has:

```
1 header row
64 schedule rows
```

The firmware-facing SD schedule schema is:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

The firmware-facing `policy` field must be a single-character code.

Run 030 uses:

```
F for TXA fixed-all rows
U for TXB usefulness-threshold rows
U for TXC usefulness-threshold rows
```

## 3. Firmware inspection result

Before this milestone, the repository contained transmitter firmware directories for TXA and TXB only:

```
firmware/first_radio_link_TX-A
firmware/first_radio_link_TX_B
```

The firmware inspection found:

```
TXA uses TX_ID = "TXA" and NODE_ID = "N01"
TXB uses TX_ID = "TXB" and NODE_ID = "N16"
```

Both TXA and TXB already use the microSD replay path:

```
/schedule.csv
```

Both transmitter sketches already:

```
initialize the SD card
open /schedule.csv
check the expected CSV header
parse the schedule rows
count schedule rows
count SEND rows
replay only rows where send == 1
include TX_ID and NODE_ID in transmitted packets
```

The missing piece for Run 030 was a TXC firmware configuration.

## 4. TXC firmware preparation

This milestone adds:

```
firmware/first_radio_link_TX_C/
```

The TXC sketch was created by copying the existing TXB SD replay sketch and changing only the transmitter identity fields and serial banner.

TXC identity:

```
TX_ID = "TXC"
NODE_ID = "N31"
```

Expected TXC startup banner:

```
=== TX-C: LilyGO LoRa32 sender ===
```

The TXC firmware should otherwise preserve the same SD replay behavior as TXA and TXB.

This is deliberate. The goal is not to redesign the firmware in v3.6. The goal is to add the smallest explicit third-transmitter configuration required for the first three-transmitter physical preparation.

## 5. Stale copied header cleanup

Copying the TXB firmware directory also copied older compiled-header files:

```
trace_data_TXB.h
schedule_data_TXB.h
```

The Run 030 SD replay path uses `/schedule.csv`, not compiled schedule headers.

Those TXB-named header files should not remain in the TXC firmware directory because they could create confusion about the intended TXC identity or replay source.

The TXC firmware directory should therefore contain the TXC sketch without stale TXB schedule/header artifacts.

## 6. SD-card schedule mapping

For the later physical replay, each transmitter SD card should contain its own SD-facing schedule copied as:

```
/schedule.csv
```

The intended mapping is:

```
TXA/N01 -> traces/run030_sd_txa_schedule.csv copied as /schedule.csv
TXB/N16 -> traces/run030_sd_txb_schedule.csv copied as /schedule.csv
TXC/N31 -> traces/run030_sd_txc_schedule.csv copied as /schedule.csv
```

The compact SEND-only files are not SD replay files.

Do not copy these compact files to SD cards as `/schedule.csv`:

```
traces/run030_reporting_txa_fixed_all_compact.csv
traces/run030_reporting_txb_medium_threshold_compact.csv
traces/run030_reporting_txc_strict_threshold_compact.csv
```

## 7. Expected startup checks

After flashing or opening each transmitter sketch and inserting the prepared SD card, each board should report its identity and schedule counts.

Expected identities:

```
TXA/N01
TXB/N16
TXC/N31
```

Expected schedule row counts:

```
TXA: schedule_rows=64
TXB: schedule_rows=64
TXC: schedule_rows=64
```

Expected SEND row counts:

```
TXA: send_rows=64
TXB: send_rows=32
TXC: send_rows=16
```

A mismatch in identity, row count, or SEND count should stop the physical preparation.

## 8. Recommended physical-prep checklist

Before the later receiver-logging milestone:

```
Confirm TXA physical board label.
Confirm TXB physical board label.
Confirm TXC physical board label.
Confirm TXA is flashed with firmware/first_radio_link_TX-A.
Confirm TXB is flashed with firmware/first_radio_link_TX_B.
Confirm TXC is flashed with firmware/first_radio_link_TX_C.
Confirm TXA SD card contains TXA schedule as /schedule.csv.
Confirm TXB SD card contains TXB schedule as /schedule.csv.
Confirm TXC SD card contains TXC schedule as /schedule.csv.
Confirm no compact SEND-only file was copied as /schedule.csv.
Confirm all three boards initialize SD successfully.
Confirm all three boards open /schedule.csv successfully.
Confirm all three boards report 64 schedule rows.
Confirm TXA reports 64 SEND rows.
Confirm TXB reports 32 SEND rows.
Confirm TXC reports 16 SEND rows.
Confirm receiver firmware is unchanged unless explicitly documented.
Confirm receiver logging command is ready but not yet run as part of this milestone.
```

## 9. Deferred physical replay outputs

The later v3.7 physical replay milestone should produce receiver-side outputs such as:

```
logs/rx_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay_rejects.csv
```

and report outputs such as:

```
reports/run030_schedule_aware_manifest.json
reports/run030_schedule_aware_summary.csv
reports/run030_schedule_aware_summary.json
```

Those files are not part of v3.6.

## 10. Interpretation boundary

This milestone is physical preparation only.

It does not establish:

```
three-transmitter physical replay behavior
12-transmitter behavior
exact transmitted-packet counts
confirmed collision counts
synchronized latency
LoRaWAN behavior
energy savings
live belief-controller behavior
operational wildfire behavior
```

Preserve the current cautions:

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
Do not overgeneralize from two-transmitter or three-transmitter lab runs.
```

## 11. Completion criteria

This milestone is complete when:

```
TXC firmware directory exists.
TXC firmware identity is TXC/N31.
TXC startup banner identifies TX-C.
stale TXB-named header files are removed from the TXC firmware directory.
the Run 030 SD-card schedule mapping is documented.
expected startup row and SEND counts are documented.
README includes a short v3.6 addendum.
no receiver log is collected.
no physical replay claims are made.
```

## 12. Summary

Run 030 physical preparation adds the missing TXC firmware configuration and documents the SD-card mapping for the first three-transmitter SD-backed replay.

The intended prepared setup is:

```
TXA/N01: /schedule.csv from traces/run030_sd_txa_schedule.csv, expected send_rows=64
TXB/N16: /schedule.csv from traces/run030_sd_txb_schedule.csv, expected send_rows=32
TXC/N31: /schedule.csv from traces/run030_sd_txc_schedule.csv, expected send_rows=16
```

The next milestone should perform the actual three-transmitter receiver-side physical replay only after these startup checks are confirmed.
