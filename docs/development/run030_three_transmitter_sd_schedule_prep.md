# Run 030 three-transmitter SD schedule preparation

Milestone: v3.5-three-transmitter-sd-schedule-prep
Branch: exp050-three-transmitter-sd-schedule-prep
Status: Schedule-preparation milestone

## 1. Purpose

This milestone prepares the schedule artifacts for the first three-transmitter microSD-backed replay.

It follows the design milestone:

```
v3.4-three-transmitter-sd-replay-design
```

The core question carried forward from v3.4 is:

```
Can the SD-backed, manifest-bound replay workflow remain readable when we move from two transmitters to three transmitters?
```

This milestone is schedule-preparation only.

It does not copy files to SD cards.

It does not flash firmware.

It does not perform physical startup checks.

It does not run the receiver logger.

It does not collect or parse a physical replay log.

Those steps are deferred to later milestones.

## 2. Confirmed repository state

The v3.4 design milestone has been merged and tagged on `main`:

```
v3.4-three-transmitter-sd-replay-design
```

The current v3 schedule sequence is:

```
v3.0-run029-longer-sd-schedule-prep
v3.1-run029-longer-sd-physical-prep
v3.2-run029-longer-sd-physical-replay
v3.3-longer-sd-replay-synthesis
v3.4-three-transmitter-sd-replay-design
```

This milestone begins the next sequence:

```
v3.5-three-transmitter-sd-schedule-prep
v3.6-three-transmitter-sd-physical-prep
v3.7-three-transmitter-sd-physical-replay
v3.8-three-transmitter-sd-replay-synthesis
```

## 3. Design decision carried forward

The third transmitter identity is now:

```
TXC/N31
```

The three-transmitter schedule design is:

```
TXA/N01: fixed-all baseline, 64/64 SEND
TXB/N16: medium threshold, 32/64 SEND
TXC/N31: strict threshold, 16/64 SEND
```

The schedule period remains:

```
64 rows
```

The packet format should be preserved.

The SD-facing schedule files remain all-slot CSVs copied to each card as:

```
/schedule.csv
```

Expected SD schedule schema:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

Compact SEND-only CSVs remain analysis/reference artifacts and should not be copied to SD cards as `/schedule.csv`.

## 4. Why this milestone exists

Run 028 established the first successful 16-row microSD-backed physical replay.

Run 029 extended the SD-backed replay path to a 64-row schedule.

The next uncertainty is no longer basic SD schedule storage. The next uncertainty is whether the manifest-bound workflow remains readable when a third transmitter is introduced.

This milestone prepares that test while preserving the project’s small-milestone discipline.

## 5. Script inspection result

The current schedule-generation script is still oriented around two transmitters.

The help output for `scripts/make_reporting_schedule.py` exposes:

```
--txa-policy
--txb-policy
--threshold
```

It does not yet expose:

```
--txc-policy
--txc-node-id
separate thresholds per transmitter
a generic transmitter configuration file
an arbitrary list of transmitter streams
```

This is acceptable for the earlier TXA/TXB runs, but the three-transmitter schedule-prep milestone should not hide this limitation.

The current analyzer path also contains two-transmitter comparison assumptions. In particular, the existing scheduled replay analysis uses baseline/comparison language and ratio fields that were designed for TXB/TXA comparisons.

That does not prevent schedule artifact preparation, but it means later analysis must be handled carefully.

## 6. Recommended v3.5 approach

For v3.5, use the smallest safe tooling extension that produces explicit three-transmitter artifacts without changing firmware or physical replay behavior.

The preferred approach is:

1. Preserve the existing two-transmitter schedule-generation path for earlier runs.
2. Add a simple Run 030-specific schedule preparation route, or extend the generator carefully.
3. Produce explicit TXA, TXB, and TXC full schedules.
4. Produce compact SEND-only reference CSVs for TXA, TXB, and TXC.
5. Produce SD-facing all-slot CSVs for TXA, TXB, and TXC.
6. Validate all three SD-facing CSVs.
7. Record the manifest and schedule counts.
8. Do not perform physical preparation in this milestone.

The safest implementation choice is a small Run 030 preparation script or a minimal generator extension that avoids disturbing prior runs.

