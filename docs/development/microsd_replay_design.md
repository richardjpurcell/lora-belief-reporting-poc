# v2.3 microSD replay design

## 1. Purpose

This note designs the first microSD-backed replay milestone for the `lora-belief-reporting-poc` repository.

The goal is conservative: move scheduled replay data from compiled firmware headers to a microSD card while preserving the existing research semantics, packet format, receiver logging, parsing, schedule-aware analysis, manifest-bound reproduction, and bundle validation workflow.

This milestone is design-only. It does not implement or physically test SD replay.

Planned milestone:

```
v2.3-microsd-replay-design
```

Recommended branch:

```
exp038-microsd-replay-design
```

Likely later physical milestone:

```
v2.4-run028-microsd-replay
```

## 2. Why microSD now

The compiled firmware-header approach has worked well for short two-transmitter scheduled replays. It supported the threshold-family physical replay phase, including fixed-all, medium-threshold, strict-threshold, and loose-threshold scheduled skipping.

However, compiled headers will become cumbersome as the project moves toward:

* longer schedules;
* AWSRT-derived demand and reporting traces;
* repeated physical replay experiments;
* 3, 6, and eventually 12 active transmitters;
* easier field preparation and schedule swapping;
* cleaner separation between analysis artifacts and board-local replay configuration.

The microSD route should make replay schedules easier to load, inspect, replace, archive, and reproduce without recompiling firmware for every schedule change.

## 3. Relationship to the completed threshold-family phase

The threshold-family phase closed at:

```
v2.2-threshold-family-final-synthesis
```

The completed threshold-family ladder was:

| Schedule family  | Scheduled TXB SEND rows | Observed TXB/TXA ratio | TXB mean delivered usefulness |
| ---------------- | ----------------------: | ---------------------: | ----------------------------: |
| Loose threshold  |                   12/16 |                 0.7475 |                         0.667 |
| Medium threshold |                    8/16 |      0.4875 and 0.5000 |           approximately 0.785 |
| Strict threshold |                    4/16 |                 0.2520 |                         0.866 |

The careful bounded interpretation is:

> Runs 024--027 support a bounded threshold-family interpretation: changing the usefulness-threshold schedule changes the observed received-packet proportion in the expected direction, while the threshold-selected stream preserves higher mean delivered usefulness per received packet than the fixed-all stream.

The SD-card milestone should preserve this interpretation. It should not introduce new claims about airtime optimization, exact transmitted-packet counts, collisions, latency, energy, or live belief maintenance.

## 4. Non-goals

This milestone does not attempt to:

* change the packet format;
* change receiver logging;
* change parser logic;
* change schedule-aware analyzer logic;
* change the manifest-bound reproduction workflow;
* change the number of transmitters;
* introduce a live belief-maintenance controller;
* infer exact transmitted-packet counts;
* infer collisions from missing sequence numbers;
* infer latency from `recv_ms` and `tx_ms`;
* claim energy savings without current or power measurements;
* claim airtime optimization;
* generalize beyond the small point-to-point 915 MHz LoRa lab setting.

Preferred language:

> reduced physical transmission attempts under scheduled skipping

Avoid:

> airtime optimization
> energy savings
> confirmed collisions
> measured latency
> LoRaWAN behavior

## 5. First target: reproduce Run 027 from SD

The first SD-backed physical replay should reproduce an already-known two-transmitter schedule.

Preferred candidate:

```
Run 027
```

Reason:

Run 027 is the newest clean physical replay and used the loose-threshold schedule. It provides a simple and useful first SD target.

Run 027 schedule structure:

| Transmitter | Node | Policy                     | SEND rows |
| ----------- | ---- | -------------------------- | --------: |
| TXA         | N01  | fixed-all                  |     16/16 |
| TXB         | N16  | loose usefulness threshold |     12/16 |

Known Run 027 comparison point:

| Quantity                               |  Value |
| -------------------------------------- | -----: |
| Scheduled TXB/TXA SEND ratio           | 0.7500 |
| Observed TXB/TXA received-packet ratio | 0.7475 |

The first SD replay should compare:

