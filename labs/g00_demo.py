#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 00: Simple demo.
To run this lab:
* Start GNS3 by executing "./gn3_run.sh" in a Terminal window.
* Select Lab00 from the Projects library.
* Start all devices.

If Lab00 does not exist, follow the instructions in DEMO.md to create the lab.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import logging
import sys
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="labs.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

child = pexpect.spawn("telnet 192.168.1.100 5001")
time.sleep(30)
child.sendline()
child.sendline("enable ! Enter Priviledged EXEC Mode")
child.expect_exact("R1#")
child.sendline("configure terminal ! Enter Global Configuration Mode")
child.expect_exact("R1(config)#")
child.sendline("interface FastEthernet0/0  ! Enter Interface Configuration Mode")
child.expect_exact("R1(config-if)#")
child.sendline("ip address 192.168.1.10 255.255.255.0 ! Set the IP address of the router")
child.expect_exact("R1(config-if)#")
child.sendline("no shutdown ! Bring up the interface")
child.expect_exact("R1(config-if)#")
child.sendline("exit ! Exit Interface Configuration Mode")
child.expect_exact("R1(config)#")
child.sendline("ip route 0.0.0.0 0.0.0.0 192.168.1.100 ! Configure the default gateway")
child.expect_exact("R1(config)#")
child.sendline("end ! Exit Global Configuration Mode")
child.expect_exact("R1#")
child.sendline("write memory ! Save new configuration to flash memory")
child.expect_exact("R1#")
child.sendline("copy running-config startup-config ! Use the current configuration for startup")
child.expect_exact("R1#")
child.sendline("exit")
print("Script complete. Have a nice day.")