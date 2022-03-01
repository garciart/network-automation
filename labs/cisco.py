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
        ">", "#", "(config)#", "(config-if)#", "(config-line)#", "(config-switch)#",
        "(config-router)#", ]

    _device_hostname = None
    _device_prompts = None
    _device_ip_addr = None
    _port_number = None
    _vty_username = None
    _vty_password = None
    _console_password = None
    _aux_password = None
    _enable_password = None

    _eol = "\r"

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

    def connect_via_telnet(self, device_ip_addr=_device_ip_addr, port_number=_port_number,
                           verbose=True):
        utility.validate_ip_address(device_ip_addr)
        utility.validate_port_number(port_number)
        print("Checking Telnet client is installed...")
        _, exitstatus = pexpect.run("which telnet", withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Telnet client is not installed.")
        print("Telnet client is installed.")
        print("Connecting to {0} on port {1} via Telnet...".format(device_ip_addr, port_number))
        child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile = sys.stdout
        else:
            # Save output to file
            fout = open("{0}-{1}".format(
                self._device_hostname, datetime.utcnow().strftime("%y%m%d-%H%M%SZ")), "wb")
            child.logfile = fout
        # Get to Privileged EXEC Mode
        self._clear_startup_msgs(child)
        self.access_priv_exec_mode(child)
        print("Connected to {0} on port {1} via Telnet.".format(device_ip_addr, port_number))
        return child

    def connect_via_serial(self,
                           serial_device="ttyS0",
                           baud_rate=9600,
                           data_bits=8,
                           parity="n",
                           stop_bit=1,
                           flow_control="N",
                           verbose=True):
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
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile = sys.stdout
        else:
            # Save output to file
            fout = open("{0}-{1}".format(
                self._device_hostname, datetime.utcnow().strftime("%y%m%d-%H%M%SZ")), "wb")
            child.logfile = fout
        # Get to Privileged EXEC Mode
        self._clear_startup_msgs(child)
        self.access_priv_exec_mode(child)
        return child

    def _clear_startup_msgs(self, child, username=_vty_username, password=_vty_password, eol=_eol):
        # MUST BE RUN IMMEDIATELY AFTER PEXPECT.SPAWN!
        # noinspection PyTypeChecker
        index = child.expect_exact([pexpect.TIMEOUT, ] + self._device_prompts, 1)
        if index != 0:
            # If you find a hostname prompt (e.g., R1#) before any other prompt,
            # you are accessing an open line
            print("\x1b[31;1mYou may be accessing an open or uncleared virtual teletype " +
                  "session.\nOutput from previous commands may cause pexpect searches to fail.\n" +
                  "To prevent this in the future, reload the device to clear any artifacts.\x1b[0m")
            self._set_pexpect_cursor(child)
            return
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
                child.sendline(password + eol)
            elif index == index_offset + 4:
                child.sendline("no" + eol)
            elif index == index_offset + 5:
                child.sendline("yes" + eol)
            elif index == index_offset + 6:
                child.sendline(eol)

    def access_priv_exec_mode(self, child, enable_password=_enable_password, eol=_eol):
        self._set_pexpect_cursor(child)

        print("Accessing Privileged EXEC Mode...")
        child.sendline(eol)
        index = child.expect_exact(self._device_prompts, 1)
        if index == 0:
            child.sendline("enable" + eol)
            index = child.expect_exact(["Password:", self._device_prompts[1], ], 1)
            if index == 0:
                child.sendline(enable_password + eol)
                child.expect_exact(self._device_prompts[1], 1)
        elif index != 1:
            child.sendline("end" + eol)
            child.expect_exact(self._device_prompts[1], 1)
        print("Privileged EXEC Mode accessed.")

    def format_memory(self, child, disk_name="flash", eol=_eol):
        self.access_priv_exec_mode(child)

        print("Formatting device memory...")
        # Format the memory. Look for the final characters of the following strings:
        # "Format operation may take a while. Continue? [confirm]"
        # "Format operation will destroy all data in "flash:".  Continue? [confirm]"
        # "66875392 bytes available (0 bytes used)"
        child.sendline("format {0}:".format(disk_name) + eol)
        child.expect_exact("Continue? [confirm]")
        child.sendline(eol)
        child.expect_exact("Continue? [confirm]")
        child.sendline(eol)
        # Not all devices ask for this
        index = child.expect_exact(["Enter volume ID", pexpect.TIMEOUT, ], timeout=1)
        if index == 0:
            child.sendline(eol)
        child.expect_exact("Format of {0} complete".format(disk_name), timeout=120)
        child.sendline("show {0}".format(disk_name) + eol)
        child.expect_exact("(0 bytes used)")
        child.expect_exact(self._device_prompts[1])
        print("Device memory formatted.")

    def get_device_info(self, child, eol=_eol):
        self.access_priv_exec_mode(child)

        print("Getting device information...")
        child.sendline("show version | include [IOSios] [Ss]oftware" + eol)
        child.expect_exact(self._device_prompts[1])

        software_ver = str(child.before).split(
            "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
        if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
            raise RuntimeError("Cannot get the device's software version.")
        print("Software version: {0}".format(software_ver))

        child.sendline("show inventory | include [Cc]hassis" + eol)
        child.expect_exact(self._device_prompts[1])
        # child.expect_exact(device_prompts[1])
        device_name = str(child.before).split(
            "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
        if not re.compile(r"[Cc]hassis").search(device_name):
            raise RuntimeError("Cannot get the device's name.")
        print("Device name: {0}".format(device_name))

        child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]" + eol)
        child.expect_exact(self._device_prompts[1])
        # child.expect_exact(device_prompts[1])
        serial_num = str(child.before).split(
            "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
        if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
            raise RuntimeError("Cannot get the device's serial number.")
        print("Serial number: {0}".format(serial_num))

    def set_device_ip_addr(self, child, new_ip_address, new_netmask="255.255.255.0", commit=True,
                           eol=_eol):
        self.access_priv_exec_mode(child)

        print("Setting the device's IP address...")
        child.sendline("configure terminal" + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("interface FastEthernet0/0" + eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("ip address {0} {1}".format(new_ip_address, new_netmask) + eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("no shutdown" + eol)
        child.expect_exact(self._device_prompts[3])
        child.sendline("end" + eol)
        child.expect_exact(self._device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline("write memory" + eol)
            child.expect_exact(self._device_prompts[1])
        print("Device IP address set.")

    def ping_from_device(self, child, destination_ip_addr, count=4, eol=_eol):
        self.access_priv_exec_mode(child)

        print("Pinging {0}...".format(destination_ip_addr))
        child.sendline("ping {0} repeat {1}".format(destination_ip_addr, count) + eol)
        index = child.expect(["percent (0/4)", r"percent \([1-4]/4\)", ])
        if index == 0:
            raise RuntimeError("Cannot ping {0} from this device.".format(destination_ip_addr))
        print("Pinged {0}.".format(destination_ip_addr))

    @staticmethod
    def ping_device(device_ip_addr, count=4):
        print("Pinging {0}...".format(device_ip_addr))
        _, exitstatus = pexpect.run("ping -c {0} {1}".format(count, device_ip_addr),
                                    withexitstatus=True)
        if exitstatus != 0:
            # No need to read the output. Ping returns a non-zero value if no packets are received
            raise RuntimeError("Cannot ping the device at {0}.".format(device_ip_addr))
        print("Pinged {0}.".format(device_ip_addr))

    def secure_device(self, child, vty_username=_vty_username, vty_password=_vty_password,
                      privilege=15, console_password=_console_password, aux_password=_aux_password,
                      enable_password=_enable_password, commit=True, eol=_eol):
        self.access_priv_exec_mode(child)

        print("Securing the network device...")

        child.sendline("configure terminal" + eol)
        child.expect_exact(self._device_prompts[2])

        # Secure the device with a username and an unencrypted password
        child.sendline("username {0} password {1}".format(vty_username, vty_password) + eol)
        # If the device already is configured with a user secret, you may see:
        # ERROR: Can not have both a user password and a user secret.
        # Please choose one or the other.
        # That is OK for this lab
        child.expect_exact(self._device_prompts[2])

        # Set virtual teletype lines to use device username and password
        child.sendline("line vty 0 4" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("login local" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("exit" + eol)
        child.expect_exact(self._device_prompts[2])

        # Secure console port connections
        child.sendline("line console 0" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("password {0}".format(console_password) + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("login" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("exit" + eol)
        child.expect_exact(self._device_prompts[2])

        # Secure auxiliary port connections
        child.sendline("line aux 0" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("password {0}".format(aux_password) + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("login" + eol)
        child.expect_exact(self._device_prompts[4])
        child.sendline("exit" + eol)
        child.expect_exact(self._device_prompts[2])

        # Secure Privileged EXEC Mode
        child.sendline("enable password {0}".format(enable_password) + eol)
        # If the device already is configured with an enable secret, you may see:
        # The enable password you have chosen is the same as your enable secret.
        # This is not recommended.  Re-enter the enable password.
        # That is OK for this lab
        child.expect_exact(self._device_prompts[2])
        # Test security
        child.sendline("end" + eol)
        child.expect_exact(self._device_prompts[1])
        child.sendline("disable" + eol)
        child.expect_exact(self._device_prompts[0])
        child.sendline("enable" + eol)
        child.expect_exact("Password:")
        child.sendline("{0}".format(enable_password) + eol)
        child.expect_exact(self._device_prompts[1])
        child.sendline("configure terminal" + eol)
        child.expect_exact(self._device_prompts[2])

        # Encrypt the Privileged EXEC Mode password
        child.sendline("no enable password" + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("enable secret {0}".format(enable_password) + eol)
        child.expect_exact(self._device_prompts[2])

        # Encrypt the device's password
        child.sendline(
            "no username {0} password {1}".format(vty_username, vty_password) + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("username {0} privilege {1} secret {2}".format(vty_username, privilege,
                                                                      vty_password) + eol)
        child.expect_exact(self._device_prompts[2])

        # Encrypt the console and auxiliary port passwords
        child.sendline("service password-encryption" + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("end" + eol)
        child.expect_exact(self._device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline("write memory" + eol)
            child.expect_exact(self._device_prompts[1])
        print("Network device secured.")

    def set_clock(self, child, time_to_set="12:00:00 Jan 1 2021", eol=_eol):
        self.access_priv_exec_mode(child)

        print("Setting the network device's clock.")
        child.sendline("clock set {0}".format(time_to_set) + eol)
        child.expect_exact(self._device_prompts[1])
        print("Network device clock set.")

    def synch_clock(self, child, ntp_server_ip, commit=True, eol=_eol):
        self.access_priv_exec_mode(child)

        print("Synchronizing the network device's clock.")
        child.sendline("configure terminal" + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("ntp server {0}".format(ntp_server_ip) + eol)
        child.expect_exact(self._device_prompts[2])
        child.sendline("end" + eol)
        child.expect_exact(self._device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline("write memory" + eol)
            child.expect_exact(self._device_prompts[1])
        print("Waiting 60 seconds for the NTP server to synchronize...")
        time.sleep(60)
        print("Network device clock synchronized.")

    def set_device_hostname(self, child):
        self.access_priv_exec_mode(child)

        print("Changing the device's hostname...")
        print("Device's hostname changed.")

    def _set_pexpect_cursor(self, child, eol=_eol):
        # Move the pexpect cursor forward to the newest hostname prompt
        tracer_round = ";{0}".format(int(time.time()))
        # Add a carriage return here, not in the tracer_round,
        # or you won't find the tracer_round later
        child.sendline(tracer_round + eol)
        child.expect_exact("{0}".format(tracer_round), timeout=1)
        # WATCH YOUR CURSORS! You must also consume the prompt after the tracer round
        # or the pexepect cursor will stop at the wrong prompt
        # The next cursor will stop here -> R2#show version | include [IOSios] [Ss]oftware
        #                                   Cisco IOS Software...
        #      But it needs to stop here -> R2#
        child.expect_exact(self._device_prompts, 1)

    @staticmethod
    def close_telnet(child, eol=_eol):
        print("Closing Telnet connection...")
        child.sendcontrol("]")
        child.expect_exact("telnet>")
        child.sendline("q" + eol)
        child.expect_exact(["Connection closed.", pexpect.EOF, ])
        child.close()
        print("Telnet connection closed")

    @staticmethod
    def close_putty(child):
        print("Closing PuTTY session...")
        child.close()
        print("PuTTY session closed")

    @staticmethod
    def close_ssh(child, device_ip_addr=_device_ip_addr, eol=_eol):
        utility.validate_ip_address(device_ip_addr)
        print("Closing SSH session...")
        child.sendline("~." + eol)
        child.expect_exact(["Connection to {0} closed.".format(device_ip_addr), pexpect.EOF, ])
        child.close()
        print("SSH session closed")


if __name__ == "__main__":
    print("ERROR: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
