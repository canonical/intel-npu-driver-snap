#!/usr/bin/env python3
import sys
import platform
import argparse
import re
from typing import Tuple

def parse_version(version_str: str) -> Tuple[int, ...]:
    try:
        # Find all sequences of one or more digits in the string
        numbers = re.findall(r'\d+', version_str)
        if not numbers:
            raise ValueError("No version numbers found in the string.")
        
        # Convert the list of number strings to a tuple of integers
        return tuple(map(int, numbers))
    except (ValueError, TypeError):
        print("state: unsupported")
        sys.exit(1)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check if the current kernel version is at least the required version."
    )
    parser.add_argument(
        "required_version", 
        help="The minimum required kernel version."
    )
    args = parser.parse_args()

    current_version_str = platform.release()
    
    current_version = parse_version(current_version_str)
    required_version = parse_version(args.required_version)
    
    if current_version >= required_version:
        print("state: supported")
        return 0
    else:
        print("state: unsupported")
        return 1

if __name__ == "__main__":
    sys.exit(main())
