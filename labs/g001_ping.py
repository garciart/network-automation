#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 1: Ping the device from the host.
Make sure GNS3 is running first (gns3_run.sh)

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

import subprocess
import sys

import lab_utils as lu

DEVICE_ADDRESS = "192.168.1.10"


def main():
    """Function to ping the device from the host.

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int
    """
    rval = lu.FAIL
    try:
        result = subprocess.call(["ping", "-c", "4", DEVICE_ADDRESS])
        if result == 0:
            print("Ping successful: Received a reply from {0}.".format(DEVICE_ADDRESS))
            rval = lu.SUCCESS
        elif result == 1:
            print("Ping unsuccessful: No reply from {0}.".format(DEVICE_ADDRESS))
        else:
            print("Ping unsuccessful: Error code {0}.".format(result))
            rval = lu.ERROR
        print("Lab complete. Have a nice day.")
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR
    return rval


if __name__ == "__main__":
    print("Lab 1: Pinging the device at {0} from the host...".format(DEVICE_ADDRESS))
    main()
