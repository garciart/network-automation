#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 4: Get information about a network device

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import re
import sys
import time

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def run(child, device_hostname, eol="\r"):
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
    # The next cursor will stop here -> R2#show version | include [IOSios] [Ss]oftware
    #                                   Cisco IOS Software...
    #                       Not here -> R2#
    child.expect_exact(device_prompts[1], 1)

    print("Getting device information...")
    child.sendline("show version | include [IOSios] [Ss]oftware" + eol)
    child.expect_exact(device_prompts[1])

    software_ver = str(child.before).split(
        "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
    if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
        raise RuntimeError("Cannot get the device's software version.")
    print("Software version: {0}".format(software_ver))

    child.sendline("show inventory | include [Cc]hassis" + eol)
    child.expect_exact(device_prompts[1])
    # child.expect_exact(device_prompts[1])
    device_name = str(child.before).split(
        "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Cc]hassis").search(device_name):
        raise RuntimeError("Cannot get the device's name.")
    print("Device name: {0}".format(device_name))

    child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]" + eol)
    child.expect_exact(device_prompts[1])
    # child.expect_exact(device_prompts[1])
    serial_num = str(child.before).split(
        "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
        raise RuntimeError("Cannot get the device's serial number.")
    print("Serial number: {0}".format(serial_num))

    return child


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
