#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pexpect tutorial

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2020-2021, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"

import pexpect


def run_wrapper(cli_cmd, timeout=5):
    try:
        child_result, child_exitstatus = pexpect.run("/bin/bash -c '{0}'".format(cli_cmd),
                                                     timeout=5, withexitstatus=True)
        print("Exit status: {0}".format(child_exitstatus))
        if child_exitstatus is None or child_exitstatus != 0:
            print("Command failed: {0}".format(child_result.decode().strip()))
        else:
            print("Success!\n{0}".format(child_result.decode().strip()))
    except pexpect.ExceptionPexpect as ex:
        # If you use a non-existent command, pexpect will throw an exception
        print(ex.value)


def main():
    print("Hello, friend.")
    print("Welcome to the pexpect tutorial.")
    print("First command is pexpect.run. I prefer to use pexpect.run over subprocess in Python 2.7,\n" +
          "since commands can be piped and subprocess does not have a timeout feature.")
    print("\nThe first command, \"su -\", will timeout waiting for the root password:")
    run_wrapper("su -")
    print("\nThe second command, \"sudo -l\", will return an error waiting for the user password:")
    run_wrapper("sudo -l")
    print("\nThe third command, \"ls -l\", will succeed and return the output of the command:")
    run_wrapper("ls -l")
    print("\nThe fourth command, \"ls -l | grep grue\", will fail, since there are no file named \"grue\":")
    run_wrapper("ls -l | grep Mxyzptlk")
    print("\nThe fifth command, \"ls -l | grep py\", will succeed and return the output of the command:")
    run_wrapper("ls -l | grep py")
    print("\nThe sixth command, \"grue\", will throw an exception, since there is no command named \"grue\":")
    run_wrapper("grue")


if __name__ == "__main__":
    main()
