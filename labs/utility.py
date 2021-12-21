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

import hashlib
import logging
import os
import socket
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

__all__ = ["run_cli_commands", "open_telnet_port", "close_telnet_port", "enable_ssh",
           "disable_ssh", "enable_ftp", "disable_ftp",
           "enable_tftp", "disable_tftp", "set_utc_time", "enable_ntp", "disable_ntp",
           "validate_ip_address", "validate_port_number", "validate_subnet_mask",
           "validate_filepath", "get_file_hash", ]

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filemode="w",
                    # Use /var/log/utility.log for production
                    filename="{0}/utility.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"


def run_cli_commands(list_of_commands, sudo_password=None):
    """Runs and logs all commands in utility.log. Exceptions must be handled by the
    instantiating module.

    :param list list_of_commands: A list of commands to run through the CLI.
    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the method.
    :return: None
    :rtype: None
    """
    for c in list_of_commands:
        logging.debug("Command: {0}".format(c))
        command_output, exitstatus = pexpect.run(
            c,
            events={
                "(?i)password": sudo_password if sudo_password is not None else (getpass() + "\r")},
            withexitstatus=True)
        logging.debug(
            # For Python 2.x, use string_escape.
            # For Python 3.x, use unicode_escape.
            # Do not use utf-8; Some characters, such as backticks, will cause exceptions
            "Output:\n{0}\nExit status: {1}\n".format(
                command_output.decode("string_escape").strip(), exitstatus))


def open_telnet_port(sudo_password):
    """List of commands to open the Telnet port.

    :return: None
    :rtype: None
    """
    run_cli_commands(["which telnet",
                      "sudo firewall-cmd --zone=public --add-port=23/tcp", ],
                     sudo_password)


def close_telnet_port(sudo_password):
    """List of commands to close the Telnet port.

    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --remove-port=23/tcp", ],
                     sudo_password)


def enable_ssh(sudo_password):
    """List of commands to enable the Secure Shell (SSH) Protocol Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["which sshd",
                      "sudo firewall-cmd --zone=public --add-service=ssh",
                      "sudo firewall-cmd --zone=public --add-port=22/tcp",
                      "sudo systemctl start sshd", ],
                     sudo_password)


def disable_ssh(sudo_password):
    """List of commands to disable Secure Shell (SSH) Protocol Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl stop sshd",
                      "sudo firewall-cmd --zone=public --remove-port=22/tcp",
                      "sudo firewall-cmd --zone=public --remove-service=ssh", ],
                     sudo_password)


def enable_ftp(sudo_password):
    """List of commands to enable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :return: None
    :rtype: None
    """
    run_cli_commands([
        "which vsftpd",
        "sudo firewall-cmd --zone=public --add-port=20/tcp",
        "sudo firewall-cmd --zone=public --add-port=21/tcp",
        "sudo firewall-cmd --zone=public --add-service=ftp",
        "sudo sed --in-place '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
        "sed --in-place --expression '\\$aftp_username=nobody' /etc/vsftpd/vsftpd.conf",
        "sudo systemctl start vsftpd", ],
        sudo_password)


def disable_ftp(sudo_password):
    """List of commands to disable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl stop vsftpd",
                      "sudo sed --in-place '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                      "sudo firewall-cmd --zone=public --remove-service=ftp",
                      "sudo firewall-cmd --zone=public --remove-port=21/tcp",
                      "sudo firewall-cmd --zone=public --remove-port=20/tcp", ],
                     sudo_password)


