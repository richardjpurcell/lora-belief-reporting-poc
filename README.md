# LoRa Belief-Reporting Proof of Concept

This repository contains a small-scale ESP32/LilyGO LoRa proof of concept for studying delivery-versus-usefulness reporting under constrained LoRa airtime.

The project uses point-to-point LoRa at 915 MHz with LilyGO LoRa32 boards. Synthetic sensing packets carry both communication metadata and epistemic/usefulness metadata. A physical LoRa receiver supplies real delivery outcomes, including received packet counts, RSSI, SNR, receiver inter-arrival timing, and sequence-gap behaviour.

The central research motivation is that information delivery is not the same as information usefulness. In this proof of concept, delivered packets can be analyzed both as communication events and as carriers of synthetic belief-maintenance/usefulness metadata.

This is not a LoRaWAN system and not yet an operational adaptive reporting policy. The current repository is a laboratory proof of concept for logging, parsing, and analyzing physical delivery outcomes together with synthetic usefulness metadata.

## Repository structure

docs/development/   Development notes and run documentation
firmware/           Arduino sketches for RX and TX boards
logs/               Raw and parsed receiver logs
scripts/            Python logging and parsing scripts
figures/            Figures for notes or papers
notes/              Scratch notes and early pitch material

## Current status

Completed milestones include:

* heartbeat tests on three LilyGO LoRa32 boards;
* first point-to-point LoRa link;
* two-transmitter reception;
* CRC-enabled packet transmission;
* transmitter ID and logical node ID in the packet schema;
* receiver logging to CSV;
* parser support for valid and malformed packets;
* reporting-rate ladder Runs 005-010.


v0.2 dynamic usefulness checkpoint:

Branch `exp011-dynamic-usefulness` extends the initial reporting-rate ladder by
moving from fixed usefulness metadata to time-varying usefulness metadata
generated directly in transmitter firmware.

Runs 011 and 012 preserve the same packet schema as the v0.1 runs, but TXB/N16
now emits demand-like usefulness phases while TXA/N01 remains a lower-value
baseline stream. The parser now supports `--seq-window`, allowing usefulness and
priority to be summarized by sequence window.

Run 012 is the cleanest v0.2 result. It used freshly reset transmitters at a
1000 ms reporting interval. TXA/N01 delivered 245 packets and TXB/N16 delivered
247 packets. Despite nearly equal delivery counts, TXA/N01 delivered total
usefulness 67.35 while TXB/N16 delivered total usefulness 121.90. The
sequence-window summary recovered the intended TXB/N16 low/high/low/high
usefulness pattern.

This supports the proof-of-concept claim that packet delivery count and
delivered usefulness are not equivalent, and that a physical LoRa testbed can
carry synthetic epistemic metadata whose usefulness varies over time.

v0.3 trace-driven metadata replay checkpoint:

Branch `exp017-trace-driven-metadata-replay` moved the transmitters from
firmware-generated phase logic to compiled-in trace-header replay. TX-A and
TX-B used separate trace files converted into Arduino headers with
`scripts/make_trace_headers.py`.

Run 017 is the cleanest v0.3 result. TXA/N01 delivered 316 packets with 0
observed sequence gaps and total usefulness 88.48. TXB/N16 delivered 315
packets with 0 observed sequence gaps and total usefulness 145.25. TX-B used a
500 ms startup offset to avoid simultaneous periodic transmissions when both
transmitters were powered at the same time.

This run confirmed that trace-driven LoRa metadata replay can preserve temporal
usefulness structure under physical packet delivery.

v0.4 synthetic belief-demand trace generator checkpoint:

Branch `exp018-synthetic-belief-demand-traces` introduced a reusable synthetic
belief-demand trace generator. Run 018 moved the trace source from manually
assembled phase traces to generated traces while preserving the existing
compiled-in firmware replay workflow.

Run 018 produced 616 valid packets and 3 malformed packets. TXA/N01 delivered
306 packets with total usefulness 85.68 and mean usefulness 0.280. TXB/N16
delivered 310 packets with total usefulness 141.00 and mean usefulness 0.455.
The TXB/N16 sequence-window summary recovered the generator-defined usefulness
phases.

This run confirmed that reusable synthetic trace generation can feed the
physical LoRa replay workflow while continuing to separate delivery count from
delivered usefulness.

v0.5 policy-controlled synthetic trace checkpoint:

Branch `exp019-policy-controlled-traces` adds policy-controlled synthetic
traces. Run 019 generates two reporting streams from the same synthetic
belief-demand substrate:

* TXA/N01 uses a fixed-all policy, encoded as policy `F`;
* TXB/N16 uses a usefulness-threshold policy, encoded as policy `U`.

The firmware still transmits once per second, so Run 019 is not yet an
airtime-saving experiment. The policy layer controls trace content and
usefulness metadata, not physical transmission timing.

Run 019 produced 979 valid packets and 3 malformed packets. TXA/N01 delivered
490 packets with total usefulness 235.7 and mean usefulness 0.481. TXB/N16
delivered 489 packets with total usefulness 425.6 and mean usefulness 0.870.
Observed sequence gaps were light: TXA/N01 had one missing sequence value
`[209]`, and TXB/N16 had one missing sequence value `[186]`.

