# Run 033 eight-transmitter physical prep

## Purpose

This note records the Run 033 eight-transmitter physical-preparation milestone.

The purpose is to prepare the physical bench plan for the eight-transmitter bridge before any receiver logging or packet collection.

This milestone does not copy SD cards, flash firmware, run the receiver, collect packets, parse packets, or make physical replay claims.

## Starting point

Run 033 already has repository-side schedule artifacts from the schedule-prep milestone:

* `scripts/prepare_run033_eight_tx_schedules.py`
* `traces/run033_reporting_reporting_schedule_manifest.json`
* `traces/run033_sd_txa_schedule.csv`
* `traces/run033_sd_txb_schedule.csv`
* `traces/run033_sd_txc_schedule.csv`
* `traces/run033_sd_txd_schedule.csv`
* `traces/run033_sd_txe_schedule.csv`
* `traces/run033_sd_txf_schedule.csv`
* `traces/run033_sd_txg_schedule.csv`
* `traces/run033_sd_txh_schedule.csv`

The physical-prep milestone adds the startup/bench plan around those schedule artifacts.

## Physical-prep artifacts

Script:

* `scripts/prepare_run033_eight_tx_physical_prep.py`

Phase-plan CSV:

* `traces/run033_eight_tx_phase_plan_physical_prep.csv`

Summary artifacts:

* `outputs/run033_eight_tx_physical_prep_summary.json`
* `outputs/run033_eight_tx_physical_prep_summary.csv`

Receiver log target for the later physical replay milestone:

* `logs/rx_run_033_eight_transmitter_sd_replay.csv`

Planned parsed-log targets for the later analysis step:

* `logs/parsed_run_033_eight_transmitter_sd_replay.csv`
* `logs/parsed_run_033_eight_transmitter_sd_replay_rejects.csv`

Planned output targets for the later physical replay analysis:

* `outputs/run033_eight_transmitter_manifest_replay_summary.json`
* `outputs/run033_eight_transmitter_manifest_replay_summary.csv`
* `outputs/run033_eight_transmitter_manifest_replay_validation.json`

## Startup and SD schedule plan

The proposed startup order preserves the successful Run 032 TXF-bridge ordering for the first six transmitters, then appends the two new bridge transmitters.

| Startup order | Transmitter | Node | Expected SEND rows | Expected ratio to TXA | Startup offset ms | SD schedule |
| -------------: | ----------- | ---: | -----------------: | --------------------: | ----------------: | ----------- |
| 1 | TXD | N46 | 8/64 | 0.125000 | 0 | `traces/run033_sd_txd_schedule.csv` |
| 2 | TXA | N01 | 64/64 | TXA anchor | 500 | `traces/run033_sd_txa_schedule.csv` |
| 3 | TXF | N76 | 16/64 | 0.250000 | 2000 | `traces/run033_sd_txf_schedule.csv` |
| 4 | TXB | N16 | 32/64 | 0.500000 | 2750 | `traces/run033_sd_txb_schedule.csv` |
| 5 | TXC | N31 | 16/64 | 0.250000 | 4250 | `traces/run033_sd_txc_schedule.csv` |
| 6 | TXE | N61 | 32/64 | 0.500000 | 7250 | `traces/run033_sd_txe_schedule.csv` |
| 7 | TXG | N91 | 8/64 | 0.125000 | 8750 | `traces/run033_sd_txg_schedule.csv` |
| 8 | TXH | N106 | 4/64 | 0.062500 | 10250 | `traces/run033_sd_txh_schedule.csv` |

The startup offsets are programmed bench-prep values. They are not synchronization claims, latency claims, or collision-avoidance claims.

## SD-card copy checklist for later bench setup

For the later physical bench setup, each repository-side SD schedule should be copied to the matching transmitter SD card as the firmware-expected schedule filename.

| Transmitter | Node | Source schedule | Destination filename |
| ----------- | ---: | --------------- | -------------------- |
| TXA | N01 | `traces/run033_sd_txa_schedule.csv` | `SCHEDULE.CSV` |
| TXB | N16 | `traces/run033_sd_txb_schedule.csv` | `SCHEDULE.CSV` |
| TXC | N31 | `traces/run033_sd_txc_schedule.csv` | `SCHEDULE.CSV` |
| TXD | N46 | `traces/run033_sd_txd_schedule.csv` | `SCHEDULE.CSV` |
| TXE | N61 | `traces/run033_sd_txe_schedule.csv` | `SCHEDULE.CSV` |
| TXF | N76 | `traces/run033_sd_txf_schedule.csv` | `SCHEDULE.CSV` |
| TXG | N91 | `traces/run033_sd_txg_schedule.csv` | `SCHEDULE.CSV` |
| TXH | N106 | `traces/run033_sd_txh_schedule.csv` | `SCHEDULE.CSV` |

This milestone does not perform that copy.

## Receiver checklist for later replay

Before the later physical replay:

1. confirm receiver firmware and serial port;
2. start receiver logging before powering transmitters;
3. record absolute start time in lab notes;
4. save the raw receiver log as `logs/rx_run_033_eight_transmitter_sd_replay.csv`;
5. do not edit the raw receiver log after capture.

## Bench checklist for later replay

Before the later physical replay:

1. confirm each board identity label TXA through TXH;
2. confirm node identities N01 through N106;
3. confirm each SD card receives the matching Run 033 schedule file;
4. confirm programmed startup offsets match `traces/run033_eight_tx_phase_plan_physical_prep.csv`;
5. record transmitter placement order;
6. record receiver placement;
7. record antenna and power conditions;
8. preserve any anomalies in lab notes.

## Post-run analysis checklist

After a later physical replay:

1. parse the raw receiver log;
2. write parsed valid-packet CSV;
3. write rejects CSV;
4. generate manifest-bound summary JSON and CSV;
5. generate manifest-bound validation JSON;
6. report receiver-side packet proportions relative to TXA;
7. report malformed/rejected rows explicitly;
8. report observed sequence gaps explicitly.

## Interpretation boundary

This milestone prepares the physical replay plan only.

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

* `v5.3-run033-eight-transmitter-physical-replay`

The next milestone should use this physical-prep plan to conduct the eight-transmitter physical replay, collect the receiver log, parse it, generate manifest-bound summary and validation outputs, and document the bounded bench result.
