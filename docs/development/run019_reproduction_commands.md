python scripts/generate_policy_traces.py

python scripts/make_trace_headers.py \
  --infile traces/run019_txa_fixed_all.csv \
  --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h

python scripts/make_trace_headers.py \
  --infile traces/run019_txb_usefulness_threshold.csv \
  --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h

python scripts/receiver_logger.py \
  --port /dev/cu.usbserial-576B0005451 \
  --out logs/rx_run_019_policy_controlled.csv

python scripts/parse_receiver_log.py \
  --infile logs/rx_run_019_policy_controlled.csv \
  --out logs/parsed_run_019_policy_controlled.csv \
  --seq-window 50

  # Run 019 Reproduction Commands

This note records the command-line steps used to regenerate the Run 019 policy-controlled synthetic traces, rebuild the compiled-in Arduino trace headers, log the physical receiver output, and parse the resulting receiver log.

Run 019 belongs to the v0.5 policy-controlled synthetic trace milestone.

## 1. Generate policy-controlled traces

From the repository root:

```bash
python scripts/generate_policy_traces.py
```

Default Run 019 outputs:

```text
traces/run019_base_demand.csv
traces/run019_txa_fixed_all.csv
traces/run019_txb_usefulness_threshold.csv
traces/run019_policy_manifest.json
```

The default generator settings are:

```text
run_id: R19
TX-A policy: fixed_all
TX-B policy: usefulness_threshold
threshold: 0.50
```

Expected summary:

```text
Generated R19 policy-controlled traces

Base demand rows: 320

TXA/N01 fixed_all: 320 rows, total usefulness=149.50, mean usefulness=0.467
TXB/N16 usefulness_threshold: 120 rows, threshold=0.50, total usefulness=104.50, mean usefulness=0.871
```

## 2. Regenerate Arduino trace headers

Generate the TX-A compiled-in trace header:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run019_txa_fixed_all.csv \
  --outfile firmware/first_radio_link_TX-A/trace_data_TXA.h
```

Generate the TX-B compiled-in trace header:

```bash
python scripts/make_trace_headers.py \
  --infile traces/run019_txb_usefulness_threshold.csv \
  --outfile firmware/first_radio_link_TX_B/trace_data_TXB.h
```

Expected header row counts:

```text
firmware/first_radio_link_TX-A/trace_data_TXA.h: TRACE_ROW_COUNT = 320
firmware/first_radio_link_TX_B/trace_data_TXB.h: TRACE_ROW_COUNT = 120
```

## 3. Upload firmware

Use Arduino IDE.

Upload TX-A firmware to the TX-A board:

```text
firmware/first_radio_link_TX-A/first_radio_link_TX-A.ino
```

Upload TX-B firmware to the TX-B board:

```text
firmware/first_radio_link_TX_B/first_radio_link_TX_B.ino
```

For Run 019, both transmitter sketches should use:

```text
RUN_ID = R19
```

The RX firmware was unchanged from the previous working receiver setup.

## 4. Log receiver output

Start the receiver logger before powering or resetting both transmitters.

Check the receiver logger interface with:

```bash
python scripts/receiver_logger.py --help
```

Then run the logger using the RX serial port for the receiver board. Example:

```bash
python scripts/receiver_logger.py \
  --port /dev/cu.usbserial-576B0005451 \
  --outfile logs/rx_run_019_policy_controlled.csv
```

If the local script uses `--out` instead of `--outfile`, use the option shown by `--help`.

## 5. Parse the receiver log

```bash
python scripts/parse_receiver_log.py \
  --infile logs/rx_run_019_policy_controlled.csv \
  --out logs/parsed_run_019_policy_controlled.csv \
  --seq-window 50
```

Expected parsed outputs:

```text
logs/parsed_run_019_policy_controlled.csv
logs/parsed_run_019_policy_controlled_rejects.csv
```

## 6. Run 019 result summary

Run 019 produced:

```text
Valid packets:      979
Malformed packets:  3
```

Packets by transmitter and node:

```text
TXA/N01: 490
TXB/N16: 489
```

Observed sequence gaps:

```text
TXA/N01: missing 1 -> [209]
TXB/N16: missing 1 -> [186]
```

Delivered usefulness:

```text
TXA/N01 fixed_all:              total usefulness 235.7, mean usefulness 0.481
TXB/N16 usefulness_threshold:   total usefulness 425.6, mean usefulness 0.870
```

## 7. Interpretation caution

Run 019 is a policy-controlled trace-content experiment, not yet an airtime-saving experiment.

The firmware still transmits once per second. The policy layer controls the trace rows and usefulness metadata that are replayed, not the physical radio transmission schedule.

Observed sequence gaps should not be interpreted directly as collisions. They mean that a packet was not received or not logged within the observed sequence range.
