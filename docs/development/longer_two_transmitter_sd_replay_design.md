# Longer two-transmitter SD replay design

## 1. Purpose

This note defines the next controlled step after the successful Run 028 microSD-backed replay and the v2.8 SD workflow cleanup.

The purpose is to design a longer two-transmitter SD-backed replay before adding more transmitters.

Milestone:

```
v2.9-longer-two-transmitter-sd-replay-design
```

Branch:

```
exp044-longer-two-transmitter-sd-replay-design
```

This is a design-only milestone. It does not add a new physical run.

## 2. Motivation

Run 028 confirmed that the Run 027-style loose-threshold schedule could be replayed from microSD rather than compiled firmware headers.

Run 028 used a short 16-row schedule:

| TX  | Node | Schedule                   | Rows | SEND rows | SKIP rows |
| --- | ---- | -------------------------- | ---: | --------: | --------: |
| TXA | N01  | fixed-all                  |   16 |        16 |         0 |
| TXB | N16  | loose usefulness threshold |   16 |        12 |         4 |

The result was successful:

| TX  | Node | Received packets | Mean delivered usefulness |
| --- | ---- | ---------------: | ------------------------: |
| TXA | N01  |              378 |                     0.539 |
| TXB | N16  |              284 |                     0.668 |

Ratio result:

| Quantity                |  Value |
| ----------------------- | -----: |
| Scheduled TXB/TXA ratio | 0.7500 |
| Observed TXB/TXA ratio  | 0.7513 |

The practical reason for microSD-backed replay is not fully exercised by a 16-row schedule. The next step should therefore increase schedule length while keeping the physical setup simple.

## 3. Design principle

The next physical run should change one main thing:

> schedule length

It should not also change transmitter count, packet format, receiver logging, parser behavior, or the schedule-aware analysis pipeline.

Keeping the run two-transmitter avoids mixing two questions:

1. Can the SD replay path handle longer schedules?
2. What happens when more transmitters share the channel?

This milestone addresses the first question only.

## 4. Proposed Run 029

Proposed run identifier:

```
Run 029
```

Proposed firmware run ID:

```
R29
```

Proposed milestone after this design:

```
v3.0-run029-longer-sd-physical-replay
```

Proposed branch after this design:

```
exp045-run029-longer-sd-physical-replay
```

Proposed replay mechanism:

```
microSD-backed /schedule.csv
```

Proposed transmitter roles:

| TX  | Node | Role                                           |
| --- | ---- | ---------------------------------------------- |
| TXA | N01  | fixed-all baseline                             |
| TXB | N16  | usefulness-threshold scheduled-skipping stream |

## 5. Schedule length

Recommended first longer schedule length:

```
64 demand rows
```

Rationale:

* 64 rows is long enough to exercise SD-backed replay beyond the initial 16-row prototype.
* It is still short enough to inspect manually.
* It preserves a simple relationship to the existing 16-row examples.
* It avoids jumping immediately to hundreds or thousands of rows before the workflow is proven.

The schedule period would be:

| TX  | Rows |       SEND rows |       SKIP rows |         Send fraction |
| --- | ---: | --------------: | --------------: | --------------------: |
| TXA |   64 |              64 |               0 |                 1.000 |
| TXB |   64 | target 32 or 48 | target 32 or 16 | target 0.500 or 0.750 |

## 6. Recommended threshold condition

There are two reasonable choices.

### Option A: medium threshold, 32/64 SEND

This repeats the Run 024/025-style medium send-fraction condition at longer schedule length.

Expected schedule ratio:

```
TXB/TXA = 32/64 = 0.5000
```

Advantages:

* Directly exercises skipped slots.
* Stronger contrast in packet count.
* Easier to see if the longer SD schedule preserves scheduled silence.

Disadvantages:

* Less similar to the immediately preceding Run 028 loose-threshold result.

### Option B: loose threshold, about 48/64 SEND

This repeats the Run 027/028-style loose send-fraction condition at longer schedule length.

Expected schedule ratio:

```
TXB/TXA = 48/64 = 0.7500
```

Advantages:

* Closest conceptual continuation from Run 028.
* Good for checking storage-mechanism continuity.

Disadvantages:

* We have already tested the 0.75 ratio with Run 027 and Run 028.
* The skipped-slot contrast is less strong than the 0.50 condition.

## 7. Recommendation

Use Option A first:

```
TXA: 64/64 SEND
TXB: 32/64 SEND
```

This makes Run 029 a longer-schedule version of the medium threshold condition.

The reason is practical: a 50% send fraction provides a clear skipped-slot pattern and a clear receiver-side proportion check. Since Run 024 and Run 025 already established the 8/16 medium condition, Run 029 can ask whether the same kind of proportional result holds when the schedule length increases from 16 to 64 rows.

Recommended target:

| TX  | Node | Rows | SEND rows | SKIP rows | Expected ratio |
| --- | ---- | ---: | --------: | --------: | -------------: |
| TXA | N01  |   64 |        64 |         0 |         1.0000 |
| TXB | N16  |   64 |        32 |        32 |         0.5000 |

## 8. Schedule generation route

The current repository already contains:

