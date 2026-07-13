# Run 047 Three-Receiver Outdoor Repeat 2

## Purpose

Run 047 is the second outdoor residential/treed repeat in the final three-receiver replay design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

The replay manifest, transmitter firmware, transmitter offsets, receiver identities, parsing method, matching key, and validation workflow are held fixed from the close indoor bench and indoor NLOS conditions.

Matching key:

    tx_id, node_id, seq

## Logistics Note

Due to field logistics, Runs 046--048 were captured before the Git branch and per-run prep notes were created. The raw logs were recovered onto this branch before parsing and analysis.

## Results Summary

Run 047 completed the second outdoor residential/treed repeat in the final three-receiver design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1374 | 1373 |
| RXB_TBEAM | 1119 | 1118 |
| RXC_TBEAM | 1631 | 1630 |

Parsed valid packet counts:

| Receiver | Parsed valid rows | Reject rows |
|---|---:|---:|
| RXA_LORA32 | 1373 | 0 |
| RXB_TBEAM | 1118 | 0 |
| RXC_TBEAM | 1630 | 0 |

All reject files contained headers only.

### Three-Receiver Packet-Identity Comparison

Common-window comparison:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1373 |
| RXB unique packet identities | 1118 |
| RXC unique packet identities | 1629 |
| Union packet identities | 1645 |
| Observed by all three receivers | 1038 |
| Observed by exactly two receivers | 399 |
| Observed by exactly one receiver | 208 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 5 |
| RXB_TBEAM | 6 |
| RXC_TBEAM | 197 |

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
| RXA_LORA32 | 0.42207792207792205 | -0.07792207792207795 |
| RXB_TBEAM | 0.2869757174392936 | -0.2130242825607064 |
| RXC_TBEAM | 0.421505376344086 | -0.078494623655914 |

### Interpretation

Run 047 repeats the main outdoor pattern from Run 046. The replay remains manifest-bound and validation-clean, but the receiver-side evidence again shows strong receiver-set divergence.

RXC again accounts for most receiver-specific-only packet identities. RXB remains weaker than RXA and RXC in packet count and shows a larger TXK/TXA distortion than the other receivers. This remains descriptive receiver-side evidence only.
