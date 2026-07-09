# Run 036 Dual-Receiver Design

## Purpose

Run 036 prepares a dual-receiver diagnostic for the twelve-transmitter manifest-bound LoRa replay. The scientific question is:

> Given the same structured twelve-transmitter replay, do two independent physical receivers observe the same report structure?

The experiment keeps the replay manifest fixed so that RXA/RXB differences can be interpreted as receiver-side observation differences rather than changes in the manifest, transmitter schedule, reporting policy, or replay structure.

## Hardware Roles

Run 036 uses two receivers:

- RXA: original LilyGo LoRa32 receiver.
- RXB: LilyGo T-Beam receiver.

The original LoRa32 receiver is retained as RXA because it preserves continuity with the Run 035 twelve-transmitter alternate-offset replay. The T-Beam is introduced as RXB to create an independent second receiver path before attempting any later matched T-Beam/T-Beam experiment.

## Receiver Sketches

The historical receiver sketch is preserved unchanged:

    firmware/first_radio_link_RX/first_radio_link_RX.ino

Run 036 adds two explicit receiver sketches:

    firmware/first_radio_link_RX_A_LORA32/first_radio_link_RX_A_LORA32.ino
    firmware/first_radio_link_RX_B_TBEAM/first_radio_link_RX_B_TBEAM.ino

Expected receiver identities are:

    RXA_LORA32
    RXB_TBEAM

## Parser Compatibility Decision

The packet data row format is intentionally preserved:

    RX,millis,payload,rssi,snr

Receiver identity is not added to packet rows in this design milestone. Receiver identity is carried by the log filename and startup/banner lines. This avoids changing the existing parser before the first dual-receiver capture.

Expected Run 036 raw log names are:

    logs/rx_run_036_dual_receiver_rxa_lora32.csv
    logs/rx_run_036_dual_receiver_rxb_tbeam.csv

## Radio Settings

The legacy receiver sketch explicitly sets the LoRa band to 915 MHz and uses the existing sketch/library defaults for other LoRa settings unless changed elsewhere.

The Run 036 design does not introduce new spreading-factor, bandwidth, coding-rate, or sync-word settings. This preserves continuity with the Run 035 receiver behavior.

The RXB T-Beam pin mapping is a design setting to verify during upload/test. The T-Beam has not yet been flashed in this repository workflow, so v5.17 does not treat RXB operation as experimentally validated.

## Planned Packet Matching

Run 036 analysis should parse each receiver log back to manifest rows using transmitter identity and sequence number.

For each manifest-expected SEND opportunity, packets can then be classified as:

- observed by RXA only;
- observed by RXB only;
- observed by both receivers;
- observed by neither receiver, relative to manifest expectation.

The first matching key should be manifest-relative packet identity rather than receiver timestamp. Receiver timestamps are useful receiver-side metadata, but Run 036 should not claim synchronized latency unless a separate synchronization method is introduced and validated.

## Metrics to Prioritize

Run 036 should prioritize:

- RXA-only packet identities;
- RXB-only packet identities;
- packet identities observed by both receivers;
- manifest-expected SEND opportunities observed by neither receiver;
- receiver-side union;
- receiver-side intersection;
- per-receiver transmitter representation;
- per-receiver report-class preservation;
- divergence between RXA and RXB observed report distributions.

Possible later report-class groupings include transmitter identity, priority, freshness window, policy label, usefulness metadata, and manifest-defined report class.

## Interpretation Boundaries

Receiver logs are receiver-side observations, not ground-truth transmitted-packet records.

Missing sequence numbers mean packets were not received or not logged by that receiver within the observed sequence range. Missing packets do not by themselves prove collision, interference, timing drift, transmitter failure, receiver failure, or any specific physical cause.

Preservation metrics are descriptive, not causal.

Run 036 does not claim LoRaWAN behavior, energy savings, airtime optimization, synchronized latency, arbitrary-layout generalization, operational wildfire behavior, or validation of exact transmitted-packet counts.

The experiment remains manifest-bound and manifest-relative. Replay execution, received packets, parsed logs, summaries, validation checks, and interpretation should all tie back to the fixed replay manifest.

## Near-Term Workflow

The v5.17 milestone prepares the dual-receiver design only. It does not run the physical replay.

The next physical milestone should capture the same twelve-transmitter replay with both receivers active and write separate RXA/RXB logs for manifest-bound comparison.
