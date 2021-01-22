#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 1: Ping the device from the host.
Make sure GNS3 is running first (gns3_run.sh)

Project: Automation

Requirements:
- Python 2.7.5
- pexpect
"""
from __future__ import print_function

import shlex
import subprocess
import sys

import pexpect

import lab_utils as lu

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

# Global variables and constants
# DEVICE_ADDRESS = "192.168.1.10"
DEVICE_ADDRESS = "8.8.8.8"


def ping_using_subprocess(cmd):
    """Function to ping the device from the host using subprocess.check_output. Remember, in Python 2.7,
    subprocess does not have a timeout setting.

    :param cmd: Command or script to execute in the command-line interface.
    :type cmd: str

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises cpe: CalledProcessError to catch non-zero return values from subprocess.
    :raises ex: RuntimeError for any other exceptions or errors.
    """
    rval = lu.FAIL, result = None
    try:
        sanitized_cmd = shlex.split(cmd)  # ["ping", "-c", "4", DEVICE_ADDRESS]
        # subprocess.call returns a returncode
        # subprocess.check_call returns a returncode of 0 for success or a CalledProcessError for a non-zero value
        # subprocess.check_output returns output or a CalledProcessError with a returncode and output
        try:
            result = subprocess.check_output(sanitized_cmd)
            print("{0}: Ping successful - Received a reply from {1}.".format(cmd, DEVICE_ADDRESS))
            rval = lu.SUCCESS, result
        except subprocess.CalledProcessError as cpe:
            lu.log_message("{0}: Error - Code {1}, Output {2}.".format(cmd, cpe.returncode, cpe.output))
            rval = lu.ERROR, cpe.output
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR, result
    return rval


def ping_using_pexpect(cmd, timeout=30):
    """Function to ping the device from the host using pexpect.run.

    :param cmd: Command or script to execute in the command-line interface.
    :type cmd: str
    :param timeout: Time limit to complete the command in seconds.
    :type timeout: int

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises ex: RuntimeError for any exceptions or errors.
    """
    rval = lu.FAIL, child_result = None
    try:
        child_result, child_exitstatus = pexpect.run(cmd, timeout=timeout, withexitstatus=True)
        if child_exitstatus is None:
            lu.log_message("{0}: Operation timed out.".format(cmd))
        elif child_exitstatus != 0:
            lu.log_message("{0}: Error - {1}".format(cmd, child_result))
            rval = lu.ERROR, child_result
        else:
            print("{0}: Ping successful - Received a reply from {1}.".format(cmd, DEVICE_ADDRESS))
            rval = lu.SUCCESS, child_result
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR, child_result
    return rval


if __name__ == "__main__":
    print("Lab 1a: Pinging the device at {0} from the host using subprocess...".format(DEVICE_ADDRESS))
    print("rval =", ping_using_subprocess("ping -c 4 {0}".format(DEVICE_ADDRESS)))
    print("Lab 1b: Pinging the device at {0} from the host using pexpect...".format(DEVICE_ADDRESS))
    print("rval =", ping_using_pexpect("ping -c 4 {0}".format(DEVICE_ADDRESS)))
    print("Lab complete. Have a nice day.")
