# Run 030 Multi-Transmitter Reproduction Commands

## Purpose

This note records the canonical reproduction commands for the Run 030 N-transmitter manifest replay workflow.

The purpose of this milestone is reproducibility cleanup. It does not introduce a new physical run, firmware change, schedule change, parser change, or analysis interpretation change.

The workflow reproduced here is:

1. Run the list-valued multi-transmitter manifest analyzer.
2. Regenerate the Run 030 summary JSON and CSV.
3. Run the list-valued multi-transmitter bundle validator.
4. Regenerate the Run 030 validation JSON.
5. Confirm that the validation bundle remains coherent.

## Current milestone

This note belongs to:

* `v3.11-multi-transmitter-repro-cleanup`

It follows:

* `v3.9-three-transmitter-analysis-generalization`
* `v3.10-multi-transmitter-bundle-validation`

## Input artifacts

Run 030 uses the list-valued manifest:

* `traces/run030_reporting_reporting_schedule_manifest.json`

The parsed valid receiver packet CSV is:

* `logs/parsed_run_030_three_transmitter_sd_replay.csv`

The manifest refers to three transmitter schedules:

* `traces/run030_reporting_txa_fixed_all_schedule.csv`
* `traces/run030_reporting_txb_medium_threshold_schedule.csv`
* `traces/run030_reporting_txc_strict_threshold_schedule.csv`

The three transmitters are:

* TXA/N01
* TXB/N16
* TXC/N31

## Step 1: regenerate the Run 030 N-transmitter analysis summary

Run:

```
python scripts/analyze_scheduled_replay_manifest_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --out-csv outputs/run030_three_transmitter_manifest_replay_summary.csv
```

Expected console summary:

```
Wrote JSON summary: outputs/run030_three_transmitter_manifest_replay_summary.json
Wrote CSV summary:  outputs/run030_three_transmitter_manifest_replay_summary.csv

Per-transmitter received packet counts:
  TXA/N01: 393 received, 64/64 scheduled SEND
  TXB/N16: 194 received, 32/64 scheduled SEND
  TXC/N31: 98 received, 16/64 scheduled SEND

Expected-vs-observed ratios:
  TXB/TXA: observed=0.4936, expected=0.5000, diff=-0.0064
  TXC/TXA: observed=0.2494, expected=0.2500, diff=-0.0006
  TXC/TXB: observed=0.5052, expected=0.5000, diff=0.0052
```

## Step 2: regenerate the Run 030 validation report

Run:

```
python scripts/validate_manifest_replay_bundle_multi.py \
  --manifest traces/run030_reporting_reporting_schedule_manifest.json \
  --summary-json outputs/run030_three_transmitter_manifest_replay_summary.json \
  --summary-csv outputs/run030_three_transmitter_manifest_replay_summary.csv \
  --parsed logs/parsed_run_030_three_transmitter_sd_replay.csv \
  --out-json outputs/run030_three_transmitter_manifest_replay_validation.json
```

Expected final validation result:

```
Validation summary: 101/101 checks passed; 0 failed.
Wrote validation JSON: outputs/run030_three_transmitter_manifest_replay_validation.json
```

## Step 3: confirm the reproduction is clean

Run:

```
git status
```

Expected result:

```
nothing to commit, working tree clean
```

Optionally check the regenerated tracked outputs:

```
git diff -- outputs/run030_three_transmitter_manifest_replay_summary.json \
  outputs/run030_three_transmitter_manifest_replay_summary.csv \
  outputs/run030_three_transmitter_manifest_replay_validation.json
```

Expected result:

* no diff

## Tool status after v3.11

The repository now has both legacy two-transmitter tools and newer N-transmitter tools.

Legacy tools:

* `scripts/analyze_scheduled_replay.py`
* `scripts/analyze_scheduled_replay_from_manifest.py`
* `scripts/validate_run_bundle.py`

These remain available for earlier two-transmitter workflow artifacts.

The newer N-transmitter tools are:

* `scripts/analyze_scheduled_replay_manifest_multi.py`
* `scripts/validate_manifest_replay_bundle_multi.py`

For list-valued manifests such as Run 030, prefer the newer N-transmitter tools.

## What this reproduction confirms

This reproduction confirms that the Run 030 list-valued manifest, transmitter schedule CSVs, parsed receiver CSV, summary JSON, summary CSV, and validation JSON remain mutually consistent.

It confirms that the analyzer can regenerate the same Run 030 summary artifacts.

It confirms that the validator can re-check the regenerated bundle and produce a passing validation report.

The confirmed validation result is:

```
101/101 checks passed; 0 failed.
```

## Bounded interpretation

This reproduction supports a narrow artifact-level conclusion:

The Run 030 SD-backed, manifest-bound, three-transmitter replay workflow is reproducible from the committed manifest, schedule CSVs, parsed receiver CSV, analyzer, and validator.

This does not infer exact transmitted-packet counts.

This does not confirm collisions.

This does not turn observed sequence gaps into collision evidence.

This does not treat `recv_ms` and `tx_ms` as synchronized board clocks.

This does not measure true latency.

This does not evaluate LoRaWAN behavior.

This does not establish airtime optimization.

This does not establish energy savings.

This does not establish scaling behavior beyond this three-transmitter lab replay.

This does not use a live belief-maintenance controller.

This does not evaluate operational wildfire behavior.

## Relationship to the longer-term project

This cleanup milestone makes the multi-transmitter path easier to repeat before scaling.

The intended progression remains:

1. Stabilize schedule generation.
2. Stabilize SD-card replay.
3. Stabilize physical replay parsing.
4. Stabilize manifest-bound multi-transmitter analysis.
5. Stabilize validation and reproducibility bundles.
6. Then cautiously scale transmitter count and/or move closer to AWSRT-derived belief-demand traces.

The next hardware step should remain separate from this milestone. The next trace-semantics step should also remain separate from this milestone.