This is the first successful policy-controlled synthetic trace replay. It
strengthens the core proof-of-concept result: two LoRa streams can have nearly
identical physical delivery counts while carrying substantially different
delivered usefulness because their metadata traces are generated by different
reporting policies.

The current receiver-row schema is:

RX,recv_ms,run_id,tx_id,node_id,seq,tx_ms,region,event,priority,usefulness,stale_after,policy,rssi,snr

v0.6 generic demand-trace adapter checkpoint:

Branch `exp021-v06-trace-adapter-design` adds a generic belief-maintenance
demand-trace adapter. The adapter introduces an explicit intermediate layer
between source-side demand records and the compact firmware trace CSVs already
used by the ESP32/LilyGO LoRa proof-of-concept.

The v0.6 adapter path is:

```text
source / belief-maintenance demand record
→ generic demand-trace schema
→ compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

Run 020 is an adapter reproduction check, not a physical radio run. It uses a
small generic adapter input file:

```text
traces/run020_adapter_example_input.csv
```

with schema:

```text
source_id,source_time,demand_index,region_id,event_type,priority,usefulness,stale_after,policy_hint,source_policy,source_note
```

The adapter converts this generic input into compact firmware trace CSVs using
the existing compact schema:

```text
seq,region,event,priority,usefulness,stale_after,policy
```

The Run 020 adapter example produces two compact traces:

* TXA uses a fixed-all policy, encoded as policy `F`, with 16 compact rows;
* TXB uses a usefulness-threshold policy, encoded as policy `U`, with 8 compact rows at threshold `0.50`.

The generated files are:

```text
traces/run020_adapter_txa_fixed_all.csv
traces/run020_adapter_txb_usefulness_threshold.csv
traces/run020_adapter_manifest.json
```

Both compact traces validate through the existing header-generation path:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txa_fixed_all.csv \
  --outfile /tmp/trace_data_TXA_adapter_test.h

python scripts/make_trace_headers.py \
  --infile traces/run020_adapter_txb_usefulness_threshold.csv \
  --outfile /tmp/trace_data_TXB_adapter_test.h
```

This confirms that the generic adapter layer can produce Arduino-compatible
trace-header inputs without changing firmware.

The v0.6 checkpoint does not change transmitter firmware, receiver firmware,
packet schema, SD-card replay, LoRa timing, or physical transmission behaviour.
It is not an airtime-saving experiment and does not make any claim about
collisions or physical delivery performance.

The main purpose of v0.6 is to prepare the repository for future
AWSRT-inspired or AWSRT-derived demand traces without making AWSRT a dependency
of the LoRa proof-of-concept. The adapter keeps source-side demand semantics
separate from compact firmware trace rows, making the source-to-packet-metadata
transformation more explicit and auditable.

v0.7 adapter-generated physical replay checkpoint:

Branch `exp022-v07-adapter-physical-replay` performs the first physical LoRa
replay of adapter-generated compact traces. The traces were produced by the
v0.6 generic demand-trace adapter and then compiled into the existing
ESP32/LilyGO transmitter firmware using the current trace-header workflow.

The replay path is:

```text
generic belief-maintenance demand trace
→ adapter-generated compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

Run 021 uses the existing once-per-second transmitter firmware. It is not yet
an airtime-saving experiment. The policy layer affects the metadata carried in
packets, not the physical transmission schedule.

For Run 021, TXA/N01 used the adapter-generated fixed-all trace, encoded as
policy `F`, with 16 compact trace rows. TXB/N16 used the adapter-generated
usefulness-threshold trace, encoded as policy `U`, with 8 compact trace rows.
The firmware run ID was updated to `R21`.

Run 021 produced 731 valid packets and 0 malformed packets. TXA/N01 delivered
367 packets with total usefulness 198.05 and mean usefulness 0.540. TXB/N16
delivered 364 packets with total usefulness 285.30 and mean usefulness 0.784.

Observed sequence gaps were light: TXA/N01 had one missing sequence value
`[9]`, and TXB/N16 had three missing sequence values `[30, 57, 228]`. These are
observed sequence gaps only and should not be interpreted as confirmed
collisions.

This is the first successful physical replay of adapter-generated traces. It
extends the v0.6 trace-interface milestone into the physical LoRa workflow:
adapter-generated metadata can be compiled into the existing firmware, replayed
over the LilyGO LoRa boards, logged by the receiver, and analyzed with the
existing parser.

The main interpretation remains delivery-versus-usefulness separation. TXA/N01
and TXB/N16 delivered nearly identical packet counts, but TXB/N16 carried
substantially higher delivered usefulness because its metadata trace was
threshold-selected. The result does not yet demonstrate airtime reduction,
because both transmitters still send once per second.

v0.8 reporting-schedule design checkpoint:

Branch `exp023-v08-reporting-schedule-design` adds an explicit reporting
schedule layer between generic demand traces and compact firmware trace CSVs.

The v0.8 path is:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ SEND-only compact firmware trace CSV
→ Arduino trace header
→ future physical LoRa replay
```

Run 022 is a design-stage reproduction check, not a physical radio run. It uses
the existing generic adapter example input:

```text
traces/run020_adapter_example_input.csv
```

and produces reporting schedules plus compact firmware traces using:

