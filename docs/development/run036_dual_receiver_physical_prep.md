# Run 036 Dual-Receiver Physical Prep

## Purpose

Run 036 physical prep prepares the hardware and logging workflow for the dual-receiver twelve-transmitter replay.

This milestone does not record physical replay evidence. It prepares the RXA/RXB upload, serial logging, and artifact naming workflow so that the later physical replay can compare two receiver-side observations of the same fixed manifest.

## Receiver Roles

Run 036 uses:

- RXA: original LilyGo LoRa32 receiver.
- RXB: LilyGo T-Beam receiver.

RXA preserves continuity with Run 035. RXB provides an independent second receiver path.

The fixed replay manifest and twelve-transmitter schedule should remain unchanged from the Run 035 alternate-offset replay setup unless a later milestone explicitly documents otherwise.

## Receiver Sketches

Upload these sketches:

    firmware/first_radio_link_RX_A_LORA32/first_radio_link_RX_A_LORA32.ino
    firmware/first_radio_link_RX_B_TBEAM/first_radio_link_RX_B_TBEAM.ino

Expected startup banners:

    === RXA_LORA32: LilyGO LoRa32 receiver ===
    === RXB_TBEAM: LilyGO T-Beam receiver ===

Expected packet row format remains:

    RX,millis,payload,rssi,snr

Receiver identity is carried by log filename and startup banner, not by adding a receiver field to packet rows.

## RXB T-Beam Verification

The T-Beam has not yet been validated in this repository workflow.

Before treating RXB as a usable receiver, verify:

- the sketch compiles for the selected T-Beam board target;
- the upload succeeds;
- the serial monitor shows the RXB startup banner;
- LoRa initialization reports OK;
- the board receives at least one known test packet or replay packet;
- the raw log preserves the expected packet row format.

The RXB pin mapping is a physical-prep setting to verify during upload/test, not a completed experimental result.

## Expected Raw Log Files

Use separate terminal sessions or serial loggers for RXA and RXB.

Expected raw logs:

    logs/rx_run_036_dual_receiver_rxa_lora32.csv
    logs/rx_run_036_dual_receiver_rxb_tbeam.csv

Do not combine receiver logs during capture. Keep RXA and RXB raw logs separate so that receiver-side evidence can be compared after parsing.

## Pre-Run Checklist

Before the dual-receiver replay:

- confirm branch and repository state;
- confirm both receiver sketches are uploaded to the intended boards;
- confirm RXA serial output shows the RXA banner;
- confirm RXB serial output shows the RXB banner;
- confirm both receivers report LoRa init OK;
- confirm both antennas are attached;
- confirm both receiver serial logs are being written to distinct filenames;
- confirm the twelve transmitter SD cards still contain the intended Run 035 alternate-offset schedules;
- confirm TXK uses STARTUP_OFFSET_MS = 133;
- confirm TXL uses STARTUP_OFFSET_MS = 271;
- confirm no new manifest or schedule changes are introduced during this prep milestone.

## Post-Capture Artifact Plan

The later physical replay milestone should produce at least:

    logs/rx_run_036_dual_receiver_rxa_lora32.csv
    logs/rx_run_036_dual_receiver_rxb_tbeam.csv
    logs/parsed_run_036_dual_receiver_rxa_lora32.csv
    logs/parsed_run_036_dual_receiver_rxb_tbeam.csv
    logs/parsed_run_036_dual_receiver_rxa_lora32_rejects.csv
    logs/parsed_run_036_dual_receiver_rxb_tbeam_rejects.csv
    outputs/run036_dual_receiver_rxa_manifest_replay_summary.csv
    outputs/run036_dual_receiver_rxb_manifest_replay_summary.csv
    outputs/run036_dual_receiver_comparison_summary.csv
    outputs/run036_dual_receiver_comparison_summary.json
    outputs/run036_dual_receiver_validation.json

Exact artifact names may be adjusted later, but receiver identity should remain explicit.

## Planned Comparison

The physical replay should support:

- RXA-only packet identities;
- RXB-only packet identities;
- packet identities observed by both receivers;
- manifest-expected SEND opportunities observed by neither receiver;
- receiver-side union;
- receiver-side intersection;
- per-receiver transmitter representation;
- per-receiver report-class preservation;
- divergence between RXA and RXB observed report distributions.

Packet matching should use manifest-relative packet identity:

    transmitter identity
    node identity
    sequence number

Receiver timestamp should not be used as the primary matching key because RXA and RXB clocks are not assumed synchronized.

## Interpretation Boundaries

Receiver logs are receiver-side observations, not ground-truth transmitted-packet records.

Missing packets do not by themselves prove collision, interference, timing drift, transmitter failure, receiver failure, or any specific physical cause.

This prep milestone does not claim successful RXB operation, successful dual-receiver replay, LoRaWAN behavior, synchronized latency, energy savings, airtime optimization, arbitrary-layout generalization, or operational wildfire behavior.

The later Run 036 physical replay should remain manifest-bound and manifest-relative: replay execution, received packets, parsed logs, summary artifacts, validation checks, and interpretation should tie back to the fixed replay manifest.
