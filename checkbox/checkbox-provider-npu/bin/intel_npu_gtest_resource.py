#!/usr/bin/env python3
import os
import subprocess
import sys


def print_as_resource(d: dict) -> None:
    for k, v in d.items():
        print(f"{k}: {v}")

    print("")


def get_extra_flags(category) -> list[str]:
    extra_flags = []
    if category.startswith("ZeInit"):
        extra_flags.append("--ze-init-tests")
    return extra_flags


def get_metric_streamer_allowed_states(category: str) -> list[str]:
    if category.startswith("Metric"):
        return ["supported"]
    else:
        return ["supported", "unsupported"]


def get_ivpu_bo_create_allowed_states(category: str, test_name: str)\
        -> list[str]:
    if category in ["CompilerInDriverWithProfiling", "CommandMemoryFill"] or\
            (category == "ImmediateCmdList" and
             test_name == "FillCopyUsingBarriers"):
        return ["supported"]
    else:
        return ["supported", "unsupported"]


# Known failures:
# - Device.GetZesEngineGetActivity:
#     No sysfs access for NPU activity data
# - ExternalMemoryZe.GpuZeFillToNpuZeCopy:
#     No GPU support for test
# - ExternalMemoryZe.NpuZeFillToGpuZeCopy:
#     No GPU support for test
# - ExternalMemoryDmaHeap.DmaHeapToNpu/2KB:
#     requires access to /dev/dma_heap/system
# - ExternalMemoryDmaHeap.DmaHeapToNpu/16MB:
#     requires access to /dev/dma_heap/system
# - ExternalMemoryDmaHeap.DmaHeapToNpu/255MB:
#     requires access to /dev/dma_heap/system
# - DriverCache.CheckWhenSpaceLessThanAllBlobs:
#     bug in the test, will be fixed in upstream
# - CommandQueuePriority.\
#        executeManyLowPriorityJobsExpectHighPriorityJobCompletesFirst
#     failing on Arrow Lake and Lunar Lake
def is_known_failure(category, test_name):
    if test_name.find("Gpu") != -1 or \
            category.find("DmaHeap") != -1 or \
            (category == "Device" and
             test_name == "GetZesEngineGetActivity") or\
            (category == "DriverCache" and
             test_name == "CheckWhenSpaceLessThanAllBlobs") or\
            (category == "CommandQueuePriority" and
             test_name ==
             "executeManyLowPriorityJobsExpectHighPriorityJobCompletesFirst"):
        return True
    else:
        return False


def main() -> int:
    config_path = os.path.join(os.environ.get('HOME'),
                               "snap/intel-npu-driver/current/basic.yaml")
    gtest_output = subprocess.run(["intel-npu-driver.npu-umd-test", "-l",
                                   "--config", config_path],
                                  capture_output=True, text=True)

    for line in gtest_output.stdout.strip().splitlines():
        if '.' in line:
            category, test_name = line.split('.', 1)

            extra_flags = get_extra_flags(category)
            metric_streamer_allowed_states = \
                get_metric_streamer_allowed_states(category)
            ivpu_bo_create_allowed_states = \
                get_ivpu_bo_create_allowed_states(category, test_name)
            known_failure = is_known_failure(category, test_name)

            print_as_resource({
                "name": test_name,
                "category": category,
                "extra_flags": " ".join(extra_flags),
                "metric_streamer_allowed_states":
                    metric_streamer_allowed_states,
                "ivpu_bo_create_allowed_states":
                    ivpu_bo_create_allowed_states,
                "known_failure": known_failure
                })


if __name__ == "__main__":
    sys.exit(main())