```bash
python scripts/make_reporting_schedule.py \
  --infile traces/run020_adapter_example_input.csv \
  --out-prefix traces/run022_reporting \
  --run-id R22 \
  --txa-policy fixed_all \
  --txb-policy usefulness_threshold \
  --threshold 0.50
```

The generated schedule files are:

```text
traces/run022_reporting_txa_fixed_all_schedule.csv
traces/run022_reporting_txb_usefulness_threshold_schedule.csv
```

The generated SEND-only compact trace files are:

```text
traces/run022_reporting_txa_fixed_all_compact.csv
traces/run022_reporting_txb_usefulness_threshold_compact.csv
```

The generated manifest is:

```text
traces/run022_reporting_reporting_schedule_manifest.json
```

For Run 022, TXA uses the fixed-all policy, encoded as policy `F`. All 16
demand rows are marked `SEND`, so the TXA compact trace contains 16 rows.

TXB uses the usefulness-threshold policy, encoded as policy `U`, with threshold
`0.50`. The TXB schedule contains 16 demand rows: 8 rows marked `SEND` and 8
rows marked `SKIP`. The TXB compact trace contains only the 8 `SEND` rows.

The manifest reports:

```text
TXA fixed_all:
  demand rows: 16
  send rows: 16
  skip rows: 0
  send fraction: 1.0
  scheduled total usefulness: 8.62
  scheduled mean usefulness: 0.53875

TXB usefulness_threshold:
  demand rows: 16
  send rows: 8
  skip rows: 8
  send fraction: 0.5
  scheduled total usefulness: 6.27
  scheduled mean usefulness: 0.78375
```

Both compact trace outputs validate through the existing header-generation path
using `scripts/make_trace_headers.py`.

This milestone introduces the distinction needed for constrained-airtime
experiments: demand rows, scheduled reporting decisions, compact transmitted
metadata rows, and receiver rows are different objects.

The v0.8 result does not demonstrate airtime reduction yet. It is a
reporting-schedule design artifact. Airtime-saving claims require a later
physical run in which firmware actually skips or schedules transmissions
differently.

v0.9 scheduled-SEND physical replay checkpoint:

Branch `exp024-v09-scheduled-send-physical-replay` performs the first physical
LoRa replay of compact traces produced from the v0.8 reporting-schedule
workflow.

The replay path is:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ SEND-only compact firmware trace CSV
→ Arduino trace header
→ physical LoRa replay
→ parsed receiver-row analysis
```

Run 023 uses the existing once-per-second transmitter firmware. It is a
physical replay of scheduled-SEND compact traces, but it is not yet a true
time-slotted packet-skipping experiment. The firmware does not preserve skipped
source-demand slots as silent intervals.

For Run 023, TXA/N01 used the fixed-all compact trace derived from the v0.8
schedule, encoded as policy `F`, with 16 compact trace rows. TXB/N16 used the
usefulness-threshold compact trace derived from the v0.8 schedule, encoded as
policy `U`, with 8 compact trace rows. The firmware run ID was updated to
`R23`.

Run 023 produced 735 valid packets and 0 malformed packets. TXA/N01 delivered
366 packets with total usefulness 197.83 and mean usefulness 0.541. TXB/N16
delivered 369 packets with total usefulness 289.55 and mean usefulness 0.785.

Observed sequence gaps were light: TXA/N01 had five missing sequence values
`[59, 93, 250, 294, 307]`, and TXB/N16 had one missing sequence value `[111]`.
These are observed sequence gaps only and should not be interpreted as confirmed
collisions.

This is the first successful physical replay of compact traces produced from
the reporting-schedule workflow. It extends v0.8 from a design-stage SEND/SKIP
schedule artifact into the physical LoRa replay workflow.

The main interpretation remains delivery-versus-usefulness separation. TXA/N01
and TXB/N16 delivered nearly identical packet counts, but TXB/N16 carried
substantially higher delivered usefulness because its compact replay trace
contains threshold-selected SEND rows. The result does not yet demonstrate
airtime reduction, because both transmitters still send once per second.

### v1.0 skipped-slot physical replay

The `v1.0` milestone introduces true skipped-slot firmware replay.

Earlier scheduled-SEND runs used SEND-only compact traces, so transmitters still sent once per second. In `v1.0`, the firmware reads full SEND/SKIP schedule headers. Each schedule row represents one reporting slot:

```text
SEND -> transmit one LoRa packet
SKIP -> remain silent for that slot
```

This preserves the demand timeline and makes reporting decisions physically affect transmission attempts.

The v1.0 skipped-slot path is:

```text
generic belief-maintenance demand trace
→ SEND/SKIP reporting schedule
→ Arduino schedule header
→ firmware slot loop
→ SEND transmits
→ SKIP remains silent
→ receiver log
→ parsed delivery-versus-usefulness analysis
```

Run 024 used the existing v0.8 reporting schedules:

```text
traces/run022_reporting_txa_fixed_all_schedule.csv
traces/run022_reporting_txb_usefulness_threshold_schedule.csv
```

These schedules were converted into firmware schedule headers using:

```text
scripts/make_schedule_headers.py
```

The generated schedule headers are:

```text
firmware/first_radio_link_TX-A/schedule_data_TXA.h
firmware/first_radio_link_TX_B/schedule_data_TXB.h
```

Schedule counts:

```text
TX-A: 16 schedule rows, 16 SEND, 0 SKIP
TX-B: 16 schedule rows, 8 SEND, 8 SKIP
```

Run 024 produced:

```text
Valid packets:      537
Malformed packets:  1
```

Packets by transmitter and node:

```text
TXA/N01: 361 packets
TXB/N16: 176 packets
```

This is the first physical result in the repository where the usefulness-threshold stream transmits substantially fewer packets because skipped schedule rows are preserved as silent firmware slots.

The receiver inter-arrival summary supports this interpretation:

```text
N01 mean receiver inter-arrival: 1.008 s
N16 mean receiver inter-arrival: 2.069 s
```

TX-A continued to appear at approximately one-second intervals, while TX-B appeared at approximately two-second intervals because alternate TX-B schedule slots were skipped.

Usefulness by node:

```text
TXA/N01 mean usefulness: 0.540
TXB/N16 mean usefulness: 0.786
```

The careful v1.0 interpretation is that Run 024 demonstrates reduced physical transmission attempts under scheduled skipping while preserving higher mean delivered usefulness in the usefulness-threshold stream.

It does not prove collision reduction, and it does not measure true transmitter-to-receiver latency.

### v1.1 schedule-aware analysis

The v1.1 analysis layer adds schedule-aware interpretation for skipped-slot physical replay runs.

The receiver parser remains packet-centric: it parses valid received packets and writes malformed rows to a rejects file. The new schedule-aware analyzer combines parsed receiver rows with the reporting schedules used by the transmitter firmware.

For Run 024:

```
python scripts/analyze_scheduled_replay.py \
  --schedule-a traces/run022_reporting_txa_fixed_all_schedule.csv \
  --schedule-b traces/run022_reporting_txb_usefulness_threshold_schedule.csv \
  --parsed logs/parsed_run_024_skipped_slot_replay.csv \
  --out-json reports/run024_schedule_aware_summary.json \
  --out-csv reports/run024_schedule_aware_summary.csv
