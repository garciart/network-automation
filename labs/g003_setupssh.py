#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script 3: Telnet into the device and set up SSH.
Make sure GNS3 is running first (gns3_run.sh)

Also check that 192.168.1.1 is not in your ~/.ssh/known_hosts file.

Using Python 2.7.5
"""
from __future__ import print_function
import getpass
import telnetlib


# Initialize default values
cloud_ip = "192.168.1.1"
device_ip = "192.168.1.10"
device_netmask = "255.255.255.0"
telnet_pw = "cisco"
device_pw = "cisco"


def setup_ssh(tn_conn):
    """Function to enable SSH on the device
    :param tn_conn: the Telnet connection
    :returns:
    :raises ex: raises a base exception
    """
    try:
        print("Setting up SSH...")
        tn_conn.write("configure terminal\n")
        print(tn_conn.read_until("Enter configuration commands, one per line. End with CNTL/Z.", 30))
        tn_conn.write("ip domain-name rgprogramming.com\n")
        print(tn_conn.read_until("R1(config)#", 30))
        tn_conn.write("crypto key generate rsa\n")
        print(tn_conn.read_until("How many bits in the modulus [512]:", 30))
        tn_conn.write("1024\n")
        # Choosing a key modulus greater than 512 may take a few minutes, so do not timeout.
        print("Generating RSA keys...")
        print(tn_conn.read_until("R1(config)#"))
        tn_conn.write("ip ssh time-out 60\n")
        print(tn_conn.read_until("R1(config)#", 30))
        # Valid authentication retries values are from 1-5
        tn_conn.write("ip ssh authentication-retries 3\n")
        print(tn_conn.read_until("R1(config)#", 30))
        tn_conn.write("line vty 0 15\n")
        print(tn_conn.read_until("R1(config-line)#", 30))
        tn_conn.write("transport input ssh\n")
        print(tn_conn.read_until("R1(config-line)#", 30))
        tn_conn.write("login local\n")
        print(tn_conn.read_until("R1(config-line)#", 30))
        tn_conn.write("username admin password cisco\n")
        print(tn_conn.read_until("R1(config-line)#", 30))
        tn_conn.write("end\n")
        print(tn_conn.read_until("R1#", 30))
        tn_conn.write("show ip ssh\n")
        print(tn_conn.read_until("R1#", 30))
        tn_conn.write("exit\n")
        print(tn_conn.read_all())
    except BaseException as ex:
        print("Oops! Something went wrong:", ex)


def main():
    """Function to telnet into the device and set up SSH."""
    print("Script 3: Setup SSH through Telnet...")
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
        print("Script complete. Have a nice day.")
        """
        Once complete, you can access the router from the terminal using "ssh admin@192.168.1.1" and entering "cisco" as the password.
        """
    except BaseException as ex:
        print("Oops! Something went wrong:", ex)


if __name__ == "__main__":
    main()