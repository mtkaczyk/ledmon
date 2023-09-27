# Intel(R) Enclosure LED Utilities
# Copyright (C) 2009-2023 Intel Corporation.

# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.

# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.

import pytest
import subprocess

class TestParameters():
        ledctl_bin = "sudo src/ledctl/ledctl"
        SUCCESS_EXIT_CODE = 0
        CMDLINE_ERROR_EXIT_CODE = 35

        def verify_if_flag_is_enabled(self):
                cmd = (self.ledctl_bin + " -T").split()
                result = subprocess.run(cmd)
                assert result.returncode == self.SUCCESS_EXIT_CODE,\
                        "Test flag is disabled. Please add configure option \"--enable-test\"."

        def run_ledctl_command(self, parameters):
                cmd = (self.ledctl_bin + " " + parameters).split()
                return subprocess.run(cmd)

        @pytest.mark.parametrize("valid_mode_commands", [
                "-h",
                "--help",
                "-v",
                "--version",
                "-L -T",
                "--list-controllers -T",
                "-P -c vmd -T",
                "--list-slots --controller-type=vmd -T",
                "-G -c vmd -d /dev/nvme0n1 -T",
                "--get-slot --controller-type=vmd --device=/dev/nvme0n1 -T",
                "-G -c vmd -p 1 -T",
                "--get-slot --controller-type=vmd --slot=1 -T",
        ],)
        def test_parameters_are_valid_short_test_flag_first(self, valid_mode_commands):
                self.verify_if_flag_is_enabled()

                result = self.run_ledctl_command(valid_mode_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE


        @pytest.mark.parametrize("valid_ibpi_commands", [
                "normal=/dev/nvme0n1 -T",
                "normal=/dev/nvme0n1 -x -T",
                "normal=/dev/nvme0n1 --listed-only -T",
                "normal=/dev/nvme0n1 -l /var/log/ledctl.log -T",
                "normal=/dev/nvme0n1 --log=/var/log/ledctl.log -T",
                "normal=/dev/nvme0n1 --log-level=all -T",
                "normal=/dev/nvme0n1 --all -T",
                "-x normal={ /dev/nvme0n1 } -T",
                "locate=/dev/nvme0n1 rebuild={ /sys/block/sd[a-b] } -T",
                "off={ /dev/sda /dev/sdb } -T",
                "locate=/dev/sda,/dev/sdb,/dev/sdc -T"

        ],)
        def test_ibpi_parameters_are_valid_short_test_flag_first(self, valid_ibpi_commands):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(valid_ibpi_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE

        @pytest.mark.parametrize("invalid_modes_commands_usage", [
                "-l /var/log/ledctl.log -T", # log file should be used with valid command
                "--log=/var/log/ledctl.log -T", # log file should be used with valid command
                "--log-level=all -T", #  log level should be used with valid command
                "-x -t", # listed-only can be used only with ibpi command
                "--listed-only -T", # listed-only can be used only with ibpi command
        ],)
        def test_modes_parameters_invalid_short_test_flag_first(self, invalid_modes_commands_usage):
                self.verify_if_flag_is_enabled()
                result = self.run_ledctl_command(invalid_modes_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE

        @pytest.mark.parametrize("invalid_ibpi_commands_usage", [
                "normal=/dev/nvme0n1 -G -c vmd --slot=2 -T", # mix IBPI set LED state with get slot state
                "normal=/dev/nvme0n1 --information -T", # invalid flag
                "normal=/dev/nvme0n1 -L -T", # mix IBPI set LED state with list controllers
                "--listed-only { locate={ /dev/nvme0n1 } } -x rebuild=/dev/nvme1n1 s d } -T",
                "--listed-only { locate={ /dev/nvme0n1 } -x rebuild=/dev/nvme1n1 } -T"
          ],)
        def test_ibpi_parameters_invalid_short_test_flag_first(self, invalid_ibpi_commands_usage):
                self.verify_if_flag_is_enabled()
                result = self.run_ledctl_command( invalid_ibpi_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE


        @pytest.mark.parametrize("invalid_parameters", [
                "-L a -T",
                "a b c -L d e f -T",
                "-L test -T"
        ],)
        def test_invalid_parameters(self, invalid_parameters):
                self.verify_if_flag_is_enabled()
                result = self.run_ledctl_command(invalid_parameters)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE

