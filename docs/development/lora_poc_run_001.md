# LoRa POC Run 001: Receiver Logger and Parser Test

## Date

2026-06-22

## Purpose

This run tested whether packets from the LilyGO LoRa receiver can be logged by a Python serial logger, parsed into structured packet rows, and summarized with both communication metadata and synthetic usefulness metadata.

## Hardware

- RX: LilyGO LoRa32 T3 V1.6.1, running receiver firmware
- TX-A: LilyGO LoRa32 T3 V1.6.1, sending logical node `N01`
- TX-B: LilyGO LoRa32 T3 V1.6.1, sending logical node `N16`
- Frequency: 915 MHz
- Antennas attached to all boards
- RX connected to laptop by USB
- TX boards powered separately or by USB

## Software

- Conda environment: `dcoss-lora-poc`
- Python: 3.11.15
- pyserial: 3.5
- pandas: 3.0.3
- Logger: `scripts/receiver_logger.py`
- Parser: `scripts/parse_receiver_log.py`

## Input and Output Files

- Raw receiver log: `logs/rx_run_001.csv`
- Parsed valid packets: `logs/parsed_run_001.csv`
- Malformed/rejected packets: `logs/parsed_run_001_rejects.csv`

## Summary

The parser reported:

```text
Valid packets:      25
Malformed packets:  1
```

Packets by node:

```text
N01    19
N16     6
```

Radio metadata by node:

```text
N01 mean RSSI: -24.32 dBm
N01 mean SNR:    9.67 dB

N16 mean RSSI: -55.50 dBm
N16 mean SNR:    9.38 dB
```

Usefulness by node:

```text
N01 total usefulness: 14.06
N16 total usefulness:  4.80
```

## Notes

One malformed receiver line was observed and written to the reject file. This confirms that the parser can preserve malformed or corrupted packets without contaminating valid packet metrics.

The current packet format does not yet include separate physical transmitter identifiers. The next firmware revision should include `tx_id` so that physical transmitters and logical node identifiers can be distinguished.

The transmitter and receiver `millis()` clocks are not synchronized. Receiver inter-arrival time is meaningful, but `recv_ms - tx_ms` should not yet be interpreted as true latency.

## Status

Milestone complete: real LoRa receiver logs can be captured, parsed, summarized, and joined with synthetic usefulness metadata.
