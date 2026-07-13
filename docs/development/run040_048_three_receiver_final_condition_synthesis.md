# Runs 040--048 Three-Receiver Final Condition Synthesis

## Purpose

Runs 040--048 form the final three-receiver physical replay experiment.

The experiment compares receiver-side report preservation across three physical conditions while holding the replay manifest, transmitter firmware, transmitter offsets, receiver identities, parser, matching key, and validation workflow fixed.

Matching key:

    tx_id, node_id, seq

The purpose is not to identify physical causes such as collisions, path loss, antenna effects, receiver sensitivity, or interference. The purpose is to measure whether the manifest-bound reporting structure remains visible in receiver-side LoRa replay evidence, and whether that structure is identically preserved across receivers and conditions.

## Conditions

| Condition | Runs | Description |
|---|---|---|
| A | 040--042 | Close indoor bench |
| B | 043--045 | Indoor residential no-line-of-sight, approximately 30 ft |
| C | 046--048 | Outdoor residential/treed path, approximately 300--500 m, possible line of sight |

## Common-Window Three-Receiver Summary

| Condition | Run | RXA valid | RXB valid | RXC valid | Union | All three | Exactly two | Exactly one |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A close indoor bench | 040 | 1744 | 1765 | 1763 | 1773 | 1728 | 43 | 2 |
| A close indoor bench | 041 | 1606 | 1622 | 1617 | 1628 | 1589 | 39 | 0 |
| A close indoor bench | 042 | 1650 | 1673 | 1675 | 1680 | 1638 | 42 | 0 |
| B indoor residential NLOS | 043 | 1667 | 1647 | 1654 | 1680 | 1628 | 32 | 20 |
| B indoor residential NLOS | 044 | 1667 | 1624 | 1655 | 1670 | 1617 | 42 | 11 |
| B indoor residential NLOS | 045 | 1672 | 1636 | 1675 | 1682 | 1620 | 61 | 1 |
| C outdoor residential/treed | 046 | 1403 | 1047 | 1722 | 1726 | 977 | 492 | 257 |
| C outdoor residential/treed | 047 | 1373 | 1118 | 1629 | 1645 | 1038 | 399 | 208 |
| C outdoor residential/treed | 048 | 1310 | 997 | 1487 | 1502 | 907 | 478 | 117 |

## Receiver-Specific-Only Packet Identities

| Condition | Run | RXA-only | RXB-only | RXC-only |
|---|---|---:|---:|---:|
| A close indoor bench | 040 | 0 | 0 | 2 |
| A close indoor bench | 041 | 0 | 0 | 0 |
| A close indoor bench | 042 | 0 | 0 | 0 |
| B indoor residential NLOS | 043 | 18 | 0 | 2 |
| B indoor residential NLOS | 044 | 11 | 0 | 0 |
| B indoor residential NLOS | 045 | 0 | 0 | 1 |
| C outdoor residential/treed | 046 | 2 | 1 | 254 |
| C outdoor residential/treed | 047 | 5 | 6 | 197 |
| C outdoor residential/treed | 048 | 2 | 6 | 109 |

## Condition-Level Pattern

The three conditions show increasing receiver-side divergence.

| Condition | Runs | Exactly-one range | Main receiver-specific pattern |
|---|---|---:|---|
| A close indoor bench | 040--042 | 0--2 | Almost no receiver-specific-only packet identities |
| B indoor residential NLOS | 043--045 | 1--20 | Small receiver-specific-only counts; TXH/N106 repeatedly has zero all-three identities |
| C outdoor residential/treed | 046--048 | 117--257 | Large exactly-one counts dominated by RXC-only identities; RXB records fewer packets |

## Manifest Validation

All receiver-specific replay bundles passed manifest validation across all final-condition runs.

| Condition | Runs | Receiver-specific validations |
|---|---|---|
| A close indoor bench | 040--042 | all RXA/RXB/RXC bundles passed 321 / 321 checks |
| B indoor residential NLOS | 043--045 | all RXA/RXB/RXC bundles passed 321 / 321 checks |
| C outdoor residential/treed | 046--048 | all RXA/RXB/RXC bundles passed 321 / 321 checks |

## TXK/TXA Ratio

The expected manifest TXK/TXA ratio is 0.5.

| Condition | Run | RXA observed | RXB observed | RXC observed |
|---|---|---:|---:|---:|
| A close indoor bench | 040 | 0.4306418219461698 | 0.4315352697095436 | 0.4306418219461698 |
| A close indoor bench | 041 | 0.435665914221219 | 0.43243243243243246 | 0.4401805869074492 |
| A close indoor bench | 042 | 0.43231441048034935 | 0.437636761487965 | 0.44273127753303965 |
| B indoor residential NLOS | 043 | 0.4392935982339956 | 0.4407894736842105 | 0.43736263736263736 |
| B indoor residential NLOS | 044 | 0.43736263736263736 | 0.44543429844098 | 0.43956043956043955 |
| B indoor residential NLOS | 045 | 0.437636761487965 | 0.4398249452954048 | 0.4389978213507625 |
| C outdoor residential/treed | 046 | 0.43859649122807015 | 0.11217183770883055 | 0.4355179704016913 |
| C outdoor residential/treed | 047 | 0.42207792207792205 | 0.2869757174392936 | 0.421505376344086 |
| C outdoor residential/treed | 048 | 0.4177777777777778 | 0.3608490566037736 | 0.43013100436681223 |

Across Conditions A and B, TXK/TXA remains consistently below the expected manifest ratio but is similar across receivers. In Condition C, RXA and RXC remain in the same broad below-expected range, while RXB shows much stronger TXK/TXA distortion.

## Paper-Facing Interpretation

Across the final three-receiver experiment, the manifest-bound replay structure remains visible in receiver-side evidence: all receiver-specific manifest bundles pass validation, and the planned transmitter roles and ratios can still be summarized from the receiver logs.

However, the structure is not identically preserved across receivers or physical conditions. The close indoor bench condition shows high three-receiver overlap. The indoor residential NLOS condition introduces modest receiver-specific structure and a repeated TXH/N106 pattern. The outdoor residential/treed condition produces substantially stronger receiver-side asymmetry, including large RXC-only exactly-one counts and lower RXB packet counts.

These results support treating report preservation as an observed, manifest-relative property. A replay manifest can specify intended reporting structure, but receiver-side logs show how that structure is preserved, distorted, or unevenly visible under physical replay conditions.

## Interpretation Boundary

These results are descriptive receiver-side measurements. They do not by themselves identify the physical causes of packet differences. In particular, they should not be interpreted as proving path loss, antenna effects, receiver sensitivity differences, collisions, interference, timing drift, energy effects, LoRaWAN behavior, or live-controller behavior.

The contribution is the manifest-bound measurement method and the receiver-side evidence it produces.
