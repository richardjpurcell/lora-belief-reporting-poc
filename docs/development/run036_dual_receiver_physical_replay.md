# Run 036 Dual-Receiver Physical Replay

## Purpose

Run 036 tests whether two independent physical receivers observe the same manifest-relative report structure during the same twelve-transmitter LoRa replay.

The scientific question is:

> Given the same structured twelve-transmitter replay, do two independent physical receivers observe the same report structure?

Run 036 keeps the replay manifest fixed and compares receiver-side evidence from:

- RXA: LilyGo LoRa32 receiver.
- RXB: LilyGo T-Beam receiver.

## Capture Artifacts

Raw receiver logs:

    logs/rx_run_036_dual_receiver_rxa_lora32.csv
    logs/rx_run_036_dual_receiver_rxb_tbeam.csv

Parsed receiver logs:

    logs/parsed_run_036_dual_receiver_rxa_lora32.csv
    logs/parsed_run_036_dual_receiver_rxb_tbeam.csv

Reject logs:

    logs/parsed_run_036_dual_receiver_rxa_lora32_rejects.csv
    logs/parsed_run_036_dual_receiver_rxb_tbeam_rejects.csv

Comparison artifacts:

    outputs/run036_dual_receiver_comparison_summary.csv
    outputs/run036_dual_receiver_comparison_summary.json

## Receiver-Side Packet Counts

The raw log line counts were:

    RXA raw log lines: 1614
    RXB raw log lines: 1630

Because each raw CSV includes a header row, this corresponds to approximately:

    RXA raw rows after header: 1613
    RXB raw rows after header: 1629

After parsing:

    RXA valid packets: 1612
    RXA malformed rows: 1
    RXB valid packets: 1629
    RXB malformed rows: 0

All twelve transmitter identities were present in both parsed receiver logs.

## Packet Identity Matching

The dual-receiver comparison used the manifest-relative packet identity:

    tx_id
    node_id
    seq

Receiver timestamp was not used as the matching key because RXA and RXB clocks are not assumed to be synchronized.

## Dual-Receiver Overlap Result

The packet-identity comparison found:

    RXA unique packet identities: 1612
    RXB unique packet identities: 1629
    Union packet identities: 1633
    Intersection packet identities: 1608
    RXA-only packet identities: 4
    RXB-only packet identities: 21

Observation-class counts:

    both: 1608
    rxa_only: 4
    rxb_only: 21

This indicates high receiver-side overlap, but not identity-level equivalence between the two receivers.

## Per-Transmitter Packet Identity Summary

| Transmitter | Node | Union | Both | RXA-only | RXB-only |
|---|---:|---:|---:|---:|---:|
| TXA | N01 | 446 | 441 | 0 | 5 |
| TXB | N16 | 222 | 220 | 0 | 2 |
| TXC | N31 | 110 | 108 | 0 | 2 |
| TXD | N46 | 55 | 55 | 0 | 0 |
| TXE | N61 | 220 | 215 | 1 | 4 |
| TXF | N76 | 110 | 110 | 0 | 0 |
| TXG | N91 | 54 | 54 | 0 | 0 |
| TXH | N106 | 28 | 27 | 0 | 1 |
| TXI | N121 | 110 | 106 | 1 | 3 |
| TXJ | N136 | 54 | 54 | 0 | 0 |
| TXK | N151 | 196 | 190 | 2 | 4 |
| TXL | N166 | 28 | 28 | 0 | 0 |


## Manifest-Bound Validation

Each receiver log was analyzed independently against the fixed Run 035 twelve-transmitter replay manifest:

    traces/run035_reporting_reporting_schedule_manifest.json

Receiver-specific manifest-bound analysis artifacts:

    outputs/run036_dual_receiver_rxa_manifest_replay_summary.csv
    outputs/run036_dual_receiver_rxa_manifest_replay_summary.json
    outputs/run036_dual_receiver_rxa_manifest_replay_validation.json
    outputs/run036_dual_receiver_rxb_manifest_replay_summary.csv
    outputs/run036_dual_receiver_rxb_manifest_replay_summary.json
    outputs/run036_dual_receiver_rxb_manifest_replay_validation.json

