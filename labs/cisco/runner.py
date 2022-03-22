# -*- coding: utf-8 -*-
"""

"""

from labs.cisco.c3745 import Cisco3745
from labs.cisco.ios_l2 import CiscoIOSL2
from labs.cisco.iosxe_l3 import CiscoIOSXEL3
from labs.cisco.reporter import Reporter


def main(reporter):
    """Runner to test Cisco IOS and IOS-XE devices

    :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
        the status and progress of the script.

    :return: None
    :rtype: None
    """

    # """
    c3745 = Cisco3745(device_hostname='R1',
                      eol='\r',
                      device_ip_addr='192.168.1.20',
                      pma_ip_addr='192.168.1.10',
                      username=None,
                      password=None,
                      ethernet_port='FastEthernet0/0',
                      subnet_mask='255.255.255.0',
                      config_file_path='/var/lib/tftpboot/startup-config-c3745.tftp')
    c3745.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
              telnet_port_num=5003)
    # """

    # """
    switch = CiscoIOSL2(device_hostname='Switch',
                        eol='',
                        device_ip_addr='192.168.1.30',
                        pma_ip_addr='192.168.1.10',
                        username=None,
                        password=None,
                        vlan_name='vlan 1',
                        vlan_port='GigabitEthernet0/0',
                        subnet_mask='255.255.255.0',
                        config_file_path='/var/lib/tftpboot/startup-config-switch.tftp')
    switch.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
               telnet_port_num=5002)
    # """

    # """
    router = CiscoIOSXEL3(device_hostname='Router',
                          eol='',
                          device_ip_addr='192.168.1.40',
                          pma_ip_addr='192.168.1.10',
                          username=None,
                          password=None,
                          ethernet_port='GigabitEthernet1',
                          subnet_mask='255.255.255.0',
                          config_file_path='/var/lib/tftpboot/startup-config-router.tftp')
    router.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
               telnet_port_num=5004)
    # """


if __name__ == '__main__':
    r = Reporter()
    main(r)
