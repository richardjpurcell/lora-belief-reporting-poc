# Three-Transmitter SD Replay Design

Milestone: v3.4-three-transmitter-sd-replay-design
Branch: exp049-three-transmitter-sd-replay-design
Status: Design-only

## Purpose

This milestone designs the smallest safe three-transmitter SD-backed replay experiment for the LoRa belief-reporting proof of concept.

The core design question is:

```
Can the SD-backed, manifest-bound replay workflow remain readable when we move from two transmitters to three transmitters?
```

This is a storage-and-replay workflow design milestone. It does not generate schedules, copy SD cards, flash firmware, run receivers, or collect physical logs.

## Current basis

The current microSD-backed replay phase has been synthesized through Run 029.

Run 028 established the first successful 16-row microSD-backed physical replay:

```
TXA/N01: 16/16 SEND, 378 received packets, mean usefulness 0.539
TXB/N16: 12/16 SEND, 284 received packets, mean usefulness 0.668

Scheduled TXB/TXA ratio: 0.7500
Observed TXB/TXA ratio: 0.7513
```

Run 029 extended the SD-backed replay path to a 64-row schedule:

```
TXA/N01: 64/64 SEND, 478 received packets, mean usefulness 0.526
TXB/N16: 32/64 SEND, 241 received packets, mean usefulness 0.810

Scheduled TXB/TXA ratio: 0.5000
Observed TXB/TXA ratio: 0.5042
Malformed packets: 0
```

Careful current synthesis:

```
Under similar two-transmitter lab conditions, microSD-backed all-slot schedule replay preserved the expected scheduled-skipping received-packet proportions for both a 16-row loose-threshold condition and a 64-row medium-threshold condition, while the threshold-selected stream retained higher mean delivered usefulness per received packet than the fixed-all stream.
```

## Interpretation boundary

This milestone preserves the current interpretation boundary.

The existing SD replay phase is a storage-and-replay result, not a network-scaling result.

It does not yet establish:

```
three-or-more-transmitter behavior
12-transmitter behavior
exact transmitted-packet counts
confirmed collision counts
synchronized latency
LoRaWAN behavior
energy savings
live belief-controller behavior
operational wildfire behavior
```

Required cautions:

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
Do not overgeneralize from two-transmitter lab runs.
```

## Proposed three-transmitter design

The next step should be a cautious move from two transmitters to three transmitters.

The recommended starting design is:

```
TXA/N01: fixed-all baseline, 64/64 SEND
TXB/N16: medium threshold, 32/64 SEND
TXC/N31: strict threshold, 16/64 SEND
```

The TXC node ID should be confirmed against the physical label on the third transmitter before schedule preparation. If the physical board is already labeled differently, the physical label should take precedence over the placeholder N31.

## Why this design

The three-transmitter design should preserve as much of the Run 029 structure as possible while adding only one new physical interaction surface.

Keeping 64 rows has several advantages:

```
it reuses the current longer SD replay period scale
it avoids changing duration and schedule length at the same time as transmitter count
it gives enough rows for 64/64, 32/64, and 16/64 scheduled-send patterns
it keeps the first three-transmitter experiment small enough to inspect manually
```

Using strict threshold behavior for TXC is preferable to introducing a phase-shifted medium threshold in the first three-transmitter run.

A strict 16/64 TXC stream gives a simple expected scheduled proportion:

```
TXB/TXA scheduled ratio: 32/64 = 0.5000
TXC/TXA scheduled ratio: 16/64 = 0.2500
TXC/TXB scheduled ratio: 16/32 = 0.5000
```

These ratios should remain readable in receiver-side summaries without requiring claims about exact transmitted packet counts.

A phase-shifted medium threshold may be useful later, but it introduces an additional design variable. For the first three-transmitter SD replay test, transmitter count should be the main new variable.

## Packet format

The existing packet format should be preserved for v3.4 and the later physical replay milestones unless a concrete parser limitation is discovered.

The packet stream should continue to expose at least:

```
tx_id
node_id
seq
region
event
priority
usefulness
stale_after
policy
send
tx_ms
crc or existing integrity field, if already present
```

The goal is not to redesign the packet. The goal is to test whether the existing SD-backed replay workflow remains readable with one additional transmitter identity.

## SD replay convention

The firmware-facing SD schedule file is an all-slot CSV copied to each transmitter SD card as:

```
/schedule.csv
```

Expected schema:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

The SEND-only compact CSVs are not SD replay files and should not be copied to the card as `/schedule.csv`.

For a later schedule-prep milestone, each transmitter should receive its own all-slot SD schedule file, then that file should be copied to that board’s SD card as `/schedule.csv`.

## Parser and analyzer implications

The existing parser should be reviewed before schedule generation, but v3.4 should not modify it unless a clear two-transmitter assumption is found.

The expected parser/analyzer review questions are:

```
Does parse_receiver_log.py accept arbitrary tx_id values beyond TXA and TXB?
Does parse_receiver_log.py group by tx_id and node_id generically?
Does analyze_scheduled_replay_from_manifest.py compare all manifest-listed transmitters or only two hard-coded transmitters?
Does compare_scheduled_runs.py assume two transmitters in scheduled ratio summaries?
Are output tables and JSON summaries able to represent TXA, TXB, and TXC together?
Are malformed-packet and reject summaries independent of transmitter count?
```

The preferred design outcome is to keep the parser and analyzer generic. If hard-coded two-transmitter assumptions exist, they should be addressed in a later schedule-prep or analysis-prep milestone, not hidden inside the physical run.

## Later v3.5 schedule-prep target

The later v3.5-three-transmitter-sd-schedule-prep milestone should produce schedule artifacts only.

Expected files:

```
traces/run030_three_tx_adapter_input.csv

