#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 2: Access a network device's Privileged EXEC Mode

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import sys
import traceback

import pexpect

import labs.lab01_telnet
import labs.lab02_exec_mode

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def main():
    child = None
    try:
        print("Lab 1: Connect to an unconfigured device through the Console port")
        device_hostname = "R1"
        gateway_ip_addr = "192.168.1.1"
        device_console_port = 5002
        console_password = "ciscon"
        child = labs.lab01_telnet.connect(
            device_hostname, gateway_ip_addr, device_console_port, password=console_password)
        print("Lab 2: Lab 2: Access a network device's Privileged EXEC Mode")
        child.sendline("disable\r")
        child.expect_exact(device_hostname + ">")
        enable_password = "cisen"
        child = labs.lab02_exec_mode.enable(child, device_hostname, enable_password)
        child.sendline("configure terminal\r")
        child.expect_exact(device_hostname + "(config)#")
        child.sendline("interface FastEthernet0/0\r")
        child.expect_exact(device_hostname + "(config-if)#")
        child = labs.lab02_exec_mode.enable(child, device_hostname, enable_password)
        labs.lab01_telnet.disconnect(child)
    except (pexpect.ExceptionPexpect, ValueError, RuntimeError, OSError,):
        # Unpack sys.exc_info() to get error information
        e_type, e_value, _ = sys.exc_info()
        # Instantiate the message container
        err_msg = ""
        if e_type in (pexpect.ExceptionPexpect, pexpect.EOF, pexpect.TIMEOUT,):
            # Add a heading to EOF and TIMEOUT errors
            if pexpect.EOF:
                err_msg += "EOF reached: Child process exited unexpectedly.\n"
            elif pexpect.TIMEOUT:
                err_msg += "Timed-out looking for the expected search string.\n"
            # Add trace
            err_msg += pexpect.ExceptionPexpect(e_type).get_trace()
            # For pexpect.run calls...
            if "searcher" not in str(e_value):
                err_msg += (str(e_value).strip("\r\n"))
            # For pexpect.expect-type calls...
            else:
                # Log what was actually found during the pexpect call
                _e_value = "Expected {0}\nFound {1}.".format(
                    str(e_value).split("searcher: ")[1].split("buffer (last 100 chars):")[0].strip(),
                    str(e_value).split("before (last 100 chars): ")[1].split("after:")[0].strip())
                # Remove any unwanted escape characters here, like backspaces, etc.
                e_value = _e_value.replace("\b", "")
                err_msg += _e_value
        elif e_type in (ValueError, RuntimeError, OSError,):
            err_msg += (traceback.format_exc().strip())
        print(err_msg)
    finally:
        # Ensure the child is closed
        if child:
            print("Closing child...")
            child.close()
            print("Child closed.")
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    main()