```

Headline result:

```
TXA: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
TXB: 8/16 schedule rows SEND; 176 received packets; mean delivered usefulness 0.786
Observed received-packet ratio 0.4875; scheduled send-fraction ratio 0.5000.
```

This supports the careful interpretation that the TXB received-packet ratio is consistent with scheduled skipping while retaining higher mean usefulness per received packet.

The schedule CSVs define one repeated schedule period, so the analysis compares schedule proportions and observed packet proportions. It does not infer exact transmitted packet counts, confirmed collisions, true latency, or airtime optimization.

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

### v1.3 run-bundle validation

The v1.3 layer adds validation for manifest-bound replay-analysis bundles.

The validator checks that a run manifest points to existing artifacts and that the schedule-aware summary outputs agree with the manifest’s expected headline values.

For Run 024:

```
python scripts/validate_run_bundle.py \
  --manifest reports/run024_schedule_aware_manifest.json
```

The Run 024 bundle passes validation:

```
Bundle validation PASSED: reports/run024_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The validator confirms consistency among the manifest, schedule CSVs, firmware schedule headers, raw receiver log, parsed valid receiver log, parsed rejects log, summary JSON, summary CSV, expected headline values, transmitter labels, and node labels.

The validated headline remains:

```
TXA/N01: 16/16 schedule rows SEND; 361 received packets; mean delivered usefulness 0.540
TXB/N16: 8/16 schedule rows SEND; 176 received packets; mean delivered usefulness 0.786
Observed received-packet ratio 0.4875; scheduled send-fraction ratio 0.5000.
```

This is a validation checkpoint, not a new physical experiment. The careful interpretation remains unchanged: the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, consistent with scheduled skipping, while TXB retained higher mean delivered usefulness per received packet. The validation does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, or airtime optimization.

### v1.4 multi-run comparison scaffold

The v1.4 layer adds a comparison scaffold for one or more manifest-bound scheduled replay bundles.

At this milestone, only Run 024 is included. Therefore, this is not yet a multi-run empirical comparison. It is a scaffold that summarizes the validated Run 024 bundle and prepares the repository to include future scheduled replay runs.

For Run 024:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json \
  --validate
```

The `--validate` flag runs the v1.3 bundle validator before adding the run to the comparison output.

Generated outputs:

* `reports/scheduled_replay_comparison.csv`
* `reports/scheduled_replay_comparison.json`

Current comparison output:

```
Runs summarized: 1
Transmitter rows: 2
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
```

The scaffold preserves the Run 024 proportional comparison:

```
observed TXB/TXA received-packet ratio ≈ 0.4875
scheduled TXB/TXA send-fraction ratio = 0.5000
```

This is a comparison scaffold, not yet a replicated multi-run result. The careful interpretation remains that the validated Run 024 bundle is consistent with scheduled skipping while preserving higher mean delivered usefulness in the usefulness-threshold stream. The analysis does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, or airtime optimization.

### Run 025 planned repeat scheduled replay

Run 025 is planned as a second skipped-slot scheduled replay using the same Run 022 schedules as Run 024.

The purpose is replication under similar lab conditions, not a new policy experiment.

Planned Run 025 path:

```
logs/rx_run_025_skipped_slot_replay_repeat.csv
  → logs/parsed_run_025_skipped_slot_replay_repeat.csv
  → reports/run025_schedule_aware_summary.json
  → reports/run025_schedule_aware_manifest.json
  → bundle validation
  → Run 024 / Run 025 comparison
