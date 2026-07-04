# Run 032 six-transmitter synthesis

## Purpose

This note synthesizes the validated three-, four-, and six-transmitter SD-backed physical replay progression through Run 032.

The purpose is not to start the next hardware run. The purpose is to turn Run 032 into a scale-up decision point before deciding whether the next cautious hardware step should be a repeated six-transmitter run, an eight-transmitter bridge, or preparation toward twelve transmitters.

## Current confirmed repository state

Current confirmed state at the start of this synthesis milestone:

| Item | State |
| ---- | ----- |
| Branch | `main` |
| Origin | aligned with `origin/main` |
| HEAD | `4daa4b2 Merge Run 032 six-transmitter physical replay` |
| Tag at HEAD | `v4.8-run032-six-transmitter-physical-replay` |
| Working tree | clean |

This synthesis belongs to the planned milestone:

| Item | Value |
| ---- | ----- |
| Branch | `exp067-run032-six-transmitter-synthesis` |
| Intended tag | `v4.9-run032-six-transmitter-synthesis` |
| New note | `docs/development/run032_six_transmitter_synthesis.md` |

## Evidence path so far

The current scale-up path is:

| Step | Run | Main result |
| ---- | --- | ----------- |
| Three-transmitter SD replay | Run 030 | First validated three-transmitter SD-backed replay with receiver-side proportions close to the scheduled SEND ladder. |
| Four-transmitter SD replay | Run 031 | First successful adjusted-position four-transmitter replay, followed by startup-phase validation showing phase/schedule interaction sensitivity. |
| Six-transmitter SD replay | Run 032 | Clean six-transmitter replay with receiver-side proportions close to expected scheduled ratios and full manifest-bundle validation. |

The key interpretation is that the workflow has progressed from a readable three-transmitter replay, to a four-transmitter replay that exposed startup-phase sensitivity, to a clean six-transmitter replay under one physical bench condition.

## Run 030 three-transmitter result

Run 030 moved the SD-backed replay workflow from two transmitters to three.

Schedule design:

| Transmitter | Node | Scheduled SEND rows |
| ----------- | ---: | ------------------: |
| TXA | N01 | 64/64 |
| TXB | N16 | 32/64 |
| TXC | N31 | 16/64 |

Physical replay summary:

| Item | Value |
| ---- | ----: |
| Valid packets | 685 |
| Malformed packets | 1 |

Receiver-side packet counts:

| Transmitter | Node | Received valid packets |
| ----------- | ---: | ---------------------: |
| TXA | N01 | 393 |
| TXB | N16 | 194 |
| TXC | N31 | 98 |

Expected-vs-observed receiver-side ratios:

| Ratio | Observed | Expected | Difference |
| ----- | -------: | -------: | ---------: |
| TXB/TXA | 0.4936 | 0.5000 | -0.0064 |
| TXC/TXA | 0.2494 | 0.2500 | -0.0006 |
| TXC/TXB | 0.5052 | 0.5000 | 0.0052 |

Later validation of the Run 030 N-transmitter replay bundle passed:

| Validation | Result |
| ---------- | ------ |
| Checks passed | 101/101 |
| Checks failed | 0 |

Careful interpretation:

Run 030 established that the SD-backed, manifest-bound replay workflow remained readable when moving from two transmitters to three transmitters under that lab condition. It did not establish larger-scale behavior, exact transmitted-packet counts, confirmed collisions, synchronized latency, LoRaWAN behavior, airtime optimization, energy savings, live-controller behavior, or operational wildfire behavior.

## Run 031 four-transmitter result and startup-phase sensitivity

Run 031 extended the schedule ladder to four transmitters.

Schedule design:

| Transmitter | Node | Scheduled SEND rows |
| ----------- | ---: | ------------------: |
| TXA | N01 | 64/64 |
| TXB | N16 | 32/64 |
| TXC | N31 | 16/64 |
| TXD | N46 | 8/64 |

The successful adjusted-position four-transmitter replay produced:

| Item | Value |
| ---- | ----: |
| Valid packets | 800 |
| Malformed packets / rejects | 0 |
| Validation checks passed | 136/136 |
| Validation checks failed | 0 |

Receiver-side packet counts:

| Transmitter | Node | Received valid packets |
| ----------- | ---: | ---------------------: |
| TXA | N01 | 433 |
| TXB | N16 | 212 |
| TXC | N31 | 102 |
| TXD | N46 | 53 |

Expected-vs-observed receiver-side ratios:

| Ratio | Observed | Expected | Difference |
| ----- | -------: | -------: | ---------: |
| TXB/TXA | 0.4896 | 0.5000 | -0.0104 |
| TXC/TXA | 0.2356 | 0.2500 | -0.0144 |
| TXD/TXA | 0.1224 | 0.1250 | -0.0026 |
| TXC/TXB | 0.4811 | 0.5000 | -0.0189 |
| TXD/TXB | 0.2500 | 0.2500 | 0.0000 |
| TXD/TXC | 0.5196 | 0.5000 | 0.0196 |

