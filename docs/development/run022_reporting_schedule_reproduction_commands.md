# Run 022 Reporting Schedule Reproduction Commands

## Purpose

Run 022 is a v0.8 design-stage reporting-schedule check.

It demonstrates that a generic belief-maintenance demand trace can be converted into explicit `SEND` / `SKIP` reporting schedules and then reduced into compact firmware trace CSVs containing `SEND` rows only.

This is not a physical LoRa run.

No firmware, SD-card replay, radio timing, or receiver logging changes are made in this step.

## Branch

```text
exp023-v08-reporting-schedule-design
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

## Reporting Schedule Command

```bash
python scripts/make_reporting_schedule.py \
  --infile traces/run020_adapter_example_input.csv \
  --out-prefix traces/run022_reporting \
  --run-id R22 \
  --txa-policy fixed_all \
  --txb-policy usefulness_threshold \
  --threshold 0.50
```

## Expected Output

```text
Read generic demand rows: 16
Wrote TX-A schedule: traces/run022_reporting_txa_fixed_all_schedule.csv (16 SEND, 0 SKIP)
Wrote TX-B schedule: traces/run022_reporting_txb_usefulness_threshold_schedule.csv (8 SEND, 8 SKIP)
Wrote TX-A SEND-only compact trace: traces/run022_reporting_txa_fixed_all_compact.csv (16 rows)
Wrote TX-B SEND-only compact trace: traces/run022_reporting_txb_usefulness_threshold_compact.csv (8 rows)
Wrote reporting schedule manifest: traces/run022_reporting_reporting_schedule_manifest.json
```

## Generated Schedule Files

```text
traces/run022_reporting_txa_fixed_all_schedule.csv
traces/run022_reporting_txb_usefulness_threshold_schedule.csv
```

The schedule schema is:

```text
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_name,policy_code,decision,decision_reason
```

The schedule files retain all source demand rows and add reporting decisions.

For the Run 022 example:

```text
TX-A fixed_all:              16 SEND, 0 SKIP
TX-B usefulness_threshold:    8 SEND, 8 SKIP
```

## Generated Compact Trace Files

```text
traces/run022_reporting_txa_fixed_all_compact.csv
traces/run022_reporting_txb_usefulness_threshold_compact.csv
```

The compact trace schema remains:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

The compact trace files contain `SEND` rows only.

For the Run 022 example:

```text
TX-A compact trace rows: 16
TX-B compact trace rows: 8
```

## Manifest

Generated manifest:

```text
traces/run022_reporting_reporting_schedule_manifest.json
```

The manifest records the input file, output files, schemas, policies, threshold, and schedule summaries.

The Run 022 manifest reports:

```text
TX-A fixed_all:
  demand rows: 16
  send rows: 16
  skip rows: 0
  send fraction: 1.0
  scheduled total usefulness: 8.62
  scheduled mean usefulness: 0.53875

TX-B usefulness_threshold:
  demand rows: 16
  send rows: 8
  skip rows: 8
  send fraction: 0.5
  scheduled total usefulness: 6.27
  scheduled mean usefulness: 0.78375
```

## Header-Generation Validation

Validate the TX-A compact trace:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run022_reporting_txa_fixed_all_compact.csv \
  --outfile /tmp/trace_data_TXA_reporting_test.h
```

Expected output:

```text
Wrote /tmp/trace_data_TXA_reporting_test.h
```

Validate the TX-B compact trace:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run022_reporting_txb_usefulness_threshold_compact.csv \
  --outfile /tmp/trace_data_TXB_reporting_test.h
```

Expected output:

```text
Wrote /tmp/trace_data_TXB_reporting_test.h
```

## Interpretation

Run 022 confirms the new reporting-schedule layer:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ SEND-only compact firmware trace CSV
→ Arduino-compatible trace header
```

The important distinction is that the schedule preserves both sent and skipped demand rows, while the compact firmware trace contains only rows selected for transmission.

This prepares the repository for future constrained-airtime experiments in which skipped rows can correspond to actual skipped transmissions.

## Cautions

Run 022 is a design-stage schedule artifact, not a physical LoRa experiment.

It does not demonstrate airtime reduction.

It does not demonstrate collision reduction.

It does not change firmware timing or packet scheduling.

Airtime-saving claims require a later physical run in which the firmware actually skips or schedules transmissions differently.
