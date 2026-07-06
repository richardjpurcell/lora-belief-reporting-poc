# Phase-aware replay method freeze

## Purpose

This note freezes the phase-aware physical replay method that emerged from Run 033.

Run 033 showed that scaling scheduled SD-backed replay from six to eight transmitters is not only a matter of adding devices. Startup phase can affect whether sparse scheduled transmitters remain visible in the receiver-side packet log.

This method freeze defines how future N-transmitter physical replay runs should represent, inspect, and document startup phases before being treated as canonical validation evidence.

## Background

Earlier milestones established the scheduled replay ladder:

| Run | Scale | Main result |
| --- | ---: | --- |
| Run 030 | 3 transmitters | Multi-transmitter manifest-bound replay became practical. |
| Run 031 | 4 transmitters | Startup-phase sensitivity became visible and was validated. |
| Run 032 | 6 transmitters | Clean six-transmitter SD-backed replay validated the next scale point. |
| Run 033 | 8 transmitters | Eight-transmitter replay succeeded after deterministic startup-phase deconfliction. |

Run 033 exposed a phase artifact. Initial full-group attempts showed TXH absent and TXD weak or absent. Diagnostic tests confirmed that the individual transmitter/card/receiver paths were viable. The successful candidate replay occurred after deterministic startup-phase deconfliction removed exact same-ms scheduled SEND coincidences among scheduled transmitters.

This method freeze turns that lesson into a reusable procedure.

## Definitions

### Slot interval

The slot interval is the fixed time step used by the transmitter firmware to advance through the replay schedule.

For the current physical replay ladder, the slot interval is treated as fixed.

The primary validation ladder should not use random slot-interval jitter unless a later milestone explicitly defines a robustness experiment.

### Startup offset

A startup offset is the transmitter-specific delay applied before a transmitter begins stepping through its SD-backed schedule.

Startup offsets are expressed in milliseconds.

Startup offsets are part of the physical replay method. They are not incidental bench details.

### Scheduled SEND row

A scheduled SEND row is a row in a transmitter schedule where the schedule says the transmitter should send rather than skip.

The scheduled SEND rows come from the manifest-bound schedule artifacts, not from the receiver log.

### Schedule-time SEND event

A schedule-time SEND event is the expected replay time of a scheduled SEND row:

event_time_ms = startup_offset_ms + slot_interval_ms * schedule_row_index

This is not a claim about exact RF transmit time. It is a deterministic schedule-time approximation used to inspect replay phase structure.

### Exact scheduled SEND coincidence

An exact scheduled SEND coincidence occurs when two or more scheduled transmitters have schedule-time SEND events at the same millisecond.

Exact scheduled SEND coincidences should be avoided in future canonical physical replay candidates.

### Near scheduled SEND coincidence

A near scheduled SEND coincidence occurs when two or more scheduled transmitters have schedule-time SEND events within a configured timing window.

Near coincidences do not automatically invalidate a run, but they should be reported.

For current bench diagnostics, useful reporting windows are:

| Window | Use |
| ---: | --- |
| 0 ms | exact same-ms scheduled SEND coincidences |
| 100 ms | close phase interactions |
| 150 ms | conservative near-coincidence reporting |
| 250 ms | coarse phase-grid reporting |

## Method rule

Future N-transmitter physical replay candidates should satisfy this rule before being treated as canonical validation evidence:

> The candidate phase plan should avoid exact same-ms scheduled SEND coincidences among structured scheduled transmitters while preserving the manifest schedules and fixed slot interval.

This rule does not require large separation between all transmitters. Run 033 showed that closeness alone is not necessarily the problem. The stronger problem was repeated exact coincidence between structured SEND schedules.

## Required phase-plan representation

Each physical replay candidate should record:

| Field | Meaning |
| --- | --- |
| run_id | Run identifier, such as R33 |
| tx_id | Transmitter identifier, such as TXA |
| node_id | Node identifier, such as N01 |
| schedule_csv | SD-backed schedule source |
| startup_offset_ms | Firmware startup offset |
| slot_interval_ms | Replay slot interval |
| scheduled_send_rows | Number of SEND rows in the schedule |
| scheduled_skip_rows | Number of SKIP rows in the schedule |

This information may appear in a physical-prep summary, a development note, or a dedicated phase-plan artifact.

## Required checks before replay

Before a physical replay is treated as canonical, the project should check:

