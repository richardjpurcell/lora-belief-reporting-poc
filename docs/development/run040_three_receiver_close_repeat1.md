# Run 040 Three-Receiver Close Indoor Repeat 1

## Purpose

Run 040 is the first data run in the final three-receiver experiment design.

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

Run 040 keeps fixed:

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

    logs/rx_run_040_close_repeat1_rxa_lora32.csv
    logs/rx_run_040_close_repeat1_rxb_tbeam.csv
    logs/rx_run_040_close_repeat1_rxc_tbeam.csv

## Planned Parsed Logs

    logs/parsed_run_040_close_repeat1_rxa_lora32.csv
    logs/parsed_run_040_close_repeat1_rxa_lora32_rejects.csv
    logs/parsed_run_040_close_repeat1_rxb_tbeam.csv
    logs/parsed_run_040_close_repeat1_rxb_tbeam_rejects.csv
    logs/parsed_run_040_close_repeat1_rxc_tbeam.csv
    logs/parsed_run_040_close_repeat1_rxc_tbeam_rejects.csv

## Planned Analysis Outputs

Receiver-specific manifest summaries and validations:

    outputs/run040_close_repeat1_rxa_manifest_replay_summary.csv
    outputs/run040_close_repeat1_rxa_manifest_replay_summary.json
    outputs/run040_close_repeat1_rxa_manifest_replay_validation.json
    outputs/run040_close_repeat1_rxb_manifest_replay_summary.csv
    outputs/run040_close_repeat1_rxb_manifest_replay_summary.json
    outputs/run040_close_repeat1_rxb_manifest_replay_validation.json
    outputs/run040_close_repeat1_rxc_manifest_replay_summary.csv
    outputs/run040_close_repeat1_rxc_manifest_replay_summary.json
    outputs/run040_close_repeat1_rxc_manifest_replay_validation.json

Three-receiver packet-identity comparison:

    outputs/run040_close_repeat1_three_receiver_comparison_summary.csv
    outputs/run040_close_repeat1_three_receiver_comparison_summary.json
    outputs/run040_close_repeat1_three_receiver_common_window_comparison_summary.csv
    outputs/run040_close_repeat1_three_receiver_common_window_comparison_summary.json

## Primary Metrics

For Run 040, compute:

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

Run 040 is a receiver-side replay observation, not a ground-truth transmitted-packet record.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, transmitter failure, receiver failure, or any specific physical cause.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

The paper-facing interpretation remains manifest-relative and descriptive.

## Results Summary

Run 040 completed the first close indoor bench repeat in the final three-receiver design.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1745 | 1744 |
| RXB_TBEAM | 1766 | 1765 |
| RXC_TBEAM | 1764 | 1763 |

The three logs ended on the same final packet identity:

    TXB/N16 seq 240

Final observed wall-clock timestamp:

    2026-07-11T14:06:07.252+00:00

### Three-Receiver Packet-Identity Comparison

Full-log and common-window comparison results were identical because the parsed receiver logs shared the same observation window.

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1744 |
| RXB unique packet identities | 1765 |
| RXC unique packet identities | 1763 |
| Union packet identities | 1773 |
| Observed by all three receivers | 1728 |
| Observed by exactly two receivers | 43 |
| Observed by exactly one receiver | 2 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 0 |
| RXB_TBEAM | 0 |
| RXC_TBEAM | 2 |

Exactly-two pair counts:

| Receiver pair | Packet identities |
|---|---:|
| RXA_LORA32 + RXB_TBEAM | 10 |
| RXA_LORA32 + RXC_TBEAM | 6 |
| RXB_TBEAM + RXC_TBEAM | 27 |

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
| RXA_LORA32 | 0.4306418219461698 | -0.0693581780538302 |
| RXB_TBEAM | 0.4315352697095436 | -0.0684647302904564 |
| RXC_TBEAM | 0.4306418219461698 | -0.0693581780538302 |

### Interpretation

Run 040 supports the final paper framing: the receiver-side logs strongly preserve the manifest structure, but preservation is not identical across receivers.

Most packet identities were observed by all three receivers, while a small number were observed by only two receivers or only one receiver. This supports treating receiver-side report preservation as a measured, manifest-relative property rather than assuming that the planned reporting structure is identically visible at every receiver.

The repeated TXK/TXA deviation remains visible across all three receivers. This makes the TXK/TXA ratio a useful receiver-side summary for manifest-ratio distortion, while remaining descriptive rather than causal.

Receiver-specific packet identities should not be interpreted as evidence of a specific physical cause without additional instrumentation.
