#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 3: Format a network device's flash memory

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import sys
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"

CISCO_PROMPTS = [
    ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]


def main(device_hostname, device_ip_address, port=23):
    print(YLW + "Connecting to device using Telnet...\n" + CLR)
    # Add hostname to standard Cisco prompt endings
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    # Spawn the child and change default settings
    child = pexpect.spawn("telnet {0} {1}".format(device_ip_address, port))
    # Slow down commands to prevent race conditions with output
    child.delaybeforesend = 0.5
    # Echo both input and output to the screen
    child.logfile = sys.stdout
    # Ensure you are not accessing an active session
    try:
        child.expect_exact(prompt_list, timeout=10)
        # If this is a new session, you will not find a prompt
        # If a prompt is found, print the warning and reload
        # Otherwise, catch the TIMEOUT and proceed
        print(RED +
              "You may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect expect calls to fail.\n" +
              "To prevent this, we are reloading this device to clear any artifacts.\n" +
              "Reloading now...\n" + CLR)
        child.sendline("reload\r")
        child.expect_exact("Proceed with reload? [confirm]")
        child.sendline("\r")
        child.expect_exact(pexpect.EOF)
        exit()
    except pexpect.TIMEOUT:
        # Clear initial questions until a prompt is reached
        while True:
            index = child.expect_exact(
                ["Press RETURN to get started",
                 "Would you like to terminate autoinstall? [yes/no]:",
                 "Would you like to enter the initial configuration dialog? [yes/no]:",
                 "Password:", ] + prompt_list)
            if index == 0:
                child.sendline("\r")
            elif index == 1:
                child.sendline("yes\r")
            elif index == 2:
                child.sendline("no\r")
            elif index == 3:
                # If configured, warn and prompt for a password
                print(YLW + "Warning" + CLR +
                      " - This device has already been configured and secured.\n" +
                      "Changes made by this script may be incompatible with the current " +
                      "configuration.\n")
                password = getpass()
                child.sendline(password + "\r")
            else:
                break
    print(GRN + "Connected to device using Telnet.\n" + CLR)

    # A reloaded device's prompt will be either R1> (User EXEC mode) or R1# (Privileged EXEC Mode).
    # Just in case the device boots into User EXEC mode, enable Privileged EXEC Mode .
    # If the device is already in Privileged EXEC Mode, the enable command will not affect anything.
    child.sendline("enable\r")
    index = child.expect_exact(["Password:", prompt_list[1], ])
    if index == 0:
        password = getpass()
        child.sendline(password + "\r")
        child.expect_exact(prompt_list[1])

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

    print(YLW + "Closing telnet connection...\n" + CLR)
    child.sendcontrol("]")
    child.sendline("q\r")
    index = child.expect_exact(["Connection closed.", pexpect.EOF, ])
    # Close the Telnet child process
    child.close()
    print(GRN + "Telnet connection closed: {0}\n".format(index) + CLR)


if __name__ == "__main__":
    try:
        main("R1", "192.168.1.1", port=5001)
    except RuntimeError:
        pass
    except pexpect.TIMEOUT:
        print(RED + "Error: Unable to find the expect search string.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.TIMEOUT).get_trace())
    except pexpect.EOF:
        print(RED + "Error: Child closed unexpectedly.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.EOF).get_trace())
