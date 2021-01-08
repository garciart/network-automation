#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script 00: Connect to device through serial port.
Make sure GNS3 is running first (gns3_run.sh)

Also check that no 192.168.1.X addresses are in your ~/.ssh/known_hosts file.

Using Python 2.7.5

Remember: sudo usermod -a -G dialout gns3user
May also have to do the same thing with lock
Using /dev/ttyS0
"""
from __future__ import print_function

import sys
import lab_utils as lu


def main():
    rval = lu.FAIL
    try:
        print("Hello, friend.")
        lu.log_message("What's up?")
        rval = lu.SUCCESS
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR
    return rval


if __name__ == "__main__":
    main()
