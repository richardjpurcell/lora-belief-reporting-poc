# Run 034 ten-transmitter physical replay

## Purpose

This note records the Run 034 ten-transmitter SD-backed physical replay candidate.

Run 034 is a bridge from the validated Run 033 eight-transmitter replay toward a future twelve-transmitter target. It uses the schedule-prep, phase-plan, and physical-prep artifacts prepared in the preceding milestones.

This note records the receiver-side evidence and manifest-bound validation result. It does not claim exact transmitted-packet counts, RF collision mechanisms, synchronized latency, LoRaWAN behavior, energy savings, live-controller behavior, twelve-transmitter behavior, or operational wildfire deployment behavior.

## Milestone context

This replay follows:

- `v5.7-run034-ten-transmitter-schedule-prep`
- `v5.8-run034-ten-transmitter-phase-plan`
- `v5.9-run034-ten-transmitter-physical-prep`

Physical-replay branch:

- `exp078-run034-ten-transmitter-physical-replay`

Candidate replay artifacts:

- `logs/rx_run_034_ten_transmitter_sd_replay_candidate.csv`
- `logs/parsed_run_034_ten_transmitter_sd_replay_candidate.csv`
- `logs/parsed_run_034_ten_transmitter_sd_replay_candidate_rejects.csv`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_summary.json`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_summary.csv`
- `outputs/run034_ten_transmitter_manifest_replay_candidate_validation.json`

## Physical preparation notes

All ten devices were prepared with Run 034 firmware.

The SD-card workflow was adjusted because only one SD card could be mounted at a time. The following helper was added:

- `scripts/copy_run034_one_sd_schedule_to_card.sh`

The helper copies one Run 034 SD schedule at a time to the mounted matching card.

TXI and TXJ firmware serial-print labels were corrected after creation from template sketches:

- `firmware/first_radio_link_TX_I/first_radio_link_TX_I.ino`
- `firmware/first_radio_link_TX_J/first_radio_link_TX_J.ino`

The manifest analysis and validation tools were patched to accept the richer list-of-records `expected_scheduled_ratios` manifest representation used by Run 034 while preserving the older dictionary representation.

## Receiver-log parse summary

Parsed receiver log:

- valid packets: 1406
- malformed packets: 2

## Per-transmitter replay summary

| TX | Node | Received packets | Scheduled SEND rows | Scheduled SKIP rows |
| --- | --- | ---: | ---: | ---: |
| TXA | N01 | 0 | 64/ | 0 |
| TXB | N16 | 0 | 32/ | 32 |
| TXC | N31 | 0 | 16/ | 48 |
| TXD | N46 | 0 | 8/ | 56 |
| TXE | N61 | 0 | 32/ | 32 |
| TXF | N76 | 0 | 16/ | 48 |
| TXG | N91 | 0 | 8/ | 56 |
| TXH | N106 | 0 | 4/ | 60 |
| TXI | N121 | 0 | 16/ | 48 |
| TXJ | N136 | 0 | 8/ | 56 |

## Receiver-side ratio comparisons

Ratios are computed from receiver-side packet counts relative to TXA/N01.

| Ratio | Scheduled expected | Observed received-packet ratio | Observed minus expected |
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

## Manifest-bound validation

Validation output:

- `outputs/run034_ten_transmitter_manifest_replay_candidate_validation.json`

Validation result:

- passed: `True`
- checks total: 271
- checks passed: 271
- checks failed: 0

The candidate replay passes the manifest-bound validation checks.

## Interpretation

Run 034 advances the validated physical replay scale point from eight transmitters to ten transmitters under the bounded bench conditions used here.

The key evidence is:

- all ten expected transmitters are present in the receiver-side log
- receiver-side packet counts follow the scheduled SEND ladder
- the two new transmitters, TXI/N121 and TXJ/N136, are present
- the sparse TXH/N106 transmitter remains visible
- malformed packets are limited to the rejects file and do not prevent validation
- manifest-bound validation passes 271/271 checks

This supports Run 034 as a successful ten-transmitter bridge candidate.

## Interpretation boundaries

This milestone does not establish:

- exact transmitted-packet counts
- confirmed RF collision mechanisms
- absence of collisions
- synchronized latency
- LoRaWAN behavior
- energy savings
- airtime optimization
- live-controller behavior
- twelve-transmitter behavior
- operational wildfire deployment behavior

This milestone supports:

- a ten-transmitter SD-backed scheduled replay under bench conditions
- manifest-bound replay analysis for ten transmitters
- receiver-side scheduled-ratio preservation at the ten-transmitter bridge scale
- continued use of phase-aware startup planning for larger physical replays

## Next milestone

The next recommended milestone is:

- `v5.11-run034-ten-transmitter-synthesis`

That milestone should synthesize what Run 034 establishes, what it does not establish, and whether the next step should be repeat-ten, a diagnostic variation, or cautious movement toward twelve transmitters.
