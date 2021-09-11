#!/usr/bin/Python
# -*- coding: utf-8 -*-
"""Lab 001: Configure a device for Ethernet (Layer 3) connections.
To run this lab:

* Start GNS3 by executing "gn3_run" in a Terminal window.
* Select lab001 from the Projects library.
* Start all devices.
* Run this script (i.e., "Python lab001-ping.py")

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

import shlex
import subprocess
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
        # Enter Privileged EXEC mode
        child.sendline("configure terminal\r")
        child.expect_exact("R1(config)#")
        # Access Ethernet port
        child.sendline("interface FastEthernet0/0\r")
        child.expect_exact("R1(config-if)#")
        # Assign an IPv4 address and subnet mask
        child.sendline("ip address 192.168.1.20 255.255.255.0\r")
        child.expect_exact("R1(config-if)#")
        # Bring FastEthernet0/0 up
        child.sendline("no shutdown\r")
        time.sleep(5)
        child.expect_exact("R1(config-if)#")
        child.sendline("exit\r")
        child.expect_exact("R1(config)#")
        # Set cisco as the User EXEC mode password
        child.sendline("enable secret cisco\r")
        child.expect_exact("R1(config)#")
        # Require IP addresses instead of URLs to reduce typos
        child.sendline("no ip domain-lookup\r")
        child.expect_exact("R1(config)#")
        # Enter line configuration mode and specify the type of line
        child.sendline("line console 0\r")
        child.expect_exact("R1(config-line)#")
        # Set cisco as the console terminal line password
        child.sendline("password cisco\r")
        child.expect_exact("R1(config-line)#")
        # Require console terminal login
        child.sendline("login\r")
        child.expect_exact("R1(config-line)#")
        # Allow up to five connections for virtual teletype (vty) remote console access (Telnet, SSH, etc.)
        child.sendline("line vty 0 4\r")
        child.expect_exact("R1(config-line)#")
        # Set cisco as the remote console access password
        child.sendline("password cisco\r")
        child.expect_exact("R1(config-line)#")
        # Require Telnet and SSH login
        child.sendline("login\r")
        child.expect_exact("R1(config-line)#")
        child.sendline("end\r")
        child.expect_exact("R1#")
        # Save the configuration
        child.sendline("write memory\r")
        """
        Building configuration...
        [OK]
        R1#
        """
        child.expect_exact("[OK]", timeout=120)
        # Set the configuration as default
        child.sendline("copy running-config startup-config\r")
        child.expect_exact("Destination filename [startup-config]?")
        child.sendline("\r")
        """
        Building configuration...
        [OK]
        R1#
        """
        child.expect_exact("[OK]", timeout=120)
        print("Configuration successful.")

        print("Checking connectivity...")
        # Ping the host from the device
        child.sendline('ping 192.168.1.10\r')
        # Check for the fail condition first, since the child will always return a prompt
        index = child.expect(['Success rate is 0 percent', "R1#", ], timeout=60)
        if index == 0:
            raise RuntimeError('Unable to ping the host from the device.')
        else:
            # Ping the device from the host
            cmd = 'ping -c 4 192.168.1.20'
            # No need to read the output. Ping returns a non-zero value if no packets are received,
            # which will cause a check_output exception
            subprocess.check_output(shlex.split(cmd))
        # Close Telnet and disconnect from device
        child.sendcontrol("]")
        child.sendline('q\r')
        print("Connectivity to and from the device is good.")

        print("Checking security...")
        child = pexpect.spawn("telnet 192.168.1.20")
        child.sendline("cisco\r")
        child.expect_exact("R1>")
        print("Security is good.")

        # Close Telnet and disconnect from device
        child.sendcontrol("]")
        child.sendline('q\r')
        print("Successfully configured the device and checked connectivity.")
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
