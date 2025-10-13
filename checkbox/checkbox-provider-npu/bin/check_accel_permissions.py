#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from typing import Optional

def find_npu_device_path() -> Optional[Path]:
    base_sys_path = Path("/sys/class/accel")
    if not base_sys_path.is_dir():
        return None

    for device_dir in base_sys_path.iterdir():
        try:
            # Check if the driver's name is 'intel_vpu'
            driver_path = device_dir / "device" / "driver"
            if "intel_vpu" in os.path.basename(os.readlink(driver_path)):
                device_path = Path("/dev/accel") / device_dir.name
                if device_path.exists():
                    return device_path
        except (IOError, FileNotFoundError):
            # Ignore directories that don't match the expected structure
            continue
    return None

def print_permission_error(device_path: Path):
    user = os.getenv('USER', 'your_user')
    print(f"Test Failure: User lacks required permissions for {device_path}", file=sys.stderr)
    print("   Please ensure you are part of the 'render' group and the device has the correct ownership.", file=sys.stderr)
    print("   Suggested commands:", file=sys.stderr)
    print(f"   1. sudo usermod -a -G render {user}  (then log out and back in)", file=sys.stderr)
    print(f"   2. sudo chown root:render {device_path} && sudo chmod g+rw {device_path}", file=sys.stderr)
    
def main() -> int:
    npu_device = find_npu_device_path()

    if not npu_device:
        print("Test Failure: Could not find an Intel NPU device in /sys/class/accel.", file=sys.stderr)
        return 1

    # Check for read and write permissions
    has_read_perm = os.access(npu_device, os.R_OK)
    has_write_perm = os.access(npu_device, os.W_OK)

    if has_read_perm and has_write_perm:
        return 0
    else:
        print_permission_error(npu_device)
        return 1

if __name__ == "__main__":
    sys.exit(main())
