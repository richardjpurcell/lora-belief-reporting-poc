# Run 029 longer SD schedule preparation

## 1. Purpose

This note documents the Run 029 schedule-preparation milestone.

Milestone:

```
v3.0-run029-longer-sd-schedule-prep
```

Branch:

```
exp045-run029-longer-sd-schedule-prep
```

This is a schedule-preparation milestone only. It does not copy schedules to SD cards and does not add a new physical LoRa run.

The purpose is to prepare and validate a longer two-transmitter SD-backed replay schedule before any physical replay.

## 2. Relationship to previous work

Run 028 was the first successful microSD-backed physical replay. It used a 16-row loose-threshold schedule:

| TX  | Node | Rows | SEND rows | SKIP rows |
| --- | ---- | ---: | --------: | --------: |
| TXA | N01  |   16 |        16 |         0 |
| TXB | N16  |   16 |        12 |         4 |

Run 028 confirmed that the Run 027-style scheduled-skipping semantics could move from compiled firmware headers to microSD-backed `/schedule.csv` replay under similar two-transmitter lab conditions.

The v2.9 design milestone recommended a longer two-transmitter SD replay before adding more transmitters. Run 029 schedule preparation follows that recommendation.

## 3. Design target

Run 029 is designed as a longer two-transmitter version of the medium-threshold scheduled-skipping condition.

Target:

| TX  | Node | Role                        | Rows | SEND rows | SKIP rows | Send fraction |
| --- | ---- | --------------------------- | ---: | --------: | --------: | ------------: |
| TXA | N01  | fixed-all baseline          |   64 |        64 |         0 |        1.0000 |
| TXB | N16  | usefulness-threshold stream |   64 |        32 |        32 |        0.5000 |

Expected scheduled TXB/TXA ratio:

```
32/64 = 0.5000
```

This increases schedule length from 16 rows to 64 rows while keeping the physical design two-transmitter.

## 4. Run 029 generic input

A new 64-row generic demand input was created:

```
traces/run029_longer_adapter_input.csv
```

Schema:

```
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_hint,source_policy,source_note
```

The input alternates between high-usefulness and low-usefulness rows. With a usefulness threshold of `0.50`, this produces 32 threshold-passing rows and 32 below-threshold rows.

The `policy_hint` field is set to the single-character value `F`, matching the existing adapter input constraints.

Example rows:

```
S000,0,0,A,1,0.750,0.720,5,F,synthetic_run029_longer,high_usefulness_slot
S001,1,1,B,0,0.200,0.180,5,F,synthetic_run029_longer,low_usefulness_slot
S002,2,2,C,1,0.810,0.780,5,F,synthetic_run029_longer,high_usefulness_slot
S003,3,3,D,1,0.240,0.220,5,F,synthetic_run029_longer,low_usefulness_slot
```

## 5. Reporting schedule generation

The reporting schedules were generated with:

```
python scripts/make_reporting_schedule.py \
  --infile traces/run029_longer_adapter_input.csv \
  --out-prefix traces/run029_reporting \
  --run-id R29 \
  --txa-policy fixed_all \
  --txb-policy usefulness_threshold \
  --threshold 0.50
```

Observed output:

```
Read generic demand rows: 64
Wrote TX-A schedule: traces/run029_reporting_txa_fixed_all_schedule.csv (64 SEND, 0 SKIP)
Wrote TX-B schedule: traces/run029_reporting_txb_usefulness_threshold_schedule.csv (32 SEND, 32 SKIP)
Wrote TX-A SEND-only compact trace: traces/run029_reporting_txa_fixed_all_compact.csv (64 rows)
Wrote TX-B SEND-only compact trace: traces/run029_reporting_txb_usefulness_threshold_compact.csv (32 rows)
Wrote reporting schedule manifest: traces/run029_reporting_reporting_schedule_manifest.json
```

Generated full schedule CSVs:

```
traces/run029_reporting_txa_fixed_all_schedule.csv
traces/run029_reporting_txb_usefulness_threshold_schedule.csv
```

Generated SEND-only compact traces:

```
traces/run029_reporting_txa_fixed_all_compact.csv
traces/run029_reporting_txb_usefulness_threshold_compact.csv
```

Generated reporting manifest:

```
traces/run029_reporting_reporting_schedule_manifest.json
```

## 6. Reporting schedule counts

The generated schedule counts are:

| TX  | Schedule rows | SEND rows | SKIP rows |
| --- | ------------: | --------: | --------: |
| TXA |            64 |        64 |         0 |
| TXB |            64 |        32 |        32 |

TXA fixed-all schedule starts:

```
S000,0,0,A,1,0.750,0.720,5,fixed_all,F,SEND,fixed_all sends every demand row
S001,1,1,B,0,0.200,0.180,5,fixed_all,F,SEND,fixed_all sends every demand row
S002,2,2,C,1,0.810,0.780,5,fixed_all,F,SEND,fixed_all sends every demand row
```

TXB usefulness-threshold schedule starts:

```
S000,0,0,A,1,0.750,0.720,5,usefulness_threshold,U,SEND,usefulness 0.720 >= threshold 0.500
S001,1,1,B,0,0.200,0.180,5,usefulness_threshold,U,SKIP,usefulness 0.180 < threshold 0.500
S002,2,2,C,1,0.810,0.780,5,usefulness_threshold,U,SEND,usefulness 0.780 >= threshold 0.500
```

## 7. Reporting manifest patch

