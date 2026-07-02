# Run 032 twelve-transmitter slot-phase design

## Status

Design note.

This note starts the next design step after `v4.4-run031-startup-phase-validation`.

The goal is to design a startup-phase and slot-phasing strategy that can plausibly support a future twelve-transmitter SD-backed replay experiment without immediately jumping to a twelve-board physical replay.

## Milestone intent

Proposed milestone:

* `v4.5-twelve-transmitter-slot-phase-design`

This milestone is a design and analysis milestone only.

It does not flash twelve transmitters.

It does not run a twelve-transmitter physical replay.

It does not establish twelve-transmitter behavior.

It does not claim airtime optimization.

It does not confirm collisions.

It does not infer exact transmitted-packet counts.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish energy savings.

It does not use a live belief-maintenance controller.

It does not evaluate operational wildfire behavior.

## Motivation from Run 031 v4.4

Run 031 v4.4 showed that receiver-side packet proportions in the four-transmitter setup were strongly affected by programmed startup phase.

The key A/B/C result was:

* Condition A: baseline programmed phase

  * TXA/N01: 0 ms
  * TXB/N16: 500 ms
  * TXC/N31: 750 ms
  * TXD/N46: 1000 ms
  * TXD/N46 received packets: 0

* Condition B: TXD-first programmed phase

  * TXD/N46: 0 ms
  * TXA/N01: 500 ms
  * TXB/N16: 750 ms
  * TXC/N31: 1000 ms
  * TXD/N46 received packets: 50
  * TXD/TXA observed ratio: 0.1253
  * TXD/TXA expected ratio: 0.1250

* Condition C: TXA-first stretched programmed phase

  * TXA/N01: 0 ms
  * TXB/N16: 500 ms
  * TXC/N31: 1000 ms
  * TXD/N46: 1500 ms
  * TXC/N31 received packets: 1
  * TXD/N46 received packets: 46

The A/B/C pattern suggests that the issue is not TXD identity alone.

It also suggests that the issue is not a simple standalone rule that a 1000 ms offset is always bad, because TXC/N31 used a 1000 ms offset successfully in Condition B but nearly disappeared in Condition C.

The more careful interpretation is that receiver-side reception appears sensitive to a relative phase/schedule interaction. In particular, sparse scheduled transmitters may be poorly received when their programmed replay phase aligns with TXA's fixed-all 1 s rhythm modulo the slot interval.

This remains a receiver-side phase/schedule-interaction hypothesis. The current evidence does not prove collisions or exact transmitted-packet counts.

## Design problem

For twelve transmitters, startup delay must be treated as replay phase.

The design problem is not simply:

* choose twelve arbitrary startup offsets

The design problem is:

* assign twelve startup phases so that repeated SEND opportunities are distributed across the receiver-side rhythm;
* avoid repeatedly aligning sparse scheduled transmitters with high-rate fixed-all transmitters;
* preserve schedule interpretability;
* produce analyzable expected receiver-side packet ratios;
* leave enough structure that physical results can be compared against a manifest-bound expectation.

## Current timing model

The current Run 031 firmware and schedule family use:

* slot interval: 1000 ms
* SD-backed replay
* one schedule row per slot opportunity
* scheduled SEND or SKIP per row
* repeated schedule traversal during the capture

The Run 031 four-transmitter scheduled-send ladder was:

* TXA/N01: fixed-all baseline, 64/64 SEND
* TXB/N16: medium threshold scheduled skipping, 32/64 SEND
* TXC/N31: strict threshold scheduled skipping, 16/64 SEND
* TXD/N46: very-strict threshold scheduled skipping, 8/64 SEND

This creates nested send rhythms:

* fixed-all: approximately every 1 s
* medium threshold: approximately every 2 s
* strict threshold: approximately every 4 s
* very-strict threshold: approximately every 8 s

For twelve transmitters, these rhythms should be treated as part of the phase-design problem.

## Design principle 1: separate high-rate anchors

A fixed-all transmitter is not just another node.

Because it transmits at every slot opportunity, it creates a strong 1 s receiver-side rhythm.

A twelve-transmitter design should avoid placing sparse transmitters at phases that repeatedly align with fixed-all transmitters modulo the 1 s slot interval.

For a first twelve-transmitter design, use no more than one or two fixed-all anchors unless the explicit purpose is to stress the receiver.

If more than one fixed-all transmitter is used, their startup phases should be deliberately separated and analyzed as high-rate anchors.

## Design principle 2: assign phase by send density, not only identity

