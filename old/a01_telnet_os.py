# Simple connectivity test using Telnet and os
# Make sure GNS3 is running and the loopback adapter (cloud1) is connected to
# a new router. Take note of the new router's console port number.

import os
import subprocess


def main():
    try:
        r_port = input("Enter localhost port number: ")
        print("Connecting to new router through Telnet on port %s..." % r_port)

        os.system("telnet localhost %s" % r_port)

        # If successful:
        # Move input focus to Terminal
        # Press [Return] to reach the router prompt
        # Input "exit" to exit router configuration
        # Press [CTRL] + []] to reach the Telnet prompt
        # Input [q] to exit Telnet
    except Exception as ex:
        print("Oops! Something went wrong:", ex)


if __name__ == "__main__":
    main()
