#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Python practice using Paul Browning's excellent book, 101 Labs

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


def main():
    """
    :raises ex: RuntimeError for any exceptions or errors.
    """
    try:
        print("Hello, friend.")
        # child = pexpect.spawn("pgrep gns3server")
        child_result, child_exitstatus = pexpect.run("pgrep gns3server", timeout=30, withexitstatus=True)
        if child_exitstatus == 0:
            print(child_exitstatus, child_result.decode().strip())
            print("GNS3 server is running; process number {0}.".format(child_result.decode().strip()))

        else:
            print("GNS3 is not running. Please run gns3_run to start GNS3.")
    except BaseException as ex:
        raise ex


if __name__ == "__main__":
    main()
