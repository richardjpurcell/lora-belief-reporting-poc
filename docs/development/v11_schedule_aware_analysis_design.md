# v1.1 Schedule-Aware Analysis Design

## Purpose

Run 024 demonstrated that a reporting schedule can change physical transmission behavior: scheduled `SEND` rows are transmitted, while scheduled `SKIP` rows remain silent. The existing parser correctly remains packet-centric: it parses what the receiver observed and excludes malformed rows from valid-packet analysis.

For skipped-slot experiments, however, the evidence is split across two artifacts:

1. the reporting schedule, which records the intended `SEND`/`SKIP` policy; and
2. the parsed receiver log, which records valid packets that were actually received.

The v1.1 milestone adds a schedule-aware analyzer that combines these two artifacts without changing the parser.

## Design principle

The parser remains packet-centric.

The new analyzer becomes schedule-aware.

This preserves the receiver-log parser as a low-level parsing tool while adding a higher-level experiment-analysis layer for scheduled replay runs.

## Inputs

The analyzer should accept:

- schedule CSV for transmitter A;
- schedule CSV for transmitter B;
- parsed receiver CSV;
- JSON output path;
- CSV output path.

Example:

    python scripts/analyze_scheduled_replay.py \
      --schedule-a traces/run022_reporting_txa_fixed_all_schedule.csv \
      --schedule-b traces/run022_reporting_txb_usefulness_threshold_schedule.csv \
      --parsed logs/parsed_run_024_skipped_slot_replay.csv \
      --out-json reports/run024_schedule_aware_summary.json \
      --out-csv reports/run024_schedule_aware_summary.csv

## Outputs

The analyzer should report per transmitter/node:

- demand rows;
- scheduled `SEND` rows;
- scheduled `SKIP` rows;
- send fraction;
- received valid packets;
- observed sequence range;
- observed missing transmitted sequences;
- scheduled usefulness total for `SEND` rows;
- scheduled usefulness mean for `SEND` rows;
- delivered usefulness total;
- delivered usefulness mean per received packet;
- received packets per scheduled `SEND` row;
- delivered usefulness per scheduled demand row;
- delivered usefulness per scheduled `SEND` row;
- mean receiver inter-arrival.

It should also include a cross-transmitter comparison for Run 024-style experiments:

- scheduled send-fraction ratio;
- observed received-packet ratio;
- whether the observed packet ratio is consistent with scheduled skipping.

## Important interpretation boundary

The schedule CSV contains one schedule period, while the firmware loops over that schedule repeatedly. Therefore, the analyzer must not pretend that there were only sixteen physical slots in the run.

The schedule can support statements about proportions, such as:

- `TX-B scheduled SEND for 8/16 rows`;
- `TX-B scheduled send fraction was 0.5`;
- `TX-B/TX-A observed received-packet ratio was approximately 176/361 ≈ 0.488`.

It must not infer exact transmitted packet counts unless the run duration and number of completed schedule cycles are explicitly known.

Preferred wording:

> The observed packet-count ratio is consistent with the scheduled skipped-slot ratio.

Avoid overclaiming:

- do not call observed sequence gaps confirmed collisions;
- do not interpret `recv_ms - tx_ms` as true latency;
- do not claim airtime optimization;
- do not claim live belief-controller behavior.

## Run 024 expected headline

For Run 024, the expected headline is approximately:

- TX-A: 16/16 schedule rows `SEND`; 361 received packets; mean delivered usefulness 0.540.
- TX-B: 8/16 schedule rows `SEND`; 176 received packets; mean delivered usefulness 0.786.

Careful interpretation:

> TX-B used approximately half the scheduled transmission opportunities while retaining higher usefulness per received packet. The observed TX-B/TX-A received-packet ratio is close to the scheduled send-fraction ratio, which is consistent with scheduled skipping.