| Replay mechanism         | Run            | Expected schedule semantics |
| ------------------------ | -------------- | --------------------------- |
| Compiled firmware header | Run 027        | TXA 16/16, TXB 12/16        |
| microSD-backed replay    | likely Run 028 | TXA 16/16, TXB 12/16        |

The ideal result for Run 028 is not bit-for-bit packet-count equality. It is a bounded reproduction of the same schedule semantics under similar lab conditions.

Expected design statement:

> Run 028 should preserve the Run 027 schedule semantics while changing only the schedule storage and firmware replay mechanism.

## 6. Existing compiled-header flow

The current scheduled replay mechanism uses generated firmware headers.

Current approximate flow:

1. Analysis-facing schedule CSVs are generated in `traces/`.
2. Compact schedule CSVs are generated in `traces/`.
3. Header files are generated for TXA and TXB.
4. Each transmitter firmware includes its corresponding schedule header.
5. Firmware loops through the schedule array.
6. Rows marked `SEND` produce packets.
7. Rows marked `SKIP` produce silence for that scheduled opportunity.
8. Receiver logger records arriving packets.
9. Parser converts receiver logs into parsed packet CSVs.
10. Schedule-aware analyzer compares parsed packets with the schedule manifest.
11. Reports and comparison summaries are generated.

This flow has been sufficient for the threshold-family phase.

The SD-backed flow should preserve the same analysis-side interpretation while replacing step 3 and the compiled-header dependency with board-local SD loading.

## 7. Proposed SD-backed flow

Proposed first SD-backed flow:

1. Preserve full analysis-facing schedule CSVs in `traces/`.
2. Generate or copy compact firmware-facing replay CSVs for each transmitter.
3. Place the compact replay CSV on the corresponding transmitter’s microSD card.
4. Firmware initializes SD at startup.
5. Firmware opens the configured schedule file.
6. Firmware parses rows into an in-memory array.
7. Firmware prints schedule identity, row count, SEND count, and SKIP count to serial output.
8. Firmware loops through the in-memory schedule array just like the compiled-header implementation.
9. Rows marked `SEND` produce packets using the existing packet format.
10. Rows marked `SKIP` remain silent for that scheduled opportunity.
11. Receiver logger remains unchanged.
12. Parser remains unchanged.
13. Schedule-aware analyzer remains unchanged.
14. Manifest-bound analysis remains unchanged.

The first implementation should load rows into RAM at startup rather than stream from SD during replay. This keeps runtime behavior closer to the compiled-header implementation and reduces timing uncertainty from SD reads.

## 8. File layout options

Three possible file layout options were considered.

### Option A: one simple file per transmitter SD card

Each SD card contains:

```
/schedule.csv
```

Advantages:

* simplest firmware configuration;
* easiest first physical test;
* no per-device filename logic;
* least opportunity for path mistakes.

Disadvantages:

* schedule identity must be confirmed through file contents or serial metadata;
* less explicit when preparing many cards.

### Option B: explicit transmitter-specific schedule file

Each SD card contains one transmitter-specific file, for example:

```
/tx_schedule.csv
```

or:

```
/TXA_schedule.csv
/TXB_schedule.csv
```

Advantages:

* clearer file identity;
* easier visual inspection when SD cards are prepared on a laptop;
* can support a shared convention across boards.

Disadvantages:

* firmware must know or be configured for the expected filename;
* slightly more naming complexity.

### Option C: device config plus schedule

Each SD card contains:

```
/config.json
/schedule.csv
```

Advantages:

* future-ready for 3, 6, and 12 transmitter scaling;
* can store node ID, transmitter ID, schedule ID, replay period, and other metadata;
* separates device identity from schedule rows.

Disadvantages:

* adds parser complexity;
* JSON parsing on microcontrollers is possible but not needed for the first SD replay;
* creates more failure modes.

## 9. Recommended first file layout

Recommended for first implementation:

```
/schedule.csv
```

Each transmitter’s SD card should contain a single firmware-facing compact schedule file named `schedule.csv`.

The schedule identity should be printed from explicit columns or constants at startup. For the first implementation, the schedule identity can also be documented through the physical preparation note and the manifest.

Recommended first physical card preparation:

