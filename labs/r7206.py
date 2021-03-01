#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Script.
To run this lab:
* Start GNS3 by executing "./gn3_run.sh" in a Terminal window.
* Select Lab00 from the Projects library.
* Start all devices.

If Lab00 does not exist, follow the instructions in DEMO.md to create the lab.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import logging
import sys
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="labs.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


class Ramon7206(object):
    @property
    def device_ip_address(self):
        return self._device_ip_address

    @property
    def subnet_mask(self):
        return self._subnet_mask

    @property
    def start_up_config_file(self):
        return self._start_up_config_file

    def __init__(self, start_up_config_file, device_ip_address, subnet_mask):
        self._device_ip_address = device_ip_address
        self._subnet_mask = subnet_mask
        self._start_up_config_file = start_up_config_file

    def run(self, ui, **kwargs):
        try:
            print("Hello from Cisco Ramon!")
            self._connect_to_device()
        except pexpect.exceptions.ExceptionPexpect:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            ui.error("Type {0}: {1} in {2} at line {3}.".format(e_type.__name__,
                                                                ex_value,
                                                                ex_traceback.tb_frame.f_code.co_filename,
                                                                ex_traceback.tb_lineno))
        finally:
            ui.info('Script complete. Have a nice day.')

    def _setup_host(self):
        pass

    def _connect_to_device(self):
        child = pexpect.spawn("telnet {0}".format(self._device_ip_address))

    def _setup_device(self):
        pass

    def _transfer_files(self):
        pass

    def _verify_device_configuration(self):
        pass


class Utility(object):
    @staticmethod
    def is_gns3_running():
        child_result, child_exitstatus = pexpect.run("pgrep gns3server", timeout=30, withexitstatus=True)
        if child_exitstatus == 0:
            return True
        else:
            raise RuntimeError("GNS3 is not running. " +
                               "Please run ./gns3_run.sh to start GNS3 before executing this script.")

    @staticmethod
    def is_the_lab_loaded(host_ip_address):
        child_result, child_exitstatus = pexpect.run("ping -c 4 {0}".format(host_ip_address))
        if child_exitstatus == 0:
            return True
        else:
            raise RuntimeError("Unable to reach device." +
                               "Please load Lab 0 in GNS3 and start all devices before executing this script.")

    def _enable_tftp(self):
        pass

    def _disable_tftp(self):
        pass


class UserInterface(object):
    @staticmethod
    def info(msg):
        print("Message: {0}".format(msg))

    @staticmethod
    def error(msg):
        print("Error: {0}".format(msg))


if __name__ == "__main__":
    HOST_IP_ADDRESS = "192.168.1.100"
    try:
        print("Hello from Cisco Ramon!")

        utility = Utility()
        if utility.is_gns3_running():
            print("GNS3 is running: Check")
        else:
            raise RuntimeError("GNS3 is not running.")
        if utility.is_the_lab_loaded(HOST_IP_ADDRESS):
            print("Lab 0 is loaded and started: Check")
        else:
            raise RuntimeError("Lab is not loaded.")

        if sys.argv[1] and sys.argv[1] == "-x":
            r7206 = Ramon7206(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            r7206 = Ramon7206("192.168.1.100", "192.168.1.10", "255.255.255.0")

        user_interface = UserInterface()
        r7206.run(user_interface)
    except pexpect.exceptions.ExceptionPexpect as ex:
        e_type, e_value, e_traceback = sys.exc_info()
        print("Type {0}: {1} in {2} at line {3}.".format(e_type.__name__,
                                                         e_value,
                                                         e_traceback.tb_frame.f_code.co_filename,
                                                         e_traceback.tb_lineno))
    finally:
        print('Script complete. Have a nice day.')
