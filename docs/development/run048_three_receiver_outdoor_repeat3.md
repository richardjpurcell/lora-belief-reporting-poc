# Run 048 Three-Receiver Outdoor Repeat 3

## Purpose

Run 048 is the third outdoor residential/treed repeat in the final three-receiver replay design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

The replay manifest, transmitter firmware, transmitter offsets, receiver identities, parsing method, matching key, and validation workflow are held fixed from the close indoor bench and indoor NLOS conditions.

Matching key:

    tx_id, node_id, seq

## Logistics Note

Due to field logistics, Runs 046--048 were captured before the Git branch and per-run prep notes were created. The raw logs were recovered onto this branch before parsing and analysis.

## Results Summary

Run 048 completed the third outdoor residential/treed repeat in the final three-receiver design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1311 | 1310 |
| RXB_TBEAM | 999 | 998 |
| RXC_TBEAM | 1490 | 1489 |

Parsed valid packet counts:

| Receiver | Parsed valid rows | Reject rows |
|---|---:|---:|
| RXA_LORA32 | 1310 | 0 |
| RXB_TBEAM | 998 | 0 |
| RXC_TBEAM | 1489 | 0 |

All reject files contained headers only.

### Three-Receiver Packet-Identity Comparison

Common-window comparison:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1310 |
| RXB unique packet identities | 997 |
| RXC unique packet identities | 1487 |
| Union packet identities | 1502 |
| Observed by all three receivers | 907 |
| Observed by exactly two receivers | 478 |
| Observed by exactly one receiver | 117 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 2 |
| RXB_TBEAM | 6 |
| RXC_TBEAM | 109 |

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
| RXA_LORA32 | 0.4177777777777778 | -0.0822222222222222 |
| RXB_TBEAM | 0.3608490566037736 | -0.1391509433962264 |
| RXC_TBEAM | 0.43013100436681223 | -0.06986899563318777 |

### Interpretation

Run 048 completes the outdoor residential/treed condition. It preserves the same broad pattern as Runs 046 and 047, but with fewer exactly-one packet identities than the first two outdoor repeats.

RXC again accounts for most receiver-specific-only packet identities. RXB again has the lowest parsed packet count. The manifest validation remains clean, but receiver-side preservation is much less uniform than in the close indoor bench and indoor NLOS conditions.
