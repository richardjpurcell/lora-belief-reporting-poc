# Run 024--026 Threshold-Family Synthesis

## Purpose

This note consolidates the first three physical scheduled replay runs in the LoRa belief-reporting proof of concept.

Runs 024, 025, and 026 form a small threshold-family experiment. They test whether a usefulness-threshold reporting schedule changes the observed physical received-packet proportion while preserving higher mean delivered usefulness per received packet.

This is a synthesis milestone, not a new physical run.

## Milestone Context

Current branch:

```
exp034-threshold-family-synthesis
```

Planned tag:

```
v1.9-threshold-family-synthesis
```

Relevant prior milestones:

```
v1.0 skipped-slot physical replay
v1.1 schedule-aware analysis
v1.2 manifest-bound replay analysis
v1.3 run-bundle validation
v1.4 multi-run comparison scaffold
v1.5 Run 025 second scheduled replay design
v1.6 Run 025 second scheduled replay
v1.7 Run 026 threshold-variant design
v1.8 Run 026 threshold-variant physical replay
```

## Evidence Ladder

The current evidence path is:

```
reporting schedule
  → firmware schedule header
  → physical skipped-slot LoRa replay
  → receiver log
  → packet-centric parser
  → schedule-aware analysis
  → manifest-bound reproduction
  → bundle validation
  → multi-run comparison
```

The important separation is that the parser remains packet-centric, while the schedule-aware analyzer compares parsed received packets against the schedule that generated the physical transmission opportunities.

## Runs Included

The current threshold-family synthesis includes:

```
Run 024: first skipped-slot physical replay
Run 025: repeated skipped-slot physical replay under similar schedule conditions
Run 026: stricter usefulness-threshold physical replay
```

Runs 024 and 025 use the same Run 022 schedules:

```
TXA/N01: fixed-all schedule, 16/16 SEND rows
TXB/N16: usefulness-threshold schedule, 8/16 SEND rows
```

Run 026 uses a stricter threshold schedule:

```
TXA/N01: fixed-all schedule, 16/16 SEND rows
TXB/N16: usefulness-threshold schedule, 4/16 SEND rows
```

## Summary Table

| Run     | TXA schedule | TXB schedule | TXA received packets | TXB received packets | Observed TXB/TXA ratio | Scheduled TXB/TXA ratio | TXA mean usefulness | TXB mean usefulness |
| ------- | -----------: | -----------: | -------------------: | -------------------: | ---------------------: | ----------------------: | ------------------: | ------------------: |
| Run 024 |   16/16 SEND |    8/16 SEND |                  361 |                  176 |                 0.4875 |                  0.5000 |               0.540 |               0.786 |
| Run 025 |   16/16 SEND |    8/16 SEND |                  368 |                  184 |                 0.5000 |                  0.5000 |               0.539 |               0.785 |
| Run 026 |   16/16 SEND |    4/16 SEND |                  504 |                  127 |                 0.2520 |                  0.2500 |               0.538 |               0.866 |

## Main Observation

Across Runs 024, 025, and 026, the observed TXB/TXA received-packet ratio closely tracks the scheduled TXB/TXA send-fraction ratio.

Runs 024 and 025 used an 8/16 TXB SEND schedule:

```
scheduled TXB/TXA ratio: 0.5000
```

Observed ratios:

```
Run 024: 0.4875
Run 025: 0.5000
```

Run 026 used a stricter 4/16 TXB SEND schedule:

```
scheduled TXB/TXA ratio: 0.2500
```

Observed ratio:

```
Run 026: 0.2520
```

This supports the schedule-aware interpretation that the physical replay is preserving the intended scheduled-skipping pattern under similar lab conditions.

## Delivered Usefulness Observation

In all three runs, the usefulness-threshold stream retained higher mean delivered usefulness per received packet than the fixed-all stream.

Runs 024 and 025:

```
TXA mean usefulness: approximately 0.539--0.540
TXB mean usefulness: approximately 0.785--0.786
```

Run 026:

```
TXA mean usefulness: 0.538
TXB mean usefulness: 0.866
```

Run 026 shows the expected effect of a stricter threshold: TXB sends fewer schedule rows and its mean delivered usefulness per received packet increases.

## Careful Interpretation

The careful interpretation is:

```
Across three physical scheduled replay runs, the observed received-packet proportions are close to the scheduled send-fraction proportions. The usefulness-threshold stream produces fewer received packets when scheduled to skip more slots, while retaining higher mean delivered usefulness per received packet.
```

This supports a bounded threshold-family result:

```
threshold policy
  → scheduled SEND/SKIP proportion
  → physical received-packet proportion
  → delivered usefulness-per-packet profile
```

The result strengthens the repository’s central delivery-versus-usefulness claim: packet delivery count and delivered usefulness are not equivalent.

## What This Shows

The current evidence supports the following claims:

* The firmware can preserve SEND/SKIP schedule rows as physical transmit/silent slots.
* A usefulness-threshold stream can produce fewer physical received packets than a fixed-all stream.
* The observed received-packet ratio can track the scheduled send-fraction ratio under similar lab conditions.
* The usefulness-threshold stream can retain higher mean delivered usefulness per received packet.
* A stricter threshold can further reduce the observed received-packet ratio while increasing mean delivered usefulness.
* The schedule-aware analyzer, manifest-bound reproduction, bundle validator, and multi-run comparison scaffold now support repeated physical replay evidence.

## What This Does Not Show

The current evidence does not show:

