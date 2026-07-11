# Run 041 Three-Receiver Close Indoor Repeat 2

## Purpose

Run 041 is the first data run in the final three-receiver experiment design.

It uses the close indoor bench condition with:

- twelve transmitters;
- three receivers;
- the fixed Run 035 manifest-bound replay;
- unchanged transmitter firmware and offsets;
- unchanged receiver packet format.

## Experimental Condition

Condition A: close indoor bench.

This condition is the most controlled available indoor setup and serves as the baseline for the final three-receiver experiment set.

## Receiver Set

| Receiver | Board role | Sketch |
|---|---|---|
| RXA_LORA32 | LilyGo LoRa32 receiver | `firmware/first_radio_link_RX_A_LORA32/first_radio_link_RX_A_LORA32.ino` |
| RXB_TBEAM | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_B_TBEAM/first_radio_link_RX_B_TBEAM.ino` |
| RXC_TBEAM | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_C_TBEAM/first_radio_link_RX_C_TBEAM.ino` |

## Fixed Setup

Run 041 keeps fixed:

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

    logs/rx_run_040_close_repeat2_rxa_lora32.csv
    logs/rx_run_040_close_repeat2_rxb_tbeam.csv
    logs/rx_run_040_close_repeat2_rxc_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_040_close_repeat2_rxa_lora32.csv
    logs/parsed_run_040_close_repeat2_rxa_lora32_rejects.csv
    logs/parsed_run_040_close_repeat2_rxb_tbeam.csv
    logs/parsed_run_040_close_repeat2_rxb_tbeam_rejects.csv
    logs/parsed_run_040_close_repeat2_rxc_tbeam.csv
    logs/parsed_run_040_close_repeat2_rxc_tbeam_rejects.csv

## Planned Analysis Outputs

Receiver-specific manifest summaries and validations:

    outputs/run041_close_repeat2_rxa_manifest_replay_summary.csv
    outputs/run041_close_repeat2_rxa_manifest_replay_summary.json
    outputs/run041_close_repeat2_rxa_manifest_replay_validation.json
    outputs/run041_close_repeat2_rxb_manifest_replay_summary.csv
    outputs/run041_close_repeat2_rxb_manifest_replay_summary.json
    outputs/run041_close_repeat2_rxb_manifest_replay_validation.json
    outputs/run041_close_repeat2_rxc_manifest_replay_summary.csv
    outputs/run041_close_repeat2_rxc_manifest_replay_summary.json
    outputs/run041_close_repeat2_rxc_manifest_replay_validation.json

Three-receiver packet-identity comparison:

    outputs/run041_close_repeat2_three_receiver_comparison_summary.csv
    outputs/run041_close_repeat2_three_receiver_comparison_summary.json
    outputs/run041_close_repeat2_three_receiver_common_window_comparison_summary.csv
    outputs/run041_close_repeat2_three_receiver_common_window_comparison_summary.json

## Primary Metrics

For Run 041, compute:

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

Run 041 is a receiver-side replay observation, not a ground-truth transmitted-packet record.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, transmitter failure, receiver failure, or any specific physical cause.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

The paper-facing interpretation remains manifest-relative and descriptive.

## Results Summary

Run 041 completed the second close indoor bench repeat in the final three-receiver design.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1608 | 1607 |
| RXB_TBEAM | 1623 | 1622 |
| RXC_TBEAM | 1618 | 1617 |

The three logs ended on the same final packet identity:

    TXK/N151 seq 222

Final observed wall-clock timestamp:

    2026-07-11T14:24:14.099+00:00

### Parse Results

| Receiver | Valid packets | Malformed packets |
|---|---:|---:|
| RXA_LORA32 | 1606 | 1 |
| RXB_TBEAM | 1622 | 0 |
| RXC_TBEAM | 1617 | 0 |

RXA had one malformed row. RXB and RXC had no malformed packet rows.

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
| RXA_LORA32 | 0.4356659142212190 | -0.0643340857787810 |
| RXB_TBEAM | 0.43243243243243246 | -0.06756756756756754 |
| RXC_TBEAM | 0.4401805869074492 | -0.0598194130925508 |

### Interpretation

Run 041 repeats the main Run 040 pattern: the receiver-side logs remain manifest-bound and validation-clean, but the observed receiver evidence is not identical across receivers.

The TXK/TXA ratio remains below the manifest expectation on all three receivers. This reinforces the usefulness of TXK/TXA as a compact manifest-ratio diagnostic while keeping the interpretation descriptive rather than causal.

The single RXA malformed row should be reported as a parser-level observation, not as a physical explanation.

### Three-Receiver Packet-Identity Comparison

Full-log and common-window comparison results were identical because the parsed receiver logs shared the same observation window.

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1606 |
| RXB unique packet identities | 1622 |
| RXC unique packet identities | 1617 |
| Union packet identities | 1628 |
| Observed by all three receivers | 1589 |
| Observed by exactly two receivers | 39 |
| Observed by exactly one receiver | 0 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 0 |
| RXB_TBEAM | 0 |
| RXC_TBEAM | 0 |

Exactly-two pair counts:

| Receiver pair | Packet identities |
|---|---:|
| RXA_LORA32 + RXB_TBEAM | 11 |
| RXA_LORA32 + RXC_TBEAM | 6 |
| RXB_TBEAM + RXC_TBEAM | 22 |
