#!/bin/bash -e

usermod -a -G render ubuntu
# Newer versions of Ubuntu ship Udev rules which handle this,
# but 22.04 does not
chown root:render /dev/accel/accel0
chmod g+rw /dev/accel/accel0

echo
echo "========= Checkbox NPU ========="
echo "====== DEVICE KERNEL INFO ======"
echo
uname -a
echo
echo "================================"
echo
