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

import pexpect


def run(child,
        device_hostname,
        device_username="",
        device_password="",
        privilege=15,
        console_password="",
        auxiliary_password="",
        enable_password="",
        commit=True):
    print("Securing the network device...")

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
    # The next cursor will stop here -> R2#configure terminal
    #                       Not here -> R2#
    child.expect_exact(device_prompts[1], 1)

    child.sendline("configure terminal\r")
    child.expect_exact(device_prompts[2])

    # Secure the device with a username and an unencrypted password
    child.sendline("username {0} password {1}\r".format(device_username, device_password))
    # If the device already is configured with a user secret, you may see:
    # ERROR: Can not have both a user password and a user secret.
    # Please choose one or the other.
    # That is OK for this lab
    child.expect_exact(device_prompts[2])

    # Set virtual teletype lines to use device username and password
    child.sendline("line vty 0 4\r")
    child.expect_exact(device_prompts[5])
    child.sendline("login local\r")
    child.expect_exact(device_prompts[5])
    child.sendline("exit\r")
    child.expect_exact(device_prompts[2])

    # Secure console port connections
    child.sendline("line console 0\r")
    child.expect_exact(device_prompts[5])
    child.sendline("password {0}\r".format(console_password))
    child.expect_exact(device_prompts[5])
    child.sendline("login\r")
    child.expect_exact(device_prompts[5])
    child.sendline("exit\r")
    child.expect_exact(device_prompts[2])

    # Secure auxiliary port connections
    child.sendline("line aux 0\r")
    child.expect_exact(device_prompts[5])
    child.sendline("password {0}\r".format(auxiliary_password))
    child.expect_exact(device_prompts[5])
    child.sendline("login\r")
    child.expect_exact(device_prompts[5])
    child.sendline("exit\r")
    child.expect_exact(device_prompts[2])

    # Secure Privileged EXEC Mode
    child.sendline("enable password {0}\r".format(enable_password))
    # If the device already is configured with an enable secret, you may see:
    # The enable password you have chosen is the same as your enable secret.
    # This is not recommended.  Re-enter the enable password.
    # That is OK for this lab
    child.expect_exact(device_prompts[2])
    # Test security
    child.sendline("end\r")
    child.expect_exact(device_prompts[1])
    child.sendline("disable\r")
    child.expect_exact(device_prompts[0])
    child.sendline("enable\r")
    child.expect_exact("Password:")
    child.sendline("{0}\r".format(enable_password))
    child.expect_exact(device_prompts[1])
    child.sendline("configure terminal\r")
    child.expect_exact(device_prompts[2])

    # Encrypt the Privileged EXEC Mode password
    child.sendline("no enable password\r")
    child.expect_exact(device_prompts[2])
    child.sendline("enable secret {0}\r".format(enable_password))
    child.expect_exact(device_prompts[2])

    # Encrypt the device's password
    child.sendline("no username {0} password {1}\r".format(device_username, device_password))
    child.expect_exact(device_prompts[2])
    child.sendline("username {0} privilege {1} secret {2}\r".format(device_username, privilege, device_password))
    child.expect_exact(device_prompts[2])

    # Encrypt the console and auxiliary port passwords
    child.sendline("service password-encryption\r")
    child.expect_exact(device_prompts[2])
    child.sendline("end\r")
    child.expect_exact(device_prompts[1])

    # Save changes if True
    if commit:
        child.sendline("write memory\r")
        child.expect_exact(device_prompts[1])
    print("Network device secured.\r")
    return child


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))