traces/run030_reporting_reporting_schedule_manifest.json

traces/run030_reporting_txa_fixed_all_schedule.csv
traces/run030_reporting_txa_fixed_all_compact.csv

traces/run030_reporting_txb_medium_threshold_schedule.csv
traces/run030_reporting_txb_medium_threshold_compact.csv

traces/run030_reporting_txc_strict_threshold_schedule.csv
traces/run030_reporting_txc_strict_threshold_compact.csv

traces/run030_sd_txa_schedule.csv
traces/run030_sd_txb_schedule.csv
traces/run030_sd_txc_schedule.csv
```

The SD schedule files should be all-slot CSVs and should validate against the SD schedule schema.

The compact files should remain analysis/reference artifacts only.

## Later v3.6 physical-prep target

The later v3.6-three-transmitter-sd-physical-prep milestone should be a physical preparation checkpoint.

Expected startup checks:

```
Confirm TXA physical board label and node ID N01.
Confirm TXB physical board label and node ID N16.
Confirm TXC physical board label and selected node ID.
Confirm each board has a readable microSD card.
Confirm each SD card contains the intended all-slot schedule copied as /schedule.csv.
Confirm no compact SEND-only schedule is copied as /schedule.csv.
Confirm each board prints or otherwise exposes the expected tx_id and node_id on startup.
Confirm each board reports the expected schedule row count.
Confirm each board reports the expected SEND count.
Confirm receiver logging starts before transmitter replay.
Confirm serial monitor settings and log naming conventions.
Confirm battery or USB power arrangement is stable for all boards.
Confirm antenna placement is similar to previous lab runs unless deliberately changed.
```

The physical-prep milestone should stop before collecting the real replay log.

## Later v3.7 physical-replay target

The later v3.7-three-transmitter-sd-physical-replay milestone should collect and parse the first three-transmitter physical replay.

Expected receiver-side raw output:

```
logs/rx_run_030_three_transmitter_sd_replay.csv
```

Expected parsed outputs:

```
logs/parsed_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay_rejects.csv
```

Expected report outputs:

```
reports/run030_schedule_aware_manifest.json
reports/run030_schedule_aware_summary.csv
reports/run030_schedule_aware_summary.json
```

The report should summarize, at minimum:

```
received packets by tx_id and node_id
malformed packet count
observed sequence gaps by tx_id and node_id
scheduled SEND rows by tx_id and node_id
observed packet proportions by tx_id and node_id
scheduled packet proportions by tx_id and node_id
mean delivered usefulness by tx_id and node_id
receiver-side inter-arrival summaries
```

The analysis should avoid claiming exact transmitted-packet counts, confirmed collisions, true latency, energy savings, or network scaling.

## Later v3.8 synthesis target

The later v3.8-three-transmitter-sd-replay-synthesis milestone should compare the three-transmitter physical replay against Run 028 and Run 029.

The synthesis should ask whether the manifest-bound SD replay workflow remained readable after adding one transmitter.

A possible successful outcome would be:

```
Under similar lab conditions, the three-transmitter SD-backed replay preserved readable transmitter identities, zero or low malformed-packet behavior, and receiver-side packet proportions that remained interpretable relative to scheduled SEND proportions.
```

A possible cautious outcome would be:

```
The three-transmitter SD-backed replay remained partially readable, but receiver-side packet proportions or sequence-gap behavior suggested that physical interaction effects became more visible after adding the third transmitter.
```

A possible failure outcome would be:

```
The three-transmitter SD-backed replay did not remain readable enough for schedule-aware analysis, requiring parser, firmware, startup, or physical-layout changes before further transmitter-count increases.
```

All three outcomes are useful.

## Recommended v3.4 decision

For v3.4, the recommended design decision is:

```
Use TXC with the physical node ID confirmed before schedule preparation.
Use N31 as the provisional node ID if no physical label has already been assigned.
Keep the schedule period at 64 rows.
Preserve the existing packet format.
Use TXA as fixed-all 64/64 SEND.
Use TXB as medium-threshold 32/64 SEND.
Use TXC as strict-threshold 16/64 SEND.
Treat v3.4 as design-only.
Defer schedule generation to v3.5.
Defer SD card copying and firmware startup checks to v3.6.
Defer receiver logging and physical replay to v3.7.
Defer synthesis and cross-run interpretation to v3.8.
```

## Milestone summary

v3.4 designs the smallest cautious step from two-transmitter SD-backed replay to three-transmitter SD-backed replay.

It does not claim network scaling.

It does not claim energy savings.

It does not claim collision measurement.

It does not claim LoRaWAN behavior.

It prepares the project to test the next uncertainty: whether the SD-backed, manifest-bound replay workflow remains readable when one additional transmitter is introduced.
