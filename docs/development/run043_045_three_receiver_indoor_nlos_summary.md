# Runs 043--045 Three-Receiver Indoor NLOS Summary

## Purpose

Runs 043--045 form the indoor residential no-line-of-sight condition in the final three-receiver replay design.

The purpose of this condition is to test whether receiver-side evidence preserves the manifest-bound replay structure when the receivers are separated indoors with no direct line of sight.

Condition description:

    Indoor residential no-line-of-sight, approximately 30 ft separation, no direct line of sight.

The replay manifest, transmitter firmware, transmitter offsets, receiver identities, parsing method, matching key, and validation workflow were held fixed from the close indoor bench condition.

Matching key:

    tx_id, node_id, seq

## Runs

| Run | Tag | Condition | Repeat |
|---|---|---|---:|
| 043 | v5.29-three-receiver-indoor-nlos-repeat1 | indoor residential NLOS | 1 |
| 044 | v5.30-three-receiver-indoor-nlos-repeat2 | indoor residential NLOS | 2 |
| 045 | v5.31-three-receiver-indoor-nlos-repeat3 | indoor residential NLOS | 3 |

## Common-Window Three-Receiver Summary

| Run | RXA valid | RXB valid | RXC valid | Union | All three | Exactly two | Exactly one |
|---|---:|---:|---:|---:|---:|---:|---:|
| 043 | 1667 | 1647 | 1654 | 1680 | 1628 | 32 | 20 |
| 044 | 1667 | 1624 | 1655 | 1670 | 1617 | 42 | 11 |
| 045 | 1672 | 1636 | 1675 | 1682 | 1620 | 61 | 1 |

## Receiver-Specific-Only Packet Identities

| Run | RXA-only | RXB-only | RXC-only |
|---|---:|---:|---:|
| 043 | 18 | 0 | 2 |
| 044 | 11 | 0 | 0 |
| 045 | 0 | 0 | 1 |

## Exactly-Two Pair Counts

| Run | RXA+RXB | RXA+RXC | RXB+RXC |
|---|---:|---:|---:|
| 043 | 8 | 13 | 11 |
| 044 | 4 | 35 | 3 |
| 045 | 7 | 45 | 9 |

## TXH/N106 Receiver-Set Pattern

TXH/N106 repeatedly stands out in the indoor NLOS condition.

| Run | TXH union | TXH all three | TXH exactly two | TXH exactly one |
|---|---:|---:|---:|---:|
| 043 | 28 | 0 | 9 | 19 |
| 044 | 28 | 0 | 17 | 11 |
| 045 | 29 | 0 | 28 | 1 |

Across all three indoor NLOS repeats, TXH/N106 appears in the receiver-side evidence but has zero packet identities observed by all three receivers.

## Manifest Validation

All receiver-specific replay bundles passed manifest validation.

| Run | RXA validation | RXB validation | RXC validation |
|---|---|---|---|
| 043 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |
| 044 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |
| 045 | 321 / 321 passed | 321 / 321 passed | 321 / 321 passed |

## Interpretation

The indoor NLOS condition preserves the manifest-bound replay structure strongly enough for all receiver-specific replay bundles to validate cleanly.

However, compared with the close indoor bench condition, the indoor NLOS condition introduces more visible receiver-set structure. Runs 043, 044, and 045 all include packet identities observed by exactly one receiver, although the count decreases across the three repeats.

The repeated TXH/N106 pattern is the clearest condition-level observation. In all three indoor NLOS repeats, TXH/N106 has no packet identities observed by all three receivers. This supports treating receiver-side report preservation as a manifest-relative observed property rather than assuming that the manifest structure is identically visible at every receiver.

This remains descriptive receiver-side evidence. These runs do not identify the physical cause of the receiver-set differences.