```
scripts/make_reporting_schedule.py
scripts/make_sd_schedule_csv.py
scripts/validate_sd_schedule.py
```

The cleanest route is:

1. create or generate a 64-row generic demand input;
2. create full analysis-facing reporting schedules;
3. convert those schedules into all-slot SD schedules;
4. validate the SD schedules;
5. copy the validated SD schedules to transmitter SD cards;
6. run the physical replay in a later milestone.

The intended path is:

```
generic demand trace
→ full reporting schedule CSV
→ all-slot SD schedule CSV
→ /schedule.csv on SD card
→ physical LoRa replay
→ parsed receiver log
→ manifest-bound schedule-aware analysis
```

## 9. Proposed files

Potential Run 029 source input:

```
traces/run029_longer_adapter_input.csv
```

Potential full schedule outputs:

```
traces/run029_reporting_txa_fixed_all_schedule.csv
traces/run029_reporting_txb_usefulness_threshold_schedule.csv
```

Potential SD schedule outputs:

```
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
```

Potential receiver outputs for later physical replay:

```
logs/rx_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay_rejects.csv
```

Potential reports for later physical replay:

```
reports/run029_schedule_aware_manifest.json
reports/run029_schedule_aware_summary.csv
reports/run029_schedule_aware_summary.json
```

Potential development notes:

```
docs/development/longer_two_transmitter_sd_replay_design.md
docs/development/run029_longer_sd_replay.md
```

## 10. Firmware expectations

The existing Run 028 SD-backed transmitter firmware should support this run without structural changes if the schedule row count remains within the firmware’s configured maximum.

The firmware already:

* loads `/schedule.csv`;
* stores rows in RAM;
* reports `rows_loaded`, `send_rows`, and `skip_rows`;
* loops over the loaded schedule period;
* transmits on `send=1`;
* remains silent on `send=0`.

Before a physical Run 029, confirm the current maximum schedule row capacity in both transmitter sketches.

If the current maximum is:

```
MAX_SCHEDULE_ROWS = 256
```

then a 64-row schedule is comfortably within the current limit.

## 11. Validation expectations

Before any physical replay, validate the generated SD schedules.

Expected TXA validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txa_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 64 \
  --expected-skip-rows 0
```

Expected TXB validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txb_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 32 \
  --expected-skip-rows 32
```

The validator should be run before copying files to SD cards.

## 12. SD-card preparation expectations

The existing board-oriented card convention should continue:

| TX  | Node | SD volume  | SD path         |
| --- | ---- | ---------- | --------------- |
| TXA | N01  | `LORA_TXA` | `/schedule.csv` |
| TXB | N16  | `LORA_TXB` | `/schedule.csv` |

For Run 029:

| TX  | Source file copied to card          |
| --- | ----------------------------------- |
| TXA | `traces/run029_sd_txa_schedule.csv` |
| TXB | `traces/run029_sd_txb_schedule.csv` |

The manifest should record both the repository source schedule and the physical card convention.

## 13. Physical-run expectations

A later Run 029 physical replay should check:

* transmitter startup row counts;
* TXA reports 64 loaded rows, 64 SEND, 0 SKIP;
* TXB reports 64 loaded rows, 32 SEND, 32 SKIP;
* receiver parser reports valid and malformed packet counts;
* TXB/TXA observed received-packet ratio is near 0.5000;
* TXB mean delivered usefulness remains higher than TXA mean delivered usefulness.

The exact received packet counts should not be predicted in advance.

## 14. Analysis expectations

The manifest-bound analysis should compare:

| Quantity                       | Expected interpretation              |
| ------------------------------ | ------------------------------------ |
| scheduled send-fraction ratio  | known from schedule counts           |
| observed received-packet ratio | receiver-side physical outcome       |
| mean delivered usefulness      | metadata carried in received packets |
| missing sequences              | observed sequence gaps only          |
| receiver inter-arrival         | receiver-side timing only            |

The analysis should not infer:

* exact transmitted-packet counts;
* confirmed collision counts;
* true latency;
* LoRaWAN behavior;
* airtime optimization;
* energy savings;
* live belief-controller behavior.

## 15. Success criterion

Run 029 would be successful if:

1. the longer all-slot SD schedules validate;
2. both transmitters load the expected row counts from SD;
3. the receiver logs valid packets using the existing packet format;
4. the parser and manifest-bound analyzer work unchanged;
5. the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio;
6. TXB retains higher mean delivered usefulness per received packet than TXA.

The most important success criterion is not an exact packet count. It is whether the longer SD-backed schedule preserves the expected proportional scheduled-skipping behavior under physical replay.

## 16. Cautions

The usual cautions remain:

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
* Do not overgeneralize from a two-transmitter lab run.

## 17. Next step after this design

After this design milestone, the next implementation milestone should generate the Run 029 64-row schedule artifacts.

Suggested next milestone:

```
v3.0-run029-longer-sd-schedule-prep
```

Possible branch:

```
exp045-run029-longer-sd-schedule-prep
```

That milestone should create and validate the Run 029 source trace, full schedule CSVs, and SD schedule CSVs before any physical replay.
