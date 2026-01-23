# Checkbox Provider for Intel NPU Driver Snap

This directory contains the Checkbox NPU Provider, including the snap recipe for building the snap and integrating with the Checkbox snap. The test plan runs the NPU user mode driver validation tool.

## Installation

```
sudo snap install --classic snapcraft
sudo snap install checkbox24
lxd init --auto
git clone https://github.com/canonical/intel-npu-driver-snap.git
cd intel-npu-driver-snap/checkbox
snapcraft
sudo snap install --dangerous --classic ./checkbox-npu_1.0.0_amd64.snap
```

## Automated run

```
checkbox-npu.test-runner-automated
```

## Manual run

```
checkbox-npu.test-runner
```
