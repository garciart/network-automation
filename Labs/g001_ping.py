#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script 1: Ping the device from the host.
Make sure GNS3 is running first (gns3_run.sh)

Using Python 2.7.5
"""
from __future__ import print_function
import subprocess


def main():
    """Function to ping the device from the host."""
    try:
        print("Script 1: Ping test...")
        address = "192.168.1.10"
        result = subprocess.call(["ping", "-c", "4", address])
        if result == 0:
            print("Ping successful: Received a reply from %s." % (address))
        elif result == 1:
            print("Ping unsuccessful: No reply from %s." % (address))
        else:
            print("Ping unsuccessful: Error code %s." % (result))
        print("Script complete. Have a nice day.")
    except BaseException as ex:
        print("Oops! Something went wrong:", ex)


if __name__ == "__main__":
    main()