# Run 025 second scheduled replay design

## Purpose

Run 024 demonstrated skipped-slot physical replay using a fixed-send transmitter and a usefulness-threshold transmitter.

The v1.0–v1.4 milestones then built a reproducible evidence path around that run:

* v1.0: skipped-slot physical replay;
* v1.1: schedule-aware analysis;
* v1.2: manifest-bound reproduction;
* v1.3: run-bundle validation;
* v1.4: comparison scaffold.

Run 025 should be the next physical scheduled replay. Its purpose is to provide a second manifest-bound scheduled replay bundle so the comparison scaffold can begin to summarize more than one physical run.

This design note defines Run 025 before collecting the physical data.

## Experimental intent

Run 025 should repeat the Run 024 structure with minimal changes.

The primary goal is replication of the skipped-slot replay path, not exploration of a new policy.

A good Run 025 should answer:

> Does the same fixed-send versus usefulness-threshold scheduled replay pattern remain observable in a second physical run under similar lab conditions?

This keeps the interpretation careful. Run 025 should strengthen the evidence path by adding a second run, but it should not be framed as a general wireless-network result.

## Proposed run identity

Run ID:

* `run025`

Proposed raw receiver log:

* `logs/rx_run_025_skipped_slot_replay_repeat.csv`

Proposed parsed valid log:

* `logs/parsed_run_025_skipped_slot_replay_repeat.csv`

Proposed rejects log:

* `logs/parsed_run_025_skipped_slot_replay_repeat_rejects.csv`

Proposed schedule-aware outputs:

* `reports/run025_schedule_aware_summary.json`
* `reports/run025_schedule_aware_summary.csv`

Proposed manifest:

* `reports/run025_schedule_aware_manifest.json`

Proposed development note after the run:

* `docs/development/run025_skipped_slot_replay_repeat.md`

## Schedule choice

Use the same Run 022 schedules as Run 024:

* `traces/run022_reporting_txa_fixed_all_schedule.csv`
* `traces/run022_reporting_txb_usefulness_threshold_schedule.csv`

Use the same generated firmware schedule headers unless they have been modified:

* `firmware/first_radio_link_TX-A/schedule_data_TXA.h`
* `firmware/first_radio_link_TX_B/schedule_data_TXB.h`

This keeps Run 025 as a repeat of the same scheduled replay condition.

## Transmitter roles

TXA / N01:

* fixed-all schedule;
* expected schedule period: 16 demand rows;
* expected scheduled SEND rows: 16;
* expected scheduled SKIP rows: 0;
* expected send fraction: 1.0.

TXB / N16:

* usefulness-threshold schedule;
* expected schedule period: 16 demand rows;
* expected scheduled SEND rows: 8;
* expected scheduled SKIP rows: 8;
* expected send fraction: 0.5.

## Physical setup

Keep the setup as close as practical to Run 024:

* point-to-point LoRa at 915 MHz;
* same receiver firmware;
* same transmitter firmware;
* same transmitter schedule headers;
* same board identities if possible;
* same approximate board placement;
* same antenna orientation if possible;
* same power source setup if possible;
* same serial logging approach.

Any unavoidable setup changes should be documented in the run note.

## Run duration

Use a similar logging duration to Run 024 if practical.

The schedule contains one period of 16 rows and loops repeatedly in firmware. Therefore, the run duration should be long enough to observe many repeated schedule cycles.

Do not treat the schedule as only 16 physical slots. The analysis should continue to compare schedule proportions and observed packet proportions.

## Collection command

Use the receiver logger with a Run 025 output path.

The exact command depends on the serial port, but the intended output file is:

```
logs/rx_run_025_skipped_slot_replay_repeat.csv
```

Example shape:

```
python scripts/receiver_logger.py \
  --port <RECEIVER_SERIAL_PORT> \
  --baud 115200 \
  --outfile logs/rx_run_025_skipped_slot_replay_repeat.csv
```

