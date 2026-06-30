# Legacy and Multi-Transmitter Tool Status

## Purpose

This note records the current status of the scheduled replay analysis and validation tools after the repository transition from two-transmitter manifests to list-valued N-transmitter manifests.

This is a documentation/status milestone. It does not change firmware, schedules, logs, parser behavior, analysis semantics, validation semantics, or physical replay results.

## Current milestone

This note belongs to:

* `v3.12-legacy-tool-status-cleanup`

It follows:

* `v3.9-three-transmitter-analysis-generalization`
* `v3.10-multi-transmitter-bundle-validation`
* `v3.11-multi-transmitter-repro-cleanup`

## Why this note exists

The repository now contains two generations of scheduled replay tooling.

The earlier generation supports two-transmitter replay artifacts, especially runs where the manifest uses keyed transmitter entries such as:

* `transmitters.a`
* `transmitters.b`

The newer generation supports list-valued N-transmitter manifests, such as Run 030, where transmitters are represented as a list:

* TXA/N01
* TXB/N16
* TXC/N31

Both tool generations remain useful, but they should be understood as serving different artifact shapes.

## Preferred tools for list-valued N-transmitter manifests

For Run 030 and later list-valued transmitter manifests, prefer:

* `scripts/analyze_scheduled_replay_manifest_multi.py`
* `scripts/validate_manifest_replay_bundle_multi.py`

These tools are the current preferred path for N-transmitter SD-backed replay analysis and validation.

### Multi-transmitter analyzer

Use:

* `scripts/analyze_scheduled_replay_manifest_multi.py`

Purpose:

This script reads a manifest with a list-valued `transmitters` field, combines each transmitter schedule with the parsed receiver CSV, and writes N-transmitter summary outputs.

Canonical Run 030 command:

```
python scripts/analyze_scheduled_replay_manifest_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --out-csv outputs/run030_three_transmitter_manifest_replay_summary.csv
```

The analyzer is intended for Run 030 and later N-transmitter SD replay runs.

It compares scheduled SEND proportions with observed receiver-side packet proportions.

It does not infer exact transmitted-packet counts, confirmed collisions, synchronized latency, LoRaWAN behavior, airtime optimization, energy savings, or live-controller behavior.

### Multi-transmitter validator

Use:

* `scripts/validate_manifest_replay_bundle_multi.py`

Purpose:

This script validates that a list-valued N-transmitter manifest replay bundle is structurally coherent. It checks that the manifest, schedule CSVs, parsed receiver CSV, summary JSON, and summary CSV agree on the expected replay structure and scheduled headline values.

Canonical Run 030 command:

```
python scripts/validate_manifest_replay_bundle_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --summary-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --summary-csv outputs/run030_three_transmitter_manifest_replay_summary.csv \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_validation.json
```

Confirmed Run 030 validation result:

```
Validation summary: 101/101 checks passed; 0 failed.
```

The validator does not infer exact transmitted-packet counts, confirmed collisions, synchronized latency, LoRaWAN behavior, airtime optimization, energy savings, live-controller behavior, or operational wildfire behavior.

## Legacy two-transmitter tools

The following tools remain available for earlier two-transmitter artifacts:

* `scripts/analyze_scheduled_replay.py`
* `scripts/analyze_scheduled_replay_from_manifest.py`
* `scripts/validate_run_bundle.py`

These tools should not be deleted at this stage because they document and support earlier milestones in the repository.

They are best understood as legacy two-transmitter tools, not as the preferred path for Run 030-style list-valued manifests.

### Direct two-schedule analyzer

Tool:

* `scripts/analyze_scheduled_replay.py`

Purpose:

This script combines two reporting schedules with a parsed receiver log. It is schedule-aware but shaped around two transmitter labels.

It remains useful for earlier two-transmitter scheduled replay runs.

It is not the preferred tool for list-valued N-transmitter manifests.

### Two-transmitter manifest wrapper

Tool:

* `scripts/analyze_scheduled_replay_from_manifest.py`

Purpose:

This script reads an earlier manifest structure and invokes `scripts/analyze_scheduled_replay.py`.

It expects two keyed transmitters:

* `transmitters.a`
* `transmitters.b`

It remains useful for earlier manifest-bound two-transmitter analysis artifacts.

It is not the preferred tool for list-valued N-transmitter manifests.

### Two-transmitter bundle validator

Tool:

* `scripts/validate_run_bundle.py`

Purpose:

This script validates earlier manifest-bound scheduled replay bundles.

It expects required keys such as:

* `transmitters.a.tx_id`
* `transmitters.a.schedule_csv`
* `transmitters.b.tx_id`
* `transmitters.b.schedule_csv`

It remains useful for earlier two-transmitter validation artifacts.

It is not the preferred validator for list-valued N-transmitter manifests.

## Current tool-status summary

| Tool                                                 | Status                                    | Preferred use                                                                       |
| ---------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| `scripts/analyze_scheduled_replay.py`                | Legacy                                    | Direct two-schedule analysis for earlier two-transmitter runs                       |
| `scripts/analyze_scheduled_replay_from_manifest.py`  | Legacy                                    | Manifest-bound two-transmitter analysis using `transmitters.a` and `transmitters.b` |
| `scripts/validate_run_bundle.py`                     | Legacy                                    | Bundle validation for earlier two-transmitter manifest structures                   |
| `scripts/analyze_scheduled_replay_manifest_multi.py` | Current preferred N-transmitter analyzer  | List-valued transmitter manifests such as Run 030                                   |
| `scripts/validate_manifest_replay_bundle_multi.py`   | Current preferred N-transmitter validator | List-valued transmitter manifest replay bundles such as Run 030                     |

## Interpretation boundaries

This tool-status cleanup does not change any physical replay result.

It does not add evidence for exact transmitted-packet counts.

It does not confirm collisions.

It does not establish synchronized latency.

It does not evaluate LoRaWAN behavior.

It does not establish airtime optimization.

It does not establish energy savings.

It does not establish live-controller behavior.

It does not establish scaling behavior beyond the completed three-transmitter lab replay.

It does not evaluate operational wildfire behavior.

## Recommendation going forward

For earlier two-transmitter milestones, keep using the legacy tools when reproducing those exact artifacts.

For Run 030 and later list-valued manifests, use the N-transmitter tools:

* `scripts/analyze_scheduled_replay_manifest_multi.py`
* `scripts/validate_manifest_replay_bundle_multi.py`

Future scale-up work should build from the list-valued manifest path rather than expanding the old `transmitters.a` / `transmitters.b` tooling.
