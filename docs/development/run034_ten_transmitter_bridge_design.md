# Run 034 ten-transmitter bridge design

## Purpose

Run 034 is proposed as a ten-transmitter bridge between the validated Run 033 eight-transmitter replay and a future twelve-transmitter target.

This is a design-only milestone. It does not generate schedules, modify firmware, flash transmitters, or run a physical replay.

The purpose is to define the next cautious scaling step using the phase-aware replay method frozen in v5.5.

## Rationale

Run 033 successfully advanced the validated physical replay scale point from six to eight transmitters, but it also exposed a startup-phase artifact. Exact repeated scheduled SEND coincidences could suppress sparse scheduled transmitters in the receiver-side packet log under the bench condition.

The v5.5 method freeze therefore made phase-aware startup planning part of the physical replay method.

Run 034 should not simply add transmitters. It should extend the bridge cautiously while applying phase-aware planning from the beginning.

## Proposed ten-transmitter bridge

Run 034 keeps the Run 033 eight-transmitter ladder and adds two transmitters.

| TX | Node | Proposed role | Scheduled SEND rows |
| --- | --- | --- | ---: |
| TXA | N01 | fixed-all anchor | 64/64 |
| TXB | N16 | medium threshold | 32/64 |
| TXC | N31 | strict threshold | 16/64 |
| TXD | N46 | very-strict threshold | 8/64 |
| TXE | N61 | medium threshold | 32/64 |
| TXF | N76 | strict threshold | 16/64 |
| TXG | N91 | very-strict threshold | 8/64 |
| TXH | N106 | ultra-strict threshold | 4/64 |
| TXI | N121 | strict threshold | 16/64 |
| TXJ | N136 | very-strict threshold | 8/64 |

The proposed additions are:

* TXI/N121: strict threshold, 16/64 scheduled SEND rows
* TXJ/N136: very-strict threshold, 8/64 scheduled SEND rows

This adds meaningful physical load and structured SEND opportunities without jumping directly to twelve transmitters.

## Expected ratios relative to TXA

The expected receiver-side ratios relative to the fixed-all TXA anchor are:

| Ratio | Expected |
| --- | ---: |
| TXB/TXA | 0.5000 |
| TXC/TXA | 0.2500 |
| TXD/TXA | 0.1250 |
| TXE/TXA | 0.5000 |
| TXF/TXA | 0.2500 |
| TXG/TXA | 0.1250 |
| TXH/TXA | 0.0625 |
| TXI/TXA | 0.2500 |
| TXJ/TXA | 0.1250 |

These ratios are schedule-defined expectations. They are not exact transmitted-packet counts.

## Phase-aware design requirement

Run 034 must use phase-aware startup planning before any physical replay.

The design requirement is:

> The candidate phase plan should avoid exact same-ms scheduled SEND coincidences among structured scheduled transmitters while preserving the manifest schedules and fixed slot interval.

This requirement comes from the v5.5 phase-aware replay method freeze.

## Candidate startup offset direction

The final Run 033 phase-shifted offset state was:

| TX | Node | Startup offset, ms |
| --- | --- | ---: |
| TXH | N106 | 100 |
| TXD | N46 | 900 |
| TXA | N01 | 1000 |
| TXF | N76 | 2500 |
| TXB | N16 | 3250 |
| TXC | N31 | 4750 |
| TXE | N61 | 7750 |
| TXG | N91 | 9450 |

A candidate Run 034 phase direction is to keep those offsets and add two non-coincident offsets for TXI and TXJ.

Initial candidate offsets for later schedule-prep testing:

| TX | Node | Candidate startup offset, ms | Note |
| --- | --- | ---: | --- |
| TXI | N121 | 5850 | strict threshold addition |
| TXJ | N136 | 10650 | very-strict threshold addition |

These are not frozen firmware values. They are design candidates that must be checked against the actual generated Run 034 schedules before physical preparation.

The schedule-prep milestone must compute exact and near scheduled SEND coincidences using the generated Run 034 schedule CSVs and the candidate offsets.

## Required phase checks

Before Run 034 physical preparation, the project should compute:

* exact same-ms scheduled SEND coincidences
* near scheduled SEND coincidences within at least 150 ms
* per-transmitter scheduled SEND event times
* pairwise repeated overlap patterns
* whether any sparse transmitter has all SEND opportunities aligned with a denser transmitter

The phase check should be preserved as a repository artifact.

A candidate phase plan should not advance to physical preparation if exact same-ms scheduled SEND coincidences remain among structured scheduled transmitters.

## Proposed milestone sequence

The proposed Run 034 milestone sequence is:

| Milestone | Purpose |
| --- | --- |
| v5.6-run034-ten-transmitter-bridge-design | Design the ten-transmitter bridge. |
| v5.7-run034-ten-transmitter-schedule-prep | Generate schedules and manifest for ten transmitters. |
| v5.8-run034-ten-transmitter-phase-plan | Compute and document phase-aware startup offsets. |
| v5.9-run034-ten-transmitter-physical-prep | Prepare firmware identities, SD mapping, and bench plan. |
| v5.10-run034-ten-transmitter-physical-replay | Run and validate the ten-transmitter physical replay. |
| v5.11-run034-ten-transmitter-synthesis | Synthesize the ten-transmitter result and decide whether to proceed to twelve. |

This sequence separates schedule generation from phase planning so that the v5.5 method is applied explicitly.

## Why not jump directly to twelve?

Run 033 was successful, but it also revealed a method requirement. The correct next step is to apply that method at the next bridge scale before trying the full target.

A ten-transmitter bridge has three advantages:

1. It tests phase-aware planning under more physical load than Run 033.
2. It adds new strict and very-strict scheduled transmitters without changing the whole ladder at once.
3. It provides a controlled decision point before twelve transmitters.

If Run 034 is clean, the project can proceed to a twelve-transmitter target design with more confidence.

If Run 034 exposes new phase or receiver-side artifacts, those can be diagnosed before the full twelve-transmitter attempt.

## Interpretation boundaries

This design does not establish:

* ten-transmitter physical replay success
* exact transmitted-packet counts
* confirmed RF collision mechanisms
* absence of collisions
* synchronized latency
* LoRaWAN behavior
* energy savings
* airtime optimization
* live-controller behavior
* twelve-transmitter behavior
* operational wildfire deployment behavior

This design supports:

* a cautious ten-transmitter bridge between eight and twelve transmitters
* phase-aware schedule and startup planning before physical replay
* continued manifest-bound receiver-side validation
* a controlled decision point before the twelve-transmitter target

## Bottom line

Run 034 should be a ten-transmitter bridge, not a direct twelve-transmitter jump.

The design should keep the validated Run 033 A-H ladder, add TXI/N121 and TXJ/N136, and apply phase-aware startup planning before any physical preparation.

The next milestone should generate the Run 034 schedules and manifest, then compute exact and near scheduled SEND coincidences before firmware or bench preparation.