```

The planned comparison command is:

```
python scripts/compare_scheduled_runs.py \
  --manifest reports/run024_schedule_aware_manifest.json \
  --manifest reports/run025_schedule_aware_manifest.json \
  --out-csv reports/scheduled_replay_comparison.csv \
  --out-json reports/scheduled_replay_comparison.json \
  --validate
```

The expected careful interpretation is that a second run can test whether the observed packet proportions remain consistent with the scheduled send-fraction difference while the usefulness-threshold stream retains higher mean delivered usefulness per received packet.

This planned run should still avoid claims about exact transmitted-packet counts, confirmed collisions, true latency, LoRaWAN behavior, live belief-controller behavior, or airtime optimization.

### Run 025 skipped-slot replay repeat

Run 025 repeats the Run 024 skipped-slot physical replay under similar lab conditions using the same Run 022 reporting schedules.

Run 025 parser summary:

```
Valid packets:      552
Malformed packets:  0

TXA/N01: 368 packets
TXB/N16: 184 packets

TXA/N01 mean usefulness: 0.539
TXB/N16 mean usefulness: 0.785
```

Manifest-bound schedule-aware analysis:

```
TXA/N01: 16/16 schedule rows SEND; 368 received packets; mean delivered usefulness 0.539
TXB/N16: 8/16 schedule rows SEND; 184 received packets; mean delivered usefulness 0.785
Observed received-packet ratio 0.5000; scheduled send-fraction ratio 0.5000.
```

Run 025 passed bundle validation:

```
Bundle validation PASSED: reports/run025_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The Run 024 / Run 025 comparison now summarizes two physical scheduled replay runs:

```
Runs summarized: 2
Transmitter rows: 4
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786
run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785
```

Careful interpretation:

> Run 025 provides a second physical scheduled replay consistent with the Run 024 skipped-slot pattern. In both runs, the observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio, while TXB retains higher mean delivered usefulness per received packet.

The analysis remains bounded. It does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, LoRaWAN behavior, or airtime optimization.

### Run 026 strict-threshold scheduled replay

Run 026 extends the Run 024 / Run 025 skipped-slot replay sequence by testing a stricter usefulness-threshold schedule.

Runs 024 and 025 used the Run 022 schedules, where TXA/N01 used a fixed-all schedule and TXB/N16 used a usefulness-threshold schedule with 8 SEND rows out of 16 schedule rows. Run 026 keeps TXA/N01 fixed-all but raises the TXB/N16 usefulness threshold to `0.79`, producing 4 SEND rows out of 16 schedule rows.

Schedule counts:

```
TXA/N01: 16/16 SEND rows
TXB/N16: 4/16 SEND rows
```

Scheduled send-fraction ratio:

```
TXB/TXA = 4/16 = 0.2500
```

Run 026 parser summary:

```
Valid packets:      631
Malformed packets:  2

TXA/N01: 504 packets
TXB/N16: 127 packets

TXA/N01 mean usefulness: 0.538
TXB/N16 mean usefulness: 0.866
```

Manifest-bound schedule-aware analysis:

```
TXA/N01: 16/16 schedule rows SEND; 504 received packets; mean delivered usefulness 0.538
TXB/N16: 4/16 schedule rows SEND; 127 received packets; mean delivered usefulness 0.866
Observed received-packet ratio 0.2520; scheduled send-fraction ratio 0.2500.
```

The observed TXB/TXA received-packet ratio is close to the scheduled send-fraction ratio:

```
observed received-packet ratio: 0.2520
scheduled send-fraction ratio: 0.2500
```

Run 026 therefore adds a stricter-threshold point to the scheduled replay sequence. Compared with Runs 024 and 025, TXB/N16 scheduled fewer SEND rows and produced approximately one quarter as many received packets as TXA/N01, while retaining higher mean delivered usefulness per received packet.

Run 026 also passed through the manifest-bound analysis and bundle-validation workflow after updating the Run 026 manifest’s expected headline values.

The three-run scheduled replay comparison now summarizes Runs 024, 025, and 026:

```
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786

run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785

run026 TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
run026 TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866
```

Careful interpretation:

> Run 026 is consistent with the stricter scheduled-skipping condition carrying through to the physical replay. The observed TXB/TXA received-packet ratio was approximately 0.2520, close to the scheduled send-fraction ratio of 0.2500, while TXB retained higher mean delivered usefulness per received packet.

Together, Runs 024, 025, and 026 support a bounded threshold-family interpretation: changing the usefulness-threshold schedule changes the observed received-packet proportion in the expected direction while preserving the distinction between packet delivery count and delivered usefulness.

The analysis remains bounded. It does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, LoRaWAN behavior, or airtime optimization.

### Run 027 loose-threshold scheduled replay

Run 027 extends the threshold-family scheduled replay sequence by testing a looser usefulness-threshold schedule.

Runs 024 and 025 used a medium usefulness-threshold schedule, where TXB/N16 had 8 SEND rows out of 16 schedule rows. Run 026 used a stricter threshold, where TXB/N16 had 4 SEND rows out of 16 schedule rows. Run 027 adds the loose-threshold condition, where TXB/N16 has 12 SEND rows out of 16 schedule rows.

