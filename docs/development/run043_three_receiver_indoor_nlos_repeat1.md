# Run 043 Three-Receiver Close Indoor Repeat 1

## Purpose

Run 043 is the first data run in the final three-receiver experiment design.

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

Run 043 keeps fixed:

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

    logs/rx_run_040_indoor_nlos_repeat1_rxa_lora32.csv
    logs/rx_run_040_indoor_nlos_repeat1_rxb_tbeam.csv
    logs/rx_run_040_indoor_nlos_repeat1_rxc_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_040_indoor_nlos_repeat1_rxa_lora32.csv
    logs/parsed_run_040_indoor_nlos_repeat1_rxa_lora32_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat1_rxb_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat1_rxb_tbeam_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat1_rxc_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat1_rxc_tbeam_rejects.csv

## Planned Analysis Outputs

Receiver-specific manifest summaries and validations:

    outputs/run043_indoor_nlos_repeat1_rxa_manifest_replay_summary.csv
    outputs/run043_indoor_nlos_repeat1_rxa_manifest_replay_summary.json
    outputs/run043_indoor_nlos_repeat1_rxa_manifest_replay_validation.json
    outputs/run043_indoor_nlos_repeat1_rxb_manifest_replay_summary.csv
    outputs/run043_indoor_nlos_repeat1_rxb_manifest_replay_summary.json
    outputs/run043_indoor_nlos_repeat1_rxb_manifest_replay_validation.json
    outputs/run043_indoor_nlos_repeat1_rxc_manifest_replay_summary.csv
    outputs/run043_indoor_nlos_repeat1_rxc_manifest_replay_summary.json
    outputs/run043_indoor_nlos_repeat1_rxc_manifest_replay_validation.json

Three-receiver packet-identity comparison:

    outputs/run043_indoor_nlos_repeat1_three_receiver_comparison_summary.csv
    outputs/run043_indoor_nlos_repeat1_three_receiver_comparison_summary.json
    outputs/run043_indoor_nlos_repeat1_three_receiver_common_window_comparison_summary.csv
    outputs/run043_indoor_nlos_repeat1_three_receiver_common_window_comparison_summary.json

## Primary Metrics

For Run 043, compute:

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

Run 043 is a receiver-side replay observation, not a ground-truth transmitted-packet record.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, transmitter failure, receiver failure, or any specific physical cause.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

The paper-facing interpretation remains manifest-relative and descriptive.

## Results Summary

Run 043 completed the first indoor residential no-line-of-sight repeat in the final three-receiver design.

Condition description:

    Indoor residential no-line-of-sight, approximately 30 ft separation, no direct line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1669 | 1668 |
| RXB_TBEAM | 1648 | 1647 |
| RXC_TBEAM | 1655 | 1654 |

The three logs ended on the same final packet identity:

    TXC/N31 seq 113

Final observed wall-clock timestamp:

    2026-07-11T14:59:34.336+00:00

### Three-Receiver Packet-Identity Comparison

Full-log and common-window comparison results were identical because the parsed receiver logs shared the same observation window.

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1667 |
| RXB unique packet identities | 1647 |
| RXC unique packet identities | 1654 |
| Union packet identities | 1680 |
| Observed by all three receivers | 1628 |
| Observed by exactly two receivers | 32 |
| Observed by exactly one receiver | 20 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 18 |
| RXB_TBEAM | 0 |
| RXC_TBEAM | 2 |

Exactly-two pair counts:

| Receiver pair | Packet identities |
|---|---:|
| RXA_LORA32 + RXB_TBEAM | 8 |
| RXA_LORA32 + RXC_TBEAM | 13 |
| RXB_TBEAM + RXC_TBEAM | 11 |

The strongest per-transmitter receiver-set difference was TXH/N106:

| Transmitter | Union identities | All three | Exactly two | Exactly one |
|---|---:|---:|---:|---:|
| TXH/N106 | 28 | 0 | 9 | 19 |

### Manifest Validation

All three receiver-specific manifest replay bundles passed validation.

| Receiver | Checks passed | Checks failed | Passed |
|---|---:|---:|---|
| RXA_LORA32 | 321 / 321 | 0 | true |
| RXB_TBEAM | 321 / 321 | 0 | true |
| RXC_TBEAM | 321 / 321 | 0 | true |

### Manifest-Ratio Check

The expected manifest TXK/TXA ratio is 0.5.

Observed TXK/TXA ratios:

| Receiver | Observed TXK/TXA | Observed - expected |
|---|---:|---:|
| RXA_LORA32 | 0.4392935982339956 | -0.0607064017660044 |
| RXB_TBEAM | 0.4407894736842105 | -0.0592105263157895 |
| RXC_TBEAM | 0.43736263736263736 | -0.06263736263736264 |

### Interpretation

Run 043 is the first final-design indoor residential no-line-of-sight repeat. The receiver-side logs remain manifest-bound and validation-clean, but receiver-set packet identity preservation differs from the close indoor bench repeats.

Unlike the close bench repeats, Run 043 includes receiver-specific-only packet identities. Most of these were RXA-only, with a smaller number RXC-only and none RXB-only. This should be treated as receiver-side evidence of condition-dependent preservation structure, not as a physical explanation.

TXH/N106 shows the strongest receiver-set difference in this run: none of its packet identities were observed by all three receivers, while 19 were observed by exactly one receiver. This is a descriptive result only; it does not by itself identify the cause of the receiver-specific evidence.

The TXK/TXA ratio remains below the manifest expectation on all three receivers. This continues the recurring manifest-ratio distortion pattern seen in the close indoor condition.
