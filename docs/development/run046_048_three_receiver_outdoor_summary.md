# Runs 046--048 Three-Receiver Outdoor Summary

## Purpose

Runs 046--048 form the outdoor residential/treed condition in the final three-receiver replay design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

Due to field logistics, the three outdoor repeats were captured before the Git branch and per-run prep notes were created. The raw logs were recovered, renamed into the intended Run 046--048 sequence, parsed, analyzed, and validated on the recovery branch.

The replay manifest, transmitter firmware, transmitter offsets, receiver identities, parsing method, matching key, and validation workflow were held fixed from the close indoor bench and indoor NLOS conditions.

Matching key:

    tx_id, node_id, seq

## Runs

| Run | Condition | Repeat |
|---|---|---:|
| 046 | outdoor residential/treed possible LOS | 1 |
| 047 | outdoor residential/treed possible LOS | 2 |
| 048 | outdoor residential/treed possible LOS | 3 |

## Raw Receiver Log Counts

| Run | RXA raw lines | RXB raw lines | RXC raw lines |
|---|---:|---:|---:|
| 046 | 1404 | 1050 | 1724 |
| 047 | 1374 | 1119 | 1631 |
| 048 | 1311 | 999 | 1490 |

## Common-Window Three-Receiver Summary

| Run | RXA valid | RXB valid | RXC valid | Union | All three | Exactly two | Exactly one |
|---|---:|---:|---:|---:|---:|---:|---:|
| 046 | 1403 | 1047 | 1722 | 1726 | 977 | 492 | 257 |
| 047 | 1373 | 1118 | 1629 | 1645 | 1038 | 399 | 208 |
| 048 | 1310 | 997 | 1487 | 1502 | 907 | 478 | 117 |

## Receiver-Specific-Only Packet Identities

| Run | RXA-only | RXB-only | RXC-only |
|---|---:|---:|---:|
| 046 | 2 | 1 | 254 |
| 047 | 5 | 6 | 197 |
| 048 | 2 | 6 | 109 |

## Manifest Validation

All receiver-specific replay bundles passed manifest validation.

| Run | RXA validation | RXB validation | RXC validation |
|---|---|---|---|
| 046 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |
| 047 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |
| 048 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |

## TXK/TXA Ratio

The expected manifest TXK/TXA ratio is 0.5.

| Run | RXA observed | RXB observed | RXC observed |
|---|---:|---:|---:|
| 046 | 0.43859649122807015 | 0.11217183770883055 | 0.4355179704016913 |
| 047 | 0.42207792207792205 | 0.2869757174392936 | 0.421505376344086 |
| 048 | 0.4177777777777778 | 0.3608490566037736 | 0.43013100436681223 |

## Interpretation

The outdoor residential/treed condition is the strongest receiver-side stress condition in the final three-receiver design.

All receiver-specific manifest replay bundles validate cleanly, so the replay evidence remains manifest-bound. However, the receiver-set structure is much less uniform than in the close indoor bench and indoor NLOS conditions.

Across all three outdoor repeats, RXB records substantially fewer packets than RXA and RXC. RXC accounts for most receiver-specific-only packet identities. This pattern is especially visible in the common-window comparisons, where RXC-only packet identities dominate the exactly-one class.

The outdoor condition therefore supports the paper's central measurement claim: receiver-side report preservation is an observed, manifest-relative property. The manifest structure remains visible, but it is not identically preserved at every receiver under a more stressful physical condition.

These results remain descriptive receiver-side evidence. They do not by themselves identify path loss, antenna placement, receiver sensitivity, interference, collision, timing drift, or any other physical cause.
