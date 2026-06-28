# Run 024 schedule-aware analysis

## Purpose

Run 024 was the first skipped-slot physical replay run. It demonstrated that a reporting schedule can affect physical transmission behavior: scheduled `SEND` rows are transmitted, while scheduled `SKIP` rows remain silent.

The original parser remains packet-centric. It analyzes valid packets observed by the receiver and writes malformed rows to a rejects file.

This note adds the schedule-aware interpretation layer for Run 024 by comparing:

1. the reporting schedules used by the transmitter firmware; and
2. the parsed receiver log from the physical replay.

## Inputs

Schedules:

* `traces/run022_reporting_txa_fixed_all_schedule.csv`
* `traces/run022_reporting_txb_usefulness_threshold_schedule.csv`

Parsed receiver log:

* `logs/parsed_run_024_skipped_slot_replay.csv`

Analyzer:

* `scripts/analyze_scheduled_replay.py`

Generated outputs:

* `reports/run024_schedule_aware_summary.json`
* `reports/run024_schedule_aware_summary.csv`

## Reproduction command

```
python scripts/analyze_scheduled_replay.py \
  --schedule-a traces/run022_reporting_txa_fixed_all_schedule.csv \
  --schedule-b traces/run022_reporting_txb_usefulness_threshold_schedule.csv \
  --parsed logs/parsed_run_024_skipped_slot_replay.csv \
  --out-json reports/run024_schedule_aware_summary.json \
  --out-csv reports/run024_schedule_aware_summary.csv
```

## Analyzer output

```
Wrote JSON summary: reports/run024_schedule_aware_summary.json
Wrote CSV summary:  reports/run024_schedule_aware_summary.csv
TXA: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
TXB: 8/16 schedule rows SEND; 176 received packets; mean delivered usefulness 0.786
Observed received-packet ratio 0.4875; scheduled send-fraction ratio 0.5000.
Interpretation: received packet ratio is consistent with scheduled skipping, not proof of exact transmitted-packet or collision counts.
```

## Summary

Run 024 combines a fixed-send transmitter schedule with a usefulness-threshold transmitter schedule.

| Transmitter | Schedule rows | SEND rows | SKIP rows | Send fraction | Received valid packets | Mean delivered usefulness |
| ----------- | ------------: | --------: | --------: | ------------: | ---------------------: | ------------------------: |
| TXA         |            16 |        16 |         0 |         1.000 |                    361 |                     0.540 |
| TXB         |            16 |         8 |         8 |         0.500 |                    176 |                     0.786 |

The usefulness-threshold stream scheduled `SEND` on half of its schedule rows while retaining higher mean usefulness per received packet.

The observed TXB/TXA received-packet ratio was:

```
176 / 361 = 0.4875
```

The scheduled TXB/TXA send-fraction ratio was:

```
0.5 / 1.0 = 0.5000
```

This supports the interpretation that the observed packet-count ratio is consistent with the scheduled skipped-slot behavior.

## Interpretation

Run 024 supports the following careful claim:

> TXB used approximately half the scheduled transmission opportunities while retaining higher usefulness per received packet. The observed TXB/TXA received-packet ratio was close to the scheduled send-fraction ratio, which is consistent with scheduled skipping.

This is stronger than earlier metadata-only reporting-policy experiments because the reporting policy now changes physical transmitter behavior.

## Cautions

This result should not be overinterpreted.

* This is point-to-point LoRa at 915 MHz, not LoRaWAN.
* The schedule CSVs define one schedule period; the firmware loops over that schedule repeatedly.
* The schedule-aware analyzer compares schedule proportions and observed packet proportions.
* It does not infer exact transmitted packet counts.
* Missing sequence numbers are observed sequence gaps, not confirmed collisions.
* `recv_ms` and `tx_ms` are not synchronized across boards and should not be interpreted as true latency.
* Usefulness and priority are synthetic metadata in this milestone.
* The run does not yet use a live belief-maintenance controller.
* The appropriate wording is “reduced physical transmission attempts under scheduled skipping,” not “airtime optimization.”

## Milestone contribution

Run 024 plus the v1.1 schedule-aware analyzer closes the analysis gap introduced by skipped-slot replay.

The parser remains packet-centric.

The analyzer is schedule-aware.

Together, they support a delivery-versus-usefulness analysis path that includes both intended reporting demand and observed receiver delivery.
