#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 00: Simple demo.
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


class Ramon3745(object):
    @property
    def host_ip_address(self):
        return self._host_ip_address

    @host_ip_address.setter
    def host_ip_address(self, host_ip_address):
        pass

    @property
    def device_ip_address(self):
        return self._device_ip_address

    @property
    def subnet_mask(self):
        return self._subnet_mask

    @property
    def start_up_config_file(self):
        return self._start_up_config_file

    def __init__(self, host_ip_address, device_ip_address, subnet_mask, start_up_config_file):
        self._host_ip_address = host_ip_address
        self._device_ip_address = device_ip_address
        self._subnet_mask = subnet_mask
        self._start_up_config_file = start_up_config_file

    def run(self):
        try:
            print("Hello from Cisco Ramon!")
            #if self._is_gns3_running():
                #print("GNS3 is running: Check")
            if self._is_the_lab_loaded():
                print("Lab 0 is loaded and started: Check")
        except BaseException:
            print(sys.exc_info())

    @staticmethod
    def _is_gns3_running():
        child_result, child_exitstatus = pexpect.run("pgrep gns3server", timeout=30, withexitstatus=True)
        if child_exitstatus == 0:
            return True
        else:
            raise RuntimeError("GNS3 is not running. " +
                               "Please run ./gns3_run.sh to start GNS3 before executing this script.")

    def _is_the_lab_loaded(self):
        child_result, child_exitstatus = pexpect.run("ping -c 4 {0}".format(self._device_ip_address),
                                                     timeout=30, withexitstatus=True)
        if child_exitstatus == 0:
            return True
        else:
            raise RuntimeError("Unable to reach device." +
                               "Please load Lab 0 in GNS3 and start all devices before executing this script.")

    def _connect_to_device(self):
        child = pexpect.spawn("telnet {0}".format(self._device_ip_address))

    def _enable_tftp(self):
        pass

    def _disbale_tftp(self):
        pass


if __name__ == "__main__":
    r3745 = Ramon3745("192.168.1.100", "192.168.1.10", "255.255.255.0", "")
    r3745.run()
