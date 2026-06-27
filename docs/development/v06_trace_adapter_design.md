# v0.6 Trace Adapter Design

## Purpose

The v0.6 milestone introduces a small, explicit adapter layer between belief-maintenance demand records and the compact trace-header CSV files currently used by the ESP32/LilyGO LoRa proof-of-concept firmware.

The purpose is not to change the radio experiment yet. Instead, v0.6 defines a stable intermediate format that future synthetic, AWSRT-inspired, or AWSRT-derived demand traces can map into before being reduced to the compact firmware trace format.

This keeps the current v0.5 physical replay workflow stable while preparing the repository for more realistic belief-maintenance trace sources.

## Current v0.5 State

In v0.5, Run 019 demonstrated policy-controlled synthetic trace replay.

Two trace streams were generated from the same synthetic belief-demand substrate:

* TX-A / N01 used a `fixed_all` reporting policy.
* TX-B / N16 used a `usefulness_threshold` reporting policy.

Both transmitters still sent packets once per second. The policy layer controlled the metadata content of the trace, not the physical transmission schedule.

Run 019 therefore showed that two LoRa streams can deliver nearly identical received packet counts while carrying substantially different delivered usefulness. It was not yet an airtime-saving experiment.

## Why an Adapter Layer Is Needed

The repository now has three distinct layers that should not be collapsed:

1. Synthetic or source-side belief-maintenance demand records.
2. Compact firmware trace CSV rows.
3. Transmitted receiver-row packet schema.

The compact firmware trace CSV is intentionally small:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

This is suitable for generating Arduino trace headers, but it is too narrow to preserve source-side meaning. A future source trace may include richer information, such as source timestamps, region identifiers, source policy names, scenario identifiers, or notes about how usefulness was computed.

If those source-side fields are forced directly into the compact firmware CSV, the repository loses interpretability. If the firmware CSV is expanded too early, the firmware path becomes unstable.

The adapter layer solves this by separating source demand semantics from compact packet metadata.

## Layer Model

The intended v0.6/v0.7 path is:

```text
source / belief-maintenance demand record
→ generic demand-trace schema
→ compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

In v0.6, only the first three steps are designed and lightly implemented.

The physical replay path remains unchanged.

## Generic Demand-Trace Schema

The proposed generic adapter input schema is:

```text
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_hint,source_policy,source_note
```

### Field meanings

`source_id`

: Identifier for the source trace, scenario, artifact, or generator run.

`source_time`

: Source-side time value. This may be a timestep, simulation tick, logical time, or timestamp string. It is not assumed to be synchronized with ESP32 clock time.

`demand_index`

: Monotonic source-side demand row index.

`region_id`

: Source-side region or cell identifier. This may be richer than the compact firmware field allows.

`event_type`

: Source-side event indicator. For the current compact firmware path, this must be reducible to integer `0` or `1`.

`priority`

: Numeric priority in `[0,1]`.

`usefulness`

: Numeric belief-maintenance usefulness in `[0,1]`.

`stale_after`

: Non-negative integer indicating how long the row should be considered fresh in source-side logical steps.

`policy_hint`

: Single-character compact policy code intended for firmware output, such as `F` or `U`.

`source_policy`

: Human-readable source-side policy name, such as `fixed_all` or `usefulness_threshold`.

`source_note`

: Optional note for provenance, debugging, or interpretation.

## Compact Firmware Trace Output

The adapter emits compact firmware trace CSV rows compatible with `scripts/make_trace_headers.py`:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

The conversion rules are intentionally conservative:

* `seq` is assigned by the adapter output row order.
* `region` is derived from `region_id` and must become a single character.
* `event` is derived from `event_type` and must be `0` or `1`.
* `priority` is copied and must remain in `[0,1]`.
* `usefulness` is copied and must remain in `[0,1]`.
* `stale_after` is copied and must be a non-negative integer.
* `policy` is derived from `policy_hint` and must be a single character.

These rules preserve compatibility with the existing trace-header generator.

## Policy Filtering

The first adapter script should support two simple output policies:

* `fixed_all`
* `usefulness_threshold`

For `fixed_all`, all valid input demand rows are emitted.

For `usefulness_threshold`, only rows with:

```text
usefulness >= threshold
```

are emitted.

This mirrors the Run 019 comparison while moving the input source to a more general adapter schema.

## Relationship to AWSRT-Inspired Traces

The v0.6 adapter is designed to be compatible with future AWSRT-derived outputs, but AWSRT is not required by this repository milestone.

The LoRa proof-of-concept should remain framed generically as belief-maintenance-aware reporting under constrained LoRa airtime. The adapter can be described as AWSRT-inspired because it preserves a pathway from belief-maintenance demand records into packet metadata, but the v0.6 implementation should not depend on AWSRT code, AWSRT artifacts, or a live AWSRT export.

This keeps the LoRa repository independently reproducible.

## What v0.6 Does Not Change

v0.6 does not change:

* transmitter firmware;
* receiver firmware;
* packet schema;
* radio timing;
* once-per-second transmission behaviour;
* SD-card replay;
* receiver logging;
* parsed receiver-row analysis.

Therefore, v0.6 does not claim airtime reduction or collision reduction.

Those claims require a later milestone in which physical transmission scheduling or packet skipping is changed and measured.

## Proposed v0.6 Files

The small v0.6 change set should include:

```text
docs/development/v06_trace_adapter_design.md
scripts/adapt_demand_trace.py
traces/run020_adapter_example_input.csv
traces/run020_txa_adapter_fixed_all.csv
traces/run020_txb_adapter_usefulness_threshold.csv
traces/run020_adapter_manifest.json
docs/development/run020_adapter_reproduction_commands.md
```

The generated compact CSV outputs should remain compatible with:

```bash
python scripts/make_trace_headers.py
```

## Example Command Shape

A likely adapter command is:

```bash
python scripts/adapt_demand_trace.py \
  --infile traces/run020_adapter_example_input.csv \
  --out-prefix traces/run020_adapter \
  --run-id R20 \
  --txa-policy fixed_all \
  --txb-policy usefulness_threshold \
  --threshold 0.50
```

Expected outputs:

```text
traces/run020_txa_adapter_fixed_all.csv
traces/run020_txb_adapter_usefulness_threshold.csv
traces/run020_adapter_manifest.json
```

## v0.6 Success Criteria

The v0.6 milestone is complete when:

1. The adapter design note clearly distinguishes source demand records, generic adapter rows, compact firmware trace rows, Arduino headers, transmitted packets, and parsed receiver rows.
2. A small generic adapter CSV can be converted into compact trace-header CSVs.
3. The compact outputs pass the existing `make_trace_headers.py` validation path.
4. The Run 019 interpretation remains unchanged.
5. No firmware changes are required.
6. No physical LoRa run is claimed as part of v0.6 unless explicitly added later.

## Suggested Interpretation

v0.6 should be described as a trace-interface milestone.

It prepares the repository to accept richer belief-maintenance demand traces while preserving the simple firmware replay path already validated in v0.5.

The key contribution is not new radio behaviour yet. The key contribution is making the source-to-firmware transformation explicit, auditable, and compatible with future AWSRT-like demand exports.
