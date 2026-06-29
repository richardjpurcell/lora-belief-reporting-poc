# Run 028 microSD-backed replay design

## 1. Purpose

This note designs the first concrete physical replay using the microSD-backed schedule mechanism designed in `v2.3-microsd-replay-design`.

The planned run is:

```
Run 028: microSD-backed replay of Run 027-style schedule
```

The intended milestone is:

```
v2.4-run028-microsd-replay-design
```

This is a design and implementation-planning milestone. It should define the firmware changes, SD card preparation steps, logging procedure, parser command, analysis command, and expected comparison before performing the physical replay.

The key design principle is:

> Change the schedule storage and replay mechanism only. Do not change the schedule semantics, packet format, receiver logger, parser, analyzer, transmitter count, or interpretation framework.

## 2. Current repository state

The previous milestone completed and pushed:

```
v2.3-microsd-replay-design
```

Current confirmed state after the previous merge:

```
branch: main
origin/main up to date
working tree clean
HEAD: 40f314b Merge microSD replay design
tag: v2.3-microsd-replay-design
```

The next recommended branch is:

```
exp039-run028-microsd-replay-design
```

Suggested setup commands:

```
git checkout main
git pull --ff-only
git checkout -b exp039-run028-microsd-replay-design
```

Suggested design note path:

```
docs/development/run028_microsd_replay_design.md
```

## 3. Relationship to v2.3

The `v2.3` design note established the general conservative microSD replay direction:

* use a compact firmware-facing CSV on the SD card;
* preserve full analysis-facing schedule CSVs in `traces/`;
* use `/schedule.csv` as the first simple SD-card layout;
* load schedule rows into RAM at startup;
* loop through the rows as the compiled-header implementation currently does;
* send only on rows marked `SEND`;
* remain silent on rows marked `SKIP`;
* preserve the existing packet format;
* preserve receiver logging;
* preserve parser behavior;
* preserve schedule-aware analysis;
* preserve manifest-bound reproduction.

Run 028 is the first concrete physical replay candidate for that design.

## 4. Why Run 027 is the replay target

Run 027 is the preferred target because it is the newest clean physical replay in the threshold-family sequence and uses the loose-threshold schedule.

Run 027 schedule structure:

| Transmitter | Node | Schedule type              | SEND rows |
| ----------- | ---- | -------------------------- | --------: |
| TXA         | N01  | fixed-all                  |     16/16 |
| TXB         | N16  | loose usefulness threshold |     12/16 |

Run 027 known schedule and received-packet comparison:

| Quantity                               |  Value |
| -------------------------------------- | -----: |
| Scheduled TXB/TXA SEND ratio           | 0.7500 |
| Observed TXB/TXA received-packet ratio | 0.7475 |

Run 028 should reproduce the Run 027 schedule semantics while changing only the storage and replay mechanism.

The intended comparison is:

| Run     | Replay mechanism            | TXA schedule | TXB schedule |
| ------- | --------------------------- | ------------ | ------------ |
| Run 027 | compiled firmware header    | 16/16 SEND   | 12/16 SEND   |
| Run 028 | microSD-backed schedule CSV | 16/16 SEND   | 12/16 SEND   |

## 5. Non-goals

Run 028 should not attempt to introduce new research claims or new system features.

Non-goals:

* do not change the packet payload format;
* do not change LoRa radio settings unless required for compatibility;
* do not change the receiver logger;
* do not change the parser;
* do not change the schedule-aware analyzer;
* do not change the manifest-bound analysis workflow;
* do not increase transmitter count;
* do not introduce live belief-maintenance control;
* do not introduce AWSRT-derived traces yet;
* do not claim energy savings;
* do not claim airtime optimization;
* do not infer exact transmitted-packet counts unless firmware-side counters are explicitly instrumented;
* do not infer collisions from missing sequence numbers;
* do not interpret `recv_ms` and `tx_ms` as synchronized latency.

Preferred language:

> microSD-backed reproduction of an existing scheduled-skipping replay

and:

> reduced physical transmission attempts under scheduled skipping

Avoid language such as:

> airtime optimization
> energy savings
> confirmed collisions
> measured latency
> LoRaWAN result

This remains point-to-point LoRa at 915 MHz, not LoRaWAN.