| Board | Node | SD file         | Source compact CSV                                             |
| ----- | ---- | --------------- | -------------------------------------------------------------- |
| TXA   | N01  | `/schedule.csv` | `traces/run027_reporting_txa_fixed_all_compact.csv`            |
| TXB   | N16  | `/schedule.csv` | `traces/run027_reporting_txb_usefulness_threshold_compact.csv` |

This keeps the board firmware simple and places the burden of schedule identity on the experiment manifest and card-preparation procedure.

Future versions can add `/config.json` or transmitter-specific filenames once the SD replay path has been physically validated.

## 10. Firmware-facing CSV schema

The repository already contains full schedule CSVs and compact schedule CSVs for Run 027:

```
traces/run027_reporting_txa_fixed_all_schedule.csv
traces/run027_reporting_txb_usefulness_threshold_schedule.csv
traces/run027_reporting_txa_fixed_all_compact.csv
traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

The design question is whether firmware should parse the full analysis-facing schedule CSV or a compact firmware-facing replay CSV.

Recommendation:

> Use a compact firmware-facing CSV on the board. Preserve the full schedule CSV in `traces/` for reproducibility and analysis.

Reason:

The microcontroller does not need fields such as long policy names or decision reasons during replay. The firmware should only parse fields needed to preserve packet payloads and SEND/SKIP behavior.

A suitable compact firmware-facing schema is:

| Column         | Purpose                                       |
| -------------- | --------------------------------------------- |
| `demand_index` | schedule row identity / repeated period index |
| `region_id`    | synthetic demand region metadata              |
| `event_type`   | synthetic event metadata                      |
| `priority`     | synthetic priority metadata                   |
| `usefulness`   | synthetic usefulness metadata                 |
| `stale_after`  | synthetic staleness metadata                  |
| `policy_code`  | compact policy identifier                     |
| `decision`     | `SEND` or `SKIP`                              |

The firmware-facing CSV should avoid fields that are useful for analysis but unnecessary for board replay, such as:

* `source_id`;
* verbose `policy_name`;
* verbose `decision_reason`.

Those fields should remain in the full schedule CSV and manifest-bound analysis artifacts.

## 11. Startup behavior

On startup, the transmitter firmware should:

1. Initialize serial output.
2. Initialize LoRa as before.
3. Initialize SD.
4. Attempt to open `/schedule.csv`.
5. Parse the CSV header.
6. Parse schedule rows into an in-memory array.
7. Count total rows.
8. Count rows marked `SEND`.
9. Count rows marked `SKIP`.
10. Print a startup summary.

Suggested serial startup summary:

```
SD replay mode
schedule_file=/schedule.csv
node_id=N01
tx_id=TXA
rows_loaded=16
send_rows=16
skip_rows=0
replay_period_rows=16
packet_format=existing
```

For TXB Run 027-style replay:

```
SD replay mode
schedule_file=/schedule.csv
node_id=N16
tx_id=TXB
rows_loaded=16
send_rows=12
skip_rows=4
replay_period_rows=16
packet_format=existing
```

The startup summary should make it easy to confirm that the correct SD schedule was loaded before beginning receiver logging.

## 12. Runtime behavior

Runtime behavior should match the compiled-header scheduled replay as closely as possible.

For each schedule row:

* if `decision == SEND`, transmit a packet using the existing packet format;
* if `decision == SKIP`, do not transmit a packet for that scheduled slot;
* advance to the next row;
* after the final row, loop back to the first row;
* preserve the same approximate inter-slot timing used by the compiled-header scheduled replay.

The schedule CSV defines a repeated schedule period. It should not be interpreted as a one-time finite trace unless a later milestone explicitly introduces finite replay semantics.

## 13. Failure modes

The first SD firmware implementation should fail conservatively and visibly.

### SD initialization failure

If SD initialization fails:

* print a clear serial error;
* do not silently fall back to a compiled schedule;
* do not transmit packets;
* remain in a safe idle/error loop.

Rationale:

Silent fallback would make physical replay provenance ambiguous.

### Missing schedule file

If `/schedule.csv` is missing:

* print a clear serial error;
* do not transmit packets;
* remain in a safe idle/error loop.

### Malformed header

If the CSV header is missing or does not match the expected compact schema:

* print a clear serial error;
* do not transmit packets;
* remain in a safe idle/error loop.

### Malformed row

If a row is malformed:

* print the row number and reason if feasible;
* do not transmit packets;
* remain in a safe idle/error loop.

For the first implementation, fail-fast behavior is preferable to partial replay because it preserves experiment clarity.

### Too many rows

The firmware should define a maximum row count.

Initial suggested constant:

```
MAX_SCHEDULE_ROWS = 256
```

This is much larger than the 16-row schedules used in Run 027, but still simple for early testing.

If the schedule exceeds the maximum row count:

* print a clear serial error;
* do not transmit packets;
* remain in a safe idle/error loop.

The maximum can be increased later after memory use is measured.

### Invalid decision value

Allowed values:

```
SEND
SKIP
```

If any other decision value appears:

* print a clear serial error;
* do not transmit packets.

## 14. RAM loading versus streaming

Recommendation for the first implementation:

> Load the schedule into RAM at startup.

Rationale:

* 16-row schedules are tiny;
* startup parsing is easier to debug than runtime SD reads;
* replay timing remains closer to compiled-header replay;
* SD I/O does not occur during scheduled slot execution;
* failure happens before the experiment begins rather than during replay.

Streaming row-by-row from SD can be considered later if schedule sizes grow beyond comfortable RAM limits.

Early experiments are expected to fit in RAM, even if schedules grow from 16 rows to hundreds of rows.

## 15. Preserving packet format

The first SD replay must preserve the current packet payload format.

The receiver logger and parser should not need to know whether a packet came from:

* a compiled trace header;
* a compiled schedule header;
* a microSD-loaded schedule row.

This is central to the design.

The only intended difference is where the transmitter obtains replay-row metadata.

The packet should continue to include the existing fields used by the parser and analyzer, including transmitter identity, node identity, sequence, metadata fields, and checksum/CRC behavior as currently implemented.

## 16. TXA and TXB separation

For the first SD replay, TXA and TXB should remain separate firmware sketches or separate board configurations, consistent with the current repository structure.

Current firmware directories:

```
firmware/first_radio_link_TX-A/
firmware/first_radio_link_TX_B/
```

First SD design should not require a general multi-transmitter firmware abstraction.

Each transmitter gets its own SD card containing `/schedule.csv`.

Suggested first SD contents:

TXA SD card:

```
/schedule.csv
    copied from traces/run027_reporting_txa_fixed_all_compact.csv
