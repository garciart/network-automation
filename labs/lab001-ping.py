#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 001: Configure a device for Ethernet (Layer 3) connections.
To run this lab:

* Start GNS3 by executing "gn3_run" in a Terminal window.
* Select lab001 from the Projects library.
* Start all devices.
* Run this script (i.e., "python lab001.py")

Developer Notes:

* Remember to make this script executable (i.e., "sudo chmod 755 lab001.py")
* If lab001 does not exist, follow the instructions in lab001-ping.md to create the lab.

Project: Automation

Requirements:

* Python 2.7+
* pexpect
* GNS3
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
        print("Connecting to the device and configuring for Layer 3 connectivity...")

        # Connect to the device and allow time for any boot messages to clear
        child = pexpect.spawn("telnet 192.168.1.1 5001")
        time.sleep(10)
        child.sendline("\r")

        # Check for a prompt, either R1> (User EXEC mode) or R1# (Privileged EXEC Mode)
        # and enable Privileged EXEC Mode if in User EXEC mode.
        index = child.expect_exact(["R1>", "R1#", ])
        if index == 0:
            child.sendline("enable\r")
            child.expect_exact("R1#")


        # Close Telnet and disconnect from device
        child.sendcontrol("]")
        child.sendline('q\r')

        print("Successfully connected to the device and formatted the flash memory.")
    except BaseException:
        e_type, e_value, e_traceback = sys.exc_info()
        print("Error: Type {0}: {1} in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))
    finally:
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    print("Hello, friend.")
    main()