The generated reporting manifest originally inherited an older milestone description from the reporting-schedule generator.

It was patched to identify this artifact as part of:

```
v3.0-run029-longer-sd-schedule-prep
```

The manifest now records:

* Run ID `R29`;
* 64-row generic input path;
* TXA full schedule path;
* TXB full schedule path;
* TXA compact trace path;
* TXB compact trace path;
* scheduled SEND/SKIP summaries;
* SD schedule output paths;
* expected SD row counts;
* a caution that SD-backed replay should use all-slot SD schedule CSVs, not SEND-only compact traces.

Important manifest distinction:

| Artifact type     | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| full schedule CSV | analysis-facing SEND/SKIP schedule              |
| compact CSV       | SEND-only trace artifact                        |
| SD schedule CSV   | firmware-facing all-slot `/schedule.csv` source |

For physical SD-backed replay, use the SD schedule CSVs.

## 8. SD schedule generation

The full schedules were converted into SD-facing all-slot schedules.

TXA conversion:

```
python scripts/make_sd_schedule_csv.py \
  --infile traces/run029_reporting_txa_fixed_all_schedule.csv \
  --out traces/run029_sd_txa_schedule.csv
```

Observed result:

```
Wrote SD schedule CSV: traces/run029_sd_txa_schedule.csv
Rows: 64
SEND rows: 64
SKIP rows: 0
```

TXB conversion:

```
python scripts/make_sd_schedule_csv.py \
  --infile traces/run029_reporting_txb_usefulness_threshold_schedule.csv \
  --out traces/run029_sd_txb_schedule.csv
```

Observed result:

```
Wrote SD schedule CSV: traces/run029_sd_txb_schedule.csv
Rows: 64
SEND rows: 32
SKIP rows: 32
```

Generated SD schedule files:

```
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
```

## 9. SD schedule validation

The Run 029 SD schedules were validated with the v2.8 validator.

TXA validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txa_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 64 \
  --expected-skip-rows 0
```

Observed result:

```
SD schedule validation PASSED: traces/run029_sd_txa_schedule.csv
Rows:      64
SEND rows: 64
SKIP rows: 0
```

TXB validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txb_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 32 \
  --expected-skip-rows 32
```

Observed result:

```
SD schedule validation PASSED: traces/run029_sd_txb_schedule.csv
Rows:      64
SEND rows: 32
SKIP rows: 32
```

This confirms that the Run 029 SD schedules have the all-slot schema expected by the transmitter firmware:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

## 10. Prepared artifact bundle

This milestone prepares the following Run 029 artifacts:

```
traces/run029_longer_adapter_input.csv
traces/run029_reporting_txa_fixed_all_schedule.csv
traces/run029_reporting_txb_usefulness_threshold_schedule.csv
traces/run029_reporting_txa_fixed_all_compact.csv
traces/run029_reporting_txb_usefulness_threshold_compact.csv
traces/run029_reporting_reporting_schedule_manifest.json
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
```

No receiver logs or physical replay reports are created in this milestone.

## 11. Expected physical replay setup

A later physical Run 029 should copy the validated SD schedules to the board-oriented SD cards:

| TX  | Node | SD volume  | Source file                         | SD destination  |
| --- | ---- | ---------- | ----------------------------------- | --------------- |
| TXA | N01  | `LORA_TXA` | `traces/run029_sd_txa_schedule.csv` | `/schedule.csv` |
| TXB | N16  | `LORA_TXB` | `traces/run029_sd_txb_schedule.csv` | `/schedule.csv` |

Expected transmitter startup checks:

| TX  | Expected rows loaded | Expected SEND rows | Expected SKIP rows |
| --- | -------------------: | -----------------: | -----------------: |
| TXA |                   64 |                 64 |                  0 |
| TXB |                   64 |                 32 |                 32 |

The physical run should not begin until those startup row counts are confirmed.

## 12. Expected physical replay interpretation

A later Run 029 physical replay should test whether the longer SD-backed schedule preserves the expected proportional skipped-slot behavior.

Expected schedule ratio:

```
scheduled TXB/TXA ratio = 0.5000
```

The expected qualitative result is:

* TXB should produce approximately half as many received packets as TXA, subject to physical LoRa variation;
* TXB should retain higher mean delivered usefulness per received packet than TXA;
* the parser and manifest-bound schedule-aware analyzer should work unchanged.

The exact received packet counts should not be predicted.

## 13. Cautions

This milestone is schedule preparation only. It does not demonstrate a new physical replay.

The usual interpretation cautions remain:

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one repeated schedule period.
* The analyzer compares schedule proportions and observed packet proportions.
* The analyzer does not infer exact transmitted-packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* Use the wording “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”
* Do not claim energy savings unless current or power measurements are added.
* Do not overgeneralize from two-transmitter lab runs.

## 14. Summary

Run 029 schedule preparation is complete.

Prepared schedule target:

| TX  | Node | Rows | SEND rows | SKIP rows | Send fraction |
| --- | ---- | ---: | --------: | --------: | ------------: |
| TXA | N01  |   64 |        64 |         0 |        1.0000 |
| TXB | N16  |   64 |        32 |        32 |        0.5000 |

The all-slot SD schedules validate successfully and are ready for a later physical replay milestone.

Recommended next milestone:

```
v3.1-run029-longer-sd-physical-prep
```

That milestone should handle SD-card copying, transmitter startup checks, and receiver logging setup before or during the physical replay.
