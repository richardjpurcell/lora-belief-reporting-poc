# Run 033 eight-transmitter schedule prep

## Purpose

This note records the Run 033 eight-transmitter schedule-preparation milestone.

The purpose is to prepare repository-side schedule artifacts for the planned eight-transmitter bridge from the validated Run 032 six-transmitter replay toward the eventual twelve-transmitter platform.

This milestone does not copy schedules to SD cards, flash firmware, run hardware, collect receiver logs, or make physical replay claims.

## Repair completed first

Before generating Run 033 schedules, this milestone restored two accidentally emptied Run 032 artifacts:

| File | Repair |
| ---- | ------ |
| `scripts/prepare_run032_six_tx_schedules.py` | Restored from the last known non-empty version. |
| `traces/run032_reporting_reporting_schedule_manifest.json` | Restored from the last known non-empty version. |

This repair was necessary because Run 033 schedule prep should be based on a real Run 032 schedule-preparation pattern, not an empty script or empty manifest.

## Generated Run 033 artifacts

Schedule-preparation script:

* `scripts/prepare_run033_eight_tx_schedules.py`

Manifest:

* `traces/run033_reporting_reporting_schedule_manifest.json`

Base schedule copy:

* `traces/run033_eight_tx_base_schedule.csv`

Repository-side all-slot schedule CSVs:

| Transmitter | File |
| ----------- | ---- |
| TXA | `traces/run033_reporting_txa_fixed_all_schedule.csv` |
| TXB | `traces/run033_reporting_txb_medium_threshold_schedule.csv` |
| TXC | `traces/run033_reporting_txc_strict_threshold_schedule.csv` |
| TXD | `traces/run033_reporting_txd_very_strict_threshold_schedule.csv` |
| TXE | `traces/run033_reporting_txe_medium_threshold_schedule.csv` |
| TXF | `traces/run033_reporting_txf_strict_threshold_schedule.csv` |
| TXG | `traces/run033_reporting_txg_very_strict_threshold_schedule.csv` |
| TXH | `traces/run033_reporting_txh_ultra_strict_threshold_schedule.csv` |

Compact SEND-only inspection CSVs:

| Transmitter | File |
| ----------- | ---- |
| TXA | `traces/run033_reporting_txa_fixed_all_compact.csv` |
| TXB | `traces/run033_reporting_txb_medium_threshold_compact.csv` |
| TXC | `traces/run033_reporting_txc_strict_threshold_compact.csv` |
| TXD | `traces/run033_reporting_txd_very_strict_threshold_compact.csv` |
| TXE | `traces/run033_reporting_txe_medium_threshold_compact.csv` |
| TXF | `traces/run033_reporting_txf_strict_threshold_compact.csv` |
| TXG | `traces/run033_reporting_txg_very_strict_threshold_compact.csv` |
| TXH | `traces/run033_reporting_txh_ultra_strict_threshold_compact.csv` |

Repository-side SD-facing schedule CSVs:

| Transmitter | File |
| ----------- | ---- |
| TXA | `traces/run033_sd_txa_schedule.csv` |
| TXB | `traces/run033_sd_txb_schedule.csv` |
| TXC | `traces/run033_sd_txc_schedule.csv` |
| TXD | `traces/run033_sd_txd_schedule.csv` |
| TXE | `traces/run033_sd_txe_schedule.csv` |
| TXF | `traces/run033_sd_txf_schedule.csv` |
| TXG | `traces/run033_sd_txg_schedule.csv` |
| TXH | `traces/run033_sd_txh_schedule.csv` |

## Source schedule

The Run 033 script uses the normalized all-slot Run 032 TXA schedule as its source:

* `traces/run032_reporting_txa_fixed_all_schedule.csv`

This is intentional.

The wider Run 032 base schedule, `traces/run032_six_tx_base_schedule.csv`, has source/decision columns and is not directly in the SD-facing schedule schema. The TXA all-slot schedule has the normalized schema:

| Column |
| ------ |
| `seq` |
| `region` |
| `event` |
| `priority` |
| `usefulness` |
| `stale_after` |
| `policy` |
| `send` |

The Run 033 script rewrites `policy` and `send` for each transmitter.

## Run 033 candidate ladder

| Transmitter | Node | Role | Expected SEND rows |
| ----------- | ---: | ---- | -----------------: |
| TXA | N01 | fixed-all anchor | 64/64 |
| TXB | N16 | medium threshold scheduled skipping | 32/64 |
| TXC | N31 | strict threshold scheduled skipping | 16/64 |
| TXD | N46 | very-strict threshold scheduled skipping | 8/64 |
| TXE | N61 | medium threshold scheduled skipping | 32/64 |
| TXF | N76 | strict threshold scheduled skipping | 16/64 |
| TXG | N91 | very-strict threshold scheduled skipping | 8/64 |
| TXH | N106 | ultra-strict threshold scheduled skipping | 4/64 |

Expected receiver-side ratios relative to TXA:

| Ratio | Expected |
| ----- | -------: |
| TXB/TXA | 0.5000 |
| TXC/TXA | 0.2500 |
| TXD/TXA | 0.1250 |
| TXE/TXA | 0.5000 |
| TXF/TXA | 0.2500 |
| TXG/TXA | 0.1250 |
| TXH/TXA | 0.0625 |

These are scheduled SEND ratios, not exact transmitted-packet counts.

## Validation checks performed

The generated manifest records:

* run ID;
* milestone;
* source schedule;
* schedule period length;
* SD schedule schema;
* eight transmitter entries;
* expected SEND rows;
* expected skip rows;
* compact CSV paths;
* repository-side SD CSV paths;
* expected scheduled ratios relative to TXA;
* interpretation boundary.

The generated schedule files were checked for:

* eight transmitter entries;
* 64 all-slot rows per schedule file;
* expected SEND row counts;
* compact SEND-only row counts matching expected SEND rows;
* 64 rows per SD-facing schedule file;
* expected ratio metadata.

## Phase-plan status

Startup offsets are intentionally not fixed in this milestone.

The Run 033 manifest marks startup offsets as deferred to the later physical-preparation milestone.

This preserves the v5 ladder:

1. bridge design;
2. schedule prep;
3. physical prep;
4. physical replay;
5. synthesis.

## Interpretation boundary

This milestone prepares schedule artifacts only.

It does not establish:

* exact transmitted-packet counts;
* confirmed RF collisions or absence of RF collisions;
* synchronized latency;
* LoRaWAN behavior;
* airtime optimization;
* energy optimization;
* live-controller behavior;
* eight-transmitter physical replay behavior;
* twelve-transmitter behavior;
* operational wildfire or deployment behavior.

## Recommended next milestone

Recommended next milestone:

* `v5.2-run033-eight-transmitter-physical-prep`

The next milestone should prepare the physical bench procedure, startup offsets, board identity mapping, SD-card copy checklist, receiver checklist, and post-run analysis checklist.

It should still avoid making replay claims until a receiver log has actually been collected and analyzed.
