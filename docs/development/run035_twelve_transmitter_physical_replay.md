# Run 035 twelve-transmitter physical replay

## Status

Run 035 produced a twelve-transmitter receiver-side physical replay candidate using an
alternate-offset firmware adjustment for TXK and TXL.

The run is best interpreted as an alternate-offset twelve-transmitter bridge result,
not as a validation of the original Run 035 TXK/TXL phase-plan offsets.

## Physical replay caveat

The original Run 035 physical-prep offsets for the final two transmitters were:

| Transmitter | Original prepared offset |
|---|---:|
| TXK/N151 | 14950 ms |
| TXL/N166 | 12950 ms |

In the full twelve-transmitter bench condition, TXK and TXL were not observed with
those prepared offsets. When TXI, TXJ, TXK, and TXL were run as a smaller subset,
TXK and TXL were observed. For the alternate full twelve-transmitter capture, the
following ad hoc firmware offsets were used:

| Transmitter | Alternate physical offset |
|---|---:|
| TXK/N151 | 133 ms |
| TXL/N166 | 271 ms |

This means the alternate replay demonstrates twelve-transmitter receiver-side
presence under adjusted physical timing, but does not validate the original
TXK/TXL offset choices from the prepared phase plan.

## Artifacts

Input and parsed receiver artifacts:

- `logs/rx_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv`
- `logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv`
- `logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate_rejects.csv`

Manifest-bound analysis artifacts:

- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.json`
- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.csv`
- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_validation.json`

## Bundle validation

The alternate replay bundle passed manifest-bound validation:

| Check summary | Value |
|---|---:|
| Passed | True |
| Checks total | 321 |
| Checks passed | 321 |
| Checks failed | 0 |

## Receiver-side packet counts

Total received valid packets, summed from the per-transmitter table: `1635`.

| Transmitter | Scheduled SEND rows | Scheduled SKIP rows | Received valid packets |
|---|---:|---:|---:|
| TXA/N01 | 64 | 0 | 448 |
| TXB/N16 | 32 | 32 | 226 |
| TXC/N31 | 16 | 48 | 111 |
| TXD/N46 | 8 | 56 | 56 |
| TXE/N61 | 32 | 32 | 220 |
| TXF/N76 | 16 | 48 | 111 |
| TXG/N91 | 8 | 56 | 55 |
| TXH/N106 | 4 | 60 | 17 |
| TXI/N121 | 16 | 48 | 110 |
| TXJ/N136 | 8 | 56 | 54 |
| TXK/N151 | 32 | 32 | 199 |
| TXL/N166 | 4 | 60 | 28 |

## Receiver-side ratio comparison

Ratios are normalized against TXA/N01. These ratios compare receiver-side packet
counts against the scheduled SEND-row ladder in the Run 035 manifest.

| Ratio | Expected scheduled ratio | Observed received ratio | Observed - expected |
|---|---:|---:|---:|
| TXB/TXA | 0.5000 | 0.5045 | +0.0045 |
| TXC/TXA | 0.2500 | 0.2478 | -0.0022 |
| TXD/TXA | 0.1250 | 0.1250 | +0.0000 |
| TXE/TXA | 0.5000 | 0.4911 | -0.0089 |
| TXF/TXA | 0.2500 | 0.2478 | -0.0022 |
| TXG/TXA | 0.1250 | 0.1228 | -0.0022 |
| TXH/TXA | 0.0625 | 0.0379 | -0.0246 |
| TXI/TXA | 0.2500 | 0.2455 | -0.0045 |
| TXJ/TXA | 0.1250 | 0.1205 | -0.0045 |
| TXK/TXA | 0.5000 | 0.4442 | -0.0558 |
| TXL/TXA | 0.0625 | 0.0625 | +0.0000 |

## Interpretation

The alternate replay gives evidence that all twelve transmitters can be represented
in a manifest-bound physical replay and that the receiver-side packet ladder remains
broadly visible under the adjusted offsets.

The strongest ratio deviations are TXK/TXA and TXH/TXA. TXK is under-represented
relative to its expected 0.5 scheduled ratio, and TXH is also weak relative to its
expected 0.0625 scheduled ratio. Therefore this run should be described as a
successful twelve-transmitter presence/bridge candidate rather than a clean final
ratio-preservation result.

## Boundaries

This result should not be interpreted as evidence of:

- validated LoRaWAN behaviour;
- synchronized latency;
- exact RF collision attribution;
- energy or airtime optimization;
- arbitrary layout generalization;
- operational wildfire deployment behaviour.

The result is limited to this bench setup, these twelve transmitter identities, the
Run 035 schedule manifest, the alternate TXK/TXL physical offsets, and the receiver
log captured for this run.
