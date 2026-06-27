# Run 020 Adapter Reproduction Commands

## Purpose

Run 020 is a v0.6 design-stage adapter check.

It demonstrates that a generic belief-maintenance demand-trace CSV can be converted into compact firmware trace CSVs that remain compatible with the existing Arduino trace-header generation path.

This is not a physical LoRa run.

No firmware, SD-card replay, radio timing, or receiver logging changes are made in this step.

## Branch

```text
exp021-v06-trace-adapter-design
```

## Input

Generic adapter input:

```text
traces/run020_adapter_example_input.csv
```

Generic adapter input schema:

```text
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_hint,source_policy,source_note
```

## Adapter Command

```bash
python scripts/adapt_demand_trace.py \
  --infile traces/run020_adapter_example_input.csv \
  --out-prefix traces/run020_adapter \
  --run-id R20 \
  --txa-policy fixed_all \
  --txb-policy usefulness_threshold \
  --threshold 0.50
```

## Expected Adapter Output

```text
Read generic demand rows: 16
Wrote TX-A compact trace: traces/run020_adapter_txa_fixed_all.csv (16 rows)
Wrote TX-B compact trace: traces/run020_adapter_txb_usefulness_threshold.csv (8 rows)
Wrote adapter manifest:  traces/run020_adapter_manifest.json
```

Generated compact trace files:

```text
traces/run020_adapter_txa_fixed_all.csv
traces/run020_adapter_txb_usefulness_threshold.csv
```

Generated manifest:

```text
traces/run020_adapter_manifest.json
```

## Compact Trace Schema

The adapter emits compact firmware trace CSVs with the existing schema:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

These files are intended to remain compatible with:

```text
scripts/make_trace_headers.py
```

## Header-Generation Validation

Validate TX-A:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txa_fixed_all.csv \
  --outfile /tmp/trace_data_TXA_adapter_test.h
```

Expected output:

```text
Wrote /tmp/trace_data_TXA_adapter_test.h
```

Validate TX-B:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txb_usefulness_threshold.csv \
  --outfile /tmp/trace_data_TXB_adapter_test.h
```

Expected output:

```text
Wrote /tmp/trace_data_TXB_adapter_test.h
```

## Header Inspection

Inspect the temporary headers:

```bash
head -40 /tmp/trace_data_TXA_adapter_test.h
head -40 /tmp/trace_data_TXB_adapter_test.h
```

Expected header properties:

```text
TX-A TRACE_ROW_COUNT = 16
TX-A policy code = F

TX-B TRACE_ROW_COUNT = 8
TX-B policy code = U
```

## Interpretation

Run 020 confirms the source-to-compact-trace adapter path:

```text
generic belief-maintenance demand trace
→ compact firmware trace CSV
→ Arduino-compatible trace header
```

This is a trace-interface milestone, not a physical experiment.

The result prepares the repository for future AWSRT-inspired or AWSRT-derived demand traces without making AWSRT a dependency of the LoRa proof-of-concept.

## Cautions

Do not interpret Run 020 as evidence of LoRa airtime reduction.

Do not interpret Run 020 as evidence of collision reduction.

Do not compare `recv_ms` and `tx_ms`; no receiver/transmitter clock synchronization is involved.

Do not change firmware for this milestone unless a later step explicitly requires it.

Run 020 only shows that richer generic demand records can be reduced into the compact trace format already used by the current firmware workflow.
