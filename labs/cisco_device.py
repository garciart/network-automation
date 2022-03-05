# -*- coding: utf-8 -*-
"""Cisco 9500 device class.

Developer notes:
- Protected and private methods (i.e., start with underscores) can be used with multiple devices

"""
import os
import re
import sys
import time
from datetime import datetime

import pexpect

from labs import utility


class CiscoDevice(object):
    _device_hostname = None
    _cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-line)#", "(config-switch)#",
        "(config-router)#", ]
    _device_prompts = None
    _eol = None

    def __init__(self, device_hostname):
        """Class instantiation

        :param str device_hostname: The hostname of the device.
        :return: None
        :rtype: None
        """
        self._device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self._device_prompts = ["{0}{1}".format(device_hostname, p) for p in self._cisco_prompts]

    def _connect_via_telnet(self,
                            device_ip_addr,
                            port_number,
                            verbose=True,
                            eol="",
                            username=None,
                            password=None,
                            enable_password=None):
        """Connect to a network device using Telnet.

        :param str device_ip_addr: The device's IP address.
        :param int port_number: The port number for the connections.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file
        :param str eol: The EOL sequence (LF or CLRF) used by the connection (See comments below).
        :param str username: The username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: The Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: The connection in a child application object.
        :rtype: pexpect.spawn
        """
        print("Checking Telnet client is installed...")
        _, exitstatus = pexpect.run("which telnet", withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Telnet client is not installed.")
        print("Telnet client is installed.")

        # Validate inputs
        utility.validate_ip_address(device_ip_addr)
        utility.validate_port_number(port_number)

        print("Connecting to {0} on port {1} via Telnet...".format(device_ip_addr, port_number))
        child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile_read = sys.stdout
        else:
            # Save output to file
            output_file = open("{0}-{1}".format(
                self._device_hostname, datetime.utcnow().strftime("%y%m%d-%H%M%SZ")), "wb")
            child.logfile = output_file

        # End-of-line (EOL) issues: pexpect.sendline() sends a line feed ("\n") after the text.
        # However, depending on:
        # - The physical port used to connect to the device (e.g., VTY, Console, etc.)
        # - The protocol (e.g., Telnet, SSH, Reverse Telnet, etc.)
        # - The network port (e.g., 23, 2000, 4000, etc.)
        # - The terminal emulator (e.g., PuTTY, Minicom, etc.)
        # - The emulation (e.g., VT100, VT102, ANSI, etc.)
        # The device may require a carriage return ("\r") before the line feed to create a CRLF
        # (i.e., pexpect.sendline("text\r")).
        # Therefore, the user must designate an EOL, based on the connection,
        # which this class will append to each sendline.
        self._eol = eol

        # Get to Privileged EXEC Mode
        self.__clear_startup_msgs(child, username, password)
        self.__access_priv_exec_mode(child, enable_password)

        print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
        return child

    # NOTE - Cannot reduce the code complexity of this method in Python 2.7
    # The purpose of trailing NOSONAR comment is to suppress the SonarLint warning
    def __clear_startup_msgs(self, child, username=None, password=None):  # NOSONAR
        """**RUN IMMEDIATELY AFTER PEXPECT.SPAWN!**

        This method clears common Cisco IOS startup messages until it reaches a
        device prompt (e.g., switch>, switch#, etc.).

        :param pexpect.spawn child: The connection in a child application object.
        :param str username: The username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: The Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.

        :return: None
        :rtype: None
        """
        # Check for a hostname prompt (e.g., switch#) first.
        # If you find a hostname prompt, you have cleared the startup messages.
        # However, if the first thing you find is a hostname prompt, you are accessing
        # an open line. Warn the user, but return control back to the calling method
        # noinspection PyTypeChecker
        index = child.expect_exact([pexpect.TIMEOUT, ] + self._device_prompts, 1)
        if index != 0:
            print("\x1b[31;1mYou may be accessing an open or uncleared virtual teletype " +
                  "session.\nOutput from previous commands may cause pexpect searches to fail.\n" +
                  "To prevent this in the future, reload the device to clear any artifacts.\x1b[0m")
            self.__set_pexpect_cursor(child)
            return

        # Cycle through the startup prompts until you get to a hostname prompt
        index = 0
        while 0 <= index <= 7:
            index = child.expect_exact(
                ["Login invalid",
                 "Bad passwords",
                 "Username:",
                 "Password:",
                 "Would you like to enter the initial configuration dialog? [yes/no]:",
                 "Would you like to terminate autoinstall? [yes/no]:",
                 "Press RETURN to get started",
                 "Escape character is", ] + self._device_prompts, timeout=60)
            # Do not use range (it is zero-based and does not assess the high value)
            if index in (0, 1,):
                raise RuntimeError("Invalid credentials provided.")
            elif index == 2:
                if username is None:
                    raise RuntimeError("Username requested, but none provided.")
                child.sendline(username + self._eol)
            elif index == 3:
                print("\x1b[31;1mWarning - This device has already been configured and secured.\n" +
                      "Changes made by this script may be incompatible with the current " +
                      "configuration.\x1b[0m")
                if password is None:
                    raise RuntimeError("Password requested, but none provided.")
                child.sendline(password + self._eol)
            elif index == 4:
                child.sendline("no" + self._eol)
            elif index == 5:
                child.sendline("yes" + self._eol)
            elif index == 6:
                child.sendline(self._eol)
            elif index == 7:
                # "Escape character is '^]'." is a Telnet prompt, not a device prompt
                child.send("\r")

    def __access_priv_exec_mode(self, child, enable_password=None):
        """This method places the pexpect cursor at a Privileged EXEC Mode prompt (e.g., switch#)
        for subsequent commands.

        :param pexpect.spawn child: The connection in a child application object.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None
        """
        print("Accessing Privileged EXEC Mode...")
        self.__set_pexpect_cursor(child)
        child.sendline(self._eol)
        index = child.expect_exact(self._device_prompts, 1)
        if index == 0:
            # Get out of User EXEC Mode
            child.sendline("enable" + self._eol)
            index = child.expect_exact(["Password:", self._device_prompts[1], ], 1)
            if index == 0:
                child.sendline(enable_password + self._eol)
                child.expect_exact(self._device_prompts[1], 1)
        elif index != 1:
            # Get out of Global Configuration Mode
            child.sendline("end" + self._eol)
            child.expect_exact(self._device_prompts[1], 1)
        print("Privileged EXEC Mode accessed.")

    def __set_pexpect_cursor(self, child):
        """This method sends a 'tracer round' in the form of a timestamp comment to move the
        pexpect cursor forward to the last hostname prompt.

        :param pexpect.spawn child: The connection in a child application object.

        :return: None
        :rtype: None
        """
        # Wait five seconds to allow any system messages to clear
        time.sleep(5)

        tracer_round = ";{0}".format(int(time.time()))
        # Add the EOL here, not in the tracer_round, or you won't find the tracer_round later
        child.sendline(tracer_round + self._eol)
        child.expect_exact("{0}".format(tracer_round), timeout=1)
        # WATCH YOUR CURSORS! You must also consume the prompt after tracer_round
        # or the pexepect cursor will stop at the wrong prompt
        # The next cursor will stop here -> R2#show version | include [IOSios] [Ss]oftware
        #                                   Cisco IOS Software...
        #      But it needs to stop here -> R2#
        child.expect_exact(self._device_prompts, 1)

    def _get_device_info(self, child, enable_password=None):
        """Get information about the network device.

        :param pexpect.spawn child: The connection in a child application object.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: The name of the default file system; the device's IOS version; the device's  name;
            and the device's serial number
        :rtype: tuple
        """
        print("Getting device information...")

        # Get the name of the default file system
        try:
            # Get the name of the default drive. Depending on the device, it may be bootflash,
            # flash, slot (for linear memory cards), or disk (for CompactFlash disks)
            self.__access_priv_exec_mode(child, enable_password)
            child.sendline("dir" + self._eol)
            # If the drive is not formatted, a warning will appear. Wait for it to pass
            child.expect_exact(
                ["before an image can be booted from this device", pexpect.TIMEOUT], timeout=5)
            default_filesystem = str(child.before).split(
                "Directory of ")[1].split(":/\r")[0].strip()
            if not default_filesystem.startswith(("bootflash", "flash", "slot", "disk",)):
                raise RuntimeError("Cannot get the device's working drive.")
            print("Default drive: {0}".format(default_filesystem))
            index = 0
            while index == 0:
                index = child.expect_exact(["More", pexpect.TIMEOUT], 1)
                if index == 0:
                    child.sendline(self._eol)
        except IndexError:
            default_filesystem = None

        try:
            self.__set_pexpect_cursor(child)
            child.sendline("show version | include [IOSios] [Ss]oftware" + self._eol)
            child.expect_exact(self._device_prompts[1])
            software_ver = str(child.before).split(
                "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
            if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
                raise RuntimeError("Cannot get the device's software version.")
            print("Software version: {0}".format(software_ver))
        except IndexError:
            software_ver = None

        try:
            child.sendline("show inventory | include [Cc]hassis" + self._eol)
            child.expect_exact(self._device_prompts[1])
            # child.expect_exact(device_prompts[1])
            device_name = str(child.before).split(
                "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
            if not re.compile(r"[Cc]hassis").search(device_name):
                raise RuntimeError("Cannot get the device's name.")
            print("Device name: {0}".format(device_name))
        except IndexError:
            device_name = None

        try:
            child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]" + self._eol)
            child.expect_exact(self._device_prompts[1])
            # child.expect_exact(device_prompts[1])
            serial_num = str(child.before).split(
                "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
            if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
                raise RuntimeError("Cannot get the device's serial number.")
            print("Serial number: {0}".format(serial_num))
        except IndexError:
            serial_num = None

        return default_filesystem, software_ver, device_name, serial_num

    def run(self):
        """Configuration sequence goes here

        :return: None
        :rtype: None
        """
        child = None
        try:
            child = self._connect_via_telnet("192.168.1.1", 5001, eol="\r")
            filesystem, software_ver, device_name, serial_num = self._get_device_info(child)
            print(filesystem)
        finally:
            if child:
                child.close()


if __name__ == "__main__":
    c = CiscoDevice("R1")
    c.run()
    # print("ERROR: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
