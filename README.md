# Intel NPU Driver Snap

Snap recipe for the [Intel NPU Driver](https://github.com/intel/linux-npu-driver/). This snap is designed to be a producer snap providing NPU (neural processing unit) firmware and user-space libraries (including the user mode driver and NPU compiler) for consumption by application snaps via the [content interface](https://snapcraft.io/docs/content-interface).

## Instructions for building and running the snap

### Building and installing the snap locally

**Important note**: run `snapcraft` in the current directory
in order for the install hook to get integrated with the
snap correctly.

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

### Loading new NPU firmware

Now connect the snap to the `kernel-firmware-control` snap interface,
which allows the snap to access a file in /sys for customizing the
kernel's firmware search path:

```
sudo snap connect intel-npu-driver:kernel-firmware-control
```

Now run the following to customize the search path:

```
sudo intel-npu-driver.set-firmware-path
```

The expected output is something like the following:

```
Firmware search path is set to: /var/snap/intel-npu-driver/x1
```

Now reload the `intel_vpu` kernel module to load the updated firmware:

```
sudo rmmod intel_vpu
sudo modprobe intel_vpu
```

Verify it's running and loaded correctly with:

```
lsmod | grep intel_vpu
sudo dmesg | grep intel_vpu
```

### Running the vpu-umd-test application

First connect to the `custom-device` interface, which allows access the
NPU device node on the host:

```
sudo snap connect intel-npu-driver:intel-npu-plug intel-npu-driver:intel-npu-slot
```

If you have not done so already, ensure the following
are performed in oder to set up non-root access to the
NPU device:

```
sudo usermod -a -G render $USER # log out and log back in
```

If this is your first run, or if you re-loaded the `intel_vpu` driver,
then you'll also need to perform the following:

```
sudo chown root:render /dev/accel/accel0
sudo chmod g+rw /dev/accel/accel0
```

Create input for tests. Note, the input must be stored in a special directory
that is accessible both inside and outside the snap.

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
