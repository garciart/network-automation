# -*- coding: utf-8 -*-
"""Test of the CiscoIOS class (cisco_ios.py) using the Cisco IOSvL2 switch image in GNS3.
"""
import os.path
import sys

from exercises.cisco_ios import CiscoIOS
from labs import (validate_ip_address,
                  validate_port_number,
                  validate_subnet_mask,
                  validate_password,
                  run_cli_command, )

__all__ = ['CiscoIOSL2', ]


class CiscoIOSL2(object):
    _cisco_prompts = [
        '>', '#', '(config)#', '(config-if)#', '(config-line)#', '(config-switch)#', ]

    def __init__(self,
                 device_hostname,
                 eol,
                 device_ip_addr,
                 ethernet_port,
                 remote_ip_addr,
                 subnet_mask,
                 device_username=None,
                 device_password=None,
                 file_to_transfer=None,
                 **options):
        """Instantiates the device when the user opens the procedure GUI.

        :param str device_hostname: Hostname of the device.
        :param str eol: EOL sequence (LF or CRLF) used by the connection (See comments below).
        :param str device_ip_addr: IPv4 address of the device.
        :param str ethernet_port: Ethernet interface port name used to connect to the device.
        :param str remote_ip_addr: IPv4 address of the remote host.
        :param str subnet_mask: Netmask to apply for communication between the host and the device.
        :param str device_username: Username for Virtual Teletype (VTY) connections when
            'login local' is set in the device's startup-config file.
        :param str device_password: Console, Auxiliary, or VTY password, depending on the
            connection and if a password is set in the device's startup-config file.
        :param str file_to_transfer: Path and name for the file to upload or download
            (must already exist in /var/lib/tftpboot for TFTP transfers, even if empty).

        :return: None
        :rtype: None
        """
        self._device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self._device_prompts = ['{0}{1}'.format(device_hostname, p) for p in self._cisco_prompts]

        # End-of-line (EOL) issues: pexpect.sendline() sends a line feed ('\n') after the text.
        # However, depending on:
        # - The physical port used to connect to the device (e.g., VTY, Console, etc.)
        # - The protocol (e.g., Telnet, SSH, etc.)
        # - The network port (e.g., 23, 2000, 4000, etc.)
        # - The terminal emulator (e.g., PuTTY, Minicom, etc.)
        # - The emulation (e.g., VT100, VT102, ANSI, etc.)
        # The device may require a carriage return ('\r') before the line feed to create a CRLF
        # (i.e., pexpect.sendline('text\r')).
        # Therefore, the user must designate an EOL, based on the connection,
        # which will be appended to each sendline.
        self._eol = eol

        validate_ip_address(device_ip_addr)
        self._device_ip_addr = device_ip_addr

        self._ethernet_port = ethernet_port

        validate_ip_address(remote_ip_addr)
        self._remote_ip_addr = remote_ip_addr

        validate_subnet_mask(subnet_mask)
        self._subnet_mask = subnet_mask

        self._username = device_username
        self._password = device_password

        if file_to_transfer:
            # TODO: Validate that exists here (or at all?)
            self._file_to_transfer = file_to_transfer

        if options['remote_username']:
            self._remote_username = options['remote_username']

        if options['remote_password']:
            self._remote_password = options['remote_password']

        if options['vlan_name']:
            self._vlan_name = options['vlan_name']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        validate_password(password)
        self._password = password

    @property
    def file_to_transfer(self):
        return self._file_to_transfer

    @file_to_transfer.setter
    def file_to_transfer(self, file_to_transfer):
        # TODO: Validate that exists here (or at all?)
        self._file_to_transfer = file_to_transfer

    def run(self, reporter, connection_type='serial', **options):
        switch = CiscoIOS(self._device_hostname)
        child = None
        try:
            # Connect to the device
            if connection_type == 'serial':
                child = switch.connect_via_serial(reporter,
                                                  eol=self._eol,
                                                  serial_device='ttyUSB0',
                                                  baud_rate=9600,
                                                  data_bits=8,
                                                  username=self._username,
                                                  password=self._password,
                                                  verbose=False)
            elif connection_type == 'telnet':
                validate_ip_address(options['telnet_ip_addr'])
                # For standard and reverse Telnet connections
                validate_port_number(options['telnet_port_num'])
                child = switch.connect_via_telnet(reporter, eol=self._eol,
                                                  telnet_ip_addr=options['telnet_ip_addr'],
                                                  telnet_port_num=options['telnet_port_num'],
                                                  username=self._username,
                                                  password=self._password,
                                                  verbose=True)

            # Get the device's information
            default_file_system, software_ver, device_name, serial_num = switch.get_device_info(
                child, reporter, eol=self._eol)
            reporter.note('Default drive: {0}'.format(default_file_system))
            reporter.note('Software version: {0}'.format(software_ver))
            reporter.note('Device name: {0}'.format(device_name))
            reporter.note('Serial number: {0}'.format(serial_num))

            # Format the drive (Dynamips only)
            # switch.format_file_system(child, reporter, eol=self._eol,
            #                          device_file_system=default_file_system)

            # Enable Layer 3 communications
            switch.set_switch_ip_addr(child, reporter, eol=self._eol,
                                      vlan_name=self._vlan_name,
                                      vlan_port=self._ethernet_port,
                                      new_ip_address=self._device_ip_addr,
                                      new_netmask=self._subnet_mask,
                                      commit=True)
            switch.ping_from_device(child, reporter, eol=self._eol,
                                    destination_ip_addr=self._remote_ip_addr,
                                    count=4)
            reporter.note(run_cli_command('ping -c 4 {0}'.format(self._remote_ip_addr)))

            switch.enable_ssh(child, reporter, eol=self._eol,
                              label='ADVENTURES',
                              modulus=1024,
                              version=2,
                              commit=True)

            # switch.secure_device(child, reporter, eol=self._eol,
            #                      vty_username='admin',
            #                      vty_password='cisco',
            #                      privilege=15,
            #                      console_password='ciscon',
            #                      aux_password='cisaux',
            #                      enable_password='cisen',
            #                      commit=True)

            # Transfer a file from and to the device using SCP
            switch.set_scp_source_interface(child, reporter, eol=self._eol,
                                            scp_interface_port=self._ethernet_port,
                                            commit=True)

            # For startup-config or running-config, use 'nvram' instead of default_file_system
            switch.download_from_device_scp(child, reporter, eol=self._eol,
                                            device_file_system='nvram',
                                            remote_ip_addr=self._remote_ip_addr,
                                            remote_username=self._remote_username,
                                            file_to_download='startup-config',
                                            destination_filepath=self._file_to_transfer + '.scp',
                                            remote_password=self._remote_password)
            switch.upload_to_device_scp(child, reporter, eol=self._eol,
                                        device_file_system=default_file_system,
                                        remote_ip_addr=self._remote_ip_addr,
                                        remote_username=self._remote_username,
                                        file_to_upload=self._file_to_transfer + '.scp',
                                        destination_filepath=os.path.basename(
                                            self._file_to_transfer + '.scp'),
                                        remote_password=self._remote_password)

            # Transfer a file from and to the device using FTP
            switch.download_file_ftp(child, reporter, eol=self._eol,
                                     device_file_system='nvram',
                                     remote_ip_addr=self._remote_ip_addr,
                                     remote_username=self._remote_username,
                                     file_to_download='startup-config',
                                     destination_filepath=self._file_to_transfer + '.ftp',
                                     remote_password=self._remote_password)

            switch.upload_file_ftp(child, reporter, eol=self._eol,
                                   device_file_system=default_file_system,
                                   remote_ip_addr=self._remote_ip_addr,
                                   remote_username=self._remote_username,
                                   file_to_upload=self._file_to_transfer + '.ftp',
                                   destination_filepath=os.path.basename(
                                       self._file_to_transfer + '.ftp'),
                                   remote_password=self._remote_password)

            # Transfer a file from and to the device using TFTP
            switch.set_tftp_source_interface(child, reporter, eol=self._eol,
                                             tftp_interface_port=self._ethernet_port,
                                             commit=True)
            # For startup-config or running-config, use 'nvram' instead of default_file_system
            switch.download_from_device_tftp(child, reporter, eol=self._eol,
                                             device_file_system='nvram',
                                             remote_ip_addr=self._remote_ip_addr,
                                             file_to_download='startup-config',
                                             destination_filepath=self._file_to_transfer + '.tftp')
            switch.upload_to_device_tftp(child, reporter, eol=self._eol,
                                         device_file_system=default_file_system,
                                         remote_ip_addr=self._remote_ip_addr,
                                         file_to_upload=self._file_to_transfer + '.tftp',
                                         destination_filepath=os.path.basename(
                                             self._file_to_transfer + '.tftp'))

        except BaseException:
            ex_type, ex_value, traceback = sys.exc_info()
            reporter.error()
            raise ex_type, ex_value, traceback
        finally:
            # Close all connections
            if connection_type == 'serial':
                switch.close_serial_connection(child, reporter)
            else:
                switch.close_telnet_connection(child, reporter)
