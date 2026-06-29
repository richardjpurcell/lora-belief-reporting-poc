# Three-transmitter SD replay synthesis

Milestone: v3.8-three-transmitter-sd-replay-synthesis
Branch: exp053-three-transmitter-sd-replay-synthesis
Status: Synthesis milestone

## 1. Purpose

This note synthesizes the first three-transmitter microSD-backed replay phase in the LoRa belief-reporting proof of concept.

It follows the milestone sequence:

```
v3.4-three-transmitter-sd-replay-design
v3.5-three-transmitter-sd-schedule-prep
v3.6-three-transmitter-sd-physical-prep
v3.7-three-transmitter-sd-physical-replay
```

The core question for this phase was:

```
Can the SD-backed, manifest-bound replay workflow remain readable when we move from two transmitters to three transmitters?
```

The short answer from Run 030 is:

```
Yes, under this bench condition.
```

Run 030 does not prove general network scaling. It supports a bounded workflow-readability claim.

## 2. Prior SD-backed replay basis

Before the three-transmitter phase, the project had two successful two-transmitter SD-backed replay checkpoints.

Run 028 established the first successful 16-row microSD-backed physical replay:

```
TXA/N01: 16/16 SEND, 378 received packets, mean usefulness 0.539
TXB/N16: 12/16 SEND, 284 received packets, mean usefulness 0.668

Scheduled TXB/TXA ratio: 0.7500
Observed TXB/TXA ratio: 0.7513
Malformed packets: 0
```

Run 029 extended the SD-backed replay path to a 64-row schedule:

```
TXA/N01: 64/64 SEND, 478 received packets, mean usefulness 0.526
TXB/N16: 32/64 SEND, 241 received packets, mean usefulness 0.810

Scheduled TXB/TXA ratio: 0.5000
Observed TXB/TXA ratio: 0.5042
Malformed packets: 0
```

The careful synthesis after Run 029 was:

```
Under similar two-transmitter lab conditions, microSD-backed all-slot schedule replay preserved the expected scheduled-skipping received-packet proportions for both a 16-row loose-threshold condition and a 64-row medium-threshold condition, while the threshold-selected stream retained higher mean delivered usefulness per received packet than the fixed-all stream.
```

The interpretation boundary was that this was a storage-and-replay result, not a network-scaling result.

## 3. Three-transmitter design target

The Run 030 design added the smallest practical third-transmitter step.

The intended schedule design was:

```
TXA/N01: fixed-all baseline, 64/64 SEND
TXB/N16: medium threshold, 32/64 SEND
TXC/N31: strict threshold, 16/64 SEND
```

Expected scheduled SEND proportions were:

```
TXB/TXA = 32/64 = 0.5000
TXC/TXA = 16/64 = 0.2500
TXC/TXB = 16/32 = 0.5000
```

The schedule period remained 64 rows.

The packet format was preserved.

The SD replay convention remained:

```
each transmitter SD card receives an all-slot schedule copied as /schedule.csv
```

The compact SEND-only CSVs remained analysis/reference artifacts and were not copied to SD cards.

## 4. Schedule preparation result

The v3.5 schedule-preparation milestone produced a manifest-bound set of three SD-facing schedules:

```
traces/run030_sd_txa_schedule.csv
traces/run030_sd_txb_schedule.csv
traces/run030_sd_txc_schedule.csv
```

Each validated successfully:

```
TXA/N01: 64 rows, 64 SEND, 0 SKIP
TXB/N16: 64 rows, 32 SEND, 32 SKIP
TXC/N31: 64 rows, 16 SEND, 48 SKIP
```

The generated SD-facing files used the firmware-facing schedule schema:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

A practical validation issue was found and corrected during schedule preparation: the firmware-facing `policy` field must be a single-character code.

Run 030 used:

```
F for TXA fixed-all rows
U for TXB usefulness-threshold rows
U for TXC usefulness-threshold rows
```

The manifest and documentation preserved the human-readable policy meanings.

## 5. Physical preparation result

The v3.6 physical-preparation milestone added the missing TXC firmware configuration:

```
firmware/first_radio_link_TX_C/
```

TXC identity was set to:

```
TX_ID = "TXC"
NODE_ID = "N31"
```

The TXC firmware reused the same SD replay behavior as TXA and TXB.

The intended SD-card mapping was:

