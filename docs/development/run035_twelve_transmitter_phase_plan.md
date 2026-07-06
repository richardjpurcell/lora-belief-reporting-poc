# Run 035 twelve-transmitter phase plan

## Purpose

Run 035 phase planning assigns deterministic startup offsets for the twelve-transmitter scheduled replay prepared in `v5.13-run035-twelve-transmitter-schedule-prep`.

This is an analysis/design milestone only. It does not modify firmware, copy schedules to SD cards, flash transmitters, collect receiver logs, run hardware, or make physical replay claims.

The purpose is to preserve a deterministic phase-aware startup plan before physical preparation.

## Inputs

The phase-plan script reads the Run 035 manifest:

- `traces/run035_reporting_reporting_schedule_manifest.json`

It uses the generated Run 035 schedules from:

- `v5.13-run035-twelve-transmitter-schedule-prep`

The phase-plan script is:

- `scripts/prepare_run035_twelve_tx_phase_plan.py`

## Outputs

The milestone writes:

- `outputs/run035_twelve_tx_phase_plan.csv`
- `outputs/run035_twelve_tx_phase_plan_summary.json`
- `outputs/run035_twelve_tx_phase_plan_exact_coincidences.csv`
- `outputs/run035_twelve_tx_phase_plan_near_coincidences.csv`
- `outputs/run035_twelve_tx_phase_plan_pairwise_min_deltas.csv`

It also updates:

- `traces/run035_reporting_reporting_schedule_manifest.json`

The manifest now records assigned startup offsets for each transmitter.

## Phase-plan parameters

| Parameter | Value |
| --- | ---: |
| Slot interval | 10000 ms |
| Near-coincidence window | 150 ms |
| Transmitter count | 12 |
| Total scheduled SEND events | 240 |
| Offset search step | 50 ms |
| Offset search range | 0-14950 ms |

## Offset-selection method

The Run 035 phase-plan script carries forward the successful Run 034 A-J startup offsets.

It then deterministically searches for TXK and TXL offsets.

The selection rule is:

1. reject candidate offsets that create exact same-ms scheduled SEND coincidences;
2. reject candidate offsets that create near scheduled SEND coincidences within 150 ms;
3. prefer offsets after the existing maximum offset when possible;
4. maximize minimum schedule-time separation from the prior selected plan;
5. use the smallest remaining offset as the final deterministic tie-breaker.

TXK was selected first.

TXL was selected second, after TXK was already part of the selected plan.

Because the bounded search range ended at 14950 ms, TXK was appended after the Run 034 A-J maximum offset, while TXL was placed at a non-coincident offset within the same bounded range.

## Assigned startup offsets

| TX | Node | Startup offset ms | Scheduled SEND rows | Offset source |
| --- | --- | ---: | ---: | --- |
| TXA | N01 | 1000 | 64 | carried forward from Run 034 |
| TXB | N16 | 3250 | 32 | carried forward from Run 034 |
| TXC | N31 | 4750 | 16 | carried forward from Run 034 |
| TXD | N46 | 800 | 8 | carried forward from Run 034 |
| TXE | N61 | 7750 | 32 | carried forward from Run 034 |
| TXF | N76 | 2500 | 16 | carried forward from Run 034 |
| TXG | N91 | 9450 | 8 | carried forward from Run 034 |
| TXH | N106 | 100 | 4 | carried forward from Run 034 |
| TXI | N121 | 5850 | 16 | carried forward from Run 034 |
| TXJ | N136 | 10650 | 8 | carried forward from Run 034 |
| TXK | N151 | 14950 | 32 | selected by Run 035 deterministic offset search |
| TXL | N166 | 12950 | 4 | selected by Run 035 deterministic offset search |

## TXK and TXL selection trace

| TX | Node | Selected offset ms | Min delta against prior plan | Valid candidates |
| --- | --- | ---: | ---: | ---: |
| TXK | N151 | 14950 | 3950 ms | 227 |
| TXL | N166 | 12950 | 1950 ms | 223 |

This selection trace is a schedule-time planning diagnostic.

It does not prove collision absence or physical-layer behavior.

## Coincidence-check result

| Check | Result |
| --- | ---: |
| Exact same-ms scheduled SEND coincidences | 0 |
| Near scheduled SEND coincidences within 150 ms | 0 |
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
| TXE/N61 | TXI/N121 | 1900 | 4 | 4 |
| TXA/N01 | TXL/N166 | 1950 | 7 | 6 |
| TXK/N151 | TXL/N166 | 2000 | 6 | 6 |

These values are schedule-time separations. They are not measured RF timings.

## Manifest update

The Run 035 manifest now records:

- assigned `startup_offset_ms` values;
- `startup_offset_status` values indicating assignment by `v5.14-run035-twelve-transmitter-phase-plan`;
- a `phase_plan` object summarizing the check;
- links to the phase-plan output files.

This makes the later physical-preparation milestone manifest-bound and phase-aware.

## Future physical-prep handoff

The next milestone may use the assigned startup offsets to prepare firmware and SD-card workflow.

However, this phase-plan milestone does not perform that work.

Physical preparation still needs to handle:

- TXK and TXL firmware sketches using the underscore naming convention;
- adjusted internal TX labels and node IDs;
- two additional SD cards;
- appropriate SD-card volume labels replacing the default `NO NAME`;
- one-card-at-a-time SD schedule copying;
- bench layout and startup procedure.

## Interpretation boundaries

This milestone does not establish:

- twelve-transmitter physical replay success;
- exact transmitted-packet counts;
- confirmed RF collision mechanisms;
- absence of collisions;
- synchronized latency;
- LoRaWAN behavior;
- energy savings;
- airtime optimization;
- live-controller behavior;
- arbitrary-layout twelve-node behavior;
- operational wildfire deployment behavior.

This milestone supports:

- deterministic startup offset assignment;
- exact same-ms scheduled SEND coincidence checking;
- near scheduled SEND coincidence checking;
- manifest-bound handoff to physical preparation.

## Next milestone

The next recommended milestone is:

- `v5.15-run035-twelve-transmitter-physical-prep`

That milestone should prepare firmware identities, TXK/TXL sketches, SD-card workflow, card labels, and bench plan using the phase-plan offsets preserved here.
