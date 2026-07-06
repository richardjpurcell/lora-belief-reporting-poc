# Run 035 twelve-transmitter cautious bridge design

## Purpose

Run 035 is proposed as a cautious twelve-transmitter bridge design following the successful Run 034 ten-transmitter SD-backed scheduled physical replay.

This is a design-only milestone. It does not generate schedules, modify firmware, prepare SD cards, flash transmitters, or run a physical replay.

The purpose is to define the next staged scaling step while preserving the phase-aware, manifest-bound method that made Run 034 interpretable.

## Starting point

Run 034 succeeded as a ten-transmitter bridge under bounded bench conditions.

The key evidence from Run 034 was:

* all ten expected transmitters were present in the receiver-side log;
* TXI/N121 and TXJ/N136 were successfully added;
* sparse TXH/N106 remained visible;
* receiver-side packet proportions followed the scheduled SEND ladder closely;
* manifest-bound validation passed 271/271 checks;
* the Run 034 phase-aware startup plan was sufficient for the candidate replay;
* one-card-at-a-time SD preparation worked as the practical bench workflow.

The correct interpretation is not that twelve transmitters will automatically work.

The correct interpretation is:

> Run 034 succeeded as a ten-transmitter bridge, so the project can now begin cautious twelve-transmitter bridge design using the same staged, phase-aware, manifest-bound method.

## Design boundary

Run 035 v5.12 is design-only.

It should not:

* create twelve-transmitter schedules;
* create TXK or TXL firmware;
* prepare SD cards;
* rename SD-card volumes;
* create physical-prep scripts;
* flash devices;
* run a physical replay;
* claim twelve-transmitter success.

Those steps belong to later milestones after schedule preparation and phase-plan analysis.

## Proposed twelve-transmitter bridge

Run 035 should keep the Run 034 A-J set and add two candidate transmitters:

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
| TXK | N151 | medium threshold | 32/64 |
| TXL | N166 | ultra-strict threshold | 4/64 |

The proposed additions are:

* TXK/N151: medium threshold, 32/64 scheduled SEND rows
* TXL/N166: ultra-strict threshold, 4/64 scheduled SEND rows

This choice deliberately adds one denser scheduled transmitter and one sparse scheduled transmitter.

TXK tests whether the ten-transmitter result can tolerate another medium-rate participant.

TXL tests whether a second ultra-sparse participant can remain visible when twelve physical devices are active.

## Why TXK should be medium threshold

TXK should use the medium threshold role for three reasons.

First, the Run 034 ladder already contains repeated medium, strict, and very-strict roles, but only two medium transmitters: TXB/N16 and TXE/N61.

Second, adding a medium transmitter increases physical replay load without making the new transmitter so sparse that absence would be hard to diagnose.

Third, the 32/64 schedule gives enough receiver-side packet opportunities to support meaningful manifest-relative ratio checking.

Expected TXK/TXA ratio:

| Ratio | Expected |
| --- | ---: |
| TXK/TXA | 0.5000 |

## Why TXL should be ultra-strict threshold

TXL should use the ultra-strict role for three reasons.

First, Run 034 showed that sparse TXH/N106 remained visible after phase-aware preparation.

Second, adding a second ultra-sparse transmitter creates a stricter bridge test than simply adding another medium or strict transmitter.

Third, a second 4/64 role directly tests whether sparse scheduled participants remain interpretable in the receiver-side log under twelve-device bench conditions.

Expected TXL/TXA ratio:

| Ratio | Expected |
| --- | ---: |
| TXL/TXA | 0.0625 |

## Expected ratios relative to TXA

The expected receiver-side ratios relative to the fixed-all TXA anchor are schedule-defined:

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
| TXK/TXA | 0.5000 |
| TXL/TXA | 0.0625 |

These are scheduled expectations. They are not exact transmitted-packet counts.

## Required staged method

Run 035 should preserve the staged method:

1. bridge design;
2. schedule preparation;
3. phase-plan analysis;
4. physical preparation;
5. physical replay;
6. synthesis.

This separation is now mandatory for larger physical replay work.

The twelve-transmitter case should not move directly from design to bench execution.

## Deterministic startup offsets are mandatory

Before any Run 035 physical preparation, the project must compute deterministic startup offsets for all twelve transmitters.

The phase-plan milestone must inspect the generated twelve-transmitter schedules and candidate offsets together.

The goal is not to prove that collisions are absent. The goal is to avoid known schedule/startup artifacts that can make sparse scheduled transmitters disappear from the receiver-side log.

## Required SEND coincidence checks

Before physical preparation, the phase-plan milestone must compute and preserve:

