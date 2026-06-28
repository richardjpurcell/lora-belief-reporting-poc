# Run 026 Threshold-Variant Scheduled Replay Design

## Purpose

Run 026 is a controlled threshold-variant scheduled replay designed to extend the Run 024 and Run 025 physical scheduled replay results.

Runs 024 and 025 showed that a usefulness-threshold transmitter produced approximately half the received packets of the fixed-send transmitter while retaining higher mean delivered usefulness per received packet. Run 026 asks whether a stricter usefulness threshold further reduces physical transmission attempts while increasing or preserving mean delivered usefulness per received packet.

## Relationship to Prior v1 Milestones

This run continues the v1 physical scheduled replay sequence:

* v1.0 skipped-slot physical replay
* v1.1 schedule-aware analysis
* v1.2 manifest-bound replay analysis
* v1.3 run-bundle validation
* v1.4 multi-run comparison scaffold
* v1.5 Run 025 second scheduled replay design
* v1.6 Run 025 second scheduled replay

Run 026 preserves the same evidence ladder:

```
physical replay
  → packet-centric parser
  → schedule-aware analysis
  → manifest-bound reproduction
  → run-bundle validation
  → multi-run comparison
```

## Research Question

Does a stricter usefulness-threshold schedule further reduce physical transmission attempts while increasing or preserving mean delivered usefulness per received packet?

## Experimental Structure

Run 026 uses the same basic two-transmitter physical replay structure as Runs 024 and 025.

TXA uses a fixed-all schedule.

TXB uses a stricter usefulness-threshold schedule.

Planned structure:

```
TXA/N01: fixed-all schedule
TXB/N16: stricter usefulness-threshold schedule
```

The Run 024 and Run 025 TXB schedule used 8 SEND rows out of 16 schedule rows. Run 026 uses a stricter threshold that produces 4 SEND rows out of 16 schedule rows.

Planned schedule density:

```
TXA: 16/16 SEND rows
TXB: 4/16 SEND rows
```

Expected scheduled TXB/TXA send-fraction ratio:

```
0.25
```

## Threshold-Selection Method

The threshold was selected by inspecting the existing Run 022 usefulness distribution rather than guessing.

The existing Run 022 TXB usefulness values were:

```
0.08, 0.15, 0.18, 0.21,
0.36, 0.42, 0.46, 0.49,
0.63, 0.67, 0.74, 0.77,
0.79, 0.84, 0.91, 0.92
```

Candidate stricter thresholds produced the following SEND-like counts:

```
threshold >= 0.74: 6/16 SEND rows
threshold >= 0.77: 5/16 SEND rows
threshold >= 0.79: 4/16 SEND rows
threshold >= 0.84: 3/16 SEND rows
threshold >= 0.91: 2/16 SEND rows
threshold >= 0.92: 1/16 SEND row
```

Run 026 selects:

```
threshold = 0.79
```

This choice is stricter than the Run 024/025 threshold condition while preserving enough repeated SEND opportunities for a physical replay. It should create a visibly different scheduled replay condition: TXB should attempt approximately one quarter as many scheduled transmissions as TXA, rather than approximately one half as in Runs 024 and 025.

## Planned Files

Generated trace and schedule files:

```
traces/run026_reporting_txa_fixed_all_compact.csv
traces/run026_reporting_txb_usefulness_threshold_compact.csv
traces/run026_reporting_txa_fixed_all_schedule.csv
traces/run026_reporting_txb_usefulness_threshold_schedule.csv
traces/run026_reporting_reporting_schedule_manifest.json
```

Firmware schedule headers:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

Physical receiver log:

```
logs/rx_run_026_strict_threshold_replay.csv
```

Parsed outputs:

```
logs/parsed_run_026_strict_threshold_replay.csv
logs/parsed_run_026_strict_threshold_replay_rejects.csv
```

Reports:

```
reports/run026_schedule_aware_summary.json
reports/run026_schedule_aware_summary.csv
reports/run026_schedule_aware_manifest.json
```

Development notes:

```
docs/development/run026_threshold_variant_design.md
docs/development/run026_strict_threshold_replay.md
```

## Schedule Generation Commands

Generate the Run 026 schedules:

```
python scripts/make_reporting_schedule.py \
    --infile traces/run020_adapter_example_input.csv \
    --out-prefix traces/run026_reporting \
    --run-id run026_strict_threshold \
    --txa-policy fixed_all \
    --txb-policy usefulness_threshold \
    --threshold 0.79
```

Inspect the generated files:

```
ls traces/run026_reporting*
column -s, -t traces/run026_reporting_txb_usefulness_threshold_schedule.csv
```

Expected schedule counts:

