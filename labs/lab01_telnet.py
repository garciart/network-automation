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


def connect(device_hostname, device_ip_addr, port_number=23, username="", password="", eol="\r"):
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
    child.logfile_read = sys.stdout
    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # noinspection PyTypeChecker
    index = child.expect_exact([pexpect.TIMEOUT, ] + device_prompts, 1)
    if index != 0:
        # If you find a hostname prompt (e.g., R1#) before any other prompt, you are accessing an open line
        print("\x1b[31;1mYou may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect searches to fail.\n" +
              "To prevent this in the future, reload the device to clear any artifacts.\x1b[0m")
        # Move the pexpect cursor forward to the newest hostname prompt
        tracer_round = ";{0}".format(int(time.time()))
        # Add the carriage return here, not in the tracer_round.
        # Otherwise, you won't find the tracer_round later
        child.sendline(tracer_round + eol)
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
             "Press RETURN to get started", ], timeout=60)
        if index < index_offset:
            break
        elif index in (index_offset + 0, index_offset + 1):
            raise RuntimeError("Invalid credentials provided.")
        elif index in (index_offset + 2, index_offset + 3):
            print("\x1b[31;1mWarning - This device has already been configured and secured.\n" +
                  "Changes made by this script may be incompatible with the current configuration.\x1b[0m")
            if index == index_offset + 2:
                # child.sendline((_username if _username is not None else raw_input("Username: ")) + eol)
                child.sendline(username)
                child.expect_exact("Password:")
            # child.sendline((_password if _password is not None else getpass("Enter password: ")) + eol)
            child.sendline(password + eol)
        elif index == index_offset + 4:
            child.sendline("no" + eol)
        elif index == index_offset + 5:
            child.sendline("yes" + eol)
        elif index == index_offset + 6:
            child.sendline(eol)
    print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
    return child


def disconnect(child, eol="\r"):
    print("Closing Telnet connection...")
    child.sendcontrol("]")
    child.expect_exact("telnet>")
    child.sendline("q" + eol)
    child.expect_exact(["Connection closed.", pexpect.EOF, ])
    child.close()
    print("Telnet connection closed")


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
