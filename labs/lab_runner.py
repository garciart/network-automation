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
import time
import traceback
from datetime import datetime
from getpass import getpass

import pexpect

import labs.lab01_telnet
import labs.lab02_exec_mode
import labs.lab03_format
import labs.lab04_info
import labs.lab05_enable_layer3
import labs.lab06_secure_device
import labs.lab07_clock
from labs.utility import enable_ntp

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


def main():
    # End-of-line (EOL) issue: Depending on the physical port you use (Console, VTY, etc.),
    # AND the port number you use (23, 5001, etc.), Cisco may require a carriage return ("\r")
    # when using pexpect.sendline. Also, each terminal emulator may have different EOL
    # settings. One solution is to edit the terminal emulator's runtime configuration file
    # (telnetrc, minirc, etc) before running this script, then setting or unsetting the
    # telnet transparent setting on the device.
    # Our solution is, based on testing, to append the correct EOL to each sendline.
    eol = "\r"
    child = None
    try:
        print("Lab 1: Connect to an unconfigured device through the Console port")
        device_hostname = "R1"
        gateway_ip_addr = "192.168.1.1"
        device_console_port = 5001
        device_ip_addr = "192.168.1.20"
        device_netmask = "255.255.255.0"
        disk_name = "flash"
        host_ip_addr = "192.168.1.10"
        # Listing of Cisco IOS prompts without a hostname
        cisco_prompts = [
            ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
        # Prepend the hostname to the standard Cisco prompt endings
        device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
        # Include a console port password in case the device is secured.
        # The default console port password for the labs is "ciscon"
        console_password = "ciscon"
        child = labs.lab01_telnet.connect(
            device_hostname, gateway_ip_addr, device_console_port, password=console_password)

        print("Lab 2: Access a network device's Privileged EXEC Mode")
        # Part 1: Enter Privileged EXEC Mode from the device's current mode, whatever it is
        # Include an enable password in case the device is secured.
        # The default enable password for the labs is "cisen"
        enable_password = "cisen"
        labs.lab02_exec_mode.run(child, device_hostname, enable_password)

        # Part 2: Test switching between User EXEC mode and Privileged EXEC Mode
        child.sendline("disable" + eol)
        child.expect_exact(device_prompts[0])
        labs.lab02_exec_mode.run(child, device_hostname, enable_password)

        # Part 2: Test switching between Global Configuration modes and Privileged EXEC Mode
        child.sendline("configure terminal" + eol)
        child.expect_exact(device_prompts[2])
        child.sendline("interface FastEthernet0/0" + eol)
        child.expect_exact(device_prompts[3])
        labs.lab02_exec_mode.run(child, device_hostname, enable_password)

        print("Lab 3: Format a network device's memory")
        # For the Cisco 3745, the disk_name is the default value of "flash",
        # while for the Cisco 7206, the disk_name is "disk0"
        labs.lab03_format.run(child, device_hostname, disk_name=disk_name)

        print("Lab 4: Get information about a network device")
        labs.lab04_info.run(child, device_hostname)

        print("Lab 5: Enable Layer 3 communications to and from a network device")
        # Part 1: Enable Layer 3 communications
        labs.lab05_enable_layer3.run(child, device_hostname, device_ip_addr, new_netmask=device_netmask, commit=True)
        # Part 2: Ping the host from the device
        labs.lab05_enable_layer3.ping_from_device(child, device_ip_addr)
        # Part 3: Ping the device from the host
        labs.lab05_enable_layer3.ping_device(device_ip_addr)

        print("Lab 6: Secure a network device")
        labs.lab06_secure_device.run(child,
                                     device_hostname,
                                     device_username="admin",
                                     device_password="cisco",
                                     privilege=15,
                                     console_password="ciscon",
                                     auxiliary_password="cisaux",
                                     enable_password="cisen",
                                     commit=True)

        # Telnet to the new IP address and repeat Labs 1, 3, 4, and part of 5
        labs.lab01_telnet.disconnect(child)
        child.close()
        # VTY line connections do not need a carriage return!
        child = labs.lab01_telnet.connect(
            device_hostname, device_ip_addr, username="admin", password="cisco", eol="")
        labs.lab02_exec_mode.run(child, device_hostname, enable_password, eol="")
        labs.lab04_info.run(child, device_hostname, eol="")
        # Ping the host from the device
        labs.lab05_enable_layer3.ping_from_device(child, host_ip_addr, eol="")
        # Ping the device from the host
        labs.lab05_enable_layer3.ping_device(device_ip_addr)

        print("Lab 7: Set a network device's clock")
        sudo_password = getpass("Enter the sudo password: ")
        enable_ntp(sudo_password)
        child.sendline("show clock")
        child.expect_exact(device_prompts[1])
        now = datetime.now()
        labs.lab07_clock.set_clock(child, device_hostname, now.strftime("%H:%M:%S %b %-d %Y"), eol="")
        child.sendline("show clock")
        child.expect_exact(device_prompts[1])
        labs.lab07_clock.synch_clock(child, device_hostname, sudo_password, host_ip_addr, eol="")
        child.sendline("show ntp status")
        child.expect_exact(device_prompts[1])
        child.sendline("show clock")
        child.expect_exact(device_prompts[1])

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
                e_value = "Expected {0}\nFound {1}.".format(
                    str(e_value).split("searcher: ")[1].split("buffer (last 100 chars):")[0].strip(),
                    str(e_value).split("before (last 100 chars): ")[1].split("after:")[0].strip())
                # Remove any unwanted escape characters here, like backspaces, etc.
                e_value = e_value.replace("\b", "")
                err_msg += e_value
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