```

TXB SD card:

```
/schedule.csv
    copied from traces/run027_reporting_txb_usefulness_threshold_compact.csv
```

The card label, board label, startup serial output, and run manifest should all agree.

## 17. Reproducibility and manifests

The SD-backed replay should remain manifest-bound.

For the later Run 028 physical replay, the manifest should record:

* run ID;
* replay mechanism: `microSD`;
* source full schedule CSV for TXA;
* source full schedule CSV for TXB;
* source compact firmware-facing CSV for TXA;
* source compact firmware-facing CSV for TXB;
* SD filename used on each board;
* expected row count for each board;
* expected SEND count for each board;
* expected SKIP count for each board;
* firmware commit;
* parser version;
* analyzer version;
* receiver log filename;
* parsed log filename;
* schedule-aware report filename.

The analyzer should continue to use repository-side schedule artifacts and manifest paths, not the physical SD card itself.

The SD card is a replay medium. The repository remains the source of reproducible analysis truth.

## 18. Planned v2.4 physical replay

The likely next physical milestone after this design is:

```
v2.4-run028-microsd-replay
```

Possible run name:

```
Run 028: microSD-backed replay of Run 027-style schedule
```

Expected setup:

| Board | Node | Replay source                                                    | Expected SEND rows |
| ----- | ---- | ---------------------------------------------------------------- | -----------------: |
| TXA   | N01  | microSD `/schedule.csv` from Run 027 fixed-all compact CSV       |              16/16 |
| TXB   | N16  | microSD `/schedule.csv` from Run 027 loose-threshold compact CSV |              12/16 |

Expected comparison:

| Run     | Replay mechanism | TXA schedule | TXB schedule | Expected TXB/TXA scheduled ratio |
| ------- | ---------------- | ------------ | ------------ | -------------------------------: |
| Run 027 | compiled header  | 16/16 SEND   | 12/16 SEND   |                           0.7500 |
| Run 028 | microSD          | 16/16 SEND   | 12/16 SEND   |                           0.7500 |

Careful expected interpretation:

> If Run 028 produces a received-packet ratio near the Run 027 result under similar lab conditions, it will support the claim that the schedule storage/replay mechanism can be changed from compiled headers to microSD without changing the bounded scheduled-skipping interpretation.

Avoid claiming exact equivalence because physical LoRa packet reception varies across runs.

## 19. Future path to AWSRT-derived traces

The SD replay path is important for AWSRT-derived traces because future traces may be longer and more varied than the current 16-row schedules.

The intended future path is:

1. Generate AWSRT-derived demand or belief-reporting traces.
2. Convert them into analysis-facing schedule CSVs.
3. Generate compact firmware-facing replay CSVs.
4. Place compact replay CSVs on transmitter SD cards.
5. Run physical scheduled replay.
6. Parse receiver logs.
7. Analyze received packets against manifest-bound schedule artifacts.
8. Compare physical replay behavior against the intended schedule semantics.

At that stage, usefulness and priority may still be synthetic or trace-derived metadata unless a live controller is introduced. The project should continue to distinguish clearly between replaying a schedule and performing live belief-maintenance control.

## 20. Future path to 12 transmitters

The medium-term hardware planning target is:

```
12 active transmitters
2 spare boards
```

The microSD design should support this direction without needing to solve all scaling issues immediately.

Possible future 12-transmitter SD preparation pattern:

| Item                   | Future convention                                       |
| ---------------------- | ------------------------------------------------------- |
| Board label            | TX01 through TX12                                       |
| Node label             | N01 through N12 or mapped region IDs                    |
| SD schedule file       | `/schedule.csv`                                         |
| Optional future config | `/config.json`                                          |
| Repository source      | `traces/runXXX_tx##_compact.csv`                        |
| Manifest source        | run-level JSON manifest binding each TX to its schedule |

