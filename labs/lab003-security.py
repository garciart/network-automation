#!/usr/bin/Python
# -*- coding: utf-8 -*-
"""Lab 003: Basic Network Device Security.
To run this lab:

* Start GNS3 by executing "gns3_run" in a Terminal window.
* Setup the lab environment according to lab003-security.md.
* Start all devices.
* Run this script (i.e., "python lab003-security.py")

Project: Automation

Requirements:

* Python 2.7+
* pexpect
* subprocess
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
        print("Connecting to the device and configuring for Layer 3 connectivity...")

        # Connect to the device and allow time for any boot messages to clear
        console_ports = ("5000", "5001", "5002", "5003", "5004", "5005", None,)
        for port in console_ports:
            child = pexpect.spawn("telnet 192.168.1.1 {0}".format(port))
            index = child.expect(["Press RETURN to get started.", pexpect.EOF, ])
            if port is None:
                raise RuntimeError("Cannot connect to console port: Out of range.")
            if index == 0:
                break
        time.sleep(5)
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
        # Set cisco as the User EXEC mode password
        child.sendline("enable secret cisco\r")
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
        # Set the new configuration as default
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
            e_traceback.tb_lineno if e_traceback.tb_next is None
            else e_traceback.tb_next.tb_lineno))
    finally:
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    print("Welcome to Lab 003: Basic Network Device Security.")
    main()
