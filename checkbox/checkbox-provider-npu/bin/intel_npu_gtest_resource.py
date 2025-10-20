#!/usr/bin/env python3
import os
import subprocess
import sys


def print_resource_line(key: str, value: str) -> None:
    print(f"{key}: {value}")


def print_as_resource(d: dict) -> None:
    for k, v in d.items():
        print_resource_line(k, v)

    print("")


def main() -> int:
    config_path = os.path.join(os.environ.get('HOME'),
                               "snap/intel-npu-driver/current/basic.yaml")
    gtest_output = subprocess.run(["intel-npu-driver.npu-umd-test", "-l",
                                   "--config", config_path],
                                  capture_output=True, text=True)

    for line in gtest_output.stdout.strip().splitlines():
        if '.' in line:
            category, test_name = line.split('.', 1)

            extra_flags = []
            metric_streamer_allowed_states = ["supported", "unsupported"]
            ivpu_bo_create_allowed_states = ["supported", "unsupported"]
            known_failure = False

            if category.startswith("ZeInit"):
                extra_flags.append("--ze-init-tests")

            if category.startswith("Metric"):
                metric_streamer_allowed_states = ["supported"]

            if category in ["CompilerInDriverWithProfiling",
                            "CommandMemoryFill"] or\
                    line == "ImmediateCmdList.FillCopyUsingBarriers":
                ivpu_bo_create_allowed_states = ["supported"]

            # Device.GetZesEngineGetActivity:
            #   No sysfs access for NPU activity data
            # ExternalMemoryZe.GpuZeFillToNpuZeCopy:
            #   No GPU support for test
            # ExternalMemoryZe.NpuZeFillToGpuZeCopy:
            #   No GPU support for test
            # ExternalMemoryDmaHeap.DmaHeapToNpu/2KB:
            #   requires access to /dev/dma_heap/system
            # ExternalMemoryDmaHeap.DmaHeapToNpu/16MB:
            #   requires access to /dev/dma_heap/system
            # ExternalMemoryDmaHeap.DmaHeapToNpu/255MB:
            #   requires access to /dev/dma_heap/system
            if test_name.find("Gpu") != -1 or \
                    category.find("DmaHeap") != -1 or \
                    line == "Device.GetZesEngineGetActivity":
                known_failure = True

            if not known_failure:
                print_as_resource({
                    "name": test_name,
                    "category": category,
                    "extra_flags": " ".join(extra_flags),
                    "metric_streamer_allowed_states":
                        metric_streamer_allowed_states,
                    "ivpu_bo_create_allowed_states":
                        ivpu_bo_create_allowed_states,
                    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