```
TXA/N01 -> traces/run030_sd_txa_schedule.csv copied as /schedule.csv
TXB/N16 -> traces/run030_sd_txb_schedule.csv copied as /schedule.csv
TXC/N31 -> traces/run030_sd_txc_schedule.csv copied as /schedule.csv
```

During physical preparation, the third SD card was renamed:

```
LORA_TXC
```

The final SD volume labels used were:

```
LORA_TXA
LORA_TXB
LORA_TXC
```

Each card was checked with:

```
ls -l
head -5
wc -l
```

Each card contained a `/schedule.csv` file with 65 lines: one header plus 64 schedule rows.

## 6. Startup offset condition

During preparation for Run 030, a practical bench observation was carried forward:

```
the receiver behaves better when transmitter starts are staggered
```

The Run 030 firmware condition used:

```
TXA: RUN_ID=R30, no startup offset
TXB: RUN_ID=R30, STARTUP_OFFSET_MS=500
TXC: RUN_ID=R30, STARTUP_OFFSET_MS=750
```

TXC was intentionally changed from a copied 500 ms startup offset to a 750 ms startup offset so that TXB and TXC would not share the same start offset.

This offset condition should be treated as part of the Run 030 bench setup.

It should not be generalized as an optimized timing scheme.

## 7. Startup verification result

Before receiver logging, all three boards were verified through serial startup output.

TXA startup confirmed:

```
tx_id=TXA
node_id=N01
rows_loaded=64
send_rows=64
skip_rows=0
replay_period_rows=64
packet_format=existing
```

TXB startup confirmed:

```
tx_id=TXB
node_id=N16
rows_loaded=64
send_rows=32
skip_rows=32
replay_period_rows=64
packet_format=existing
```

TXC startup confirmed:

```
tx_id=TXC
node_id=N31
rows_loaded=64
send_rows=16
skip_rows=48
replay_period_rows=64
packet_format=existing
```

This confirmed that all three boards read the intended `/schedule.csv` files before the receiver-side physical replay.

## 8. Run 030 receiver-side result

Run 030 produced:

```
logs/rx_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay.csv
logs/parsed_run_030_three_transmitter_sd_replay_rejects.csv
```

The parser summary was:

```
Valid packets:      685
Malformed packets:  1
```

Packets by transmitter and node:

```
TXA/N01: 393
TXB/N16: 194
TXC/N31:  98
```

Missing observed sequence numbers:

```
TXA/N01: missing 1 -> [78]
TXB/N16: missing 3 -> [10, 12, 89]
TXC/N31: none
```

The parser accepted TXC/N31 cleanly as a third transmitter identity.

The receiver-side stream was readable across all three transmitters.

The single malformed packet was documented in the rejects file. It did not prevent the run from being readable.

## 9. Observed versus scheduled proportions

Run 030 scheduled SEND ratios:

```
TXB/TXA = 0.5000
TXC/TXA = 0.2500
TXC/TXB = 0.5000
```

Run 030 observed receiver-side packet ratios:

```
TXB/TXA = 194 / 393 = 0.4936
TXC/TXA =  98 / 393 = 0.2494
TXC/TXB =  98 / 194 = 0.5052
```

The observed receiver-side packet proportions were close to the scheduled SEND proportions.

This supports the careful interpretation that the scheduled-skipping structure remained visible after adding a third transmitter.

This does not imply exact transmitted-packet counts or confirmed collision behavior.

## 10. Usefulness preservation

Run 030 preserved the intended mean-usefulness ordering:

```
TXA/N01: mean usefulness 0.524
TXB/N16: mean usefulness 0.810
TXC/N31: mean usefulness 0.870
```

This ordering is consistent with the schedule design:

```
fixed-all baseline < medium threshold < strict threshold
```

Total usefulness by node was:

```
TXA/N01: 205.80
TXB/N16: 157.14
TXC/N31:  85.26
```

Mean priority by node was:

```
TXA/N01: 0.549
TXB/N16: 0.840
TXC/N31: 0.900
```

The usefulness and priority values remain synthetic metadata.

The meaningful result is not that one transmitter is universally better than another. The result is that the physical receiver/parser recovered the intended schedule-conditioned metadata pattern across three transmitter streams.

## 11. Receiver inter-arrival observations

Approximate receiver inter-arrival times by node were:

