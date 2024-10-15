# Intel NPU Driver Snap

Snap recipe for the [Intel NPU Driver](https://github.com/intel/linux-npu-driver/). This snap is designed to be a producer snap providing NPU (neural processing unit) firmware, char device node access, and user-space libraries (including the user mode driver and NPU compiler) for consumption by application snaps. It exposes slots for consumer snaps to connect to (see below) but also provides firmware binary blobs for the NPU device and packages an app for validating the user space driver (`vpu-umd-test`).

## Host OS Support

### Meteor Lake

The [`vpu-umd-test` user mode driver validation tool](#running-the-vpu-umd-test-application) is used to validate the snap with the following host OS + kernel on a [Intel Core Ultra 7 155H](https://www.intel.com/content/www/us/en/products/sku/236847/intel-core-ultra-7-processor-155h-24m-cache-up-to-4-80-ghz/specifications.html).

| Host OS | Kernel Version | NPU Kernel Driver Support | Test Results | Comments |
| ----- | :--: | :----------------: | :------------: | :------------------------------: |
| 22.04 | 5.15 | :x:                | N/A            | Standard 22.04 kernel            |
| 22.04 | 6.8  | :white_check_mark: | 184/199 passed | Hardware enablement (HWE) kernel |
| 24.04 | 6.8  | :white_check_mark: | 184/199 passed | Standard 24.04 kernel            |
| 24.10 | 6.11 | :white_check_mark: | 190/199 passed | Proposed 24.10 kernel            |

Skipped tests on kernel 6.8 and lower only:

- Metric streamer feature missing from `intel_vpu` kernel module (6 tests)

Skipped tests common across all host OS and kernel versions:

- GPU driver not present (2 tests)
- DMA capabilities require tests to be run as root (3 tests)
- Compiler in driver tests under investigation (3 tests)
- Command queue priority under investigation (1 test)

## Instructions for building and running the snap

### Building and installing the snap locally

**Important note**: run `snapcraft` in the current directory in order for the install hook to get integrated with the snap correctly.

Build the snap:

```
snapcraft
```

```
sudo snap install --dangerous ./intel-npu-driver_*_amd64.snap
```

Note that this triggers an install hook that copies the firmware
binary blobs to /var/snap/intel-npu-driver/current so that they
are accessible to the kernel driver running on the host.

### Snap slots

* **intel-npu**: provides access to the NPU device node on the host
* **npu-libs**: provides access to NPU libs, namely the NPU user mode driver with compiler

An example snippet for a consuming app's `snapcraft.yaml` may look like:

```yaml
plugs:
  intel-npu:
    interface: custom-device
    custom-device: intel-npu-device
  npu-libs:
    interface: content
    content: npu-libs-2404
    target: $SNAP/usr/lib/npu-libs-2404

environment:
  LD_LIBRARY_PATH: $SNAP/usr/lib/npu-libs-2404:$LD_LIBRARY_PATH

apps:
  npu-enabled-app:
    command: ...
    plugs:
      - intel-npu
      - npu-libs
```

### Loading new NPU firmware

After installing the snap, check that the firmware search path was updated with:

```
sudo cat /sys/module/firmware_class/parameters/path
```

The expected output is something like:

```
/var/snap/intel-npu-driver/x1
```

Verify the `intel_vpu` kernel module is running and loaded the current firmware:

```
sudo dmesg | grep intel_vpu
```

Typical output:

```
[    4.706576] intel_vpu 0000:00:0b.0: enabling device (0000 -> 0002)
[    4.714294] intel_vpu 0000:00:0b.0: [drm] Firmware: intel/vpu/vpu_37xx_v0.0.bin, version: 20230726*MTL_CLIENT_SILICON-release*2101*ci_tag_mtl_pv_vpu_rc_20230726_2101*648a666b8b9
[    4.796516] [drm] Initialized intel_vpu 1.0.0 20230117 for 0000:00:0b.0 on minor 0
[   11.084478] intel_vpu 0000:00:0b.0: [drm] Firmware: intel/vpu/vpu_37xx_v0.0.bin, version: 20240726*MTL_CLIENT_SILICON-release*0004*ci_tag_ud202428_vpu_rc_20240726_0004*e4a99ed6b3e
[   11.211998] [drm] Initialized intel_vpu 1.0.0 20230117 for 0000:00:0b.0 on minor 0
```

In this example output the system initially boots with the firmware that ships with OS before reloading more recent firmware provided by the snap. Check the [upstream repo from Intel](https://github.com/intel/linux-npu-driver/releases) for the expected firmware version for your platform.

### Running the vpu-umd-test application

To allow non-root access to the NPU device, first ensure the appropriate user is in the `render` Unix group:

```
sudo usermod -a -G render $USER # log out and log back in
```

Next apply the appropriate permissions on the device node. This is required each time the `intel_vpu` driver is reloaded, e.g. when the snap is first installed or following a reboot.

```
sudo chown root:render /dev/accel/accel0
sudo chmod g+rw /dev/accel/accel0
```

Create input for tests. Here we store input in a special directory that is accessible both inside and outside the snap. This directory is created the first time you run the application. This is not a strict requirement for consuming snaps, for example a consuming snap may allow access to a user's home directory through the [home interface](https://snapcraft.io/docs/home-interface).

```
intel-npu-driver.vpu-umd-test --help
```

Now move into the special directory and create the input:

```
cd $HOME/snap/intel-npu-driver/current
mkdir -p models/add_abc
curl -o models/add_abc/add_abc.xml https://raw.githubusercontent.com/openvinotoolkit/openvino/master/src/core/tests/models/ir/add_abc.xml
touch models/add_abc/add_abc.bin
curl -o basic.yaml https://raw.githubusercontent.com/intel/linux-npu-driver/v1.6.0/validation/umd-test/configs/basic.yaml
```

Finally run the application:

```
intel-npu-driver.vpu-umd-test --config=basic.yaml
```
