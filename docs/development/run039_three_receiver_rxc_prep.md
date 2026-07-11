# Run 039 Three-Receiver RXC Prep

## Purpose

This note prepares the third receiver for the final three-receiver experiment design.

The receiver set for the final paper experiment is:

- RXA: LilyGo LoRa32 receiver;
- RXB: LilyGo T-Beam receiver;
- RXC: second LilyGo T-Beam receiver.

RXC is added to support three-receiver packet-identity comparison: packet identities observed by all three receivers, by exactly two receivers, or by exactly one receiver.

## RXC Firmware Sketch

RXC sketch path:

    firmware/first_radio_link_RX_C_TBEAM/first_radio_link_RX_C_TBEAM.ino

RXC expected banner:

    === RXC_TBEAM: LilyGO T-Beam receiver ===

RXC packet row format remains unchanged:

    RX,millis,payload,rssi,snr

Keeping the packet row unchanged preserves compatibility with the existing receiver logger and parser workflow.

## Expected Receiver Roles

| Receiver | Board role | Sketch |
|---|---|---|
| RXA | LilyGo LoRa32 receiver | `firmware/first_radio_link_RX_A_LORA32/first_radio_link_RX_A_LORA32.ino` |
| RXB | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_B_TBEAM/first_radio_link_RX_B_TBEAM.ino` |
| RXC | LilyGo T-Beam receiver | `firmware/first_radio_link_RX_C_TBEAM/first_radio_link_RX_C_TBEAM.ino` |

## RXC Upload Verification

After uploading the RXC sketch, confirm through serial monitor that RXC prints:

    === RXC_TBEAM: LilyGO T-Beam receiver ===
    LoRa init OK.
    Waiting for packets...

## Planned Raw Log Naming

Use separate logger sessions for all three receivers.

Suggested raw log naming pattern for final experiment runs:

    logs/rx_run_040_close_repeat1_rxa_lora32.csv
    logs/rx_run_040_close_repeat1_rxb_tbeam.csv
    logs/rx_run_040_close_repeat1_rxc_tbeam.csv

Condition/run naming should remain explicit about:

- run number;
- physical condition;
- repeat number;
- receiver identity;
- receiver board role.

## Interpretation Boundaries

RXC adds another receiver-side observation stream. It does not provide ground-truth transmitted-packet records.

RXB and RXC are both T-Beam-class receivers, but they should not be treated as calibrated identical instruments.

Receiver-specific packet identities do not by themselves establish collision, interference, timing drift, antenna behavior, board sensitivity, transmitter failure, receiver failure, or any specific physical cause.
