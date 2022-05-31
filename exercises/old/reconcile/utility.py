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
import traceback
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
                "(?i)password": (sudo_password + "\r") if sudo_password is not None else (
                        getpass() + "\r")},
            withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to execute command {0}: {1}".format(c, command_output))
        logging.debug(
            # For Python 2.x, use string_escape.
            # For Python 3.x, use unicode_escape.
            # Do not use utf-8; Some characters, such as backticks, will cause exceptions
            "Output:\n{0}\nExit status: {1}\n".format(
                command_output.decode("string_escape").strip(), exitstatus))


def run_cli_command(command, sudo_password=None):
    """Runs OS commands. Exceptions must be handled by the instantiating module.

    :param str command: The command to run through the command-line interface (CLI).
    :param str sudo_password: The superuser password to execute a command that requires
        elevated privileges.
    :return: The result of the command.
    :rtype: str
    :raises RuntimeError: If unable to execute the command.
    """
    command_output, exitstatus = pexpect.run(command,
                                             events={"(?i)password": sudo_password},
                                             withexitstatus=True)
    if exitstatus != 0:
        # For Python 2.x, use string_escape.
        # For Python 3.x, use unicode_escape.
        # Do not use utf-8; Some characters, such as backticks, will cause exceptions
        raise RuntimeError("Exit status: {0} - Unable to {1}: {2}".format(
            exitstatus, command, command_output.decode("string_escape").strip()))
    return "Output:\n{0}".format(command_output.decode("string_escape").strip())


def open_telnet_port(sudo_password):
    """List of commands to open the Telnet port.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["which telnet",
                      "sudo firewall-cmd --zone=public --add-port=23/tcp", ],
                     sudo_password)


def close_telnet_port(sudo_password):
    """List of commands to close the Telnet port.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --remove-port=23/tcp", ],
                     sudo_password)


def enable_ssh(sudo_password):
    """List of commands to enable the Secure Shell (SSH) Protocol Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl start sshd",
                      "sudo firewall-cmd --zone=public --add-service=ssh",
                      "sudo firewall-cmd --zone=public --add-port=22/tcp", ],
                     sudo_password)


def disable_ssh(sudo_password):
    """List of commands to disable Secure Shell (SSH) Protocol Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --remove-port=22/tcp",
                      "sudo firewall-cmd --zone=public --remove-service=ssh",
                      "sudo systemctl stop sshd", ],
                     sudo_password)


def enable_ftp(sudo_password):
    """List of commands to enable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands([
        "sudo sed --in-place '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
        "sudo sed --in-place --expression '$aftp_username=nobody' /etc/vsftpd/vsftpd.conf",
        "sudo systemctl start vsftpd",
        "sudo firewall-cmd --zone=public --add-port=20/tcp",
        "sudo firewall-cmd --zone=public --add-port=21/tcp",
        "sudo firewall-cmd --zone=public --add-service=ftp", ],
        sudo_password)


def disable_ftp(sudo_password):
    """List of commands to disable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --remove-service=ftp",
                      "sudo firewall-cmd --zone=public --remove-port=21/tcp",
                      "sudo firewall-cmd --zone=public --remove-port=20/tcp",
                      "sudo sed --in-place '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf",
                      "sudo systemctl stop vsftpd", ],
                     sudo_password)


def enable_tftp(sudo_password):
    """List of commands to enable the Trivial File Transfer Protocol (TFTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo systemctl start tftp",
                      "sudo firewall-cmd --zone=public --add-port=69/udp",
                      "sudo firewall-cmd --zone=public --add-service=tftp",
                      "sudo mkdir --parents --verbose /var/lib/tftpboot",
                      "sudo chmod 777 --verbose /var/lib/tftpboot", ],
                     sudo_password)


def disable_tftp(sudo_password):
    """List of commands to disable the Trivial File Transfer Protocol (TFTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo firewall-cmd --zone=public --remove-service=tftp",
                      "sudo firewall-cmd --zone=public --remove-port=69/udp",
                      "sudo systemctl stop tftp", ],
                     sudo_password)


