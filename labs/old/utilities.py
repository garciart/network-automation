import logging
import os
import socket
import subprocess
import sys
import time
from getpass import getpass

import pexpect

__all__ = ["error_message", "log_message", "prompt_for_password", "run_cli_commands",
           "validate_ip_address", "validate_port_number", "validate_subnet_mask", ]


def error_message(exc_info, **options):
    """Formats exception or error information for logging and debugging.

    :param tuple exc_info: Exception details from sys module.
    :param Exception options: The exception object for pexpect's ExceptionPexpect (pex) or
        for subprocess' CalledProcessError (cpe).

    :return: The formatted message.

    .. seealso:: https://realpython.com/the-most-diabolical-python-antipattern/#why-log-the-full-stack-trace
    """
    # Get keyword arguments. Initialize default to None to prevent SonarLint reference error
    pex = options.get("pex", pexpect.ExceptionPexpect(None))
    cpe = options.get("cpe", subprocess.CalledProcessError(0, "", None))

    # Unpack sys.exc_info() to get error information
    e_type, e_value, e_traceback = exc_info
    if pex.value:
        # This code is for pexpect.ExceptionPexpect. It retrieves the device's response to
        # pexpect.sendline() from the state of the spawned object (__str__ from ex) for
        # logging. Otherwise, if you match TIMEOUT or EOF when calling expect or expect_exact,
        # pexpect does not retain the state of the object, since it believes you will
        # handle the exception by other means (e.g., generic message to the user, etc.).
        # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
        # https://pexpect.readthedocs.io/en/stable/_modules/pexpect/exceptions.html#TIMEOUT

        # For pexpect.run calls...
        if "searcher" not in str(pex):
            e_value = str(pex).strip("\r\n")
        # For pexpect.expect-type calls...
        else:
            # Log what was actually found during the pexpect call
            e_value = "Expected {0}, found \"{1}".format(
                str(pex).split("searcher: ")[1].split("buffer (last 100 chars):")[0],
                str(pex).split("before (last 100 chars): ")[1].split("after:")[0]
            )
            # Remove any unwanted escape characters here, like backspaces, etc.
        # e_value = re.sub("[\b\r\n]", " ", e_value).replace("  ", " ")
        e_value = " ".join(e_value.replace("\b", "").split())
    elif cpe.output:
        # This code is for subprocess.CalledProcessError. In Python 2.7, subprocess only
        # returns the reason for a non-zero return code (i.e., the CLI's response) in a
        # CalledProcessError object unless the shell option is set to True, which is unsafe due
        # to potential shell injections.
        # https://docs.python.org/2/library/subprocess.html#subprocess.check_output
        e_value = "'{0}' failed: {1}".format(cpe.cmd, cpe.output)

    # Move up the error stack to retrieve the function or method where the error or exception
    # actually occurred,instead of the line number where the function or method was called.
    if e_traceback.tb_next is not None:
        e_traceback = e_traceback.tb_next
    # Return the formatted message for logging
    # Start with a linefeed to avoid tailing device OS messages
    # Error message format:
    # - e_type: Type of error.
    # - e_value: Error message.
    # - e_traceback.tb_frame.f_code.co_filename: The name of the file that caused the error.
    # - e_traceback.tb_lineno: The line number where the error occurred.
    msg = ("\nType {0}: \"{1}\" in {2} at line {3}.\n".format(
        e_type.__name__,
        e_value,
        e_traceback.tb_frame.f_code.co_filename,
        e_traceback.tb_lineno))
    log_message(msg, level=logging.ERROR)
    return msg


# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="{0}/labs.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


def log_message(msg, level=logging.ERROR, show_msg=False):
    """Utility to log messages, errors, or warnings.

    :param str msg: Information to log.
    :param int level: Recommend:
        INFO for general messages;
        DEBUG for debugging messages;
        WARNING for exceptions that allow the application to continue;
        ERROR for exceptions that close the application;
        CRITICAL for exceptions that halt the application, defaults to logging.ERROR.
    :param bool show_msg: Display message in stdout.

    :return: None
    :rtype: None

    :raise RuntimeError: If logging was unsuccessful.

    .. seealso:: https://docs.python.org/2/library/sys.html#sys.exc_info
    .. seealso:: https://docs.python.org/2/library/logging.html
    """
    if msg is None or ((level % 10 != 0) and (50 <= level <= 10)):
        raise RuntimeError("We are venting something out into space.")
    switcher = {
        10: logging.debug,
        20: logging.info,
        30: logging.warning,
        40: logging.critical,
        50: logging.error,
    }
    # Execute logging function based on level
    switcher[level](msg)

    if show_msg:
        print("Houston, we've had a problem:", msg)


def prompt_for_password(prompt="Password:", password=None):
    """Prompts for a password if no password is provided or if the supplied password timeout
    session has ended. See run_cli_commands for an example of use.

    :param str prompt: The message to display at the prompt ("VTY terminal password", etc.)
    :param str password: The password, if it exists. If supplied, there will be no prompt.
    :return: The password received as an argument or from the prompt.
    :rtype: str
    """
    if password is None:
        password = getpass(prompt=prompt)
    return password


def run_cli_commands(list_of_commands, sudo_password=None):
    """Use the command line interface with error detection.

    :param str sudo_password: The sudo password, if it exists.
    :param list list_of_commands: The commands to execute.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to run a command.
    """
    for c in list_of_commands:
        (command_output, exitstatus) = pexpect.run(c,
                                                   events={"(?i)password": prompt_for_password(
                                                       sudo_password)},
                                                   withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to {0}: {1}".format(c, command_output.strip()))


def validate_ip_address(ip_address, ipv4_only=True):
    """Checks that the argument is a valid IP address.

    :param str ip_address: The IP address to check.
    :param bool ipv4_only: If the method should only validate IPv4-type addresses.

    :return: True if the IP address is valid; false if not.
    :rtype: bool

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
        return True
    else:
        raise ValueError("Argument contains an invalid IP address: {0}".format(ip_address))


def validate_port_number(port_number):
    """Check if the port number is within range.

    :param int port_number: The port number to check.

    :return: True if the port number is valid; false if not.
    :rtype: bool

    :raises ValueError: if the port number is invalid.
    """
    if port_number not in range(0, 65535):
        raise ValueError("Invalid port number.")
    return True


def validate_subnet_mask(subnet_mask):
    """Checks that the argument is a valid subnet mask.

    :param str subnet_mask: The subnet mask to check.

    :return: True if the subnet mask is valid; false if not.
    :rtype: bool

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
        return True
    else:
        raise ValueError("Invalid subnet mask: {0}.".format(subnet_mask))


if __name__ == "__main__":
    print("Error: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
