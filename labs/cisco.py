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
                    # For production, use "/var/log/utility.log"
                    filename="{0}/utility.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"


class Cisco:
    _cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]

    _device_hostname = None
    _device_ip_address = None
    _telnet_port = None
    _vty_username = None
    _vty_password = None
    _console_password = None
    _aux_password = None
    _enable_password = None

    # End-of-line (EOL) issue: Depending on the physical port you use (Console, VTY, etc.),
    # AND the port number you use (23, 5001, etc.), Cisco may require a carriage return ("\r")
    # when using pexpect.sendline. Also, each terminal emulator may have different EOL
    # settings. One solution is to edit the terminal emulator's runtime configuration file
    # (telnetrc, minirc, etc) before running this script, then setting or unsetting the
    # telnet transparent setting on the device, but you would have to do this every time.
    # My solution is to send a line and wait for a TIMEOUT. If the command goes through
    # without timing-out, I do not do anything.
    # If I receive a TIMEOUT, I send a CR (which pushes my input through), and I then append
    # a CR to all the rest of my commands.
    _eol = ""

    def __init__(self, device_hostname,
                 device_ip_address,
                 telnet_port=23,
                 vty_username=None,
                 vty_password=None,
                 console_password=None,
                 aux_password=None,
                 enable_password=None):
        """Class instantiation

        :param str device_hostname: The hostname of the device (req).
        :param str device_ip_address: The device's IP address (req).
        :param int telnet_port: The port number for Telnet connections.
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
        # The following commands will raise exceptions if invalid
        utility.validate_ip_address(device_ip_address)
        self._device_ip_address = device_ip_address
        utility.validate_port_number(telnet_port)
        self._telnet_port = telnet_port
        self._vty_username = vty_username
        self._vty_password = vty_password
        self._console_password = console_password
        self._aux_password = aux_password
        self._enable_password = enable_password

    def connect_via_telnet(self, verbose=False):
        """Connect to the device via Telnet.

        :return: The connection in a child application object.
        :rtype: pexpect.spawn
        """
        print(YLW + "Connecting to device using Telnet...\n" + CLR)
        # Allow only one login attempt
        login_attempted = False
        # Add the hostname to the standard Cisco prompt endings
        self._cisco_prompts = [
            "{0}{1}".format(self._device_hostname, p) for p in self._cisco_prompts]
        # Spawn the child and change default settings
        child = pexpect.spawn("telnet {0} {1}".format(self._device_ip_address, self._telnet_port))
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        # Echo both input and output to the screen
        if verbose:
            child.logfile = sys.stdout
        # Ensure you are not accessing an active session
        try:
            child.expect_exact(self._cisco_prompts, timeout=10)
            # If this is a new session, you will not find a prompt. If a prompt is found,
            # print the warning and reload; otherwise, catch the TIMEOUT and proceed.
            print(RED +
                  "You may be accessing an open or uncleared virtual teletype session.\n" +
                  "Output from previous commands may cause pexpect expect calls to fail.\n" +
                  "To prevent this, we are reloading this device to clear any artifacts.\n" +
                  "Reloading now...\n" + CLR)
            # Send command with a carriage return, regardless of the correct EOL
            child.sendline("reload\r")
            child.expect_exact(["Proceed with reload? [confirm]", pexpect.TIMEOUT, ], timeout=5)
            child.sendline("\r")
            raise RuntimeError("Device reloaded for security. Run this script again.")
        except pexpect.TIMEOUT:

            def check_and_warn():
                if login_attempted is True:
                    raise RuntimeError("Invalid credentials provided.")
                print(YLW + "Warning - This device has already been configured and secured.\n" +
                      "Changes made by this script may be incompatible with the current " +
                      "configuration.\n" + CLR)

            # Clear initial questions until a prompt is reached
            while True:
                index = child.expect_exact(
                    ["Press RETURN to get started",
                     "Would you like to terminate autoinstall? [yes/no]:",
                     "Would you like to enter the initial configuration dialog? [yes/no]:",
                     "Username:", "Password:", pexpect.TIMEOUT, ] + self._cisco_prompts)
                if index == 0:
                    child.sendline(self._eol)
                elif index == 1:
                    child.sendline("yes" + self._eol)
                elif index == 2:
                    child.sendline("no" + self._eol)
                elif index == 3:
                    check_and_warn()
                    if self._vty_username is None:
                        raw_input("Username: ")
                    child.sendline(self._vty_username + self._eol)
                elif index == 4:
                    # Not all connections require a username
                    check_and_warn()
                    if self._vty_password is None:
                        getpass()
                    child.sendline(self._vty_password + self._eol)
                    login_attempted = True
                elif index == 5:
                    if self._eol == "":
                        self._eol = "\r"
                        child.sendline(self._eol)
                    else:
                        raise RuntimeError("Cannot determine EOL setting.")
                else:
                    # Prompt found; continue script
                    break
        print(GRN + "Connected to device using Telnet.\n" + CLR)
        return child

    def enable_privileged_exec_mode(self, child):
        """Enable Privileged EXEC Mode (R1#) from User EXEC mode (R1>).

        **Note** - A reloaded device's prompt  will be either R1> (User EXEC mode) or
        R1# (Privileged EXEC Mode). Just in case the device boots into User EXEC mode,
        enable Privileged EXEC ModeThe enable command will not affect anything if the device
        is already in Privileged EXEC Mode.

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        """
        print(YLW + "Enabling Privileged EXEC Mode...\n" + CLR)
        # Add hostname to standard Cisco prompt endings

        child.sendline("disable" + self._eol)
        child.expect_exact(self._cisco_prompts[0])

        child.sendline("enable" + self._eol)
        index = child.expect_exact(["Password:", self._cisco_prompts[1], ])
        if index == 0:
            if self._enable_password is None:
                getpass()
            child.sendline(self._enable_password + self._eol)
            child.expect_exact(self._cisco_prompts[1])
        print(GRN + "Privileged EXEC Mode enabled.\n" + CLR)

    def format_flash_memory(self, child):
        """Format the flash memory. Look for the final characters of the following strings:

        - "Format operation may take a while. Continue? [confirm]"
        - "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        - "66875392 bytes available (0 bytes used)"

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        """
        print(YLW + "Formatting flash memory...\n" + CLR)
        child.sendline("format flash:" + self._eol)
        child.expect_exact("Continue? [confirm]")
        child.sendline(self._eol)
        child.expect_exact("Continue? [confirm]")
        child.sendline(self._eol)
        child.expect_exact("Format of flash complete", timeout=120)
        child.sendline("show flash" + self._eol)
        child.expect_exact("(0 bytes used)")
        child.expect_exact(self._cisco_prompts[1])
        print(GRN + "Flash memory formatted.\n" + CLR)

    def get_device_information(self, child):
        """Get the device's flash memory. This will only work after a reload.

        :param pexpect.spawn child: The connection in a child application object.
        :returns: The device's Internetwork Operating System (IOS) version, model number,
          and serial number.
        :rtype: tuple
        """
        print(YLW + "Getting device information...\n" + CLR)
        child.sendline("show version | include [IOSios] [Ss]oftware" + self._eol)
        child.expect_exact(self._cisco_prompts[1])

        software_ver = str(child.before).split(
            "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
        if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
            raise RuntimeError("Cannot get the device's software version.")
        print(GRN + "Software version: {0}".format(software_ver) + CLR)

        child.sendline("show inventory | include [Cc]hassis" + self._eol)
        child.expect_exact(self._cisco_prompts[1])

        device_name = str(child.before).split(
            "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
        if not re.compile(r"[Cc]hassis").search(device_name):
            raise RuntimeError("Cannot get the device's name.")
        print(GRN + "Device name: {0}".format(device_name) + CLR)

        child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]" + self._eol)
        child.expect_exact(self._cisco_prompts[1])

        serial_num = str(child.before).split(
            "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
        if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
            raise RuntimeError("Cannot get the device's serial number.")
        print(GRN + "Serial number: {0}".format(serial_num) + CLR)
        return software_ver, device_name, serial_num

    def close_telnet_connection(self, child):
        """Close the Telnet client

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        """
        print(YLW + "Closing telnet connection...\n" + CLR)
        child.sendcontrol("]")
        child.sendline("q" + self._eol)
        index = child.expect_exact(["Connection closed.", pexpect.EOF, ])
        # Close the Telnet child process
        child.close()
        print(GRN + "Telnet connection closed: {0}\n".format(index) + CLR)


if __name__ == "__main__":
    print(RED + "ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])) + CLR)