However, Run 031 also exposed startup-phase sensitivity.

The later phase-validation milestone tested the same four-transmitter schedule under different programmed startup phase patterns:

| Condition | Phase pattern | Key result |
| --------- | ------------- | ---------- |
| A | TXA first, near-simultaneous baseline | TXD/N46 received 0 packets even though TXA/TXB/TXC remained close to expected ratios. |
| B | TXD first | Full four-transmitter success; TXD/TXA observed 0.1253 against expected 0.1250. |
| C | TXA first, stretched spacing | Not a full four-transmitter success; TXC/N31 nearly disappeared while TXD remained close to expected ratio. |

Careful interpretation:

Run 031 established that a four-transmitter SD-backed replay could produce receiver-side packet proportions close to the scheduled SEND ladder under the successful adjusted-position/phase condition. It also showed that the bench setup is sensitive to programmed startup phase and schedule interaction. That sensitivity should remain part of the scale-up interpretation.

## Run 032 six-transmitter result

Run 032 extended the physical replay from four transmitters to six transmitters.

Schedule design:

| Transmitter | Node | Role | Scheduled SEND rows |
| ----------- | ---: | ---- | ------------------: |
| TXA | N01 | fixed-all anchor | 64/64 |
| TXB | N16 | medium threshold scheduled skipping | 32/64 |
| TXC | N31 | strict threshold scheduled skipping | 16/64 |
| TXD | N46 | very-strict threshold scheduled skipping | 8/64 |
| TXE | N61 | medium threshold scheduled skipping | 32/64 |
| TXF | N76 | strict threshold scheduled skipping | 16/64 |

Physical replay summary:

| Item | Value |
| ---- | ----: |
| Valid packets | 1156 |
| Malformed packets | 0 |
| Validation checks passed | 171/171 |
| Validation checks failed | 0 |

Receiver-side packet counts:

| Transmitter | Node | Received valid packets | Scheduled SEND rows |
| ----------- | ---: | ---------------------: | ------------------: |
| TXA | N01 | 442 | 64/64 |
| TXB | N16 | 220 | 32/64 |
| TXC | N31 | 110 | 16/64 |
| TXD | N46 | 55 | 8/64 |
| TXE | N61 | 219 | 32/64 |
| TXF | N76 | 110 | 16/64 |

Expected-vs-observed receiver-side ratios relative to TXA:

| Ratio | Observed | Expected | Difference |
| ----- | -------: | -------: | ---------: |
| TXB/TXA | 0.4977 | 0.5000 | -0.0023 |
| TXC/TXA | 0.2489 | 0.2500 | -0.0011 |
| TXD/TXA | 0.1244 | 0.1250 | -0.0006 |
| TXE/TXA | 0.4955 | 0.5000 | -0.0045 |
| TXF/TXA | 0.2489 | 0.2500 | -0.0011 |

Observed sequence gaps were not reported for any of the six transmitters in the parsed receiver-side result.

Careful interpretation:

Run 032 is a strong six-transmitter validation point. Under this physical bench run, the prepared six-transmitter SD replay setup produced receiver-side packet proportions closely aligned with the configured scheduled SEND ratios. The run also produced zero malformed packets and passed the N-transmitter manifest-bundle validation.

## Cross-run comparison

| Run | Transmitters | Scheduled SEND ladder | Valid packets | Malformed packets | Receiver-side count summary | Validation |
| --- | ------------: | --------------------- | ------------: | ----------------: | --------------------------- | ---------- |
| Run 030 | 3 | 64, 32, 16 | 685 | 1 | TXA 393; TXB 194; TXC 98 | 101/101 |
| Run 031 | 4 | 64, 32, 16, 8 | 800 | 0 | TXA 433; TXB 212; TXC 102; TXD 53 | 136/136 |
| Run 032 | 6 | 64, 32, 16, 8, 32, 16 | 1156 | 0 | TXA 442; TXB 220; TXC 110; TXD 55; TXE 219; TXF 110 | 171/171 |

Ratio comparison relative to TXA:

| Run | TXB/TXA expected | TXB/TXA observed | TXC/TXA expected | TXC/TXA observed | TXD/TXA expected | TXD/TXA observed | Additional ratios |
| --- | ---------------: | ---------------: | ---------------: | ---------------: | ---------------: | ---------------: | ---------------- |
| Run 030 | 0.5000 | 0.4936 | 0.2500 | 0.2494 | n/a | n/a | TXC/TXB 0.5052 observed vs 0.5000 expected |
| Run 031 | 0.5000 | 0.4896 | 0.2500 | 0.2356 | 0.1250 | 0.1224 | TXD/TXB 0.2500 observed vs 0.2500 expected |
| Run 032 | 0.5000 | 0.4977 | 0.2500 | 0.2489 | 0.1250 | 0.1244 | TXE/TXA 0.4955; TXF/TXA 0.2489 |

## What Run 032 establishes

