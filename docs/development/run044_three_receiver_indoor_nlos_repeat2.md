# Run 044 Three-Receiver Close Indoor Repeat 2

## Purpose

Run 044 is the first data run in the final three-receiver experiment design.

It uses the indoor residential no-line-of-sight condition with:

- twelve transmitters;
- three receivers;
- the fixed Run 035 manifest-bound replay;
- unchanged transmitter firmware and offsets;
- unchanged receiver packet format.

## Experimental Condition

Condition A: indoor residential no-line-of-sight.

This condition is the most controlled available indoor setup and serves as the baseline for the final three-receiver experiment set.

## Receiver Set

| Receiver | Board role | Sketch |
|---|---|---|
| RXA_LORA32 | LilyGo LoRa32 receiver | `firmware/first_radio_link_RX_A_LORA32/first_radio_link_RX_A_LORA32.ino` |
| RXB_TBEAM | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_B_TBEAM/first_radio_link_RX_B_TBEAM.ino` |
| RXC_TBEAM | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_C_TBEAM/first_radio_link_RX_C_TBEAM.ino` |

## Fixed Setup

Run 044 keeps fixed:

- the Run 035 twelve-transmitter manifest;
- the Run 035 alternate-offset replay setup;
- TXK/N151 `STARTUP_OFFSET_MS = 133`;
- TXL/N166 `STARTUP_OFFSET_MS = 271`;
- all transmitter schedules;
- all transmitter firmware apart from the already-established offsets;
- receiver packet row format `RX,millis,payload,rssi,snr`;
- parser workflow;
- manifest-bound analyzer workflow;
- validation workflow.

## Expected Raw Logs

Use separate serial logger sessions:

    logs/rx_run_040_indoor_nlos_repeat2_rxa_lora32.csv
    logs/rx_run_040_indoor_nlos_repeat2_rxb_tbeam.csv
    logs/rx_run_040_indoor_nlos_repeat2_rxc_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_040_indoor_nlos_repeat2_rxa_lora32.csv
    logs/parsed_run_040_indoor_nlos_repeat2_rxa_lora32_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat2_rxb_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat2_rxb_tbeam_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat2_rxc_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat2_rxc_tbeam_rejects.csv

## Planned Analysis Outputs

Receiver-specific manifest summaries and validations:

    outputs/run044_indoor_nlos_repeat2_rxa_manifest_replay_summary.csv
    outputs/run044_indoor_nlos_repeat2_rxa_manifest_replay_summary.json
    outputs/run044_indoor_nlos_repeat2_rxa_manifest_replay_validation.json
    outputs/run044_indoor_nlos_repeat2_rxb_manifest_replay_summary.csv
    outputs/run044_indoor_nlos_repeat2_rxb_manifest_replay_summary.json
    outputs/run044_indoor_nlos_repeat2_rxb_manifest_replay_validation.json
    outputs/run044_indoor_nlos_repeat2_rxc_manifest_replay_summary.csv
    outputs/run044_indoor_nlos_repeat2_rxc_manifest_replay_summary.json
    outputs/run044_indoor_nlos_repeat2_rxc_manifest_replay_validation.json

Three-receiver packet-identity comparison:

    outputs/run044_indoor_nlos_repeat2_three_receiver_comparison_summary.csv
    outputs/run044_indoor_nlos_repeat2_three_receiver_comparison_summary.json
    outputs/run044_indoor_nlos_repeat2_three_receiver_common_window_comparison_summary.csv
    outputs/run044_indoor_nlos_repeat2_three_receiver_common_window_comparison_summary.json

## Primary Metrics

For Run 044, compute:

- valid packets per receiver;
- parsed reject rows per receiver;
- manifest-bundle validation result per receiver;
- receiver union packet identities;
- packet identities observed by all three receivers;
- packet identities observed by exactly two receivers;
- packet identities observed by exactly one receiver;
- receiver-specific-only packet identities;
- per-transmitter received counts per receiver;
- manifest-ratio deviations per receiver, especially TXK/TXA.

## Serial Port Mapping

Record before capture:

| Receiver | Serial port |
|---|---|
| RXA_LORA32 | |
| RXB_TBEAM | |
| RXC_TBEAM | |

## Logging Guidance

Start all three receiver loggers before starting the transmitters.

Stop all three receiver loggers as close together as practical after the replay. If start or stop times differ, report both full-log and common-window packet-identity comparisons.

## Interpretation Boundaries

Run 044 is a receiver-side replay observation, not a ground-truth transmitted-packet record.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, transmitter failure, receiver failure, or any specific physical cause.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

The paper-facing interpretation remains manifest-relative and descriptive.
