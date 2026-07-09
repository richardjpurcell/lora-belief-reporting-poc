# Run 038 Dual-Receiver Placement Variation

## Purpose

Run 038 repeats the fixed twelve-transmitter dual-receiver replay while changing only the physical placement/separation of the receivers within the available indoor environment.

The purpose is to test whether the Run 036/Run 037 receiver-side packet-identity overlap and manifest-relative preservation pattern remains visible under a modest indoor placement change.

## Scientific Question

Given the same twelve-transmitter manifest replay and the same RXA/RXB receiver setup, does increased indoor receiver/transmitter separation change receiver-side report preservation?

## Fixed Setup

Run 038 should keep fixed:

- the Run 035 twelve-transmitter manifest;
- the Run 035 alternate-offset physical replay setup;
- TXK/N151 `STARTUP_OFFSET_MS = 133`;
- TXL/N166 `STARTUP_OFFSET_MS = 271`;
- RXA as the LilyGo LoRa32 receiver;
- RXB as the LilyGo T-Beam receiver;
- the RXA/RXB receiver sketches from Run 036;
- the packet row format `RX,millis,payload,rssi,snr`;
- the parser, manifest-bound analyzer, validator, and dual-receiver comparison workflow.

Run 038 should not introduce:

- a new manifest;
- new transmitter schedules;
- new transmitter firmware offsets;
- a third receiver;
- a controller;
- AWSRT trace input;
- LoRaWAN behavior;
- energy, airtime, or scaling claims.

## Changed Variable

The changed variable is physical placement/separation within the available house environment.

Approximate setup notes to record before or after capture:

- transmitter cluster location:
- RXA location:
- RXB location:
- approximate RXA/RXB separation:
- approximate transmitter-to-RXA separation:
- approximate transmitter-to-RXB separation:
- walls/floors/major obstructions:
- antenna orientation changes:
- other relevant environmental notes:

This is an approximate indoor placement variation, not a calibrated propagation study.

## Expected Raw Logs

Use separate serial logger sessions:

    logs/rx_run_038_dual_receiver_placement_rxa_lora32.csv
    logs/rx_run_038_dual_receiver_placement_rxb_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_038_dual_receiver_placement_rxa_lora32.csv
    logs/parsed_run_038_dual_receiver_placement_rxa_lora32_rejects.csv
    logs/parsed_run_038_dual_receiver_placement_rxb_tbeam.csv
    logs/parsed_run_038_dual_receiver_placement_rxb_tbeam_rejects.csv

## Planned Analysis Outputs

    outputs/run038_dual_receiver_placement_rxa_manifest_replay_summary.csv
    outputs/run038_dual_receiver_placement_rxa_manifest_replay_summary.json
    outputs/run038_dual_receiver_placement_rxa_manifest_replay_validation.json
    outputs/run038_dual_receiver_placement_rxb_manifest_replay_summary.csv
    outputs/run038_dual_receiver_placement_rxb_manifest_replay_summary.json
    outputs/run038_dual_receiver_placement_rxb_manifest_replay_validation.json
    outputs/run038_dual_receiver_placement_comparison_summary.csv
    outputs/run038_dual_receiver_placement_comparison_summary.json
    outputs/run038_dual_receiver_placement_common_window_comparison_summary.csv
    outputs/run038_dual_receiver_placement_common_window_comparison_summary.json

## Logging Guidance

Start both receiver loggers before starting the transmitters.

Stop both receiver loggers as close together as practical after the replay. If start or stop times differ, report both the full-log packet-identity comparison and the common-window comparison.

## Interpretation Boundaries

Run 038 is an indoor placement-variation check, not a causal physical-channel diagnosis.

Receiver logs are receiver-side observations, not ground-truth transmitted-packet records.

RXA-only and RXB-only packet identities do not by themselves prove collision, interference, timing drift, transmitter failure, receiver failure, antenna effects, wall attenuation, or any specific physical cause.

The common-window comparison should be preferred for paper-facing RXA/RXB overlap claims if logger start or stop times differ.

## Result Summary

Run 038 repeated the fixed twelve-transmitter replay while changing only the indoor physical placement/separation of the receiver setup.

Raw receiver logs:

    logs/rx_run_038_dual_receiver_placement_rxa_lora32.csv
    logs/rx_run_038_dual_receiver_placement_rxb_tbeam.csv

Parsed receiver logs:

    logs/parsed_run_038_dual_receiver_placement_rxa_lora32.csv
    logs/parsed_run_038_dual_receiver_placement_rxb_tbeam.csv

Manifest-bound validation:

| Receiver | Manifest-bundle checks passed | Manifest-bundle checks failed |
|---|---:|---:|
| RXA_LORA32 | 321 / 321 | 0 |
| RXB_TBEAM | 321 / 321 | 0 |

Full-log and common-window packet identity overlap were identical because both receiver logs had the same wall-time observation window.

Packet identity overlap:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1522 |
| RXB unique packet identities | 1531 |
| Union packet identities | 1536 |
| Intersection packet identities | 1517 |
| RXA-only packet identities | 5 |
| RXB-only packet identities | 14 |

Run 038 again showed high receiver-side packet-identity overlap without identity-level equivalence. Compared with Runs 036 and 037, the placement variation produced fewer total received packet identities while preserving the same general dual-receiver pattern.

The strongest manifest-ratio deviations in Run 038 were TXH/TXA and TXK/TXA:

| Receiver | Ratio | Expected | Observed | Observed minus expected |
|---|---|---:|---:|---:|
| RXA_LORA32 | TXH/TXA | 0.0625 | 0.0071 | -0.0554 |
| RXA_LORA32 | TXK/TXA | 0.5000 | 0.4316 | -0.0684 |
| RXB_TBEAM | TXH/TXA | 0.0625 | 0.0023 | -0.0602 |
| RXB_TBEAM | TXK/TXA | 0.5000 | 0.4366 | -0.0634 |

TXK under-preservation remains visible across receiver logs. TXH under-preservation appears strongly in this placement-variation run. These are manifest-relative receiver-side observations under the current indoor bench setup, not causal claims about propagation, collision, antenna behavior, or transmitter failure.
