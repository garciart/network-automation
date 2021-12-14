# -*- coding: utf-8 -*-
"""Lab Utility Module.
Contains commands common to more than one script.

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
import socket
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

__all__ = ["run_cli_commands", "enable_ssh", "disable_ssh", "enable_ftp", "disable_ftp",
           "enable_tftp", "disable_tftp", "set_utc_time", "enable_ntp", "disable_ntp",
           "validate_ip_address", "validate_port_number", "validate_subnet_mask", ]

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
                "(?i)password": sudo_password if sudo_password is not None else (getpass() + "\r")},
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


def validate_ip_address(ip_address, ipv4_only=True):
    """Checks that the argument is a valid IP address. Causes an exception if invalid.

    :param str ip_address: The IP address to check.
    :param bool ipv4_only: If the method should only validate IPv4-type addresses.

    :raises ValueError: If the IP address is invalid.
    """
    if ip_address is not None and ip_address.strip():
        ip_address = ip_address.strip()
        try:
            socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            if ipv4_only:
                raise ValueError(
                    "Argument contains an invalid IPv4 address: {0}".format(ip_address))
            else:
                try:
                    socket.inet_pton(socket.AF_INET6, ip_address)
                except socket.error:
                    raise ValueError(
                        "Argument contains an invalid IP address: {0}".format(ip_address))
    else:
        raise ValueError("Argument contains an invalid IP address: {0}".format(ip_address))


def validate_port_number(port_number):
    """Check if the port number is within range. Causes an exception if invalid.

    :param int port_number: The port number to check.
    :raises ValueError: if the port number is invalid.
    """
    if port_number not in range(0, 65535):
        raise ValueError("Invalid port number.")


def validate_subnet_mask(subnet_mask):
    """Checks that the argument is a valid subnet mask. Causes an exception if invalid.

    :param str subnet_mask: The subnet mask to check.

    :raises ValueError: if the subnet mask is invalid.

    .. seealso::
        https://codereview.stackexchange.com/questions/209243/verify-a-subnet-mask-for-validity-in-python
    """
    if subnet_mask is not None and subnet_mask.strip():
        subnet_mask = subnet_mask.strip()
        a, b, c, d = (int(octet) for octet in subnet_mask.split("."))
        mask = a << 24 | b << 16 | c << 8 | d
        if mask < 1:
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
                raise ValueError("Invalid subnet mask: {0}".format(subnet_mask))
    else:
        raise ValueError("Invalid subnet mask: {0}.".format(subnet_mask))














if __name__ == "__main__":
    print(RED + "ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])) + CLR)
