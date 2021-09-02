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
import difflib
import hashlib
import logging
import os
import shlex
import socket
import subprocess
import sys
import telnetlib
import time

import pexpect

from labs import CiscoRouter  # Super class!

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="labs.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


class Ramon7206(CiscoRouter):
    # Class variables
    @property
    def device_name(self):
        return "cisco7206"

    PEXPECT_ERROR_MESSAGE = "Type {0}: Expected {1}, found {2} in {3} at line {4}."
    PEXPECT_EXPECTED = "searcher_string:\n    0: "
    PEXPECT_FOUND = "before (last 100 chars): "
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
        self._priority = kwargs.get("priority", 1)
        self._org_eth_config = {
            "name": None,
            "ipv4": None,
            "netmask": None,
            "broadcast": None,
            "ipv6": None,
            "mac": None,
        }
        current_utc = datetime.datetime.utcnow()
        self._backup_file_path = "r1-config-{0}.cfg".format(current_utc.strftime("%Y-%m-%d-%H%M"))

        """
        # Get and save the original Ethernet configuration
        # Use network device names from RHEL 6 (eth), Fedora 15 (em), and RHEL 7 (en)
        eth_interface_name = [i for i in os.listdir("/sys/class/net/") if i.startswith(
            ("em", "en", "eth"))]
        if len(eth_interface_name) < 1:
            raise RuntimeError("No Ethernet interfaces were found. Use ifconfig to diagnose.")
        elif len(eth_interface_name) > 1:
            raise RuntimeError(
                "Multiple Ethernet interfaces were found. " +
                "Please remove all Ethernet connections except for the connection to the device.")
        else:
            # Future: os.popen(
                "ip addr show {0}".format(
                    eth_interface_name[0])).read().split("inet ")[1].split("/")[0]
            eth_config = os.popen("ifconfig {0}".format(eth_interface_name[0])).read()
            self._org_eth_config["name"] = eth_interface_name[0]
            self._org_eth_config["ipv4"] = eth_config.split("inet ")[1].split(" ")[0].strip()
            self._org_eth_config["netmask"] = eth_config.split("netmask ")[1].split(" ")[0].strip()
            self._org_eth_config["broadcast"] = eth_config.split("broadcast ")[1].split(" ")[
                0].strip()
            self._org_eth_config["ipv6"] = eth_config.split("inet6 ")[1].split(" ")[0].strip()
            self._org_eth_config["mac"] = eth_config.split("ether ")[1].split(" ")[0].strip()
        """

    def run(self, ui_messenger, **kwargs):
        ui_messenger.info("Hello from Cisco Ramon!")
        child = None
        # Catch all exceptions here, except for pexpect feedback
        try:
            # self._configure_host(ui_messenger, **kwargs)
            child = self._connect_to_device(ui_messenger, **kwargs)
            self._configure_device(child, ui_messenger, **kwargs)
            self._verify_configuration(ui_messenger, **kwargs)
            self._backup_configuration(child, ui_messenger, **kwargs)
            self._upload_configuration(child, ui_messenger, **kwargs)
            self._reload_device(child, ui_messenger, **kwargs)
            self._disconnect_from_device(child, ui_messenger, **kwargs)
            # self._reset_host(ui_messenger, **kwargs)
        except (RuntimeError, pexpect.ExceptionPexpect):
            ex_type, ex_value, ex_traceback = sys.exc_info()
            ui_messenger.error("Type {0}: {1} in {2} at line {3}.".format(
                ex_type.__name__,
                ex_value,
                ex_traceback.tb_frame.f_code.co_filename,
                ex_traceback.tb_lineno))
        finally:
            # Ensure child is closed
            if child:
                child.close()
            ui_messenger.info("Good-bye from Cisco Ramon.")

    def _configure_host(self, ui_messenger, **kwargs):
        # TODO: PLACEHOLDER CODE ONLY! For the labs, run gns3_run.sh to configure host
        ui_messenger.info("Configuring host for file transfer...")
        cmd = (
            # Add the tap device
            "sudo ip tuntap add tap0 mode tap",
            # Configure the tap
            "sudo ifconfig tap0 0.0.0.0 promisc up",
            # Zero out the default Ethernet connection
            "sudo ifconfig {0} 0.0.0.0 promisc up".format(self._org_eth_config["name"]),
            # Create the bridge
            "sudo brctl addbr br0",
            # Add the tap to the bridge
            "sudo brctl addif br0 tap0",
            # Add the default Ethernet connection to the bridge
            "sudo brctl addif br0 {0}".format(self._org_eth_config["name"]),
            # Start the bridge
            "sudo ifconfig br0 up",
            # Configure the bridge
            "sudo ifconfig br0 {0} netmask {1}".format(self._host_ip_address, self._subnet_mask),
            # Setup the default gateway
            "sudo route add default gw {0}".format(
                self._host_ip_address[:self._host_ip_address.rfind(
                    ".") + 1] + "1"),
        )
        for i, c in enumerate(cmd, 1):
            # ui_messenger.debug(shlex.split(c))
            retcode = subprocess.call(shlex.split(c))
            if retcode != 0:
                raise RuntimeError(
                    "Unable to configure host: Cannot execute {0}".format(c))
        ui_messenger.info("Host configured for file transfer.")

    def _connect_to_device(self, ui_messenger, **kwargs):
        ui_messenger.info("Connecting to device from host (please wait 30 seconds)...")
        # Use local try-expect to capture pexpect feedback, but push RuntimeError to run method
        child = None
        try:
            index = 0
            while 0 <= index <= 3:
                # FYI - This simulates a console connection. Using child =
                # pexpect.spawn("telnet {0}".format(self._device_ip_address), timeout=10) on a
                # device with an IP address may result in a "Password required, but none set" error
                child = pexpect.spawn("telnet {0} {1}".format(self._host_ip_address, "5001"),
                                      timeout=10)
                time.sleep(30)
                # Send a return to clear any messages
                child.sendline("\r")
                # pexpect will break the loop with an error if the index is not found
                index = child.expect_exact([
                    "R1>",
                    "R1#",
                    "Would you like to terminate autoinstall? [yes/no]:",
                    "Would you like to enter the initial configuration dialog? [yes/no]:", ])
                ui_messenger.debug("Spawn index = {0}.".format(index))
                if index in [0, 1]:
                    ui_messenger.debug("Connected to device from host.")
                    break
                if index == 2:
                    child.sendline("yes\r")
                if index == 3:
                    child.sendline("no\r")
            return child
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to connect to device from host.")

    def _configure_device(self, child, ui_messenger, **kwargs):
        ui_messenger.info("Configuring device for file transfer...")
        # Use local try-expect to capture pexpect feedback, but push RuntimeError to run method
        try:
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

            # Generate keys for SCP transfer: 1024 will enable SSH 1.99 and 2048 will enable SSH 2
            child.sendline("crypto key zeroize rsa\r")
            index = 0
            while 0 <= index <= 1:
                index = child.expect_exact(["Do you really want to remove these keys? [yes/no]:",
                                            self.PROMPT_CONFIG])
                if index == 0:
                    child.sendline("yes\r")
                    child.expect_exact(self.PROMPT_CONFIG)
                else:
                    break
            child.sendline("crypto key generate rsa general-keys label gns3user modulus 1024\r\r")
            child.expect_exact(self.PROMPT_CONFIG, timeout=30)
            # Enable secure copy of files from host
            child.sendline("ip scp server enable\r")
            child.expect_exact(self.PROMPT_CONFIG)

            # Have TFTP as a backup if SCP fails
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
            ui_messenger.info("Device configured for file transfer.")
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to configure device for file transfer.")

    def _verify_configuration(self, ui_messenger, **kwargs):
        ui_messenger.info("Verifying device configuration...")
        try:
            cmd = "ping -c 4 {0}".format(self._device_ip_address)
            result = subprocess.check_output(shlex.split(cmd))
            if int(result.split("packets transmitted, ")[1].split(" ")[0].strip()) > 0:
                ui_messenger.info("Device configuration verified.")
            else:
                raise RuntimeError(
                    "Unable to ping {0}: {1}".format(self._device_ip_address, result))
        except subprocess.CalledProcessError as cpe:
            raise RuntimeError(
                "Unable to ping {0}: {1}".format(self._device_ip_address, cpe.output))

    def _backup_configuration(self, child, ui_messenger, **kwargs):
        ui_messenger.info("Backing up configuration file...")
        utility = Utilities()
        # Use try-finally to ensure TFTP is diabled even if an error occurs
        # Any exceptions will be caught by the run method
        try:
            utility.enable_tftp(ui_messenger,
                                upload_filename=self._config_file_path,
                                download_filename=self._backup_file_path)
            child.sendline("\r")
            child.expect_exact("R1#")
            # nvram:startup-config and system:running-config
            child.sendline("copy nvram:startup-config tftp:\r")
            # child.sendline("copy nvram:startup-config scp:\r")
            child.expect_exact("Address or name of remote host [")
            child.sendline("{0}\r".format(self._host_ip_address))
            # child.expect_exact("Destination username [")
            # child.sendline("{0}\r".format("gns3user"))
            child.expect_exact("Destination filename [")
            child.sendline("{0}\r".format(self._backup_file_path))
            # child.sendline("/var/lib/tftpboot/{0}\r".format(self._backup_file_path))
            index = 0
            while 0 <= index <= 2:
                index = child.expect_exact(["Error",
                                            "Do you want to overwrite?",
                                            "Password:",
                                            "bytes copied in"], searchwindowsize=100)
                ui_messenger.debug("Backup index = {0}.".format(index))
                if index == 0:
                    raise RuntimeError(
                        "Cannot upload new configuration file (upload index {0}".format(index))
                if index == 1:
                    child.sendline("yes\r")
                if index == 2:
                    child.sendline("gns3user\r")
                if index == 3:
                    ui_messenger.info("Configuration file backed up.")
                    break
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to backup configuration file.")

        finally:
            utility.disable_tftp(ui_messenger)

    def _upload_configuration(self, child, ui_messenger, **kwargs):
        ui_messenger.info("Uploading new configuration file...")
        utility = Utilities()
        # Use try-finally to ensure TFTP is diabled even if an error occurs
        # Any exceptions will be caught by the run method
        try:
            # Provide the user with a computed hash for comparison
            self.__get_config_file_hash(self._config_file_path, ui_messenger, **kwargs)
            utility.enable_tftp(ui_messenger)

            child.sendline("\r")
            child.expect_exact("R1#")
            # nvram:startup-config and system:running-config
            child.sendline("copy tftp: nvram:startup-config:\r")
            # child.sendline("copy scp: nvram:startup-config:\r")
            child.expect_exact("Address or name of remote host [")
            child.sendline("{0}\r".format(self._host_ip_address))
            # child.expect_exact("Source username [")
            # child.sendline("{0}\r".format("gns3user"))
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
                ui_messenger.debug("Upload index = {0}.".format(index))
                if index == 0:
                    raise RuntimeError(
                        "Cannot upload new configuration file (upload index {0}".format(index))
                if index == 1:
                    child.sendline("yes\r")
                if index == 2:
                    child.sendline("gns3user\r")
                if index == 3:
                    ui_messenger.info("New configuration file uploaded.")
                    break
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to upload configuration file.")

        finally:
            utility.disable_tftp(ui_messenger)

    @staticmethod
    def __get_config_file_hash(config_file_path, ui_messenger, **kwargs):
        ui_messenger.info("Computed hashes for {0}:".format(config_file_path))
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
            ui_messenger.info("{0}: {1}".format(t, hasher.hexdigest()))

    def _reload_device(self, child, ui_messenger, **kwargs):
        ui_messenger.info("Reloading device...")
        # Use local try-expect to capture pexpect feedback, but push RuntimeError to run method
        try:
            child.sendline("reload\r")
            child.expect_exact("Proceed with reload? [confirm]")
            child.sendline("\r")
            child.expect_exact("Reload requested by console.")
            ui_messenger.info("Device reloading (please wait 30 seconds)...")
            time.sleep(30)
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to reload device.")

    def _disconnect_from_device(self, child, ui_messenger, **kwargs):
        ui_messenger.info("Disconnecting from device...")
        # Use local try-expect to capture pexpect feedback, but push RuntimeError to run method
        try:
            child.sendline("exit\r")
            index = child.expect_exact(["Reload", "Press RETURN to get started."])
            if index == 0:
                ui_messenger.warning("Possible device reload loop. Stop and restart the device.")
            child.sendcontrol("]")
            child.expect_exact("telnet>")
            child.sendline("quit\r")
            child.expect_exact("Connection closed.")
            ui_messenger.info("Disconnected from device.")
        except pexpect.ExceptionPexpect as ex:
            # ui_messenger.debug(ex)
            e_type, e_value, e_traceback = sys.exc_info()
            ui_messenger.error(self.PEXPECT_ERROR_MESSAGE.format(
                e_type.__name__,
                str(ex).split(self.PEXPECT_EXPECTED)[1].split("\n")[0].strip("\r\n"),
                str(ex).split(self.PEXPECT_FOUND)[1].split("\n")[0].strip("\r\n"),
                e_traceback.tb_frame.f_code.co_filename,
                e_traceback.tb_lineno
            ))
            raise RuntimeError("Unable to disconnect from device.")
        finally:
            child.close()

    def _reset_host(self, ui_messenger, **kwargs):
        ui_messenger.info("Resetting host to original configuration...")
        # TODO: PLACEHOLDER CODE ONLY! For the labs, run gns3_run.sh to configure host
        # Upon exit from GNS3, reset the default Ethernet connection to access the Internet
        cmd = (
            # Stop the bridge
            "sudo ifconfig br0 down",
            # Remove the default Ethernet connection from the bridge
            "sudo brctl delif br0 {0}".format(self._org_eth_config["name"]),
            # Remove the tap from the bridge
            "sudo brctl delif br0 tap0",
            # Delete the bridge
            "sudo brctl delbr br0",
            # Stop the tap
            "sudo ifconfig tap0 down",
            # Delete the tap
            "sudo ip link delete tap0",
            # Reset the default Ethernet connection
            "sudo ifconfig {0} -promisc".format(self._org_eth_config["name"]),
            "sudo ifconfig {0} {1} up".format(self._org_eth_config["name"],
                                              self._org_eth_config["ipv4"]),
            "sudo ifconfig {0} netmask {1}".format(self._org_eth_config["name"],
                                                   self._org_eth_config["netmask"]),
            "sudo ifconfig {0} broadcast {1}".format(self._org_eth_config["name"],
                                                     self._org_eth_config["broadcast"]),
            # Check your OS; may use service networking restart
            "sudo systemctl restart network",
        )
        ui_messenger.info("Resetting the network (please wait 30 seconds...)")
        for i, c in enumerate(cmd, 1):
            # ui_messenger.debug(shlex.split(c))
            retcode = subprocess.call(shlex.split(c))
            if retcode != 0:
                raise RuntimeError(
                    "Unable to reset host: Cannot execute {0}".format(c))
        ui_messenger.info("Host reset to original configuration.")