A generic many-transmitter scheduler can come later. The immediate goal is not full scaling infrastructure. The immediate goal is a clear, reproducible three-transmitter schedule set.

## 7. Expected output files

This milestone should produce:

```
traces/run030_three_tx_adapter_input.csv

traces/run030_reporting_reporting_schedule_manifest.json

traces/run030_reporting_txa_fixed_all_schedule.csv
traces/run030_reporting_txa_fixed_all_compact.csv

traces/run030_reporting_txb_medium_threshold_schedule.csv
traces/run030_reporting_txb_medium_threshold_compact.csv

traces/run030_reporting_txc_strict_threshold_schedule.csv
traces/run030_reporting_txc_strict_threshold_compact.csv

traces/run030_sd_txa_schedule.csv
traces/run030_sd_txb_schedule.csv
traces/run030_sd_txc_schedule.csv
```

The development note for this milestone is:

```
docs/development/run030_three_transmitter_sd_schedule_prep.md
```

A short README addendum should also be added.

## 8. Expected schedule counts

Expected all-slot row counts:

```
TXA/N01: 64 rows
TXB/N16: 64 rows
TXC/N31: 64 rows
```

Expected SEND counts:

```
TXA/N01: 64/64 SEND
TXB/N16: 32/64 SEND
TXC/N31: 16/64 SEND
```

Expected SKIP counts:

```
TXA/N01: 0/64 SKIP
TXB/N16: 32/64 SKIP
TXC/N31: 48/64 SKIP
```

Expected scheduled ratios against TXA:

```
TXB/TXA: 32/64 = 0.5000
TXC/TXA: 16/64 = 0.2500
```

Expected scheduled ratio between thresholded transmitters:

```
TXC/TXB: 16/32 = 0.5000
```

These are scheduled-send proportions only. They are not transmitted-packet counts, collision counts, or energy measurements.

## 9. Policy labels

Recommended schedule policy labels:

```
fixed_all
usefulness_threshold_medium
usefulness_threshold_strict
```

The exact label strings should remain simple and parser-safe.

For compatibility with earlier schedule files, the compact and SD-facing CSVs should preserve simple field values where possible. If the existing scripts expect `fixed_all` and `usefulness_threshold`, then the threshold family can be documented in filenames and manifest fields rather than requiring a new policy string in every row.

A safe convention is:

```
TXA row policy value: fixed_all
TXB row policy value: usefulness_threshold
TXC row policy value: usefulness_threshold
```

and manifest metadata records:

```
TXB threshold_family: medium
TXB expected_send_rows: 32
TXC threshold_family: strict
TXC expected_send_rows: 16
```

This avoids introducing a packet-format or parser change during schedule preparation.

## 10. Manifest requirements

The Run 030 manifest should record:

```
run_id
milestone
schedule_period_rows
transmitter count
transmitter identities
node IDs
schedule file paths
compact file paths
SD-facing file paths
expected rows per transmitter
expected SEND rows per transmitter
expected SKIP rows per transmitter
expected scheduled ratios
interpretation cautions
```

The manifest should make clear that TXC/N31 is the third transmitter.

It should also make clear that the SD-facing files are all-slot schedules and that compact files are not SD-card files.

## 11. Validation commands

Each SD-facing schedule should validate independently.

Expected validation commands:

```
python scripts/validate_sd_schedule.py \
    --infile traces/run030_sd_txa_schedule.csv \
    --expected-rows 64 \
    --expected-send-rows 64 \
    --expected-skip-rows 0

python scripts/validate_sd_schedule.py \
    --infile traces/run030_sd_txb_schedule.csv \
    --expected-rows 64 \
    --expected-send-rows 32 \
    --expected-skip-rows 32

python scripts/validate_sd_schedule.py \
    --infile traces/run030_sd_txc_schedule.csv \
    --expected-rows 64 \
    --expected-send-rows 16 \
    --expected-skip-rows 48
```

The validation result should be included in the milestone summary.

## 12. Schedule review commands

After artifact generation, inspect the headers and first rows:

```
head -5 traces/run030_sd_txa_schedule.csv
head -5 traces/run030_sd_txb_schedule.csv
head -5 traces/run030_sd_txc_schedule.csv
```

Check row counts:

