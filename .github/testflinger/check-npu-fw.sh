#!/bin/bash -e

set -e
fw_search_path=$(sudo cat /sys/module/firmware_class/parameters/path)
echo "[INFO]: fw_search_path: ${fw_search_path}"
echo "[INFO]: $(snap services intel-npu-driver.load-npu-firmware)"
echo "[INFO]: $(sudo snap logs intel-npu-driver.load-npu-firmware)"
if [ -z "${fw_search_path}" ]; then
  >&2 echo "Test error: Firmware search path not updated."
  exit 1
fi
echo "Checking for firmware in the expected path ${fw_search_path}/intel/vpu"
ls "${fw_search_path}"/intel/vpu/ | grep ".*.bin$"
echo "Test success: Found .bin file(s) in the expected path."
