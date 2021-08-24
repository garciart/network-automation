#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Hash Checker!
Enter the full path of the file at the prompt. Example output:

Welcome to My Hash Checker!

Enter the filename (current directory) or full path of the file
to check: c3745-adventerprisek9-mz.124-25d.bin
The hashes for c3745-adventerprisek9-mz.124-25d.bin are:
- MD5:    563797308a3036337c3dee9b4ab54649
- SHA1:   a1e583a54843802520cbe0c47bddf8b6ebd0118c
- SHA256: 158ec1c7a6bc5895a5d3408629dac1609304df76e3f35daea3241e116e9db5d4
Script complete. Have a nice day.

Project: Automation
"""
from __future__ import print_function

import hashlib


def main(mystring):
    print("The hashes for {0} are:".format(mystring))
    print("- MD5:    {0}".format(hashlib.md5(mystring).hexdigest()))
    print("- SHA1:   {0}".format(hashlib.sha1(mystring).hexdigest()))
    print("- SHA256: {0}\n".format(hashlib.sha256(mystring).hexdigest()))


if __name__ == "__main__":
    print("Welcome to the Hash Checker!\n")
    mystring = input("Enter the string to hash: ")
    main(mystring.encode())
    print("Script complete. Have a nice day.")
