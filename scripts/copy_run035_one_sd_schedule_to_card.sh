#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo 'Usage: $0 <TX_ID> [mounted_volume_path]' >&2
  echo 'Valid TX_ID values: TXA TXB TXC TXD TXE TXF TXG TXH TXI TXJ TXK TXL' >&2
  exit 2
fi

TX_ID="$1"
MOUNT_OVERRIDE="${2:-}"

case "$TX_ID" in
  TXA)
    SOURCE='traces/run035_sd_txa_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXA'
    ;;
  TXB)
    SOURCE='traces/run035_sd_txb_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXB'
    ;;
  TXC)
    SOURCE='traces/run035_sd_txc_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXC'
    ;;
  TXD)
    SOURCE='traces/run035_sd_txd_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXD'
    ;;
  TXE)
    SOURCE='traces/run035_sd_txe_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXE'
    ;;
  TXF)
    SOURCE='traces/run035_sd_txf_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXF'
    ;;
  TXG)
    SOURCE='traces/run035_sd_txg_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXG'
    ;;
  TXH)
    SOURCE='traces/run035_sd_txh_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXH'
    ;;
  TXI)
    SOURCE='traces/run035_sd_txi_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXI'
    ;;
  TXJ)
    SOURCE='traces/run035_sd_txj_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXJ'
    ;;
  TXK)
    SOURCE='traces/run035_sd_txk_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXK'
    ;;
  TXL)
    SOURCE='traces/run035_sd_txl_schedule.csv'
    DEFAULT_VOLUME='/Volumes/LORA_TXL'
    ;;
  *)
    echo 'Unknown TX_ID. Valid values: TXA TXB TXC TXD TXE TXF TXG TXH TXI TXJ TXK TXL' >&2
    exit 2
    ;;
esac

VOLUME="${MOUNT_OVERRIDE:-$DEFAULT_VOLUME}"

echo "Preparing Run 035 SD schedule for ${TX_ID}"
echo "Source: ${SOURCE}"
echo "Mounted volume: ${VOLUME}"

test -f "$SOURCE"
test -d "$VOLUME"

rm -f "$VOLUME/schedule.csv" "$VOLUME/SCHEDULE.CSV"
cp "$SOURCE" "$VOLUME/schedule.csv"
sync

echo "Copied ${SOURCE} to ${VOLUME}/schedule.csv"
echo 'Eject the card cleanly before removing it.'
