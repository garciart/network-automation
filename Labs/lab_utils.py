#!python
# -*- coding: utf-8 -*-
"""
Static utility functions for completing labs.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import logging
import sys
import time

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2019-2020, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="Labs/lab.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")

# Set to True during development and to False during production
DISPLAY_ERRORS = True
DISPLAY_MESSAGES = True

# Function return values
SUCCESS = 0
FAIL = 1
ERROR = 2


def log_error(exc_info, level=logging.ERROR):
    rval = FAIL
    try:
        e_type, e_value, e_traceback = sys.exc_info()
        print(e_type,
              e_value,
              e_traceback.tb_frame.f_code.co_filename,
              e_traceback.tb_lineno)
        logging.error(exc_info)
        rval = SUCCESS
    except BaseException as ex:
        print("Oops! Something went wrong:", ex)
        rval = ERROR
    return rval


def log_message(msg, level=logging.INFO):
    rval = FAIL
    try:
        print(msg)
        logging.info(msg)
        rval = SUCCESS
    except BaseException as ex:
        print("Oops! Something went wrong:", ex)
        rval = ERROR
    return rval


if __name__ == "__main__":
    try:
        raise RuntimeError("What?")
    except RuntimeError:
        log_error(sys.exc_info())
    log_message("Hello, world!")
