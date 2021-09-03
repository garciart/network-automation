#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 000: Telnet into a device and format the flash memory.
To run this lab:

* Start GNS3 by executing "gn3_run" in a Terminal window.
* Select lab000 from the Projects library.
* Start all devices.
* Run this script (i.e., "python lab000.py")

Developer Notes:

* Remember to make this script executable (i.e., "sudo chmod 755 lab000.py")
* If lab000 does not exist, follow the instructions in README.md to create the lab.

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
        print("Connecting to the device and formatting the flash memory...")

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

        # Format the flash memory. Look for the final characters of the following strings:
        # "Format operation may take a while. Continue? [confirm]"
        # "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        # "66875392 bytes available (0 bytes used)"
        #
        child.sendline("format flash:\r")
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        child.expect_exact("Format of flash complete", timeout=120)
        child.sendline("show flash\r")
        child.expect_exact("(0 bytes used)")

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