Both receiver bundles passed validation:

| Receiver | Passed | Checks total | Checks passed | Checks failed |
|---|---:|---:|---:|---:|
| RXA_LORA32 | true | 321 | 321 | 0 |
| RXB_TBEAM | true | 321 | 321 | 0 |

This means both receiver-side logs are internally consistent with the manifest-bound replay-analysis bundle. It does not mean that either receiver log is ground truth for all transmitted packets.

## Receiver-Side Manifest Summary

The receiver-specific manifest summaries report:

| Transmitter | Node | Scheduled SEND rows | RXA received packets | RXB received packets |
|---|---:|---:|---:|---:|
| TXA | N01 | 64 | 441 | 446 |
| TXB | N16 | 32 | 220 | 222 |
| TXC | N31 | 16 | 108 | 110 |
| TXD | N46 | 8 | 55 | 55 |
| TXE | N61 | 32 | 216 | 219 |
| TXF | N76 | 16 | 110 | 110 |
| TXG | N91 | 8 | 54 | 54 |
| TXH | N106 | 4 | 27 | 28 |
| TXI | N121 | 16 | 107 | 109 |
| TXJ | N136 | 8 | 54 | 54 |
| TXK | N151 | 32 | 192 | 194 |
| TXL | N166 | 4 | 28 | 28 |

The strongest manifest-ratio deviation remains TXK/TXA for both receivers:

    RXA TXK/TXA observed-minus-expected: -0.0646
    RXB TXK/TXA observed-minus-expected: -0.0650

This should be interpreted as receiver-side representation relative to the manifest, not as a causal diagnosis of the physical channel.


## Common-Window Receiver Comparison

RXB logging continued slightly longer than RXA logging. To reduce start/stop truncation effects, a common-window comparison was added using only parsed packets whose `wall_time_utc` fell within the shared RXA/RXB observation interval.

Common wall-time window:

    start: 2026-07-09T13:16:48.437000+00:00
    stop:  2026-07-09T13:24:09.511000+00:00

Common-window packet identity result:

    RXA common valid packets: 1612
    RXB common valid packets: 1613
    Common union packet identities: 1617
    Common intersection packet identities: 1608
    Common RXA-only packet identities: 4
    Common RXB-only packet identities: 5

Compared with the full-log result, the common-window result reduces RXB-only packet identities from 21 to 5. This indicates that most full-log RXB-only identities were caused by RXB continuing to log after RXA had stopped, rather than by receiver disagreement during the shared observation interval.

The common-window comparison is the safer basis for paper-facing claims about RXA/RXB packet-identity overlap.

## Preliminary Interpretation

Run 036 provides dual-receiver evidence for the same fixed twelve-transmitter replay.

The two receivers observed very similar manifest-relative packet support, but they did not observe exactly the same packet identity set. RXB observed more packet identities overall, while RXA observed a small number of packet identities not observed by RXB.

This supports the paper framing that receiver-side evidence should not automatically be treated as a complete representation of the manifest-bound replay. Even under a shared replay, receiver-side observations can differ.

## Interpretation Boundaries

Receiver logs are receiver-side observations, not ground-truth transmitted-packet records.

RXA-only and RXB-only packet identities do not by themselves prove collision, interference, timing drift, transmitter failure, receiver failure, or any specific physical cause.

The result does not claim synchronized latency, LoRaWAN behavior, energy savings, airtime optimization, arbitrary-layout generalization, operational wildfire behavior, or exact transmitted-packet counts.

The result is descriptive and manifest-bound: received packets, parsed logs, comparison summaries, validation checks, and interpretation are tied back to the fixed replay manifest and receiver-side evidence.
