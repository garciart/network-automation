# -*- coding: utf-8 -*-
"""Test of the CiscoIOS class (cisco_ios.py) using the Cisco 3745 router image in GNS3.
"""
import sys

from cisco_ios import CiscoIOS
from labs.cisco.utility import (validate_ip_address, validate_port_number, validate_subnet_mask,
                                validate_filepath, validate_password,
                                run_cli_command, )

__all__ = ['Cisco3745', ]


class Cisco3745(object):
    _cisco_prompts = [
        '>', '#', '(config)#', '(config-if)#', '(config-line)#', '(config-router)#', ]

    def __init__(self,
                 device_hostname=None,
                 eol=None,
                 device_ip_addr=None,
                 pma_ip_addr=None,
                 username=None,
                 password=None,
                 ethernet_port=None,
                 subnet_mask=None,
                 config_file_path=None,
                 **options):
        """Instantiates the device when the user opens the procedure GUI.
        """
        self._device_hostname = device_hostname
        # Prepend the hostname to the standard Cisco prompt endings
        self._device_prompts = ['{0}{1}'.format(device_hostname, p) for p in self._cisco_prompts]

        self._eol = eol

        validate_ip_address(device_ip_addr)
        self._device_ip_addr = device_ip_addr

        validate_ip_address(pma_ip_addr)
        self._pma_ip_addr = pma_ip_addr

        self._username = username
        self._password = password

        self._ethernet_port = ethernet_port

        validate_subnet_mask(subnet_mask)
        self._subnet_mask = subnet_mask

        if config_file_path:
            validate_filepath(config_file_path)
            self._config_file_path = config_file_path

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        validate_password(password)
        self._password = password

    def run(self, reporter, connection_type=None, **options):
        c3745 = CiscoIOS(self._device_hostname)
        child = None
        try:
            if connection_type == 'serial':
                child = c3745.connect_via_serial(reporter,
                                                 serial_device='ttyUSB0',
                                                 baud_rate=9600,
                                                 data_bits=8,
                                                 eol=self._eol)
            elif connection_type == 'telnet':
                validate_ip_address(options['telnet_ip_addr'])
                # For standard and reverse Telnet connections
                validate_port_number(options['telnet_port_num'])
                child = c3745.connect_via_telnet(reporter,
                                                 options['telnet_ip_addr'],
                                                 telnet_port_num=options['telnet_port_num'],
                                                 eol=self._eol)
            else:
                raise RuntimeError('Connection type must be \'serial\' or \'telnet\'.')
            default_file_system, software_ver, device_name, serial_num = c3745.get_device_info(
                child, reporter, self._eol)
            reporter.note('Default drive: {0}'.format(default_file_system))
            reporter.note('Software version: {0}'.format(software_ver))
            reporter.note('Device name: {0}'.format(device_name))
            reporter.note('Serial number: {0}'.format(serial_num))
            c3745.format_file_system(child, reporter, self._eol, default_file_system)
            c3745.set_router_ip_addr(child, reporter,
                                     eol=self._eol,
                                     ethernet_port=self._ethernet_port,
                                     new_ip_address=self._device_ip_addr,
                                     new_netmask=self._subnet_mask,
                                     commit=False)
            c3745.ping_from_device(child, reporter, self._eol, self._pma_ip_addr, count=4)
            reporter.note(run_cli_command('ping -c 4 {0}'.format(self._pma_ip_addr)))
            c3745.download_from_device_tftp(child,
                                            reporter,
                                            self._eol,
                                            self._ethernet_port,
                                            'startup-config',
                                            self._pma_ip_addr,
                                            self._config_file_path)
            c3745.upload_to_device_tftp(child,
                                        reporter,
                                        self._eol,
                                        self._pma_ip_addr,
                                        self._config_file_path,
                                        default_file_system)
        except BaseException:
            ex_type, ex_value, traceback = sys.exc_info()
            reporter.error()
            raise ex_type, ex_value, traceback
        finally:
            c3745.close_telnet_connection(child, reporter)