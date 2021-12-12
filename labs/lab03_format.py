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

    print(YLW + "Formatting flash memory...\n" + CLR)
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
    child.expect_exact(prompt_list[1])
    print(GRN + "Flash memory formatted.\n" + CLR)

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