If the receiver logger options differ locally, use the repository-supported invocation and preserve the output path above.

## Parsing command

After collection, parse the receiver log:

```
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_025_skipped_slot_replay_repeat.csv \
  --outfile logs/parsed_run_025_skipped_slot_replay_repeat.csv
```

If the parser uses `--out` rather than `--outfile`, use the supported alias and keep the proposed output path.

Expected parser outputs:

* `logs/parsed_run_025_skipped_slot_replay_repeat.csv`
* `logs/parsed_run_025_skipped_slot_replay_repeat_rejects.csv`

## Schedule-aware analysis command

After parsing:

```
python scripts/analyze_scheduled_replay.py \
  --schedule-a traces/run022_reporting_txa_fixed_all_schedule.csv \
  --schedule-b traces/run022_reporting_txb_usefulness_threshold_schedule.csv \
  --parsed logs/parsed_run_025_skipped_slot_replay_repeat.csv \
  --out-json reports/run025_schedule_aware_summary.json \
  --out-csv reports/run025_schedule_aware_summary.csv \
  --tx-a-label TXA \
  --tx-b-label TXB \
  --node-a-label N01 \
  --node-b-label N16
```

## Manifest-bound reproduction

After the first schedule-aware summary is generated, create:

* `reports/run025_schedule_aware_manifest.json`

Then reproduce the analysis through the manifest-bound wrapper:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run025_schedule_aware_manifest.json
```

## Bundle validation

Validate the Run 025 bundle:

```
python scripts/validate_run_bundle.py \
  --manifest reports/run025_schedule_aware_manifest.json
```

The validation should pass before Run 025 is added to the comparison scaffold.

## Multi-run comparison

After Run 025 validates, compare Run 024 and Run 025:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --manifest reports/run025_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json \
  --validate
```

At that point, the comparison scaffold will become a true two-run comparison.

## Expected result pattern

Run 025 should not be expected to match Run 024 packet counts exactly.

A useful Run 025 would show:

* TXA has more received packets than TXB;
* TXB/TXA received-packet ratio is near the scheduled send-fraction ratio of 0.5;
* TXB retains higher mean delivered usefulness per received packet than TXA;
* rejects, if any, are excluded from valid-packet analysis;
* observed sequence gaps are reported carefully, not interpreted as confirmed collisions.

The expected qualitative pattern is:

> The usefulness-threshold transmitter schedules approximately half the transmission opportunities while preserving higher mean delivered usefulness per received packet.

The expected careful ratio wording is:

> The observed TXB/TXA received-packet ratio is consistent with the scheduled skipped-slot ratio.

## Interpretation boundary

Run 025 should be interpreted as a second physical scheduled replay under similar lab conditions.

Even if Run 025 matches Run 024 closely, avoid overclaiming.

Do not claim:

* exact transmitted-packet counts;
* confirmed collisions;
* true latency from `recv_ms - tx_ms`;
* airtime optimization;
* LoRaWAN behavior;
* live belief-controller behavior;
* general wireless-network performance.

Prefer:

> reduced physical transmission attempts under scheduled skipping;

and:

> observed packet proportions consistent with the scheduled send-fraction difference.

## Success criteria

Run 025 is successful if:

1. raw receiver log is collected;
2. parser produces valid and rejects files;
3. schedule-aware analysis produces Run 025 JSON and CSV reports;
4. Run 025 manifest can reproduce the analysis;
5. Run 025 bundle validation passes;
6. Run 024 and Run 025 can both be included in the comparison scaffold;
7. documentation preserves the interpretation cautions.

## Milestone contribution

This design prepares the first repeat scheduled replay after Run 024.

The expected contribution is not a new software layer. The contribution is a carefully planned second physical run that can reuse the existing reproducibility ladder:

```
physical replay
  → parser
  → schedule-aware analysis
  → manifest-bound reproduction
  → run-bundle validation
  → multi-run comparison
```
