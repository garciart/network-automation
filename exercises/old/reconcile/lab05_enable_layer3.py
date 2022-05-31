#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 5: Enable Layer 3 communications to and from a network device

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

import sys
import time

import pexpect


def run(child, device_hostname, new_ip_address, new_netmask="255.255.255.0", commit=True, eol="\r"):
    print("Enabling Layer 3 communications...")

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
    # The next cursor will stop here -> R2#configure terminal
    #                       Not here -> R2#
    child.expect_exact(device_prompts[1], 1)

    child.sendline("configure terminal" + eol)
    child.expect_exact(device_prompts[2])
    child.sendline("interface FastEthernet0/0" + eol)
    child.expect_exact(device_prompts[3])
    child.sendline("ip address {0} {1}".format(new_ip_address, new_netmask) + eol)
    child.expect_exact(device_prompts[3])
    child.sendline("no shutdown" + eol)
    child.expect_exact(device_prompts[3])
    child.sendline("end" + eol)
    child.expect_exact(device_prompts[1])

    # Save changes if True
    if commit:
        child.sendline("write memory" + eol)
        child.expect_exact(device_prompts[1])
    print("Layer 3 communications enabled.")


def ping_from_device(child, destination_ip_addr, count=4, eol="\r"):
    child.sendline("ping {0} repeat {1}".format(destination_ip_addr, count) + eol)
    index = child.expect(["percent (0/4)", r"percent \([1-4]/4\)", ])
    if index == 0:
        raise RuntimeError("Cannot ping {0} from this device.".format(destination_ip_addr))


def ping_device(device_ip_addr, count=4):
    _, exitstatus = pexpect.run("ping -c {0} {1}".format(count, device_ip_addr), withexitstatus=True)
    if exitstatus != 0:
        # No need to read the output. Ping returns a non-zero value if no packets are received
        raise RuntimeError("Cannot ping the device at {0}.".format(device_ip_addr))


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