class Utilities(object):
    # Class Variables
    TFTP_DIR = "/var/lib/tftpboot"
    TFTP_CONFIG_FILE = "/etc/xinetd.d/tftp"

    # Function return values
    SUCCESS = 0
    FAIL = 1
    ERROR = 2

    @staticmethod
    def validate_file_path(file_path):
        """Checks that the file exists. The private method double_check() takes into account
        misspelled or incorrectly formatted file paths, such as var/lib/tftpbootc7206-config.cfg

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
                    # Double check using ML if the file does not exist
                    best_match = Utilities._double_check(file_path)
                    if best_match is None:
                        raise ValueError("{0} does not exist.".format(file_path))
                    else:
                        file_path = best_match

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
    def _double_check(file_path):
        """Looks for file paths that may have been misspelled or incorrectly
        formatted, such as var/lib/tftpbootc7206-config.cfg

        :param file_path: The path to the file.
        :type file_path: str

        :return: The valid file path or None if not found.
        :rtype: str

        :raises IndexError: If the file type cannot be identified.
        """
        # Get the extension of the file and create a wildcard
        try:
            file_type = "*.{0}".format(file_path.rsplit(".", 1)[1])
        except IndexError:
            return None
        # Create a pool of files with the same extension
        cmd = shlex.split("find / -name '{0}'".format(file_type))
        p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=open(os.devnull, "w"))
        p2 = subprocess.Popen(["grep", "-v", "Permission denied"], stdin=p1.stdout,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        possibilities, err = p2.communicate()
        # Find the best match to the file name within the pool, if any
        if possibilities:
            return \
                difflib.get_close_matches(file_path, possibilities.decode("utf-8").splitlines(),
                                          n=1)[0]

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

    def enable_tftp(self, ui_messenger, upload_filename=None, download_filename=None, **kwargs):
        """This function:

        * Verifies the default TFTP directory exists (/var/lib/tftpboot) and it
          has the correct permissions
        * Enables the TFTP service, opens the firewall, and starts the TFTP server.

        :returns: True if the function succeeded or raises a RuntimeError.
        :rtype: bool

        :raises RuntimeError: If unable to enable the TFTP service.
        """
        rval = self.FAIL
        try:
            ui_messenger.debug("Checking if the tftpboot directory exists...")
            dir_exists = os.path.isdir(self.TFTP_DIR)
            if not dir_exists:
                ui_messenger.warning("tftpboot directory does not exist. Creating...")
                cmd = "sudo mkdir -p -m755 {0}".format(self.TFTP_DIR)
                retcode = subprocess.call(shlex.split(cmd))
                if retcode != 0:
                    raise RuntimeError("Unable to create tftpboot directory.")
                else:
                    ui_messenger.debug("tftpboot directory created.")
            else:
                ui_messenger.debug("Directory exists: Good to go.")

            ui_messenger.debug(
                "Checking the tftpboot directory has correct permissions (i.e., 755+)...")
            try:
                dir_permissions = subprocess.check_output(["stat", "-c", "%a", self.TFTP_DIR])
                if int(dir_permissions) < 755:
                    ui_messenger.warning(
                        "Incorrect permissions for tftpboot directory: Correcting...")
                    cmd = "sudo chmod 755 {0}".format(self.TFTP_DIR)
                    retcode = subprocess.call(shlex.split(cmd))
                    if retcode != 0:
                        raise RuntimeError("Unable to correct tftpboot directory permissions.")
                    else:
                        ui_messenger.debug("tftpboot directory permissions corrected.")
                else:
                    ui_messenger.debug("tftpboot directory permissions correct.")
            except subprocess.CalledProcessError as cpe:
                raise RuntimeError(
                    "Unable to check tftpboot directory permission: {0}".format(cpe.output))

            if upload_filename is not None:
                ui_messenger.debug(
                    "Checking the new configuration file has correct permissions (i.e., 666)...")
                try:
                    file_permissions = subprocess.check_output(
                        ["stat", "-c", "%a", upload_filename])
                    # Permissions must be 666 to write FROM the switch and to send TO the switch
                    if int(file_permissions) < 666:
                        ui_messenger.warning(
                            "Incorrect permissions for new configuration file: Correcting...")
                        cmd = "sudo chmod 666 {0}".format(upload_filename)
                        retcode = subprocess.call(shlex.split(cmd))
                        if retcode != 0:
                            raise RuntimeError(
                                "Unable to correct new configuration file permissions.")
                        else:
                            ui_messenger.debug(
                                "New configuration file permissions corrected.")
                    else:
                        ui_messenger.debug("Configuration file permissions correct: Good to go.")
                except subprocess.CalledProcessError as cpe:
                    raise RuntimeError(
                        "Unable to check new configuration file permission: {0}".format(
                            cpe.output))

            if download_filename is not None:
                ui_messenger.debug("Creating the download destination file...")
                # Permissions must be 666 to write FROM the switch and to send TO the switch
                cmd = ("touch {0}/{1}".format(self.TFTP_DIR, download_filename),
                       "chmod 666 {0}/{1}".format(self.TFTP_DIR, download_filename))
                for i, c in enumerate(cmd, 1):
                    # ui_messenger.debug(shlex.split(c))
                    retcode = subprocess.call(shlex.split(c))
                    if retcode != 0:
                        raise RuntimeError(
                            "Unable to create the download destination file."
                            if i == 1 else
                            "Unable to set download destination file permissions.")
                    else:
                        ui_messenger.debug(
                            "Download destination file created."
                            if i == 1 else
                            "Download destination file permissions set.")

            ui_messenger.debug(
                "Checking the TFTP service config file has correct permissions (i.e., 666+)...")
            try:
                file_permissions = subprocess.check_output(
                    ["stat", "-c", "%a", self.TFTP_CONFIG_FILE])
                if int(file_permissions) < 666:
                    ui_messenger.warning(
                        "Incorrect permissions for TFTP service config file: Correcting...")
                    cmd = "sudo chmod 666 {0}".format(self.TFTP_CONFIG_FILE)
                    retcode = subprocess.call(shlex.split(cmd))
                    if retcode != 0:
                        raise RuntimeError(
                            "Unable to correct TFTP service config file permissions.")
                    else:
                        ui_messenger.debug(
                            "TFTP service config file permissions corrected.")
                else:
                    ui_messenger.debug("Permissions correct: Good to go.")
            except subprocess.CalledProcessError as cpe:
                raise RuntimeError(
                    "Unable to check TFTP service config file permission: {0}".format(
                        cpe.output))

            ui_messenger.debug("Modifying the TFTP service configuration...")
            cmd = (
                "sudo sed -i 's|server_args             = -s {0}" +
                "|server_args             = -c -s {0}|g' /etc/xinetd.d/tftp".format(self.TFTP_DIR),
                "sudo sed -i 's|disable                 = yes" +
                "|disable                 = no|g' /etc/xinetd.d/tftp")
            for i, c in enumerate(cmd, 1):
                # ui_messenger.debug(shlex.split(c))
                retcode = subprocess.call(shlex.split(c))
                if retcode != 0:
                    raise RuntimeError(
                        "Unable to set TFTP configuration to enabled ({0}/2)".format(i))
                else:
                    ui_messenger.debug("TFTP configuration set to enabled ({0}/2)".format(i))

            ui_messenger.debug("Allowing TFTP traffic through firewall...")
            cmd = "sudo firewall-cmd --zone=public --add-service=tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to modify firewall settings.")
            else:
                ui_messenger.debug("Firewall settings modified.")

            ui_messenger.debug("Starting the TFTP server...")
            cmd = "sudo systemctl start tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to start the TFTP service.")
            else:
                ui_messenger.debug("TFTP service started.")

            ui_messenger.debug("Enabling the TFTP server...")
            cmd = "sudo systemctl enable tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to enable the TFTP service.")
            else:
                ui_messenger.debug("TFTP service enabled.")

            ui_messenger.debug("Don\"t forget to reset the TFTP service configuration before " +
                               "shutting down the machine!!!")
            rval = self.SUCCESS
        except RuntimeError:
            rval = self.ERROR
            raise RuntimeError("Unable to enable the TFTP service: {0}".format(sys.exc_info()))
        return rval

    def disable_tftp(self, ui_messenger, **kwargs):
        """Disable the TFTP service, close the firewall, and shutdown the TFTP
        server.

        :returns: If the function succeeded (0); if it failed (1); or if there was
            an error (2).
        :rtype: int

        :raises RuntimeError: If unable to disable the TFTP service.
        """
        rval = self.FAIL
        try:
            # Disable the TFTP service and stop the TFTP server
            ui_messenger.debug("Resetting the TFTP service configuration...")
            cmd = (
                "sudo sed -i 's|server_args             = -c -s {0}" +
                "|server_args             = -s {0}|g' /etc/xinetd.d/tftp".format(self.TFTP_DIR),
                "sudo sed -i 's|disable                 = no" +
                "|disable                 = yes|g' /etc/xinetd.d/tftp")
            for i, c in enumerate(cmd, 1):
                # ui_messenger.debug(shlex.split(c))
                retcode = subprocess.call(shlex.split(c))
                if retcode != 0:
                    raise RuntimeError("Unable to set TFTP settings to disabled ({0}/2)".format(i))
                else:
                    ui_messenger.debug("TFTP settings set to disabled ({0}/2)".format(i))

            ui_messenger.debug(
                "Restoring default permissions for the TFTP service config file (i.e., 644)...")
            cmd = "sudo chmod 644 {0}".format(self.TFTP_CONFIG_FILE)
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError(
                    "Unable to restore TFTP service config file permissions.")
            else:
                ui_messenger.debug("TFTP service config file permissions restored.")

            ui_messenger.debug("Blocking TFTP traffic through firewall...")
            cmd = "sudo firewall-cmd --zone=public --remove-service=tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to modify firewall settings.")
            else:
                ui_messenger.debug("Firewall settings modified.")

            ui_messenger.debug("Stopping the TFTP service...")
            cmd = "sudo systemctl stop tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to stop the TFTP service.")
            else:
                ui_messenger.debug("TFTP service stopped.")

            ui_messenger.debug("Disabling the TFTP service...")
            cmd = "sudo systemctl disable tftp"
            retcode = subprocess.call(shlex.split(cmd))
            if retcode != 0:
                raise RuntimeError("Unable to disable the TFTP service.")
            else:
                ui_messenger.debug("TFTP service disabled.")
            rval = self.SUCCESS
        except RuntimeError:
            rval = self.ERROR
            raise RuntimeError("Unable to disable the TFTP service: {0}".format(sys.exc_info()))
        return rval

    @staticmethod
    def pexpect_run_wrapper(cmd, timeout=30, error_message=None):
        child_result, child_exitstatus = pexpect.run(cmd, timeout=timeout, withexitstatus=True)
        if child_exitstatus == 0:
            return child_result
        else:
            raise RuntimeError(error_message if error_message else child_result.decode("utf-8"))


class UserInterface(object):
    @staticmethod
    def info(msg):
        print("Message: {0}".format(msg))

    @staticmethod
    def debug(msg):
        print("Debug: {0}".format(msg))

    @staticmethod
    def warning(msg):
        print("Warning: {0}".format(msg))

    @staticmethod
    def error(msg):
        print("Error: {0}".format(msg))


if __name__ == "__main__":
    # To maintain scope, create empty class containers here
    ui_messenger = r7206 = object()
    cmd = retcode = None

    # Only catch errors and exceptions due to invalid inputs or incorrectly connected devices.
    # Programming and logic errors will be reported and corrected through user feedback
    try:
        # Instantiate the user interface messaging object here,
        # since it does not have error-handling code
        ui_messenger = UserInterface()
        ui_messenger.info("Running Cisco Ramon...")

        # Initialize default parameter values
        config_file_path = "R1_7206_i1_startup-config.cfg"
        device_ip_address = "192.168.1.10"
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
            ui_messenger.warning("You are running this application with default test values.")

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
            ui_messenger.info("GNS3 is running.")

        # TODO: Just for GNS3
        # Check if the lab is loaded and the device is started
        try:
            # In Lab 0, the unconfigured router is connected to the host through console
            # port 5001 TCP.
            t = telnetlib.Telnet(host_ip_address, "5001", timeout=15)
            if t:
                ui_messenger.info("Device reached.")
                t.close()
        except socket.error:
            raise RuntimeError(
                "Unable to reach device. " +
                "Please load Lab 0 in GNS3 and start all devices before executing this script.")

    except (IndexError, RuntimeError):
        # Format the error, report, and exit
        e_type, e_value, e_traceback = sys.exc_info()
        ui_messenger.error("Type {0}: '{1}' in {2} at line {3}.".format(
            e_type.__name__,
            e_value,
            e_traceback.tb_frame.f_code.co_filename,
            e_traceback.tb_lineno))
        ui_messenger.info("Good-bye.")
        exit(1)

    # The Ramon object has its own error-handling code
    r7206.run(ui_messenger)
    ui_messenger.info("Script complete. Have a nice day.")
