# Run 039 Three-Receiver Final Experiment Design

## Purpose

Run 039 defines the final three-receiver experiment design intended to support the paper results section.

This design replaces the earlier ad hoc dual-receiver sequence with a systematic final experiment set:

- three receivers;
- three physical conditions;
- three repeated runs per condition;
- the same twelve-transmitter manifest-bound replay throughout.

## Receiver Set

The final receiver set will contain:

- RXA: LilyGo LoRa32 receiver;
- RXB: LilyGo T-Beam receiver;
- RXC: second LilyGo T-Beam receiver.

RXA preserves continuity with the earlier LoRa32 receiver. RXB and RXC provide two nominally similar T-Beam-class receivers. The purpose is not to claim calibrated hardware equivalence, but to observe whether packet identities differ across a three-receiver set.

## Fixed Experimental Elements

Across all final experiment runs, keep fixed:

- the Run 035 twelve-transmitter manifest;
- the Run 035 alternate-offset physical replay setup;
- TXK/N151 `STARTUP_OFFSET_MS = 133`;
- TXL/N166 `STARTUP_OFFSET_MS = 271`;
- all transmitter firmware and schedules;
- packet row format `RX,millis,payload,rssi,snr`;
- parser workflow;
- manifest-bound analyzer workflow;
- manifest-bundle validation workflow;
- receiver packet-identity matching key: `tx_id + node_id + seq`.

Do not introduce:

- a new manifest;
- new transmitter schedules;
- new transmitter offsets;
- AWSRT trace input;
- a controller;
- LoRaWAN behavior;
- energy, airtime, or scaling claims;
- synchronized latency claims;
- operational wildfire claims.

## Physical Conditions

The final paper experiment will use three physical conditions.

### Condition A: Close Indoor Bench

Purpose: baseline repeatability under the most controlled available setup.

Three repeats:

- Run 040: close indoor bench repeat 1
- Run 041: close indoor bench repeat 2
- Run 042: close indoor bench repeat 3

### Condition B: Indoor Residential No-Line-of-Sight

Purpose: modest indoor residential separation stress.

Approximate setup:

- receivers/transmitters separated by approximately 30 ft;
- no direct line of sight if practical;
- residential building environment.

Three repeats:

- Run 043: indoor residential NLOS repeat 1
- Run 044: indoor residential NLOS repeat 2
- Run 045: indoor residential NLOS repeat 3

### Condition C: Outdoor Residential/Treed

Purpose: larger outdoor separation while remaining practical and bounded.

Approximate setup:

- receivers/transmitters separated by approximately 300--500 m;
- residential/treed area;
- possible line of sight.

Three repeats:

- Run 046: outdoor residential/treed repeat 1
- Run 047: outdoor residential/treed repeat 2
- Run 048: outdoor residential/treed repeat 3

## Deferred Condition

A wooded forest no-line-of-sight condition is deferred from the main paper experiment.

Rationale: this condition would introduce a stronger propagation/environmental measurement component, including vegetation attenuation, terrain obstruction, antenna placement, receiver height, weather, and uncontrolled no-line-of-sight effects. It may be valuable as future work or an exploratory stress test, but it is not part of the main final experiment design.

## Primary Three-Receiver Metrics

For each run, compute:

- valid packets per receiver;
- parsed reject rows per receiver;
- manifest-bundle validation result per receiver;
- receiver union packet identities;
- packet identities observed by all three receivers;
- packet identities observed by exactly two receivers;
- packet identities observed by exactly one receiver;
- receiver-specific-only packet identities;
- per-transmitter received packet counts per receiver;
- per-transmitter manifest-ratio deviations per receiver;
- TXK/TXA deviation per receiver;
- optional descriptive RSSI/SNR summaries per receiver.

## Interpretation Boundaries

These experiments measure receiver-side evidence only.

The results should not be interpreted as:

- exact transmitted-packet counts;
- causal diagnosis of collisions;
- causal diagnosis of interference;
- causal diagnosis of wall attenuation;
- causal diagnosis of vegetation attenuation;
- causal diagnosis of antenna effects;
- causal diagnosis of transmitter or receiver failure;
- synchronized latency;
- LoRaWAN behavior;
- energy savings;
- airtime optimization;
- network scaling;
- operational wildfire performance.

The paper-facing claim remains narrower: under fixed manifest-bound LoRa replay, receiver-side report preservation is an observed, manifest-relative property that can be compared across receivers and physical conditions.

## Expected Final Paper Result

The expected final results section should be organized around three conditions and three repeats per condition, not around individual ad hoc runs.

The central table should report, for each condition and repeat:

- RXA valid packets;
- RXB valid packets;
- RXC valid packets;
- receiver union identities;
- identities observed by all three receivers;
- identities observed by exactly two receivers;
- identities observed by exactly one receiver.

A second table should report manifest-ratio preservation, especially TXK/TXA, across receivers and conditions.
