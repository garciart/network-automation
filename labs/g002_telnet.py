#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script 2: Telnet into the device and ping the host.
Make sure GNS3 is running first (gns3_run.sh)

Using Python 2.7.5
"""
from __future__ import print_function
# import getpass
import telnetlib


def main():
    """Function to telnet into the device and ping the host."""
    print("Script 2: Telnet login test...")
    try:
        # Initialize default values
        cloud_ip = "192.168.1.1"
        device_ip = "192.168.1.10"
        telnet_pw = "cisco"
        device_pw = "cisco"

        # Attempt to connect to device on port 23 and time out after 30 seconds
        tn_conn = telnetlib.Telnet(device_ip, 23, 30)
        # Manual note: [Return] to reach the router prompt
        print(tn_conn.read_until("Password: ", 30))
        # OPTIONAL: Ask for a password
        # telnet_pw = getpass.getpass()
        tn_conn.write("{0}\n".format(telnet_pw))
        print(tn_conn.read_until("R1>", 30))
        tn_conn.write("enable\n")
        print(tn_conn.read_until("Password: ", 30))
        # device_pw = getpass.getpass()
        tn_conn.write("{0}\n".format(device_pw))
        print(tn_conn.read_until("R1#", 30))

        # Ping the host from the device to test the connection
        tn_conn.write("ping {0}\n".format(cloud_ip))
        print(tn_conn.read_until(" ms", 30))
        tn_conn.write("exit\n")
        print(tn_conn.read_all())
        # Manual note: Press [CTRL] + []] to reach the Telnet prompt, then input [q] to exit Telnet
        print("Script complete. have a nice day.")
    except RuntimeError as ex:
        print("Oops! Something went wrong:", ex)


if __name__ == "__main__":
    main()