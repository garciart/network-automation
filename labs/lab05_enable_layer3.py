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

import re

import pexpect

import utility

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


def main(device_hostname, device_ip_address, port_number=23):
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]

    child = utility.connect_via_telnet(
        device_hostname, device_ip_address, port_number, "admin", "cisco")
    utility.enable_privileged_exec_mode(child, device_hostname)
    # utility.format_flash_memory(child, device_hostname)
    utility.get_device_information(child, device_hostname)

    # TODO: CODE GOES HERE

    utility.close_telnet_connection(child)


if __name__ == "__main__":
    try:
        main("R1", "192.168.1.1", port_number=5002)
        # main("R1", "192.168.1.20", port_number=23)
    except RuntimeError:
        pass
    except pexpect.TIMEOUT:
        print(RED + "Error: Unable to find the expect search string.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.TIMEOUT).get_trace())
    except pexpect.EOF:
        print(RED + "Error: Child closed unexpectedly.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.EOF).get_trace())
