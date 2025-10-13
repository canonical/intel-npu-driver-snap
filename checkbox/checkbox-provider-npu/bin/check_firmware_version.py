#!/usr/bin/env python3
import sys
import re
import subprocess
from pathlib import Path
from typing import Optional, List

FIRMWARE_SEARCH_DIR = Path("/snap/intel-npu-driver/current/lib/firmware/updates/intel/vpu")
VERSION_PATTERN = re.compile(r"^(\d{8}\*|[A-Z][a-z]{2}\s+\d{1,2}\s+\d{4}\*).*")

def get_active_firmware_line() -> Optional[str]:
    try:
        result = subprocess.run(
            ['sudo', 'dmesg'],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        all_lines = result.stdout.splitlines()

        matching_lines = [line for line in all_lines if "Firmware: intel/vpu" in line]

        if not matching_lines:
            print("Error: No 'intel_vpu' firmware logs found in dmesg.", file=sys.stderr)
            return None

        return matching_lines[-1]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: Could not execute 'sudo dmesg'.\n   {e}", file=sys.stderr)
        return None

def find_version_in_file(filepath: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ['sudo', 'strings', filepath],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        for line in result.stdout.splitlines():
            if VERSION_PATTERN.match(line):
                return line # Return the first match found
    except (subprocess.CalledProcessError, FileNotFoundError):
        # This can happen with corrupted files or if 'strings' isn't installed
        return None
    return None

def main() -> int:
    active_firmware_line = get_active_firmware_line()
    if not active_firmware_line:
        return 1

    if not FIRMWARE_SEARCH_DIR.is_dir():
        print(f"Error: Firmware directory not found at '{FIRMWARE_SEARCH_DIR}'", file=sys.stderr)
        return 1

    for filepath in FIRMWARE_SEARCH_DIR.iterdir():
        if filepath.is_file() and filepath.suffix == '.bin':
            driver_version = find_version_in_file(filepath)

            if driver_version and driver_version in active_firmware_line:
                print("\nTest success: Loaded NPU firmware version matches a file from the snap.")
                print(f"   Matching Version: {driver_version}")
                return 0

    print("\nTest failure: The loaded firmware does not match any version in the snap files.", file=sys.stderr)
    print(f"   Loaded dmesg line contains: '{active_firmware_line}'", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