The phase assignment should reflect expected scheduled-send density.

A useful transmitter class structure is:

* high-rate class:

  * fixed-all or near-fixed-all transmitters
  * highest receiver-side rhythm pressure
* medium-rate class:

  * approximately half of schedule rows are SEND
  * repeated 2 s rhythm under current schedule shape
* low-rate class:

  * approximately one quarter of schedule rows are SEND
  * repeated 4 s rhythm under current schedule shape
* sparse class:

  * approximately one eighth of schedule rows are SEND
  * repeated 8 s rhythm under current schedule shape

Sparse transmitters should not be treated as harmless simply because they send less often. Run 031 v4.4 suggests that sparse transmitters can be disproportionately affected if their few SEND opportunities repeatedly land in a poor phase relation.

## Design principle 3: analyze superframe phase, not only startup offset

A startup offset such as 1000 ms, 1500 ms, or 2500 ms is only meaningful relative to:

* the 1 s slot interval;
* the repeated send/skip pattern;
* the full schedule period;
* the other transmitters' phases.

For the current schedule family, an 8 s diagnostic superframe is a natural first analysis window because the fixed-all, half-rate, quarter-rate, and eighth-rate rhythms all repeat within or against this period.

For twelve transmitters, phase diagnostics should inspect at least:

* modulo 1000 ms;
* modulo 2000 ms;
* modulo 4000 ms;
* modulo 8000 ms.

A later script should report whether candidate transmitter phases repeatedly align with high-rate anchors inside these residue windows.

## Candidate twelve-transmitter role set

A first twelve-transmitter design can use a structured expansion of the Run 031 family.

One possible role set is:

* 2 fixed-all transmitters
* 4 medium-threshold transmitters
* 3 strict-threshold transmitters
* 3 very-strict-threshold transmitters

This gives twelve devices while avoiding an excessive number of fixed-all transmitters.

Candidate identities:

* TXA/N01: fixed-all
* TXB/N16: medium threshold
* TXC/N31: strict threshold
* TXD/N46: very-strict threshold
* TXE/N61: medium threshold
* TXF/N76: strict threshold
* TXG/N91: very-strict threshold
* TXH/N106: medium threshold
* TXI/N121: strict threshold
* TXJ/N136: very-strict threshold
* TXK/N151: fixed-all
* TXL/N166: medium threshold

The exact node IDs are provisional. They should be chosen consistently with the repository's existing naming conventions and any physical board labels.

## Candidate phase table A: simple 500 ms lanes

A naive twelve-device phase table would spread devices every 500 ms:

* TXA/N01: 0 ms
* TXB/N16: 500 ms
* TXC/N31: 1000 ms
* TXD/N46: 1500 ms
* TXE/N61: 2000 ms
* TXF/N76: 2500 ms
* TXG/N91: 3000 ms
* TXH/N106: 3500 ms
* TXI/N121: 4000 ms
* TXJ/N136: 4500 ms
* TXK/N151: 5000 ms
* TXL/N166: 5500 ms

This table is simple and easy to explain, but it is probably not the safest first physical design.

Run 031 v4.4 suggests that a sparse transmitter can be lost when its programmed phase repeatedly aligns with a high-rate transmitter's 1 s rhythm. A simple 500 ms lane table may create repeated alignments between devices that share the same modulo-1000 phase.

Therefore this table should be treated only as a baseline candidate for analysis.

## Candidate phase table B: separated density-aware lanes

A better first candidate is to separate high-rate anchors first, then place medium, low, and sparse transmitters away from those anchors.

Candidate table:

* TXA/N01: 500 ms
* TXK/N151: 5500 ms
* TXB/N16: 750 ms
* TXE/N61: 1750 ms
* TXH/N106: 2750 ms
* TXL/N166: 3750 ms
* TXC/N31: 1250 ms
* TXF/N76: 3250 ms
* TXI/N121: 5250 ms
* TXD/N46: 0 ms
* TXG/N91: 2500 ms
* TXJ/N136: 4500 ms

Rationale:

* TXA/N01 inherits the successful Condition B active phase at 500 ms.
* One sparse transmitter, TXD/N46, inherits the successful Condition B phase at 0 ms.
* Medium and strict transmitters are placed on quarter-offset lanes rather than only integer-second lanes.
* The second fixed-all transmitter is separated from TXA over the larger superframe.
* Sparse transmitters are not all placed on the same modulo-1000 phase.

This is still only a candidate. It must be checked with a phase-risk script before physical replay.

## Candidate phase table C: one-anchor conservative design

