#!/usr/bin/env bash
set -euo pipefail

echo 'Copying Run 034 SD schedules to mounted transmitter cards'
echo 'This removes old schedule.csv/SCHEDULE.CSV before copying the Run 034 schedule.'

echo 'Preparing TXA card: /Volumes/LORA_TXA'
test -d '/Volumes/LORA_TXA'
rm -f '/Volumes/LORA_TXA/schedule.csv' '/Volumes/LORA_TXA/SCHEDULE.CSV'
cp 'traces/run034_sd_txa_schedule.csv' '/Volumes/LORA_TXA/schedule.csv'
sync

echo 'Preparing TXB card: /Volumes/LORA_TXB'
test -d '/Volumes/LORA_TXB'
rm -f '/Volumes/LORA_TXB/schedule.csv' '/Volumes/LORA_TXB/SCHEDULE.CSV'
cp 'traces/run034_sd_txb_schedule.csv' '/Volumes/LORA_TXB/schedule.csv'
sync

echo 'Preparing TXC card: /Volumes/LORA_TXC'
test -d '/Volumes/LORA_TXC'
rm -f '/Volumes/LORA_TXC/schedule.csv' '/Volumes/LORA_TXC/SCHEDULE.CSV'
cp 'traces/run034_sd_txc_schedule.csv' '/Volumes/LORA_TXC/schedule.csv'
sync

echo 'Preparing TXD card: /Volumes/LORA_TXD'
test -d '/Volumes/LORA_TXD'
rm -f '/Volumes/LORA_TXD/schedule.csv' '/Volumes/LORA_TXD/SCHEDULE.CSV'
cp 'traces/run034_sd_txd_schedule.csv' '/Volumes/LORA_TXD/schedule.csv'
sync

echo 'Preparing TXE card: /Volumes/LORA_TXE'
test -d '/Volumes/LORA_TXE'
rm -f '/Volumes/LORA_TXE/schedule.csv' '/Volumes/LORA_TXE/SCHEDULE.CSV'
cp 'traces/run034_sd_txe_schedule.csv' '/Volumes/LORA_TXE/schedule.csv'
sync

echo 'Preparing TXF card: /Volumes/LORA_TXF'
test -d '/Volumes/LORA_TXF'
rm -f '/Volumes/LORA_TXF/schedule.csv' '/Volumes/LORA_TXF/SCHEDULE.CSV'
cp 'traces/run034_sd_txf_schedule.csv' '/Volumes/LORA_TXF/schedule.csv'
sync

echo 'Preparing TXG card: /Volumes/LORA_TXG'
test -d '/Volumes/LORA_TXG'
rm -f '/Volumes/LORA_TXG/schedule.csv' '/Volumes/LORA_TXG/SCHEDULE.CSV'
cp 'traces/run034_sd_txg_schedule.csv' '/Volumes/LORA_TXG/schedule.csv'
sync

echo 'Preparing TXH card: /Volumes/LORA_TXH'
test -d '/Volumes/LORA_TXH'
rm -f '/Volumes/LORA_TXH/schedule.csv' '/Volumes/LORA_TXH/SCHEDULE.CSV'
cp 'traces/run034_sd_txh_schedule.csv' '/Volumes/LORA_TXH/schedule.csv'
sync

echo 'Preparing TXI card: /Volumes/LORA_TXI'
test -d '/Volumes/LORA_TXI'
rm -f '/Volumes/LORA_TXI/schedule.csv' '/Volumes/LORA_TXI/SCHEDULE.CSV'
cp 'traces/run034_sd_txi_schedule.csv' '/Volumes/LORA_TXI/schedule.csv'
sync

echo 'Preparing TXJ card: /Volumes/LORA_TXJ'
test -d '/Volumes/LORA_TXJ'
rm -f '/Volumes/LORA_TXJ/schedule.csv' '/Volumes/LORA_TXJ/SCHEDULE.CSV'
cp 'traces/run034_sd_txj_schedule.csv' '/Volumes/LORA_TXJ/schedule.csv'
sync
