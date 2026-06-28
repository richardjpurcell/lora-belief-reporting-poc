# Run 027 Loose-Threshold Scheduled Replay Design

## Purpose

Run 027 is a controlled loose-threshold scheduled replay design.

Runs 024, 025, and 026 established a small threshold-family sequence for physical scheduled replay:

* Runs 024 and 025 used a usefulness-threshold schedule with 8 SEND rows out of 16 schedule rows for TXB.
* Run 026 used a stricter usefulness-threshold schedule with 4 SEND rows out of 16 schedule rows for TXB.
* Run 027 is designed to add a looser usefulness-threshold condition with 12 SEND rows out of 16 schedule rows for TXB.

The purpose is to fill in the upper part of the threshold ladder and test whether a looser threshold produces an observed received-packet proportion closer to three quarters of the fixed-all transmitter while preserving higher mean delivered usefulness than the fixed-all stream.

This is a design milestone, not yet a physical replay result.

## Branch and Milestone Context

Current design branch:

```
exp035-run027-loose-threshold-design
```

Planned design tag:

```
v2.0-run027-loose-threshold-design
```

Expected later physical replay branch:

```
exp036-run027-loose-threshold-replay
```

Expected later physical replay tag:

```
v2.1-run027-loose-threshold-replay
```

## Relationship to Runs 024--026

Runs 024--026 created the first threshold-family evidence sequence.

Run 024:

```
TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
Observed TXB/TXA received-packet ratio: 0.4875
Scheduled TXB/TXA send-fraction ratio: 0.5000
```

Run 025:

```
TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785
Observed TXB/TXA received-packet ratio: 0.5000
Scheduled TXB/TXA send-fraction ratio: 0.5000
```

Run 026:

```
TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866
Observed TXB/TXA received-packet ratio: 0.2520
Scheduled TXB/TXA send-fraction ratio: 0.2500
```

Run 027 is designed to add a looser 12/16 TXB condition.

The intended threshold ladder is:

```
TXA fixed-all baseline: 16/16 SEND
TXB loose threshold:   12/16 SEND
TXB medium threshold:   8/16 SEND
TXB strict threshold:   4/16 SEND
```

## Research Question

Does a looser usefulness-threshold schedule produce an observed TXB/TXA received-packet ratio near the scheduled send-fraction ratio of 0.75 while still preserving higher mean delivered usefulness per received packet than the fixed-all TXA stream?

## Experimental Structure

Run 027 uses the same basic two-transmitter scheduled replay structure as Runs 024--026.

Planned structure:

```
TXA/N01: fixed-all schedule
TXB/N16: usefulness-threshold schedule
```

Schedule rows:

```
TXA: 16/16 SEND rows
TXB: 12/16 SEND rows
```

TXB usefulness threshold:

```
0.36
```

Scheduled TXB/TXA send-fraction ratio:

```
12 / 16 = 0.7500
```

## Threshold-Selection Method

The threshold was chosen from the existing 16-row generic demand trace usefulness distribution.

The relevant usefulness values are:

```
0.08, 0.15, 0.18, 0.21,
0.36, 0.42, 0.46, 0.49,
0.63, 0.67, 0.74, 0.77,
0.79, 0.84, 0.91, 0.92
```

Candidate lower thresholds produce the following SEND-like counts:

```
threshold >= 0.36: 12/16 SEND rows
threshold >= 0.42: 11/16 SEND rows
threshold >= 0.46: 10/16 SEND rows
threshold >= 0.49:  9/16 SEND rows
```

Run 027 selects:

```
threshold = 0.36
```

This produces the desired loose-threshold condition:

```
TXB: 12 SEND rows, 4 SKIP rows
```

This threshold complements the existing 8/16 and 4/16 conditions from Runs 024--026.

## Schedule Generation

Run 027 schedules were generated with:

```
python scripts/make_reporting_schedule.py \
    --infile traces/run020_adapter_example_input.csv \
    --out-prefix traces/run027_reporting \
    --run-id run027_loose_threshold \
    --txa-policy fixed_all \
    --txb-policy usefulness_threshold \
    --threshold 0.36
```

The generator reported:

