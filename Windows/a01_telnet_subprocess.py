# Simple connectivity test using Telnet and subprocess
# Make sure GNS3 is running and the loopback adapter (cloud1) is connected to
# a new router. Take note of the new router's console port number.

import subprocess


def main():
    try:
        print("Hello, friend.")
        r_port = input("Enter localhost port number: ")
        print("Connecting to new router through Telnet on port %s..." % r_port)
        p = subprocess.Popen("telnet localhost %s" % r_port,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result = p.stdout.readlines()
        if result == []:
            raise Exception("WTF?")
        else:
            print(result)
    except Exception as ex:
        print("Oops! Something went wrong:", ex)


if __name__ == "__main__":
    main()
