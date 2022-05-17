# -*- coding: utf-8 -*-
"""Cisco device class.

Developer notes:
- Protected and private methods (i.e., start with underscores) can be used with multiple devices
- Golden Rule - Start methods that use pexpect with a 'sendline' and finish with an 'expect'

"""
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

        :param str device_hostname: Hostname of the device.
        :return: None
        :rtype: None
        """
        self._device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self._device_prompts = ["{0}{1}".format(device_hostname, p) for p in self._cisco_prompts]

    def _connect_via_telnet(self,
                            device_ip_addr,
                            port_number=None,
                            verbose=True,
                            eol="",
                            username=None,
                            password=None,
                            enable_password=None):
        """Connect to a network device using Telnet.

        :param str device_ip_addr: Device's IP address.
        :param int port_number: Port number for the connections.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file.
        :param str eol: EOL sequence (LF or CRLF) used by the connection (See comments below).
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Connection in a child application object.
        :rtype: pexpect.spawn
        """
        print("Checking Telnet client is installed...")
        _, exitstatus = pexpect.run("which telnet", withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Telnet client is not installed.")
        print("Telnet client is installed.")

        # Validate inputs
        utility.validate_ip_address(device_ip_addr)
        if port_number:
            utility.validate_port_number(port_number)

        print("Connecting to {0} on port {1} via Telnet...".format(device_ip_addr, port_number))
        if port_number:
            child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
        else:
            child = pexpect.spawn("telnet {0}".format(device_ip_addr))

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
        # which will be appended to each sendline.
        self._eol = eol

        # Get to Privileged EXEC Mode
        self.__clear_startup_prompts(child, username, password)
        self.__access_priv_exec_mode(child, enable_password)

        print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
        return child

    # NOTE - Cannot reduce the code complexity of this method in Python 2.7
    # The purpose of trailing NOSONAR comment is to suppress the SonarLint warning
    def __clear_startup_prompts(self, child, username=None, password=None):  # NOSONAR
        """**RUN IMMEDIATELY AFTER PEXPECT.SPAWN!**

        This method clears common Cisco IOS startup messages and prompts until it reaches a
        device prompt (e.g., switch>, switch#, etc.).

        :param pexpect.spawn child: Connection in a child application object.
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.

        :return: None
        :rtype: None
        """
        # Check for a hostname prompt (e.g., switch#) first.
        # If you find a hostname prompt, you have cleared the startup messages.
        # However, if the first thing you find is a hostname prompt, you are accessing
        # an open line. Warn the user, but return control back to the calling method
        # noinspection PyTypeChecker
        index = child.expect_exact([pexpect.TIMEOUT, ] + self._device_prompts, timeout=5)
        if index != 0:
            print("\x1b[31;1mYou may be accessing an open or uncleared virtual teletype " +
                  "session.\nOutput from previous commands may cause pexpect searches to fail.\n" +
                  "To prevent this in the future, reload the device to clear any artifacts.\x1b[0m")
            self.__reset_pexpect_cursor(child)
            return

        # Set initial timeout to 10 minutes to clear startup messages
        timeout = 600
        # If a prompt is not found, attempt to force a prompt by sending a CRLF (see below)
        force_prompt = True
        # Cycle through the startup prompts until you get to a hostname prompt
        index = 0
        while 0 <= index <= 6:
            try:
                index = child.expect_exact(
                    ["Login invalid",
                     "Bad passwords",
                     "Username:",
                     "Password:",
                     "Would you like to enter the initial configuration dialog",
                     "Would you like to terminate autoinstall",
                     "Press RETURN to get started", ] + self._device_prompts, timeout=timeout)
                # Do not use range (it is zero-based and does not assess the high value)
                if index in (0, 1,):
                    raise ValueError("Invalid credentials provided.")
                elif index == 2:
                    if username is None:
                        raise ValueError("Username requested, but none provided.")
                    child.sendline(username + self._eol)
                elif index == 3:
                    if password is None:
                        raise ValueError("Password requested, but none provided.")
                    child.sendline(password + self._eol)
                    print("\x1b[31;1m" +
                          "Warning - This device has already been configured and secured.\n" +
                          "Changes made by this script may be incompatible with the current " +
                          "configuration." +
                          "\x1b[0m")
                elif index == 4:
                    child.sendline("no" + self._eol)
                elif index == 5:
                    child.sendline("yes" + self._eol)
                elif index == 6:
                    child.sendline(self._eol)
                timeout = 60
            except pexpect.TIMEOUT as pex:
                # If no prompt appears, the device may be waiting for input. Send a full CRLF to
                # force; if the prompt still does not appear, then raise an exception
                if force_prompt:
                    child.sendline("\r")
                    force_prompt = False
                else:
                    raise pex

    def __access_priv_exec_mode(self, child, enable_password=None):
        """This method places the pexpect cursor at a Privileged EXEC Mode prompt (e.g., switch#)
        for subsequent commands.

        :param pexpect.spawn child: Connection in a child application object.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None
        """
        print("Accessing Privileged EXEC Mode...")
        self.__reset_pexpect_cursor(child)
        child.sendline(self._eol)
        index = child.expect_exact(self._device_prompts)
        if index == 0:
            # Get out of User EXEC Mode
            child.sendline("enable" + self._eol)
            index = child.expect_exact(["Password:", self._device_prompts[1], ])
            if index == 0:
                child.sendline(enable_password + self._eol)
                child.expect_exact(self._device_prompts[1])
        elif index != 1:
            # Get out of Global Configuration Mode
            child.sendline("end" + self._eol)
            child.expect_exact(self._device_prompts[1])
        print("Privileged EXEC Mode accessed.")

    def __reset_pexpect_cursor(self, child):
        """This method sends a 'tracer round' in the form of a timestamp comment to move the
        pexpect cursor forward to the last hostname prompt.

        :param pexpect.spawn child: Connection in a child application object.

        :return: None
        :rtype: None
        """
        # Wait five seconds to allow any system messages to clear
        time.sleep(5)

        tracer_round = ";{0}".format(int(time.time()))
        # Add the EOL here, not in the tracer_round, or you won't find the tracer_round later
        child.sendline(tracer_round + self._eol)
        child.expect_exact("{0}".format(tracer_round))
        # WATCH YOUR CURSORS! You must also consume the prompt after tracer_round
        # or the pexepect cursor will stop at the wrong prompt
        # The next cursor will stop here -> R2#show version | include [IOSios] [Ss]oftware
        #                                   Cisco IOS Software...
        #      But it needs to stop here -> R2#
        child.expect_exact(self._device_prompts)

    def _get_device_info(self, child, enable_password=None):
        """Get information about the network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Name of the default file system; the device's IOS version; the device's  name;
            and the device's serial number.
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
            default_file_system = str(child.before).split(
                "Directory of ")[1].split(":")[0].strip()
            if not default_file_system.startswith(("bootflash", "flash", "slot", "disk",)):
                raise RuntimeError("Cannot get the device's working drive.")
            print("Default drive: {0}".format(default_file_system))
            index = 0
            while index == 0:
                index = child.expect_exact(["More", pexpect.TIMEOUT], timeout=5)
                if index == 0:
                    child.sendline(self._eol)
        except IndexError as ex:
            print(ex.message)
            default_file_system = None

        try:
            self.__reset_pexpect_cursor(child)
            child.sendline("show version | include [IOSios] [Ss]oftware" + self._eol)
            child.expect_exact(self._device_prompts[1])
            software_ver = str(child.before).split(
                "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
            if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
                raise RuntimeError("Cannot get the device's software version.")
            print("Software version: {0}".format(software_ver))
        except IndexError as ex:
            print(ex.message)
            software_ver = None

        try:
            child.sendline("show inventory | include [Cc]hassis" + self._eol)
            child.expect_exact(self._device_prompts[1])
            device_name = str(child.before).split(
                "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
            if not re.compile(r"[Cc]hassis").search(device_name):
                raise RuntimeError("Cannot get the device's name.")
            print("Device name: {0}".format(device_name))
        except IndexError as ex:
            print(ex.message)
            device_name = None

        try:
            child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]" + self._eol)
            child.expect_exact(self._device_prompts[1])
            serial_num = str(child.before).split(
                "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
            if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
                raise RuntimeError("Cannot get the device's serial number.")
            print("Serial number: {0}".format(serial_num))
        except IndexError as ex:
            print(ex.message)
            serial_num = None

        return default_file_system, software_ver, device_name, serial_num

    def _format_file_system(self, child, file_system):
        """Format a file system (i.e., memory) on a network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param str file_system: File system to format.

        :return: None
        :rtype: None
        """
        # Validate inputs
        if not file_system.startswith(("bootflash", "flash", "slot", "disk", )):
            raise ValueError("Invalid Cisco file system name.")

        print("Formatting device memory...")
        self.__access_priv_exec_mode(child)
        # Format the memory. Look for the final characters of the following strings:
        # "Format operation may take a while. Continue? [confirm]"
        # "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        # "66875392 bytes available (0 bytes used)"
        child.sendline("format {0}:".format(file_system) + self._eol)
        index = 1
        while index != 0:
            index = child.expect_exact(
                [pexpect.TIMEOUT, "Continue? [confirm]", "Enter volume ID", ], timeout=5)
            if index != 0:
                child.sendline(self._eol)
        child.expect_exact("Format of {0} complete".format(file_system), timeout=120)
        child.sendline("show {0}".format(file_system) + self._eol)
        child.expect_exact("(0 bytes used)")
        child.expect_exact(self._device_prompts[1])
        print("Device memory formatted.")

    def _set_device_ip_addr(self, child, ethernet_port, new_ip_address,
                            new_netmask="255.255.255.0", commit=True):
        """Set the device's IP address.

        :param pexpect.spawn child: Connection in a child application object.
        :param str ethernet_port: Ethernet interface port name to configure.
        :param str new_ip_address: New IPv4 address for the device.
        :param str new_netmask: New netmask for the device.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        # Validate inputs
        # ethernet_port, while not validated, should start with F(ast), G(iga), etc.
        utility.validate_ip_address(new_ip_address)
        utility.validate_subnet_mask(new_netmask)

        print("Setting the device's IP address...")

        self.__access_priv_exec_mode(child)
        child.sendline("configure terminal" + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("interface {0}".format(ethernet_port) + self._eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("ip address {0} {1}".format(new_ip_address, new_netmask) + self._eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("no shutdown" + self._eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("end" + self._eol)
        child.expect_exact(self._device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline("write memory" + self._eol)
            child.expect_exact("[OK]")
            child.expect_exact(self._device_prompts[1])
        print("Device IP address set.")

    def _ping_from_device(self, child, destination_ip_addr, count=4):
        """Check the connection to another device.

        :param pexpect.spawn child: Connection in a child application object.
        :param str destination_ip_addr: IPv4 address of the other device.
        :param int count: Number of pings to send.

        :return: None
        :rtype: None
        """
        # Validate inputs
        # ethernet_port, while not validated, should start with F(ast), G(iga), etc.
        utility.validate_ip_address(destination_ip_addr)
        # While the ping count can be greater than 10,
        # restrict to less than 10 when checking connections
        if count < 1 or count >= 32:
            raise ValueError("Ping count is restricted to less than 32 pings.")

        print("Pinging {0}...".format(destination_ip_addr))
        self.__access_priv_exec_mode(child)
        child.sendline("ping {0} repeat {1}".format(destination_ip_addr, count) + self._eol)
        index = child.expect(["percent (0/4)", r"percent \([1-4]/4\)", ])
        if index == 0:
            raise RuntimeError("Cannot ping {0} from this device.".format(destination_ip_addr))
        print("Pinged {0}.".format(destination_ip_addr))

    @staticmethod
    def _ping_device(device_ip_addr, count=4):
        """Check the connection to the device. This command is run from the host computer.

        :param str device_ip_addr: IPv4 address of the device.
        :param int count: Number of pings to send.

        :return: None
        :rtype: None
        """
        print("Pinging {0}...".format(device_ip_addr))
        _, exitstatus = pexpect.run("ping -c {0} {1}".format(count, device_ip_addr),
                                    withexitstatus=True)
        if exitstatus != 0:
            # No need to read the output. Ping returns a non-zero value if no packets are received
            raise RuntimeError("Cannot ping the device at {0}.".format(device_ip_addr))
        print("Pinged {0}.".format(device_ip_addr))

    def _secure_device(self,
                       child,
                       vty_username=None,
                       vty_password=None,
                       privilege=15,
                       console_password=None,
                       aux_password=None,
                       enable_password=None,
                       commit=True):
        """Secure the device. To skip a setting, leave out the parameter or set to None

        :param pexpect.spawn child: Connection in a child application object.
        :param str vty_username: Username for a virtual teletype line connection.
        :param str vty_password: Password for a virtual teletype line connection.
        :param int privilege: Cisco CLI command access level: 1 = Test commands (e.g., ping) only
            with Read-only privileges, 15 = Full access to commands with write privileges
        :param str console_password: Password for a virtual teletype line connection.
        :param str aux_password: Password for a virtual teletype line connection.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        print("Securing the network device...")
        self.__access_priv_exec_mode(child)
        child.sendline("configure terminal" + self._eol)
        child.expect_exact(self._device_prompts[2])

        if vty_username and vty_password:
            # Secure the device with a username and an unencrypted password
            child.sendline(
                "username {0} password {1}".format(vty_username, vty_password) + self._eol)
            # If the device already is configured with a user secret, you may see:
            # "ERROR: Can not have both a user password and a user secret."
            # "Please choose one or the other."
            # That is OK; you encrypt the password later
            child.expect_exact(self._device_prompts[2])

            # Set virtual teletype lines to use device username and password
            child.sendline("line vty 0 4" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("login local" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("exit" + self._eol)
            child.expect_exact(self._device_prompts[2])

            # Encrypt the device's password
            child.sendline(
                "no username {0} password {1}".format(vty_username, vty_password) + self._eol)
            index = 0
            while index == 0:
                # noinspection PyTypeChecker
                index = child.expect_exact(["[confirm]", self._device_prompts[2], ])
                child.sendline(self._eol)
            child.sendline("username {0} privilege {1} secret {2}".format(vty_username, privilege,
                                                                          vty_password) + self._eol)
            child.expect_exact(self._device_prompts[2])

        if console_password:
            # Secure console port connections
            child.sendline("line console 0" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("password {0}".format(console_password) + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("login" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("exit" + self._eol)
            child.expect_exact(self._device_prompts[2])

        if aux_password:
            # Secure auxiliary port connections
            child.sendline("line aux 0" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("password {0}".format(aux_password) + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("login" + self._eol)
            child.expect_exact(self._device_prompts[4])
            child.sendline("exit" + self._eol)
            child.expect_exact(self._device_prompts[2])

        if console_password or aux_password:
            # Encrypt the console and auxiliary port passwords
            child.sendline("service password-encryption" + self._eol)
            child.expect_exact(self._device_prompts[2])

        if enable_password:
            # Secure Privileged EXEC Mode
            child.sendline("enable password {0}".format(enable_password) + self._eol)
            # If the device already is configured with an enable secret, you may see:
            # "The enable password you have chosen is the same as your enable secret."
            # "This is not recommended.  Re-enter the enable password."
            # That is OK; you encrypt the password later
            child.expect_exact(self._device_prompts[2])
            # Test security
            child.sendline("end" + self._eol)
            child.expect_exact(self._device_prompts[1])
            child.sendline("disable" + self._eol)
            child.expect_exact(self._device_prompts[0])
            child.sendline("enable" + self._eol)
            child.expect_exact("Password:")
            child.sendline("{0}".format(enable_password) + self._eol)
            child.expect_exact(self._device_prompts[1])
            child.sendline("configure terminal" + self._eol)
            child.expect_exact(self._device_prompts[2])

            # Encrypt the Privileged EXEC Mode password
            child.sendline("no enable password" + self._eol)
            index = 0
            while index == 0:
                # noinspection PyTypeChecker
                index = child.expect_exact(["[confirm]", self._device_prompts[2], ])
                child.sendline(self._eol)
            child.sendline("enable secret {0}".format(enable_password) + self._eol)
            child.expect_exact(self._device_prompts[2])

        child.sendline("end" + self._eol)
        child.expect_exact(self._device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline("write memory" + self._eol)
            child.expect_exact(self._device_prompts[1])

        print("Network device secured.")

    def _close_telnet(self, child):
        """Close the Telnet connection.

        :param pexpect.spawn child: Connection in a child application object.

        :return: None
        :rtype: None
        """
        print("Closing Telnet connection...")
        child.sendcontrol("]")
        child.expect_exact("telnet>")
        child.sendline("q" + self._eol)
        child.expect_exact(["Connection closed.", pexpect.EOF, ])
        child.close()
        print("Telnet connection closed")

    def _enable_ssh(self, child, label, modulus=1024, version=None, timeout=120, retries=3,
                    commit=True):
        """Enable SSH communications.

        :param pexpect.spawn child: Connection in a child application object.
        :param str label: Name for the Rivest, Shamir, and Adelman (RSA) key pair.
        :param int modulus: Modulus of a certification authority (CA) key.
        :param int version: Force SSH version 1 or 2 (default is 1.99)
        :param int timeout: Wait time for a response from the client before closing the connection.
        :param int retries: Number of SSH authentication retries allowed.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        self.__access_priv_exec_mode(child)
        child.sendline("configure terminal" + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("crypto key zeroize rsa" + self._eol)
        index = child.expect_exact(["Do you really want to remove these keys? [yes/no]:",
                                    self._device_prompts[1]])
        if index == 0:
            child.sendline("yes" + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("crypto key generate rsa general-keys label {0} modulus {1}".format(
            label, modulus) + self._eol)
        child.expect_exact(self._device_prompts[2])
        if version == 1 or version == 2:
            child.sendline("ip ssh version {0}".format(version) + self._eol)
            child.expect_exact(self._device_prompts[2])
        if timeout >= 0:
            child.sendline("ip ssh time-out {0}".format(timeout) + self._eol)
            child.expect_exact(self._device_prompts[2])
        if retries >= 0:
            child.sendline("ip ssh authentication-retries {0}".format(retries) + self._eol)
            child.expect_exact(self._device_prompts[2])
        child.sendline("end" + self._eol)
        child.expect_exact(self._device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline("write memory" + self._eol)
            child.expect_exact(self._device_prompts[1])

    def _set_clock(self, child, time_to_set):
        """Set the device's clock.

        :param pexpect.spawn child: Connection in a child application object.
        :param time_to_set: Time to set on the device

        :return: None
        :rtype: None
        """
        print("Setting the network device's clock.")
        self.__access_priv_exec_mode(child)
        child.sendline("clock set {0}".format(time_to_set) + self._eol)
        child.expect_exact(self._device_prompts[1])
        print("Network device clock set.")

    def _synch_clock(self, child, ntp_server_ip, commit=True):
        """Synchronize the device's clock with an NTP server. Ensure an NTP server is running
        before calling this method.

        :param pexpect.spawn child: Connection in a child application object.
        :param ntp_server_ip: IPv4 address of the NTP server.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        print("Synchronizing the network device's clock.")
        self.__access_priv_exec_mode(child)
        child.sendline("configure terminal" + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("ntp server {0}".format(ntp_server_ip) + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("end" + self._eol)
        child.expect_exact(self._device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline("write memory" + self._eol)
            child.expect_exact(self._device_prompts[1])

        print("Waiting 60 seconds for the NTP server to synchronize...")
        time.sleep(60)
        print("Network device clock synchronized.")

    def _download_from_device_tftp(self, child, ethernet_port, file_to_download,
                                   destination_ip_addr, destination_file_name, commit=True):
        """Download a file form the device using the TFTP protocol.

        Developer Notes:
          - TFTP must be installed: i.e., sudo yum -y install tftp tftp-server.
          - While the destination's TFTP service does not need to be running,
            the firewall ports must allow TFTP traffic.
          - The destination file must ealready exist, even if empty.

        :param pexpect.spawn child: Connection in a child application object.
        :param str ethernet_port: Ethernet interface port name to configure.
        :param str file_to_download: File to download
            (e.g., startup-config, flash:/foo.txt, etc.)
        :param str destination_ip_addr: IPv4 address of the device.
        :param str destination_file_name: Name for the downloaded file (Must already exist,
            even if empty.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        print("Downloading {0} from the device...".format(file_to_download))
        self.__access_priv_exec_mode(child)
        child.sendline("configure terminal" + self._eol)
        child.expect_exact(self._device_prompts[2])

        child.sendline("ip tftp source-interface {0}".format(ethernet_port) + self._eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("end" + self._eol)
        child.expect_exact(self._device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline("write memory" + self._eol)
            child.expect_exact(self._device_prompts[1])

        child.sendline("copy {0} tftp://{1}/{2}".format(
            file_to_download, destination_ip_addr, destination_file_name) + self._eol)
        child.expect_exact("Address or name of remote host")
        child.sendline("{0}".format(destination_ip_addr) + self._eol)
        child.expect_exact("Destination filename")
        child.sendline("{0}".format(destination_file_name) + self._eol)
        index = 0
        while 0 <= index <= 1:
            index = child.expect_exact(["Error",
                                        "Do you want to overwrite?",
                                        "bytes copied in"], timeout=120)
            if index == 0:
                # Get error information between "Error" and the prompt; some hints:
                # Timeout = Port not open or firewall may be closed
                # No such file or directory = Destination file may not exist
                # Undefined error = Destination file permissions may be
                child.expect_exact(self._device_prompts[1])
                raise RuntimeError(
                    "Cannot upload new configuration file: Error {0}".format(child.before))
            if index == 1:
                child.sendline("yes" + self._eol)
        print("{0} downloaded from the device.".format(file_to_download))

    def _upload_to_device_tftp(self, child):
        pass

    def run(self):
        """Configuration sequence goes here

        :return: None
        :rtype: None
        """
        child = None
        try:
            """
            # Use reverse Telnet to connect to the device through the GNS3 server
            child = self._connect_via_telnet("192.168.1.1", 5001, eol="")

            # Get information about the device, especially the default file system
            file_system, software_ver, device_name, serial_num = self._get_device_info(child)
            print(file_system)
            # self._format_file_system(child, file_system=file_system)

            # Enable Layer 3 communications
            self._set_device_ip_addr(child, "Gi1", "192.168.1.20", commit=True)
            self._ping_from_device(child, "192.168.1.10")
            self._ping_device("192.168.1.20")

            # Secure the device. To skip a setting, leave out the parameter or set to None
            self._secure_device(child,
                                vty_username="admin",
                                vty_password="cisco",
                                privilege=15,
                                console_password="ciscon",
                                # aux_password="cisaux",
                                enable_password="cisen",
                                commit=True)

            # Reload the device and close the connection
            child.sendline("reload" + self._eol)
            child.expect_exact("Proceed with reload? [confirm]")
            child.sendline(self._eol))
            self._close_telnet(child)
            print("Device reloading (please wait)...")

            # raw_input("\n\x1b[31;1mMANUALLY RELOAD THE DYNAMIPS DEVICE NOW!\n" +
            #           "Press Enter to continue\x1b[0m\n")
            """

            # Reconnect to the device over Ethernet
            print("Reconnecting...")
            # Allow five minutes for the device to boot up,
            # but poll the device for a connection every 30 seconds
            for try_to_connect in range(10 + 1):
                try:
                    child = self._connect_via_telnet("192.168.1.20", eol="", username="admin",
                                                     password="cisco", enable_password="cisen")
                    break
                except pexpect.EOF:
                    if try_to_connect == 10:
                        raise RuntimeError("Cannot reconnect to device.")
                    time.sleep(30)
            self._ping_from_device(child, "192.168.1.10")
            self._ping_device("192.168.1.20")

            # Enable SSH
            self._enable_ssh(child, "adventures", 1024)
            child.sendline("show ip ssh" + self._eol)
            child.expect_exact(self._device_prompts[1])
            print(child.before)

            sudo_password = "gns3user"

            """
            # Close the Telnet connection and reconnect using SSH
            self._close_telnet(child)
            utility.enable_ssh(sudo_password)
            username = "admin"
            password = "cisco"
            device_ip_address = "192.168.1.20"
            child = pexpect.spawn("ssh {0}:{1}@{2}".format(username, password, device_ip_address))
            """

            # Set and synchronize the device's clock
            utility.enable_ntp(sudo_password)
            child.sendline("show clock" + self._eol)
            child.expect_exact(self._device_prompts[1])
            now = datetime.now()
            self._set_clock(child, now.strftime("%H:%M:%S %b %-d %Y"))
            child.sendline("show clock" + self._eol)
            child.expect_exact(self._device_prompts[1])
            self._synch_clock(child, "192.168.1.10")
            child.sendline("show ntp status" + self._eol)
            child.expect_exact(self._device_prompts[1])
            child.sendline("show clock" + self._eol)
            child.expect_exact(self._device_prompts[1])

            # Transfer files back and forth using TFTP
            utility.enable_tftp(sudo_password)

            ethernet_port = "Gi1"
            file_to_download = "nvram:/startup-config"
            destination_ip_addr = "192.168.1.10"
            destination_file_name = "startup-config.tftp"
            commands = ["sudo touch /var/lib/tftpboot/{0}".format(destination_file_name),
                        "sudo chmod 777 --verbose /var/lib/tftpboot/{0}".format(
                            destination_file_name), ]
            utility.run_cli_commands(commands, sudo_password=sudo_password)

            self._download_from_device_tftp(child, ethernet_port, file_to_download,
                                            destination_ip_addr, destination_file_name, commit=True)

            """
            STOPPED HERE!
            """

            utility.disable_tftp(sudo_password)

            # Transfer files back and forth using FTP
            utility.enable_ftp(sudo_password)

            utility.disable_ftp(sudo_password)

            # Close all connections and services
            self._close_telnet(child)
            utility.disable_ntp(sudo_password)

        finally:
            if child:
                child.close()


if __name__ == "__main__":
    # Cisco 3745 - R1 - flash - eol="\r" - F0/0
    # Cisco 7206 - R2 - disk0 - eol="\r" - F0/0
    # CiscoCSR1000v16.6.1-VIRL-1 - Router - bootflash - eol="" - Gi1
    # CiscoIOSvL215.2.1-1 - Switch - flash0 - eol="" -
    c = CiscoDevice("Router")
    c.run()
    # print("ERROR: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
