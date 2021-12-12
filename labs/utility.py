# -*- coding: utf-8 -*-
"""Lab Utility Module.
Use this module to interact with the operating system, instead of running commands separately.

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import logging
import os
import re
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

__all__ = ["run_cli_commands", "enable_ssh", "disable_ssh", "enable_ftp", "disable_ftp",
           "enable_tftp", "disable_tftp", "set_utc_time", "enable_ntp", "disable_ntp",
           "connect_via_telnet", "enable_privileged_exec_mode", "close_telnet_connection", ]

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filemode="w",
                    # filename="/var/log/utility.log",
                    filename="{0}/utility.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"

CISCO_PROMPTS = [
    ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]


def run_cli_commands(list_of_commands, sudo_password=None):
    """Runs and logs all commands in utility.log. Exceptions must be handled by the
    instantiating module.

    :param list list_of_commands: A list of commands to run through the CLI.
    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the method.
    """
    for c in list_of_commands:
        logging.debug("Command: {0}".format(c))
        command_output, exitstatus = pexpect.run(
            c,
            events={
                "(?i)password": sudo_password if sudo_password is not None else getpass() + "\r"},
            withexitstatus=True)
        logging.debug(
            # For Python 3.x, use unicode_escape.
            # Do not use utf-8; Some characters, such as backticks, will cause exceptions
            "Output:\n{0}\nExit status: {1}\n".format(
                command_output.decode("string_escape").strip(), exitstatus))


def enable_ssh():
    """List of commands to enable the Secure Shell (SSH) Protocol Service.
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --add-service=ssh",
                      "sudo firewall-cmd --zone=public --add-port=22/tcp",
                      "sudo systemctl start sshd", ])


def disable_ssh():
    """List of commands to disable Secure Shell (SSH) Protocol Service.
    """
    run_cli_commands(["sudo systemctl stop sshd",
                      "sudo firewall-cmd --zone=public --remove-port=22/tcp",
                      "sudo firewall-cmd --zone=public --remove-service=ssh", ])


def enable_ftp():
    """List of commands to enable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --add-port=20/tcp",
                      "sudo firewall-cmd --zone=public --add-port=21/tcp",
                      "sudo firewall-cmd --zone=public --add-service=ftp",
                      "sudo sed -i '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                      "echo -e 'ftp_username=nobody' | sudo tee -a /etc/vsftpd/vsftpd.conf",
                      "sudo systemctl start vsftpd", ])


def disable_ftp():
    """List of commands to disable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.
    """
    run_cli_commands(["sudo systemctl stop vsftpd",
                      "sudo sed -i '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                      "sudo firewall-cmd --zone=public --remove-service=ftp",
                      "sudo firewall-cmd --zone=public --remove-port=21/tcp",
                      "sudo firewall-cmd --zone=public --remove-port=20/tcp", ])


def enable_tftp():
    """List of commands to enable the Trivial File Transfer Protocol (TFTP) Service.
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --add-port=69/udp",
                      "sudo firewall-cmd --zone=public --add-service=tftp",
                      "sudo mkdir --parents --verbose /var/lib/tftpboot",
                      "sudo chmod 777 --verbose /var/lib/tftpboot",
                      "sudo systemctl start tftp", ])


def disable_tftp():
    """List of commands to disable the Trivial File Transfer Protocol (TFTP) Service.
    """
    run_cli_commands(["sudo systemctl stop tftp",
                      "sudo firewall-cmd --zone=public --remove-service=tftp",
                      "sudo firewall-cmd --zone=public --remove-port=69/udp", ])


