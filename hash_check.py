#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Hash Checker!
Enter the full path of the file at the prompt. Example output:

Welcome to My Hash Checker!

Enter the character string to hash: Network Automation
The hashes for Network Automation are:
- MD5:    a99099ad955b23a7489ea7126175d115
- SHA1:   ee88670aacd4a73c28646c22815b8f85df614d80
- SHA256: 27eeb88202a9e1b35c036ccf43a6849909ebe68b7d23a53857244e60e0a63fd8
Script complete. Have a nice day.

Project: Automation
"""
from __future__ import print_function

import hashlib


def main(string):
    """Application entry point.

    :param str string: The character string to be hashed.

    :returns: None
    :rtype: None
    """
    print("The hashes for {0} are:".format(string))
    print("- MD5:    {0}".format(hashlib.md5(string).hexdigest()))
    print("- SHA1:   {0}".format(hashlib.sha1(string).hexdigest()))
    print("- SHA256: {0}\n".format(hashlib.sha256(string).hexdigest()))


if __name__ == "__main__":
    print("Welcome to the Hash Checker!\n")
    string_to_hash = raw_input("Enter the character string to hash: ")
    main(string_to_hash.encode(encoding='UTF-8'))
    print("Script complete. Have a nice day.")
