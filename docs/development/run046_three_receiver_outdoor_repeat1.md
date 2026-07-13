# Run 046 Three-Receiver Outdoor Repeat 1

## Purpose

Run 046 is the first outdoor residential/treed repeat in the final three-receiver replay design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

The replay manifest, transmitter firmware, transmitter offsets, receiver identities, parsing method, matching key, and validation workflow are held fixed from the close indoor bench and indoor NLOS conditions.

Matching key:

    tx_id, node_id, seq

## Logistics Note

Due to field logistics, Runs 046--048 were captured before the Git branch and per-run prep notes were created. The raw logs were recovered onto this branch before parsing and analysis.

## Results Summary

Run 046 completed the first outdoor residential/treed repeat in the final three-receiver design.

Condition description:

    Outdoor residential/treed path, approximately 300--500 m separation, possible line of sight.

Raw receiver log line counts:

| Receiver | Raw log lines | Approx. data rows |
|---|---:|---:|
| RXA_LORA32 | 1404 | 1403 |
| RXB_TBEAM | 1050 | 1049 |
| RXC_TBEAM | 1724 | 1723 |

Parsed valid packet counts:

| Receiver | Parsed valid rows | Reject rows |
|---|---:|---:|
| RXA_LORA32 | 1403 | 0 |
| RXB_TBEAM | 1047 | 2 |
| RXC_TBEAM | 1723 | 0 |

RXB had two malformed rows during parsing. The other reject files contained headers only.

### Three-Receiver Packet-Identity Comparison

Common-window comparison:

| Metric | Value |
|---|---:|
| RXA unique packet identities | 1403 |
| RXB unique packet identities | 1047 |
| RXC unique packet identities | 1722 |
| Union packet identities | 1726 |
| Observed by all three receivers | 977 |
| Observed by exactly two receivers | 492 |
| Observed by exactly one receiver | 257 |

Receiver-specific-only packet identities:

| Receiver | Receiver-specific-only identities |
|---|---:|
| RXA_LORA32 | 2 |
| RXB_TBEAM | 1 |
| RXC_TBEAM | 254 |

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
| RXA_LORA32 | 0.43859649122807015 | -0.06140350877192985 |
| RXB_TBEAM | 0.11217183770883055 | -0.38782816229116945 |
| RXC_TBEAM | 0.4355179704016913 | -0.0644820295983087 |

### Interpretation

Run 046 is a substantially more stressful receiver-side condition than the close indoor bench and indoor NLOS runs. The manifest-bound replay structure remains validation-clean, but the receiver-set packet identity structure changes sharply.

RXC observed many packet identities not observed by RXA or RXB. RXB also showed much lower parsed packet counts and a severe TXK/TXA ratio distortion. This should be treated as descriptive receiver-side evidence, not as a physical-cause diagnosis.