* exact transmitted-packet counts;
* confirmed collision counts;
* true transmitter-to-receiver latency;
* LoRaWAN behaviour;
* airtime optimization;
* energy savings;
* live belief-maintenance control;
* operational wildfire relevance;
* scalability to many transmitters.

Missing sequence numbers remain observed sequence gaps only. They should not be interpreted as confirmed collisions.

`recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.

Usefulness and priority remain synthetic metadata at this stage.

## Why This Is a Useful Pause Point

Run 024 established physical skipped-slot replay.

Run 025 showed repeatability under the same schedule family.

Run 026 showed that changing the threshold changes the observed packet proportion in the expected direction.

Together, these runs move the repository from a single proof-of-concept replay toward a small controlled experimental family.

This is a good point to pause and consolidate before adding more hardware complexity.

## Recommended Next Experimental Direction

The next physical schedule condition should likely be a looser usefulness threshold, producing approximately 12/16 TXB SEND rows.

That would create a clearer threshold ladder:

```
TXA fixed-all baseline: 16/16 SEND
TXB loose threshold:   12/16 SEND
TXB medium threshold:   8/16 SEND
TXB strict threshold:   4/16 SEND
```

The current evidence already includes the 8/16 and 4/16 conditions. A 12/16 condition would fill in the upper part of the threshold family.

A later repeat of the 4/16 condition may also be useful, but the immediate scientific value is probably higher from adding a looser threshold point.

## Suggested Next Milestones

Suggested documentation milestone:

```
v1.9-threshold-family-synthesis
```

Suggested next threshold-design milestone:

```
v2.0-run027-loose-threshold-design
```

Suggested next physical replay milestone:

```
v2.1-run027-loose-threshold-replay
```

Suggested comparison milestone:

```
v2.2-threshold-family-comparison-update
```

## Timeline Toward AWSRT Output

AWSRT-derived traces should not be introduced as the next immediate step. The current repository should first finish stabilizing the schedule-family replay workflow.

Recommended order:

```
threshold-family synthesis
  → one additional threshold condition
  → stable threshold-family comparison
  → AWSRT-like demand trace adapter input
  → AWSRT-derived replay trace
  → physical replay of AWSRT-derived schedules
```

The first AWSRT-facing step should be replay-based, not live control.

A good first AWSRT integration target is:

```
AWSRT output or AWSRT-inspired run artifact
  → generic demand-trace schema
  → reporting schedule
  → firmware replay
  → physical LoRa log
  → schedule-aware analysis
```

The important design rule is to keep AWSRT outside the LoRa firmware path. AWSRT should generate or inspire demand records; the LoRa repository should adapt those records into its existing generic demand schema.

## Timeline Toward microSD Replay

microSD replay becomes useful when trace or schedule size starts to exceed what is convenient to compile into firmware headers.

The current compiled-header approach is still acceptable for 16-row schedules, but it will become painful for longer schedules, more nodes, and AWSRT-derived traces.

Recommended order:

```
compiled schedule headers for small schedules
  → microSD schedule replay for two transmitters
  → microSD replay with longer schedules
  → microSD replay with AWSRT-derived demand schedules
  → microSD replay across multiple transmitters
```

The first microSD milestone should not change the research question. It should reproduce an already-known schedule condition from SD card rather than introducing new policy semantics at the same time.

A good first microSD test would be:

```
replay Run 026-style 4/16 schedule from microSD
  and compare against the compiled-header Run 026 result
```

This would isolate the storage/replay mechanism from the reporting-policy result.

## Timeline Toward More Transmitters

Scaling transmitters should come after the two-transmitter schedule pipeline is stable.

Recommended scaling path:

```
2 transmitters: current baseline
  → 3 transmitters: add one more scheduled stream
  → 5 transmitters: small multi-node replay
  → 10 transmitters: load/stress family
  → approximately 30 transmitters: larger lab platform
```

The next scaling step should be 3 or 5 transmitters, not 30.

Before many-transmitter experiments, the repository will need stronger support for:

* node identifier assignment;
* per-transmitter schedule generation;
* per-transmitter firmware or SD-card configuration;
* run-start coordination;
* receiver logging robustness;
* manifest generation for many transmitters;
* comparison summaries across more than two streams;
* cautious language around packet loss, sequence gaps, and collision-like stress.

The comparison scripts currently focus on two transmitters. Multi-transmitter scaling will require extending the analysis model beyond TXA/TXB pairwise ratios.

## Medium-Term Destination

The medium-term destination is a reproducible low-cost physical replay platform for belief-maintenance reporting demand.

The intended path is:

```
AWSRT-inspired or AWSRT-derived demand
  → generic demand records
  → reporting policy schedule
  → physical LoRa replay
  → packet-centric receiver logging
  → schedule-aware analysis
  → manifest-bound validation
  → comparison across policies, thresholds, and physical conditions
```

The longer-term paper direction is not simply “LoRa performance.” It is:

```
delivery versus usefulness in constrained IoT reporting
```

with careful distinctions among:

* demand rows;
* scheduled SEND/SKIP decisions;
* physical transmission opportunities;
* observed packet arrivals;
* delivered usefulness;
* sequence gaps;
* receiver timing;
* reproducible analysis artifacts.

## Recommended Immediate Next Step After This Note

After committing this synthesis note, proceed to a looser-threshold design milestone.

The next design question should be:

```
What threshold produces approximately 12/16 TXB SEND rows from the current 16-row demand trace?
```

That would create the planned loose-threshold condition for Run 027.

Potential next branch:

```
exp035-run027-loose-threshold-design
```

Potential next tag:

```
v2.0-run027-loose-threshold-design
```
