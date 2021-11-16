#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 1: Set up the Host's Linux Environment

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


def main():
    """A G-d Object. For training only; I know its cognitive complexity is in the hundreds and
    there are WAY too many comments.

    :return: None
    :rtype: None

    :raise RuntimeError: If anything goes wrong.
    """
    print("Setting up the host's Linux environment...\n")
    # Create the child here so it can be closed in the finally block if there is an error
    child = None
    try:
        # Check if Telnet is installed
        print("Checking if Telnet is installed...")
        # Send the command
        child = pexpect.spawn("which telnet")
        # Look for a search string
        index = child.expect_exact(["/telnet", "no telnet", pexpect.EOF, pexpect.TIMEOUT, ])
        # 0 = Telnet installed
        # 1 = Telnet is not installed
        # 2 = (EOF) The command or arguments (i.e., "which telnet") are invalid and
        #     the child has closed
        # 3 = (TIMEOUT) None of the expected search string were not found
        if index == 1:
            raise RuntimeError("Script halted: Telnet client is not installed.")
        elif index == 2:
            raise RuntimeError("Script halted: Unable to run the command as written.")
        elif index == 3:
            raise RuntimeError("Script halted: Expected search string not found.")
        else:
            # Ooooh! Sprucing up messages with colors!
            print(GRN + "Telnet is installed." + CLR)

        print()

        # You cannot run "which scp" in the same child as "which telnet". You will receive an EOF,
        # since the child (i.e., "which telnet") closed when it finished its job; it will close
        # implicitly, whether you close it explicitly (e.g., "child.close()", etc.) or not
        print("Checking if SCP is installed (the wrong way)...")
        child.sendline("which scp\r")
        index = child.expect_exact(["/scp", "no scp", pexpect.EOF, pexpect.TIMEOUT, ])
        # Pexpect will raise an EOF exception
        if index == 2:
            # Just an example; do not throw an exception
            print(RED + "Cannot run \"which scp\" on an implicitly closed child." + CLR)
        else:
            raise RuntimeError("Oops! I was wrong!")

        print()

        # The correct way is to create a new child. As I said, child.close() is not really needed,
        # since the child was closed implicitly when the command finished running
        child.close()
        print("Checking if SCP is installed (the right way)...")
        child = pexpect.spawn("which scp")
        index = child.expect_exact(["/scp", "no scp", pexpect.EOF, pexpect.TIMEOUT, ])
        if index == 1:
            raise RuntimeError("Script halted: SCP program is not installed.")
        elif index == 2:
            raise RuntimeError("Script halted: Unable to run the command as written.")
        elif index == 3:
            raise RuntimeError("Script halted: Expected search string not found.")
        else:
            print(GRN + "SCP is installed." + CLR)

        print()

        # Now, for an easier way. pexpect.run() will use its exit status to see if the commands
        # worked (0) or not (greater than 0)
        print("Checking if the required clients and services are installed (the short way)...")
        list_of_commands = [
            "which telnet", "which scp", "which ntpd", "which tftp", "which vsftpd", "which sshd", ]
        for c in list_of_commands:
            command_output, exit_status = pexpect.run(c, withexitstatus=True)
            if exit_status != 0:
                raise RuntimeError(command_output.strip())
            else:
                print(GRN + "{0}: Program installed.".format(c) + CLR)

        print()

        # This is what happens if pexpect.run() finds an error
        print("This will cause an error: There is no foo...")
        command_output, exit_status = pexpect.run("which foo", withexitstatus=True)
        if exit_status != 0:
            # Just an example; do not throw an exception
            print(RED + command_output.strip() + CLR)

        print()

        print("Checking service statuses...")
        list_of_commands = ["systemctl status ntpd",
                            "systemctl status tftp",
                            "systemctl status vsftpd",
                            "systemctl status sshd", ]
        for c in list_of_commands:
            command_output, exit_status = pexpect.run(c, withexitstatus=True)
            if exit_status != 0:
                print(YLW + "{0}: Service not installed or loaded.".format(c) + CLR)
            else:
                print(GRN + "{0}: Service active.".format(c) + CLR)

        print()

        # What if you try to run a command that requires a password?
        # pexpect.run() will timeout after 30 seconds
        print(
            "Trying to run a command as sudo without providing a password " +
            YLW + "(default timeout is 30 seconds)" + CLR + "...")
        command_output, exit_status = pexpect.run(
            "sudo firewall-cmd --zone=public --add-port=20/tcp",
            withexitstatus=True)
        if exit_status != 0:
            # Just an example; do not throw an exception
            print(RED + "{0}: Timed-out as expected.".format(command_output) + CLR)
        else:
            raise RuntimeError("Oops! I was wrong!")

        print()

        # Use getpass() to get a password on-the-go!
        print("Using getpass() to prompt for a password...\n")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        command_output, exit_status = pexpect.run(
            "sudo firewall-cmd --zone=public --add-port=20/tcp",
            events={"(?i)password": getpass() + "\r"},
            withexitstatus=True)
        if exit_status != 0:
            raise RuntimeError("{0}: Could not modify firewall.".format(command_output))
        else:
            print(GRN + "{0}: Success.".format(command_output.strip()) + CLR)

        print()

        print("Getting a password and using it to run multiple commands...\n")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        sudo_password = getpass()
        list_of_commands = ["sudo firewall-cmd --zone=public --add-port=21/tcp",
                            "sudo firewall-cmd --zone=public --add-port=22/tcp",
                            "sudo firewall-cmd --zone=public --add-service=ssh",
                            "sudo firewall-cmd --zone=public --add-service=ftp",
                            "sudo firewall-cmd --zone=public --add-port=23/tcp",
                            "sudo firewall-cmd --zone=public --add-port=123/udp",
                            "sudo firewall-cmd --zone=public --add-service=ntp",
                            "sudo firewall-cmd --zone=public --add-port=69/udp",
                            "sudo firewall-cmd --zone=public --add-service=tftp", ]
        for c in list_of_commands:
            command_output, exit_status = pexpect.run(
                c,
                events={"(?i)password": sudo_password + "\r"},
                withexitstatus=True)
            if exit_status != 0:
                raise RuntimeError("{0}: Could not modify firewall.".format(c))
            else:
                print(GRN + "{0}: Success.".format(c) + CLR)

        print()

        print("Verifying the NTP configuration...")
        # Check if the NTP server address is in the ntp.conf file
        command_output, exit_status = pexpect.run(
            "grep \"server 127.127.1.0\" /etc/ntp.conf", withexitstatus=True)
        # If found, continue. If not, append to file
        if exit_status != 0:
            # Get the location of the Bourne Again Shell (Bash) executable
            command_output, exit_status = pexpect.run("which bash", withexitstatus=True)
            # You cannot continue without Bash, so raise an exception
            if exit_status != 0:
                raise RuntimeError(command_output.strip())
            else:
                # Use the bash to run a piped command in Pexpect
                bash = command_output
                print("Modifying ntp.conf...")
                # Clear incoming and outgoing text before using getpass()
                time.sleep(0.5)
                command_output, exit_status = pexpect.run(
                    "{0} -c 'echo -e \"server 127.127.1.0\" | sudo tee -a /etc/ntp.conf'".format(
                        bash),
                    events={"(?i)password": getpass() + "\r"},
                    withexitstatus=True)
                if exit_status != 0:
                    # You cannot continue without NTP, so raise an exception
                    raise RuntimeError(command_output.strip())
        print(GRN + "NTP configuration verified." + CLR)

        print()

        print("Starting the NTP service...")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        command_output, exit_status = pexpect.run("sudo systemctl start ntpd",
                                                  events={"(?i)password": getpass() + "\r"},
                                                  withexitstatus=True)
        if exit_status != 0:
            # You cannot continue without NTP, so raise an exception
            raise RuntimeError(command_output.strip())
        print(GRN + "NTP service started" + CLR)

        print()

        print("Verifying the TFTP configuration...")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        sudo_password = getpass()
        list_of_commands = ["sudo mkdir --parents --verbose /var/lib/tftpboot",
                            "sudo chmod 777 --verbose /var/lib/tftpboot",
                            "sudo touch /var/lib/tftpboot/startup-config.bak",
                            "sudo chmod 777 --verbose /var/lib/tftpboot/startup-config.bak", ]
        for c in list_of_commands:
            command_output, exit_status = pexpect.run(
                c,
                events={"(?i)password": sudo_password + "\r"},
                withexitstatus=True)
            if exit_status != 0:
                # You cannot continue without TFTP, so raise an exception
                raise RuntimeError(command_output.strip())
        print(GRN + "TFTP configuration verified." + CLR)

        print()

        print("Starting the TFTP service...")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        command_output, exit_status = pexpect.run("sudo systemctl start tftp",
                                                  events={"(?i)password": getpass() + "\r"},
                                                  withexitstatus=True)
        if exit_status != 0:
            # You cannot continue without TFTP, so raise an exception
            raise RuntimeError(command_output.strip())
        print(GRN + "TFTP service started" + CLR)

        print()

        print("Starting the FTP service...")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        command_output, exit_status = pexpect.run("sudo systemctl start vsftpd",
                                                  events={"(?i)password": getpass() + "\r"},
                                                  withexitstatus=True)
        if exit_status != 0:
            # You cannot continue without FTP, so raise an exception
            raise RuntimeError(command_output.strip())
        print(GRN + "FTP service started" + CLR)

        print()

        print("Starting the SSH service...")
        # Clear incoming and outgoing text before using getpass()
        time.sleep(0.5)
        command_output, exit_status = pexpect.run("sudo systemctl start sshd",
                                                  events={"(?i)password": getpass() + "\r"},
                                                  withexitstatus=True)
        if exit_status != 0:
            # You cannot continue without SSH, so raise an exception
            raise RuntimeError(command_output.strip())
        print(GRN + "SSH service started" + CLR)

        print()

        print("The host's Linux environment is set up.")
    except RuntimeError:
        e_type, e_value, e_traceback = sys.exc_info()
        print("{0}: \"{1}\" at line number {2}.".format(
            e_type.__name__, e_value, e_traceback.tb_lineno))
    finally:
        child.close()


if __name__ == "__main__":
    main()
