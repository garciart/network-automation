# -*- coding: utf-8 -*-
"""Lab Utility Class.
Use this class to interact with the operating system, instead of running commands separately.

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import logging
import os
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filemode="w",
                    filename="/var/log/utility.log",
                    # filename="{0}/utility.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


class Utility:
    _sudo_password = None

    def __init__(self, sudo_password=None):
        """Class instantiation

        :param str sudo_password: The superuser password to execute commands that require
            elevated privileges. The user will be prompted for the password if not supplied
            during the call to the method.
        """
        self._sudo_password = (sudo_password if sudo_password is not None else getpass()) + "\r"

    def run(self, list_of_commands):
        """Runs and logs all commands in utility.log. Exceptions must be handled by the
        instantiating module.

        :param list list_of_commands: A list of commands to run through the CLI.
        """
        for c in list_of_commands:
            logging.debug("Command: {0}".format(c))
            command_output, exitstatus = pexpect.run(
                c,
                events={"(?i)password": self._sudo_password},
                withexitstatus=True)
            logging.debug(
                # For Python 3.x, use unicode_escape.
                # Do not use utf-8; Some characters, such as backticks, will cause exceptions
                "Output:\n{0}\nExit status: {1}\n".format(
                    command_output.decode("string_escape").strip(), exitstatus))

    def enable_ssh(self):
        """List of commands to enable the Secure Shell (SSH) Protocol Service.
        """
        self.run(["sudo firewall-cmd --zone=public --add-service=ssh",
                  "sudo firewall-cmd --zone=public --add-port=22/tcp",
                  "sudo systemctl start sshd", ])

    def disable_ssh(self):
        """List of commands to disable Secure Shell (SSH) Protocol Service.
        """
        self.run(["sudo systemctl stop sshd",
                  "sudo firewall-cmd --zone=public --remove-port=22/tcp",
                  "sudo firewall-cmd --zone=public --remove-service=ssh", ])

    def enable_ftp(self):
        """List of commands to enable the Very Secure File Transfer Protocol Daemon (vsftpd)
        service.
        """
        self.run(["sudo firewall-cmd --zone=public --add-port=20/tcp",
                  "sudo firewall-cmd --zone=public --add-port=21/tcp",
                  "sudo firewall-cmd --zone=public --add-service=ftp",
                  "sudo sed -i '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                  "echo -e 'ftp_username=nobody' | sudo tee -a /etc/vsftpd/vsftpd.conf",
                  "sudo systemctl start vsftpd", ])

    def disable_ftp(self):
        """List of commands to disable the Very Secure File Transfer Protocol Daemon (vsftpd)
        service.
        """
        self.run(["sudo systemctl stop vsftpd",
                  "sudo sed -i '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                  "sudo firewall-cmd --zone=public --remove-service=ftp",
                  "sudo firewall-cmd --zone=public --remove-port=21/tcp",
                  "sudo firewall-cmd --zone=public --remove-port=20/tcp", ])

    def enable_tftp(self):
        """List of commands to enable the Trivial File Transfer Protocol (TFTP) Service.
        """
        self.run(["sudo firewall-cmd --zone=public --add-port=69/udp",
                  "sudo firewall-cmd --zone=public --add-service=tftp",
                  "sudo mkdir --parents --verbose /var/lib/tftpboot",
                  "sudo chmod 777 --verbose /var/lib/tftpboot",
                  "sudo systemctl start tftp", ])

    def disable_tftp(self):
        """List of commands to disable the Trivial File Transfer Protocol (TFTP) Service.
        """
        self.run(["sudo systemctl stop tftp",
                  "sudo firewall-cmd --zone=public --remove-service=tftp",
                  "sudo firewall-cmd --zone=public --remove-port=69/udp", ])

    def set_utc_time(self, new_datetime):
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
        self.run(["sudo timedatectl set-ntp false",
                  "sudo timedatectl set-timezone UTC",
                  "sudo timedatectl set-time \"{0}\"".format(new_datetime),
                  "sudo timedatectl set-local-rtc 0",
                  "sudo date --set \"{0} UTC\"".format(new_datetime), ])

    def enable_ntp(self):
        """List of commands to enable the Network Time Protocol (NTP) Service.
        """
        self.run(["sudo firewall-cmd --zone=public --add-port=123/udp",
                  "sudo firewall-cmd --zone=public --add-service=ntp",
                  "sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf",
                  "sudo sed -i '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                  "echo -e 'server 127.127.1.0' | sudo tee -a /etc/ntp.conf",
                  "echo -e 'fudge 127.127.1.0 stratum 10' | sudo tee -a /etc/ntp.conf",
                  "sudo systemctl start ntpd", ])

    def disable_ntp(self):
        """List of commands to disable the Network Time Protocol (NTP) Service.
        """
        self.run(["sudo systemctl stop ntpd",
                  "sudo sed -i '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                  "sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf",
                  "sudo firewall-cmd --zone=public --remove-service=ntp",
                  "sudo firewall-cmd --zone=public --remove-port=123/udp", ])


if __name__ == "__main__":
    print("ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])))