Schedule counts:

```
TXA/N01: 16/16 SEND rows
TXB/N16: 12/16 SEND rows
```

Scheduled send-fraction ratio:

```
TXB/TXA = 12/16 = 0.7500
```

Run 027 parser summary:

```
Valid packets:      699
Malformed packets:  0

TXA/N01: 400 packets
TXB/N16: 299 packets

TXA/N01 mean usefulness: 0.539
TXB/N16 mean usefulness: 0.667
```

Manifest-bound schedule-aware analysis:

```
TXA/N01: 16/16 schedule rows SEND; 400 received packets; mean delivered usefulness 0.539
TXB/N16: 12/16 schedule rows SEND; 299 received packets; mean delivered usefulness 0.667
Observed received-packet ratio 0.7475; scheduled send-fraction ratio 0.7500.
```

Run 027 passed bundle validation:

```
Bundle validation PASSED: reports/run027_schedule_aware_manifest.json
Checks passed: 70 / 70
```

The four-run scheduled replay comparison now summarizes Runs 024, 025, 026, and 027:

```
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786

run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785

run026 TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
run026 TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866

run027 TXA/N01: 16/16 SEND rows; 400 received packets; mean delivered usefulness 0.539
run027 TXB/N16: 12/16 SEND rows; 299 received packets; mean delivered usefulness 0.667
```

Together, Runs 024--027 now form a clearer threshold-family ladder:

```
12/16 loose threshold  → observed ratio 0.7475; TXB mean usefulness 0.667
 8/16 medium threshold → observed ratio 0.4875 and 0.5000; TXB mean usefulness approximately 0.785
 4/16 strict threshold → observed ratio 0.2520; TXB mean usefulness 0.866
```

Careful interpretation:

> Run 027 is consistent with the loose scheduled-skipping condition carrying through to the physical replay. The observed TXB/TXA received-packet ratio was approximately 0.7475, close to the scheduled send-fraction ratio of 0.7500, while TXB retained higher mean delivered usefulness per received packet than TXA.

Together, Runs 024--027 support a bounded threshold-family interpretation: changing the usefulness-threshold schedule changes the observed received-packet proportion in the expected direction, while the threshold-selected stream preserves higher mean delivered usefulness per received packet than the fixed-all stream.

The analysis remains bounded. It does not infer exact transmitted-packet counts, confirmed collisions, true latency, live belief-controller behavior, LoRaWAN behavior, airtime optimization, or energy savings.

### Threshold-family synthesis through Run 027

Runs 024--027 form the first complete threshold-family physical replay sequence in this repository.

The sequence compares a fixed-all TXA stream against usefulness-threshold TXB streams with different scheduled SEND fractions:

```
TXA fixed-all baseline: 16/16 SEND rows
TXB loose threshold:   12/16 SEND rows
TXB medium threshold:   8/16 SEND rows
TXB strict threshold:   4/16 SEND rows
```

Summary:

```
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16: 8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786

run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16: 8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785

run026 TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
run026 TXB/N16: 4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866

run027 TXA/N01: 16/16 SEND rows; 400 received packets; mean delivered usefulness 0.539
run027 TXB/N16: 12/16 SEND rows; 299 received packets; mean delivered usefulness 0.667
```

Threshold-family ladder:

```
12/16 loose threshold  → observed ratio 0.7475; TXB mean usefulness 0.667
 8/16 medium threshold → observed ratio 0.4875 and 0.5000; TXB mean usefulness approximately 0.785
 4/16 strict threshold → observed ratio 0.2520; TXB mean usefulness 0.866
```

Main interpretation:

> Runs 024--027 support a bounded threshold-family interpretation: changing the usefulness-threshold schedule changes the observed received-packet proportion in the expected direction, while the threshold-selected stream preserves higher mean delivered usefulness per received packet than the fixed-all stream.

The schedule-aware relationship is:

```
scheduled TXB/TXA ratio 0.7500 → observed ratio 0.7475
scheduled TXB/TXA ratio 0.5000 → observed ratio 0.4875 and 0.5000
scheduled TXB/TXA ratio 0.2500 → observed ratio 0.2520
```

The usefulness relationship is:

```
loose threshold:   TXB mean usefulness 0.667
medium threshold:  TXB mean usefulness approximately 0.785
strict threshold:  TXB mean usefulness 0.866
```

The analysis remains bounded. It does not infer exact transmitted-packet counts, confirmed collision counts, true latency, LoRaWAN behavior, airtime optimization, energy savings, live belief-controller behavior, operational wildfire relevance, or scalability to the planned 12-transmitter platform.

This completes the first threshold-family phase for now. The next recommended direction is microSD-backed replay design, because compiled firmware headers will become cumbersome for longer traces, AWSRT-derived demand schedules, and larger transmitter counts.

### microSD-backed replay through Run 028

The next phase moved the scheduled replay mechanism from compiled firmware schedule headers to microSD-backed schedule loading.

The motivation was practical. Compiled schedule headers worked well for short 16-row, two-transmitter experiments, but they will become cumbersome for longer traces, AWSRT-derived schedules, repeated replay experiments, and future scaling beyond TXA/TXB.

