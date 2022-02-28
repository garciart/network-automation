# -*- coding: utf-8 -*-
"""Cisco commands class.
Contains Cisco tasks and commands common to more than one script.

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
import logging
import os
import re
import sys
import time
from datetime import datetime
from getpass import getpass

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

# Enable error and exception logging
import pexpect

from labs import utility

logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filemode="w",
                    # For development, use "/var/log/cisco.log"
                    # For production, use datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
                    filename="{0}/cisco-{1}.log".format(
                        os.getcwd(), datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"


class Cisco(object):
    _cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]

    _device_hostname = None
    _device_prompts = None
    _device_ip_addr = None
    _port_number = None
    _vty_username = None
    _vty_password = None
    _console_password = None
    _aux_password = None
    _enable_password = None

    _eol = ""

    def __init__(self, device_hostname,
                 device_ip_addr=None,
                 port_number=23,
                 vty_username=None,
                 vty_password=None,
                 console_password=None,
                 aux_password=None,
                 enable_password=None,
                 eol="\r"):
        """Class instantiation

        :param str device_hostname: The hostname of the device (req).
        :param str device_ip_addr: The device's IP address (req).
        :param int port_number: The port number for the connections.
        :param str vty_username: Username for login local setting.
        :param str vty_password: Password when logging in remotely.
        :param str console_password: Password when logging in using the console port.
        :param str aux_password: Password when logging in using the auxiliary port.
        :param str enable_password: Password to enable Privileged EXEC Mode.
        :return: None
        :rtype: None
        """
        if device_hostname is None or not device_hostname.strip():
            raise ValueError("Device hostname required.")
        else:
            self._device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self._device_prompts = ["{0}{1}".format(device_hostname, p) for p in self._cisco_prompts]
        # The following commands will raise exceptions if invalid
        if device_ip_addr:
            utility.validate_ip_address(device_ip_addr)
        self._device_ip_addr = device_ip_addr
        if port_number:
            utility.validate_port_number(port_number)
        self._port_number = port_number
        self._vty_username = vty_username
        self._vty_password = vty_password
        self._console_password = console_password
        self._aux_password = aux_password
        self._enable_password = enable_password
        self._eol = eol

    def connect_via_telnet(self, device_ip_addr=_device_ip_addr, port_number=_port_number):
        utility.validate_ip_address(device_ip_addr)
        utility.validate_port_number(port_number)
        print("Checking Telnet client is installed...")
        _, exitstatus = pexpect.run("which telnet", withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Telnet client is not installed.")
        print("Telnet client is installed.")
        print("Connecting to {0} on port {1} via Telnet...".format(device_ip_addr, port_number))
        child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
        # Accept changes (e.g., delay, logfile, etc.) to child object
        child = self.clear_startup_msgs(child)
        print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
        return child

    def connect_via_serial(self,
                           serial_device="ttyS0",
                           baud_rate=9600,
                           data_bits=8,
                           parity="n",
                           stop_bit=1,
                           flow_control="N"):
        child = None
        print("Checking if a terminal emulator is installed...")
        _, exitstatus = pexpect.run("which putty", withexitstatus=True)
        if exitstatus != 0:
            _, exitstatus = pexpect.run("which minicom", withexitstatus=True)
            if exitstatus != 0:
                raise RuntimeError("A terminal emulator is not installed.")
            else:
                print("minicom client is installed.")
                # Format: minicom --device /dev/tty0 -baudrate 9600 --8bit
                mode = "--8bit" if data_bits == 8 else "--7bit"
                cmd = "minicom --device {0} --baudrate {1} {2}".format(
                    serial_device, baud_rate, mode)
        else:
            print("PuTTY is installed.")
            # Format: putty -serial /dev/tty0 -sercfg 9600,8,n,1,N
            cmd = "putty -serial {0} -sercfg {1},{2},{3},{4},{5}".format(
                serial_device, baud_rate, data_bits, parity, stop_bit, flow_control)
        print(cmd)
        child = pexpect.spawn(cmd)
        # Accept changes (e.g., delay, logfile, etc.) to child object
        child = self.clear_startup_msgs(child)
        return child

    def clear_startup_msgs(self, child, username=_vty_username, password=_vty_password):
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        # Echo both input and output to the screen
        child.logfile_read = sys.stdout

        # noinspection PyTypeChecker
        index = child.expect_exact([pexpect.TIMEOUT, ] + self._device_prompts, 1)
        if index != 0:
            # If you find a hostname prompt (e.g., R1#) before any other prompt,
            # you are accessing an open line
            print("\x1b[31;1mYou may be accessing an open or uncleared virtual teletype " +
                  "session.\nOutput from previous commands may cause pexpect searches to fail.\n" +
                  "To prevent this in the future, reload the device to clear any artifacts.\x1b[0m")
            # Move the pexpect cursor forward to the newest hostname prompt
            tracer_round = ";{0}".format(int(time.time()))
            # Add the carriage return here, not in the tracer_round.
            # Otherwise, you won't find the tracer_round later
            child.sendline(tracer_round + self._eol)
            child.expect_exact("{0}".format(tracer_round), timeout=1)
        # Always try to find hostname prompts before anything else
        index_offset = len(self._device_prompts)
        while True:
            index = child.expect_exact(
                self._device_prompts +
                ["Login invalid",
                 "Bad passwords",
                 "Username:",
                 "Password:",
                 "Would you like to enter the initial configuration dialog? [yes/no]:",
                 "Would you like to terminate autoinstall? [yes/no]:",
                 "Press RETURN to get started", ], timeout=60)
            if index < index_offset:
                break
            elif index in (index_offset + 0, index_offset + 1):
                raise RuntimeError("Invalid credentials provided.")
            elif index in (index_offset + 2, index_offset + 3):
                print("\x1b[31;1mWarning - This device has already been configured and secured.\n" +
                      "Changes made by this script may be incompatible with the current " +
                      "configuration.\x1b[0m")
                if index == index_offset + 2:
                    # child.sendline(
                    #     (username if username is not None else raw_input("Username: ")) + eol)
                    child.sendline(username)
                    child.expect_exact("Password:")
                    # child.sendline(
                    #       (password if password is not None else getpass(
                    #       "Enter password: ")) + eol)
                child.sendline(password + self._eol)
            elif index == index_offset + 4:
                child.sendline("no" + self._eol)
            elif index == index_offset + 5:
                child.sendline("yes" + self._eol)
            elif index == index_offset + 6:
                child.sendline(self._eol)
        return child


if __name__ == "__main__":
    print("ERROR: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
