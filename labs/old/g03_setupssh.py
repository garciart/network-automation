#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 3: Telnet into the device and set up SSH.
Make sure GNS3 is running first (gns3_run.sh)
Also check that 192.168.1.1 is not in your ~/.ssh/known_hosts file.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import sys
import telnetlib

from labs.old import lab_utils as lu

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgcoding.com"
__license__ = "MIT"

# Initialize default values
cloud_ip = "192.168.1.1"
device_ip = "192.168.1.20"
device_netmask = "255.255.255.0"
telnet_pw = "cisco"
device_pw = "cisco"

# Global variables and constants
PROMPT_ENABLED = "R1(config)#"
PROMPT_LINE_CONFIG_MODE = "R1(config-line)#"


def setup_ssh(tn_conn):
    """Function to enable SSH on the device

    :param tn_conn: the Telnet connection
    :type tn_conn: class:Telnet

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises ex: raises a runtime error
    """
    rval = lu.FAIL
    try:
        print("Setting up SSH...")
        tn_conn.write("configure terminal\n")
        print(tn_conn.read_until("Enter configuration commands, one per line. End with CNTL/Z.", 30))
        tn_conn.write("ip domain-name rgcoding.com\n")
        print(tn_conn.read_until(PROMPT_ENABLED, 30))
        tn_conn.write("crypto key generate rsa\n")
        print(tn_conn.read_until("How many bits in the modulus [512]:", 30))
        tn_conn.write("1024\n")
        # Choosing a key modulus greater than 512 may take a few minutes, so do not timeout.
        print("Generating RSA keys...")
        print(tn_conn.read_until(PROMPT_ENABLED))
        tn_conn.write("ip ssh time-out 60\n")
        print(tn_conn.read_until(PROMPT_ENABLED, 30))
        # Valid authentication retries values are from 1-5
        tn_conn.write("ip ssh authentication-retries 3\n")
        print(tn_conn.read_until(PROMPT_ENABLED, 30))
        tn_conn.write("line vty 0 15\n")
        print(tn_conn.read_until(PROMPT_LINE_CONFIG_MODE, 30))
        tn_conn.write("transport input ssh\n")
        print(tn_conn.read_until(PROMPT_LINE_CONFIG_MODE, 30))
        tn_conn.write("login local\n")
        print(tn_conn.read_until(PROMPT_LINE_CONFIG_MODE, 30))
        tn_conn.write("username admin password cisco\n")
        print(tn_conn.read_until(PROMPT_LINE_CONFIG_MODE, 30))
        tn_conn.write("end\n")
        print(tn_conn.read_until("R1#", 30))
        tn_conn.write("show ip ssh\n")
        print(tn_conn.read_until("R1#", 30))
        tn_conn.write("exit\n")
        print(tn_conn.read_all())
        rval = lu.SUCCESS
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR
    return rval


def main():
    """Function to telnet into the device and set up SSH."""
    print("Lab 3: Setup SSH through Telnet...")
    rval = lu.FAIL
    try:
        # Attempt to connect to device on port 23 and time out after 30 seconds
        tn_conn = telnetlib.Telnet(device_ip, 23, 30)
        print(tn_conn.read_until("Password: ", 30))
        tn_conn.write("%s\n" % telnet_pw)
        print(tn_conn.read_until("R1>", 30))
        tn_conn.write("enable\n")
        print(tn_conn.read_until("Password: ", 30))
        tn_conn.write("%s\n" % device_pw)
        print(tn_conn.read_until("R1#", 30))
        setup_ssh(tn_conn)
        rval = lu.SUCCESS
        print("Lab complete. Have a nice day.")
        """
        Once complete, you can access the router from the terminal using "ssh admin@192.168.1.1" /
        and entering "cisco" as the password.
        """
    except RuntimeError:
        lu.log_error(sys.exc_info())
        rval = lu.ERROR
    return rval


if __name__ == "__main__":
    print("Lab 1: Ping another device...")
    result = lu.simple_cli_call("pgrep gns3server")
    if int(result[0]) == 0 and int(result[1]) > 0:
        main()
        print("Lab complete. Have a nice day.")
    else:
        print("Cannot run program: GNS3 is not running.")
    main()