The first SD design should not overbuild for 12 transmitters. It should simply avoid choices that would block the 12-transmitter path.

The most important future-proofing step is to keep schedule identity and transmitter identity explicit in the repository manifest and serial startup output.

## 21. Documentation and commit plan

Recommended v2.3 file:

```
docs/development/microsd_replay_design.md
```

Recommended branch:

```
exp038-microsd-replay-design
```

Recommended commit:

```
git add docs/development/microsd_replay_design.md
git commit -m "Design microSD-backed scheduled replay"
```

Recommended merge and tag after review:

```
git checkout main
git merge --no-ff exp038-microsd-replay-design -m "Merge microSD replay design"
git tag -a v2.3-microsd-replay-design -m "v2.3 microSD replay design"
git push origin main
git push origin v2.3-microsd-replay-design
```

## 22. Summary

The v2.3 milestone designs a conservative microSD-backed replay mechanism.

The first implementation should:

* use `/schedule.csv` on each transmitter SD card;
* use a compact firmware-facing CSV;
* preserve full schedule CSVs in `traces/`;
* load schedule rows into RAM at startup;
* loop over rows as the compiled-header firmware currently does;
* send only on `SEND` rows;
* remain silent on `SKIP` rows;
* preserve the existing packet format;
* preserve the receiver logger;
* preserve the parser;
* preserve schedule-aware analysis;
* preserve manifest-bound reproduction;
* fail visibly and conservatively on SD, file, or CSV errors.

The first physical SD replay should be Run 028, a microSD-backed reproduction of the Run 027-style schedule:

| Board   | Schedule                    |
| ------- | --------------------------- |
| TXA/N01 | fixed-all, 16/16 SEND       |
| TXB/N16 | loose threshold, 12/16 SEND |

The scientific role of Run 028 should be bounded:

> Run 028 tests whether the schedule storage and replay mechanism can move from compiled firmware headers to microSD while preserving the existing scheduled-skipping interpretation under similar two-transmitter lab conditions.
