#!python
# -*- coding: utf-8 -*-
"""Unit tests for module Labs/lab_utils.py.

Project: Automation

Requirements:
- Python 2.7.5
"""
import unittest

from labs import lab_utils

# Module metadata dunders
__author__ = "Rob Garcia"
__copyright__ = "Copyright 2019-2020, Rob Garcia"
__email__ = "rgarcia@rgcoding.com"
__license__ = "MIT"


class Test(unittest.TestCase):
    """Check boundary conditions for functions in lab_utils.py.

    :param unittest.TestCase: A class whose instances are single test cases.
    :type unittest.TestCase: class
    """

    def test_log_message_is_not_none(self):
        """A NULL log message should return a Runtime Error.
        """
        arg = None
        self.assertRaises(RuntimeError, lab_utils.log_message, arg)


if __name__ == "__main__":
    unittest.main()
