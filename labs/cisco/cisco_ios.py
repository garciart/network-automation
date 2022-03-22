# -*- coding: utf-8 -*-
"""Common Cisco IOS and IOS-XE tasks.
"""
import os
import re
import sys
import time
from datetime import datetime

import pexpect

from labs.cisco.utility import (validate_ip_address,
                                validate_port_number,
                                validate_subnet_mask,
                                validate_filepath,
                                fix_tftp_filepath,
                                prep_for_tftp_download,
                                enable_tftp,
                                disable_tftp, )

__all__ = ['CiscoIOS', ]


class CiscoIOS(object):
    cisco_prompts = [
        '>', '#', '(config)#', '(config-if)#', '(config-line)#', '(config-switch)#',
        '(config-router)#', ]

    def __init__(self, device_hostname):
        """Class instantiation

        :param str device_hostname: Hostname of the device.
        
        :return: None
        :rtype: None
        """
        self.device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self.device_prompts = ['{0}{1}'.format(device_hostname, p) for p in self.cisco_prompts]

    def connect_via_telnet(self,
                           reporter,
                           telnet_ip_addr,
                           telnet_port_num=22,
                           verbose=True,
                           eol='',
                           username=None,
                           password=None,
                           enable_password=None):
        """Connect to a network device using Telnet.

        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str telnet_ip_addr: Device's IP address for Telnet.
        :param int telnet_port_num: Port number for the connection, both standard (22) and others.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file.
        :param str eol: EOL sequence (LF or CLRF) used by the connection (See comments below).
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Connection in a child application object.
        :rtype: pexpect.spawn
        """
        reporter.step(
            'Connecting to {0} on port {1} via Telnet...'.format(telnet_ip_addr, telnet_port_num))

        _, exitstatus = pexpect.run('which telnet', withexitstatus=True)
        if exitstatus != 0:
            raise RuntimeError('Telnet client is not installed.')

        # Validate inputs
        validate_ip_address(telnet_ip_addr)
        if telnet_port_num:
            validate_port_number(telnet_port_num)

        if telnet_port_num:
            child = pexpect.spawn('telnet {0} {1}'.format(telnet_ip_addr, telnet_port_num))
        else:
            child = pexpect.spawn('telnet {0}'.format(telnet_ip_addr))

        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile = sys.stdout
        else:
            # Save output to file
            output_file = open('{0}-{1}'.format(
                self.device_hostname, datetime.utcnow().strftime('%y%m%d-%H%M%SZ')), 'wb')
            child.logfile = output_file

        # End-of-line (EOL) issues: pexpect.sendline() sends a line feed ('\n') after the text.
        # However, depending on:
        # - The physical port used to connect to the device (e.g., VTY, Console, etc.)
        # - The protocol (e.g., Telnet, SSH, Reverse Telnet, etc.)
        # - The network port (e.g., 23, 2000, 4000, etc.)
        # - The terminal emulator (e.g., PuTTY, Minicom, etc.)
        # - The emulation (e.g., VT100, VT102, ANSI, etc.)
        # The device may require a carriage return ('\r') before the line feed to create a CRLF
        # (i.e., pexpect.sendline('text\r')).
        # Therefore, the user must designate an EOL, based on the connection,
        # which will be appended to each sendline.

        # Get to Privileged EXEC Mode
        self.__clear_startup_prompts(child, reporter, eol, username, password)
        self.__access_priv_exec_mode(child, eol, enable_password)

        reporter.success()
        return child

    def connect_via_serial(self,
                           reporter,
                           serial_device='ttyUSB0',
                           baud_rate=9600,
                           data_bits=8,
                           verbose=True,
                           eol='',
                           username=None,
                           password=None,
                           enable_password=None):
        """Connect to the device using Minicom.

        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str serial_device: PMA serial device interface name.
        :param int baud_rate: Baud rate for connection.
        :param int data_bits: Data bit size for connection.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file.
        :param str eol: EOL sequence (LF or CLRF) used by the connection (See EOL comments below).
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Connection in a child application object.
        :rtype: pexpect.spawn
        """
        # Validate inputs
        if serial_device not in ('ttyACM0', 'ttyUSB0',):
            reporter.error()
            raise ValueError('Invalid serial device name.')
        if baud_rate not in (50, 75, 110, 150, 300, 600, 1200, 1800, 2000, 2400, 3600, 4800, 7200,
                             9600, 14400, 19200, 28800, 38400, 56000, 57600, 115200, 128000,):
            reporter.error()
            raise ValueError('Invalid baud rate.')
        if data_bits not in (7, 8,):
            reporter.error()
            raise ValueError('Invalid data bit size.')

        reporter.step('Checking if Minicom is installed...')
        _, exitstatus = pexpect.run('which minicom', withexitstatus=True)
        if exitstatus != 0:
            reporter.error()
            raise RuntimeError('Minicom is not installed.')
        reporter.success()

        reporter.step('Connecting to device via {0}...'.format(serial_device))
        # Format: minicom --device /dev/ttyUSB0 --baudrate 9600 --8bit --noinit
        mode = '--8bit' if data_bits == 8 else '--7bit'
        cmd = 'minicom --device {0} --baudrate {1} {2} --noinit'.format(
            serial_device, baud_rate, mode)
        child = pexpect.spawn(cmd)
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile = sys.stdout

        # End-of-line (EOL) issues: pexpect.sendline() sends a line feed ('\n') after the text.
        # However, depending on:
        # - The physical port used to connect to the device (e.g., VTY, Console, etc.)
        # - The protocol (e.g., Telnet, SSH, Reverse Telnet, etc.)
        # - The network port (e.g., 23, 2000, 4000, etc.)
        # - The terminal emulator (e.g., PuTTY, Minicom, etc.)
        # - The emulation (e.g., VT100, VT102, ANSI, etc.)
        # The device may require a carriage return ('\r') before the line feed to create a CRLF
        # (i.e., pexpect.sendline('text\r')).
        # Therefore, the user must designate an EOL, based on the connection,
        # which will be appended to each sendline.

        # Get to Privileged EXEC Mode
        self.__clear_startup_prompts(child, reporter, eol, username, password)
        self.__access_priv_exec_mode(child, eol, enable_password)

        reporter.success()
        return child

    # NOTE - Cannot reduce the code complexity of this method in Python 2.7
    # The purpose of trailing NOSONAR comment is to suppress the SonarLint warning
    def __clear_startup_prompts(  # NOSONAR
            self, child, reporter, eol='', username=None, password=None):
        """**RUN IMMEDIATELY AFTER PEXPECT.SPAWN!**

        This method clears common Cisco IOS startup messages and prompts until it reaches a
        device prompt (e.g., switch>, switch#, etc.).

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.

        :return: None
        :rtype: None
        """
        # Check for a hostname prompt (e.g., switch#) first.
        # If you find a hostname prompt, you have cleared the startup messages.
        # However, if the first thing you find is a hostname prompt, you are accessing
        # an open line. Warn the user, but return control back to the calling method

        child.sendline('\r')

        # noinspection PyTypeChecker
        index = child.expect_exact([pexpect.TIMEOUT, ] + self.device_prompts, timeout=5)
        if index != 0:
            reporter.warn(
                '\x1b[31;1mYou may be accessing an open or uncleared virtual teletype session.\n' +
                'Output from previous commands may cause pexpect searches to fail.\n' +
                'To prevent this in the future, reload the device to clear any artifacts.\x1b[0m')
            self.__reset_pexpect_cursor(child, eol)
            return

        # Set initial timeout to 10 minutes to clear startup messages
        timeout = 600
        # If a prompt is not found, attempt to force a prompt by sending a CRLF (see below)
        force_prompt = True
        # Cycle through the startup prompts until you get to a hostname prompt
        index = 0
        while 0 <= index <= 6:
            try:
                index = child.expect_exact(
                    ['Login invalid',
                     'Bad passwords',
                     'Username:',
                     'Password:',
                     'Would you like to enter the initial configuration dialog',
                     'Would you like to terminate autoinstall',
                     'Press RETURN to get started',
                     ] + self.device_prompts, timeout=timeout)
                # Do not use range (it is zero-based and does not assess the high value)
                if index in (0, 1,):
                    reporter.error()
                    raise ValueError('Invalid credentials provided.')
                elif index == 2:
                    child.sendline(username + eol)
                elif index == 3:
                    child.sendline(password + eol)
                    reporter.warn(
                        '\x1b[31;1m' +
                        'Warning - This device has already been configured and secured.\n' +
                        'Changes made by this script may be incompatible with the current ' +
                        'configuration.' +
                        '\x1b[0m')
                elif index == 4:
                    child.sendline('no' + eol)
                elif index == 5:
                    child.sendline('yes' + eol)
                elif index == 6:
                    child.sendline(eol)
                timeout = 120
            except pexpect.TIMEOUT as pex:
                # If no prompt appears, the device may be waiting for input. Send a full CRLF to
                # force; if the prompt still does not appear, then raise an exception
                if force_prompt:
                    child.sendline('\r')
                    force_prompt = False
                else:
                    reporter.error()
                    raise pex

    def __access_priv_exec_mode(self, child, eol='', enable_password=None):
        """This method places the pexpect cursor at a Privileged EXEC Mode prompt (e.g., switch#)
        for subsequent commands.

        :param pexpect.spawn child: Connection in a child application object.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None
        """
        self.__reset_pexpect_cursor(child, eol)
        child.sendline(eol)
        index = child.expect_exact(self.device_prompts)
        if index == 0:
            # Get out of User EXEC Mode
            child.sendline('enable' + eol)
            index = child.expect_exact(['Password:', self.device_prompts[1], ])
            if index == 0:
                child.sendline(enable_password + eol)
                child.expect_exact(self.device_prompts[1])
        elif index != 1:
            # Get out of Global Configuration Mode
            child.sendline('end' + eol)
            child.expect_exact(self.device_prompts[1])

    def __reset_pexpect_cursor(self, child, eol=''):
        """This method sends a 'tracer round' in the form of a timestamp comment to move the
        pexpect cursor forward to the last hostname prompt.

        :param pexpect.spawn child: Connection in a child application object.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.

        :return: None
        :rtype: None
        """
        # Wait five seconds to allow any system messages to clear
        time.sleep(5)

        tracer_round = ';{0}'.format(int(time.time()))
        # Add the EOL here, not in the tracer_round, or you won't find the tracer_round later
        child.sendline(tracer_round + eol)
        child.expect_exact('{0}'.format(tracer_round))
        # WATCH YOUR CURSORS! You must also consume the prompt after tracer_round
        # or the pexepect cursor will stop at the wrong prompt
        # The next cursor will stop here -> R2#show version | include [IOSios] [Ss]oftware
        #                                   Cisco IOS Software...
        #      But it needs to stop here -> R2#
        child.expect_exact(self.device_prompts)

    def get_device_info(self, child, reporter, eol='', enable_password=None):
        """Get information about the network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Name of the default file system; the device's IOS version; the device's  name;
            and the device's serial number.
        :rtype: tuple
        """
        reporter.step('Getting device information...')
        self.__access_priv_exec_mode(child, eol, enable_password)

        try:
            # Get the name of the default drive. Depending on the device, it may be bootflash,
            # flash, slot (for linear memory cards), or disk (for CompactFlash disks)
            child.sendline('dir' + eol)
            index = child.expect_exact(['More', self.device_prompts[1], ])
            dir_list = str(child.before)
            if index == 0:
                # No need to get the whole dir listing; break the printout of the listing
                child.sendcontrol('c')
                child.expect_exact(self.device_prompts[1])
            default_file_system = dir_list.split(
                'Directory of ')[1].split(':')[0].strip()
            if not default_file_system.startswith(('bootflash', 'flash', 'slot', 'disk',)):
                raise RuntimeError('Cannot get the device\'s working drive.')
            # If the drive is not formatted, a warning will appear, followed by another prompt.
            # Wait for it to pass, and get to the correct prompt
            child.expect_exact(
                ['before an image can be booted from this device', pexpect.TIMEOUT, ], timeout=5)
            self.__reset_pexpect_cursor(child, eol)
        except (RuntimeError, IndexError) as ex:
            # RuntimeError = explicit, while IndexError = implicit if split index is out of range
            reporter.warn(ex.message)
            default_file_system = None

        try:
            # Get the IOS version
            child.sendline('show version | include [IOSios] [Ss]oftware' + eol)
            child.expect_exact(self.device_prompts[1])
            software_ver = str(child.before).split(
                'show version | include [IOSios] [Ss]oftware\r')[1].split('\r')[0].strip()
            if not re.compile(r'[IOSios] [Ss]oftware').search(software_ver):
                raise RuntimeError('Cannot get the device\'s software version.')
        except (RuntimeError, IndexError) as ex:
            reporter.warn(ex.message)
            software_ver = None

        try:
            # Get the name of the device
            child.sendline('show inventory | include [Cc]hassis' + eol)
            child.expect_exact(self.device_prompts[1])
            device_name = str(child.before).split(
                'show inventory | include [Cc]hassis\r')[1].split('\r')[0].strip()
            if not re.compile(r'[Cc]hassis').search(device_name):
                raise RuntimeError('Cannot get the device\'s name.')
        except (RuntimeError, IndexError) as ex:
            reporter.warn(ex.message)
            device_name = None

        try:
            # Get the serial number of the device
            child.sendline('show version | include [Pp]rocessor [Bb]oard [IDid]' + eol)
            child.expect_exact(self.device_prompts[1])
            serial_num = str(child.before).split(
                'show version | include [Pp]rocessor [Bb]oard [IDid]\r')[1].split('\r')[0].strip()
            if not re.compile(r'[Pp]rocessor [Bb]oard [IDid]').search(serial_num):
                raise RuntimeError('Cannot get the device\'s serial number.')
        except (RuntimeError, IndexError) as ex:
            reporter.warn(ex.message)
            serial_num = None

        reporter.success()
        return default_file_system, software_ver, device_name, serial_num

    def format_file_system(self, child, reporter, eol, file_system):
        """Format a file system (i.e., memory) on a network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str file_system: File system to format.

        :return: None
        :rtype: None
        """
        # Validate inputs
        if not file_system.startswith(('bootflash', 'flash', 'slot', 'disk',)):
            reporter.error()
            raise ValueError('Invalid Cisco file system name.')

        reporter.step('Formatting device memory...')
        self.__access_priv_exec_mode(child, eol)
        # Format the memory. Look for the final characters of the following strings:
        # 'Format operation may take a while. Continue? [confirm]'
        # 'Format operation will destroy all data in 'flash:'.  Continue? [confirm]'
        # '66875392 bytes available (0 bytes used)'
        child.sendline('format {0}:'.format(file_system) + eol)
        index = 1
        while index != 0:
            index = child.expect_exact(
                [pexpect.TIMEOUT, 'Continue? [confirm]', 'Enter volume ID', ], timeout=5)
            if index != 0:
                child.sendline(eol)
        child.expect_exact('Format of {0} complete'.format(file_system), timeout=120)
        child.sendline('show {0}'.format(file_system) + eol)
        child.expect_exact('(0 bytes used)')
        child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_switch_ip_addr(self, child, reporter, eol, vlan_name, vlan_port, new_ip_address,
                           new_netmask, commit=True):
        """Set a switch's IP address.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str vlan_name: Virtual Local Area Network (VLAN) interface to configure.
        :param str vlan_port: Ethernet interface port name to configure and connect to VLAN.
        :param str new_ip_address: New IPv4 address for the device.
        :param str new_netmask: New netmask for the device.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        # Validate inputs
        # ethernet_port, while not validated, should start with F(ast), G(iga), etc.
        validate_ip_address(new_ip_address)
        validate_subnet_mask(new_netmask)

        reporter.step('Setting the switch\'s IP address...')

        self.__access_priv_exec_mode(child, eol)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])

        # Configure Ethernet port
        child.sendline('interface {0}'.format(vlan_port) + eol)
        child.expect_exact(self.device_prompts[3])
        # Configure the VLAN membership mode
        child.sendline('switchport mode access' + eol)
        child.expect_exact(self.device_prompts[3])
        # Assign the port to the VLAN
        child.sendline('switchport access {0}'.format(vlan_name) + eol)
        child.expect_exact(self.device_prompts[3])
        # Set to forwarding state immediately, bypassing the listening and learning states
        # Used to prevent L2 switching loops when connecting to the PMA
        child.sendline('spanning-tree portfast' + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('no shutdown' + eol)
        child.expect_exact(self.device_prompts[3])

        # Configure VLAN
        child.sendline('interface {0}'.format(vlan_name) + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline("ip address {0} {1}".format(new_ip_address, new_netmask) + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('no shutdown' + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_router_ip_addr(self, child, reporter, eol, ethernet_port, new_ip_address,
                           new_netmask, commit=True):
        """Set a router's IP address.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str ethernet_port: Ethernet interface port name to configure.
        :param str new_ip_address: New IPv4 address for the device.
        :param str new_netmask: New netmask for the device.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        # Validate inputs
        # ethernet_port, while not validated, should start with F(ast), G(iga), etc.
        validate_ip_address(new_ip_address)
        validate_subnet_mask(new_netmask)

        reporter.step('Setting the router\'s IP address...')

        self.__access_priv_exec_mode(child, eol)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])

        # Configure Ethernet port
        child.sendline('interface {0}'.format(ethernet_port) + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline("ip address {0} {1}".format(new_ip_address, new_netmask) + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('no shutdown' + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def ping_from_device(self, child, reporter, eol, destination_ip_addr, count=4):
        """Check the connection to another device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str destination_ip_addr: IPv4 address of the other device.
        :param int count: Number of pings to send; limited to 32.

        :return: None
        :rtype: None
        """
        # Validate inputs
        validate_ip_address(destination_ip_addr)

        # While the ping count can be greater than 32,
        # restrict count to less than 32 when checking connections
        if count < 1 or count >= 32:
            raise ValueError('Ping count is restricted to less than 32 pings.')

        reporter.step('Pinging {0}...'.format(destination_ip_addr))
        self.__access_priv_exec_mode(child, eol)
        child.sendline('ping {0} repeat {1}'.format(destination_ip_addr, count) + eol)
        index = child.expect(['Success rate is 0 percent', self.device_prompts[1], ])
        if index == 0:
            raise RuntimeError('Cannot ping {0} from this device.'.format(destination_ip_addr))
        reporter.success()

    def download_from_device_tftp(self, child, reporter, eol, ethernet_port, file_to_download,
                                  destination_ip_addr, destination_file_name, commit=True):
        """Download a file form the device using the TFTP protocol.

        Developer Notes:
          - TFTP must be installed: i.e., sudo yum -y install tftp tftp-server.
          - While the destination's TFTP service does not need to be running,
            the firewall ports must allow TFTP traffic.
          - The destination file must already exist, even if empty.

        :param pexpect.spawn child: Connection in a child application object.
        :param mtk.gui.windows.Reporter reporter: A reference to the popup GUI window that reports
          the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str ethernet_port: Restrict TFTP traffic through this Ethernet interface port.
        :param str file_to_download: File to download
            (e.g., startup-config, flash:/foo.txt, etc.)
        :param str destination_ip_addr: IPv4 address of the device.
        :param str destination_file_name: Name for the downloaded file (must already exist,
            even if empty.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None
        """
        # Validate inputs
        validate_ip_address(destination_ip_addr)

        destination_file_name = fix_tftp_filepath(destination_file_name)
        validate_filepath('/var/lib/tftpboot/{0}'.format(destination_file_name))
        prep_for_tftp_download('/var/lib/tftpboot/{0}'.format(destination_file_name))

        reporter.step('Downloading {0} from the device...'.format(file_to_download))
        self.__access_priv_exec_mode(child, eol)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])

        child.sendline('ip tftp source-interface {0}'.format(ethernet_port) + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])

        try:
            enable_tftp()
            child.sendline('copy {0} tftp://{1}/{2}'.format(
                file_to_download, destination_ip_addr, destination_file_name) + eol)
            child.expect_exact('Address or name of remote host')
            child.sendline('{0}'.format(destination_ip_addr) + eol)
            child.expect_exact('Destination filename')
            child.sendline('{0}'.format(destination_file_name) + eol)
            index = 0
            while 0 <= index <= 1:
                index = child.expect_exact(['Error',
                                            'Do you want to overwrite?',
                                            'bytes copied in', ], timeout=120)
                if index == 0:
                    # Get error information between 'Error' and the prompt; some hints:
                    # Timeout = Port not open or firewall may be closed
                    # No such file or directory = Destination file may not exist
                    # Undefined error = Destination file permissions may be
                    child.expect_exact(self.device_prompts[1])
                    raise RuntimeError(
                        'Cannot download file: Error {0}'.format(child.before))
                if index == 1:
                    child.sendline('yes' + eol)
        finally:
            disable_tftp()

        reporter.step('{0} downloaded from the device.'.format(file_to_download))

    def upload_to_device_tftp(
            self, child, reporter, eol, source_ip_address, file_path, file_system):
        """ Upload a file from the PMA to the device using TFTP.

        :param pexpect.spawn child: Connection in a child application object.
        :param mtk.gui.windows.Reporter reporter: A reference to the popup GUI window that reports
          the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str source_ip_address: IPv4 address of thw device with the file.
        :param str file_path: File to transfer to the device.
        :param str file_system: Name of the device's default file system

        :return: None
        :rtype: None

        :raise RuntimeError: If unable to enable or disable TFTP services.
        :raise pexpect.ExceptionPexpect: If the result of a sendline command does not match the
          expected result (raised from the pexpect module).
        """
        reporter.step('Transferring {0} to the device using TFTP:'.format(
            os.path.basename(file_path)))

        try:
            enable_tftp()
            # Attempt TFTP copy three times in case of connection time-outs
            for _ in range(3):
                child.sendline('copy tftp: {0}:'.format(file_system) + eol)
                child.expect_exact('Address or name of remote host')
                child.sendline(source_ip_address + eol)
                child.expect_exact('Source filename [')
                child.sendline(
                    file_path.lstrip('/').replace('var/lib/tftpboot', '').lstrip('/') + eol)
                child.expect_exact('Destination filename [')
                child.sendline(os.path.basename(file_path) + eol)
                # Allow ten minutes for transfer (test transfer was 7205803 bytes in 97.946 secs
                # at 73569 bytes/sec)
                index = child.expect_exact(
                    ['Do you want to over write? [confirm]',
                     'bytes copied in',
                     'Timed out',
                     pexpect.TIMEOUT, ], timeout=600)
                if index == 0:
                    # child.send('\r')
                    child.sendline(eol)
                    index2 = child.expect_exact(
                        ['bytes copied in', 'Timed out', pexpect.TIMEOUT, ], timeout=240)
                    if index2 == 0:
                        break
                elif index == 1:
                    break
            child.sendline(eol)
        finally:
            disable_tftp()
        child.expect_exact(self.device_prompts[1])

        reporter.success()

    @staticmethod
    def close_telnet_connection(child, reporter):
        """Close the Telnet connection.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.

        :return: None
        :rtype: None
        """
        reporter.step('Closing Telnet connection...')
        if child:
            # Bring up the Telnet prompt
            child.sendcontrol(']')
            child.expect_exact('telnet>')
            # Request exit. BTW, depending on the connection, the carriage return may confirm the
            # request, making the next step redundant. This has no adverse effect.
            child.sendline('q\r')
            child.expect_exact(['Connection closed.', pexpect.EOF, ])
            # While pexpect.EOF closes the child implicitly,
            # close it explicitly as well, just in case
            child.close()
        reporter.success()

    @staticmethod
    def close_serial_connection(child, reporter):
        """Close the serial connection.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.

        :return: None
        :rtype: None
        """
        reporter.step('Closing serial connection...')
        if child:
            # Close minicom correctly so the modem will reset and not lock!
            # Bring up the Minicom command menu
            child.sendcontrol('a')
            # Request exit. BTW, depending on the connection, the carriage return may confirm the
            # request, making the next step redundant. This has no adverse effect.
            child.sendline('x\r')
            # Confirm request
            child.sendline('\r')
            # While pexpect.EOF closes the child implicitly,
            # close it explicitly as well, just in case
            child.close()
        reporter.success()


if __name__ == '__main__':
    raise RuntimeError(
        'Script {0} cannot be run independently of the MTK application.'.format(sys.argv[0]))