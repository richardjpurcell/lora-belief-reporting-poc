### v1.2 manifest-bound replay analysis

The v1.2 layer adds manifest-bound reproduction for skipped-slot replay analysis.

The parser remains packet-centric. The schedule-aware analyzer remains responsible for combining reporting schedules with parsed receiver rows. The new manifest-bound wrapper reads a run manifest and invokes the existing analyzer with the correct paths and labels.

For Run 024, the manifest is:

* `reports/run024_schedule_aware_manifest.json`

The analysis can be reproduced with:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run024_schedule_aware_manifest.json
```

A dry run shows the resolved analyzer command without executing it:

```
python scripts/analyze_scheduled_replay_from_manifest.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --dry-run
```

The manifest-bound command reproduces the v1.1 schedule-aware headline:

```
TXA/N01: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
TXB/N16: 8/16 schedule rows SEND; 176 received packets; mean delivered usefulness 0.786
Observed received-packet ratio 0.4875; scheduled send-fraction ratio 0.5000.
```

This is a reproducibility improvement rather than a new physical experiment. It makes the relationship among schedules, firmware headers, receiver logs, parsed logs, reports, and interpretation cautions explicit in a machine-readable manifest.

The careful interpretation remains unchanged: the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, consistent with scheduled skipping, while TXB retained higher mean delivered usefulness per received packet. The analysis does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, or airtime optimization.
