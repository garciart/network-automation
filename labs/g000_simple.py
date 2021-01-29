#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 00: Simple demo of subprocess and pexpect without verification or validation (e.g., unit testing, etc.).

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import subprocess

import pexpect

import lab_utils as lu

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"


def main():
    """Function to display contents of the current folder.

    :return: 0 if the function succeeded, 1 if it failed, or 2 if there was an error.
    :rtype: int

    :raises ex: RuntimeError for any exceptions or errors.
    """
    rval = lu.FAIL
    try:
        print("List files using subprocess first...")
        result = subprocess.run(["ls", "-l"])
        print(result, '\n')

        print("Now listing files using pexpect...")
        child_result = pexpect.run("ls -l")
        print(child_result.decode())

        rval = lu.SUCCESS
    except RuntimeError:
        rval = lu.ERROR
    return rval


if __name__ == "__main__":
    main()
