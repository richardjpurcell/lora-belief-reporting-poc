# Run 032 six-transmitter phase bridge design

## Purpose

This milestone creates a six-transmitter bridge between the four-transmitter Run 031 startup-phase validation and the planned twelve-transmitter Run 032 slot-phase design.

The goal is deliberately modest: test whether the optimized 250 ms-grid phase logic from the twelve-transmitter design remains readable when scaled from four to six transmitters.

This milestone does not flash firmware, prepare hardware, or perform a physical replay. It only creates and analyzes a six-transmitter phase-plan candidate.

## Context

Run 031 showed that receiver-side packet reception is sensitive to programmed startup phase.

The current cautious interpretation is a receiver-side phase/schedule-interaction hypothesis: sparse scheduled transmitters can be poorly received when their replay phase aligns badly with TXA's fixed-all 1 s rhythm.

The Run 031 result should not be overinterpreted as confirmed collisions, exact transmitted-packet counts, synchronized latency, airtime optimization, energy savings, LoRaWAN behavior, live-controller behavior, twelve-transmitter physical behavior, or operational wildfire behavior.

Run 032 then introduced two twelve-transmitter phase-plan diagnostics:

* Conservative one-anchor candidate
* Optimized 250 ms-grid candidate

The optimized 250 ms-grid candidate produced fewer analyzer risk flags and is the preferred twelve-transmitter design candidate. However, it remains a simplified design diagnostic, not a physical validation.

## Bridge rationale

The six-transmitter bridge avoids jumping directly from four physical transmitters to twelve physical transmitters.

The bridge subset is derived from the optimized 250 ms-grid twelve-transmitter candidate and preserves:

* one fixed-all anchor,
* two medium scheduled-skipping transmitters,
* one strict scheduled-skipping transmitter,
* two very-strict scheduled-skipping transmitters.

This keeps the experiment close enough to the four-transmitter setup to remain physically manageable, while adding enough scheduled-skipping diversity to test whether the phase-plan logic remains interpretable at the next scale.

## Selected six-transmitter subset

| Transmitter | Node | Role                                     | Threshold family | Startup offset |
| ----------- | ---: | ---------------------------------------- | ---------------- | -------------: |
| TXD         |  N46 | very-strict threshold scheduled skipping | very_strict      |           0 ms |
| TXA         |  N01 | fixed-all anchor                         | fixed_all        |         500 ms |
| TXB         |  N16 | medium threshold scheduled skipping      | medium           |        2750 ms |
| TXG         |  N91 | very-strict threshold scheduled skipping | very_strict      |        4000 ms |
| TXC         |  N31 | strict threshold scheduled skipping      | strict           |        4250 ms |
| TXE         |  N61 | medium threshold scheduled skipping      | medium           |        7250 ms |

Composition:

| Group                          | Count |
| ------------------------------ | ----: |
| fixed-all anchor               |     1 |
| medium scheduled skipping      |     2 |
| strict scheduled skipping      |     1 |
| very-strict scheduled skipping |     2 |
| total transmitters             |     6 |

## Files

Input source:

* `traces/run032_twelve_tx_phase_plan_optimized_250ms.csv`

Bridge phase plan:

* `traces/run032_six_tx_phase_plan_bridge.csv`

Analyzer outputs:

* `outputs/run032_six_tx_phase_plan_bridge_summary.json`
* `outputs/run032_six_tx_phase_plan_bridge_summary.csv`

Analyzer command:

`python scripts/analyze_phase_plan.py --phase-plan traces/run032_six_tx_phase_plan_bridge.csv --out-json outputs/run032_six_tx_phase_plan_bridge_summary.json --out-csv outputs/run032_six_tx_phase_plan_bridge_summary.csv`

## Analyzer result

The six-transmitter bridge diagnostic produced:

| Diagnostic             | Result |
| ---------------------- | -----: |
| transmitter count      |      6 |
| fixed-all anchor count |      1 |
| risk flags             |      0 |

Residue groups modulo 1000 ms:

| Residue | Transmitters     |
| ------: | ---------------- |
|    0 ms | TXD/N46, TXG/N91 |
|  250 ms | TXC/N31, TXE/N61 |
|  500 ms | TXA/N01          |
|  750 ms | TXB/N16          |

The diagnostic reports no repeated SEND/SEND alignments under the simplified modeled-send-period assumptions and no fixed-anchor modular alignment flags.

## Interpretation

The six-transmitter subset is a suitable bridge candidate.

The result supports moving from the four-transmitter phase-validation milestone toward a six-transmitter preparation milestone, but only cautiously. It shows that the chosen six-transmitter subset is clean under the current phase-plan analyzer. It does not show that six physical boards will behave well at the receiver.

The appropriate next step is to document this bridge plan and, only after review, decide whether to prepare six SD schedules and firmware/hardware assignments.

## Boundaries

This milestone does not claim:

* confirmed collisions,
* exact transmitted-packet counts,
* synchronized latency,
* airtime optimization,
* energy savings,
* LoRaWAN behavior,
* live-controller behavior,
* twelve-transmitter physical behavior,
* operational wildfire behavior.

Use receiver-side packet proportions when comparing physical results.

Use phase/schedule-interaction hypothesis when describing the Run 031 interpretation.

Use reduced physical transmission attempts under scheduled skipping rather than energy savings.

## Next possible step

If this design note is accepted, the next milestone can prepare a six-transmitter physical replay candidate using this bridge plan.

That follow-up should still remain bounded: first prepare schedules and hardware assignments, then inspect diffs, then commit, and only later decide whether to flash boards or run a physical replay.
