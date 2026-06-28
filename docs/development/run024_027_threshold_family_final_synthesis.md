# Run 024--027 Threshold-Family Final Synthesis

## Purpose

This note consolidates Runs 024, 025, 026, and 027 as the first complete threshold-family physical replay sequence in the LoRa belief-reporting proof of concept.

The sequence tests whether changing a usefulness-threshold reporting schedule changes the observed physical received-packet proportion in the expected direction while preserving higher mean delivered usefulness per received packet in the threshold-selected stream.

This is a synthesis milestone. It does not introduce a new physical run.

## Branch and Milestone Context

Current branch:

```
exp037-threshold-family-final-synthesis
```

Planned milestone tag:

```
v2.2-threshold-family-final-synthesis
```

Relevant prior milestones:

```
v1.8-run026-threshold-variant-replay
v1.9-threshold-family-synthesis
v2.0-run027-loose-threshold-design
v2.1-run027-loose-threshold-replay
```

## Why This Synthesis Exists

The earlier v1.9 threshold-family synthesis covered Runs 024--026. At that point, the physical evidence included:

```
8/16 medium threshold
4/16 strict threshold
```

Run 027 added the missing loose-threshold point:

```
12/16 loose threshold
```

Together, Runs 024--027 now provide a clearer threshold ladder:

```
TXB loose threshold:   12/16 SEND
TXB medium threshold:   8/16 SEND
TXB strict threshold:   4/16 SEND
```

TXA remains the fixed-all comparison stream:

```
TXA fixed-all baseline: 16/16 SEND
```

## Evidence Ladder

The repository now supports the following physical replay evidence ladder:

```
generic demand trace
  → reporting schedule
  → firmware schedule header
  → physical LoRa replay
  → receiver log
  → packet-centric parser
  → schedule-aware analysis
  → manifest-bound reproduction
  → run-bundle validation
  → multi-run comparison
  → development note and README checkpoint
```

This matters because each run is not only a physical observation; it is also tied to reproducible schedule, parser, summary, manifest, validation, and comparison artifacts.

## Runs Included

The threshold-family sequence includes:

```
Run 024: first skipped-slot physical replay
Run 025: repeated skipped-slot physical replay
Run 026: strict-threshold physical replay
Run 027: loose-threshold physical replay
```

Runs 024 and 025 used the same medium-threshold schedule:

```
TXA/N01: fixed-all schedule, 16/16 SEND rows
TXB/N16: usefulness-threshold schedule, 8/16 SEND rows
```

Run 026 used a stricter threshold schedule:

```
TXA/N01: fixed-all schedule, 16/16 SEND rows
TXB/N16: usefulness-threshold schedule, 4/16 SEND rows
```

Run 027 used a looser threshold schedule:

```
TXA/N01: fixed-all schedule, 16/16 SEND rows
TXB/N16: usefulness-threshold schedule, 12/16 SEND rows
```

## Summary Table

| Run     | TXA schedule | TXB schedule | TXA received packets | TXB received packets | Observed TXB/TXA ratio | Scheduled TXB/TXA ratio | TXA mean usefulness | TXB mean usefulness |
| ------- | -----------: | -----------: | -------------------: | -------------------: | ---------------------: | ----------------------: | ------------------: | ------------------: |
| Run 024 |   16/16 SEND |    8/16 SEND |                  361 |                  176 |                 0.4875 |                  0.5000 |               0.540 |               0.786 |
| Run 025 |   16/16 SEND |    8/16 SEND |                  368 |                  184 |                 0.5000 |                  0.5000 |               0.539 |               0.785 |
| Run 026 |   16/16 SEND |    4/16 SEND |                  504 |                  127 |                 0.2520 |                  0.2500 |               0.538 |               0.866 |
| Run 027 |   16/16 SEND |   12/16 SEND |                  400 |                  299 |                 0.7475 |                  0.7500 |               0.539 |               0.667 |

## Threshold Ladder

The physical threshold-family ladder is now:

```
12/16 loose threshold  → observed ratio 0.7475; TXB mean usefulness 0.667
 8/16 medium threshold → observed ratio 0.4875 and 0.5000; TXB mean usefulness approximately 0.785
 4/16 strict threshold → observed ratio 0.2520; TXB mean usefulness 0.866
```

This is the clearest result family in the repository so far.

The schedule-aware relationship is:

```
scheduled TXB/TXA ratio 0.7500 → observed ratio 0.7475
scheduled TXB/TXA ratio 0.5000 → observed ratio 0.4875 and 0.5000
scheduled TXB/TXA ratio 0.2500 → observed ratio 0.2520
```

The usefulness relationship is:

```
loose threshold:   TXB mean usefulness 0.667
medium threshold:  TXB mean usefulness approximately 0.785
strict threshold:  TXB mean usefulness 0.866
```

This is consistent with the expected threshold tradeoff:

```
looser threshold:
  more TXB received packets
  lower TXB mean usefulness

stricter threshold:
  fewer TXB received packets
  higher TXB mean usefulness
```

## Main Finding

Across Runs 024--027, the observed TXB/TXA received-packet ratio closely tracks the scheduled TXB/TXA send-fraction ratio.

At the same time, the threshold-selected TXB stream retains higher mean delivered usefulness per received packet than the fixed-all TXA stream.

Careful statement:

```
Runs 024--027 support a bounded threshold-family interpretation: changing the usefulness-threshold schedule changes the observed received-packet proportion in the expected direction, while the threshold-selected stream preserves higher mean delivered usefulness per received packet than the fixed-all stream.
```

## What Is Stronger After Run 027

Run 027 strengthens the threshold-family evidence in four ways.

First, it fills the loose-threshold point. Before Run 027, the threshold family had medium and strict conditions. Run 027 adds the 12/16 condition, completing a simple 12/8/4 ladder.

Second, it shows the expected received-packet proportion. TXB scheduled 12 SEND rows out of 16 and produced an observed TXB/TXA received-packet ratio of 0.7475, close to the scheduled ratio of 0.7500.

Third, it preserves the usefulness separation. TXB mean delivered usefulness was 0.667, above TXA mean delivered usefulness of 0.539.

Fourth, it improves the evidence sequence. Runs 024--027 now show a monotonic usefulness pattern across the threshold stream:

```
loose threshold:   0.667
medium threshold:  approximately 0.785
strict threshold:  0.866
```

## What This Shows

The current evidence supports the following bounded claims:

* The firmware can preserve scheduled SEND/SKIP rows as physical transmit/silent slots.
* A usefulness-threshold stream can produce fewer received packets than a fixed-all stream.
* The observed received-packet ratio can closely track the scheduled send-fraction ratio under similar lab conditions.
* Looser thresholds produce more received packets and lower mean delivered usefulness in the threshold stream.
* Stricter thresholds produce fewer received packets and higher mean delivered usefulness in the threshold stream.
* The threshold-selected stream can retain higher mean delivered usefulness per received packet than the fixed-all stream.
* The schedule-aware analyzer, manifest-bound reproduction, bundle validator, and multi-run comparison scripts now support a small physical replay result family.

## What This Does Not Show

The current evidence does not show:

* exact transmitted-packet counts;
* confirmed collision counts;
* true transmitter-to-receiver latency;
* LoRaWAN behavior;
* airtime optimization;
* energy savings;
* live belief-maintenance control;
* operational wildfire relevance;
* scalability to 12 transmitters;
* performance under many-transmitter contention.

Missing sequence numbers remain observed sequence gaps only. They should not be interpreted as confirmed collisions.

`recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.

Usefulness and priority remain synthetic metadata at this stage.

## Interpretation Boundaries

Preserve the following wording discipline:

* Say “point-to-point LoRa,” not LoRaWAN.
* Say “scheduled skipping,” not airtime optimization.
* Say “observed sequence gaps,” not collisions.
* Say “received-packet ratio,” not exact transmitted-packet ratio.
* Say “receiver-observed inter-arrival,” not latency.
* Say “synthetic usefulness metadata,” not live belief value.
* Say “bounded physical replay evidence,” not operational system validation.

## Why This Is a Good Phase Boundary

Runs 024--027 are enough to mark the first threshold-family phase as complete for now.

The repository now has:

```
medium-threshold repeat evidence
strict-threshold variant evidence
loose-threshold variant evidence
manifest-bound replay summaries
bundle validation
multi-run comparison
README and development-note documentation
```

Additional repetitions may still be useful later, but the immediate educational and research value is now higher in moving to the next mechanism rather than adding another two-transmitter threshold run.

## Recommended Next Direction

The next recommended direction is microSD-backed replay design.

Reason:

```
The compiled-header approach is acceptable for 16-row schedules and two transmitters, but it will become cumbersome for longer schedules, AWSRT-derived traces, and the planned 12-transmitter platform.
```

The next milestone should therefore be a design milestone, not an immediate physical stress test.

Suggested next branch:

```
exp038-microsd-replay-design
```

Suggested next tag:

```
v2.3-microsd-replay-design
```

Suggested design note:

```
docs/development/microsd_replay_design.md
```

The first microSD target should be conservative:

```
reproduce an already-known two-transmitter schedule from microSD
```

A good first candidate is Run 027, because it is the newest and cleanest full loose-threshold replay. The microSD test should first reproduce a known schedule rather than introduce new AWSRT traces, more transmitters, or live controller behavior at the same time.

## Medium-Term Path

A reasonable staged path from here is:

```
v2.2 threshold-family final synthesis
  → v2.3 microSD replay design
  → v2.4 two-transmitter microSD replay
  → v2.5 AWSRT-derived demand-trace adapter design
  → v2.6 AWSRT-derived two-transmitter replay
  → v2.7 three-transmitter replay design
  → later 5/6 transmitter replay
  → later 12-transmitter replay platform
```

The current hardware planning target is:

```
12 active transmitters
2 spare boards
```

The repository should continue to stabilize storage, replay, logging, manifest, and validation mechanisms before increasing transmitter count.

## Planned Commit

Files expected for this synthesis milestone:

```
docs/development/run024_027_threshold_family_final_synthesis.md
README.md
```

Suggested commit:

```
git add docs/development/run024_027_threshold_family_final_synthesis.md
git add README.md
git commit -m "Synthesize completed threshold-family replay results"
```

Suggested tag:

```
git tag -a v2.2-threshold-family-final-synthesis \
    -m "v2.2 threshold-family final synthesis"
```

Suggested push:

```
git push origin exp037-threshold-family-final-synthesis
git push origin v2.2-threshold-family-final-synthesis
```