def enable_tftp(sudo_password):
    """List of commands to enable the Trivial File Transfer Protocol (TFTP) Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["which tftp",
                      "sudo firewall-cmd --zone=public --add-port=69/udp",
                      "sudo firewall-cmd --zone=public --add-service=tftp",
                      "sudo mkdir --parents --verbose /var/lib/tftpboot",
                      "sudo chmod 777 --verbose /var/lib/tftpboot",
                      "sudo systemctl start tftp", ],
                     sudo_password)


def disable_tftp(sudo_password):
    """List of commands to disable the Trivial File Transfer Protocol (TFTP) Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl stop tftp",
                      "sudo firewall-cmd --zone=public --remove-service=tftp",
                      "sudo firewall-cmd --zone=public --remove-port=69/udp", ],
                     sudo_password)


def set_utc_time(new_datetime, sudo_password):
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
    try:
        run_cli_commands(["which timedatectl",
                          "sudo timedatectl set-ntp false",
                          "sudo timedatectl set-timezone UTC",
                          "sudo timedatectl set-time \"{0}\"".format(new_datetime),
                          "sudo timedatectl set-local-rtc 0", ],
                         sudo_password)
    finally:
        run_cli_commands(["sudo date --set \"{0} UTC\"".format(new_datetime), ],
                         sudo_password)


def enable_ntp(sudo_password):
    """List of commands to enable the Network Time Protocol (NTP) Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["which ntpd",
                      "sudo firewall-cmd --zone=public --add-port=123/udp",
                      "sudo firewall-cmd --zone=public --add-service=ntp",
                      "sudo sed --in-place '/server 127.127.1.0/d' /etc/ntp.conf",
                      "sudo sed --in-place '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                      "sed --in-place --expression '\\$aserver 127.127.1.0' /etc/ntp.conf",
                      "sed --in-place --expression '\\$afudge 127.127.1.0 stratum 10' /etc/ntp.conf",
                      "sudo systemctl start ntpd", ],
                     sudo_password)


def disable_ntp(sudo_password):
    """List of commands to disable the Network Time Protocol (NTP) Service.

    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl stop ntpd",
                      "sudo sed --in-place '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                      "sudo sed --in-place '/server 127.127.1.0/d' /etc/ntp.conf",
                      "sudo firewall-cmd --zone=public --remove-service=ntp",
                      "sudo firewall-cmd --zone=public --remove-port=123/udp", ],
                     sudo_password)


def validate_ip_address(ip_address, ipv4_only=True):
    """Checks that the argument is a valid IP address. Causes an exception if invalid.

    :param str ip_address: The IP address to check.
    :param bool ipv4_only: If the method should only validate IPv4-type addresses.
    :return: None
    :rtype: None
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
    :return: None
    :rtype: None
    :raises ValueError: if the port number is invalid.
    """
    if port_number not in range(0, 65535):
        raise ValueError("Invalid port number.")


def validate_subnet_mask(subnet_mask):
    """Checks that the argument is a valid subnet mask. Causes an exception if invalid.

    :param str subnet_mask: The subnet mask to check.
    :return: None
    :rtype: None
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


def validate_filepath(filepath):
    """Check if the filepath exists. Causes an exception if invalid.

    :param str filepath: The filepath to check.
    :return: None
    :rtype: None
    :raises ValueError: if the filepath is invalid.
    """
    if not os.path.exists(filepath):
        raise ValueError("Invalid filepath.")


def get_file_hash(filepaths):
    """Hash a file.

    :param list filepaths: The files to be hashed.
    :return: A dictionary of hashes for the file.
    :rtype: dict
    :raises ValueError: if the filepath mask is invalid.
    """
    if not isinstance(filepaths, list):
        filepaths = [filepaths, ]
    file_hashes = {}
    for f in filepaths:
        if not os.path.exists(f):
            raise ValueError("Invalid filepath.")
        for a in hashlib.algorithms:
            try:
                h = hashlib.new(a)
                # noinspection PyTypeChecker
                h.update(open(f, "rb").read())
                file_hashes.update({a: h.hexdigest()})
            except ValueError:
                file_hashes.update({a: False})
    logging.info(file_hashes)
    return file_hashes


if __name__ == "__main__":
    print(RED + "ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])) + CLR)