def set_utc_time(new_datetime):
    """Sets the system time without a connection to the Internet. Use before enabling the
    Network Time Protocol (NTP) Service for offline synchronization.

    **Note** - For maximum compatibility with devices, the timezone will be set UTC.

    :param str new_datetime: The desired UTC date and time, in "YYYY-MM-DD HH:MM:SS" format.
    :return: None
    :rtype: None
    :raise RuntimeError: If the desired UTC date and time are in the wrong format.
    """
    import datetime
    try:
        datetime.datetime.strptime(new_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise RuntimeError("Invalid date-time format; expected \"YYYY-MM-DD HH:MM:SS\".")
    run_cli_commands(["sudo timedatectl set-ntp false",
                      "sudo timedatectl set-timezone UTC",
                      "sudo timedatectl set-time \"{0}\"".format(new_datetime),
                      "sudo timedatectl set-local-rtc 0",
                      "sudo date --set \"{0} UTC\"".format(new_datetime), ])


def enable_ntp():
    """List of commands to enable the Network Time Protocol (NTP) Service.
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --add-port=123/udp",
                      "sudo firewall-cmd --zone=public --add-service=ntp",
                      "sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf",
                      "sudo sed -i '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                      "echo -e 'server 127.127.1.0' | sudo tee -a /etc/ntp.conf",
                      "echo -e 'fudge 127.127.1.0 stratum 10' | sudo tee -a /etc/ntp.conf",
                      "sudo systemctl start ntpd", ])


def disable_ntp():
    """List of commands to disable the Network Time Protocol (NTP) Service.
    """
    run_cli_commands(["sudo systemctl stop ntpd",
                      "sudo sed -i '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                      "sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf",
                      "sudo firewall-cmd --zone=public --remove-service=ntp",
                      "sudo firewall-cmd --zone=public --remove-port=123/udp", ])


def connect_via_telnet(device_hostname, device_ip_address, port_number=23):
    """Connect to the device via Telnet.

    :param str device_hostname: The hostname of the device.
    :param str device_ip_address: The IP address that will be used to connect to the device.
    :param int port_number: The port number for the connection.
    """
    print(YLW + "Connecting to device using Telnet...\n" + CLR)
    # Add hostname to standard Cisco prompt endings
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    # Spawn the child and change default settings
    child = pexpect.spawn("telnet {0} {1}".format(device_ip_address, port_number))
    # Slow down commands to prevent race conditions with output
    child.delaybeforesend = 0.5
    # Echo both input and output to the screen
    # child.logfile = sys.stdout
    # Ensure you are not accessing an active session
    try:
        child.expect_exact(prompt_list, timeout=10)
        # If this is a new session, you will not find a prompt
        # If a prompt is found, print the warning and reload
        # Otherwise, catch the TIMEOUT and proceed
        print(RED +
              "You may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect expect calls to fail.\n" +
              "To prevent this, we are reloading this device to clear any artifacts.\n" +
              "Reloading now...\n" + CLR)
        child.sendline("reload\r")
        child.expect_exact("Proceed with reload? [confirm]")
        child.sendline("\r")
        # Expect the child to close
        child.expect_exact([pexpect.EOF, pexpect.TIMEOUT, ])
        exit()
    except pexpect.TIMEOUT:
        # Clear initial questions until a prompt is reached
        while True:
            index = child.expect_exact(
                ["Press RETURN to get started",
                 "Would you like to terminate autoinstall? [yes/no]:",
                 "Would you like to enter the initial configuration dialog? [yes/no]:",
                 "Password:", ] + prompt_list)
            if index == 0:
                child.sendline("\r")
            elif index == 1:
                child.sendline("yes\r")
            elif index == 2:
                child.sendline("no\r")
            elif index == 3:
                # If configured, warn and prompt for a password
                print(YLW + "Warning - This device has already been configured and secured.\n" +
                      "Changes made by this script may be incompatible with the current " +
                      "configuration.\n" + CLR)
                password = getpass()
                child.sendline(password + "\r")
            else:
                # Prompt found; continue script
                break
    print(GRN + "Connected to device using Telnet.\n" + CLR)
    return child


def enable_privileged_exec_mode(child, device_hostname):
    """Enable Privileged EXEC Mode (R1#) from User EXEC mode (R1>).

    **Note** - A reloaded device's prompt  will be either R1> (User EXEC mode) or
    R1# (Privileged EXEC Mode). The enable command will not affect anything if the device
    is already in Privileged EXEC Mode.

    :param pexpect.spawn child: The connection in a child application object.
    :param str device_hostname: The hostname of the device.
    :return: None
    :rtype: None
    """
    print(YLW + "Enabling Privileged EXEC Mode...\n" + CLR)
    # Add hostname to standard Cisco prompt endings
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    child.sendline("enable\r")
    index = child.expect_exact(["Password:", prompt_list[1], ])
    if index == 0:
        password = getpass()
        child.sendline(password + "\r")
        child.expect_exact(prompt_list[1])
    print(GRN + "Privileged EXEC Mode enabled.\n" + CLR)


def close_telnet_connection(child):
    """Close the Telnet client

    :param pexpect.spawn child: The connection in a child application object.
    :return: None
    :rtype: None
    """
    print(YLW + "Closing telnet connection...\n" + CLR)
    child.sendcontrol("]")
    child.sendline("q\r")
    index = child.expect_exact(["Connection closed.", pexpect.EOF, ])
    # Close the Telnet child process
    child.close()
    print(GRN + "Telnet connection closed: {0}\n".format(index) + CLR)


def format_flash_memory(child, device_hostname):
    """Format the flash memory. Look for the final characters of the following strings:

    - "Format operation may take a while. Continue? [confirm]"
    - "Format operation will destroy all data in "flash:".  Continue? [confirm]"
    - "66875392 bytes available (0 bytes used)"

    :param pexpect.spawn child: The connection in a child application object.
    :param str device_hostname: The hostname of the device.
    :return: None
    :rtype: None
    """
    print(YLW + "Formatting flash memory...\n" + CLR)
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    child.sendline("format flash:\r")
    child.expect_exact("Continue? [confirm]")
    child.sendline("\r")
    child.expect_exact("Continue? [confirm]")
    child.sendline("\r")
    child.expect_exact("Format of flash complete", timeout=120)
    child.sendline("show flash\r")
    child.expect_exact("(0 bytes used)")
    child.expect_exact(prompt_list[1])
    print(GRN + "Flash memory formatted.\n" + CLR)


def get_device_information(child, device_hostname):
    """Get the device's flash memory. This will only work after a reload.

    :param pexpect.spawn child: The connection in a child application object.
    :param str device_hostname: The hostname of the device.
    :returns: The device's Internetwork Operating System (IOS) version, model number,
      and serial number.
    :rtype: tuple
    """
    print(YLW + "Getting device information...\n" + CLR)
    prompt_list = ["{0}{1}".format(device_hostname, p) for p in CISCO_PROMPTS]
    child.sendline("show version | include [IOSios] [Ss]oftware\r")
    child.expect_exact(prompt_list[1])

    software_ver = str(child.before).split(
        "show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
    if not re.compile(r"[IOSios] [Ss]oftware").search(software_ver):
        raise RuntimeError("Cannot get the device's software version.")
    print(GRN + "Software version: {0}".format(software_ver) + CLR)

    child.sendline("show inventory | include [Cc]hassis\r")
    child.expect_exact(prompt_list[1])

    device_name = str(child.before).split(
        "show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Cc]hassis").search(device_name):
        raise RuntimeError("Cannot get the device's name.")
    print(GRN + "Device name: {0}".format(device_name) + CLR)

    child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]\r")
    child.expect_exact(prompt_list[1])

    serial_num = str(child.before).split(
        "show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(serial_num):
        raise RuntimeError("Cannot get the device's serial number.")
    print(GRN + "Serial number: {0}".format(serial_num) + CLR)
    return software_ver, device_name, serial_num


if __name__ == "__main__":
    print(RED + "ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])) + CLR)