## 6. Source schedule files

Run 028 should use the Run 027 compact schedule CSVs already present in `traces/`.

TXA source file:

```
traces/run027_reporting_txa_fixed_all_compact.csv
```

TXB source file:

```
traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

The corresponding full analysis-facing schedule CSVs are:

```
traces/run027_reporting_txa_fixed_all_schedule.csv
traces/run027_reporting_txb_usefulness_threshold_schedule.csv
```

The compact CSVs should be copied to the SD cards as:

```
/schedule.csv
```

Recommended SD card preparation:

| Physical board | Node | SD card file    | Repository source                                              |
| -------------- | ---- | --------------- | -------------------------------------------------------------- |
| TXA            | N01  | `/schedule.csv` | `traces/run027_reporting_txa_fixed_all_compact.csv`            |
| TXB            | N16  | `/schedule.csv` | `traces/run027_reporting_txb_usefulness_threshold_compact.csv` |

The SD card itself is the replay medium. The repository schedule CSVs and manifest remain the reproducibility source of truth.

## 7. Expected compact CSV schema

The firmware-facing compact schedule CSV should contain only the fields needed for replay and packet metadata.

Expected compact schema:

| Column         | Meaning                       |
| -------------- | ----------------------------- |
| `demand_index` | schedule row / demand index   |
| `region_id`    | synthetic region metadata     |
| `event_type`   | synthetic event metadata      |
| `priority`     | synthetic priority metadata   |
| `usefulness`   | synthetic usefulness metadata |
| `stale_after`  | synthetic staleness metadata  |
| `policy_code`  | compact policy identifier     |
| `decision`     | `SEND` or `SKIP`              |

The firmware should not need to parse verbose analysis-facing fields such as:

* `source_id`;
* `policy_name`;
* `decision_reason`.

Those should remain available in the full schedule CSVs and manifest-bound analysis artifacts.

## 8. SD card layout

For Run 028, each transmitter SD card should have the simplest possible layout:

```
/schedule.csv
```

No `/config.json` should be required for the first physical SD replay.

This keeps the first implementation conservative and debuggable. Transmitter identity should remain encoded in the firmware sketch or board-specific constants, as in the current TXA and TXB firmware organization.

Future milestones may add:

```
/config.json
/schedule.csv
```

but this should not be part of Run 028 unless strictly necessary.

## 9. Firmware implementation target

Run 028 needs a firmware patch for the transmitter sketches.

Current transmitter firmware directories:

```
firmware/first_radio_link_TX-A/
firmware/first_radio_link_TX_B/
```

The first implementation can either patch both existing sketches directly or introduce shared helper logic later. For Run 028, direct and explicit patching is acceptable because the project still has only two active transmitters.

Firmware behavior should be:

1. initialize serial output;
2. initialize LoRa as before;
3. initialize SD;
4. open `/schedule.csv`;
5. parse compact CSV rows into an in-memory schedule array;
6. count total rows, SEND rows, and SKIP rows;
7. print a startup summary;
8. loop through the loaded schedule rows;
9. send packets on `SEND`;
10. stay silent on `SKIP`;
11. wrap back to the first row after the final row;
12. preserve the existing packet payload format.

The implementation should load all rows at startup rather than stream from SD during replay.

Reason:

* Run 027-style schedules are only 16 rows;
* startup parsing is easier to debug;
* runtime behavior remains close to the compiled-header implementation;
* SD I/O does not affect slot timing during replay.

Suggested initial maximum:

```
MAX_SCHEDULE_ROWS = 256
```

This is comfortably above the first 16-row use case while still being simple to reason about.

## 10. Startup serial checklist

Before beginning receiver logging, the transmitter serial monitor should confirm the loaded schedule.

Suggested TXA startup output:

```
SD replay mode
schedule_file=/schedule.csv
tx_id=TXA
node_id=N01
rows_loaded=16
send_rows=16
skip_rows=0
replay_period_rows=16
packet_format=existing
```

Suggested TXB startup output:

```
SD replay mode
schedule_file=/schedule.csv
tx_id=TXB
node_id=N16
rows_loaded=16
send_rows=12
skip_rows=4
replay_period_rows=16
packet_format=existing
```

Run 028 should not begin until both transmitters print the expected row counts.

## 11. Failure behavior

The first SD replay firmware should fail visibly and conservatively.

### SD initialization failure

If SD initialization fails:

* print a clear serial error;
* do not transmit packets;
* remain idle or enter an error loop.

### Missing `/schedule.csv`

If the file is missing:

* print a clear serial error;
* do not transmit packets;
* remain idle or enter an error loop.

### Malformed header

If the CSV header is missing or unexpected:

* print a clear serial error;
* do not transmit packets.

### Malformed row

If a row cannot be parsed:

* print the row number if feasible;
* print the reason if feasible;
* do not transmit packets.

### Invalid decision value

Allowed decision values:

```
SEND
SKIP
```

Any other value should stop replay.

### Too many rows

If the CSV exceeds `MAX_SCHEDULE_ROWS`:

* print a clear serial error;
* do not transmit packets.

For this milestone, fail-fast behavior is better than partial replay because it protects run provenance.

## 12. Packet format preservation

The most important implementation constraint is packet-format preservation.

The receiver logger and parser should not need to know whether a received packet came from:

* compiled trace data;
* compiled schedule data;
* microSD-loaded schedule data.

The SD-backed replay should produce the same packet field structure that the current parser expects.

Only the source of the schedule row changes.

This preserves continuity with:

* existing receiver logs;
* `scripts/parse_receiver_log.py`;
* schedule-aware analysis;
* manifest-bound replay analysis;
* multi-run comparison.

## 13. Receiver logging plan

Run 028 should use the existing receiver logger.

Likely receiver log output path:

```
logs/rx_run_028_microsd_replay.csv
```

The exact command should follow the existing repository pattern for receiver logging.

A likely command shape is:

```
python scripts/receiver_logger.py --outfile logs/rx_run_028_microsd_replay.csv
```

Before final use, confirm the current logger arguments with:

```
python scripts/receiver_logger.py --help
```

The receiver logging procedure should not be changed as part of Run 028 unless the existing command requires a filename update.

## 14. Parser plan

Run 028 should use the existing parser.

Likely parser command:

```
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_028_microsd_replay.csv \
  --out logs/parsed_run_028_microsd_replay.csv
