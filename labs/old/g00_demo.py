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

import sys
import time

import pexpect

# Module metadata dunders
__author__ = 'Rob Garcia'
__copyright__ = 'Copyright 2020-2021, Rob Garcia'
__email__ = 'rgarcia@rgcoding.com'
__license__ = 'MIT'


def main():
    try:
        child = pexpect.spawn('telnet 192.168.1.200 5001')
        time.sleep(10)
        child.sendline('\r')
        # Enter Privileged EXEC Mode
        child.sendline('enable\r')
        child.expect_exact('R1#', timeout=5)
        print(child.before.decode('utf-8'))
        print(child.after.decode('utf-8'))
        # Enter Global Configuration Mode
        child.sendline('configure terminal\r')
        child.expect_exact('R1(config)#')
        # Enter Interface Configuration Mode
        child.sendline('interface FastEthernet0/0\r')
        child.expect_exact('R1(config-if)#')
        # Set the IP address of the router
        child.sendline('ip address 192.168.1.20 255.255.255.0\r')
        child.expect_exact('R1(config-if)#')
        # Bring up the interface
        child.sendline('no shutdown\r')
        child.expect_exact('R1(config-if)#')
        # Exit Interface Configuration Mode
        child.sendline('exit\r')
        child.expect_exact('R1(config)#')
        # Configure the default gateway
        child.sendline('ip route 0.0.0.0 0.0.0.0 192.168.1.1\r')
        child.expect_exact('R1(config)#')
        # Exit Global Configuration Mode
        child.sendline('end\r')
        child.expect_exact('R1#')
        # Save new configuration to flash memory
        child.sendline('write memory\r')
        time.sleep(10)
        child.expect_exact('R1#')
        # Use the current configuration for startup
        child.sendline('copy running-config startup-config\r')
        child.expect_exact('R1#')
        # Exit Telnet
        child.sendline('exit\r')
        child.expect_exact('Press RETURN to get started.')
        child.sendcontrol(']')
        child.expect_exact('telnet>')
        child.sendline('quit\r')
    except pexpect.exceptions.ExceptionPexpect as ex:
        e_type, e_value, e_traceback = sys.exc_info()
        print("Type {0}: {1} in {2} at line {3}.".format(e_type.__name__,
                                                         e_value,
                                                         e_traceback.tb_frame.f_code.co_filename,
                                                         e_traceback.tb_lineno))
    finally:
        print('Script complete. Have a nice day.')


if __name__ == '__main__':
    main()