```
TXA: 16 SEND, 0 SKIP
TXB: 4 SEND, 12 SKIP
```

## Firmware Header Plan

The firmware currently includes schedule headers at:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

For physical Run 026, regenerate these headers from the Run 026 schedule CSVs:

```
python scripts/make_schedule_headers.py \
    --infile traces/run026_reporting_txa_fixed_all_schedule.csv \
    --outfile firmware/first_radio_link_TX-A/schedule_data_TXA.h \
    --guard SCHEDULE_DATA_TXA_H

python scripts/make_schedule_headers.py \
    --infile traces/run026_reporting_txb_usefulness_threshold_schedule.csv \
    --outfile firmware/first_radio_link_TX_B/schedule_data_TXB.h \
    --guard SCHEDULE_DATA_TXB_H
```

Overwriting the firmware headers is acceptable as long as the schedule CSVs, generation command, and manifest preserve reproducibility. Runs 024 and 025 remain reproducible from their committed schedule CSVs, logs, parsed logs, reports, and manifests.

## Physical Setup Plan

Use the same basic physical setup as Runs 024 and 025 unless deliberately changed and documented.

Record any setup differences, including:

* board placement;
* antenna orientation;
* USB/power arrangement;
* receiver placement;
* nearby interference or environmental changes;
* firmware upload date/time;
* serial logging method.

The physical run should be treated as another bounded lab replay, not as a general LoRa performance benchmark.

## Parsing and Analysis Commands

After the physical replay, parse the receiver log:

```
python scripts/parse_receiver_log.py \
    --infile logs/rx_run_026_strict_threshold_replay.csv \
    --out logs/parsed_run_026_strict_threshold_replay.csv
```

Run schedule-aware analysis:

```
python scripts/analyze_scheduled_replay.py \
    --parsed logs/parsed_run_026_strict_threshold_replay.csv \
    --txa-schedule traces/run026_reporting_txa_fixed_all_schedule.csv \
    --txb-schedule traces/run026_reporting_txb_usefulness_threshold_schedule.csv \
    --out-json reports/run026_schedule_aware_summary.json \
    --out-csv reports/run026_schedule_aware_summary.csv
```

Run manifest-bound reproduction:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
    --manifest reports/run026_schedule_aware_manifest.json
```

Validate the Run 026 bundle:

```
python scripts/validate_run_bundle.py \
    --manifest reports/run026_schedule_aware_manifest.json
```

Compare Runs 024, 025, and 026:

```
python scripts/compare_scheduled_runs.py \
    --manifests \
        reports/run024_schedule_aware_manifest.json \
        reports/run025_schedule_aware_manifest.json \
        reports/run026_schedule_aware_manifest.json \
    --out-csv reports/scheduled_replay_comparison.csv \
    --out-json reports/scheduled_replay_comparison.json
```

## Expected Pattern

If the stricter threshold behaves as intended:

```
TXB schedules 4/16 SEND rows.
TXA schedules 16/16 SEND rows.
The scheduled TXB/TXA send-fraction ratio is 0.25.
The observed TXB/TXA received-packet ratio should drop below the Run 024/025 ratio of approximately 0.5.
TXB mean delivered usefulness should increase or remain high relative to TXA.
TXB should produce fewer received packets while preserving a higher usefulness-per-received-packet profile.
```

This would extend the Run 024/025 result from one threshold setting to a small threshold family.

## Interpretation Boundaries

This run remains a bounded physical scheduled replay.

Preserve the following cautions:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period; firmware loops over it repeatedly.
* The analysis compares schedule proportions and observed packet proportions.
* Do not infer exact transmitted-packet counts unless firmware-side transmission counts are instrumented.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and must not be interpreted as true latency.
* Usefulness and priority are synthetic metadata at this stage.
* The run does not yet use a live belief-maintenance controller.
* Avoid airtime-optimization claims.
* Use “reduced physical transmission attempts under scheduled skipping” rather than broader optimization language.
* Do not overgeneralize from a small number of lab runs.

## Commit and Tag Plan

After the Run 026 design note and generated schedule files are checked:

```
git status
git add docs/development/run026_threshold_variant_design.md
git add traces/run026_reporting*
git commit -m "Design Run 026 threshold variant scheduled replay"
```

Then tag the design milestone:

```
git tag -a v1.7-run026-threshold-variant-design \
    -m "v1.7 Run 026 threshold variant design"
```

Push the branch and tag:

```
git push origin exp032-run026-threshold-variant-design
git push origin v1.7-run026-threshold-variant-design
```

The physical replay should be handled as a later milestone:

```
exp033-run026-threshold-variant-replay
v1.8-run026-threshold-variant-replay
```