1. All transmitter identities match the intended run.
2. All SD schedules match the intended run.
3. Startup offsets are recorded.
4. Schedule-time SEND events are computed from schedule rows and startup offsets.
5. Exact same-ms scheduled SEND coincidences are listed.
6. Near scheduled SEND coincidences are listed for the chosen reporting window.
7. Any deliberate phase compromises are documented.

The exact coincidence check is the most important gate for canonical validation.

## Recommended workflow

### Step 1: Prepare schedules

Generate or restore the manifest-bound schedules.

Validate schedule row counts and SEND/SKIP counts against the manifest.

### Step 2: Prepare firmware identities

Confirm each transmitter firmware has the intended:

- RUN_ID
- TX_ID
- NODE_ID
- STARTUP_OFFSET_MS

### Step 3: Compute phase overlaps

Before flashing or replaying, compute scheduled SEND event times from:

- transmitter schedule CSV
- startup offset
- fixed slot interval

Report:

- exact same-ms scheduled SEND coincidences
- near coincidences within the chosen reporting window

### Step 4: Adjust deterministic startup offsets

If exact scheduled SEND coincidences are present among structured scheduled transmitters, adjust deterministic startup offsets.

Prefer small deterministic offset changes over random jitter.

Preserve the same schedules and fixed slot interval unless the milestone explicitly studies jitter.

### Step 5: Recompute phase overlaps

After any offset change, recompute the overlap report.

The candidate should have no exact same-ms scheduled SEND coincidences among scheduled transmitters before proceeding to canonical replay.

### Step 6: Run physical replay

Capture the receiver log under the chosen phase plan.

Parse the receiver log and preserve rejects/malformed rows.

### Step 7: Analyze against manifest

Run manifest-bound analysis and validation.

A canonical replay candidate should preserve the expected receiver-side ratio structure within bounded physical replay interpretation limits.

### Step 8: Document interpretation boundaries

Every physical replay result should continue to avoid overclaiming.

## Canonical replay criteria

A phase-shifted replay can become canonical evidence for a milestone when:

- the phase plan is documented
- exact scheduled SEND coincidences have been checked
- the receiver log is preserved
- the parsed valid-packet log is preserved
- malformed/reject output is preserved
- manifest-bound summary outputs are preserved
- validation outputs are preserved
- all transmitters expected in the run are receiver-visible
- interpretation boundaries are stated

The canonical replay does not need to be perfect in every sequence position. Physical replay can still have missing receiver-side sequences. The main requirement is that the replay remains interpretable relative to the manifest-defined scheduled SEND ratios.

## Diagnostic replay naming

When a replay attempt is not canonical, name it explicitly.

Recommended suffixes:

| Suffix | Use |
| --- | --- |
| attempt1_txh_absent | transmitter absent from first attempt |
| attempt2_txh_absent_txd_weak | repeated absence or weakness |
| receiver_probe | single-transmitter receiver visibility test |
| subset_probe | reduced group diagnostic |
| phase_shifted_candidate | candidate replay after phase deconfliction |
| canonical | accepted primary evidence for milestone |

Diagnostic attempts should be preserved when they explain why the canonical method changed.

## Jitter policy

Random slot jitter should not be part of the primary validation ladder at this stage.

Deterministic startup offsets are preferred because they preserve:

- reproducibility
- fixed slot interval
- schedule identity
- manifest-bound analysis interpretability

Jitter may be useful later as a separate robustness experiment.

Possible later variants include:

- seeded deterministic startup jitter
- bounded seeded slot-interval jitter
- repeated phase-randomized robustness trials

Those should be separate milestones, not replacements for deterministic canonical replay.

## Interpretation boundaries

Phase-aware replay analysis does not establish:

- exact transmitted-packet counts
- confirmed RF collision mechanisms
- absence of collisions
- synchronized latency
- LoRaWAN behavior
- energy savings
- airtime optimization
- live-controller behavior
- arbitrary-layout scaling
- operational wildfire deployment behavior

It supports a bounded claim:

> Under a documented bench condition, manifest-bound scheduled replay can produce interpretable receiver-side packet proportions when startup phases are planned to avoid repeated exact scheduled SEND coincidences.

## Implication for next scale step

The next larger physical replay should not begin by simply adding transmitters.

Before a ten- or twelve-transmitter replay, the project should:

1. design the transmitter set
2. generate schedules
3. assign deterministic startup offsets
4. compute exact and near scheduled SEND coincidences
5. revise offsets until exact scheduled SEND coincidences are removed
6. preserve the phase plan before flashing
7. then run the physical replay

This makes phase-aware startup planning a standard part of the physical replay method.
