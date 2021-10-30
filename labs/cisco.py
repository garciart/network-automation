"""Cisco device functions class

Project: Automation
"""
import os
import re
import socket
import sys
import time
from getpass import getpass

import pexpect

# Module metadata dunders
__author__ = "Rob Garcia"
__license__ = "MIT"


class Cisco:
    PROMPT_LIST = ["R1>", "R1#", "R1(config)#", "R1(config-if)#", "R1(config-router)#", "R1(config-line)#", ]

    _ACCESS_CONFIG_CMD = "configure terminal\r"
    _COPIED_MSG = "bytes copied in"
    _ENCRYPT_CONFIG_CMD = "service password-encryption\r"
    _EXIT_CMD = "exit\r"
    _FILE_SYSTEM_PREFIX = ["startup-config", "running-config", "nvram", "flash", "slot", ]
    _PASSWORD_PROMPT = "Password:"
    _SET_PASSWORD_CMD = "password {0}\r"
    _REQUIRE_LOGIN_CMD = "login\r"

    _sudo_password = None
    _enable_password = None
    _vty_password = None

    def __init__(self):
        """Class instantiation.

        :return: None
        :rtype: None
        """
        pass

    def connect_via_telnet(self, device_ip_addr, port_number=23):
        """Connect to the device via Telnet.

        :param str device_ip_addr: The IP address that will be used to connect to the device.
        :param int port_number: The port number for the connection.
        :return: The connection in a child application object.
        :raise pexpect.ExceptionPexpect: If the result of a spawn or sendline command does not match the
          expected result (raised from the pexpect module).
        :raise RuntimeError: If unable to connect via Telnet.
        """
        print("Connecting to device using Telnet...")
        # Validate arguments
        validate_ip_address(device_ip_addr)
        validate_port_number(port_number)
        # Open Telnet connection port
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands(
            ["sudo firewall-cmd --zone=public --add-port=23/tcp", ], self._sudo_password)
        child = pexpect.spawn("telnet {0} {1}".format(device_ip_addr, port_number))
        child.delaybeforesend = 1
        if not child:
            raise RuntimeError("Cannot connect via Telnet.")
        prompts = [pexpect.EOF, "Press RETURN to get started", self._PASSWORD_PROMPT, ] + self.PROMPT_LIST
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
                time.sleep(5)
            elif index == 2:
                # "Password" appears if the device has already been configured
                self._vty_password = prompt_for_vty_password(self._vty_password)
                already_configured = True
                child.sendline(self._vty_password + "\r")
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
        return child

    def close_telnet_conn(self, child):
        """Close Telnet and disconnect from device.

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        """
        print("Closing telnet connection...")
        self._reset_prompt(child)
        child.sendline("disable\r")
        time.sleep(1)
        child.expect_exact(self.PROMPT_LIST[0])
        child.sendcontrol("]")
        child.sendline("q\r")
        child.expect_exact("Connection closed.")
        # Close the Telnet child process
        child.close()
        # Close the firewall port
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands(
            ["sudo firewall-cmd --zone=public --remove-port=23/tcp", ], self._sudo_password)
        print("Telnet connection closed.")

    def get_device_info(self, child):
        """Get the device's flash memory. This will only work after a reload.

        :param pexpect.spawn child: The connection in a child application object.
        :returns: The device's Internetwork Operating System (IOS) version, model number, and serial number.
        :rtype: tuple
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Getting device information...")
        child = self._reset_prompt(child)
        i = child.sendline("show version | include [IOSios] [Ss]oftware\r")
        print(i)
        t = child.read()
        print(t)
        child.expect_exact(self.PROMPT_LIST[1])
        _software_ver = str(child.before).splitlines()[-1]
        if not re.compile(r"[IOSios] [Ss]oftware").search(_software_ver):
            raise RuntimeError("Cannot get the device's software version.")
        print("- Software version: {0}".format(_software_ver))

        child.sendline("show inventory | include [Cc]hassis\r")
        child.expect_exact(self.PROMPT_LIST[1])
        _device_name = str(child.before).splitlines()[-1]
        if not re.compile(r"[Cc]hassis").search(_device_name):
            raise RuntimeError("Cannot get the device's name.")
        print("- Device name: {0}".format(_device_name))

        child.sendline("show version | include [Pp]rocessor [Bb]oard [IDid]\r")
        child.expect_exact(self.PROMPT_LIST[1])
        _serial_num = str(child.before).splitlines()[-1]
        if not re.compile(r"[Pp]rocessor [Bb]oard [IDid]").search(_serial_num):
            raise RuntimeError("Cannot get the device's serial number.")
        print("- Serial number: {0}".format(_serial_num))
        return _software_ver, _device_name, _serial_num

    def format_flash_memory(self, child):
        """Format the device's flash memory.

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Formatting flash memory...")
        self._reset_prompt(child)
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
        print("Flash memory formatted: {0}".format(str(child.before).splitlines()[-1]))

    def set_device_ip_addr(self, child, new_device_ip_addr, subnet_mask):
        """Configure a device for Ethernet (Layer 3) connections.

        :param pexpect.spawn child: The connection in a child application object.
        :param str new_device_ip_addr: The desired IPv4 address of the device.
        :param str subnet_mask: The subnet mask for the network.
        :return: None
        :rtype: None
        :raise RuntimeError: If unable to set the IPv4 address.
        """
        print("Configuring device for Ethernet (Layer 3) connections...")
        # Validate arguments
        validate_ip_address(new_device_ip_addr)
        validate_subnet_mask(subnet_mask)
        self._reset_prompt(child)
        # Enter Global Configuration mode
        child.sendline(self._ACCESS_CONFIG_CMD)
        child.expect_exact(self.PROMPT_LIST[2])
        # Access Ethernet port
        child.sendline("interface FastEthernet0/0\r")
        child.expect_exact(self.PROMPT_LIST[3])
        # Assign an IPv4 address and subnet mask
        child.sendline("ip address {0} {1}\r".format(new_device_ip_addr, subnet_mask))
        child.expect_exact(self.PROMPT_LIST[3])
        # Bring the Ethernet port up
        child.sendline("no shutdown\r")
        time.sleep(1)
        child.expect_exact(self.PROMPT_LIST[3])
        child.sendline("end\r")
        child.expect_exact(self.PROMPT_LIST[1])
        print("Device configured for Ethernet (Layer 3) connections.")

    def check_l3_connectivity(self, child, host_ip_addr, device_ip_addr):
        """Check connectivity between devices using ping.

        :param pexpect.spawn child: The connection in a child application object.
        :param str host_ip_addr: The IPv4 address of the host.
        :param str device_ip_addr: The IPv4 address of the device.
        :return: None
        :rtype: None
        :raise RuntimeError: If unable to configure the device.
        """
        print("Checking connectivity...")
        # Validate arguments
        validate_ip_address(host_ip_addr)
        validate_ip_address(device_ip_addr)
        self._reset_prompt(child)
        # Ping the host from the device
        child.sendline("ping {0}\r".format(host_ip_addr))
        # Check for the fail condition first, since the child will always return a prompt
        index = child.expect_exact(["Success rate is 0 percent", self.PROMPT_LIST[1], ], timeout=60)
        if index == 0:
            raise RuntimeError("Unable to ping the host from the device.")
        else:
            # Ping the device from the host
            cmd = "ping -c 4 {0}".format(device_ip_addr)
            # No need to read the output. Ping returns a non-zero value if no packets are received,
            # which will cause a check_output exception
            # subprocess.check_output(shlex.split(cmd))
            run_cli_commands([cmd, ])
        print("Connectivity check is good.")

    def download_from_device_tftp(self, child, device_filepath, host_ip_addr, new_filename=None):
        """Download a file from a device using TFTP.

        Developer Note: TFTP must be installed: i.e., sudo yum -y install tftp tftp-server

        :param pexpect.spawn child: The connection in a child application object.
        :param str device_filepath: The location of the file to download (i.e., startup-config, flash:/foo.txt, etc.)
        :param str host_ip_addr: The IPv4 address of the host.
        :param str new_filename: (Optional) A new name for the downloaded file.
        :return: None
        :rtype: None
        :raise RuntimeError: If unable to enable or disable TFTP services.
        """
        print("Downloading {0} over TFTP...".format(device_filepath))
        # Validate arguments
        if not device_filepath.startswith(tuple(self._FILE_SYSTEM_PREFIX)):
            raise ValueError("Valid device file system (flash:, slot0:, etc.) not specified.")
        validate_ip_address(host_ip_addr)
        # Do not use os.path.basename; you are downloading from the device,
        # and it may use a different format from Linux
        new_filename = device_filepath.rsplit('/', 1)[-1] if new_filename is None else new_filename.lstrip(
            "/").replace("var/lib/tftpboot", "").lstrip("/")
        self._reset_prompt(child)
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands([
            "sudo firewall-cmd --zone=public --add-service=tftp",
            "sudo mkdir --parents --verbose /var/lib/tftpboot",
            "sudo chmod 777 --verbose /var/lib/tftpboot",
            "sudo touch /var/lib/tftpboot/{0}".format(new_filename),
            "sudo chmod 777 --verbose /var/lib/tftpboot/{0}".format(new_filename),
            "sudo systemctl enable tftp",
            "sudo systemctl start tftp",
        ], self._sudo_password)
        child.sendline("copy {0} tftp://{1}/{2}\r".format(device_filepath, host_ip_addr, new_filename))
        child.expect_exact("Address or name of remote host")
        child.sendline("\r")
        child.expect_exact("Destination filename")
        child.sendline("\r")
        index = child.expect_exact([self._COPIED_MSG, "Error", ], timeout=60)
        if index != 0:
            raise RuntimeError("Cannot download {0} from device using TFTP.".format(device_filepath))
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands([
            "sudo systemctl stop tftp",
            "sudo systemctl disable tftp",
            "sudo firewall-cmd --zone=public --remove-service=tftp",
        ], self._sudo_password)
        print("File downloaded to /var/lib/tftpboot/{0}.".format(new_filename))

    def upload_to_device_tftp(self, child, upload_filepath, host_ip_addr, new_filename=None):
        """Upload a file to a device using TFTP. The file will be saved in the flash file system (i.e., flash:/foo.txt),
        unless prefixed by another file system (i.e., slot0:/bar.txt)

        Developer Note: TFTP must be installed.

        :param pexpect.spawn child: The connection in a child application object.
        :param str upload_filepath: The file to upload.
        :param str host_ip_addr: The IPv4 address of the host.
        :param str new_filename: (Optional) A new name for the uploaded file.
        :return: None
        :rtype: None
        :raise RuntimeError: If unable to enable or disable TFTP services.
        """
        print("Uploading {0} over TFTP...".format(os.path.basename(upload_filepath)))
        # Validate arguments
        if not upload_filepath.lstrip("/").startswith("var/lib/tftpboot"):
            raise RuntimeError(
                "The filepath must start with /var/lib/tftpboot and the file to upload must be in that directory.")
        validate_ip_address(host_ip_addr)
        if new_filename and not new_filename.startswith(tuple(self._FILE_SYSTEM_PREFIX)):
            raise ValueError("Valid device file system (flash:, slot0:, etc.) not specified.")
        self._reset_prompt(child)
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands([
            "sudo firewall-cmd --zone=public --add-service=tftp",
            "sudo chmod 777 --verbose /var/lib/tftpboot/",
            "sudo chmod 777 --verbose {0}".format(upload_filepath),
            "sudo systemctl enable tftp",
            "sudo systemctl start tftp",
        ], self._sudo_password)
        # Ensure parameters are valid. Do not use os.path.basename; you are uploading to the device, and it may use a
        # different format from Linux
        if new_filename is None:
            print("No file system specified. Uploading to flash:/")
        new_filename = upload_filepath.rsplit('/', 1)[-1] if new_filename is None else new_filename
        # Remove /var/lib/tftpboot/ from upload_filepath; copy will automatically use /var/lib/tftpboot/
        child.sendline("copy tftp://{0}/{1} {2}\r".format(
            host_ip_addr, upload_filepath.replace("/var/lib/tftpboot/", ""), new_filename))
        child.expect_exact("Destination filename")
        child.sendline("\r")
        index = child.expect_exact(["Error", self._COPIED_MSG, "Do you want to over write", ])
        # Check for over write message first, but leave "Error" at index 0
        if index == 2:
            child.sendline("\r")
            index = child.expect_exact(["Error", self._COPIED_MSG, ])
        if index == 0:
            raise RuntimeError("Cannot upload {0} to device using TFTP.".format(upload_filepath))
        self._sudo_password = prompt_for_sudo_password()
        run_cli_commands([
            "sudo systemctl stop tftp",
            "sudo systemctl disable tftp",
            "sudo firewall-cmd --zone=public --remove-service=tftp",
        ], self._sudo_password)
        print("{0} uploaded.".format(os.path.basename(new_filename)))

    def update_startup_config(self, child):
        """Save changes to the running configuration (e.g., IP address, etc.) to the device's default startup
        configuration.

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Updating the device's startup configuration...")
        self._reset_prompt(child)
        child.sendline("write memory\r")
        time.sleep(1)
        index = child.expect_exact(["Error", "[OK]", ])
        if index == 0:
            raise RuntimeError("Cannot update startup configuration.")
        print("Startup configuration updated.")

    def restore_startup_config(self, child):
        """Restore configuration from a backup. Backup must exist in the device's flash file system.

        :param pexpect.spawn child: The connection in a child application object.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Restoring the device's startup configuration...")
        self._reset_prompt(child)
        child.sendline("copy startup-config.bak startup-config\r")
        index = child.expect_exact(["Error", "[OK]", "Destination filename [startup-config]?", ], timeout=60)
        # Check for destination filename message first, but leave "Error" at index 0
        if index == 2:
            child.sendline("\r")
            index = child.expect_exact(["Error", "[OK]", ], timeout=60)
        if index == 0:
            raise RuntimeError("Cannot restore startup configuration.")
        print("Startup configuration restored.")

    def secure_privileged_exec_mode(self, child, password, encrypt=True):
        """Require a password when entering Privileged EXEC mode from user EXEC mode.

        :param pexpect.spawn child: The connection in a child application object.
        :param string password: The desired Privileged EXEC mode password.
        :param bool encrypt: If True, encrypt the password in the startup and running config files;
          otherwise, store in plain text.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Securing Privileged EXEC mode...")
        self._reset_prompt(child)
        child.sendline(self._ACCESS_CONFIG_CMD)
        child.expect_exact(self.PROMPT_LIST[2])
        if encrypt:
            child.sendline("enable secret {0}\r".format(password))
        else:
            child.sendline("enable password {0}\r".format(password))
        child.expect_exact(self.PROMPT_LIST[2])
        self._reset_prompt(child)
        print("Privileged EXEC mode secured.")

    def secure_console_port(self, child, password, encrypt=True):
        """Require a password when accessing the device through the console port.

        :param pexpect.spawn child: The connection in a child application object.
        :param string password: The desired console terminal password.
        :param bool encrypt: If True, encrypt the password in the startup and running config files;
          otherwise, store in plain text.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Securing the console port...")
        self._reset_prompt(child)
        # Enter Global configuration mode
        child.sendline(self._ACCESS_CONFIG_CMD)
        child.expect_exact(self.PROMPT_LIST[2])
        # Enter configuration mode for the console port
        child.sendline("line console 0\r")
        child.expect_exact(self.PROMPT_LIST[5])
        # Set the console terminal password
        child.sendline(self._SET_PASSWORD_CMD.format(password))
        child.expect_exact(self.PROMPT_LIST[5])
        # Require console terminal login
        child.sendline(self._REQUIRE_LOGIN_CMD)
        child.expect_exact(self.PROMPT_LIST[5])
        if encrypt:
            child.sendline(self._EXIT_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
            child.sendline(self._ENCRYPT_CONFIG_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
        self._reset_prompt(child)
        print("Console port secured.")

    def secure_auxiliary_port(self, child, password, encrypt=True):
        """Require a password when accessing the device through the auxiliary port.

        :param pexpect.spawn child: The connection in a child application object.
        :param string password: The desired auxiliary terminal password.
        :param bool encrypt: If True, encrypt the password in the startup and running config files;
          otherwise, store in plain text.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Securing the Auxiliary port...")
        self._reset_prompt(child)
        # Enter Global configuration mode
        child.sendline(self._ACCESS_CONFIG_CMD)
        child.expect_exact(self.PROMPT_LIST[2])
        # Enter configuration mode for the auxiliary port
        child.sendline("line aux 0\r")
        child.expect_exact(self.PROMPT_LIST[5])
        # Set the auxiliary terminal password
        child.sendline(self._SET_PASSWORD_CMD.format(password))
        child.expect_exact(self.PROMPT_LIST[5])
        # Require auxiliary terminal login
        child.sendline(self._REQUIRE_LOGIN_CMD)
        child.expect_exact(self.PROMPT_LIST[5])
        if encrypt:
            child.sendline(self._EXIT_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
            child.sendline(self._ENCRYPT_CONFIG_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
        self._reset_prompt(child)
        print("Auxiliary port secured.")

    def secure_virtual_teletype(self, child, password, encrypt=True):
        """Require a password when accessing the device's virtual teletype (VTY) remote terminal through
        Telnet, SSH, etc.

        :param pexpect.spawn child: The connection in a child application object.
        :param string password: The desired VTY terminal password.
        :param bool encrypt: If True, encrypt the password in the startup and running config files;
          otherwise, store in plain text.
        :return: None
        :rtype: None
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        print("Securing Virtual Teletype (vty) remote terminal access...")
        self._reset_prompt(child)
        # Enter Global configuration mode
        child.sendline(self._ACCESS_CONFIG_CMD)
        child.expect_exact(self.PROMPT_LIST[2])
        # Enter configuration mode for all 5 (0-4) VTY terminals
        child.sendline("line vty 0 4\r")
        child.expect_exact(self.PROMPT_LIST[5])
        # Set the VTY terminal password
        child.sendline(self._SET_PASSWORD_CMD.format(password))
        child.expect_exact(self.PROMPT_LIST[5])
        # Require Telnet and SSH login
        child.sendline(self._REQUIRE_LOGIN_CMD)
        child.expect_exact(self.PROMPT_LIST[5])
        if encrypt:
            child.sendline(self._EXIT_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
            child.sendline(self._ENCRYPT_CONFIG_CMD)
            child.expect_exact(self.PROMPT_LIST[2])
        self._reset_prompt(child)
        print("Virtual Teletype (vty) remote terminal access secured.")

    def _reset_prompt(self, child):
        """Resets the prompt to Privileged EXEC mode on Cisco devices.

        Check for a prompt:
             * "R1>" (User EXEC mode)
             * "R1#" (Privileged EXEC Mode)
             * "R1(*)" (Any Global Configuration mode: R1(config)#, R1(vlan)#, etc.)
        Then set to Privileged EXEC Mode using the "enable" or "end" commands.

        :param pexpect.spawn child: The connection in a child application object.
        :return: The updated connection in a child application object.
        :rtype: pexpect.spawn
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        # child.sendline(self._EXIT_CMD)
        # child.expect_exact(["Press RETURN to get started", ] + self.PROMPT_LIST)
        child.sendline("\r")
        index = child.expect_exact([self._PASSWORD_PROMPT, ] + self.PROMPT_LIST)
        if index == 0:
            self._vty_password = prompt_for_vty_password(self._vty_password)
            child.sendline(self._vty_password + "\r")
            index = child.expect_exact(self.PROMPT_LIST)
            if index == 0:
                child.sendline("enable\r")
                index = child.expect_exact([self._PASSWORD_PROMPT, ] + self.PROMPT_LIST)
                if index == 0:
                    self._enable_password = prompt_for_enable_password(self._enable_password)
                    child.sendline(self._enable_password + "\r")
                    child.expect_exact(self.PROMPT_LIST)
        return child
        """
        elif index > 1:
            # "End" takes you back to Privileged EXEC Mode, while "exit" takes you back to the previous mode.
            child.sendline("end\r")
            child.expect_exact(self.PROMPT_LIST[1])
        """


def validate_ip_address(ip_address, ipv4_only=True):
    """Checks that the argument is a valid IP address.

    :param str ip_address: The IP address to check.
    :param bool ipv4_only: If the method should only validate IPv4-type addresses.

    :return: True if the IP address is valid; false if not.
    :rtype: bool

    :raises ValueError: If the IP address is invalid.
    """
    if ip_address is not None and ip_address.strip():
        ip_address = ip_address.strip()
        try:
            socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            if ipv4_only:
                raise ValueError("Argument contains an invalid IPv4 address: {0}".format(ip_address))
            else:
                try:
                    socket.inet_pton(socket.AF_INET6, ip_address)
                except socket.error:
                    raise ValueError("Argument contains an invalid IP address: {0}".format(ip_address))
        return True
    else:
        raise ValueError("Argument contains an invalid IP address: {0}".format(ip_address))


def validate_subnet_mask(subnet_mask):
    """Checks that the argument is a valid subnet mask.

    :param str subnet_mask: The subnet mask to check.

    :return: True if the subnet mask is valid; false if not.
    :rtype: bool

    :raises ValueError: if the subnet mask is invalid.

    .. seealso::
        https://codereview.stackexchange.com/questions/209243/verify-a-subnet-mask-for-validity-in-python
    """
    if subnet_mask is not None and subnet_mask.strip():
        subnet_mask = subnet_mask.strip()
        a, b, c, d = (int(octet) for octet in subnet_mask.split("."))
        mask = a << 24 | b << 16 | c << 8 | d
        if mask < 1:
            raise ValueError("Invalid subnet mask: {0}".format(subnet_mask))
        else:
            # Count the number of consecutive 0 bits at the right.
            # https://wiki.python.org/moin/BitManipulation#lowestSet.28.29
            m = mask & -mask
            right0bits = -1
            while m:
                m >>= 1
                right0bits += 1
            # Verify that all the bits to the left are 1"s
            if mask | ((1 << right0bits) - 1) != 0xffffffff:
                raise ValueError("Invalid subnet mask: {0}".format(subnet_mask))
        return True
    else:
        raise ValueError("Invalid subnet mask: {0}.".format(subnet_mask))


def validate_port_number(port_number):
    """Check if the port number is within range.

    :param int port_number: The port number to check.

    :return: True if the port number is valid; false if not.
    :rtype: bool

    :raises ValueError: if the port number is invalid.
    """
    if port_number not in range(0, 65535):
        raise ValueError("Invalid port number.")
    return True


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


def prompt_for_sudo_password(sudo_password=None):
    """Prompts for a password to run sudo commands.

    :param str sudo_password: The sudo password, if it exists. If supplied, there will be no prompt.
    :return: The sudo password received as an argument or from the prompt.
    :rtype: str
    """
    if sudo_password is None:
        sudo_password = getpass(prompt="SUDO password: ") + "\r"
    return sudo_password


def prompt_for_enable_password(enable_password=None):
    """Prompts for a password to access Privileged EXEC mode.

    :param str enable_password: The enable password, if it exists. If supplied, there will be no prompt.
    :return: The Privileged EXEC mode password received as an argument or from the prompt.
    :rtype: str
    """
    if enable_password is None:
        enable_password = getpass(prompt="Privileged EXEC mode password: ")
    return enable_password


def prompt_for_vty_password(vty_password=None):
    """Prompts for a password to access the device's virtual teletype (VTY) remote terminal.

    :param str vty_password: The virtual teletype (VTY) password, if it exists. If supplied, there will be no prompt.
    :return: The VTY terminal password received as an argument or from the prompt.
    :rtype: str
    """
    if vty_password is None:
        vty_password = getpass(prompt="VTY terminal password: ")
    return vty_password


if __name__ == "__main__":
    print("Error: Script {0} cannot be run independently.".format(os.path.basename(sys.argv[0])))
