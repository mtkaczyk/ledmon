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

        def run_ledctl_command(self, use_short_test_flag, parameters):
                test_flag = "-T" if use_short_test_flag == True else "--test"
                cmd = (self.ledctl_bin + " " + test_flag + " " + parameters).split()
                return subprocess.run(cmd)

        @pytest.mark.parametrize("valid_mode_commands", [
                "-h",
                "--help",
                "-v",
                "--version",
                "-L",
                "--list-controllers",
                "-P -c vmd",
                "--list-slots --controller-type=vmd",
                "-G -c vmd -d /dev/nvme0n1",
                "--get-slot --controller-type=vmd --device=/dev/nvme0n1",
                "-G -c vmd -p 1",
                "--get-slot --controller-type=vmd --slot=1",
        ],)
        def test_parameters_are_valid_short_test_flag_first(self, valid_mode_commands):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(True, valid_mode_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE
                # test using long test flag format "--test"
                result = self.run_ledctl_command(False, valid_mode_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE


        @pytest.mark.parametrize("valid_ibpi_commands", [
                "normal=/dev/nvme0n1",
                "normal=/dev/nvme0n1 -x",
                "normal=/dev/nvme0n1 --listed-only",
                "normal=/dev/nvme0n1 -l /var/log/ledctl.log",
                "normal=/dev/nvme0n1 --log=/var/log/ledctl.log",
                "normal=/dev/nvme0n1 --log-level=all",
                "normal=/dev/nvme0n1 --all",
                "-x normal={ /dev/nvme0n1 }",
                "locate=/dev/nvme0n1 rebuild={ /sys/block/sd[a-b] }",
                "off={ /dev/sda /dev/sdb }",
                "locate=/dev/sda,/dev/sdb,/dev/sdc"

        ],)
        def test_ibpi_parameters_are_valid_short_test_flag_first(self, valid_ibpi_commands):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(True, valid_ibpi_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE
                # test using long test flag format "--test"
                result = self.run_ledctl_command(False, valid_ibpi_commands)
                assert result.returncode == self.SUCCESS_EXIT_CODE

        @pytest.mark.parametrize("invalid_modes_commands_usage", [
                "-l /var/log/ledctl.log", # log file should be used with valid command
                "--log=/var/log/ledctl.log", # log file should be used with valid command
                "--log-level=all", #  log level should be used with valid command
                "-x", # listed-only can be used only with ibpi command
                "--listed-only", # listed-only can be used only with ibpi command
        ],)
        def test_modes_parameters_invalid_short_test_flag_first(self, invalid_modes_commands_usage):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(True, invalid_modes_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE
                # test using long test flag format "--test"
                result = self.run_ledctl_command(False, invalid_modes_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE

        @pytest.mark.parametrize("invalid_ibpi_commands_usage", [
                "normal=/dev/nvme0n1 -G -c vmd --slot=2", # mix IBPI set LED state with get slot state
                "normal=/dev/nvme0n1 --information", # invalid flag
                "normal=/dev/nvme0n1 -L", # mix IBPI set LED state with list controllers
                "--listed-only { locate={ /dev/nvme0n1 } } -x rebuild=/dev/nvme1n1 s d }",
                "--listed-only { locate={ /dev/nvme0n1 } -x rebuild=/dev/nvme1n1 }"
          ],)
        def test_ibpi_parameters_invalid_short_test_flag_first(self, invalid_ibpi_commands_usage):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(True, invalid_ibpi_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE
                # test using long test flag format "--test"
                result = self.run_ledctl_command(False, invalid_ibpi_commands_usage)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE

        @pytest.mark.parametrize("invalid_parameters", [
                "-L a",
                "a b c -L d e f",
                "-L test"
        ],)
        def test_invalid_parameters(self, invalid_parameters):
                self.verify_if_flag_is_enabled()
                # test using short test flag format "-T"
                result = self.run_ledctl_command(True, invalid_parameters)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE
                # test using long test flag format "--test"
                result = self.run_ledctl_command(False, invalid_parameters)
                assert result.returncode == self.CMDLINE_ERROR_EXIT_CODE