* exact same-ms scheduled SEND coincidences;
* near scheduled SEND coincidences within at least 150 ms;
* per-transmitter scheduled SEND event times;
* pairwise repeated overlap patterns;
* whether any sparse transmitter has all SEND opportunities aligned with a denser transmitter;
* whether the two ultra-strict transmitters, TXH and TXL, have distinguishable scheduled SEND opportunities;
* whether the candidate plan introduces new repeated coincidences involving TXK or TXL.

A candidate twelve-transmitter phase plan should not advance to physical preparation if exact same-ms scheduled SEND coincidences remain among structured scheduled transmitters.

Near coincidences should be documented rather than overinterpreted. They are planning diagnostics, not proof of RF-layer mechanisms.

## Candidate startup offset direction

The Run 034 phase-aware startup plan should be treated as the starting point, not as a frozen twelve-transmitter plan.

Run 035 should begin by carrying forward the A-J offsets and then searching for non-coincident candidate offsets for TXK and TXL.

Any TXK/TXL offsets proposed during schedule preparation are provisional until checked against the generated Run 035 schedule CSVs.

The phase-plan milestone should produce repository artifacts comparable to the Run 034 phase-plan outputs:

* exact coincidence table;
* near coincidence table;
* phase-plan summary JSON;
* design note or phase-plan note explaining the selected offsets.

## Future firmware and SD-card requirements

Because Run 035 adds two new physical devices, later physical-prep milestones will need to create TXK and TXL firmware sketches.

The firmware should use the same underscore naming convention already used for TXA through TXJ:

| TX | Firmware directory | Sketch file |
| --- | --- | --- |
| TXK | `firmware/first_radio_link_TX_K/` | `first_radio_link_TX_K.ino` |
| TXL | `firmware/first_radio_link_TX_L/` | `first_radio_link_TX_L.ino` |

The internal serial-print labels, TX identifiers, node identifiers, and schedule filenames must be adjusted for TXK/N151 and TXL/N166.

Later physical preparation will also require two additional SD cards.

Those cards should be renamed from the default `NO NAME` volume label to appropriate TX-specific labels before use. The exact volume-label convention should be decided during physical preparation, but the goal is to reduce ambiguity during one-card-at-a-time copying and bench setup.

These firmware and SD-card tasks are not part of v5.12. They belong to the physical-prep milestone after schedule generation and phase-plan analysis.

## Proposed milestone sequence

The proposed Run 035 milestone sequence is:

| Milestone | Purpose |
| --- | --- |
| `v5.12-run035-twelve-transmitter-cautious-bridge-design` | Design the twelve-transmitter bridge only. |
| `v5.13-run035-twelve-transmitter-schedule-prep` | Generate and inspect twelve-transmitter schedules and manifest. |
| `v5.14-run035-twelve-transmitter-phase-plan` | Compute deterministic startup offsets and exact/near scheduled SEND coincidence checks. |
| `v5.15-run035-twelve-transmitter-physical-prep` | Prepare firmware identities, TXK/TXL sketches, SD-card workflow, card labels, and bench plan. |
| `v5.16-run035-twelve-transmitter-physical-replay` | Attempt the twelve-transmitter physical replay and analyze receiver logs. |
| `v5.17-run035-twelve-transmitter-synthesis` | Synthesize the twelve-transmitter result and decide the next direction. |

## Advancement criteria from v5.12

This design milestone is complete when the repository contains a bounded Run 035 twelve-transmitter bridge design that:

* preserves Run 034 as the evidence base;
* defines TXK/N151 and TXL/N166 candidate identities;
* assigns TXK and TXL schedule roles;
* explains why twelve-transmitter work must remain staged;
* requires deterministic startup offsets before physical prep;
* requires exact and near scheduled SEND coincidence checks before physical prep;
* records future TXK/TXL firmware and SD-card obligations without performing them yet;
* preserves interpretation boundaries.

## Interpretation boundaries

This design does not establish:

* twelve-transmitter physical replay success;
* exact transmitted-packet counts;
* confirmed RF collision mechanisms;
* absence of collisions;
* synchronized latency;
* LoRaWAN behavior;
* energy savings;
* airtime optimization;
* live-controller behavior;
* arbitrary-layout twelve-node behavior;
* operational wildfire deployment behavior.

This design supports:

* cautious twelve-transmitter bridge planning;
* preservation of the staged method;
* manifest-relative schedule expectations;
* phase-aware planning before physical preparation;
* explicit handling of new-device firmware and SD-card requirements in later milestones.

## Bottom line

Run 035 should begin as a twelve-transmitter cautious bridge design, not as a twelve-transmitter physical replay attempt.

The design should keep the validated Run 034 A-J set, add TXK/N151 and TXL/N166 as candidate devices, assign TXK a medium threshold role and TXL an ultra-strict threshold role, and require deterministic phase-plan analysis before any firmware, SD-card, or bench preparation work.
