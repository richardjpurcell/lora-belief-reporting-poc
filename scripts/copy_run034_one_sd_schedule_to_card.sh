#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 TXA [mounted_volume_path]"
  echo
  echo "Examples:"
  echo "  $0 TXA"
  echo "  $0 TXI /Volumes/LORA_TXI"
  exit 1
fi

TX="$1"
VOLUME="${2:-/Volumes/LORA_${TX}}"

case "$TX" in
  TXA) SRC="traces/run034_sd_txa_schedule.csv" ;;
  TXB) SRC="traces/run034_sd_txb_schedule.csv" ;;
  TXC) SRC="traces/run034_sd_txc_schedule.csv" ;;
  TXD) SRC="traces/run034_sd_txd_schedule.csv" ;;
  TXE) SRC="traces/run034_sd_txe_schedule.csv" ;;
  TXF) SRC="traces/run034_sd_txf_schedule.csv" ;;
  TXG) SRC="traces/run034_sd_txg_schedule.csv" ;;
  TXH) SRC="traces/run034_sd_txh_schedule.csv" ;;
  TXI) SRC="traces/run034_sd_txi_schedule.csv" ;;
  TXJ) SRC="traces/run034_sd_txj_schedule.csv" ;;
  *)
    echo "Unknown TX: $TX"
    echo "Expected TXA through TXJ"
    exit 1
    ;;
esac

if [ ! -f "$SRC" ]; then
  echo "Missing source schedule: $SRC"
  exit 1
fi

if [ ! -d "$VOLUME" ]; then
  echo "Mounted volume not found: $VOLUME"
  exit 1
fi

echo "Preparing $TX card at $VOLUME"
echo "Source: $SRC"
echo "Destination: $VOLUME/schedule.csv"

rm -f "$VOLUME/schedule.csv" "$VOLUME/SCHEDULE.CSV"
cp "$SRC" "$VOLUME/schedule.csv"
sync

echo
echo "Copied schedule:"
ls -l "$VOLUME/schedule.csv"

echo
echo "Row count:"
wc -l "$VOLUME/schedule.csv"

echo
echo "Done. Eject the card cleanly before removing it."