```
TXA/N01: mean 1.003 s, min 0.999 s, max 2.000 s
TXB/N16: mean 2.031 s, min 1.999 s, max 4.000 s
TXC/N31: mean 3.979 s, min 2.000 s, max 6.005 s
```

These are consistent with the schedule structure:

```
TXA sends every slot
TXB sends approximately every second slot
TXC sends less frequently under the strict threshold schedule
```

These are receiver-side observations only.

They are not synchronized latency measurements.

## 12. Comparison across SD-backed replay milestones

| Run     | Transmitters | Schedule length | Scheduled condition             | Observed result                                                           | Malformed packets |
| ------- | ------------ | --------------: | ------------------------------- | ------------------------------------------------------------------------- | ----------------: |
| Run 028 | 2            |         16 rows | TXA 16/16, TXB 12/16            | TXB/TXA observed 0.7513 vs scheduled 0.7500                               |                 0 |
| Run 029 | 2            |         64 rows | TXA 64/64, TXB 32/64            | TXB/TXA observed 0.5042 vs scheduled 0.5000                               |                 0 |
| Run 030 | 3            |         64 rows | TXA 64/64, TXB 32/64, TXC 16/64 | TXB/TXA observed 0.4936, TXC/TXA observed 0.2494, TXC/TXB observed 0.5052 |                 1 |

Across these SD-backed replay milestones, the receiver-side packet proportions remained close to the scheduled SEND proportions under similar bench conditions.

Run 030 extends this pattern from two transmitters to three transmitters.

The correct interpretation is workflow readability under a bounded bench condition, not general wireless-network scaling.

## 13. Main synthesis

Run 030 supports the following bounded claim:

```
The SD-backed, manifest-bound replay workflow remained readable when moving from two transmitters to three transmitters under this lab condition.
```

The basis for this claim is:

```
all three transmitter identities were recovered by the receiver/parser
TXC/N31 was accepted cleanly as a third transmitter identity
observed receiver-side packet proportions were close to scheduled SEND proportions
the intended usefulness ordering was preserved
receiver-side inter-arrival summaries were consistent with schedule structure
only one malformed raw packet was observed across 685 valid packets
```

This is a meaningful next step beyond the two-transmitter SD replay phase.

It tests the next uncertainty identified after Run 029: small multi-transmitter physical interaction, rather than basic SD schedule storage.

## 14. What Run 030 does not establish

Run 030 does not establish:

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

The following cautions remain active:

```
This is point-to-point LoRa at 915 MHz, not LoRaWAN.
The schedule CSVs define one repeated schedule period.
The analysis compares schedule proportions and observed packet proportions.
The analysis does not infer exact transmitted-packet counts.
Missing sequence numbers are observed sequence gaps only, not confirmed collisions.
recv_ms and tx_ms are not synchronized across boards and are not true latency.
Receiver inter-arrival summaries are receiver-side observations only.
Usefulness and priority are synthetic metadata.
The run does not yet use a live belief-maintenance controller.
Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
Do not claim energy savings unless current or power measurements are added.
Do not overgeneralize from this three-transmitter lab run.
```

## 15. Recommended next direction

The project should not jump directly from this single three-transmitter run to a 12-transmitter claim.

The next good choices are:

```
Option A: repeat the three-transmitter Run 030 condition to check repeatability
Option B: add a three-transmitter analysis generalization milestone
Option C: design a four-transmitter or five-transmitter cautious next step
Option D: improve startup-offset documentation and possibly make offsets configurable
```

The recommended immediate next step is Option B:

```
add a three-transmitter analysis generalization milestone
```

The reason is that the parser handled TXC cleanly, but some existing schedule-aware analysis and validation tools were originally shaped around TXA/TXB pairwise comparisons. Before scaling further, the analysis layer should become explicitly multi-transmitter-aware.

A possible next milestone is:

```
v3.9-multi-transmitter-schedule-analysis-design
```

or, if continuing the Run 030 thread:

```
v3.9-three-transmitter-analysis-generalization
```

The next analysis milestone should avoid physical hardware changes and should focus on making the manifest-bound analysis able to report arbitrary transmitter sets cleanly.

## 16. Final statement

The three-transmitter SD replay phase achieved its intended bounded goal.

Run 030 shows that the SD-backed, manifest-bound replay workflow can remain readable after adding a third transmitter under this lab condition.

The result is strong enough to justify the next analysis-infrastructure step.

It is not yet a scaling result.
