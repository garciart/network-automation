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
import time

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def run(child, device_hostname):
    print("Formatting flash memory...")

    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # Move the pexpect cursor forward to the newest hostname prompt
    tracer_round = ";{0}".format(int(time.time()))
    # Add a carriage return here, not in the tracer_round, or you won't find the tracer_round later
    child.sendline(tracer_round + "\r")
    child.expect_exact("{0}".format(tracer_round), timeout=1)
    # WATCH YOUR CURSORS! You must consume the prompt after the tracer round
    # or the pexepect cursor will stop at the wrong prompt
    # The next cursor will stop here -> R2#format flash
    #                       Not here -> Format operation may take a while. Continue? [confirm]
    child.expect_exact(device_prompts[1], 1)

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
    child.expect_exact(device_prompts[1])
    print("Flash memory formatted.")
    return child


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
