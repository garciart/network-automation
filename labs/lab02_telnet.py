#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 2: Access a network device's Privileged EXEC Mode

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


def main(device_hostname, device_ip_address, port_number=23, vty_username=None, vty_password=None,
         enable_password=None):
    """Connect to the device via Telnet.

    :param str device_hostname: The hostname of the device.
    :param str device_ip_address: The IP address that will be used to connect to the device.
    :param int port_number: The port number for the connection.
    :param str vty_username: Username for login local setting.
    :param str vty_password: Password when logging in remotely.
    :param str enable_password: Password to enable Privileged EXEC Mode.
    """
    print(YLW + "Connecting to device using Telnet...\n" + CLR)
    # End-of-line (EOL) issue: Depending on the physical port you use (Console, VTY, etc.),
    # AND the port number you use (23, 5001, etc.), Cisco may require a carriage return ("\r")
    # when using pexpect.sendline. Also, each terminal emulator may have different EOL
    # settings. One solution is to edit the terminal emulator's runtime configuration file
    # (telnetrc, minirc, etc) before running this script, then setting or unsetting the
    # telnet transparent setting on the device, but you would have to do this every time.
    # My solution is to send a line and wait for a TIMEOUT. If the command goes through
    # without timing-out, I do not do anything.
    # If I receive a TIMEOUT, I send a CR (which pushes my input through), and I then append
    # a CR to all the rest of my commands.
    _eol = ""
    # Allow only one login attempt
    login_attempted = False
    # Add the hostname to the standard Cisco prompt endings
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    # Spawn the child and change default settings
    child = pexpect.spawn("telnet {0} {1}".format(device_ip_address, port_number))
    # Slow down commands to prevent race conditions with output
    child.delaybeforesend = 0.5
    # Echo both input and output to the screen
    child.logfile = sys.stdout
    # Ensure you are not accessing an active session
    try:
        child.expect_exact(prompt_list, timeout=10)
        # If this is a new session, you will not find a prompt. If a prompt is found,
        # print the warning and reload; otherwise, catch the TIMEOUT and proceed.
        print(RED +
              "You may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect expect calls to fail.\n" +
              "To prevent this, we are reloading this device to clear any artifacts.\n" +
              "Reloading now...\n" + CLR)
        child.sendline("reload" + _eol)
        child.expect_exact("Proceed with reload? [confirm]")
        child.sendline(_eol)
        # Expect the child to close
        child.expect_exact([pexpect.EOF, pexpect.TIMEOUT, ])
        exit()
    except pexpect.TIMEOUT:

        def check_and_warn():
            if login_attempted is True:
                raise RuntimeError("Invalid credentials provided.")
            print(YLW + "Warning - This device has already been configured and secured.\n" +
                  "Changes made by this script may be incompatible with the current " +
                  "configuration.\n" + CLR)

        # Clear initial questions until a prompt is reached
        while True:
            index = child.expect_exact(
                ["Press RETURN to get started",
                 "Would you like to terminate autoinstall? [yes/no]:",
                 "Would you like to enter the initial configuration dialog? [yes/no]:",
                 "Username:", "Password:", pexpect.TIMEOUT, ] + prompt_list)
            if index == 0:
                child.sendline(_eol)
            elif index == 1:
                child.sendline("yes" + _eol)
            elif index == 2:
                child.sendline("no" + _eol)
            elif index == 3:
                check_and_warn()
                vty_username = vty_username if vty_username is not None else raw_input("Username: ")
                child.sendline(vty_username + _eol)
            elif index == 4:
                # Not all connections require a username
                check_and_warn()
                vty_password = vty_password if vty_password is not None else getpass()
                child.sendline(vty_password + _eol)
                login_attempted = True
            elif index == 5:
                if _eol == "":
                    _eol = "\r"
                    child.sendline(_eol)
                else:
                    raise RuntimeError("Cannot determine EOL setting.")
            else:
                # Prompt found; continue script
                break
    print(GRN + "Connected to device using Telnet.\n" + CLR)

    print(YLW + "Enabling Privileged EXEC Mode...\n" + CLR)
    # A reloaded device's prompt will be either R1> (User EXEC mode) or R1# (Privileged EXEC Mode)
    # Just in case the device boots into User EXEC mode, enable Privileged EXEC Mode
    # The enable command will not affect anything if the device is already in Privileged EXEC Mode
    child.sendline("disable" + _eol)
    child.expect_exact(prompt_list[0])
    child.sendline("enable" + _eol)
    index = child.expect_exact(["Password:", prompt_list[1], ])
    if index == 0:
        enable_password = enable_password if enable_password is not None else getpass()
        child.sendline(enable_password + _eol)
        child.expect_exact(prompt_list[1])
    print(GRN + "Privileged EXEC Mode enabled.\n" + CLR)

    # Close the Telnet client
    print(YLW + "Closing telnet connection...\n" + CLR)
    child.sendcontrol("]")
    child.sendline("q" + _eol)
    index = child.expect_exact(["Connection closed.", pexpect.EOF, ])
    # Close the Telnet child process
    child.close()
    print(GRN + "Telnet connection closed: {0}\n".format(index) + CLR)


if __name__ == "__main__":
    try:
        main("R1", "192.168.1.20", port_number=23, vty_username="admin", vty_password="cisco",
             enable_password="cisen")
    except pexpect.TIMEOUT:
        print(RED + "Error: Unable to find the expect search string.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.TIMEOUT).get_trace())
    except pexpect.EOF:
        print(RED + "Error: Child closed unexpectedly.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.EOF).get_trace())
