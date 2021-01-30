# -*- coding: utf-8 -*-
"""Static utility functions and variables to support labs.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import logging
import sys
import time

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="labs.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# Set to True during development and to False during production
DISPLAY_ERRORS = True
DISPLAY_MESSAGES = True

# Function return values
SUCCESS = 0
FAIL = 1
ERROR = 2


def log_error(exc_info, level=logging.ERROR):
    """Utility to log exceptions as errors or warnings.

    :param exc_info: Exception details from the sys module.
    :type exc_info: tuple
    :param level: Recommend:
        WARNING for exceptions that allow the application to continue;
        ERROR for exceptions that close the application;
        CRITICAL for exceptions that halt the application,
        defaults to logging.ERROR.
    :type level: int

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises ex: RuntimeError for any exceptions or errors.

    .. seealso:: https://docs.python.org/2/library/sys.html#sys.exc_info
    .. seealso:: https://docs.python.org/2/library/logging.html
    """
    rval = FAIL
    if exc_info is not None and ((level % 10 == 0) and (50 >= level >= 30)):
        try:
            e_type, e_value, e_traceback = exc_info
            msg = "Type {0}: {1} in {2} at line {3}.".format(e_type.__name__,
                                                             e_value,
                                                             e_traceback.tb_frame.f_code.co_filename,
                                                             e_traceback.tb_lineno)
            if DISPLAY_ERRORS:
                print("Houston, we've had a problem:", msg)

            if level == logging.WARNING:
                logging.warning(msg)
            elif level == logging.CRITICAL:
                logging.critical(msg)
            else:
                logging.error(msg)
            rval = SUCCESS
        except RuntimeError as ex:
            print("We are venting something out into space.", ex)
            rval = ERROR
    return rval


def log_message(msg, level=logging.INFO):
    """Utility to log non-error messages.

    :param msg: Message for log.
    :type msg: str
    :param level: Use DEBUG or INFO as needed, defaults to logging.INFO.
    :type level: int

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises ex: RuntimeError for any exceptions or errors.

    .. seealso:: https://docs.python.org/2/library/logging.html
    """
    rval = FAIL
    # This works: stop playing with it, dang it!
    if msg is not None and msg.strip() and ((level % 10 == 0) and (20 >= level >= 0)):
        try:
            if DISPLAY_MESSAGES:
                print(msg)
            logging.debug(msg) if logging.DEBUG else logging.info(msg)
            rval = SUCCESS
        except RuntimeError:
            log_error(sys.exc_info())
            rval = ERROR
    return rval


def simple_cli_call(cmd, fail_content=None, pass_content=None, timeout=30):
    """Simple function (no piping) to execute command-line interface (CLI) commands and scripts using pexpect.run.

    :param cmd: Command or script to execute in the command-line interface.
    :type cmd: str
    :param fail_content: The call fails if any item is present; evaluated before pass_content.
    :type fail_content: list
    :param pass_content: The call succeeds if any item if present.
    :type pass_content: list
    :param timeout: Time limit to complete the command in seconds.
    :type timeout: int

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error, as well as the text as a string.
    :rtype: tuple

    :raises ex: RuntimeError for any exceptions or errors.
    """
    fail_content = fail_content if fail_content is not None else []
    pass_content = pass_content if pass_content is not None else []
    child_result = None
    rval = (FAIL, child_result)
    try:
        child_result, child_exitstatus = pexpect.run(cmd, timeout=timeout, withexitstatus=True)
        child_result = child_result.decode().strip()
        if child_exitstatus is None:
            log_message("{0}: Operation timed out.".format(cmd))
        elif any(item in child_result for item in fail_content):
            log_message("{0}: Fail content found: {1}".format(cmd, child_result))
        elif child_exitstatus != 0:
            log_message("{0}: Error: {1}".format(cmd, child_result))
            rval = ERROR, child_result
        elif pass_content and not any(item in child_result for item in pass_content):
            log_message("{0}: Pass content not found: {1}".format(cmd, child_result))
        else:
            print("{0}: Success.".format(cmd))
            rval = SUCCESS, child_result
    except RuntimeError:
        log_error(sys.exc_info())
        rval = ERROR, child_result
    return rval


if __name__ == "__main__":
    log_message("Script {0} cannot be run independently from this application.".format(sys.argv[0]))
    raise RuntimeError("Script {0} cannot be run independently from this application.".format(sys.argv[0]))