```
wc -l traces/run030_sd_txa_schedule.csv
wc -l traces/run030_sd_txb_schedule.csv
wc -l traces/run030_sd_txc_schedule.csv
```

Because each file has a header plus 64 data rows, each file should have 65 lines.

Check SEND counts:

```
python - <<'PY'
import csv
from pathlib import Path

for path in [
    Path("traces/run030_sd_txa_schedule.csv"),
    Path("traces/run030_sd_txb_schedule.csv"),
    Path("traces/run030_sd_txc_schedule.csv"),
]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    send = sum(1 for r in rows if str(r["send"]).strip() == "1")
    skip = sum(1 for r in rows if str(r["send"]).strip() == "0")
    print(path, "rows", len(rows), "send", send, "skip", skip)
PY
```

Expected output:

```
traces/run030_sd_txa_schedule.csv rows 64 send 64 skip 0
traces/run030_sd_txb_schedule.csv rows 64 send 32 skip 32
traces/run030_sd_txc_schedule.csv rows 64 send 16 skip 48
```

## 13. Analyzer boundary

This milestone does not need to solve all analysis generalization.

However, it should record that the current analysis path was originally shaped around TXA/TXB comparisons.

For the later physical replay milestone, analysis should either:

1. generalize the analyzer to support an arbitrary manifest-listed transmitter set; or
2. produce a careful Run 030-specific summary that reports per-transmitter packet counts and scheduled proportions without relying on a single TXB/TXA comparison field.

The desired later Run 030 analysis should report:

```
received packets by tx_id and node_id
malformed packet count
observed sequence gaps by tx_id and node_id
scheduled SEND rows by tx_id and node_id
observed packet proportions by tx_id and node_id
scheduled packet proportions by tx_id and node_id
mean delivered usefulness by tx_id and node_id
receiver-side inter-arrival summaries
```

It should avoid claiming:

```
exact transmitted-packet counts
confirmed collisions
true latency
synchronized latency
LoRaWAN behavior
energy savings
network scaling
operational wildfire behavior
```

## 14. Physical preparation deferred

The later v3.6 milestone should perform physical preparation.

That milestone should confirm:

```
TXA physical label and node ID N01
TXB physical label and node ID N16
TXC physical label and node ID N31
each board has the intended SD-facing file copied as /schedule.csv
no compact SEND-only file is copied as /schedule.csv
each board reports the expected row count at startup
each board reports the expected SEND count at startup
receiver logging is ready before replay begins
```

None of those physical steps are part of v3.5.

## 15. Cautions preserved

This remains point-to-point LoRa at 915 MHz, not LoRaWAN.

The schedule CSVs define one repeated schedule period.

The analyzer compares schedule proportions and observed packet proportions.

The analyzer does not infer exact transmitted-packet counts.

Missing sequence numbers are observed sequence gaps only, not confirmed collisions.

Receiver timestamps and transmitter timestamps are not synchronized and are not true latency.

Receiver inter-arrival summaries are receiver-side observations only.

Usefulness and priority are synthetic metadata.

The run does not use a live belief-maintenance controller.

Use the wording:

```
reduced physical transmission attempts under scheduled skipping
```

Do not use:

```
airtime optimization
```

Do not claim energy savings unless current or power measurements are added.

Do not overgeneralize from two-transmitter or three-transmitter lab runs.

## 16. Completion criteria

This milestone is complete when:

1. TXC/N31 is recorded as the third transmitter identity.
2. The Run 030 three-transmitter schedule artifacts are generated.
3. TXA, TXB, and TXC SD-facing schedules validate successfully.
4. Expected SEND/SKIP counts are confirmed.
5. The manifest records all three transmitters.
6. The README includes a short v3.5 addendum.
7. No physical replay claims are added.
8. The milestone is committed, merged to `main`, tagged, and pushed.

## 17. Summary

Run 030 schedule preparation is the first concrete artifact step toward a three-transmitter SD-backed replay.

The main result of this milestone should be a clean, validated, manifest-bound set of three all-slot SD schedules:

```
TXA/N01: 64/64 SEND
TXB/N16: 32/64 SEND
TXC/N31: 16/64 SEND
```

This prepares the project for physical startup checks in v3.6 and the first three-transmitter SD replay in v3.7.