Run 032 establishes the following bounded claims:

1. The six-transmitter Run 032 replay bundle is internally consistent at the manifest-analysis-validation level.
2. The receiver parser recovered all six intended transmitter/node identities.
3. Receiver-side packet proportions were close to the configured scheduled SEND ratios relative to the TXA fixed-all anchor.
4. The six-transmitter physical replay produced zero malformed packets in this capture.
5. No missing observed transmitted sequences were reported in the parsed receiver-side result.
6. The N-transmitter manifest-bound analysis and validation workflow remains usable beyond the three- and four-transmitter cases.
7. The SD-backed schedule mechanism remains practical for this six-transmitter bench replay.

## What Run 032 does not establish

Run 032 does not establish:

1. exact physical transmitted-packet counts;
2. confirmed RF collisions or confirmed absence of RF collisions;
3. synchronized transmitter-to-receiver latency;
4. LoRaWAN behavior;
5. airtime optimization;
6. energy optimization;
7. live-controller behavior;
8. eight-transmitter behavior;
9. twelve-transmitter behavior;
10. operational wildfire or deployment behavior;
11. general physical robustness across placements, rooms, antenna arrangements, power conditions, or repeated bench sessions.

The result should therefore be described as a validated six-transmitter receiver-side replay result under one physical bench condition, not as a general scaling proof.

## Scale-up decision

Run 032 is strong enough to support a scale-up decision, but it should not be treated as an unqualified twelve-transmitter result.

There are three reasonable next paths.

### Option 1: repeat six transmitters

A repeated six-transmitter run would test repeatability under similar conditions.

Advantages:

* tests whether the clean six-transmitter proportions recur;
* strengthens the six-transmitter validation point;
* provides a useful check before adding more hardware complexity.

Disadvantages:

* does not increase transmitter-count coverage;
* may delay the more informative bridge toward twelve transmitters.

This is the safest next physical replay if the main concern is repeatability.

### Option 2: eight-transmitter bridge

An eight-transmitter bridge is the preferred next scale-up path.

Advantages:

* increases transmitter count without jumping directly to twelve;
* tests whether the six-transmitter phase/schedule strategy remains readable with two additional boards;
* creates a more cautious scaling ladder: 3 -> 4 -> 6 -> 8 -> 12;
* preserves the bounded laboratory proof-of-concept style.

Disadvantages:

* requires design, schedule preparation, physical preparation, and careful replay documentation;
* may expose new phase/schedule interactions that need diagnostic handling.

This is the recommended next hardware direction after the v4.9 synthesis milestone.

### Option 3: prepare directly toward twelve

Direct twelve-transmitter preparation may continue at the design level, but a physical twelve-transmitter replay should not be the next step.

Advantages:

* keeps the long-term platform goal visible;
* can reuse the phase-plan work already started for twelve transmitters.

Disadvantages:

* skips an important intermediate physical bridge;
* risks overinterpreting one clean six-transmitter run;
* makes diagnosis harder if the twelve-transmitter replay behaves poorly.

This should remain a design-track activity for now, not the next physical replay.

## Recommendation

The recommended next path is:

1. Complete this v4.9 synthesis milestone.
2. Use the synthesis to record that Run 032 is a strong six-transmitter validation point, but still one physical bench condition.
3. Do not jump directly to twelve transmitters.
4. Start an eight-transmitter bridge design milestone.
5. Keep twelve-transmitter preparation as a later target after the eight-transmitter bridge has been designed, prepared, physically replayed, analyzed, and synthesized.

Recommended next milestone:

| Milestone | Purpose |
| --------- | ------- |
| `v5.0-run033-eight-transmitter-bridge-design` | Design an eight-transmitter bridge from the validated six-transmitter replay toward the eventual twelve-transmitter platform. |

Likely follow-on sequence:

| Milestone | Purpose |
| --------- | ------- |
| `v5.0-run033-eight-transmitter-bridge-design` | Design only; no schedules copied, no flashing, no receiver logging. |
| `v5.1-run033-eight-transmitter-schedule-prep` | Generate and validate eight-transmitter schedule artifacts. |
| `v5.2-run033-eight-transmitter-physical-prep` | Prepare firmware identities, SD-card mapping, startup offsets, and bench checklist. |
| `v5.3-run033-eight-transmitter-physical-replay` | Run the eight-transmitter physical replay and analyze the receiver log. |
| `v5.4-run033-eight-transmitter-synthesis` | Decide whether to repeat eight, adjust phase strategy, or proceed toward twelve. |

## Final bounded claim

Run 032 supports the following bounded claim:

The Run 032 six-transmitter SD-backed replay produced a clean receiver-side result under one physical bench condition, with six recovered transmitter identities, zero malformed packets, no reported observed sequence gaps, receiver-side packet proportions close to the configured scheduled SEND ratios, and a fully validated N-transmitter replay bundle.

It does not establish twelve-transmitter behavior. It should therefore be used as a scale-up decision point, not as a final scaling claim.