A more conservative first twelve-transmitter design would keep only one fixed-all transmitter and avoid a second high-rate anchor.

Candidate role set:

* 1 fixed-all transmitter
* 5 medium-threshold transmitters
* 3 strict-threshold transmitters
* 3 very-strict-threshold transmitters

Candidate table:

* TXA/N01: 500 ms
* TXB/N16: 750 ms
* TXE/N61: 1750 ms
* TXH/N106: 2750 ms
* TXK/N151: 3750 ms
* TXL/N166: 4750 ms
* TXC/N31: 1250 ms
* TXF/N76: 3250 ms
* TXI/N121: 5250 ms
* TXD/N46: 0 ms
* TXG/N91: 2500 ms
* TXJ/N136: 4500 ms

Rationale:

* This preserves TXA as the only fixed-all anchor.
* It preserves the successful Condition B phase relation between TXA and TXD.
* It reduces high-rate pressure while still scaling to twelve transmitters.
* It may be a safer first physical twelve-transmitter attempt than a design with two fixed-all transmitters.

This may be the preferred first physical twelve-transmitter candidate after analysis.

## Phase-risk analysis requirement

Before flashing twelve boards, create a phase-risk analysis script.

Proposed script:

* `scripts/analyze_phase_plan.py`

Inputs:

* a transmitter phase-plan CSV or JSON;
* transmitter identity;
* node identity;
* role or schedule class;
* startup offset in ms;
* schedule CSV path;
* slot interval in ms;
* diagnostic residue windows.

Suggested output artifacts:

* `outputs/run032_twelve_tx_phase_plan_summary.json`
* `outputs/run032_twelve_tx_phase_plan_summary.csv`

The script should report:

* transmitter count;
* assigned startup offset per transmitter;
* scheduled SEND rows per transmitter;
* expected send fraction per transmitter;
* pairwise phase differences;
* modulo-1000 phase groupings;
* modulo-2000 phase groupings;
* modulo-4000 phase groupings;
* modulo-8000 phase groupings;
* repeated SEND/SEND co-phase opportunities;
* repeated alignment with fixed-all transmitters;
* sparse-transmitter alignment risks.

The script should not claim physical collision probability.

It should only report candidate phase-plan risk under the schedule and phase assumptions.

## Proposed phase-risk flags

The phase-risk script should flag:

* any sparse transmitter sharing a modulo-1000 phase band with a fixed-all transmitter;
* any strict or very-strict transmitter whose SEND rows repeatedly align with a fixed-all transmitter over the 8 s diagnostic window;
* any group of three or more transmitters sharing a narrow modulo-1000 residue band;
* any pair of high-rate or medium-rate transmitters with repeated SEND/SEND co-phase opportunities;
* any transmitter class whose SEND opportunities are concentrated into a small number of receiver-side phase bands.

Suggested qualitative labels:

* low risk;
* moderate risk;
* high risk;
* needs physical validation.

These labels should be treated as design diagnostics, not predictions of physical delivery.

## Recommended next steps

1. Commit this design note as the start of the v4.5 design milestone.

2. Create a candidate phase-plan data file for the conservative one-anchor design.

   Suggested file:

   * `traces/run032_twelve_tx_phase_plan_conservative.csv`

3. Create `scripts/analyze_phase_plan.py`.

4. Run the phase-risk analysis over at least Candidate B and Candidate C.

5. Choose one candidate as the first twelve-transmitter physical-prep target.

6. Only after the phase-risk analysis should firmware, SD schedules, and board-label preparation begin.

## Preferred first candidate

The preferred first candidate is Candidate phase table C, the one-anchor conservative design.

Reason:

* v4.4 showed sensitivity to relative phase.
* one fixed-all transmitter reduces high-rate pressure;
* the successful Condition B TXA/TXD phase relation is preserved;
* twelve transmitters can still be represented;
* the design is easier to interpret if the first twelve-transmitter attempt fails.

Candidate phase table C should still be treated as a hypothesis, not a validated solution.

## Interpretation boundary

This note designs a next-step phase strategy for a future twelve-transmitter point-to-point LoRa bench experiment.

It does not establish twelve-transmitter behavior.

It does not infer exact transmitted-packet counts.

It does not confirm collisions.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish airtime optimization.

It does not establish energy savings.

It does not use a live belief-maintenance controller.

It does not evaluate operational wildfire behavior.

Usefulness and priority remain synthetic metadata.

Observed packet ratios in later experiments should be described as receiver-side packet proportions.