```
Read generic demand rows: 16
Wrote TX-A schedule: traces/run027_reporting_txa_fixed_all_schedule.csv (16 SEND, 0 SKIP)
Wrote TX-B schedule: traces/run027_reporting_txb_usefulness_threshold_schedule.csv (12 SEND, 4 SKIP)
Wrote TX-A SEND-only compact trace: traces/run027_reporting_txa_fixed_all_compact.csv (16 rows)
Wrote TX-B SEND-only compact trace: traces/run027_reporting_txb_usefulness_threshold_compact.csv (12 rows)
Wrote reporting schedule manifest: traces/run027_reporting_reporting_schedule_manifest.json
```

## Generated Files

Generated schedule files:

```
traces/run027_reporting_txa_fixed_all_schedule.csv
traces/run027_reporting_txb_usefulness_threshold_schedule.csv
```

Generated compact trace files:

```
traces/run027_reporting_txa_fixed_all_compact.csv
traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

Generated schedule manifest:

```
traces/run027_reporting_reporting_schedule_manifest.json
```

Design note:

```
docs/development/run027_loose_threshold_design.md
```

## TXB Schedule Rows

The generated TXB schedule contains 12 SEND rows and 4 SKIP rows.

TXB SEND rows occur where usefulness is greater than or equal to 0.36:

```
t000 A usefulness 0.920 SEND
t002 C usefulness 0.840 SEND
t003 D usefulness 0.420 SEND
t004 E usefulness 0.790 SEND
t006 G usefulness 0.670 SEND
t007 H usefulness 0.490 SEND
t008 A usefulness 0.910 SEND
t010 C usefulness 0.770 SEND
t011 D usefulness 0.360 SEND
t012 E usefulness 0.740 SEND
t014 G usefulness 0.630 SEND
t015 H usefulness 0.460 SEND
```

TXB SKIP rows occur where usefulness is below 0.36:

```
t001 B usefulness 0.180 SKIP
t005 F usefulness 0.080 SKIP
t009 B usefulness 0.210 SKIP
t013 F usefulness 0.150 SKIP
```

## Expected Pattern

If the physical replay behaves consistently with the scheduled-skipping pattern observed in Runs 024--026, the expected Run 027 pattern is:

```
TXA schedules 16/16 SEND rows.
TXB schedules 12/16 SEND rows.
The scheduled TXB/TXA send-fraction ratio is 0.7500.
The observed TXB/TXA received-packet ratio should be near 0.75 under similar lab conditions.
TXB mean delivered usefulness should remain above TXA mean delivered usefulness, but should likely be lower than the strict-threshold Run 026 TXB mean usefulness.
```

Expected qualitative relationship across the threshold family:

```
looser threshold:
  more TXB packets
  lower TXB mean usefulness than strict threshold
  observed TXB/TXA ratio closer to 1.0

stricter threshold:
  fewer TXB packets
  higher TXB mean usefulness
  observed TXB/TXA ratio farther below 1.0
```

Run 027 should therefore help complete the threshold ladder:

```
12/16 loose threshold
 8/16 medium threshold
 4/16 strict threshold
```

## Planned Physical Replay Files

The later physical replay milestone should use the following file names.

Firmware schedule headers:

```
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

Raw receiver log:

```
logs/rx_run_027_loose_threshold_replay.csv
```

Parsed outputs:

```
logs/parsed_run_027_loose_threshold_replay.csv
logs/parsed_run_027_loose_threshold_replay_rejects.csv
```

Schedule-aware reports:

```
reports/run027_schedule_aware_summary.json
reports/run027_schedule_aware_summary.csv
```

Manifest:

```
reports/run027_schedule_aware_manifest.json
```

Replay note:

```
docs/development/run027_loose_threshold_replay.md
```

Updated comparison outputs:

```
reports/scheduled_replay_comparison.csv
reports/scheduled_replay_comparison.json
```

## Planned Firmware Header Generation

This design milestone does not require regenerating firmware headers.

The physical replay milestone should regenerate the schedule headers from the Run 027 schedule CSVs:

```
python scripts/make_schedule_headers.py \
    --infile traces/run027_reporting_txa_fixed_all_schedule.csv \
    --outfile firmware/first_radio_link_TX-A/schedule_data_TXA.h \
    --guard SCHEDULE_DATA_TXA_H

python scripts/make_schedule_headers.py \
    --infile traces/run027_reporting_txb_usefulness_threshold_schedule.csv \
    --outfile firmware/first_radio_link_TX_B/schedule_data_TXB.h \
    --guard SCHEDULE_DATA_TXB_H
```

Overwriting the firmware schedule headers is acceptable for the physical replay milestone as long as the source schedule CSVs, generation commands, and manifests preserve reproducibility.

