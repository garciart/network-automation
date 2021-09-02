#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 000: Telnet into a device and format the flash memory.
To run this lab:
* Start GNS3 by executing "./gn3_run" in a Terminal window.
* Select lab000 from the Projects library.
* Start all devices.

If lab000 does not exist, follow the instructions in README.md to create the lab.

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
        # Format the flash memory
        child.sendline("format flash:")
        # Expect "Format operation may take a while. Continue? [confirm]"
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        # Expect "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        child.expect_exact("Format of flash complete", timeout=120)
        child.sendline("show flash")
        # Expect "66875392 bytes available (0 bytes used)"
        child.expect_exact("(0 bytes used)")
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
