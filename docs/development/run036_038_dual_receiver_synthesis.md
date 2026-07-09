# Run 036--038 Dual-Receiver Synthesis

## Purpose

This note consolidates the dual-receiver physical replay results from Runs 036--038.

The purpose is to provide a paper-facing synthesis of receiver-side report preservation under:

- an initial dual-receiver physical replay;
- common-window correction for unequal logger stop times;
- an unchanged repeat run;
- a modest indoor placement variation.

This synthesis remains descriptive and manifest-relative. It does not infer exact transmitted-packet counts or physical causes.

## Experimental Sequence

| Run | Milestone | Purpose | Changed variable |
|---|---|---|---|
| Run 036 | `v5.19-run036-dual-receiver-physical-replay` | First dual-receiver observation of the twelve-transmitter replay | Added second receiver |
| Run 036 common-window | `v5.20-run036-common-window-analysis` | Correct full-log comparison for unequal logger stop times | Analysis window only |
| Run 037 | `v5.21-run037-dual-receiver-repeat` | Repeat Run 036 without changing setup | Repeat capture |
| Run 038 | `v5.22-run038-dual-receiver-placement-variation` | Repeat with modest indoor placement/separation change | Receiver/transmitter placement |

## Common-Window Packet Identity Comparison

Packet identities are matched by:

    tx_id + node_id + seq

| Run | RXA unique identities | RXB unique identities | Union identities | Both receivers | RXA-only | RXB-only |
|---|---:|---:|---:|---:|---:|---:|
| Run 036 common-window | 1612 | 1613 | 1617 | 1608 | 4 | 5 |
| Run 037 common-window | 1571 | 1586 | 1589 | 1568 | 3 | 18 |
| Run 038 placement | 1522 | 1531 | 1536 | 1517 | 5 | 14 |

## Manifest-Bound Validation

Each receiver-specific manifest replay bundle passed validation.

| Run | RXA validation | RXB validation |
|---|---:|---:|
| Run 036 | 321 / 321 | 321 / 321 |
| Run 037 | 321 / 321 | 321 / 321 |
| Run 038 | 321 / 321 | 321 / 321 |

## Manifest-Ratio Deviations

The strongest repeated manifest-ratio deviation across the dual-receiver runs is TXK/TXA.

| Run | Receiver | TXK/TXA expected | TXK/TXA observed | Observed minus expected |
|---|---|---:|---:|---:|
| Run 036 | RXA_LORA32 | 0.5000 | 0.4354 | -0.0646 |
| Run 036 | RXB_TBEAM | 0.5000 | 0.4350 | -0.0650 |
| Run 037 | RXA_LORA32 | 0.5000 | 0.4439 | -0.0561 |
| Run 037 | RXB_TBEAM | 0.5000 | 0.4365 | -0.0635 |
| Run 038 | RXA_LORA32 | 0.5000 | 0.4316 | -0.0684 |
| Run 038 | RXB_TBEAM | 0.5000 | 0.4366 | -0.0634 |

Run 038 also showed strong TXH/TXA under-preservation under the placement-variation condition.

| Run | Receiver | TXH/TXA expected | TXH/TXA observed | Observed minus expected |
|---|---|---:|---:|---:|
| Run 038 | RXA_LORA32 | 0.0625 | 0.0071 | -0.0554 |
| Run 038 | RXB_TBEAM | 0.0625 | 0.0023 | -0.0602 |

## Interpretation

Across Runs 036--038, the two receivers produced high packet-identity overlap, but not identity-level equivalence.

The common-window Run 036 comparison showed that most of the full-log RXB-only identities were due to RXB continuing to log after RXA stopped. After common-window correction, Run 036 had 1608 shared packet identities, with 4 RXA-only and 5 RXB-only identities.

Run 037 repeated the same setup and again showed high overlap, with 1568 shared packet identities in the common observation window, 3 RXA-only identities, and 18 RXB-only identities.

Run 038 changed the indoor placement/separation condition. It again showed high overlap, with 1517 shared packet identities, 5 RXA-only identities, and 14 RXB-only identities. The total number of observed packet identities decreased relative to the earlier bench runs, while the overall dual-receiver pattern remained visible.

Together, these runs support a bounded claim: under a fixed manifest-bound twelve-transmitter LoRa replay, receiver-side observations can preserve the broad manifest-relative report structure while still differing at the individual packet-identity level.

## Paper-Facing Claim

A suitable paper-facing statement is:

> Across three dual-receiver replay analyses, receiver-side logs showed high packet-identity overlap but not identity-level equivalence. Common-window comparisons found 1608, 1568, and 1517 packet identities observed by both receivers in Runs 036, 037, and 038, respectively, with small but nonzero receiver-specific packet identities in each run. This supports treating receiver-side report preservation as an observed, manifest-relative property rather than assuming that a planned reporting structure is identically preserved at every receiver.

## Boundaries

These results should not be interpreted as:

- a causal diagnosis of collisions, interference, wall attenuation, antenna behavior, timing drift, transmitter failure, or receiver failure;
- a ground-truth transmitted-packet record;
- a LoRaWAN result;
- an energy or airtime-optimization result;
- a synchronized latency result;
- a general indoor propagation study;
- an operational wildfire sensing result.

The correct interpretation is narrower: these are receiver-side observations from a small-scale manifest-bound LoRa replay testbed.