def set_utc_time(new_datetime, sudo_password):
    """Sets the system time without a connection to the Internet. Use before enabling the
    Network Time Protocol (NTP) Service for offline synchronization.

    **Note** - For maximum compatibility with devices, the timezone will be set UTC.

    :param str new_datetime: The desired UTC date and time, in "YYYY-MM-DD HH:MM:SS" format.
    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
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
        run_cli_commands(["sudo timedatectl set-ntp false",
                          "sudo timedatectl set-timezone UTC",
                          "sudo timedatectl set-time \"{0}\"".format(new_datetime),
                          "sudo timedatectl set-local-rtc 0", ],
                         sudo_password)
    finally:
        run_cli_commands(["sudo date --set \"{0} UTC\"".format(new_datetime), ],
                         sudo_password)


def enable_ntp(sudo_password):
    """List of commands to enable the Network Time Protocol (NTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands([
        "sudo sed --in-place '/server 127.127.1.0/d' /etc/ntp.conf",
        "sudo sed --in-place '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
        "sudo sed --in-place --expression '$aserver 127.127.1.0' /etc/ntp.conf",
        "sudo sed --in-place --expression '$afudge 127.127.1.0 stratum 10' /etc/ntp.conf",
        "sudo systemctl start ntpd",
        "sudo firewall-cmd --zone=public --add-port=123/udp",
        "sudo firewall-cmd --zone=public --add-service=ntp", ],
        sudo_password)


def disable_ntp(sudo_password):
    """List of commands to disable the Network Time Protocol (NTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    run_cli_commands(["sudo sed --in-place '/fudge 127.127.1.0 stratum 10/d' /etc/ntp.conf",
                      "sudo sed --in-place '/server 127.127.1.0/d' /etc/ntp.conf",
                      "sudo firewall-cmd --zone=public --remove-service=ntp",
                      "sudo firewall-cmd --zone=public --remove-port=123/udp",
                      "sudo systemctl stop ntpd", ],
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
        # noinspection PyTypeChecker
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


def create_error_msg(exc_info):
    """Captures and formats exception or error information for logging and debugging.

    :param tuple exc_info: Exception details from the sys module.
    :return: The formatted message.

    .. seealso:: https://realpython.com/the-most-diabolical-python-antipattern/#why-log-the-full-stack-trace
    """
    # Unpack sys.exc_info() to get error information
    e_type, e_value, _ = exc_info
    # Instantiate the message container
    err_msg = ""
    if e_type in (pexpect.ExceptionPexpect, pexpect.EOF, pexpect.TIMEOUT,):
        # This code retrieves the device's response to pexpect.sendline()
        # from the state of the spawned object (__str__ from ex).
        # If you match TIMEOUT or EOF when calling expect or expect_exact,
        # pexpect does not retain the state of the object for examination afterwards.
        # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
        # https://pexpect.readthedocs.io/en/stable/_modules/pexpect/exceptions.html#TIMEOUT

        # Add a heading to EOF and TIMEOUT errors
        if pexpect.EOF:
            err_msg += "EOF reached: Child process exited unexpectedly.\n"
        elif pexpect.TIMEOUT:
            err_msg += "Timed-out looking for the expected search string.\n"

        # Add trace
        err_msg += pexpect.ExceptionPexpect(e_type).get_trace()

        # For pexpect.run calls...
        if "searcher" not in str(e_value):
            err_msg += (str(e_value).strip("\r\n"))
        # For pexpect.expect-type calls...
        else:
            # Log what was actually found during the pexpect call
            e_value = "Expected {0}\nFound {1}.".format(
                str(e_value).split("searcher: ")[1].split("buffer (last 100 chars):")[0].strip(),
                str(e_value).split("before (last 100 chars): ")[1].split("after:")[0].strip()
            )
            # Remove any unwanted escape characters here, like backspaces, etc.
            e_value = e_value.replace("\b", "")
            err_msg += e_value
    elif e_type in (ValueError, RuntimeError, OSError,):
        # This application manually raises two types of errors: ValueError and RuntimeError.
        # Invalid inputs will throw ValueErrors.
        # Non-zero exit statuses or other issues (e.g., missing credentials, etc.) will throw RuntimeErrors.
        # OSError captures non-Popen subprocess exceptions. In Python 2.7, subprocess only returns the
        # reason for a non-zero return code (i.e., the CLI's response) unless the shell option is set to True,
        # which is unsafe due to potential injections.
        # https://docs.python.org/2/library/subprocess.html#subprocess.check_output
        # All other errors and exceptions indicate syntax or semantic programming issues.
        err_msg += (traceback.format_exc().strip())
    return err_msg


def connect_via_telnet(device_hostname, device_ip_address, port_number=23, username="", password=""):
    """Connect to the device via Telnet.
    :param str device_hostname: The hostname of the device.
    :param str device_ip_address: The IP address that will be used to connect to the device.
    :param int port_number: The port number for the connection.
    :param str username: Username (for a configured device).
    :param str password: Password (for a configured device).
    :returns: The connection to the device in a child application object.
    :rtype: pexpect.spawn
    """
    print("Checking Telnet client is installed...")
    run_cli_command("which telnet")
    print("Telnet client is installed.")
    print("Connecting to {0} on port {1} via Telnet...".format(device_ip_address, port_number))
    child = pexpect.spawn("telnet {0} {1}".format(device_ip_address, port_number))
    # Slow down commands to prevent race conditions with output
    child.delaybeforesend = 0.5
    # Echo both input and output to the screen
    # child.logfile = sys.stdout
    # Listing of Cisco IOS prompts without a hostname
    cisco_prompts = [
        ">", "#", "(config)#", "(config-if)#", "(config-router)#", "(config-line)#", ]
    # Prepend the hostname to the standard Cisco prompt endings
    device_prompts = ["{0}{1}".format(device_hostname, p) for p in cisco_prompts]
    # noinspection PyTypeChecker
    index = child.expect_exact([pexpect.TIMEOUT, ] + device_prompts, 1)

    # End-of-line (EOL) issue: Depending on the physical port you use (Console, VTY, etc.),
    # AND the port number you use (23, 5001, etc.), Cisco may require a carriage return ("\r")
    # when using pexpect.sendline. Also, each terminal emulator may have different EOL
    # settings. One solution is to append the carriage return to each sendline.
    # Nother solution is to edit the terminal emulator's runtime configuration file
    # (telnetrc, minirc, etc) before running this script, then setting or unsetting the
    # telnet transparent setting on the device.

    if index != 0:
        # If you find a hostname prompt (e.g., R1#) before any other prompt, you are accessing an open line
        print("You may be accessing an open or uncleared virtual teletype session.\n" +
              "Output from previous commands may cause pexpect searches to fail.\n" +
              "To prevent this in the future, reload the device to clear any artifacts.")
        # Move the pexpect cursor forward to the newest hostname prompt
        tracer_round = ";{0}".format(int(time.time()))
        # Add the carriage return here, not in the tracer_round.
        # Otherwise, you won't find the tracer_round later
        child.sendline(tracer_round + "\r")
        child.expect_exact("{0}".format(tracer_round), timeout=1)
    # Always try to find hostname prompts before anything else
    index_offset = len(device_prompts)
    while True:
        index = child.expect_exact(
            device_prompts +
            ["Login invalid",
             "Bad passwords",
             "Username:",
             "Password:",
             "Would you like to enter the initial configuration dialog? [yes/no]:",
             "Would you like to terminate autoinstall? [yes/no]:",
             "Press RETURN to get started", ])
        if index < index_offset:
            break
        elif index in (index_offset + 0, index_offset + 1):
            raise RuntimeError("Invalid credentials provided.")
        elif index in (index_offset + 2, index_offset + 3):
            print("Warning - This device has already been configured and secured.\n" +
                  "Changes made by this script may be incompatible with the current configuration.")
            if index == 0:
                # child.sendline((_username if _username is not None else raw_input("Username: ")) + "\r")
                child.sendline(username + "\r")
                child.expect_exact("Password:")
            # child.sendline((_password if _password is not None else getpass("Enter password: ")) + "\r")
            child.sendline(password + "\r")
        elif index == index_offset + 4:
            child.sendline("no\r")
        elif index == index_offset + 5:
            child.sendline("yes\r")
        elif index == index_offset + 6:
            child.sendline("\r")
    print("Connected to {0} on port {1} via Telnet.".format(device_ip_address, port_number))
    return child


def close_telnet_connection(child):
    print("Closing Telnet connection...")
    child.sendcontrol("]")
    child.expect_exact("telnet>")
    child.sendline("q\r")
    child.expect_exact(["Connection closed.", pexpect.EOF, ])
    print("Telnet connection closed")


def enable_privileged_exec_mode(child, device_prompts, enable_password=""):
    print("Enabling Privileged EXEC Mode...")
    # A reloaded device's prompt will be either R1> (User EXEC mode) or R1# (Privileged EXEC Mode)
    # Just in case the device boots into User EXEC mode, enable Privileged EXEC Mode
    # The enable command will not affect anything if the device is already in Privileged EXEC Mode
    child.sendline("disable\r")
    child.expect_exact(device_prompts[0])
    child.sendline("enable\r")
    index = child.expect_exact(["Password:", device_prompts[1], ])
    if index == 0:
        enable_password = enable_password if enable_password is not None else getpass()
        child.sendline(enable_password + "\r")
        child.expect_exact(device_prompts[1])
    print(GRN + "Privileged EXEC Mode enabled.")


if __name__ == "__main__":
    print(RED + "ERROR: Script {0} cannot be run independently.".format(
        os.path.basename(sys.argv[0])) + CLR)
