#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 1: Connect to a network device using Telnet

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import sys
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def connect(device_hostname, device_ip_addr, port_number=23, username="", password=""):
    print("Checking Telnet client is installed...")
    _, exitstatus = pexpect.run("which telnet", withexitstatus=True)
    if exitstatus != 0:
        raise RuntimeError("Telnet client is not installed.")
    print("Telnet client is installed.")

    print("Connecting to {0} on port {1} via Telnet...".format(device_ip_addr, port_number))
    child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
    # Slow down commands to prevent race conditions with output
    child.delaybeforesend = 0.5
    # Echo both input and output to the screen
    child.logfile = sys.stdout
    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # noinspection PyTypeChecker
    index = child.expect_exact([pexpect.TIMEOUT, ] + device_prompts, 1)

    # End-of-line (EOL) issue: Depending on the physical port you use (Console, VTY, etc.),
    # AND the port number you use (23, 5001, etc.), Cisco may require a carriage return ("\r")
    # when using pexpect.sendline. Also, each terminal emulator may have different EOL
    # settings. One solution is to append the carriage return to each sendline.
    # Nother solution is to edit the terminal emulator's runtime configuration file
    # (telnetrc, minirc, etc) before running this script, then setting or unsetting the
    # telnet transparent setting on the device.

    if index != 0:
        # If you find a hostname prompt (e.g., R1#) before any other prompt, you are accessing an open line
        print("You may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect searches to fail.\n" +
              "To prevent this in the future, reload the device to clear any artifacts.")
        # Move the pexpect cursor forward to the newest hostname prompt
        tracer_round = ";{0}".format(int(time.time()))
        # Add the carriage return here, not in the tracer_round.
        # Otherwise, you won't find the tracer_round later
        child.sendline(tracer_round + "\r")
        child.expect_exact("{0}".format(tracer_round), timeout=1)
    # Always try to find hostname prompts before anything else
    index_offset = len(device_prompts)
    while True:
        index = child.expect_exact(
            device_prompts +
            ["Login invalid",
             "Bad passwords",
             "Username:",
             "Password:",
             "Would you like to enter the initial configuration dialog? [yes/no]:",
             "Would you like to terminate autoinstall? [yes/no]:",
             "Press RETURN to get started", ])
        if index < index_offset:
            break
        elif index in (index_offset + 0, index_offset + 1):
            raise RuntimeError("Invalid credentials provided.")
        elif index in (index_offset + 2, index_offset + 3):
            print("Warning - This device has already been configured and secured.\n" +
                  "Changes made by this script may be incompatible with the current configuration.")
            if index == 0:
                # child.sendline((_username if _username is not None else raw_input("Username: ")) + "\r")
                child.sendline(username + "\r")
                child.expect_exact("Password:")
            # child.sendline((_password if _password is not None else getpass("Enter password: ")) + "\r")
            child.sendline(password + "\r")
        elif index == index_offset + 4:
            child.sendline("no\r")
        elif index == index_offset + 5:
            child.sendline("yes\r")
        elif index == index_offset + 6:
            child.sendline("\r")
    print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
    return child


def disconnect(child):
    print("Closing Telnet connection...")
    child.sendcontrol("]")
    child.expect_exact("telnet>")
    child.sendline("q\r")
    child.expect_exact(["Connection closed.", pexpect.EOF, ])
    child.close()
    print("Telnet connection closed")


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
