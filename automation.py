#!/usr/bin/python
"""Automation Demo

Project: Automation

To run this lab:

* Start GNS3 by executing "gn3_run" in a Terminal window.
* Add a Cloud and a C3745 router
* Connect the cloud's tap interface to the router's FastEthernet0/0 interface
* Start all devices.
* Run this script (i.e., "python automation.py")
"""
from __future__ import print_function

import time

import pexpect

print("Connecting to the device...")

# Connect to the device and allow time for any boot-up messages to clear
child = pexpect.spawn("telnet 192.168.1.1 5001")
time.sleep(5)

# Look for a welcome message to ensure the device was reloaded and you are not eavesdropping
child.expect("Press RETURN to get started")
child.sendline("\r")

# Check for a prompt, either R1> (User EXEC mode) or R1# (Privileged EXEC Mode)
# and enable Privileged EXEC Mode if in User EXEC mode.
index = child.expect_exact(["R1>", "R1#", ])
if index == 0:
    child.sendline("enable\r")
    child.expect_exact("R1#")
print("Connected to the device.")

# Get the device's hardware and software information
child.sendline("show version\r")

# Create a variable to hold the information
output = ""

# Initialize the expect index
index = -1

# Use a loop to scroll through the output
# You can also avoid the loop by sending the command, "terminal length 0"
while index != 0:
    index = child.expect(["R1#", "--More--", pexpect.TIMEOUT, ])
    output = output + (child.before)
    if index == 1:
        child.sendline(" ")
    elif index == 2:
        print("Search string not found.")
        break
print("Getting device information:\n" + output.strip().replace("\n\n", ""))

# Cause and handle an error
print("Looking for a string...")
child.sendline("\r")
index = child.expect(["Automation is fun!", pexpect.TIMEOUT, ])
if index == 0:
    print("Search string found.")
else:
    print("Search string not found.")

# Close Telnet and disconnect from device
print("Disconnecting from the device...")
child.sendcontrol("]")
child.sendline('q\r')
child.close()

print("Script complete. Have a nice day.")
