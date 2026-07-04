# Run 033 eight-transmitter bridge design

## Purpose

This note designs the next cautious hardware step after the Run 032 six-transmitter synthesis.

The purpose of Run 033 is to create an eight-transmitter bridge between the validated six-transmitter bench replay and the eventual twelve-transmitter platform.

This milestone is design-only.

It does not generate schedules, copy SD-card files, flash firmware, run a receiver, collect packets, or make new physical replay claims.

## Current starting point

The repository is starting this design milestone from:

| Item | State |
| ---- | ----- |
| Branch base | `main` |
| Latest tag | `v4.9-run032-six-transmitter-synthesis` |
| Latest milestone | Run 032 six-transmitter synthesis |
| New branch | `exp068-run033-eight-transmitter-bridge-design` |
| Intended milestone | `v5.0-run033-eight-transmitter-bridge-design` |

## Why eight before twelve

Run 032 is a strong six-transmitter validation point, but it remains one physical bench condition.

The validated scale-up ladder so far is:

| Step | Run | Result |
| ---- | --- | ------ |
| Three transmitters | Run 030 | Validated three-transmitter SD-backed replay. |
| Four transmitters | Run 031 | Validated four-transmitter replay, with later startup-phase sensitivity discovered. |
| Six transmitters | Run 032 | Clean six-transmitter replay with close receiver-side proportions and 171/171 validation checks passed. |

The next step should not jump directly to twelve transmitters.

Eight transmitters are a useful bridge because they add hardware density while keeping the diagnostic problem smaller than twelve. If the eight-transmitter run behaves poorly, the result should still be interpretable. If it behaves well, it strengthens the case for later twelve-transmitter preparation.

## Design principle

Run 033 should preserve the bounded laboratory proof-of-concept claim:

delivery count -> usefulness metadata -> scheduled skipping -> SD-backed replay -> N-transmitter manifest-bound analysis -> validated physical scaling ladder.

The eight-transmitter bridge should test whether the six-transmitter schedule and phase strategy remains readable with two additional transmitters.

The result should be interpreted through receiver-side packet proportions and manifest-bound validation, not through claims about exact transmitted counts, collision avoidance, synchronized latency, LoRaWAN behavior, airtime optimization, energy optimization, live-controller behavior, or operational wildfire deployment.

## Candidate transmitter set

Run 033 should extend the Run 032 six-transmitter set with two additional transmitters.

| Transmitter | Node | Candidate role | Candidate scheduled SEND rows |
| ----------- | ---: | -------------- | ----------------------------: |
| TXA | N01 | fixed-all anchor | 64/64 |
| TXB | N16 | medium threshold scheduled skipping | 32/64 |
| TXC | N31 | strict threshold scheduled skipping | 16/64 |
| TXD | N46 | very-strict threshold scheduled skipping | 8/64 |
| TXE | N61 | medium threshold scheduled skipping | 32/64 |
| TXF | N76 | strict threshold scheduled skipping | 16/64 |
| TXG | N91 | very-strict threshold scheduled skipping | 8/64 |
| TXH | N106 | ultra-strict threshold scheduled skipping | 4/64 |

This candidate ladder would give:

| Scheduled SEND rows | Transmitters |
| ------------------: | ------------ |
| 64/64 | TXA |
| 32/64 | TXB, TXE |
| 16/64 | TXC, TXF |
| 8/64 | TXD, TXG |
| 4/64 | TXH |

This design keeps the existing Run 032 structure and adds one additional 8/64 transmitter plus one lower-rate 4/64 transmitter.

## Expected receiver-side ratios

If TXA remains the fixed-all anchor, the expected receiver-side ratios relative to TXA are:

| Ratio | Expected |
| ----- | -------: |
| TXB/TXA | 0.5000 |
| TXC/TXA | 0.2500 |
| TXD/TXA | 0.1250 |
| TXE/TXA | 0.5000 |
| TXF/TXA | 0.2500 |
| TXG/TXA | 0.1250 |
| TXH/TXA | 0.0625 |

These are expected receiver-side proportions under the manifest schedule design. They are not exact transmitted-packet claims.

## Startup-phase design requirement

Run 031 showed that phase/schedule interaction can strongly affect receiver-side outcomes.

Therefore Run 033 should not be treated only as an eight-transmitter count increase. It should also be treated as a phase-sensitive bench design.

The Run 033 physical-preparation milestone should explicitly define:

1. programmed startup order;
2. intended startup offsets;
3. SD-card identity mapping;
4. transmitter placement order;
5. receiver placement;
6. antenna and power conditions;
7. a pre-run checklist;
8. a post-run parser and validation checklist.

