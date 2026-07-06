# Run 034 ten-transmitter phase plan

## Purpose

Run 034 phase planning assigns deterministic startup offsets for the ten-transmitter scheduled replay prepared in `v5.7-run034-ten-transmitter-schedule-prep`.

This is an analysis/design milestone only. It does not modify firmware, copy schedules to SD cards, flash transmitters, collect receiver logs, or make physical replay claims.

The purpose is to preserve a phase-aware startup plan before physical preparation.

## Inputs

The phase-plan script reads the Run 034 manifest:

- `traces/run034_reporting_reporting_schedule_manifest.json`

It uses the generated Run 034 schedules from:

- `v5.7-run034-ten-transmitter-schedule-prep`

The phase-plan script is:

- `scripts/prepare_run034_ten_tx_phase_plan.py`

## Outputs

The milestone writes:

- `outputs/run034_ten_tx_phase_plan_summary.json`
- `outputs/run034_ten_tx_phase_plan_exact_coincidences.csv`
- `outputs/run034_ten_tx_phase_plan_near_coincidences.csv`

It also updates:

- `traces/run034_reporting_reporting_schedule_manifest.json`

The manifest now records assigned startup offsets for each transmitter.

## Phase-plan parameters

| Parameter | Value |
| --- | ---: |
| Slot interval | 10000 ms |
| Near-coincidence window | 150 ms |
| Transmitter count | 10 |
| Total scheduled SEND events | 204 |

## Assigned startup offsets

| TX | Node | Startup offset ms | Scheduled SEND rows |
| --- | --- | ---: | ---: |
| TXA | N01 | 1000 | 64 |
| TXB | N16 | 3250 | 32 |
| TXC | N31 | 4750 | 16 |
| TXD | N46 | 800 | 8 |
| TXE | N61 | 7750 | 32 |
| TXF | N76 | 2500 | 16 |
| TXG | N91 | 9450 | 8 |
| TXH | N106 | 100 | 4 |
| TXI | N121 | 5850 | 16 |
| TXJ | N136 | 10650 | 8 |

## Coincidence-check result

| Check | Result |
| --- | ---: |
| Exact same-ms scheduled SEND coincidences | 0 |
| Near scheduled SEND coincidences | 0 |
| Minimum pairwise scheduled SEND separation | 200 ms |
| Status | pass |

The selected deterministic startup offsets pass the schedule-time coincidence checks used in this milestone.

The exact-coincidence output contains only the CSV header because no exact same-ms scheduled SEND coincidences were found.

The near-coincidence output contains only the CSV header because no cross-transmitter scheduled SEND events were found within the configured near-coincidence window.

## Smallest pairwise separations

The smallest pairwise schedule-time separations are:

| TX A | TX B | Min delta ms | Seq A | Seq B |
| --- | --- | ---: | ---: | ---: |
| TXA/N01 | TXD/N46 | 200 | 6 | 6 |
| TXA/N01 | TXJ/N136 | 350 | 7 | 6 |
| TXD/N46 | TXH/N106 | 700 | 6 | 6 |
| TXB/N16 | TXF/N76 | 750 | 4 | 4 |
| TXA/N01 | TXH/N106 | 900 | 6 | 6 |
| TXC/N31 | TXI/N121 | 1100 | 4 | 4 |
| TXG/N91 | TXJ/N136 | 1200 | 6 | 6 |
| TXA/N01 | TXF/N76 | 1500 | 4 | 4 |
| TXB/N16 | TXC/N31 | 1500 | 4 | 4 |
| TXA/N01 | TXG/N91 | 1550 | 7 | 6 |
| TXD/N46 | TXF/N76 | 1700 | 6 | 6 |
| TXE/N61 | TXG/N91 | 1700 | 6 | 6 |

These values are schedule-time separations. They are not measured RF timings.

## Manifest update

The Run 034 manifest now records:

- assigned `startup_offset_ms` values
- `startup_offset_status` values indicating assignment by `v5.8-run034-ten-transmitter-phase-plan`
- a `phase_plan` object summarizing the check
- links to the phase-plan output files

This makes the later physical-preparation milestone manifest-bound and phase-aware.

## Interpretation boundaries

This milestone does not establish:

- ten-transmitter physical replay success
- exact transmitted-packet counts
- confirmed RF collision mechanisms
- absence of collisions
- synchronized latency
- LoRaWAN behavior
- energy savings
- airtime optimization
- live-controller behavior
- twelve-transmitter behavior
- operational wildfire deployment behavior

This milestone supports:

- deterministic startup offset assignment
- exact same-ms scheduled SEND coincidence checking
- near scheduled SEND coincidence checking
- manifest-bound handoff to physical preparation

## Next milestone

The next recommended milestone is:

- `v5.9-run034-ten-transmitter-physical-prep`

That milestone should prepare firmware and SD-card copying instructions using the phase-plan offsets preserved here.
