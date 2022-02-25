#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 3: Format a network device's memory

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import sys
import time

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

import pexpect


def run(child, device_hostname, disk_name="flash", eol="\r"):
    print("Formatting device memory...")

    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # Move the pexpect cursor forward to the newest hostname prompt
    tracer_round = ";{0}".format(int(time.time()))
    # Add a carriage return here, not in the tracer_round, or you won't find the tracer_round later
    child.sendline(tracer_round + eol)
    child.expect_exact("{0}".format(tracer_round), timeout=1)
    # WATCH YOUR CURSORS! You must consume the prompt after the tracer round
    # or the pexepect cursor will stop at the wrong prompt
    # The next cursor will stop here -> R2#format flash
    #                       Not here -> Format operation may take a while. Continue? [confirm]
    child.expect_exact(device_prompts[1], 1)

    # Format the memory. Look for the final characters of the following strings:
    # "Format operation may take a while. Continue? [confirm]"
    # "Format operation will destroy all data in "flash:".  Continue? [confirm]"
    # "66875392 bytes available (0 bytes used)"
    child.sendline("format {0}:".format(disk_name) + eol)
    child.expect_exact("Continue? [confirm]")
    child.sendline(eol)
    child.expect_exact("Continue? [confirm]")
    child.sendline(eol)
    # Not all devices ask for this
    index = child.expect_exact(["Enter volume ID", pexpect.TIMEOUT, ], timeout=1)
    if index == 0:
        child.sendline(eol)
    child.expect_exact("Format of {0} complete".format(disk_name), timeout=120)
    child.sendline("show {0}".format(disk_name) + eol)
    child.expect_exact("(0 bytes used)")
    child.expect_exact(device_prompts[1])
    print("Device memory formatted.")


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
