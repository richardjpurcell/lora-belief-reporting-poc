# Run 037 Dual-Receiver Repeat

## Purpose

Run 037 repeats the Run 036 dual-receiver physical replay without changing the manifest, transmitter schedules, receiver sketches, or receiver roles.

The purpose is to check repeatability of the dual-receiver receiver-side evidence pattern observed in Run 036.

## Scientific Question

Given the same structured twelve-transmitter replay and the same RXA/RXB receiver setup, does a second capture show similar receiver-side report preservation and packet-identity overlap?

## Fixed Setup

Run 037 should keep fixed:

- the Run 035 twelve-transmitter manifest;
- the Run 035 alternate-offset physical replay setup;
- TXK/N151 `STARTUP_OFFSET_MS = 133`;
- TXL/N166 `STARTUP_OFFSET_MS = 271`;
- RXA as the LilyGo LoRa32 receiver;
- RXB as the LilyGo T-Beam receiver;
- the RXA/RXB receiver sketches from Run 036;
- the packet row format `RX,millis,payload,rssi,snr`;
- separate RXA and RXB raw log files.

Run 037 should not introduce a new transmitter schedule, new manifest, new receiver type, third receiver, AWSRT trace, controller, or application-specific usefulness model.

## Expected Raw Logs

Use separate serial logger sessions:

    logs/rx_run_037_dual_receiver_repeat_rxa_lora32.csv
    logs/rx_run_037_dual_receiver_repeat_rxb_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_037_dual_receiver_repeat_rxa_lora32.csv
    logs/parsed_run_037_dual_receiver_repeat_rxa_lora32_rejects.csv
    logs/parsed_run_037_dual_receiver_repeat_rxb_tbeam.csv
    logs/parsed_run_037_dual_receiver_repeat_rxb_tbeam_rejects.csv

## Planned Analysis Outputs

    outputs/run037_dual_receiver_repeat_rxa_manifest_replay_summary.csv
    outputs/run037_dual_receiver_repeat_rxa_manifest_replay_summary.json
    outputs/run037_dual_receiver_repeat_rxa_manifest_replay_validation.json
    outputs/run037_dual_receiver_repeat_rxb_manifest_replay_summary.csv
    outputs/run037_dual_receiver_repeat_rxb_manifest_replay_summary.json
    outputs/run037_dual_receiver_repeat_rxb_manifest_replay_validation.json
    outputs/run037_dual_receiver_repeat_comparison_summary.csv
    outputs/run037_dual_receiver_repeat_comparison_summary.json
    outputs/run037_dual_receiver_repeat_common_window_comparison_summary.csv
    outputs/run037_dual_receiver_repeat_common_window_comparison_summary.json

## Logging Guidance

Start both receiver loggers before starting the transmitters.

Stop both receiver loggers as close together as practical after the replay. If stop times differ, report both the full-log packet-identity comparison and the common-window comparison.

## Interpretation Boundaries

Run 037 is a repeatability check, not a causal physical-channel diagnosis.

Receiver logs are receiver-side observations, not ground-truth transmitted-packet records.

RXA-only and RXB-only packet identities do not by themselves prove collision, interference, timing drift, transmitter failure, receiver failure, or any specific physical cause.

The common-window comparison should be preferred for paper-facing RXA/RXB overlap claims if logger start or stop times differ.

## Result Summary

Run 037 repeated the Run 036 dual-receiver setup without changing the manifest, transmitter schedules, transmitter offsets, receiver roles, or packet format.

Raw receiver logs:

    logs/rx_run_037_dual_receiver_repeat_rxa_lora32.csv
    logs/rx_run_037_dual_receiver_repeat_rxb_tbeam.csv

Parsed receiver logs:

    logs/parsed_run_037_dual_receiver_repeat_rxa_lora32.csv
    logs/parsed_run_037_dual_receiver_repeat_rxb_tbeam.csv

Manifest-bound validation:

| Receiver | Manifest-bundle checks passed | Manifest-bundle checks failed |
|---|---:|---:|
| RXA_LORA32 | 321 / 321 | 0 |
| RXB_TBEAM | 321 / 321 | 0 |

Full-log packet identity overlap:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1572 |
| RXB unique packet identities | 1586 |
| Union packet identities | 1590 |
| Intersection packet identities | 1568 |
| RXA-only packet identities | 4 |
| RXB-only packet identities | 18 |

Common-window packet identity overlap:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1571 |
| RXB unique packet identities | 1586 |
| Union packet identities | 1589 |
| Intersection packet identities | 1568 |
| RXA-only packet identities | 3 |
| RXB-only packet identities | 18 |

Run 037 repeats the main Run 036 observation: two independent receivers observing the same fixed twelve-transmitter manifest replay produce high receiver-side packet-identity overlap, but not identity-level equivalence.

In the common observation window, RXA and RXB shared 1568 packet identities, with 3 RXA-only and 18 RXB-only packet identities. This remains receiver-side descriptive evidence only; the result does not by itself identify a physical cause.

The repeated TXK/TXA manifest-ratio deviation remains visible in both receivers:

| Receiver | TXK/TXA expected ratio | TXK/TXA observed ratio | Observed minus expected |
|---|---:|---:|---:|
| RXA_LORA32 | 0.5000 | 0.4439 | -0.0561 |
| RXB_TBEAM | 0.5000 | 0.4365 | -0.0635 |

This supports treating TXK under-preservation as a repeated manifest-relative observation under the current bench replay configuration, not as a conclusion about a specific causal mechanism.
