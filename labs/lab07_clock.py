#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 6: Secure a network device

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


def verify_connection(child, device_hostname, eol="\r"):
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
    return device_prompts


def synch_clock(child, device_hostname, sudo_password, ntp_server_ip, commit=True, eol="\r"):
    print("Synchronizing the network device's clock." + eol)
    device_prompts = verify_connection(child, device_hostname, eol="\r")
    child.sendline("configure terminal" + eol)
    child.expect_exact(device_prompts[2])
    child.sendline("ntp server {0}".format(ntp_server_ip) + eol)
    child.expect_exact(device_prompts[2])
    child.sendline("end" + eol)
    child.expect_exact(device_prompts[1])
    # Save changes if True
    if commit:
        child.sendline("write memory" + eol)
        child.expect_exact(device_prompts[1])
    print("Waiting 60 seconds for the NTP server to synchronize...")
    time.sleep(60)
    print("Network device clock synchronized." + eol)


def set_clock(child, device_hostname, time_to_set="12:00:00 Jan 1 2021", eol="\r"):
    print("Setting the network device's clock." + eol)
    device_prompts = verify_connection(child, device_hostname, eol="\r")
    child.sendline("clock set {0}".format(time_to_set) + eol)
    child.expect_exact(device_prompts[1])
    print("Network device clock set." + eol)


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
