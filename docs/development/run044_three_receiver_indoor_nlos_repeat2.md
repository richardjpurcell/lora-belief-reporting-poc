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

## Results Summary

Run 044 completed the second indoor residential no-line-of-sight repeat in the final three-receiver design.

Condition description:

    Indoor residential no-line-of-sight, approximately 30 ft separation, no direct line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1668 | 1667 |
| RXB_TBEAM | 1625 | 1624 |
| RXC_TBEAM | 1656 | 1655 |

The three logs ended on the same final packet identity:

    TXK/N151 seq 228

Final observed wall-clock timestamp:

    2026-07-11T15:13:47.355+00:00

### Three-Receiver Packet-Identity Comparison

Full-log and common-window comparison results were identical because the parsed receiver logs shared the same observation window.

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1667 |
| RXB unique packet identities | 1624 |
| RXC unique packet identities | 1655 |
| Union packet identities | 1670 |
| Observed by all three receivers | 1617 |
| Observed by exactly two receivers | 42 |
| Observed by exactly one receiver | 11 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 11 |
| RXB_TBEAM | 0 |
| RXC_TBEAM | 0 |

Exactly-two pair counts:

| Receiver pair | Packet identities |
|---|---:|
| RXA_LORA32 + RXB_TBEAM | 4 |
| RXA_LORA32 + RXC_TBEAM | 35 |
| RXB_TBEAM + RXC_TBEAM | 3 |

The strongest per-transmitter receiver-set difference was again TXH/N106:

| Transmitter | Union identities | All three | Exactly two | Exactly one |
|---|---:|---:|---:|---:|
| TXH/N106 | 28 | 0 | 17 | 11 |

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
| RXA_LORA32 | 0.43736263736263736 | -0.06263736263736264 |
| RXB_TBEAM | 0.44543429844098 | -0.05456570155902 |
| RXC_TBEAM | 0.43956043956043955 | -0.06043956043956045 |

### Interpretation

Run 044 is the second final-design indoor residential no-line-of-sight repeat. Like Run 043, it remains manifest-bound and validation-clean while showing receiver-set packet identity differences that were not present in the same way in the close indoor bench repeats.

Run 044 again includes receiver-specific-only packet identities. In this repeat, all exactly-one identities were RXA-only.

TXH/N106 again shows the strongest receiver-set difference: none of its packet identities were observed by all three receivers. This repeats the Run 043 TXH/N106 pattern and should be reported as descriptive receiver-side evidence, not as a physical-cause diagnosis.

The TXK/TXA ratio remains below the manifest expectation on all three receivers. This continues the recurring manifest-ratio distortion pattern across both close indoor and indoor NLOS conditions.
