#!/usr/bin/env python3
import subprocess, os, sys

def print_resource_line(key: str, value: str):
    print(f"{key}: {value}")

def print_as_resource(d: dict):
    for k, v in d.items():
        print_resource_line(k, v)

    print("")

def main() -> int:
    gtest_output = subprocess.run(["intel-npu-driver.npu-umd-test", "-l",
                                   "--config", os.path.join(os.environ.get('HOME'),
                                                            "snap/intel-npu-driver/current/basic.yaml")],
                                  capture_output=True, text=True)
    
    for line in gtest_output.stdout.strip().splitlines():
        if '.' in line:
            category, test_name = line.split('.', 1)
    
            if category.startswith("ZeInit"):
                use_serial = "-I"
            else:
                use_serial = "-S"
    
            print_as_resource({
                "name": test_name,
                "category": category,
                "use_serial": use_serial
                })

if __name__ == "__main__":
    sys.exit(main())
