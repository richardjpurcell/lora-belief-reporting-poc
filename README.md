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

Runs 011 and 012 preserve the same packet schema as the v0.1 runs, but TXB/N16+now emits demand-like usefulness phases while TXA/N01 remains a lower-value
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

## Scope caution

Missing sequence numbers should not be overinterpreted as collisions. A missing sequence means that a packet was not received or not logged within the observed sequence range. Possible causes include LoRa loss, packet overlap, receiver timing, power or USB issues, or logger-side effects.

The usefulness and priority fields are currently synthetic metadata. They are not yet generated by a live belief-maintenance controller.

