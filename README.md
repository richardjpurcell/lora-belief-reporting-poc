# LoRa Belief-Reporting Proof of Concept

This repository contains a small-scale ESP32/LilyGO LoRa proof of concept for studying delivery-versus-usefulness reporting under constrained point-to-point LoRa airtime.

Synthetic sensing packets carry communication metadata and belief/usefulness metadata. A physical LoRa receiver supplies real receiver-side delivery outcomes, including packet counts, RSSI, SNR, receiver inter-arrival timing, and sequence-gap behaviour.

The central research motivation is:

> information delivery is not the same as information usefulness.

This is a laboratory proof of concept for logging, parsing, and analyzing physical delivery outcomes together with synthetic usefulness metadata.

It is not a LoRaWAN system, not an operational adaptive reporting policy, not a live belief-maintenance controller, and not an operational wildfire system.

## Current validated state

The current branch result is the Run 035 twelve-transmitter alternate-offset physical replay candidate.

Run 035 demonstrates receiver-side presence for all twelve transmitters and passes the manifest-bound replay bundle validator. The result is caveated: the successful full twelve-transmitter capture used alternate TXK/TXL firmware startup offsets and therefore does not validate the original prepared TXK/TXL phase-plan offsets.

Current branch milestone candidate:

- `v5.16-run035-twelve-transmitter-physical-replay`

Latest completed milestone on `main` before this branch:

- `v5.15-run035-twelve-transmitter-physical-prep`
- `v5.14-run035-twelve-transmitter-phase-plan`
- `v5.13-run035-twelve-transmitter-schedule-prep`
- `v5.12-run035-twelve-transmitter-cautious-bridge-design`

Previous stable physical replay milestone:

- `v5.11-run034-ten-transmitter-synthesis`

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

## Latest result: Run 035 twelve-transmitter alternate-offset physical replay

The current milestone candidate is the Run 035 twelve-transmitter physical replay milestone.

Run 035 produced an alternate-offset twelve-transmitter SD-backed scheduled physical replay candidate. The receiver-side parsed log contains all twelve transmitter identities and the manifest replay bundle validator passed all checks.

Physical replay note:

- `docs/development/run035_twelve_transmitter_physical_replay.md`

Receiver artifacts:

- `logs/rx_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv`
- `logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv`
- `logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate_rejects.csv`

Manifest-bound analysis artifacts:

- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.json`
- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.csv`
- `outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_validation.json`

Validation summary:

| Check | Value |
|---|---:|
| Manifest-bundle checks passed | 321 / 321 |
| Manifest-bundle checks failed | 0 |
| Received valid packets, summed per transmitter | 1635 |
| Parsed reject rows | 0 |

Receiver-side packet counts:

| TX | Node | Scheduled SEND rows | Received valid packets |
| --- | --- | ---: | ---: |
| TXA | N01 | 64 | 448 |
| TXB | N16 | 32 | 226 |
| TXC | N31 | 16 | 111 |
| TXD | N46 | 8 | 56 |
| TXE | N61 | 32 | 220 |
| TXF | N76 | 16 | 111 |
| TXG | N91 | 8 | 55 |
| TXH | N106 | 4 | 17 |
| TXI | N121 | 16 | 110 |
| TXJ | N136 | 8 | 54 |
| TXK | N151 | 32 | 199 |
| TXL | N166 | 4 | 28 |

Physical replay caveat:

The original prepared TXK/TXL offsets were:

| TX | Original prepared offset |
| --- | ---: |
| TXK | 14950 ms |
| TXL | 12950 ms |

Those offsets did not produce received TXK/TXL packets in the full twelve-transmitter bench condition. The successful alternate capture used:

| TX | Alternate physical offset |
| --- | ---: |
| TXK | 133 ms |
| TXL | 271 ms |

Interpretation boundary: Run 035 v5.16 should be interpreted as an alternate-offset twelve-transmitter receiver-side presence and bridge candidate. It does not establish validation of the original prepared TXK/TXL phase-plan offsets, exact transmitted-packet counts, confirmed RF collision mechanisms, absence of collisions, synchronized latency, LoRaWAN behavior, energy savings, airtime optimization, live-controller behavior, arbitrary-layout twelve-node behavior, or operational wildfire behavior.

## Reproducing the latest analysis

The Run 035 alternate parsed receiver log is:

- `logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv`

The Run 035 manifest is:

- `traces/run035_reporting_reporting_schedule_manifest.json`

Regenerate the Run 035 alternate-offset N-transmitter analysis outputs:

    python scripts/analyze_scheduled_replay_manifest_multi.py \
      --manifest traces/run035_reporting_reporting_schedule_manifest.json \
      --parsed logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv \
      --out-json outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.json \
      --out-csv outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.csv

Validate the Run 035 alternate-offset replay bundle:

    python scripts/validate_manifest_replay_bundle_multi.py \
      --manifest traces/run035_reporting_reporting_schedule_manifest.json \
      --summary-json outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.json \
      --summary-csv outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_summary.csv \
      --parsed logs/parsed_run_035_twelve_transmitter_sd_replay_candidate_alternate.csv \
      --out-json outputs/run035_twelve_transmitter_manifest_replay_candidate_alternate_validation.json

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