The microSD replay phase spans four milestones:

```
v2.3-microsd-replay-design
v2.4-run028-microsd-replay-design
v2.5-run028-microsd-firmware-prep
v2.6-run028-microsd-physical-replay
```

The main replay path is now:

```text
full analysis-facing SEND/SKIP schedule CSV
→ all-slot SD schedule CSV
→ /schedule.csv on transmitter microSD card
→ firmware loads schedule rows at startup
→ SEND transmits
→ SKIP remains silent
→ receiver log
→ parser
→ manifest-bound schedule-aware analysis
```

A key correction during this phase was the distinction between SEND-only compact CSVs and all-slot SD schedule CSVs. The earlier compact CSVs contain only transmitted rows and therefore omit skipped schedule slots. They are not suitable as direct `/schedule.csv` replay files for SD-backed scheduled skipping. For microSD replay, the firmware needs all schedule slots, including both SEND and SKIP rows.

A new SD schedule converter was added:

```text
scripts/make_sd_schedule_csv.py
```

For Run 028, it generated:

```text
traces/run028_sd_txa_schedule.csv
traces/run028_sd_txb_schedule.csv
```

using the SD-facing schema:

```text
seq,region,event,priority,usefulness,stale_after,policy,send
```

where `send=1` means transmit and `send=0` means remain silent for that schedule slot.

Two SD cards were prepared using a board-oriented naming convention:

```text
LORA_TXA → TXA/N01 → /schedule.csv from traces/run028_sd_txa_schedule.csv
LORA_TXB → TXB/N16 → /schedule.csv from traces/run028_sd_txb_schedule.csv
```

A small probe sketch was added to confirm that the boards could read `/schedule.csv` from microSD before attempting full LoRa replay:

```text
firmware/sd_schedule_probe/sd_schedule_probe.ino
```

Both TXA and TXB successfully initialized the SD card, opened `/schedule.csv`, and printed the expected schedule rows. TXB’s SD probe confirmed the expected SKIP rows at demand indices `1`, `5`, `9`, and `13`.

The transmitter firmware was then updated so that TXA and TXB load `/schedule.csv` at startup while preserving the existing parser-facing packet format.

Updated firmware files:

```text
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
```

Startup checks confirmed:

```text
TXA/N01:
  rows_loaded=16
  send_rows=16
  skip_rows=0

TXB/N16:
  rows_loaded=16
  send_rows=12
  skip_rows=4
```

Run 028 was the first physical microSD-backed replay. It reused the Run 027-style loose-threshold schedule semantics:

```text
TXA/N01: fixed-all, 16/16 SEND
TXB/N16: loose usefulness threshold, 12/16 SEND
```

Run 028 parser summary:

```text
Valid packets:      662
Malformed packets:  0

TXA/N01: 378 packets
TXB/N16: 284 packets

TXA/N01 mean usefulness: 0.539
TXB/N16 mean usefulness: 0.668
```

Manifest-bound schedule-aware analysis:

```text
TXA/N01: 16/16 schedule rows SEND; 378 received packets; mean delivered usefulness 0.539
TXB/N16: 12/16 schedule rows SEND; 284 received packets; mean delivered usefulness 0.668
Observed received-packet ratio 0.7513; scheduled send-fraction ratio 0.7500.
```

Run 028 aligns closely with the compiled-header Run 027 loose-threshold replay:

```text
Run 027:
  scheduled TXB/TXA ratio: 0.7500
  observed TXB/TXA ratio:  0.7475
  TXB mean usefulness:     0.667

Run 028:
  scheduled TXB/TXA ratio: 0.7500
  observed TXB/TXA ratio:  0.7513
  TXB mean usefulness:     0.668
```

The scheduled replay comparison now summarizes Runs 024--028:

```text
run024 TXA/N01: 16/16 SEND rows; 361 received packets; mean delivered usefulness 0.540
run024 TXB/N16:  8/16 SEND rows; 176 received packets; mean delivered usefulness 0.786

run025 TXA/N01: 16/16 SEND rows; 368 received packets; mean delivered usefulness 0.539
run025 TXB/N16:  8/16 SEND rows; 184 received packets; mean delivered usefulness 0.785

run026 TXA/N01: 16/16 SEND rows; 504 received packets; mean delivered usefulness 0.538
run026 TXB/N16:  4/16 SEND rows; 127 received packets; mean delivered usefulness 0.866

run027 TXA/N01: 16/16 SEND rows; 400 received packets; mean delivered usefulness 0.539
run027 TXB/N16: 12/16 SEND rows; 299 received packets; mean delivered usefulness 0.667

run028 TXA/N01: 16/16 SEND rows; 378 received packets; mean delivered usefulness 0.539
run028 TXB/N16: 12/16 SEND rows; 284 received packets; mean delivered usefulness 0.668
```

Careful interpretation:

> Run 028 supports a bounded storage-mechanism interpretation: the Run 027-style scheduled-skipping semantics can move from compiled firmware headers to microSD-backed replay while preserving the expected received-packet proportion and delivered-usefulness pattern under similar two-transmitter lab conditions.

The result does not prove exact equivalence between compiled-header and SD-backed replay. Physical LoRa reception varies across runs. The correct interpretation is that the expected scheduled-skipping pattern and usefulness pattern were preserved when the schedule storage mechanism changed.

