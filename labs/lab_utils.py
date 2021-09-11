# -*- coding: utf-8 -*-
"""Static utility functions and variables to support labs.

Project: Automation

Requirements:
- Python 2.7+
- pexpect
"""
from __future__ import print_function

import logging
import os
import re
import subprocess
import sys
import time

import pexpect

__all__ = ['log_message', 'error_message']

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgcoding.com"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="{0}/labs.log".format(os.getcwd()),
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


def log_message(msg, level=logging.ERROR, show_msg=False, show_err=False):
    """Utility to log messages, errors, or warnings.

    :param str msg: Information to log.
    :param int level: Recommend:
        INFO for general messages;
        DEBUG for debugging messages;
        WARNING for exceptions that allow the application to continue;
        ERROR for exceptions that close the application;
        CRITICAL for exceptions that halt the application,
        defaults to logging.ERROR.
    :param bool show_msg: Display message in stdout.
    :param bool show_err: Display error in stdout.

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
        print(msg)
    elif show_err:
        print("Houston, we've had a problem:", msg)


def error_message(exc_info, **options):
    """Formats exception or error information for logging and debugging.

    :param tuple exc_info: Exception details from sys module.
    :param Exception options: The exception object for pexpect's ExceptionPexpect (pex) or
        for subprocess' CalledProcessError (cpe).

    :return: The formatted message.

    .. seealso:: https://realpython.com/the-most-diabolical-python-antipattern/#why-log-the-full-stack-trace
    """
    # Inform the user the step failed
    print('Fail')

    # Get keyword arguments. Initialize default to None to prevent SonarLint reference error
    pex = options.get('pex', pexpect.ExceptionPexpect(None))
    cpe = options.get('cpe', subprocess.CalledProcessError(0, '', None))

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

        # Log what was actually found during the pexpect call
        e_value = 'Expected {0}, found {1}'.format(
            str(pex).split('searcher_string:\n    0: ')[1].split('\n')[0].strip('\r\n'),
            str(pex).split('before (last 100 chars): ')[1].split('\n')[0].strip('\r\n')
        )
        # Remove any unwanted escape characters here, like backspaces, etc.
        e_value = re.sub('[\b]', '', e_value)
    elif cpe.output:
        # This code is for subprocess.CalledProcessError. In Python 2.7, subprocess only
        # returns the reason for a non-zero return code (i.e., the CLI's response) in a
        # CalledProcessError object unless the shell option is set to True, which is unsafe due
        # to potential shell injections.
        # https://docs.python.org/2/library/subprocess.html#subprocess.check_output

        e_value = '"{0}" failed: {1}'.format(cpe.cmd, cpe.output)

    # Return the formatted message for logging
    # Start with a linefeed to avoid tailing device OS messages
    # Error message format:
    # - e_type: Type of error.
    # - e_value: Error message.
    # - e_traceback.tb_frame.f_code.co_filename: The name of the file that caused the error.
    # - e_traceback.tb_lineno: The line number where the error occurred. The ternary operator
    #     checks if tb_next exists; if so, it moves up the error stack to retrieve the line
    #     number where the error or exception actually occurred in a function or method,
    #     instead of the line number where the function or method was called.
    msg = ('\nType {0}: {1} in {2} at line {3}.\n'.format(
        e_type.__name__,
        e_value,
        e_traceback.tb_frame.f_code.co_filename,
        e_traceback.tb_lineno if e_traceback.tb_next is None
        else e_traceback.tb_next.tb_lineno))
    log_message(msg, level=logging.ERROR)
    return msg


if __name__ == "__main__":
    log_message("Script {0} cannot be run independently from this application.".format(
        sys.argv[0]), level=logging.WARNING)
    raise RuntimeError("Script {0} cannot be run independently from this application.".format(sys.argv[0]))
