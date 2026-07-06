# Run 034 ten-transmitter synthesis

## Purpose

This note synthesizes the Run 034 ten-transmitter bridge result.

Run 034 was designed as a cautious bridge between the validated Run 033 eight-transmitter physical replay and a future twelve-transmitter target. It was not intended to jump directly to twelve transmitters, nor to make a general claim about arbitrary LoRa network scaling.

The synthesis question is:

> Did Run 034 provide enough bounded bench evidence to move from ten-transmitter validation toward cautious twelve-transmitter preparation?

The answer is yes, with important boundaries.

## Milestone context

Run 034 progressed through the following milestones:

- `v5.6-run034-ten-transmitter-bridge-design`
- `v5.7-run034-ten-transmitter-schedule-prep`
- `v5.8-run034-ten-transmitter-phase-plan`
- `v5.9-run034-ten-transmitter-physical-prep`
- `v5.10-run034-ten-transmitter-physical-replay`

Physical replay artifacts:

- `logs/rx_run_034_ten_transmitter_sd_replay_candidate.csv`
- `logs/parsed_run_034_ten_transmitter_sd_replay_candidate.csv`
- `logs/parsed_run_034_ten_transmitter_sd_replay_candidate_rejects.csv`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_summary.json`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_summary.csv`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_validation.json`

## Main result

Run 034 advances the validated physical replay scale point from eight transmitters to ten transmitters under the bounded bench conditions used here.

Manifest-bound validation passed:

- checks passed: 271/271
- checks failed: 0

The physical replay is therefore a successful ten-transmitter bridge candidate.

## Receiver-side evidence

Receiver-side packet counts:

| TX | Node | Received packets | Scheduled SEND rows |
| --- | --- | ---: | ---: |
| TXA | N01 | 445 | 64/64 |
| TXB | N16 | 217 | 32/64 |
| TXC | N31 | 112 | 16/64 |
| TXD | N46 | 54 | 8/64 |
| TXE | N61 | 222 | 32/64 |
| TXF | N76 | 109 | 16/64 |
| TXG | N91 | 54 | 8/64 |
| TXH | N106 | 28 | 4/64 |
| TXI | N121 | 112 | 16/64 |
| TXJ | N136 | 53 | 8/64 |

Receiver-side ratio comparisons relative to TXA/N01:

| Ratio | Expected | Observed | Difference |
| --- | ---: | ---: | ---: |
| TXB/TXA | 0.5000 | 0.4876 | -0.0124 |
| TXC/TXA | 0.2500 | 0.2517 | 0.0017 |
| TXD/TXA | 0.1250 | 0.1213 | -0.0037 |
| TXE/TXA | 0.5000 | 0.4989 | -0.0011 |
| TXF/TXA | 0.2500 | 0.2449 | -0.0051 |
| TXG/TXA | 0.1250 | 0.1213 | -0.0037 |
| TXH/TXA | 0.0625 | 0.0629 | 0.0004 |
| TXI/TXA | 0.2500 | 0.2517 | 0.0017 |
| TXJ/TXA | 0.1250 | 0.1191 | -0.0059 |

## What Run 034 establishes

Run 034 establishes a bounded ten-transmitter bench result.

Specifically, it shows that:

- all ten expected transmitters were visible in the receiver-side log;
- the two new transmitters, TXI/N121 and TXJ/N136, were successfully added;
- the sparse TXH/N106 transmitter remained visible;
- receiver-side packet proportions followed the scheduled SEND ladder closely;
- the manifest-bound validation bundle passed all checks;
- the Run 034 phase-aware startup plan was sufficient for this candidate replay;
- one-card-at-a-time SD preparation worked as a practical bench workflow.

This is stronger than simply observing packets from ten devices. The replay remained interpretable against the manifest, the scheduled SEND ladder, and the phase-aware preparation artifacts.

## What Run 034 does not establish

Run 034 does not establish:

- exact transmitted-packet counts;
- confirmed RF collision mechanisms;
- absence of collisions;
- synchronized latency;
- LoRaWAN behavior;
- energy savings;
- airtime optimization;
- live-controller behavior;
- twelve-transmitter behavior;
- arbitrary-layout ten-node behavior;
- operational wildfire deployment behavior.

## Methodological lesson

Run 034 reinforces the Run 033 lesson that phase-aware preparation is now part of the method.

The successful ten-transmitter replay depended on staged preparation:

- schedule preparation;
- deterministic startup phase planning;
- physical preparation;
- manifest-bound replay analysis;
- validation against expected schedule structure.

Therefore, the next scale step should not be treated as “just add two more devices.” The twelve-transmitter step should preserve the staged method.

## Practical lesson

Run 034 also added a practical bench lesson: one-card-at-a-time SD preparation is safer for the current workflow.

The helper added during the physical replay milestone:

- `scripts/copy_run034_one_sd_schedule_to_card.sh`

should be retained for future physical preparation milestones, especially when only one card can be mounted at a time.

## Recommendation

After Run 034 synthesis, the project should move toward cautious twelve-transmitter preparation.

The next step should be:

- `v5.12-run035-twelve-transmitter-cautious-bridge-design`

It should not be immediate twelve-transmitter physical replay.

Recommended sequence:

| Milestone | Purpose |
| --- | --- |
| `v5.11-run034-ten-transmitter-synthesis` | Synthesize the ten-transmitter bridge result. |
| `v5.12-run035-twelve-transmitter-cautious-bridge-design` | Design the twelve-transmitter bridge only. |
| `v5.13-run035-twelve-transmitter-schedule-prep` | Generate and inspect twelve-transmitter schedules and manifest. |
| `v5.14-run035-twelve-transmitter-phase-plan` | Compute deterministic startup offsets and coincidence checks. |
| `v5.15-run035-twelve-transmitter-physical-prep` | Prepare firmware and SD-card workflow. |
| `v5.16-run035-twelve-transmitter-physical-replay` | Attempt the twelve-transmitter physical replay and analyze receiver logs. |
| `v5.17-run035-twelve-transmitter-synthesis` | Synthesize the twelve-transmitter result and decide next direction. |

## Conclusion

Run 034 succeeded as a ten-transmitter bridge.

The correct conclusion is not “jump to twelve now.”

The correct conclusion is:

> Run 034 succeeded as a ten-transmitter bridge, so the project can now begin cautious twelve-transmitter bridge design using the same staged, phase-aware, manifest-bound method.

The twelve-transmitter step should be treated as a new bridge with its own schedule generation, phase-plan analysis, physical preparation, physical replay, and synthesis.