## Planned Parser Command

After the physical replay, parse the receiver log with:

```
python scripts/parse_receiver_log.py \
    --infile logs/rx_run_027_loose_threshold_replay.csv \
    --out logs/parsed_run_027_loose_threshold_replay.csv \
    --seq-window 50
```

## Planned Schedule-Aware Analysis Command

After parsing, run schedule-aware analysis with:

```
python scripts/analyze_scheduled_replay.py \
    --parsed logs/parsed_run_027_loose_threshold_replay.csv \
    --schedule-a traces/run027_reporting_txa_fixed_all_schedule.csv \
    --schedule-b traces/run027_reporting_txb_usefulness_threshold_schedule.csv \
    --out-json reports/run027_schedule_aware_summary.json \
    --out-csv reports/run027_schedule_aware_summary.csv
```

Expected schedule-aware headline shape:

```
TXA: 16/16 schedule rows SEND; [received packets] received packets; mean delivered usefulness [value]
TXB: 12/16 schedule rows SEND; [received packets] received packets; mean delivered usefulness [value]
Observed received-packet ratio [near 0.75]; scheduled send-fraction ratio 0.7500.
```

## Planned Manifest-Bound Reproduction

The physical replay milestone should create:

```
reports/run027_schedule_aware_manifest.json
```

Then reproduce analysis with:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
    --manifest reports/run027_schedule_aware_manifest.json
```

## Planned Bundle Validation

Validate the Run 027 bundle with:

```
python scripts/validate_run_bundle.py \
    --manifest reports/run027_schedule_aware_manifest.json
```

The manifest expected-headline values should be filled from the actual Run 027 schedule-aware summary before validation.

## Planned Multi-Run Comparison

After validation, update the scheduled replay comparison across Runs 024--027:

```
python scripts/compare_scheduled_runs.py \
    --manifest reports/run024_schedule_aware_manifest.json \
    --manifest reports/run025_schedule_aware_manifest.json \
    --manifest reports/run026_schedule_aware_manifest.json \
    --manifest reports/run027_schedule_aware_manifest.json \
    --out-csv reports/scheduled_replay_comparison.csv \
    --out-json reports/scheduled_replay_comparison.json \
    --validate
```

The expected comparison family after Run 027 is:

```
Run 024: TXB 8/16 SEND
Run 025: TXB 8/16 SEND
Run 026: TXB 4/16 SEND
Run 027: TXB 12/16 SEND
```

## Interpretation Boundaries

This design remains bounded.

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
* Do not claim energy savings unless current or power measurements are added.

## Scaling Context

The current hardware planning target is 12 active transmitters with 2 spare boards.

Run 027 remains a two-transmitter experiment. The purpose is to complete the small threshold-family ladder before increasing hardware complexity.

A reasonable future scaling path is:

```
2 transmitters: current validated baseline
  → 3 transmitters: first multi-transmitter generalization
  → 5 or 6 transmitters: small network replay
  → 12 transmitters: full available platform
  → 2 spares: replacement/debug reserve
```

The repository should continue to stabilize schedule generation, logging, manifest-bound reproduction, and validation before scaling transmitter count.

## Immediate Commit Plan

For this design milestone, include:

```
docs/development/run027_loose_threshold_design.md
traces/run027_reporting_reporting_schedule_manifest.json
traces/run027_reporting_txa_fixed_all_compact.csv
traces/run027_reporting_txa_fixed_all_schedule.csv
traces/run027_reporting_txb_usefulness_threshold_compact.csv
traces/run027_reporting_txb_usefulness_threshold_schedule.csv
```

Suggested commit:

```
git add docs/development/run027_loose_threshold_design.md
git add traces/run027_reporting_reporting_schedule_manifest.json
git add traces/run027_reporting_txa_fixed_all_compact.csv
git add traces/run027_reporting_txa_fixed_all_schedule.csv
git add traces/run027_reporting_txb_usefulness_threshold_compact.csv
git add traces/run027_reporting_txb_usefulness_threshold_schedule.csv

git commit -m "Design Run 027 loose-threshold scheduled replay"
```

Suggested tag:

```
git tag -a v2.0-run027-loose-threshold-design \
    -m "v2.0 Run 027 loose-threshold scheduled replay design"
```

Suggested push:

```
git push origin exp035-run027-loose-threshold-design
git push origin v2.0-run027-loose-threshold-design
```
