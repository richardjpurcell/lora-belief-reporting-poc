# LoRa Belief-Reporting Proof of Concept

This repository contains a small-scale ESP32/LilyGO LoRa proof of concept for studying delivery-versus-usefulness reporting under constrained point-to-point LoRa airtime.

Synthetic sensing packets carry communication metadata and belief/usefulness metadata. A physical LoRa receiver supplies real receiver-side delivery outcomes, including packet counts, RSSI, SNR, receiver inter-arrival timing, and sequence-gap behaviour.

The central research motivation is:

> information delivery is not the same as information usefulness.

This is a laboratory proof of concept for logging, parsing, and analyzing physical delivery outcomes together with synthetic usefulness metadata.

It is not a LoRaWAN system, not an operational adaptive reporting policy, not a live belief-maintenance controller, and not an operational wildfire system.

## Current validated state

The current validated scale point is the Run 032 six-transmitter SD-backed physical replay.

Latest completed milestone on this branch:

- `v4.9-run032-six-transmitter-synthesis`

Previous stable tag before this branch:

- `v4.7-run032-six-transmitter-physical-prep`

Run 032 physical transmitter set:

| Transmitter | Node | Role | Scheduled SEND rows | Scheduled SKIP rows | Startup offset ms |
|---|---:|---|---:|---:|---:|
| TXA | N01 | fixed-all anchor | 64 | 0 | 500 |
| TXB | N16 | medium threshold scheduled skipping | 32 | 32 | 2750 |
| TXC | N31 | strict threshold scheduled skipping | 16 | 48 | 4250 |
| TXD | N46 | very-strict threshold scheduled skipping | 8 | 56 | 0 |
| TXE | N61 | medium threshold scheduled skipping | 32 | 32 | 7250 |
| TXF | N76 | strict threshold scheduled skipping | 16 | 48 | 2000 |

The physical phase order used for the Run 032 bridge candidate was:

TXD -> TXA -> TXF -> TXB -> TXC -> TXE

## Latest result: Run 032 six-transmitter physical replay

Run 032 produced:

| Transmitter | Node | Received valid packets | Scheduled SEND fraction |
|---|---:|---:|---:|
| TXA | N01 | 442 | 1.000 |
| TXB | N16 | 220 | 0.500 |
| TXC | N31 | 110 | 0.250 |
| TXD | N46 | 55 | 0.125 |
| TXE | N61 | 219 | 0.500 |
| TXF | N76 | 110 | 0.250 |

Parser summary:

- Valid packets: 1156
- Malformed packets: 0
- Missing observed transmitted sequences: none for all six transmitters

Expected-vs-observed receiver-side ratios relative to TXA:

| Ratio | Observed receiver-side ratio | Expected scheduled ratio | Difference |
|---|---:|---:|---:|
| TXB/TXA | 0.4977 | 0.5000 | -0.0023 |
| TXC/TXA | 0.2489 | 0.2500 | -0.0011 |
| TXD/TXA | 0.1244 | 0.1250 | -0.0006 |
| TXE/TXA | 0.4955 | 0.5000 | -0.0045 |
| TXF/TXA | 0.2489 | 0.2500 | -0.0011 |

Bundle validation result:

- Validation summary: 171/171 checks passed; 0 failed

Detailed notes:

- `docs/development/run032_six_transmitter_physical_replay.md`
- `docs/development/run032_six_transmitter_synthesis.md`

## Reproducing the latest analysis

The Run 032 parsed receiver log is:

- `logs/parsed_run_032_six_transmitter_sd_replay.csv`

The Run 032 manifest is:

- `traces/run032_reporting_reporting_schedule_manifest.json`

Regenerate the Run 032 N-transmitter analysis outputs:

    python scripts/analyze_scheduled_replay_manifest_multi.py \
      --manifest traces/run032_reporting_reporting_schedule_manifest.json \
      --parsed logs/parsed_run_032_six_transmitter_sd_replay.csv \
      --out-json outputs/run032_six_transmitter_manifest_replay_summary.json \
      --out-csv outputs/run032_six_transmitter_manifest_replay_summary.csv

Validate the Run 032 replay bundle:

    python scripts/validate_manifest_replay_bundle_multi.py \
      --manifest traces/run032_reporting_reporting_schedule_manifest.json \
      --summary-json outputs/run032_six_transmitter_manifest_replay_summary.json \
      --summary-csv outputs/run032_six_transmitter_manifest_replay_summary.csv \
      --parsed logs/parsed_run_032_six_transmitter_sd_replay.csv \
      --out-json outputs/run032_six_transmitter_manifest_replay_validation.json

Preferred tools for list-valued N-transmitter manifests:

- `scripts/analyze_scheduled_replay_manifest_multi.py`
- `scripts/validate_manifest_replay_bundle_multi.py`

Older two-transmitter tools remain available for earlier historical artifacts.

## Repository structure

| Path | Purpose |
|---|---|
| `docs/development/` | Development notes, run documentation, design notes, and milestone history |
| `firmware/` | Arduino sketches for RX and TX boards |
| `logs/` | Raw and parsed receiver logs |
| `outputs/` | Analysis summaries and validation outputs |
| `scripts/` | Python logging, parsing, schedule, analysis, and validation scripts |
| `traces/` | Demand traces, reporting schedules, SD schedules, and manifests |
| `figures/` | Figures for notes or papers |
| `notes/` | Scratch notes and early pitch material |

## Current replay path

The current SD-backed scheduled replay path is:

1. full analysis-facing SEND/SKIP schedule CSV;
2. all-slot SD schedule CSV;
3. `/schedule.csv` on each transmitter microSD card;
4. firmware loads schedule rows at startup;
5. `SEND` rows transmit LoRa packets;
6. `SKIP` rows remain silent;
7. receiver log is parsed;
8. manifest-bound N-transmitter analysis compares scheduled and observed receiver-side proportions;
9. bundle validator checks manifest, schedules, parsed logs, summaries, and interpretation-boundary metadata.

The SD-facing schedule schema is:

`seq,region,event,priority,usefulness,stale_after,policy,send`

where `send=1` means transmit and `send=0` means remain silent for that schedule slot.

SEND-only compact CSVs are not SD replay schedules because they omit skipped slots.

## Scope boundaries

The project currently supports bounded receiver-side replay analysis.

The analysis may report:

- valid and malformed receiver rows;
- receiver-side packet counts;
- observed sequence gaps;
- RSSI and SNR summaries;
- receiver inter-arrival timing;
- synthetic delivered usefulness and priority summaries;
- receiver-side packet proportions relative to scheduled SEND ratios.

The analysis does not infer:

- exact physical transmitted-packet counts;
- confirmed RF collisions or absence of RF collisions;
- synchronized packet latency;
- LoRaWAN behavior;
- airtime or energy optimization;
- live-controller behavior;
- 12-transmitter behaviour from smaller runs;
- operational wildfire or deployment behaviour.

Missing sequence numbers should not be overinterpreted as collisions. A missing sequence means that a packet was not received or not logged within the observed sequence range. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB issues, or logger-side effects.

The usefulness and priority fields are synthetic metadata. They are not yet generated by a live belief-maintenance controller.

The setup uses point-to-point LoRa at 915 MHz. It is not a LoRaWAN system.

`recv_ms` and `tx_ms` are measured on different boards and should not be interpreted as synchronized packet-latency measurements.

## Milestone history

The former long README milestone history has been moved to:

- `docs/development/project_milestone_history.md`

That file preserves the chronological development record from early heartbeat tests through the multi-transmitter SD replay milestones.
