#!/usr/bin/env python3
import unittest
import io
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import check_accel_permissions

class TestFindNpuDevicePath(unittest.TestCase):
    @patch('os.readlink', return_value='../../bus/pci/drivers/intel_vpu')
    @patch('check_accel_permissions.Path')
    def test_device_found(self, mock_path_class, mock_readlink):
        # Mock that "/sys/class/accel" exists
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = True
        
        # Add accel0 into the folder
        mock_accel0 = MagicMock()
        mock_accel0.name = 'accel0'
        mock_base_path.iterdir.return_value = [mock_accel0]

        # Mock for device_dir / "device" / "driver"
        mock_driver_path = MagicMock()
        mock_accel0.__truediv__.return_value.__truediv__.return_value = mock_driver_path

        # Mock for Path("/dev/accel") / device_dir.name
        mock_dev_base = MagicMock()
        mock_dev_device = MagicMock()
        mock_dev_device.exists.return_value = True
        mock_dev_base.__truediv__.return_value = mock_dev_device

        # Configure mock_path_class to return the correct mock for each path
        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            if path_str == "/dev/accel":
                return mock_dev_base
            return MagicMock() 

        mock_path_class.side_effect = path_side_effect
        
        result = check_accel_permissions.find_npu_device_path()
        self.assertEqual(result, mock_dev_device)

    @patch('check_accel_permissions.Path')
    def test_no_sys_class_accel(self, mock_path_class):
        """Test when the base /sys/class/accel directory doesn't exist."""
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = False

        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            return MagicMock()
        
        mock_path_class.side_effect = path_side_effect

        result = check_accel_permissions.find_npu_device_path()
        
        self.assertIsNone(result)

    @patch('os.readlink', return_value='../../bus/pci/drivers/other_driver')
    @patch('check_accel_permissions.Path')
    def test_wrong_driver(self, mock_path_class, mock_readlink):
        """Test when a device exists but it's not the 'intel_vpu' driver."""
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = True
        
        mock_accel0 = MagicMock()
        mock_accel0.name = 'accel0'
        mock_base_path.iterdir.return_value = [mock_accel0]

        # Mock for device_dir / "device" / "driver"
        mock_driver_path = MagicMock()
        mock_accel0.__truediv__.return_value.__truediv__.return_value = mock_driver_path

        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            return MagicMock() 

        mock_path_class.side_effect = path_side_effect
        
        result = check_accel_permissions.find_npu_device_path()
        
        # Should return None because driver name didn't match
        self.assertIsNone(result)

    @patch('os.readlink', return_value='../../bus/pci/drivers/intel_vpu')
    @patch('check_accel_permissions.Path') # Patches Path *within* the script
    def test_driver_found_but_dev_missing(self, mock_path_class, mock_readlink):
        """Test when the sysfs entry exists, but the /dev/accel node does not."""
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = True
        
        mock_accel0 = MagicMock()
        mock_accel0.name = 'accel0'
        mock_base_path.iterdir.return_value = [mock_accel0]

        # Mock for device_dir / "device" / "driver"
        mock_driver_path = MagicMock()
        mock_accel0.__truediv__.return_value.__truediv__.return_value = mock_driver_path

        mock_dev_base = MagicMock()
        mock_dev_device = MagicMock()
        # Here, the device doesn't exist
        mock_dev_device.exists.return_value = False 
        mock_dev_base.__truediv__.return_value = mock_dev_device

        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            if path_str == "/dev/accel":
                return mock_dev_base
            return MagicMock() 

        mock_path_class.side_effect = path_side_effect
        
        result = check_accel_permissions.find_npu_device_path()
        
        # Should return None because device_path.exists() was false
        self.assertIsNone(result)


    @patch('os.readlink', side_effect=FileNotFoundError)
    @patch('check_accel_permissions.Path')
    def test_malformed_sysfs_entry(self, mock_path_class, mock_readlink):
        """Test when a directory in accel/ lacks the 'device/driver' structure."""
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = True
        
        mock_accel0 = MagicMock()
        mock_accel0.name = 'accel0'
        mock_base_path.iterdir.return_value = [mock_accel0]

        # Mock for device_dir / "device" / "driver"
        mock_driver_path = MagicMock()
        mock_accel0.__truediv__.return_value.__truediv__.return_value = mock_driver_path

        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            return MagicMock() 

        mock_path_class.side_effect = path_side_effect
        
        result = check_accel_permissions.find_npu_device_path()
        
        # Should return None because readlink failed
        self.assertIsNone(result)
        
        # Verify it tried to read the link
        mock_readlink.assert_called_with(mock_driver_path)

    @patch('os.readlink', return_value='../../bus/pci/drivers/intel_vpu')
    @patch('check_accel_permissions.Path')
    def test_multiple_devices_first_missing_dev_second_ok(self, mock_path_class, mock_readlink):
        """Test finding the 2nd device if the 1st /dev node is missing."""
        mock_base_path = MagicMock()
        mock_base_path.is_dir.return_value = True
        
        mock_accel0 = MagicMock()
        mock_accel0.name = 'accel0'
        mock_accel1 = MagicMock()
        mock_accel1.name = 'accel1'
        mock_base_path.iterdir.return_value = [mock_accel0, mock_accel1]

        mock_driver_path0 = MagicMock()
        mock_accel0.__truediv__.return_value.__truediv__.return_value = mock_driver_path0
        mock_driver_path1 = MagicMock()
        mock_accel1.__truediv__.return_value.__truediv__.return_value = mock_driver_path1

        # Mock for Path("/dev/accel") / device_dir.name
        mock_dev_base = MagicMock()
        mock_dev_device0 = MagicMock()
        mock_dev_device0.exists.return_value = False
        mock_dev_device1 = MagicMock()
        mock_dev_device1.exists.return_value = True
        
        def dev_truediv_side_effect(name):
            if name == 'accel0':
                return mock_dev_device0
            if name == 'accel1':
                return mock_dev_device1
            return MagicMock()
        mock_dev_base.__truediv__.side_effect = dev_truediv_side_effect

        def path_side_effect(path_str):
            if path_str == "/sys/class/accel":
                return mock_base_path
            if path_str == "/dev/accel":
                return mock_dev_base
            return MagicMock() 

        mock_path_class.side_effect = path_side_effect
        
        result = check_accel_permissions.find_npu_device_path()
        
        # Check that the correct device path is returned (the SECOND one)
        self.assertEqual(result, mock_dev_device1)
        
        # Verify it checked both driver links
        mock_readlink.assert_any_call(mock_driver_path0)
        mock_readlink.assert_any_call(mock_driver_path1)
        
        # Verify it checked exists() for BOTH /dev nodes
        mock_dev_device0.exists.assert_called_with()
        mock_dev_device1.exists.assert_called_with()


