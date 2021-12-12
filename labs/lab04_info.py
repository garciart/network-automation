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

    child = utility.connect_via_telnet(device_hostname, device_ip_address, port_number)
    utility.enable_privileged_exec_mode(child, device_hostname)
    utility.format_flash_memory(child, device_hostname)

    print(YLW + "Getting device information...\n" + CLR)
    child.sendline("show version | include [IOSios] [Ss]oftware\r")
    child.expect_exact(prompt_list[1])

    software_ver = str(child.before).split(
        "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
    if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
        raise RuntimeError("Cannot get the device's software version.")
    print(GRN + "Software version: {0}".format(software_ver) + CLR)

    child.sendline("show inventory | include [Cc]hassis\r")
    child.expect_exact(prompt_list[1])

    device_name = str(child.before).split(
        "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Cc]hassis").search(device_name):
        raise RuntimeError("Cannot get the device's name.")
    print(GRN + "Device name: {0}".format(device_name) + CLR)

    child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]\r")
    child.expect_exact(prompt_list[1])

    serial_num = str(child.before).split(
        "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
        raise RuntimeError("Cannot get the device's serial number.")
    print(GRN + "Serial number: {0}".format(serial_num) + CLR)

    utility.close_telnet_connection(child)


if __name__ == "__main__":
    try:
        main("R1", "192.168.1.1", port_number=5001)
    except RuntimeError:
        pass
    except pexpect.TIMEOUT:
        print(RED + "Error: Unable to find the expect search string.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.TIMEOUT).get_trace())
    except pexpect.EOF:
        print(RED + "Error: Child closed unexpectedly.\n" + CLR +
              pexpect.ExceptionPexpect(pexpect.EOF).get_trace())
