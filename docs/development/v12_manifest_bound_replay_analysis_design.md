# v1.2 Manifest-Bound Replay Analysis Design

## Purpose

The v1.1 schedule-aware analyzer combines reporting schedules with parsed receiver logs. It works well for Run 024, but it still requires the user to manually provide each input path.

The v1.2 milestone adds a manifest-bound analysis layer. The goal is to make scheduled replay analysis easier to reproduce by collecting run metadata and input paths in a small manifest file.

This should not change the receiver parser or the v1.1 schedule-aware analyzer’s core interpretation. Instead, v1.2 adds a reproducibility wrapper around the existing analysis path.

## Design principle

The parser remains packet-centric.

The v1.1 analyzer remains schedule-aware.

The v1.2 layer becomes manifest-bound.

This keeps responsibilities separated:

* `scripts/parse_receiver_log.py` parses receiver logs.
* `scripts/analyze_scheduled_replay.py` combines schedules with parsed receiver rows.
* a new manifest-driven path supplies the input paths and run metadata consistently.

## Motivation

Run 024 now has several linked artifacts:

* schedule CSV for TXA;
* schedule CSV for TXB;
* firmware schedule headers generated from those schedules;
* receiver log;
* parsed receiver log;
* reject log;
* schedule-aware JSON and CSV reports;
* development notes;
* README checkpoint.

The evidence is reproducible, but the relationships among these files are currently documented in prose and command examples.

A manifest-bound replay analysis should make those relationships explicit.

## Proposed manifest

Add a manifest such as:

* `reports/run024_schedule_aware_manifest.json`

The manifest should record:

* run ID;
* milestone;
* description;
* transmitter labels;
* node labels if known;
* schedule paths;
* parsed receiver log path;
* reject log path;
* output JSON path;
* output CSV path;
* caution notes.

The manifest should also preserve the key interpretation boundary:

> The schedule CSVs define one repeated schedule period. The analyzer compares schedule proportions and observed packet proportions. It does not infer exact transmitted packet counts, confirmed collisions, true latency, or airtime optimization.

## Proposed command

The v1.2 path should allow:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run024_schedule_aware_manifest.json
```

This wrapper should read the manifest and call the existing schedule-aware analysis logic.

## Implementation options

There are two reasonable implementation approaches.

### Option A: wrapper script

Add a small wrapper:

* `scripts/analyze_scheduled_replay_from_manifest.py`

This wrapper reads the manifest, constructs the same inputs used by `scripts/analyze_scheduled_replay.py`, and runs the analysis.

This is the preferred v1.2 approach because it avoids destabilizing the v1.1 analyzer.

### Option B: add manifest support to the existing analyzer

Extend `scripts/analyze_scheduled_replay.py` with a `--manifest` argument.

This is slightly simpler for users but risks making the analyzer more complicated.

For v1.2, use Option A unless there is a strong reason not to.

## Expected files

Add:

* `docs/development/v12_manifest_bound_replay_analysis_design.md`
* `reports/run024_schedule_aware_manifest.json`
* `scripts/analyze_scheduled_replay_from_manifest.py`
* `docs/development/run024_manifest_bound_replay_analysis.md`

Update:

* `README.md`

## Expected workflow

1. Create the v1.2 branch.
2. Add this design note.
3. Add a Run 024 manifest.
4. Add the wrapper script.
5. Test manifest-bound analysis on Run 024.
6. Confirm that generated outputs match the v1.1 outputs.
7. Document the manifest-bound Run 024 reproduction.
8. Update the README with a short v1.2 checkpoint.
9. Merge and tag as `v1.2-manifest-bound-replay-analysis`.

## Expected Run 024 result

The manifest-bound analysis should reproduce the v1.1 headline:

```
TXA: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
TXB: 8/16 schedule rows SEND; 176 received packets; mean delivered usefulness 0.786
Observed received-packet ratio 0.4875; scheduled send-fraction ratio 0.5000.
```

The key validation criterion is not a new scientific result. It is reproducibility of the existing schedule-aware result from a manifest-bound command.

## Interpretation

The careful interpretation remains:

> Run 024 shows that the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, consistent with scheduled skipping, while TXB retained higher mean delivered usefulness per received packet.

This still does not infer:

* exact transmitted-packet counts;
* confirmed collisions;
* true latency;
* airtime optimization;
* live belief-controller behavior.

## Milestone contribution

v1.2 improves experiment reproducibility.

v1.0 demonstrated skipped-slot physical replay.

v1.1 added schedule-aware analysis.

v1.2 binds that analysis to an explicit manifest so the relationship among schedules, receiver logs, parsed logs, reports, and interpretation cautions is machine-readable and easier to reproduce.
