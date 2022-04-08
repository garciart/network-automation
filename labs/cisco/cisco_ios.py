# -*- coding: utf-8 -*-
"""Common Cisco IOS and IOS-XE tasks.

Developer notes:

- All CLI commands are the same between Cisco IOS and IOS XE.
- While most method parameters are written out as keyword arguments, you can enter arguments
 positionally, without the keyword, as long as they are in the correct order.

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
                                validate_file_path,
                                validate_switch_priority,
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
        """Class instantiation.

        :param str device_hostname: Hostname of the device.

        :return: None
        :rtype: None
        """
        self.device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self.device_prompts = ['{0}{1}'.format(device_hostname, p) for p in self.cisco_prompts]

    def connect_via_telnet(self, reporter, eol,
                           telnet_ip_addr,
                           telnet_port_num=22,
                           username=None,
                           password=None,
                           enable_password=None,
                           verbose=False):
        """Connect to a network device using Telnet.

        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection (See comments below).
        :param str telnet_ip_addr: Device's IP address for Telnet.
        :param int telnet_port_num: Port number for the connection, both standard (22) and others.
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file.

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

    def connect_via_serial(self, reporter, eol,
                           serial_device='/dev/ttyUSB0',
                           baud_rate=9600,
                           data_bits=8,
                           username=None,
                           password=None,
                           enable_password=None,
                           verbose=False):
        """Connect to the device using Minicom.

        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection (See EOL comments below).
        :param str serial_device: Remote host serial device interface name.
        :param int baud_rate: Baud rate for connection.
        :param int data_bits: Data bit size for connection.
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool verbose: True (default) to echo both input and output to the screen,
            or false to save output to a time-stamped file.

        :return: Connection in a child application object.
        :rtype: pexpect.spawn

        :raise ValueError: If an argument is invalid.
        :raise RuntimeError: If Minicom is not installed.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Connecting to device via {0}...'.format(serial_device))

        # Validate inputs and ensure that Minicom is installed
        if serial_device not in ('/dev/ttyACM0', '/dev/ttyUSB0',):
            reporter.error()
            raise ValueError('Invalid serial device name.')
        if baud_rate not in (50, 75, 110, 150, 300, 600, 1200, 1800, 2000, 2400, 3600, 4800, 7200,
                             9600, 14400, 19200, 28800, 38400, 56000, 57600, 115200, 128000,):
            reporter.error()
            raise ValueError('Invalid baud rate.')
        if data_bits not in (7, 8,):
            reporter.error()
            raise ValueError('Invalid data bit size.')

        _, exitstatus = pexpect.run('which minicom', withexitstatus=True)
        if exitstatus != 0:
            reporter.error()
            raise RuntimeError('Minicom is not installed.')

        # Connect using Minicom command line
        # Format: minicom --device /dev/ttyUSB0 --baudrate 9600 --8bit --wrap
        mode = '--8bit' if data_bits == 8 else '--7bit'
        cmd = 'minicom --device {0} --baudrate {1} {2} --wrap'.format(
            serial_device, baud_rate, mode)
        child = pexpect.spawn(cmd)
        # Slow down commands to prevent race conditions with output
        child.delaybeforesend = 0.5
        if verbose:
            # Echo both input and output to the screen
            child.logfile_read = sys.stdout

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
    def __clear_startup_prompts(self, child, reporter, eol,  # NOSONAR
                                username=None,
                                password=None):
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

        :raise ValueError: If an argument is invalid.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        # Check for a hostname prompt (e.g., switch#) first.
        # If you find a hostname prompt, you have cleared the startup messages.
        # However, if the first thing you find is a hostname prompt, you are accessing
        # an open line. Warn the user, but return control back to the calling method

        # noinspection PyTypeChecker
        index = child.expect_exact(['Cisco', 'Loading', 'Waiting', 'Initializing',
                                    pexpect.TIMEOUT, ] + self.device_prompts, timeout=60)
        # If index < 4 (i.e., a startup keyword appears is found within 60 seconds),
        # the device is still displaying startup messages. Continue to the while loop...
        if index == 4:
            # If no text is found, the device may be waiting for input.
            # Force a prompt by sending a full carriage-return and line-feed.
            child.sendline('\r')
        elif index > 4:
            reporter.warn(
                '\x1b[33mYou may be accessing an open or uncleared virtual teletype session.\n' +
                'Output from previous commands may cause pexpect searches to fail.\n' +
                'To prevent this in the future, reload the device to clear any artifacts.\x1b[0m')
            self.__reset_pexpect_cursor(child, eol)
            return

        # Allow an additional 5 minutes to clear startup messages
        timeout = 300
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
                        '\x1b[33m' +
                        'Warning - This device has already been configured and secured.\n' +
                        'Changes made by this script may be incompatible with the current ' +
                        'configuration.' +
                        '\x1b[0m')
                elif index == 4:
                    child.sendline('no' + eol)
                elif index == 5:
                    child.sendline('yes' + eol)
                elif index == 6:
                    # Force a prompt by sending a full carriage-return and line-feed
                    child.sendline('\r')
                # Wait five seconds to allow any system messages to clear
                # time.sleep(5)
            except pexpect.TIMEOUT as pex:
                reporter.error()
                raise pex

    def __access_priv_exec_mode(self, child, eol, enable_password=None):
        """This method places the pexpect cursor at a Privileged EXEC Mode prompt (e.g., switch#)
        for subsequent commands.

        :param pexpect.spawn child: Connection in a child application object.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
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

    def __reset_pexpect_cursor(self, child, eol):
        """This method sends a 'tracer round' in the form of a timestamp comment to move the
        pexpect cursor forward to the last hostname prompt.

        :param pexpect.spawn child: Connection in a child application object.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        # Wait five seconds to allow any system messages to clear
        time.sleep(5)

        tracer_round = ';{0}'.format(int(time.time()))
        # Add the EOL here, not in the tracer_round, or you won't find the tracer_round later
        child.sendline(tracer_round + eol)
        child.expect_exact('{0}'.format(tracer_round))
        # WATCH YOUR CURSORS! You must also consume the prompt after tracer_round
        # or the pexepect cursor will stop at the wrong prompt
        #                   The cursor may stop here -> R2#;1648073691
        # But it needs to stop at the following line -> R2#
        child.expect_exact(self.device_prompts)

    def get_device_info(self, child, reporter, eol, enable_password=None):
        """Get information about the network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: Name of the default file system; the device's IOS version; the device's  name;
            and the device's serial number.
        :rtype: tuple

        :raise RuntimeError: If unable to get info (caught and value set to None)
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
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
            child.sendline('show inventory | include DESCR:' + eol)
            child.expect_exact(self.device_prompts[1])
            device_name = str(child.before).split(
                'show inventory | include DESCR:\r')[1].split('\r')[0].strip()
            if not re.compile(r'DESCR:').search(device_name):
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

        # Get rid of ANSI escape sequences
        ansi_seq = re.compile('(?:\\x1b\[)([\w;]+)(H)')
        default_file_system = ansi_seq.sub('', str(default_file_system)).strip()
        software_ver = ansi_seq.sub('', str(software_ver)).strip()
        device_name = ansi_seq.sub('', str(device_name)).strip()
        serial_num = ansi_seq.sub('', str(serial_num)).strip()

        reporter.success()
        return default_file_system, software_ver, device_name, serial_num

    def format_file_system(self, child, reporter, eol, device_file_system):
        """Format a file system (i.e., memory) on a network device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system to format.

        :return: None
        :rtype: None
        """
        # Validate inputs
        if not device_file_system.startswith(('bootflash', 'flash', 'slot', 'disk',)):
            reporter.error()
            raise ValueError('Invalid Cisco file system name.')

        reporter.step('Formatting device memory...')
        self.__access_priv_exec_mode(child, eol)
        # Format the memory. Look for the final characters of the following strings:
        # 'Format operation may take a while. Continue? [confirm]'
        # 'Format operation will destroy all data in 'flash:'.  Continue? [confirm]'
        # '66875392 bytes available (0 bytes used)'
        child.sendline('format {0}:'.format(device_file_system) + eol)
        index = 1
        while index != 0:
            index = child.expect_exact(
                [pexpect.TIMEOUT, 'Continue? [confirm]', 'Enter volume ID', ], timeout=5)
            if index != 0:
                child.sendline(eol)
        child.expect_exact('Format of {0} complete'.format(device_file_system), timeout=120)
        child.sendline('show {0}'.format(device_file_system) + eol)
        child.expect_exact('(0 bytes used)')
        child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_switch_ip_addr(self, child, reporter, eol,
                           vlan_name,
                           vlan_port,
                           new_ip_address,
                           new_netmask,
                           enable_password=None,
                           commit=True):
        """Set a switch's IP address.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str vlan_name: Virtual Local Area Network (VLAN) interface to configure.
        :param str vlan_port: Ethernet interface port name to configure and connect to VLAN.
        :param str new_ip_address: New IPv4 address for the device.
        :param str new_netmask: New netmask for the device.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Setting the switch\'s IP address...')
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        # FYI, vlan_port, while not validated, should start with F(ast), G(iga), etc.
        validate_ip_address(new_ip_address)
        validate_subnet_mask(new_netmask)

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
        # Used to prevent L2 switching loops when connecting to the remote host
        child.sendline('spanning-tree portfast' + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('no shutdown' + eol)
        child.expect_exact(self.device_prompts[3])

        # Configure VLAN
        child.sendline('interface {0}'.format(vlan_name) + eol)
        child.expect_exact(self.device_prompts[3])
        child.sendline('ip address {0} {1}'.format(new_ip_address, new_netmask) + eol)
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

    def set_router_ip_addr(self, child, reporter, eol,
                           ethernet_port,
                           new_ip_address,
                           new_netmask,
                           commit=True):
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
        child.sendline('ip address {0} {1}'.format(new_ip_address, new_netmask) + eol)
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

    def ping_from_device(self, child, reporter, eol,
                         destination_ip_addr,
                         count=4,
                         enable_password=None):
        """Check the connection to another device.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str destination_ip_addr: IPv4 address of the other device.
        :param int count: Number of pings to send; limited to 32.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise ValueError: If an argument is invalid.
        :raise RuntimeError: If unable to ping the remote device.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Pinging {0}...'.format(destination_ip_addr))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        validate_ip_address(destination_ip_addr)

        # While the ping count can be greater than 32,
        # restrict count to less than 32 when checking connections
        if count < 1 or count >= 32:
            raise ValueError('Ping count is restricted to less than 32 pings.')

        child.sendline('ping {0} repeat {1}'.format(destination_ip_addr, count) + eol)
        index = child.expect(['Success rate is 0 percent', self.device_prompts[1], ])
        if index == 0:
            raise RuntimeError('Cannot ping {0} from this device.'.format(destination_ip_addr))
        reporter.success()

    def set_switch_priority(self, child, reporter, eol,
                            switch_number=1,
                            switch_priority=1,
                            enable_password=None,
                            commit=True):
        reporter.step('Setting switch priority...')
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)
        # Validate inputs
        if not 1 <= switch_number <= 9:
            raise ValueError('Invalid switch stack member number.')
        validate_switch_priority(switch_priority)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('switch {0} priority {1}'.format(switch_number, switch_priority))
        index = 0
        while index == 0:
            index = child.expect_exact(
                ['Do you want to continue', 'New Priority has been set successfully', ])
            if index == 0:
                child.sendline(eol)
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def enable_ssh(self, child, reporter, eol,
                   label=None,
                   modulus=1024,
                   version=1.99,
                   time_out=120,
                   retries=3,
                   enable_password=None,
                   commit=True):
        """Enable SSH communications.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str label: Name for the Rivest, Shamir, and Adelman (RSA) key pair.
        :param int modulus: Modulus size for the certification authority (CA) key.
        :param int version: Force SSH version 1 or 2 (Leave blank for the default of 1.99)
        :param int time_out: Wait time for a response from the client before closing the connection.
        :param int retries: Number of SSH authentication retries allowed.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None

        :raise ValueError: If an argument is invalid.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Enabling SSH on the device...')
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        if not 350 <= modulus <= 4096:
            raise ValueError('Invalid modulus size.')
        if version not in (1, 1.99, 2,):
            raise ValueError('Invalid SSH version.')
        # BTW, 0 disables the client and the max is 2147483647; a little over 68 years!
        if not 1 <= time_out <= 2147483647:
            raise ValueError('Invalid time-out wait time.')
        if not 1 <= retries <= 5:
            raise ValueError('Invalid authentication retries allowed.')

        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('crypto key zeroize rsa' + eol)
        index = child.expect_exact(['Do you really want to remove these keys? [yes/no]:',
                                    self.device_prompts[2], ])
        if index == 0:
            child.sendline('yes' + eol)
            child.expect_exact(self.device_prompts[2])
        child.sendline('crypto key generate rsa general-keys label {0} modulus {1}'.format(
            label, modulus) + eol)
        child.expect_exact(self.device_prompts[2])
        if version == 1 or version == 2:
            child.sendline('ip ssh version {0}'.format(version) + eol)
            child.expect_exact(self.device_prompts[2])
        else:
            child.sendline('no ip ssh version' + eol)
            child.expect_exact(self.device_prompts[2])
        if time_out >= 0:
            child.sendline('ip ssh time-out {0}'.format(time_out) + eol)
            child.expect_exact(self.device_prompts[2])
        if retries >= 0:
            child.sendline('ip ssh authentication-retries {0}'.format(retries) + eol)
            child.expect_exact(self.device_prompts[2])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])

        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_scp_source_interface(self, child, reporter, eol,
                                 scp_interface_port,
                                 enable_password=None,
                                 commit=True):
        """Set the source IP address for SCP traffic. By default, the device will choose the port
        with an IP address closest to the remote IP address. This method overrides the default
        setting.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str scp_interface_port: Restrict SCP traffic through this Ethernet interface port.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Restricting SCP traffic to {0}'.format(scp_interface_port))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('ip scp source-interface {0}'.format(scp_interface_port) + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def download_from_device_scp(self, child, reporter, eol,
                                 device_file_system,
                                 remote_ip_addr,
                                 remote_username,
                                 file_to_download,
                                 destination_filepath,
                                 remote_password,
                                 enable_password=None):
        """Download a file form the device using the SCP protocol.

        Developer Notes:
            - SCP must be installed: i.e., sudo yum install -y openssh-clients openssh.
            - While the destination's SCP service does not need to be running,
              the firewall ports must allow SCP traffic.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system where the file is located on the device.
        :param str remote_ip_addr: IPv4 address of the remote host.
        :param str remote_username: Remote username to authenticate SCP transfers.
        :param str file_to_download: File to download
            (e.g., startup-config, flash:/foo.txt, etc.)
        :param str destination_filepath: Name for the downloaded file.
        :param str remote_password: Remote password to authenticate SCP transfers.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Downloading {0} from the device using SCP...'.format(file_to_download))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        validate_ip_address(remote_ip_addr)

        # copy flash:/test1.scp scp://gns3user:gns3user@192.168.1.10/test1.cfg
        child.sendline('copy {0}: scp:'.format(device_file_system) + eol)
        index = 0
        while index != 7:
            # Allow 10 minutes for the transfer
            # Reference: 14606129 bytes copied in 166.925 secs (87501 bytes/sec)
            index = child.expect_exact(['Source filename',
                                        'Address or name of remote host',
                                        'Destination username',
                                        'Destination filename',
                                        'Password:',
                                        'Do you want to over write? [confirm]',
                                        'Error',
                                        'bytes copied in', ], timeout=600)
            if index == 0:
                child.sendline(file_to_download + eol)
            elif index == 1:
                child.sendline(remote_ip_addr + eol)
            elif index == 2:
                child.sendline(remote_username + eol)
            elif index == 3:
                child.sendline(destination_filepath.lstrip('/') + eol)
            elif index == 4:
                child.sendline(remote_password + eol)
            elif index == 5:
                child.sendline(eol)
            elif index == 6:
                raise RuntimeError('Unable to download file to container.')
        child.expect_exact(self.device_prompts[1])
        reporter.success()

    def upload_to_device_scp(self, child, reporter, eol,
                             device_file_system,
                             remote_ip_addr,
                             remote_username,
                             file_to_upload,
                             destination_filepath,
                             remote_password,
                             enable_password=None):
        """ Upload a file from the remote host to the device using SCP.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system where the file is located on the device.
        :param str remote_ip_addr: IPv4 address of the remote host.
        :param str remote_username: Remote username to authenticate SCP transfers.
        :param str file_to_upload: File to upload
            (e.g., startup-config, flash:/foo.txt, etc.)
        :param str destination_filepath: Name for the downloaded file.
        :param str remote_password: Remote password to authenticate SCP transfers.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Uploading {0} to the device using SCP...'.format(
            os.path.basename(file_to_upload)))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        validate_ip_address(remote_ip_addr)
        # Do not validate file path if the file is in the SSHv1 Docker container
        if remote_username != 'sshtransfer':
            validate_file_path(file_to_upload)

        # copy scp://gns3user:gns3user@192.168.1.10/test1.cfg flash:/test1.scp
        child.sendline('copy scp: {0}:'.format(device_file_system) + eol)
        index = 0
        while index != 7:
            # Allow 10 minutes for the transfer
            # Reference: 14606129 bytes copied in 166.925 secs (87501 bytes/sec)
            index = child.expect_exact(['Address or name of remote host',
                                        'Source username',
                                        'Source filename',
                                        'Destination filename',
                                        'Password:',
                                        'Do you want to over write? [confirm]',
                                        'Error',
                                        'bytes copied in', ], timeout=600)
            if index == 0:
                child.sendline(remote_ip_addr + eol)
            elif index == 1:
                child.sendline(remote_username + eol)
            elif index == 2:
                child.sendline(file_to_upload + eol)
            elif index == 3:
                child.sendline(destination_filepath.lstrip('/') + eol)
            elif index == 4:
                child.sendline(remote_password + eol)
            elif index == 5:
                child.sendline(eol)
            elif index == 6:
                raise RuntimeError('Unable to upload file from container.')
        child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_tftp_source_interface(self, child, reporter, eol,
                                  tftp_interface_port,
                                  enable_password=None,
                                  commit=True):
        """Set the source IP address for TFTP traffic. By default, the device will choose the port
        with an IP address closest to the remote IP address. This method overrides the default
        setting.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str tftp_interface_port: Restrict TFTP traffic through this Ethernet interface port.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Restricting TFTP traffic to {0}'.format(tftp_interface_port))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)
        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('ip tftp source-interface {0}'.format(tftp_interface_port) + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])
        reporter.success()

    def download_from_device_tftp(self, child, reporter, eol,
                                  device_file_system,
                                  remote_ip_addr,
                                  file_to_download,
                                  destination_filepath,
                                  enable_password=None):
        """Download a file form the device using the TFTP protocol.

        Developer Notes:
            - TFTP must be installed: i.e., sudo yum -y install tftp tftp-server.
            - While the destination's TFTP service does not need to be running,
              the firewall ports must allow TFTP traffic.
            - The destination file must already exist, even if empty.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system where the file is located on the device.
        :param str remote_ip_addr: IPv4 address of the remote host.
        :param str file_to_download: File to download (e.g., startup-config, flash:/foo.txt, etc.)
        :param str destination_filepath: Path and name for the downloaded file (must already exist,
            even if empty).
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise RuntimeError: If unable to download the file.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Downloading {0} from the device using TFTP...'.format(file_to_download))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        validate_ip_address(remote_ip_addr)

        destination_filepath = fix_tftp_filepath(destination_filepath)
        try:
            validate_file_path('/var/lib/tftpboot/{0}'.format(destination_filepath))
        except ValueError:
            prep_for_tftp_download('/var/lib/tftpboot/{0}'.format(destination_filepath))

        try:
            enable_tftp()
            child.sendline('copy {0}:/{1} tftp://{2}/{3}'.format(device_file_system,
                                                                 file_to_download, remote_ip_addr,
                                                                 destination_filepath) + eol)
            child.expect_exact('Address or name of remote host')
            child.sendline('{0}'.format(remote_ip_addr) + eol)
            child.expect_exact('Destination filename')
            child.sendline('{0}'.format(destination_filepath) + eol)
            index = 0
            while 0 <= index <= 1:
                index = child.expect_exact(['Timed out',
                                            'Error',
                                            'Do you want to overwrite?',
                                            'bytes copied in', ], timeout=600)
                if index in (0, 1, ):
                    # Get error information between 'Error' and the prompt; some hints:
                    # Timeout = Port not open or firewall may be closed
                    # No such file or directory = Destination file may not exist
                    # Undefined error = Destination file permissions may be
                    child.expect_exact(self.device_prompts[1])
                    raise RuntimeError(
                        'Cannot download file: Error {0}'.format(child.before))
                if index == 2:
                    child.sendline('yes' + eol)
        finally:
            disable_tftp()
        reporter.success()

    def upload_to_device_tftp(self, child, reporter, eol,
                              device_file_system,
                              remote_ip_addr,
                              file_to_upload,
                              destination_filepath,
                              enable_password=None):
        """ Upload a file from the remote host to the device using TFTP.

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system where the file is located on the device.
        :param str remote_ip_addr: IPv4 address of the remote host.
        :param str file_to_upload: File to upload (e.g., /var/lib/tftpboot/file.name, etc.)
        :param str destination_filepath: Path and name for the downloaded file (must already exist,
            even if empty).
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise RuntimeError: If unable to transfer file using TFTP.
        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Uploading {0} to the device using TFTP:'.format(
            os.path.basename(file_to_upload)))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        # Validate inputs
        validate_ip_address(remote_ip_addr)

        file_to_upload = fix_tftp_filepath(file_to_upload)
        try:
            validate_file_path('/var/lib/tftpboot/{0}'.format(file_to_upload))
        except ValueError:
            prep_for_tftp_download('/var/lib/tftpboot/{0}'.format(file_to_upload))

        try:
            enable_tftp()
            # Attempt TFTP copy three times in case of connection time-outs
            for _ in range(3 + 1):
                child.sendline('copy tftp: {0}:'.format(device_file_system) + eol)
                child.expect_exact('Address or name of remote host')
                child.sendline(remote_ip_addr + eol)
                child.expect_exact('Source filename [')
                child.sendline(
                    file_to_upload.lstrip('/').replace(
                        'var/lib/tftpboot', '').lstrip('/') + eol)
                child.expect_exact('Destination filename [')
                child.sendline(destination_filepath.lstrip('/') + eol)
                # Allow ten minutes for transfer (test transfer was 7205803 bytes in 97.946 secs
                # at 73569 bytes/sec)
                index = child.expect_exact(
                    ['Do you want to over write? [confirm]',
                     'bytes copied in',
                     'Timed out',
                     'Error',
                     pexpect.TIMEOUT, ], timeout=600)
                if index == 0:
                    child.sendline(eol)
                    index2 = child.expect_exact(
                        ['bytes copied in', 'Timed out', pexpect.TIMEOUT, ], timeout=600)
                    if index2 == 0:
                        break
                elif index == 1:
                    break
            child.sendline(eol)
        finally:
            disable_tftp()
        child.expect_exact(self.device_prompts[1])
        reporter.success()

    def set_config_for_boot(self, child, reporter, eol,
                            device_file_system,
                            boot_config_file,
                            enable_password=None,
                            commit=True):
        """Specify the the configuration file from which the system configures itself during
        initialization (startup)

        :param pexpect.spawn child: Connection in a child application object.
        :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str device_file_system: File system where the new boot config file is located.
        :param str boot_config_file: Boot config file to use during startup.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.
        :param bool commit: True to save changes to startup-config.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step(
            'Setting {0} as the initialization (startup) configuration...'.format(boot_config_file))
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        child.sendline('configure terminal' + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('boot config {0}:/{1}'.format(device_file_system, boot_config_file) + eol)
        child.expect_exact(self.device_prompts[2])
        child.sendline('end' + eol)
        child.expect_exact(self.device_prompts[1])
        # Save changes if True
        if commit:
            child.sendline('write memory' + eol)
            child.expect_exact('[OK]')
            child.expect_exact(self.device_prompts[1])

    def reload_device(self, child, reporter, eol,
                      username=None,
                      password=None,
                      enable_password=None):
        """Reloads and reboots the device.

        :param pexpect.spawn child: The connection in a child application object.
        :param mtk.gui.windows.Reporter reporter: A reference to the popup GUI window that reports
            the status and progress of the script.
        :param str eol: EOL sequence (LF or CLRF) used by the connection.
        :param str username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str password: Console, Auxiliary, or VTY password, depending on the connection
            and if a password is set in the device's startup-config file.
        :param str enable_password: Password to enable Privileged EXEC Mode from User EXEC Mode.

        :return: None
        :rtype: None

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
        """
        reporter.step('Rebooting (~ 5 min):')
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)

        child.expect_exact(self.device_prompts[1])
        child.sendline('reload' + eol)
        child.expect_exact('Proceed with reload? [confirm]')
        # child.send('\r')
        child.sendline(eol)
        # Finished rebooting
        # Get to Privileged EXEC Mode
        self.__clear_startup_prompts(child, reporter, eol, username=username, password=password)
        self.__access_priv_exec_mode(child, eol, enable_password=enable_password)
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

        :raise pexpect.ExceptionPexpect: If the result of a send command does not match the
            expected result (raised from the pexpect module).
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
        'Script {0} cannot be run independently of the application.'.format(sys.argv[0]))
