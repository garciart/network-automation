#!python
# -*- coding: utf-8 -*-
"""Unit tests for module Labs/lab_utils.py.

Project: Automation

Requirements:
- Python 2.7.5
"""
import sys
import unittest

import labs.old.lab_utils as lu

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2019-2020, Rob Garcia"
__email__ = "rgarcia@rgprogramming.com"
__license__ = "MIT"


class Test(unittest.TestCase):
    """Check boundary conditions for functions in lab_utils.py.

    :param unittest.TestCase: A class whose instances are single test cases.
    :type unittest.TestCase: class
    """

    # Function return values
    SUCCESS = 0
    FAIL = 1
    ERROR = 2

    def test_log_message_is_not_none(self):
        """A NULL log message should return FAIL.
        """
        arg = None
        result = lu.log_message(arg)
        self.assertEqual(result, self.FAIL)


if __name__ == "__main__":
    unittest.main()
