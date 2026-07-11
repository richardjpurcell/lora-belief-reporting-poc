# Run 045 Three-Receiver Close Indoor Repeat 3

## Purpose

Run 045 is the first data run in the final three-receiver experiment design.

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

Run 045 keeps fixed:

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

    logs/rx_run_040_indoor_nlos_repeat3_rxa_lora32.csv
    logs/rx_run_040_indoor_nlos_repeat3_rxb_tbeam.csv
    logs/rx_run_040_indoor_nlos_repeat3_rxc_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_040_indoor_nlos_repeat3_rxa_lora32.csv
    logs/parsed_run_040_indoor_nlos_repeat3_rxa_lora32_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat3_rxb_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat3_rxb_tbeam_rejects.csv
    logs/parsed_run_040_indoor_nlos_repeat3_rxc_tbeam.csv
    logs/parsed_run_040_indoor_nlos_repeat3_rxc_tbeam_rejects.csv

## Planned Analysis Outputs

Receiver-specific manifest summaries and validations:

    outputs/run045_indoor_nlos_repeat3_rxa_manifest_replay_summary.csv
    outputs/run045_indoor_nlos_repeat3_rxa_manifest_replay_summary.json
    outputs/run045_indoor_nlos_repeat3_rxa_manifest_replay_validation.json
    outputs/run045_indoor_nlos_repeat3_rxb_manifest_replay_summary.csv
    outputs/run045_indoor_nlos_repeat3_rxb_manifest_replay_summary.json
    outputs/run045_indoor_nlos_repeat3_rxb_manifest_replay_validation.json
    outputs/run045_indoor_nlos_repeat3_rxc_manifest_replay_summary.csv
    outputs/run045_indoor_nlos_repeat3_rxc_manifest_replay_summary.json
    outputs/run045_indoor_nlos_repeat3_rxc_manifest_replay_validation.json

Three-receiver packet-identity comparison:

    outputs/run045_indoor_nlos_repeat3_three_receiver_comparison_summary.csv
    outputs/run045_indoor_nlos_repeat3_three_receiver_comparison_summary.json
    outputs/run045_indoor_nlos_repeat3_three_receiver_common_window_comparison_summary.csv
    outputs/run045_indoor_nlos_repeat3_three_receiver_common_window_comparison_summary.json

## Primary Metrics

For Run 045, compute:

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

Run 045 is a receiver-side replay observation, not a ground-truth transmitted-packet record.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, transmitter failure, receiver failure, or any specific physical cause.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

The paper-facing interpretation remains manifest-relative and descriptive.

## Results Summary

Run 045 completed the third indoor residential no-line-of-sight repeat in the final three-receiver design.

Condition description:

    Indoor residential no-line-of-sight, approximately 30 ft separation, no direct line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1673 | 1672 |
| RXB_TBEAM | 1638 | 1637 |
| RXC_TBEAM | 1676 | 1675 |

The three logs ended on the same final packet identity:

    TXA/N01 seq 458

Final observed wall-clock timestamp:

    2026-07-11T15:27:38.250+00:00

### Three-Receiver Packet-Identity Comparison

Full-log and common-window comparison results were identical because the parsed receiver logs shared the same observation window.

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1672 |
| RXB unique packet identities | 1636 |
| RXC unique packet identities | 1675 |
| Union packet identities | 1682 |
| Observed by all three receivers | 1620 |
| Observed by exactly two receivers | 61 |
| Observed by exactly one receiver | 1 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 0 |
| RXB_TBEAM | 0 |
| RXC_TBEAM | 1 |

Exactly-two pair counts:

| Receiver pair | Packet identities |
|---|---:|
| RXA_LORA32 + RXB_TBEAM | 7 |
| RXA_LORA32 + RXC_TBEAM | 45 |
| RXB_TBEAM + RXC_TBEAM | 9 |

The strongest per-transmitter receiver-set difference was again TXH/N106:

| Transmitter | Union identities | All three | Exactly two | Exactly one |
|---|---:|---:|---:|---:|
| TXH/N106 | 29 | 0 | 28 | 1 |

### Manifest Validation

All three receiver-specific manifest replay bundles passed validation.

| Receiver | Checks passed | Checks failed | Passed |
|---|---:|---:|---|
| RXA_LORA32 | 321 / 321 | 0 | true |
| RXB_TBEAM | 321 / 321 | 0 | true |
| RXC_TBEAM | 321 / 321 | 0 | true |

### Interpretation

Run 045 is the third final-design indoor residential no-line-of-sight repeat. It remains manifest-bound and validation-clean while again showing receiver-set packet identity differences.

Exactly-one packet identities are still present in this repeat, but at a much lower count than Runs 043 and 044. The single receiver-specific-only identity was RXC-only.

TXH/N106 again shows the strongest receiver-set difference: none of its packet identities were observed by all three receivers. Across Runs 043, 044, and 045, this gives a repeated indoor NLOS pattern: TXH/N106 appears in the receiver-side evidence, but not as all-three preserved packet identities.

This remains a descriptive receiver-side result. It should not be interpreted as identifying a physical cause without additional measurement.
