# Three-transmitter analysis generalization

Milestone: v3.9-three-transmitter-analysis-generalization
Branch: exp054-three-transmitter-analysis-generalization
Status: Analysis tooling milestone

## 1. Purpose

This milestone generalizes the schedule-aware analysis path for the three-transmitter Run 030 result.

The immediate motivation is that Run 030 uses a list-valued manifest transmitter structure:

```
transmitters:
  - TXA/N01
  - TXB/N16
  - TXC/N31
```

That structure is appropriate for three-transmitter and later N-transmitter replay runs.

However, some earlier analysis tooling was shaped around two-transmitter TXA/TXB runs.

The purpose of this milestone is to add a narrow multi-transmitter manifest analysis path without disturbing the older two-transmitter tools.

## 2. Starting point

The branch started from:

```
main
v3.8-three-transmitter-sd-replay-synthesis
```

The working tree was clean before this milestone.

The current completed SD replay sequence is:

```
v3.4-three-transmitter-sd-replay-design
v3.5-three-transmitter-sd-schedule-prep
v3.6-three-transmitter-sd-physical-prep
v3.7-three-transmitter-sd-physical-replay
v3.8-three-transmitter-sd-replay-synthesis
```

## 3. Tool inspection findings

The inspection found three important analysis-layer facts.

First, the receiver parser is already broadly multi-transmitter-safe for Run 030:

```
scripts/parse_receiver_log.py
```

It groups summaries by:

```
tx_id
node_id
tx_id/node_id
```

This is why the parser accepted TXC/N31 cleanly during Run 030.

Second, the older direct analyzer remains two-transmitter-shaped:

```
scripts/analyze_scheduled_replay.py
```

It uses a pairwise interface:

```
--schedule-a
--schedule-b
--tx-a-label
--tx-b-label
```

It also reports ratio comparisons over a baseline.

That script remains useful for earlier TXA/TXB replay runs, but it is not the cleanest path for Run 030 and later N-transmitter runs.

Third, the earlier manifest wrapper is also two-transmitter-shaped:

```
scripts/analyze_scheduled_replay_from_manifest.py
```

It expects manifest keys such as:

```
transmitters.a.schedule_csv
transmitters.b.schedule_csv
transmitters.a.tx_id
transmitters.b.tx_id
```

Run 030 does not use that structure. Its schedule manifest uses a list-valued transmitter field.

Therefore, the correct v3.9 step is to add a new multi-transmitter manifest analyzer rather than forcing the older A/B wrapper to handle both schema families.

## 4. New analyzer

This milestone adds:

```
scripts/analyze_scheduled_replay_manifest_multi.py
```

The new analyzer reads:

```
--manifest
--parsed
--out-json
--out-csv
```

For Run 030, the command used was:

```
python scripts/analyze_scheduled_replay_manifest_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --out-csv outputs/run030_three_transmitter_manifest_replay_summary.csv
```

The analyzer reads the manifest's list-valued:

```
transmitters
```

field and processes each transmitter object.

For each transmitter it summarizes:

```
tx_id
node_id
role
policy
policy_code
threshold_family
schedule_csv
demand_rows
scheduled_send_rows
scheduled_skip_rows
send_fraction
scheduled send usefulness totals and means
received valid packets
observed sequence range
observed missing sequence count
delivered usefulness totals and means
delivered priority totals and means
mean receiver inter-arrival time
received packets per scheduled send row
received packets per scheduled demand row
```

It also computes observed receiver-side packet ratios for transmitter pairs and compares them to manifest-provided expected scheduled ratios when present.

## 5. Run 030 analyzer result

The new analyzer produced:

```
outputs/run030_three_transmitter_manifest_replay_summary.json
outputs/run030_three_transmitter_manifest_replay_summary.csv
```

The command output was:

```
TXA/N01: 393 received, 64/64 scheduled SEND
TXB/N16: 194 received, 32/64 scheduled SEND
TXC/N31: 98 received, 16/64 scheduled SEND
```

Expected-vs-observed ratios were:

```
TXB/TXA: observed=0.4936, expected=0.5000, diff=-0.0064
TXC/TXA: observed=0.2494, expected=0.2500, diff=-0.0006
TXC/TXB: observed=0.5052, expected=0.5000, diff=0.0052
```

This matches the Run 030 physical-replay and synthesis notes.

## 6. Output shape

The JSON output contains:

```
run_id
milestone
manifest
parsed_receiver_csv
per_transmitter
expected_scheduled_ratios
observed_received_packet_ratios
ratio_comparisons
interpretation_boundary
```

The CSV output contains one row per transmitter.

For Run 030, the CSV rows are:

```
TXA/N01
TXB/N16
TXC/N31
```

This output shape is intentionally simple. It is designed to support README summaries, development notes, and future manifest-bound replay comparisons.

## 7. Interpretation boundary

This analyzer preserves the same interpretation boundary as the physical replay notes.

It compares scheduled SEND proportions with observed receiver-side packet proportions.

It does not infer:

```
exact transmitted-packet counts
confirmed collision counts
synchronized latency
LoRaWAN behavior
airtime optimization
energy savings
live belief-controller behavior
operational wildfire behavior
```

Missing sequence numbers remain observed sequence gaps only.

Receiver inter-arrival summaries remain receiver-side observations only.

Usefulness and priority remain synthetic metadata.

## 8. Why a new script instead of patching the old wrapper

The older tools remain useful for the earlier two-transmitter milestones.

The new script avoids making the A/B wrapper overly complex.

This keeps the transition clear:

```
scripts/analyze_scheduled_replay.py
    legacy direct two-schedule analyzer

scripts/analyze_scheduled_replay_from_manifest.py
    legacy two-transmitter manifest wrapper

scripts/analyze_scheduled_replay_manifest_multi.py
    list-valued N-transmitter manifest analyzer
```

This is a low-risk addition because it does not disturb earlier analysis commands.

## 9. Result

The v3.9 milestone establishes a manifest-bound multi-transmitter analysis path for Run 030.

The parser had already accepted TXC/N31 cleanly.

The new analyzer now lets the schedule-aware analysis layer summarize Run 030 directly from:

```
traces/run030_reporting_reporting_schedule_manifest.json
logs/parsed_run_030_three_transmitter_sd_replay.csv
```

The resulting output reproduces the expected three-transmitter ratios and per-transmitter schedule summaries.

## 10. Recommended next step

After this milestone, the next good step is to add a short README addendum and commit:

```
scripts/analyze_scheduled_replay_manifest_multi.py
outputs/run030_three_transmitter_manifest_replay_summary.json
outputs/run030_three_transmitter_manifest_replay_summary.csv
docs/development/three_transmitter_analysis_generalization.md
```

A later milestone can decide whether to generalize bundle validation as well.

That should be separate from this analyzer milestone.
