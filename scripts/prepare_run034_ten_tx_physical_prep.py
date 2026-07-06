#!/usr/bin/env python3
"""
Prepare Run 034 ten-transmitter physical-prep artifacts.

This script updates repository-side firmware sketches for Run 034 and writes
physical-preparation checklist artifacts.

It does not flash hardware, copy files to SD cards, collect receiver logs, or
make physical replay claims.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path
from typing import Any


MANIFEST = Path("traces/run034_reporting_reporting_schedule_manifest.json")
SUMMARY_JSON = Path("outputs/run034_ten_tx_physical_prep_summary.json")
SUMMARY_CSV = Path("outputs/run034_ten_tx_physical_prep_summary.csv")
SD_COPY_SCRIPT = Path("scripts/copy_run034_sd_schedules_to_cards.sh")

RUN_ID = "R34"
MILESTONE = "v5.9-run034-ten-transmitter-physical-prep"

FIRMWARE = {
    "TXA": {
        "dir": Path("firmware/first_radio_link_TX_A"),
        "ino": "first_radio_link_TX_A.ino",
        "template_tx": None,
    },
    "TXB": {
        "dir": Path("firmware/first_radio_link_TX_B"),
        "ino": "first_radio_link_TX_B.ino",
        "template_tx": None,
    },
    "TXC": {
        "dir": Path("firmware/first_radio_link_TX_C"),
        "ino": "first_radio_link_TX_C.ino",
        "template_tx": None,
    },
    "TXD": {
        "dir": Path("firmware/first_radio_link_TX_D"),
        "ino": "first_radio_link_TX_D.ino",
        "template_tx": None,
    },
    "TXE": {
        "dir": Path("firmware/first_radio_link_TX_E"),
        "ino": "first_radio_link_TX_E.ino",
        "template_tx": None,
    },
    "TXF": {
        "dir": Path("firmware/first_radio_link_TX_F"),
        "ino": "first_radio_link_TX_F.ino",
        "template_tx": None,
    },
    "TXG": {
        "dir": Path("firmware/first_radio_link_TX_G"),
        "ino": "first_radio_link_TX_G.ino",
        "template_tx": None,
    },
    "TXH": {
        "dir": Path("firmware/first_radio_link_TX_H"),
        "ino": "first_radio_link_TX_H.ino",
        "template_tx": None,
    },
    "TXI": {
        "dir": Path("firmware/first_radio_link_TX_I"),
        "ino": "first_radio_link_TX_I.ino",
        "template_tx": "TXC",
    },
    "TXJ": {
        "dir": Path("firmware/first_radio_link_TX_J"),
        "ino": "first_radio_link_TX_J.ino",
        "template_tx": "TXD",
    },
}


def read_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    txs = manifest.get("transmitters", [])

    if len(txs) != 10:
        raise ValueError(f"Expected 10 transmitters, found {len(txs)}")

    missing_offsets = [
        tx["tx_id"]
        for tx in txs
        if tx.get("startup_offset_ms") is None
    ]
    if missing_offsets:
        raise ValueError(f"Missing startup offsets for: {missing_offsets}")

    return manifest


def sketch_path(tx_id: str) -> Path:
    info = FIRMWARE[tx_id]
    return info["dir"] / info["ino"]


def ensure_new_firmware_dirs() -> None:
    for tx_id, info in FIRMWARE.items():
        template_tx = info["template_tx"]
        if template_tx is None:
            continue

        dst_dir = info["dir"]
        dst_ino = dst_dir / info["ino"]

        if dst_dir.exists():
            if not dst_ino.exists():
                raise FileNotFoundError(
                    f"{dst_dir} exists but expected sketch is missing: {dst_ino}"
                )
            continue

        src_info = FIRMWARE[template_tx]
        src_dir = src_info["dir"]
        src_ino = src_dir / src_info["ino"]

        if not src_ino.exists():
            raise FileNotFoundError(f"Template sketch missing: {src_ino}")

        shutil.copytree(src_dir, dst_dir)

        copied_ino = dst_dir / src_info["ino"]
        if not copied_ino.exists():
            raise FileNotFoundError(f"Copied sketch missing: {copied_ino}")

        copied_ino.rename(dst_ino)


def replace_one(pattern: str, replacement: str, text: str, *, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Expected exactly one replacement for {label}; got {count}")
    return new_text


def patch_sketch(path: Path, *, tx_id: str, node_id: str, startup_offset_ms: int) -> None:
    if not path.exists():
        raise FileNotFoundError(path)

    original = path.read_text(encoding="utf-8")
    text = original

    text = replace_one(
        r'const\s+char\*\s+RUN_ID\s*=\s*"R\d+"\s*;',
        f'const char* RUN_ID = "{RUN_ID}";',
        text,
        label=f"{path} RUN_ID",
    )
    text = replace_one(
        r'const\s+char\*\s+TX_ID\s*=\s*"TX[A-Z]"\s*;',
        f'const char* TX_ID = "{tx_id}";',
        text,
        label=f"{path} TX_ID",
    )
    text = replace_one(
        r'const\s+char\*\s+NODE_ID\s*=\s*"N\d+"\s*;',
        f'const char* NODE_ID = "{node_id}";',
        text,
        label=f"{path} NODE_ID",
    )
    text = replace_one(
        r'const\s+unsigned\s+long\s+STARTUP_OFFSET_MS\s*=\s*\d+\s*;',
        f'const unsigned long STARTUP_OFFSET_MS = {startup_offset_ms};',
        text,
        label=f"{path} STARTUP_OFFSET_MS",
    )

    if '"R33"' in text:
        raise ValueError(f"Unpatched R33 remains in {path}")

    if original != text:
        path.write_text(text, encoding="utf-8")


def write_summary(rows: list[dict[str, Any]]) -> None:
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "run_id": "run034_ten_transmitter_physical_prep",
        "milestone": MILESTONE,
        "firmware_run_id": RUN_ID,
        "purpose": (
            "Prepare Run 034 firmware and SD-card physical-prep instructions. "
            "No physical replay has been run."
        ),
        "transmitter_count": len(rows),
        "transmitters": rows,
        "sd_card_actions": [
            "For TXA-TXH existing cards: remove old schedule.csv/SCHEDULE.CSV and copy the matching Run 034 SD schedule as schedule.csv.",
            "For TXI and TXJ new cards: rename cards from NO NAME to LORA_TXI and LORA_TXJ, then copy the matching Run 034 SD schedule as schedule.csv.",
        ],
        "expected_receiver_log": "logs/rx_run_034_ten_transmitter_sd_replay_candidate.csv",
        "expected_analysis_outputs": [
            "outputs/run034_ten_transmitter_manifest_replay_candidate_summary.json",
            "outputs/run034_ten_transmitter_manifest_replay_candidate_summary.csv",
            "outputs/run034_ten_transmitter_manifest_replay_candidate_validation.json",
        ],
        "interpretation_boundary": [
            "Physical preparation only; no receiver log has been collected.",
            "Does not establish ten-transmitter physical replay success.",
            "Does not infer exact transmitted-packet counts.",
            "Does not confirm RF collisions or absence of collisions.",
            "Does not establish synchronized latency.",
            "Does not evaluate LoRaWAN behavior.",
            "Does not establish energy savings or airtime optimization.",
            "Does not use a live belief-maintenance controller.",
            "Does not evaluate operational wildfire behavior.",
        ],
    }

    SUMMARY_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "tx_id",
        "node_id",
        "firmware_sketch",
        "run_id",
        "startup_offset_ms",
        "sd_source",
        "sd_volume",
        "sd_destination",
        "expected_send_rows",
        "expected_rows",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_sd_copy_script(rows: list[dict[str, Any]]) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "echo 'Copying Run 034 SD schedules to mounted transmitter cards'",
        "echo 'This removes old schedule.csv/SCHEDULE.CSV before copying the Run 034 schedule.'",
        "",
    ]

    for row in rows:
        volume = row["sd_volume"]
        source = row["sd_source"]
        tx_id = row["tx_id"]
        lines.extend(
            [
                f"echo 'Preparing {tx_id} card: {volume}'",
                f"test -d '{volume}'",
                f"rm -f '{volume}/schedule.csv' '{volume}/SCHEDULE.CSV'",
                f"cp '{source}' '{volume}/schedule.csv'",
                f"sync",
                "",
            ]
        )

    SD_COPY_SCRIPT.write_text("\n".join(lines), encoding="utf-8")
    SD_COPY_SCRIPT.chmod(0o755)


def main() -> None:
    manifest = read_manifest()
    ensure_new_firmware_dirs()

    rows: list[dict[str, Any]] = []

    for tx in manifest["transmitters"]:
        tx_id = tx["tx_id"]
        node_id = tx["node_id"]
        offset = int(tx["startup_offset_ms"])

        path = sketch_path(tx_id)
        patch_sketch(
            path,
            tx_id=tx_id,
            node_id=node_id,
            startup_offset_ms=offset,
        )

        rows.append(
            {
                "tx_id": tx_id,
                "node_id": node_id,
                "firmware_sketch": str(path),
                "run_id": RUN_ID,
                "startup_offset_ms": offset,
                "sd_source": tx["sd_csv"],
                "sd_volume": f"/Volumes/LORA_{tx_id}",
                "sd_destination": f"/Volumes/LORA_{tx_id}/schedule.csv",
                "expected_send_rows": tx["expected_send_rows"],
                "expected_rows": tx["expected_rows"],
            }
        )

    write_summary(rows)
    write_sd_copy_script(rows)

    print("Prepared Run 034 physical-prep artifacts")
    print()
    print(f"Wrote: {SUMMARY_JSON}")
    print(f"Wrote: {SUMMARY_CSV}")
    print(f"Wrote: {SD_COPY_SCRIPT}")
    print()
    print("Firmware/card table:")
    for row in rows:
        print(
            f"  {row['tx_id']}/{row['node_id']}: "
            f"{row['firmware_sketch']}, "
            f"RUN_ID={row['run_id']}, "
            f"STARTUP_OFFSET_MS={row['startup_offset_ms']}, "
            f"SD={row['sd_source']} -> {row['sd_destination']}"
        )

    print()
    print("No hardware has been flashed and no SD card has been modified by this script.")


if __name__ == "__main__":
    main()