```

Expected parser outputs:

```
logs/parsed_run_028_microsd_replay.csv
logs/parsed_run_028_microsd_replay_rejects.csv
```

The parser should not require any SD-specific options.

## 15. Schedule-aware analysis plan

Run 028 should use the existing schedule-aware analyzer from a manifest, following the manifest-bound pattern used for Runs 024--027.

Likely report outputs:

```
reports/run028_schedule_aware_manifest.json
reports/run028_schedule_aware_summary.csv
reports/run028_schedule_aware_summary.json
```

The Run 028 manifest should bind:

* parsed receiver log;
* TXA full schedule CSV;
* TXB full schedule CSV;
* TXA compact firmware-facing CSV;
* TXB compact firmware-facing CSV;
* replay mechanism;
* expected row counts;
* expected SEND/SKIP counts;
* firmware commit;
* analysis scripts;
* output report paths.

The analyzer should use the repository schedule artifacts, not the SD card contents directly.

## 16. Proposed Run 028 manifest fields

A Run 028 manifest should include fields similar to earlier schedule-aware manifests, with additional SD-specific provenance.

Suggested additional fields:

| Field                         | Meaning                                                         |
| ----------------------------- | --------------------------------------------------------------- |
| `run_id`                      | `run028_microsd_replay`                                         |
| `replay_mechanism`            | `microSD`                                                       |
| `sd_schedule_filename`        | `/schedule.csv`                                                 |
| `txa_compact_schedule_source` | `traces/run027_reporting_txa_fixed_all_compact.csv`             |
| `txb_compact_schedule_source` | `traces/run027_reporting_txb_usefulness_threshold_compact.csv`  |
| `txa_full_schedule_source`    | `traces/run027_reporting_txa_fixed_all_schedule.csv`            |
| `txb_full_schedule_source`    | `traces/run027_reporting_txb_usefulness_threshold_schedule.csv` |
| `txa_expected_rows`           | `16`                                                            |
| `txa_expected_send_rows`      | `16`                                                            |
| `txa_expected_skip_rows`      | `0`                                                             |
| `txb_expected_rows`           | `16`                                                            |
| `txb_expected_send_rows`      | `12`                                                            |
| `txb_expected_skip_rows`      | `4`                                                             |

This makes it clear that Run 028 is a storage/replay-mechanism comparison, not a new threshold-family schedule.

## 17. Expected Run 028 comparison

The first comparison should place Run 028 beside Run 027.

Expected design-level comparison:

| Run     | Replay mechanism | TXA expected SEND rows | TXB expected SEND rows | Expected scheduled TXB/TXA ratio |
| ------- | ---------------- | ---------------------: | ---------------------: | -------------------------------: |
| Run 027 | compiled header  |                  16/16 |                  12/16 |                           0.7500 |
| Run 028 | microSD          |                  16/16 |                  12/16 |                           0.7500 |

The observed received-packet ratio for Run 028 should be expected to be near 0.75 under similar lab conditions, but exact equality should not be expected.

Careful comparison language:

> Run 028 tests whether the Run 027 schedule semantics can be replayed from microSD while preserving the bounded scheduled-skipping interpretation under similar two-transmitter lab conditions.

Avoid:

> Run 028 proves equivalence between compiled-header and SD replay.

Better:

> Run 028 provides a first physical check that changing the schedule storage medium does not obviously disturb the observed schedule-ratio behavior in this small lab setup.

## 18. Expected documentation after physical replay

After the later physical replay is performed, create a separate run note:

```
docs/development/run028_microsd_replay.md
```

That note should document:

* hardware setup;
* SD card preparation;
* firmware commit;
* transmitter startup serial summaries;
* receiver log command;
* parser command;
* analyzer command;
* observed packet counts;
* observed TXB/TXA ratio;
* mean delivered usefulness by transmitter;
* comparison against Run 027;
* cautions and limitations.

The current note only designs the run. It should not include physical results.

## 19. Possible implementation sequence

Recommended staged implementation sequence after this design note:

1. Create `exp039-run028-microsd-replay-design`.
2. Add this design note.
3. Commit and optionally tag the design milestone.
4. Create a follow-up implementation branch for SD firmware changes.
5. Patch TXA firmware for SD-backed schedule loading.
6. Patch TXB firmware for SD-backed schedule loading.
7. Confirm the sketches compile.
8. Prepare TXA SD card with the fixed-all compact schedule.
9. Prepare TXB SD card with the loose-threshold compact schedule.
10. Confirm startup serial output on both boards.
11. Perform Run 028 receiver logging.
12. Parse receiver log.
13. Run manifest-bound schedule-aware analysis.
14. Compare Run 028 against Run 027.
15. Document physical results in a separate run note.
16. Merge and tag the physical replay milestone only after results are documented.

This preserves the project’s current working method: design first, implement carefully, then run and document.

## 20. Commit and tag plan for this design milestone

Recommended commit:

```
git add docs/development/run028_microsd_replay_design.md
git commit -m "Design Run 028 microSD replay"
```

Possible merge:

```
git checkout main
git merge --no-ff exp039-run028-microsd-replay-design -m "Merge Run 028 microSD replay design"
```

Possible tag:

```
git tag -a v2.4-run028-microsd-replay-design -m "v2.4 Run 028 microSD replay design"
```

Possible push:

```
git push origin main
git push origin v2.4-run028-microsd-replay-design
```

## 21. Summary

Run 028 should be the first physical replay that uses microSD-backed schedule storage.

It should reproduce the Run 027-style two-transmitter schedule:

| Transmitter | Node | Schedule                   | SEND rows |
| ----------- | ---- | -------------------------- | --------: |
| TXA         | N01  | fixed-all                  |     16/16 |
| TXB         | N16  | loose usefulness threshold |     12/16 |

The only intended change is:

| Before                            | After                               |
| --------------------------------- | ----------------------------------- |
| compiled firmware schedule header | `/schedule.csv` loaded from microSD |

The core research purpose is bounded:

> Run 028 checks whether the schedule storage/replay mechanism can move from compiled firmware headers to microSD while preserving the existing scheduled-skipping semantics, packet format, and analysis pipeline.

This is a necessary bridge toward longer traces, AWSRT-derived schedules, and eventual 12-transmitter scaling, but it should remain a small two-transmitter storage-mechanism validation run.
