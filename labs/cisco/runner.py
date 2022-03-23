# -*- coding: utf-8 -*-
"""

"""

from labs.cisco.iosxe_l3 import CiscoIOSXEL3
from labs.cisco.reporter import Reporter


def main(reporter):
    """Runner to test Cisco IOS and IOS-XE devices

    :param labs.cisco.Reporter reporter: A reference to the popup GUI window that reports
        the status and progress of the script.

    :return: None
    :rtype: None
    """

    """
    c3745 = Cisco3745(device_hostname='R1',
                      eol='\r',
                      device_ip_addr='192.168.1.20',
                      ethernet_port='FastEthernet0/0',
                      remote_ip_addr='192.168.1.10',
                      subnet_mask='255.255.255.0',
                      # username=None,
                      # password=None,
                      file_to_transfer='/var/lib/tftpboot/start-3745',
                      remote_username='gns3user',
                      remote_password='gns3user')
    c3745.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
              telnet_port_num=5003)
    """

    """
    switch = Cisco9500(device_hostname='Switch',
                       eol='',
                       device_ip_addr='192.168.1.30',
                       vlan_name='vlan 1',
                       ethernet_port='GigabitEthernet0/0',
                       remote_ip_addr='192.168.1.10',
                       subnet_mask='255.255.255.0',
                       username=None,
                       password=None,
                       file_to_transfer='/var/lib/tftpboot/start-9500',
                       remote_username='gns3user',
                       remote_password='gns3user')
    switch.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
               telnet_port_num=5001)
    """

    """
    switch = CiscoIOSL2(device_hostname='Switch',
                        eol='',
                        device_ip_addr='192.168.1.40',
                        vlan_name='vlan 1',
                        ethernet_port='GigabitEthernet0/0',
                        remote_ip_addr='192.168.1.10',
                        subnet_mask='255.255.255.0',
                        username=None,
                        password=None,
                        file_to_transfer='/var/lib/tftpboot/start-IOSvL2',
                        remote_username='gns3user',
                        remote_password='gns3user')
    switch.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
               telnet_port_num=5001)
    """

    # """
    router = CiscoIOSXEL3(device_hostname='Router',
                          eol='',
                          device_ip_addr='192.168.1.50',
                          ethernet_port='GigabitEthernet1',
                          remote_ip_addr='192.168.1.10',
                          subnet_mask='255.255.255.0',
                          # username=None,
                          # password=None,
                          file_to_transfer='/var/lib/tftpboot/start-IOSv3',
                          remote_username='gns3user',
                          remote_password='gns3user')
    router.run(reporter, connection_type='telnet', telnet_ip_addr='192.168.1.1',
               telnet_port_num=5004)
    # """


if __name__ == '__main__':
    r = Reporter()
    main(r)
