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

## Installing test dependencies

```
checkbox-npu.install-full-deps
```

Note this will NOT install the `intel-npu-driver` snap by default. This is by design as typically tests will be run on a modified version of the snap built and installed locally. To install the latest version from the `latest/beta` channel in the Snap Store use:

```
checkbox-npu.install-full-deps --install_from_store
```

## Automated run

```
checkbox-npu.test-runner-automated
```

## Manual run

```
checkbox-npu.test-runner
```
