#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 001: Configure a device for Ethernet (Layer 3) connections.
To run this lab:
* Start GNS3 by executing "./gn3_run" in a Terminal window.
* Select lab001 from the Projects library.
* Start all devices.

If lab001 does not exist, follow the instructions in lab001.md to create the lab.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import sys
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def main():
    try:
        # Connect to the device and allow time for the boot sequence to finish
        child = pexpect.spawn("telnet 192.168.1.100 5001")
        time.sleep(30)
        child.sendline("\r")
        # Enter Privileged EXEC Mode
        child.sendline("enable\r")
        child.expect_exact("R1#")
        # TODO: Configuration code
        # TODO: Disconnect from device
    except BaseException:
        e_type, e_value, e_traceback = sys.exc_info()
        print("Type {0}: {1} in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))
    finally:
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    print("Hello, friend")
    main()
