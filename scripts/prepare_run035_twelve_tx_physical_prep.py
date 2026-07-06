#!/usr/bin/env python3
"""
Prepare Run 035 twelve-transmitter physical-prep artifacts.

This script updates repository-side firmware sketches for Run 035 and writes
physical-preparation checklist artifacts.

It does not flash hardware, copy files to mounted SD cards, collect receiver
logs, run hardware, parse receiver logs, validate a physical replay, or make
physical replay claims.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path
from typing import Any


MANIFEST = Path("traces/run035_reporting_reporting_schedule_manifest.json")
SUMMARY_JSON = Path("outputs/run035_twelve_tx_physical_prep_summary.json")
SUMMARY_CSV = Path("outputs/run035_twelve_tx_physical_prep_summary.csv")
ONE_CARD_SD_COPY_SCRIPT = Path("scripts/copy_run035_one_sd_schedule_to_card.sh")

RUN_ID = "R35"
MILESTONE = "v5.15-run035-twelve-transmitter-physical-prep"

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
        "template_tx": None,
    },
    "TXJ": {
        "dir": Path("firmware/first_radio_link_TX_J"),
        "ino": "first_radio_link_TX_J.ino",
        "template_tx": None,
    },
    "TXK": {
        "dir": Path("firmware/first_radio_link_TX_K"),
        "ino": "first_radio_link_TX_K.ino",
        "template_tx": "TXI",
    },
    "TXL": {
        "dir": Path("firmware/first_radio_link_TX_L"),
        "ino": "first_radio_link_TX_L.ino",
        "template_tx": "TXJ",
    },
}


def read_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    txs = manifest.get("transmitters", [])

    expected_tx_ids = [f"TX{letter}" for letter in "ABCDEFGHIJKL"]
    observed_tx_ids = [tx["tx_id"] for tx in txs]

    if observed_tx_ids != expected_tx_ids:
        raise ValueError(f"Expected TX order {expected_tx_ids}, found {observed_tx_ids}")

    missing_offsets = [
        tx["tx_id"]
        for tx in txs
        if tx.get("startup_offset_ms") is None
    ]
    if missing_offsets:
        raise ValueError(f"Missing startup offsets for: {missing_offsets}")

    if not manifest.get("phase_plan", {}).get("claims", {}).get("phase_plan_computed"):
        raise ValueError("Run 035 manifest does not record completed phase planning")

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
    tx_letter = tx_id[-1]

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
    text = replace_one(
        r'Serial\.println\("=== TX-[A-Z]: LilyGO LoRa32 sender ==="\);',
        f'Serial.println("=== TX-{tx_letter}: LilyGO LoRa32 sender ===");',
        text,
        label=f"{path} serial banner",
    )

    if '"R34"' in text or '"R33"' in text:
        raise ValueError(f"Old run ID remains in {path}")

    if f'const char* TX_ID = "{tx_id}";' not in text:
        raise ValueError(f"TX_ID patch failed for {path}")

    if f'const char* NODE_ID = "{node_id}";' not in text:
        raise ValueError(f"NODE_ID patch failed for {path}")

    if f'const unsigned long STARTUP_OFFSET_MS = {startup_offset_ms};' not in text:
        raise ValueError(f"STARTUP_OFFSET_MS patch failed for {path}")

    path.write_text(text, encoding="utf-8")


def write_summary(rows: list[dict[str, Any]]) -> None:
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "run_id": "run035_twelve_transmitter_physical_prep",
        "milestone": MILESTONE,
        "firmware_run_id": RUN_ID,
        "purpose": (
            "Prepare Run 035 firmware and SD-card physical-prep instructions. "
            "No physical replay has been run."
        ),
        "transmitter_count": len(rows),
        "transmitters": rows,
        "sd_card_actions": [
            "For TXA-TXJ existing cards: remove old schedule.csv/SCHEDULE.CSV and copy the matching Run 035 SD schedule as schedule.csv.",
            "For TXK and TXL new cards: rename cards from NO NAME to LORA_TXK and LORA_TXL, then copy the matching Run 035 SD schedule as schedule.csv.",
            "Use the one-card-at-a-time helper when only one SD card can be mounted at a time.",
        ],
        "one_card_copy_helper": str(ONE_CARD_SD_COPY_SCRIPT),
        "expected_receiver_log": "logs/rx_run_035_twelve_transmitter_sd_replay_candidate.csv",
        "expected_analysis_outputs": [
            "outputs/run035_twelve_transmitter_manifest_replay_candidate_summary.json",
            "outputs/run035_twelve_transmitter_manifest_replay_candidate_summary.csv",
            "outputs/run035_twelve_transmitter_manifest_replay_candidate_validation.json",
        ],
        "interpretation_boundary": [
            "Physical preparation only; no receiver log has been collected.",
            "Does not establish twelve-transmitter physical replay success.",
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
        "new_firmware",
        "new_sd_card",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_one_card_sd_copy_script(rows: list[dict[str, Any]]) -> None:
    source_by_tx = {row["tx_id"]: row["sd_source"] for row in rows}
    valid_tx = " ".join(source_by_tx)

    case_lines = []
    for tx_id, source in source_by_tx.items():
        case_lines.extend(
            [
                f"  {tx_id})",
                f"    SOURCE='{source}'",
                f"    DEFAULT_VOLUME='/Volumes/LORA_{tx_id}'",
                "    ;;",
            ]
        )

    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "if [[ $# -lt 1 || $# -gt 2 ]]; then",
        f"  echo 'Usage: $0 <TX_ID> [mounted_volume_path]' >&2",
        f"  echo 'Valid TX_ID values: {valid_tx}' >&2",
        "  exit 2",
        "fi",
        "",
        "TX_ID=\"$1\"",
        "MOUNT_OVERRIDE=\"${2:-}\"",
        "",
        "case \"$TX_ID\" in",
        *case_lines,
        "  *)",
        f"    echo 'Unknown TX_ID. Valid values: {valid_tx}' >&2",
        "    exit 2",
        "    ;;",
        "esac",
        "",
        "VOLUME=\"${MOUNT_OVERRIDE:-$DEFAULT_VOLUME}\"",
        "",
        "echo \"Preparing Run 035 SD schedule for ${TX_ID}\"",
        "echo \"Source: ${SOURCE}\"",
        "echo \"Mounted volume: ${VOLUME}\"",
        "",
        "test -f \"$SOURCE\"",
        "test -d \"$VOLUME\"",
        "",
        "rm -f \"$VOLUME/schedule.csv\" \"$VOLUME/SCHEDULE.CSV\"",
        "cp \"$SOURCE\" \"$VOLUME/schedule.csv\"",
        "sync",
        "",
        "echo \"Copied ${SOURCE} to ${VOLUME}/schedule.csv\"",
        "echo 'Eject the card cleanly before removing it.'",
        "",
    ]

    ONE_CARD_SD_COPY_SCRIPT.write_text("\n".join(lines), encoding="utf-8")
    ONE_CARD_SD_COPY_SCRIPT.chmod(0o755)


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
                "new_firmware": tx_id in {"TXK", "TXL"},
                "new_sd_card": tx_id in {"TXK", "TXL"},
            }
        )

    write_summary(rows)
    write_one_card_sd_copy_script(rows)

    print("Prepared Run 035 physical-prep artifacts")
    print()
    print(f"Wrote: {SUMMARY_JSON}")
    print(f"Wrote: {SUMMARY_CSV}")
    print(f"Wrote: {ONE_CARD_SD_COPY_SCRIPT}")
    print()
    print("Firmware/card table:")
    for row in rows:
        print(
            f"  {row['tx_id']}/{row['node_id']}: "
            f"{row['firmware_sketch']}, "
            f"RUN_ID={row['run_id']}, "
            f"offset={row['startup_offset_ms']} ms, "
            f"sd={row['sd_volume']}"
        )


if __name__ == "__main__":
    main()
