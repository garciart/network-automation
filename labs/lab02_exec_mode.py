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
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def enable(child, device_hostname, password=""):
    print("Access a network device's Privileged EXEC Mode...")

    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # Move the pexpect cursor forward to the newest hostname prompt
    tracer_round = ";{0}".format(int(time.time()))
    # Add the carriage return here, not in the tracer_round.
    # Otherwise, you won't find the tracer_round later
    child.sendline(tracer_round + "\r")
    child.expect_exact("{0}".format(tracer_round), timeout=1)
    index = child.expect_exact(device_prompts, 1)
    if index == 0:
        child.sendline("enable\r")
        index = child.expect_exact(["Password:", device_prompts[1], ], 1)
        if index == 0:
            child.sendline(password + "\r")
            child.expect_exact(device_prompts[1], 1)
    elif index != 1:
        child.sendline("end\r")
        child.expect_exact(device_prompts[1], 1)
    print("Privileged EXEC Mode accessed.")
    return child


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