This v5.0 design milestone should only record those requirements. It should not yet choose final firmware or SD-card operations.

## Candidate phase strategy

The preferred design direction is to extend the successful Run 032 phase approach cautiously.

Candidate idea:

| Startup order | Transmitter | Scheduled SEND rows |
| ------------- | ----------- | ------------------: |
| 1 | TXA | 64/64 |
| 2 | TXB | 32/64 |
| 3 | TXC | 16/64 |
| 4 | TXD | 8/64 |
| 5 | TXE | 32/64 |
| 6 | TXF | 16/64 |
| 7 | TXG | 8/64 |
| 8 | TXH | 4/64 |

This preserves a readable ordering, but the final phase spacing should be selected in the later physical-preparation milestone.

An alternate strategy would interleave lower-rate and higher-rate nodes to reduce repeated phase interactions among similar scheduled SEND patterns. That should remain a design option if the simple extension is judged too risky.

## Analysis requirements

The Run 033 analysis should produce the same kind of evidence as Run 032:

| Artifact | Purpose |
| -------- | ------- |
| Receiver log | Raw physical replay capture. |
| Parsed receiver CSV | Valid packet rows recovered by transmitter/node. |
| Rejects CSV | Malformed or rejected rows, if any. |
| Summary JSON | Receiver-side packet counts and expected-vs-observed ratios. |
| Summary CSV | Human-readable ratio summary. |
| Validation JSON | Manifest-bound validation checks. |
| Development note | Physical replay interpretation and bounded claim. |

The validation should check:

1. expected transmitters are present;
2. no unexpected transmitters are present;
3. scheduled SEND rows match the manifest;
4. receiver-side ratios are computed relative to TXA;
5. malformed/rejected rows are reported;
6. observed sequence gaps are reported;
7. summary artifacts are internally consistent;
8. validation results are machine-readable.

## Success criteria

Run 033 should be considered successful only if:

1. all eight intended transmitter identities are recovered;
2. the parser produces a clean or explainable receiver-side result;
3. malformed packet counts are reported explicitly;
4. receiver-side ratios are close enough to the scheduled SEND ladder to remain readable;
5. the N-transmitter manifest-bundle validation passes;
6. the development note preserves the bounded bench interpretation.

The result does not need to be perfect to be scientifically useful. A failure or partial failure may still be useful if it identifies a phase/schedule interaction, placement sensitivity, parsing issue, or scale-up boundary.

## Non-goals

Run 033 does not attempt to establish:

1. exact physical transmitted-packet counts;
2. confirmed RF collisions or absence of RF collisions;
3. synchronized latency;
4. LoRaWAN behavior;
5. airtime optimization;
6. energy optimization;
7. live-controller behavior;
8. twelve-transmitter behavior;
9. operational wildfire or deployment behavior.

## Recommended milestone sequence

The recommended v5 sequence is:

| Milestone | Purpose |
| --------- | ------- |
| `v5.0-run033-eight-transmitter-bridge-design` | Design the eight-transmitter bridge only. |
| `v5.1-run033-eight-transmitter-schedule-prep` | Generate and inspect Run 033 schedule artifacts. |
| `v5.2-run033-eight-transmitter-physical-prep` | Prepare identities, SD mapping, startup offsets, and bench checklist. |
| `v5.3-run033-eight-transmitter-physical-replay` | Run the eight-transmitter physical replay and analyze receiver logs. |
| `v5.4-run033-eight-transmitter-synthesis` | Decide whether to repeat eight, adjust phase strategy, or prepare toward twelve. |

## Recommended decision

Proceed with an eight-transmitter bridge before twelve.

The preferred candidate schedule ladder is:

| Transmitter | Node | Scheduled SEND rows |
| ----------- | ---: | ------------------: |
| TXA | N01 | 64/64 |
| TXB | N16 | 32/64 |
| TXC | N31 | 16/64 |
| TXD | N46 | 8/64 |
| TXE | N61 | 32/64 |
| TXF | N76 | 16/64 |
| TXG | N91 | 8/64 |
| TXH | N106 | 4/64 |

The final schedule files, startup offsets, and hardware procedure should be created in later milestones, not in this design milestone.

## Final bounded claim for this milestone

This milestone designs an eight-transmitter bridge from the validated Run 032 six-transmitter result toward the eventual twelve-transmitter platform.

It does not produce new replay evidence. It records the rationale, candidate transmitter ladder, expected receiver-side ratios, phase-sensitivity requirements, analysis requirements, success criteria, and next milestone sequence.