class TestPrintPermissionError(unittest.TestCase):
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch.dict('os.environ', {'USER': 'test_user'})
    def test_prints_to_stderr_with_user(self, mock_stderr):
        """Test that the error message prints correctly with a USER env var."""
        device = Path('/dev/accel1')
        check_accel_permissions.print_permission_error(device)
        
        output = mock_stderr.getvalue()
        self.assertIn("Test Failure: User lacks required permissions", output)
        self.assertIn("sudo usermod -a -G render test_user", output)
        self.assertIn("sudo chown root:render /dev/accel1", output)

    @patch('sys.stderr', new_callable=io.StringIO)
    @patch.dict('os.environ', {}, clear=True)
    def test_prints_to_stderr_no_user(self, mock_stderr):
        """Test that the error message prints correctly using the default user."""
        device = Path('/dev/accele1')
        check_accel_permissions.print_permission_error(device)
        
        output = mock_stderr.getvalue()
        self.assertIn("Test Failure: User lacks required permissions", output)
        # Checks that it fell back to the default 'your_user'
        self.assertIn("sudo usermod -a -G render your_user", output)
        self.assertIn("sudo chown root:render /dev/accele1", output)


class TestMainFunction(unittest.TestCase):
    @patch('check_accel_permissions.print_permission_error')
    @patch('os.access', return_value=True)
    @patch('check_accel_permissions.find_npu_device_path', return_value=Path('/dev/accel0'))
    def test_main_success(self, mock_find_device, mock_access, mock_print_err):
        """Test the main success path: device found, permissions OK."""
        return_code = check_accel_permissions.main()
        
        self.assertEqual(return_code, 0)
        
        # Check os.access was called for both Read and Write
        mock_access.assert_any_call(Path('/dev/accel0'), os.R_OK)
        mock_access.assert_any_call(Path('/dev/accel0'), os.W_OK)
        
        # Error function should not be called
        mock_print_err.assert_not_called()

    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('check_accel_permissions.find_npu_device_path', return_value=None)
    def test_main_device_not_found(self, mock_find_device, mock_stderr):
        """Test the main failure path: no device found."""
        return_code = check_accel_permissions.main()
        
        self.assertEqual(return_code, 1)
        self.assertIn("Could not find an Intel NPU device", mock_stderr.getvalue())

    @patch('check_accel_permissions.print_permission_error')
    @patch('os.access', side_effect=lambda path, mode: False if mode == os.R_OK else True)
    @patch('check_accel_permissions.find_npu_device_path', return_value=Path('/dev/accel0'))
    def test_main_no_read_permission(self, mock_find_device, mock_access, mock_print_err):
        """Test the main failure path: device found, but no read permission."""
        return_code = check_accel_permissions.main()
        
        self.assertEqual(return_code, 1)
        # The permission error function should be called
        mock_print_err.assert_called_once_with(Path('/dev/accel0'))

    @patch('check_accel_permissions.print_permission_error')
    @patch('os.access', side_effect=lambda path, mode: True if mode == os.R_OK else False)
    @patch('check_accel_permissions.find_npu_device_path', return_value=Path('/dev/accel0'))
    def test_main_no_write_permission(self, mock_find_device, mock_access, mock_print_err):
        """Test the main failure path: device found, but no write permission."""
        return_code = check_accel_permissions.main()
        
        self.assertEqual(return_code, 1)
        # The permission error function should be called
        mock_print_err.assert_called_once_with(Path('/dev/accel0'))


if __name__ == "__main__":
    unittest.main()
