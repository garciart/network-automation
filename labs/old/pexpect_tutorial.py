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
__email__ = "rgarcia@rgcoding.com"
__license__ = "MIT"

import sys

import pexpect


def run_wrapper(cli_cmd, timeout=5):
    try:
        child_result, child_exitstatus = pexpect.run("/bin/bash -c '{0}'".format(cli_cmd),
                                                     timeout=timeout, withexitstatus=True)
        print("Exit status: {0}".format(child_exitstatus))
        if child_exitstatus is None or child_exitstatus != 0:
            print("Fail: The response to the command was: {0}".format(child_result.decode().strip()))
        else:
            print("Success! Response:\n{0}".format(child_result.decode().strip()))
    except pexpect.ExceptionPexpect:
        print(sys.exc_info())
    except TypeError:
        print(sys.exc_info())


def spawn_wrapper(cli_cmd, timeout=5):
    try:
        child = pexpect.spawn("/bin/bash")
        child.sendline(cli_cmd)
        i = child.expect_exact("$", pexpect.EOF, pexpect.TIMEOUT)
    except pexpect.ExceptionPexpect:
        print(sys.exc_info())
    except TypeError:
        print(sys.exc_info())
    finally:
        child.close()


def main():
    print("Hello, friend.")
    print("Welcome to the pexpect tutorial.")
    print("First command is pexpect.run. I prefer to use pexpect.run over subprocess in Python 2.7,\n" +
          "since commands can be piped and subprocess does not have a timeout feature.")
    print(
        "\nThe first command, \"su -\", will fail, since it does not receive the root password within the timeout limit:")
    run_wrapper("su -")
    print(
        "\nThe second command, \"sudo -l\", will fail because the user is already a super user. It will also fail for non-SU's as well, but due to a timeout:")
    run_wrapper("sudo -l")
    print("\nThe third command, \"ls -l\", will succeed and return the directory listing:")
    run_wrapper("ls -l")
    print("\nThe fourth command, \"ls -l | grep 'grue'\", will fail, since a file named \"grue\" was not found:")
    run_wrapper("ls -l | grep Mxyzptlk")
    print(
        "\nThe fifth command, \"ls -l | grep '.py'\", will succeed and return the name of this script, as well as any other .py files:")
    run_wrapper("ls -l | grep py")
    print("\nThe sixth command, will throw an exception, since the timeout value must be an integer:")
    run_wrapper("ls -l", timeout='a')
    spawn_wrapper("ls -l")


if __name__ == "__main__":
    main()
