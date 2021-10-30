import re
import time
from datetime import datetime

import pexpect

PROMPT_LIST = ["R1>", "R1#", "R1(config)#", "R1(config-if)#", "R1(config-router)#", "R1(config-line)#", ]

_ACCESS_CONFIG_CMD = "configure terminal\r"
_COPIED_MSG = "bytes copied in"
_ENCRYPT_CONFIG_CMD = "service password-encryption\r"
_EXIT_CMD = "exit\r"
_FILE_SYSTEM_PREFIX = ["startup-config", "running-config", "nvram", "flash", "slot", ]
_PASSWORD_PROMPT = "Password:"
_SET_PASSWORD_CMD = "password {0}\r"
_REQUIRE_LOGIN_CMD = "login\r"


def run_cli_commands(list_of_commands, sudo_password=None):
    """Use the command line interface with error detection.

    :param str sudo_password: The sudo password, if it exists.
    :param list list_of_commands: The commands to execute.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to run a command.
    """
    for c in list_of_commands:
        (command_output, exitstatus) = pexpect.run(c,
                                                   events={"(?i)password": sudo_password},
                                                   withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to {0}: {1}".format(c, command_output.strip()))


def main():
    print("Hello, friend.")
    run_cli_commands(
        ["sudo firewall-cmd --zone=public --add-port=23/tcp", ], "gns3user\r")
    child = pexpect.spawn("telnet {0} {1}".format("192.168.1.1", 5002), maxread=360, searchwindowsize=360)
    if not child:
        raise RuntimeError("Cannot connect via Telnet.")
    child.delaybeforesend = 0.5
    prompts = [pexpect.EOF, "Press RETURN to get started", _PASSWORD_PROMPT, ] + PROMPT_LIST
    connected = False
    already_configured = False
    possible_active_session = True
    while not connected:
        index = child.expect_exact(prompts)
        # If EOF with no prompts found
        if index == 0:
            raise RuntimeError("Cannot connect via Telnet.")
        elif index == 1:
            # "Press RETURN to get started" appears if the device was properly restarted or reloaded,
            # clearing any artifacts from previous terminal sessions
            possible_active_session = False
            child.sendline("\r")
            # time.sleep(5)
        elif index == 2:
            # "Password" appears if the device has already been configured
            _vty_password = "cisco"
            already_configured = True
            child.sendline(_vty_password + "\r")
        else:
            # You may be accessing an active VTY line if a prompt appears immediately
            if possible_active_session:
                print("You may be accessing an open or uncleared virtual teletype session. \n" +
                      "Output from previous commands may cause pexpect expect calls to fail. \n" +
                      "We recommend you restart or reload this device to clear any artifacts. \n")
            if already_configured:
                print("This device has already been configured and secured. Changes may be \n" +
                      "incompatible with the current configuration. We recommend you reset \n" +
                      "the device to the default configuration or upload a complete new configuration. \n")
            connected = True
    print("Connected to device using Telnet.")

    child.sendline("\renable\r")
    child.expect_exact(PROMPT_LIST[1])

    print("Getting device information...")

    # Ask for the device info first, and then set the device's time to move the device info
    # into the 'before' buffer (weird pexpect issue)
    child.sendline("show version | include [IOSios] [Ss]oftware\r")
    child.expect_exact(PROMPT_LIST[1])

    child = set_clock(child)

    # Look for the text between the two carriage returns
    _software_ver = str(
        child.before).split("show version | include [IOSios] [Ss]oftware\r")[1].split("\r")[0].strip()
    if not re.compile(r"[IOSios] [Ss]oftware").search(_software_ver):
        raise RuntimeError("Cannot get the device's software version.")
    print("- Software version: {0}".format(_software_ver))

    child.sendline("show inventory | include [Cc]hassis\r")
    child.expect_exact(PROMPT_LIST[1])

    child = set_clock(child)

    _device_name = str(
        child.before).split("show inventory | include [Cc]hassis\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Cc]hassis").search(_device_name):
        raise RuntimeError("Cannot get the device's name.")
    print("- Device name: {0}".format(_device_name))

    child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]\r")
    child.expect_exact(PROMPT_LIST[1])

    child = set_clock(child)

    _serial_num = str(
        child.before).split("show version | include [Pp]rocessor [Bb]oard [IDid]\r")[1].split("\r")[0].strip()
    if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(_serial_num):
        raise RuntimeError("Cannot get the device's serial number.")
    print("- Serial number: {0}".format(_serial_num))

    print("Closing telnet connection...")
    child.sendline("disable\r")
    # time.sleep(1)
    child.expect_exact(PROMPT_LIST[0])
    child.sendcontrol("]")
    child.sendline("q\r")
    child.expect_exact("Connection closed.")
    # Close the Telnet child process
    child.close()
    # Close the firewall port
    run_cli_commands(
        ["sudo firewall-cmd --zone=public --remove-port=23/tcp", ], "gns3user\r")
    print("Telnet connection closed.")


def set_clock(child, timestamp=None):
    """Set the device's clock.

    :param pexpect.spawn child: The connection in a child application object.
    :param datetime timestamp: A datetime tuple (year, month, day, hour, minute, second).
    :returns: The updated connection in a child application object.
    :rtype: pexpect.spawn
    """
    if not timestamp:
        timestamp = datetime.utcnow()
    child.sendline("clock set {0}\r".format(timestamp.strftime("%H:%M:%S %d %b %Y")))
    child.expect_exact("{0}, configured from console by console".format(timestamp.strftime("%H:%M:%S UTC %a %b %d %Y")))
    return child


if __name__ == "__main__":
    main()