The microSD phase does not infer exact transmitted-packet counts, confirmed collisions, true latency, LoRaWAN behavior, airtime optimization, energy savings, live belief-controller behavior, or scalability to the planned 12-transmitter platform.

This phase prepares the repository for longer traces, AWSRT-derived schedules, and future 3 → 6 → 12 transmitter scaling by separating firmware flashing from schedule swapping. The repository remains the source of reproducible analysis truth; the SD card is the physical replay medium.

### v2.8 microSD workflow cleanup

The `v2.8` milestone adds a small validation guardrail for microSD-backed replay schedules.

The key workflow distinction is that SEND-only compact CSVs are not valid SD replay schedules. Compact CSVs omit skipped slots and have schema:

```
seq,region,event,priority,usefulness,stale_after,policy
```

The transmitter firmware expects an all-slot SD schedule CSV with explicit SEND/SKIP decisions:

```
seq,region,event,priority,usefulness,stale_after,policy,send
```

where `send=1` means transmit and `send=0` means remain silent for that slot.

The new validator is:

```
scripts/validate_sd_schedule.py
```

It checks the SD-facing schema, contiguous sequence values, basic field types, and optional expected row counts.

Run 028 SD schedule validation:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run028_sd_txa_schedule.csv \
  --expected-rows 16 \
  --expected-send-rows 16 \
  --expected-skip-rows 0

python scripts/validate_sd_schedule.py \
  --infile traces/run028_sd_txb_schedule.csv \
  --expected-rows 16 \
  --expected-send-rows 12 \
  --expected-skip-rows 4
```

Both Run 028 SD schedules pass validation. The validator also correctly rejects the Run 027 SEND-only compact CSV because it lacks the required `send` column.

This milestone does not add a new physical replay. It makes the SD-card workflow safer before longer traces, AWSRT-derived schedules, or larger transmitter-count tests.

### v2.9 longer two-transmitter SD replay design

The `v2.9` milestone defines a design-only next step after the successful Run 028 microSD-backed replay and the `v2.8` SD workflow cleanup.

The purpose is to test the practical value of SD-backed replay with a longer schedule before adding transmitter-count complexity.

Run 028 used a short 16-row schedule:

```
TXA/N01: 16/16 SEND
TXB/N16: 12/16 SEND
```

Run 028 confirmed that the Run 027-style loose-threshold schedule semantics could move from compiled firmware headers to microSD-backed `/schedule.csv` replay while preserving the expected received-packet proportion under similar two-transmitter lab conditions.

The recommended next physical direction is a longer two-transmitter SD replay, not yet a three-transmitter run.

Proposed Run 029 target:

```
TXA/N01: fixed-all baseline, 64/64 SEND
TXB/N16: usefulness-threshold stream, 32/64 SEND
```

Expected scheduled TXB/TXA ratio:

```
32/64 = 0.5000
```

This would make Run 029 a longer-schedule version of the medium-threshold condition from Runs 024 and 025.

The intended path is:

```
generic demand trace
→ full reporting schedule CSV
→ all-slot SD schedule CSV
→ validated /schedule.csv on transmitter SD card
→ physical LoRa replay
→ parsed receiver log
→ manifest-bound schedule-aware analysis
```

The design recommends keeping the next physical replay two-transmitter so that only one main thing changes:

```
schedule length
```

It should not simultaneously change transmitter count, packet format, receiver logging, parser behavior, or the manifest-bound analysis pipeline.

Potential Run 029 files:

```
traces/run029_longer_adapter_input.csv
traces/run029_reporting_txa_fixed_all_schedule.csv
traces/run029_reporting_txb_usefulness_threshold_schedule.csv
traces/run029_sd_txa_schedule.csv
traces/run029_sd_txb_schedule.csv
logs/rx_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay.csv
logs/parsed_run_029_longer_sd_replay_rejects.csv
reports/run029_schedule_aware_manifest.json
reports/run029_schedule_aware_summary.csv
reports/run029_schedule_aware_summary.json
```

Before any physical replay, the SD schedules should validate with:

```
python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txa_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 64 \
  --expected-skip-rows 0

python scripts/validate_sd_schedule.py \
  --infile traces/run029_sd_txb_schedule.csv \
  --expected-rows 64 \
  --expected-send-rows 32 \
  --expected-skip-rows 32
```

The design milestone does not add a new physical run. It defines the next controlled experiment: increase the schedule length from 16 rows to 64 rows while preserving the existing two-transmitter SD replay workflow and bounded interpretation language.

The recommended follow-on milestone is:

```
v3.0-run029-longer-sd-schedule-prep
```

That milestone should generate and validate the Run 029 schedule artifacts before any physical replay.

## Scope caution

Missing sequence numbers should not be overinterpreted as collisions. A missing sequence means that a packet was not received or not logged within the observed sequence range. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB issues, or logger-side effects.

Malformed packets are written to parser reject files and excluded from valid-packet analysis.

The usefulness and priority fields are currently synthetic metadata. They are not yet generated by a live belief-maintenance controller.

The setup uses point-to-point LoRa at 915 MHz. It is not a LoRaWAN system.

`recv_ms` and `tx_ms` are measured on different boards and should not be interpreted as synchronized packet-latency measurements.