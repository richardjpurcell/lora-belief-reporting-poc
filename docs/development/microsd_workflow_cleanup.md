# microSD workflow cleanup

## 1. Purpose

This note documents a small workflow-cleanup milestone after the first successful microSD-backed physical replay.

The immediate purpose is to make the SD-card replay path harder to misuse before increasing schedule length or transmitter count.

Milestone:

```
v2.8-microsd-workflow-cleanup
```

Branch:

```
exp043-microsd-workflow-cleanup
```

## 2. Background

Run 028 successfully replayed the Run 027-style loose-threshold schedule from microSD.

The confirmed Run 028 result was:

| TX  | Node | Schedule                    | Received packets | Mean delivered usefulness |
| --- | ---- | --------------------------- | ---------------: | ------------------------: |
| TXA | N01  | fixed-all, 16/16 SEND       |              378 |                     0.539 |
| TXB | N16  | loose threshold, 12/16 SEND |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

Run 028 showed that the Run 027-style scheduled-skipping semantics can move from compiled firmware schedule headers to microSD-backed `/schedule.csv` replay under similar two-transmitter lab conditions.

However, the Run 028 preparation also revealed a practical workflow hazard.

## 3. Workflow hazard

The repository contains several schedule-like CSV files with different meanings.

In particular, there is an important difference between:

| File type                            | Includes SKIP rows? | Suitable as `/schedule.csv`? |
| ------------------------------------ | ------------------: | ---------------------------: |
| SEND-only compact firmware trace CSV |                  no |                           no |
| full analysis-facing schedule CSV    |                 yes |                 not directly |
| all-slot SD schedule CSV             |                 yes |                          yes |

The compact CSVs have schema:

```
seq,region,event,priority,usefulness,stale_after,policy
```

These are SEND-only packet streams. They omit skipped demand slots.

The SD replay firmware expects:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

The final `send` column is essential:

| `send` value | Meaning                 |
| -----------: | ----------------------- |
|          `1` | transmit this slot      |
|          `0` | remain silent this slot |

Accidentally copying a SEND-only compact CSV to an SD card as `/schedule.csv` would remove the skipped-slot structure and would undermine the scheduled-skipping experiment.

## 4. Added validator

This milestone adds a narrow validator for SD-facing replay schedules:

```
scripts/validate_sd_schedule.py
```

The validator checks that an SD schedule has the exact expected header:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

It also checks that:

* the file has at least one data row;
* `seq` is contiguous from 0;
* `region` is a single character;
* `event` is an integer;
* `priority` is numeric;
* `usefulness` is numeric;
* `stale_after` is an integer;
* `policy` is a single character;
* `send` is either `0` or `1`.

Optional arguments allow a run to check expected row counts:

```
--expected-rows
--expected-send-rows
--expected-skip-rows
```

## 5. Validation examples

Run 028 TXA SD schedule validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run028_sd_txa_schedule.csv \
  --expected-rows 16 \
  --expected-send-rows 16 \
  --expected-skip-rows 0
```

Observed result:

```
SD schedule validation PASSED: traces/run028_sd_txa_schedule.csv
Rows:      16
SEND rows: 16
SKIP rows: 0
```

Run 028 TXB SD schedule validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run028_sd_txb_schedule.csv \
  --expected-rows 16 \
  --expected-send-rows 12 \
  --expected-skip-rows 4
```

Observed result:

```
SD schedule validation PASSED: traces/run028_sd_txb_schedule.csv
Rows:      16
SEND rows: 12
SKIP rows: 4
```

## 6. Negative check

The validator was also tested against a SEND-only compact CSV:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

Observed result:

```
ERROR: unexpected header.
Expected: seq,region,event,priority,usefulness,stale_after,policy,send
Found:    seq,region,event,priority,usefulness,stale_after,policy
```

This is the desired failure mode.

It confirms that the validator catches the most important SD workflow mistake: accidentally using a SEND-only compact CSV where an all-slot SD schedule CSV is required.

## 7. Recommended SD-card preparation checklist

Before any future SD-backed physical replay, use this checklist.

1. Generate or identify the full analysis-facing schedule CSV.

2. Convert it to an all-slot SD schedule CSV using:

   ```
   scripts/make_sd_schedule_csv.py
   ```

3. Validate the SD schedule CSV using:

   ```
   scripts/validate_sd_schedule.py
   ```

4. Confirm expected row counts:

   ```
   expected total rows
   expected SEND rows
   expected SKIP rows
   ```

5. Copy the validated SD schedule CSV to the transmitter card as:

   ```
   /schedule.csv
   ```

6. Confirm card identity.

7. Run the SD probe sketch or inspect transmitter startup output.

8. Confirm firmware startup row counts:

   ```
   rows_loaded
   send_rows
   skip_rows
   ```

9. Only then begin receiver logging.

## 8. Recommended manifest fields

Future SD-backed replay manifests should record both the analysis-facing schedule and the SD-facing schedule.

Recommended transmitter metadata:

```
"schedule_csv": "path/to/full_analysis_schedule.csv",
"sd_schedule_csv": "path/to/all_slot_sd_schedule.csv",
"sd_volume_name": "LORA_TXA",
"sd_path": "/schedule.csv",
"expected_rows": 16,
"expected_send_rows": 16,
"expected_skip_rows": 0
```

The repository schedule artifacts remain the source of reproducible truth. The SD card is the physical replay medium.

## 9. Interpretation

This milestone does not add a new physical replay and does not change the Run 028 result.

It adds a guardrail around the SD-card workflow.

The guarded interpretation is:

> SD-backed scheduled replay requires all-slot schedule CSVs with explicit SEND/SKIP decisions. SEND-only compact traces must not be used directly as `/schedule.csv`.

This cleanup reduces the chance of accidentally removing scheduled silence from future physical replay experiments.

## 10. Next directions

After this cleanup, there are two reasonable next routes.

### Route A: longer two-transmitter SD replay

Keep the current two-transmitter setup but increase schedule length. This would test the practical motivation for microSD-backed replay without adding transmitter-count complexity.

### Route B: three-transmitter SD replay design

Begin a design-only milestone for adding a third transmitter. This would prepare the path toward 3 → 6 → 12 transmitter scaling, but it should start with schedules, manifests, node naming, card naming, and analysis expectations before any physical run.

Recommended next step:

> Start with a longer two-transmitter SD replay design unless there is a strong reason to prioritize transmitter-count scaling immediately.

A longer two-transmitter SD replay would exercise the SD-card path more directly while keeping the physical setup manageable.
