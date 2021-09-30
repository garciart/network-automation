#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lab 000: Combo Lab

Tasks:
* Telnet into a device
* Format the flash memory.
* Save configuration

To run this lab:
* Start GNS3 by executing "gns3_run" in a Terminal window.
* Setup the lab environment according to lab001-telnet.md.
* Start all devices.
* Run this script (i.e., "python lab001-telnet.py")

Project: Automation

Requirements:
* Python 2.7+
* pexpect
* GNS3
"""
from __future__ import print_function

import os
import re
import shlex
import socket
import subprocess
import sys
import time
from getpass import getpass

import pexpect

import lab_utils

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"

GATEWAY_IP_ADDRESS = "192.168.1.1"
HOST_IP_ADDRESS = "192.168.1.10"
DEVICE_IP_ADDRESS = "192.168.1.20"
SUBNET_MASK = "255.255.255.0"
PROMPT_LIST = ["R1>", "R1#", "R1(", ]

sudo_password = None


def main():
    child = None
    try:
        print("Beginning lab...")
        child = connect_via_telnet(GATEWAY_IP_ADDRESS)
        child.delaybeforesend = 0.5
        # software_ver, device_name, serial_num
        _, _, _ = get_device_info(child)
        format_device_memory(child)
        assign_device_ip_addr(child, DEVICE_IP_ADDRESS, SUBNET_MASK)
        check_l3_connectivity(child, HOST_IP_ADDRESS, DEVICE_IP_ADDRESS)
        download_file_tftp(child, "startup-config")
        close_telnet_conn(child)
        print("Finished lab.")
    # Let the user know something went wrong and put the details in the log file.
    # Catch pexpect and subprocess exceptions first, so other exceptions
    # (e.g., BaseException, etc) do not handle them by accident
    except pexpect.ExceptionPexpect as pex:
        print(lab_utils.error_message(sys.exc_info(), pex=pex))
    except subprocess.CalledProcessError as cpe:
        print(lab_utils.error_message(sys.exc_info(), cpe=cpe))
    except BaseException:
        print(lab_utils.error_message(sys.exc_info()))
    finally:
        if child:
            child.close()
        print("\n***Restart the device before running this script again.***\n")
        print("Script complete. Have a nice day.")


def connect_via_telnet(gateway_ip_address):
    """Connect to the device via Telnet.

    :return: The connection in a child application object.
    :raise pexpect.ExceptionPexpect: If the result of a spawn or sendline command does not match the
      expected result (raised from the pexpect module).
    """
    print("Connecting to device using Telnet...")
    # Open Telnet connection port
    __run_commands(["sudo firewall-cmd --zone=public --add-port=23/tcp", ])
    """
    child = pexpect.spawn("sudo firewall-cmd --zone=public --add-port=23/tcp")
    index = child.expect_exact(["success", "password", ])
    if index == 1:
        child.sendline(__prompt_for_password())
        child.expect_exact("success")
    # Close this child; you will spawn a new one for the actual connection
    child.close()
    """
    print("Iterating through console port range...")
    # Connect to the device and allow time for any boot messages to clear
    console_ports = [str(p) for p in range(5000, (5005 + 1))]
    # Add a None as a flag to tell the loop that all ports were checked
    console_ports.append(None)
    child = None
    for port in console_ports:
        if child:
            child.close()
        child = pexpect.spawn("telnet {0} {1}".format(gateway_ip_address, port))
        # Do not use extend, do not overwrite PROMPT_LIST
        index = child.expect_exact(PROMPT_LIST + ["Press RETURN to get started", pexpect.EOF, ])
        if port is None:
            raise RuntimeError("Cannot connect to console port.")
        if index in range(len(PROMPT_LIST) + 1):
            break
    time.sleep(5)
    child.sendline("\r")
    child.expect_exact(PROMPT_LIST)
    print("Connected to device using Telnet.")
    return child


def get_device_info(child):
    """Get the device's flash memory. This will only work after a reload.

    :param pexpect.spawn child: The connection in a child application object.
    :returns: The device's Internetwork Operating System (IOS) version, model number, and serial number.
    :rtype: tuple
    :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
      expected result (raised from the pexpect module).
    """
    print("Getting device information...")
    __reset_prompt(child)
    # Reset pexpect cursor to multiple prompts in a row
    child.sendline("enable\r\r\r")
    child.expect_exact("enable\r\nR1#\r\nR1#\r\nR1#")

    child.send("show version | include [IOSios] [Ss]oftware\r\n")
    child.expect_exact("R1#")
    __software_ver = str(child.before).splitlines()[1]
    if not re.compile(r"[IOSios] [Ss]oftware").search(__software_ver):
        raise RuntimeError("Cannot get the device's software version.")
    print("- Software version: {0}".format(__software_ver))

    child.sendline("show inventory | include [Cc]hassis\r")
    child.expect_exact("R1#")
    __device_name = str(child.before).splitlines()[1]
    if not re.compile(r"[Cc]hassis").search(__device_name):
        raise RuntimeError("Cannot get the device's name.")
    print("- Device name: {0}".format(__device_name))

    child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]\r")
    child.expect_exact("R1#")
    __serial_num = str(child.before).splitlines()[1]
    if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(__serial_num):
        raise RuntimeError("Cannot get the device's serial number.")
    print("- Serial number: {0}".format(__serial_num))
    return __software_ver, __device_name, __serial_num


def format_device_memory(child):
    """Format the device's flash memory.

    :param pexpect.spawn child: The connection in a child application object.
    :return: None
    :rtype: None
    :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
      expected result (raised from the pexpect module).
    """
    print("Formatting flash memory...")
    __reset_prompt(child)
    child.sendline("format flash:\r")
    # Expect "Format operation may take a while. Continue? [confirm]"
    child.expect_exact("Continue? [confirm]")
    child.sendline("\r")
    # Expect "Format operation will destroy all data in "flash:".  Continue? [confirm]"
    child.expect_exact("Continue? [confirm]")
    child.sendline("\r")
    child.expect_exact("Format of flash complete", timeout=120)
    child.sendline("show flash\r")
    # Expect "XXXXXXXX bytes available (0 bytes used)"
    child.expect_exact("(0 bytes used)")
    print("Flash memory formatted.")


def assign_device_ip_addr(child, new_device_ip, subnet_mask):
    """Configure a device for Ethernet (Layer 3) connections.

    :param pexpect.spawn child: The connection in a child application object.
    :param str new_device_ip: The desired IPv4 address of the device.
    :param str subnet_mask: The subnet mask for the network.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to set the IPv4 address.
    """
    print("Configuring device for Ethernet (Layer 3) connections...")
    __reset_prompt(child)
    # Enter Global Configuration mode
    child.sendline("configure terminal\r")
    child.expect_exact("R1(config)#")
    # Access Ethernet port
    child.sendline("interface FastEthernet0/0\r")
    child.expect_exact("R1(config-if)#")
    # Assign an IPv4 address and subnet mask
    child.sendline("ip address {0} {1}\r".format(new_device_ip, subnet_mask))
    child.expect_exact("R1(config-if)#")
    # Bring the Ethernet port up
    child.sendline("no shutdown\r")
    time.sleep(5)
    child.expect_exact("R1(config-if)#")
    child.sendline("end\r")
    child.expect_exact("R1#")
    print("Device configured for Ethernet (Layer 3) connections.")


def check_l3_connectivity(child, host_ip, device_ip):
    """Check connectivity between devices using ping.

    :param pexpect.spawn child: The connection in a child application object.
    :param str host_ip: The IPv4 address of the host.
    :param str device_ip: The IPv4 address of the device.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to configure the device.
    """
    print("Checking connectivity...")
    try:
        socket.inet_pton(socket.AF_INET, host_ip)
        socket.inet_pton(socket.AF_INET, device_ip)
    except socket.error:
        raise RuntimeError("Invalid host or device IPv4 address.")
    __reset_prompt(child)
    # Ping the host from the device
    child.sendline("ping {0}\r".format(host_ip))
    # Check for the fail condition first, since the child will always return a prompt
    index = child.expect_exact(["Success rate is 0 percent", "R1#", ], timeout=60)
    if index == 0:
        raise RuntimeError("Unable to ping the host from the device.")
    else:
        # Ping the device from the host
        cmd = "ping -c 4 {0}".format(device_ip)
        # No need to read the output. Ping returns a non-zero value if no packets are received,
        # which will cause a check_output exception
        subprocess.check_output(shlex.split(cmd))
    print("Connectivity to and from the device is good.")


def download_file_tftp(child, file_path_to_download, new_file_name=None):
    """Download a file from a device using TFTP.

    Developer Note: TFTP must be installed: i.e., sudo yum -y install tftp tftp-server

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path_to_download: The location of the file to download (i.e., startup-config, flash:/foo.txt, etc.)
    :param str new_file_name: (Optional) A new name for the downloaded file.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable TFTP services.
    """
    print("Downloading {0} over TFTP...".format(file_path_to_download))
    __reset_prompt(child)
    # Ensure parameters are valid. Do not use os.path.basename; you are downloading from the device, and it may use a
    # different format from Linux
    new_file_name = file_path_to_download.rsplit('/', 1)[-1] if new_file_name is None else new_file_name
    __run_commands([
        "sudo firewall-cmd --zone=public --add-service=tftp",
        "sudo mkdir --parents --verbose /var/lib/tftpboot/Downloads",
        "sudo chmod 777 --verbose /var/lib/tftpboot/Downloads",
        "sudo touch /var/lib/tftpboot/Downloads/{0}".format(new_file_name),
        "sudo chmod 777 --verbose /var/lib/tftpboot/Downloads/{0}".format(new_file_name),
        "sudo systemctl enable tftp",
        "sudo systemctl start tftp",
    ])
    cmd = "copy {0} tftp://{1}/Downloads/{2}\r".format(file_path_to_download, HOST_IP_ADDRESS,  new_file_name)
    print(cmd)
    child.sendline("copy {0} tftp://{1}/Downloads/{2}\r".format(file_path_to_download, HOST_IP_ADDRESS,  new_file_name))
    child.expect_exact("Address or name of remote host")
    child.sendline("\r")
    child.expect_exact("Destination filename")
    child.sendline("\r")
    index = child.expect_exact(["bytes copied in", "Error", ])
    if index != 0:
        raise RuntimeError("Cannot download {0} from device using TFTP.".format(file_path_to_download))
    __run_commands([
        "sudo systemctl stop tftp",
        "sudo systemctl disable tftp",
        "sudo firewall-cmd --zone=public --remove-service=tftp",
    ])
    print("{0} downloaded.".format(file_path_to_download))


def upload_file_tftp(child, file_path, upload_path="flash:/"):
    """Upload a file to a device using TFTP.

    Developer Note: TFTP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to upload.
    :param str upload_path: The location to save the file; default is flash:/.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable TFTP services.
    """
    print("Uploading {0} over TFTP...".format(file_path))
    __reset_prompt(child)

    print("{0} uploaded.".format(file_path))


def download_file_ftp(child, file_path, download_path="~/Downloads"):
    """Download a file from a device using FTP.

    Developer Note: FTP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to download.
    :param str download_path: The location to save the file; default is ~/Downloads.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable FTP services.
    """
    print("Downloading {0} over FTP...".format(file_path))
    __reset_prompt(child)

    print("{0} downloaded.".format(file_path))


def upload_file_ftp(child, file_path, upload_path="flash:/"):
    """Upload a file to a device using FTP.

    Developer Note: FTP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to upload.
    :param str upload_path: The location to save the file; default is flash:/.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable FTP services.
    """
    print("Uploading {0} over FTP...".format(file_path))
    __reset_prompt(child)

    print("{0} uploaded.".format(file_path))


def download_file_scp(child, file_path, download_path="~/Downloads"):
    """Download a file from a device using SCP.

    Developer Note: SCP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to download.
    :param str download_path: The location to save the file; default is ~/Downloads.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable SCP services.
    """
    print("Downloading {0} over SCP...".format(file_path))
    __reset_prompt(child)

    print("{0} downloaded.".format(file_path))


def upload_file_scp(child, file_path, upload_path="flash:/"):
    """Upload a file to a device using SCP.

    Developer Note: SCP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to upload.
    :param str upload_path: The location to save the file; default is flash:/.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable SCP services.
    """
    print("Uploading {0} over SCP...".format(file_path))
    __reset_prompt(child)

    print("{0} uploaded.".format(file_path))


def download_file_sftp(child, file_path, download_path="~/Downloads"):
    """Download a file from a device using SFTP.

    Developer Note: SFTP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to download.
    :param str download_path: The location to save the file; default is ~/Downloads.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable SFTP services.
    """
    print("Downloading {0} over SFTP...".format(file_path))
    __reset_prompt(child)

    print("{0} downloaded.".format(file_path))


def upload_file_sftp(child, file_path, upload_path="flash:/"):
    """Upload a file to a device using SFTP.

    Developer Note: SFTP must be installed.

    :param pexpect.spawn child: The connection in a child application object.
    :param str file_path: The file to upload.
    :param str upload_path: The location to save the file; default is flash:/.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to enable or disable SFTP services.
    """
    print("Uploading {0} over SFTP...".format(file_path))
    __reset_prompt(child)

    print("{0} uploaded.".format(file_path))


def close_telnet_conn(child):
    """Close Telnet and disconnect from device.

    :param pexpect.spawn child: The connection in a child application object.

    :return: None
    :rtype: None
    """
    print("Closing telnet connection...")
    __reset_prompt(child)
    child.sendline("disable\r")
    time.sleep(1)
    child.expect_exact("R1>")
    child.sendcontrol("]")
    child.sendline("q\r")
    child.expect_exact("Connection closed.")
    # Close the Telnet child process
    child.close()
    # Close the firewall port
    __run_commands(["sudo firewall-cmd --zone=public --remove-port=23/tcp", ])
    print("Telnet connection closed.")


def __prompt_for_password():
    """Allows running of sudo commands.

    :return: The sudo password
    :rtype: str
    """
    global sudo_password
    if sudo_password is None:
        sudo_password = getpass(prompt="SUDO password: ") + "\r\n"
    return sudo_password


def __reset_prompt(child):
    """Resets the prompt to Privileged EXEC mode on Cisco devices.

    Check for a prompt:
         * "R1>" (User EXEC mode)
         * "R1#" (Privileged EXEC Mode)
         * "R1(" (Any Global Configuration mode: R1(config)#, R1(vlan)#, etc.)
    Then set to Privileged EXEC Mode using the "enable" or "end" commands.

    :param pexpect.spawn child: The connection in a child application object.
    :return: None
    :rtype: None
    :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
      expected result (raised from the pexpect module).
    """
    child.sendline("\r")
    index = child.expect_exact(PROMPT_LIST)
    if index == 0:
        child.sendline("enable\r")
        child.expect_exact("R1#")
    elif index == 2:
        # "End" takes you back to Privileged EXEC Mode, while "exit" takes you back to the previous mode.
        child.sendline("end\r")
        child.expect_exact("R1#")


def __run_commands(commands):
    """Run commands with error detection.

    :param list commands: The commands to execute.
    :return: None
    :rtype: None
    :raise RuntimeError: If unable to run a command.
    """
    for c in commands:
        (command_output, exitstatus) = pexpect.run(c,
                                                   events={"(?i)password": __prompt_for_password()},
                                                   withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError("Unable to {0}: {1}".format(c, command_output.strip()))


if __name__ == "__main__":
    print("Welcome to Lab 000!")
    main()
