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
