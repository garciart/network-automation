#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 001: Telnet into a device and format the flash memory.
To run this lab:

* Start GNS3 by executing "gns3_run" in a Terminal window.
* Setup the lab environment according to lab001-telnet.md.
* Start all devices.
* Run this script (i.e., "python lab001-telnet.py")

Project: Automation

Requirements:

* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import os
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def main():
    print("Lab 1: Telnet and pexpect.")
    child = None
    try:
        # Warn the user to reload the device before continuing
        raw_input("\x1b[5;33m" +
                  "** WARNING ** - Ensure you have reloaded the device in GNS3 before continuing this script.\n\n" +
                  "Press [ENTER] to continue when you are ready to continue> \x1b[0m")
        print("Enabling Telnet...")
        sudo_password = getpass(prompt="SUDO password: ") + "\r"
        cmd = "sudo firewall-cmd --zone=public --add-port=23/tcp"
        (command_output, exitstatus) = pexpect.run(cmd,
                                                   events={"(?i)password": sudo_password},
                                                   withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to {0}: {1}".format(cmd, command_output.strip()))
        print("Telnet enabled.")

        print("Connecting to device using Telnet...")
        for console_port_number in range(5000, 5005 + 1):
            if child:
                child.close()
            try:
                child = pexpect.spawn("telnet 192.168.1.1 {0}".format(console_port_number))
                break
            except pexpect.ExceptionPexpect:
                pass
        if not child:
            raise RuntimeError("Cannot connect via console port.")

        # If pexpect does not find "Press RETURN to get started", the user did not reload the device.
        # If the device is not reloaded, the user may access a VTY line containing artifacts from an earlier
        # (or even a current) session, which may cause pexpect calls to fail.
        child.expect("Press RETURN to get started")
        child.sendline("\r")
        # Add a log file to the child
        child.logfile = open("{0}/lab001.log".format(os.getcwd()), "w")

        # Check for a prompt and get to R1# (Privileged EXEC Mode):
        # If at R1> (User EXEC mode), enter "enable" to get to R1#.
        # If at R1(config)# or any other Global Configuration Mode, enter "end" to get to R1#.
        # WARNING - pexpect is not greedy, and it will stop at the first at matching prompt.
        # Therefore, if the user did not reload the device, pexpect may match a prompt from a session still in memory.
        # This will cause pexpect to stop at the wrong line, possibly causing the expect to fail.
        index = child.expect_exact([
            "Password:",
            "R1>",
            "R1#",
            "R1(config)#",
            "R1(config-if)#",
            "R1(config-router)#",
            "R1(config-line)#", ])
        if index == 0:
            raise RuntimeWarning("This device is already configured. Do not run this script.")
        elif index == 1:
            child.sendline("enable\r")
            child.expect_exact("R1#")
        elif index > 2:
            child.sendline("exit\r")
            child.expect_exact("R1#")
        print("Connected to device using Telnet.")

        """
        # Format the flash memory. Look for the final characters of the following strings:
        # "Format operation may take a while. Continue? [confirm]"
        # "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        # "66875392 bytes available (0 bytes used)"
        child.sendline("format flash:\r")
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        child.expect_exact("Continue? [confirm]")
        child.sendline("\r")
        child.expect_exact("Format of flash complete", timeout=120)
        child.sendline("show flash\r")
        child.expect_exact("(0 bytes used)")
        """

        # pexpect reads from the start of the buffer to the expected result (non-greedy.
        # If a send does not have an associated expect, the expected result may appear before the desired
        # output, as demonstrated below.
        child.sendline("; Pexpect will read this comment into the buffer.\r")
        child.expect_exact("R1#")
        print(child.before)
        child.sendline("; Pexpect will read only up to the prompt following this comment.\r")
        child.sendline("; Pexpect will not reach this comment.\r")
        child.sendline("; Pexpect will not reach this comment, either.\r")
        child.expect_exact("R1#")
        print(child.before)

        print("Reloading device and closing telnet connection...")
        child.sendline("reload\r")
        index = child.expect_exact(
            ["System configuration has been modified. Save? [yes/no]:", "Proceed with reload? [confirm]", ])
        if index == 0:
            child.sendline("no\r")
        child.sendline("\r")
        print("Device reloaded.")
        child.sendcontrol("]")
        child.sendline("q\r")
        child.expect_exact("Connection closed.")
        # Close the Telnet child process
        child.close(force=True)
        print("Telnet connection closed.")

        print("Resetting the Linux environment...")
        # Close the firewall port
        if not sudo_password:
            sudo_password = getpass(prompt="SUDO password: ") + "\r"
        cmd = "sudo firewall-cmd --zone=public --remove-port=23/tcp"
        (command_output, exitstatus) = pexpect.run(cmd,
                                                   events={"(?i)password": sudo_password},
                                                   withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to {0}: {1}".format(cmd, command_output.strip()))
        print("Linux environment reset.")

    except:
        # Simple error handling
        e_type, e_value, e_traceback = sys.exc_info()
        print("Error: Type {0}: {1} in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))
    finally:
        if child:
            child.close()
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    print("Welcome to Lab 001: Telnet into a device and format the flash memory.")
    main()
