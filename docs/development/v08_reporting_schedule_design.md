# v0.8 Reporting-Schedule Design

## Purpose

The v0.8 milestone begins the transition from metadata-only policy traces toward constrained-airtime reporting.

Previous milestones showed that belief-maintenance usefulness metadata can be generated, adapted, compiled into firmware headers, physically replayed over point-to-point LoRa, logged by the receiver, and analyzed after reception.

The v0.8 goal is to define a reporting-schedule layer that can distinguish demand records that are selected for transmission from demand records that are skipped.

This milestone is design-first. It should not yet be interpreted as evidence of airtime savings unless a later physical run changes transmission behaviour and measures the resulting packet counts.

## Background

In v0.5 and v0.7, both transmitters still sent packets once per second.

The policy layer changed the metadata carried in packets, not the physical transmission schedule. As a result, those experiments demonstrated delivery-versus-usefulness separation, but not airtime reduction.

To study constrained LoRa airtime, the repository now needs an explicit reporting decision layer.

## Layer Model

The intended v0.8 path is:

```text
source / belief-maintenance demand record
→ generic demand-trace schema
→ reporting schedule schema
→ compact firmware trace CSV containing SEND rows only
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

This separates four concepts that should not be collapsed:

1. Demand rows: source-side opportunities or reasons to report.
2. Reporting schedule rows: decisions about whether each demand row should be sent or skipped.
3. Compact firmware trace rows: metadata for rows selected for transmission.
4. Receiver rows: packets physically received and logged.

## Reporting Decision Semantics

Each generic demand row receives a reporting decision:

```text
SEND
SKIP
```

A `SEND` row is eligible to become a transmitted packet.

A `SKIP` row is retained in the schedule and manifest for analysis, but it is not included in the compact firmware trace CSV.

This means the compact firmware trace CSV remains a transmitted-packet metadata file, not a complete demand file.

## Proposed Reporting-Schedule Schema

The reporting schedule should preserve the source-side demand context and add explicit reporting-decision fields.

Proposed schema:

```text
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_name,policy_code,decision,decision_reason
```

Field meanings:

`source_id`

: Identifier for the source trace, scenario, artifact, or generator run.

`source_time`

: Source-side logical time, simulation tick, or timestamp.

`demand_index`

: Monotonic source-side demand row index.

`region_id`

: Source-side region or cell identifier.

`event_type`

: Event indicator reducible to the compact firmware `event` field.

`priority`

: Priority in `[0,1]`.

`usefulness`

: Belief-maintenance usefulness in `[0,1]`.

`stale_after`

: Non-negative source-side freshness horizon.

`policy_name`

: Human-readable reporting policy name.

`policy_code`

: Single-character compact code, such as `F`, `U`, or a future airtime-aware code.

`decision`

: Either `SEND` or `SKIP`.

`decision_reason`

: Short human-readable reason for the decision.

## Candidate Policies

The first reporting-schedule implementation should support simple, auditable policies:

### fixed_all

Every demand row is marked `SEND`.

This reproduces the current all-reporting behaviour.

### usefulness_threshold

Rows with usefulness greater than or equal to a threshold are marked `SEND`.

Rows below the threshold are marked `SKIP`.

This is the first simple constrained-reporting policy.

### top_k_per_window

Within each source-side window, only the top `k` rows by usefulness are marked `SEND`.

This policy is useful for later experiments because it creates an explicit reporting budget.

For the first v0.8 implementation, `fixed_all` and `usefulness_threshold` are enough. `top_k_per_window` can be documented as a future extension.

## Compact Firmware Output Rule

Only `SEND` rows are emitted to the compact firmware trace CSV.

The compact firmware trace schema remains unchanged:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

The compact `seq` field is reassigned over transmitted rows only.

This makes the compact trace compatible with the existing `make_trace_headers.py` script.

## Why Skipped Rows Should Not Go Into Firmware CSV

The current firmware trace CSV describes metadata for packets that will be transmitted.

A skipped row is not a packet.

Including skipped rows in the compact firmware CSV would blur the distinction between source demand opportunities and transmitted packets.

Instead, skipped rows should remain in the reporting schedule and manifest. This allows later analysis of:

```text
total demand rows
selected SEND rows
skipped rows
physical received rows
delivered usefulness
delivered usefulness per transmitted packet
delivered usefulness per demand opportunity
```

## Future Physical Evidence Needed

A future physical airtime-aware run should report at least:

```text
source demand rows
scheduled SEND rows
scheduled SKIP rows
transmitted packet attempts
received valid packets
malformed packets
observed sequence gaps
total delivered usefulness
mean delivered usefulness
delivered usefulness per received packet
```

If the firmware actually skips transmissions, then physical packet counts can be compared to the fixed-all baseline.

Only then should the repository make airtime-saving claims.

## v0.8 Non-Goals

v0.8 does not require SD-card replay.

v0.8 does not require AWSRT integration.

v0.8 does not require changing the receiver packet schema.

v0.8 should not interpret observed sequence gaps as collisions.

v0.8 should not use `recv_ms - tx_ms` as true latency because transmitter and receiver clocks are not synchronized.

## Summary

v0.8 defines the reporting-schedule layer needed for future constrained-airtime experiments.

The key design decision is that demand rows and transmitted rows are different objects.

A reporting schedule records both `SEND` and `SKIP` decisions, while the compact firmware trace contains only rows selected for transmission.
