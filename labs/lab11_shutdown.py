#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 11: Shutdown clients and services

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

# ANSI Color Constants
CLR = "\x1b[0m"
RED = "\x1b[31;1m"
GRN = "\x1b[32m"
YLW = "\x1b[33m"


def run(eol="\r"):
    """A G-d Object. For training only; I know its cognitive complexity is in the hundreds and
    there are WAY too many comments.

    :return: None
    :rtype: None

    :raise RuntimeError: If anything goes wrong.
    """
    print("Shutting down clients and services...")

    print()

    print("Shutting down Telnet...")
    # Clear incoming and outgoing text before using getpass()
    time.sleep(0.5)
    command_output, exit_status = pexpect.run(
        "sudo firewall-cmd --zone=public --remove-port=23/tcp",
        events={"(?i)password": getpass() + eol},
        withexitstatus=True)
    if exit_status != 0:
        raise RuntimeError(command_output.strip())
    print(GRN + "Telnet port closed." + CLR)

    print()

    print("Shutting down FTP...")
    # Clear incoming and outgoing text before using getpass()
    time.sleep(0.5)
    sudo_password = getpass()
    list_of_commands = ["sudo firewall-cmd --zone=public --remove-port=21/tcp",
                        "sudo firewall-cmd --zone=public --remove-service=ftp",
                        "sudo systemctl stop vsftpd", ]
    for c in list_of_commands:
        command_output, exit_status = pexpect.run(
            c,
            events={"(?i)password": sudo_password + eol},
            withexitstatus=True)
        if exit_status != 0:
            raise RuntimeError(command_output.strip())
    print(GRN + "FTP service stopped and ports closed." + CLR)

    print()

    print("Shutting down NTP...")
    # Clear incoming and outgoing text before using getpass()
    time.sleep(0.5)
    sudo_password = getpass()
    list_of_commands = ["sudo firewall-cmd --zone=public --remove-port=123/udp",
                        "sudo firewall-cmd --zone=public --remove-service=ntp",
                        "sudo systemctl stop ntpd",
                        "sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf", ]
    for c in list_of_commands:
        command_output, exit_status = pexpect.run(
            c,
            events={"(?i)password": sudo_password + eol},
            withexitstatus=True)
        if exit_status != 0:
            raise RuntimeError(command_output.strip())
    print(GRN + "NTP service stopped and ports closed." + CLR)

    print()

    print("Shutting down TFTP...")
    # Clear incoming and outgoing text before using getpass()
    time.sleep(0.5)
    sudo_password = getpass()
    list_of_commands = ["sudo firewall-cmd --zone=public --remove-port=69/udp",
                        "sudo firewall-cmd --zone=public --remove-service=tftp",
                        "sudo systemctl stop tftp", ]
    for c in list_of_commands:
        command_output, exit_status = pexpect.run(
            c,
            events={"(?i)password": sudo_password + eol},
            withexitstatus=True)
        if exit_status != 0:
            raise RuntimeError(command_output.strip())
    print(GRN + "TFTP service stopped and ports closed." + CLR)

    print()

    print("Clients and services shut down.")


if __name__ == "__main__":
    raise RuntimeError("Run script {0} with lab_runner.py.\n" +
                       "To run {0} independently, add main function with arguments.".format(sys.argv[0]))
