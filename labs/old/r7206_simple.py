#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Script.
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

import argparse
import datetime
import hashlib
import os
import shlex
import socket
import subprocess
import sys
import telnetlib
import time

import pexpect

from labs.old import CiscoRouter  # Super class!


class Ramon7206(CiscoRouter):
    # Class variables
    @property
    def device_name(self):
        return "cisco7206"

    PROMPT = "R1>"
    PROMPT_EXEC = "R1#"
    PROMPT_CONFIG = "R1(config)#"
    PROMPT_INTERFACE = "R1(config-if)#"

    def __init__(
            self, config_file_path, device_ip_address, subnet_mask, host_ip_address, **kwargs):
        """Set instance variables and save original Ethernet configuration.

        :param config_file_path:
        :param device_ip_address:
        :param subnet_mask:
        :param host_ip_address:

        :raises FileNotFoundError: blah, blah, blah.
        :raises IndexError: blah, blah, blah.
        :raises RuntimeError: blah, blah, blah.
        """
        self._device_ip_address = Utilities.validate_ip_address(device_ip_address)
        self._subnet_mask = Utilities.validate_subnet_mask(subnet_mask)
        self._config_file_path = Utilities.validate_file_path(config_file_path)
        self._host_ip_address = Utilities.validate_ip_address(host_ip_address)
        self._device_ethernet_interface = kwargs.get(
            "device_ethernet_interface", "FastEthernet0/0")
        current_utc = datetime.datetime.utcnow()
        self._backup_file_path = "r1-config-{0}.cfg".format(current_utc.strftime("%Y-%m-%d-%H%M"))

    def run(self, **kwargs):
        print("Hello from Cisco Ramon!")
        child = None
        # Catch all exceptions here, except for pexpect feedback
        try:
            # self._configure_host(**kwargs)
            child = self._connect_to_device(**kwargs)
            self._configure_device(child, **kwargs)
            self._verify_configuration(**kwargs)
            self._upload_configuration(child, **kwargs)
            self._reload_device(child, **kwargs)
            self._disconnect_from_device(child, **kwargs)
            # self._reset_host(**kwargs)
        except (IndexError, RuntimeError):
            print(self.__exception_message(sys.exc_info()))
        except pexpect.ExceptionPexpect as pex:
            print(self.__exception_message(sys.exc_info(), pex))
        except subprocess.CalledProcessError as cpe:
            print(self.__exception_message(sys.exc_info(), cpe))
        finally:
            # Ensure child is closed
            if child:
                child.close()
            print("Good-bye from Cisco Ramon.")

    @staticmethod
    def __exception_message(exc_info, ex=None):
        e_type, e_value, e_traceback = exc_info
        if e_type.__name__ == "TIMEOUT":
            e_value = "Expected {0}, found {1}".format(
                str(ex).split("searcher_string:\n    0: ")[1].split("\n")[0].strip("\r\n"),
                str(ex).split("before (last 100 chars): ")[1].split("\n")[0].strip("\r\n")
            )
        elif e_type.__name__ == "CalledProcessError":
            e_value = "subprocess results: {0}".format(ex.output)
        return ("Type {0}: {1} in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))

    def _configure_host(self, **kwargs):
        pass

    def _connect_to_device(self, **kwargs):
        print("Connecting to device from host (please wait 15 seconds)...")
        child = None
        index = 0
        while 0 <= index <= 3:
            # FYI - This simulates a console connection. Using child =
            # pexpect.spawn("telnet {0}".format(self._device_ip_address), timeout=10) on a
            # device with an IP address may result in a "Password required, but none set" error
            child = pexpect.spawn("telnet {0} {1}".format(self._host_ip_address, "5001"),
                                  timeout=10)
            time.sleep(15)
            # Send a return to clear any messages
            child.sendline("\r")
            # pexpect will break the loop with an error if the index is not found
            index = child.expect_exact([
                self.PROMPT,
                self.PROMPT_EXEC,
                "Would you like to terminate autoinstall? [yes/no]:",
                "Would you like to enter the initial configuration dialog? [yes/no]:",
                "Continue with configuration dialog? [yes/no]:", ])
            print("Debug: Spawn index = {0}.".format(index))
            if index in [0, 1]:
                print("Debug: Connected to device from host.")
                break
            if index == 2:
                child.sendline("yes\r")
            if index in [3, 4]:
                child.sendline("no\r")
        return child

    def _configure_device(self, child, **kwargs):
        print("Configuring device for file transfer...")
        # Send two returns and enable, in case the device is already in Privileged EXEC Mode
        child.sendline("\r")
        # Enter Privileged EXEC Mode
        child.sendline("enable\r")
        child.expect_exact("R1#")
        # Enter Global Configuration Mode
        child.sendline("configure terminal\r")
        child.expect_exact(self.PROMPT_CONFIG)
        # Enter Interface Configuration Mode
        child.sendline("interface {0}\r".format(self._device_ethernet_interface))
        child.expect_exact(self.PROMPT_INTERFACE)
        # Set the IP address of the router
        child.sendline(
            "ip address {0} {1}\r".format(self._device_ip_address, self._subnet_mask))
        child.expect_exact(self.PROMPT_INTERFACE)
        # Bring up the interface
        child.sendline("no shutdown\r")
        child.expect_exact(self.PROMPT_INTERFACE)
        # Exit Interface Configuration Mode
        child.sendline("exit\r")
        child.expect_exact(self.PROMPT_CONFIG)
        # Configure the default gateway
        child.sendline("ip route 0.0.0.0 0.0.0.0 {0}\r".format(self._host_ip_address))
        child.expect_exact(self.PROMPT_CONFIG)

        # Ensure the router uses F0/0 as the TFTP source interface
        child.sendline(
            "ip tftp source-interface {0}\r".format(self._device_ethernet_interface))
        child.expect_exact(self.PROMPT_CONFIG)
        # Exit Global Configuration Mode
        child.sendline("end\r")
        child.expect_exact("R1#")
        # Save new configuration to flash memory
        child.sendline("write memory\r")
        time.sleep(10)
        child.expect_exact("R1#")
        print("Device configured for file transfer.")

    def _verify_configuration(self, **kwargs):
        print("Verifying device configuration...")
        cmd = "ping -c 4 {0}".format(self._device_ip_address)
        result = subprocess.check_output(shlex.split(cmd))
        if int(result.split("packets transmitted, ")[1].split(" ")[0].strip()) > 0:
            print("Device configuration verified.")
        else:
            raise RuntimeError(
                "Unable to ping {0}: {1}".format(self._device_ip_address, result))

    def _upload_configuration(self, child, **kwargs):
        print("Uploading new configuration file...")
        # Use try-finally to ensure TFTP is diabled even if an error occurs
        # Any exceptions will be caught by the run method
        try:
            # Provide the user with a computed hash for comparison
            self.__get_config_file_hash(self._config_file_path, **kwargs)
            cmd = "sudo ./tftp_service enable {0}".format(self._config_file_path)
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Could not enable the TFTP service.")
            child.sendline("\r")
            child.expect_exact("R1#")
            # nvram:startup-config and system:running-config
            child.sendline("copy tftp: nvram:startup-config:\r")
            child.expect_exact("Address or name of remote host [")
            child.sendline("{0}\r".format(self._host_ip_address))
            child.expect_exact("Source filename [")
            child.sendline("{0}\r".format(self._config_file_path.lstrip("/var/lib/tftpboot/")))
            # child.sendline("{0}\r".format(self._config_file_path))
            child.expect_exact("Destination filename [")
            child.sendline("startup-config\r")
            index = 0
            while 0 <= index <= 2:
                # Do not use pexpect.EOF or pexpect.TIMEOUT. Allow the exception to show what was
                # actually found
                index = child.expect_exact(
                    ["Error",
                     "Do you want to overwrite?",
                     "Password:",
                     "[OK]"], searchwindowsize=100)
                print("Debug: Upload index = {0}.".format(index))
                if index == 0:
                    raise RuntimeError(
                        "Cannot upload new configuration file (upload index {0}".format(index))
                if index == 1:
                    child.sendline("yes\r")
                if index == 2:
                    child.sendline("gns3user\r")
                if index == 3:
                    print("New configuration file uploaded.")
                    break
        finally:
            cmd = "sudo ./tftp_service disable"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Could not disable the TFTP service.")

    @staticmethod
    def __get_config_file_hash(config_file_path, **kwargs):
        print("Computed hashes for {0}:".format(config_file_path))
        blocksize = 65536
        hashes = {
            "hashlib": [hashlib.md5(), hashlib.sha1(), hashlib.sha256()],
            "title": ["MD5 hash", "SHA1 hash", "SHA256 hash"],
        }
        for h, t in zip(hashes["hashlib"], hashes["title"]):
            hasher = h
            with open(config_file_path, "rb") as afile:
                buf = afile.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(blocksize)
            print("{0}: {1}".format(t, hasher.hexdigest()))

    @staticmethod
    def _reload_device(child, **kwargs):
        print("Reloading device...")
        child.sendline("reload\r")
        child.expect_exact("Proceed with reload? [confirm]")
        child.sendline("\r")
        child.expect_exact("Reload requested by console.")
        print("Device reloading (please wait 30 seconds)...")
        time.sleep(30)

    @staticmethod
    def _disconnect_from_device(child, **kwargs):
        print("Disconnecting from device...")
        try:
            child.sendline("exit\r")
            index = child.expect_exact(["Reload", "Press RETURN to get started."])
            if index == 0:
                print("Warning: Possible device reload loop. Stop and restart the device.")
            child.sendcontrol("]")
            child.expect_exact("telnet>")
            child.sendline("quit\r")
            child.expect_exact("Connection closed.")
            print("Disconnected from device.")
        finally:
            child.close()

    def _reset_host(self, **kwargs):
        pass


class Utilities(object):
    # Function return values
    SUCCESS = 0
    FAIL = 1
    ERROR = 2

    @staticmethod
    def validate_file_path(file_path):
        """Checks that the file exists.

        :param file_path: The path to the file.
        :type file_path: str

        :return: The valid file path.
        :rtype: str

        :raises ValueError: If the argument is invalid, or the file permissions are
            incorrect and cannot be reset.
        """
        if file_path is not None and file_path.strip():
            file_path = file_path.strip()
            # Hide stdout, but show stderr; use os.devnull instead of
            # subprocess.DEVNULL in Python 2.7.
            with open(os.devnull, "w") as quiet:
                # Check if file exists
                cmd = "ls {0}".format(file_path)
                retcode = subprocess.call(shlex.split(cmd), stdout=quiet, stderr=quiet)
                if retcode != 0:
                    raise ValueError("{0} does not exist.".format(file_path))
            # Check the file's permissions
            try:
                cmd = "stat -c %a {0}".format(file_path)
                result = subprocess.check_output(shlex.split(cmd))
                if int(result) < 644:
                    cmd = "sudo chmod 644 {0}".format(file_path)
                    retcode = subprocess.call(shlex.split(cmd))
                    if retcode != 0:
                        raise RuntimeError("Cannot change permissions for {0}.".format(
                            file_path))
            except subprocess.CalledProcessError as cpe:
                raise RuntimeError(
                    "Unable to check permissions for {0}: {1}".format(file_path, cpe.output))
            return file_path
        else:
            raise ValueError("Invalid file path: {0}.".format(file_path))

    @staticmethod
    def validate_ip_address(ip_address, ipv4_only=True):
        """Checks that the argument is a valid IP address.

        :param ip_address: The IP address to check.
        :type ip_address: str
        :param ipv4_only: If the method should only validate for IPv4-type
            addresses.
        :type ipv4_only: bool

        :return: The valid IP address.
        :rtype: str

        :raises ValueError: If the argument is invalid.
        """
        if ip_address is not None and ip_address.strip():
            # Check if the IP address is valid (AF_INET for IPv4, AF_INET6 for
            # IPv6); raise an exception if invalid.
            ip_address = ip_address.strip()
            try:
                socket.inet_pton(socket.AF_INET, ip_address)
                return ip_address
            except socket.error:
                if ipv4_only:
                    raise ValueError(
                        "Argument contains an invalid IPv4 address: {0}".format(
                            ip_address))
                else:
                    try:
                        socket.inet_pton(socket.AF_INET6, ip_address)
                        return ip_address
                    except socket.error:
                        raise ValueError(
                            "Argument contains an invalid IP address: {0}".format(
                                ip_address))
        else:
            raise ValueError(
                "Argument contains an invalid IP address: {0}".format(ip_address))

    @staticmethod
    def validate_subnet_mask(subnet_mask):
        """Checks that the argument is a valid subnet mask.

        :param subnet_mask: The subnet mask to check.
        :type subnet_mask: str

        :return: The valid subnet mask.
        :rtype: str

        :raises ValueError: if the argument is invalid.

        .. seealso::
            https://codereview.stackexchange.com/questions/209243/verify-a-subnet-mask-for-validity-in-python
        """
        if subnet_mask is not None and subnet_mask.strip():
            a, b, c, d = (int(octet) for octet in subnet_mask.split("."))
            mask = a << 24 | b << 16 | c << 8 | d
            if mask == 0:
                raise ValueError("Invalid subnet mask: {0}".format(subnet_mask))
            else:
                # Count the number of consecutive 0 bits at the right.
                # https://wiki.python.org/moin/BitManipulation#lowestSet.28.29
                m = mask & -mask
                right0bits = -1
                while m:
                    m >>= 1
                    right0bits += 1
                # Verify that all the bits to the left are 1"s
                if mask | ((1 << right0bits) - 1) != 0xffffffff:
                    raise ValueError(
                        "Invalid subnet mask: {0}".format(subnet_mask))
            return subnet_mask
        else:
            raise ValueError("Invalid subnet mask: {0}.".format(subnet_mask))


if __name__ == "__main__":
    # To maintain scope, create empty class containers here
    r7206 = object()
    cmd = retcode = None

    # Only catch errors and exceptions due to invalid inputs or incorrectly connected devices.
    # Programming and logic errors will be reported and corrected through user feedback
    try:
        print("Running Cisco Ramon...")

        # Initialize default parameter values
        config_file_path = "/var/lib/tftpboot/R1_7206_i1_startup-config.cfg"
        device_ip_address = "192.168.1.20"
        subnet_mask = "255.255.255.0"
        host_ip_address = "192.168.1.1"
        device_ethernet_interface = "FastEthernet0/0"

        # Get parameter values from the command-line
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-x", "--execute",
            help="Run from the command line using the supplied parameter values. " +
                 "Requires config_file_path, device_ip_address, and subnet_mask.")
        parser.add_argument(
            "--config_file_path",
            help="The location of the configuration file to load into the router.")
        parser.add_argument(
            "--device_ip_address",
            help="The IP address for uploading the configuration file to the router.")
        parser.add_argument(
            "--subnet_mask",
            help="The subnet mask that applies to the host and router. " +
                 "Default is {0}.".format(subnet_mask),
            default=subnet_mask)
        parser.add_argument(
            "--host_ip_address",
            help="The IP address of the host. Default is {0}.".format(host_ip_address),
            default=host_ip_address)
        args = parser.parse_args()

        if args.execute:
            # Replace default values with user-supplied values
            config_file_path = args.config_file_path
            device_ip_address = args.device_ip_address
            subnet_mask = args.subnet_mask if args.subnet_mask else subnet_mask
            host_ip_address = args.host_ip_address if args.host_ip_address else host_ip_address
        else:
            print("Warning: You are running this application with default test values.")

        # Instantiate the router object here, since __init__ does not have error-handling code
        r7206 = Ramon7206(
            config_file_path, device_ip_address, subnet_mask, host_ip_address,
            device_ethernet_interface=device_ethernet_interface)

        # TODO: Just for GNS3
        # Check that GNS3 is running; if false, the method will raise an error and the script
        # will exit.
        # Use subprocess here, so the user running the script, if not root, gets prompted for
        # their password
        cmd = "sudo -S pgrep gns3server"  # Returns the process ID
        retcode = subprocess.call(shlex.split(cmd))
        if retcode != 0:
            raise RuntimeError(
                "GNS3 is not running. " +
                "Please run gns3_run to start GNS3 before executing this script.")
        else:
            print("GNS3 is running.")

        # TODO: Just for GNS3
        # Check if the lab is loaded and the device is started
        try:
            # In Lab 0, the unconfigured router is connected to the host through console
            # port 5001 TCP.
            t = telnetlib.Telnet(host_ip_address, "5001", timeout=15)
            if t:
                print("Device reached.")
                t.close()
        except socket.error:
            raise RuntimeError(
                "Unable to reach device. " +
                "Please load Lab 0 in GNS3 and start all devices before executing this script.")

    except (IndexError, RuntimeError, ValueError):
        # Format the error, report, and exit
        e_type, e_value, e_traceback = sys.exc_info()
        print("Error: Type {0}: '{1}' in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))
        print("Good-bye.")
        exit(1)

    # The Ramon object has its own error-handling code
    r7206.run()
    print("Script complete. Have a nice day.")
